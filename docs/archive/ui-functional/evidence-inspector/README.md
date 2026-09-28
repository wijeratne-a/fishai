# Evidence inspector (spec)

**Status:** Spec with **mock data only**. Not wired to the live globe (`globe/prototype`). Do not treat this folder as a running UI.

## Purpose

A future side-panel (or dock) that shows one scientific answer at a time without implying live tracking or published nowcasts when the card is not `PUBLISHED`.

## Required fields

| Field | Meaning | Mock example (synthetic) |
|---|---|---|
| Species | Taxon under inspection | “Demo reef fish (*Exampleus synthetica*)” |
| Output type | Exactly one honesty label | `INTERNAL` / `INTERNAL_MODEL_OUTPUT` |
| Probability | Detection or occurrence probability if issued | `0.31` (internal only) |
| Uncertainty | Confidence / interval / qualitative how-sure | “Low — spatial block holdout not shown” |
| Valid time | Phenomenon or prediction valid interval | `2023-06-01T00:00:00Z` … `2023-06-01T23:59:59Z` |
| Model version | Stable model id | `internal-demo-v0` |
| Support | In-range vs out-of-support | `SUPPORTED` or `UNSUPPORTED` |
| Sources | Provenance handles / licenses | Synthetic survey frame + synthetic SST join |
| Limitations | What is not claimed | Not a published nowcast; not ecological absence; not harvest advice |

## Non-goals

- No latitude or longitude fields in inspector payloads.
- No wiring into MapLibre layers, past-report grids, or Willapa demo cells.
- No claim that mock probability is a live animal location.

## Mock-only note

Any JSON or HTML under this directory (if added later) remains fixture material for design review. Shipping requires a separate integration workstream and a real `PUBLISHED` card before nowcast/forecast output types appear.
