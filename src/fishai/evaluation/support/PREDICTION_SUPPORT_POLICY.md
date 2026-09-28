# Prediction support policy

**Status:** Executable labeling policy for evaluation. Not a nowcast claim.

## Purpose

Every scored prediction point must carry a **support label** that states whether the query lies inside the numeric domain implied by training features. Support is not confidence and is not probability calibration.

## Inputs (no raw coordinates required)

- Query feature vector (numeric only)
- Training feature matrix (same columns, same order)
- Optional per-column `feature_kinds`: `spatial`, `environmental`, `temporal`, or `other`
- Distance thresholds (`support_max_distance`, `weak_max_distance`)

Coordinates are never required. Spatial structure, when present, is encoded as numeric proxy features (for example cell indices or scaled offsets), not as latitude/longitude in this module.

## Labels

| Label | Meaning |
|---|---|
| `SUPPORTED` | Nearest-train distance within support radius and all features inside training ranges |
| `WEAK_SUPPORT` | Inside weak radius or near range edges; still single-domain, not typed extrapolation |
| `SPATIAL_EXTRAPOLATION` | Spatial feature(s) outside training range (only that kind) |
| `ENVIRONMENTAL_EXTRAPOLATION` | Environmental feature(s) outside training range (only that kind) |
| `TEMPORAL_EXTRAPOLATION` | Temporal feature(s) outside training range (only that kind) |
| `UNSUPPORTED` | Beyond weak radius, multi-kind range violations, empty train, or untyped range failure |

## Rules

1. Distance uses Euclidean nearest-neighbor distance in feature space to the training set.
2. A feature is out of range when it falls outside `[train_min, train_max]` for that column (optional margin from config).
3. Exactly one typed kind out of range → that extrapolation label, even if distance is small.
4. Two or more typed kinds out of range → `UNSUPPORTED`.
5. Out of range with no typed kinds (all `other` / missing kinds) → `UNSUPPORTED`.
6. Support labels do not authorize publication, fishing guidance, or collapsing uncertainty into one score.

## Evaluation use

Report primary metrics **both pooled and stratified by support label**. Do not average away `UNSUPPORTED` points without stating the slice.
