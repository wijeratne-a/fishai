# fishaisdm (R modeling core)

CUFES delta models consume processed **`cufes_events`**, **`cufes_counts`**, and
along-track **event covariates** (see ingest PRs #4 and #2). `load_model_data()`
joins on `event_id`, projects each tow to a mesh location at the **UTM 11N track
midpoint** (km), and drops rows with missing endpoints or empty covariates (QC
summary on attribute `fishai_data_qc`).

## Effort offset (delta sdmTMB)

Sample volume **`volume_m3`** enters as **`log_effort = log(volume_m3)`**.
`fit_delta_engine()` passes `offset = "log_effort"` to `sdmTMB::sdmTMB()`. For
**delta** families, sdmTMB applies the offset to the **positive (catch rate)
component only**; the encounter component uses `log_effort` as a fixed effect in
the shared formula. Do not zero-fill effort or covariates—drop upstream or in
`load_model_data()` QC instead.
