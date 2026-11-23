import json
import re
from datetime import datetime
from pathlib import Path

import pytest

from src.reminder_agent import ReminderResult, validate_result


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "specs"
    / "001-reminder-agent"
    / "contracts"
    / "reminder-result.schema.json"
)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def test_reminder_result_schema_contract_file_is_the_expected_shape():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert set(schema["required"]) == {
        "title",
        "date",
        "time",
        "status",
        "clarification",
    }
    assert schema["additionalProperties"] is False
    assert schema["properties"]["status"]["enum"] == [
        "ready",
        "needs_clarification",
    ]


@pytest.mark.parametrize(
    "payload",
    [
        {
            "title": "Study Python",
            "date": "2026-11-23",
            "time": "18:00",
            "status": "ready",
            "clarification": None,
        },
        {
            "title": "Call Mom",
            "date": "2026-11-22",
            "time": "15:00",
            "status": "ready",
            "clarification": None,
        },
    ],
)
def test_ready_contract_payloads(payload):
    result = validate_result(payload)

    assert set(result.to_dict()) == {
        "title",
        "date",
        "time",
        "status",
        "clarification",
    }
    assert result.status == "ready"
    assert DATE_PATTERN.fullmatch(result.date)
    assert TIME_PATTERN.fullmatch(result.time)
    assert result.clarification is None


def test_ready_result_has_status_dependent_fields():
    ready = ReminderResult(
        title="Submit report",
        date="2026-11-30",
        time="12:00",
        status="ready",
        clarification=None,
    )

    assert validate_result(ready) == ready
