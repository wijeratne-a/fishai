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

## Reference volume \(V_\text{ref}\) (maps only)

At freeze time, **`reference_volume_m3`** is the **median** `volume_m3` over training events that passed `load_model_data()` QC. The frozen artifact stores:

- `reference_volume_m3`
- `reference_volume_source` (`n_events`, `training_end`, volume quantiles)

No hard-coded round reference volumes.

**Prediction maps** always apply **`log(V_ref)`** to the component-1 linear predictor (and pass **`offset = rep(log(V_ref), n)`** to component 2). sdmTMB **`predict()`** with **`newdata`** returns component-1 **`est1`** without the training offset; FishAI adds **`log(V)`** back before **`1 - exp(-exp(eta))`**. Fitted per-event offsets are never replayed on maps.

Output metadata includes `reference_volume_m3` and states that encounter probability is **per \(V_\text{ref}\) m³ filtered**.

If `reference_volume_m3` is absent from the frozen config, prediction **refuses** output.

## Cross-validation and held-out scoring

**Held-out events** (spatial CV, LFO, frozen-model scoring) use each row’s own **`log(volume_m3)`** offset—the real sample effort. Only gridded map products use \(V_\text{ref}\).
