from datetime import UTC, datetime
from typing import Any

TODO_FIELDS = {
    "id",
    "title",
    "description",
    "completed",
    "created_at",
    "updated_at",
}


def parse_utc_timestamp(value: Any) -> datetime:
    assert isinstance(value, str), value
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    assert parsed.tzinfo is not None, value
    assert parsed.utcoffset() == UTC.utcoffset(parsed), value
    return parsed.astimezone(UTC)


def assert_todo_shape(todo: Any) -> dict[str, Any]:
    assert isinstance(todo, dict), todo
    assert set(todo) == TODO_FIELDS, todo

    todo_id = todo["id"]
    assert isinstance(todo_id, str), todo
    # UUID parsing is deliberately independent of the application's code.
    from uuid import UUID

    UUID(todo_id)

    assert isinstance(todo["title"], str), todo
    assert 1 <= len(todo["title"]) <= 200, todo
    assert isinstance(todo["description"], str), todo
    assert len(todo["description"]) <= 2000, todo
    assert isinstance(todo["completed"], bool), todo
    parse_utc_timestamp(todo["created_at"])
    parse_utc_timestamp(todo["updated_at"])
    return todo


def assert_error_response(response: Any) -> dict[str, Any]:
    assert response.headers.get("content-type", "").startswith("application/json")
    error = response.json()
    assert isinstance(error, dict), error
    assert set(error).issubset({"code", "message", "details"}), error
    assert isinstance(error.get("code"), str) and error["code"], error
    assert isinstance(error.get("message"), str) and error["message"], error

    if "details" in error:
        assert isinstance(error["details"], list), error
        for detail in error["details"]:
            assert isinstance(detail, dict), detail
            assert set(detail) == {"field", "message"}, detail
            assert isinstance(detail["field"], str), detail
            assert isinstance(detail["message"], str), detail
    return error
