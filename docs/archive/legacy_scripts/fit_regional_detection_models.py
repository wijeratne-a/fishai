#!/usr/bin/env python3
"""Regional detection baselines. Latest year is an untouched temporal holdout."""

from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit/multi-species"

HOLDOUT = {
    "Florida Keys": 2024,
    "Puerto Rico": 2023,
    "USVI": 2023,
    "Flower Garden Banks": 2024,
}
# If set, only these years train. Do not silently ingest an extra pre-holdout file.
LOCKED_TRAIN_YEARS = {
    "Puerto Rico": (2016, 2019, 2021),
}
LIMITS = {
    "Florida Keys": 6,
    "Puerto Rico": 4,
    "USVI": 4,
    "Flower Garden Banks": 2,
}


def sources():
    raw = ROOT / "data/raw/biological"
    for path in sorted(raw.glob("noaa-rvc-florida-keys-*.csv.gz")):
        year = int(path.name.split("-")[-1].split(".")[0])
        yield "Florida Keys", year, path
    base = raw / "noaa-ncrmp"
    for dataset, region in {
        "CRCP_Reef_Fish_Surveys_Puerto_Rico": "Puerto Rico",
        "CRCP_Reef_Fish_Surveys_USVI": "USVI",
        "CRCP_Reef_Fish_Surveys_Flower_Gardens": "Flower Garden Banks",
    }.items():
        for path in sorted((base / dataset).glob("*.csv.gz")):
            yield region, int(path.stem.split(".")[0]), path


def load_region(region: str):
    events = {}
    universe = defaultdict(set)
    for reg, year, path in sources():
        if reg != region:
            continue
        with gzip.open(path, "rt", encoding="latin-1", newline="") as handle:
            reader = csv.DictReader(handle)
            first = True
            for row in reader:
                year_s = (row.get("YEAR") or "").strip()
                if first and year_s == "":
                    first = False
                    continue
                first = False
                key = (year, (row.get("PRIMARY_SAMPLE_UNIT") or "").strip(), (row.get("STATION_NR") or "").strip(), (row.get("time") or "").strip())
                code = (row.get("SPECIES_CD") or "").strip()
                if not code:
                    continue
                universe[year].add(code)
                depth_s = (row.get("DEPTH") or row.get("SAMPLE_DEPTH") or "").strip()
                vis_s = (row.get("UNDERWATER_VISIBILITY") or "").strip()
                rec = events.get(key)
                if rec is None:
                    rec = {
                        "year": year,
                        "block": (row.get("SUB_REGION_NR") or row.get("SUB_REGION_NAME") or "NA").strip() or "NA",
                        "habitat": (row.get("HABITAT_CD") or "NA").strip() or "NA",
                        "depth": float(depth_s) if depth_s else None,
                        "vis": float(vis_s) if vis_s else None,
                        "pos": set(),
                        "name": {},
                    }
                    events[key] = rec
                if (row.get("SCIENTIFIC_NAME") or "").strip():
                    rec["name"][code] = (row.get("SCIENTIFIC_NAME") or "").strip()
                if float(row["NUM"]) > 0:
                    rec["pos"].add(code)
    return events, universe


def sigmoid(value: float) -> float:
    if value > 30:
        return 1.0
    if value < -30:
        return 0.0
    return 1.0 / (1.0 + math.exp(-value))


def fit(rows, habitats, years):
    width = len(design(rows[0], habitats, years))
    beta = [0.0] * width
    for _ in range(60):
        grad = [0.0] * len(beta)
        for rec in rows:
            x = design(rec, habitats, years)
            p = sigmoid(sum(b * xi for b, xi in zip(beta, x)))
            err = p - rec["y"]
            for i, xi in enumerate(x):
                grad[i] += err * xi
        scale = max(len(rows), 1)
        beta = [b - 0.08 * g / scale for b, g in zip(beta, grad)]
    if not beta or any(not math.isfinite(value) for value in beta):
        raise RuntimeError("NONFINITE_MODEL_PARAMETERS")
    return beta


def design(rec, habitats, years):
    if rec.get("depth") is None or rec.get("vis") is None:
        raise ValueError("design() refuses missing depth or visibility; do not invent 15")
    x = [1.0, float(rec["depth"]) / 30.0, float(rec["vis"]) / 30.0]
    for year in years[1:]:
        x.append(1.0 if rec["year"] == year else 0.0)
    # pad year slots to fixed? years list is the training years present
    for habitat in habitats[1:]:
        x.append(1.0 if rec["habitat"] == habitat else 0.0)
    return x


def metrics(pairs):
    n = len(pairs)
    brier = sum((p - y) ** 2 for p, y in pairs) / n
    ll = 0.0
    for p, y in pairs:
        p = min(max(p, 1e-6), 1 - 1e-6)
        ll += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    pos = [p for p, y in pairs if y == 1]
    neg = [p for p, y in pairs if y == 0]
    auc = None
    if pos and neg:
        wins = 0.0
        for p in pos:
            for nval in neg:
                wins += 1 if p > nval else 0.5 if p == nval else 0
        auc = wins / (len(pos) * len(neg))
    return brier, ll / n, auc


def rank_and_fit(region, events, universe):
    hold = HOLDOUT[region]
    locked = LOCKED_TRAIN_YEARS.get(region)
    train_years = list(locked) if locked else sorted(y for y in universe if y < hold)
    if hold not in universe or not train_years:
        return [], []
    shared = set.intersection(*[universe[y] for y in train_years + [hold]])
    ranked = []
    for code in shared:
        if "ITAJ" in code or "GOLIATH" in code:
            continue
        by_year = {}
        for year in train_years + [hold]:
            evs = [rec for rec in events.values() if rec["year"] == year and code in universe[year]]
            dets = sum(code in rec["pos"] for rec in evs)
            by_year[year] = (dets, len(evs))
        train_d = sum(by_year[y][0] for y in train_years)
        hold_d = by_year[hold][0]
        train_n = sum(by_year[y][1] for y in train_years)
        if train_d < 40 or hold_d < 8:
            continue
        prev = train_d / train_n
        if prev > 0.9 or prev < 0.05:
            continue
        blocks = defaultdict(int)
        for rec in events.values():
            if rec["year"] in train_years and code in rec["pos"]:
                blocks[rec["block"]] += 1
        if sum(v >= 5 for v in blocks.values()) < 2:
            continue
        name = ""
        for rec in events.values():
            if code in rec["name"]:
                name = rec["name"][code]
                break
        ranked.append((train_d, code, name, by_year, prev))
    ranked.sort(reverse=True)
    chosen = ranked[: LIMITS[region]]
    results = []
    for train_d, code, name, by_year, prev in chosen:
        rows = []
        for rec in events.values():
            if code not in universe[rec["year"]]:
                continue
            if rec["depth"] is None or rec.get("vis") is None:
                continue
            rows.append({
                "year": rec["year"],
                "block": rec["block"],
                "habitat": rec["habitat"],
                "depth": rec["depth"],
                "vis": rec["vis"],
                "y": 1 if code in rec["pos"] else 0,
            })
        train = [r for r in rows if r["year"] in train_years]
        test = [r for r in rows if r["year"] == hold]
        if len(train) < 50 or len(test) < 15 or sum(r["y"] for r in test) < 8:
            continue
        counts = {}
        for rec in train:
            counts[rec["habitat"]] = counts.get(rec["habitat"], 0) + 1
        habitats = [h for h, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:6]]
        years = sorted({r["year"] for r in train})
        blocks = sorted({r["block"] for r in train})
        pooled_m, pooled_b = [], []
        fold_ok = 0
        for block in blocks:
            tr = [r for r in train if r["block"] != block]
            te = [r for r in train if r["block"] == block]
            if len(te) < 8 or sum(r["y"] for r in tr) < 5:
                continue
            rate = sum(r["y"] for r in tr) / len(tr)
            beta = fit(tr, habitats, years)
            for rec in te:
                x = design(rec, habitats, years)
                pooled_m.append((sigmoid(sum(b * xi for b, xi in zip(beta, x))), rec["y"]))
                pooled_b.append((rate, rec["y"]))
            fold_ok += 1
        if not pooled_m:
            continue
        mb, ml, ma = metrics(pooled_m)
        bb, bl, _ = metrics(pooled_b)
        rate = sum(r["y"] for r in train) / len(train)
        beta = fit(train, habitats, years)
        hold_m, hold_b = [], []
        for rec in test:
            x = design(rec, habitats, years)
            hold_m.append((sigmoid(sum(b * xi for b, xi in zip(beta, x))), rec["y"]))
            hold_b.append((rate, rec["y"]))
        hb, hl, ha = metrics(hold_m)
        hbb, hbl, _ = metrics(hold_b)
        beat = hb < hbb and hl < hbl
        status = "BASELINE_VALIDATED" if beat else "FAILED_TEMPORAL_VALIDATION"
        if mb >= bb:
            status = "FAILED_SPATIAL_VALIDATION"
        results.append({
            "region": region,
            "species_code": code,
            "scientific_name": name,
            "train_years": ",".join(map(str, years)),
            "holdout_year": hold,
            "train_events": len(train),
            "holdout_events": len(test),
            "train_detections": sum(r["y"] for r in train),
            "holdout_detections": sum(r["y"] for r in test),
            "spatial_brier": round(mb, 4),
            "spatial_prevalence_brier": round(bb, 4),
            "holdout_brier": round(hb, 4),
            "holdout_prevalence_brier": round(hbb, 4),
            "holdout_logloss": round(hl, 4),
            "holdout_prevalence_logloss": round(hbl, 4),
            "holdout_auc": None if ha is None else round(ha, 3),
            "folds_used": fold_ok,
            "status": status,
        })
    return chosen, results


def main() -> None:
    all_results = []
    ranking_lines = ["region,species_code,scientific_name,train_detections,holdout_detections,train_prevalence"]
    for region in HOLDOUT:
        print(f"loading {region}", file=sys.stderr)
        events, universe = load_region(region)
        chosen, results = rank_and_fit(region, events, universe)
        for train_d, code, name, by_year, prev in chosen:
            hold = HOLDOUT[region]
            ranking_lines.append(
                f"{region},{code},{name},{train_d},{by_year[hold][0]},{prev:.3f}"
            )
        all_results.extend(results)
        print(f"{region} fitted {len(results)}", file=sys.stderr)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "REGIONAL_SPECIES_RANKING.csv").write_text("\n".join(ranking_lines) + "\n", encoding="utf-8")
    if all_results:
        with (OUT / "MODEL_RESULTS.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(all_results[0]))
            writer.writeheader()
            writer.writerows(all_results)
        with (OUT / "TEMPORAL_HOLDOUT_RESULTS.csv").open("w", newline="") as handle:
            fields = ["region", "species_code", "holdout_year", "holdout_events", "holdout_detections", "holdout_brier", "holdout_prevalence_brier", "holdout_logloss", "holdout_auc", "status"]
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_results)
    print(json.dumps({"fitted": len(all_results), "passed": sum(r["status"] == "BASELINE_VALIDATED" for r in all_results)}))


if __name__ == "__main__":
    main()
