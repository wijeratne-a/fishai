# Conflict detection

**Date:** 2026-09-18  
**Graph:** `example_graph_gigas.jsonld`  
**Status:** Rules for a small-team query layer. No production conflict engine is running.

Contradictory edges are first-class. They must **surface**, not be averaged into a smoother map.

---

## 1. What counts as a conflict

Two edges **conflict** when they share enough applicability to be about the same claim but cannot both be acted on.

Match key (all must overlap unless a rule says otherwise):

`predicate` × `subject` × `object-class` × `decision_applicability` × `life_stage_applicability` ∩ × `geographic_applicability.region_id` (or parent region) × overlapping `date_range`.

Then any of:

| Code | Pattern | Fixture example |
|------|---------|-----------------|
| `C-CAUSAL` | Same EMIV is `MECHANISTIC_CAUSAL` on one edge and `WRONG_TARGET` / `WRONG_STAGE` / `WRONG_GEOGRAPHY` / `IRRELEVANT_EMIV` on another, for the **same** decision × stage × region | `EMIV-BGC-FECAL-001` WRONG_TARGET vs any attempt to USES_EMIV it in B4 |
| `C-GEO` | MECHANISTIC_CAUSAL evidence from region A applied as if it were region B | Cheney 2000 Puget Sound hypoxia treated as Willapa intertidal bag truth |
| `C-STAGE` | Same taxon, different stage, same model bind | Larval Ω_aragonite vs `farmed_growout` 72 h bags |
| `C-RANGE` | Two `HAS_TOLERANCE` on the same EMIV with incompatible numeric envelopes (none numeric in v0) | Reserved |
| `C-HYP` | `COMPETES_WITH` hypotheses applied without habitat stratification | H1 air×tide vs H2 hypoxia as a **universal** Willapa cause |
| `C-LABEL` | Regulatory / survey node used as the biological label | WDOH class or SoundToxins *Alexandrium* as ops-stress |
| `C-TRANSFER` | `FORBIDDEN_TRANSFER` matched | Chinook SST encounter → oyster bags |
| `C-PRIVACY` | Edge would require `NEVER_PUBLISH` or neighbor-farm geometry to be true at claimed grain | Trap GPS, ESU holding pools — **omitted**, so the conflict is “claim vs missing node” |

Non-conflicts (do **not** flag):

- H1 and H2 both present **with** habitat split (intertidal vs subtidal).  
- PROXY SST existing alongside MECHANISTIC_CAUSAL air×tide — SST is labeled PROXY/IRRELEVANT for the oyster decision.  
- SoundToxins sampling *Heterosigma* (animal-stress HAB) **and** *Alexandrium* (harvest toxin) — different predicates (`ASSOCIATED_WITH` EMIV vs `CONSTRAINED_BY` NSSP).

---

## 2. How they are stored

1. **Preventive edges:** `FORBIDDEN_TRANSFER` and `TransferConstraint` nodes (Chinook SST, OA-larva, DOH-as-stress, OsHV-1 CA, Hood Canal DO, SNE hypoxia, SoundToxins-as-ops-label).  
2. **Open scientific tension:** `review_status=CONFLICT_OPEN` on the disputed edge. Fixture: Raymond-as-Willapa-bag-truth; *Protoceratium* yessotoxin hypothesis; H1 `COMPETES_WITH` H2; Cheney `CONFLICTS_WITH` H1 if unstratified.  
3. **Materialized `CONFLICTS_WITH`:** optional explicit edge between the two claims. Fixture has one (Cheney observation → H1) so a query does not have to infer it.

Do not delete the losing edge. Set `review_status` to `CONFLICT_OPEN`, `DEPRECATED`, or `REJECTED` and keep provenance.

---

## 3. Detection algorithm (v0, SQL)

Run on write and nightly. Pseudocode:

```
for each pair of edges e1, e2 (e1.id < e2.id):
  if applicability_overlap(e1, e2):
    if e1.predicate in (RELEVANT_EMIV, USES_EMIV) and e2.predicate == IRRELEVANT_EMIV
       and same emiv and same decision:
         if e1.causal_status == MECHANISTIC_CAUSAL and e2.causal_status in WRONG_*:
           emit C-CAUSAL   # this is often *intentional* (larva vs adult). Require stage overlap.
    if e1.predicate == e2.predicate and e1.subject == e2.subject
       and e1.geographic_applicability.region_id != e2.geographic_applicability.region_id
       and either claims unbounded_do_not_use:
         emit C-GEO
    if FORBIDDEN_TRANSFER matches a proposed bind:
         emit C-TRANSFER and block the bind
```

**Stage overlap is mandatory.** Larva MECHANISTIC_CAUSAL Ω and adult WRONG_STAGE Ω is **correct encoding**, not a bug. Only flag if a caller binds both to the same `decision_applicability`.

---

## 4. How they surface (product / factory)

| Surface | Behavior |
|---------|----------|
| Species page (PUBLIC) | Banner: “Competing hypotheses for 72 h stress: aerial heat×tide (intertidal) vs hypoxia (subtidal / stratified basins).” No farm ids. |
| Model factory Step 3–5 | Bind fails closed on `C-TRANSFER` / `C-LABEL`. `C-GEO` requires an extrapolation flag (v0: none granted). |
| `/forecasts/{id}/explain` | List `CONFLICT_OPEN` edges that touch used EMIVs. Do not silently pick a winner. |
| Missing-knowledge report | Conflicts are not the same as missing sensors; show both. |
| Agent / LLM tools | Tool must return conflict records. Forbidden to “reconcile” by dropping citations. |

If two MECHANISTIC_CAUSAL edges disagree on sign (more heat → more stress vs more heat → less stress) at the same stage/region/decision, **stop the claim**. That pattern is not in the fixture; add `CONFLICTS_WITH` if it appears.

---

## 5. Fixture conflicts to use as tests

1. **Chinook SST → oyster bags:** `FORBIDDEN_TRANSFER` (must block).  
2. **WDOH growing area → ops-stress label:** `WRONG_TARGET` + `FORBIDDEN_TRANSFER` from `model/doh-class-as-stress`.  
3. **SoundToxins *Alexandrium* → B4 score:** `FORBIDDEN_TRANSFER` from `survey/soundtoxins` to B4.  
4. **Cheney 2000 vs H1 without split:** `CONFLICTS_WITH`, `CONFLICT_OPEN`.  
5. **Raymond 2021 `OBSERVED_IN` Willapa:** `CONFLICT_OPEN` because the paper is Salish Sea; analogue ≠ local GT.  
6. **OsHV-1 HOSTS_DISEASE** with `WRONG_GEOGRAPHY` for Willapa 72 h vs CA causal literature — not a merge.

Passing test: a query for “why is this oyster 72 h model blocked from using SST encounter weights?” returns constraint `block-chinook-sst-to-gigas-bags` without requiring a graph DBA.
