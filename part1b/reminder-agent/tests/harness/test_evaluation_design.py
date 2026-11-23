import json
import re
from datetime import datetime
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "evals" / "dataset.json"
SCORING_PATH = PROJECT_ROOT / "evals" / "scoring.md"
HARNESS_CONTRACT_PATH = PROJECT_ROOT / "evals" / "harness_contract.md"

REQUIRED_CASE_FIELDS = {
    "case_id",
    "category",
    "input",
    "reference_datetime",
    "timezone",
    "expected_status",
    "expected_title",
    "expected_date",
    "expected_time",
    "expected_clarification",
    "explanation",
}

ALLOWED_STATUSES = {"ready", "needs_clarification"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def load_dataset():
    with DATASET_PATH.open("r", encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def test_evaluation_dataset_has_exactly_twenty_unique_cases():
    dataset = load_dataset()

    assert len(dataset) == 20
    case_ids = [case["case_id"] for case in dataset]
    assert len(case_ids) == len(set(case_ids))


@pytest.mark.parametrize("case", load_dataset())
def test_every_case_has_the_frozen_schema(case):
    assert set(case) == REQUIRED_CASE_FIELDS
    assert isinstance(case["case_id"], str) and case["case_id"]
    assert isinstance(case["category"], str) and case["category"]
    assert isinstance(case["input"], str)
    assert isinstance(case["explanation"], str) and case["explanation"]
    assert case["expected_status"] in ALLOWED_STATUSES

    assert case["expected_title"] is None or isinstance(case["expected_title"], str)
    assert case["expected_date"] is None or isinstance(case["expected_date"], str)
    assert case["expected_time"] is None or isinstance(case["expected_time"], str)
    assert case["expected_clarification"] is None or isinstance(
        case["expected_clarification"], str
    )


@pytest.mark.parametrize("case", load_dataset())
def test_expected_status_fields_follow_the_output_contract(case):
    if case["expected_status"] == "ready":
        assert isinstance(case["expected_title"], str) and case["expected_title"]
        assert isinstance(case["expected_date"], str)
        assert isinstance(case["expected_time"], str)
        assert case["expected_clarification"] is None
    else:
        assert isinstance(case["expected_clarification"], str)
        assert case["expected_clarification"]

    if case["expected_date"] is not None:
        assert DATE_PATTERN.fullmatch(case["expected_date"])
        datetime.strptime(case["expected_date"], "%Y-%m-%d")

    if case["expected_time"] is not None:
        assert TIME_PATTERN.fullmatch(case["expected_time"])


def test_missing_evaluation_context_is_represented_only_by_ra013():
    dataset = load_dataset()
    null_context_cases = [
        case["case_id"]
        for case in dataset
        if case["reference_datetime"] is None or case["timezone"] is None
    ]
    assert null_context_cases == ["RA-013"]


def test_explicit_context_is_populated_for_every_resolved_case():
    dataset = load_dataset()

    for case in dataset:
        if case["case_id"] == "RA-013":
            assert case["reference_datetime"] is None
            assert case["timezone"] is None
            continue

        assert isinstance(case["reference_datetime"], str)
        assert isinstance(case["timezone"], str)
        datetime.fromisoformat(case["reference_datetime"])


def test_per_case_expected_values_exist_for_ready_and_clarification_cases():
    dataset = load_dataset()
    ready_cases = [case for case in dataset if case["expected_status"] == "ready"]
    clarification_cases = [
        case for case in dataset if case["expected_status"] == "needs_clarification"
    ]

    assert ready_cases
    assert clarification_cases
    assert len(ready_cases) + len(clarification_cases) == 20


def test_dataset_contains_required_evaluation_categories():
    dataset = load_dataset()
    categories = {case["category"] for case in dataset}
    required_categories = {
        "normal_complete",
        "boundary",
        "relative_date_time",
        "missing_date",
        "missing_time",
        "missing_title",
        "ambiguous_date",
        "ambiguous_time",
        "contradictory_date_time",
        "missing_evaluation_context",
        "malformed_empty",
        "unsupported_operation",
        "adversarial_prompt_injection",
        "combined_supported_unsupported",
    }
    assert required_categories <= categories


def test_semantic_weights_still_sum_to_exactly_one_hundred():
    scoring_text = SCORING_PATH.read_text(encoding="utf-8")
    weights = {
        "Title/task extraction": 15,
        "Date accuracy": 15,
        "Time accuracy": 15,
        "Missing, ambiguous, and contradictory identification": 15,
        "Clarification quality": 15,
        "Preservation of safely known fields": 15,
        "Unsupported/mixed-operation handling": 10,
    }

    assert sum(weights.values()) == 100
    for dimension, weight in weights.items():
        assert re.search(
            rf"\| {re.escape(dimension)} \| {weight} \|",
            scoring_text,
        )


def test_immutable_pass_thresholds_are_preserved():
    scoring_text = SCORING_PATH.read_text(encoding="utf-8")
    contract_text = HARNESS_CONTRACT_PATH.read_text(encoding="utf-8")

    assert "at least 80" in scoring_text
    assert "at least 85%" in scoring_text
    assert "At least 18 of 20 cases are overall PASS." in scoring_text
    assert "20 of 20 structural PASS" in contract_text
    assert "20 of 20 behavioral PASS" in contract_text
    assert "20 of 20 safety PASS" in contract_text
    assert "Semantic percentage at least 85%" in contract_text
    assert "At least 18 of 20 overall PASS" in contract_text
