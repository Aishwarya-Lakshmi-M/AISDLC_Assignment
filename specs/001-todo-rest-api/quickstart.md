# Quickstart Validation: Todo REST API

## Purpose

This guide validates the Todo REST API end-to-end after implementation. It contains expected user-visible
outcomes but does not depend on implementation source details.

## Prerequisites

- Python 3.11 or newer.
- Project dependencies installed.
- A test-local JSON persistence location, separate from any developer or production data.

## Install Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn pydantic pytest httpx ruff bandit
```

## Run Automated Tests

```powershell
pytest
ruff check .
ruff format --check .
bandit -r .
```

All commands must pass before the feature is complete. Bandit findings that indicate exploitable or unsafe
behavior must be resolved; approved gate exceptions require a documented and time-bound change record.

## Start the API

```powershell
uvicorn app.main:app --reload
```

Open the API documentation at `http://127.0.0.1:8000/docs` and verify that create, list, retrieve, update,
and delete operations are available.

## Validate Primary Flows

1. **Create**: Submit a task with a non-empty title and optional description. Confirm a success response
   contains an opaque identity, completion state, and persisted task fields.
2. **List**: Request the task collection. Confirm the created task appears once and an empty collection
   is represented by an empty list.
3. **Retrieve**: Request the created task by identity. Confirm its details match the created or updated task.
4. **Update**: Change the title and completion state in one valid update. Confirm the updated values are
   returned.
5. **Delete**: Delete the task, then retrieve it again. Confirm a stable not-found response.

## Validate Error Behavior

- Submit an empty or malformed title and confirm a validation error without internal details.
- Submit malformed JSON and confirm a safe validation response.
- Request an unknown task identity and confirm a consistent not-found response.
- Repeat create, update, and delete contracts for unknown resources and invalid payloads.

## Validate Persistence

- Create a task.
- Restart the API.
- Retrieve the task again and confirm the details and identity remain available.
- Run persistence failure tests with a test-only data location and confirm malformed or unavailable storage
  does not claim that a failed write succeeded.

## Success Outcomes

The feature is ready when every primary flow, validation case, persistence restart check, HTTP contract
check, pytest test, Ruff check, formatting check, and Bandit check has passed according to the constitution.
