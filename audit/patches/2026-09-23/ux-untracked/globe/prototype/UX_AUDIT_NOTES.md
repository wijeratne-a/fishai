# UX audit notes — FishAI marine globe prototype

**Auditor role:** UI/UX Lead (honesty-preserving)  
**Date:** 2026-09-22  
**Worktree:** isolated `ux/globe-honesty-pass`  
**Scope:** presentation, copy, modes, legend, answer strip, evidence panel, discoverability — not species models or publication gates.

---

## 2.1 First-run (first ~5 seconds)

| Finding | Severity | Status |
|---|---|---|
| Purpose was buried in a dismissible dialog; cold load needed a one-line product sentence next to search | High | Fixed — purpose line under search |
| First-run dialog leaned instructional but not the agreed purpose sentence | Med | Fixed — aligned copy |
| Willapa oyster working-conditions demo correctly gated behind Learn | OK | Preserved |
| Empty answer strip already prompted action | OK | Strengthened empty copy |
| Banner honesty (“not live tracking / not harvest”) is good | OK | Kept; toned marketing elsewhere |

## 2.2 Map / globe interaction

| Finding | Severity | Status |
|---|---|---|
| Drag / zoom / tilt work via MapLibre; instructions lived only inside Layers | High | Fixed — persistent map hints + compact 2D/3D · North · Home tools |
| Flat map toggle was unlabeled as 2D/3D | Med | Fixed — “2D flat map / 3D globe” wording + toolbar |
| Home / North up / Reset tilt existed but were easy to miss | Med | Fixed — toolbar duplicates primary actions |
| Camera / basemap science left to other agents | — | No retune |

## 2.3 Answer strip and panels

| Finding | Severity | Status |
|---|---|---|
| Honesty fields (Where now / Soon / Depth / This is not) were present | OK | Labels/copy tightened |
| “This is not” competed with dense “targets” jargon | Med | Fixed — targets detail Expert-only |
| Evidence panel jumped into field lists; weak plain-language top summary | High | Fixed — summary + Observation / Estimate / Environment / Methods groups |
| Evidence / Learn discoverable via nav | OK | Nav labels clarified |
| Mode switch already kept selected species | OK | Verified; no clear on nav change |

## 2.4 Visual hierarchy

| Finding | Severity | Status |
|---|---|---|
| Search is prominent in chrome — good | OK | Kept |
| Answer dock can overwhelm with scientific status + targets | Med | Fixed — quieter primary strip |
| Map stamp / resolution / coords competed for attention | Low | Left; hints are quieter |

## 2.5 Legend semantics

| Finding | Severity | Status |
|---|---|---|
| Labels used Guessed / Future / Don’t know | High | Fixed → Measured / Estimate / Forecast / Past reports / Unknown |
| Patterns already existed (not color alone) | OK | Legend swatches + micro-explanations |
| Past reports needed explicit “not live presence” microcopy | Med | Fixed |

## 2.6 Copy / jargon

| Finding | Severity | Status |
|---|---|---|
| Primary UI targets line used occurrence probability / relative abundance | Med | Moved under Expert |
| Guessed / Future / Don’t know in truth labels | Med | Relabeled |
| No dominant covariates / posterior / CPUE in primary chrome | OK | Kept technical terms out of primary strip |
| Overclaiming: published estimate copy only when gate true | OK | Preserved; experimental wording when issued |

## 2.7 Accessibility and performance basics

| Finding | Severity | Status |
|---|---|---|
| Skip link, focus-visible, aria-live status present | OK | Kept |
| Contrast on dark chrome is generally adequate | OK | Answer “This is not” strengthened visually |
| Narrow layout stacks chrome → answer → map | OK | Retained media query |
| Full ocean hatch for unknown (beyond past-report cells) not drawn world-wide | Known gap | Honesty via strip + legend; optional Gaps control for demo cells |

---

## Honesty constraints (do not weaken)

- “No issued location.” when no validated published model
- “No forecast issued.” unless published forecast exists
- Depth unknown / not modeled unless meaningful depth model exists
- How sure = None without validation metrics
- This is not: live tracking, a fishing map, or a count of animals
- Oyster demo stays Learn-gated; not harvest / food-safety / animal GPS
- Zero assumption that any species forecast is ready (goliath grouper = NOT_PUBLISHED)

---

## Follow-ups (human / other agents)

- Optional full-ocean unknown hatch when a species context is active (architecture/basemap ownership)
- Past-report cell click → evidence detail is wired; further cell metadata depends on OBIS payload richness
- Commit / merge via `/apply-worktree` when ready
