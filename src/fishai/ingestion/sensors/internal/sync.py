"""Orchestrate sensor sync jobs."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from fishai.ingestion.sources import require_approved
from fishai.ingestion.sensors.internal.archive import append_hfr_zarr, write_glider_parquet, write_ndbc_parquet
from fishai.ingestion.sensors.internal.config import load_sensors_config, pilot_bbox
from fishai.ingestion.sensors.internal.http import get_http_client
from fishai.ingestion.sensors.internal.qc import qc_glider_profiles, qc_hfradar, qc_ndbc
from fishai.ingestion.sensors.sources.gliders import fetch_profiles, list_active
from fishai.ingestion.sensors.sources.hfradar import closed_hour_window, fetch_hfr
from fishai.ingestion.sensors.sources.ndbc import fetch_ndbc, list_stations


def parse_since(since: str, now: datetime | None = None) -> datetime:
    now = now or datetime.now(timezone.utc)
    m = re.fullmatch(r"(\d+)(h|d)", since.strip().lower())
    if not m:
        raise ValueError(f"invalid since spec: {since!r}")
    n, unit = int(m.group(1)), m.group(2)
    delta = timedelta(hours=n) if unit == "h" else timedelta(days=n)
    return now - delta


def run_sync(since: str = "24h") -> dict:
    cfg = load_sensors_config()
    bbox = pilot_bbox(cfg)
    client = get_http_client(
        min_interval_s=float(cfg["http"]["min_interval_s"]),
        timeout_s=float(cfg["http"]["timeout_s"]),
        max_retries=int(cfg["http"]["max_retries"]),
        backoff_base_s=float(cfg["http"]["backoff_base_s"]),
    )
    budget = int(cfg["http"]["daily_request_budget"])
    report: dict = {"sources": {}}

    require_approved("sccoos_hfr")
    t0, t1 = closed_hour_window(hours=24)
    hfr = fetch_hfr(t0, t1, bbox, client=client)
    hfr = qc_hfradar(hfr, cfg["qc"])
    zpath = append_hfr_zarr(hfr, cfg)
    report["sources"]["sccoos_hfr"] = {"rows": int(hfr.sizes.get("time", 0)), "zarr": str(zpath)}

    if client.request_count_today() >= budget:
        report["budget_exhausted"] = True
        return report

    require_approved("ndbc_met")
    since_dt = parse_since(since)
    stations = list_stations(bbox, client=client)
    ndbc = fetch_ndbc(since_dt, datetime.now(timezone.utc), bbox, stations, client=client)
    ndbc = qc_ndbc(ndbc, cfg["qc"])
    pq = write_ndbc_parquet(ndbc, datetime.now(timezone.utc), cfg)
    report["sources"]["ndbc_met"] = {"rows": len(ndbc), "stations": len(stations), "parquet": str(pq) if pq else None}

    try:
        require_approved("ioos_glider_dac")
    except Exception as exc:
        report["sources"]["ioos_glider_dac"] = {"skipped": str(exc)}
        return report

    if client.request_count_today() >= budget:
        report["budget_exhausted"] = True
        return report

    active = list_active(bbox, since_dt, client=client)
    glider_paths = []
    for ds_id in active:
        if client.request_count_today() >= budget:
            break
        prof = fetch_profiles(ds_id, since_dt, datetime.now(timezone.utc), client=client)
        prof = qc_glider_profiles(prof, cfg["qc"])
        path = write_glider_parquet(prof, ds_id, datetime.now(timezone.utc), cfg)
        if path:
            glider_paths.append(str(path))
    report["sources"]["ioos_glider_dac"] = {"datasets": active, "parquet_files": glider_paths}
    report["http_requests"] = client.request_count_today()
    return report
