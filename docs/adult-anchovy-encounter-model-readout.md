# Adult northern anchovy encounter model — fit readout

Branch: `cursor/fishai-adult-anchovy-fit-cv-79f5`. Public ERDDAP + Copernicus GLORYS only.

## Training table (rebuilt 2026-10-06)

| Check | Result |
|---|---:|
| Presence rows (both species) | 307 |
| Observation rows (presences + implied absences, post-GLORYS QC) | 1,140 |
| Physics events (pilot bbox) | 706 |
| Adult L50 gates | sardine ≥160 mm SL; anchovy ≥98 mm SL |

Anchovy modeling frame after covariate exclusion and effort QC: **400** rows (**154** presences, **246** absences). Purse-seine nearshore sets use a **1 min reference effort** for the Poisson offset (`log(1)=0`); trawl rows use observed tow duration.

## Model spec

Mirrors validated CUFES egg anchovy config (`configs/models/cufes_anchovy.yaml`): **sdmTMB** delta-gamma, **poisson-link**, spatial **[on, on]**, spatiotemporal **[off, off]**, barrier mesh, **rw0** daily intercept. Spatial-block CV: **60 km** blocks, seed **20260928**, **4** folds, sequential fits.

## Spatial-block CV scores (2026-10-06)

| Metric | Value |
|---|---:|
| Summed ELPD (4 folds, eligible) | **−1074.69** |
| Fold log-lik | −57.04, −220.65, −432.35, −364.66 |
| Out-of-fold AUC | **0.850** |
| Out-of-fold TSS (threshold 0.5) | **0.462** |
| Out-of-fold Boyce (moving-window) | **0.600** |
| Fit rows | 400 (154 presences, 246 absences) |

Full manifest: `prereg/adult_anchovy_spatial_block_cv_scores.json`.

## Product language

Maps and copy describe **adult encounter / spawning-season distribution evidence** from fishery-independent CPS surveys — not live fish tracking, not harvest advice.
