# Transferable lessons from birds

Birds have the most mature large-scale distribution and movement systems. Their success rests on three things fish mostly lack: millions of standardized observations, a direct aggregate sensor (weather radar), and animals visible from land.

## What these systems do

- **eBird** collects very large numbers of checklists with effort fields (Sullivan et al. 2009, S78). A checklist marked complete lets analysts treat unreported species as non-detections for that effort (Johnston et al. 2021, S80).
- **eBird Status and Trends** estimates relative abundance at a standardized effort, week by week, with uncertainty (Fink et al. 2020, S79).
- **BirdCast** trained gradient-boosted trees on 23 years of spring weather-radar observations and weather reanalysis. The model explained up to 81 percent of variation in nocturnal migration intensity and 62 to 76 percent for forecasts 1 to 7 days ahead. Operational forecasts are generated from weather model output. It predicts aggregate migration intensity, not species (Van Doren and Horton 2018, S20; checked this pass).
- **Weather radar networks** measure birds aloft at continental scale (Dokter et al. 2011, S21).
- **Motus** is a coordinated automated radio-telemetry network on one shared frequency with a central database. By 2017 it had tracked more than 9,000 individuals of over 87 species. Animals are detected only near stations, and filtering false positives increases false negatives (Taylor et al. 2017, S03; checked this pass). Motus was initially inspired by the Ocean Tracking Network.
- **Bird banding** recoveries depend on where people find and report birds (S113).

## What transfers to FishAI

1. **A complete list plus effort turns citizen reports into zeros.** A reef survey program that records complete species lists and duration could supply effort-aware non-detections. Check each program's protocol before assuming this.
2. **Standardize predictions to a reference effort,** such as the probability of detection on one standard survey.
3. **Forecasts work when two conditions hold:** a long archive of a direct aggregate signal, and skillful weather or ocean forecasts at the lead time. FishAI has neither for fish at scale.
4. **Score forecasts by lead time.** BirdCast reports skill separately for each forecast horizon.
5. **Shared networks beat single projects.** A common frequency and a central database let one team's animals be detected at another team's stations.
6. **Generalize sensitive locations** before public display (Chapman 2020, S86).

## What does not transfer

- Weather radar does not see underwater.
- Most fish cannot be seen by observers on land or at the surface.
- No marine program yet produces complete checklists at eBird's scale.

## FishAI actions

- Prefer survey sources whose records mark the species list as complete and record effort.
- Report any future forecast skill by lead time, never as one number.
- Treat the ocean acoustic telemetry networks as the Motus analogue, used internally and under agreement.
