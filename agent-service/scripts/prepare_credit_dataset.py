from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = REPO_ROOT / "data" / "raw" / "german_credit" / "german.data"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
EVAL_DIR = REPO_ROOT / "data" / "eval"
SEED_DIR = REPO_ROOT / "data" / "seed"

GERMAN_COLUMNS = [
    "checking_status",
    "duration_months",
    "credit_history",
    "purpose_code",
    "credit_amount",
    "savings_status",
    "employment_since",
    "installment_rate",
    "personal_status",
    "other_debtors",
    "present_residence_since",
    "property_code",
    "age",
    "other_installment_plans",
    "housing",
    "existing_credits",
    "job",
    "people_liable",
    "telephone",
    "foreign_worker",
    "target",
]

REQUIRED_COLUMNS = [
    "case_id",
    "age",
    "monthly_income",
    "work_years",
    "existing_debt",
    "overdue_count",
    "asset_proof_count",
    "amount",
    "term_months",
    "purpose",
    "debt_income_ratio",
    "ground_truth_risk",
]

PURPOSE_MAP = {
    "A40": "new car",
    "A41": "used car",
    "A42": "furniture equipment",
    "A43": "radio television",
    "A44": "domestic appliances",
    "A45": "repairs",
    "A46": "education",
    "A47": "vacation",
    "A48": "retraining",
    "A49": "business",
    "A410": "others",
}

EMPLOYMENT_YEARS_MAP = {
    "A71": 0,
    "A72": 0.5,
    "A73": 2,
    "A74": 5,
    "A75": 8,
}

CREDIT_HISTORY_OVERDUE_MAP = {
    "A30": 0,
    "A31": 0,
    "A32": 0,
    "A33": 1,
    "A34": 2,
}

PROPERTY_ASSET_MAP = {
    "A121": 2,
    "A122": 2,
    "A123": 1,
    "A124": 0,
}

SAVINGS_ASSET_MAP = {
    "A61": 0,
    "A62": 1,
    "A63": 1,
    "A64": 2,
    "A65": 1,
}

INSTALLMENT_FRACTION_MAP = {
    1: 0.35,
    2: 0.30,
    3: 0.22,
    4: 0.18,
}

MODEL_FEATURES = [
    "age",
    "monthly_income",
    "work_years",
    "existing_debt",
    "overdue_count",
    "asset_proof_count",
    "amount",
    "term_months",
    "debt_income_ratio",
]


def _as_int(value: str) -> int:
    return int(value.strip())


def map_german_credit_record(raw: dict[str, str], case_index: int) -> dict[str, object]:
    amount = _as_int(raw["credit_amount"])
    term_months = max(_as_int(raw["duration_months"]), 1)
    age = _as_int(raw["age"])
    installment_rate = _as_int(raw["installment_rate"])
    existing_credits = max(_as_int(raw["existing_credits"]), 1)

    monthly_payment = amount / term_months
    installment_fraction = INSTALLMENT_FRACTION_MAP.get(installment_rate, 0.25)
    monthly_income = round(max(1800.0, monthly_payment / installment_fraction * 6), 2)
    existing_debt = round(amount * existing_credits * (1.6 + installment_rate * 0.55), 2)
    annual_income = max(monthly_income * 12, 1.0)

    return {
        "case_id": f"CASE_{case_index:04d}",
        "age": age,
        "monthly_income": monthly_income,
        "work_years": EMPLOYMENT_YEARS_MAP.get(raw["employment_since"], 1),
        "existing_debt": existing_debt,
        "overdue_count": CREDIT_HISTORY_OVERDUE_MAP.get(raw["credit_history"], 0),
        "asset_proof_count": min(
            4,
            PROPERTY_ASSET_MAP.get(raw["property_code"], 0) + SAVINGS_ASSET_MAP.get(raw["savings_status"], 0),
        ),
        "amount": amount,
        "term_months": term_months,
        "purpose": PURPOSE_MAP.get(raw["purpose_code"], "others"),
        "debt_income_ratio": round(existing_debt / annual_income, 4),
        "ground_truth_risk": "LOW" if raw["target"] == "1" else "HIGH",
    }


def read_german_credit_rows(path: Path = RAW_DATA_PATH) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run agent-service/scripts/download_german_credit.py or place german.data manually."
        )

    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            values = line.strip().split()
            if not values:
                continue
            if len(values) != len(GERMAN_COLUMNS):
                raise ValueError(f"Unexpected German Credit row width {len(values)}: {line[:80]}")
            rows.append(dict(zip(GERMAN_COLUMNS, values)))
    return rows


def write_csv(rows: Iterable[dict[str, object]], path: Path, columns: list[str] = REQUIRED_COLUMNS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=columns)
        writer.writeheader()
        writer.writerows(materialized)


def split_rows(rows: list[dict[str, object]], seed: int = 42, test_ratio: float = 0.2) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    shuffled = rows[:]
    random.Random(seed).shuffle(shuffled)
    test_size = max(1, round(len(shuffled) * test_ratio))
    return shuffled[test_size:], shuffled[:test_size]


def classify_demo_risk(row: dict[str, object]) -> str:
    dti = float(row["debt_income_ratio"])
    overdue_count = int(row["overdue_count"])
    amount_to_income = float(row["amount"]) / max(float(row["monthly_income"]) * 12, 1.0)
    if row["ground_truth_risk"] == "HIGH" or overdue_count >= 2 or dti >= 0.8 or amount_to_income >= 2.0:
        return "HIGH"
    if overdue_count == 1 or dti >= 0.4 or amount_to_income >= 1.0:
        return "MEDIUM"
    return "LOW"


def _pick_rows_by_demo_risk(rows: list[dict[str, object]], per_bucket: int = 4) -> list[dict[str, object]]:
    buckets = {"LOW": [], "MEDIUM": [], "HIGH": []}
    for row in rows:
        bucket = classify_demo_risk(row)
        if len(buckets[bucket]) < per_bucket:
            buckets[bucket].append(row)
    selected = buckets["LOW"][:4] + buckets["MEDIUM"][:3] + buckets["HIGH"][:3]
    if len(selected) < 10:
        seen = {row["case_id"] for row in selected}
        selected.extend(row for row in rows if row["case_id"] not in seen)
    return selected[:10]


def generate_seed_sql(rows: list[dict[str, object]]) -> None:
    selected = _pick_rows_by_demo_risk(rows)
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    customer_lines = [
        "-- Generated mock customers from public German Credit mappings. Do not treat as real customer data.",
    ]
    loan_lines = [
        "-- Generated mock loan applications from public German Credit mappings. Import customers first.",
    ]

    for index, row in enumerate(selected, start=1):
        name = f"Seed Customer {index:03d}"
        id_card_masked = f"4401********{index:04d}"
        phone_masked = f"138****{index:04d}"
        customer_lines.extend(
            [
                "insert into customer(name, id_card_masked, phone_masked, age, monthly_income, work_years, existing_debt, overdue_count, asset_proof_count)",
                (
                    f"select '{name}', '{id_card_masked}', '{phone_masked}', {int(row['age'])}, "
                    f"{float(row['monthly_income']):.2f}, {float(row['work_years']):.1f}, "
                    f"{float(row['existing_debt']):.2f}, {int(row['overdue_count'])}, {int(row['asset_proof_count'])}"
                ),
                f"where not exists (select 1 from customer where name = '{name}');",
                "",
            ]
        )
        purpose = str(row["purpose"]).replace("'", "''")
        loan_lines.extend(
            [
                "insert into loan_application(customer_id, amount, term_months, purpose, status, created_by)",
                (
                    f"select id, {float(row['amount']):.2f}, {int(row['term_months'])}, "
                    f"'generated seed {row['case_id']} {purpose}', 'SUBMITTED', null"
                ),
                "from customer",
                f"where name = '{name}'",
                f"  and not exists (select 1 from loan_application where purpose = 'generated seed {row['case_id']} {purpose}');",
                "",
            ]
        )

    (SEED_DIR / "generated_customers_seed.sql").write_text("\n".join(customer_lines), encoding="utf-8")
    (SEED_DIR / "generated_loan_applications_seed.sql").write_text("\n".join(loan_lines), encoding="utf-8")


def _feature_payload(row: dict[str, object]) -> dict[str, object]:
    return {name: row[name] for name in MODEL_FEATURES}


def generate_eval_cases(rows: list[dict[str, object]]) -> None:
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    case_specs = [
        ("low risk public-data mapped case", lambda row: classify_demo_risk(row) == "LOW"),
        ("medium risk public-data mapped case", lambda row: classify_demo_risk(row) == "MEDIUM"),
        ("high risk public-data mapped case", lambda row: classify_demo_risk(row) == "HIGH"),
        ("High debt-income ratio", lambda row: float(row["debt_income_ratio"]) >= 0.8),
        ("High overdue history", lambda row: int(row["overdue_count"]) >= 2),
        ("Requested amount is high relative to simulated income", lambda row: float(row["amount"]) >= float(row["monthly_income"]) * 1.5),
    ]
    cases = []
    used: set[str] = set()
    for note, predicate in case_specs:
        match = next((row for row in rows if row["case_id"] not in used and predicate(row)), None)
        if match is None:
            match = max(rows, key=lambda row: float(row["debt_income_ratio"]))
        used.add(str(match["case_id"]))
        cases.append(
            {
                "case_id": match["case_id"],
                "features": _feature_payload(match),
                "expected_risk": classify_demo_risk(match),
                "notes": note,
            }
        )

    with (EVAL_DIR / "model_eval_cases.jsonl").open("w", encoding="utf-8") as target:
        for case in cases:
            target.write(json.dumps(case, ensure_ascii=False) + "\n")


def prepare_dataset(raw_path: Path = RAW_DATA_PATH) -> list[dict[str, object]]:
    raw_rows = read_german_credit_rows(raw_path)
    mapped_rows = [map_german_credit_record(row, index) for index, row in enumerate(raw_rows, start=1)]
    train_rows, test_rows = split_rows(mapped_rows)

    write_csv(mapped_rows, PROCESSED_DIR / "credit_cases.csv")
    write_csv(train_rows, PROCESSED_DIR / "train.csv")
    write_csv(test_rows, PROCESSED_DIR / "test.csv")
    generate_seed_sql(mapped_rows)
    generate_eval_cases(mapped_rows)
    return mapped_rows


def main() -> int:
    try:
        rows = prepare_dataset()
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Prepared {len(rows)} German Credit cases under {PROCESSED_DIR}")
    print(f"Generated seed SQL under {SEED_DIR}")
    print(f"Generated model eval cases under {EVAL_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
