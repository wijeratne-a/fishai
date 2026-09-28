# Transferable lessons from insects and pest surveillance

Insects are the clearest case where tagging individuals is impossible and useful surveillance still exists. The systems that work estimate risk, flux, and timing. They do not track individual insects.

## What these systems do

- **Radar measures aggregate flux.** Vertical-looking and weather radars measure the mass movement of insects aloft and sort them only coarsely by size (Hu et al. 2016, S22; Chapman et al. 2011, S23). Species are not resolved without ground sampling.
- **Vector surveillance counts per trap-night.** Mosquito programs rely on standardized traps at fixed sentinel sites, so a count has an effort denominator.
- **Global vector maps are suitability maps.** The global *Aedes* distribution work combined occurrence records with environmental covariates to map where the vectors can occur (Kraemer et al. 2015, S81). That is a suitability product, not a local abundance count.
- **Locust monitoring combines field reports, habitat condition, and forecasts.** The FAO Desert Locust Information Service issues graded warnings rather than precise maps (S82; program documentation, not re-checked in this pass).
- **Pollinator monitoring uses short fixed counts.** Standardized timed counts and traps give effort-aware data (UK Pollinator Monitoring Scheme, S114).
- **Degree-day models predict timing.** Accumulated temperature predicts development stages, which forecasts when a pest appears, not where each individual is.

## What transfers to FishAI

1. **Effort is the unit.** A trap-night is the insect version of a completed reef survey. A count without effort is not a rate.
2. **Fixed sentinel sites beat scattered reports** for timing and trend, because the method and place stay constant.
3. **Aggregate sensors measure biomass, not species.** Fisheries echosounders are the marine analogue of insect radar. They need trawl or video ground truth before any species claim.
4. **Environmental triggers forecast timing.** For fish, temperature-linked spawning or recruitment timing can become a testable hypothesis. It is not a location forecast.
5. **Graded warnings with stated evidence are more honest than a precise map** when observation is sparse.
6. **Suitability is not abundance.** Global maps built from occurrence records belong at Level 0 to 2.
7. **Hierarchical surveillance works:** many cheap sensors plus a few expensive validation samples.

## What does not transfer

- Radar does not see into water.
- Dense trap networks have no marine equivalent at scale. eDNA and passive acoustics are sparse by comparison.
- Pest surveillance exists to support control. FishAI must not become a harvest guide.

## FishAI actions

- Keep effort fields mandatory for every structured source.
- Treat any future echosounder data as aggregate biomass until species composition is known.
- Record timing relationships, such as temperature and spawning, as hypotheses to test.
- If a public product is ever shown, prefer graded, evidence-labeled categories over fine probability grids where data are sparse.
