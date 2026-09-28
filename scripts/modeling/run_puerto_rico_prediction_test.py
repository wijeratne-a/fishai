#!/usr/bin/env python3
"""Internal Puerto Rico detection feasibility test for two species only.

INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.

Finalize path: survey-only vs survey-date MUR SST (jplMURSST41 analysed_sst).
Does not overwrite audit/multi-species/MODEL_RESULTS.csv.
Does not write latitude/longitude into audit outputs.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = (
    ROOT
    / "data"
    / "raw"
    / "biological"
    / "noaa-ncrmp"
    / "CRCP_Reef_Fish_Surveys_Puerto_Rico"
)
RESTRICTED_DIR = ROOT / "data" / "restricted"
SST_CACHE_DIR = RESTRICTED_DIR / "environmental" / "jplMURSST41" / "by-date"
OUT_DIR = ROOT / "audit" / "prediction-test"

SPECIES = (
    ("STE PART", "Stegastes partitus"),
    ("SPA AURO", "Sparisoma aurofrenatum"),
)
TRAIN_YEARS = (2016, 2019, 2021)
HOLDOUT_YEAR = 2023
YEARS = TRAIN_YEARS + (HOLDOUT_YEAR,)
RANDOM_SEED = 20260926
ZERO_RULE = (
    "Detected if any row for SPECIES_CD has NUM > 0; "
    "species must be on that year's species list; "
    "survey non-detection is not ecological absence"
)
PUBLICATION_STATUS = "NOT_PUBLISHED"
L2_LAMBDA = 0.05
MAX_HABITATS = 6
SST_TRAIN_MISSING_MAX = 0.20
SST_CALIBRATION_TOL = 0.15
SST_MAX_DAY_OFFSET = 2  # past days only; future calendar days are leakage
RESULTS_LOCK = OUT_DIR / "RESULTS_LOCKED"
MIN_NONTRIVIAL_BYTES = 10_000
UA = "FishAI-internal-research/1.0 (public ERDDAP; internal feasibility)"
NCEI_DATASET = "CRCP_Reef_Fish_Surveys_Puerto_Rico"
MUR_DATASET = "jplMURSST41"
MUR_BASE = f"https://coastwatch.pfeg.noaa.gov/erddap/griddap/{MUR_DATASET}.csv"
# Coarse Puerto Rico regional box; stride ~0.1° (10×0.01° MUR cells).
PR_LAT = (17.8, 18.6)
PR_LON = (-67.5, -65.2)
MUR_STRIDE = 10
FORBIDDEN_OUTPUT_KEYS = frozenset(
    {"latitude", "longitude", "lat", "lon", "LATITUDE", "LONGITUDE"}
)
ATLANTIC_COLS = [
    "time",
    "latitude",
    "longitude",
    "YEAR",
    "MONTH",
    "DAY",
    "PRIMARY_SAMPLE_UNIT",
    "STATION_NR",
    "SAMPLE_DEPTH",
    "UNDERWATER_VISIBILITY",
    "HABITAT_CD",
    "REGION",
    "SUB_REGION_NAME",
    "SPECIES_CD",
    "SCIENTIFIC_NAME",
    "COMMON_NAME",
    "LEN",
    "NUM",
    "accession_url",
]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_provenance() -> dict:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return {"git_commit": None, "tree_status": "GIT_UNAVAILABLE"}
    try:
        dirty = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        dirty = ""
    return {
        "git_commit": commit,
        "tree_status": "DIRTY_TREE" if dirty else "CLEAN",
    }


def required_paths() -> list[Path]:
    return [RAW_DIR / f"{year}.csv.gz" for year in YEARS]


def missing_inputs() -> list[str]:
    out = []
    for path in required_paths():
        if not path.is_file() or path.stat().st_size < MIN_NONTRIVIAL_BYTES:
            out.append(str(path.relative_to(ROOT)))
    return out


def download_year_gzip(year: int) -> Path:
    """Download one Puerto Rico year from NCEI ERDDAP if missing/non-trivial."""
    dest = RAW_DIR / f"{year}.csv.gz"
    if dest.is_file() and dest.stat().st_size >= MIN_NONTRIVIAL_BYTES:
        return dest
    cols = ",".join(ATLANTIC_COLS)
    url = (
        f"https://www.ncei.noaa.gov/erddap/tabledap/{NCEI_DATASET}.csv?"
        f"{cols}&YEAR={year}"
    )
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(dest.suffix + ".partial")
    delay = 2.0
    last_err: Exception | None = None
    for attempt in range(1, 5):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=600) as response:
                data = response.read()
            if data.lstrip()[:1] == b"<" or len(data) < MIN_NONTRIVIAL_BYTES:
                raise RuntimeError(f"unexpected payload for {year}: bytes={len(data)}")
            with gzip.open(partial, "wb") as handle:
                handle.write(data)
            partial.replace(dest)
            return dest
        except Exception as exc:  # noqa: BLE001 — record and retry
            last_err = exc
            if partial.exists():
                partial.unlink()
            if attempt == 4:
                break
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"failed to download {year}: {last_err}")


def ensure_gzip_inputs() -> list[str]:
    """Ensure all four year gzips exist; download only missing/non-trivial ones."""
    downloaded: list[str] = []
    for year in YEARS:
        path = RAW_DIR / f"{year}.csv.gz"
        if path.is_file() and path.stat().st_size >= MIN_NONTRIVIAL_BYTES:
            continue
        download_year_gzip(year)
        downloaded.append(str(path.relative_to(ROOT)))
    return downloaded


def load_puerto_rico_events(
    paths: list[Path] | None = None,
) -> tuple[dict[tuple, dict], dict[int, set[str]]]:
    """Load events from Puerto Rico gzips. Coordinates are read but never stored."""
    paths = paths or required_paths()
    events: dict[tuple, dict] = {}
    universe: dict[int, set[str]] = defaultdict(set)
    for path in paths:
        year = int(path.name.split(".")[0])
        with gzip.open(path, "rt", encoding="latin-1", newline="") as handle:
            reader = csv.DictReader(handle)
            first = True
            for row in reader:
                year_s = (row.get("YEAR") or "").strip()
                if first and year_s == "":
                    first = False
                    continue
                first = False
                time_s = (row.get("time") or "").strip()
                key = (
                    year,
                    (row.get("PRIMARY_SAMPLE_UNIT") or "").strip(),
                    (row.get("STATION_NR") or "").strip(),
                    time_s,
                )
                code = (row.get("SPECIES_CD") or "").strip()
                if not code:
                    continue
                universe[year].add(code)
                depth_s = (row.get("DEPTH") or row.get("SAMPLE_DEPTH") or "").strip()
                vis_s = (row.get("UNDERWATER_VISIBILITY") or "").strip()
                rec = events.get(key)
                if rec is None:
                    survey_date = time_s[:10] if len(time_s) >= 10 else None
                    rec = {
                        "year": year,
                        "date": survey_date,
                        "block": (
                            row.get("SUB_REGION_NR")
                            or row.get("SUB_REGION_NAME")
                            or "NA"
                        ).strip()
                        or "NA",
                        "habitat": (row.get("HABITAT_CD") or "NA").strip() or "NA",
                        "depth": float(depth_s) if depth_s else None,
                        "vis": float(vis_s) if vis_s else None,
                        "pos": set(),
                        "name": {},
                        "sst": None,
                        "sst_offset_days": None,
                    }
                    events[key] = rec
                if (row.get("SCIENTIFIC_NAME") or "").strip():
                    rec["name"][code] = (row.get("SCIENTIFIC_NAME") or "").strip()
                try:
                    num = float(row["NUM"])
                except (KeyError, TypeError, ValueError):
                    continue
                if num > 0:
                    rec["pos"].add(code)
    return events, dict(universe)


def label_event_for_species(
    rec: dict,
    code: str,
    universe: dict[int, set[str]],
) -> int | None:
    """Return 1/0 if species is on the year's list; None if not evaluable."""
    year = int(rec["year"])
    if code not in universe.get(year, set()):
        return None
    return 1 if code in rec.get("pos", set()) else 0


def training_mask(
    years: list[int] | tuple[int, ...],
    holdout_year: int,
    train_years: tuple[int, ...] | list[int] = TRAIN_YEARS,
) -> list[bool]:
    """True only for explicit train years. Holdout and interstitial years are out."""
    allowed = {int(y) for y in train_years}
    hold = int(holdout_year)
    return [int(y) in allowed and int(y) != hold for y in years]


def causal_sst_offsets(max_past_days: int) -> list[int]:
    """Same-day then past days. Positive offsets are post-event leakage."""
    if max_past_days < 0:
        raise ValueError("max_past_days must be >= 0")
    return [0] + [-day for day in range(1, max_past_days + 1)]


def resolve_sst_for_day(
    day: date,
    day_sst: dict[str, float | None],
    max_past_days: int = SST_MAX_DAY_OFFSET,
) -> tuple[float | None, int | None]:
    """Pick SST on the survey date, else a past day. Never a future day."""
    for offset in causal_sst_offsets(max_past_days):
        value = day_sst.get((day + timedelta(days=offset)).isoformat())
        if value is not None:
            return value, abs(offset)
    return None, None


def require_finite_parameters(beta: list[float]) -> list[float]:
    if not beta or any(not math.isfinite(value) for value in beta):
        raise RuntimeError("NONFINITE_MODEL_PARAMETERS")
    return beta


def sigmoid(value: float) -> float:
    if value > 30:
        return 1.0
    if value < -30:
        return 0.0
    return 1.0 / (1.0 + math.exp(-value))


def design(
    rec: dict,
    habitats: list[str],
    years: list[int],
    *,
    include_sst: bool = False,
) -> list[float]:
    if rec.get("depth") is None or rec.get("vis") is None:
        raise ValueError("design() refuses missing depth or visibility; do not invent 15")
    x = [1.0, float(rec["depth"]) / 30.0, float(rec["vis"]) / 30.0]
    for year in years[1:]:
        x.append(1.0 if rec["year"] == year else 0.0)
    for habitat in habitats[1:]:
        x.append(1.0 if rec["habitat"] == habitat else 0.0)
    if include_sst:
        sst = rec.get("sst")
        if sst is None:
            raise ValueError("design(include_sst=True) requires non-missing sst")
        x.append((float(sst) - 28.0) / 3.0)
    return x


def fit_l2_logistic(
    rows: list[dict],
    habitats: list[str],
    years: list[int],
    *,
    l2: float = L2_LAMBDA,
    seed: int = RANDOM_SEED,
    steps: int = 120,
    lr: float = 0.08,
    include_sst: bool = False,
) -> list[float]:
    """Simple L2-regularized logistic (intercept unpenalized). Deterministic given seed."""
    _ = seed
    width = len(design(rows[0], habitats, years, include_sst=include_sst))
    beta = [0.0] * width
    n = max(len(rows), 1)
    for _ in range(steps):
        grad = [0.0] * width
        for rec in rows:
            x = design(rec, habitats, years, include_sst=include_sst)
            p = sigmoid(sum(b * xi for b, xi in zip(beta, x)))
            err = p - rec["y"]
            for i, xi in enumerate(x):
                grad[i] += err * xi
        for i in range(width):
            penalty = 0.0 if i == 0 else l2 * beta[i]
            beta[i] -= lr * (grad[i] / n + penalty)
    return require_finite_parameters(beta)


def predict_proba(
    rows: list[dict],
    beta: list[float],
    habitats: list[str],
    years: list[int],
    *,
    include_sst: bool = False,
) -> list[float]:
    return [
        sigmoid(
            sum(b * xi for b, xi in zip(beta, design(rec, habitats, years, include_sst=include_sst)))
        )
        for rec in rows
    ]


def brier(pairs: list[tuple[float, float]]) -> float:
    return sum((p - y) ** 2 for p, y in pairs) / len(pairs)


def log_loss(pairs: list[tuple[float, float]]) -> float:
    total = 0.0
    for p, y in pairs:
        p = min(max(p, 1e-6), 1.0 - 1e-6)
        total += -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))
    return total / len(pairs)


def parse_iso_date(value: str) -> date:
    return date.fromisoformat(value[:10])


def http_get_bytes(url: str, *, max_attempts: int = 5) -> bytes:
    delay = 2.0
    last_err: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=120) as response:
                status = getattr(response, "status", 200)
                if status in (429, 500, 502, 503, 504):
                    raise urllib.error.HTTPError(
                        url, status, f"HTTP {status}", response.headers, None
                    )
                return response.read()
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code not in (429, 500, 502, 503, 504) or attempt == max_attempts:
                raise
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if attempt == max_attempts:
                raise
        time.sleep(delay)
        delay = min(delay * 2, 60.0)
    raise RuntimeError(f"http_get_bytes failed: {last_err}")


def mur_url_for_day(day: date) -> str:
    # MUR daily fields are conventionally at 09:00Z.
    t = f"{day.isoformat()}T09:00:00Z"
    return (
        f"{MUR_BASE}?analysed_sst"
        f"[({t}):1:({t})]"
        f"[({PR_LAT[0]}):{MUR_STRIDE}:({PR_LAT[1]})]"
        f"[({PR_LON[0]}):{MUR_STRIDE}:({PR_LON[1]})]"
    )


def parse_mur_mean(payload: bytes) -> float | None:
    text = payload.decode("utf-8", errors="replace")
    if text.lstrip().startswith("<"):
        return None
    reader = csv.DictReader(io.StringIO(text))
    vals: list[float] = []
    for row in reader:
        raw = (row.get("analysed_sst") or "").strip()
        if not raw or raw.lower() in {"nan", "none", "null"}:
            continue
        # Skip ERDDAP units row.
        try:
            vals.append(float(raw))
        except ValueError:
            continue
    if not vals:
        return None
    return sum(vals) / len(vals)


def fetch_sst_for_day(day: date) -> float | None:
    """Fetch/cached regional mean analysed_sst for one calendar day. No fabrication."""
    SST_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = SST_CACHE_DIR / f"{day.isoformat()}.csv"
    meta = SST_CACHE_DIR / f"{day.isoformat()}.json"
    if cache.is_file() and cache.stat().st_size > 0:
        mean = parse_mur_mean(cache.read_bytes())
        if mean is not None:
            return mean
        if meta.is_file():
            info = json.loads(meta.read_text(encoding="utf-8"))
            if info.get("status") == "empty":
                return None
    url = mur_url_for_day(day)
    payload = http_get_bytes(url)
    time.sleep(0.15)  # pace only after network fetch
    cache.write_bytes(payload)
    mean = parse_mur_mean(payload)
    meta.write_text(
        json.dumps(
            {
                "date": day.isoformat(),
                "url": url,
                "status": "ok" if mean is not None else "empty",
                "mean_analysed_sst": mean,
                "bytes": len(payload),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return mean


def join_survey_date_sst(
    events: dict[tuple, dict],
) -> dict:
    """Assign survey-date MUR SST to events. Cache by date; sequential requests."""
    dates = sorted(
        {
            parse_iso_date(rec["date"])
            for rec in events.values()
            if rec.get("date")
        }
    )
    day_sst: dict[str, float | None] = {}
    blockers: list[str] = []
    fetched = 0

    def ensure_day(day: date) -> float | None:
        nonlocal fetched
        key = day.isoformat()
        if key in day_sst:
            return day_sst[key]
        value = fetch_sst_for_day(day)
        day_sst[key] = value
        fetched += 1
        return value

    try:
        # Pass 1: exact survey dates only.
        for day in dates:
            ensure_day(day)
        # Pass 2: same-day miss → past days only. Future days are leakage.
        for day in dates:
            if day_sst.get(day.isoformat()) is not None:
                continue
            for offset in causal_sst_offsets(SST_MAX_DAY_OFFSET)[1:]:
                if ensure_day(day + timedelta(days=offset)) is not None:
                    break
    except Exception as exc:  # noqa: BLE001
        blockers.append(
            f"ERDDAP_jplMURSST41_failure_after_retries: {type(exc).__name__}: {exc}"
        )

    resolved: dict[str, tuple[float | None, int | None]] = {}
    for day in dates:
        resolved[day.isoformat()] = resolve_sst_for_day(
            day, day_sst, max_past_days=SST_MAX_DAY_OFFSET
        )

    n_events = 0
    n_missing = 0
    for rec in events.values():
        n_events += 1
        d = rec.get("date")
        if not d or d not in resolved:
            rec["sst"] = None
            rec["sst_offset_days"] = None
            n_missing += 1
            continue
        val, off = resolved[d]
        rec["sst"] = val
        rec["sst_offset_days"] = off
        if val is None:
            n_missing += 1

    missing_fraction = (n_missing / n_events) if n_events else 1.0
    return {
        "distinct_survey_dates": len(dates),
        "dates_requested": fetched,
        "events": n_events,
        "events_missing_sst": n_missing,
        "sst_missing_fraction": round(missing_fraction, 6),
        "blockers": blockers,
        "dataset": MUR_DATASET,
        "variable": "analysed_sst",
        "regional_box": {"lat": PR_LAT, "lon": PR_LON, "stride": MUR_STRIDE},
        "max_day_offset": SST_MAX_DAY_OFFSET,
        "allowed_offsets": causal_sst_offsets(SST_MAX_DAY_OFFSET),
        "future_day_offsets_forbidden": True,
        "cache_dir": str(SST_CACHE_DIR.relative_to(ROOT)),
    }


def build_labeled_rows(
    events: dict[tuple, dict],
    universe: dict[int, set[str]],
    code: str,
    *,
    require_sst: bool = False,
) -> list[dict]:
    rows: list[dict] = []
    for rec in events.values():
        y = label_event_for_species(rec, code, universe)
        if y is None:
            continue
        if rec["depth"] is None or rec.get("vis") is None:
            continue
        if require_sst and rec.get("sst") is None:
            continue
        rows.append(
            {
                "year": rec["year"],
                "block": rec["block"],
                "habitat": rec["habitat"],
                "depth": rec["depth"],
                "vis": rec["vis"],
                "sst": rec.get("sst"),
                "y": y,
            }
        )
    return rows


def sanitize_record(rec: dict) -> dict:
    return {k: v for k, v in rec.items() if k not in FORBIDDEN_OUTPUT_KEYS}


def spatial_pooled(
    train: list[dict],
    habitats: list[str],
    years: list[int],
    *,
    include_sst: bool,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]], int]:
    blocks = sorted({r["block"] for r in train})
    pooled_model: list[tuple[float, float]] = []
    pooled_base: list[tuple[float, float]] = []
    folds_used = 0
    for block in blocks:
        tr = [r for r in train if r["block"] != block]
        te = [r for r in train if r["block"] == block]
        if len(te) < 8 or sum(r["y"] for r in tr) < 5:
            continue
        rate = sum(r["y"] for r in tr) / len(tr)
        beta = fit_l2_logistic(
            tr, habitats, years, seed=RANDOM_SEED, include_sst=include_sst
        )
        preds = predict_proba(te, beta, habitats, years, include_sst=include_sst)
        for p, rec in zip(preds, te):
            pooled_model.append((p, rec["y"]))
            pooled_base.append((rate, rec["y"]))
        folds_used += 1
    return pooled_model, pooled_base, folds_used


def score_holdout(
    train: list[dict],
    test: list[dict],
    habitats: list[str],
    years: list[int],
    *,
    include_sst: bool,
) -> dict:
    train_rate = sum(r["y"] for r in train) / len(train)
    beta = fit_l2_logistic(
        train, habitats, years, seed=RANDOM_SEED, include_sst=include_sst
    )
    hold_preds = predict_proba(test, beta, habitats, years, include_sst=include_sst)
    hold_model = list(zip(hold_preds, [r["y"] for r in test]))
    hold_base = [(train_rate, r["y"]) for r in test]
    mean_pred = sum(hold_preds) / len(hold_preds)
    hold_prev = sum(r["y"] for r in test) / len(test)
    return {
        "train_prevalence": train_rate,
        "holdout_prevalence": hold_prev,
        "mean_predicted_probability": mean_pred,
        "holdout_brier_model": brier(hold_model),
        "holdout_brier_baseline": brier(hold_base),
        "holdout_logloss_model": log_loss(hold_model),
        "holdout_logloss_baseline": log_loss(hold_base),
        "calibration_gap": abs(mean_pred - hold_prev),
    }


def evaluate_species(
    code: str,
    scientific_name: str,
    events: dict[tuple, dict],
    universe: dict[int, set[str]],
    *,
    sst_join: dict | None = None,
) -> dict:
    rows = build_labeled_rows(events, universe, code, require_sst=False)
    train = [r for r in rows if r["year"] in TRAIN_YEARS]
    test = [r for r in rows if r["year"] == HOLDOUT_YEAR]
    if not train or not test:
        raise RuntimeError(f"Insufficient rows for {code}: train={len(train)} test={len(test)}")

    mask = training_mask([r["year"] for r in rows], HOLDOUT_YEAR)
    assert all(not m for r, m in zip(rows, mask) if r["year"] == HOLDOUT_YEAR)
    assert all(m for r, m in zip(rows, mask) if r["year"] in TRAIN_YEARS)

    counts: dict[str, int] = {}
    for rec in train:
        counts[rec["habitat"]] = counts.get(rec["habitat"], 0) + 1
    habitats = [h for h, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:MAX_HABITATS]]
    years = sorted({r["year"] for r in train})

    pooled_model, pooled_base, folds_used = spatial_pooled(
        train, habitats, years, include_sst=False
    )
    survey = score_holdout(train, test, habitats, years, include_sst=False)
    spatial_brier_model = brier(pooled_model) if pooled_model else None
    spatial_brier_base = brier(pooled_base) if pooled_base else None

    beats_prev = (
        survey["holdout_brier_model"] < survey["holdout_brier_baseline"]
        and survey["holdout_logloss_model"] < survey["holdout_logloss_baseline"]
    )
    if spatial_brier_model is not None and spatial_brier_base is not None:
        beats_prev = beats_prev and spatial_brier_model < spatial_brier_base

    # Training SST missingness among depth-complete labeled train events.
    train_sst_missing = sum(1 for r in train if r.get("sst") is None) / len(train)
    sst_eligible = train_sst_missing < SST_TRAIN_MISSING_MAX
    sst_score = None
    sst_spatial_brier = None
    sst_accepted = False
    sst_skip_reason = None
    join_blockers = list((sst_join or {}).get("blockers") or [])

    if join_blockers:
        sst_skip_reason = "sst_join_blocked"
        sst_eligible = False
    elif not sst_eligible:
        sst_skip_reason = (
            f"train_sst_missing_fraction={train_sst_missing:.4f} >= {SST_TRAIN_MISSING_MAX}"
        )
    else:
        train_sst = [r for r in train if r.get("sst") is not None]
        test_sst = [r for r in test if r.get("sst") is not None]
        if len(train_sst) < 20 or len(test_sst) < 8:
            sst_skip_reason = "insufficient_complete_sst_rows"
        else:
            pooled_sst, _, _ = spatial_pooled(
                train_sst, habitats, years, include_sst=True
            )
            sst_spatial_brier = brier(pooled_sst) if pooled_sst else None
            sst_score = score_holdout(
                train_sst, test_sst, habitats, years, include_sst=True
            )
            # Acceptance: holdout Brier AND log loss ≤ survey-only; calibration not wild.
            sst_accepted = (
                sst_score["holdout_brier_model"] <= survey["holdout_brier_model"]
                and sst_score["holdout_logloss_model"] <= survey["holdout_logloss_model"]
                and sst_score["calibration_gap"] <= SST_CALIBRATION_TOL
            )
            if not sst_accepted:
                sst_skip_reason = "sst_did_not_earn_a_place"

    model_retained = "sst" if sst_accepted else "survey_only"

    record = {
        "label": "INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED",
        "region": "Puerto Rico",
        "species_code": code,
        "scientific_name": scientific_name,
        "train_years": list(TRAIN_YEARS),
        "holdout_year": HOLDOUT_YEAR,
        "train_events": len(train),
        "holdout_events": len(test),
        "train_detections": sum(r["y"] for r in train),
        "holdout_detections": sum(r["y"] for r in test),
        "train_prevalence": round(survey["train_prevalence"], 6),
        "spatial_folds_used": folds_used,
        "spatial_brier_model": None if spatial_brier_model is None else round(spatial_brier_model, 6),
        "spatial_brier_baseline": None if spatial_brier_base is None else round(spatial_brier_base, 6),
        "holdout_brier_model": round(survey["holdout_brier_model"], 6),
        "holdout_brier_baseline": round(survey["holdout_brier_baseline"], 6),
        "holdout_logloss_model": round(survey["holdout_logloss_model"], 6),
        "holdout_logloss_baseline": round(survey["holdout_logloss_baseline"], 6),
        "survey_only_holdout_brier": round(survey["holdout_brier_model"], 6),
        "survey_only_holdout_logloss": round(survey["holdout_logloss_model"], 6),
        "sst_model_holdout_brier": None
        if sst_score is None
        else round(sst_score["holdout_brier_model"], 6),
        "sst_model_holdout_logloss": None
        if sst_score is None
        else round(sst_score["holdout_logloss_model"], 6),
        "sst_spatial_brier": None if sst_spatial_brier is None else round(sst_spatial_brier, 6),
        "sst_mean_predicted_probability": None
        if sst_score is None
        else round(sst_score["mean_predicted_probability"], 6),
        "sst_holdout_prevalence": None
        if sst_score is None
        else round(sst_score["holdout_prevalence"], 6),
        "sst_calibration_gap": None
        if sst_score is None
        else round(sst_score["calibration_gap"], 6),
        "train_sst_missing_fraction": round(train_sst_missing, 6),
        "sst_eligible": sst_eligible,
        "sst_accepted": sst_accepted,
        "sst_skip_reason": sst_skip_reason,
        "model_retained": model_retained,
        "beats_baseline": beats_prev,
        "publication_status": PUBLICATION_STATUS,
        "on_the_globe": False,
        "predictors_survey_only": [
            "depth",
            "underwater_visibility",
            "year",
            "habitat_code",
        ],
        "predictors_sst": [
            "depth",
            "underwater_visibility",
            "year",
            "habitat_code",
            "survey_date_analysed_sst",
        ],
        "sst_joined": bool(sst_join) and not join_blockers,
        "obis_used": False,
        "zero_rule": ZERO_RULE,
        "model": "l2_logistic",
        "l2_lambda": L2_LAMBDA,
        "random_seed": RANDOM_SEED,
    }
    return sanitize_record(record)


def accept_sst_model(
    survey_brier: float,
    survey_logloss: float,
    sst_brier: float,
    sst_logloss: float,
    mean_pred: float,
    holdout_prevalence: float,
    *,
    tol: float = SST_CALIBRATION_TOL,
) -> bool:
    """Pure acceptance rule used by tests and evaluate_species."""
    return (
        sst_brier <= survey_brier
        and sst_logloss <= survey_logloss
        and abs(mean_pred - holdout_prevalence) <= tol
    )


def build_final_status(results: list[dict], sst_join: dict, blockers: list[str]) -> str:
    species = "; ".join(f"{r['species_code']} ({r['scientific_name']})" for r in results)
    survey_brier = "; ".join(
        f"{r['species_code']} {r['survey_only_holdout_brier']:.6f}" for r in results
    )
    sst_brier_parts = []
    for r in results:
        val = r.get("sst_model_holdout_brier")
        sst_brier_parts.append(
            f"{r['species_code']} {'NA' if val is None else f'{val:.6f}'}"
        )
    retained = "; ".join(f"{r['species_code']} {r['model_retained']}" for r in results)
    beats = "; ".join(
        f"{r['species_code']} {'YES' if r['beats_baseline'] else 'NO'}" for r in results
    )
    miss = sst_join.get("sst_missing_fraction")
    miss_s = "NA" if miss is None else f"{miss:.6f}"
    blocker_s = "NONE" if not blockers else "; ".join(blockers)
    return "\n".join(
        [
            "FINAL STATUS:",
            f"SPECIES: {species}",
            f"TRAIN YEARS: {', '.join(str(y) for y in TRAIN_YEARS)}",
            f"HOLDOUT YEAR: {HOLDOUT_YEAR}",
            f"SURVEY-ONLY HOLDOUT BRIER: {survey_brier}",
            f"SST MODEL HOLDOUT BRIER: {'; '.join(sst_brier_parts)}",
            f"MODEL RETAINED: {retained}",
            f"SST MISSING FRACTION: {miss_s}",
            f"BEATS PREVALENCE: {beats}",
            f"PUBLICATION: {PUBLICATION_STATUS}",
            "ON THE GLOBE: NO",
            "COORDINATES IN REPORT: NO",
            f"BLOCKERS: {blocker_s}",
        ]
    )


def write_final_report(results: list[dict], sst_join: dict, blockers: list[str]) -> Path:
    if RESULTS_LOCK.is_file():
        raise RuntimeError(
            "RESULTS_LOCKED: inspected-holdout report is quarantined; refuse overwrite"
        )
    status = build_final_status(results, sst_join, blockers)
    lines = [
        status,
        "",
        "Label: INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.",
        "",
        "# Puerto Rico internal prediction finalize — report",
        "",
        "**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**",
        "",
        "Survey-only L2 logistic versus constant training prevalence, plus optional "
        "survey-date MUR `analysed_sst` (`jplMURSST41`) joined via a coarse Puerto Rico "
        "regional box cached under `data/restricted/`. Train years 2016/2019/2021 only; "
        "2023 scored once per model. SST retained only if holdout Brier and log loss are "
        "≤ survey-only and mean predicted probability is within 0.15 of holdout prevalence.",
        "",
        f"SST join: missing_fraction={sst_join.get('sst_missing_fraction')}; "
        f"distinct_dates={sst_join.get('distinct_survey_dates')}; "
        f"cache={sst_join.get('cache_dir')}.",
        "",
        "| Species | Survey Brier | SST Brier | Retained | Beats prevalence | SST skip |",
        "|---|---:|---:|---|---|---|",
    ]
    for r in results:
        sst_b = r.get("sst_model_holdout_brier")
        lines.append(
            f"| {r['species_code']} | {r['survey_only_holdout_brier']:.6f} | "
            f"{'NA' if sst_b is None else f'{sst_b:.6f}'} | {r['model_retained']} | "
            f"{'yes' if r['beats_baseline'] else 'no'} | {r.get('sst_skip_reason') or ''} |"
        )
    if any(r["model_retained"] == "survey_only" for r in results) and not blockers:
        if any(r.get("sst_skip_reason") == "sst_did_not_earn_a_place" for r in results):
            lines.extend(
                [
                    "",
                    "SST did not earn a place for at least one species under the acceptance rule; "
                    "survey-only model retained where SST was not accepted.",
                ]
            )
    lines.extend(
        [
            "",
            "**INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.**",
            "",
        ]
    )
    path = OUT_DIR / "PUERTO_RICO_FINAL_REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def build_manifest(
    input_hashes: dict[str, str],
    results: list[dict],
    sst_join: dict,
    blockers: list[str],
    downloaded: list[str],
) -> dict:
    prov = git_provenance()
    return {
        "label": "INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED",
        "publication_status": PUBLICATION_STATUS,
        "on_the_globe": False,
        "coordinates_in_report": False,
        "dataset": NCEI_DATASET,
        "data_file_paths": [str(p.relative_to(ROOT)) for p in required_paths()],
        "sha256": input_hashes,
        "downloaded_this_run": downloaded,
        "random_seed": RANDOM_SEED,
        "train_years": list(TRAIN_YEARS),
        "holdout_year": HOLDOUT_YEAR,
        "species": [{"code": c, "scientific_name": n} for c, n in SPECIES],
        "zero_rule": ZERO_RULE,
        "predictors_survey_only": [
            "depth",
            "underwater_visibility",
            "year",
            "habitat_code",
        ],
        "sst": {
            "dataset": MUR_DATASET,
            "variable": "analysed_sst",
            "joined": bool(sst_join) and not blockers,
            "missing_fraction": sst_join.get("sst_missing_fraction"),
            "cache_dir": sst_join.get("cache_dir"),
            "spatial_support": "coarse_puerto_rico_regional_box",
            "max_day_offset": SST_MAX_DAY_OFFSET,
            "allowed_offsets": causal_sst_offsets(SST_MAX_DAY_OFFSET),
            "future_day_offsets_forbidden": True,
            "acceptance": {
                "train_missing_max": SST_TRAIN_MISSING_MAX,
                "calibration_tol": SST_CALIBRATION_TOL,
                "rule": "retain SST if holdout Brier and log loss <= survey-only and |mean_pred - holdout_prevalence| <= 0.15",
            },
        },
        "obis_used": False,
        "git_commit": prov["git_commit"],
        "tree_status": prov["tree_status"],
        "blockers": blockers,
        "results_summary": [
            {
                "species_code": r["species_code"],
                "survey_only_holdout_brier": r["survey_only_holdout_brier"],
                "sst_model_holdout_brier": r.get("sst_model_holdout_brier"),
                "model_retained": r["model_retained"],
                "beats_baseline": r["beats_baseline"],
            }
            for r in results
        ],
        "run_finished_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    blockers: list[str] = []

    try:
        downloaded = ensure_gzip_inputs()
    except Exception as exc:  # noqa: BLE001
        blockers.append(f"gzip_download_failure: {type(exc).__name__}: {exc}")
        downloaded = []

    missing = missing_inputs()
    if missing:
        blockers.append("MISSING_PUERTO_RICO_GZIP: " + ", ".join(missing))
        (OUT_DIR / "MISSING_INPUTS.json").write_text(
            json.dumps(
                {
                    "missing": missing,
                    "publication_status": PUBLICATION_STATUS,
                    "blockers": blockers,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        # Cannot fit without surveys.
        report = OUT_DIR / "PUERTO_RICO_FINAL_REPORT.md"
        report.write_text(
            "\n".join(
                [
                    "FINAL STATUS:",
                    "SPECIES: STE PART (Stegastes partitus); SPA AURO (Sparisoma aurofrenatum)",
                    f"TRAIN YEARS: {', '.join(str(y) for y in TRAIN_YEARS)}",
                    f"HOLDOUT YEAR: {HOLDOUT_YEAR}",
                    "SURVEY-ONLY HOLDOUT BRIER: NA",
                    "SST MODEL HOLDOUT BRIER: NA",
                    "MODEL RETAINED: NA",
                    "SST MISSING FRACTION: NA",
                    "BEATS PREVALENCE: NA",
                    f"PUBLICATION: {PUBLICATION_STATUS}",
                    "ON THE GLOBE: NO",
                    "COORDINATES IN REPORT: NO",
                    f"BLOCKERS: {'; '.join(blockers)}",
                    "",
                    "Label: INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        manifest = {
            "label": "INTERNAL FEASIBILITY TEST — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED",
            "publication_status": PUBLICATION_STATUS,
            "blockers": blockers,
            "sha256": {},
            "random_seed": RANDOM_SEED,
            **git_provenance(),
        }
        (OUT_DIR / "PUERTO_RICO_RUN_MANIFEST.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({"ok": False, "blockers": blockers}))
        return 2

    input_hashes = {str(p.relative_to(ROOT)): file_sha256(p) for p in required_paths()}
    events, universe = load_puerto_rico_events()

    sst_join = {
        "sst_missing_fraction": None,
        "distinct_survey_dates": None,
        "cache_dir": str(SST_CACHE_DIR.relative_to(ROOT)),
        "blockers": [],
    }
    try:
        sst_join = join_survey_date_sst(events)
        blockers.extend(sst_join.get("blockers") or [])
    except Exception as exc:  # noqa: BLE001
        msg = f"ERDDAP_jplMURSST41_failure_after_retries: {type(exc).__name__}: {exc}"
        blockers.append(msg)
        sst_join["blockers"] = [msg]

    results = []
    for code, name in SPECIES:
        results.append(
            evaluate_species(code, name, events, universe, sst_join=sst_join)
        )

    results_path = OUT_DIR / "RESULTS.json"
    results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    report_path = write_final_report(results, sst_join, blockers)
    manifest = build_manifest(input_hashes, results, sst_join, blockers, downloaded)
    for key in FORBIDDEN_OUTPUT_KEYS:
        assert key not in manifest
        for rec in results:
            assert key not in rec
    manifest_path = OUT_DIR / "PUERTO_RICO_RUN_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "RUN_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "wrote": [
                    str(report_path.relative_to(ROOT)),
                    str(manifest_path.relative_to(ROOT)),
                    str(results_path.relative_to(ROOT)),
                ],
                "blockers": blockers,
                "sst_missing_fraction": sst_join.get("sst_missing_fraction"),
                "model_retained": [r["model_retained"] for r in results],
            }
        )
    )
    return 0 if not any(b.startswith("MISSING_") for b in blockers) else 2


if __name__ == "__main__":
    raise SystemExit(main())
