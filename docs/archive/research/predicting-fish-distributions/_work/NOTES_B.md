# NOTES_B — coordinator

Track B: movement-method matrix, wildlife analogues, transferable forecast systems. No fitting, no globe, no bulk download.

## Telemetry limits (FishAI)

- FishAI has **no tags, no receivers, no PSAT/SPOT/Fastloc**. Anything that needs detections of tagged animals is `REQUIRES_TELEMETRY` or `REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA`.
- **None of the 25 methods is `DO_NOW`.** Closest next step on movement-adjacent work is survey **center-of-gravity** after environmental joins (`DO_AFTER_ENVIRONMENTAL_JOINS`), then **seasonal redistribution** only if a second season exists (`DO_AFTER_MORE_STRUCTURED_DATA`). SBC LTER is Jul–Aug only; RVC is not a seasonal series.
- Tags describe **tagged individuals**. Array geometry, tag failure, and detection range dominate “where the fish was not heard.” Do not treat receiver silence as absence (S11, S12).
- Fastloc GPS and archival **tidal** location are `NOT_RECOMMENDED` for current FishAI frames (Keys/PR/USVI/FGB reef fish; kelp bass). Surfacing GPS is the wrong animal; North Sea tidal geolocation is the wrong ocean.
- Public OTN/ATN/Movebank maps are **not** training labels. Embargo and coarsening rules exist (S84–S86).

## Larval connectivity

- Q6 is a **different question** from Q4/Q5. Particles are not adult movement.
- CMS / OpenDrift / Ichthyop need 3-D currents at spawning time, a spawning-location field, pelagic duration, and a behaviour rule. **Wrong behaviour can beat a passive run in the wrong direction** (Bode et al. 2019, P312): parentage on anemonefish showed biophysical models with incorrect vertical behaviour performed **worse than a passive-larva model**.
- Validation needs **parentage, otolith chemistry, or an equivalent origin dataset** at the same sites. Almany et al. 2017 (P311): clownfish observed 10–15 km, Laplacian 13–19 km, 90 percent of settlement within 31–43 km; butterflyfish 43–64 km; ~10,000 km², eight sites. That is not a Keys damselfish result.
- Public feasibility is **low** without a genetics/otolith partner. Priority: `REQUIRES_PARTNERSHIP_OR_RESTRICTED_DATA`.
- Do not advertise HYCOM-forced particles as a nowcast of adult damselfish.

## Forecast verification lessons (copy these)

- **Baseline first.** Keys damselfish detection beats intercept (Brier 0.095 vs 0.125). Kelp bass **failed 2022** (0.296 vs 0.244). Habitat-folder empty; do not join SST and claim a forecast.
- **Issue time.** Archive the ocean product that existed when the map was issued. HYCOM GLBy0.08 ends **2024-09-05**.
- **Lead time.** BirdCast reports 1–7 d skill separately (S20). FluSight scores weeks separately (P326). FishAI can at best score **survey-year** leads until cadence changes.
- **Nowcast refusal.** EPA NowCast needs two of the last three hours (P328). Biennial RVC is not a nowcast (Q7 vs Q2).
- **Emissions/driver bias.** HRRR-Smoke underpredicted PM2.5 when FRP was too low (P329). If the environmental driver is wrong at issue time, the downstream fish field is wrong.
- **Ensembles.** Reich et al. 2019 stack beat CDC unweighted mean (P326). Do not average a failed species model into a working one.
- **Probabilities.** Report Brier/reliability, not pins. Damselfish high-p bin was miscalibrated (0.907 vs 0.855).

## Matrix / sources housekeeping

- `MOVEMENT_METHOD_MATRIX.csv`: **25 data rows**, 18 columns. Priorities: 15 telemetry, 6 partnership, 2 not recommended, 1 after env joins, 1 after more structured data.
- `_work/SOURCES_B.csv`: **P300–P400** (101 rows). FluSight is Reich et al. 2019 *PLOS Computational Biology* e1007486 (not PNAS); 22 teams, 21-model stack, second in challenge, training CV score 0.406. Movebank “6 billion” **not** used. P329 DOI is **10.1175/BAMS-D-20-0329.1** (Chow, Yu, Young, Ahmadov et al.). P318 is method-class only (preprint). P303: HPE<15 retains 79% of VPS positions, mean error 3.3 m.
- Reuse S01–S123; do not duplicate those rows here.

## What not to tell product

- Do not promise individual fish locations.
- Do not treat one CalCOFI egg cruise as a larval-connectivity validating dataset for Keys or SBC.
- Do not treat 11 SBC sites × Jul–Aug as a seasonal redistribution series.
