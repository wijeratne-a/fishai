# Uncertainty Policy — Ocean Intelligence Builder / FishAI

**Agent:** QUALITY_AND_VALIDATION_AGENT  
**Date:** 2026-09-18  
**Version:** `UNCERTAINTY-2026-09-18-v1`  
**Status:** Policy for all three candidates. No scores issued yet.  
**Rule:** **No opaque single score.** A number without reasons, freshness, and limitations is not a product output.

This policy implements project §15.5 and the 14-field product-output contract (fields 6–9, 11). Validation of the policy is specified in `forecast_scorecard_template.md` §4.

---

## 1. What every prediction must carry

Customer-facing and internal issuances include **all** of:

| Field | Type | Notes |
| --- | --- | --- |
| `confidence_category` | `{high, medium, low}` | Composite, not a model logit |
| `confidence_reasons[]` | short codes + one-line prose | Why this category |
| `uncertainty_interval` **or** `uncertainty_rationale` | numeric interval on the **label scale**, or prose if interval not identifiable | Never invent a fake ± |
| `input_freshness` | per critical input age + overall `fresh / stale / missing_critical` | |
| `observation_density` | `low / medium / high` vs locked geography | |
| `missing_data_state` | list of missing critical inputs | Empty list only if none missing |
| `extrapolation_flag` | boolean + which dimension (space, season, climate, management era, vessel/farm) | |
| `known_limitations[]` | including contract exclusions | |
| `model_or_baseline_version` | id | |
| `issued_at` | UTC | |

Optional internal: conformal interval, quantile interval, Brier-reliability bucket.

**Forbidden:** a lone “72 / 100 AI score,” a traffic light with no reasons, or “high confidence” when critical inputs are missing.

---

## 2. Confidence category is a rule, not a vibe

Category is computed from **observable issuance facts**. Hypothesis rule (lock after first retro; do not neural-net this until the table is calibrated):

### 2.1 Inputs to the rule

| Code | High contribution | Medium | Low |
| --- | --- | --- | --- |
| FRESH | all critical inputs within SLA (`data_quality_dashboard_spec.md` §5.3) | one non-critical stale | any **critical** missing or stale |
| DENSITY | local GT density high (see §2.2) | medium | low or empty neighborhood |
| IN_DOMAIN | covariates inside training 5–95% envelope; same season; same management era | one mild excursion | novel heatwave/hypoxia/closure regime, new basin, new gauge size, closed→open salmon year shock |
| SOURCE_HEALTH | primary sources up | fallback active | Tier C only / outage |
| CALIBRATION_OK | latest prospective/time-forward BSS>0 and ECE within hypothesis band **in this slice** | overall OK, slice unknown | last window failed calibration or never evaluated |
| LABEL_SUPPORT | recent local verified outcomes inside horizon×2 | adequate environment, sparse biology | no local outcomes this season |

**Category rule (hypothesis):**

- **High** if FRESH=high AND DENSITY≠low AND IN_DOMAIN=high AND SOURCE_HEALTH≠low AND CALIBRATION_OK≠low AND LABEL_SUPPORT≠low.
- **Low** if any of: FRESH=low, IN_DOMAIN=low, SOURCE_HEALTH=low, CALIBRATION_OK=low, or LABEL_SUPPORT=low.
- **Medium** otherwise.

If rules conflict, **take the worse category**. Do not average.

### 2.2 Density definitions (hypotheses)

| Candidate | High | Medium | Low |
| --- | --- | --- | --- |
| A Oyster | This farm has labels on ≥80% of last 28 days; ≥1 neighboring basin farm reporting | This farm ≥50% last 28 days | Farm new or <50% completion |
| B Chinook | ≥15 partner trips in this district in last 14 **open** days | 5–14 | <5 or season just opened |
| C Lobster | ≥20 trips in this zone in last 14 days (partner or timely lawful feed) | 5–19 | <5 |

These cutoffs will be wrong; they exist so v0 is auditable.

---

## 3. Intervals vs rationale

| Product | Prefer | If not identifiable |
| --- | --- | --- |
| Oyster risk | Probability with reliability diagram; optional 72h event probability interval from a calibrated Bernoulli or conformal | “Unquantified: sparse events; category only” |
| Chinook encounter | Probability + ECE; rank band as **lower / middle / upper tercile** of comparable **open** days (not “top 20%”) | Rank without probability, labeled as rank-only |
| Lobster CPUE | Quantile interval (10–90 or 20–80) on soak-adj CPUE | “Direction/rank only; pounds not calibrated” |

**Never** attach a ±% that was not produced by a declared method (quantile regression, conformal, historical residual scale by slice). If the method was not run, use `uncertainty_rationale` instead of fake numbers.

**Coverage obligation:** if you print an 80% interval, score coverage. If coverage is outside 0.70–0.90 in the current slice, **downgrade to Low** and stop printing that interval until recalibrated.

---

## 4. High / medium / low — user-visible meaning

Use this copy (tune with PRODUCT; do not contradict):

### High

Recent local verified outcomes, stable environmental inputs, model/baseline operating inside trained conditions, sources healthy, last validation slice acceptable.

**User meaning:** “Conditions look like cases we have scored before.”  
**Does not mean:** guarantee of catch, survival, or legal harvest.

### Medium

Adequate environment but sparse recent biological/operational observations, **or** mild domain excursion, **or** fallback source in use.

**User meaning:** “Treat as a watch, not a sure bet.”

### Low

Missing key data, novel/extrapolated conditions, limited historical examples, source outage, failed recent calibration, or season/management shock.

**User meaning:** “Insufficient to change a high-cost action.” Prefer **suppress recommendation** and show context only (official forecasts, closures, last observed CPUE).

**Low + expensive action:** do not recommend the action. Showing data is allowed; commanding “go/don’t go” is not.

---

## 5. Suppression policy

Issue a **context-only brief** (no model probability, no rank list) when:

1. Confidence is Low **and** a critical input is missing.  
2. Legal/privacy/ecological gate fails.  
3. Universe is empty (Chinook season closed; farm unstocked; lobster trip with 0 hauls).  
4. Red-team blocker is open for this claim type.  
5. Official authority contradicts a dangerous inference (e.g. area closed to harvest — oyster brief must show closure as authority, not “but our stress is low so maybe harvest”).

Suppressed issuances still store `forecast_id` with `suppressed=true` for completion metrics.

---

## 6. Candidate-specific limitations (always eligible for `known_limitations[]`)

### A — Oyster

- Not a food-safety determination. Verify WA DOH / NSSP status.  
- Not legal authorization to harvest.  
- Sensor-based stress ≠ mortality.  
- Lead time is for environmental onset, not sudden gear failure.  
- Neighboring leases are not independent; one basin can be all High together without new information.

### B — Chinook

- Not a catch guarantee; not abundance; not a count of fish in the ocean.  
- Not navigation or weather-safety advice; link official NWS/USCG.  
- Not a license or bag-limit check; user must verify CDFW/ODFW/PFMC.  
- Unfished cells are unknown, not empty.  
- AIS/vessel density is not fish.  
- Year-to-year ocean abundance can dominate 48h skill; High is relative to **this season’s** observations when density is high, still not a run-size forecast.

### C — Lobster

- CPUE ≠ stock abundance.  
- Not a quota or trap-cap recommendation.  
- One 10-minute square per official trip is a location error source.  
- Gauge/vent regulation changes break comparability.  
- Other vessels’ official reports may be weeks old.  
- High-liner history does not transfer to a new operator.

---

## 7. Validation of uncertainty (required)

The confidence system **fails** (even if AUROC is fine) if any of:

1. High-confidence issuances are **not** more accurate/calibrated than Low on a pre-registered window.  
2. >95% of issuances are High (the category carries no information).  
3. Extrapolation_flag=false on clearly out-of-year heatwave / new gauge era / new district.  
4. Intervals are printed with coverage <0.60 or >0.98 for an “80%” interval without disclosure.  
5. Customer text contradicts `missing_data_state`.

Remediation: recode the rule table; do not add an uncalibrated “confidence neural net.”

---

## 8. Internal vs external

| Audience | May see |
| --- | --- |
| Customer | Category, reasons in plain language, interval or rationale, freshness, missing inputs, limitations, official links |
| Internal | Full rule trace, slice ECE, source outage IDs, partner density (not publishable) |
| Public marketing | **Nothing** that implies a validated skill number until prospective GO |

---

## 9. Relation to better forecast

A forecast that is sharper but uncalibrated, or that says High during outages, is **not better**. Uncertainty performance is a **co-equal** go/no-go block with skill vs baseline (`go_no_go_scorecard.md` §4).
