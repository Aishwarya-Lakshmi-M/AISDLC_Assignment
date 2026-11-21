# Implementation Plan: Todo REST API

**Branch**: `001-todo-rest-api` | **Date**: 2026-11-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-todo-rest-api/spec.md`

## Summary

Build a scoped Todo REST API that creates, retrieves, updates, completes, and deletes tasks while
preserving data in local JSON storage. The implementation will use FastAPI route handlers, Pydantic
schemas, a focused task service/repository boundary, and HTTP tests that verify public behavior and
API contracts.

## Technical Context

**Language/Version**: Python 3.11 or newer

**Primary Dependencies**: FastAPI, Pydantic, pytest, HTTPX, Uvicorn, Ruff, Bandit

**Storage**: Local JSON file with atomic replacement or a recoverable staged-write strategy; unexpected
read/write failures return HTTP 500 with a consistent `storage_error` response

**Testing**: pytest unit, HTTP integration, and API contract tests

**Target Platform**: Local development server and test environment

**Project Type**: Single-project REST web service

**Performance Goals**: Small local collection; CRUD responses complete within the user-facing success
expectations in the specification

**Constraints**: No external database or authentication; JSON data must remain valid after failures;
consistent JSON errors; HTTP 500 for storage failures, HTTP 400 for malformed UUIDs, HTTP 404 for valid
unknown IDs, and no exposure of internal paths or exceptions

**Scale/Scope**: Core CRUD operations and task completion management for a single local or trusted client

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Gate                       | Status | Plan Response                                                                             |
| -------------------------- | ------ | ----------------------------------------------------------------------------------------- |
| Specification traceability | Pass   | Every API behavior maps to an FR or acceptance scenario in the spec.                      |
| Modular Python design      | Pass   | Routes, schemas, task behavior, and JSON persistence remain separate modules.             |
| Test-first delivery        | Pass   | Tests will be defined before implementation and include failure-first checks.             |
| REST consistency           | Pass   | Resource routes, HTTP methods, UUID validation, deterministic listing, and stable errors. |
| Integration and contracts  | Pass   | HTTP/API tests cover public routes, payloads, status codes, and error contracts.          |
| Secure persistence         | Pass   | Atomic writes, corruption handling, input constraints, and safe error responses.          |
| Scope control              | Pass   | No authentication, scheduling, collaboration, soft deletion, or speculative features.     |
| Automated quality gates    | Pass   | pytest, Ruff check/format, and Bandit are required before completion.                     |

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-rest-api/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── main.py
├── api/
│   └── todos.py
├── models/
│   └── todo.py
├── services/
│   └── todo_service.py
└── persistence/
    └── json_repository.py

tests/
├── unit/
├── contract/
└── integration/

data/
└── todos.json
```

**Structure Decision**: Use one FastAPI application package with small modules for routing, request and
response models, task behavior, and JSON persistence. The repository layout keeps HTTP concerns separate
from data behavior and allows focused unit and integration test boundaries.

## Post-Design Constitution Re-check

_GATE: Re-evaluation after research and Phase 1 design._

All constitution gates remain satisfied. The design includes explicit test-first and API contract coverage,
UUID malformed-ID HTTP 400 behavior, valid-ID HTTP 404 behavior, UTC timestamps, oldest-first/ID-tie listing,
modular Python boundaries, JSON atomic-write behavior, safe error contracts, and the required pytest, Ruff,
and Bandit quality gates. No complexity exception is required.

## Complexity Tracking

No constitution violations are planned. Repository abstraction and persistence module boundaries are
limited to the smallest design needed to isolate JSON behavior and testable task operations.
