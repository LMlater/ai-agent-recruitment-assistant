import json
import shutil
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.risk_model_service import RiskModelNotFoundError, RiskModelService


TEST_TMP_DIR = Path(__file__).parent / "tmp_model_service"


class DummyRiskModel:
    def predict_proba(self, rows):
        return [[0.18, 0.82]]


@pytest.fixture()
def model_dir():
    TEST_TMP_DIR.mkdir(exist_ok=True)
    case_dir = TEST_TMP_DIR / uuid.uuid4().hex
    case_dir.mkdir()
    yield case_dir
    shutil.rmtree(case_dir, ignore_errors=True)


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


def test_risk_model_service_predicts_with_existing_model(model_dir):
    model_path = model_dir / "credit_risk_model.joblib"
    metadata_path = model_dir / "model_metadata.json"
    feature_names = list(_features().keys())
    model_path.write_text("placeholder model artifact", encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "model_name": "logistic_regression_baseline",
                "features": feature_names,
                "label": "ground_truth_risk",
                "metrics": {"roc_auc": 0.7},
            }
        ),
        encoding="utf-8",
    )

    with patch("app.services.risk_model_service.joblib.load", return_value=DummyRiskModel()):
        result = RiskModelService(model_path=model_path, metadata_path=metadata_path).predict_risk(_features())

    assert result["model_risk_probability"] == pytest.approx(0.82)
    assert result["model_risk_label"] == "HIGH"
    assert result["model_version"] == "logistic_regression_baseline"
    assert result["features_used"] == feature_names
    assert result["explanation"]


def test_risk_model_service_missing_model_has_clear_exception(model_dir):
    service = RiskModelService(
        model_path=model_dir / "missing_model.joblib",
        metadata_path=model_dir / "missing_metadata.json",
    )

    with pytest.raises(RiskModelNotFoundError, match="Risk model artifact not found"):
        service.predict_risk(_features())
