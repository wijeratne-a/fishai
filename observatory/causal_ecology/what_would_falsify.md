# What would falsify this causal-ecology design

**Date:** 2026-09-18  
**Status:** Pre-registered attacks on the **graph + contracts**, not on a fitted model (there is none).

If a test below fails, **demote** the edge (`causal_status_policy.md`). Do not rebrand the same claim. Do not train through the failure.

---

## 1. Universal falsifiers (engine-level)

| ID | Claim under test | Falsifier | Consequence |
|---|---|---|---|
| F-ENG-01 | “We have a causal model” | Any user-facing \(do(\cdot)\), SHAP-as-cause, or twin language | Stop-ship; remain `HYPOTHETICAL/RESEARCH MODE` |
| F-ENG-02 | Status honesty | An edge labeled `CAUSALLY_TESTED` whose citation is only a correlation table (e.g. Barton 2012 used as if it identified 72 h adult death) | Demote; Barton stays correlative **hatchery** support on E31, never E32 |
| F-ENG-03 | Weakest-link aggregation | A path containing SST→tissue-T (`UNKNOWN`) emitted as causal mortality | Contract break |
| F-ENG-04 | Predictive ≠ causal | A correlative expert rule described as “drivers caused” | Rewrite to prediction-contract language |
| F-ENG-05 | Label validity | Ops-stress trained or scored on WA DOH closures | BLOCKER (RT-OYS-04; `ground_truth_relabel_W1.md`) |
| F-ENG-06 | Counterfactual banner | Any scenario without **SCENARIO ESTIMATE — NOT OBSERVED FACT** | Do not emit |
| F-ENG-07 | Privacy | Lease-grain mortality or hypoxia map public | `NEVER_PUBLISH` incident (`sensitive_location_policy.md`) |

---

## 2. W1 mechanism falsifiers

### F-W1-HEAT-01 — 2021 was air × midday emersion × solar, not SST

**Claim:** Satellite or foundation SST is an adequate cause or sufficient predictor of 2021-type intertidal mortality.

**Falsifier (marine-domain E1, bound here):** Reconstruct 26–28 Jun 2021. Rank sites by **forecast/observed air T × daytime emersion × solar geometry**. Rank the same sites by SST-only. Compare to Raymond et al. 2022 maps / WSG narrative / Miner et al. 2025 morning-vs-afternoon tide contrast.

- **Pass (mechanism survives):** air×tide×solar separates affected vs spared sites **better** than SST-only; Olympic morning-low sites fared better at similar regional SST.  
- **Fail:** SST-only wins **and** labels are true farm/field mortality → **demote E05** and revisit E03 transport to farms; more likely: **labels are wrong** (closures or water T). Do **not** ship SST.

**Citations:** https://doi.org/10.1002/ecy.3798 · https://doi.org/10.3389/fmars.2025.1503019

### F-W1-HEAT-02 — SST ≥ 19 °C kill law

**Claim:** Crossing ~19 °C SST/water for a few hours is sufficient for 72 h bag death.

**Falsifier:** (i) FAO/NOAA envelopes already allow much wider survival T. (ii) George et al. 2023: water 30 °C **without** aerial 44 °C is not the high-mortality multi-stressor arm. (iii) Any season with many hours ≥19 °C and **low** protocol mortality on intertidal bags at **night** or **immersed** tides.

**Fail the kill law if any of those hold** — already the design position (E08 = `OBSERVED_CORRELATION`, not a law). Promoting E08 is forbidden.

https://doi.org/10.1111/gcb.16880

### F-W1-HEAT-03 — tissue T = SST

**Claim:** E06 should be upgraded.

**Falsifier:** Simultaneous biomimetic / mud / bag loggers vs nearest SST pixel during midday emersion: large positive tissue−SST residuals on clear, hot, low-tide days.

**Observed in literature already** → E06 stays `UNKNOWN`. Upgrade only if a named lease shows tissue T tracked SST within a pre-registered bound **during emersion** (unexpected).

### F-W1-HORIZON-01 — 72 h captures death

**Claim:** 72 h mortality labels measure the heat event.

**Falsifier:** Deaths accrue days–weeks later (Raymond 2022; George day-30). If 72 h labels miss the event, either extend the **label** window (not the ops **indicator** window) or keep \(Y\) = exposure/workability, not % dead.

---

## 3. Wrong-stage / wrong-geography / wrong-label

| ID | Claim | Falsifier | Edge |
|---|---|---|---|
| F-W1-OA-01 | Ω/pH headlines 72 h bags | Adult bag mortality tracks Ω after adjusting air×tide×DO | E32 stays `UNKNOWN` unless that happens; E31 remains larvae |
| F-W1-OA-02 | Barton 2012 identifies adult farm death | Paper is hatchery larvae vs intake Ω | Do not promote |
| F-W1-VIRUS-01 | OsHV-1 is the WA 72 h driver | Local PCR/qPCR **and** a challenge or tightly timed epidemic on WA farms | E34 stays `UNKNOWN` after 2020 OR/WA sentinel non-detect https://doi.org/10.3354/dao03868 |
| F-W1-DOH-01 | Closures are ops GT | Heat-kill with harvest **open**; or closure with healthy bags (toxin/fecal) | E42 stays `UNKNOWN` as mortality |
| F-W1-HAB-01 | “HAB in region” is one cause | Animal-stress list and NSSP list diverge; *Heterosigma* vs *Alexandrium* | Keep split; E35 `EXPERT_HYPOTHESIS` until named-taxon tests |
| F-W1-GEO-01 | One WA model | Hood Canal DO event without Willapa aerial pattern, or reverse | E29 survives; pooled model dies |
| F-W1-CULTURE-01 | Culture method is a dummy | Intertidal vs raft mortality reverse under the same SST | E25/E02 survive as mandatory strata |

---

## 4. Counterfactual-template falsifiers

| Template | Would upgrade (rare) | Would confirm **forbid** (default) |
|---|---|---|
| +2 °C water as 2021 replay | Air/tide/solar actually unchanged **and** bags die like 2021 | Water-only / SST-only does not match 2021 maps |
| DO below threshold WA-wide | Skill in **every** basin with sensors | Willapa heat days without hypoxia still kill intertidal stock |
| 30-day MHW = 2021 | 2021 SST time series is the lethal exposure | 2021 is AHW + lowest daytime tides |
| Current direction 72 h death | Pre-registered current reversal with mortality not explained by air/DO/handling | Only seasonal growth (E18) moves |
| Prey drop 72 h death | Named starvation protocol at 72 h | Only weeks-scale condition |
| MPA reduces fishing → bag survival | A farm mortality path through fishing (does not exist for planted stock) | Wrong system |
| HAB as legality | — | Always a policy fork, never ops \(Y\) |
| Preferred-depth hypoxia public map | — | Reverse-engineering test fails (`sensitive_location_policy.md` §8) |

---

## 5. Confounder falsifiers

If month×basin dummies absorb all deviance of an “AI driver,” the driver is **climatology** (E47). If only farms that report after rumors show mortality, `CF.sampling_effort` dominates (E45). If SST-only products are complete because sensors are missing, that is `CF.data_availability`, not evidence SST caused death (E52).

---

## 6. What would **not** count as falsification

- A correlative model beating persistence on random CV (leakage).  
- Marketing demand for a single stress score.  
- Sibling API copy calling Raymond et al. 2022 a “causal stressor.”  
- HiveClaw causal-runtime performance (different project; not a marine identification).

---

## 7. Stop rules

1. If the only passing 2021 discriminator is SST/chl → **do not ship** (marine-domain E1 fail).  
2. If ops labels are closures → **do not train**.  
3. If a counterfactual is emitted without the banner or as a fact → **incident**.  
4. If OsHV-1 or OA is user-facing on 72 h bags without a new edge review → **incident**.
