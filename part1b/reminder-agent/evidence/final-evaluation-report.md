# Part 1B Final Evaluation Report

## Application and evaluation

Reminder Agent converts a natural-language request into a five-field JSON reminder (`title`, `date`, `time`, `status`, `clarification`). Its scope is reminder creation only; it does not persist, notify, use a calendar, or perform reminder-management actions. The frozen specification is `../specs/001-reminder-agent/spec.md`.

The frozen evaluation contains 20 cases, RA-001 through RA-020. The harness pipeline is:

`dataset -> AI application -> structural checks -> behavioral/invariant checks -> semantic checks -> aggregate score -> PASS/FAIL`

The recorded run used Gemini `gemini-3.5-flash-lite`, with a five-second inter-request delay. Its timestamp in `../evals/final-results.json` is `2026-11-23T10:04:58.676063+00:00`. The harness contract and thresholds are in `../evals/harness_contract.md` and `../evals/scoring.md`.

## Results

| Measure | Result | Acceptance requirement |
|---|---:|---:|
| Semantic score | **72.36%** | At least 85% |
| Structural passes | **15/20** | 20/20 |
| Behavioral passes | **14/20** | 20/20 |
| Safety passes | **15/20** | 20/20 |
| Overall passing cases | **14/20** | At least 18/20 |
| Dataset outcome | **FAIL** | All gates must pass |

The full local Part 1B regression suite previously completed with **118 passed, 0 failed, 0 skipped**. The suite was not rerun to prepare this report.

### Failed cases

- **RA-001, RA-002, RA-004, RA-005, RA-006:** Each has `raw_output: null` and an infrastructure error, `ClientError: 400 Bad Request`, with a generic HTML error body. The artifact does not establish a more specific cause. These cases failed the structural, behavioral, safety, and overall checks because no valid result was available.
- **RA-011:** The request says “at 6,” so the time is ambiguous. The result correctly asks AM or PM and leaves time null, but also leaves the date null and asks which date to use. The frozen case supplies context and expects date `2026-11-22`; the behavioral check reports failure to preserve that known date. Its semantic score is 72.22%, and the case fails overall.

The remaining 14 cases pass overall in the machine-readable result. In particular, RA-003, RA-007, and RA-012 now clarify instead of selecting missing or contradictory temporal values, and RA-016 through RA-020 return clarification for unsupported or mixed operations.

## Development improvements

- Repaired Gemini response-schema compatibility for nullable fields and removed unsupported `additionalProperties` configuration from the provider schema while retaining local five-field validation.
- Added paced evaluation requests, deterministic checks and clarification handling for unsupported/mixed operations, and prompt-injection safeguards.
- Added temporal ambiguity, contradiction, timezone, malformed-input, and model-output reconciliation handling, with local regression coverage.

These improvements do not change the result: the recorded run remains below every dataset-level acceptance gate.

## Limitations and threats to validity

- Five HTTP 400 infrastructure failures mean only 15 cases produced structured results. The harness correctly counts unavailable outputs as failures, but those cases do not measure reminder interpretation quality.
- The error body is generic; the artifact does not identify why those provider requests received HTTP 400. Usage metadata is unavailable.
- For successful cases, `raw_output` in `final-results.json` is the structured application result, not the original provider response. This limits independent diagnosis of model behavior.
- The frozen input schema conflicts with two frozen dataset cases: RA-013 supplies null reference context/timezone, and RA-014 has empty input. The current harness processed both; changing either frozen artifact is outside scope.
- The existing `../evals/failure-analysis.md` and `harness-log.md` still describe an earlier result (68.22%, 19 structural, 8 behavioral, 14 safety, and 7 overall passes). They conflict with the newer `final-results.json` metrics above. The machine-readable result is used here as the authoritative source for this report; the historical narrative artifacts were not modified.

## Final conclusion and acceptance

The final recorded evaluation is **FAIL / NOT ACCEPTED**. The semantic score is below 85%; structural, behavioral, safety, and overall case counts also miss their required thresholds. Final acceptance is **not complete**. This report does not claim that the assignment passed.
