from datetime import datetime

import pytest

from src.reminder_agent import (
    EvaluationContext,
    ReminderRequest,
    create_reminder,
    validate_result,
    validate_unsupported_result,
)


CONTEXT = EvaluationContext(
    reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
    timezone="Asia/Kolkata",
)


def test_unsupported_result_uses_the_five_field_contract():
    result = create_reminder(ReminderRequest("Delete the dentist reminder.", CONTEXT))

    assert set(result.to_dict()) == {
        "title",
        "date",
        "time",
        "status",
        "clarification",
    }
    validated = validate_result(result)
    assert validated.status == "needs_clarification"
    assert validated.clarification


def test_validator_accepts_unsupported_clarification():
    result = validate_unsupported_result(
        {
            "title": None,
            "date": None,
            "time": None,
            "status": "needs_clarification",
            "clarification": "Rescheduling is unsupported.",
        }
    )

    assert result.status == "needs_clarification"


def test_validator_rejects_ready_status_for_explicit_unsupported_result():
    with pytest.raises(ValueError, match="Unsupported operations"):
        validate_unsupported_result(
            {
                "title": "Dentist appointment",
                "date": "2026-11-23",
                "time": "18:00",
                "status": "ready",
                "clarification": None,
            }
        )
