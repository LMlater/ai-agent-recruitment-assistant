from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

AGENT_SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(AGENT_SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_SERVICE_ROOT))

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from scripts.prepare_credit_dataset import MODEL_FEATURES, PROCESSED_DIR, REPO_ROOT


MODEL_DIR = REPO_ROOT / "agent-service" / "models"
EVAL_DIR = REPO_ROOT / "data" / "eval"
MODEL_PATH = MODEL_DIR / "credit_risk_model.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"
METRICS_PATH = EVAL_DIR / "model_metrics.json"
RANDOM_SEED = 42


def _load_dataset() -> pd.DataFrame:
    dataset_path = PROCESSED_DIR / "credit_cases.csv"
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"{dataset_path} not found. Run agent-service/scripts/prepare_credit_dataset.py before training."
        )
    return pd.read_csv(dataset_path)


def train_model() -> dict[str, object]:
    dataset = _load_dataset()
    missing_features = [feature for feature in MODEL_FEATURES if feature not in dataset.columns]
    if missing_features:
        raise ValueError(f"Dataset missing model features: {missing_features}")

    y = (dataset["ground_truth_risk"] == "HIGH").astype(int)
    train_dataset, test_dataset = train_test_split(
        dataset,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=y,
    )
    x_train = train_dataset[MODEL_FEATURES]
    x_test = test_dataset[MODEL_FEATURES]
    y_train = (train_dataset["ground_truth_risk"] == "HIGH").astype(int)
    y_test = (test_dataset["ground_truth_risk"] == "HIGH").astype(int)

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_SEED,
                ),
            ),
        ]
    )
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "test_size": int(len(y_test)),
        "train_size": int(len(y_train)),
        "random_seed": RANDOM_SEED,
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    train_dataset.to_csv(PROCESSED_DIR / "train.csv", index=False)
    test_dataset.to_csv(PROCESSED_DIR / "test.csv", index=False)

    artifact = {
        "pipeline": pipeline,
        "features": MODEL_FEATURES,
        "label_mapping": {"LOW": 0, "HIGH": 1},
        "risk_probability_threshold": 0.5,
    }
    joblib.dump(artifact, MODEL_PATH)

    metadata = {
        "model_name": "logistic_regression_baseline",
        "dataset": "UCI German Credit / Statlog German Credit",
        "features": MODEL_FEATURES,
        "label": "ground_truth_risk",
        "metrics": metrics,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "German Credit is a public teaching dataset and is not Chinese bank production data.",
            "Several project fields are simulated from coded attributes and are not real income or debt records.",
            "The model is a baseline approval-assistance signal and must not be used for automatic lending decisions.",
            "This artifact is not connected to RiskAgent in the current iteration.",
        ],
    }
    METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def main() -> int:
    try:
        metadata = train_model()
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Trained {metadata['model_name']} with metrics: {json.dumps(metadata['metrics'], ensure_ascii=False)}")
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metadata to {METADATA_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
