# Partner Data Program

**Date:** 2026-09-18  
**Status:** Design. No partners signed. DUAs require HUMAN LEGAL REVIEW.  
**Goal:** A permissioned network that improves briefs **for contributors** without turning their living into a public map.

Applies to all three candidate wedges. **v0 emphasis: shellfish farm program** (recommended). Charter and buyer programs are specified so we do not paint them on later as an afterthought.

---

## 0. Defaults that do not wait for counsel’s prose

| Default | Rule |
|---|---|
| Exact productive spots (charter waypoints, lobster traps, dense bed patches) | **PRIVATE / NEVER_PUBLISH** |
| Farm performance (mortality, yield, labor) | **PRIVATE** |
| Buyer prices, volumes, supplier names | **PRIVATE** |
| Shared research file | Spatially **coarsened**, temporally **delayed**, **opt-in**, written method |
| Public heatmaps of catch or yield | **Forbidden** |
| GFW / AIS as abundance | **Forbidden** |
| Hardware mandate | **Forbidden** until partner-first ladder fails |

---

## 1. Shellfish farm partner program (v0)

### They receive

- Lease-level 72h ops-risk brief (email + PDF)
- Historical comparison **of their own logs vs our statuses**
- Monitoring / action **options** checklist (not commands)
- Private operational record (outcomes)
- Optional aggregated benchmark **only** if they sign a separate method (off by default)
- Data-contribution credits (`pricing_hypothesis.md`)

### They may contribute

Farm zone (private code), stocking/seed (optional), growth (optional), mortality (flag or count), harvest **ops** (not legal status), closures **they experienced** (context), water tests (if they choose), sensors, observations, interventions, gear/density, yield (optional), fouling.

### Privacy

- Farm data private
- No public disclosure of performance
- Aggregation/benchmarking requires explicit agreement
- Location: strict access control; customer email uses **lease names they chose**, not a public GIS dump

### Why they would bother

The brief is worse than NANOOS unless it is **their** lease. The only way to get that is sensors they already have **or** 30-second outcomes. Credits + private weekly calibration are the incentive. Ego/science is not.

---

## 2. Charter captain / fleet partner program

### They receive

- Private trip logbook
- Private historical analytics
- Forecast tailored to **coarsened operating range** (≥10 km cells)
- Structured catch/effort capture
- Post-trip summary
- Optional aggregated regional benchmark (opt-in)
- Credits / lower in-season price for completeness

### They may contribute

Species, catch/no-catch, count/size bucket, effort, gear/method, time, **general or exact location according to privacy settings**, depth, environment, optional trip cost/fuel, bycatch/absence where permitted.

### Privacy

- Exact productive locations private
- Shared data coarsened, aggregated, delayed, opt-in
- Contributor data **never** becomes a public spot map
- Use governed by agreement

### Why they would bother

“BiteTime” apps already exist. They log if (1) the logbook replaces a paper notebook, (2) the next 48h brief is visibly using **their** no-catch days, (3) we cannot leak spots to other captains in the harbor. If we cannot guarantee (3), do not run this program.

---

## 3. Seafood buyer / processor partner program

Not the 30-day wedge. Specify now so oyster farms are not later asked to expose buyer terms.

### They receive

- Supply-disruption **context** (env + official closures as links)
- Regional outlook at **coarse** geography
- Availability risk (if we ever have rights to it)
- Sourcing **options**, not orders
- Historical **their** supplier/region performance — never another customer’s

### They may contribute

Fulfillment, availability, price, quality, rejection, delays, substitution, order volume — aggregated/private.

### Privacy

- Terms, volume, prices, supplier identities confidential
- No cross-customer exposure
- Aggregation requires approved methodology

**Relevance to oyster v0:** none, except a farm might *also* be a dealer. Treat dealer records as farm-private unless a buyer contract exists.

---

## 4. Required partner-data features (build list)

| Feature | v0 (8-week pilot) | v1 (paid) |
|---|---|---|
| Consent capture | Signature / email accept of DUA version hash | Same + re-consent on version bump |
| Data-use agreement version | Yes | Yes |
| Access tier selection | PRIVATE default | PRIVATE / COARSENED opt-in |
| Privacy preference | Farm-level | Lease-level if needed |
| Revocation process | Email to operator; stop new use in 5 business days | Documented SLA |
| Retention policy | See outcome spec | Counsel-approved |
| Audit trail | Brief_id ↔ outcome_id log | Immutable log |
| Contributor dashboard | **Weekly email is enough** | Simple private page if asked |
| Export/delete | CSV on request | Self-serve |
| 30-second outcome flow | Yes | Yes |
| Data-quality feedback | “we marked this late / contradictory” | Same |
| Reporting incentive | Completeness gate + credit | Same |

---

## 5. Partner-first data ladder (no hardware heroics)

Before proposing proprietary sensors:

1. Open/public (NANOOS, NWS, tides)
2. Agency (WDOH as **context**, NERRS)
3. Partner exports (existing loggers, spreadsheets)
4. Existing boat/farm sensors
5. Manual structured observations (this program)
6. Low-cost mobile capture (photo)
7. Logbook integrations (later: BlueTrace, Esri, Excel)
8. Licensed data
9. Proprietary hardware **only** with a separate approval memo (payback, install burden, privacy, certification, etc.)

---

## 6. Access tiers (align with rights agent)

| Tier | Meaning |
|---|---|
| PRIVATE | Only that farm/vessel and FishAI operators under DUA |
| COARSENED | ≥ agreed cell size, delayed, for internal model only |
| APPROVED_PARTNER_CONSENT | Named study / association file |
| NEVER_PUBLISH | Coordinates, trap-level, precise beds |
| RESTRICTED | Cannot leave jurisdiction / cannot train public models |

Default new partner: **PRIVATE + NEVER_PUBLISH coordinates**.

---

## 7. Outreach channels (plan, not a fake pipeline)

| Wedge | Where to find design partners |
|---|---|
| Oyster | PCSGA; Washington Sea Grant; NANOOS user list (public program); known farms that already host WDOH loggers (Calm Cove, Chelsea Farms, Taylor, etc. are **publicly named as sensor hosts** — that is **not** consent to be our customer; still need a real ask) |
| Chinook | Newport / Charleston / Fort Bragg / Bodega harbors; charter associations; **only in open season** |
| Lobster | Zone councils, co-ops, GMRI networks — slower, relationship-heavy |

**Do not** cold-email a sensor-host list as if they are already partners.

---

## 8. Incentives (summary)

- Utility: private calibration
- Price: credits / free pilot
- Control: revocation + no public map
- Fairness: we eat our own cooking — if we cannot QA a brief, they do not owe us logs that day

Cash for data (paying $X per log) is a last resort; it buys biased, rushed taps. Prefer **product-gated** incentives.

---

## 9. Association / co-op deals

A PCSGA or co-op seat can be discounted if members opt into a **delayed coarsened** file for validation. Individual PRIVATE always available. Never make “share with the association” the only paid tier.

---

## 10. Red lines

- No scraping partner portals
- No training a public demo on a farm’s mortality
- No “anonymized” maps that re-identify a single lease in a small bay
- No using AIS to infer another lobster’s CPUE
- No presenting partner quotes as traction without a signed logo release
