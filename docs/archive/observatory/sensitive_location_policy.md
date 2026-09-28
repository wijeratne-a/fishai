# Sensitive species and location policy — Global Saltwater Life Observatory

**Status:** INTERNAL POLICY DRAFT, NOT LEGAL ADVICE  
**Date:** 2026-09-18  
**HUMAN LEGAL REVIEW REQUIRED** before production, partner onboarding, or any public map.

This policy is stricter than the most permissive source licence. A CC0 or public-domain coordinate is still `NEVER_PUBLISH` if releasing it would enable poaching, overfishing, habitat damage, harassment, commercial harm, legal violations, or safety risks.

**Global observation is not a justification to expose sensitive data.**

Companion: `data_rights_register.md`, `partner_network_design.md`. Commercial-wedge analogue (do not overwrite): `artifacts/data_rights_and_privacy/privacy_and_sensitive_location_policy.md`.

---

## 1. Purpose and scope

The observatory may eventually hold physics, occurrences, telemetry, acoustics, eDNA, catch, farm, and citizen-science records for saltwater life worldwide. Those records include animals that are hunted, traded, harassed, or commercially secret, and places that are nesting beaches, spawning aggregations, nurseries, private fishing grounds, farms, tribal territories, and security-sensitive marine infrastructure.

This policy covers:

- All taxa in salt water (marine mammals, turtles, elasmobranchs, bony fishes, invertebrates, plants/algae, microbes) and their habitats.
- Raw, normalized, feature, twin, forecast, evaluation, marketing, weight, and log layers.
- Research APIs and any future public app.

---

## 2. Privacy tiers

| Tier | Native resolution visible to | Public product | Training / digital twin | Typical contents |
|---|---|---|---|---|
| `PUBLIC` | Anyone | Native OK only after **ecological-harm review** | OK | Open environmental fields; official MPA outlines |
| `COARSENED` | Staff + models | After spatial generalization | OK at that grain | 0.1°–1° presence; RFMO/stat areas |
| `DELAYED` | Staff + models during embargo | Only after embargo **and** still at allowed grain | Internal now | Historical tracks; post-season nesting indices |
| `RESTRICTED` | Named staff / statutory or contract purpose | No | Only if outputs cannot invert | Mixed-licence in situ; unpublished surveys |
| `PRIVATE` | Contributing partner + DPA processors | No microdata | Only if DPA allows | Logs, farm KPIs, PI-owned tracks |
| `NEVER_PUBLISH` | Minimize; break-glass / legal hold | Never | Never in public or shared weights | Nest GPS, VMS, TEK, PAM bearings, user identity |

**Default when unsure:** one tier stricter.

`DELAYED` never overrides `NEVER_PUBLISH`. Embargo is for records that become lower-risk after animals have left, a season has closed, or a paper has been published — not for sites that remain targetable year after year (traditional nesting beaches, known grouper spawning GPSs, remaining abalone beds).

---

## 3. Non-negotiable defaults

Unless **counsel + partner (or nation) + ecological-harm review** rewrite them in writing:

1. **Exact catch, set, trap, and charter waypoints are private.** Public maps never show them.
2. **Public biological layers use broad zones**, at least as coarse as §7, and only after harm review.
3. **Farm performance is private.** Mortality, growth, disease, yield, feed, genetics: `PRIVATE` / `NEVER_PUBLISH` publicly.
4. **Breeding, nesting, spawning, calving, haul-out, and nursery sites are `NEVER_PUBLISH` at capture resolution.**
5. **No public spot maps** — heatmaps of “life,” live pins, replay tracks, “best 10 holes,” “go see this whale.”
6. **Indigenous data require sovereignty and consent (CARE).** Default `NEVER_PUBLISH`. FAIR is not consent.
7. **AIS / VMS / GFW are not abundance.** Vessel identity `NEVER_PUBLISH` in public products. No competitor tracking.
8. **Telemetry raw tracks of sensitive taxa are `NEVER_PUBLISH`.** Public Movebank points still get observatory coarsening if they reveal nests, aggregations, or current animal position.
9. **Rare-taxon eDNA native coordinates are `NEVER_PUBLISH`.**
10. **Acoustic localization of marine mammals (and fish spawning choruses) is `NEVER_PUBLISH`.** Official Slow Zones may be **linked**, not densified.
11. **User identity, crew, and citizen-scientist accounts are `NEVER_PUBLISH`.**
12. **Security-sensitive marine infrastructure is not an observatory targeting layer.**
13. **Official sanitation, seasons, CITES, ESA, and licences stay with the authority.** The observatory may link out; it may not authorize take, entry, or harassment.

---

## 4. Ecological-harm review (required for every public layer)

A public layer is any tile, API field, figure, CSV, demo, or weight dump reachable without a partner ACL.

### 4.1 Harm classes (any one is enough to fail `PUBLIC` at native grain)

| Harm class | Ocean examples |
|---|---|
| Poaching / illegal take | Remaining abalone or holothurian beds; turtle nests; sawfish; Appendix I sharks |
| Overfishing / aggregation fishing | Grouper/snapper spawning GPS and moon-timed choruses |
| Habitat damage | Rare coral thickets; seagrass remnants; intertidal haul-outs |
| Harassment | Real-time whale/dolphin/sirenian positions; pupping beaches; bird colonies |
| Commercial harm | Private fishing grounds; farm KPIs; unpublished PI sites |
| Legal violation | ESA/MMPA take facilitation; MSA confidentiality; CITES targeting; GDSP/PII |
| Safety / security | Vessel routes that expose highliners or sensitive infrastructure |

### 4.2 Review steps

1. Identify taxon (WoRMS), life-history moment (migrating vs nesting vs spawning), and place type.  
2. Apply §5 defaults and §6 `NEVER_PUBLISH` classes.  
3. Apply GBIF-style sensitivity criteria (Chapman 2020): is there a harmful human activity, is the taxon/site vulnerable, and would **this grain** enable it — including mosaic with AIS, iNat, and charts.  
4. Run reverse-engineering tests (§8).  
5. Assign tier, public grain, embargo. Document reviewer, date, residual risk.  
6. **IUCN Red List category is a trigger, not a publishing licence and not automatic concealment of every LC animal.** Conversely, LC taxa at a spawning aggregation or nest are still sensitive.

GBIF generalization categories used as a **ceiling** for anything that is not `NEVER_PUBLISH` (https://docs.gbif.org/sensitive-species-best-practices/master/en/):

| GBIF category | Sensitivity | Coordinate rule | Observatory mapping |
|---|---|---|---|
| 1 Extreme | Even general locality may threaten | Withhold, or watershed / 1° / large region | `NEVER_PUBLISH` or `COARSENED` at ≥1° **and** often `DELAYED` |
| 2 High | Finer than ~10 km threatens | Round to 0.1° | Public max 0.1° / H3 res 5, usually `DELAYED` |
| 3 Medium | Finer than ~1 km threatens | Round to 0.01° | Rarely used for marine vertebrates; prefer coarser |
| 4 Low | Finer than ~100 m threatens | Round to 0.001° | Almost never public for this program |
| Not sensitive | | Unrestricted if licence allows | Still harm-reviewed; farms/vessels still private |

**Do not randomize coordinates** (GBIF: generalization over randomization). Random jitter is reversible and looks like false precision. Use grids, official units, or withhold.

Preserve `coordinateUncertaintyInMeters`, `dataGeneralizations`, and `informationWithheld`. Never “improve” a generalized point.

---

## 5. Default publish rules by taxon class

Defaults are **public-product** rules. Internal `PRIVATE`/`RESTRICTED` stores may be finer under access control. Life-history overrides taxonomy: a LC snapper on a spawning aggregation follows the aggregation row, not the LC bony-fish row.

| Taxon / situation class | Public default | Minimum public grain if anything ships | Embargo if not `NEVER_PUBLISH` | Notes |
|---|---|---|---|---|
| **Marine mammals — mysticetes (incl. NARW, blue, fin, humpback, gray)** | `NEVER_PUBLISH` occurrence at native/PAM/telemetry grain | Official Slow Zone / SMA **as the authority publishes**; or basin/EEZ seasonal **presence** after review | N/A for individuals; ≥3 years for historical 1° presence | MMPA/ESA. Link WhaleMap/PACM; do not add observatory bearings. |
| **Marine mammals — odontocetes (sperm, beaked, orca, small cetaceans)** | `NEVER_PUBLISH` fine occurrence | 1° / LME seasonal, delayed | ≥1–3 years | Beaked-whale foraging canyons: treat as GBIF Cat 1. |
| **Pinnipeds / sirenians — haul-outs, pupping, warm-water refuges** | `NEVER_PUBLISH` site GPS | Regional (state/province) seasonal occupancy | After season **and** coarsened | Harassment and vessel strike. |
| **Sea turtles — nesting beaches, internesting, hatchling emergence** | `NEVER_PUBLISH` beach, crawl, nest, night timing | Country/region nesting **season** index, delayed | ≥1 year after season; many beaches stay `NEVER_PUBLISH` | CITES App I; ESA. |
| **Sea turtles — foraging / migration tracks** | Raw tracks `NEVER_PUBLISH` | 0.1° or coarser, delayed | ≥1 year (Movebank-class); longer if track returns to a nest | Do not reveal natal beach by backtracking. |
| **Elasmobranchs — sawfish, angel sharks, guitarfish, rhino rays** | `NEVER_PUBLISH` | Large region / 1° presence if already public in assessments | Usually never finer | Extreme trafficking and extinction risk. |
| **Elasmobranchs — reef and coastal sharks/rays, aggregations, nurseries, pupping** | Aggregation/nursery `NEVER_PUBLISH` | 0.1°–1° historical presence | ≥1 year; aggregations often never | CITES listings expanding. Tourism-famous sites: do not add **new** secret sites; do not live-track. |
| **Elasmobranchs — pelagic (blue, mako, silky) in RFMO fisheries** | No vessel-level; no tagging GPS | RFMO statistical area / 5° public tables | Match RFMO lag | Tags remain PI/`DELAYED`. |
| **Bony fishes — spawning aggregations (grouper, snapper, wrasse, etc.)** | `NEVER_PUBLISH` GPS, depth, moon timing | Basin or management unit, multi-year delayed | Default never for active sites | Direct IUU intelligence. |
| **Bony fishes — anadromous listed salmonids; holding pools, mouths at spawn** | `NEVER_PUBLISH` | Official critical habitat / management area only | N/A | ESA overlay; inherit commercial Chinook rails. |
| **Bony fishes — other listed / endemic / seahorse / Napoleon wrasse** | `NEVER_PUBLISH` fine | 0.1°–1° | ≥1 year | CITES/IUCN trigger. |
| **Bony fishes — widely distributed LC pelagics with public RFMO stats** | `COARSENED` | RFMO / FAO area × year (published grain) | As published | Still not a public CPUE heatmap. |
| **Diadromous eels, sturgeon, totoaba-class high-value** | `NEVER_PUBLISH` | National/regional only if official | Usually never | Trafficking. |
| **Seabirds — colonies, nests, rafts** | `NEVER_PUBLISH` colony GPS in season | IBA/region, delayed | After season, ≥0.1° | |
| **Invertebrates — abalone, queen conch, giant clam, sea cucumber, lobster hotspots, precious coral** | Remaining beds `NEVER_PUBLISH` | Statistical area public landings only | Never for remnant GPS | Poaching + commercial secrecy. |
| **Corals / sessile habitat-formers — remnant rare thickets, black/precious coral** | `NEVER_PUBLISH` unpublished sites | Official reef maps at **published** grain | N/A | Anchor, blast, harvest. |
| **Seagrass / listed macroalgae remnants** | Fine unpublished patches `COARSENED` or `NEVER_PUBLISH` | Official habitat maps | | |
| **Plankton / microbes / common eDNA** | `COARSENED` | Program station grid or 0.1° | Optional delay for unpublished cruises | DNA ≠ count. |
| **Rare / listed eDNA positives** | `NEVER_PUBLISH` sample GPS | Large region after delay if at all | ≥1 year | |
| **Aquaculture stock on private leases** | Performance `PRIVATE` | Growing-area / concession outline only, no KPIs | N/A | Disease outbreaks `NEVER_PUBLISH` attributed. |
| **Habitat-only environmental fields (SST, SSH, oxygen, GEBCO)** | `PUBLIC` after licence | Native if not fused with biology | None | Fusion inherits biological tier. Not navigation. |

**Override rule:** if two rows conflict, take the stricter.

---

## 6. `NEVER_PUBLISH` classes (absolute)

Do not put in public products, marketing, open eval sets, shared weights, screenshots, or support blogs:

1. Nesting beaches, crawls, nest GPS, hatchling-emergence nights.  
2. Rookeries, haul-outs, calving/pupping grounds, natal-stream holding pools.  
3. Active spawning-aggregation coordinates, depths, and timing (including fish choruses used to find them).  
4. Nursery, internesting, and pupping grounds at capture resolution.  
5. Raw ARGOS/GPS/PSAT tracks of turtles, marine mammals, sawfish, and aggregation-forming sharks; any track that back-solves a nest or den.  
6. Acoustic localization / bearings / TDOA solutions on marine mammals; raw audio that enables it.  
7. eDNA positives of rare, listed, or aggregation taxa at native sample coordinates.  
8. Remaining beds of high-value invertebrates and precious coral not already on official public maps at that grain.  
9. VMS; live AIS identity; competitor or highliner routes; reconstructed fishing patterns.  
10. Private fishing grounds, trap GPS, charter waypoints, lease corners.  
11. Farm KPIs, disease, genetics, yield, buyer prices.  
12. Tribal / Indigenous knowledge, TEK, usual-and-accustomed targeting layers, unconsented nation data.  
13. Unpublished proprietary survey GPS and embargoed research sites.  
14. User identity, crew PII, citizen-scientist true names joined to sites.  
15. Security-sensitive marine infrastructure (unpublished cables, naval operating patterns, non-public port vulnerabilities).  
16. iNaturalist/eBird **true** coordinates when geoprivacy is obscured or private.  
17. CITES Appendix I (and high-risk II) wild-population pinpoints that enable trafficking.  
18. Any mosaic product that, combined with public AIS/charts/iNat, recovers a class above.

Legal-hold copies, if required, live in a `NEVER_PUBLISH` store with break-glass access — not in the twin that feeds public APIs.

---

## 7. Location coarsening and official units

Use WGS84 for exchange. Coarsen **at the product boundary** and materialize a public-safe derivative so a warehouse leak is not a nest leak (same write-time pattern as the commercial geospatial access model).

### 7.1 Suggested public grains (until a human reviewer tightens them)

| Content | Public spatial ceiling | Public temporal ceiling |
|---|---|---|
| Environmental fields | Native if licensed | Native |
| Official MPA / critical habitat / Slow Zone | **Exactly** the authority polygon | Authority refresh |
| LC pelagic catch tables | RFMO/FAO published unit | Published lag (often year) |
| Non-sensitive historical occurrence | 0.1° (GBIF Cat 2) or coarser | Monthly or coarser; not “today” |
| Sensitive but not Cat 1 (reviewer-approved) | 1° / LME / EEZ | Seasonal or annual; `DELAYED` ≥1 year |
| Cat 1 / §6 classes | No public coordinate | N/A |

Internal features may be finer only inside `PRIVATE`/`RESTRICTED` with IAM that public jobs cannot mount.

### 7.2 Delay defaults (when `DELAYED` applies)

| Modality | Default embargo before any public coarsened derivative |
|---|---|
| Movebank-class tracks of protected/mobile taxa | ≥ 1 year; 3 years if nest/aggregation risk remains |
| Nesting / pupping / haul-out counts | After the season; often still no coordinates |
| Spawning aggregations | Default **no public derivative**; if a recovery program insists, multi-year and ≥1° |
| PAM detections | Do not publish observatory localizations; official products only |
| eDNA rare taxa | ≥ 1 year and regional grain |
| Partner catch | Never public at trip scale; multi-partner rule-of-3 + coarsen + delay |

---

## 8. Reverse-engineering tests (required before a public map)

A public layer **fails** if a reasonably skilled user can:

- Recover a nest, haul-out, aggregation, lease, trap cluster, or waypoint within 500 m (tighter for beaches and harbors).  
- Isolate one vessel, farm, or tagged animal by toggling filters.  
- Combine observatory output with public AIS, iNat, or charts to name a highliner or relocate a turtle.  
- Back-solve a nesting beach from a “migration corridor” animation.  
- Use time-slider + PAM cell to wait on a whale.

Failed tests → coarsen, delay, add official-unit aggregation, or withhold. Document the test. Do not ship a disclaimer under a failing heatmap.

---

## 9. Modality-specific rules

### 9.1 OBIS / GBIF flags

Honor provider `informationWithheld` / `dataGeneralizations` / national sensitive-species flags. Re-coarsen listed marine taxa even when a publisher released points. Do not treat aggregator presence as a licence to un-generalize.

### 9.2 Telemetry

Raw tracks: `NEVER_PUBLISH` for §6 taxa. Do not animate “current location.” Public, if ever: subsampled historical points at §7 grain after embargo, stripped of individual IDs that map to named animals (no “watch Turtle X”).

### 9.3 eDNA

Publish methods and, for common taxa, coarsened survey grids. Rare positives: regional presence/absence after delay, or withhold. Never a station map of sawfish DNA.

### 9.4 Acoustics

**Allowed public:** link to NOAA/agency Slow Zones and PACM **as published**.  
**Forbidden public:** observatory-computed positions, array geometry that enables DIY localization of the same calls, live hydrophone streams of NARW/other listed callers, fish-spawning chorus GPSs.

### 9.5 AIS / GFW / VMS

Do not ingest GFW for this stack (NC). Do not show identity. Do not use as abundance. Vessel routes of partners: `PRIVATE`.

### 9.6 Citizen science

Never request hidden iNat coordinates. Do not run a public rare-species leaderboard. Obscured points stay obscured; do not “correct” them with EXIF or AIS.

### 9.7 Farms and fishing grounds

Partner-only dashboards. Public environmental outlooks must not invert a lease (rule-of-3 + growing-area or larger).

---

## 10. Entity and identity rules

| Entity | Public | Partner / PI dashboard | Ban |
|---|---|---|---|
| Vessel name, MMSI, IMO, callsign | No | Owner’s vessels only | Competitor tracking |
| Person, crew, email, citizen-scientist identity | No | Account profile only | Marketing lists |
| Farm / company name | Only if opt-in | Yes | Other farms’ KPIs |
| Tagged animal public name | No by default | PI study only | Live “follow this whale” |
| Tribal affiliation of a landing | No | Only if the nation is the customer | Inference of treaty catch |
| Hydrophone / camera exact install GPS | No if it localizes animals | Operator yes | Harassment / theft |

---

## 11. Public product, marketing, and model-release rules

**May contain:** coarsened environmental fields; official links; method and uncertainty cards; delayed regional presence of non-sensitive taxa that passed harm review.

**May not contain:** exact biological pins; live tracks; farm leaderboards; “guaranteed fish”; “safe to harvest”; “go see animals here”; ESA/MMPA take advice; CITES targeting.

**Open weights / notebooks:** strip `PRIVATE`, `RESTRICTED`, `DELAYED` (unexpired), `NEVER_PUBLISH`. Treat eval GPS as toxic.

**Logs:** users will paste coordinates; retain minimally; do not train on them.

---

## 12. Is a global public map unsafe as v1?

**Yes. A global public map of saltwater life is unsafe as v1 and is rejected.**

Reasons (any one would suffice):

1. **Mixed taxa.** One world canvas cannot apply §5 defaults without leaking the strictest class through the loosest layer (fusion, time sliders, “all life” heatmaps).  
2. **Harm.** Nesting beaches, spawning aggregations, NARW, sawfish, and remnant invertebrate beds are exactly what a global occurrence map wants to show.  
3. **Licence.** IUCN spatial is non-commercial; GFW is NC; GBIF/OBIS mixed NC; Movebank mostly restricted.  
4. **Science.** The commercial scientific red team already blocks public fine biological maps (B-ALL-06; RT-XCUT-11). False precision plus leakage.  
5. **No review factory yet.** Ecological-harm review, reverse-engineering tests, and partner revocation are not implemented.  
6. **Identity and infrastructure.** AIS fusion and port/cable context become surveillance.  
7. **Indigenous data.** A global map will scrape or infer TEK unless the default is withhold.

**v1 public surface (allowed to design, still no ingest):** physics/chemistry context; bathymetry-as-habitat with not-for-navigation notice; taxonomy; evidence-type legend; official designation **links**; perhaps a **non-biological** coverage map (“where sensors exist,” not “where animals are”). Partner-private maps stay behind ACL.

A later public biological layer, if ever: **one taxon class × coarsened grain × delayed × harm-reviewed**, never a global animal atlas.

---

## 13. Access, retention, revocation (contract for later engineering)

| Store | Access | Retention default until counsel |
|---|---|---|
| Raw GPS / tracks / PAM bearings / eDNA stations | Partner- or PI-scoped; public jobs cannot mount | Contractual; delete/return on revocation |
| Coarsened delayed features | Staff + training jobs | Versioned for audit |
| Public serving tiles | CDN | Only harm-reviewed derivatives |
| Confidential government / VMS / observer | **Do not store** unless statutory authorization | N/A |
| `NEVER_PUBLISH` hold | Break-glass pair | Minimize; legal hold only |

On revocation: stop ingest and new training; delete or return raw; do not onboard training-use if influence cannot be unwound (`partner_network_design.md`).

---

## 14. Incident triggers

Halt the public layer and notify counsel and affected partners/nations if:

- A map reveals a nest, aggregation, lease, trap line, or drift within policy grain.  
- A release includes MMSI, logbook, TEK, hidden iNat coords, or PAM bearings.  
- Output is reasonably read as take, harvest, navigation, or viewing-guide authorization.  
- Confidential MSA/state or analogue statistics were ingested.  
- A tagged animal or colony is harassed using observatory output.

Do not “fix forward” by coarsening in place without an incident record.

---

## 15. Permitted vs prohibited (privacy / ecology lens)

**Permitted:** private decision support and research under DPA; coarsened delayed environmental intelligence; linking to official authorities; partner-only biological detail.

**Prohibited:** legal fishing/take authorization; navigation/weather-safety; harvest/food-safety stamps; catch or viewing guarantees; public spot maps; competitor AIS hunting; unconsented Indigenous data; live wildlife targeting.

Draft user-facing disclaimer: `data_rights_register.md` §2.2.
