# Outcome Capture Spec — 30-second loop

**Date:** 2026-09-18  
**Purpose:** Turn a brief into **permissioned, private, temporally honest labels** without asking operators for a second job.

Interviews and pilots have **not** run. Completeness targets below are **design gates**, not observed rates.

---

## 1. Why a user would log (the actual product question)

People will not “contribute data for science.” They will log if **at least two** of these are true:

| Motive | Mechanic |
|---|---|
| **Selfish memory** | The weekly note is *their* Elevated-vs-hard-work chart. Without logs it is empty. |
| **Better next brief** | Copy: “If you tell us whether Saturday was actually hard, Tuesday’s brief uses it. If you don’t, we keep using a station 3 km away.” |
| **Money** | Design partner: briefs pause if weekly completeness < 60%. Paid: **$50–$100 bill credit** at ≥80%. |
| **Cover** | A private timestamped ops record for insurance, crew disputes, or “why we didn’t tumble.” Not a legal product; still useful. |
| **Respect** | 30 seconds, magic link, no new password, works on a phone in the truck, can skip photo. |
| **Fairness** | We never publish their answers. Neighbors cannot buy their mortality. |

**Will not work:** gamification, public leaderboards, “help train AI,” extra desktop software, logging exact lat/lon as a required field.

If 8-week completeness is <40% after incentives, the capture design failed — do not “nudge harder”; shorten the form or kill the wedge.

---

## 2. Channel

| Channel | Use |
|---|---|
| Magic link in every email/PDF/WhatsApp | Primary |
| Reply “OK / HARD / ABORT” to the brief email | Backup for no-browser |
| QR on the PDF | Crew on the beach |
| Weekly reminder only if 0 logs in 5 days | Once, not daily nag |

No account creation in v0. Token binds to `farm_id + lease_id + window_id`. Tokens expire in 14 days; late logs are marked `late=true` (usable with caution, not for same-day calibration theater).

---

## 3. Schema (oyster recommended)

Keep v0 **narrow**. Do not collect a full farm ERP.

### 3.1 Required (target 30s)

| Field | Type | Notes |
|---|---|---|
| `brief_id` | string | Hidden, from token |
| `lease_id` | enum | Hidden or confirm-if-mismatch |
| `window_start` / `window_end` | datetime UTC | Hidden |
| `worked_lease` | yes / no_wx_ops / no_other | Q1 |
| `workability` | ok / hard / aborted / na | Q2 |
| `handling_done` | yes / no / na | Q3 tumbling/sort/harvest-handling **ops**, not legal harvest |
| `flags[]` | subset of gaping, mortality_above_normal, gear, freshwater_feel, low_do_feel, none | Q4 |
| `brief_changed_plan` | yes / no / unsure | Decision-value, not biology |
| `submitted_at` | datetime | Server |
| `late` | bool | Server |

### 3.2 Optional

| Field | Type | Notes |
|---|---|---|
| `photo` | image | PRIVATE; EXIF stripped; no public use |
| `note` | ≤140 chars | Free text; do not encourage coordinates |
| `crew_hours` | number | Only if they want economics |
| `sensor_export_ref` | string | If they dropped a file that week |

### 3.3 Explicitly do not collect in v0

- Exact GPS of productive patches
- Customer names / buyer prices
- Full mortality counts unless they volunteer
- Vibrio sample results as a **label we predict** (food-safety firewall)
- Other farms’ conditions

### 3.4 Chinook variant (if ever)

Required: date, coarsened cell (≥10 km) **or** “usual range,” hours fished, Chinook catch **count or none**, anglers, legal-open confirmation checkbox. Optional: size bucket, other species. **Never** exact waypoint as a required field. Default privacy: exact spots PRIVATE.

### 3.5 Lobster variant (if ever)

Required: trip date, zone, traps hauled, pounds kept, soak hours (approx OK). Optional: bait type, bait cost, discarded/v-notch counts if they already record them. **Never** trap GPS in a shared or default-on field. Coordinates = NEVER_PUBLISH if captured on-device for their private logbook.

---

## 4. Label policy (for validation agent)

| Outcome | May train / evaluate | Must not |
|---|---|---|
| Workability, handling done, gear flag | Yes — ops-stress target | Interpret as mortality probability without more data |
| Gaping / mortality_above_normal | Yes as **weak** farm observation (Tier 2) | Treat as official pathology |
| WDOH closure | Context feature or **exclusion** | Food-safety **label** for the ops model |
| `brief_changed_plan` | Decision-value metric | Biological truth |
| Photo | Human QA / later research with consent | Scraped into public models |

Truth hierarchy: farm observation is **Tier 2 operational**, not Tier 1 lab measurement, unless a lab result is separately consented.

---

## 5. Timing and leakage

- Form is tied to a **brief_id** issued before the window.
- Users may log after the window; `late` flag on.
- Assemblers must **not** peek at today’s outcomes before issuing today’s brief (even in a manual MVP). Split roles if needed.
- Replay: store token issue time vs submit time.

---

## 6. Completeness and quality

| Metric | 30-day design-partner gate | 90-day paid gate |
|---|---|---|
| Work-day log rate | ≥60% | ≥70% |
| Duplicate/contradictory | Spot-check | <10% unresolved |
| Photo rate | Unscored | Unscored |
| `brief_changed_plan` filled | ≥50% of logs | ≥60% |

Incentives: see `pricing_hypothesis.md`. Pause free briefs if completeness collapses — otherwise we train on non-response bias and call it a model.

---

## 7. Consent UX (must be visible)

On the form footer, always:

> Private to your farm. Not a public map. Not sold to neighbors. You can revoke. This is not a food-safety report to WDOH — if you need to notify the State, use official channels.

First-time token: tap-through of DUA version hash.

---

## 8. Error / feedback mechanism (contract field 14)

Same form, `mode=error` or email reply `WRONG`.

Fields: category (wrong lease, stale, sounds like food-safety, unsafe, other), free text, optional screenshot.

SLA: acknowledgment next business day; High-severity (food-safety bleed, location leak) **same day** if received during operating hours.

---

## 9. Retention

| Data | Retention (hypothesis; counsel + rights agent) |
|---|---|
| Outcomes + brief_id | Duration of contract + 24 months for validation, unless revocation |
| Photos | 12 months then delete unless they opt to keep in private logbook |
| Magic-link tokens | 14 days |
| Error tickets | 24 months |

Export: CSV of their rows within 14 days of request. Delete: follow DUA; we may keep **de-identified** brief-level analytics if the DUA allows — default **no** for n<5 farms (re-identification).

---

## 10. Implementation note (least build)

v0: Tally / Google Form / Typeform **only if** (a) not training public models on the sheet, (b) sharing is off, (c) we copy to a private store daily, (d) no third-party sells the responses. Prefer a single private form backend as soon as a partner asks “who can see this.”

Do not build a contributor dashboard in week 1. The **weekly calibration email** is the dashboard.
