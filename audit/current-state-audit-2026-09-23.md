# Global Marine Life Intelligence System — Current-State Audit

## Audit Snapshot

- **Repository:** `/Users/wijeratne/dev/fishai`
- **Branch:** `branch` (local name; no upstream)
- **Commit:** `20db75e50b3ad48a28aff8edd3528792598b908d` — “Initial snapshot to enable isolated worktrees for parallel agent work.” Only commit.
- **Upstream:** none. `git remote -v` is empty. **CANNOT_VERIFY_REMOTE_STATE**
- **Working tree:** dirty, unstaged, nothing staged. 14 modified files, 1 untracked (`species/goliath-grouper/OBSERVATION_PLAN.md`)
- **Worktree:** `ux/globe-honesty-pass` at the same SHA, path `/Users/wijeratne/.cursor/worktrees/fishai-ux-11dc21e2/fishai-4091d9f6d7c3`, also dirty
- **OS:** Darwin 25.6.0, arm64, `GANs-MacBook-Air.local`
- **Audit window:** 2026-09-23 20:45:37–20:47:49 PDT
- **Files changed during the audit:** none. Start and end `git status` matched on both trees.
- **Those dirty files are still MOVING_TARGET** relative to other agents, because they are uncommitted and the two trees edit overlapping UI files.
- **Commands:** `git status/diff/log/worktree/rev-parse`, `find`, `lsof`, `curl` of both Vite servers, file reads. No build, test, install, format, or git write. `ps` was blocked by the sandbox.
- **Constraint:** read-only. Prior audits were not treated as proof when code disagreed.

## Direct Verdict

The runnable product is a Vite + MapLibre globe that searches species and refuses to issue a current location or a forecast. It can show coarsened historical OBIS cells, and a Learn-only synthetic Willapa oyster working-conditions demo. It cannot estimate where marine life is now, and it cannot forecast where it will be, including Atlantic goliath grouper.

What is working in code: species search against a local WoRMS-id catalog, a publication gate that stays closed (`PUBLISHED` count is zero), honesty copy (“No issued location.” / “No forecast issued.”), client-side withholding of white-shark past-report locations, and a globe style that references NASA Blue Marble and EOX Sentinel-2 cloudless 2020.

What is only a demo: Willapa hex cells, stations, SST and habitat overlays, and the oyster 72-hour working-conditions story. `public/fixtures/meta.json` labels that data synthetic.

What is documentation only: observatory catalogs, model cards, validation protocols, VAST/ISDM/movement designs, FAIR/CARE policy, and the goliath ecology and model ladder. `MODEL_LADDER.md` uses “IMPLEMENTED” for prose and an API row count. No model is fitted. `VALIDATION.md` says every holdout is **NOT RUN**.

What is broken as a single product: two dev servers both listen on port 5173 and serve different UIs. `http://[::1]:5173/` is the main checkout (Learn still says “Guessed” / “Don’t know”). `http://127.0.0.1:5173/` is the UX worktree (purpose line; legend words Measured, Estimate, Forecast, Past reports, Unknown). Same port, different apps.

The globe’s smoothness was **NOT_TESTED** in this audit. Frame rate was also not measured in `VERIFICATION.md`.

The single largest blocker is the absence of effort-aware observations, a fitted model, holdout skill, and a real publication decision. Until those exist, an honest globe must keep saying it does not know where the animals are.

**Final classification: `FUNCTIONAL_HISTORICAL_ATLAS`.** A user can search a name and see unknown-now plus optional historical reports. That is not a validated estimator or forecaster.

## Changes Since Prior Audit

Prior alignment report: `audit/global-marine-life-alignment-report.md` (2026-09-22). It described demotiles as the live style and a simpler answer strip. Current uncommitted main code has moved past that.

| Change | Where | Status | Verification |
|---|---|---|---|
| Git repo created; one snapshot commit; no remote | repo root | Committed | Verified |
| NASA GIBS Blue Marble + EOX 2020 globe style; GEBCO recorded, `wired: false` | `basemap.ts` on main only | Uncommitted | CODE_PRESENT_NOT_RUN |
| Camera constants, reduced motion, drag-vs-click | `camera.ts` on main only | Uncommitted | CODE_PRESENT_NOT_RUN |
| Goliath taxon `no_estimate`, AphiaID 159353 | `taxa.json` both trees | Uncommitted | CODE_PRESENT |
| Goliath answer copy and ecology depth note | `main.ts` both trees, diverging | Uncommitted MOVING_TARGET | CODE_PRESENT_NOT_RUN this session |
| UX legend/evidence/modes | worktree only (`legend.ts`, `evidence.ts`, `UX_AUDIT_NOTES.md`) | Uncommitted | HTML served on 127.0.0.1:5173 |
| Goliath papers | `species/goliath-grouper/` | Mostly in the snapshot; `OBSERVATION_PLAN.md` untracked | DOCUMENTATION_ONLY |
| Publication remains `NOT_PUBLISHED` | `PUBLICATION_DECISION.md`, `model-cards.json` | In snapshot | Verified in files |
| Remote branches | — | Absent | CANNOT_VERIFY_REMOTE_STATE |

`VERIFICATION.md` on the main tree claims a 2026-09-22 browser pass (goliath: no issued location, 7 coarse cells, 332,628 OBIS rows). That file is dirty, and this audit did not re-run the search. Treat those numbers as **CLAIMED_NOT_VERIFIED**.

## Architecture Map

```
Browser UI (index.html + main.ts)
  → MapLibre GL JS 6.10 globe (mapApp.ts, camera.ts, basemap.ts)
    → Layer controller (layers.ts publication gates)
      → Local fixtures (Willapa GeoJSON, taxa, model-cards, evidence-by-cell)
      → Live browser fetch: WoRMS name lookup, OBIS occurrence count/years/1° grid
        → NO warehouse, NO training, NO inference service, NO forecast job
          → Publication gate: mayDraw* requires PUBLISHED (zero cards qualify)
```

Missing links, explicit:

- No backend or API of this project’s own.
- No scheduled ingest. `ingest.py` raises `PermissionError` before acquire.
- `model_registry/`, `ingestion_pipeline/`, `data_dictionary/`, `evaluation_reports/` are empty.
- No model artifact, no skill table, no tile pyramid for biology.
- GEBCO is cataloged and not set as terrain.
- Depth radios filter Willapa fixture flags. They are not a water column.
- `modesNotInPrototype` in `meta.json` still lists vertical/horizontal slices, seafloor habitat, and forecast timelapse.

## Capability Matrix

Scale: 0 absent, 1 docs only, 2 fixture/demo, 3 partial, 4 runnable unvalidated, 5 validated.

| Area | Score | Confidence | Why |
|---|---|---|---|
| 7.1 Taxonomy | 3 | HIGH | Local catalog with AphiaIDs and common names; WoRMS fallback in `worms.ts`. No life stages, stocks, or synonym graph in the app. |
| 7.2 Observations | 2 | HIGH | Live OBIS presence counts, coarsened. No effort, non-detections, telemetry, eDNA, acoustics, cameras, or fisheries microdata in code. |
| 7.3 Ocean state | 2 | HIGH | Visual Blue Marble shading. Willapa SST/habitat are fixtures. No salinity, currents, oxygen, chlorophyll pipeline, reanalysis, or forecast fields. |
| 7.4 Species biology | 1 | HIGH | Goliath ecology is a sourced markdown profile, not a model layer. |
| 7.5 Modeling | 1 | HIGH | Gate functions exist. Ladder rungs 4–8 are NOT STARTED or BLOCKED. No VAST, ISDM, occupancy, ensemble, or assimilation code. |
| 7.6 Validation | 1 | HIGH | Protocol written. Record of runs: **NOT RUN**. No tests in the repo (`*test*` search: 0). |
| 7.7 Operations | 0 | HIGH | `project_state.json` is `STATE_10_PAUSED_FOR_HUMAN_DECISION`. `approved_sources` is `[]`. No registry, monitor, or rollback runtime. |

## Goliath Grouper Status

Taxon in the catalog: *Epinephelus itajara*, AphiaID 159353, status `no_estimate`. No goliath model card. Decision file: **`NOT_PUBLISHED`**. That status is substantiated: there is no model, no holdout, no rights-approved ingest, no named reviewer. Not `PUBLICATION_STATUS_NOT_SUBSTANTIATED` — the decision correctly refuses publication.

1. **Search:** Yes, in code, common and scientific names. Not re-clicked this session.
2. **Correct taxon:** The fixture says AphiaID 159353. This audit did not re-query WoRMS.
3. **Historical observations:** Optional live OBIS grid, labeled past reports. Not a stored observation warehouse. The 332,628 figure is a documented API claim, not rechecked.
4. **Sampling effort:** No.
5. **Non-detections:** No.
6. **Juvenile nursery habitat:** Text only. Pins blocked.
7. **Adult reef/wreck habitat:** Text only. Wrecks not drawn.
8. **Spawning season:** July–September as copy. Not a map. Aggregation sites blocked.
9. **Depth:** An ecology sentence (juveniles in mangrove shallows; adults about 0–50 m). Not a depth model.
10. **Habitat-suitability model:** Not started.
11. **Current-occurrence model:** No. UI is required to say “No issued location.”
12. **Relative abundance:** No.
13. **Movement model:** Blocked, not built.
14. **Spawning-aggregation model:** No. Layer blocked.
15. **Forecast:** No. “No forecast issued.”
16. **Uncertainty:** “Not assessed.” / “None” for other species. No probability intervals.
17. **Baseline beaten:** No model, so no.
18. **Spatial validation:** Not run.
19. **Temporal validation:** Not run.
20. **Prospective validation:** Not run.
21. **Publication decision:** A written `NOT_PUBLISHED`. Not an issued scientific product.
22. **UI may show:** Unknown ocean; search result; coarsened past-report cells if OBIS returns them (`n ≥ 3`, at most 80, about 1°); ecology and limitation text.
23. **UI must not show:** Current-estimate or forecast layers, abundance heat, wreck or nursery pins, a confidence score presented as skill, or a claim that the system knows where every goliath is.
24. **Blocker for a first defensible estimate:** Rights-approved, effort-aware detection and non-detection data; a stated prediction target; a fitted model that beats the written baselines on spatial-block and time-forward holdout; calibration; sensitive-site review; a named human publisher. None of that is in the tree.

## Scientific Honesty

Enforced in code on the main tree:

- `mayDrawCurrentEstimate` / `mayDrawForecast` / abundance / movement require `publishStatus === "PUBLISHED"` and the matching flag. The only card is Magallana gigas, `NOT_PUBLISHED`, all flags false, Willapa demo allowed.
- Cold-load answer is empty: search prompt, no forecast, how sure “None,” this is not live tracking.
- Past reports copy says they are not where animals are now, and states the 80-cell cap.
- White shark (AphiaID 105838) returns before any OBIS draw.
- Willapa cells start hidden (`showWillapaCells: false`).

No P0 false “live tracking” string was found in the current UI source. Violations and gaps:

| Claim risk | Where | Why it misleads | Evidence actually available | Severity |
|---|---|---|---|---|
| Past-report cells can be read as the species’ map | `obis.ts` draws a prefix of the API grid, max 80 | Cap is disclosed; order is API order, not “densest cells” or a complete range | Compiler counts, not presence now | P2 |
| Depth radios look global | `index.html` Explore | They filter fixture flags only | No depth model | P2 |
| “IMPLEMENTED” on ladder rungs 0–3 | `MODEL_LADDER.md` | Sounds like software models | Prose and an OBIS count | P2 |
| Root README: “This is not a world map” and paused Willapa wedge | `README.md` | The globe is a world map prototype; commercial wedge is still undecided | Two products in one repo | P2 |
| `meta.json` “No OBIS… were downloaded” | fixtures | True of the fixture generator; the app now fetches OBIS at runtime | Easy to mix up | P3 |
| Error copy “map stays striped” | `evidence.ts` | Ocean-wide hatch is not on by default | Unknown is mostly the answer strip plus legend | P3 |

Layer classes that actually render: **HISTORICAL_RECORD** (OBIS, when a search returns cells), **DEMO_OR_SYNTHETIC** (Willapa, Learn only), **ENVIRONMENTAL_CONTEXT** (fixture SST), **UNKNOWN** (default and legend). **CURRENT_MODEL_ESTIMATE** and **FORECAST** are gated off except as demo encodings inside the oyster screen.

## Globe and Geospatial Status

- Engine: MapLibre GL JS 6.10.0. Projection `globe`, 2D via mercator toggle in code.
- Camera code: center `[0, 15]`, zoom 1.6, pitch handling, wheel zoom, double-click, keyboard, touch pitch, north-up, tilt reset, home, reduced motion, drag threshold before select. **NOT_TESTED** this session.
- Imagery in `basemap.ts`: NASA GIBS `BlueMarble_ShadedRelief_Bathymetry` (max meaningful zoom 8, ~500 m shading, not a DEM), EOX `s2cloudless-2020` from zoom 6 to 12, MapLibre demotiles as vector/glyph fallback. Attribution strings are in the source registry.
- GEBCO 2024 is listed and **not wired**. No `setTerrain`.
- Biological resolution is ~1° when past reports draw. Zoom past that does not add biological detail (`zoomBeyondBiologicalResolution`).
- LOD design docs are not a tile service.
- Performance class: **NOT_TESTED**. Hardware available: Apple Silicon MacBook Air. Browser interaction was not driven.

## UI/UX Status

This session confirmed served HTML only, not click journeys.

**Main checkout (`[::1]:5173`):** first-run dialog, search, four modes (Find, Explore, Evidence, Learn), answer dock, “No forecast issued” in the footer. Learn still says Measured / Guessed / Future / Don’t know. Purpose sentence is inside the dialog, not a standing line under search.

**UX worktree (`127.0.0.1:5173`):** standing purpose line, modes renamed Find Species / Explore Ocean / Evidence & Data / Learn & Methods, legend vocabulary Measured / Estimate / Forecast / Past reports / Unknown. That UI is not in the main working tree.

Journeys A–F were **not** executed in a browser here. From code: cold load does not open the oyster demo; goliath is `no_estimate`; unsupported names fall through to WoRMS or “No matching name”; evidence for non-oyster species is the past-report summary, not the 16-field Willapa panel (`showCell` returns early unless the taxon is the oyster demo). Mobile, contrast, and focus were not measured. A skip link and several labels exist.

## Data and Model Status

- **Observations:** none stored. OBIS is a browser call.
- **Ocean data:** not ingested. Visual basemap only.
- **Habitat:** goliath habitat is prose. Willapa “favorable conditions” are fixture polygons.
- **Models:** none fitted. One draft card, not published.
- **Forecasts:** none. Demo 72-hour working-conditions window is synthetic and Learn-gated.
- **Validation:** designed, not run.

## Rights and Safety

Documented widely (`observatory/sensitive_location_policy.md`, data-rights artifacts). Enforced in code:

- Ingest stub refuses production acquire.
- `approved_sources` is empty, so a warehouse ingest is still blocked.
- White-shark locations are withheld in the browser before fetch.
- Goliath display rules are coarsen-or-withhold in the client, not a server policy. There is no server. Client-side hiding is the only control, which the audit standard treats as insufficient for truly sensitive coordinates. This build avoids that by not shipping aggregation coordinates at all.
- No API keys or `.env` in the prototype. Tile URLs are public NASA and EOX endpoints.
- `escapeHtml` covers `& < > "`. Evidence links put URLs in `href` after escaping quotes; a `javascript:` URL in fixture data would still be a risk. Fixtures are local, not user uploads. No upload path was found.
- OBIS/WoRMS runtime use is not an entry in `approved_sources`. That is a policy gap, not a secret leak.

## Parallel-Agent Conflicts

Do not merge either tree onto the other as-is.

Both modify: `index.html`, `README.md`, `VERIFICATION.md`, `taxa.json`, `answer.ts`, `layers.ts`, `main.ts`, `mapApp.ts`, `styles.css`, `types.ts`.

Main only: `basemap.ts`, `camera.ts`, `places.ts`, `IMPLEMENTATION_BRIEF.md`.

Worktree only: `evidence.ts`, `legend.ts`, `UX_AUDIT_NOTES.md`.

Terminology already diverges (Guessed/Don’t know vs Estimate/Unknown). Two Vite processes split port 5173 by address family, so “localhost” is ambiguous. No `<<<<<<<` merge markers in source. The `=======` hits in `GLOBAL_MARINE_LIFE_INTELLIGENCE_PROMPT.md` are markdown rules, not conflicts.

## Test and Runtime Results

| Command | Result |
|---|---|
| `git status`, `git log`, `git worktree list` | One commit, two dirty worktrees, no remote |
| `curl -g http://[::1]:5173/` | 200, main `index.html` (Guessed / Don’t know) |
| `curl http://127.0.0.1:5173/` | 200, worktree `index.html` (purpose line, Measured/Estimate) |
| `npm run build`, `tsc`, tests, lint | **Not run.** A build would write `dist/`. No test script exists. |
| Browser journeys, frame rate | **NOT_TESTED** |

## Scorecard

| # | Dimension | Score | Why it is not higher |
|---|---|---|---|
| 1 | Mission alignment | 34 | Honesty matches the mission. The mission’s estimate and forecast are absent. |
| 2 | Taxonomy | 48 | Usable name resolution for a catalog. No stocks, stages, or synonym service beyond WoRMS-on-miss. |
| 3 | Observations | 22 | One presence API, coarsened. No effort or non-detection. |
| 4 | Ocean state | 16 | Picture of Earth, not an ocean analysis. |
| 5 | Behavior and climate | 14 | One ecology essay. |
| 6 | Inference / ML | 8 | Gates only. |
| 7 | Forecasting | 6 | Refused, correctly. Demo forecast is synthetic. |
| 8 | Validation | 8 | Written tests, zero runs. |
| 9 | Goliath implementation | 30 | Search, taxon id, refusal, optional history. No estimate. |
| 10 | Globe experience | 50 | Real globe stack and basemap code. Interaction not retested; GEBCO off; biological detail is 1°. |
| 11 | UI / plain language | 58 | Answer strip is plain on the main tree. Learn still says “Guessed.” Two UIs disagree. |
| 12 | Accessibility | 36 | Skip link, labels, patterns exist. Contrast, mobile, and keyboard were not measured. |
| 13 | Performance | 30 | **NOT_TESTED.** Confidence LOW. |
| 14 | Rights and sensitive locations | 46 | Strong refusal to ingest; display controls are client-only; OBIS use is outside `approved_sources`. |
| 15 | Operational readiness | 8 | Paused state, no service. |
| 16 | Documentation accuracy | 44 | Prototype README is mostly honest. Root README, `meta.json`, and “IMPLEMENTED” ladder rows drift. |
| 17 | Parallel-work health | 22 | Overlapping uncommitted edits and two servers on one port. |

Confidence is HIGH on “no model / no forecast,” MEDIUM on UI behavior (code plus served HTML, no clicks), LOW on performance.

## Findings

**No P0 substantiated.** No published fake estimate, no exposed credential, no aggregation coordinates, no gate flipped to `PUBLISHED`.

**P1 — F1. No operational goliath estimate.** Status: confirmed in source. Affected: `PUBLICATION_DECISION.md`, `model-cards.json`, `main.ts`. Current: “No issued location.” Expected: that refusal until holdouts exist. Impact: the product cannot answer “where now.” Action: keep the gate; do not paint habitat as presence. Owner: species-model workstream. Acceptance: a card stays `NOT_PUBLISHED` until spatial and temporal holdouts beat the written baselines.

**P1 — F2. Two uncommitted UIs and two servers.** Status: MOVING_TARGET. Affected: the overlapping files listed above; PIDs 69241 (main prototype) and 87539 (UX worktree), both port 5173. Current: IPv6 and IPv4 serve different HTML. Expected: one app. Impact: reviewers will certify the wrong UI. Action: do not merge blindly; pick one UI after both workstreams stop. Acceptance: one worktree, one listener, one legend vocabulary.

**P1 — F3. Historical cells are not a validated distribution.** Status: code present. Affected: `obis.ts`. Current: first matching features, cap 80, `n ≥ 3`. Expected: either a complete coarse map or an explicit “partial extract, not the range” statement. Impact: a handful of cells can look like the animal’s geography. Action: state truncation and selection rule in the answer, or rank and cover the domain. Acceptance: a user can tell that missing cells are not absence and that the draw is not the full OBIS grid.

**P2 — F4. Depth, SST, and habitat controls outrun the science.** Willapa-only. Acceptance: disabled or captioned “demo only” until a published layer exists.

**P2 — F5. No automated tests on the publication gate or the sensitive-taxon withhold.** Acceptance: a test that a non-`PUBLISHED` card cannot turn on estimate or forecast layers, and that AphiaID 105838 yields no geometry.

**P2 — F6. Documentation drift.** Root README, fixture meta, and ladder wording. Acceptance: each “implemented” row names a file that runs.

**P2 — F7. Accessibility and mobile unverified.** Acceptance: keyboard search, focus, and a 390px layout checked against the served app.

**P3 — F8. Branch is named `branch`, history is one snapshot, no remote.** Acceptance: a real default branch only when someone chooses to publish the repo.

**P3 — F9. “Map stays striped” overclaims the default ocean.** Acceptance: copy matches the actual hatch, which applies to cells, not the whole Earth.

## Top 15 Next Actions

1. **Stop and reconcile the two globe trees** before any further UI or camera edits. Component: `globe/prototype`. Wait for both workstreams. Gate: one `index.html`. Conflict: high.
2. **Keep goliath `NOT_PUBLISHED`.** Component: model card gate. Do not wait. Acceptance: zero `PUBLISHED` cards. Scientific gate.
3. **Say the OBIS draw is a capped extract.** Component: `obis.ts` / past-report copy. Can proceed on the chosen tree. UX honesty gate.
4. **Do not add a forecast slider.** No forecast exists. Wait for validation. Scientific gate.
5. **Leave GEBCO unwired** until a tiled, licensed terrain product exists. Basemap workstream. Conflict: medium with camera agents.
6. **Add gate tests** after the trees converge. Conflict: medium if `layers.ts` is still moving.
7. **Rights-review OBIS display** into `approved_sources` or document the browser exception. Data-rights workstream. Do not start a warehouse ingest.
8. **Collect effort and non-detections** before any occupancy model. Species workstream. This blocks the first estimate.
9. **Fit nothing that cannot beat the four baselines in `VALIDATION.md`.** Scientific gate.
10. **Sensitive-site review before any sub-degree goliath geometry.** Safety gate.
11. **Name a human reviewer and publisher** before any card can change status. Governance gate.
12. **Re-verify cold load and goliath search in a browser** on the surviving server only. UX gate. Prior `VERIFICATION.md` is stale relative to the split.
13. **Measure frame time** before calling the globe smooth. Performance gate. Not claimed here.
14. **Align root README** with “historical atlas plus refused estimate,” after the globe settles. Docs gate. Conflict: low.
15. **Decide the commercial wedge separately** (`decision_required.md` is still paused). Do not let Willapa ops-risk become the species answer. Product gate.

## Do Not Merge Yet

- `ux/globe-honesty-pass` onto main, or the reverse. Overlapping files will clobber camera/basemap work or the UX legend/evidence pass.
- Any change that sets `publishStatus` to `PUBLISHED` for goliath or the oyster card.
- Any spawning-site, wreck, or nursery coordinate layer.
- Declaring `VERIFICATION.md` or `UX_AUDIT_NOTES.md` as the current product. Both are uncommitted and describe different trees.
- The initial git snapshot as a release. It has no remote and the real work is uncommitted.

## Safe to Preserve

- “No issued location.” and “No forecast issued.” when no card is `PUBLISHED`.
- “This is not live tracking, a fishing map, or a count of animals.”
- `mayDrawCurrentEstimate` and `mayDrawForecast` as hard gates.
- White-shark withhold before draw.
- Goliath `no_estimate` and aggregation pins withheld.
- Willapa demo off until Learn.
- Past reports labeled historical, `n ≥ 3`, max 80, ~1°.
- `ingest.py` production acquire left blocked.
- Empty `approved_sources` until a human rights review.

## Final State Classification

**`FUNCTIONAL_HISTORICAL_ATLAS`**

Evidence: a globe app runs; search resolves *Epinephelus itajara* to a `no_estimate` record; the only species geometry path is a coarsened OBIS history; current estimates and forecasts are impossible with the cards on disk; validation runs are empty; the observatory is markdown. A validated single-species estimator would require a fitted model and holdouts. Those files are not in the repository.
