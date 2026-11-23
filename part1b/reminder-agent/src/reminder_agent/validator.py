"""Validation for the approved ReminderResult JSON contract."""

import json
import re
from datetime import date
from typing import Any, Mapping

from .model import ReminderResult, ReminderStatus


REQUIRED_FIELDS = {"title", "date", "time", "status", "clarification"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
RAW_OUTPUT_DIAGNOSTIC_LIMIT = 500


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_optional_string(value: object) -> bool:
    return value is None or _is_non_empty_string(value)


def _validate_date(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate_time(value: object) -> bool:
    if value is None:
        return True
    return isinstance(value, str) and TIME_PATTERN.fullmatch(value) is not None


def validate_result(result: Mapping[str, Any] | ReminderResult) -> ReminderResult:
    """Validate a result mapping or ReminderResult and return a normalized result."""

    if isinstance(result, ReminderResult):
        values: dict[str, Any] = result.to_dict()
    elif isinstance(result, Mapping):
        values = dict(result)
    else:
        raise ValueError("ReminderResult must be a mapping or ReminderResult")

    if set(values) != REQUIRED_FIELDS:
        raise ValueError("ReminderResult must contain exactly five required fields")

    status = values["status"]
    if status not in ("ready", "needs_clarification"):
        raise ValueError("ReminderResult status is invalid")

    title = values["title"]
    date_value = values["date"]
    time_value = values["time"]
    clarification = values["clarification"]

    if not _validate_optional_string(title):
        raise ValueError("ReminderResult title must be a non-empty string or null")
    if not _validate_date(date_value):
        raise ValueError("ReminderResult date must be YYYY-MM-DD or null")
    if not _validate_time(time_value):
        raise ValueError("ReminderResult time must be HH:MM or null")
    if clarification is not None and not _is_non_empty_string(clarification):
        raise ValueError("ReminderResult clarification must be a non-empty string or null")

    if status == "ready":
        if not _is_non_empty_string(title):
            raise ValueError("A ready reminder must include a title")
        if not isinstance(date_value, str):
            raise ValueError("A ready reminder must include a date")
        if not isinstance(time_value, str):
            raise ValueError("A ready reminder must include a time")
        if clarification is not None:
            raise ValueError("A ready reminder must have null clarification")
    elif not _is_non_empty_string(clarification):
        raise ValueError("A clarification reminder must include clarification")

    return ReminderResult(
        title=title,
        date=date_value,
        time=time_value,
        status=status,
        clarification=clarification,
    )


def parse_and_validate_result(raw_output: str) -> ReminderResult:
    """Parse one raw JSON object and validate it against the approved contract."""

    excerpt = raw_output[:RAW_OUTPUT_DIAGNOSTIC_LIMIT]
    if len(raw_output) > RAW_OUTPUT_DIAGNOSTIC_LIMIT:
        excerpt += "..."

    try:
        value = json.loads(raw_output)
        if not isinstance(value, Mapping):
            raise ValueError("AI output must be one JSON object")
        return validate_result(value)
    except ValueError as error:
        raise ValueError(
            f"{error}; raw model output (first "
            f"{RAW_OUTPUT_DIAGNOSTIC_LIMIT} characters): {excerpt!r}"
        ) from error


def validate_unsupported_result(result: Mapping[str, Any] | ReminderResult) -> ReminderResult:
    """Require an unsupported-operation result to remain needs_clarification."""

    validated = validate_result(result)
    if validated.status != "needs_clarification":
        raise ValueError("Unsupported operations must not return ready")
    return validated
