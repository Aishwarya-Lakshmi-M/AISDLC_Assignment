"""Reminder Agent package foundation."""

from .context import EvaluationContext, ReminderRequest
from .model import ReminderResult
from .model import (
    create_clarification_result,
    create_ready_result,
    create_unsupported_result,
)
from .parser import (
    AIAdapterConfig,
    AIResponseClient,
    GeminiAIResponseClient,
    ProviderNeutralAIAdapter,
    create_reminder,
    interpret_complete_reminder,
)
from .validator import (
    parse_and_validate_result,
    validate_result,
    validate_unsupported_result,
)

__all__ = [
    "AIAdapterConfig",
    "AIResponseClient",
    "GeminiAIResponseClient",
    "EvaluationContext",
    "ProviderNeutralAIAdapter",
    "ReminderRequest",
    "ReminderResult",
    "create_ready_result",
    "create_unsupported_result",
    "create_reminder",
    "create_clarification_result",
    "interpret_complete_reminder",
    "parse_and_validate_result",
    "validate_result",
    "validate_unsupported_result",
]
