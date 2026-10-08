#!/usr/bin/env python3
"""Sample issued WCOFS covariates for adult sardine 24h holdout rows (public PDS only)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

WCOFS_ARCHIVE_START = dt.date(2024, 7, 1)
DYN_Z_COLS = ("temp_3m_z", "sal_3m_z", "mld_z", "sst_grad_z", "dist_front_z")
UPSTREAM = {
    "temp_3m_z": "T3m",
    "sal_3m_z": "S3m",
    "mld_z": "MLD_m",
    "sst_grad_z": "sst_grad",
    "dist_front_z": "front_distance_km",
}


def _nearest_cell(lat: float, lon: float, lat_axis: np.ndarray, lon_axis: np.ndarray) -> tuple[int, int]:
    from fishai.ingestion.physics.cufes_training_covariates import normalize_lon_for_axis

    lon = normalize_lon_for_axis(lon, lon_axis)
    j = int(np.argmin(np.abs(lat_axis - lat)))
    i = int(np.argmin(np.abs(lon_axis - lon)))
    return j, i


def _event_lat_lon(row: pd.Series) -> tuple[float, float]:
    lat0, lon0 = float(row["lat"]), float(row["lon"])
    lat1 = row.get("stop_lat")
    lon1 = row.get("stop_lon")
    if pd.notna(lat1) and pd.notna(lon1):
        return (lat0 + float(lat1)) / 2.0, (lon0 + float(lon1)) / 2.0
    return lat0, lon0


def _resolve_issued_key(day: dt.date, lead: str, list_keys) -> str:
    """Public PDS key for an issued forecast lead.

    Prefer a ROMS ``fields`` object (new or legacy name). When that product is
    not published, use ``regulargrid.{lead}``, which is the issued forecast
    file on later cycles (standard depth levels, not s-coordinates).
    """
    from fishai.ingestion.physics.wcofs_pds_store import (
        CycleNotAvailable,
        layout_prefixes,
        resolve_fields_key,
    )

    try:
        return resolve_fields_key(day, lead, list_keys)
    except CycleNotAvailable:
        pass
    ymd = day.strftime("%Y%m%d")
    bases = {
        f"wcofs.t03z.{ymd}.regulargrid.{lead}.nc",
        f"nos.wcofs.regulargrid.{lead}.{ymd}.t03z.nc",
    }
    matches: list[str] = []
    for prefix in layout_prefixes(day):
        for key in list_keys(prefix):
            if key.rsplit("/", 1)[-1] in bases:
                matches.append(key)
    unique = sorted(set(matches))
    if len(unique) == 1:
        return unique[0]
    if not unique:
        raise CycleNotAvailable(f"no WCOFS forecast {lead} for {day.isoformat()}")
    raise CycleNotAvailable(
        f"ambiguous WCOFS forecast {lead} for {day.isoformat()}: {unique[:5]}"
    )


def _open_wcofs_bytes(data: bytes):
    from fishai.ingestion.physics.sources.wcofs import _open_dataset_from_bytes

    return _open_dataset_from_bytes(data)


def _resolve_lead(cutoff: dt.date, h_days: int, cycle_exists) -> tuple[dt.date, str, str | None]:
    from fishai.ingestion.physics.sources import wcofs as wcofs_src
    from fishai.ingestion.physics.wcofs_daily import resolve_lead_for_offset

    offset_h = h_days * 24
    tag = f"f{offset_h:03d}"
    if tag not in wcofs_src.FORECAST_LEADS:
        return cutoff, tag, "lead_out_of_range"
    if cycle_exists(cutoff):
        return cutoff, tag, None
    lp = resolve_lead_for_offset(
        cutoff,
        offset_h,
        primary_available=False,
        cycle_exists_fn=cycle_exists,
        max_missed_cycles=5,
    )
    if lp is None:
        return cutoff, tag, "missing_operational_cycle"
    return lp.cycle_date, lp.lead_tag, lp.fallback


def _fetch_wcofs_fields(cycle: dt.date, lead: str, bbox: tuple[float, float, float, float]):
    """Return (dataset, s3_key, error). error is None on success."""
    from fishai.ingestion.physics.http_util import get_bytes
    from fishai.ingestion.physics.sources.wcofs import DEFAULT_SUBSET_MARGIN_CELLS, _subset_bbox
    from fishai.ingestion.physics.wcofs_pds_s3_list import list_keys_under_prefix
    from fishai.ingestion.physics.wcofs_pds_store import CycleNotAvailable, _s3_url

    try:
        key = _resolve_issued_key(cycle, lead, list_keys_under_prefix)
    except CycleNotAvailable:
        return None, None, "missing_wcofs_object"
    url = _s3_url(key)
    try:
        data = get_bytes(url, extra_cache_key=f"{cycle.isoformat()}_{lead}")
        ds = _open_wcofs_bytes(data)
        ds.attrs["wcofs_s3_key"] = key
        if "lat_rho" in ds:
            ds = _subset_bbox(ds, bbox, margin_cells=DEFAULT_SUBSET_MARGIN_CELLS)
        return ds, key, None
    except Exception as exc:  # noqa: BLE001
        return None, key, f"fetch_failed:{type(exc).__name__}:{exc}"[:240]


def _values_from_fields(fields: dict, lat: float, lon: float, lat_dst, lon_dst) -> dict[str, float] | None:
    j, i = _nearest_cell(lat, lon, lat_dst, lon_dst)
    out: dict[str, float] = {}
    for z_col, raw in UPSTREAM.items():
        val = float(fields[raw][j, i])
        if not np.isfinite(val):
            return None
        out[z_col] = val
    return out


def _sample_roms_fields(ds, lat: float, lon: float, config: dict) -> dict[str, float] | None:
    from fishai.ingestion.physics.wcofs_glorys_overlap import (
        glorys_grid_from_config,
        wcofs_covariate_arrays_on_glorys_grid,
    )

    lat_dst, lon_dst = glorys_grid_from_config(config)
    fields = wcofs_covariate_arrays_on_glorys_grid(ds, lat_dst, lon_dst, config)
    return _values_from_fields(fields, lat, lon, lat_dst, lon_dst)


def _regulargrid_fields(ds, config: dict) -> dict | None:
    """Bin an issued regular-grid forecast onto the GLORYS grid, then the shared covariates.

    Later WCOFS cycles publish ``regulargrid.fHHH`` instead of ROMS ``fields.fHHH``.
    Depth is already meters, positive down. Source points inside each GLORYS cell
    are averaged with equal weight. This is still an issued WCOFS forecast.
    """
    from fishai.ingestion.physics.wcofs_glorys_grid import (
        WcofsGlorysGrid,
        compute_wcofs_covariates_on_glorys_grid,
    )
    from fishai.ingestion.physics.wcofs_glorys_overlap import depth_grid_m, glorys_grid_from_config

    lat_dst, lon_dst = glorys_grid_from_config(config)
    depth_grid = depth_grid_m(config)
    lat2 = np.asarray(ds["Latitude"].values, dtype=float)
    lon2 = np.asarray(ds["Longitude"].values, dtype=float)
    lon2 = np.where(lon2 > 180.0, lon2 - 360.0, lon2)
    mask = np.asarray(ds["mask"].values) == 1
    depth_src = np.asarray(ds["Depth"].values, dtype=float)
    temp = np.asarray(ds["temp"].values, dtype=float)
    salt = np.asarray(ds["salt"].values, dtype=float)
    if temp.ndim == 4:
        temp = temp[0]
        salt = salt[0]
    pad = 0.2
    window = (
        (lat2 >= float(lat_dst.min()) - pad)
        & (lat2 <= float(lat_dst.max()) + pad)
        & (lon2 >= float(lon_dst.min()) - pad)
        & (lon2 <= float(lon_dst.max()) + pad)
        & mask
    )
    jj, ii = np.where(window)
    if jj.size == 0:
        return None
    j_idx = np.abs(lat2[jj, ii, None] - lat_dst[None, :]).argmin(axis=1)
    i_idx = np.abs(lon2[jj, ii, None] - lon_dst[None, :]).argmin(axis=1)
    order = np.argsort(depth_src)
    z = depth_src[order]
    nj, ni, nz = lat_dst.size, lon_dst.size, depth_grid.size
    temp_sum = np.zeros((nj, ni, nz), dtype=float)
    salt_sum = np.zeros((nj, ni, nz), dtype=float)
    counts = np.zeros((nj, ni), dtype=float)
    for n in range(jj.size):
        tcol = temp[order, jj[n], ii[n]]
        scol = salt[order, jj[n], ii[n]]
        finite = np.isfinite(tcol) & np.isfinite(scol)
        if int(finite.sum()) < 2:
            continue
        t_i = np.interp(depth_grid, z[finite], tcol[finite], left=np.nan, right=np.nan)
        s_i = np.interp(depth_grid, z[finite], scol[finite], left=np.nan, right=np.nan)
        j = int(j_idx[n])
        i = int(i_idx[n])
        temp_sum[j, i] += np.where(np.isfinite(t_i), t_i, 0.0)
        salt_sum[j, i] += np.where(np.isfinite(s_i), s_i, 0.0)
        counts[j, i] += 1.0
    good = counts > 0
    temp_g = np.full((nj, ni, nz), np.nan, dtype=float)
    salt_g = np.full((nj, ni, nz), np.nan, dtype=float)
    temp_g[good] = temp_sum[good] / counts[good, None]
    salt_g[good] = salt_sum[good] / counts[good, None]
    wet = np.broadcast_to(good[:, :, None], (nj, ni, nz)).astype(float).copy()
    wet[~good] = 0.0
    gridded = WcofsGlorysGrid(
        lat=np.asarray(lat_dst, dtype=float),
        lon=np.asarray(lon_dst, dtype=float),
        depth_m=np.asarray(depth_grid, dtype=float),
        temp=temp_g,
        salt=salt_g,
        wet_fraction=wet,
    )
    return compute_wcofs_covariates_on_glorys_grid(gridded)


def _sample_covariates(ds, lat: float, lon: float, config: dict) -> dict[str, float] | None:
    if "lat_rho" in ds and "temp" in ds:
        return _sample_roms_fields(ds, lat, lon, config)
    if "Latitude" in ds and "temp" in ds and "Depth" in ds:
        from fishai.ingestion.physics.wcofs_glorys_overlap import glorys_grid_from_config

        fields = _regulargrid_fields(ds, config)
        if fields is None:
            return None
        lat_dst, lon_dst = glorys_grid_from_config(config)
        return _values_from_fields(fields, lat, lon, lat_dst, lon_dst)
    return None


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
    from fishai.ingestion.physics.wcofs_pds_store import cycle_available
    from fishai.ingestion.sources import load_sources_manifest

    parser = argparse.ArgumentParser(description="WCOFS operational covariates for adult sardine 24h holdout")
    parser.add_argument("--cutoffs-json", required=True, help="JSON with cutoffs list (YYYY-MM-DD)")
    parser.add_argument(
        "--training-table",
        default=str(REPO_ROOT / "data/processed/adult_cps/adult_cps_training_table.parquet"),
    )
    parser.add_argument(
        "--events-table",
        default=str(REPO_ROOT / "data/processed/adult_cps/adult_cps_events.parquet"),
    )
    parser.add_argument(
        "--scientific-name",
        default="Sardinops sagax",
        help="Species filter (must match adult_cps_sardine.yaml)",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    with Path(args.cutoffs_json).open(encoding="utf-8") as handle:
        cutoffs = [dt.date.fromisoformat(c) for c in json.load(handle)["cutoffs"]]

    train = pd.read_parquet(args.training_table)
    train = train[train["species"] == args.scientific_name].copy()
    events = pd.read_parquet(args.events_table)
    ev_cols = [
        c
        for c in (
            "event_id",
            "start_time",
            "start_latitude",
            "start_longitude",
            "stop_latitude",
            "stop_longitude",
            "lat",
            "lon",
            "stop_lat",
            "stop_lon",
        )
        if c in events.columns
    ]
    train = train.merge(events[ev_cols], on="event_id", how="left")
    time_col = "start_time" if "start_time" in train.columns else "time"
    train["event_day"] = pd.to_datetime(train[time_col], utc=True).dt.date
    if "lat" not in train.columns and "start_latitude" in train.columns:
        train["lat"] = train["start_latitude"]
        train["lon"] = train["start_longitude"]
        train["stop_lat"] = train["stop_latitude"]
        train["stop_lon"] = train["stop_longitude"]

    manifest = load_sources_manifest()
    pilot = manifest.get("pilot") or {}
    box = pilot.get("bbox") or {}
    bbox = (float(box["lat_min"]), float(box["lat_max"]), float(box["lon_min"]), float(box["lon_max"]))
    config = load_overlap_config()

    prepared: dict[tuple[dt.date, str], tuple] = {}

    def _prepared_fields(cycle: dt.date, lead: str):
        token = (cycle, lead)
        if token in prepared:
            return prepared[token]
        ds, key, fetch_err = _fetch_wcofs_fields(cycle, lead, bbox)
        if ds is None:
            prepared[token] = (None, key, fetch_err or "missing_wcofs_object")
            return prepared[token]
        try:
            from fishai.ingestion.physics.wcofs_glorys_overlap import glorys_grid_from_config

            lat_dst, lon_dst = glorys_grid_from_config(config)
            if "lat_rho" in ds and "temp" in ds:
                from fishai.ingestion.physics.wcofs_glorys_overlap import (
                    wcofs_covariate_arrays_on_glorys_grid,
                )

                fields = wcofs_covariate_arrays_on_glorys_grid(ds, lat_dst, lon_dst, config)
            elif "Latitude" in ds and "temp" in ds and "Depth" in ds:
                fields = _regulargrid_fields(ds, config)
                if fields is None:
                    prepared[token] = (None, key, "non_finite_wcofs_cell")
                    return prepared[token]
            else:
                prepared[token] = (None, key, "unsupported_wcofs_product")
                return prepared[token]
            prepared[token] = (fields, key, None)
            return prepared[token]
        except Exception as exc:  # noqa: BLE001
            prepared[token] = (None, key, f"fetch_failed:{type(exc).__name__}:{exc}"[:240])
            return prepared[token]
        finally:
            ds.close()

    rows: list[dict] = []
    for cutoff in cutoffs:
        hold = train[train["event_day"].isin([cutoff + dt.timedelta(days=h) for h in (1, 2, 3)])]
        for _, ev in hold.iterrows():
            h_days = int((ev["event_day"] - cutoff).days)
            lat, lon = _event_lat_lon(ev)
            base = {
                "cutoff": cutoff.isoformat(),
                "event_id": ev["event_id"],
                "event_day": ev["event_day"].isoformat(),
                "horizon_days": h_days,
                "lat": lat,
                "lon": lon,
            }
            if cutoff < WCOFS_ARCHIVE_START:
                rows.append(
                    {
                        **base,
                        "physics_source": "damped_anomaly_proxy",
                        "operational_claim": "NOT_ISSUED_FORECAST",
                        "proxy_reason": "coverage_forced_proxy",
                        "wcofs_s3_key": "",
                        "wcofs_lead_tag": "",
                        **{c: np.nan for c in DYN_Z_COLS},
                    }
                )
                continue
            cycle, lead, fallback = _resolve_lead(cutoff, h_days, cycle_available)
            fields, key, fetch_err = _prepared_fields(cycle, lead)
            if fields is None:
                rows.append(
                    {
                        **base,
                        "physics_source": "damped_anomaly_proxy",
                        "operational_claim": "NOT_ISSUED_FORECAST",
                        "proxy_reason": fetch_err or "missing_wcofs_object",
                        "wcofs_s3_key": key or "",
                        "wcofs_lead_tag": lead,
                        **{c: np.nan for c in DYN_Z_COLS},
                    }
                )
                continue
            from fishai.ingestion.physics.wcofs_glorys_overlap import glorys_grid_from_config

            lat_dst, lon_dst = glorys_grid_from_config(config)
            sampled = _values_from_fields(fields, lat, lon, lat_dst, lon_dst)
            if sampled is None:
                rows.append(
                    {
                        **base,
                        "physics_source": "damped_anomaly_proxy",
                        "operational_claim": "NOT_ISSUED_FORECAST",
                        "proxy_reason": "non_finite_wcofs_cell",
                        "wcofs_s3_key": key or "",
                        "wcofs_lead_tag": lead,
                        **{c: np.nan for c in DYN_Z_COLS},
                    }
                )
                continue
            rows.append(
                {
                    **base,
                    "physics_source": "wcofs_issued_forecast",
                    "operational_claim": "ISSUED_FORECAST",
                    "proxy_reason": fallback or "",
                    "wcofs_s3_key": key or "",
                    "wcofs_lead_tag": lead,
                    **sampled,
                }
            )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
