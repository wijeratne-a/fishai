# Behavior evidence notes (WS43)

Research catalog only. Hypotheses are **not** encoded into a fitted FishAI model in this workstream.

## Scope rules followed

- Each hypothesis names a **group or stock**, a **region**, and a **life stage** (or survey frame stage).
- One population’s result is not generalized to the species.
- No sample sizes invented. `sample_size_claim` stays `none_stated` until a power analysis or counted table exists.
- No paper DOIs fabricated. Established ecological patterns are labeled `established-pattern` and remain `untested-for-FishAI` until a local frame exists.
- SST, chlorophyll, and salinity are **guild-varying candidates**, not universal behavior drivers (see `features/`).

## What exists locally vs not

| Need | Repo status |
|---|---|
| Reef survey depth, visibility, habitat code | Present on Atlantic RVC tables; used in internal survey-only baselines |
| MUR analysed SST (`jplMURSST41`) | Snippet / small box only; **not joined** to dives |
| WCOFS / Copernicus / RTOFS forecasts | **Not acquired** (WCOFS not subset; Copernicus no credentials; RTOFS search HTTP 404) |
| Bottom temperature, oxygen, rugosity grids, seagrass/mangrove maps | **Not acquired in this repo** |
| Mesopelagic / deep-sea effort frames | **Absent** |
| Fitted behavior or environmental models | **None** in this lane |

## Established patterns vs FishAI tests

- **Diel vertical migration in mesopelagic fishes** (H-BEH-005): marked `established-pattern` / `untested-for-FishAI`. No DOI invented. No amplitude estimated here.
- **OMZ-associated mesopelagic vertical structure** (H-BEH-006): same confidence pattern; oxygen products not in repo.
- All RVC-linked hypotheses (H-BEH-001–004, H-BEH-016): mechanisms are plausible for visual reef surveys; **FishAI has not filed a dedicated behavior contrast** beyond noting that depth/visibility/habitat enter survey-only baselines. Environmental SST skill for the two Puerto Rico accepted species remains a proposed next test, not a result.

## Explicit non-claims

- No nowcast or forecast is issued from these hypotheses.
- Egg/larva patterns (e.g. CUFES) are not adult locations.
- Nursery/mangrove hypotheses must stay coarse; precise nursery pins stay withheld.
- Catalog rows are not training features until a separate modeling lane joins verified fields under as-of rules.

## Files in this folder

- `BEHAVIOR_VARIABLE_CATALOG.csv` — behavior-relevant variables and links to feature IDs
- `SPECIES_BEHAVIOR_HYPOTHESES.csv` — scoped testable claims
- `BEHAVIOR_EVIDENCE_NOTES.md` — this note
