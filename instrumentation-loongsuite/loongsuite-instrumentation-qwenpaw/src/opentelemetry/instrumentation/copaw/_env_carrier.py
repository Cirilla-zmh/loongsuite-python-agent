"""Compatibility exports for legacy CoPaw imports."""

from opentelemetry.instrumentation.qwenpaw._env_carrier import (
    EnvironmentGetter,
    EnvironmentSetter,
)

__all__ = ["EnvironmentGetter", "EnvironmentSetter"]
