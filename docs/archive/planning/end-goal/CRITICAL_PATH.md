# Critical path

**Current phase:** `GLOBAL_DATA_ACQUISITION`  
**Publication:** No species card is `PUBLISHED`. No nowcast or forecast is issued. Do **not** publish a globe occurrence/probability layer.

## Critical path (ordered)

1. **Keep acquiring structured surveys** into ignored `data/raw/` with manifests and checksums. Prefer zero-bearing Atlantic gaps only when catalog years exist; do not invent Pacific zeros.
2. **Do not refit** the Puerto Rico baselines (or any species suite) in this phase. The two 2023-holdout passes remain internal historical detection models, not nowcasts.
3. **Do not join and score environmental models** as a substitute for acquisition work in this phase. The next *scientific* dependency after the phase allows it is historical environmental match (starting with verified `jplMURSST41` to Puerto Rico survey dates in protected storage)—recorded here so it is not forgotten, not so it is executed now.
4. **Leave forecast/current ocean acquisition blocked** until a real dataset ID is verified (WCOFS still not subset; RTOFS CoastWatch search HTTP 404; Copernicus needs an account). No large grid downloads in tight loops.
5. **Keep the globe as a historical atlas** (Earth, past reports, unknown). Goliath remains without published locations.

## Explicit non-goals this phase

- Fitting or expanding species models  
- Applying bias corrections  
- Publishing a global probability or current-location layer  
- Treating GEBCO or unjoined SST snippets as ready predictors  

## Next action on the critical path

Continue structured survey acquisition and manifest hygiene. Defer historical SST–dive matching and any refit until this acquisition phase is ended by the user.
