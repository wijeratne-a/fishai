# 4D domains — Atlantic goliath grouper

**Status:** Designed. No operational 4D field is issued.  
**Taxon:** *Epinephelus itajara*, AphiaID 159353.  
**Rule:** do not collapse the targets below into “where the goliath are.”

---

## Prediction targets (keep separate)

| Target | Meaning | Issued today? |
|---|---|---|
| **Occurrence probability** | P(present \| lon, lat, depth, time) for a named life stage | **No.** No published card. |
| **Habitat suitability** | Favorable conditions (mangrove, structure, depth, salinity) | **Not presence.** Not drawn as animals. |
| **Relative abundance index** | Concentration vs a defined comparison set — not a census | **No.** |
| **Spawning-aggregation presence** | Whether an aggregation is active in a coarsened cell in season | **Blocked.** Exact sites withheld. No layer. |
| **24–72h forecast** | Near-term change in a named target | **No forecast issued.** |
| **Seasonal pattern** | Jul–Sep spawning window vs the rest of the year (ecology) | Described in text only. Not a playback. |
| **Unknown** | Insufficient evidence | **Default.** |

A forecast is a time-forward statement of one of those targets. It is not a seventh “fish map.”

---

## First prototype domain (in)

**Geography (coarsened):** southwest Florida / **Ten Thousand Islands** and **adjacent nearshore reefs** on the southwest Florida shelf. Named at bay-to-shelf scale, not wreck scale. Approximate working box for later work (not a survey stratum): about **26.5°N–25.0°N**, **82.3°W–80.9°W**. This box is a **domain boundary**, not a presence polygon.

**Why here:** NOAA’s fetched science overview names Ten Thousand Islands as the 1997–2005 **juvenile** study area, with offshore adult work in the Florida Keys / Gulf / South Atlantic. That is a research geography, not a claim that animals are there now.

**Depth bands:**
- **Mangrove / estuary shallows** — juvenile (and some adult) ecology from Florida Museum and FishBase.
- **Adult 0–50 m structure** — coral, rock, mud, artificial reef / wreck *class* of habitat. FishBase also lists 0–100 m; 50 m is the first-slice adult band, not a hard physiological limit.

**Time:**
- **Historical training window** — compiled public records (when rights allow ingest). Not “now.”
- **Operational now** — not issued. Unknown.
- **Spawning season** — **July–September** as stated by Florida Museum (accessed 2026-09-22). Lunar timing is noted on that page; we do not encode a moon-phase layer.

**Vertical / 4D:** lon, lat, depth band, time class. No water-column mesh is built.

---

## Out of domain (do not draw as this slice)

- Pacific *E. quinquefasciatus* / eastern Pacific “goliath.”
- Eastern Atlantic (Senegal–Congo) until a separate domain is specified.
- New England stray records as a core habitat.
- Exact spawning wrecks, named dive sites, or juvenile GPS pins.
- Partner telemetry tracks, unpublished survey microdata, restricted aggregation lists.
- AIS, VMS, or fishing effort as fish presence.
- Willapa oyster fixtures (wrong ocean, wrong taxon, wrong decision).
- Food-safety, harvest authorization, or ESA listing advice.
- A claim that the system knows where every goliath grouper is at every moment.

---

## Grain

Public geometry, if any, is **≥ ~1°** or withheld. Client-side hiding of a fine cache is not enough: do not fetch, store, or tile aggregation-scale coordinates for the public globe.
