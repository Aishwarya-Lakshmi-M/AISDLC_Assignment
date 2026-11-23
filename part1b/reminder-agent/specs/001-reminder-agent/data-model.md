# Data Model: Reminder Agent

## EvaluationContext

The explicit context required to resolve relative expressions.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `reference_datetime` | ISO 8601 datetime | Yes | Supplied by the application/evaluation caller |
| `timezone` | IANA timezone name | Yes | Explicit and not inferred |

The application MUST NOT obtain these values from the machine clock or environment.

## ReminderRequest

The natural-language input and its evaluation context.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `text` | String | Yes | Non-empty; may describe complete, incomplete, ambiguous, or unsupported requests |
| `context` | EvaluationContext | Yes | Both reference datetime and timezone are required |

## ReminderResult

The only application output.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `title` | String or null | Yes | Concise title for ready; null when not safely known |
| `date` | String or null | Yes | `YYYY-MM-DD` for ready values; null otherwise |
| `time` | String or null | Yes | `HH:MM` for ready values; null otherwise |
| `status` | String | Yes | Exactly `ready` or `needs_clarification` |
| `clarification` | String or null | Yes | Null for ready; specific question or unsupported-operation explanation otherwise |

## State Rules

### Ready

All of `title`, `date`, and `time` are known and valid, `status` is `ready`, and `clarification` is null.

### Needs Clarification

`status` is `needs_clarification`, known fields are preserved, unknown fields are null, and
`clarification` is non-empty. This includes missing details, ambiguous expressions, unavailable context,
contradictory input, and unsupported operations.

### Validation Rules

- Exactly five fields MUST be present.
- No extra fields are allowed.
- Date values MUST be valid ISO 8601 calendar dates.
- Time values MUST be valid 24-hour clock values.
- `ready` MUST contain valid title, date, and time values and null clarification.
- `needs_clarification` MUST contain a non-empty clarification.
- Unsupported operations MUST never return `ready`.
