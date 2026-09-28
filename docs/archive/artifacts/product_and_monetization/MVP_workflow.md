# MVP Workflow — Oyster 72h Ops-Risk Brief (canonical)

**Canonical file.** `product_MVP_workflow.md` points here.  
**Date:** 2026-09-18  
**Wedge status:** UNRESOLVED; this workflow is specified for the **recommended** candidate (W1 Willapa oyster 72h ops-stress) and sketched for the other two.

**Claims halt:** no customer-facing **model** score. After founder lock, v0 is a **manual** Category D brief. Sample geography is **Willapa**, never Totten / Vp Category 3. SST is not oyster body temperature.

**Minimum lovable output:** one valuable answer in **<60 seconds**.  
**Chosen format:** daily **email + 1-page PDF**. Optional WhatsApp/SMS **only when status is Elevated or High**, or when data are too stale to issue a brief.

Do not build a multi-tab terminal.

---

## 1. Who uses this

**Primary user:** Washington oyster farm manager (or owner-operator) who:

- Plans tomorrow’s tide work the afternoon/evening before
- Already glances at NANOOS, weather, tides, and WDOH
- Manages 1–N leases; labor and boat time are scarce
- Will not install a new app to get a risk note

**Secondary users (same farm, read-only):** crew lead, hatchery/farm liaison. They do not get a different product in v0.

**Not a user in v0:** recreational harvesters, restaurants, insurers, the general public.

---

## 2. Job to be done

> “Before I set the crew list and the skiff plan, tell me whether the next 72 hours look like a **typical**, **elevated**, or **high** operational-stress window **for this lease** — and what that does *not* authorize me to skip.”

Success is:

- They open the email
- They understand status + why + confidence in one screen
- They pick an **option** or keep the current plan
- They tap the 30-second outcome form after the work window
- They still check WDOH themselves

---

## 3. Onboarding (20–30 minutes, once)

No app store. A 30-minute call + a one-page farm card.

### 3.1 Farm card (we fill this; they confirm)

| Field | Why |
|---|---|
| Farm legal name / contact | Delivery + DUA |
| Growing area name (WDOH) | Context link only |
| 1–3 named leases (private codes, not public maps) | Unit of forecast |
| Culture method (on-bottom, longline, flip-bag, tumbled, FLUPSY, etc.) | Stress pathways differ |
| Typical tide work windows | Workability |
| “Do not work if…” rules of thumb they already use | Baseline we must beat |
| On-lease sensors? Export format? | Partner-first data |
| Delivery: email required; WhatsApp optional | Channel |
| Privacy: exact coordinates NEVER in customer email body beyond their own lease name | Default |

### 3.2 Consent and rights (same call)

- Data-use agreement version ID
- Access tier: **PRIVATE** farm data
- Outcome logging is part of the pilot, not optional “if you feel like it”
- Revocation, retention, export described in `partner_data_program.md`
- We bookmark WDOH; we do not scrape behind logins

### 3.3 First brief

Within 2 business days of onboarding: one **manual** brief using public sources + farm card, clearly labeled **analyst-assembled, unvalidated for your lease**.

---

## 4. Daily operating loop (oyster)

```
16:00–16:30 local (PDT/PST)
   Pull as-of snapshots (NANOOS, NWS, tides, waves, rainfall)
   Check WDOH closure page as CONTEXT (do not use as food-safety label)
   Compute or analyst-assign OSI-72 + confidence
   Render 14-field brief (email HTML + PDF)
   If status Elevated/High OR freshness fail → optional WhatsApp ping
   Human QA gate (pilot): 5-minute read for unsafe wording / food-safety bleed

Evening
   Manager reads in <60s, forwards PDF to crew lead if needed

Next 1–3 tide windows
   Work happens or is skipped

After work window (or next morning)
   30-second outcome form
   Optional “WRONG” reply

Weekly (Monday)
   One-paragraph calibration note: “last week we said Elevated 3 times; you reported hard-work 2, abort 0, mortality flag 1”
```

**Latency target:** brief in inbox by 16:30 local; data as-of stamps visible. If a Tier A source is down, issue a **degraded brief** or a **cannot-issue** notice — never a silent stale “green.”

---

## 5. <60-second read path

Email subject is the product:

```
[FishAI] Willapa Zone B · ELEVATED ops-stress · 72h · Low conf · NOT harvest/food-safety
```

Limitations on the same screen: Category D indicator only; not harvest authorization; air×tide×solar not SST-as-body-temperature; tercile rank not a probability; official WA DOH module is separate.

Above the fold (mobile email):

1. Status chip (Typical / Elevated / High / Cannot issue)
2. Horizon end time
3. One-sentence meaning
4. One-sentence **NOT** meaning
5. Confidence
6. Top 2 drivers (**air × emersion** and **wind/wave** first; water T/DO/S supporting only)
7. 2–4 action OPTIONS
8. Buttons: **Log outcome (30s)** · **Report error** · **WDOH closures**

PDF is the archive + crew printout. Same 14 fields, no extra dashboards.

---

## 6. Status vocabulary (locked)

| Status | Customer meaning | We may not say |
|---|---|---|
| Typical | Conditions rank near the middle of comparable historical windows | “Safe to harvest” |
| Elevated | Higher-than-usual operational stress / disruption likelihood | “Harvest is illegal” / “Oysters are unsafe” |
| High | Among the more extreme comparable windows; still not a guarantee of loss | “Expect X% mortality” |
| Cannot issue | Data too stale, rights blocked, or official source conflict unresolved | A guessed status |

Never use: safe, approved, closed, open, legal, illegal, toxic, Vibrio-positive, guaranteed, abundant.

---

## 7. Human QA gate (required in pilot)

A person (founder or trained operator) checks, before send:

- [ ] 14 fields present
- [ ] No harvest-legal language
- [ ] WDOH link present
- [ ] Options not commands
- [ ] Confidence not overstated
- [ ] Lease name matches farm card
- [ ] Freshness stamps present
- [ ] If Cannot issue, we sent that — we did not recycle yesterday’s green

After 30 clean sends, QA can become sample-based (every Nth + all High).

---

## 8. Error and incident workflow

| Event | Response |
|---|---|
| User taps Report error | Human ack next business day; log in issues register |
| User says we contradicted WDOH | **Stop that claim class immediately**; WDOH wins; red-team |
| Stale data > freshness SLA | Cannot-issue or degraded banner |
| Sensitive location in an outbound | Treat as incident; purge; notify partner per DUA |
| User asks for “is it safe to eat / harvest” | Scripted refusal + WDOH links; do not improvise |

---

## 9. Why this is lower friction than other formats

| Format | Oyster v0? | Reason |
|---|---|---|
| Daily email + PDF | **Yes — default** | Matches office/truck planning; printable for crew; 14 fields fit |
| WhatsApp | Optional ping | Good for Elevated; bad as only channel (formatting, archival, 14 fields) |
| SMS | Optional 160-char ping | Link to PDF only; cannot fit contract in SMS body |
| Weekly email | Too slow for 72h | May add as a Monday recap, not the product |
| Simple map | No for v0 | NANOOS already is a map; our job is the decision sentence |
| Dashboard | No for v0 | Overbuild |
| API | No for v0 | Maybe later for Taylor-class GIS |
| Spreadsheet | Fallback | If a partner lives in Excel, weekly dump of briefs + outcomes |

---

## 10. Workflow sketches for the other two candidates (not v0)

### Chinook charter (if ever selected)

- **Format:** WhatsApp 18:00 local + morning confirmation. PDF on request.
- **Onboarding:** harbor, vessel, operating-range **polygon coarsened to ≥10 km cells**, season calendar, privacy = exact spots NEVER shared.
- **Loop:** evening brief → trip → 30s catch/no-catch + effort. Pause product when season closed (do not sell a closed fishery).
- **Hard rules:** no nav, no weather-safety, no license advice, no “you will catch.”

### Lobster CPUE (second-wedge candidate)

- **Format:** email/PDF night before next planned trip; WhatsApp optional.
- **Onboarding:** zone, typical soak, trap count (not locations), bait type, privacy = trap coordinates NEVER_PUBLISH.
- **Loop:** brief → trip → haul-level or trip-level CPUE in 30–90s (trip-level first).
- **Hard rules:** no AIS-as-abundance; no neighbor maps; DMR landings are context not vessel truth.

---

## 11. Staffing the manual MVP (least build)

| Role | Time | Notes |
|---|---|---|
| Brief assembler | 20–40 min/farm/day | Can cover 3 design partners in <2 hours |
| QA | 5 min/brief | Same person until volume forces split |
| Partner success | 30 min/week/farm | Outcomes, DUA, complaints |
| Domain reviewer | 1–2 hrs every 2 weeks | Wording + physiology sanity |

This is the product until a paid pilot demands automation. Automate **render + source pull** before automating the score.

---

## 12. Acceptance tests for “workflow works”

1. A manager who has never seen the PDF can answer “what changed / what next / why / confidence / options / what it is not / how to report” in one minute.
2. A crew member does not read it as harvest permission.
3. Outcome form completes on a phone with wet hands / gloves-off in 30 seconds.
4. We can replay the brief with as-of data (no future leakage) — handoff to geospatial + validation agents.
5. No brief ships without the 14 fields.
