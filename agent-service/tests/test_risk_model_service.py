from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.risk_model_service import RiskModelNotFoundError, RiskModelService


class DummyRiskModel:
    def __init__(self, probability=0.82):
        self.probability = probability

    def predict_proba(self, rows):
        return [[1 - self.probability, self.probability]]


def _features():
    return {
        "age": 35,
        "monthly_income": 6800.0,
        "work_years": 2,
        "existing_debt": 90000.0,
        "overdue_count": 2,
        "asset_proof_count": 0,
        "amount": 150000.0,
        "term_months": 36,
        "debt_income_ratio": 1.1,
    }


def test_risk_model_service_predicts_with_existing_model():
    feature_names = list(_features().keys())
    metadata = {
        "model_name": "logistic_regression_baseline",
        "features": feature_names,
        "label": "ground_truth_risk",
        "metrics": {"roc_auc": 0.7},
    }

    with patch.object(RiskModelService, "_load_model", return_value=DummyRiskModel(0.82)), patch.object(
        RiskModelService, "_load_metadata", return_value=metadata
    ):
        result = RiskModelService().predict_risk(_features())

    assert result["model_risk_probability"] == pytest.approx(0.82)
    assert result["model_risk_label"] == "HIGH"
    assert result["model_version"] == "logistic_regression_baseline"
    assert result["features_used"] == feature_names
    assert result["explanation"]


def test_risk_model_service_missing_model_has_clear_exception():
    service = RiskModelService(
        model_path=Path(__file__).parent / "missing_model.joblib",
        metadata_path=Path(__file__).parent / "missing_metadata.json",
    )

    with pytest.raises(RiskModelNotFoundError, match="Risk model artifact not found"):
        service.predict_risk(_features())


@pytest.mark.parametrize(
    ("probability", "expected_label"),
    [
        (0.34, "LOW"),
        (0.35, "MEDIUM"),
        (0.64, "MEDIUM"),
        (0.65, "HIGH"),
    ],
)
def test_risk_model_service_maps_probability_to_three_risk_levels(probability, expected_label):
    with patch.object(RiskModelService, "_load_model", return_value=DummyRiskModel(probability)), patch.object(
        RiskModelService, "_load_metadata", return_value={"model_name": "unknown", "features": [], "metrics": {}}
    ):
        result = RiskModelService().predict_risk(_features())

    assert result["model_risk_label"] == expected_label
    assert result["model_version"] == "unknown"


def test_risk_model_service_missing_feature_raises_clear_error():
    metadata = {"model_name": "logistic_regression_baseline", "features": list(_features().keys())}
    incomplete_features = _features()
    incomplete_features.pop("amount")

    with patch.object(RiskModelService, "_load_model", return_value=DummyRiskModel()), patch.object(
        RiskModelService, "_load_metadata", return_value=metadata
    ):
        service = RiskModelService()
        with pytest.raises(ValueError, match="Missing model features"):
            service.predict_risk(incomplete_features)
