from pathlib import Path
import runpy
import sys

from scripts.prepare_credit_dataset import REQUIRED_COLUMNS, map_german_credit_record


RAW_GOOD_CASE = {
    "checking_status": "A11",
    "duration_months": "12",
    "credit_history": "A32",
    "purpose_code": "A43",
    "credit_amount": "2096",
    "savings_status": "A61",
    "employment_since": "A74",
    "installment_rate": "2",
    "personal_status": "A93",
    "other_debtors": "A101",
    "present_residence_since": "3",
    "property_code": "A121",
    "age": "49",
    "other_installment_plans": "A143",
    "housing": "A152",
    "existing_credits": "1",
    "job": "A173",
    "people_liable": "2",
    "telephone": "A191",
    "foreign_worker": "A201",
    "target": "1",
}


def test_mapped_case_contains_project_required_fields():
    mapped = map_german_credit_record(RAW_GOOD_CASE, case_index=1)

    assert set(REQUIRED_COLUMNS).issubset(mapped.keys())
    assert mapped["case_id"] == "CASE_0001"
    assert mapped["age"] == 49
    assert mapped["amount"] == 2096
    assert mapped["term_months"] == 12
    assert mapped["purpose"]


def test_ground_truth_risk_mapping_is_project_label():
    good_case = map_german_credit_record(RAW_GOOD_CASE, case_index=1)
    bad_raw = {**RAW_GOOD_CASE, "target": "2"}
    bad_case = map_german_credit_record(bad_raw, case_index=2)

    assert good_case["ground_truth_risk"] == "LOW"
    assert bad_case["ground_truth_risk"] == "HIGH"


def test_derived_income_and_debt_income_ratio_are_reasonable():
    mapped = map_german_credit_record(RAW_GOOD_CASE, case_index=1)

    assert mapped["monthly_income"] > 0
    assert mapped["existing_debt"] >= 0
    assert 0 <= mapped["debt_income_ratio"] < 10


def test_mapping_can_surface_high_debt_income_cases():
    raw_high_debt = {
        **RAW_GOOD_CASE,
        "duration_months": "72",
        "credit_amount": "18424",
        "installment_rate": "4",
        "existing_credits": "4",
    }

    mapped = map_german_credit_record(raw_high_debt, case_index=99)

    assert mapped["debt_income_ratio"] >= 0.8


def test_mapping_does_not_emit_real_identity_or_phone_fields():
    mapped = map_german_credit_record(RAW_GOOD_CASE, case_index=1)

    forbidden_fields = {"id_card", "id_card_masked", "identity_card", "phone", "phone_masked", "mobile"}
    assert forbidden_fields.isdisjoint(mapped.keys())


def test_train_script_can_be_loaded_from_file_path():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "train_risk_model.py"
    agent_service_root = str(script_path.parents[1])
    original_sys_path = sys.path[:]
    original_scripts_module = sys.modules.pop("scripts", None)
    original_prepare_module = sys.modules.pop("scripts.prepare_credit_dataset", None)

    try:
        sys.path = [str(script_path.parent)] + [path for path in sys.path if path not in {"", agent_service_root}]
        loaded_globals = runpy.run_path(str(script_path), run_name="not_main")
    finally:
        sys.path = original_sys_path
        if original_scripts_module is not None:
            sys.modules["scripts"] = original_scripts_module
        if original_prepare_module is not None:
            sys.modules["scripts.prepare_credit_dataset"] = original_prepare_module

    assert "train_model" in loaded_globals
