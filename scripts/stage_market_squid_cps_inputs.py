#!/usr/bin/env python3
"""Stage processed CPS catch + specimen parquets via GCS mirror (Phase 1 market squid)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def main() -> int:
    import pyarrow as pa
    import pyarrow.parquet as pq

    from fishai.ingestion.adult.constants import NEARSHORE_SPECIMENS_PATH, TRAWL_SPECIMENS_PATH
    from fishai.ingestion.adult.inport_csv import (
        normalize_nearshore_specimen_row,
        normalize_nearshore_set_catch_row,
        normalize_trawl_haul_catch_row,
        normalize_trawl_specimen_row,
        read_inport_csv,
    )
    from fishai.ingestion.adult.specimens import normalize_nearshore_specimens, normalize_trawl_specimens
    from fishai.ingestion.biology.cps_nearshore.pipeline import (
        build_set_species_matrix,
        processed_dir as near_processed_dir,
        write_parquet_contracts as near_write_parquet,
        write_qc_report as near_write_qc,
    )
    from fishai.ingestion.biology.cps_nearshore.zero_frame import DEFAULT_EVIDENCE_PATH as NEAR_EVIDENCE
    from fishai.ingestion.biology.cps_nearshore.transform import transform_rows as near_transform
    from fishai.ingestion.biology.cps_trawl.pipeline import (
        build_haul_species_matrix,
        processed_dir as trawl_processed_dir,
        write_parquet_contracts as trawl_write_parquet,
        write_qc_report as trawl_write_qc,
    )
    from fishai.ingestion.biology.cps_trawl.zero_frame import DEFAULT_EVIDENCE_PATH as TRAWL_EVIDENCE
    from fishai.ingestion.biology.cps_trawl.transform import transform_rows as trawl_transform

    gcs = REPO_ROOT / "scripts" / "fetch_adult_cps_gcs_mirror.py"
    print("fetch GCS mirror CSVs...")
    subprocess.check_call([sys.executable, str(gcs)])

    trawl_csv = REPO_ROOT / "data" / "raw" / "swfsc_cps_trawl_haul_catch" / "FRDCPSTrawlLHHaulCatch_2003.csv"
    near_csv = REPO_ROOT / "data" / "raw" / "swfsc_cps_nearshore_set_catch" / "cps_nearshore_set_catch_gcs.csv"

    print("transform trawl InPort CSV...")
    trawl_raw = read_inport_csv(trawl_csv, normalize_trawl_haul_catch_row)
    trawl_t = trawl_transform(trawl_raw)
    trawl_matrix = build_haul_species_matrix(trawl_t.hauls, trawl_t.catch, evidence_path=TRAWL_EVIDENCE)
    trawl_out = trawl_processed_dir()
    trawl_write_parquet(trawl_t.hauls, trawl_t.catch, trawl_matrix, trawl_out)
    trawl_write_qc(trawl_t.qc_report, trawl_out)
    print(f"trawl hauls={len(trawl_t.hauls)} catch_rows={len(trawl_t.catch)}")

    print("transform nearshore InPort CSV...")
    near_raw = read_inport_csv(near_csv, normalize_nearshore_set_catch_row)
    near_t = near_transform(near_raw)
    near_matrix = build_set_species_matrix(near_t.sets, near_t.catch, evidence_path=NEAR_EVIDENCE)
    near_out = near_processed_dir()
    near_write_parquet(near_t.sets, near_t.catch, near_matrix, near_out)
    near_write_qc({"raw_rows": len(near_raw), "qc_flags": near_t.qc_flags}, near_out)
    print(f"nearshore sets={len(near_t.sets)} catch_rows={len(near_t.catch)}")

    trawl_spec = REPO_ROOT / "data" / "raw" / "swfsc_cps_trawl_haul_catch" / "specimens" / "FRDCPSTrawlLHSpecimen_gcs.csv"
    near_spec = (
        REPO_ROOT / "data" / "raw" / "swfsc_cps_nearshore_set_catch" / "specimens" / "FRDCPSNearshoreSpecimen_gcs.csv"
    )
    trawl_rows = read_inport_csv(trawl_spec, normalize_trawl_specimen_row)
    near_rows = read_inport_csv(near_spec, normalize_nearshore_specimen_row)
    trawl_df = normalize_trawl_specimens(trawl_rows)
    near_df = normalize_nearshore_specimens(near_rows)
    TRAWL_SPECIMENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(trawl_df), TRAWL_SPECIMENS_PATH)
    NEARSHORE_SPECIMENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(near_df), NEARSHORE_SPECIMENS_PATH)
    print(f"trawl_specimens rows={len(trawl_df)} nearshore_specimens rows={len(near_df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
