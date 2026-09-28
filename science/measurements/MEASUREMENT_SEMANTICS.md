# Measurement semantics

**Status:** Binding validation contract.  
**Registry:** `science/measurements/UNIT_REGISTRY.yaml`  
**Conflicts:** `audit/measurements/UNIT_CONFLICTS.csv`

## Principle

Every measured value must carry an explicit **quantity**, **unit**, and **measurement type**. Silent unit swaps and quantity conflations are rejected.

## Atlantic RVC `NUM`

Atlantic Reef Visual Census / NCRMP extracts (Florida Keys, Puerto Rico, USVI, Flower Garden Banks) publish `NUM` as a **real-valued average**, not an integer fish count.

This follows existing audit language in `audit/multi-species/ATLANTIC_ZERO_SEMANTICS.md` and related zero-semantics notes:

- A zero row means that species code was on the year’s survey list and the published `NUM` was 0.
- `NUM` is not an integer count of fish.
- Detection at species level requires any length-bin row with `NUM > 0`; non-detection requires the code on the year list and all bins at 0.

Validation implications:

- `measurement_type=atlantic_rvc_num` must use unit `real_valued_average`.
- Treating `NUM` as an integer fish count is a unit/quantity conflict (`UC-NUM-AS-INTEGER-COUNT`).
- Do not cast `NUM` to `int` for modeling features without a documented policy outside this contract.

## Quantity boundaries

| Quantity | May be used as | Must not be treated as |
|---|---|---|
| `count` | Discrete individuals when the source says so | Areal density without area |
| `real_valued_average` | Atlantic RVC `NUM` index | Integer fish count |
| `cpue` | Catch or detections per documented effort | Absolute abundance |
| `abundance` | Source-defined abundance only | Synonym for CPUE |
| `sea_surface_temperature` | Skin / near-surface temperature | Bottom temperature |
| `bottom_temperature` | Near-bottom / bottom product | Analysed SST under another label |

## Unit conversion

- Length: feet must convert to meters with an explicit factor (`0.3048`). Labeling a foot value as meters without conversion fails.
- Temperature: Kelvin must convert to Celsius with an explicit offset (`K − 273.15`). Labeling Kelvin as Celsius without conversion fails.
- Date-only records use `time_precision=DAY`. Inventing an hour (or finer) is a conflict (`UC-DATE-ONLY-INVENTED-HOUR`).

## Environmental vs biological

SST, chlorophyll, currents, and similar fields are `subject_kind=ENVIRONMENTAL`. They are covariates, not fish observations. Surface SST must not be labeled `bottom_temperature`.

## Synthetic validation

`tests/measurements/test_units.py` exercises forbidden patterns with synthetic values only. No raw survey coordinates or live ocean grids are required.
