# Habitat source limitations

- `HABITAT_CD` on NOAA RVC tables is an **observed** field recorded on the survey dive. It describes the sampled station, not a continuous habitat map.
- **GEBCO** (and similar bathymetry) is a **bathymetric derivative** source. Depth or slope is not reef evidence and must not be treated as coral-reef presence.
- GEBCO was **not downloaded** in this run. No licensed reef-habitat grid is in the training path.
- Do not infer reef absence or presence from bathymetry alone.
