<!--
Sync Impact Report:
- Version change: 1.0.0 -> 2.0.0
- Modified principles:
  - Specification-Driven Todo API Delivery -> Specification-Driven Reminder Creation
  - Maintainable Modular Python -> Traceable Python Implementation
  - REST API Consistency and Predictable Responses -> Deterministic Structured Output
  - Test-First and Automated Validation -> Test-First and Evidence-Based Validation
  - API Integration and Contract Verification -> Harness and Semantic Validation
  - Security, Input Validation, and Safe Persistence -> Safe Input and No-Invention Rules
  - Scope Control and Product Simplicity -> Single-Purpose Reminder Scope
- Added sections: Reminder Schema and Processing Constraints; Evaluation and Quality Gates
- Removed sections: Todo REST API rules and JSON persistence requirements
- Follow-up TODOs: Ratification date is unknown
-->

# Reminder Agent Constitution

## Core Principles

### I. Specification-Driven Reminder Creation

Every feature MUST begin from an approved Spec Kit specification that defines natural-language input,
the structured reminder output, acceptance criteria, clarification behavior, and boundaries. Implementation
MUST follow the approved specification and MUST NOT introduce behavior outside reminder creation.
Specifications, plans, tasks, tests, and implementation MUST remain traceable to each required behavior.

### II. Traceable Python Implementation

The application MUST be implemented in Python with cohesive modules that separate input handling,
reminder parsing, structured-output construction, validation, and evaluation support. Functions and
classes MUST have one clear responsibility, explicit inputs and outputs, and type annotations for public
interfaces. Dependencies MUST remain explicit and MUST be added only for a demonstrated project need.

### III. Deterministic Structured Output

The output for a reminder request MUST follow one stable JSON shape with exactly these fields:
`title`, `date`, `time`, `status`, and `clarification`. A completed reminder MUST use
`status: "ready"` and set `clarification` to `null`. An incomplete or ambiguous request MUST use
`status: "needs_clarification"` and provide a concise clarification question in `clarification`.
The implementation MUST emit JSON-compatible values and MUST NOT represent missing data with invented
dates, times, titles, or defaults.

### IV. Test-First and Evidence-Based Validation

Tests MUST be written before implementation for each new behavior. Test coverage MUST include complete
requests, missing required fields, ambiguous information, relative date and time expressions, malformed
input, unsupported requests, and representative natural-language variants. A focused test MUST fail
before implementation and pass before the behavior is integrated. All tests and validation evidence
MUST be reproducible from repository commands.

### V. Harness and Semantic Validation

The project MUST provide or support a single evaluation harness that assesses structural correctness,
behavioral properties, and semantic quality for a dataset of at least 15 cases. The harness MUST verify
the required JSON fields, field types, status values, clarification behavior, no-invention rules, and
scope compliance. A reminder MUST be judged semantically only against the request context and approved
date/time interpretation rules.

### VI. Safe Input and No-Invention Rules

The application MUST treat natural-language input as untrusted and MUST validate every generated field
before returning it. If required information is missing or ambiguous, the application MUST ask a suitable
clarification question instead of guessing or selecting a default. It MUST reject or route unsupported
operations safely, MUST avoid unsafe prompt instructions or sensitive-data disclosure, and MUST NOT
invent context not present in the request or specification.

### VII. Single-Purpose Reminder Scope

The implementation MUST only create reminders. It MUST NOT implement databases, notifications, calendar
integration, rescheduling, snoozing, or unrelated task-management features. The smallest implementation
that satisfies the approved specification and harness MUST be preferred, and added complexity MUST be
documented and justified before it is approved.

## Reminder Schema and Processing Constraints

- The canonical output fields MUST be `title`, `date`, `time`, `status`, and `clarification`.
- A ready reminder MUST use an ISO 8601 calendar date in `YYYY-MM-DD` format and a 24-hour time in
  `HH:MM` format.
- A needs-clarification reminder MUST follow the same output shape and MUST preserve its known fields
  while using `null` for fields that cannot be determined safely.
- The status MUST be exactly `ready` or `needs_clarification`.
- The application MUST NOT persist reminder data, send notifications, integrate with calendars, or
  perform rescheduling or snoozing.
- Relative date and time expressions MUST be resolved only by the documented current-date and timezone
  conventions approved in the specification.
- Generated data MUST be validated as JSON and against the documented schema before it is returned.

## Evaluation and Quality Gates

- Work MUST follow the Spec Kit sequence: specify, clarify or plan when needed, task, implement, and analyze.
- The test suite MUST pass for structural, behavioral, and semantic cases.
- The evaluation harness MUST run against at least 15 cases and MUST report pass, fail, or
  needs-clarification outcomes without silent fallback.
- Output validation MUST reject extra fields, wrong field types, invalid dates or times, invalid statuses,
  invented ready values, and missing clarification questions.
- Scope-sensitive tests MUST prove that database, notification, calendar, rescheduling, and snoozing
  behavior remains out of the implementation.
- Quality-gate exceptions MUST be time-bound, documented in the change record, and approved before merge.

## Governance

This constitution supersedes conflicting local development practices for Reminder Agent. Amendments
MUST identify the affected principle or section, document the rationale and compatibility impact, update
the constitution version, and preserve or explicitly migrate affected specifications and implementations.

Semantic versioning applies to constitution changes: MAJOR for incompatible governance or removal or
redefinition of a core principle, MINOR for a new principle or materially expanded requirement, and
PATCH for wording clarification or non-semantic refinement. Amendment proposals require repository
approval before adoption. Compliance reviews MUST verify specifications, tests, harness coverage,
implementation scope, structured output, no-invention behavior, and quality gates against this constitution.

**Version**: 2.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Record the original adoption date | **Last Amended**: 2026-11-22
