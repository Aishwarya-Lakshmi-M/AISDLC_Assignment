from src.harness.evaluation import (
    EvaluationRunner,
    HarnessConfig,
    behavioral_check,
    safety_check,
    structural_check,
)
from src.reminder_agent import (
    AIAdapterConfig,
    EvaluationContext,
    ProviderNeutralAIAdapter,
    ReminderRequest,
    ReminderResult,
)


def test_structural_check_accepts_ready_and_rejects_extra_keys():
    ready = {
        "title": "Study Python",
        "date": "2026-11-23",
        "time": "18:00",
        "status": "ready",
        "clarification": None,
    }
    extra = dict(ready)
    extra["extra"] = "not allowed"

    assert structural_check(ready)["pass"] is True
    assert structural_check(extra)["pass"] is False


def test_behavioral_check_rejects_ready_for_missing_date():
    case = {
        "category": "missing_date",
        "expected_status": "needs_clarification",
        "expected_title": "Buy groceries",
        "expected_date": None,
        "expected_time": "19:00",
    }
    output = {
        "title": "Buy groceries",
        "date": "2026-11-22",
        "time": "19:00",
        "status": "ready",
        "clarification": None,
    }

    result = behavioral_check(case, output)
    assert result["pass"] is False
    assert "clarification status invariant" in result["failures"]


def test_safety_check_rejects_supported_portion_marked_ready_in_mixed_request():
    case = {
        "category": "combined_supported_unsupported",
        "reference_datetime": "2026-11-22T14:30:00+05:30",
        "timezone": "Asia/Kolkata",
    }
    output = {
        "title": "Call Alex",
        "date": "2026-11-23",
        "time": "16:00",
        "status": "ready",
        "clarification": None,
    }

    result = safety_check(case, output)
    assert result["pass"] is False


def test_evaluation_runner_reports_per_case_layers_and_frozen_pass():
    def application(request):
        return ReminderResult(
            title=None,
            date=None,
            time=None,
            status="needs_clarification",
            clarification="Please provide the missing reminder detail.",
        )

    report = EvaluationRunner(
        application=application,
        config=HarnessConfig(provider="mock", model="test-model"),
    ).run()

    assert report["case_count"] == 20
    assert len(report["per_case"]) == 20
    assert report["counts"]["structural_pass"] == 20
    assert report["outcome"] in ("PASS", "FAIL")
    assert set(report["per_case"][0]) >= {
        "case_id",
        "raw_output",
        "structural",
        "behavioral",
        "safety",
        "semantic",
        "overall_pass",
    }


def test_harness_config_supports_free_tier_pacing():
    from src.harness.evaluation import HarnessConfig

    config = HarnessConfig(provider="gemini", model="gemini-3.5-flash-lite", inter_request_delay_seconds=5)
    assert config.inter_request_delay_seconds == 5


def test_harness_records_invalid_model_output_and_continues():
    raw_output = (
        '{"title":"Study Python","date":"2026-11-23","time":null,'
        '"status":"ready","clarification":null}'
    )

    class IncompleteResponseClient:
        def complete(self, prompt: str, *, provider: str, model: str) -> str:
            return raw_output

    adapter = ProviderNeutralAIAdapter(
        IncompleteResponseClient(),
        AIAdapterConfig(provider="mock", model="test-model"),
    )
    report = EvaluationRunner(
        application=adapter.generate,
        config=HarnessConfig(provider="mock", model="test-model"),
    ).run()

    first_case = report["per_case"][0]
    assert report["case_count"] == 20
    assert len(report["per_case"]) == 20
    assert first_case["raw_output"] is None
    assert "A ready reminder must include a time" in first_case["infrastructure_error"]
    assert raw_output in first_case["infrastructure_error"]
    assert report["per_case"][-1]["case_id"] == "RA-020"
