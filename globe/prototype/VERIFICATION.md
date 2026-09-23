# Browser verification — readable life atlas (2026-09-22)

Checked at `http://localhost:5173/` after Phases A–G.

| Flow | Result |
|---|---|
| Cold load 1440×900 | Empty answer: “Search a species or pick a place.” Four nav items. One-line banner. No Category D, AphiaID, or later-modes list. |
| Yellowfin tuna | Where now = no issued location; Soon = no forecast; How sure = None; Depth unknown. Then 246,964 past reports (1788–2026), coarse cells, license note. |
| Pacific oyster from homepage | No issued location. Demo stays on Learn. |
| Learn → oyster demo | Working-conditions strip on Nahcotta cell. Expert off hides Category D and the 16 fields. Expert on shows all 16 plus JSON. |
| Unknown cell (C05) | Don’t know / no forecast / not absence. |
| Measured cell (C13) | “Water temperature (measured): 15.3 °C. This is not a sighting of animals.” |
| Place list keyboard | Native `<select>` with plain place names. |
| No matching name | `asdfqwertynotareal` → “No matching name.” |
| Dungeness crab | 54,618 past reports (1909–2026), 3 coarse cells, “not where they are now.” |
| Narrow ~390px | Search, then answer, then map, then panels. One `h1`, skip to search, `aria-live`, 14px time bar. |
