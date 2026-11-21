# Tasks: Todo REST API

**Input**: Design documents from `/specs/001-todo-rest-api/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Runs independently of incomplete tasks in the same phase.
- **[Story]**: Maps work to US1, US2, or US3.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python project and shared tool configuration.

- [x] T001 Create the application package structure for `app/`, `app/api/`, `app/models/`, `app/services/`, `app/persistence/`, `tests/`, and `data/` per [plan.md](plan.md)
- [x] T002 Create `pyproject.toml` with FastAPI, Pydantic, pytest, HTTPX, Uvicorn, Ruff, and Bandit dependencies
- [x] T003 Create `app/__init__.py` and `app/api/__init__.py`, `app/models/__init__.py`, `app/services/__init__.py`, and `app/persistence/__init__.py`
- [x] T004 [P] Configure pytest paths and test settings in `pyproject.toml`
- [x] T005 [P] Configure Ruff lint and format settings in `pyproject.toml`
- [x] T006 [P] Configure Bandit scan settings in `pyproject.toml`
- [x] T007 Create the initial test-local JSON file layout in `data/todos.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared infrastructure that every user story depends on.

**CRITICAL**: No user story implementation begins until this phase completes.

- [x] T008 Create Pydantic request and response schemas for `TodoTask`, `CreateTodo`, `UpdateTodo`, and `Error` in `app/models/todo.py`, covering `TodoTask.id`, `TodoTask.title`, `TodoTask.description`, `TodoTask.completed`, `TodoTask.created_at`, `TodoTask.updated_at`, `Create Task Input.title`, `Create Task Input.description`, and `Create Task Input.completed` as defined in [data-model.md](data-model.md)
- [x] T009 Implement UUID task identity and UTC timestamp helpers for `TodoTask.id`, `TodoTask.created_at`, and `TodoTask.updated_at` in `app/models/todo.py`; ensure both timestamps are always present, `created_at` is immutable, and successful updates change `updated_at` as defined in [data-model.md](data-model.md)
- [x] T010 Implement the JSON repository interface and atomic staged-write behavior for `Persistence Representation` in `app/persistence/json_repository.py`
- [x] T011 Implement safe handling for missing, malformed, unreadable, and unavailable JSON storage in `app/persistence/json_repository.py`; map unexpected read/write failures to `storage_error` responses with HTTP 500
- [x] T012 Implement shared service exceptions for validation, not-found, and storage failures in `app/services/todo_service.py`
- [x] T013 Configure FastAPI application creation and route registration in `app/main.py`
- [x] T014 Add consistent HTTP exception handlers for validation, malformed-ID, not-found, and `storage_error` response contracts in `app/main.py`; unexpected persistence failures must return HTTP 500
- [x] T015 [P] Create pytest fixtures for a temporary JSON file and FastAPI test client in `tests/conftest.py`
- [x] T016 [P] Add unit coverage for repository read, write, malformed-data, and missing-file behavior in `tests/unit/test_json_repository.py`

**Checkpoint**: Shared models, persistence, API setup, and error handling are ready.

---

## Phase 3: User Story 1 - Create and Retrieve Todo Tasks (Priority: P1) MVP

**Goal**: Allow a client to create a task, retrieve it by ID, and list all tasks.

**Independent Test**: Create a valid task, retrieve it by identity, and confirm it appears in the list.

### Tests for User Story 1

> Write these tests first and confirm that they fail before implementation.

- [x] T017 [P] [US1] Add contract tests for `POST /todos`, `GET /todos`, and `GET /todos/{todoId}` in `tests/contract/test_todos_contract.py`, based on [contracts/openapi.yaml](contracts/openapi.yaml)
- [x] T018 [P] [US1] Add integration tests for create, list, retrieve, invalid create input, empty-list, malformed-ID HTTP 400, unknown-ID HTTP 404, UTC timestamps, deterministic oldest-first/ID-tie ordering, and storage HTTP 500 behavior in `tests/integration/test_todo_create_retrieve.py`
- [x] T019 [P] [US1] Add repository-backed unit tests for task creation and retrieval in `tests/unit/test_todo_create_retrieve.py`

### Implementation for User Story 1

- [x] T020 [US1] Implement create and retrieve operations in `app/services/todo_service.py`, satisfying `TodoTask.id`, `TodoTask.title`, `TodoTask.description`, `TodoTask.completed`, `TodoTask.created_at`, and `TodoTask.updated_at` constraints from [data-model.md](data-model.md), including UTC timestamps and immutable `created_at`
- [x] T021 [US1] Implement list-task behavior in `app/services/todo_service.py`, sorting ascending by `TodoTask.created_at` and using `TodoTask.id` as a tie-breaker as defined in [data-model.md](data-model.md)
- [x] T022 [US1] Implement create, list, and retrieve route handlers in `app/api/todos.py`
- [x] T023 [US1] Apply create payload validation for `Create Task Input.title` at exactly 1-200 characters, `Create Task Input.description` at exactly 0-2000 characters, and `Create Task Input.completed` in `app/api/todos.py` according to [data-model.md](data-model.md)
- [x] T024 [US1] Map create/list/retrieve outcomes to success, validation, malformed-ID HTTP 400, unknown-ID HTTP 404, and unexpected storage HTTP 500 responses in `app/api/todos.py`
- [x] T025 [US1] Verify that created and retrieved task payloads match `TodoTask` and the OpenAPI contract in `tests/contract/test_todos_contract.py`

**Checkpoint**: User Story 1 is independently usable: create, list, and retrieve work through HTTP.

---

## Phase 4: User Story 2 - Update Todo Tasks (Priority: P2)

**Goal**: Allow a client to change task fields or completion status.

**Independent Test**: Create a task, partially update it, and retrieve the updated values; verify unknown IDs fail consistently.

### Tests for User Story 2

- [x] T026 [P] [US2] Add contract tests for `PATCH /todos/{todoId}` in `tests/contract/test_todo_update_contract.py`
- [x] T027 [P] [US2] Add integration tests for partial title, description, and completion updates; empty-PATCH HTTP 422; malformed-ID HTTP 400; unknown-ID HTTP 404; immutable `created_at`; changed `updated_at`; and storage HTTP 500 in `tests/integration/test_todo_update.py`
- [x] T028 [P] [US2] Add unit tests for update state transitions and timestamp changes in `tests/unit/test_todo_update.py`

### Implementation for User Story 2

- [x] T029 [US2] Implement partial update behavior in `app/services/todo_service.py`, preserving `TodoTask.id` and `TodoTask.created_at` while generating a changed UTC `updated_at` as defined in [data-model.md](data-model.md)
- [x] T030 [US2] Apply update-field validation for `Update Task Input.title` at exactly 1-200 characters, `Update Task Input.description` at exactly 0-2000 characters, and `Update Task Input.completed` in `app/api/todos.py`; reject an empty PATCH body with HTTP 422 according to [data-model.md](data-model.md)
- [x] T031 [US2] Implement `PATCH /todos/{todoId}` in `app/api/todos.py`; return HTTP 422 for an empty update, HTTP 400 for malformed IDs, HTTP 404 for valid unknown IDs, and HTTP 500 for storage failures
- [x] T032 [US2] Verify active/completed state transitions preserve the `TodoTask.completed` contract in `tests/integration/test_todo_update.py`

**Checkpoint**: User Stories 1 and 2 work independently, and updates preserve task identity and stored state.

---

## Phase 5: User Story 3 - Delete Todo Tasks (Priority: P3)

**Goal**: Allow a client to remove an existing task and receive consistent absent-resource behavior.

**Independent Test**: Create a task, delete it, confirm `204`, and confirm later retrieval returns `404`.

### Tests for User Story 3

- [x] T033 [P] [US3] Add contract tests for `DELETE /todos/{todoId}` and post-delete retrieval in `tests/contract/test_todo_delete_contract.py`
- [x] T034 [P] [US3] Add integration tests for successful delete, repeated delete, malformed-ID HTTP 400, unknown-ID HTTP 404, and storage HTTP 500 behavior in `tests/integration/test_todo_delete.py`

### Implementation for User Story 3

- [x] T035 [US3] Implement deletion and unknown-ID behavior in `app/services/todo_service.py`
- [x] T036 [US3] Implement `DELETE /todos/{todoId}` in `app/api/todos.py` with `204` success, malformed-ID HTTP 400, unknown-ID HTTP 404, and storage HTTP 500 responses
- [x] T037 [US3] Verify deleted tasks no longer appear in list/retrieve operations and persist across application restart in `tests/integration/test_todo_delete.py`

**Checkpoint**: All three user stories are independently testable and the core Todo lifecycle is complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, quality gates, and final validation.

- [x] T038 [P] Add package command documentation and API startup instructions to `README.md`
- [x] T039 [P] Synchronize generated API documentation with `specs/001-todo-rest-api/contracts/openapi.yaml`
- [x] T040 [P] Add unit tests for title 200-character maximum, description 2000-character maximum, completion boundary values, malformed UUID IDs, UTC timestamps, and empty PATCH behavior in `tests/unit/test_todo_validation.py`, citing `TodoTask.title`, `TodoTask.description`, `TodoTask.completed`, `TodoTask.created_at`, `TodoTask.updated_at`, and `TodoTask.id` from [data-model.md](data-model.md)
- [x] T041 [P] Add persistence corruption, read failure, and atomic-write failure tests in `tests/unit/test_json_repository.py`, verifying the consistent `storage_error` HTTP 500 contract
- [x] T042 Run `pytest` and resolve any failing HTTP, contract, unit, or integration tests
- [x] T043 Run `ruff check .` and resolve lint violations
- [x] T044 Run `ruff format --check .` and resolve formatting drift
- [x] T045 Run `bandit -r .` and resolve unresolved high-severity security findings
- [x] T046 Execute end-to-end scenarios in `specs/001-todo-rest-api/quickstart.md` and record the outcomes
- [x] T047 Review implementation against every functional requirement in `specs/001-todo-rest-api/spec.md` and complete any requirement gaps

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately and establishes project files.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user-story work.
- **US1 (Phase 3)**: Depends on Foundational and provides the MVP.
- **US2 (Phase 4)**: Depends on Foundational; may integrate with US1 but remains independently testable.
- **US3 (Phase 5)**: Depends on Foundational; may integrate with US1 but remains independently testable.
- **Polish (Phase 6)**: Starts after the desired user stories pass their focused tests.

### User Story Dependencies

- **User Story 1**: No dependency on other user stories.
- **User Story 2**: Uses shared task models/repository but does not require US3.
- **User Story 3**: Uses shared task models/repository but does not require US2.

### Within Each User Story

- Contract and integration tests are written before implementation.
- Shared models and repository behavior precede story services.
- Service behavior precedes route handlers.
- Route behavior precedes final contract verification.

## Parallel Opportunities

- T004-T006 can run in parallel after `pyproject.toml` exists.
- T015-T016 can run in parallel after the foundational interfaces are defined.
- T017-T019 can run in parallel inside US1.
- T026-T028 can run in parallel inside US2.
- T033-T034 can run in parallel inside US3.
- T038-T041 can run in parallel during polish after implementation.
- Different user stories can proceed in parallel after Phase 2 by separate contributors.

## Parallel Example: User Story 1

```text
T017: Contract tests in tests/contract/test_todos_contract.py
T018: HTTP integration tests in tests/integration/test_todo_create_retrieve.py
T019: Repository/unit tests in tests/unit/test_todo_create_retrieve.py
```

## Parallel Example: User Story 2

```text
T026: Update contract tests in tests/contract/test_todo_update_contract.py
T027: Update integration tests in tests/integration/test_todo_update.py
T028: Update state/unit tests in tests/unit/test_todo_update.py
```

## Parallel Example: User Story 3

```text
T033: Delete contract tests in tests/contract/test_todo_delete_contract.py
T034: Delete integration tests in tests/integration/test_todo_delete.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational infrastructure.
3. Complete US1 tests and implementation.
4. Stop and validate US1 independently with pytest and HTTP test scenarios.
5. Only then add US2 and US3 unless parallel execution is explicitly staffed.

### Incremental Delivery

1. Deliver create/list/retrieve in US1.
2. Add update behavior in US2.
3. Add delete behavior in US3.
4. Finish cross-cutting documentation and quality gates in polish.
