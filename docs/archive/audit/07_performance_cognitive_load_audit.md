# Performance and cognitive-load audit

**Measured:** 1440×900 desktop, `localhost:5173`, C17 selected.  
**Not a load-test lab:** fixtures are tiny (27 polygons). Performance pain is **human**, not FPS.

---

## 1. Runtime performance (adequate)

| Item | Observation |
|---|---|
| Stack | Vite 6.4.3, MapLibre 6.10, no backend |
| Fixtures | 27 hexes, 3 station points, small JSON — fine |
| `generate-fixtures.mjs` | Offline; not on the critical path of a page view |
| Map workers | `setWorkerUrl` in `main.ts` — OK |
| Paint | Multiple fill+pattern layers per cell (`mapApp.ts`) — cheap at n=27 |
| Cooperative gestures overlay | Always-on hint; `pointer-events: none` |
| `resizeLater` / rAF | Map resize on window resize |
| Document scrollHeight | 987 vs 900 viewport (`overflow: hidden` on html/body) — leftover skip-link/layout slack from VERIFICATION.md |

**P3:** if this visual language is applied to a global hex grid, pattern fills + per-cell labels + 16-field HTML inject will not scale. That is not today’s crash. Do not “optimize” by dropping UNKNOWN hatch.

No evidence of jank that explains founder confusion. **They cannot understand the sentences.**

---

## 2. Cognitive load — first screen (P0)

Miller-ish working memory: the 30s goal is **five** chunks (where now, soon, sure, depth, why). The GUI presents **dozens**.

### Word counts (live `innerText`)

| Region | Words | Role |
|---|---|---|
| Banner | 34 | Negations + acronyms |
| Left rail | 305 | Modes, stubs, later-modes list |
| Evidence (C17) | **896** | Ops essay + 16 fields |
| Timebar | 69 | Dual timestamps ×4 + model id |
| **Total chrome** | **~1300** | Before counting canvas labels |

C17 ops headline alone is a paragraph of Category D, Tier 3, WAC 246-282-006, Vibrio, FDA, tissue toxin, fixture tercile.

### Fold (1440×900)

| Need | In first viewport? |
|---|---|
| Species name | Only if user parses OPS-RISK block mid-panel |
| Search | No |
| Legend | No (y≈1034) |
| Jump list | No (y≈958) |
| Why / observed vs forecast | No (y≈1372) |
| Fields 1–2 now/soon | No (y≈1697+) |
| Banner NOTs | Yes — first 64px |
| Mode 2–7, 10 dead list | Yes |
| Timebar ISO soup | Yes — last 100px |

**Left rail visible:** AOI, modes including dead list, unknown slogan, depth stub. **Not visible:** the decoder ring (legend) or the only reliable selector.

**Right panel visible:** Category D legal/ops essay. **Not visible:** the four questions the panel was specified to put above the fold (`evidence_explorer.md` §2).

This is inverted hierarchy: **warnings and mode catalogs first, answers last.**

---

## 3. Competing visual systems on one map

A user may enable, at once:

1. Truth-state fill + 6 pattern layers  
2. Unknown-map recolor  
3. SST circles  
4. Habitat dots  
5. `n=` typography  
6. Station dots (Mode 8)  
7. Cell ID labels  
8. Map stamp  
9. Cooperative-gesture copy  
10. Navigation + scale + attribution  

`layer_stack.md` says hatch must remain visible and SST must not become abundance. The **UI still offers** three overlays labeled “stubs” next to a mode that also toggles density. Cognitive result: “which color is the fish?”

Default C17 also **thickens** the ops-risk outline (`isOpsRiskExample` width 2.4). Attention is pulled to the worst-jargon cell.

---

## 4. Timebar as cognitive tax

Seven columns, 0.65rem labels, each value like:

`2026-09-18T23:00:00Z · Sep 18, 2026, 16:00 PDT`

`formatClock` in `main.ts` **always** concatenates UTC ISO and PDT. Valid-for **doubles** that with an arrow. At 1440px columns wrap mid-timestamp (screenshot/timebar: ISO split across lines). Users do not get “next 3 days.” They get a log file.

Footer also says `low (category, not a %)` and `GLOBE-PROTO-FIXTURE-2026-09-18-v0` — expert metadata in the persistent chrome.

---

## 5. Interaction performance (human)

| Action | Cost |
|---|---|
| Understand what to click | High — no search, map clicks miss |
| Select C05 UNKNOWN | Scroll 200px+ of rail + open 28 enum options |
| Read why on C17 | Scroll ~600px of ops in a 390px-wide column |
| Compare two cells | Change select; no Mode 7; working memory of enums |
| Undo overlays | Three checkboxes + mode + unknown (state coupling: Mode 9 forces unknown on, SST hidden when unknown on) |

State coupling (`main.ts`: Mode 9 sets `unknownMap = true`; `mapApp.ts`: SST hidden if `unknownOn`) is **correct scientifically** and **opaque**. User checks SST, switches Mode 9, circles vanish.

---

## 6. Mobile cognitive load

`styles.css` `@media (max-width: 1100px)`: document scroll, map 50vh, then evidence. Timebar 2 columns — **more** wrapping of ISO strings. Banner becomes two rows. User first sees disclaimer, then **the entire rail** (modes, later modes, depth…) **before the map**. Species goal is even farther.

Commercial spec wanted a **sticky does-not-mean strip** and a 30s form. This layout is the opposite: scroll through a design-doc.

---

## 7. Performance of honesty copy

Repeating “not a live animal map / fixture / not harvest” in banner, stamp, AOI, depth, layers, every cell’s field 12, C17 headline, and live region is **honest** and **habituating**. After the third repetition, the **fourth** line (FORECAST vs OBSERVED) dies with the rest.

**Fix is not fewer facts. It is one short composition**, then Expert for the rest. See `09_redesign_spec.md`.

---

## 8. What would actually make the UI faster (for humans)

1. Remove later-modes list and Mode 8/9 from the first column (fold those into Explore toggles).  
2. Search first; 16 fields behind Expert.  
3. One local time, one horizon.  
4. Legend as 4 items: Measured / Guessed / Future / Don’t know (merge gap+unknown for default; split in Expert).  
5. Do not auto-open C17.  
6. Do not draw cell IDs at default zoom.  
7. Keep MapLibre 2D; do not add 3D “performance” theater.

None of these require a faster GPU. They require **fewer simultaneous meanings**.
