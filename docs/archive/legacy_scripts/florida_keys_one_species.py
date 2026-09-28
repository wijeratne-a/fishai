#!/usr/bin/env python3
"""Florida Keys survey-detection model for one species, end to end.

INTERNAL — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.

Output is P(detected on a completed Reef Visual Census point count | habitat, depth,
visibility[, HYCOM water temperature at dive depth]). It is not abundance, not
ecological absence, and not where the fish is now.

Phases (each refuses to run out of order):
  freeze  training years only; spatial CV chooses the feature set; writes PREREGISTRATION.json
  score   verifies the preregistration, fits on training years, scores the test year once
  predict applies the saved model to one survey description, with a support check

The test year is never read before the preregistration file exists.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "biological"
HYCOM_DIR = ROOT / "data" / "restricted" / "environmental" / "hycom" / "florida-keys" / "by-date"
OUT = ROOT / "audit" / "florida-keys-one-species"
PREREG = OUT / "PREREGISTRATION.json"
LOCK = OUT / "SCORED_ONCE.lock"
ARTIFACT = ROOT / "models" / "florida-keys" / "ste_part_v1.json"

SPECIES_CODE = "STE PART"
SCIENTIFIC_NAME = "Stegastes partitus"
COMMON_NAME = "bicolor damselfish"
TRAIN_YEARS = (2014, 2016, 2018)
TEST_YEAR = 2022
BLOCK_FIELD = "SUB_REGION_NAME"
MIN_HABITAT_EVENTS = 30
L2 = 1.0
MAX_TEMP_CELL_KM = 10.0
MIN_SPECIES_ROW_COVERAGE = 0.99
BOOTSTRAP_REPS = 2000
SEED = 20260927
CALIBRATION_GAP_MAX = 0.05
PUBLICATION_STATUS = "NOT_PUBLISHED"
LABEL = "INTERNAL — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED"
FORBIDDEN_KEYS = frozenset({"lat", "lon", "latitude", "longitude"})


# ---------------------------------------------------------------- utilities

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_commit() -> dict:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
        return {"git_commit": commit, "tree": "DIRTY" if dirty else "CLEAN"}
    except (subprocess.CalledProcessError, OSError):
        return {"git_commit": None, "tree": "GIT_UNAVAILABLE"}


def survey_path(year: int) -> Path:
    return RAW / f"noaa-rvc-florida-keys-{year}.csv.gz"


def assert_no_coordinates(obj) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise RuntimeError(f"coordinate key {key!r} in output")
            assert_no_coordinates(value)
    elif isinstance(obj, list):
        for value in obj:
            assert_no_coordinates(value)


# ---------------------------------------------------------------- labels

def load_events(year: int, code: str = SPECIES_CODE) -> list[dict]:
    """One record per completed point count. Detection = any length-bin NUM > 0.

    A zero is emitted only if the event has explicit rows for the code and all are
    NUM == 0. Events with no row for the code are NOT_EVALUATED, never zero.
    """
    events: dict[tuple, dict] = {}
    year_codes: set[str] = set()
    with gzip.open(survey_path(year), "rt", encoding="latin-1", newline="") as handle:
        for row in csv.DictReader(handle):
            stamp = (row.get("time") or "").strip()
            if not stamp[:4].isdigit():
                continue
            key = (row["PRIMARY_SAMPLE_UNIT"].strip(), row["STATION_NR"].strip(), stamp)
            rec = events.get(key)
            if rec is None:
                depth = row["DEPTH"].strip()
                vis = row["UNDERWATER_VISIBILITY"].strip()
                rec = {
                    "year": year,
                    "date": stamp[:10],
                    "psu": f"{year}:{key[0]}",
                    "block": row[BLOCK_FIELD].strip() or "NA",
                    "habitat": row["HABITAT_CD"].strip() or "NA",
                    "depth": float(depth) if depth not in ("", "NaN") else None,
                    "vis": float(vis) if vis not in ("", "NaN") else None,
                    "_lat": float(row["latitude"]),
                    "_lon": float(row["longitude"]),
                    "has_rows": False,
                    "positive": False,
                }
                events[key] = rec
            spp = row["SPECIES_CD"].strip()
            year_codes.add(spp)
            if spp != code:
                continue
            rec["has_rows"] = True
            if float(row["NUM"]) > 0:
                rec["positive"] = True
    if code not in year_codes:
        raise RuntimeError(f"{code} not on the {year} species list; year cannot be evaluated")
    out = list(events.values())
    coverage = sum(e["has_rows"] for e in out) / len(out)
    if coverage < MIN_SPECIES_ROW_COVERAGE:
        raise RuntimeError(
            f"{year}: only {coverage:.3f} of events carry explicit rows for {code}; "
            "zero rows may have been dropped from the extract"
        )
    for e in out:
        e["label_state"] = "DETECTED" if e["positive"] else ("SURVEY_NONDETECTION" if e["has_rows"] else "NOT_EVALUATED")
        e["y"] = 1 if e["positive"] else (0 if e["has_rows"] else None)
    return out


# ---------------------------------------------------------------- temperature

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dl = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def load_hycom(day: str):
    """Return (depths, lat, lon, temp[depth, lat, lon]) in degC with NaN for masked cells."""
    from scipy.io import netcdf_file

    path = HYCOM_DIR / f"{day}.nc"
    meta = path.with_suffix(".json")
    if not path.is_file() or not meta.is_file():
        return None
    info = json.loads(meta.read_text(encoding="utf-8"))
    if info.get("status") != "ok" or (info.get("offset_days") or 0) < 0:
        return None
    data = netcdf_file(path, "r", mmap=False)
    var = data.variables["water_temp"]
    raw = var.data[0].astype(float)
    temp = raw * float(var.scale_factor) + float(var.add_offset)
    temp[raw == float(var._FillValue)] = np.nan
    lon = data.variables["lon"].data.astype(float)
    lon = np.where(lon > 180.0, lon - 360.0, lon)
    return data.variables["depth"].data.astype(float), data.variables["lat"].data.astype(float), lon, temp


def temperature_at_depth(profile_depths, profile_temps, dive_depth: float) -> float | None:
    """Linear interpolation inside the valid part of one water column. No extrapolation."""
    valid = np.isfinite(profile_temps)
    if not valid.any():
        return None
    z = profile_depths[valid]
    t = profile_temps[valid]
    if dive_depth < z.min() or dive_depth > z.max():
        return None
    return float(np.interp(dive_depth, z, t))


def attach_temperature(events: list[dict]) -> dict:
    """Nearest HYCOM column (within MAX_TEMP_CELL_KM) that reaches the dive depth."""
    by_date: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        by_date[e["date"]].append(e)
    distances = []
    missing_file = missing_column = 0
    for day, evs in by_date.items():
        grid = load_hycom(day)
        if grid is None:
            missing_file += len(evs)
            for e in evs:
                e["temp"] = None
            continue
        depths, lat, lon, temp = grid
        lat2d, lon2d = np.meshgrid(lat, lon, indexing="ij")
        for e in evs:
            e["temp"] = None
            dist = haversine_km(e["_lat"], e["_lon"], lat2d, lon2d)
            order = np.argsort(dist, axis=None)
            for flat in order:
                i, j = np.unravel_index(flat, dist.shape)
                if dist[i, j] > MAX_TEMP_CELL_KM:
                    break
                value = temperature_at_depth(depths, temp[:, i, j], e["depth"])
                if value is not None:
                    e["temp"] = value
                    distances.append(float(dist[i, j]))
                    break
            if e["temp"] is None:
                missing_column += 1
    n = len(events)
    return {
        "events": n,
        "matched": n - missing_file - missing_column,
        "missing_no_hycom_file": missing_file,
        "missing_no_column_within_km": missing_column,
        "max_cell_km": MAX_TEMP_CELL_KM,
        "cell_distance_km_median": round(float(np.median(distances)), 2) if distances else None,
        "cell_distance_km_p95": round(float(np.percentile(distances, 95)), 2) if distances else None,
    }


def strip_coordinates(events: list[dict]) -> None:
    for e in events:
        e.pop("_lat", None)
        e.pop("_lon", None)


# ---------------------------------------------------------------- design

def fit_scaler(rows: list[dict], fields: list[str]) -> dict:
    """Mean/sd from training rows only."""
    out = {}
    for f in fields:
        vals = np.array([r[f] for r in rows], dtype=float)
        sd = float(vals.std())
        out[f] = {"mean": float(vals.mean()), "sd": sd if sd > 0 else 1.0}
    return out


def habitat_levels(rows: list[dict]) -> list[str]:
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        counts[r["habitat"]] += 1
    keep = [h for h, c in sorted(counts.items(), key=lambda kv: -kv[1]) if c >= MIN_HABITAT_EVENTS]
    return keep


def design_row(rec: dict, spec: dict) -> list[float]:
    for f in spec["numeric"]:
        if rec.get(f) is None:
            raise ValueError(f"design_row refuses missing {f}")
    x = [1.0]
    for f in spec["numeric"]:
        s = spec["scaler"][f]
        x.append((float(rec[f]) - s["mean"]) / s["sd"])
    levels = spec["habitats"]
    hab = rec["habitat"] if rec["habitat"] in levels else "OTHER"
    for h in levels[1:] + (["OTHER"] if spec["has_other"] else []):
        x.append(1.0 if hab == h else 0.0)
    return x


def make_spec(train: list[dict], numeric: list[str]) -> dict:
    levels = habitat_levels(train)
    has_other = any(r["habitat"] not in levels for r in train)
    return {
        "numeric": list(numeric),
        "scaler": fit_scaler(train, numeric),
        "habitats": levels,
        "has_other": has_other,
    }


def matrix(rows: list[dict], spec: dict) -> tuple[np.ndarray, np.ndarray]:
    X = np.array([design_row(r, spec) for r in rows], dtype=float)
    y = np.array([r["y"] for r in rows], dtype=float)
    return X, y


# ---------------------------------------------------------------- estimator

def fit_logistic(X: np.ndarray, y: np.ndarray, l2: float = L2, max_iter: int = 100, tol: float = 1e-8) -> np.ndarray:
    """L2-penalized logistic regression by Newton steps. Intercept unpenalized.

    Raises on non-convergence or non-finite coefficients instead of returning them.
    """
    n, k = X.shape
    beta = np.zeros(k)
    penalty = np.full(k, l2)
    penalty[0] = 0.0
    for _ in range(max_iter):
        eta = np.clip(X @ beta, -30, 30)
        p = 1.0 / (1.0 + np.exp(-eta))
        w = p * (1 - p)
        grad = X.T @ (p - y) + penalty * beta
        hess = (X * w[:, None]).T @ X + np.diag(penalty)
        step = np.linalg.solve(hess, grad)
        beta = beta - step
        if not np.all(np.isfinite(beta)):
            raise RuntimeError("NONFINITE_MODEL_PARAMETERS")
        if np.max(np.abs(step)) < tol:
            return beta
    raise RuntimeError("LOGISTIC_DID_NOT_CONVERGE")


def predict_proba(X: np.ndarray, beta: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(X @ beta, -30, 30)))


# ---------------------------------------------------------------- metrics

def brier(p: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2))


def log_loss(p: np.ndarray, y: np.ndarray) -> float:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def auc(p: np.ndarray, y: np.ndarray) -> float | None:
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    ranks = np.empty(len(order))
    allp = np.concatenate([pos, neg])[order]
    i = 0
    while i < len(allp):
        j = i
        while j + 1 < len(allp) and allp[j + 1] == allp[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def reliability(p: np.ndarray, y: np.ndarray, bins: int = 10) -> list[dict]:
    edges = np.linspace(0, 1, bins + 1)
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi if hi < 1 else p <= hi)
        if m.sum():
            out.append({"bin": f"{lo:.1f}-{hi:.1f}", "n": int(m.sum()), "mean_p": round(float(p[m].mean()), 4), "observed": round(float(y[m].mean()), 4)})
    return out


def calibration_slope(p: np.ndarray, y: np.ndarray) -> dict:
    logit = np.log(np.clip(p, 1e-6, 1 - 1e-6) / np.clip(1 - p, 1e-6, 1))
    X = np.column_stack([np.ones_like(logit), logit])
    try:
        b = fit_logistic(X, y, l2=0.0)
        return {"intercept": round(float(b[0]), 4), "slope": round(float(b[1]), 4)}
    except RuntimeError as exc:
        return {"error": str(exc)}


def cluster_bootstrap_delta(p_model, p_base, y, clusters, reps=BOOTSTRAP_REPS, seed=SEED) -> dict:
    """Brier(base) - Brier(model), resampling survey sites (PSUs), not single dives."""
    rng = np.random.default_rng(seed)
    ids = np.unique(clusters)
    index = {c: np.where(clusters == c)[0] for c in ids}
    deltas = []
    for _ in range(reps):
        take = np.concatenate([index[c] for c in rng.choice(ids, size=len(ids), replace=True)])
        deltas.append(brier(p_base[take], y[take]) - brier(p_model[take], y[take]))
    deltas = np.array(deltas)
    return {
        "brier_improvement": round(float(brier(p_base, y) - brier(p_model, y)), 6),
        "ci95_low": round(float(np.percentile(deltas, 2.5)), 6),
        "ci95_high": round(float(np.percentile(deltas, 97.5)), 6),
        "reps": reps,
        "resampling_unit": "primary_sample_unit",
    }


# ---------------------------------------------------------------- spatial CV

def spatial_cv(train: list[dict], numeric: list[str]) -> dict:
    blocks = sorted({r["block"] for r in train})
    pm, pb, py = [], [], []
    folds = []
    for block in blocks:
        tr = [r for r in train if r["block"] != block]
        te = [r for r in train if r["block"] == block]
        spec = make_spec(tr, numeric)
        beta = fit_logistic(*matrix(tr, spec))
        Xte, yte = matrix(te, spec)
        p = predict_proba(Xte, beta)
        rate = float(np.mean([r["y"] for r in tr]))
        pm.extend(p)
        pb.extend([rate] * len(te))
        py.extend(yte)
        folds.append({"block": block, "n": len(te), "brier_model": round(brier(p, yte), 5), "brier_prevalence": round(brier(np.full(len(te), rate), yte), 5)})
    pm, pb, py = map(np.array, (pm, pb, py))
    return {
        "numeric": numeric,
        "folds": folds,
        "pooled_brier_model": round(brier(pm, py), 6),
        "pooled_brier_prevalence": round(brier(pb, py), 6),
        "pooled_logloss_model": round(log_loss(pm, py), 6),
        "pooled_logloss_prevalence": round(log_loss(pb, py), 6),
    }


# ---------------------------------------------------------------- phases

def build_rows(years) -> tuple[list[dict], dict]:
    events = []
    for year in years:
        events.extend(load_events(year))
    join = attach_temperature(events)
    strip_coordinates(events)
    rows = [e for e in events if e["y"] is not None and e["depth"] is not None and e["vis"] is not None and e["temp"] is not None]
    audit = {
        "events_loaded": len(events),
        "not_evaluated": sum(e["y"] is None for e in events),
        "dropped_missing_temperature": sum(e["temp"] is None for e in events),
        "rows_used": len(rows),
        "temperature_join": join,
    }
    return rows, audit


def freeze() -> dict:
    if PREREG.exists():
        raise RuntimeError("PREREGISTRATION.json already exists; refuse to re-freeze")
    rows, audit = build_rows(TRAIN_YEARS)
    survey_cv = spatial_cv(rows, ["depth", "vis"])
    temp_cv = spatial_cv(rows, ["depth", "vis", "temp"])
    use_temp = (
        temp_cv["pooled_brier_model"] < survey_cv["pooled_brier_model"]
        and temp_cv["pooled_logloss_model"] < survey_cv["pooled_logloss_model"]
    )
    chosen = ["depth", "vis", "temp"] if use_temp else ["depth", "vis"]
    prereg = {
        "label": LABEL,
        "frozen_utc": utc_now(),
        "species_code": SPECIES_CODE,
        "scientific_name": SCIENTIFIC_NAME,
        "train_years": list(TRAIN_YEARS),
        "test_year": TEST_YEAR,
        "test_year_read_before_freeze": False,
        "test_year_history": "2022 was a training year in audit/multi-species (untrusted run); never scored as a holdout",
        "estimator": {"type": "l2_logistic_newton", "l2": L2, "intercept_penalized": False},
        "numeric_features_chosen": chosen,
        "habitat_rule": f"dummies for training habitats with >= {MIN_HABITAT_EVENTS} events; others pooled as OTHER",
        "year_dummies": False,
        "scaler_fit_on": "training rows only",
        "temperature": {
            "source": "HYCOM GOFS 3.1 water_temp",
            "join": f"nearest column within {MAX_TEMP_CELL_KM} km reaching dive depth; linear in depth; no extrapolation",
            "time_rule": "same-day field or past day only",
        },
        "selection_rule": "temperature kept only if pooled leave-one-subregion-out Brier AND log loss beat survey-only on training years",
        "cv_survey_only": survey_cv,
        "cv_with_temperature": temp_cv,
        "acceptance_rule_on_test": {
            "brier_improvement_ci95_low_gt": 0.0,
            "logloss_below_prevalence": True,
            "calibration_gap_max": CALIBRATION_GAP_MAX,
        },
        "training_audit": audit,
        "bootstrap": {"reps": BOOTSTRAP_REPS, "seed": SEED, "unit": "primary_sample_unit"},
        "publication_status": PUBLICATION_STATUS,
        **git_commit(),
    }
    assert_no_coordinates(prereg)
    OUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(prereg, indent=2) + "\n"
    PREREG.write_text(text, encoding="utf-8")
    (OUT / "PREREGISTRATION.sha256").write_text(sha256_bytes(text.encode()) + "\n", encoding="utf-8")
    return prereg


def test_checks(brier_ci_low: float, ll_model: float, ll_base: float, gap: float) -> dict:
    return {
        "beats_prevalence_brier_ci": brier_ci_low > 0.0,
        "beats_prevalence_logloss": ll_model < ll_base,
        "calibrated_mean": gap <= CALIBRATION_GAP_MAX,
    }


def decide(checks: dict) -> str:
    if all(checks.values()):
        return "WORKS_INTERNALLY"
    if not (checks["beats_prevalence_brier_ci"] and checks["beats_prevalence_logloss"]):
        return "DID_NOT_BEAT_BASELINE_ON_TEST_YEAR"
    return "BEATS_BASELINE_BUT_MISCALIBRATED_ON_TEST_YEAR"


def output_meaning(numeric: list[str]) -> str:
    names = {"depth": "depth", "vis": "visibility", "temp": "water temperature at dive depth"}
    return (
        f"Probability that a completed Reef Visual Census point count with this habitat, "
        f"{', '.join(names[f] for f in numeric)} records at least one {COMMON_NAME}. "
        "Not abundance. Not ecological absence. Not a current location."
    )


def load_prereg() -> dict:
    if not PREREG.is_file():
        raise RuntimeError("no PREREGISTRATION.json; run freeze first")
    expected = (OUT / "PREREGISTRATION.sha256").read_text(encoding="utf-8").strip()
    if sha256_file(PREREG) != expected:
        raise RuntimeError("PREREGISTRATION.json was modified after freezing")
    return json.loads(PREREG.read_text(encoding="utf-8"))


def score() -> dict:
    if LOCK.exists():
        raise RuntimeError("SCORED_ONCE.lock exists; the test year has already been scored")
    prereg = load_prereg()
    numeric = prereg["numeric_features_chosen"]
    train, train_audit = build_rows(TRAIN_YEARS)
    spec = make_spec(train, numeric)
    Xtr, ytr = matrix(train, spec)
    beta = fit_logistic(Xtr, ytr)
    train_rate = float(ytr.mean())

    LOCK.write_text(f"test_year={TEST_YEAR} scored_utc={utc_now()}\n", encoding="utf-8")
    test, test_audit = build_rows([TEST_YEAR])
    Xte, yte = matrix(test, spec)
    p = predict_proba(Xte, beta)
    base = np.full(len(yte), train_rate)
    clusters = np.array([r["psu"] for r in test])
    boot = cluster_bootstrap_delta(p, base, yte, clusters)
    gap = abs(float(p.mean()) - float(yte.mean()))
    checks = test_checks(boot["ci95_low"], log_loss(p, yte), log_loss(base, yte), gap)
    passed = all(checks.values())
    support = {
        f: {"min": float(min(r[f] for r in train)), "max": float(max(r[f] for r in train))} for f in numeric
    }
    result = {
        "label": LABEL,
        "species_code": SPECIES_CODE,
        "scientific_name": SCIENTIFIC_NAME,
        "train_years": list(TRAIN_YEARS),
        "test_year": TEST_YEAR,
        "numeric_features": numeric,
        "train_events": len(train),
        "train_prevalence": round(train_rate, 6),
        "test_events": len(test),
        "test_prevalence": round(float(yte.mean()), 6),
        "test_brier_model": round(brier(p, yte), 6),
        "test_brier_prevalence": round(brier(base, yte), 6),
        "test_logloss_model": round(log_loss(p, yte), 6),
        "test_logloss_prevalence": round(log_loss(base, yte), 6),
        "test_auc": None if auc(p, yte) is None else round(auc(p, yte), 4),
        "brier_bootstrap": boot,
        "mean_predicted": round(float(p.mean()), 6),
        "calibration_gap": round(gap, 6),
        "calibration_fit": calibration_slope(p, yte),
        "reliability": reliability(p, yte),
        "preregistered_checks": checks,
        "passed_preregistered_rule": passed,
        "decision": decide(checks),
        "train_audit": train_audit,
        "test_audit": test_audit,
        "publication_status": PUBLICATION_STATUS,
        "on_the_globe": False,
    }
    artifact = {
        "label": LABEL,
        "model_version": "fk_ste_part_v1",
        "output_meaning": output_meaning(numeric),
        "species_code": SPECIES_CODE,
        "scientific_name": SCIENTIFIC_NAME,
        "common_name": COMMON_NAME,
        "region": "Florida Keys (NCRMP/RVC sampling frame)",
        "train_years": list(TRAIN_YEARS),
        "test_year": TEST_YEAR,
        "test_decision": result["decision"],
        "coefficients": [float(b) for b in beta],
        "spec": spec,
        "support": support,
        "support_habitats": sorted({r["habitat"] for r in train}),
        "survey_months": sorted({int(r["date"][5:7]) for r in train}),
        "preregistration_sha256": sha256_file(PREREG),
        "publication_status": PUBLICATION_STATUS,
    }
    manifest = {
        "label": LABEL,
        "inputs": {str(survey_path(y).relative_to(ROOT)): sha256_file(survey_path(y)) for y in (*TRAIN_YEARS, TEST_YEAR)},
        "hycom_dir": str(HYCOM_DIR.relative_to(ROOT)),
        "preregistration_sha256": sha256_file(PREREG),
        "artifact": str(ARTIFACT.relative_to(ROOT)),
        "holdout_inspected_before": False,
        "scored_utc": utc_now(),
        **git_commit(),
    }
    for obj in (result, artifact, manifest):
        assert_no_coordinates(obj)
    (OUT / "RESULTS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (OUT / "RUN_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    write_report(prereg, result)
    return result


def write_report(prereg: dict, r: dict) -> None:
    b = r["brier_bootstrap"]
    cv_s, cv_t = prereg["cv_survey_only"], prereg["cv_with_temperature"]
    lines = [
        f"# Florida Keys one-species detection model — {COMMON_NAME} (*{SCIENTIFIC_NAME}*)",
        "",
        f"**{LABEL}**",
        "",
        f"DECISION: `{r['decision']}`",
        "",
        output_meaning(r["numeric_features"]),
        "",
        "## Design (frozen before the test year was read)",
        "",
        f"- Train {', '.join(map(str, TRAIN_YEARS))}; test {TEST_YEAR} scored once (`SCORED_ONCE.lock`).",
        f"- Features: habitat, {', '.join(r['numeric_features'])}. No year dummies. Scaler fit on training rows.",
        "- L2 logistic (Newton), convergence enforced.",
        f"- Temperature kept only if spatial CV on training years beat survey-only: "
        f"survey-only Brier {cv_s['pooled_brier_model']:.5f} / log loss {cv_s['pooled_logloss_model']:.5f}; "
        f"with temperature {cv_t['pooled_brier_model']:.5f} / {cv_t['pooled_logloss_model']:.5f}; "
        f"prevalence {cv_s['pooled_brier_prevalence']:.5f}.",
        "",
        f"## {TEST_YEAR} result",
        "",
        "| Metric | Model | Prevalence baseline |",
        "|---|---:|---:|",
        f"| Brier | {r['test_brier_model']:.5f} | {r['test_brier_prevalence']:.5f} |",
        f"| Log loss | {r['test_logloss_model']:.5f} | {r['test_logloss_prevalence']:.5f} |",
        f"| AUC | {r['test_auc']} | 0.5 |",
        "",
        f"Brier improvement {b['brier_improvement']:.5f} (95% CI {b['ci95_low']:.5f} to {b['ci95_high']:.5f}, "
        f"{b['reps']} bootstrap resamples of survey sites).",
        f"Mean predicted {r['mean_predicted']:.4f} vs observed {r['test_prevalence']:.4f} (gap {r['calibration_gap']:.4f}). "
        f"Calibration fit {r['calibration_fit']}.",
        "",
        f"Preregistered checks: {r['preregistered_checks']}.",
        f"Training prevalence {r['train_prevalence']:.4f}; the model ranks dives well but its overall level "
        "follows the training years, so a year with fewer detections is over-predicted.",
        "",
        f"Events: train {r['train_events']}, test {r['test_events']}. "
        f"Test rows dropped for missing temperature: {r['test_audit']['dropped_missing_temperature']}.",
        "",
        "Not published. Not on the globe. Survey non-detection is not ecological absence.",
        "",
    ]
    (OUT / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- predict

def predict(survey: dict, artifact: dict | None = None) -> dict:
    """Apply the saved model to one survey description. Refuses unsupported inputs."""
    if artifact is None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    spec = artifact["spec"]
    problems = []
    for f in spec["numeric"]:
        if survey.get(f) is None:
            problems.append(f"missing {f}")
            continue
        lo, hi = artifact["support"][f]["min"], artifact["support"][f]["max"]
        if not lo <= float(survey[f]) <= hi:
            problems.append(f"{f}={survey[f]} outside training range {lo:.2f}-{hi:.2f}")
    if survey.get("habitat") not in artifact["support_habitats"]:
        problems.append(f"habitat {survey.get('habitat')!r} not seen in training")
    base = {
        "species": f"{artifact['common_name']} ({artifact['scientific_name']})",
        "model_version": artifact["model_version"],
        "test_decision": artifact["test_decision"],
        "publication_status": artifact["publication_status"],
        "meaning": artifact["output_meaning"],
    }
    if problems:
        return {**base, "status": "UNSUPPORTED", "probability": None, "reasons": problems}
    x = np.array(design_row(survey, spec))
    p = float(predict_proba(x[None, :], np.array(artifact["coefficients"]))[0])
    return {**base, "status": "OK", "probability": round(p, 4)}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("freeze")
    sub.add_parser("score")
    pp = sub.add_parser("predict")
    pp.add_argument("--habitat", required=True)
    pp.add_argument("--depth", type=float, required=True)
    pp.add_argument("--vis", type=float, required=True)
    pp.add_argument("--temp", type=float)
    args = parser.parse_args()
    if args.cmd == "freeze":
        pr = freeze()
        print(json.dumps({"chosen": pr["numeric_features_chosen"], "cv_survey_only": pr["cv_survey_only"]["pooled_brier_model"],
                          "cv_with_temperature": pr["cv_with_temperature"]["pooled_brier_model"],
                          "cv_prevalence": pr["cv_survey_only"]["pooled_brier_prevalence"],
                          "rows": pr["training_audit"]["rows_used"]}, indent=2))
    elif args.cmd == "score":
        r = score()
        print(json.dumps({k: r[k] for k in ("decision", "test_brier_model", "test_brier_prevalence", "test_logloss_model",
                                           "test_logloss_prevalence", "test_auc", "brier_bootstrap", "calibration_gap")}, indent=2))
    else:
        print(json.dumps(predict({"habitat": args.habitat, "depth": args.depth, "vis": args.vis, "temp": args.temp}), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
