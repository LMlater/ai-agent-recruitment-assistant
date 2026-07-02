from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = REPO_ROOT / "agent-service" / "models" / "credit_risk_model.joblib"
DEFAULT_METADATA_PATH = REPO_ROOT / "agent-service" / "models" / "model_metadata.json"


class RiskModelNotFoundError(RuntimeError):
    pass


class RiskModelService:
    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL_PATH,
        metadata_path: Path | str = DEFAULT_METADATA_PATH,
        threshold: float = 0.5,
    ) -> None:
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.threshold = threshold
        self._artifact: Any | None = None
        self._metadata: dict[str, Any] | None = None

    def predict_risk(self, features: dict[str, Any]) -> dict[str, Any]:
        model = self._load_model()
        metadata = self._load_metadata()
        feature_names = self._feature_names(model, metadata, features)
        missing_features = [name for name in feature_names if name not in features]
        if missing_features:
            raise ValueError(f"Missing model features: {missing_features}")

        input_frame = pd.DataFrame([{name: features[name] for name in feature_names}])
        probability = self._predict_high_risk_probability(model, input_frame)
        risk_label = "HIGH" if probability >= self.threshold else "LOW"
        return {
            "model_risk_probability": round(probability, 4),
            "model_risk_label": risk_label,
            "model_version": metadata.get("model_name", "unknown"),
            "features_used": feature_names,
            "explanation": self._build_explanation(features, probability, risk_label),
        }

    def _load_model(self) -> Any:
        if self._artifact is not None:
            return self._artifact
        if not self.model_path.exists():
            raise RiskModelNotFoundError(f"Risk model artifact not found: {self.model_path}")
        self._artifact = joblib.load(self.model_path)
        return self._artifact

    def _load_metadata(self) -> dict[str, Any]:
        if self._metadata is not None:
            return self._metadata
        if not self.metadata_path.exists():
            self._metadata = {"model_name": "unknown", "features": [], "metrics": {}}
            return self._metadata
        self._metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        return self._metadata

    def _feature_names(self, model: Any, metadata: dict[str, Any], features: dict[str, Any]) -> list[str]:
        if isinstance(model, dict) and model.get("features"):
            return list(model["features"])
        if metadata.get("features"):
            return list(metadata["features"])
        return list(features.keys())

    def _predict_high_risk_probability(self, model: Any, input_frame: pd.DataFrame) -> float:
        estimator = model.get("pipeline") if isinstance(model, dict) else model
        probabilities = estimator.predict_proba(input_frame)[0]
        if len(probabilities) == 1:
            return float(probabilities[0])
        return float(probabilities[1])

    def _build_explanation(self, features: dict[str, Any], probability: float, risk_label: str) -> list[str]:
        explanation = [
            f"Baseline model estimates {probability:.2%} probability for HIGH risk, resulting in {risk_label} label."
        ]
        debt_income_ratio = float(features.get("debt_income_ratio", 0))
        if debt_income_ratio >= 0.8:
            explanation.append("Debt-income ratio is high in the mapped public-data feature set.")
        overdue_count = int(features.get("overdue_count", 0))
        if overdue_count > 0:
            explanation.append(f"Mapped overdue count is {overdue_count}.")
        monthly_income = float(features.get("monthly_income", 0))
        amount = float(features.get("amount", 0))
        if monthly_income > 0 and amount > monthly_income * 12:
            explanation.append("Requested amount is high relative to simulated monthly income.")
        if int(features.get("asset_proof_count", 0)) == 0:
            explanation.append("No mapped asset proof signal is present.")
        return explanation
