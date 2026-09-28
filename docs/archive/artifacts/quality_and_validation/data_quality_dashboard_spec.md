# Data Quality Dashboard Spec — Ocean Intelligence Builder / FishAI

**Agent:** QUALITY_AND_VALIDATION_AGENT  
**Date:** 2026-09-18  
**Version:** `DQ-DASH-2026-09-18-v1`  
**Status:** Spec only. No production dashboard. No bulk ingest.  
**Purpose:** Operationalize **better data** so sources are scored, gated, and monitored — not accumulated.

This dashboard is internal. Customer-facing briefs show a **subset**: freshness, missing inputs, confidence, rights/disclaimer — never partner identifiers or exact private locations.

---

## 1. Scope

Two layers:

1. **Source / dataset scorecard** — one row per candidate source or derived table.
2. **Issuance / product health** — one row per forecast issuance (and rolling aggregates).

Every score has: `score` (0–5), `score_definition`, `evidence`, `evaluator`, `date`, `confidence` (high/medium/low), `improvement_plan`.

**Unscored = 0 for gating purposes.** “Unknown license” is not 3.

---

## 2. Scoring scale (shared)

| Score | Meaning |
| --- | --- |
| 0 | Missing, unlawful, or unusable for this decision |
| 1 | Severe defect; research-only |
| 2 | Usable with major limitations; cannot support customer claims alone |
| 3 | Acceptable for internal baseline / research replay |
| 4 | Production-capable with documented residual risk |
| 5 | Exemplary: timely, rights-clear, outcome-linked, reproducible |

Dimensions where **higher is worse** (privacy risk, ecological sensitivity) are stored as risk 0–5 and inverted to a **usability subscore** `5 − risk` for any weighted total. The dashboard **always shows raw risk**, never only the inverted score.

---

## 3. Dimensions (required)

Each dimension below includes: definition, evidence, 0–5 anchors, owner, and a **gate**. Gates are hypotheses.

### 3.1 Relevance

**Definition:** Does this dataset change the locked decision at the locked grain and horizon?

| 0 | 3 | 5 |
| --- | --- | --- |
| Wrong species, place, or decision | Related environmental/context | Directly measures the label or a mechanistically justified covariate at usable grain |

**Evidence:** mapping to target label; marine-domain mechanism note.  
**Owner:** MARINE_DOMAIN + QUALITY  
**Gate (hypothesis):** production feature requires ≥4; context layers ≥3.

### 3.2 Accuracy

**Definition:** Agreement with a higher-tier reference when one exists (sensor cal, survey vs log, dealer vs harvester).

| 0 | 3 | 5 |
| --- | --- | --- |
| Known large bias, no correction | Typical of class; documented bias | Validated vs independent protocol |

**Evidence:** RMSE vs reference, bias tables, calibration certificates.  
**Owner:** DATA_ENGINEER + QUALITY  
**Gate:** label sources ≥4; covariates ≥3.

### 3.3 Reliability

**Definition:** Stability of the measurement process (uptime, method changes, agency vintage quality).

| 0 | 3 | 5 |
| --- | --- | --- |
| Frequent silent method changes | Occasional outages, documented | Dual-source, stable protocol |

**Evidence:** source-health time series; changelog.  
**Gate:** critical inputs ≥4.

### 3.4 Timeliness

**Definition:** Latency from observation to **availability at issuance**, vs product need.

| Product | Need (hypothesis) | Score 5 | Score 2 | Score 0 |
| --- | --- | --- | --- | --- |
| Oyster 72h | hours | ≤6 h | 1–3 d | weekly only |
| Chinook 24–48h | hours–1 d | ≤12 h | 2–7 d | monthly RecFIN as if daily |
| Lobster next-trip | ≤1–2 d for partner logs; monthly agency files are **not** timely for others’ latest trips | partner same-day | DMR by 10th of next month | annual landings |

**Evidence:** `published_at − observed_at` distribution.  
**Gate:** cannot be the sole critical input if timeliness ≤2.

### 3.5 Coverage (spatial + temporal)

**Definition:** Fraction of the decision universe observed, and years/seasons spanned.

Score **separately** spatial and temporal, then take the **min** for gating (a long time series on one pier is not coverage).

| 0 | 3 | 5 |
| --- | --- | --- |
| Outside geography or <1 season | Partial basin / 2 seasons with holes | Full locked geography × ≥3 relevant seasons |

**Gate:** GT coverage ≥3 to start baselines; ≥4 to claim geographic transfer.

### 3.6 Resolution (spatial + temporal)

**Definition:** Native grain vs required grain.

| Candidate | Required grain (hypothesis) | Score 5 | Score 1 |
| --- | --- | --- | --- |
| Oyster | farm-zone, ≤daily labels; hours for sensors | farm + hourly sensors | county-month |
| Chinook | ~10 km, daily | trip-cell-day | CRFS district-month as label |
| Lobster | TMS-trip | trip × TMS × effort | state-year landings |

Score spatial and temporal separately; gate on min.  
**Gate:** label resolution ≥4; feature resolution ≥3 or documented aggregation.

### 3.7 Completeness

**Definition:** Non-null required fields (effort, species, time, location precision, units).

| 0 | 3 | 5 |
| --- | --- | --- |
| Effort missing on CPUE; species unk | 80–90% required fields | ≥98% required fields in universe |

**Gate:** rows used for labels must meet ≥4 after QC flags (do not silently drop).

### 3.8 Consistency

**Definition:** Units, taxonomy, CRS, time zone, ID stability across vintages.

| 0 | 3 | 5 |
| --- | --- | --- |
| Mixed units, silent CRS, *C. gigas* vs *M. gigas* unmapped | Mapped with residual aliases | Canonical schema + tests green |

**Gate:** ≥4 before join into feature snapshots.

### 3.9 Comparability

**Definition:** Can values be compared across vessels, farms, years, gear, and management eras?

| 0 | 3 | 5 |
| --- | --- | --- |
| Gauge-size change ignored; mixed gear CPUE | Era flags exist | Standardized effort, era segments, documented conversions |

**Gate:** lobster CPUE ≥4 only if soak + trap-hauls + era flags exist.

### 3.10 Interoperability

**Definition:** Join keys (time, cell, taxon, source_id) to the canonical model (WGS84, UTC, approved taxonomy, H3/equal-area).

| 0 | 3 | 5 |
| --- | --- | --- |
| PDF / screenshot only | Manual ETL possible | API + schema + stable IDs |

**Gate:** production ingest ≥4.

### 3.11 Traceability

**Definition:** Can we replay from raw payload → feature → prediction → scorecard?

| 0 | 3 | 5 |
| --- | --- | --- |
| Overwrites, no hashes | Run IDs on predictions only | Immutable raw + transform hash + forecast_id lineage |

**Gate:** ≥5 for any customer-facing forecast (hypothesis: 4 allowed in first internal retro).

### 3.12 Provenance

**Definition:** Source owner, URL, license, attribution, dataset version on every record.

| 0 | 3 | 5 |
| --- | --- | --- |
| Unknown origin | Metadata table exists | Record-level provenance URL + license + version |

**Gate:** ≥4 to leave quarantine.

### 3.13 Legal usability

**Definition:** Rights class from DATA_RIGHTS agent.

| 0 | 3 | 5 |
| --- | --- | --- |
| REJECTED / UNKNOWN / scrape | CONDITIONAL / RESEARCH_ONLY (internal) | APPROVED_* matching the use (train / display / redistribute) |

**Gate:** production **must** be an APPROVED_* class. This dimension is a **hard fail** at 0–2 for customer output.

### 3.14 Privacy (risk 0–5, higher = worse)

**Definition:** Person, vessel, exact fishing location, farm performance, tribal, or inference risk.

| Risk 0 | Risk 3 | Risk 5 |
| --- | --- | --- |
| Public gridded SST | Coarsened catch cells | Exact trap GPS, named grower mortality |

**Gate:** NEVER_PUBLISH and PRIVATE data cannot score “production display” regardless of scientific quality. Training on PRIVATE requires DUA + no public leakage including explanations/heatmaps.

### 3.15 Ecological sensitivity (risk 0–5)

**Definition:** Harm if disclosed or if the product concentrates effort on sensitive habitat / spawning / protected species.

| Risk 0 | Risk 3 | Risk 5 |
| --- | --- | --- |
| Broad SST | Fine Chinook heatmap in constrained stock years | Protected-species aggregations, unpublished nursery maps |

**Gate:** risk ≥4 ⇒ coarsen, delay, or exclude. Chinook 10 km public maps in weak-run years need red-team sign-off (**hypothesis**).

### 3.16 Reproducibility

**Definition:** Independent rerun with stored parameters yields the same snapshot (bitwise or within documented tolerance).

| 0 | 3 | 5 |
| --- | --- | --- |
| Manual clicks, no vintages | Scripted but floating vintages | Pinned vintages + tests |

**Gate:** ≥4 for evaluation reports used in go/no-go.

### 3.17 Resilience

**Definition:** Fragility tier A/B/C and fallback.

| 0 | 3 | 5 |
| --- | --- | --- |
| Single unpaid scrape, no fallback | One official API, status page | Dual sources + tested fallback |

**Gate:** no production-critical prediction relies solely on Tier C. Resilience ≤2 on a critical input ⇒ auto-downgrade confidence.

### 3.18 Outcome linkage

**Definition:** Can this source be joined to the customer outcome that is the label?

| 0 | 3 | 5 |
| --- | --- | --- |
| No path to labels | Delayed / coarse join | Same grain, low-latency partner outcomes with consent |

**Gate:** a wedge without any source ≥4 on outcome linkage **fails Gate 3** (ground truth available).

---

## 4. Optional extra dimensions (display, not required for v1 gate)

- Commercial value  
- Usability (operator time to interpret raw source)  
- Source Priority Score from project north-star (0.30 relevance + 0.20 lift + 0.15 timeliness + 0.15 rights + 0.10 coverage/resolution + 0.10 defensibility)

These must **not** override a legal/privacy hard fail.

---

## 5. Dashboard views

### 5.1 Source catalog view (table)

Columns: source_id, name, candidate(s), rights class, privacy tier, fragility, 18 dimension scores, `min_gate`, last_verified, ingest_status (`NOT_INGESTED` default).

Filter: failing legal, failing timeliness, outcome-linkage = 0.

**Color:** red if any hard-fail gate; amber if min score <3; green if all production gates pass.

### 5.2 Coverage map (internal)

- Cells/farms with label density (low/med/high)  
- Never a public heatmap of partner catch or mortality  
- Overlay official closures (oyster) as **context layer** with authority attribution

### 5.3 Freshness board

Per critical variable: last successful fetch, age vs SLA, fallback state, schema-hash drift, null-rate z-score.

SLA hypotheses:

| Variable class | SLA age at issuance |
| --- | --- |
| NWP / wave forecast | ≤6 h |
| SST satellite / model | ≤24 h |
| In-situ DO/T | ≤6 h (oyster) |
| Partner outcome | ≤48 h |
| Agency landings | display vintage; never pretend real-time |
| Official closure | ≤3 h check during harvest days (oyster context) |

### 5.4 Completeness & QC

Null rates, duplicate `source_record_id`, out-of-range (SST < −2 or > 35 °C, DO < 0, CPUE negative, trap-hauls = 0 with pounds > 0), taxonomy mismatches.

**Do not delete** failing rows; flag `quality_flags[]` and exclude from training via explicit filter logged in the snapshot.

### 5.5 Rights & privacy strip

Count of records by rights class and privacy tier in the latest feature snapshot. Any UNKNOWN in a production snapshot is an automatic **issuance block**.

### 5.6 Outcome-linkage strip

Completion rate of 30-second forms; days-since-last-label per farm/vessel; independent-event count vs minimum GT.

### 5.7 Issuance packet (internal, per forecast)

Must show: source coverage, freshness, missing-input state, quality flags, uncertainty, rights status, last validation date — matching project §14.

---

## 6. Promotion gates (source → production feature)

A source may be **promoted** only if:

1. Legal usability ≥4 for the intended use (train / display / both).  
2. Privacy risk accepted with a written tier and coarsening.  
3. Ecological risk accepted or mitigated.  
4. Relevance ≥4 (feature) or ≥3 (context).  
5. Timeliness ≥3 for the product horizon (or explicitly marked `slow_context_only`).  
6. Traceability ≥4 and provenance ≥4.  
7. Completeness ≥3 on the last 30-day window.  
8. Outcome linkage ≥3 if the source is a **label**; features may be 0 on this dimension.  
9. Resilience ≥3 **or** listed as non-critical.  
10. DATA_RIGHTS register row exists.

Otherwise: `QUARANTINE` or `RESEARCH_ONLY`.

---

## 7. Candidate-specific “better data” tests

These are the **smallest** data-quality experiments that matter before modeling.

### 7.1 Oyster

| Question | Pass hypothesis |
| --- | --- |
| Can we get daily mortality/workability from ≥3 farms? | Outcome linkage ≥4 |
| Are official closures stored as context with URL + time? | Provenance ≥5 on that layer; **relevance to label = 1** (must not leak into y) |
| Is farm SST/DO latency ≤6–12 h? | Timeliness ≥4 |
| Are leases private? | Privacy risk recorded; PUBLIC display coarsened |

**Better data for oyster** is almost entirely **partner logs + as-of environment**, not more global ocean APIs.

### 7.2 Chinook

| Question | Pass hypothesis |
| --- | --- |
| Are zeros and effort on partner trips? | Completeness ≥4 |
| Is RecFIN/CRFS used only as B12/context? | Relevance-as-label = 0 for monthly series |
| Is AIS absent from y and from abundance claims? | Policy test = pass |
| Open/closed season mask at issuance? | Consistency ≥4 |

**Better data** = trip-level catch/no-catch + angler-hours + coarsened cell, not more chlorophyll layers.

### 7.3 Lobster

| Question | Pass hypothesis |
| --- | --- |
| Trap-hauls + soak + pounds present? | Completeness/comparability ≥4 |
| Post-2023 era segmented? | Comparability ≥4 |
| Agency file vintage vs partner same-day? | Timeliness scored **separately** |
| One-TMS-per-trip documented? | Accuracy/resolution capped at 3 until partner multi-cell logs exist |

**Better data** = effort-normalized, era-aware, low-latency logbooks. Dealer pounds without effort is **not** better data.

---

## 8. Metrics to plot over time (after any ingest)

- % sources in APPROVED_*  
- median issuance freshness (hours)  
- label completion rate  
- independent event/trip counts vs minima in validation protocol  
- QC fail rate (not silently falling)  
- privacy incidents (target: 0)  
- number of features with relevance ≥4 (should stay **small**)

Alert if QC fail rate doubles week-over-week or if outcome completion <50% for 14 days.

---

## 9. Implementation notes (do not build yet)

When geospatial engineering implements this:

- Store scores in a table `dq_score(source_id, dimension, as_of, score, evidence_uri, evaluator)`.
- Recompute on each ingest run and each forecast issuance.
- Default all sources `NOT_INGESTED` until rights gate.
- No PII in dashboard screenshots used for fundraising.

v0 implementation after wedge lock: a **spreadsheet or markdown table** filled by agents is sufficient. A live BI dashboard is out of scope until a source is actually ingested.
