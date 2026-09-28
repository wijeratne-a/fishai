# Actionable data-to-prediction audit

**Date:** 2026-09-23  
**Scope:** repository as it exists. Planning prose is not implementation.

```
CURRENT STATE: Historical globe plus planning. No approved biological training table. No fitted model. No nowcast. No forecast.
DOMINANT BOTTLENECK: RIGHTS_AND_PERMISSION
FIRST MODEL RECOMMENDATION: After written clearance of NCEI Accession 0282183, fit a detection-given-effort model for one common Florida Keys reef fish on the Reef Visual Census frame. Do not fit goliath grouper first.
TOP THREE ACTIONS: (1) Human sends the 0282183/0306184 rights and schema letter. (2) Human sends the CalCOFI/WCOFS fallback letter the same day. (3) Log both as SENT or NOT_SENT in the outreach register. Neither has been sent.
FIVE-DAY SUCCESS CONDITION: Both letters are sent by a named human, the outbound date is written in the register, and no survey file has been committed to git.
PIVOT CONDITION: If neither letter has a written yes within 15 business days, pause that source and advance the next ranked candidate. If 0282183 has no constructible zeros, classify it CONTEXT_ONLY and do not fit a detection model.
```

**Strategic decision:** `PAUSE_MODEL_BUILDING_PENDING_RIGHTS`

---

## 1. What was verified

Classification is from files and code, not from folder names.

| Artifact | Class | Evidence |
|---|---|---|
| Globe prototype (Vite, MapLibre, honesty gates) | IMPLEMENTED_AND_RUNNING | `globe/prototype/src/layers.ts` requires `publishStatus === "PUBLISHED"` before a current estimate or forecast. `globe/prototype/VERIFICATION.md` records a historical-atlas build. |
| `model-cards.json` | IMPLEMENTED_AND_RUNNING as a gate | One card, *Magallana gigas*, `NOT_PUBLISHED`, all estimate flags false. Zero published prediction cards. |
| Goliath publication decision | BLOCKED | `species/goliath-grouper/PUBLICATION_DECISION.md` is `NOT_PUBLISHED`. |
| RVC rights record | RIGHTS_PENDING | `RVC_RIGHTS_RECORD.md`: `CONDITIONAL_REVIEW_REQUIRED`. No hash. No download. |
| OBIS past-report layer | IMPLEMENTED_AND_RUNNING as historical display | Compiler context in `MODEL_LADDER.md` (332,628 rows). Not a survey-event frame. |
| Survey CSVs, parquet, netCDF in the repo | BLOCKED | No biological survey extract is stored. `pipeline_stub/ingest.py` refuses production acquire. |
| Written training permission | RIGHTS_PENDING | No `APPROVED_FOR_TRAINING` on any biological source. Design docs that say `APPROVED_AS_DESIGN` are not training approval. |
| Display permission for a derived probability | RIGHTS_PENDING | Not granted. |
| Survey-event frame with valid zeros | UNKNOWN | InPort describes zeros in an analysis-ready RVC product. The table was not opened. |
| Environmental source acquired or queried | PLANNING_ONLY | WCOFS and Copernicus are named. No local extract. |
| Habitat grid | PLANNING_ONLY | GEBCO catalogued and unwired. No licensed reef-habitat grid in the training path. |
| Fitted species model or baseline | BLOCKED | `MODEL_LADDER.md` rung 4 blocked. `VALIDATION.md` tests not run. |
| Inference API, tile service, scheduled prediction job | BLOCKED | No serving path for a biological nowcast. Tile design docs are not a service. |
| UI “current location” for goliath or other species | BLOCKED | Gates refuse it. Willapa oyster screen is a synthetic Learn demo, not a species estimate. |
| `INFRASTRUCTURE_FRAMEWORK.md`, `SOURCE_FAMILIES.csv`, local-50-mile notes | PLANNING_ONLY | They say so in their own headers. |
| Smith et al. 2011 PDF in `research/` | DOCUMENTATION_ONLY | Design paper. Not a data grant. Does not mention goliath grouper. |

Nothing planned is presented by the running globe as a live nowcast. The risk is the planning stack being mistaken for a pipeline. This audit treats it as paper.

---

## 2. Dominant bottleneck

**`RIGHTS_AND_PERMISSION`**

What is missing: a written yes, from the data steward, covering acquisition, protected storage, training, and coarsened derived display for one named file.

Why it prevents prediction: the project rule is that a public download is not permission. Without that writing, the survey table stays unopened, so zeros, `EPIITAJ`, effort fields, and species counts stay unknown. No later stage can start honestly.

Blocks nowcast and forecast. A forecast also needs a validated nowcast, so it is blocked twice.

Who resolves it: a human sender, then Jeremiah Blondeau (SEFSC point of contact named on the NCEI Florida fish-community pages read 2026-09-23) and NCEI (`ncei.info@noaa.gov`) for the reef census; a CalCOFI/WCOFS steward for the fallback.

Exact next action: send the two letters in `research/data-acquisition-email-templates.md`. Do not download the coordinate files first.

Evidence to close it: the reply text stored beside `RVC_RIGHTS_RECORD.md`, naming the accession, the allowed uses, and the date. Rights class moves only then.

Order: rights letter → protected copy and hash → schema and zeros → baselines → spatial and time holdout → coarsened output → human reviewer → globe. Covariate join and forecast sit after a validated detection model.

### Dependent blockers (not the first gate)

| Blocker | Missing | Prevents | Who | Next action | Resolved when |
|---|---|---|---|---|---|
| `NO_ZERO_OR_EFFORT_FRAME` | Proof that each completed dive is in the table, including species absence | A detection likelihood | Analyst after rights | Count dives, zeros, and effort fields on the approved hash | A schema note with those counts and the zero rule |
| `INSUFFICIENT_REPEAT_YEARS` | A second season with the same protocol | Time-forward test and any forecast | Same stewards | Compare 0282183 (two-stage) with 0306184 (page says single-stage) | Written protocol comparison; if they differ, 0306184 is not a naive holdout |
| `NO_COVARIATE_ALIGNMENT` | No environmental values matched to dive date and depth | Calling the output a nowcast rather than a survey-season detection rate | Analyst after the biological table exists | Join only after the event table exists | A covariate table keyed by event id |
| `NO_SCIENTIFIC_REVIEWER` | No named person | Publication | Human | Ask the survey program, in the same letter, who can review a detection model | A name in the publication file |
| `SENSITIVE_LOCATION_RISK` | Goliath aggregation, nursery, and artificial-reef sites | Public goliath tiles even after a fit | Reviewer | Withhold goliath output unless a coarse grid is explicitly cleared | Written sensitive-site decision |
| `NO_MODELING_CAPACITY` | No fitted baseline | A claimed model | Not the current constraint | Do not staff this until a cleared table exists | A baseline skill table |
| `PIPELINE_ENGINEERING` | No warehouse | Scale | Not the current constraint | Do not build ingestion ahead of one cleared file | One reproducible validation script on that file |

`NO_STRUCTURED_OBSERVATIONS` is not the label. Structured programs are identified. Their tables are not in hand. `NO_VALIDATION_PLAN` is false: `VALIDATION.md` and the feasibility note specify holdouts. They have not been run.

---

## 3. Minimum dataset versus the repo

A first local detection model needs one row per completed sampling event, or a reconstruction from a complete event list plus species rows:

stable event id, date, region or stratum, a spatial unit that can stay in protected storage, depth, method, effort, taxon id, detection or valid zero, quality-control flag, habitat or stratum.

No candidate in the repo meets that list as a stored table.

| Source class | What it can support | What it cannot support |
|---|---|---|
| OBIS / GBIF occurrence | Historical range | Local absence, current presence, abundance |
| RVC / NCRMP, if the analysis-ready file matches InPort’s “zeros added” note | Effort-aware repeated visual surveys | Nothing, until the file is approved and counted |
| GGGC, REEF | Structured or opportunistic detections | A random non-detection frame; public site maps |
| FACT / FSU sonic tags | Individual movement research | A survey detection model; public tracks |
| eDNA, PAM | Future occupancy designs | A fitted nowcast today |
| WCOFS / Copernicus | Covariates after a biological table exists | A sighting |

---

## 4. First-model choice

Scores are 0–5, 5 most favorable. Sensitive-location risk uses 5 for low risk. Scores use only what the repo has verified. Detail is in `audit/first-model-decision-memo-2026-09-23.md`.

| Choice | Rights | Frame | Zeros | Effort | Years | Env | Habitat | 50-mile support | Forecast | Sensitive (5=safer) | Time | Reviewer | Sum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A Goliath, Keys | 1 | 2 | 1 | 2 | 2 | 1 | 2 | 3 | 1 | 1 | 2 | 0 | 18 |
| B Goliath, other region | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 5 |
| C Common reef fish, same RVC frame | 1 | 2 | 1 | 2 | 2 | 1 | 2 | 3 | 1 | 4 | 3 | 0 | 22 |
| D Small reef community, same frame | 1 | 2 | 1 | 2 | 2 | 1 | 2 | 3 | 1 | 3 | 2 | 0 | 20 |
| E Ecosystem indicator | 1 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 1 | 3 | 2 | 0 | 19 |
| F Partner pilot | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 3 |

**`FIRST_MODEL_RECOMMENDATION`:** C, on the 2022 Keys Reef Visual Census frame (accession 0282183), species chosen from the approved table by detection count and display safety. Goliath stays off the first fit. Fallback if that letter is declined or the file has no zeros: CalCOFI CUFES encounter or egg presence for Pacific sardine or northern anchovy, which is choice C in a different region and is also still rights-pending.

Goliath is the wrong first species because the same unopened survey is the only structured Florida frame, the species is described as uncommon on natural-reef counts, and aggregation geometry cannot be shown.

---

## 5. Five business days (through 2026-09-30)

| ID | Owner | Object | Output | Depends on | Effort | Deadline | Pass | Fail | Then |
|---|---|---|---|---|---|---|---|---|---|
| A1 | Human sender | `research/data-acquisition-email-templates.md` Template 1, to the SEFSC contact on the NCEI page and `ncei.info@noaa.gov` | Outbound copy plus register row `SENT` with timestamp | Named storage location outside git, even if the folder is still empty | 2 hours | 2026-09-25 | Register shows SENT and the letter asks for training, coarsened display, the data dictionary, the zero rule, and coordinate rules for 0282183 and 0306184 | Letter not sent, or letter asks for site coordinates | A3 |
| A2 | Human sender | Template 2, CalCOFI CUFES and WCOFS | Second register row | None; send the same day as A1 | 1 hour | 2026-09-25 | Register shows SENT | Not sent | 15-day clock does not start |
| A3 | Human sender | `research/data-acquisition-outreach-register.md` | Both rows updated; follow-up date 2026-10-02 | A1 and A2 | 30 minutes | 2026-09-25 | Every row is `NOT_SENT` or `SENT` with a date. No row says a reply arrived unless it has | A blank “sent” claim | Do not download |
| A4 | Analyst, only if a steward replies with a dictionary or a de-identified header | Reply text | A one-page schema note: column names, whether a dive with zero goliath or zero of a named common species can be built, no coordinates | A written yes or an attached dictionary that contains no coordinates | 4 hours after reply | 2026-09-30 if the reply arrives; otherwise not due | Note states zero rule as `EXPLICIT`, `CONSTRUCTIBLE`, or `ABSENT` | Coordinates pasted into git | Stop and delete the coordinate text |
| A5 | Human sender | Same threads | One follow-up only if there is no reply | A1/A2 sent | 20 minutes | 2026-10-02 | Follow-up logged | A second product feature started instead | Keep the pause |

Do not fit, do not build an ERDDAP lake, and do not change the globe in these five days.

---

## 6. Pipeline after one source is cleared

| Step | Class |
|---|---|
| Approved source | BLOCKED |
| Protected raw storage | NOT_NEEDED_YET |
| Schema validation | NOT_NEEDED_YET |
| Event-level analysis table | NOT_NEEDED_YET |
| Covariate extraction | NOT_NEEDED_YET |
| Baseline model | NOT_NEEDED_YET |
| Spatial and temporal validation | PLANNED (`VALIDATION.md` only) |
| Coarsened probability output | NOT_NEEDED_YET |
| Sensitive-location review | PLANNED as a rule, not staffed |
| Human publication approval | BLOCKED (no named reviewer or publisher) |
| Globe display of a real estimate | PARTIAL as a gate only. The gate exists and correctly shows nothing |

Building the warehouse before A1 is answered does not produce a prediction.

---

## 7. Kill and pivot rules

- If no written yes for 0282183 arrives within 15 business days of A1 (by 2026-10-16 if A1 is sent on 2026-09-25), pause RVC and advance the CalCOFI letter’s outcome.
- If the dictionary shows no complete survey-event frame, set the source to `CONTEXT_ONLY`.
- If zeros cannot be constructed, do not fit a detection model on that file.
- Minimum detection count for a species-level model: `THRESHOLD_TO_BE_DEFINED_WITH_REVIEWER`. Until that number exists, do not fit goliath, and do not declare a common species “ready” from a guess.
- If 0306184 remains single-stage while 0282183 is two-stage, do not use 2024 as a direct holdout for a 2022 model.
- If a coarse grid still points at aggregation habitat, withhold that species.
- If no named reviewer is recorded, do not publish. The card stays `NOT_PUBLISHED`.

---

## 8. Decision

`PAUSE_MODEL_BUILDING_PENDING_RIGHTS`

The first real local model, after a written yes, is a Reef Visual Census detection model for a common Keys reef fish on accession 0282183. Goliath grouper is not that model. No nowcast or forecast is issued now.
