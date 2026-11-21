# Data Model: Todo REST API

## Todo Task

The Todo Task is the primary entity for create, retrieve, update, and delete operations.

| Field       | Type          | Required | Rules                                                      | Notes                                           |
| ----------- | ------------- | -------- | ---------------------------------------------------------- | ----------------------------------------------- |
| id          | UUID string   | Yes      | Valid UUID; unique and immutable                           | User-supplied IDs are not accepted.             |
| title       | string        | Yes      | 1-200 characters                                           | Trimmed before validation or storage.           |
| description | string        | No       | 0-2000 characters                                          | Defaults to an empty value.                     |
| completed   | boolean       | Yes      | True or false                                              | Defaults to false for new tasks.                |
| created_at  | UTC timestamp | Yes      | Automatically generated; immutable                         | Must be present in every persisted Todo record. |
| updated_at  | UTC timestamp | Yes      | Automatically generated; changes after a successful update | Must be present in every persisted Todo record. |

## Create Task Input

- `title`: required string with 1-200 characters.
- `description`: optional string with 0-2000 characters.
- `completed`: optional boolean for explicit initial status; otherwise false.

Unknown input fields MUST be rejected or consistently ignored only if the HTTP contract explicitly allows
it. The planned contract rejects unknown fields to protect against accidental payload changes.

## Update Task Input

The update operation MUST support partial changes to title, description, and completed status.
At least one supported field MUST be provided. A provided field is applied even if it changes the value to
false or an otherwise valid empty description.

- `title`: optional string with 1-200 characters.
- `description`: optional string with 0-2000 characters.
- `completed`: optional boolean.

## Task Collection

The task collection is an ordered set of Todo Tasks. The API MUST sort ascending by `created_at` and use
Todo `id` as a tie-breaker. The API MUST return an empty collection when no tasks exist and MUST not return
an error solely because the collection is empty.

## Validation Error

All validation failures MUST use a stable error object with:

- `code`: machine-readable error category.
- `message`: safe, human-readable summary.
- `details`: optional field-specific validation entries.

Internal validation implementation details and file paths MUST NOT appear in this object. Unexpected JSON
read/write failures MUST use the same object shape with `code = "storage_error"`, HTTP 500, and a safe generic
message.

## Persistence Representation

The persisted JSON representation MUST contain task records and a supported collection schema/version.
Reads and writes MUST validate the expected structure. A missing file represents an empty collection for
initial use. A malformed or unreadable file is reported as a storage failure and is not silently replaced.

## State Transitions

- New task: `completed = false`, unless the create contract explicitly sets a valid initial status.
- Active task: `completed = false`.
- Completed task: `completed = true`.
- Deleted task: no longer returned from list or item retrieval.

A task may transition repeatedly between active and completed. Updating title or description does not alter
completion state unless the update request includes that field.
