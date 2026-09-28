# Transferable systems analysis

Research-only. Weather, wildfire smoke, air-quality nowcasts, traffic, and influenza forecasting. Principles for FishAI follow. Source ids: S-ids plus P325–P330, P327 / SOURCE_INDEX P003.

These systems forecast a quantity that is later observed on a clock. FishAI currently has sparse, delayed surveys. Copy **verification culture**, not the sensor density.

## Weather forecasting

**What it is.** Numerical weather prediction (NWP) plus data assimilation, ensembles, and archived forecast-versus-analysis scores.

**Data.** Global in situ, satellite, and radar observations; models initialized many times per day.

**Output.** Deterministic and ensemble forecasts of fields (temperature, precipitation, wind) at stated lead times.

**Practices that transfer:**

- **Assimilation.** Observations correct a short-range forecast, then the model integrates forward. FishAI has no equivalent observing system for fish. Do not treat a static species-climate envelope as an assimilated state.
- **Ensembles.** Spread is a forecast of uncertainty, not a gallery of equally likely maps. Calibrate the ensemble (Gneiting and Raftery 2007; P327 / SOURCE_INDEX P003).
- **Lead-time skill.** Skill falls with lead. Bauer et al. 2015: NWP gained about **one extra skillful day per decade** at medium range (P325). Report FishAI skill by horizon, not as a single number.
- **Archived forecasts.** Operational agencies keep what was issued at **issue time**, including the analysis available then. Hindcasts that cheat with later reanalyses are labeled as such. HYCOM GLBy0.08 ends **2024-09-05**; anything after that is a different product (FISHAI_DATA_GAP_ANALYSIS).

**Does not transfer:** hourly global fish observations. A coral-reef RVC year is not a synoptic hour.

## Wildfire / smoke

**What it is.** Fire-weather indices, satellite fire radiative power (FRP), and smoke-dispersion models such as HRRR-Smoke.

**Camp Fire case (P329).** Chow, Yu, Young, Ahmadov and coauthors 2022, *Bulletin of the American Meteorological Society*: high-resolution smoke forecasting for the 2018 Camp Fire (DOI 10.1175/BAMS-D-20-0329.1). HRRR-Smoke became operational at NOAA/NCEP in **December 2020**. Later periods **underpredicted PM2.5** when satellite **FRP was too low** relative to what the fire was doing. The smoke forecast is only as good as the emissions proxy at **issue time**.

**Transferable:**

- The driver (here FRP; for fish, SST or currents) must exist at issue time and be verified as a driver, not assumed.
- If the driver is biased, the downstream field (smoke, or predicted occupancy) is biased even if the transport model is fine.
- Operationalization date is part of the archive (December 2020), not “whenever the paper was written.”

**Does not transfer:** satellite FRP for fish biomass. Reef surveys are not a fire perimeter.

## Air-quality nowcasts

**What it is.** Short-term AQI from recent monitor hours so the public is not shown a lagging 24-hour mean.

**EPA NowCast (P328).** Weighted average of the **last 12 hours** of PM2.5 (and analogous rules for other pollutants). Weight on older hours is reduced when concentrations change quickly; weight floor **0.5**. Requires data for **at least two of the last three hours**.

**Transferable:**

- Nowcast ≠ 24-hour standard. State the averaging window.
- Missing recent hours: do not emit a nowcast (two-of-three rule). FishAI should refuse a “now” map when the last survey is years old.
- Rapid change increases weight on the latest hours. FishAI has no hourly fish series; the analogue is: do not smooth over a regime shift you cannot observe.

**Does not transfer:** EPA monitor density. One CalCOFI egg cruise is not a 12-hour PM2.5 stack.

## Traffic

**What it is.** Probe-based speed on a road graph, fused with loops and incidents.

**NPMRDS (P330).** FHWA National Performance Management Research Data Set: probe speeds since **2013** on **400,000+** TMC segments, **5 / 15 / 60 minute** bins, **monthly** latency. It is a **performance archive**, not a live routing feed.

**Transferable:**

- Latency is a product attribute. Monthly delivery is honest. Fake “real-time traffic” from last month’s bins is not.
- The observation is **segment speed**, not the location of every vehicle. Analogous to: survey mean in a cell, not every fish.
- Graph topology is known. Ocean “segments” (reefs, isobaths) are not TMC codes; do not invent a traffic graph for the Keys without a survey graph.

**Does not transfer:** cellular probes in the water. Acoustic receivers are the marine analogue and FishAI does not have them.

## Disease surveillance / FluSight

**What it is.** CDC FluSight: weekly probabilistic forecasts of influenza-like illness or hospitalizations, scored after reports arrive, with **backfill** as states revise counts.

**2017/18 season, verified this pass (P326, PLOS Computational Biology, not PNAS):**

- Reich et al. 2019: **22 teams** in 2017/18; FluSight Network stacked **21** component models; the stack beat CDC’s unweighted ensemble and finished **second** in the challenge.
- Training-period leave-one-season-out average forecast score for the selected FSNetwork-TTW ensemble: **0.406**.
- Burden cited in that paper: **48.8 million** illnesses, **959,000** hospitalizations, **nearly 80,000** deaths, October 2017–May 2018 (CDC figures as reported there).

This pass did **not** use later FluSight MAE tables that were not in the 2019 paper.

**Transferable:**

- Many independently implemented models, then a stack. One in-house GLM is not FluSight.
- Score **probabilistic** forecasts (log score / weighted interval score), not only a point map.
- **Reporting delay and backfill** are part of the target. RVC “year t” is closer to a delayed epi week than to a weather analysis hour.
- Publish the ensemble **weights** and the **issue timestamp**.

**Does not transfer:** weekly national hospitalization counts. Biennial Keys RVC is the opposite cadence.

## Principles for FishAI

Copy these even when the sensors do not exist.

1. **Baselines first.** A climatology or last-survey persistence must be scored. Damselfish detection (Brier **0.095** vs intercept **0.125**, AUC **0.86**) beats a baseline; kelp bass **lost** to intercept (Brier **0.296** vs **0.244**). Do not ship a map that loses to last year.

2. **Lead-time verification.** If the product is called a forecast, score 1-year, 2-year, … separately. Biennial RVC cannot support a 7-day BirdCast-style table (S20). Annual SBC LTER (Jul–Aug, 11 sites) can support year-ahead only after multiple years exist in the archive.

3. **Issue time.** Every map must record which survey years, which ocean product (and whether that product still existed), and which model version were available **when issued**. HYCOM GLBy end date **2024-09-05** is an issue-time fact.

4. **Archiving.** Keep issued files. Do not overwrite last year’s nowcast with a reanalysis. Weather and FluSight live on this. FishAI currently has no issued-forecast archive.

5. **Reporting delays.** RVC and LTER land long after the dive. A “current” globe that uses last biennial year is a **lagged survey interpolator**, not a nowcast. Name it as such (Q7 vs Q2 in CORE_PROBLEM_DEFINITION).

6. **Ensembles.** If several models exist, combine them with a method that has been shown to beat the unweighted mean in similar scoring rules (FluSight stack, P326; Gneiting and Raftery, P327). Do not average a failed kelp-bass model with a working damselfish model and call it species-agnostic skill.

7. **Communicate probabilities.** Occupancy, detection, and relative abundance are different (Q1–Q3). A Brier-scored detection probability is honest; a fish pin is not. Calibrate (damselfish **0.907** predicted vs **0.855** observed at the 0.8–1.0 bin). Show reliability, not only AUC.

8. **Refuse when data are missing.** EPA NowCast needs two of the last three hours. FishAI should refuse Q4 (individual movement) without tags, Q6 (larval connectivity) without a validated particle experiment, and Q7 (nowcast) without a current observation or a driver that has already beaten the baseline at that lead.

9. **Tags and particles.** Tagged animals describe tagged animals. CMS/OpenDrift/Ichthyop particles are not adult movement (MOVEMENT_METHOD_MATRIX; Bode et al. 2019, P312).

10. **Partnership data stay behind the policy.** OTN/ATN/Movebank embargoes exist because tracks are sensitive (S84–S86). Do not scrape them into a public globe.
