# Sensitive display rules

**Program:** FishAI / Global Saltwater Life Observatory  
**Path:** `/Users/wijeratne/dev/fishai/globe/sensitive_display_rules.md`  
**Agent:** USER_INTERFACE_AND_EVIDENCE_EXPLAINABILITY_AGENT  
**Date:** 2026-09-18  
**Status:** Binding visual application of privacy tiers. Not legal advice. Human legal + ecological-harm review required before any public map.

Policy sources (do not overwrite): `../observatory/sensitive_location_policy.md`, `../artifacts/data_rights_and_privacy/privacy_and_sensitive_location_policy.md`.

**A global public map of saltwater life is unsafe as v1 and is rejected.**

---

## 1. Publish classes (badge on every layer)

| Class | Globe may show | Native geometry in browser? |
|---|---|---|
| `PUBLIC` | After licence **and** ecological-harm review | Only if review says native OK (env, official polygons, bathy) |
| `COARSENED` | Parent cells / official units | **No** — only generalized features |
| `DELAYED` | After embargo, still at allowed grain | No live “now” |
| `RESTRICTED` | Named staff / statutory UI | Not public tiles |
| `PRIVATE` | Contributing partner only | Partner ACL; public jobs cannot mount |
| `NEVER_PUBLISH` | Nothing (or legal-hold store) | **Never** in globe, screenshots, eval sets, weights |

**Default when unsure:** one class stricter. `DELAYED` never overrides `NEVER_PUBLISH`.

Badge copy: `Publish: COARSENED · 0.1° / growing-area · not native GPS`.

---

## 2. Zoom is a privacy control

Sibling tile/LOD design implements this; UI rules:

| Zoom | Allowed biological-ish content |
|---|---|
| Global | Support-tier summaries, coverage hatch, **no** animals |
| Regional | Env fields, habitat at published grain, historical occurrence **coarsened** |
| Local | Approved detailed records **only** if publish class allows; W1 public = water-body + growing-area **context**, not beds |

**Do not** load raw records into the client and “hide” them with CSS. Coarsen **at the product boundary**.

Failed reverse-engineering test (500 m recovery of lease, trap, nest, waypoint; isolate one vessel; back-solve nest from corridor; wait on a whale with time slider) → coarsen, delay, or withhold. A disclaimer under a failing heatmap is not a fix.

---

## 3. Harmful precision — do not draw

From observatory §6, visualized:

- Nest / crawl / hatchling timing  
- Rookery, haul-out, calving, pupping, natal holding pools  
- Active spawning aggregation GPS, depth, moon, choruses  
- Nursery / internesting at capture grain  
- Raw tracks of turtles, mammals, sawfish, aggregation sharks  
- PAM bearings / TDOA / array geometry that enables DIY localization  
- Rare/listed eDNA native stations  
- Remaining high-value invertebrate beds, precious coral unpublished sites  
- VMS; live AIS identity; competitor routes  
- Private fishing grounds, trap GPS, charter waypoints, **lease corners**  
- Farm KPIs, disease, genetics, yield  
- TEK / Indigenous targeting layers  
- Unpublished PI sites  
- User identity / crew  
- Security-sensitive infrastructure  
- iNat true coords when obscured  
- CITES targeting pinpoints  
- Mosaics that recover any of the above with AIS/charts/iNat  

**Do not randomize coordinates.** Use official units, H3 parents, or withhold.

---

## 4. W1 visual application

| Object | Class | Globe |
|---|---|---|
| Willapa Bay shoreline / named water | PUBLIC geography | Yes |
| GEBCO-class bathymetry | PUBLIC, not-for-nav | Yes |
| WA DOH growing-area outline | Official context | Outline + caption; **not** model-colored open/closed |
| Fake coarsened H3-like cells | Fixture | Yes, labeled fixture |
| Real lease polygon / bag GPS | PRIVATE / NEVER_PUBLISH public | **No** |
| Farm mortality, yield, workability logs | PRIVATE | Partner email/PDF, not public globe |
| OSI-72 rank on public map | COARSENED to growing-area or larger if ever public | Partner: zone; public: do not invert a lease (rule-of-3) |
| Other farms’ performance | NEVER_PUBLISH | No |

---

## 5. Screenshots, demos, marketing

Treat as public layers. Fixture demos use **synthetic** cells and **explicit** fixture banners. No “live Willapa oysters” screenshots. No glowing global life poster.

---

## 6. AIS / GFW / VMS

Not an abundance layer. Identity `NEVER_PUBLISH` in public UX. Do not ingest GFW for this stack without a commercial licence path (already NC). Partner vessels: PRIVATE.

---

## 7. Official authority overlays

MPA, Slow Zone, salmon area, NSSP growing area: draw **exactly** the authority polygon and **link out**. The globe does not authorize take, entry, harvest, or harassment.
