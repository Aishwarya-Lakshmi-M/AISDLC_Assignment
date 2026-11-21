<!--
Sync Impact Report:
- Version change: 1.0.0 -> 1.1.0
- Modified principles:
  - Specification Before Implementation -> Specification-Driven Todo API Delivery
  - Library- and Module-First Design -> Maintainable Modular Python
  - Test-First Delivery -> Test-First and Automated Validation
  - Integration and Contract Verification -> API Integration and Contract Verification
  - Simplicity, Observability, and Maintainability -> Safe and Secure Persistence
- Added principles: REST API Consistency and Predictable Responses; Scope Control and Product Simplicity
- Added sections: Technology and Persistence Constraints; Quality Gates
- Removed sections: none
- Follow-up TODOs: ratification date is unknown
-->

# Todo REST API Constitution

## Core Principles

### I. Specification-Driven Todo API Delivery

Every feature MUST begin from an approved Spec Kit specification that defines its Todo API behavior,
scope, acceptance criteria, and edge cases. Implementation MUST follow the specification and MUST NOT
introduce behavior outside its approved scope. Specifications, plans, tasks, tests, and code MUST
remain traceable to a single feature outcome.

### II. Maintainable Modular Python

The application MUST use Python and FastAPI with cohesive modules that separate HTTP routing,
request schemas, domain behavior, and JSON persistence responsibilities. Functions and classes MUST
have one clear responsibility, avoid hidden global state, and use type annotations for public interfaces.
Dependencies MUST be explicit; shared behavior MUST be extracted only when it improves reuse or testability.

### III. REST API Consistency and Predictable Responses

Every Todo endpoint MUST use resource-oriented paths, explicit HTTP methods, and appropriate status
codes for success and failure. Pydantic request models MUST validate required fields, types, and values.
All validation and application errors MUST return a documented, consistent JSON error shape. Responses,
content types, ordering, and not-found behavior MUST be deterministic and MUST not expose internal
exceptions or implementation details.

### IV. Test-First and Automated Validation

pytest tests MUST be written and reviewed before implementation for each new behavior. Test suites MUST
cover success, invalid input, missing resources, persistence failures, and boundary conditions. A new
behavior MUST fail its focused test before implementation, then pass before broader changes proceed.
The implementation MUST pass the complete pytest suite, Ruff linting, and Bandit security analysis before
completion.

### V. API Integration and Contract Verification

HTTP/API tests MUST exercise the FastAPI application through its public routes, status codes, JSON
payloads, and error responses. Contract tests MUST verify request schemas and response structures,
including create, retrieve, update, delete, and task-list behavior. Shared response shapes and persisted
schema changes MUST remain backward compatible unless the specification explicitly documents and approves
a breaking change.

### VI. Security, Input Validation, and Safe Persistence

All externally supplied data MUST be validated at the API boundary and constrained to documented types,
formats, lengths, and allowed values. The application MUST reject malformed JSON and unsafe values with
safe client-facing errors. JSON-based local persistence MUST read and write atomically or recover safely
from incomplete writes, avoid data corruption, and not expose filesystem paths or sensitive details.
Bandit findings that indicate exploitable or unsafe behavior MUST be resolved before merge.

### VII. Scope Control and Product Simplicity

The implementation MUST provide create, retrieve, update, delete, and task-management capabilities only
within the approved feature scope. Repositories MUST reject speculative endpoints, abstractions,
frameworks, services, or configuration unless a current specification demonstrates a concrete need.
The smallest implementation that satisfies tested requirements MUST be preferred, and added complexity
MUST be justified in the feature plan.

## Technology and Persistence Constraints

- The API MUST be implemented in Python using FastAPI.
- pytest MUST be used for unit, HTTP, and integration testing.
- Ruff MUST perform formatting and lint validation.
- Bandit MUST scan application code for security issues.
- Todo data MUST persist through JSON-based local storage and MUST NOT require an external database.
- Persistence operations MUST maintain valid JSON and MUST handle missing, empty, malformed, and
  unavailable storage gracefully.
- API documentation MUST remain synchronized with routes, request models, response models, and
  documented error responses.

## Development Workflow and Quality Gates

- Work MUST follow the Spec Kit sequence: specify, clarify or plan when needed, task, implement, and analyze.
- Before merge or completion, the following gates MUST pass:
  - `pytest` with no failing tests.
  - `ruff check .` with no violations.
  - `ruff format --check .` with no formatting drift.
  - `bandit -r .` with no unresolved high-severity findings.
- Pull requests MUST demonstrate requirement coverage, focused test evidence, HTTP contract coverage,
  persistence behavior, lint and formatting results, and security scan results.
- Breaking API changes MUST update the specification, tests, documentation, and migration or compatibility
  notes before implementation.
- Any quality-gate exception MUST be time-bound, documented in the change record, and approved before merge.

## Governance

This constitution supersedes conflicting local development practices for the Todo REST API. Amendments
MUST identify the affected principle or section, document the rationale and compatibility impact, update
the version, and preserve or explicitly migrate existing specifications and implementations.

Semantic versioning applies to constitution changes: MAJOR for incompatible governance or removal or
redefinition of a core principle, MINOR for a new principle or materially expanded requirement, and
PATCH for wording clarification or non-semantic refinement. All amendment proposals require repository
approval before adoption. Compliance reviews MUST verify specifications, tests, HTTP contracts,
implementation, Ruff results, Bandit results, and persistence behavior against this constitution.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): Record the original adoption date | **Last Amended**: 2026-11-21
