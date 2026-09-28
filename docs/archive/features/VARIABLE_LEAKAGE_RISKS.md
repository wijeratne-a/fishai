# Variable leakage risks (WS44)

Catalog status only. No model training in this workstream. No joins claimed beyond what manifests already record.

## Rules already binding in this repo

- Environmental fields are covariates (`ENVIRONMENTAL_CONDITION`), not fish observations.
- Joins must respect as-of `published_at_utc`; future fields must not enter training rows.
- Habitat suitability is not presence.
- Survey non-detection is not proof of absence from the surrounding landscape.
- Sensitive nursery/wreck/spawning sites must not be disclosed as precise public geometry.

## Risk register by variable class

| Variable class | Leakage / misuse mode | Severity | Mitigation for FishAI |
|---|---|---|---|
| Survey depth, visibility, habitat code | Using the same dive fields that define the sample without spatial/temporal holdouts; treating habitat code as the animal | Medium | Keep protocol holdouts; label habitat as station condition; do not publish raw station codes as presence |
| Hard-bottom / rugosity (not acquired) | Deriving structure from the same dive that labels detection, or painting bathymetry as reef fish | High if invented from labels | Do not fabricate rugosity IDs; GEBCO not downloaded; bathymetry ≠ presence |
| Analysed SST (`jplMURSST41` snippet only) | Joining post-event analysis as if it were an issued forecast; treating SST as a fish layer; using future SST relative to event time | High | Snippet exists and is **not joined**; any future join needs as-of cutoff and spatial support match |
| Bottom temperature / oxygen / substrate maps (not acquired) | Borrowing surface SST/chl as if they were bottom fields; claiming depth-resolved skill without profiles | High | Mark as not acquired; demersal models need depth-matched fields |
| Chlorophyll / salinity (not acquired) | Equating productivity or salinity envelopes with abundance; inventing Copernicus product IDs | High | Status remains not acquired / account required |
| WCOFS / RTOFS / Copernicus forecast candidates | Training on fields that would not have been issued by event time; painting forecast grids as animals | Critical | WCOFS not subset; RTOFS search HTTP 404; Copernicus no credentials — **not acquired in this repo** |
| Mangrove / seagrass / nursery proximity | Public precise nursery pins; generalizing one estuary’s juveniles to the species | High (safety + science) | Keep coarse units; scope hypotheses by life stage and region |
| Time of day / light | Encoding a fitted diel model from one population as a global species law | Medium | Keep as testable scoped hypotheses in `research/behavior/` only; not a fitted product |

## Guild-specific notes

- **Reef / coral:** emphasize depth, visibility, rugosity/hard-bottom, habitat code. SST/chl/salinity are **candidates that vary by guild**, not defaults.
- **Demersal soft / rocky:** emphasize bottom temperature, oxygen, substrate. Skin SST is a weak proxy.
- **Mesopelagic / deep-sea:** surface SST/chl/salinity are generally weak or excluded; light, time of day, oxygen, and depth matter more.
- **Estuarine / mangrove / diadromous:** salinity, tide, and discharge dominate; do not copy reef predictor sets.

## Verified source facts used here

- `jplMURSST41`: probed snippet / small box only; **not joined**.
- WCOFS: candidate; **not acquired**.
- Copernicus Marine: **not acquired** (credentials).
- RTOFS forecast search: **HTTP 404**; no grid; dataset ID **not identified**.
- GEBCO: **not downloaded**.
- RVC depth, visibility, habitat code: present on survey tables; used in internal baselines only.

If a source is unclear, treat it as **not acquired in this repo**.
