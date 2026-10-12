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
    from fishai.ingestion.adult.specimen_fetch import iter_halfyear_windows
    from fishai.ingestion.biology.cps_nearshore.fetch import (
        OCEANVIEW_NEARSHORE_SET_CATCH_BASE,
        fetch_cps_nearshore_set_catch,
        raw_dir as near_raw_dir,
    )
    from fishai.ingestion.biology.cps_nearshore.pipeline import pilot_bbox_from_manifest, sync_cps_nearshore_set_catch
    from fishai.ingestion.biology.cps_trawl.pipeline import pilot_bbox_from_manifest as trawl_bbox, sync_cps_trawl_haul_catch

    bbox = trawl_bbox()
    print("sync trawl haul catch (pilot bbox)...")
    trawl_qc = sync_cps_trawl_haul_catch(
        date(2003, 7, 9),
        date(2026, 12, 31),
        fetch=True,
        bbox=bbox,
    )
    print(f"trawl hauls={trawl_qc['n_hauls']} catch_rows={trawl_qc['n_catch_rows']}")

    near_bbox = pilot_bbox_from_manifest()
    raw = near_raw_dir()
    print("sync nearshore set catch (oceanview, half-year windows)...")
    fetch_cps_nearshore_set_catch(
        date(2019, 6, 21),
        date(2026, 12, 31),
        near_bbox,
        raw,
        erddap_base=OCEANVIEW_NEARSHORE_SET_CATCH_BASE,
        window_fn=iter_halfyear_windows,
    )
    near_qc = sync_cps_nearshore_set_catch(
        date(2019, 6, 21),
        date(2026, 12, 31),
        bbox=near_bbox,
        download=False,
    )
    print(f"nearshore sets raw_rows={near_qc['raw_rows']}")

    import subprocess

    return subprocess.call(
        [sys.executable, str(REPO_ROOT / "scripts" / "fetch_adult_cps_specimens.py"), "--nearshore-half-year"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
