#!/usr/bin/env python3
"""Southern California (SBC LTER) survey-detection models, one species at a time.

INTERNAL — NOT A LIVE LOCATION — NOT A FORECAST — NOT PUBLISHED.

Output is P(detected on a completed SBC LTER annual fish transect | visibility, giant kelp
frond density on the same transect and day[, HYCOM water temperature at the site's typical
depth]). It is not abundance, not ecological absence, and not where the fish is now.

Species: kelp bass / calico bass (Paralabrax clathratus) and barred sand bass
(Paralabrax nebulifer, a stand-in for the unconfirmed "striped bass" request).
Morone saxatilis is checked by `feasibility` and is not modeled.

Phases (each refuses to run out of order), per species:
  feasibility  detection counts per year for Morone saxatilis and the modeled species
  dryrun       training-year label counts and joins only; writes nothing that gates scoring
  freeze       training years only; site-grouped CV chooses the feature set; writes PREREGISTRATION.json
  rehearse     runs the full scoring code path on a training year into a temp dir (never the test year)
  score        verifies the preregistration, fits on training years, scores the test year once
  predict      applies the saved model to one survey description, with a support check

The estimator, metrics, spatial CV, bootstrap and decision rule are imported from the
Florida Keys pipeline, whose file is left byte-identical because it is the scored code of
a locked run.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

_fk_spec = importlib.util.spec_from_file_location("fk_core", ROOT / "scripts" / "modeling" / "florida_keys_one_species.py")
fk = importlib.util.module_from_spec(_fk_spec)
_fk_spec.loader.exec_module(fk)

RAW = ROOT / "data" / "raw" / "biological" / "sbc-lter"
FISH_CSV = RAW / "Annual_fish_comb_20250903.csv"
FISH_EML = RAW / "knb-lter-sbc.17.41.eml.xml"
KELP_CSV = RAW / "Annual_Kelp_All_Years_20250903.csv"
KELP_EML = RAW / "knb-lter-sbc.18.30.eml.xml"
HYCOM_DIR = ROOT / "data" / "restricted" / "environmental" / "hycom" / "socal-sbc" / "by-date"
OUT_ROOT = ROOT / "audit" / "socal-kelp-bass"
MODELS_DIR = ROOT / "models" / "socal"

FISH_PACKAGE = "knb-lter-sbc.17.41"
KELP_PACKAGE = "knb-lter-sbc.18.30"
MISSING = -99999
SURVEY_PROTOCOL = "FISH"
FISH_AREA_M2 = 80.0
KELP_AREA_M2 = 80.0
MAX_FISH_SIZE_CM = 250
HABITAT = "KELP_REEF"
TRAIN_YEARS = tuple(range(2001, 2019))
TEST_YEAR = 2022
BASE_FEATURES = ["vis", "kelp"]
TEMP_FEATURE = "temp"
MIN_TRAIN_DETECTIONS = 50
MIN_TEST_DETECTIONS = 10
MIN_SPECIES_ROW_COVERAGE = fk.MIN_SPECIES_ROW_COVERAGE
MAX_TEMP_CELL_KM = fk.MAX_TEMP_CELL_KM
PUBLICATION_STATUS = fk.PUBLICATION_STATUS
LABEL = fk.LABEL
FORBIDDEN_KEYS = fk.FORBIDDEN_KEYS | {"_lat", "_lon", "geometry", "bbox"}

SPECIES = {
    "kelp_bass": {
        "code": "PCLA",
        "scientific_name": "Paralabrax clathratus",
        "common_name": "kelp bass (calico bass)",
        "substitution": None,
    },
    "barred_sand_bass": {
        "code": "PNEB",
        "scientific_name": "Paralabrax nebulifer",
        "common_name": "barred sand bass",
        "substitution": (
            "SUBSTITUTION — USER MUST CONFIRM: the request said 'striped bass'. True striped bass "
            "(Morone saxatilis) is not on the SBC LTER fish list, so it cannot be modeled here. "
            "Barred sand bass is the likely intended fish; this model says nothing about Morone saxatilis."
        ),
    },
}
STRIPED_BASS_SCIENTIFIC = "Morone saxatilis"

TEST_YEAR_JUSTIFICATION = (
    "2022: inside HYCOM GLBy0.08 expt_93.0 coverage (ends 2024-09-05); all 11 sites and 44 transects "
    "surveyed; separated from the last training year by three unused years (2019-2021) so fixed, "
    "resurveyed transects are not scored in the year right after training; matches the Florida Keys "
    "test year. 2021 met the same criteria and had similar aggregate detection counts."
)
TRAIN_YEARS_JUSTIFICATION = (
    "2001-2018: every year with the full mainland site set and a late July/August survey window "
    "before the gap. 2000 excluded (3 sites only, surveyed in October). The two Santa Cruz Island "
    "sites start in 2004 and IVEE transects 3,5,6,7,8 in 2011; both enter training when they start."
)
TEST_YEAR_EXPOSURE = (
    "Before freezing, aggregate per-year counts (transects, transects with missing visibility, "
    "detected and zero transects for PCLA and PNEB) were printed for every year including 2022, "
    "during data exploration and the striped-bass feasibility check the task required. No model "
    "was fit to, evaluated on, or tuned against 2022, and no 2022 covariate values were examined."
)


# ---------------------------------------------------------------- utilities

def assert_no_coordinates(obj) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise RuntimeError(f"coordinate key {key!r} in output")
            assert_no_coordinates(value)
    elif isinstance(obj, list):
        for value in obj:
            assert_no_coordinates(value)


def assert_text_has_no_site_coordinates(text: str) -> None:
    for site in sbc_sites().values():
        for value in (site["_lat"], site["_lon"]):
            for digits in (2, 3, 4):
                if f"{value:.{digits}f}" in text:
                    raise RuntimeError("site coordinate value found in output text")


def parse_int(raw: str, field: str) -> int | None:
    """Integer field; MISSING -> None. Refuses non-integers and other negatives."""
    value = float(str(raw).strip())
    if value == MISSING:
        return None
    if value != int(value) or value < 0:
        raise RuntimeError(f"{field}={raw!r} is not a non-negative integer")
    return int(value)


def parse_float(raw: str) -> float | None:
    s = str(raw).strip()
    if s in ("", "NA") or float(s) == MISSING:
        return None
    return float(s)


def paths(species: str) -> dict:
    out = OUT_ROOT / species
    return {
        "out": out,
        "prereg": out / "PREREGISTRATION.json",
        "sha": out / "PREREGISTRATION.sha256",
        "lock": out / "SCORED_ONCE.lock",
        "artifact": MODELS_DIR / f"{species}_v1.json",
    }


# ---------------------------------------------------------------- metadata

def _eml_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_eml_units() -> dict:
    """COUNT must be a number of individuals and SIZE centimeters; refuse if the EML says otherwise."""
    text = _eml_text(FISH_EML)
    units = {}
    for block in re.findall(r"<attribute\b.*?</attribute>", text, re.S):
        name = re.search(r"<attributeName>(.*?)<", block).group(1).strip()
        found = re.findall(r"<(?:standardUnit|customUnit)>(.*?)<", block)
        units[name] = found[0] if found else None
    expected = {"COUNT": "number", "SIZE": "centimeter", "VIS": "meter", "AREA": "meterSquared"}
    for field, unit in expected.items():
        if units.get(field) != unit:
            raise RuntimeError(f"EML unit for {field} is {units.get(field)!r}, expected {unit!r}")
    if f'packageId="{FISH_PACKAGE}"' not in text:
        raise RuntimeError(f"fish EML is not {FISH_PACKAGE}")
    return {k: units[k] for k in expected}


@lru_cache(maxsize=1)
def sbc_sites() -> dict:
    """Site code -> reference point and typical depth (midpoint of the EML depth range).

    Coordinates stay in memory under underscore keys and are stripped before any output.
    """
    text = _eml_text(FISH_EML)
    names = {}
    for block in re.findall(r"<attribute\b.*?</attribute>", text, re.S):
        if re.search(r"<attributeName>\s*SITE\s*<", block):
            names = dict(re.findall(r"<code>(.*?)</code>\s*<definition>(.*?)</definition>", block, re.S))
    sites = {}
    covers = re.findall(r"<geographicCoverage.*?</geographicCoverage>", text, re.S)
    for code, name in names.items():
        matches = []
        for g in covers:
            desc = re.sub(r"\s+", " ", re.search(r"<geographicDescription>(.*?)</", g, re.S).group(1)).strip()
            if desc.startswith(f"{code}:") or name.startswith(desc.split(";")[0].strip()):
                matches.append((g, desc))
        if len(matches) != 1:
            raise RuntimeError(f"site {code}: {len(matches)} geographic coverages matched")
        g, desc = matches[0]
        m = re.search(r"(?i)depth range\w*\D*?(-?\d+(?:\.\d+)?)\s*(?:m|meters)?\s*to\s*(-?\d+(?:\.\d+)?)", desc)
        if not m:
            raise RuntimeError(f"site {code}: no depth range in EML description")
        lo, hi = sorted(abs(float(v)) for v in m.groups())
        bounds = {k: float(re.search(rf"<{k}>(.*?)<", g).group(1)) for k in (
            "westBoundingCoordinate", "eastBoundingCoordinate", "northBoundingCoordinate", "southBoundingCoordinate")}
        sites[code] = {
            "depth_min_m": lo,
            "depth_max_m": hi,
            "depth_m": round((lo + hi) / 2, 2),
            "_lat": (bounds["northBoundingCoordinate"] + bounds["southBoundingCoordinate"]) / 2,
            "_lon": (bounds["westBoundingCoordinate"] + bounds["eastBoundingCoordinate"]) / 2,
        }
    if len(sites) != 11:
        raise RuntimeError(f"expected 11 SBC sites, parsed {len(sites)}")
    return sites


def site_depth_table() -> dict:
    return {code: {k: v for k, v in s.items() if not k.startswith("_")} for code, s in sbc_sites().items()}


# ---------------------------------------------------------------- labels

@lru_cache(maxsize=1)
def _fish_rows() -> tuple:
    with FISH_CSV.open(encoding="utf-8", newline="") as handle:
        return tuple(r for r in csv.DictReader(handle) if r["SURVEY"] == SURVEY_PROTOCOL)


def events_from_rows(rows, year: int, code: str) -> list[dict]:
    """One record per completed standard fish transect (site x transect x date).

    Detection = any size-row COUNT > 0. A zero only if the transect has explicit rows for
    the code and every COUNT is 0. No rows, or -99999 without a positive row, is
    NOT_EVALUATED, never zero.
    """
    events: dict[tuple, dict] = {}
    year_codes: set[str] = set()
    for row in rows:
        if row["SURVEY"] != SURVEY_PROTOCOL or int(row["YEAR"]) != year:
            continue
        day = row["DATE"].strip()
        if not re.fullmatch(rf"{year}-\d\d-\d\d", day):
            raise RuntimeError(f"{year}: survey date {day!r} missing or outside the year")
        if float(row["AREA"]) != FISH_AREA_M2:
            raise RuntimeError(f"{year}: FISH row with AREA={row['AREA']} (protocol mix?)")
        site, transect = row["SITE"].strip(), row["TRANSECT"].strip()
        key = (site, transect, day)
        vis = parse_float(row["VIS"])
        rec = events.get(key)
        if rec is None:
            rec = {
                "year": year,
                "date": day,
                "month": int(day[5:7]),
                "site": site,
                "transect": f"{site}:{transect}",
                "block": site,
                "habitat": HABITAT,
                "vis": vis,
                "has_rows": False,
                "positive": False,
                "missing_count": False,
            }
            events[key] = rec
        elif rec["vis"] != vis:
            raise RuntimeError(f"{key}: visibility differs between rows of one transect survey")
        spp = row["SP_CODE"].strip()
        year_codes.add(spp)
        if spp != code:
            continue
        rec["has_rows"] = True
        count = parse_int(row["COUNT"], "COUNT")
        size = parse_float(row["SIZE"])
        if count is None:
            rec["missing_count"] = True
            continue
        if count == 0 and size is not None:
            raise RuntimeError(f"{key}: zero COUNT carries SIZE={size}; count and size may be swapped")
        if size is not None and not 0 < size <= MAX_FISH_SIZE_CM:
            raise RuntimeError(f"{key}: SIZE={size} cm implausible; count and size may be swapped")
        if count > 0:
            rec["positive"] = True
    if code not in year_codes:
        raise RuntimeError(f"{code} not on the {year} species list; year cannot be evaluated")
    out = list(events.values())
    coverage = sum(e["has_rows"] for e in out) / len(out)
    if coverage < MIN_SPECIES_ROW_COVERAGE:
        raise RuntimeError(
            f"{year}: only {coverage:.3f} of transects carry explicit rows for {code}; "
            "zero rows may have been dropped from the extract"
        )
    for e in out:
        if e["positive"]:
            e["label_state"], e["y"] = "DETECTED", 1
        elif e["has_rows"] and not e["missing_count"]:
            e["label_state"], e["y"] = "SURVEY_NONDETECTION", 0
        else:
            e["label_state"], e["y"] = "NOT_EVALUATED", None
    return out


def load_events(year: int, code: str) -> list[dict]:
    return events_from_rows(_fish_rows(), year, code)


# ---------------------------------------------------------------- kelp on the same transect

@lru_cache(maxsize=1)
def _kelp_index() -> dict:
    with KELP_CSV.open(encoding="utf-8", newline="") as handle:
        return kelp_index_from_rows(csv.DictReader(handle))


def kelp_index_from_rows(rows) -> dict:
    idx: dict[tuple, dict] = {}
    for row in rows:
        if row["SP_CODE"].strip() != "MAPY":
            continue
        key = (int(row["YEAR"]), row["SITE"].strip(), row["TRANSECT"].strip())
        e = idx.setdefault(key, {"dates": set(), "sections": {}, "fronds": 0, "missing": False})
        e["dates"].add(row["DATE"].strip())
        e["sections"][(row["QUAD"].strip(), row["SIDE"].strip())] = float(row["AREA"])
        fronds = parse_int(row["FRONDS"], "FRONDS")
        if fronds is None:
            e["missing"] = True
        else:
            e["fronds"] += fronds
    return idx


def kelp_value(entry: dict | None, day: str) -> tuple[float | None, str]:
    """log(1 + giant kelp fronds per m2) from the same transect on the same day, else refused."""
    if entry is None:
        return None, "NO_KELP_SURVEY"
    if entry["dates"] != {day}:
        return None, "KELP_NOT_SAME_DAY"
    if entry["missing"]:
        return None, "KELP_COUNT_MISSING"
    area = sum(entry["sections"].values())
    if area != KELP_AREA_M2:
        return None, "KELP_AREA_INCOMPLETE"
    return math.log1p(entry["fronds"] / area), "OK"


def attach_kelp(events: list[dict], index: dict | None = None) -> dict:
    index = _kelp_index() if index is None else index
    reasons: dict[str, int] = defaultdict(int)
    for e in events:
        e["kelp"], why = kelp_value(index.get((e["year"], e["site"], e["transect"].split(":", 1)[1])), e["date"])
        reasons[why] += 1
    return dict(reasons)


# ---------------------------------------------------------------- temperature

def load_hycom(day: str):
    """Florida Keys reader pointed at the SoCal store (status ok, never a future field)."""
    fk.HYCOM_DIR = HYCOM_DIR
    return fk.load_hycom(day)


def attach_temperature(events: list[dict]) -> dict:
    """Nearest HYCOM column within MAX_TEMP_CELL_KM reaching the site's typical depth."""
    sites = sbc_sites()
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
        per_site: dict[str, tuple] = {}
        for e in evs:
            if e["site"] not in per_site:
                s = sites[e["site"]]
                value, used = None, None
                dist = fk.haversine_km(s["_lat"], s["_lon"], lat2d, lon2d)
                for flat in np.argsort(dist, axis=None):
                    i, j = np.unravel_index(flat, dist.shape)
                    if dist[i, j] > MAX_TEMP_CELL_KM:
                        break
                    value = fk.temperature_at_depth(depths, temp[:, i, j], s["depth_m"])
                    if value is not None:
                        used = float(dist[i, j])
                        break
                per_site[e["site"]] = (value, used)
            e["temp"], used = per_site[e["site"]]
            e["temp_depth_m"] = sites[e["site"]]["depth_m"]
            if e["temp"] is None:
                missing_column += 1
            else:
                distances.append(used)
    n = len(events)
    return {
        "events": n,
        "matched": n - missing_file - missing_column,
        "missing_no_hycom_file": missing_file,
        "missing_no_column_within_km": missing_column,
        "max_cell_km": MAX_TEMP_CELL_KM,
        "depth_rule": "site typical depth = midpoint of the EML depth range (no per-transect depth in the data)",
        "cell_distance_km_median": round(float(np.median(distances)), 2) if distances else None,
        "cell_distance_km_p95": round(float(np.percentile(distances, 95)), 2) if distances else None,
    }


# ---------------------------------------------------------------- rows

def complete(e: dict) -> bool:
    return e["y"] is not None and all(e.get(f) is not None for f in (*BASE_FEATURES, TEMP_FEATURE))


def build_rows(years, code: str) -> tuple[list[dict], dict]:
    """Rows need a label and every candidate covariate, so both CV arms use identical rows."""
    events = []
    for year in years:
        events.extend(load_events(year, code))
    kelp = attach_kelp(events)
    join = attach_temperature(events)
    rows = [e for e in events if complete(e)]
    per_year = {}
    for year in years:
        ev = [e for e in events if e["year"] == year]
        used = [r for r in rows if r["year"] == year]
        temps = [r["temp"] for r in used]
        per_year[str(year)] = {
            "transects": len(ev),
            "detected": sum(e["y"] == 1 for e in ev),
            "zero": sum(e["y"] == 0 for e in ev),
            "not_evaluated": sum(e["y"] is None for e in ev),
            "rows_used": len(used),
            "prevalence_used": round(float(np.mean([r["y"] for r in used])), 4) if used else None,
            "temp_min": round(min(temps), 2) if temps else None,
            "temp_max": round(max(temps), 2) if temps else None,
        }
    audit = {
        "transects_loaded": len(events),
        "not_evaluated": sum(e["y"] is None for e in events),
        "missing_visibility": sum(e["vis"] is None for e in events),
        "kelp_join": kelp,
        "dropped_missing_temperature": sum(e["temp"] is None for e in events),
        "rows_used": len(rows),
        "detected_used": sum(r["y"] for r in rows),
        "sites": sorted({r["site"] for r in rows}),
        "temperature_join": join,
        "per_year": per_year,
    }
    return rows, audit


# ---------------------------------------------------------------- feasibility

def detection_counts_by_scientific_name(scientific_name: str) -> dict:
    """Per-year counts of standard fish transects with any COUNT > 0 for a scientific name."""
    rows = _fish_rows()
    transects: dict[int, set] = defaultdict(set)
    detected: dict[int, set] = defaultdict(set)
    on_list: dict[int, bool] = defaultdict(bool)
    for r in rows:
        year = int(r["YEAR"])
        key = (r["SITE"], r["TRANSECT"], r["DATE"])
        transects[year].add(key)
        if r["SCIENTIFIC_NAME"].strip() == scientific_name:
            on_list[year] = True
            count = parse_int(r["COUNT"], "COUNT")
            if count:
                detected[year].add(key)
    years = sorted(transects)
    return {
        str(y): {"transects": len(transects[y]), "on_species_list": on_list[y], "detected": len(detected[y])}
        for y in years
    }


def feasibility_verdict(counts: dict, train_years=TRAIN_YEARS, test_year=TEST_YEAR) -> dict:
    train = sum(counts.get(str(y), {}).get("detected", 0) for y in train_years)
    test = counts.get(str(test_year), {}).get("detected", 0)
    ok = train >= MIN_TRAIN_DETECTIONS and test >= MIN_TEST_DETECTIONS
    return {
        "train_detected_transects": train,
        "test_year_detected_transects": test,
        "thresholds": {"train_min": MIN_TRAIN_DETECTIONS, "test_min": MIN_TEST_DETECTIONS},
        "verdict": "FEASIBLE" if ok else "INSUFFICIENT_DETECTIONS",
    }


def feasibility() -> dict:
    out = {
        "label": LABEL,
        "source": FISH_PACKAGE,
        "protocol": f"SURVEY == {SURVEY_PROTOCOL} (40 m x 2 m, 0-2 m off the bottom); CRYPTIC FISH excluded",
        "train_years": list(TRAIN_YEARS),
        "test_year": TEST_YEAR,
        "test_year_exposure": TEST_YEAR_EXPOSURE,
        "species": {},
    }
    names = {STRIPED_BASS_SCIENTIFIC: "striped bass (true)"}
    names.update({v["scientific_name"]: v["common_name"] for v in SPECIES.values()})
    for sci, common in names.items():
        counts = detection_counts_by_scientific_name(sci)
        out["species"][sci] = {
            "common_name": common,
            "on_species_list_any_year": any(v["on_species_list"] for v in counts.values()),
            **feasibility_verdict(counts),
            "per_year": counts,
        }
    assert_no_coordinates(out)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "FEASIBILITY.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------- phases

def species_info(species: str) -> dict:
    if species not in SPECIES:
        raise RuntimeError(f"unknown species {species!r}; choose from {sorted(SPECIES)}")
    return SPECIES[species]


def dryrun(species: str) -> dict:
    info = species_info(species)
    rows, audit = build_rows(TRAIN_YEARS, info["code"])
    return {"species": species, "code": info["code"], "training_audit": audit, "site_depths": site_depth_table()}


def freeze(species: str) -> dict:
    info = species_info(species)
    p = paths(species)
    if p["prereg"].exists():
        raise RuntimeError("PREREGISTRATION.json already exists; refuse to re-freeze")
    units = verify_eml_units()
    rows, audit = build_rows(TRAIN_YEARS, info["code"])
    if audit["detected_used"] < MIN_TRAIN_DETECTIONS:
        raise RuntimeError(f"INSUFFICIENT_DETECTIONS: {audit['detected_used']} detected training transects")
    survey_cv = fk.spatial_cv(rows, list(BASE_FEATURES))
    temp_cv = fk.spatial_cv(rows, [*BASE_FEATURES, TEMP_FEATURE])
    use_temp = (
        temp_cv["pooled_brier_model"] < survey_cv["pooled_brier_model"]
        and temp_cv["pooled_logloss_model"] < survey_cv["pooled_logloss_model"]
    )
    chosen = [*BASE_FEATURES, TEMP_FEATURE] if use_temp else list(BASE_FEATURES)
    prereg = {
        "label": LABEL,
        "frozen_utc": fk.utc_now(),
        "species": species,
        "species_code": info["code"],
        "scientific_name": info["scientific_name"],
        "common_name": info["common_name"],
        "substitution": info["substitution"],
        "source": {"fish": FISH_PACKAGE, "kelp": KELP_PACKAGE, "protocol": SURVEY_PROTOCOL},
        "survey_unit": "one completed standard fish transect: site x transect x date (40 m x 2 m, 80 m2)",
        "label_rule": "detected if any size-row COUNT > 0; zero only if explicit rows all COUNT == 0; "
                      "no rows or -99999 without a positive row = NOT_EVALUATED (excluded, never zero)",
        "eml_units_verified": units,
        "train_years": list(TRAIN_YEARS),
        "train_years_justification": TRAIN_YEARS_JUSTIFICATION,
        "test_year": TEST_YEAR,
        "test_year_justification": TEST_YEAR_JUSTIFICATION,
        "test_year_read_before_freeze": False,
        "test_year_exposure": TEST_YEAR_EXPOSURE,
        "estimator": {"type": "l2_logistic_newton", "l2": fk.L2, "intercept_penalized": False},
        "numeric_features_chosen": chosen,
        "features": {
            "vis": "horizontal visibility (m) recorded at the start of the transect",
            "kelp": "log(1 + giant kelp fronds per m2) counted on the same transect on the same day "
                    f"({KELP_PACKAGE}); transects without a same-day complete kelp survey are refused",
            "temp": "HYCOM water_temp at the site's typical depth (EML depth-range midpoint)",
        },
        "habitat_rule": "single habitat (rocky-reef kelp forest); no habitat dummies",
        "site_effects": "none; site identity and site depth are not features (11 fixed sites would be memorized)",
        "year_dummies": False,
        "scaler_fit_on": "training rows only",
        "missing_data_policy": "rows missing label, visibility, kelp or temperature are dropped and counted; never imputed",
        "temperature": {
            "source": "HYCOM GOFS 3.1 water_temp (one experiment per year; see data/manifests/socal-environment-manifest.csv)",
            "join": f"nearest column within {MAX_TEMP_CELL_KM} km of the site reference point reaching the site's "
                    "typical depth; linear in depth; no extrapolation",
            "time_rule": "same-day 12:00 UTC field or past day only",
            "site_depths_m": site_depth_table(),
        },
        "selection_rule": "temperature kept only if pooled leave-one-site-out Brier AND log loss beat survey-only on training years",
        "cv_grouping": "leave one site out (11 folds max); sites are fixed and resurveyed every year",
        "cv_survey_only": survey_cv,
        "cv_with_temperature": temp_cv,
        "acceptance_rule_on_test": {
            "brier_improvement_ci95_low_gt": 0.0,
            "logloss_below_prevalence": True,
            "calibration_gap_max": fk.CALIBRATION_GAP_MAX,
        },
        "training_audit": audit,
        "bootstrap": {"reps": fk.BOOTSTRAP_REPS, "seed": fk.SEED, "unit": "site"},
        "publication_status": PUBLICATION_STATUS,
        **fk.git_commit(),
    }
    assert_no_coordinates(prereg)
    p["out"].mkdir(parents=True, exist_ok=True)
    text = json.dumps(prereg, indent=2) + "\n"
    assert_text_has_no_site_coordinates(text)
    p["prereg"].write_text(text, encoding="utf-8")
    p["sha"].write_text(fk.sha256_bytes(text.encode()) + "\n", encoding="utf-8")
    return prereg


def load_prereg(species: str) -> dict:
    p = paths(species)
    if not p["prereg"].is_file():
        raise RuntimeError("no PREREGISTRATION.json; run freeze first")
    expected = p["sha"].read_text(encoding="utf-8").strip()
    if fk.sha256_file(p["prereg"]) != expected:
        raise RuntimeError("PREREGISTRATION.json was modified after freezing")
    prereg = json.loads(p["prereg"].read_text(encoding="utf-8"))
    if prereg["species"] != species or prereg["train_years"] != list(TRAIN_YEARS) or prereg["test_year"] != TEST_YEAR:
        raise RuntimeError("preregistration does not match this script's species/train/test years")
    return prereg


def output_meaning(common_name: str, numeric: list[str]) -> str:
    names = {"vis": "visibility", "kelp": "giant kelp frond density on the transect",
             "temp": "water temperature at the site's typical depth"}
    return (
        f"Probability that a completed SBC LTER annual fish transect (40 m x 2 m, late July/August, "
        f"Santa Barbara Channel) with this {', '.join(names[f] for f in numeric)} records at least one "
        f"{common_name}. Not abundance. Not ecological absence. Not a current location."
    )


def score(species: str, test_year: int | None = None, rehearsal: bool = False) -> dict:
    info = species_info(species)
    p = paths(species)
    test_year = TEST_YEAR if test_year is None else test_year
    if not rehearsal and test_year != TEST_YEAR:
        raise RuntimeError("only the preregistered test year can be scored")
    if rehearsal and test_year not in TRAIN_YEARS:
        raise RuntimeError("rehearsal may only use a training year")
    if p["lock"].exists():
        raise RuntimeError("SCORED_ONCE.lock exists; the test year has already been scored")
    prereg = load_prereg(species)
    numeric = prereg["numeric_features_chosen"]
    train, train_audit = build_rows(TRAIN_YEARS, info["code"])
    spec = fk.make_spec(train, numeric)
    Xtr, ytr = fk.matrix(train, spec)
    beta = fk.fit_logistic(Xtr, ytr)
    train_rate = float(ytr.mean())

    p["lock"].write_text(f"test_year={test_year} scored_utc={fk.utc_now()}\n", encoding="utf-8")
    test, test_audit = build_rows([test_year], info["code"])
    Xte, yte = fk.matrix(test, spec)
    prob = fk.predict_proba(Xte, beta)
    base = np.full(len(yte), train_rate)
    clusters = np.array([r["site"] for r in test])
    boot = fk.cluster_bootstrap_delta(prob, base, yte, clusters)
    boot["resampling_unit"] = "site"
    boot["clusters"] = int(len(np.unique(clusters)))
    gap = abs(float(prob.mean()) - float(yte.mean()))
    ll_model, ll_base = fk.log_loss(prob, yte), fk.log_loss(base, yte)
    checks = fk.test_checks(boot["ci95_low"], ll_model, ll_base, gap)
    test_auc = fk.auc(prob, yte)
    support = {f: {"min": float(min(r[f] for r in train)), "max": float(max(r[f] for r in train))} for f in numeric}
    result = {
        "label": LABEL,
        "species": species,
        "species_code": info["code"],
        "scientific_name": info["scientific_name"],
        "substitution": info["substitution"],
        "train_years": list(TRAIN_YEARS),
        "test_year": test_year,
        "numeric_features": numeric,
        "train_events": len(train),
        "train_detected": int(ytr.sum()),
        "train_prevalence": round(train_rate, 6),
        "test_events": len(test),
        "test_detected": int(yte.sum()),
        "test_detected_meets_minimum": int(yte.sum()) >= MIN_TEST_DETECTIONS,
        "test_prevalence": round(float(yte.mean()), 6),
        "test_brier_model": round(fk.brier(prob, yte), 6),
        "test_brier_prevalence": round(fk.brier(base, yte), 6),
        "test_logloss_model": round(ll_model, 6),
        "test_logloss_prevalence": round(ll_base, 6),
        "test_auc": None if test_auc is None else round(test_auc, 4),
        "brier_bootstrap": boot,
        "mean_predicted": round(float(prob.mean()), 6),
        "calibration_gap": round(gap, 6),
        "calibration_fit": fk.calibration_slope(prob, yte),
        "reliability": fk.reliability(prob, yte),
        "preregistered_checks": checks,
        "passed_preregistered_rule": all(checks.values()),
        "decision": fk.decide(checks),
        "coefficients_standardized": dict(zip(["intercept", *numeric], [round(float(b), 4) for b in beta])),
        "train_audit": train_audit,
        "test_audit": test_audit,
        "publication_status": PUBLICATION_STATUS,
        "on_the_globe": False,
    }
    artifact = {
        "label": LABEL,
        "model_version": f"socal_{species}_v1",
        "output_meaning": output_meaning(info["common_name"], numeric),
        "species": species,
        "species_code": info["code"],
        "scientific_name": info["scientific_name"],
        "common_name": info["common_name"],
        "substitution": info["substitution"],
        "region": "Santa Barbara Channel, SBC LTER 11 kelp-forest reef sites (annual fish survey frame)",
        "train_years": list(TRAIN_YEARS),
        "test_year": test_year,
        "test_decision": result["decision"],
        "coefficients": [float(b) for b in beta],
        "spec": spec,
        "support": support,
        "support_habitats": [HABITAT],
        "survey_months": sorted({r["month"] for r in train}),
        "kelp_transform": "kelp = log(1 + fronds per m2)",
        "preregistration_sha256": fk.sha256_file(p["prereg"]),
        "publication_status": PUBLICATION_STATUS,
    }
    inputs = [FISH_CSV, FISH_EML, KELP_CSV, KELP_EML]
    manifest = {
        "label": LABEL,
        "species": species,
        "inputs": {str(f.relative_to(ROOT)): fk.sha256_file(f) for f in inputs},
        "source_packages": {"fish": FISH_PACKAGE, "kelp": KELP_PACKAGE},
        "hycom_dir": str(HYCOM_DIR.relative_to(ROOT)),
        "train_years": list(TRAIN_YEARS),
        "test_year": test_year,
        "estimator": prereg["estimator"],
        "features": numeric,
        "missing_data_policy": prereg["missing_data_policy"],
        "preregistration_sha256": fk.sha256_file(p["prereg"]),
        "artifact": str(p["artifact"]).replace(str(ROOT) + "/", ""),
        "holdout_inspected_before": False,
        "holdout_exposure_note": TEST_YEAR_EXPOSURE,
        "rehearsal": rehearsal,
        "scored_utc": fk.utc_now(),
        **fk.git_commit(),
    }
    for obj in (result, artifact, manifest):
        assert_no_coordinates(obj)
    report = report_text(prereg, result, info)
    assert_text_has_no_site_coordinates(report)
    texts = {n: json.dumps(o, indent=2) + "\n" for n, o in (("RESULTS.json", result), ("RUN_MANIFEST.json", manifest))}
    for text in texts.values():
        assert_text_has_no_site_coordinates(text)
    for name, text in texts.items():
        (p["out"] / name).write_text(text, encoding="utf-8")
    (p["out"] / "REPORT.md").write_text(report, encoding="utf-8")
    p["artifact"].parent.mkdir(parents=True, exist_ok=True)
    p["artifact"].write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return result


def rehearse(species: str, year: int = TRAIN_YEARS[-1]) -> dict:
    """Run the whole scoring path on a training year in a temp dir. Metrics are in-sample and meaningless."""
    global OUT_ROOT, MODELS_DIR
    real = paths(species)
    saved = (OUT_ROOT, MODELS_DIR)
    with tempfile.TemporaryDirectory() as tmp:
        OUT_ROOT, MODELS_DIR = Path(tmp) / "audit", Path(tmp) / "models"
        try:
            p = paths(species)
            p["out"].mkdir(parents=True)
            shutil.copy(real["prereg"], p["prereg"])
            shutil.copy(real["sha"], p["sha"])
            r = score(species, test_year=year, rehearsal=True)
            art = json.loads(p["artifact"].read_text(encoding="utf-8"))
            probe = {f: (art["support"][f]["min"] + art["support"][f]["max"]) / 2 for f in art["spec"]["numeric"]}
            pred = predict({**probe, "month": art["survey_months"][0]}, art)
            files = sorted(x.name for x in p["out"].iterdir())
        finally:
            OUT_ROOT, MODELS_DIR = saved
    if real["lock"].exists():
        raise RuntimeError("rehearsal must not create the real lock")
    return {"rehearsal_year": year, "decision_in_sample": r["decision"], "files": files, "predict_status": pred["status"]}


def report_text(prereg: dict, r: dict, info: dict) -> str:
    b = r["brier_bootstrap"]
    cv_s, cv_t = prereg["cv_survey_only"], prereg["cv_with_temperature"]
    ta = r["test_audit"]
    lines = [
        f"# SoCal (SBC LTER) one-species detection model — {info['common_name']} (*{info['scientific_name']}*)",
        "",
        f"**{LABEL}**",
        "",
    ]
    if info["substitution"]:
        lines += [f"> **{info['substitution']}**", ""]
    lines += [
        f"DECISION: `{r['decision']}`",
        "",
        output_meaning(info["common_name"], r["numeric_features"]),
        "",
        "## Data",
        "",
        f"- Fish: SBC LTER Reef Kelp Forest Community Dynamics: Fish abundance, `{FISH_PACKAGE}` "
        "(EDI; retrieved through the DataONE LTER member node because the EDI portal/PASTA now requires login). "
        "Standard `FISH` protocol only (40 m x 2 m transect, 0-2 m off the bottom); `CRYPTIC FISH` excluded.",
        f"- Kelp: giant kelp fronds on the same transect and day, `{KELP_PACKAGE}`.",
        "- Unit: one completed transect (site x transect x date). Detection = any COUNT > 0 over size rows; "
        "-99999 is missing (NOT_EVALUATED), never zero.",
        "- 11 fixed sites resurveyed every year: CV and bootstrap group by site.",
        "",
        "## Design (frozen before the test year was read)",
        "",
        f"- Train {TRAIN_YEARS[0]}-{TRAIN_YEARS[-1]}; test {r['test_year']} scored once (`SCORED_ONCE.lock`).",
        f"- Features: {', '.join(r['numeric_features'])}. No year dummies, no site effects, no habitat dummies. "
        "Scaler fit on training rows. L2 logistic (Newton), convergence enforced.",
        f"- Temperature kept only if leave-one-site-out CV on training years beat survey-only on Brier and log loss: "
        f"survey-only {cv_s['pooled_brier_model']:.5f} / {cv_s['pooled_logloss_model']:.5f}; "
        f"with temperature {cv_t['pooled_brier_model']:.5f} / {cv_t['pooled_logloss_model']:.5f}; "
        f"prevalence {cv_s['pooled_brier_prevalence']:.5f} / {cv_s['pooled_logloss_prevalence']:.5f}. "
        f"Chosen: {', '.join(r['numeric_features'])}.",
        f"- Test-year exposure disclosure: {TEST_YEAR_EXPOSURE}",
        "",
        f"## {r['test_year']} result",
        "",
        "| Metric | Model | Prevalence baseline |",
        "|---|---:|---:|",
        f"| Brier | {r['test_brier_model']:.5f} | {r['test_brier_prevalence']:.5f} |",
        f"| Log loss | {r['test_logloss_model']:.5f} | {r['test_logloss_prevalence']:.5f} |",
        f"| AUC | {r['test_auc']} | 0.5 |",
        "",
        f"Brier improvement {b['brier_improvement']:.5f} (95% CI {b['ci95_low']:.5f} to {b['ci95_high']:.5f}, "
        f"{b['reps']} bootstrap resamples of {b['clusters']} sites).",
        f"Mean predicted {r['mean_predicted']:.4f} vs observed {r['test_prevalence']:.4f} (gap {r['calibration_gap']:.4f}). "
        f"Calibration fit {r['calibration_fit']}.",
        "",
        f"Preregistered checks: {r['preregistered_checks']}.",
        f"Training prevalence {r['train_prevalence']:.4f} ({r['train_detected']} of {r['train_events']} transects); "
        f"test {r['test_detected']} of {r['test_events']} transects detected "
        f"(minimum {MIN_TEST_DETECTIONS} {'met' if r['test_detected_meets_minimum'] else 'NOT met'}).",
        f"Test rows dropped: not evaluated {ta['not_evaluated']}, missing visibility {ta['missing_visibility']}, "
        f"kelp join {ta['kelp_join']}, missing temperature {ta['dropped_missing_temperature']}.",
        "",
        "Small test set: one year of 11 sites, so the site bootstrap is coarse and a single year cannot "
        "separate model skill from that year's conditions.",
        "",
        "Not published. Not on the globe. Survey non-detection is not ecological absence.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------- predict

def predict(survey: dict, artifact: dict) -> dict:
    """Apply a saved model to one survey description. Refuses unsupported inputs."""
    spec = artifact["spec"]
    problems = []
    for f in spec["numeric"]:
        if survey.get(f) is None:
            problems.append(f"missing {f}")
            continue
        lo, hi = artifact["support"][f]["min"], artifact["support"][f]["max"]
        if not lo <= float(survey[f]) <= hi:
            problems.append(f"{f}={survey[f]} outside training range {lo:.2f}-{hi:.2f}")
    if survey.get("month") not in artifact["survey_months"]:
        problems.append(f"month {survey.get('month')!r} outside training survey months {artifact['survey_months']}")
    base = {
        "species": f"{artifact['common_name']} ({artifact['scientific_name']})",
        "model_version": artifact["model_version"],
        "test_decision": artifact["test_decision"],
        "publication_status": artifact["publication_status"],
        "meaning": artifact["output_meaning"],
        "substitution": artifact.get("substitution"),
    }
    if problems:
        return {**base, "status": "UNSUPPORTED", "probability": None, "reasons": problems}
    x = np.array(fk.design_row({**survey, "habitat": HABITAT}, spec))
    prob = float(fk.predict_proba(x[None, :], np.array(artifact["coefficients"]))[0])
    return {**base, "status": "OK", "probability": round(prob, 4)}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("feasibility")
    for name in ("dryrun", "freeze", "rehearse", "score"):
        sp = sub.add_parser(name)
        sp.add_argument("--species", required=True, choices=sorted(SPECIES))
    pp = sub.add_parser("predict")
    pp.add_argument("--species", required=True, choices=sorted(SPECIES))
    pp.add_argument("--vis", type=float, required=True)
    pp.add_argument("--kelp-fronds-per-m2", type=float, required=True)
    pp.add_argument("--month", type=int, required=True)
    pp.add_argument("--temp", type=float)
    args = parser.parse_args()
    if args.cmd == "feasibility":
        out = feasibility()
        print(json.dumps({k: {x: v[x] for x in ("on_species_list_any_year", "train_detected_transects",
                                                "test_year_detected_transects", "verdict")}
                          for k, v in out["species"].items()}, indent=2))
    elif args.cmd == "dryrun":
        print(json.dumps(dryrun(args.species), indent=2))
    elif args.cmd == "freeze":
        pr = freeze(args.species)
        print(json.dumps({"chosen": pr["numeric_features_chosen"],
                          "cv_survey_only": [pr["cv_survey_only"]["pooled_brier_model"], pr["cv_survey_only"]["pooled_logloss_model"]],
                          "cv_with_temperature": [pr["cv_with_temperature"]["pooled_brier_model"], pr["cv_with_temperature"]["pooled_logloss_model"]],
                          "cv_prevalence": [pr["cv_survey_only"]["pooled_brier_prevalence"], pr["cv_survey_only"]["pooled_logloss_prevalence"]],
                          "rows": pr["training_audit"]["rows_used"]}, indent=2))
    elif args.cmd == "rehearse":
        print(json.dumps(rehearse(args.species), indent=2))
    elif args.cmd == "score":
        r = score(args.species)
        print(json.dumps({k: r[k] for k in ("decision", "test_events", "test_detected", "test_brier_model",
                                           "test_brier_prevalence", "test_logloss_model", "test_logloss_prevalence",
                                           "test_auc", "brier_bootstrap", "mean_predicted", "test_prevalence")}, indent=2))
    else:
        if args.kelp_fronds_per_m2 < 0:
            parser.error("kelp fronds per m2 cannot be negative")
        artifact = json.loads(paths(args.species)["artifact"].read_text(encoding="utf-8"))
        survey = {"vis": args.vis, "kelp": math.log1p(args.kelp_fronds_per_m2), "temp": args.temp, "month": args.month}
        print(json.dumps(predict(survey, artifact), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
