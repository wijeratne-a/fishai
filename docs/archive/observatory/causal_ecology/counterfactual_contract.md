# Counterfactual contract

**Date:** 2026-09-18  
**Status:** Binding. No counterfactual may be computed from a trained causal model — **none exists.**  
**Banner (mandatory on every scenario, including internal fixtures):**

# SCENARIO ESTIMATE — NOT OBSERVED FACT

If that banner is missing, the output is out of contract.

Observatory output class: `HYPOTHETICAL/RESEARCH MODE`.  
Default user-facing emission: **do not emit** (see §6).

---

## 1. What a counterfactual is here

A structured answer to: “If \(X\) had been (or will be) \(x'\) instead of \(x\), what do we **honestly not know**, and what mechanism path would we even use?”

It is **not**:

- an observation;  
- a forecast with skill;  
- \(P(Y \mid do(X=x'))\) from FishAI;  
- harvest legality, food safety, navigation safety, or a catch/survival guarantee;  
- a replay of 2021 unless the intervention matches **air × midday emersion × solar**.

Path status = **weakest** edge (`graph_schema.md` §5).

---

## 2. Required fields (every scenario)

| Field | Requirement |
|---|---|
| `banner` | Exact phrase **SCENARIO ESTIMATE — NOT OBSERVED FACT** |
| `scenario_id` | Stable ID |
| `taxon` / stage / geography / culture / horizon | Scoped |
| `intervention_X` | Well-defined; include **what is held constant** |
| `outcome_Y` | Declared; W1 default `ops_disruption_72h` **or** a named physiology node — never “health” or “legal to harvest” |
| `query_mode` | `causal` or `both` (a purely predictive what-if is a **sensitivity run**, still needs the banner) |
| `assumed_path[]` | Edge IDs |
| `path_causal_status` | Min along path |
| `identification_class` | Usually `NONE` for these templates until a reviewer upgrades |
| `assumptions[]` | Explicit, including “no fitted SCM” |
| `limitations[]` | Stage, basin, delayed death, missing sensors |
| `uncertainty` | Qualitative; **no** three-decimal probabilities; `uncalibrated` |
| `causal_evidence_tier` | The five-status label of the path, **plus** observatory evidence tier of any data (1–4) used as context |
| `data_support` | What exists **today** (usually `none` or `lab_only` / `sparse`) |
| `confounders[]` | Catalog + W1 extras |
| `anti_claims[]` | |
| `privacy` | `PRIVATE` if lease-grain; public max growing-area / withhold |
| `review_gate` | `forbidden_user_facing` or `internal_research_ok_after_review` |

---

## 3. Catalog of required scenario templates

All eight must be instantiable. None is an observed fact. W1 encoding notes are **mandatory** when taxon is *Magallana gigas* farm stock.

### 3.1 `+2 °C water` (`CF.TEMP.WATER_PLUS_2C`)

| | |
|---|---|
| Intervention | In situ **water** temperature +2 °C relative to a named baseline; **air T, tide, solar held at baseline** unless separately specified |
| W1 encoding | **Not** the 2021 Salish mechanism. 2021 was **air temperature × midday emersion × solar**, not satellite SST as body temperature. George et al. 2023: warm water **alone** is not the multi-stressor protocol that produced the large delayed-mortality contrast. **SST ≥ 19 °C is not a kill law.** |
| Typical path status | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` for metabolism/spawn; `OBSERVED_CORRELATION` if the user meant SST≥19 death; `UNKNOWN` if chained through SST→tissue T |
| User-facing without review | **Forbidden** if phrased as mass kill or as a 2021 replay |

### 3.2 `DO below threshold` (`CF.DO.BELOW_THRESHOLD`)

| | |
|---|---|
| Intervention | Dissolved oxygen below a **named** threshold at **culture depth** in a **named basin** |
| W1 encoding | Real co-stressor in Puget Sound summer mortality (Cheney et al. 2000). FAO >2 mg L⁻¹ is a culture **floor**, not a no-effect level and not a 72 h kill law. Hood Canal ≠ Willapa. Do not fuse with aerial heat into one score. |
| Typical path status | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` with local sensors; `UNKNOWN` WA-wide |
| User-facing without review | **Forbidden** as a statewide law or as harvest closure |

### 3.3 `30-day marine heatwave` (`CF.MHW.30_DAY`)

| | |
|---|---|
| Intervention | Water-column MHW lasting 30 days (Hobday-class definition must be stated); not an air heat dome unless separately specified |
| W1 encoding | Horizon mismatch: delayed mortality can accrue to ~30 **days** after exposure, while the **ops product window is 72 h**. **2021 was an atmospheric heatwave coincident with the year’s lowest daytime tides, not a marine SST event.** SST is not tissue T. |
| Typical path status | `UNKNOWN` as a 72 h bag headline; research-only as seasonal condition |
| User-facing without review | **Forbidden** as “the 2021 event” or as a 72 h death forecast |

### 3.4 `Current direction change` (`CF.CURRENT.DIRECTION`)

| | |
|---|---|
| Intervention | Named change in residual current / residence time |
| W1 encoding | Willapa residence-time contrast explains **seasonal growth** (Banas / fattening line), not 48–72 h mortality. Sessile planted stock does not advect off the lease in 72 h. |
| Typical path status | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` for seasonal growth; `UNKNOWN` for 72 h mortality |
| User-facing without review | **Forbidden** as 72 h causal mortality |

### 3.5 `Prey drop` (`CF.PREY.DROP`)

| | |
|---|---|
| Intervention | Named decline in phytoplankton food (not a toxin HAB unless declared) |
| W1 encoding | Chlorophyll is food/condition at **weeks–months**; **never abundance** (stock is planted). Weak as 72 h mortality unless a named crash/HAB. |
| Typical path status | `UNKNOWN` for 72 h mortality; `OBSERVED_CORRELATION` / `ECOLOGICALLY_SUPPORTED_ASSOCIATION` for growth |
| User-facing without review | **Forbidden** as 72 h kill or as oyster counts from ocean color |

### 3.6 `MPA reduces fishing` (`CF.MPA.REDUCE_FISHING`)

| | |
|---|---|
| Intervention | Fishing mortality of **wild** mobile taxa reduced inside a named MPA |
| W1 encoding | Pacific oysters on WA farms are **planted and sessile**. Reducing fishing is not a 72 h bag-survival mechanism. Do not launder MPAs as oyster health. For wild fisheries this template is a **different graph** (effort, catchability, hyperstability) and still not abundance. |
| Typical path status | `UNKNOWN` for W1 ops mortality |
| User-facing without review | **Forbidden** (wrong system + easy abundance misread) |

### 3.7 `HAB in region` (`CF.HAB.IN_REGION`)

| | |
|---|---|
| Intervention | Named phytoplankton taxon present above a named cell-count or toxin **context** — **must split lists** |
| W1 encoding | **Animal-stress** HABs (e.g. hypothesized *Protoceratium*/yessotoxins, high-biomass feeding shutdown) ≠ **human-toxin** NSSP lists (*Alexandrium* PSP, DSP, ASP). **WA DOH closure is regulatory, not causal mortality in the ops model.** SoundToxins ≠ tissue test. Never “safe to eat.” |
| Typical path status | `EXPERT_HYPOTHESIS` for WA 72 h animal-stress; `POLICY_MAPPING` for closures |
| User-facing without review | **Forbidden** if readable as harvest legality, toxin-free, or mixed green/red ops+sanitation score |

### 3.8 `Preferred depth hypoxic` (`CF.DEPTH.PREFERRED_HYPOXIC`)

| | |
|---|---|
| Intervention | Oxygen below a named threshold **at the depth/elevation the animals actually occupy** |
| W1 encoding | For oysters, “preferred depth” is **culture elevation**: intertidal animals may leave hypoxic water at low tide **and** take aerial heat (tradeoff). Subtidal/raft stock cannot use that escape. Not a WA-wide law. Public fine maps can invert failing leases → privacy fail. |
| Typical path status | `ECOLOGICALLY_SUPPORTED_ASSOCIATION` in named stratified basins with sensors; `UNKNOWN` as a global rule |
| User-facing without review | **Forbidden** at lease grain; forbidden as a statewide product layer |

---

## 4. Assumptions, limitations, uncertainty, evidence, data (always)

Copy this checklist into every fixture:

**Assumptions (minimum):** no FishAI SCM; intervention is ceteris paribus as specified; planted sessile stock for W1; culture method known; delayed death may push labels outside 72 h; official harvest status is a separate module.

**Limitations (minimum):** microclimate unobserved; no public farm-mortality panel; basin non-transfer; lab ≠ lease; 2021 expert ratings ≠ bag %.

**Uncertainty (minimum):** `uncalibrated`; confidence `None` for user-facing biological scores; do not print 0.73.

**Causal-evidence tier:** five-status of path + data evidence tier 1–4 of any **context** series (never promote).

**Data support:** cite programs as **existence**, not as loaded series (NANOOS, NERRS, Ecology, SoundToxins, partner logs). `integration_status = CATALOG_ONLY`.

---

## 5. Sensitivity runs vs causal scenarios

If `query_mode = predictive`, you may perturb an **input** and report that an expert rule’s **indicator rank would change**. Still use the banner. Still not a fact. Still not “caused.”

---

## 6. Forbidden as user-facing without named human domain review

**Default:** all eight templates are **not user-facing**. Research fixtures live in `fixture_counterfactuals.md` only.

**Hard-forbidden** (do not put on a customer brief, map, or sales deck even with the banner, until a named reviewer **and** this module are rewritten):

1. Any scenario missing **SCENARIO ESTIMATE — NOT OBSERVED FACT**.  
2. **`+2 °C water` or SST ≥ 19 °C as a kill law** or as a 2021 replay.  
3. **30-day MHW as the 2021 Salish die-off** or as a 72 h bag-death forecast.  
4. **Ocean acidification / Ω as a 72 h market-bag headline.**  
5. **OsHV-1 outbreak timing in Washington.**  
6. **HAB in region as harvest legality, “safe to eat,” toxin-free, or mixed ops+sanitation score.**  
7. **WA DOH / NSSP closure as causal mortality or survival.**  
8. **MPA reduces fishing → oyster survival or abundance.**  
9. **Current-direction change as 72 h causal mortality.**  
10. **Prey / chlorophyll drop as 72 h kill or as oyster abundance.**  
11. **Preferred-depth hypoxia at public lease grain** (farm KPI inversion).  
12. Numeric % mortality, catch guarantees, “harvest now,” weather-safety, commands.  
13. Public biological heatmaps of the scenario (sensitive-location policy; global life map already rejected).

**May be discussed internally after review** (still bannered, still not a product): +2 °C water as **metabolism/spawn co-factor**; DO below threshold in a **named basin with sensors**; named **animal-stress** HAB as hypothesis; culture-depth hypoxia tradeoff as mechanism note; seasonal residence-time / food as **growth**, not 72 h death.

Amendment: named human domain reviewer only.
