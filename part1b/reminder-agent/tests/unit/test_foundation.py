from datetime import datetime

import pytest

from src.reminder_agent import (
    AIAdapterConfig,
    EvaluationContext,
    ProviderNeutralAIAdapter,
    ReminderRequest,
    ReminderResult,
    parse_and_validate_result,
    validate_result,
)


class MockAIClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0
        self.provider = ""
        self.model = ""

    def complete(self, prompt: str, *, provider: str, model: str) -> str:
        self.calls += 1
        self.provider = provider
        self.model = model
        assert "reference_datetime=" in prompt
        assert "timezone=" in prompt
        return self.response


def test_evaluation_context_requires_supplied_values_but_allows_missing_context():
    context = EvaluationContext(
        reference_datetime=datetime.fromisoformat("2026-11-22T14:30:00+05:30"),
        timezone="Asia/Kolkata",
    )
    request = ReminderRequest("Remind me tomorrow", context)

    assert request.context is context
    assert request.context.reference_datetime.isoformat() == "2026-11-22T14:30:00+05:30"
    assert request.context.timezone == "Asia/Kolkata"


def test_ready_result_contract():
    result = validate_result(
        {
            "title": "Study Python",
            "date": "2026-11-23",
            "time": "18:00",
            "status": "ready",
            "clarification": None,
        }
    )

    assert result.to_dict() == {
        "title": "Study Python",
        "date": "2026-11-23",
        "time": "18:00",
        "status": "ready",
        "clarification": None,
    }


def test_clarification_result_preserves_known_fields():
    result = parse_and_validate_result(
        '{"title":"Buy groceries","date":null,"time":"19:00",'
        '"status":"needs_clarification","clarification":"Which date should I use?"}'
    )

    assert result.title == "Buy groceries"
    assert result.date is None
    assert result.time == "19:00"


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (
            {"title": "Study", "date": None, "time": "18:00", "status": "ready", "clarification": None},
            "ready",
        ),
        (
            {"title": "Study", "date": "2026-11-23", "time": "18:00", "status": "needs_clarification", "clarification": None},
            "clarification",
        ),
        (
            {"title": "Study", "date": "2026-02-30", "time": "18:00", "status": "ready", "clarification": None},
            "date",
        ),
        (
            {"title": "Study", "date": "2026-11-23", "time": "25:00", "status": "ready", "clarification": None},
            "time",
        ),
    ],
)
def test_invalid_result_states_are_rejected(payload, message):
    with pytest.raises(ValueError, match=message):
        validate_result(payload)


def test_extra_json_fields_are_rejected():
    with pytest.raises(ValueError, match="exactly five"):
        validate_result(
            {
                "title": "Study",
                "date": "2026-11-23",
                "time": "18:00",
                "status": "ready",
                "clarification": None,
                "extra": "not allowed",
            }
        )


def test_provider_adapter_makes_one_mocked_call_and_returns_one_result():
    mock = MockAIClient(
        '{"title":"Study Python","date":"2026-11-23","time":"18:00",'
        '"status":"ready","clarification":null}'
    )
    adapter = ProviderNeutralAIAdapter(
        mock,
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

    assert isinstance(result, ReminderResult)
    assert mock.calls == 1
    assert mock.provider == "mock"
    assert mock.model == "test-model"


@pytest.mark.parametrize(
    "raw_output",
    [
        "```json\n"
        '{"title":"Study Python","date":"2026-11-23","time":"18:00",'
        '"status":"ready","clarification":null}\n```',
        '{"title":"Study Python","date":"2026-11-23","time":"18:00",'
        '"status":"confirmed","clarification":null}',
        '{"title":"Study Python","date":"2026-11-23","time":"18:00:00",'
        '"status":"ready","clarification":null}',
    ],
)
def test_gemini_output_regressions_remain_structurally_invalid(raw_output):
    with pytest.raises(ValueError):
        parse_and_validate_result(raw_output)


def test_gemini_response_schema_converts_in_google_genai_sdk():
    pytest.importorskip("google.genai")
    from google.genai._transformers import t_schema

    response_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["title", "date", "time", "status", "clarification"],
        "properties": {
            "title": {"type": "string", "nullable": True},
            "date": {"type": "string", "nullable": True},
            "time": {"type": "string", "nullable": True},
            "status": {
                "type": "string",
                "enum": ["ready", "needs_clarification"],
            },
            "clarification": {"type": "string", "nullable": True},
        },
    }

    converted = t_schema(None, response_schema)

    assert converted is not None
    assert set(converted.properties) == {
        "title",
        "date",
        "time",
        "status",
        "clarification",
    }
