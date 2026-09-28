"""Registry preflight and NO_INDEPENDENT_VALIDATION messaging."""

from __future__ import annotations

import copy

import yaml

from fishai.scoring.harmonization.preflight import run_registry_preflight
from fishai.scoring.harmonization.registry import (
    load_assimilated_sources_registry,
    no_independent_validation_messages,
)


def test_committed_registry_triggers_no_independent_validation_by_name() -> None:
    reg = load_assimilated_sources_registry()
    messages = no_independent_validation_messages(reg)
    assert messages
    assert messages[0].startswith("NO_INDEPENDENT_VALIDATION:")
    assert "NDBC buoy temperature" in messages[0]
    assert "'unknown' for WCOFS" in messages[0]
    preflight = run_registry_preflight(reg)
    assert preflight["any_independent_validation_source"] is False
    assert preflight["no_independent_validation_messages"] == messages


def test_accepted_by_auditor_clears_preflight(tmp_path) -> None:
    reg = copy.deepcopy(load_assimilated_sources_registry())
    assert run_registry_preflight(reg)["any_independent_validation_source"] is False

    reg["sources"]["ndbc_buoy_temperature"]["wcofs"]["accepted_by_auditor"] = True
    assert run_registry_preflight(reg)["any_independent_validation_source"] is True
    assert no_independent_validation_messages(reg) == []

    path = tmp_path / "reg.yaml"
    path.write_text(yaml.dump(reg), encoding="utf-8")
    from fishai.scoring.harmonization.registry import load_assimilated_sources_registry as load_reg

    loaded = load_reg(path)
    assert run_registry_preflight(loaded)["any_independent_validation_source"] is True
