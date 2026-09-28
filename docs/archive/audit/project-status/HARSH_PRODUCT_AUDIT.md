# Harsh product audit

**Date:** 2026-09-26  
**Goal judged:** track any fish, anywhere, at any time, for all species, with accuracy above 80%, so someone can find where fish and seafood are.  
**Verdict:** This product will not work for that goal. It does not work now, and continuing the current plan will not get it there.

## The short version

FishAI today is a globe that shows past reports and says "unknown," plus one internal test in Puerto Rico. That test estimates whether divers recorded two common reef fish on a finished survey. It beats the historical detection rate by one to one and a half hundredths of a Brier point. It does not follow a fish, count fish, cover the ocean, use live data, or tell anyone where to go.

The data in this project cannot answer "where is this fish right now." Reef surveys run roughly every two years at randomly chosen sites. The public tables end in 2023 or 2024. Recent presence reports in the Florida Keys end on 23 July 2026. A survey zero means "not recorded on that dive." None of that is a live position.

## Why "above 80%" is the wrong test

Accuracy rewards guessing the most common answer.

- Bicolor damselfish was recorded on 178 of 248 Puerto Rico surveys in 2023. A rule that always says "present" is right about 72% of the time with no model at all.
- Redband parrotfish was recorded on 150 of 248, so "always present" is right about 60% of the time.
- Goliath grouper was recorded on 8 of 2,113 Florida Keys surveys across 2018, 2022, and 2024. A rule that always says "absent" is right more than 99% of the time and tells you nothing.

So 80% accuracy is exceeded for rare fish by a rule that knows nothing, and nearly reached for common fish the same way. The project has never measured accuracy for "where every fish is right now," because no dataset contains that answer. The honest scores are Brier and log loss compared with a baseline. On those, the Puerto Rico improvement is small.

## What the project can and cannot say today

It can say, internally:

- On a completed Puerto Rico reef survey, a simple model predicts detection of bicolor damselfish and redband parrotfish slightly better than their historical average. On 2023, Brier was 0.195 versus 0.205, and 0.233 versus 0.248.
- Where people have reported a species in the past, at a coarse grid.
- That most of the ocean is unknown for any given species.

It cannot say:

- Where any individual fish is.
- How many fish there are.
- What will be there tomorrow or next week.
- Anything useful outside four Atlantic reef areas.
- Anything about most commercial seafood species.
- Where to fish, dive, or harvest.

## Top ten problems

1. **The goal does not match the data.** Every biological source here is a scheduled survey, an egg sample, or an old presence report. Following individual fish requires tags on those fish. Tags cover a small number of animals, are often sensitive, and are not public at scale. No public source records all fish.

2. **Almost every model failed.** Sixteen species models were scored on an untouched year. Fourteen failed: all six Florida Keys species, both Flower Garden Banks species, and four U.S. Virgin Islands species whose fits produced non-numeric scores.

3. **The two passes are marginal.** Bicolor damselfish improved from 0.205 to 0.195 Brier. Redband parrotfish improved from 0.248 to 0.233. Adding sea-surface temperature for all 174 Puerto Rico survey dates made both slightly worse. There is no evidence yet that ocean conditions improve these predictions.

4. **Nothing is live.** Surveys are roughly biennial, and the public reef tables end in 2023 or 2024. OBIS reports in the Keys box end on 23 July 2026. No forecast ocean grid is saved: the RTOFS search returned HTTP 404, WCOFS was never subset, and Copernicus needs credentials the project does not have. A nowcast needs current conditions that improve the model. The only one tested did not.

5. **Coverage is a sliver of the ocean.** Usable zero-bearing surveys exist for the Florida Keys, Puerto Rico, the U.S. Virgin Islands, and Flower Garden Banks. The Pacific tables have counts and no zeros. There is one CalCOFI egg sample of about 418 rows. There are no national trawl programs, no other countries, and no 2025 reef files.

6. **The original flagship species cannot be modeled.** Goliath grouper had 1, 1, and 6 detection events in the 2018, 2022, and 2024 Keys files. Its known gathering sites are exactly the locations the project must withhold.

7. **Rights are unsettled and inconsistent.** The Reef Visual Census rights record still says `CONDITIONAL_REVIEW_REQUIRED`. The later ERDDAP downloads were classed `AUTO_ACQUIRE_INTERNAL_ONLY` because the metadata lists no use constraints and does not grant a published model. The outreach register shows both permission letters as `NOT_SENT`. Florida training used the 2018 season, accession 0208321, after the project had set that accession aside. Nothing is cleared for public display.

8. **The work is fragile.** The last commit is `0bf64b5`, the globe stabilization. Git status lists 50 uncommitted or untracked entries, which include the acquisition scripts, models, tests, and most audits. No remote is configured. No backup restore has succeeded. The earlier 16 fits have no recorded commit, seed, or output hash. The final Puerto Rico run does have a manifest, with seed 20260926 and file checksums.

9. **The predictors that matter are missing.** Reef and bottom fish respond to bottom temperature, oxygen, substrate, structure, and prey. The models use depth, visibility, year, and habitat code from the survey itself, plus sea-surface temperature that did not help. The rest is not in the project.

10. **Paperwork grew faster than the science.** Dozens of plans, schemas, and audits came out of parallel workstreams, while the validated science output is two internal survey-detection baselines. The multi-species suite used a hand-written logistic regression with a fixed number of gradient steps and no convergence check, which produced the non-numeric U.S. Virgin Islands results. The globe still has an unverified focus ring, drag, pinch, and tilt, a logged map stall that was never reproduced, and no display of valid time, model version, or extrapolation.

## Top ten strengths

1. **The map does not lie.** A current estimate or forecast is drawn only for a published card with the matching flag. No card is published, so nothing invented is drawn.

2. **Unknown is the default.** Empty ocean is shown as unknown, and past reports are labeled as past.

3. **Real survey data with real zeros.** Multi-year Reef Visual Census tables for four Atlantic areas are on disk. The checksum check matched all 25 recorded files.

4. **The data meaning was worked out correctly.** `NUM` is an average, not a count. Length bins are collapsed before a detection is called. A species code counts as a non-detection only in years whose list includes it. A survey miss is not treated as absence from the reef.

5. **Validation was honest.** Models trained on earlier years, the latest year was scored once, and the failures were reported.

6. **Negative results were accepted.** When sea-surface temperature did not help, it was dropped.

7. **Sensitive locations are protected.** Goliath sites, wrecks, nurseries, and tracks are not stored. Raw coordinates stay in ignored folders, and the sensitivity scan passed.

8. **Evidence types stay separate.** OBIS presence was never used as a training absence. Pacific zeros were not invented. Egg counts stay eggs.

9. **Guardrails are tested.** Label, unit, time, contract, evaluation, failure-recovery, and synthetic end-to-end suites passed when last run. They include tests that reject surface temperature as a fish sighting and reject an unpublished card as a probability layer.

10. **Acquisition is scripted and watched.** Downloads, validation, and a 2025 release watcher run from scripts with manifests, so new NOAA years can be added without hand edits.

## What could actually work

A narrow tool can work: the probability that a named, common species is recorded on a documented survey, in one region, for a stated year, with its uncertainty and a baseline shown beside it. That tool exists in draft for two Puerto Rico reef fish. It is a scientific estimate. It is not a fish finder, and tracking every fish everywhere at 80% accuracy is not a goal this data, or any public data, can meet.
