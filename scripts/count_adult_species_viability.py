#!/usr/bin/env python3
"""Count non–presence-only catch presences for an adult CPS species (viability gate)."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

# Accepted scientific names (ITIS / ERDDAP spellings).
MARKET_SQUID_NAMES = frozenset(
    {
        "Doryteuthis opalescens",
        "Loligo opalescens",
    }
)


def _positive(val) -> bool:
    if val is None:
        return False
    try:
        f = float(val)
    except (TypeError, ValueError):
        return False
    if math.isnan(f):
        return False
    return f > 0


def _is_presence_trawl(row) -> bool:
    from fishai.ingestion.biology.cps_trawl.catch import is_presence_only

    if is_presence_only(row.get("presence_only")):
        return False
    if _positive(row.get("weight_kg")):
        return True
    for col in ("count_raised_est", "subsample_count"):
        if _positive(row.get(col)):
            return True
    return False


def _is_presence_nearshore(row) -> bool:
    if _positive(row.get("total_weight_kg")):
        return True
    if _positive(row.get("total_number")):
        return True
    return False


def _match_species(name: str, aliases: frozenset[str]) -> bool:
    return str(name or "").strip() in aliases


def main(argv: list[str] | None = None) -> int:
    import pandas as pd

    from fishai.ingestion.adult.constants import (
        NEARSHORE_CATCH_PATH,
        NEARSHORE_SETS_PATH,
        TRAWL_CATCH_PATH,
        TRAWL_HAULS_PATH,
    )
    from fishai.ingestion.biology.cps_trawl.pipeline import pilot_bbox_from_manifest
    from fishai.ingestion.adult.specimens import (
        median_length_by_event_species,
    )
    from fishai.ingestion.adult.constants import NEARSHORE_SPECIMENS_PATH, TRAWL_SPECIMENS_PATH

    parser = argparse.ArgumentParser(description="Adult CPS species viability counts")
    parser.add_argument(
        "--species",
        default="Doryteuthis opalescens",
        help="Canonical scientific name (used in output JSON)",
    )
    parser.add_argument(
        "--alias",
        action="append",
        default=[],
        help="Additional scientific_name spellings to match in catch tables",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    aliases = frozenset({args.species, *args.alias, *MARKET_SQUID_NAMES})
    bbox = pilot_bbox_from_manifest()

    def in_pilot(lat: float | None, lon: float | None) -> bool:
        if lat is None or lon is None or pd.isna(lat) or pd.isna(lon):
            return False
        return (
            bbox.lat_min <= float(lat) <= bbox.lat_max
            and bbox.lon_min <= float(lon) <= bbox.lon_max
        )

    trawl_pres = 0
    near_pres = 0
    trawl_rows = 0
    near_rows = 0

    if TRAWL_CATCH_PATH.is_file() and TRAWL_HAULS_PATH.is_file():
        trawl = pd.read_parquet(TRAWL_CATCH_PATH)
        hauls = pd.read_parquet(TRAWL_HAULS_PATH)[["haul_id", "lat", "lon"]]
        trawl = trawl.merge(hauls, on="haul_id", how="left")
        trawl = trawl[trawl.apply(lambda r: in_pilot(r.get("lat"), r.get("lon")), axis=1)]
        trawl_rows = len(trawl)
        for _, row in trawl.iterrows():
            if not _match_species(str(row.get("species") or row.get("scientific_name")), aliases):
                continue
            if _is_presence_trawl(row):
                trawl_pres += 1
    else:
        trawl = pd.DataFrame()

    if NEARSHORE_CATCH_PATH.is_file() and NEARSHORE_SETS_PATH.is_file():
        near = pd.read_parquet(NEARSHORE_CATCH_PATH)
        sets = pd.read_parquet(NEARSHORE_SETS_PATH)[["set_id", "latitude", "longitude"]]
        near = near.merge(sets, on="set_id", how="left")
        near = near[near.apply(lambda r: in_pilot(r.get("latitude"), r.get("longitude")), axis=1)]
        near_rows = len(near)
        for _, row in near.iterrows():
            if not _match_species(str(row.get("scientific_name")), aliases):
                continue
            if _is_presence_nearshore(row):
                near_pres += 1
    else:
        near = pd.DataFrame()

    total_pres = trawl_pres + near_pres

    specimen_stats: dict[str, int | float] = {}
    for label, path in (("trawl", TRAWL_SPECIMENS_PATH), ("nearshore", NEARSHORE_SPECIMENS_PATH)):
        if not path.is_file():
            specimen_stats[f"{label}_specimen_rows"] = 0
            specimen_stats[f"{label}_specimen_matched"] = 0
            continue
        sp = pd.read_parquet(path)
        specimen_stats[f"{label}_specimen_rows"] = len(sp)
        if "scientific_name" in sp.columns:
            m = sp["scientific_name"].astype(str).str.strip().isin(aliases)
            specimen_stats[f"{label}_specimen_matched"] = int(m.sum())
            sub = sp.loc[m]
            if not sub.empty:
                for col in ("standard_length", "fork_length", "total_length"):
                    if col in sub.columns:
                        non_null = sub[col].notna().sum()
                        specimen_stats[f"{label}_{col}_non_null"] = int(non_null)

    if TRAWL_SPECIMENS_PATH.is_file():
        trawl_sp = pd.read_parquet(TRAWL_SPECIMENS_PATH)
        if "species" in trawl_sp.columns:
            msp = trawl_sp[trawl_sp["species"].astype(str).str.strip().isin(aliases)]
            specimen_stats["trawl_specimen_length_rows"] = len(msp)
            if not msp.empty:
                med = median_length_by_event_species(msp)
                specimen_stats["trawl_events_with_median_length"] = len(med)

    out = {
        "species": args.species,
        "pilot_bbox": {
            "lat_min": bbox.lat_min,
            "lat_max": bbox.lat_max,
            "lon_min": bbox.lon_min,
            "lon_max": bbox.lon_max,
        },
        "aliases_matched": sorted(aliases),
        "trawl_catch_rows_pilot": trawl_rows,
        "nearshore_catch_rows_pilot": near_rows,
        "trawl_non_presence_only_presences": trawl_pres,
        "nearshore_non_presence_only_presences": near_pres,
        "total_non_presence_only_presences": total_pres,
        "viability": (
            "not_viable"
            if total_pres < 100
            else ("marginal" if total_pres < 150 else "proceed")
        ),
        **specimen_stats,
    }

    text = json.dumps(out, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
