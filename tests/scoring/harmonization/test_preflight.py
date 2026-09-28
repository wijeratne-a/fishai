"""Registry preflight and NO_INDEPENDENT_VALIDATION messaging."""

from __future__ import annotations

import copy

import yaml

from fishai.scoring.harmonization.preflight import run_registry_preflight
from fishai.scoring.harmonization.registry import (
    load_assimilated_sources_registry,
    no_independent_validation_messages,
    wcofs_independent_observation_source,
)


def test_seeded_registry_passes_independent_validation_preflight() -> None:
    reg = load_assimilated_sources_registry()
    assert wcofs_independent_observation_source("ndbc_buoy_temperature", reg) is True
    preflight = run_registry_preflight(reg)
    assert preflight["any_independent_validation_source"] is True
    assert preflight["no_independent_validation_messages"] == []


def test_flipping_accepted_by_auditor_false_triggers_no_independent_validation() -> None:
    reg = copy.deepcopy(load_assimilated_sources_registry())
    assert run_registry_preflight(reg)["any_independent_validation_source"] is True

    reg["sources"]["ndbc_buoy_temperature"]["wcofs"]["accepted_by_auditor"] = False
    messages = no_independent_validation_messages(reg)
    assert messages
    assert messages[0].startswith("NO_INDEPENDENT_VALIDATION:")
    assert "NDBC buoy temperature" in messages[0]
    assert "'unknown' for WCOFS" in messages[0]
    preflight = run_registry_preflight(reg)
    assert preflight["any_independent_validation_source"] is False
