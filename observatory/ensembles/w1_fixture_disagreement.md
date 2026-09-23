# W1 fixture disagreement examples

**Date:** 2026-09-18  
**Status:** **Synthetic.** No farm was scored. No tides/NWS/NANOOS pulled. No lease KPIs.  
**Ensemble:** `ENS-W1-OSI72-v0` = `MC-CLIM` (B12) + `MC-RULE` (B4) + optional `MC-HUM` (B5).  
**Geography:** coarsened Willapa Bay **analogs**, not real growing-area codes and not lease names.  
**Purpose:** show how disagreement, DATA_GAP, OOD, planner fire, and incomparable quantities look **before** anyone trains or ingests.

Machine rows: [`fixture_cells.csv`](fixture_cells.csv).

---

## Shared issuance wrapper (all fixtures)

| Field | Fixture value |
|---|---|
| Species | Pacific oyster *Magallana gigas* (Aphia 836033) |
| Target | Category D OSI-72 / `ops_disruption_72h` |
| Horizon | 72h |
| `ensemble_mean_status` | `suppressed_unvalidated` (default) |
| Weights | `UNWEIGHTED_PLACEHOLDER` |
| Official DOH | **Not a member.** Not in \(D\). Not in impact. |
| SST ≥ 19 °C kill law | **Not a member.** Must not appear as B4 |
| Publish | `COARSENED` for the table; farm bands would be `PRIVATE` if real |

**Does not mean (every row):** food-safety, harvest authorization, abundance, percent dead, navigation/weather-safety certification.

---

## FX-01 — Agree Typical (no ticket)

Coarsened cell `FX-W1-WB-GA-NORTH`. Culture: intertidal. Issued `2026-09-18`.

| Member | Band | Why |
|---|---|---|
| B12 | `typical` | Fixture: this month×area rate is mid-range in the **imagined** table |
| B4 | `typical` | Fixture: no daytime-emersion×heat overlap; no partner wave rule fire |
| B5 | `typical` (logged `no`) | Manager would not have changed plans |

- \(D = 0\), `AGREE`, `ood_flag=false`, `impact=low`  
- **Planner:** do not fire  
- Product: show three Typical chips. Still not a safety determination.

---

## FX-02 — Canonical: B4 High vs B12 Typical vs missing logs (ticket P0)

Coarsened cell `FX-W1-WB-GA-CENTRAL`. Culture: intertidal bag. Issued `2026-07-15T16:00:00-07:00` (summer analog, **not** a replay of 2021 observations).

| Member | Band | Why |
|---|---|---|
| B12 | `typical` | Fixture climatology: July in this analog area is often workable; event rate not in the upper tail of the **imagined** month table |
| B4 | `high` | Fixture rule: forecast **air** overlaps **daytime low-tide emersion** + solar geometry on exposed culture. Wind/wave not required for this fire. **Not SST.** |
| B5 | `cannot_issue` | **No pre-brief log** (`DISAGREE_DATA_GAP`) |

- \(D = 1\) (High vs Typical among eligible machine members)  
- Codes: `DISAGREE_UNUSUAL_OCEAN`, `DISAGREE_ECOLOGICAL_ASSUMPTIONS`, `DISAGREE_DATA_GAP`  
- `ood_flag=true`, dimensions: `climate` (AHW-class analog), `missing_envelope` (no fitted B12, thresholds HYPOTHESIS)  
- `impact=high` (primary B4 clause)  
- **Mean if illegally averaged:** \(\bar{z}=(2+0)/2=1\) → Elevated — **ship block.** Split must remain High vs Typical.  
- **Planner:** R1 + R2 + R3 → **P0**. Needs: `NEED_OUTCOME_LOG`, `NEED_HUMAN_PRIOR`, `NEED_AHW_SLICE`.  
- Public map: growing-area split fill only. **No** “this farm will die.” **No** lease polygon.

This is the example the ensemble product is for: climatology says “July is usually fine”; the expert-rule says “this tide×air is not usual”; nobody logged outcomes yet.

---

## FX-03 — Agree High in a historically hot month (validation, not disagreement theater)

Cell `FX-W1-WB-GA-SOUTH`. Issued `2026-07-15`.

| Member | Band |
|---|---|
| B12 | `high` (fixture: this analog month×area sits in the upper tail) |
| B4 | `high` (same air×emersion fire as FX-02) |
| B5 | not logged |

- \(D = 0\) on machine members, codes: `DISAGREE_DATA_GAP` (B5/outcomes), not a band split  
- Planner: **R2 only if impact high and logs missing** → P0 for `NEED_OUTCOME_LOG`, **not** because members disagree  
- Do not invent a disagreement heatmap here. Capture outcomes so B12 vs B4 can be scored later.

---

## FX-04 — Subtidal float: B4 drops emersion (ecological assumptions / culture)

Cell `FX-W1-WB-SUBTIDAL-FLOAT`. Culture: **floating / fully subtidal**. Issued `2026-09-18`.

| Member | Band | Why |
|---|---|---|
| B12 | `typical` | Month×area table does not know culture type (known limitation) |
| B4 | `cannot_issue` | Emersion clause **dropped**; partner wave threshold **not provided** so workability clause also dropped. **Must not** substitute SST ≥ 19 °C. |
| B5 | not logged | DATA_GAP |

- \(D = null\), `DISAGREE_DATA_GAP`, `DISAGREE_ECOLOGICAL_ASSUMPTIONS`, `DISAGREE_UNRESOLVED_BIOLOGY`  
- `ood_flag=true`, `culture_or_farm`  
- Planner: R2 if a work window is scheduled (`impact`); else P3 `NEED_CULTURE_METADATA` + `NEED_WORKABILITY_THRESHOLD`  
- Lesson: pooling this cell with FX-02 in one mean is forbidden.

---

## FX-05 — Human conflicts with a quiet rule (conflicting observations)

Cell `FX-W1-WB-GA-BAYMOUTH`. Issued `2026-09-18`.

| Member | Band | Why |
|---|---|---|
| B12 | `typical` | — |
| B4 | `typical` | No primary fire |
| B5 | `elevated` | Manager logged **yes** — would have increased monitoring from other sources (consultant / gut / NANOOS) |

- \(D_{\max} = 0.5\) including human  
- Code: `DISAGREE_CONFLICTING_OBS`  
- `impact=medium` (human says watch)  
- Planner: R1 P2 — `NEED_HUMAN_PRIOR` already present; ask **which drivers** the manager used (options), do not overwrite B4 with B5 in the mean  
- B5 is contestability, not a third vote to manufacture Elevated as “consensus.”

---

## FX-06 — Joint OOD even if bands match (R3)

Cell `FX-W1-WB-OOD-AHW`. Issued `2026-07-15`. **Deliberate bad-spec warning row.**

| Member | Band | Note |
|---|---|---|
| B12 | `typical` | Month table has no AHW class |
| B4* | `typical` | **Illegal fixture:** a rejected SST≥19 °C clause that does **not** fire because **water** is “only” 17 °C while **air×emersion** would have been High |

- True B4 (air×emersion) would be `high` (see FX-02). The SST kill-law **must not sit in the ensemble**.  
- If a build ever emits this row as `AGREE Typical`, that is a **governance fail** (wrong member), not a calm ocean.  
- `ood_flag=true`, `climate` + `missing_envelope`  
- Planner R3: `NEED_AHW_SLICE`; **remove** the illegal clause rather than task a new SDM.

---

## FX-07 — Blocked candidate (must not average habitat with OSI)

Cell `FX-W1-WB-BLOCK-HABITAT`. Issued `2026-09-18`.

| Stream | Value | In `ENS-W1-OSI72-v0`? |
|---|---|---|
| B12 | `typical` | yes |
| B4 | `elevated` (fixture: workability watch only) | yes |
| `MC-HAB` T2 suitability | “highly suitable Pacific oyster habitat” | **no** |
| Imaginary CPUE / wild set | (none) | **no** |

- Machine OSI: \(D = 0.5\), `DISAGREE_ECOLOGICAL_ASSUMPTIONS` (rate vs workability)  
- Habitat chip: `INCOMPARABLE_QUANTITY` / `DISAGREE_QUANTITY_MISMATCH`  
- **Must not** compute \((z_{\mathrm{B4}} + z_{\mathrm{HAB}})/2\). Suitability of *Magallana gigas* in Willapa is a T2 research statement about envelopes, not 72h crew stress.  
- Planner: optional P2 on OSI split only; **do not** task observations to “confirm habitat.”

---

## FX-08 — Sparse new analog area (shrinkage)

Cell `FX-W1-WB-GA-SPARSE`. Issued `2026-09-18`.

| Member | Band | Why |
|---|---|---|
| B12 | `typical` | Fixture: \(n\) small; shrunk to parent basin-month (`DISAGREE_SPARSE_DATA`) |
| B4 | `elevated` | Mild air×emersion overlap, not High |
| B5 | not logged | DATA_GAP |

- \(D = 0.5\), `impact=medium` → planner R1 P2: `NEED_OUTCOME_LOG` (local labels), not a satellite cube  
- Public: coarsened bay, not a “new farm” pin.

---

## What these fixtures are not

- Not evidence that B4 beats B12.  
- Not a 2021 hindcast (no ingest; Raymond et al. 2022 is a **mechanism citation**, not a scored replay).  
- Not permission to email a grower.  
- Not real Willapa DOH identifiers.
