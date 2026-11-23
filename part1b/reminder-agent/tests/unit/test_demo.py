from datetime import datetime

import pytest

from src.reminder_agent.demo import build_demo_request


def test_build_demo_request_uses_explicit_reference_datetime_and_timezone():
    request = build_demo_request(
        "Remind me to study Python tomorrow at 6 PM",
        "2026-11-22T14:30:00+05:30",
        "Asia/Kolkata",
    )

    assert request.text == "Remind me to study Python tomorrow at 6 PM"
    assert request.context.reference_datetime == datetime.fromisoformat(
        "2026-11-22T14:30:00+05:30"
    )
    assert request.context.timezone == "Asia/Kolkata"


def test_build_demo_request_allows_missing_context_for_clarification():
    request = build_demo_request("Remind me to call Mom", "", "")

    assert request.context.reference_datetime is None
    assert request.context.timezone is None


def test_build_demo_request_rejects_invalid_reference_datetime():
    with pytest.raises(ValueError, match="ISO 8601"):
        build_demo_request("Remind me to call Mom", "tomorrow afternoon", "Asia/Kolkata")


def test_build_demo_request_requires_reference_datetime_offset():
    with pytest.raises(ValueError, match="UTC offset"):
        build_demo_request("Remind me to call Mom", "2026-11-22T14:30:00", "Asia/Kolkata")
