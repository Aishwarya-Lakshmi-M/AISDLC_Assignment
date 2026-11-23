# Quickstart: Reminder Agent Validation

## Purpose

Validate the five-field output, clarification behavior, explicit time context, semantic quality, and
scope without starting external services or using persistent storage.

## Prerequisites

- Python 3.11 or newer
- pytest available in the project environment
- A project-defined AI/model adapter available for implementation
- An evaluation case containing natural-language text, an explicit ISO 8601 reference datetime,
  and an explicit IANA timezone

## Validation Commands

After implementation, run:

```powershell
pytest tests/unit tests/contract
pytest tests/semantic tests/harness
pytest
```

The first command verifies result construction and output structure. The second verifies semantic and
scope behavior in the single evaluation harness. The final command verifies the complete test suite.

## Required Validation Cases

- A complete request must return `ready`, valid date and time fields, and null clarification.
- A missing date or time must preserve known fields and return `needs_clarification`.
- Relative expressions must use the supplied reference datetime and timezone, not the machine clock.
- Ambiguous expressions must produce a specific clarification question rather than a guessed value.
- Unsupported operations must return `needs_clarification` and explain the unsupported operation.
- Missing reference datetime or timezone must produce clarification, never an inferred ready result.
- Malformed output and extra fields must be rejected.

## Evaluation Dataset

The harness must run at least 15 cases and report structural, behavioral, semantic, and scope outcomes
for every case. The dataset must include complete requests and unsupported operations.
