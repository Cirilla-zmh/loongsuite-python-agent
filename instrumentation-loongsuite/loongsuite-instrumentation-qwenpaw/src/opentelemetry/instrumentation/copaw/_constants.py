"""Compatibility exports for legacy CoPaw imports."""

from opentelemetry.instrumentation.qwenpaw._constants import (
    COPAW_OTEL_CHILD_AGENT,
    COPAW_OTEL_INJECT_SHELL_TRACE,
    is_copaw_child_agent_process,
)

__all__ = [
    "COPAW_OTEL_CHILD_AGENT",
    "COPAW_OTEL_INJECT_SHELL_TRACE",
    "is_copaw_child_agent_process",
]
