# Part 1B Evaluation Harness Log

## Latest Genuine Evaluation

- **Run timestamp:** `2026-11-23T07:57:10.442935+00:00` (UTC); `2026-11-23 13:27:10.442935 +05:30`
- **Provider:** Gemini
- **Model:** `gemini-3.5-flash-lite`
- **Dataset:** 20 frozen cases (RA-001–RA-020)
- **Inter-request delay:** 5 seconds
- **Credential source:** `GEMINI_API_KEY` environment variable; no key is recorded here
- **Harness execution:** Completed and wrote `evals/final-results.json`
- **Outcome:** **FAIL**
- **Structural checks:** 19/20 passed
- **Behavioral checks:** 8/20 passed
- **Safety checks:** 14/20 passed
- **Overall passing cases:** 7/20
- **Semantic score:** 68.22%
- **Required semantic threshold:** 85%
- **Usage metadata:** Not available; the SDK did not expose it to the harness

The metrics above are recorded in the machine-generated `evals/final-results.json`. That file is preserved as the authoritative result evidence. No evaluation metrics were recalculated or changed for this log.

### Observed failures

- RA-003, RA-005, and RA-007 have date-resolution errors: an assumed date for midnight, the wrong “next Monday,” and a date filled in despite being absent.
- RA-011 and RA-012 select a time for an ambiguous or contradictory request instead of asking for clarification.
- RA-017, RA-018, and RA-020 return `ready` for notification/calendar, snooze, or mixed rescheduling requests.
- RA-016 and RA-019 fail unsupported-operation checks because their clarifications do not satisfy the evaluator’s unsupported-explanation requirement.
- RA-010 and RA-013 fail behavioral title-preservation checks despite 100% semantic scores; the title comparison differs in case.
- RA-008 has no validated output: the recorded error is `ValueError: A ready reminder must include a time`. No API quota error is recorded in this latest result.

See `evals/failure-analysis.md` for the case-by-case findings and pattern analysis.

## Human Assessment and Decision

- The evaluation run completed and its evidence was saved.
- The application **does not meet the acceptance criteria**: the outcome is FAIL, the semantic score is below 85%, and the structural, behavioral, safety, and per-case gates are false.
- **Human decision: FAIL / NOT ACCEPTED.**
- Final acceptance is not complete and must not be recorded as ACCEPT.

## Earlier Evaluation and Schema Compatibility History

- The initial T041 run used Gemini `gemini-3.5-flash-lite` on the 20-case dataset and recorded 16 JSON-contract failures plus 4 HTTP 429 quota errors. These remain historical results in `evals/initial-results.json`; they are not the metrics for the latest run.
- After that initial run, JSON output configuration and request pacing were added. The later T045 attempt then failed before model responses: all 20 cases recorded `AttributeError: 'list' object has no attribute 'upper'` during SDK schema conversion of nullable fields represented as `type: ["string", "null"]`.
- The nullable schema representation was repaired to use scalar `type: "string"` with `nullable: true`, and a local no-network SDK schema-conversion regression test was added. Focused local tests passed after the repair.
- A subsequent request reported `400 INVALID_ARGUMENT` because `additional_properties` reached Gemini in `response_schema`. The current adapter omits `additionalProperties` from that schema, while the local validator still enforces the exact five-field result contract. The latest artifact records no such API error.
- The latest final-results artifact contains 19 structured model outputs and one RA-008 validation exception. It does not record the earlier schema-conversion failure or the initial run’s quota errors.

No model evaluation was rerun to prepare this log. The dataset, scoring rules, thresholds, application source, and machine-generated evaluation results were not changed.
