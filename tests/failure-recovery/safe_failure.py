"""Safe failure outputs for scientific paths.

A failed model must not be replaced by another species.
"""

from __future__ import annotations

from typing import Any

SAFE_TOKENS = frozenset(
    {
        "UNKNOWN",
        "UNAVAILABLE",
        "INSUFFICIENT_DATA",
        "STALE",
        "UNSUPPORTED",
        "WITHHELD",
    }
)


def safe_failure(token: str, *, species_code: str, reason: str) -> dict[str, Any]:
    """Return a terminal safe output. Token must be one of SAFE_TOKENS."""
    token = token.upper().strip()
    if token not in SAFE_TOKENS:
        raise ValueError(f"unsafe or unknown failure token: {token}")
    return {
        "species_code": species_code,
        "status": token,
        "probability": None,
        "output_class": "SAFE_FAILURE",
        "reason": reason,
        "substitute_species": None,
    }


def resolve_model_result(
    *,
    requested_species: str,
    model_ok: bool,
    probability: float | None = None,
    failure_token: str = "INSUFFICIENT_DATA",
    failure_reason: str = "model_failed",
    alternate_species_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve one species request.

    If the model fails, return a safe token for the *requested* species.
    Never return alternate_species_result in place of the failure.
    """
    if model_ok:
        if probability is None:
            return safe_failure(
                "UNKNOWN",
                species_code=requested_species,
                reason="model_ok_but_probability_missing",
            )
        return {
            "species_code": requested_species,
            "status": "OK",
            "probability": probability,
            "output_class": "INTERNAL_MODEL_OUTPUT",
            "reason": "model_ok",
            "substitute_species": None,
        }

    # Explicitly ignore alternate_species_result — substitution is forbidden.
    _ = alternate_species_result
    return safe_failure(
        failure_token,
        species_code=requested_species,
        reason=failure_reason,
    )
