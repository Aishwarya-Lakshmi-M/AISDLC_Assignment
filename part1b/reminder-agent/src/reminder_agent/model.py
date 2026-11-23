"""Structured Reminder Agent output model."""

from dataclasses import asdict, dataclass
from typing import Literal


ReminderStatus = Literal["ready", "needs_clarification"]


@dataclass(frozen=True)
class ReminderResult:
    """The five-field reminder result shared by every application outcome."""

    title: str | None
    date: str | None
    time: str | None
    status: ReminderStatus
    clarification: str | None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


def create_ready_result(title: str, date: str, time: str) -> ReminderResult:
    """Construct and return a validated ready reminder."""

    from .validator import validate_result

    return validate_result(
        {
            "title": title,
            "date": date,
            "time": time,
            "status": "ready",
            "clarification": None,
        }
    )


def create_clarification_result(
    *,
    title: str | None = None,
    date: str | None = None,
    time: str | None = None,
    clarification: str,
) -> ReminderResult:
    """Construct a clarification result while preserving safely known fields."""

    from .validator import validate_result

    return validate_result(
        {
            "title": title,
            "date": date,
            "time": time,
            "status": "needs_clarification",
            "clarification": clarification,
        }
    )


def create_unsupported_result(
    clarification: str,
    *,
    title: str | None = None,
    date: str | None = None,
) -> ReminderResult:
    """Construct an unsupported-operation result with no confirmed time."""

    return create_clarification_result(
        title=title,
        date=date,
        time=None,
        clarification=clarification,
    )
