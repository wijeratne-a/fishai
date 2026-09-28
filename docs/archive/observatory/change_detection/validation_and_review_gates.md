# Validation and review gates — change-detection events

**Date:** 2026-09-18  
**Status:** Binding on promotion from fixture/internal candidate → any user-facing story (brief, UI, deck, press, API).  
**Today:** every CSV row fails `G-LIVE` on purpose. Nothing is story-eligible.

This is not a skill scorecard (no detector ran). Skill, when it exists, follows `observatory/validation_protocol.md` and `artifacts/quality_and_validation/`. This file answers: **which event classes require a named human scientific reviewer before a user hears them.**

---

## 1. Gate stack (all must pass for a user-facing story)

| ID | Gate | Pass criterion |
|---|---|---|
| **G-LIVE** | Not a live product writer | Wedge locked; rights; partner GT if W1; `issued_as_operational_alert` allowed by product+red-team. **Fail today.** |
| **G-TREE** | Observation-artifact rule | `bias_vs_biology.md` completed; exit node stored; effort + *p* addressed or class is GAP/ARTIFACT |
| **G-CONTRACT** | Prediction contract | Category C/D; 14 fields; no abundance/harvest/navigation/food-safety language |
| **G-FOOD-WALL** | NSSP / DOH wall (W1 and any HAB class) | Ops class not trained on closures; HAB class not a tissue stamp; official status is a **separate attributed module** |
| **G-PRIVACY** | Sensitive location policy | Publish tier respected; reverse-engineering test if any map; aggregations default `NEVER_PUBLISH` |
| **G-GRAIN** | Geography / depth honesty | No Hood Canal ORCA as Willapa; no SST as intertidal tissue; no empty-cell fill |
| **G-CAL** | Confidence | `high` only per `uncertainty_policy.md`; fixtures cannot be High |
| **G-HUMAN** | Named human reviewer | Shellfish + NSSP-literate for W1/HAB/mortality; fisheries scientist for range/phenology/depth of wild taxa; **this agent is not that person** |
| **G-STORY** | Narrative promotion | Explicit accept of `story_eligible=true`; alternatives listed; `POSSIBLE_` prefix retained until confirmed |

**Stop-ship:** any class used as “AI detected a die-off / HAB closure / new secret hole.”

---

## 2. Review requirement by `event_class`

“User-facing story” = operator brief, observatory card, screenshot, journalist talking point, or API field a customer can see.

| Class | Internal candidate log | User-facing story | W1 commercial brief |
|---|---|---|---|
| `DATA_GAP` | Allowed as coverage flag | **G-STORY** if phrased as a story; usually show UNKNOWN hatch without drama | Allowed as “cannot issue / missing local DO” **if** G-CONTRACT/G-FOOD-WALL hold |
| `POSSIBLE_OBSERVATION_ARTIFACT` | Allowed | **G-HUMAN + G-STORY** before blaming “false alarm” on a partner | Allowed as “do not read visit drop as mortality” |
| `NO_SIGNIFICANT_CHANGE` | Allowed | G-STORY if used as “all clear” (must not mean harvest-safe) | Allowed as typical stress **rank**, never harvest OK |
| `POSSIBLE_MORTALITY_EVENT` | Internal only until G-HUMAN | **Always** G-HUMAN + G-FOOD-WALL + G-PRIVACY + G-STORY | **Always** human review; PRIVATE; not a public kill map |
| `POSSIBLE_HAB_EVENT` | Internal only until G-HUMAN | **Always** G-HUMAN + G-FOOD-WALL + G-STORY | Animal-stress only; **never** harvest authorization |
| `RANGE_SHIFT` | Research log | **Always** G-HUMAN + G-TREE (effort/*p*) + G-PRIVACY | **Not a W1 product** |
| `DEPTH_SHIFT` | Research log | **Always** G-HUMAN (vertical refuge vs decline) | **Not W1** |
| `PHENOLOGY_SHIFT` | Research log | **Always** G-HUMAN (effort calendar) | **Not W1 72 h target** |
| `DISPERSAL_EVENT` | Research log | **Always** G-HUMAN + transport vs occupancy | **Not W1** |
| `AGGREGATION_EVENT` | Restricted log | **Default: no story.** If a recovery program insists: G-HUMAN + G-PRIVACY coarsen/delay or withhold | **Forbidden public map** |

`POSSIBLE_` is not cosmetic. Removing it requires independent confirmation (protocol counts, designed survey, or lab ID) **and** a human.

---

## 3. W1-specific reviewer checklist

Named humans (not agents), before any real send:

1. Shellfish aquaculture scientist / extension (heat × emersion, culture method).  
2. NSSP / WA DOH-literate reviewer (food-safety wall — RT-OYS-01 still open in commercial red team).  
3. Privacy: no lease GPS, no neighbor KPIs, no public mortality heatmap.

Checklist items:

- [ ] Air × daytime emersion used if intertidal; SST-only ⇒ do not issue mortality class  
- [ ] DOH status shown as authority, not mixed into the ops score  
- [ ] HAB copy cannot be read as “safe to eat”  
- [ ] ORCA/Hood Canal not substituted for Willapa  
- [ ] Delayed-mortality window disclosed (2021 analogue)  
- [ ] Outcome form exists (worked tide / noticed mortality) — quality B5 analogue  
- [ ] `issued_as_operational_alert` remains false until G-LIVE

---

## 4. Observatory research classes (wild taxa)

Additional reviewers: fisheries scientist familiar with the survey that produced the index; acoustician if sound; molecular if eDNA. Listed taxa / spawn aggregations: ecological-harm review (`sensitive_location_policy.md` §4) **before** coarsened public text.

Do not promote a `RANGE_SHIFT` press sentence from GBIF dots.

---

## 5. Fixture rule (this pass)

| Field | Required value |
|---|---|
| `record_status` | `FIXTURE_RESEARCH_ONLY` |
| `issued_as_operational_alert` | `false` |
| `story_eligible` | `false` |
| `human_scientific_review_required` | `true` for every biological process class; `true` for ARTIFACT/GAP/NSC if they would be shown to users as a “result” |

Replaying 2021 or 2019 **as a classification drill** does not authorize a 2026 alert with the same class.

---

## 6. Relation to quality GO/NO-GO

A future detector that “finds events” but fails prospective B4/B12 skill, or that labels effort collapses as mortality, **fails** even if the schema is valid. Gates here are **claims/safety**. Skill gates remain in `go_no_go_scorecard.md`.
