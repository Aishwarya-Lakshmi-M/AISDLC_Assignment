# Tasks: Reminder Agent

**Input**: Design documents from `/specs/001-reminder-agent/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/, quickstart.md

**Tests**: Unit tests use mocked AI responses. The actual evaluation uses one configurable,
cost-conscious AI provider/model.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files and no incomplete-task dependency)
- **[Story]**: Maps to a user story from spec.md
- Every task includes an exact file path

## Phase 1: Evaluation Design (Before Implementation)

**Purpose**: Freeze the dataset, scoring method, thresholds, guardrails, and single evaluation pipeline
before application implementation begins.

- [ ] T001 Create the evaluation directory and at least 15 separate cases in `evals/dataset.json`,
  covering normal, boundary, ambiguous, underspecified, malformed, and adversarial requests
- [ ] T002 [P] Include reference datetime, timezone, expected status, expected fields, and category metadata
  for every case in `evals/dataset.json`; keep unit-test fixtures separate
- [ ] T003 [P] Define structural validation criteria for exactly five fields, allowed types and statuses,
  date/time formats, null clarification for ready results, and required clarification text for
  `needs_clarification` in `evals/scoring.md`
- [ ] T004 [P] Define behavioral invariants and property checks for no invention, explicit context use,
  clarification preservation, deterministic formats, unsupported operations, and stable five-field output
  in `evals/scoring.md`
- [ ] T005 [P] Define measurable semantic dimensions and point rules for title correctness, date correctness,
  time correctness, clarification quality, no-invention compliance, and scope compliance in
  `evals/scoring.md`
- [ ] T006 Predefine aggregate scoring weights and acceptance thresholds in `evals/scoring.md`, including
  structural pass threshold, overall semantic threshold, required safety threshold, and minimum PASS case
  count; mark all thresholds immutable after evaluation begins
- [ ] T007 [P] Define safety guardrails and unsupported-operation checks for listing, deleting, rescheduling,
  snoozing, notifications, calendar integration, persistence, prompt injection, and other out-of-scope
  requests in `evals/scoring.md`
- [ ] T008 Create the one pipeline contract:
  dataset -> AI application -> structural checks -> behavioral/invariant checks -> semantic checks ->
  aggregate score -> PASS/FAIL in `evals/harness_contract.md`
- [ ] T009 [P] Add initial evaluation schema validation tests for the dataset, immutable threshold configuration,
  and per-case expected data in `tests/harness/test_evaluation_design.py`

**Checkpoint**: Evaluation inputs and acceptance criteria are frozen before implementation.

---

## Phase 2: Setup (Shared Infrastructure)

**Purpose**: Initialize the beginner-friendly Python project and validation tooling.

- [ ] T010 Create the Python package and test directories described in
  `specs/001-reminder-agent/plan.md` under `src/reminder_agent/`, `src/harness/`, and `tests/`
- [ ] T011 [P] Add Python project metadata and pytest development dependencies in `pyproject.toml`
- [ ] T012 [P] Configure pytest discovery and test paths in `pyproject.toml`
- [ ] T013 [P] Create package exports and shared module initialization in
  `src/reminder_agent/__init__.py`

---

## Phase 3: Foundational (Blocking Prerequisites)

**Purpose**: Implement common input, result, validation, and provider-neutral interfaces.

**CRITICAL**: No user-story implementation can begin until this phase is complete.

- [x] T014 Create `EvaluationContext` with explicit `reference_datetime` and `timezone` fields from
  `data-model.md` `EvaluationContext.reference_datetime` and
  `data-model.md` `EvaluationContext.timezone` in `src/reminder_agent/context.py`
- [x] T015 [P] Create `ReminderRequest` fields `text` and `context` from
  `data-model.md` `ReminderRequest.text` and `data-model.md` `ReminderRequest.context` in
  `src/reminder_agent/context.py`
- [x] T016 [P] Create the shared five-field `ReminderResult` model with `title`, `date`, `time`, `status`,
  and `clarification` from `data-model.md` `ReminderResult.title`, `ReminderResult.date`,
  `ReminderResult.time`, `ReminderResult.status`, and `ReminderResult.clarification` in
  `src/reminder_agent/model.py`
- [x] T017 Implement five-field JSON and state validation using
  `specs/001-reminder-agent/contracts/reminder-result.schema.json` in
  `src/reminder_agent/validator.py`
- [x] T018 [P] Add mocked-AI unit tests for common result invariants in
  `tests/unit/test_foundation.py`
- [x] T019 Implement a provider-neutral AI adapter interface configurable by provider/model name and
  limit output to one result per request in `src/reminder_agent/parser.py`

**Checkpoint**: Shared context, output model, validator, and mocked unit-test foundation are ready.

---

## Phase 4: User Story 1 - Convert a Complete Reminder Request (Priority: P1) MVP

**Goal**: Convert complete natural-language requests into ready reminders.

**Independent Test**: Complete-request cases produce valid title, date, time, status, and null
clarification using the explicit evaluation context.

### Tests for User Story 1

- [x] T020 [P] [US1] Add failing contract tests for the result schema in
  `tests/contract/test_reminder_result.py`
- [x] T021 [P] [US1] Add mocked-AI unit tests for complete and relative-date requests in
  `tests/unit/test_complete_reminders.py`

### Implementation for User Story 1

- [x] T022 [US1] Implement complete-request interpretation and title/date/time extraction in
  `src/reminder_agent/parser.py`
- [x] T023 [US1] Resolve relative expressions only from `data-model.md`
  `EvaluationContext.reference_datetime` and `EvaluationContext.timezone` in
  `src/reminder_agent/context.py`
- [x] T024 [US1] Construct ready results from `data-model.md` `ReminderResult.title`,
  `ReminderResult.date`, `ReminderResult.time`, `ReminderResult.status`, and
  `ReminderResult.clarification` in `src/reminder_agent/model.py`
- [x] T025 [US1] Reject invented or malformed ready values in `src/reminder_agent/validator.py`
- [x] T026 [US1] Expose one create-reminder application entry point in
  `src/reminder_agent/__init__.py`

**Checkpoint**: US1 independently converts complete requests to ready structured output.

---

## Phase 5: User Story 2 - Request Clarification Instead of Guessing (Priority: P2)

**Goal**: Preserve known values and request specific clarification for missing or ambiguous details.

**Independent Test**: Missing, contradictory, and ambiguous cases return `needs_clarification`, null
unknown fields, and relevant clarification text.

### Tests for User Story 2

- [x] T027 [P] [US2] Add mocked-AI unit tests for missing title, date, and time fields in
  `tests/unit/test_missing_fields.py`
- [x] T028 [P] [US2] Add semantic tests for ambiguous expressions and contradictory date/time values in
  `tests/semantic/test_ambiguity.py`

### Implementation for User Story 2

- [x] T029 [US2] Implement missing-field detection and preserve known `data-model.md`
  `ReminderResult.title`, `ReminderResult.date`, and `ReminderResult.time` values in
  `src/reminder_agent/parser.py`
- [x] T030 [US2] Implement ambiguity detection using `data-model.md` `ReminderResult.status` and
  `ReminderResult.clarification` in `src/reminder_agent/parser.py`
- [x] T031 [US2] Return `needs_clarification` with null unknown fields when
  `EvaluationContext.reference_datetime` or `EvaluationContext.timezone` is absent in
  `src/reminder_agent/context.py`
- [x] T032 [US2] Construct actionable clarification questions using `data-model.md`
  `ReminderResult.clarification` and reject arbitrary defaults in `src/reminder_agent/model.py`
- [x] T033 [US2] Validate clarification status and null unknown fields in
  `src/reminder_agent/validator.py`

**Checkpoint**: US1 and US2 independently work; no ambiguous or missing context becomes ready.

---

## Phase 6: User Story 3 - Reject Unsupported Reminder Operations (Priority: P3)

**Goal**: Route unsupported operations through `needs_clarification` without claims or side effects.

**Independent Test**: Listing, deleting, rescheduling, snoozing, notification, calendar, persistence,
and prompt-injection cases never return ready.

### Tests for User Story 3

- [x] T034 [P] [US3] Add mocked-AI scope tests for rescheduling, snoozing, notification, calendar, and
  persistence requests in `tests/semantic/test_unsupported_operations.py`
- [x] T035 [P] [US3] Add contract tests ensuring unsupported operations use
  `needs_clarification` and non-empty `data-model.md` `ReminderResult.clarification` in
  `tests/contract/test_unsupported_contract.py`

### Implementation for User Story 3

- [x] T036 [US3] Detect unsupported reminder operations in `src/reminder_agent/parser.py`
- [x] T037 [US3] Construct clear unsupported-operation explanations in `data-model.md`
  `ReminderResult.clarification` while preserving known `ReminderResult.title`,
  `ReminderResult.date`, and `ReminderResult.time` fields in `src/reminder_agent/model.py`
- [x] T038 [US3] Enforce `data-model.md` `ReminderResult.status` with value `needs_clarification`
  and prevent out-of-scope side effects in
  `src/reminder_agent/validator.py`

**Checkpoint**: All three user stories are independent and unsupported operations never become ready.

---

## Phase 7: Single Evaluation Harness and Evidence

**Purpose**: Run one cost-conscious, reproducible evaluation pipeline and record initial/final evidence.

- [x] T039 Implement one configurable AI-provider/model evaluation runner and
  `dataset -> AI application -> structural checks -> behavioral/invariant checks -> semantic checks ->
  aggregate score -> PASS/FAIL` pipeline in `src/harness/evaluation.py`
- [x] T040 [P] Add harness tests for the frozen rubric, per-layer reports, aggregate score, and PASS/FAIL
  decision in `tests/harness/test_evaluation.py`
- [x] T041 Perform an initial evaluation run against `evals/dataset.json`, record genuine results, and save
  machine-readable output in `evals/initial-results.json`
- [x] T042 Conduct genuine failure analysis from T041, classify causes and evidence, and record findings
  in `evals/failure-analysis.md`
- [x] T043 Implement repairs only for failures established by T042 in the relevant
  `src/reminder_agent/` source files
- [x] T044 Run unit and contract tests after repairs in `tests/`
- [ ] T045 Perform the final evaluation run using the unchanged rubric and threshold configuration,
  then save machine-readable final results in `evals/final-results.json`
- [ ] T046 Create `evals/evaluation-log.json` containing model/provider/configuration, frozen threshold,
  per-layer results, failures, repairs, limitations, initial/final run metadata, and a human
  `ACCEPT` or `REJECT` decision field
- [x] T047 [P] Document setup and cost-conscious provider/model run commands in `README.md`
- [ ] T048 Record any residual limitations and the human decision rationale in
  `evals/evaluation-log.json`
- [ ] T049 Run `specs/001-reminder-agent/quickstart.md` validation commands and the full pytest suite
- [ ] T050 Review source and tests to confirm no database, notification, calendar, rescheduling,
  snoozing, listing, deleting, or persistence implementation exists

**Checkpoint**: Evidence is complete, final results are machine-readable, and the human decision is recorded.

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 evaluation design is completed and frozen before application implementation.
- Phase 2 setup has no dependencies beyond Phase 1.
- Phase 3 foundation depends on Phase 2 and blocks all user stories.
- Phases 4-6 depend on Phase 3 and may proceed sequentially or in parallel.
- Phase 7 depends on all selected user stories and follows the initial-run/repair/final-run sequence.

### User Story Dependencies

- US1: independent after the foundation.
- US2: independent after the foundation; it reuses only shared models and validation.
- US3: independent after the foundation; it reuses only shared models and validation.

### Parallel Opportunities

- T002-T005 can run in parallel after the dataset skeleton exists.
- T011-T013 can run in parallel in setup.
- T015-T016 and T018 can run in parallel in the foundation.
- US1, US2, and US3 test tasks can run in parallel within their own user-story phases.
- T040 and T047-T048 can run in parallel after the harness and implementation stabilize.

## Parallel Example: User Story 1

```text
T020 Contract tests in tests/contract/test_reminder_result.py
T021 Mocked-AI unit tests in tests/unit/test_complete_reminders.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Freeze evaluation design and threshold in Phase 1.
2. Complete setup and foundational phases.
3. Complete US1 and stop to verify its independent tests.
4. Add US2 and US3 only after the MVP works.

### Incremental Delivery

1. Dataset and rubric first.
2. Setup and shared foundation.
3. Add US1, then US2, then US3.
4. Run the initial evaluation, repair genuine failures, and perform the final evaluation.

### Parallel Team Strategy

1. One person or group completes evaluation design and frozen criteria.
2. Complete setup and foundation together.
3. Assign US1, US2, and US3 independently after the foundation.
4. Complete the shared harness evidence phase only after story implementation.

## Notes

- [P] tasks use different files or no dependency on incomplete tasks.
- [Story] labels map tasks to the priority-ordered user stories.
- Unit tests use mocked AI responses; actual evaluation calls a configurable provider/model and is
  cost-conscious.
- Thresholds in `evals/scoring.md` must not change after T041 begins.
