#!/usr/bin/env python3
"""Illustrative ingestion stub for FishAI geospatial design.

Does NOT download, scrape, or ingest production datasets.
Network access is refused. Fixture mode writes a single synthetic row
to stdout so schema/partition names can be reviewed.

Usage:
  python ingest.py --mode fixture --entity CatchEffortObservation
  python ingest.py --mode fixture --entity FarmOperationalOutcome
  python ingest.py --mode fixture --entity ModelPrediction
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Callable

BLOCKED = (
    "Production acquire() is blocked until a wedge is locked, the source is "
    "rights-approved, and a human confirms a lawful access method."
)

# Names of pandera/quality checks the real pipeline must implement.
CHECKS = [
    "schema_kernel_required_fields",
    "crs_lon_lat_bounds",
    "aoi_contains_cell_or_point",
    "time_observed_vs_published",
    "published_at_not_null",
    "h3_index_valid",
    "privacy_public_file_has_no_latlon",
    "rights_status_approved_for_promote",
    "taxonomy_resolved_or_flagged",
    "catch_has_effort",
    "farm_outcome_not_food_safety_claim",
    "forecast_not_overwrite",
    "asof_feature_published_at_le_cutoff",
]


def acquire(source_id: str) -> None:
    raise PermissionError(BLOCKED + f" source_id={source_id}")


def profile(ingestion_run_id: str) -> None:
    raise PermissionError(BLOCKED + f" run={ingestion_run_id}")


def normalize(ingestion_run_id: str) -> None:
    raise PermissionError(BLOCKED + f" run={ingestion_run_id}")


def validate(ingestion_run_id: str) -> None:
    raise PermissionError(BLOCKED + f" run={ingestion_run_id}")


def promote(ingestion_run_id: str) -> None:
    raise PermissionError(BLOCKED + f" run={ingestion_run_id}")


def _fixture_catch() -> dict:
    return {
        "event_id": "01800000-0000-7000-8000-000000000010",
        "entity_type": "CatchEffortObservation",
        "source_id": "partner.fixture",
        "source_record_id": "fixture-001",
        "source_dataset_version": "fixture-0",
        "source_owner": "FIXTURE",
        "ingestion_run_id": "01800000-0000-7000-8000-000000000099",
        "observed_at_utc": "2026-09-16T10:00:00Z",
        "published_at_utc": "2026-09-16T22:00:00Z",
        "ingested_at_utc": "2026-09-18T04:00:00Z",
        "revised_at_utc": "2026-09-16T22:00:00Z",
        "latitude": None,
        "longitude": None,
        "spatial_cell_id": "872a30689ffffff",
        "h3_res": 7,
        "spatial_cell_id_public": "852a306bfffffff",
        "official_unit_id": "NEFSC_STAT_AREA:513",
        "species_taxon_id": "urn:lsid:marinespecies.org:taxname:156134",
        "accepted_scientific_name": "Homarus americanus",
        "taxonomic_authority": "WoRMS",
        "gear_type": "trap",
        "sampling_effort_type": "trap_hauls",
        "sampling_effort_value": 40,
        "sampling_effort_unit": "{haul}",
        "absence_reported": False,
        "reporting_channel": "partner_form",
        "privacy_tier": "PRIVATE",
        "data_rights_status": "APPROVED_PARTNER_CONSENT",
        "license": "LicenseRef-Partner-DUA",
        "raw_payload_reference": "fixture://none",
        "transformation_version": "0.0.0-design",
        "transform_hash": "sha256:fixture",
        "source_checksum": "sha256:fixture",
        "notes": "Synthetic stub. No bulk data.",
    }


def _fixture_farm() -> dict:
    return {
        "event_id": "01800000-0000-7000-8000-000000000020",
        "entity_type": "FarmOperationalOutcome",
        "source_id": "partner.oyster.fixture",
        "source_record_id": "fixture-ops-0001",
        "source_dataset_version": "fixture-0",
        "source_owner": "FIXTURE",
        "ingestion_run_id": "01800000-0000-7000-8000-000000000099",
        "observed_at_utc": "2026-09-17T15:00:00Z",
        "published_at_utc": "2026-09-17T16:00:00Z",
        "ingested_at_utc": "2026-09-18T04:00:00Z",
        "revised_at_utc": "2026-09-17T16:00:00Z",
        "latitude": None,
        "longitude": None,
        "spatial_cell_id": "8828d52b2dfffff",
        "h3_res": 8,
        "farm_id": "farm_internal_fixture_01",
        "growing_area_id": "WA_DOH_GROWING_AREA:FIXTURE",
        "outcome_type": "work_window_disruption",
        "severity": "medium",
        "is_food_safety_claim": False,
        "privacy_tier": "PRIVATE",
        "data_rights_status": "APPROVED_PARTNER_CONSENT",
        "license": "LicenseRef-Partner-DUA",
        "raw_payload_reference": "fixture://none",
        "transformation_version": "0.0.0-design",
        "transform_hash": "sha256:fixture",
        "source_checksum": "sha256:fixture",
        "notes": "Not a harvest authorization.",
    }


def _fixture_forecast() -> dict:
    return {
        "event_id": "01800000-0000-7000-8000-000000000030",
        "entity_type": "ModelPrediction",
        "source_id": "fishai.model",
        "source_record_id": "forecast-fixture-0001",
        "source_dataset_version": "model-none",
        "source_owner": "FishAI",
        "ingestion_run_id": "01800000-0000-7000-8000-000000000099",
        "observed_at_utc": "2026-09-18T12:00:00Z",
        "published_at_utc": "2026-09-18T12:00:00Z",
        "ingested_at_utc": "2026-09-18T12:00:00Z",
        "revised_at_utc": "2026-09-18T12:00:00Z",
        "spatial_cell_id": "8629a12ffffffff",
        "h3_res": 6,
        "forecast_id": "01800000-0000-7000-8000-000000000031",
        "project_id": "fishai",
        "wedge_id": "UNRESOLVED",
        "species_scope": "UNRESOLVED",
        "geographic_scope": "UNRESOLVED",
        "issued_at_utc": "2026-09-18T12:00:00Z",
        "forecast_window_start_utc": "2026-09-18T12:00:00Z",
        "forecast_window_end_utc": "2026-09-20T12:00:00Z",
        "target_definition": "Relative likelihood placeholder; no model trained.",
        "prediction_value": 0.0,
        "prediction_unit": "{relative_rank}",
        "confidence_category": "low",
        "model_version": "none-design-stub",
        "feature_snapshot_id": "01800000-0000-7000-8000-000000000032",
        "source_data_cutoff_utc": "2026-09-18T11:00:00Z",
        "known_missing_inputs": ["not_a_real_forecast"],
        "user_visible_limitations": "Schema fixture only.",
        "privacy_policy_applied": "public_h3_parent_res5",
        "privacy_tier": "COARSENED",
        "data_rights_status": "APPROVED_INTERNAL_ONLY",
        "license": "LicenseRef-Internal",
        "raw_payload_reference": "fixture://none",
        "transformation_version": "0.0.0-design",
        "transform_hash": "sha256:fixture",
        "source_checksum": "sha256:fixture",
        "prediction_contract_category": "D",
        "is_retrospective": False,
    }


FIXTURES: dict[str, Callable[[], dict]] = {
    "CatchEffortObservation": _fixture_catch,
    "FarmOperationalOutcome": _fixture_farm,
    "ModelPrediction": _fixture_forecast,
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=["fixture"], required=True)
    p.add_argument("--entity", choices=sorted(FIXTURES), required=True)
    p.add_argument("--source-id", default=None, help="Refused in this stub.")
    args = p.parse_args()
    if args.source_id:
        acquire(args.source_id)
    row = FIXTURES[args.entity]()
    json.dump({"checks": CHECKS, "row": row, "network": False}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
