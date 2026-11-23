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


def test_next_friday_is_resolved_but_missing_time_requests_clarification():
    result = create_reminder(
        ReminderRequest("Remind me to call the office next Friday", REFERENCE_CONTEXT)
    )

    assert result.status == "needs_clarification"
    assert result.title == "Call the office"
    assert result.date == "2026-11-27"
    assert result.time is None
    assert "time" in result.clarification.lower()


def test_bare_time_6_requests_am_pm_clarification():
    result = create_reminder(
        ReminderRequest("Remind me to join the webinar at 6", REFERENCE_CONTEXT)
    )

    assert result.status == "needs_clarification"
    assert result.title == "Join the webinar"
    assert result.date is None
    assert result.time is None
    assert "6 AM" in result.clarification
    assert "6 PM" in result.clarification
    assert "date" in result.clarification.lower()


def test_any_bare_hour_requests_am_pm_clarification_without_guessing():
    result = create_reminder(
        ReminderRequest(
            "Remind me to join the webinar tomorrow at 7",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "needs_clarification"
    assert result.title == "Join the webinar"
    assert result.date == "2026-11-23"
    assert result.time is None
    assert "7 AM" in result.clarification
    assert "7 PM" in result.clarification


def test_midnight_without_date_preserves_time_and_requests_date():
    result = create_reminder(
        ReminderRequest(
            "Remind me to submit the report at midnight",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "needs_clarification"
    assert result.title == "Submit the report"
    assert result.date is None
    assert result.time == "00:00"
    assert "date" in result.clarification.lower()


def test_midnight_with_explicit_date_is_00_00():
    result = create_reminder(
        ReminderRequest(
            "Remind me to submit the report on 2026-11-23 at midnight",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "ready"
    assert result.title == "Submit the report"
    assert result.date == "2026-11-23"
    assert result.time == "00:00"


def test_contradictory_ampm_and_24_hour_times_request_clarification():
    result = create_reminder(
        ReminderRequest(
            "Remind me to submit the form on 2026-11-23 at 6 PM, "
            "but make it 09:00 instead",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "needs_clarification"
    assert result.title == "Submit the form"
    assert result.date == "2026-11-23"
    assert result.time is None
    assert "6 PM" in result.clarification
    assert "09:00" in result.clarification


def test_equivalent_time_formats_do_not_hide_a_contradictory_time():
    result = create_reminder(
        ReminderRequest(
            "Remind me to submit the form on 2026-11-23 at 6 PM, "
            "which is 18:00, but 9 AM instead",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "needs_clarification"
    assert result.time is None
    assert "6 PM" in result.clarification
    assert "9 AM" in result.clarification
    assert "18:00" not in result.clarification


def test_midnight_in_a_title_does_not_override_an_explicit_time():
    result = create_reminder(
        ReminderRequest(
            "Remind me to listen to Midnight Oil tomorrow at 6 PM.",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "ready"
    assert result.title == "Listen to Midnight Oil"
    assert result.date == "2026-11-23"
    assert result.time == "18:00"


def test_ambiguous_time_of_day_requests_an_exact_time():
    for period in ("afternoon", "evening"):
        result = create_reminder(
            ReminderRequest(
                f"Remind me to call Mom tomorrow in the {period}",
                REFERENCE_CONTEXT,
            )
        )

        assert result.status == "needs_clarification"
        assert result.title == "Call Mom"
        assert result.date == "2026-11-23"
        assert result.time is None
        assert "time" in result.clarification.lower()


def test_midnight_and_noon_conflict_requires_clarification():
    result = create_reminder(
        ReminderRequest(
            "Remind me to submit the report on 2026-11-23 at midnight, "
            "but actually at noon",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "needs_clarification"
    assert result.title == "Submit the report"
    assert result.date == "2026-11-23"
    assert result.time is None
    assert "midnight" in result.clarification.lower()
    assert "noon" in result.clarification.lower()


def test_equivalent_named_and_numeric_times_are_not_contradictory():
    cases = (
        ("at midnight, but actually at 00:00", "00:00"),
        ("at noon, but actually at 12 PM", "12:00"),
    )

    for expressions, expected_time in cases:
        result = create_reminder(
            ReminderRequest(
                f"Remind me to submit the report on 2026-11-23 {expressions}",
                REFERENCE_CONTEXT,
            )
        )

        assert result.status == "ready"
        assert result.date == "2026-11-23"
        assert result.time == expected_time


def test_conflicting_explicit_and_relative_dates_require_clarification():
    result = create_reminder(
        ReminderRequest(
            "Remind me to submit the report tomorrow on 2026-11-30 at 9 AM.",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "needs_clarification"
    assert result.title == "Submit the report"
    assert result.date is None
    assert result.time == "09:00"
    assert "date" in result.clarification.lower()


def test_equivalent_explicit_and_relative_dates_are_not_contradictory():
    result = create_reminder(
        ReminderRequest(
            "Remind me to submit the report tomorrow on 2026-11-23 at 9 AM.",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "ready"
    assert result.date == "2026-11-23"
    assert result.time == "09:00"


def test_relative_date_uses_the_named_timezone_not_reference_offset():
    context = EvaluationContext(
        reference_datetime=datetime.fromisoformat("2026-11-22T23:30:00+00:00"),
        timezone="Asia/Kolkata",
    )
    result = create_reminder(
        ReminderRequest("Remind me to call Mom tomorrow at 9 AM.", context)
    )

    assert result.status == "ready"
    assert result.date == "2026-11-24"
    assert result.time == "09:00"


def test_invalid_timezone_does_not_resolve_a_relative_date():
    context = EvaluationContext(
        reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
        timezone="Not/A_Real_Zone",
    )
    result = create_reminder(
        ReminderRequest("Remind me to call Mom tomorrow at 9 AM.", context)
    )

    assert result.status == "needs_clarification"
    assert result.title == "Call Mom"
    assert result.date is None
    assert result.time is None
    assert "timezone" in result.clarification.lower()


def test_contradictory_times_request_clarification():
    result = create_reminder(
        ReminderRequest(
            "Remind me to submit the form on 2026-11-23 at 6 PM, "
            "but make it 9 AM instead",
            REFERENCE_CONTEXT,
        )
    )

    assert result.status == "needs_clarification"
    assert result.title == "Submit the form"
    assert result.date == "2026-11-23"
    assert result.time is None
    assert "6 PM" in result.clarification
    assert "9 AM" in result.clarification
