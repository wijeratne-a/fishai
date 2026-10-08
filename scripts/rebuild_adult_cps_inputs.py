#!/usr/bin/env python3
"""Fetch public ERDDAP catch + specimen inputs for the adult CPS training table."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def main() -> int:
    import subprocess

    odp_script = REPO_ROOT / "scripts" / "fetch_odp_adult_cps_bulk.py"
    print("ensure SWFSC ODP bulk CSVs (public GCS mirror)...")
    rc = subprocess.call([sys.executable, str(odp_script)])
    if rc != 0:
        return rc

    from fishai.ingestion.biology.cps_nearshore.pipeline import pilot_bbox_from_manifest, sync_cps_nearshore_set_catch
    from fishai.ingestion.biology.cps_trawl.pipeline import pilot_bbox_from_manifest as trawl_bbox, sync_cps_trawl_haul_catch

    bbox = trawl_bbox()
    print("sync trawl haul catch (pilot bbox)...")
    trawl_qc = sync_cps_trawl_haul_catch(
        date(2003, 7, 9),
        date(2026, 12, 31),
        fetch=False,
        bbox=bbox,
    )
    print(f"trawl hauls={trawl_qc['n_hauls']} catch_rows={trawl_qc['n_catch_rows']}")

    near_bbox = pilot_bbox_from_manifest()
    print("sync nearshore set catch (ODP bulk)...")
    near_qc = sync_cps_nearshore_set_catch(
        date(2019, 6, 21),
        date(2026, 12, 31),
        bbox=near_bbox,
        download=False,
    )
    print(f"nearshore sets raw_rows={near_qc['raw_rows']}")

    return subprocess.call(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "fetch_adult_cps_specimens.py"),
            "--odp-bulk",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
