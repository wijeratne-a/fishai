# Transferability warnings

## Region and frame

- Atlantic RVC zero-bearing tables are not interchangeable with Pacific positive-count extracts. Non-detections cannot be constructed for Pacific Hawaii, American Samoa, CNMI/Guam, or Pacific Remote Islands tables in this repo.
- Cross-region pooling mixes protocols, list membership by year, and zero semantics. A Puerto Rico holdout pass does not transfer to Florida Keys, USVI, or Flower Garden Banks.
- Survey non-detection is not proof of absence from the surrounding reef.

## Guild and depth

- Predictors that matter for reef visual detection (visibility, hard-bottom/`HABITAT_CD`, survey depth) are not demersal bottom-temperature mechanisms and are not pelagic front mechanisms.
- Analysed sea-surface temperature (`jplMURSST41`) is skin/near-surface. It does not transfer as a bottom-temperature substitute for demersal guilds.
- GEBCO bathymetry, if ever acquired, is not reef evidence and must not be painted as presence.

## Time class

- Historical joins, current snippets, and forecast grids are separate. A 2026-09-23 MUR snippet is not a survey-date match and is not a forecast.
- Models that pass a past-year holdout are not nowcasts. The two Puerto Rico baselines are historical detection models only.
- WCOFS was not acquired. RTOFS CoastWatch search returned HTTP 404. Copernicus needs an account. No forecast transfer path exists in-repo.

## Evidence type

- OBIS presence-only coastal-biased records are not RVC effort frames and must not be transferred into RVC `y`.
- Internal survey-only baselines do not license globe publication or species-card `PUBLISHED` status.
- Pattern-level ecological hypotheses are not validated transfer functions until tested under the priority rules with verified predictors.
