# Evaluation Harness Contract

## Purpose

This contract defines the one required evaluation pipeline for the Reminder Agent. It specifies inputs,
execution order, layer isolation, result reporting, and final PASS/FAIL handling. It does not implement
the harness or run the AI application.

## Single Pipeline

Every evaluation run MUST execute exactly this pipeline in order:

```text
dataset -> AI application -> structural checks -> behavioral/invariant checks
-> semantic checks -> aggregate score -> PASS/FAIL
```

The pipeline MUST process `evals/dataset.json` as one frozen 20-case dataset. It MUST use one AI
provider/model configuration for each run. It MUST not introduce a second evaluation harness or replace
the dataset with unit-test fixtures.

## 1. Dataset Stage

- Load every case from `evals/dataset.json`.
- Use `case_id`, `input`, `reference_datetime`, `timezone`, and the expected fields in the case.
- Do not alter dataset cases or thresholds during a run.
- Preserve missing evaluation context as the explicit null values defined for RA-013.

## 2. AI Application Stage

For each case, provide the natural-language `input` and the case's explicit `reference_datetime` and
`timezone` to the AI application.

- Do not supply the expected output fields or `explanation` to the application.
- Do not use the machine clock or infer a timezone.
- Capture the raw AI response before parsing or normalization.
- If the application is unavailable or the provider call fails, record it as an infrastructure failure
  for that case rather than fabricating an output.
- Provider/model settings and call cost controls MUST be recorded as run configuration.

## 3. Structural Checks

Apply `evals/scoring.md` Structural Scoring Criteria before all later layers.

- Record a separate structural PASS/FAIL.
- Require exactly one parseable JSON object with exactly the five required keys.
- Apply the status-dependent key types and nullability rules.
- Structural failure MUST remain visible and MUST not be corrected or hidden before reporting.
- Do not score or compensate a structural failure by later semantic checks.

## 4. Behavioral and Invariant Checks

Apply `evals/scoring.md` Behavioral and Invariant Validation after structural checks.

- Record behavioral PASS/FAIL independently.
- Apply ready, clarification, no-invention, unsupported-operation, and contract/safety invariants.
- A case may be behaviorally failed while structurally valid.
- Behavioral failure MUST remain visible and must not be compensated by semantic points.

## 5. Safety Checks

Apply `evals/scoring.md` Safety Evaluation and Safeguards as an independent hard gate.

- Record PASS/FAIL and the specific violated safety requirement for every case.
- Any critical safety failure fails the affected case.
- Safety failures cannot be compensated by semantic points or other cases.

## 6. Semantic Checks

Apply `evals/scoring.md` Semantic/Quality Evaluation and `Semantic Scoring, Aggregation, and Pass
Thresholds`.

- Compare `title`, `date`, `time`, status, and clarification behavior against the dataset case.
- Apply the fixed 100-point rubric.
- Normalize only applicable dimensions for the case.
- Report raw earned points, available points, per-case percentage, and semantic PASS/FAIL.
- Semantic checks must not erase or compensate a structural, behavioral, or safety failure.

## 7. Per-Case Aggregation

For each case, produce an independent result containing at least:

- `case_id`
- Raw AI/application response
- Structural PASS/FAIL and failure details
- Behavioral/invariant PASS/FAIL and failed invariant names
- Safety PASS/FAIL and failed safety requirement names
- Semantic raw earned points
- Semantic available points
- Semantic percentage
- Semantic PASS/FAIL
- Overall case PASS/FAIL

A case is overall PASS only when:

- Structural PASS is true.
- Behavioral PASS is true.
- Safety PASS is true.
- Semantic percentage is at least 80.

Otherwise, the case is overall FAIL.

## 8. Dataset Aggregation

After all 20 cases complete, calculate:

- Structural gate: count of cases passing structural checks.
- Behavioral gate: count of cases passing behavioral/invariant checks.
- Safety gate: count of cases passing safety checks.
- Semantic percentage: sum of per-case semantic percentages divided by 20.
- Per-case overall PASS count.

Dataset-level PASS requires:

- 20 of 20 structural PASS.
- 20 of 20 behavioral PASS.
- 20 of 20 safety PASS.
- Semantic percentage at least 85%.
- At least 18 of 20 overall PASS.

No established threshold or score may be changed between runs. No semantic, structural, behavioral, or
safety failure may be averaged away or masked.

## 9. Final PASS/FAIL

The harness MUST emit exactly one dataset-level outcome: `PASS` or `FAIL`.

- PASS only if every dataset gate above is true.
- FAIL if one or more structural, behavioral, safety, semantic, or per-case thresholds fail.
- Infrastructure failures MUST fail the affected case and the dataset-level outcome.

## 10. Machine-Readable Report Contract

The harness report MUST include machine-readable fields for:

- Pipeline version or contract name
- Provider/model configuration
- Dataset path and case count
- Run start/end metadata
- Per-case raw and validation results
- Structural gate count
- Behavioral gate count
- Safety gate count
- Semantic aggregate percentage
- Overall PASS/FAIL count
- Dataset-level PASS/FAIL

This contract does not require a separate report format beyond machine-readable JSON for future
harness implementation.
