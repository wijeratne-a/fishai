# Time and forecast UI

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/time_and_forecast_ui.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding clocks. Silent rewrite of issued forecasts is forbidden.

The globe is a **time machine with as-of joins**, not a live animal tracker. Internal clock: **UTC**. Display: UTC **and** local (IANA). Tide products may show a **local tide clock** in addition, never instead.

Align with `../artifacts/geospatial_data_engineer/as_of_replay_design.md` and architecture §5.

---

## 1. Persistent readout (MVP chrome — always visible)

Exactly these labels (wording may wrap; meaning may not change):

```text
Forecast issued at:     {issued_at_utc}  ({local})
Valid for:              {valid_from} → {valid_to}
Environmental inputs current through: {inputs_through / source_data_cutoff}
Last direct observation in this area: {last_direct_obs or “none in window”}
Forecast confidence:    High | Medium | Low | None
Model version:          {id or “RULE / fixture / none”}
Data coverage:          {density class + one-line missing}
```

If the view is **not** a forecast (e.g. Unknown map only), still show clocks; set forecast lines to `n/a — no forecast issued` rather than hiding the widget.

**W1 example (fixture):**

```text
Forecast issued at:     2026-09-18 23:00 UTC  (16:00 PDT)
Valid for:              2026-09-18 16:00 PDT → 2026-09-21 16:00 PDT
Environmental inputs current through: NWS 21:00 UTC · CO-OPS tides as-of 18 Sep
Last direct observation in this area: none on-lease · nearest station 3.2 km (fixture)
Forecast confidence:    Low
Model version:          OSI72-RULE-2026-09-18-v0  (fixture, not a trained model)
Data coverage:          Low — no on-lease T/DO · no 14d mortality protocol
```

---

## 2. Timeline states (mutually exclusive per **layer**)

A layer’s `time_state` is one of:

| State | Meaning | Visual |
|---|---|---|
| `OBSERVED_HISTORY` | Recorded in the past | Solid; historical palette |
| `CURRENT_ESTIMATE` | Best estimate from data available **now** (as-of) | Solid or dotted per truth state |
| `FORECAST` | Future window from issued model/rule | Dashed + clock |
| `CLIMATOLOGY` | Typical for this date/season from a **named** climate set | Muted; label `climatology {period}` |
| `ANOMALY` | Difference from that climatology | Diverging palette **separate** from abundance; reference period on legend |
| `SCENARIO` | Hypothetical (user or climate-model) | Purple **RESEARCH / SCENARIO** banner; never mixed into operator OSI |

**Do not** label climatology as a 48 h forecast. **Do not** label a scenario as current.

Multiple layers may mix states (e.g. observed tide + forecast air). The **issued product** has one primary state.

---

## 3. Controls — MVP vs later

| Control | MVP | Later |
|---|---|---|
| Issued/valid/cutoff readout | **Required** | — |
| Historical timeline scrubber | Optional stub | Full |
| Forecast playback | **Off** | Mode 6, capped speed |
| Resolution picker (hour/day/week/season) | Fixed: hourly covariates, **72h** valid window | User-selectable where data exist |
| Date comparison | Panel text | Mode 7 split |
| Anomaly mode | **Off** | Named baseline required |
| Seasonal climatology mode | **Off** | |
| Then vs now | **Off** | |
| Now vs forecast | Panel: “yesterday Typical → today Elevated” text | Map split |
| Model-version replay | Show version string | Load prior `forecast_id` |
| Climate period | **Off** | Scenario mode only |

---

## 4. Issuance identity (every forecast tile / brief)

| Field | UI name | Notes |
|---|---|---|
| `forecast_id` / `brief_id` | Brief / forecast ID | Immutable |
| `issued_at_utc` | Forecast issued at | Product time |
| `valid_from_utc` / `valid_to_utc` | Valid for | Horizon |
| `source_data_cutoff_utc` | Inputs current through | Max `published_at` in snapshot |
| `training_data_cutoff_utc` | Training labels through | If a fitted object exists; else n/a |
| `last_direct_obs_utc` | Last direct observation | In AOI × taxon × depth as defined |
| `feature_snapshot_id` | Replay pointer | Scientist drawer |
| `model_or_rule_version` | Model version | Fixture rules allowed |
| `supersedes_forecast_id` | Revises | If amendment |

**Never UPDATE** an issued forecast. UI offers **Issued view** vs **Revised view** (new id). Mixing evaluation lanes (as-of vs corrected-data) is a red-team blocker.

---

## 5. Horizon language

| Product | Horizon UI | Forbidden |
|---|---|---|
| W1 oyster OSI | 24–72 h from issuance; show both UTC and local **and** next emersion windows | “Safe to work” as weather-safety; “harvest Friday” |
| Later Chinook | 24–48 h **only if area open**; else None | “Limits tomorrow” |
| Later lobster | Next planned haul window | Public next-string GPS |
| Climatology | Season / month | Calling it a nowcast |
| Climate scenario | Named experiment (e.g. SSP) + research banner | Operator decision product |

---

## 6. Freshness and staleness

Follow uncertainty policy SLOs as **display** defaults (tune later): in-situ 6 h; waves 12 h; SST analysis 36 h; chlorophyll 48 h; official closures 6 h + re-verify before a farm brief.

| Freshness class | Chrome |
|---|---|
| Fresh | No extra chip |
| Stale | `STALE {source}` chip; confidence drop |
| Missing critical | Confidence **Low** or **None**; list in coverage line |
| Official unverified | Separate module: `Official status not verified — do not harvest on the basis of this view` |

W1: **DOH last-verified** is **not** the model clock. Two clocks, always.

---

## 7. Animation rules (when Mode 6 exists)

1. Each frame is an **issued valid_for instant** or a stored observation stamp — not a interpolated animal.
2. Cross-fade of coverage hatch is allowed; cross-fade that **invents** mid-time biological values is not.
3. Default speed: wall-clock ratio labeled (e.g. `1 h / 0.5 s`). No cinematic ease-in of schools.
4. Observed tracks: playback moves a **cursor** along a stored polyline; it does not invent positions. Listed taxa: usually **no public playback**.
5. User can pause on any frame and open Evidence Explorer for **that** `forecast_id` / obs id.

MVP: **no animation.** A static 72h window is more honest than a pulsing estuary.

---

## 8. “Current” is not “now on the animal”

`CURRENT_ESTIMATE` means **as-of the cutoff**, not “we are watching this organism.” Copy:

> Current estimate uses observations and analyses **available to the system at the cutoff**. It is not live tracking.

If last direct observation is days old, the readout must say so even if env forecasts are fresh. Fresh wind does not refresh fish.
