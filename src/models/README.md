# fishaisdm (R modeling core)

Pilot CUFES models use **Poisson-link delta** (`delta_gamma(type = "poisson-link")`
or `delta_lognormal(type = "poisson-link")`). See **`docs/CUFES_DELTA_MODEL_SPEC.md`**.

## Effort offset

Sample volume **`volume_m3`** enters as **`offset = log(volume_m3)`** on both delta
components. Egg encounter probability follows **`p = 1 - exp(-exp(eta))`** with **`eta`**
including **`log(V)`**. Do not add **`log_effort`** to the pilot formula when using
Poisson-link (effort is offset-only).

## Reference volume (maps)

**`freeze_model(..., training_dat = dat)`** sets **`reference_volume_m3`** to the
median training volume (QC-passed events) and stores quantile metadata. **`predict_engine()`**
uses **`offset = rep(log(V_ref), n)`** on maps only; held-out scoring uses each event’s
own **`log(volume_m3)`** (see **`score_encounter_on_events()`**).
