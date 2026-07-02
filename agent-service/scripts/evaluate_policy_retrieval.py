from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AGENT_SERVICE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = AGENT_SERVICE_ROOT.parent
if str(AGENT_SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_SERVICE_ROOT))

from app.services.policy_retrieval_service import PolicyRetrievalService


EVAL_DIR = REPO_ROOT / "data" / "eval"
QUESTIONS_PATH = EVAL_DIR / "rag_questions.jsonl"
RESULTS_PATH = EVAL_DIR / "rag_eval_results.json"
KNOWLEDGE_BASE_DIR = AGENT_SERVICE_ROOT / "knowledge_base"


def load_questions(path: Path = QUESTIONS_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found.")

    questions: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            record = json.loads(stripped)
            if "question" not in record or "expected_policy_codes" not in record:
                raise ValueError(f"Invalid RAG eval record at line {line_number}: {record}")
            questions.append(record)
    return questions


def compute_metrics(evaluated_cases: list[dict[str, Any]]) -> dict[str, float | int]:
    if not evaluated_cases:
        return {
            "case_count": 0,
            "recall_at_3": 0.0,
            "recall_at_5": 0.0,
            "hit_rate": 0.0,
            "mrr": 0.0,
        }

    recall_at_3_values: list[float] = []
    recall_at_5_values: list[float] = []
    hit_values: list[float] = []
    reciprocal_ranks: list[float] = []

    for case in evaluated_cases:
        expected_codes = set(case["expected_policy_codes"])
        retrieved_codes = list(case["retrieved_policy_codes"])
        if not expected_codes:
            continue

        top_3 = set(retrieved_codes[:3])
        top_5 = set(retrieved_codes[:5])
        recall_at_3_values.append(len(expected_codes.intersection(top_3)) / len(expected_codes))
        recall_at_5_values.append(len(expected_codes.intersection(top_5)) / len(expected_codes))
        hit_values.append(1.0 if expected_codes.intersection(top_5) else 0.0)

        reciprocal_rank = 0.0
        for rank, code in enumerate(retrieved_codes, start=1):
            if code in expected_codes:
                reciprocal_rank = 1 / rank
                break
        reciprocal_ranks.append(reciprocal_rank)

    denominator = len(recall_at_3_values)
    return {
        "case_count": denominator,
        "recall_at_3": sum(recall_at_3_values) / denominator,
        "recall_at_5": sum(recall_at_5_values) / denominator,
        "hit_rate": sum(hit_values) / denominator,
        "mrr": sum(reciprocal_ranks) / denominator,
    }


def evaluate_policy_retrieval(top_k: int = 5) -> dict[str, Any]:
    questions = load_questions()
    service = PolicyRetrievalService(knowledge_base_dir=KNOWLEDGE_BASE_DIR)
    evaluated_cases: list[dict[str, Any]] = []

    for question in questions:
        references = service.search(question["question"], top_k=top_k)
        retrieved_codes = [reference.policy_code for reference in references if reference.policy_code]
        evaluated_cases.append(
            {
                "id": question.get("id"),
                "question": question["question"],
                "expected_policy_codes": question["expected_policy_codes"],
                "retrieved_policy_codes": retrieved_codes,
                "references": [reference.model_dump() for reference in references],
            }
        )

    metrics = compute_metrics(evaluated_cases)
    return {
        "metadata": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "knowledge_base_dir": str(KNOWLEDGE_BASE_DIR),
            "questions_path": str(QUESTIONS_PATH),
            "top_k": top_k,
            "retrieval_method": "local TfidfVectorizer char n-gram + cosine similarity",
            "disclaimer": "Mock policy documents for learning and engineering demonstration only.",
        },
        "metrics": metrics,
        "cases": evaluated_cases,
    }


def main() -> int:
    try:
        result = evaluate_policy_retrieval()
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved RAG retrieval evaluation to {RESULTS_PATH}")
    print(json.dumps(result["metrics"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
