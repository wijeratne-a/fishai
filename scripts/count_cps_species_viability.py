#!/usr/bin/env python3
"""Count non–presence-only catch presences for a CPS species (viability gate)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def _is_presence_trawl(row: dict) -> bool:
    from fishai.ingestion.biology.cps_trawl.catch import is_presence_only, parse_catch_row

    if is_presence_only(row.get("presence_only")):
        return False
    parsed = parse_catch_row(row)
    if parsed is None:
        return False
    w = parsed.weight_kg
    if w is not None and w > 0:
        return True
    c = parsed.count_raised_est if parsed.count_raised_est is not None else parsed.subsample_count
    return c is not None and c > 0


def _is_presence_nearshore(row: dict) -> bool:
    from fishai.ingestion.biology.cps_nearshore.catch import parse_catch_row

    parsed = parse_catch_row(row)
    if parsed is None:
        return False
    w = parsed.total_weight_kg
    if w is not None and w > 0:
        return True
    n = parsed.total_number
    return n is not None and n > 0


def _species_match(row: dict, scientific_name: str, itis_tsn: int | None) -> bool:
    name = str(row.get("scientific_name") or row.get("species") or "").strip()
    if name == scientific_name:
        return True
    if itis_tsn is not None:
        raw_tsn = row.get("itis_tsn")
        try:
            if raw_tsn is not None and int(float(str(raw_tsn).strip())) == itis_tsn:
                return True
        except (TypeError, ValueError):
            pass
    return False


def count_from_processed(
    *,
    scientific_name: str,
    itis_tsn: int | None,
    trawl_catch_path: Path,
    nearshore_catch_path: Path,
) -> dict[str, int]:
    import pandas as pd

    out = {
        "trawl_catch_rows_species": 0,
        "trawl_presence_only_excluded": 0,
        "trawl_non_presence_only_presences": 0,
        "nearshore_catch_rows_species": 0,
        "nearshore_non_presence_only_presences": 0,
        "total_non_presence_only_presences": 0,
    }

    if trawl_catch_path.is_file():
        catch = pd.read_parquet(trawl_catch_path)
        for _, row in catch.iterrows():
            if str(row.get("species") or "").strip() != scientific_name:
                continue
            out["trawl_catch_rows_species"] += 1
            if bool(row.get("presence_only")):
                out["trawl_presence_only_excluded"] += 1
                continue
            w = row.get("weight_kg")
            c = row.get("count_raised_est")
            if c is None or (hasattr(c, "__float__") and pd.isna(c)):
                c = row.get("subsample_count")
            has_w = w is not None and pd.notna(w) and float(w) > 0
            has_c = c is not None and pd.notna(c) and int(c) > 0
            if has_w or has_c:
                out["trawl_non_presence_only_presences"] += 1

    if nearshore_catch_path.is_file():
        catch = pd.read_parquet(nearshore_catch_path)
        name_col = "scientific_name" if "scientific_name" in catch.columns else "species"
        sub = catch[catch[name_col].astype(str).str.strip() == scientific_name]
        out["nearshore_catch_rows_species"] = len(sub)
        for _, row in sub.iterrows():
            w = row.get("total_weight_kg")
            n = row.get("total_number")
            has_w = w is not None and pd.notna(w) and float(w) > 0
            has_n = n is not None and pd.notna(n) and int(n) > 0
            if has_w or has_n:
                out["nearshore_non_presence_only_presences"] += 1

    out["total_non_presence_only_presences"] = (
        out["trawl_non_presence_only_presences"] + out["nearshore_non_presence_only_presences"]
    )
    return out


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.adult.constants import (
        NEARSHORE_CATCH_PATH,
        TRAWL_CATCH_PATH,
    )

    parser = argparse.ArgumentParser(description="CPS species viability counts (pilot processed catch)")
    parser.add_argument("--scientific-name", default="Scomber japonicus")
    parser.add_argument("--itis-tsn", type=int, default=172409)
    parser.add_argument("--trawl-catch", type=Path, default=TRAWL_CATCH_PATH)
    parser.add_argument("--nearshore-catch", type=Path, default=NEARSHORE_CATCH_PATH)
    args = parser.parse_args(argv)

    counts = count_from_processed(
        scientific_name=args.scientific_name,
        itis_tsn=args.itis_tsn,
        trawl_catch_path=args.trawl_catch,
        nearshore_catch_path=args.nearshore_catch,
    )
    for key, val in counts.items():
        print(f"{key}={val}")
    total = counts["total_non_presence_only_presences"]
    if total < 100:
        print(f"verdict=species_not_viable")
    elif total < 150:
        print("verdict=marginal_proceed")
    else:
        print("verdict=viable_proceed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
