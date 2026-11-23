from datetime import datetime

from src.reminder_agent import (
    AIAdapterConfig,
    EvaluationContext,
    ProviderNeutralAIAdapter,
    ReminderRequest,
    create_reminder,
)


class MockAIClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def complete(self, prompt: str, *, provider: str, model: str) -> str:
        self.calls += 1
        return self.response


def test_mocked_relative_date_request_returns_ready_result():
    client = MockAIClient(
        '{"title":"Study Python","date":"2026-11-23","time":"18:00",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        client,
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    request = ReminderRequest(
        "Remind me to study Python tomorrow at 6 PM",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = adapter.generate(request)

    assert result.status == "ready"
    assert result.title == "Study Python"
    assert result.date == "2026-11-23"
    assert result.time == "18:00"
    assert result.clarification is None
    assert client.calls == 1


def test_mocked_explicit_date_request_returns_ready_result():
    client = MockAIClient(
        '{"title":"Dentist appointment","date":"2026-12-04","time":"09:30",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        client,
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    request = ReminderRequest(
        "Create a reminder for my dentist appointment on 2026-12-04 at 09:30",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = adapter.generate(request)

    assert result.status == "ready"
    assert result.title == "Dentist appointment"
    assert result.date == "2026-12-04"
    assert result.time == "09:30"


def test_create_reminder_resolves_tomorrow_and_6_pm():
    request = ReminderRequest(
        "Remind me to study Python tomorrow at 6 PM",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = create_reminder(request)

    assert result.status == "ready"
    assert result.title == "Study Python"
    assert result.date == "2026-11-23"
    assert result.time == "18:00"
    assert result.clarification is None


def test_create_reminder_resolves_relative_minutes_without_machine_clock():
    request = ReminderRequest(
        "Remind me to call Mom in 30 minutes",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = create_reminder(request)

    assert result.status == "ready"
    assert result.title == "Call Mom"
    assert result.date == "2026-11-22"
    assert result.time == "15:00"


def test_create_reminder_does_not_assume_a_missing_date():
    request = ReminderRequest(
        "Remind me to submit the report at midnight",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = create_reminder(request)

    assert result.status == "needs_clarification"
    assert result.title == "Submit the report"
    assert result.date is None
    assert result.time == "00:00"


def test_ai_adapter_uses_local_clarification_for_temporal_uncertainties():
    client = MockAIClient(
        '{"title":"Fabricated","date":"2026-11-23","time":"18:00",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        client,
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    context = EvaluationContext(
        reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
        timezone="Asia/Kolkata",
    )
    cases = (
        (
            "Remind me to submit the report at midnight",
            "Submit the report",
            None,
            "00:00",
            ("date",),
        ),
        (
            "Remind me to buy groceries at 7 PM",
            "Buy groceries",
            None,
            "19:00",
            ("date",),
        ),
        (
            "Remind me to renew my passport on 2026-12-10",
            "Renew my passport",
            "2026-12-10",
            None,
            ("time",),
        ),
        (
            "Remind me to join the webinar at 6",
            "Join the webinar",
            None,
            None,
            ("6 AM", "6 PM"),
        ),
        (
            "Remind me to submit the form on 2026-11-23 at 6 PM, "
            "but make it 9 AM instead",
            "Submit the form",
            "2026-11-23",
            None,
            ("6 PM", "9 AM"),
        ),
    )

    for text, title, date, time, clarification_parts in cases:
        result = adapter.generate(ReminderRequest(text, context))

        assert result.status == "needs_clarification"
        assert result.title == title
        assert result.date == date
        assert result.time == time
        assert all(
            part.lower() in result.clarification.lower()
            for part in clarification_parts
        )

    assert client.calls == 0


def test_ai_adapter_clarifies_when_model_changes_explicit_date():
    client = MockAIClient(
        '{"title":"Submit the report","date":"2026-12-11","time":"09:30",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        client,
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    request = ReminderRequest(
        "Remind me to submit the report on 2026-12-10 at 09:30",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = adapter.generate(request)

    assert result.status == "needs_clarification"
    assert result.title == "Submit the report"
    assert result.date == "2026-12-10"
    assert result.time == "09:30"
    assert "date" in result.clarification.lower()


def test_ai_adapter_clarifies_when_model_changes_explicit_time():
    client = MockAIClient(
        '{"title":"Submit the report","date":"2026-12-10","time":"10:00",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        client,
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    request = ReminderRequest(
        "Remind me to submit the report on 2026-12-10 at 9 AM",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = adapter.generate(request)

    assert result.status == "needs_clarification"
    assert result.title == "Submit the report"
    assert result.date == "2026-12-10"
    assert result.time == "09:00"
    assert "time" in result.clarification.lower()


def test_ai_adapter_clarifies_when_model_changes_explicit_title():
    client = MockAIClient(
        '{"title":"Drink water","date":"2026-11-23","time":"18:00",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        client,
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    request = ReminderRequest(
        "Remind me to study Python tomorrow at 6 PM",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = adapter.generate(request)

    assert result.status == "needs_clarification"
    assert result.title == "Study Python"
    assert result.date == "2026-11-23"
    assert result.time == "18:00"
    assert "title" in result.clarification.lower()


def test_ai_adapter_does_not_call_model_to_invent_missing_date_or_time():
    context = EvaluationContext(
        reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
        timezone="Asia/Kolkata",
    )
    responses = (
        (
            "Remind me to buy groceries at 7 PM",
            '{"title":"Buy groceries","date":"2026-11-23","time":"19:00",'
            '"status":"ready","clarification":null}',
            None,
            "19:00",
        ),
        (
            "Remind me to renew my passport on 2026-12-10",
            '{"title":"Renew my passport","date":"2026-12-10","time":"09:00",'
            '"status":"ready","clarification":null}',
            "2026-12-10",
            None,
        ),
    )

    for text, response, date, time in responses:
        client = MockAIClient(response)
        adapter = ProviderNeutralAIAdapter(
            client,
            AIAdapterConfig(provider="mock", model="test-model"),
        )

        result = adapter.generate(ReminderRequest(text, context))

        assert result.status == "needs_clarification"
        assert result.date == date
        assert result.time == time
        assert client.calls == 0


def test_ai_adapter_accepts_model_interpretation_for_nonstandard_complete_request():
    client = MockAIClient(
        '{"title":"Prepare the presentation","date":"2026-11-23","time":"18:00",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        client,
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    request = ReminderRequest(
        "I need a reminder because the presentation is tomorrow at 6 PM.",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = adapter.generate(request)

    assert result.status == "ready"
    assert result.title == "Prepare the presentation"
    assert result.date == "2026-11-23"
    assert result.time == "18:00"
    assert client.calls == 1


def test_malformed_alphanumeric_input_has_no_fabricated_title():
    client = MockAIClient(
        '{"title":"asdf123","date":"2026-11-23","time":"09:00",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        client,
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    request = ReminderRequest(
        "asdf123???",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = adapter.generate(request)

    assert result.status == "needs_clarification"
    assert result.title is None
    assert result.date is None
    assert result.time is None
    assert "reminder" in result.clarification.lower()
    assert client.calls == 0


def test_ai_adapter_does_not_accept_model_time_for_ambiguous_period():
    client = MockAIClient(
        '{"title":"Call Mom","date":"2026-11-23","time":"12:00",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        client,
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    request = ReminderRequest(
        "Remind me to call Mom tomorrow afternoon",
        EvaluationContext(
            reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
            timezone="Asia/Kolkata",
        ),
    )

    result = adapter.generate(request)

    assert result.status == "needs_clarification"
    assert result.title == "Call Mom"
    assert result.date == "2026-11-23"
    assert result.time is None
    assert client.calls == 0
