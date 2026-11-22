# Part 1A — Deterministic Todo REST API Validation Log

## 1. Project and validation approach

The Todo REST API was developed using Spec-Driven Development. The project artifacts include the
[feature specification](../specs/001-todo-rest-api/spec.md), [data model](../specs/001-todo-rest-api/data-model.md),
[OpenAPI contract](../specs/001-todo-rest-api/contracts/openapi.yaml), [implementation plan](../specs/001-todo-rest-api/plan.md),
[task list](../specs/001-todo-rest-api/tasks.md), and implementation under `app/`.

Validation uses an independent black-box HTTP harness. It talks to the running API through HTTP and
does not import the application implementation or its dependencies; see the [harness instructions](../harness/README.md).
The validation gates are application and contract tests, the independent harness, Ruff lint,
Ruff formatting, and Bandit SAST.

## 2. Initial validation and defect discovery

**Retrospective result:** the initial harness run was 24 passed, 4 failed, and 1 skipped. Its output
was not saved contemporaneously; this result is reconstructed from the development conversation.
No original initial-run log is available.

The four failures exposed these defects:

1. POST did not trim surrounding whitespace from a title.
2. POST did not reject a title containing only whitespace.
3. POST accepted the string `"false"` for `completed` instead of requiring a JSON boolean.
4. PATCH accepted the string `"false"` for `completed` instead of requiring a JSON boolean.

## 3. Defect repair

The implementation was updated to normalize titles by stripping whitespace and to reject titles that
are empty after normalization. `CreateTodo.completed` and `UpdateTodo.completed` use Pydantic
`StrictBool`, preventing string coercion for completion values.

Regression coverage was added to the contract tests in
[`tests/contract/test_todos_contract.py`](../tests/contract/test_todos_contract.py): tests cover title
trimming, whitespace-only rejection, and rejecting string completion values on both POST and PATCH.

## 4. Final verification results

### Application and contract tests

Reported final aggregate: **15 passed, 0 skipped, 0 failures**, with **one non-blocking
Starlette/httpx deprecation warning**.

Evidence note: the retained `app-contract-run.txt` and `app-contract-tests.txt` each record a
5-passed run with the deprecation warning. Neither file is a consolidated transcript of the
15-test aggregate.

### Independent black-box harness

The final verification record reports **28 passed, 1 skipped in 1.28 seconds**. The skipped test is
`test_todo_survives_manually_managed_api_restart`; it requires `TODO_PERSISTENCE_PHASE` to be set for
the two-phase manual-restart check. The companion `final-harness-run.txt` records the same pass/skip
counts in 1.41 seconds.

### Ruff

- `ruff check .` — **All checks passed.**
- `ruff format --check harness/tests` — **8 files already formatted.**

## 5. SAST

The initial broad Bandit scan included third-party packages in `harness/.venv`. Its retained reports
record **15 High, 39 Medium, and 823 Low** findings. All High and Medium findings in the broad text
report are located in third-party files under `harness/.venv/Lib/site-packages`, not project source.
The broad reports were retained as evidence.

A scoped scan excluded `harness/.venv` and scanned **549 lines of code**. It reported **0 High,
0 Medium, and 67 Low** findings. All 67 Low findings are B101 (`assert_used`) in test code. These
pytest assertions were reviewed and accepted; the known caveat is that Python optimization can
remove `assert` statements.

## 6. Evidence inventory

Existing files under `evidence/harness-results/`:

- `app-contract-run.txt`
- `app-contract-tests.txt`
- `bandit-report.json`
- `bandit-report.txt`
- `bandit-scoped-report.txt`
- `final-harness-run.txt`
- `final-harness-verification.txt`
- `final-ruff-check.txt`

The initial defect output is retrospective; it is not an original saved log.

## 7. Limitations

- The persistence-across-manual-restart harness test remains skipped because the two-phase
  `TODO_PERSISTENCE_PHASE` configuration was not completed.
- The application and contract test run produced one non-blocking deprecation warning.
- The scoped Bandit scan has 67 accepted Low B101 findings, with the optimization caveat described
  above.

## 8. Final human review

- [ ] Specification and implementation reviewed.
- [ ] Test evidence reviewed.
- [ ] Harness findings and fixes reviewed.
- [ ] SAST findings reviewed.
- [ ] Limitations acknowledged.

**Final decision:** UNDECIDED — a human reviewer must select **ACCEPT** or **REJECT**.
