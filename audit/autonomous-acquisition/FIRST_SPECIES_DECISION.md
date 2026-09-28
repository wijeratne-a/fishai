# First species decision

**Label:** internal feasibility only. Not a published nowcast.

The Florida Keys extract does contain Atlantic goliath grouper, under the spaced code `EPI ITAJ`, not the compact code `EPIITAJ`. Detection events were 1 in 2018, 1 in 2022, and 6 in 2024. That is too few positives in a spatial fold to support a species model. Goliath stays off the first fit, and the locations of those detections are not listed here.

Species were ranked only if their code appears in the species list of all three years (249 codes). Detection means any `NUM > 0` on that event.

## Selected species

**Chaetodon capistratus**, foureye butterflyfish, NOAA code `CHA CAPI`.

WoRMS AphiaID 159661, status accepted, exact name match on 2026-09-24.

| Year | Detection events | Events |
|---|---:|---:|
| 2018 | 438 | 843 |
| 2022 | 237 | 648 |
| 2024 | 351 | 622 |

Prevalence across 2,113 events is 0.486. Every spatial block used in the baseline had more than 100 positive events. The species is a widespread reef fish in this table, not a one-year or one-site occurrence.

## Fallbacks

1. **Sparisoma viride**, stoplight parrotfish, code `SPA VIRI`, WoRMS AphiaID 273780. 1,116 detection events, prevalence 0.528, positives in every year (495, 173, 448).
2. **Haemulon flavolineatum**, French grunt, code `HAE FLAV`, WoRMS AphiaID 275727. 906 detection events, prevalence 0.429, positives in every year (319, 223, 364).

Bluehead wrasse (`THA BIFA`) had more detections (1,965) but prevalence 0.930, so a spatial model has little contrast left to explain.

No minimum sample size was invented. The goliath counts fail because a block holdout cannot put multiple positives in every fold. The butterflyfish counts can.
