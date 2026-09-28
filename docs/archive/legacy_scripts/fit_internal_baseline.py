#!/usr/bin/env python3
"""Internal feasibility baseline for one reef fish. Not a published nowcast."""

from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "biological"
CODE = "CHA CAPI"
YEARS = (2018, 2022, 2024)


def load_events() -> list[dict]:
    events: dict[tuple, dict] = {}
    for year in YEARS:
        path = RAW / f"noaa-rvc-florida-keys-{year}.csv.gz"
        with gzip.open(path, "rt", encoding="latin-1", newline="") as handle:
            reader = csv.DictReader(handle)
            first = True
            for row in reader:
                if first and (row.get("YEAR") or "").strip() == "":
                    first = False
                    continue
                first = False
                key = (
                    year,
                    (row.get("PRIMARY_SAMPLE_UNIT") or "").strip(),
                    (row.get("STATION_NR") or "").strip(),
                    (row.get("time") or "").strip(),
                )
                rec = events.get(key)
                if rec is None:
                    vis = (row.get("UNDERWATER_VISIBILITY") or "").strip()
                    rec = {
                        "year": year,
                        "sub": (row.get("SUB_REGION_NR") or "").strip() or "NA",
                        "habitat": (row.get("HABITAT_CD") or "").strip() or "NA",
                        "depth": float(row["DEPTH"]),
                        "vis": float(vis) if vis else None,
                        "detected": False,
                    }
                    events[key] = rec
                if (row.get("SPECIES_CD") or "").strip() == CODE and float(row["NUM"]) > 0:
                    rec["detected"] = True
    rows = []
    for rec in events.values():
        if rec["vis"] is None:
            continue
        rows.append(rec)
    return rows


def sigmoid(value: float) -> float:
    if value > 30:
        return 1.0
    if value < -30:
        return 0.0
    return 1.0 / (1.0 + math.exp(-value))


def fit_logistic(rows: list[dict], habitats: list[str]) -> list[float]:
    # intercept, depth, vis, year2022, year2024, habitat dummies except first
    n_beta = 5 + len(habitats) - 1
    beta = [0.0] * n_beta
    for _ in range(80):
        grad = [0.0] * n_beta
        for rec in rows:
            x = design(rec, habitats)
            p = sigmoid(sum(b * xi for b, xi in zip(beta, x)))
            err = p - (1.0 if rec["detected"] else 0.0)
            for i, xi in enumerate(x):
                grad[i] += err * xi
        scale = max(len(rows), 1)
        beta = [b - 0.05 * g / scale for b, g in zip(beta, grad)]
    return beta


def design(rec: dict, habitats: list[str]) -> list[float]:
    x = [
        1.0,
        rec["depth"] / 30.0,
        rec["vis"] / 30.0,
        1.0 if rec["year"] == 2022 else 0.0,
        1.0 if rec["year"] == 2024 else 0.0,
    ]
    for habitat in habitats[1:]:
        x.append(1.0 if rec["habitat"] == habitat else 0.0)
    return x


def predict(beta: list[float], rec: dict, habitats: list[str]) -> float:
    return sigmoid(sum(b * xi for b, xi in zip(beta, design(rec, habitats))))


def brier(pairs: list[tuple[float, int]]) -> float:
    return sum((p - y) ** 2 for p, y in pairs) / len(pairs)


def logloss(pairs: list[tuple[float, int]]) -> float:
    total = 0.0
    for p, y in pairs:
        p = min(max(p, 1e-6), 1 - 1e-6)
        total += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return total / len(pairs)


def auc(pairs: list[tuple[float, int]]) -> float | None:
    pos = [p for p, y in pairs if y == 1]
    neg = [p for p, y in pairs if y == 0]
    if not pos or not neg:
        return None
    wins = 0.0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1
            elif p == n:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def main() -> None:
    rows = load_events()
    habitats = sorted({rec["habitat"] for rec in rows})
    by_sub: dict[str, list[dict]] = defaultdict(list)
    for rec in rows:
        by_sub[rec["sub"]].append(rec)
    fold_rows = []
    pooled_model: list[tuple[float, int]] = []
    pooled_base: list[tuple[float, int]] = []
    for held, test in by_sub.items():
        train = [rec for rec in rows if rec["sub"] != held]
        rate = sum(rec["detected"] for rec in train) / len(train)
        beta = fit_logistic(train, habitats)
        model_pairs = [(predict(beta, rec, habitats), int(rec["detected"])) for rec in test]
        base_pairs = [(rate, int(rec["detected"])) for rec in test]
        pooled_model.extend(model_pairs)
        pooled_base.extend(base_pairs)
        fold_rows.append(
            {
                "held_block_n": len(test),
                "held_positives": sum(rec["detected"] for rec in test),
                "model_brier": round(brier(model_pairs), 4),
                "baseline_brier": round(brier(base_pairs), 4),
                "model_logloss": round(logloss(model_pairs), 4),
                "baseline_logloss": round(logloss(base_pairs), 4),
            }
        )
    year_rows = []
    for held in YEARS:
        train = [rec for rec in rows if rec["year"] != held]
        test = [rec for rec in rows if rec["year"] == held]
        rate = sum(rec["detected"] for rec in train) / len(train)
        beta = fit_logistic(train, habitats)
        model_pairs = [(predict(beta, rec, habitats), int(rec["detected"])) for rec in test]
        base_pairs = [(rate, int(rec["detected"])) for rec in test]
        year_rows.append(
            {
                "held_year": held,
                "n": len(test),
                "positives": sum(rec["detected"] for rec in test),
                "model_brier": round(brier(model_pairs), 4),
                "baseline_brier": round(brier(base_pairs), 4),
                "model_logloss": round(logloss(model_pairs), 4),
                "baseline_logloss": round(logloss(base_pairs), 4),
                "model_auc": None if auc(model_pairs) is None else round(auc(model_pairs), 3),
                "protocol_note": "2024 accession page describes a single-stage design; do not treat that year as a matched holdout.",
            }
        )
    report = {
        "label": "INTERNAL FEASIBILITY MODEL — NOT PUBLISHED",
        "species_code": CODE,
        "events_with_visibility": len(rows),
        "detections": sum(rec["detected"] for rec in rows),
        "spatial_blocks": len(by_sub),
        "pooled_spatial_model_brier": round(brier(pooled_model), 4),
        "pooled_spatial_prevalence_brier": round(brier(pooled_base), 4),
        "pooled_spatial_model_logloss": round(logloss(pooled_model), 4),
        "pooled_spatial_prevalence_logloss": round(logloss(pooled_base), 4),
        "folds": fold_rows,
        "leave_one_year": year_rows,
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
