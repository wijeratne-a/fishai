"""Optional Darwin Core export (Event Core + Occurrence + eMoF) for CUFES."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Sequence


def write_dwc_triplet(
    events: Sequence[dict[str, Any]],
    occurrences: Sequence[dict[str, Any]],
    dest_dir: Path,
) -> tuple[Path, Path, Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    event_path = dest_dir / "event.txt"
    occ_path = dest_dir / "occurrence.txt"
    emof_path = dest_dir / "measurementorfact.txt"

    occ_by_sample: dict[str, list[dict[str, Any]]] = {}
    for occ in occurrences:
        occ_by_sample.setdefault(str(occ["sample_id"]), []).append(occ)

    with event_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "eventID",
                "eventDate",
                "decimalLatitude",
                "decimalLongitude",
                "footprintWKT",
                "eventType",
                "sampleSizeValue",
                "sampleSizeUnit",
            ],
        )
        writer.writeheader()
        for ev in events:
            writer.writerow(
                {
                    "eventID": ev["event_id"],
                    "eventDate": f"{ev['start_time']}/{ev['stop_time']}",
                    "decimalLatitude": ev["start_latitude"],
                    "decimalLongitude": ev["start_longitude"],
                    "footprintWKT": ev.get("track_wkt"),
                    "eventType": "cufes_sample",
                    "sampleSizeValue": ev.get("volume_m3"),
                    "sampleSizeUnit": "m^3",
                }
            )

    with occ_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "occurrenceID",
                "eventID",
                "organismQuantity",
                "organismQuantityType",
                "occurrenceStatus",
                "lifeStage",
            ],
        )
        writer.writeheader()
        for occ in occurrences:
            oid = f"{occ['sample_id']}:{occ['taxon']}"
            writer.writerow(
                {
                    "occurrenceID": oid,
                    "eventID": occ["sample_id"],
                    "organismQuantity": occ["count"],
                    "organismQuantityType": "individuals",
                    "occurrenceStatus": occ["occurrence_status"],
                    "lifeStage": occ["life_stage"],
                }
            )

    with emof_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["occurrenceID", "measurementTypeID", "measurementValue", "measurementUnit"],
        )
        writer.writeheader()
        for occ in occurrences:
            oid = f"{occ['sample_id']}:{occ['taxon']}"
            density = occ.get("density")
            if density is not None:
                writer.writerow(
                    {
                        "occurrenceID": oid,
                        "measurementTypeID": "egg_density_per_m3",
                        "measurementValue": density,
                        "measurementUnit": "count/m^3",
                    }
                )

    return event_path, occ_path, emof_path
