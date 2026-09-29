"""Holdout scoring preflight (registry / independence) before model I/O."""

from __future__ import annotations

from typing import Any

from fishai.scoring.harmonization.registry import (
    any_holdout_validation_source_independent_of_wcofs,
    no_independent_validation_messages,
)


def run_registry_preflight(registry: dict[str, Any]) -> dict[str, Any]:
    """
    Report independence state for graded holdout validation.

    Does not block scoring; verdicts are forced UNKNOWN when no independent source exists.
    """
    messages = no_independent_validation_messages(registry)
    return {
        "any_independent_validation_source": any_holdout_validation_source_independent_of_wcofs(
            registry
        ),
        "no_independent_validation_messages": messages,
    }
