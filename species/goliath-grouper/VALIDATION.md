# Validation design — Atlantic goliath grouper

**Status:** Designed. **These tests have NOT been run.** There is no held-out fit, no skill table, and no calibration plot.

A model that has not beaten a baseline on honest holdout **must not** drive a current-estimate or forecast globe layer. Today that rule keeps those layers **off**.

---

## Tests (to run later, on real held-out data)

| Test | What it asks | Metric candidates (not computed) |
|---|---|---|
| **Spatial-block holdout** | Does the model work in a withheld SW Florida block (e.g. hold out a coarsened Ten Thousand Islands cell set)? | AUC / log-loss for occupancy; never a three-decimal “hotspot” sold as truth |
| **Temporal / time-forward holdout** | Train on years ≤ T; test on years > T using only data available at T | Same, plus reliability (calibration) |
| **Method holdout** | Train on one observation type (e.g. compiled OBIS); test on another (e.g. visual survey) if rights allow | Transfer log-loss; reveal method bias |
| **Prospective** | Issue a dated prediction; score against **later** observations | Brier / log-loss vs **baseline**; as-of replay required |

**Baselines to beat (not fitted here):**
1. Range envelope (in-range vs out-of-range).
2. Seasonal frequency (Jul–Sep vs other months) on historical reports — **historical only**.
3. Habitat-only suitability (mangrove / structure / depth) — **not presence**.
4. Historical occurrence density (coarse OBIS) — **not current presence**.

If an advanced model loses to (1)–(4), it stays `NOT READY FOR USE`.

---

## What must not be used as a metric theater

- Invented accuracy percentages
- SST/chlorophyll correlation sold as presence skill
- AIS density as a fish score
- Training-set AUC without spatial and temporal holdout
- Scoring a forecast with later-revised covariates (as-of leak)

---

## Record of runs

| Date | Test | Data | Result |
|---|---|---|---|
| 2026-09-22 | All of the above | None held out; no model fitted | **NOT RUN** |

OBIS compiled totals in `MODEL_LADDER.md` are a **count of rows**, not a validation result.
