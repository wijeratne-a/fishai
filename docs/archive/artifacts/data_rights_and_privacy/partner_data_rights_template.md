# Partner data-rights agreement template (draft)

**Status:** NEGOTIATION TEMPLATE FOR COUNSEL — NOT AN EXECUTED CONTRACT  
**Date:** 2026-09-18  
**HUMAN LEGAL REVIEW REQUIRED.** This is a term sheet in plain language for charter, farm, and buyer/processor partners. It is not legal advice and must be converted by qualified counsel into a Data Processing / Data Sharing Agreement appropriate to WA, CA, OR, ME, and federal law (including MSA confidentiality if any government data are involved, ESA, and CARE if a tribal nation is the partner).

Related: `data_rights_register.md`, `privacy_and_sensitive_location_policy.md`.

Replace `[BRACKETS]`. Do not use this text as-is with a partner.

---

## A. Parties and purpose

- **Company:** `[LEGAL NAME]` operating the FishAI / Ocean Intelligence Builder product (“Company”).
- **Partner:** `[LEGAL NAME]`, type: `[charter / CPFV operator | oyster farm | buyer/processor | other]`.
- **Purpose (narrow):** provide Partner-only decision support for `[72h farm operational stress | 24–48h relative Chinook encounter | next-trip lobster CPUE / effort allocation]`.
- **Not the purpose:** fishing authorization, navigation or weather-safety service, shellfish sanitation / harvest authorization, catch guarantee, or publication of Partner’s secret locations or performance.

Company will not treat Partner data as public open data.

---

## B. Data covered

Check all that apply. Anything not checked is out of scope until an amendment.

### B1. Charter / CPFV

- [ ] Trip-level catch / no-catch / released counts by species
- [ ] Effort (hours, anglers, lines, area fished)
- [ ] Operator-owned GPS tracks or waypoints
- [ ] Vessel identifiers (name, USCG number, MMSI) for account binding only
- [ ] Photos / video (default **excluded** unless checked)
- [ ] Customer names or passenger manifests (default **excluded** — do not collect)

**Charter-specific legal note (informational):** California Fish and Game Code § 8022 makes **agency-filed** CPFV logs confidential. This agreement covers only data Partner **lawfully possesses and is free to share** (e.g., Partner’s own operational copy). It does not authorize Company to pull confidential records from CDFW, ODFW, WDFW, RecFIN confidential warehouses, or NMFS.

### B2. Farm (oyster / shellfish)

- [ ] In situ sensors (temp, salinity, DO, pH, turbidity, chlorophyll, waves)
- [ ] Husbandry logs (planting, tumbling, harvest **timing**, labor windows)
- [ ] Biological outcomes (mortality, growth, condition) — **PRIVATE**
- [ ] Lease / bed polygons
- [ ] Equipment / staff identifiers (default minimize)

**Farm-specific legal note:** Growing-area classification and biotoxin closures remain WA DOH / NSSP / FDA authority. Partner data will not be used to issue a harvest or food-safety authorization.

### B3. Buyer / processor

- [ ] Lot / ticket counts and grades from **Partner’s** purchases
- [ ] Prices (default **internal only**, never published)
- [ ] Inventory and logistics timestamps
- [ ] Supplier vessel or farm identity (default **RESTRICTED**, never public)

**Buyer-specific legal note:** Sharing prices or allocations across competing buyers may raise antitrust issues. Default is **single-Partner silo**. Any multi-buyer benchmark requires counsel and aggregation that cannot identify a firm (`rule of 3+` at minimum, often stricter).

---

## C. Licence Company receives

Partner grants Company a **limited, non-exclusive, non-transferable, revocable** licence to:

1. Store and process Covered Data to provide the Purpose to Partner.
2. Create derived features and model outputs for Partner’s account.
3. Use Covered Data for **quality control, security, and billing**.

Company does **not** receive ownership of Covered Data. Partner retains all rights not expressly granted.

**No sublicence** except to subprocessors listed in Annex 2 who are bound to this standard or stricter.

---

## D. Training-use (must be an explicit choice)

Pick **one**. Silence = **(1)**.

1. **Account-only (default).** Covered Data may not be used to train models that serve other customers.
2. **Cohort training, siloed weights.** Covered Data may train a model that also uses other partners’ data only if outputs cannot reconstruct Partner microdata and Partner may revoke (Section F).
3. **Broad training.** Covered Data may train Company foundation models, including future products listed in Annex 3. Requires extra consideration and counsel.

Even under (2) or (3):

- Exact locations remain subject to the privacy policy (`PRIVATE` / `NEVER_PUBLISH`).
- CC BY-NC, GFW, confidential government, and tribal data are never mixed in via this DPA.
- Published scientific papers using Partner data need **separate written consent**.

---

## E. Commercial derivatives

Pick all that apply. Silence = Partner dashboard only.

- [ ] Partner-only scores and alerts
- [ ] Anonymized / coarsened contribution to a **paid** zone outlook (must pass reverse-engineering tests)
- [ ] Resale of Partner microdata to third parties — **default FORBIDDEN**
- [ ] Inclusion in open-weight models or public eval sets — **default FORBIDDEN**
- [ ] Use in Company fundraising demos — only coarsened synthetic or Partner-approved screenshots

Revenue share (optional, commercial not legal): `[NONE / % / per-seat]`. Does not buy broader rights than this DPA.

---

## F. Consent, revocation, and deletion

- **Consent:** A named Partner signatory with authority to bind the organization. Click-wrap is insufficient for GPS logs without documented authority.
- **Revocation:** Partner may revoke on `[30]` days’ notice (immediately if Company breaches privacy or purpose limits).
- **After revocation Company will:**
  1. Stop ingest and new training use.
  2. Disable Partner-identifying features in production.
  3. Delete or return **raw** Covered Data within `[45]` days, except narrowly kept legal/audit logs.
  4. If training-use was (2) or (3), `[retrain without Partner data | isolate and suppress Partner influence | destroy affected checkpoints]` as specified in Annex 4. **If Company cannot technically unwind, it must not select (2) or (3).**
- **Survival:** confidentiality, non-publication of microdata, and indemnity survive revocation.

---

## G. Aggregation and public output

Company **will not** publish:

- Exact catch, bed, raft, or trap locations
- Vessel identity or tracks
- Farm KPIs attributable to Partner
- Buyer prices

Any multi-partner public statistic must meet **at least** three independent Partners, three vessels (if vessel-based), and three landing points (if landing-based), **and** pass the reverse-engineering tests in the privacy policy. Partner may require a higher bar in Annex 1.

Official government maps (e.g., WA DOH growing areas, PFMC season notices) are not Partner data; Company still will not present them as Company’s harvest or fishing authorization.

---

## H. Retention

| Class | Default retention |
|---|---|
| Raw GPS / log rows | `[24 months]` or earlier deletion on revocation |
| Derived features | `[36 months]` for audit of scores delivered |
| Model checkpoints containing Partner influence | As Annex 4 |
| Support tickets | `[18 months]`, scrub locations when possible |
| Legal hold | As required by law, minimized |

Retention is **not** permission to broaden purpose.

---

## I. Security and subprocessors

- Encryption in transit and at rest; access logged; least privilege.
- No storage in consumer AI tools or public Git.
- Annex 2 subprocessors; 30-day notice for material additions; Partner may object for reasonable privacy grounds.
- Breach notice to Partner without undue delay, not later than `[72 hours]` after Company confirms.

---

## J. Representations

Partner represents it has the right to share Covered Data (owner, or all necessary consents from vessel owners, landlords, and workers as applicable) and that sharing does not violate MSA/state confidentiality (Partner is not handing Company another person’s confidential government submission), crew privacy, or a tribal prohibition.

Company represents it will not use Covered Data to provide legal fishing, navigation, weather-safety, or shellfish food-safety authorization, and will not guarantee catch.

---

## K. Sensitive species, ESA, and Indigenous data

- If Covered Data include ESA-listed Chinook or other protected taxa, Company will coarsen or exclude them from any non-Partner view.
- If Partner is a tribal nation or the data are Indigenous, **CARE Principles** apply and this template is replaced by a nation-drafted protocol. Company does not assume consent from this form.

---

## L. Liability (placeholder for counsel)

Caps, disclaimers of weather/harvest/catch, and insurance limits to be drafted by counsel. Company data are “as is” decision support. Partner remains responsible for following official agencies (NMFS, USCG, state, tribal, WA DOH/FDA NSSP).

---

## M. Signature block (placeholder)

Partner: name, title, date, authority representation  
Company: name, title, date  
Annexes: (1) data inventory and grain, (2) subprocessors, (3) future products if any, (4) unwind/retrain procedure

---

## N. Role-specific checklist (attach to each deal)

| Topic | Charter | Farm | Buyer/processor |
|---|---|---|---|
| Ground-truth needed | Effort-normalized catch/no-catch | Mortality/growth/workability + sensors | Landings quality/timing — not a public CPUE map |
| Highest privacy harm | Spot maps, passenger PII | Lease GPS, mortality, tribal beds | Prices, supplier identity |
| Government-file trap | Do not pull CDFW logs | Do not scrape DOH viewer harvest sites as “open API” | Do not ingest confidential dealer tickets from ACCSP/PacFIN |
| Public derivative | Zone encounter **relative** rank only | Bay-scale env outlook, never farm KPI | Regional ex-vessel index only if 3+ firms and counsel |
| Revocation pain | Retrain encounter model | Retrain ops-risk model | Remove price features |
| Training-use default | (1) account-only until 3+ charters sign (2) | (1) until 3+ farms | (1) always unless antitrust memo |

---

## O. What this template refuses

- Bypass of licences, paywalls, TOS, or scraping.
- Permission to use GFW, VMS, or confidential MSA statistics.
- A catch guarantee or sanitation stamp.
- Open publication of Partner maps.
