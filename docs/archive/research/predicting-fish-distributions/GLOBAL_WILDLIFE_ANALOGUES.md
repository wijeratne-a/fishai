# Global wildlife analogues

Research-only. Source ids reuse `RESEARCH_SOURCES.csv` S-ids and `_work/SOURCES_B.csv` P300–P400. Numbers appear only if checked in this pass or already checked in global-life-tracking.

**Rule for FishAI:** these systems predict probability, intensity, or tagged-animal presence. None locates every untagged individual. Tags describe tagged individuals. Radar and acoustics without ground truth do not resolve species.

## Birds

### BirdCast

- **What it is.** Continental nocturnal bird-migration intensity forecast trained on weather-radar observations and weather reanalysis, then run on weather-model output (S20; P340).
- **Data.** 23 years of spring weather-radar observations plus reanalysis in the training paper (S20). Operational runs use weather forecasts.
- **Output.** Aggregate migration intensity, not species and not individuals (S20).
- **Validation.** The training paper explained up to 81 percent of variation in nocturnal migration intensity and 62 to 76 percent for forecasts 1 to 7 days ahead, reported by lead time (S20).
- **Transferable.** Score by lead time. Need a long archive of a direct aggregate signal plus skillful atmospheric forecasts. Freeze the model before the test period.
- **NOT transferable.** Weather radar does not see underwater. FishAI has no equivalent continental fish flux sensor. Species identity is not in the radar product.

### eBird Status and Trends

- **What it is.** Effort-standardized relative abundance and occurrence through the annual cycle from complete checklists (S78; S79; S80; P341).
- **Data.** Citizen checklists with effort fields. A complete list supplies non-detections for that effort (S80).
- **Output.** Weekly relative abundance at a reference effort. Product documentation for year 2023: 2,980 species, 52 weeks, 3 km grid, standardized as expected count on a 1 hour, 2 km expert checklist (P332). That is a product spec, not a FishAI result.
- **Validation.** Fink et al. 2020 compared Wood Thrush range-wide trajectories with independently analyzed Breeding Bird Survey data and reported corresponding decline patterns (S79; P341). Do not import that correspondence as a numeric skill score for fish.
- **Transferable.** Complete lists plus effort make zeros. Predict at a stated survey effort. Separate observer process from ecology.
- **NOT transferable.** No marine program matches eBird volume. Reef RVC is the analogue of a designed complete list, not of eBird scale. Presence-only GBIF/OBIS is not eBird.

## Tracking infrastructure

### Movebank

- **What it is.** Archive, sharing, and analysis system for animal tracking datasets with owner permissions, embargoes, licenses, and a formal repository (S04; P342).
- **Data.** Owner-submitted tracks from many tag types. Live feeds for some manufacturers (P342).
- **Output.** Individual tracks and derived analyses under the owner’s sharing rules. Not a population census.
- **Validation.** Metadata and permission checks, not a biological skill score (S04). This pass did not use an unverified animal-count for the archive.
- **Transferable.** Governance: embargo, coarsen, do not auto-publish sensitive locations (S84; S85; S86).
- **NOT transferable.** GPS tracks of birds and mammals are not reef-fish locations. Do not scrape Movebank as FishAI training rows.

### Motus

- **What it is.** Collaborative automated radio-telemetry network on one shared frequency with a central database; originally inspired by the Ocean Tracking Network (S03; P349).
- **Data.** Digitally coded tags plus stations. Animals are detected only near stations. Filtering false positives increases false negatives (S03).
- **Output.** Presence at stations and movements between stations for tagged animals.
- **Validation.** By 2017: more than 9,000 individuals of over 87 species (S03). That is a network count, not detection probability.
- **Transferable.** Shared protocol beats isolated projects. Station range is not the species range.
- **NOT transferable.** Radio does not work in seawater. The ocean analogue is acoustic arrays (S07; S08), internal and under agreement.

### ICARUS

- **What it is.** Space-based reception of small animal tags. ISS phase operated 2020 to March 2022; ICARUS 2.0 receivers launched November 2025 and May 2026; coverage still building (S05; P350).
- **Data.** Tags that transmit through air to low-orbit receivers (S05; S105).
- **Output.** Individual locations and sensors when the constellation sees the tag.
- **Validation.** Ground-truth comparison is required; this pass did not re-score a numeric error table. Status is rebuilding (S05).
- **Transferable.** Small tags and a shared space segment are an infrastructure lesson, not a FishAI data source.
- **NOT transferable.** Tags must transmit through air. Fully aquatic reef fish cannot use it.

## Marine telemetry networks

### Ocean Tracking Network

- **What it is.** Global acoustic (and related) telemetry partnership headquartered at Dalhousie; OTN Canada launched 2010 (S07; P343).
- **Data.** Coded acoustic tags and receiver arrays plus satellite tags in some projects. Detections delayed and embargoed by owners (S07; S11).
- **Output.** Presence of tagged animals at receivers; research on movement, survival, and environment.
- **Validation.** This pass re-checked funding structure (35 million CAD CFI infrastructure; 10 million CAD NSERC science; P343), not a single detection-rate number. Range tests remain mandatory (S11).
- **Transferable.** Shared arrays and a data policy. Silence between receivers is not absence.
- **NOT transferable.** Network detections are not a map of untagged fish. FishAI has no OTN agreement and no tags.

### Animal Telemetry Network

- **What it is.** U.S. IOOS community aggregator (Data Assembly Center) for satellite, acoustic, and animal-borne ocean profiles (S08; P322).
- **Data.** Investigator submissions and some near-real-time satellite-linked tags displayed on a public portal under policy (P322).
- **Output.** Catalog and map of contributed telemetry; not a national fish census.
- **Validation.** DMAC/quality-control process, not a Brier score for species occurrence (P322).
- **Transferable.** One-stop metadata and delayed public release. Same privacy limits as Movebank (S84; S85).
- **NOT transferable.** Portal tracks are tagged animals. Do not use them as RVC labels.

## Whales and other marine mammals

### Whale acoustic buoys and gliders

- **What it is.** Near-real-time passive acoustics for baleen whale calling, with analyst review (S31; S32; P347; P348).
- **Data.** Moored buoy or Slocum glider hydrophone plus onboard detection and satellite relay.
- **Output.** Daily occurrence of calling near the sensor, not a head count.
- **Validation.** Buoy: 0 percent false daily detections for right, humpback, and sei whales; 12 to 42 percent daily missed detections. Right whale detections associated with aerial sightings within about 30 to 40 km over 24 to 48 hours; humpback detections showed no association with sightings (S31). Gliders: 17 to 24 percent daily missed detections (S32).
- **Transferable.** Species-specific observation models. A sensor that works for one whale can fail for another. Continuous sentinel sites can support a nowcast of calling, not of silent fish.
- **NOT transferable.** Most reef fishes in FishAI frames are not monitored this way. Calling is not occupancy of non-callers.

### Marine mammal density models

- **What it is.** Habitat-based density surfaces from designed aerial and ship surveys (S51; S49; P344), plus dynamic products such as WhaleWatch (S76; P333).
- **Data.** Line-transect or equivalent surveys with detectability; habitat covariates. WhaleWatch added satellite telemetry of blue whales plus remotely sensed ocean fields (S76).
- **Output.** Density or occurrence probability per cell and period. WhaleWatch: monthly likelihood, uncertainty, and density; journal page states 0–3.5 individuals per 625 km² (P333). Predictions are model estimates, not current sightings (NOAA product text).
- **Validation.** Designed-survey density models are validated against held-out survey effort in the source papers (S51). WhaleWatch 2.0 is an ensemble lineage (P334). This pass did not extract a new AUC.
- **Transferable.** Design the sampling frame first. Separate detection from density. Dynamic habitat products still need contemporaneous checks.
- **NOT transferable.** Aerial counts do not see reef fish. Telemetry-informed whale models are not a license to draw live fish pins from SST.

### Seal / MEOP models

- **What it is.** Marine mammals as oceanographic platforms (CTD-SRDL tags) plus movement research (P321; P331).
- **Data.** Animal-borne temperature and salinity profiles. MEOP-CTD version 2024-03-08: 872,119 profiles, 2,086 tags, 234 deployments (P331). The 2017 review already reported more than 500,000 profiles (P321).
- **Output.** Hydrographic profiles and seal tracks. Habitat models for seals exist in the wider literature; this pass uses MEOP as an observing-system analogue, not a single habitat-model skill number.
- **Validation.** Profile quality-control (MEOP processing documentation). Track error follows Argos/Fastloc limits (S13; P337).
- **Transferable.** Depth-resolved environment from animals that actually go there. Public profile archives can help ocean models.
- **NOT transferable.** Seal CTDs are not fish locations. Fastloc/Argos require surfacing.

## Sharks, turtles, large pelagics

### Shark habitat models (EcoCast and related)

- **What it is.** Daily or near-real-time habitat and bycatch-risk surfaces from observer data, telemetry, and satellite or data-assimilative ocean fields (S74; S75; P345; P346).
- **Data.** Fisheries observer records (EcoCast: 1990 to 2014) plus satellite tags and daily ocean covariates (S74). Scales et al. 2017 used the same observer window for swordfish catchability with data-assimilative ROMS (P346).
- **Output.** Suitability or catchability surfaces and dynamic closure advice. EcoCast dynamic closures could be 2 to 10 times smaller than the existing static closure while still protecting bycatch species (S74). No individual location claimed.
- **Validation.** Time-forward and management-overlap tests in the source papers (S74; S75).
- **Transferable.** Probability not positions. Need observer or survey zeros, ocean analyses at issue time, and forward tests. Closest analogue to a future FishAI nowcast if an environmental term first beats survey-only.
- **NOT transferable.** Pelagic bycatch is not Keys RVC. SST did not save FishAI’s untrusted Puerto Rico or failed kelp-bass runs (S104).

### TurtleWatch

- **What it is.** Operational map of loggerhead (later leatherback) thermal habitat to reduce Hawaii longline bycatch (P319; P320; P400).
- **Data.** Fishery sets and interactions 1994 to 2006, satellite tracks, and satellite SST (P319).
- **Output.** Avoidance isotherms. Original recommendation: shallow sets south of the 18.5 °C (~65.5 °F) isotherm in the first quarter (P319). Product page: red band between 63.5 °F and 65.5 °F where more than 50 percent of first-quarter loggerhead interactions occurred (P400). Leatherback expansion used SST zones centred at 17.2 °C and 22.9 °C (P320).
- **Validation.** Howell et al. 2008: 2007 fleet behaviour vs 2005–2006, effort moved relative to the 18.5 °C isotherm; authors discuss why, rather than claiming a controlled experiment (P319). Siders et al. (P846): the SST band still associated with loggerhead interactions years later, but fishers did not avoid it. Habitat skill and behaviour change are different tests.
- **Transferable.** Simple, stated environmental rule plus later fishery check. Dynamic ocean management (S77). A useful map can still be unused.
- **NOT transferable.** A pelagic SST band is not a reef-detection model. Do not copy TurtleWatch isotherms onto damselfish or kelp bass.

## Terrestrial large mammals

- **What it is.** GPS collars, camera-trap occupancy, and spatial capture-recapture (S19; S26; S46).
- **Data.** Captured animals with GPS; camera-days in a sampling frame; identified individuals at detectors.
- **Output.** Tracks for tagged animals; occupancy or density for the survey frame—not live public locations of every animal.
- **Validation.** Fix-success and stationary GPS tests (S19); camera methods require a design (S26). Numeric collar-error tables were not re-extracted this pass beyond Fastloc/Argos (S13).
- **Transferable.** Sampling frame first. Detection model separate from density. Tags for parameters, not public maps (S84).
- **NOT transferable.** GPS and cellular tags do not work underwater (S19). Camera-trap density estimators are not RVC N-mixture on single visits.

## Insects

### Insect radar

- **What it is.** Vertical-looking and weather radars measuring high-altitude insect flux, sorted coarsely by size (S22; S23; P335; P380).
- **Data.** Dedicated entomological radar and/or weather radar, plus nets or traps for species.
- **Output.** Aggregate biomass and direction, not species lists.
- **Validation.** Hu et al. 2016: about 3.5 trillion insects (3,200 tons of biomass) migrate above southern UK annually, using 2000–2009 radar and aerial sampling for insects flying higher than 150 m (P335; S22).
- **Transferable.** Effort unit (trap-night or radar-hour). Aggregate sensors need ground truth. Graded flux not individual tracks.
- **NOT transferable.** Radar does not see into water. Fisheries echosounders are the marine analogue and still need species identification (S34).

### Monarch models

- **What it is.** Full-annual-cycle distribution and natal-origin inference for *Danaus plexippus* from citizen occurrence plus stable isotopes (P324).
- **Data.** Occurrence records and δ¹³C / δ²H measurements, not GPS on each butterfly.
- **Output.** Breeding occurrence surface and generation-to-generation colonization. Flockhart et al. 2013: annual breeding distribution greater than 12 million km² encompassing 99 percent occurrence probability (P324).
- **Validation.** Isotope mixing for natal origin; occurrence models with geographic and climatic covariates (P324). No FishAI-like Brier score extracted this pass.
- **Transferable.** Sparse individuals can still support a seasonal suitability and origin model if the observation process is stated. Timing and multi-generation connectivity are different questions from live location.
- **NOT transferable.** Occurrence-only butterfly maps are not reef-survey detection. Isotopes are not HYCOM temperature at a dive.

## Cross-cutting limits

1. Every analogue that works at scale either (a) has a designed survey with zeros, (b) has an aggregate sensor with a long archive, or (c) tracks a biased tagged subset and says so.
2. FishAI currently has (a) for a few frames and seasons, and has neither (b) nor (c).
3. Transfer the verification culture (lead time, effort standard, species-specific sensors). Do not transfer the sensors themselves into water.
