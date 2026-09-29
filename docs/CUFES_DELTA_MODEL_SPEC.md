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
- `reference_volume_source` (`n_events_fitting_frame`, `egg_split.fit_end`, volume quantiles)

No hard-coded round reference volumes.

**Prediction maps** always apply **`log(V_ref)`** to the component-1 linear predictor (and pass **`offset = rep(log(V_ref), n)`** to component 2). sdmTMB **`predict()`** with **`newdata`** returns component-1 **`est1`** without the training offset; FishAI adds **`log(V)`** back before **`1 - exp(-exp(eta))`**. Fitted per-event offsets are never replayed on maps.

Output metadata includes `reference_volume_m3` and states that egg encounter probability is **per \(V_\text{ref}\) m³ filtered**.

If `reference_volume_m3` is absent from the frozen config, prediction **refuses** output.

Gridded prediction row columns are defined in [CUFES_PREDICTION_OUTPUT_CONTRACT.md](CUFES_PREDICTION_OUTPUT_CONTRACT.md) (`p_encounter`, `p_lo90`, `p_hi90`, `ood_level`, `evidence_state`, `unknown_reason`, `lead_days`, per cell/species/day).

## Cross-validation and held-out scoring

**Held-out events** (spatial CV, LFO, frozen-model scoring) use each row’s own **`log(volume_m3)`** offset—the real sample effort. Only gridded map products use \(V_\text{ref}\).

### Spatial-block fold assignment (real CUFES events)

FishAI assigns folds on the modeling side from track midpoints in **EPSG:32611** (km). A ``fold_id`` column already on ``cufes_events`` is not authoritative: if any value disagrees with this assignment, loading stops.

| Parameter | Source in model YAML | Pilot value |
| --- | --- | --- |
| Block size (km) | ``max(mesh.cutoff_km, mesh.range_guess_km)`` | **60** (cutoff 9, range guess 60) |
| Assignment seed | ``prediction.seed`` | **20260928** |
| Number of folds | ``data.spatial_block_cv.n_folds`` | **4** |

Each event maps to one spatial block ``block_id = bx{floor(X/block)}_by{floor(Y/block)}`` in **EPSG:32611** (km). Block size is ``max(mesh.cutoff_km, mesh.range_guess_km)`` so blocks are at least the pre-registered spatial range. Blocks are sorted by grid row/column and centroid; contiguous segments of that order receive fold IDs ``1 … n_folds`` (deterministic from geometry and ``prediction.seed``; an MD5 digest breaks ties only). The species-agnostic table covers **all** ``cufes_events`` rows (fit and test windows) and is written as ``fold_assignment.csv`` (`event_id`, `fold_id`, `block_id`) with SHA-256 recorded in sensitivity run metadata. Spatial-block CV trains on fit-period rows only. For every event in that frame, the fold id assigned, the fold id used to score ELPD, and the fold id in ``fold_assignment`` are the same triple. ELPD selection compares only candidates that share that table and drops any run with a failed, non-converged, or non-finite fold.

### Egg-model temporal split

| Key | Role | Pilot value |
| --- | --- | --- |
| ``egg_split.fit_end`` | Inclusive last date for model fitting and spatial-block assignment | **2017-12-31** |
| ``egg_split.test_start`` / ``test_end`` | Held-out scoring window (not used as training rows) | **2018-01-01** – **2022-04-27** |
| ``egg_split.glorys_product_boundary`` | Events after this date use GLORYS **myint** (not **my**) for ocean inputs | **2021-06-30** |
| ``egg_split.test_score_include_post_boundary`` | When ``false``, test-period scoring excludes events after ``glorys_product_boundary`` | default **true** |

Leave-future-out CV trains on the fit window and scores holdout **event dates** in the test window. Spatial-block CV uses fit-period rows only.

### Barrier mesh

Pilot production configs set ``mesh.barrier.enabled: true`` with ``range_fraction: 0.1`` (Bakka land barrier; see ``add_barrier_land()``). Land polygons are loaded from ``mesh.barrier.land_sf_rds``.

Training and every spatial-CV fold mesh are built by ``build_fishai_production_mesh()``: plain mesh, then ``add_barrier_land()`` with the configured ``range_fraction``, then ``check_barrier()``. Barrier enabled requires a readable land polygon and non-empty barrier triangles; otherwise ``run_cv_spatial()`` stops. With the barrier disabled, fold meshes stay plain.

### Time index

``time_idx`` (days since ``data.time_idx_origin``, plus 1) is derived from event time with one fixed origin from the model config (frozen in the artifact config). It never depends on the earliest event in a frame, so fit, test, and all scopes give identical indices for identical timestamps. A missing or invalid origin, or an event before it, stops loading.

``time_idx`` is always recomputed from event timestamps. A supplied ``time_idx`` column is only validated: any missing value or disagreement with the timestamp-derived index stops loading. The pilot production configs use the stable epoch ``1990-01-01``, which precedes the earliest tracked pilot CUFES event (1996-03-15); the origin day is index 1. Changing the epoch changes every index and requires refitting. The artifact stores ``time_idx_origin``.

### Pilot covariates (upwelling)

Upwelling is removed from the sardine and anchovy pilot covariates and formulas; see ``prereg/pilot_model_upwelling_amendment.md``.

### Out-of-domain and DEGRADED output

Mahalanobis novelty is judged against distances of the frozen reference rows (0.99 quantile), never the prediction grid's own distribution. ``freeze_model()`` derives and stores the reference (the training-frame model covariate columns, upwelling excluded) in the artifact as ``reference`` and ``reference_cols``; production configs need no ``reference`` key, and ``predict_engine()`` refuses an artifact without them. Cells with ``ood_level >= 2`` are ``UNKNOWN``. ``DEGRADED`` keeps ``UNKNOWN`` cells and their reasons, leaves ``p_encounter`` unchanged, and widens only ``p_lo90`` and ``p_hi90`` around it by ``prediction.interval_widen`` (>= 1).
