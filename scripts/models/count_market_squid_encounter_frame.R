#!/usr/bin/env Rscript
source(file.path("src", "models", "tests", "testthat", "helper.R"))
load_fishaisdm()
cfg <- load_config_yaml("configs/models/cps_market_squid_encounter.yaml")
dat <- load_model_data(cfg = cfg, min_duration_min = 2)
cat(
  jsonlite::toJSON(
    list(
      n_rows = nrow(dat),
      n_presence = sum(dat$y > 0),
      n_absence = sum(dat$y <= 0)
    ),
    auto_unbox = TRUE
  ),
  "\n"
)
