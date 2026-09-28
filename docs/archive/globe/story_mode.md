# Story mode

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/story_mode.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Optional explainer — **later**. Not MVP. Not a substitute for the 14-field contract.

Story mode is a **guided sequence** for a species or event. Every beat is tagged:

`OBSERVATION | MODEL_INFERENCE | FORECAST | HYPOTHESIS`

Untagged beats do not ship.

---

## 1. Example flow (parent brief)

1. Select species (or W1: select **ops-stress event**, not “find oysters”).  
2. Show historical seasonal distribution **or** historical work-stress climatology.  
3. Show current ocean / air / tide conditions (env truth states).  
4. Show detected anomaly (named reference).  
5. Show how the **estimate** changed (issued vs previous issued — no silent rewrite).  
6. Show forecast (dashed).  
7. Explain evidence and uncertainty (embed Evidence Explorer).  
8. Show what data would confirm or refute (field 16).

---

## 2. Allowed story families (later)

| Family | Honest use | Risk |
|---|---|---|
| Migration events | Coarsened, delayed, non-listed or PI-only | Live tracking, nest leak |
| Marine heatwaves | Env anomaly + **habitat** or ops-stress | Painting SST as carcass counts |
| HABs | Bloom **presence** proxies, not toxin legality | Food-safety leak into W1 |
| Spawning seasons | **Calendar / phenology**, not GPS | Aggregation fishing |
| Range shifts | T1 historical or scenario | Claiming current presence |
| Unusual sightings | Single `DIRECT_OBSERVATION` stamps | Crowdsourced secret spots |
| Restoration decisions | Research; options not commands | Guarantee of recovery |
| Scientific education | Primary use of this mode | Mixing hypothesis into “the map says” |

**W1 educational story (only after fixture, still not commercial v1):** “Why 2021-class heat × midday emersion is an **ops-stress** mechanism (Raymond et al. 2022) — and why that is still not harvest advice.” Beats: tide clock (obs/harmonic), air forecast, UNKNOWN body T, DOH module separate.

---

## 3. Chrome

```text
STORY MODE  ·  RESEARCH / EDUCATION
Beat 4 of 8  ·  this beat is: FORECAST
[Not an observation]  [Not food-safety]  [Not live tracking]
```

Playback speed follows `time_and_forecast_ui.md` (no cinematic schools). User can jump to Evidence Explorer at any beat.

---

## 4. What story mode is not

- Marketing reel of glowing oceans.  
- Unconstrained LLM tour.  
- Climate-scenario scare animation labeled as a 72h product.  
- Commercial MVP (email/PDF remains the operator surface).
