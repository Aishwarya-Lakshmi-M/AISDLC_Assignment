"""Evaluation context and reminder request structures."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class EvaluationContext:
    """Explicit temporal context supplied by the application or evaluator."""

    reference_datetime: datetime | None = None
    timezone: str | None = None


@dataclass(frozen=True)
class ReminderRequest:
    """A natural-language reminder request and its evaluation context."""

    text: str
    context: EvaluationContext


def reference_datetime_in_timezone(
    context: EvaluationContext,
) -> datetime | None:
    """Return the aware reference datetime converted to its declared timezone."""

    reference = context.reference_datetime
    if reference is None or not context.timezone:
        return None
    if reference.tzinfo is None or reference.utcoffset() is None:
        return None
    try:
        target_timezone = ZoneInfo(context.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        return None
    return reference.astimezone(target_timezone)


def resolve_relative_datetime(
    text: str,
    context: EvaluationContext,
) -> datetime | None:
    """Resolve supported relative date/time expressions from explicit context only."""

    reference = reference_datetime_in_timezone(context)
    if reference is None:
        return None

    lowered = text.lower()
    date_candidates = []
    for absolute_date in re.finditer(r"\b(\d{4}-\d{2}-\d{2})\b", text):
        try:
            date_candidates.append(
                datetime.strptime(absolute_date.group(1), "%Y-%m-%d").date(),
            )
        except ValueError:
            return None

    if re.search(r"\btomorrow\b", lowered):
        date_candidates.append(reference.date() + timedelta(days=1))
    if re.search(r"\btoday\b", lowered):
        date_candidates.append(reference.date())

    next_weekday = re.search(r"\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lowered)
    if next_weekday:
        weekdays = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        target = weekdays[next_weekday.group(1)]
        days_ahead = (target - reference.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        date_candidates.append(reference.date() + timedelta(days=days_ahead))

    relative_minutes = re.search(r"\bin\s+(\d+)\s+minutes?\b", lowered)
    if relative_minutes:
        resolved_datetime = (
            reference.astimezone(timezone.utc)
            + timedelta(minutes=int(relative_minutes.group(1)))
        ).astimezone(reference.tzinfo)
        date_candidates.append(resolved_datetime.date())

    if not date_candidates or len(set(date_candidates)) > 1:
        return None
    if relative_minutes:
        return resolved_datetime
    return datetime.combine(date_candidates[0], reference.timetz())
