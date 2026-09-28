# Privacy and sensitive-location policy — FishAI

**Status:** INTERNAL POLICY DRAFT, NOT LEGAL ADVICE  
**Date:** 2026-09-18  
**HUMAN LEGAL REVIEW REQUIRED** before production, partner onboarding, or public maps.

This policy implements the data-rights register for Ocean Intelligence Builder / FishAI. It is stricter than the most permissive source license: a public-domain coordinate is still `NEVER_PUBLISH` if it is an exact catch, farm KPI, vessel identity, or listed-species holding location.

Companion: `data_rights_register.md`, `source_license_matrix.csv`, `partner_data_rights_template.md`.

---

## 1. Purpose and scope

FishAI may eventually serve farm operators, charter captains, and commercial lobster operators. Those users’ economic survival depends on **not** broadcasting secret bottom, private leases, or vessel tracks. Coastal tribes have sovereignty over their data. Listed Chinook ESUs are protected under the ESA. Shellfish sanitation is a government function.

This policy covers:

- All three unresolved wedges.
- Raw, normalized, feature, model, and product layers.
- Public apps, partner dashboards, marketing, weights, eval sets, and logs.

---

## 2. Privacy tiers

| Tier | Who may see native resolution | Public product | Training | Example |
|---|---|---|---|---|
| `PUBLIC` | Anyone | Native OK if licence allows | OK | CMEMS SST, NWS forecast, GEBCO (with not-for-nav notice) |
| `COARSENED` | Staff + models | Only after spatial/temporal aggregation | OK at coarsened or hashed grain | RecFIN district estimates; zone outlooks |
| `RESTRICTED` | Named staff under NDA / statute | No | Only if licence allows and outputs cannot invert | Mixed IOOS, unpublished HAB, historical AIS internally |
| `PRIVATE` | The contributing partner (and processors bound by DPA) | No microdata | Only if DPA training-use = yes | Farm DO time series; charter catch/no-catch |
| `NEVER_PUBLISH` | Minimize; legal hold only | Never | Never in public or shared weights | Exact set GPS; VMS; tribal TEK; vessel MMSI in UX |

**Default assignment when unsure:** one tier stricter, then queue for counsel.

---

## 3. Non-negotiable defaults

These defaults apply unless **counsel + partner (or nation)** rewrite them in writing.

1. **Exact catch locations are private.** Store, if at all, as `PRIVATE`. Public maps never show them.
2. **Public forecasts use broad zones.** Minimum public grain is defined in §5.
3. **Farm performance is private.** Mortality, growth, condition, yield, and workability scores are `PRIVATE`. Cross-farm models may use them only under DPA and only emit partner-specific or fully aggregated outputs.
4. **Sensitive species are coarsened, delayed, or excluded.** Listed Chinook, other ESA/MMPA taxa, and poaching-relevant aggregations are not published at capture resolution.
5. **No public spot maps.** Includes heatmaps, “hot drift” pins, replay tracks, and “best 10 holes” lists.
6. **Tribal / Indigenous data require sovereignty and consent.** CARE Principles (https://www.gida-global.org/careprinciples). Default `NEVER_PUBLISH`.
7. **AIS / VMS are not abundance.** Vessel identity is `PRIVATE` / `NEVER_PUBLISH`. Do not sell competitor tracking.
8. **Official sanitation, seasons, and licenses stay with the authority.** FishAI may link out; it may not authorize harvest, navigation, or take.

---

## 4. Location coarsening rules

Use WGS84 for exchange. Apply coarsening **at the product boundary**, and also store a public-safe derivative so a leak of the serving DB is not a leak of secret spots.

### 4.1 Minimum public spatial grain (until a wedge is locked)

| Wedge | Public spatial grain | Public temporal grain | Rationale |
|---|---|---|---|
| Oyster WA ops risk | NSSP/DOH **growing area** or larger (bay/subbasin). Not bed/raft/GPS. | ≥ 6–24 h outlook buckets | Beds are competitive and may be tribal or leased. |
| Chinook CA/OR encounter | PFMC/state **management area or statistical block group**, never a drift or wreck. Prefer ≥ ~10 km / H3 res 6–7 or documented equal-area equivalent. | 24–48 h; no live “they’re on it now” | ESA + spot burning. |
| Lobster GOM CPUE | NMFS/ASMFC **statistical area** or 10-minute square **only if** rule-of-3 vessels already met. Never trap GPS. | Next-trip / multi-day, not haul-by-haul | MSA/Maine confidentiality analogue even for partner-derived public layers. |

Internal model features may be finer **only** inside `PRIVATE`/`RESTRICTED` stores with access control. Any export, notebook, eval screenshot, or demo uses the public grain.

### 4.2 Reverse-engineering tests (required before a public map)

A public layer fails if a reasonably skilled user can:

- Recover a partner lease, trap cluster, or charter waypoint within 500 m.
- Isolate one vessel’s pattern by toggling filters.
- Combine FishAI output with public AIS to name a highliner.

Failed tests → coarsen, add noise, delay, or withhold. Document the test in quality/validation (not this folder’s job to run).

### 4.3 What “zone” means in copy

Say “relative outlook for Area X”, never “secret spot” or “GPS pin of the bite”.

---

## 5. Entity and identity rules

| Entity | Public | Partner dashboard | Ban |
|---|---|---|---|
| Vessel name, MMSI, IMO, radio callsign | No | Yes only for **that** owner’s vessels | Competitor tracking, AIS overlay on catch |
| Person name, crew, phone, email | No | Account profile only | Marketing lists from logs |
| Farm / company name | Only if the partner opts in | Yes | Publishing another farm’s KPIs |
| Lease / bed / trap GPS | No | Yes to owner | Sharing across farms/fleets without consent |
| Buyer prices, counts, inventory | No | Yes to that buyer | Cross-buyer price maps |
| Tribal affiliation of a landing | No | Only if the nation is the customer and agrees | Inference of treaty catch |

---

## 6. Sensitive biological and regulatory layers

### 6.1 ESA / MMPA / poaching-sensitive

- Chinook listed ESUs: public product may show **official open/closed season** (link to NMFS/PFMC) and **designated critical habitat** at official grain. Do not show holding pools, creek mouths at spawning time, or real-time “encounter pins”.
- Marine mammals / turtles / birds: exclude fine occurrence from public layers (`NEVER_PUBLISH`).
- If OBIS/GBIF points are finer than policy grain, **re-coarsen or drop** even when the publisher released them.

### 6.2 Shellfish sanitation

- Display WA DOH / NSSP classification only as **quoted official context** with timestamp and link.
- Never color a map “safe to harvest” or “safe to eat” from a FishAI model.
- Farm ops-risk scores (temp, DO, handling window) must be visually and verbally **separated** from sanitation classification.

### 6.3 Harmful algal blooms / biotoxins / pathogens

- Prefer official DOH/FDA closure language.
- Unlicensed partner HAB streams stay `RESTRICTED` until rights are clear.
- Do not provide medical or food-safety advice.

---

## 7. AIS, VMS, and effort proxies

| Source | Allowed internal use (after counsel) | Public product | Abundance claim |
|---|---|---|---|
| GFW | No (NC licence) | No | No |
| Commercial AIS | Only under paid licence | No identity; coarsened traffic maybe | No |
| Marine Cadastre historical AIS | Counsel first (redistribution conflict) | No identity; planning-density only if cleared | No |
| USCG live AIS | No | No | No |
| NOAA VMS | No | No | No |
| Partner GPS | Per DPA | Never | No |

If any vessel layer is ever shown: strip identifiers, aggregate to cells that pass rule-of-3, and label **“vessel traffic, not fish abundance.”**

---

## 8. Indigenous data sovereignty

Follow CARE (Collective Benefit, Authority to Control, Responsibility, Ethics): https://www.gida-global.org/careprinciples

**Rules:**

- Do not scrape tribal sites, harvest calendars, or TEK.
- Do not treat “public” ethnographic papers as consent to productize knowledge.
- Usual and accustomed fishing areas are not a public targeting layer.
- If a nation later partners, they control purpose, retention, revocation, and whether derivatives exist.
- OBIS policy already requires CARE; FishAI must not undo provider coarsening **or** publish finer than provider.

---

## 9. Public product, marketing, and model-release rules

**Public product may contain:** coarsened environmental fields; official links; partner-opt-in testimonials without numbers that reveal KPIs; zone-level relative scores that pass reverse-engineering tests.

**Public product may not contain:** exact spots; live vessel tracks; farm leaderboards; “guaranteed fish”; “approved for harvest”; “safe to navigate”; ESA take advice.

**Open weights / demo notebooks:** strip `PRIVATE`, `RESTRICTED`, `NEVER_PUBLISH`. Treat eval GPS as toxic.

**Logs and support tickets:** may contain locations users paste; retain minimally; do not use for training unless DPA/ToS allows.

---

## 10. Access control and retention (implementation contract for later engineering)

| Store | Access | Retention default (until counsel sets statutory minimums) |
|---|---|---|
| Raw partner GPS / logs | Partner-scoped keys; no global data-science dump | Contractual; default delete/return on revocation |
| Coarsened features | Staff + training jobs | Versioned for audit |
| Public serving tiles | CDN | Only coarsened derivatives |
| Confidential government data | **Do not store** unless a statutory authorization exists | N/A |

On partner revocation: stop training use going forward; delete or return raw; document whether already-trained models must be retrained (see DPA — default **retrain or suppress partner influence** if technically feasible; if not, do not onboard).

---

## 11. Permitted vs prohibited product uses (privacy lens)

**Permitted:** private decision support; coarsened public environmental intelligence; linking to official authorities.

**Prohibited:** legal fishing authorization; navigation/weather-safety advice; shellfish food-safety/harvest authorization; catch guarantee; public spot maps; competitor AIS hunting; unconsented tribal data.

Draft user-facing disclaimer is in `data_rights_register.md` §2.2.

---

## 12. Incident triggers

Treat as a privacy incident and halt the public layer if:

- A map reveals a partner bed, trap line, or drift within policy grain.
- A release includes MMSI, logbook, or tribal data.
- A model output is reasonably read as harvest, navigation, or food-safety authorization.
- Confidential MSA/state statistics were ingested.

Notify counsel and affected partners/nations. Do not “fix forward” by coarsening in place without an incident record.
