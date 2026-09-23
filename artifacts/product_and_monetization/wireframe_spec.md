# Wireframe Spec — Text / ASCII (not an app)

**Date:** 2026-09-18  
**MVP surface:** email (HTML-equivalent shown as text) + 1-page PDF + optional WhatsApp ping + 30-second outcome form.  
**No** multi-tab terminal, no GIS app, no dark-mode dashboard.

Every surface that can be a “product” must carry the **14 contract fields** or a deep-link to a page/PDF that does.

**Claims halt / limitations (visible on every mock):** Category D ops-stress / work-window only; **Willapa** demo geography (never Totten or other 2026 Vp Category 3 areas); air × tide × solar first (SST is not body temperature); terciles not “top 20%”; no commands; no fake decimal anomalies; hard WA DOH wall as a **separate** module; not a live forecast.

---

## 1. Email — above the fold (mobile, ~5.5" width)

```
From:    briefs@fishai.example
To:      manager@farm.example
Subject: [FishAI] Willapa Zone B · ELEVATED ops-stress · 72h · Low conf · NOT harvest/food-safety
Preheader: NOT a harvest or food-safety notice. Air×tide×solar, not SST. WDOH link inside.

┌─────────────────────────────────────────────────────────────┐
│ FISHAI  ·  OYSTER OPS-RISK BRIEF     SAMPLE / NOT A FORECAST│
│ Pacific oyster · WA Willapa DOH areas · PRIVATE Lease Zone B│
│ Issued 2026-09-18 16:00 PDT  →  valid to 2026-09-21 16:00   │
│ Brief ID OY-WA-SAMPLE-2026-09-18-B                          │
│ Evidence: Tier 3 forecast only · Category D · Low conf      │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌───────────────────────┐  │
│  │ ELEVATED   │  │ CONF: LOW  │  │ NOT FOOD-SAFETY       │  │
│  │ ops-stress │  │ no sensors │  │ NOT HARVEST AUTH      │  │
│  └────────────┘  └────────────┘  └───────────────────────┘  │
│                                                             │
│ LIMITATIONS (always visible)                                │
│ Manual format mock. No model. Not body temperature. Not Vp. │
│ SST/DO/S if shown = supporting covariates w/ lag/mismatch.  │
│                                                             │
│ WHAT CHANGED                                                │
│ Daytime emersion overlapping forecast air + wind/wave       │
│ workability entered the 72h window. Yesterday: Typical.     │
│                                                             │
│ WHAT IT MEANS                                               │
│ Upper tercile of this lease’s comparable tide/season        │
│ work-stress windows. Not a probability. Not % dead.         │
│                                                             │
│ WHAT IT DOES NOT MEAN                                       │
│ Not harvest authorization. Not a closure. Not Vibrio/PSP.   │
│ Not weather-safety or navigation. Not SST-as-kill.          │
│                                                             │
│ DRIVERS (inputs, not causes)                                │
│ 1. PRIMARY: forecast air × daytime low-tide emersion        │
│    (+ solar geometry) — not oyster body temperature         │
│ 2. PRIMARY: wind/seas above this lease’s easy-work rule     │
│ 3. SUPPORTING ONLY: nearest-station water T/DO/S            │
│    (lag + spatial mismatch; not a 19°C kill law)            │
│                                                             │
│ MISSING                                                     │
│ Ploidy · on-lease sensors · handling · HAB toxin (always)   │
│                                                             │
│ OPTIONS (pick 0–N; not orders)                              │
│ [ A shift labor off hottest emersion ]                      │
│ [ B increase monitoring this daylight tide ]                │
│ [ C inspect gear after wave/wind event ]                    │
│ [ D keep current plan ]                                     │
│                                                             │
│ [ Log outcome (30s) ]  [ Report error ]  [ WDOH closures ]  │
│                                                             │
│ Freshness: NWS 21:00 UTC · CO-OPS tides as-of 18 Sep        │
│ DOH last-verified 22:10 UTC (MODULE B, not this score)      │
│ Sources: NWS · NOAA CO-OPS · WDOH (context only)            │
│ Full 14-field PDF attached.                                 │
└─────────────────────────────────────────────────────────────┘
```

**Visual rules:**

- Status chip color: Typical = gray, Elevated = amber, High = red-outline (not alarmist flood), Cannot issue = black/white.
- “NOT FOOD-SAFETY” and “NOT HARVEST AUTH” are **always** visible without scrolling on a phone.
- Buttons are real links: form, mailto error, WDOH.
- No choropleth of Puget Sound or Willapa farms. No SST-as-body-temperature sparkline. Optional tiny **tide/emersion vs forecast-air** sketch labeled “not oyster body temperature.”

---

## 2. PDF — one page, print/crew

```
+-----------------------------------------------------------------------+
| FISHAI OPS-RISK BRIEF     SAMPLE / NOT A LIVE FORECAST / NO MODEL     |
| Species: Pacific oyster (M. gigas / C. gigas)                         |
| Geo: WA Willapa DOH growing areas · PRIVATE Lease Zone B              |
|        (NOT Totten / NOT Vp Category 3 demo)                          |
| Target: Category D 72h ops-stress / work-window (not NSSP, not dead %) |
| Horizon: 2026-09-18 16:00 PDT → 2026-09-21 16:00 PDT                  |
| Evidence: Tier 3 forecast only · Category D · Low confidence          |
+-----------------------------------------------------------------------+
| HEADLINE                                                              |
| Elevated operational stress indicator for Lease Zone B over the next  |
| 72 hours, associated with forecast air overlapping daytime emersion   |
| and wave/wind exposure. Confidence: Low. This is not a food-safety    |
| determination and not harvest authorization. SST is not body temp.    |
| Verify WA DOH growing-area and biotoxin status (WAC 246-282-006).     |
+-----------------------------------------------------------------------+
| MEANS: upper tercile vs this lease, similar tides/season.             |
| DOES NOT MEAN: harvest legality, closures, toxins, guaranteed loss,   |
|                weather-safety, oyster body temperature.               |
| FRESHNESS: NWS 2026-09-18 21:00Z · CO-OPS tides as-of 18 Sep          |
|            WDOH last-verified 22:10Z (MODULE B — separate)            |
| CONFIDENCE: LOW — no on-lease sensor; unvalidated; no fake %.         |
| DRIVERS: air×daytime emersion×solar · wind/wave workability           |
|          water T/DO/S supporting only (lag/mismatch)                  |
| MISSING: ploidy, handling, HAB toxin, on-lease sensors                |
| SOURCES: NWS · NOAA CO-OPS · WDOH viewer (context, not modeled)       |
+-----------------------------------------------------------------------+
| OPTIONS (not commands): A shift labor off hottest emersion            |
|   B increase monitoring  C inspect gear after waves  D no change      |
| OUTCOME: https://form.example/oy-sample   (30 seconds)                |
| ERROR: reply WRONG or https://form.example/oy-sample?error=1          |
| DISCLAIMER: Not food-safety / not harvest authority / not navigation. |
|             WDOH pages win if they conflict. No combined score.       |
+-----------------------------------------------------------------------+
| Official MODULE B: fortress.wa.gov/doh/oswpviewer · GrowingAreaClosures|
| Brief ID OY-WA-SAMPLE-2026-09-18-B · as-of replayable                 |
+-----------------------------------------------------------------------+
```

Footer always: Brief ID + “as-of replayable” (ties to geospatial versioning).

---

## 3. WhatsApp / SMS ping (Elevated / High / Cannot-issue only)

SMS cannot hold 14 fields. **Contract = ping + link.**

```
FishAI Willapa Zone B: ELEVATED 72h ops-stress. Low conf.
NOT food-safety / NOT harvest OK. NOT body temp.
Air×tide + wind/wave. Options in PDF (not orders).
Log 30s: https://form.example/oy
WDOH: https://fortress.wa.gov/doh/oswpviewer/index.html
```

If they have not opened the PDF, the ping still contains: scope (Zone B), target (ops-stress), horizon (72h), not-meaning (food-safety), confidence, link to full contract.

---

## 4. 30-second outcome form (mobile-first)

Single screen, huge tap targets, no login if the magic link is farm-scoped and expiring.

```
┌─────────────────────────────────────────┐
│ FishAI  ·  30-second outcome            │
│ Zone B · window 19–21 Sep · 30s         │
│ LIMIT: ops/workability log only.        │
│ Not food-safety. Not harvest. Not SST.  │
│                                         │
│ 1. Did you work this lease in-window?   │
│    [ Yes ]  [ No — weather/ops ]        │
│    [ No — other reason ]                │
│                                         │
│ 2. Workability                          │
│    [ OK ] [ Hard ] [ Aborted ] [ n/a ]  │
│                                         │
│ 3. Handling / tumble / sort?            │
│    [ Yes ] [ No ] [ n/a ]               │
│                                         │
│ 4. Anything off? (optional multi)       │
│    [ ] Gaping / stress signs            │
│    [ ] Mortality above normal           │
│    [ ] Gear/bag issue                   │
│    [ ] Freshwater / low salinity feel   │
│    [ ] Low DO / lethargy feel           │
│    [ ] None of these                    │
│                                         │
│ 5. Optional one photo (gear or animals) │
│    [ Add photo ]                        │
│                                         │
│ 6. Did the brief change your plan?      │
│    [ Yes ] [ No ] [ Not sure ]          │
│                                         │
│ [ Submit ]     [ Report an error ]      │
│ Privacy: this stays private to your farm│
└─────────────────────────────────────────┘
```

Elapsed target: 20–30 seconds if 1–4 only. Photo is extra.

**Error sub-form:**

```
What is wrong?
 ( ) Wrong lease
 ( ) Stale / missing data
 ( ) Sounds like food-safety / harvest permission
 ( ) Unsafe or nav-like advice
 ( ) Other: [________]
[ Send ]
```

---

## 5. Weekly calibration email (Monday)

```
Subject: [FishAI] Zone B week of 14 Sep — private calibration

Last 7 briefs: Typical 4 · Elevated 3 · High 0 · Cannot-issue 0
Your logs: 5/7 work days
  Elevated days you logged Hard or Aborted: 2/3
  Typical days you logged OK: 3/3
This is YOUR data. Not a public score. Not food-safety.
Keep logging: [form]
```

---

## 6. Explicitly out of wireframe scope

- Global map with layers
- Species picker
- Multi-region tabs
- Social feed
- Public heatmaps
- Push notifications for every Typical day
- In-app chat with an unconstrained LLM

If a designer asks “where does the map go?”: **NANOOS already has it.** Our wireframe is the **sentence + contract + log.**

---

## 7. Chinook / lobster (if founder overrides)

**Chinook WhatsApp (season open only; customer-facing model halted — format mock):**

```
FishAI Chinook · named PFMC/ODFW area · next 24–48h
Relative CPUE rank: [lower/middle/upper] third of comparable OPEN days.
Conf: LOW or MEDIUM only. Evidence: Tier 2 logs required; else do not issue.
NOT abundance. NOT a catch guarantee. NOT nav/weather-safety/license.
NOT SST/chl habitat. Closed or unverified = NO SCORE.
Check NMFS/CDFW/ODFW. Log catch/no-catch + effort: https://...
```

**Lobster:**

```
FishAI lobster · YOUR zone · next trip
Effort-normalized catch rank vs YOUR comparable soaks: [lower/middle/upper] third
Conf: LOW–MED (no haul-level from you last week)
NOT abundance. NOT neighbor trap map. NOT AIS stock. NOT entanglement advice.
Log trip lb + hauls: https://...
```
