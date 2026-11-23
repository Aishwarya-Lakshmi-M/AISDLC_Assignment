# Feature Specification: Reminder Agent

**Feature Branch**: `001-reminder-agent`

**Created**: 2026-11-22

**Status**: Draft

**Input**: User description: "Build an AI application that accepts a natural-language request to create a reminder and converts it into structured JSON. It must not invent missing or ambiguous information, and it must support only reminder creation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Convert a Complete Reminder Request (Priority: P1)

A user enters a natural-language sentence that fully identifies what to remind them about, when to act,
and what time is required. The application returns one structured reminder with the requested details
marked as ready.

**Why this priority**: Complete conversion is the primary value and the minimum usable product.

**Independent Test**: A request such as "Remind me to study Python tomorrow at 6 PM" produces a ready
reminder whose title, date, time, status, and clarification fields match the request and evaluation context.

**Acceptance Scenarios**:

1. **Given** a complete request with an action, date, and time, **When** the request is converted,
   **Then** the result has status `ready`, a concise title, the resolved date and time, and a null
   clarification.
2. **Given** a request that names the reminder but omits the date, **When** the request is converted,
   **Then** the result asks specifically which date should be used and does not invent a date.
3. **Given** a request that names the reminder and date but omits the time, **When** the request is converted,
   **Then** the result asks specifically which time should be used and does not invent a time.

---

### User Story 2 - Request Clarification Instead of Guessing (Priority: P2)

A user provides a vague or incomplete request. The application identifies the missing or ambiguous detail,
preserves any details that are known, and asks one suitable clarification question rather than guessing.

**Why this priority**: Preventing invented reminders is essential to the feature's trust and correctness.

**Independent Test**: An ambiguous request can be evaluated without creating a ready reminder and must
return a clarification status with a relevant question.

**Acceptance Scenarios**:

1. **Given** a request that does not identify what reminder to create, **When** the request is converted,
   **Then** the result has status `needs_clarification` and asks what activity should be reminded.
2. **Given** a request whose date or time is ambiguous, **When** the request is converted,
   **Then** the result asks for the intended date or time and leaves the corresponding unknown field empty.
3. **Given** a request containing one known value and one missing value, **When** the request is converted,
   **Then** the known value is retained and only the missing or ambiguous value is requested.
4. **Given** a genuinely ambiguous date or time such as "6" or "next Friday" with multiple equally
   plausible interpretations, **When** the request is converted, **Then** the result asks for the intended
   value rather than selecting an interpretation arbitrarily.

---

### User Story 3 - Reject Unsupported Reminder Operations (Priority: P3)

A user asks to reschedule, snooze, list, delete, persist, notify, or otherwise operate on reminders outside
the create-reminder scope. The application does not perform or imply that unsupported operation.

**Why this priority**: Clear scope boundaries prevent misleading behavior and keep the feature focused.

**Independent Test**: Unsupported operations produce no reminder marked ready and do not claim that a
database, notification, or calendar operation occurred.

**Acceptance Scenarios**:

1. **Given** a request to change an existing reminder, **When** the request is evaluated,
   **Then** the result uses status `needs_clarification`, sets any unknown reminder fields to null,
   and clearly explains that rescheduling or snoozing is unsupported.
2. **Given** a request for notification, calendar synchronization, snoozing, or persistence,
   **When** the request is evaluated, **Then** the result uses status `needs_clarification`, clearly
   explains that the operation is unsupported, and makes no claim that it occurred.
3. **Given** a request to list or delete reminders, **When** the request is evaluated,
   **Then** the result uses status `needs_clarification`, explains the unsupported operation, and never
   returns status `ready`.

---

### Edge Cases

- A request contains contradictory date or time information; the result MUST ask which interpretation is
  intended rather than choosing one.
- Relative date and time expressions MUST be resolved using the explicit reference datetime and timezone
  supplied with the evaluation context. The application MUST NOT read the machine clock or infer a timezone.
- A genuinely ambiguous date or time expression is one with two or more plausible interpretations under
  the supplied context. The result MUST use `needs_clarification`, preserve any known fields, set ambiguous
  fields to null, and ask which interpretation is intended.
- A date or time cannot be resolved because no reference datetime or timezone was supplied; the result MUST
  request clarification rather than guessing or assuming the machine location or time.
- A malformed or empty input has no reliable title, date, or time; the result MUST return clarification
  status and a suitable question.
- A request includes an extra request outside reminder creation; only the reminder portion is evaluated,
  and unsupported operations are not claimed as completed.
- Relative date or time expressions must resolve consistently from the explicit reference datetime and
  timezone supplied to the application/evaluation context.
- Unsupported operations MUST return the existing five-field JSON contract with status
  `needs_clarification`, a clear explanation in `clarification`, null unknown fields, and no `ready` status.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a natural-language request and produce exactly one reminder result.
- **FR-002**: The system MUST include the fields `title`, `date`, `time`, `status`, and `clarification`
  in every result.
- **FR-003**: A complete reminder MUST use status `ready`, a concise title, a valid date, a valid time,
  and a null clarification.
- **FR-004**: An incomplete or ambiguous reminder MUST use status `needs_clarification`, preserve known
  fields, set unknown fields to null, and include a concise clarification question.
- **FR-005**: The system MUST express a ready date in `YYYY-MM-DD` format and a ready time in `HH:MM`
  24-hour format.
- **FR-006**: The system MUST NOT invent a title, date, time, or default interpretation when the request
  does not provide or clearly imply it.
- **FR-007**: The system MUST ask for clarification for missing, contradictory, or ambiguous required
  information.
- **FR-008**: Relative date and time expressions MUST be resolved only with an explicit reference datetime
  and timezone supplied in the application/evaluation context. The system MUST NOT use the machine clock
  or infer a timezone.
- **FR-008A**: When a date or time has multiple plausible interpretations under the supplied context,
  the system MUST use `needs_clarification`, set ambiguous fields to null, and ask the user to specify
  the intended interpretation.
- **FR-009**: The system MUST reject extra structured fields, invalid date or time values, invalid statuses,
  and malformed outputs.
- **FR-010**: The system MUST limit behavior to creating a reminder and MUST NOT execute notification,
  persistence, calendar, rescheduling, snoozing, listing, or deleting operations.
- **FR-010A**: Requests for unsupported operations MUST use the existing five-field output contract,
  status `needs_clarification`, and a clear explanation in `clarification`; they MUST never return `ready`
  or claim that an unsupported operation occurred.
- **FR-011**: The system MUST produce JSON-compatible output that can be evaluated for structure,
  behavior, and semantic correctness.

### Key Entities *(include if feature involves data)*

- **Reminder Request**: A natural-language statement describing an intended reminder, including optional
  title, date, time, and ambiguity.
- **Reminder Result**: The structured outcome containing title, date, time, status, and clarification.
- **Clarification**: A concise question used when required reminder information is missing or ambiguous.
- **Evaluation Context**: The supplied reference datetime and timezone used to resolve relative date and
  time expressions consistently; it MUST be explicit and MUST NOT come from the machine clock.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90 percent of complete, unambiguous requests in the evaluation dataset produce the
  correct title, date, time, status, and null clarification.
- **SC-002**: 100 percent of cases with missing or ambiguous required information produce
  `needs_clarification` with a relevant question and no invented ready values.
- **SC-003**: 100 percent of evaluated outputs contain exactly the five required fields with valid field
  types and allowed status values.
- **SC-004**: 100 percent of unsupported-operation cases do not claim database, notification, calendar,
  rescheduling, snoozing, listing, deleting, or other out-of-scope behavior occurred, and return
  `needs_clarification` with a clear unsupported-operation explanation.
- **SC-005**: The evaluation harness assesses at least 15 representative cases and reports structural,
  behavioral, semantic, and scope results for every case.
- **SC-006**: In a usability review, at least 90 percent of clarification questions are judged specific,
  understandable, and actionable.

## Assumptions

- Relative expressions such as "tomorrow" are resolved only from an explicit reference datetime and
  timezone supplied in the evaluation context.
- If the evaluation context omits a reference datetime or timezone, the application does not infer them
  and requests clarification instead.
- The application's output is in-memory structured data and is not persisted.
- "Create a reminder" means producing structured reminder details, not sending or scheduling a message.
- The first version supports natural-language text in a single request and does not require conversation
  history or user authentication.
- No user-specific or external account data is needed.

