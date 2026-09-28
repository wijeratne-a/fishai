# Transferable lessons from marine life

## What each marine system can support

| System | Direct tracking | Local detection | Abundance | Distribution | Movement | Nowcast | Forecast |
|---|---|---|---|---|---|---|---|
| Shark, turtle, and whale satellite tags (S09; S10; S118) | Yes, for tagged animals | No | No | Partial, biased to tagging sites | Yes | Partial | No |
| Reef-fish acoustic telemetry (S11; S12) | Presence near receivers | Yes, near receivers | No | No | Partial | No | No |
| Fisheries acoustics (S34) | No | Aggregate biomass | Yes, with trawl species data | Yes along transects | No | No | No |
| Larval dispersal models (S62; S63) | No | No | No | Connectivity probabilities | Passive transport | No | Conditional on currents |
| Trawl and reef visual surveys (S41) | No | Yes, per survey | Index | Yes, in surveyed domains | No | No | No |
| Plankton monitoring (S38; S39) | No | Yes | Index | Coarse | No | Partial | No |
| Whale aerial surveys (S49) | No | Yes | Yes | Yes | No | No | No |
| Swordfish and tuna habitat models (S75) | No | No | No | Yes | No | Yes | Limited |
| Marine mammal density models (S51; S76) | No | No | Yes | Yes | No | WhaleWatch predicts dynamically | Limited |
| Dynamic ocean management tools (S74; S77) | No | No | No | Yes | No | Yes | Limited |
| Harmful algal bloom forecasting (S115) | No | Yes | No | Yes | Transport | Yes | Yes, with skill assessment |
| Marine heatwave ecology (S83) | No | No | No | Context for shifts | No | Condition only | Condition only |
| Close-kin mark-recapture (S47; S48) | No | No | Yes | No | No | No | No |
| Near real-time whale acoustics (S31; S32) | No | Yes | No | Local | No | Yes, daily occurrence | No |

## Key lessons

1. **Operational marine nowcasts predict probability, not positions.** EcoCast combined daily satellite ocean data with species models built from fisheries observer data (1990 to 2014) and satellite telemetry. Its dynamic closures could be 2 to 10 times smaller than the existing static closure while still protecting bycatch species (Hazen et al. 2018, S74; checked this pass). No individual location was claimed.
2. **Data-assimilative ocean models can drive near real-time species predictions** (Scales et al. 2017, S75). This is the closest analogue to FishAI Level 3.
3. **Acoustic telemetry answers presence near receivers.** Detection range varies with conditions and must be tested (Kessel et al. 2014, S11). Silence between receivers is not absence.
4. **Larval models give connectivity probabilities under assumptions.** Passive particles are not fish behavior (Cowen and Sponaugle 2009, S62).
5. **Adults can be counted without being seen.** Close-kin analysis of 214 juvenile white sharks first estimated about 280 to 650 adults in eastern Australia and New Zealand; CSIRO later revised the adult estimate to about 750 (470 to 1,030) (Hillary et al. 2018, S48; checked this pass). This is population size, not location.
6. **A sensor's meaning is species-specific.** The same acoustic buoy matched right whale sightings and did not match humpback sightings (S31).
7. **Pooled tag maps show hotspots but reflect where animals were tagged** (S09; S10).
8. **Marine heatwaves need consistent definitions** (Hobday et al. 2016, S83). Distributions can shift during events, so predictions need novelty flags.
9. **Forecast systems report skill.** Harmful algal bloom forecasts publish skill assessments (Stumpf et al. 2009, S115). FishAI should do the same before any forecast.

## FishAI implications

- The first defensible FishAI product is a survey-conditioned detection probability (Level 1). The route to a nowcast is the EcoCast and Scales pattern: survey or observer data plus data-assimilative ocean analyses, validated forward in time.
- Telemetry, larval connectivity, and close-kin methods answer different questions and belong later, under agreements.
- Every marine sensor added later needs a species-specific observation model.
