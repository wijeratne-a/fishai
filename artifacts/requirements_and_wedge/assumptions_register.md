# Assumptions register

**Agent:** REQUIREMENTS_AND_WEDGE_AGENT  
**Date:** 2026-09-18  
**Legend:** UNTESTED | SUPPORTED (cite) | REFUTED | UNRESOLVED (founder)  
**Rule:** Supported ≠ decided wedge. Founder values stay UNRESOLVED.

| ID | Assumption | Status | Evidence / gap | If wrong |
| --- | --- | --- | --- | --- |
| A01 | Founder wants a marine decision product, not a generic map | UNTESTED | Prompt states it; no founder interview in this run | Stop / rewrite thesis |
| A02 | Founder organization is not HiveClaw | SUPPORTED as “not evidenced,” not as a name | HiveClaw CONTEXT.md is local LLM inference; no FishAI entity found | Still do not invent a name |
| A03 | Section 2 config is unset | SUPPORTED | Empty fishai tree; user/orchestrator said founder did not supply config | N/A |
| A04 | Three shared candidates are viable ONE×ONE×ONE×ONE wedges | SUPPORTED at research-viability level | Official taxonomy, agency geographies, recurring decisions documented in wedge_options.md | Replace only with equal narrowness |
| A05 | W1 is the best **starting** wedge if the founder has no operator relationships | UNTESTED commercially; **recommended** from research | Recurrence + 3-farm ground truth + DOH polygons vs season closure (W2) and haul confidentiality (W3) | Founder picks W2/W3 with relationships |
| A06 | Willapa is a better first oyster geography than all WA or South Puget Sound | UNTESTED with customers | Historical Willapa Pacific oyster dominance (WSG 2013 regional tables); Toke Point 9440910; thinner ORCA coverage is a cost | Swap to a named SPS growing area |
| A07 | Farm operators have a 24–72h crew/stress decision distinct from DOH harvest legality | UNTESTED with named farms | NANOOS grower page; PSI mortality program; 2021 heat-dome mechanism | Wedge is only a packaging of tides they already use → weak WTP |
| A08 | NANOOS/CO-OPS/NWS/Copernicus can support a **baseline** work/stress rule after rights review | UNTESTED operationally | Portals and APIs exist; NANOOS DMP notes redistribution exceptions; Willapa in-situ sparse | Need partner sensors earlier than hoped |
| A09 | Commercial reuse of NANOOS partner streams is allowed | UNRESOLVED | Must be classified per provider by DATA_RIGHTS agent | Catalog-only forever / paid licence |
| A10 | Oyster v0 can avoid food-safety claims and still be useful | UNTESTED | Prompt requires the split; growers may **want** a safety product | If they only want “can I harvest,” stop or become a DOH link bot (not a model) |
| A11 | 20–80% PSI mortality and 2018 WDFW bag losses imply **Willapa 2026** economics | UNTESTED / risk of overgeneralization | PSI is PNW/WA growing areas; WDFW 2018 examples include Discovery Bay/Whidbey/Willapa (clams vs oysters mixed) | Overstate pain; fail interviews |
| A12 | USDA 114 farms / $106.8M means a reachable beachhead | UNTESTED | Census ≠ buyers; concentration unknown (NASS (D) cells) | Too few economic buyers in one estuary |
| A13 | W2 decision exists in the 48h autonomous window | CONDITIONALLY SUPPORTED | 2026 NMFS salmon measures in force; OR Cape Falcon–Humbug recreational Chinook season described on ODFW 2026 map; in-season closures possible | Closure → W2 EDV = 0 |
| A14 | RecFIN/CRFS can label a 24–48h charter product | REFUTED as a live label | CRFS/RecFIN are survey estimates for management, lagged | Partner logs mandatory |
| A15 | Habitat SST/chlorophyll can be sold as Chinook presence | REFUTED by prompt + science policy | Tier 3 cannot independently support presence | Keep as covariates only |
| A16 | Charter captains will share coarsened catch | UNTESTED | CPFV logs exist for CA management; sharing with a startup is different | W2 blocked on ground truth |
| A17 | Public hotspot maps would be rejected by captains/lobstermen | UNTESTED (strong prior) | Privacy non-negotiable in prompt | If they want spots, **do not build that product** |
| A18 | Maine DMR landings can label next-trip CPUE | REFUTED | Statewide/zone aggregates; confidentiality; lag | Partner haul data mandatory |
| A19 | ASMFC 2025 GOM/GBK “202 million lobsters” can appear in a user brief as local abundance | REFUTED | Assessment average 2021–23 stock-wide; not SA 513 next-trip; prompt forbids unbounded counts | Red-team blocker |
| A20 | Right-whale rules can be modeled as FishAI compliance advice | REFUTED | Official ALWTRP/NOAA only | Link + timestamp or stop |
| A21 | Operators will pay for a brief | UNTESTED | Zero interviews; zero pilots | Pivot/stop at 90-day gate |
| A22 | Operators will complete a 30-second outcome form | UNTESTED | None | No flywheel; stop adding model complexity |
| A23 | A generic ocean terminal is the wrong v0 | SUPPORTED by prompt north-star | Explicit non-goals | Founder override would be a new project |
| A24 | Dungeness delayed-opener is a better first wedge | REFUTED for *this* prompt’s 24–72h recurring test | High value but seasonal/regulatory/food-safety adjacent | Keep as later expansion only |
| A25 | HiveClaw tech is in-scope for v0 marine models | UNTESTED / out of scope here | Different repo; no marine data plane | Do not couple |
| A26 | OBIS occurrences are an abundance label | REFUTED | OBIS policy + prompt: occurrence ≠ abundance; some CC BY-NC | Catalog taxonomy/occurrence only |
| A27 | Copernicus SST may be used in value-added commercial products | SUPPORTED **conditional on credit/DOI** | CMEMS licence 2.2–2.4 (accessed 2026-09-18) | Rights agent still records attribution text |
| A28 | NOAA/NWS US-government works are typically public domain in the US | SUPPORTED **conditional** | NWS disclaimer; NCEI open data policy; still no endorsement; third-party layers differ | Per-product check |
| A29 | Three interviews of Sea Grant/PSI can substitute for farm interviews | REFUTED | Experts ≠ buyers | Still need operators |
| A30 | PRIMARY_OUTCOME_METRIC can be chosen by this agent | REFUTED | Prompt: do not invent founder choices | Pause |
| A31 | Mixed diploid/triploid oyster performance is the same label | UNTESTED | PSI SK grant treats triploid summer mortality as a research object | Split labels or lock ploidy |
| A32 | SoundToxins/ORHAB improve a **work-window** model | UNTESTED | Those programs target HAB/health; adjacent to forbidden food-safety product | Defer to later source-priority after W1 lock |
| A33 | Expanding to a second species before WTP is harmless | REFUTED by prompt | Scope lock | Do not expand |
| A34 | Founder will answer decision_required.md inside the 48h budget | UNRESOLVED | Pause state | Remain in STATE_10 |

### Highest-risk untested cluster

A07 + A10 + A21 + A22 (oyster decision is real, non-safety, paid, and logged). That cluster is the first interview target if W1 is chosen.

### Closed this iteration

A03, A14, A15, A18, A19, A20, A23, A24, A26, A29, A30, A33.
