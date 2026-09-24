"""Compatibility exports for legacy CoPaw imports."""

from opentelemetry.instrumentation.qwenpaw._shell_patch import (
    _MODULE_SHELL,
    _build_subprocess_env,
    make_execute_shell_command_wrapper,
    should_inject_trace_for_shell_command,
)

__all__ = [
    "_MODULE_SHELL",
    "_build_subprocess_env",
    "make_execute_shell_command_wrapper",
    "should_inject_trace_for_shell_command",
]
