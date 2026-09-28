# CUFES egg delta model (sdmTMB pilot)

**Status:** Active modeling contract for Southern California Bight CUFES sardine/anchovy pilots.

## Family

Pilot configs use **Poisson-link delta** models:

- Primary: `delta_gamma(type = "poisson-link")`
- Alternative: `delta_lognormal(type = "poisson-link")`

Legacy standard delta (`delta_type: standard`) remains available for experiments but is not the pilot default.

## Effort and offset

Sample volume **`volume_m3`** enters the likelihood as **`offset = log(volume_m3)`** on both delta components for Poisson-link fits.

On the **encounter (component 1)** linear predictor, the offset is the log of egg **number density** scale; with Poisson filtering,

\[
p = 1 - \exp(-n \cdot V) = 1 - \exp(-\exp(\eta))
\]

where \(\eta\) includes \(\log(V)\). The **positive (component 2)** mean carries the same offset.

Training formulas should **not** duplicate effort as `log_effort` in the fixed effects when using Poisson-link; effort is only the offset column.

## Counts (`cufes_counts`)

Long-format **`event_id` × `taxon` × `count`**. If a taxon was **not** counted on an event, there is **no row** (never an implicit zero). Each species model inner-joins events to that taxon’s rows only; QC logs **`excluded_no_count_row`**.

## Reference volume \(V_\text{ref}\) (maps only)

At freeze time, **`reference_volume_m3`** is the **median** `volume_m3` over the species **final fitting frame** (after count-row join and all QC drops). Metadata records **`n_events_fitting_frame`**.

- `reference_volume_m3`
- `reference_volume_source` (`n_events_fitting_frame`, `training_end`, volume quantiles)

No hard-coded round reference volumes.

**Prediction maps** always apply **`log(V_ref)`** to the component-1 linear predictor (and pass **`offset = rep(log(V_ref), n)`** to component 2). sdmTMB **`predict()`** with **`newdata`** returns component-1 **`est1`** without the training offset; FishAI adds **`log(V)`** back before **`1 - exp(-exp(eta))`**. Fitted per-event offsets are never replayed on maps.

Output metadata includes `reference_volume_m3` and states that encounter probability is **per \(V_\text{ref}\) m³ filtered**.

If `reference_volume_m3` is absent from the frozen config, prediction **refuses** output.

## Cross-validation and held-out scoring

**Held-out events** (spatial CV, LFO, frozen-model scoring) use each row’s own **`log(volume_m3)`** offset—the real sample effort. Only gridded map products use \(V_\text{ref}\).

### Spatial-block fold assignment (real CUFES events)

When bot1 ``cufes_events`` has no ``fold_id`` column, FishAI assigns folds on the modeling side from track midpoints in **EPSG:32611** (km):

| Parameter | Source in model YAML | Pilot value |
| --- | --- | --- |
| Block size (km) | ``mesh.cutoff_km`` | **9** |
| Assignment seed | ``prediction.seed`` | **20260928** |
| Number of folds | ``data.spatial_block_cv.n_folds`` | **4** |

Each event maps to one spatial block ``block_id = bx{floor(X/block)}_by{floor(Y/block)}``; ``fold_id`` is a deterministic function of ``block_id``, the seed, and ``n_folds`` (MD5 of ``seed:block_id``, first seven hex digits mod ``n_folds``). The table is species-agnostic (events only) and written as ``fold_assignment.csv`` (`event_id`, `fold_id`, `block_id`) with SHA-256 recorded in sensitivity run metadata. Leave-future-out CV continues to use existing ``time_idx`` logic.
