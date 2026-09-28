# Anti-goals — Active Observation Planner

**Date:** 2026-09-18  
**Status:** Binding for this design. A high OVS does not legalize an anti-goal.

The planner exists to reduce **decision-relevant uncertainty** under privacy and ecological-harm constraints. It does **not** exist to find animals for take, viewing, or competitive advantage.

---

## 1. No poaching optimization

Do not rank observations that would help a reasonably skilled user locate, time, or extract:

- remaining abalone, holothurian, queen conch, giant clam, or precious-coral beds;
- turtle nests, crawls, or emergence nights;
- sawfish / rhino ray / angel shark sites;
- grouper/snapper/wrasse **spawning aggregations** (GPS, depth, moon-timed choruses);
- listed salmonid holding pools or mouths at spawn;
- any CITES Appendix I (and high-risk II) wild pin.

`ConsPri` high ⇒ **conceal and coarsen**, not “high value target.” `KILL_SPAWN_AGG`, `KILL_NEVER_PUBLISH`, `KILL_HARM_HIGH`.

---

## 2. No public rare-species targeting

Do not recommend:

- public rare-taxon leaderboards or bounties;
- native-resolution eDNA positives of listed/rare/aggregation taxa;
- “go see this whale / shark / nest”;
- un-obscuring iNaturalist/eBird hidden coordinates;
- live PAM bearings or TDOA on marine mammals.

Allowed: delayed, coarsened, harm-reviewed regional presence of **non-sensitive** taxa; official Slow Zone **links** as the authority publishes them.

---

## 3. No AIS-as-abundance

AIS, VMS, Global Fishing Watch, tracker pings, and vessel density are **effort / safety / crowding context**, never fish, lobster, or oyster abundance.

Do not task observations whose value score depends on treating ships as animals. `KILL_AIS_ABUNDANCE`. Vessel identity is `NEVER_PUBLISH` in public products.

---

## 4. No NSSP impersonation

The planner must not:

- treat WA DOH / NSSP growing-area class, commercial closures, fecal coliform, biotoxin tissue results, or Vp control as `ops_disruption_72h` labels;
- recommend “closure sampling” as the highest-value obs for the **ops-stress** model;
- output copy a reasonable operator could read as “safe to harvest / legal to harvest / meets NSSP.”

Official harvest-open status is a **must-show constraint and authority link**, not ground truth for W1 (`artifacts/data_discovery/ground_truth_relabel_W1.md`; WAC 246-282-006). `KILL_NSSP_IMPERSONATION`, `KILL_WRONG_TARGET`.

---

## 5. Other forbidden optimizations

| Forbidden | Correct posture |
|---|---|
| Public hunt-the-fish / hunt-the-oyster map | Partner-private briefs; public non-biological coverage optional later |
| Lease-corner, trap GPS, charter waypoint recs | Named water-body / H3 res 5–6 / official unit |
| Competitor tracking | Owner’s vessels only |
| Indigenous TEK extraction | Nation protocol or withhold |
| Hardware shopping as first action | Public → partner export → existing sensors → manual → mobile → integrations |
| Maximizing rows ingested | Maximize EUR × decision value under kill rules |
| Filling empty ocean with interpolated zeros | Hatch `NO_OBSERVATIONS` |
| Open-Pacific glider “for W1” | Wrong grain and variable |
| More SST as oyster body temperature | Air × tide × bag T; SST supporting only |
| Mixing Olympia and Pacific oyster labels | Separate taxa; do not target native beds |
| Auto-tasking without a named human | Architecture human gate |

---

## 6. Test

A recommendation **fails** this file if a skilled user could use it to: take a sensitive animal, harass a listed species, open a farm’s books, impersonate a health authority, or find a secret productive spot within policy grain.

Failed recs are killed, not “disclaimed.”
