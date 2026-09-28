# Agent handoff — COST + UI/EXPLAINABILITY + product roadmap

**Agents:** COST_AND_DEPLOYMENT_ECONOMICS_AGENT, USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT, product roadmap owner  
**Date:** 2026-09-18  
**Write root:** `/Users/wijeratne/dev/fishai/observatory/`  
**Did not write:** `/Users/wijeratne/dev/fishai/artifacts/**` (commercial-wedge run)

---

## 1. Executive finding

**Recommended first prototype:** `P0-WILLAPA-MGIGAS-OSI72` — a **public-data-first software digital twin** of **Pacific oyster (*Magallana gigas*) 24–72h operational stress / work-window** in the **Willapa Bay WA DOH growing-area / lease cell**. Estimate **Category D environmental/operational conditions** (heat×emersion, waves, station T/DO/S if present). Do **not** estimate abundance, food-safety, or harvest legality. This is the smallest honest twin that can later serve the commercial 1×1×1×1 wedge. It is **not** a global taxa map.

**Year-1 budget band:** **$0.4–1.2 million USD (ESTIMATE)** for framework + that one cell (lean $0.25–0.5M; do not spend >$2M). **Hardware last:** public → partner export → existing sensors → manual obs → mobile → integrations. No EK80/DAS/AUV/VHR fleet in Year 1.

**What global coverage still cannot mean in 10 years:** a real-time census or tracker of saltwater life; abundance from SST/chl/AIS; uniform depth-resolved biomass; T6 for most taxa; eDNA-as-GPS; DAS-as-fish-finder; public fine-scale listed-species or private-spot maps; or the disappearance of UNKNOWN.

---

## 2. Files written

| File | Role |
| --- | --- |
| `cost_and_deployment_models/cost_model.md` | Six stacks, CITED vs ESTIMATE, Year-1 band |
| `product_roadmap.md` | Firewall, phases P0–P4, traction gates |
| `global_coverage_roadmap.md` | Five-axis coverage; 10-year cannots |
| `1_year_plan.md` | Framework + one cell; success/fail |
| `3_year_plan.md` | 1–4 operational-ish cells |
| `10_year_plan.md` | Planetary vision with hard cannots |
| `artifacts/product_cost/sample_evidence_ui_spec.md` | Evidence-class UI |
| `GLOBAL_SALTWATER_LIFE_OBSERVATORY_BLUEPRINT.md` | §§1–6 and 19–24 sketched; 7–18 placeholders |

---

## 3. Cost headline (order-of-magnitude)

| Stack | Year-1 P0 oyster cell | Label |
| --- | ---: | --- |
| Public software twin + partners | **$0.4–1.2M** | ESTIMATE |
| Partner sonar **export** | $0.1–0.4M extra, **not needed for P0** | ESTIMATE |
| Buy scientific sonar + ship | $0.5–2M+, **skip** | ESTIMATE + CITED kit $55k–$441k |
| eDNA mesh | $0 required; $8–20k micro-test | ESTIMATE / CITED ~$200–$250/sample |
| Hydrophone/DAS | $0 (wrong taxon); DAS box $200k–$1M+ commentary | ESTIMATE/CITED mixed |
| AUV/glider | $0 (wrong boundary); glider-month €3–30k at sea | CITED GROOM |
| VHR tasking | $0; SkySat $12–$40/km² if ever | CITED |

CMEMS physics is **free to user through 2028-06-30** (CITED licence) — still not fish.

---

## 4. UI headline

Every view: evidence class, UNKNOWN first-class, no count theater, depth+time+uncertainty, provenance, what-it-is-not. Operator surface stays **email/PDF/form**.

---

## 5. Exact next 25 actions

See blueprint **§23** (canonical list). Do not start ML, ingest, or hardware procurement before actions 1–7.

---

## 6. Prototype success / fail

**Success:** rights-approved as-of cell store; 3 farms or documented recruit fail; 14-day manual then ≥60 issuance days; ≥60% outcome completeness; contract fields on every brief; baseline documented; no heatmap; no hardware fleet.

**Fail:** 0/3 would change a crew call; food-safety-only demand; no logs; claim inflation; second species/global UI used as budget sink.

---

## 7. Handoff recipients

- Architecture: keep P0 twin **tiny** (one cell, emersion+station depth, replay).  
- Rights: NANOOS per-stream; CMEMS attribution; DOH context-only.  
- Validation: OSI-72 vs heat×tide baseline; never vs DOH closures.  
- Hypotheses: rank partner logs #1; kill global mesh as Year-1.  
- Taxonomy: do not upgrade non-P0 taxa.  
- Commercial wedge agents: **do not expand SKU.**  
- Founder: lock W1/W2/W3.

---

## 8. Confidence

| Claim | Confidence |
| --- | --- |
| P0 cell choice given commercial research | **High** as smallest honest twin; **Medium** as commercial winner (no interviews) |
| $0.4–1.2M Year-1 band | **Medium** (staffing dominates; ×2–×5) |
| 10-year cannots | **High** (physics + sampling + law) |
| Cited instrument prices | **Medium** (vintage, tenders, not our RFQ) |

---

## 9. Prohibited follow-ups

Do not interpret this handoff as approval to ingest data, train models, contact farms without founder permission, purchase sensors, or overwrite sibling catalogs/architecture/hypotheses.
