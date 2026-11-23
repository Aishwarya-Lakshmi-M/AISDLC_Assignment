from datetime import datetime

from src.reminder_agent import (
    EvaluationContext,
    ReminderRequest,
    create_reminder,
)


REFERENCE_CONTEXT = EvaluationContext(
    reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
    timezone="Asia/Kolkata",
)


def test_missing_date_preserves_title_and_time():
    result = create_reminder(
        ReminderRequest("Remind me to buy groceries at 7 PM", REFERENCE_CONTEXT)
    )

    assert result.status == "needs_clarification"
    assert result.title == "Buy groceries"
    assert result.date is None
    assert result.time == "19:00"
    assert "date" in result.clarification.lower()


def test_missing_time_preserves_title_and_date():
    result = create_reminder(
        ReminderRequest(
            "Remind me to renew my passport on 2026-12-10",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "needs_clarification"
    assert result.title == "Renew my passport"
    assert result.date == "2026-12-10"
    assert result.time is None
    assert "time" in result.clarification.lower()


def test_missing_title_preserves_date_and_time():
    result = create_reminder(
        ReminderRequest("Remind me tomorrow at 5 PM", REFERENCE_CONTEXT)
    )

    assert result.status == "needs_clarification"
    assert result.title is None
    assert result.date == "2026-11-23"
    assert result.time == "17:00"
    assert "activity" in result.clarification.lower()


def test_missing_evaluation_context_never_resolves_relative_values():
    result = create_reminder(
        ReminderRequest(
            "Remind me to back up files tomorrow morning",
            EvaluationContext(reference_datetime=None, timezone=None),
        )
    )

    assert result.status == "needs_clarification"
    assert result.title == "Back up files"
    assert result.date is None
    assert result.time is None
