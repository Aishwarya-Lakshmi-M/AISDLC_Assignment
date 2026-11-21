# Phase 0 Research: Todo REST API

## Decision: Use a modular FastAPI application

**Decision**: Implement the public HTTP API with FastAPI and separate route, schema, service, and JSON
repository modules.

**Rationale**: This matches the constitution's maintainability and modularity requirements while
keeping the implementation appropriate for a small local service. It also provides Pydantic validation
and API documentation from the public route contract.

**Alternatives considered**:

- Flask: Rejected because FastAPI/Pydantic provide stronger typed request validation and API contracts.
- A framework-free HTTP service: Rejected because it would duplicate routing and validation concerns.

## Decision: Use local JSON persistence

**Decision**: Persist Todo tasks in one local JSON file using an atomic staged-write strategy.

**Rationale**: The assignment requires JSON-based local storage. Atomic replacement minimizes partial-file
corruption; malformed existing data is handled as a storage error rather than silently overwritten.

**Alternatives considered**:

- External database: Rejected because it is outside the feature scope.
- Direct in-place JSON writes: Rejected because interrupted writes may leave malformed JSON.
- Automatic recovery that discards corrupted data: Rejected because it may destroy confirmed task data.

## Decision: Use Pydantic boundary validation

**Decision**: Validate title, description, identity, and completion fields at the API boundary, with
consistent constraints and explicit error payloads.

**Rationale**: Centralized request validation provides predictable behavior and prevents malformed values
from reaching task or persistence logic.

**Alternatives considered**:

- Validation only in the service layer: Rejected because it delays malformed requests and weakens HTTP
  contract behavior.
- No validation constraints: Rejected because it conflicts with safe input handling and predictable errors.

## Decision: Use status-specific JSON errors

**Decision**: Return consistent JSON objects for validation, not-found, conflict, and storage failures,
with status codes that match the operation condition.

**Rationale**: Predictable error responses support reliable API clients and contract tests while avoiding
internal exception leakage.

**Alternatives considered**:

- Framework-default validation responses: Rejected as inconsistent with the project's stable error contract.
- Plain text or empty errors: Rejected because clients cannot reliably identify field or operation failures.

## Decision: Test public behavior and contracts

**Decision**: Use pytest, FastAPI HTTP test support, and HTTPX for unit, integration, and contract checks.

**Rationale**: Tests must verify externally visible routes, status codes, payloads, persistence behavior,
and malformed or missing resource cases. A contract suite also protects response and validation shapes.

**Alternatives considered**:

- Unit tests only: Rejected because they do not verify HTTP semantics or integration behavior.
- Manual API checks only: Rejected because automated validation is mandatory before merge.

## Resolved Clarifications

No unresolved feature clarifications remain. The plan uses the specification assumptions: no authentication,
no external database, required title, optional description, default incomplete status, opaque task identities,
and no extra task-management capabilities.
