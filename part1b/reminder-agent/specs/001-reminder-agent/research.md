# Phase 0 Research: Reminder Agent

## Decision: Use an Explicit Evaluation Context

Relative date and time expressions will be resolved only from a supplied reference datetime and timezone.
The application will require both values and will not inspect the machine clock.

**Rationale**: This makes relative expressions reproducible across runs and evaluation cases.

**Alternatives considered**:
- Machine clock and local timezone: rejected because results vary by environment and can be guessed.
- Request text or locale timezone inference: rejected because this can select an arbitrary interpretation.

## Decision: Use an Ambiguity-First Interpretation Rule

If an expression has multiple plausible interpretations under the supplied context, the application will
return `needs_clarification` and preserve known fields.

**Rationale**: Clarification is safer and required by the specification.

**Alternatives considered**:
- Select the most common interpretation: rejected because it can arbitrarily change the reminder.
- Ask a generic clarification: rejected because a specific question is more actionable.

## Decision: Keep Unsupported Operations in the Structured Contract

Listing, deleting, rescheduling, snoozing, notification, calendar, and persistence requests will return
`needs_clarification`. The `clarification` text will explain the unsupported operation.

**Rationale**: This preserves one stable output shape and guarantees that unsupported operations never
become `ready`.

**Alternatives considered**:
- Add operation-specific fields or statuses: rejected because the contract has exactly five fields.
- Return an empty reminder: rejected because it would not explain why no reminder was created.

## Decision: Use a Provider-Neutral Python Adapter

The design will isolate AI/model behavior behind a small application interface and validate its result
before returning it. The provider is not selected in this phase.

**Rationale**: The assignment requires AI-generated output but not a particular model or service.

**Alternatives considered**:
- Provider-specific logic directly in the application: rejected as unnecessary coupling.
- No AI component: rejected because natural-language semantic interpretation is core to the feature.

## Decision: Use pytest and a Single Evaluation Harness

The implementation plan includes pytest coverage and one harness that runs at least 15 cases covering
structure, behavior, semantics, and scope.

**Rationale**: This directly satisfies the constitution and success criteria.

**Alternatives considered**:
- Separate harnesses by concern: rejected because the constitution requires a single harness.
