test_that("open review flags block hake but not sardine or anchovy", {
  flags <- file.path(FISHAI_ROOT, "src", "models", "tests", "fixtures", "synthetic_cufes_review_flags.json")
  mk <- function(taxon) {
    base <- if (taxon == "anchovy") {
      file.path(FISHAI_ROOT, "configs", "models", "cufes_anchovy_synthetic.yaml")
    } else {
      file.path(FISHAI_ROOT, "configs", "models", "cufes_sardine_synthetic.yaml")
    }
    cfg <- load_config_yaml(base)
    cfg$species$taxon <- taxon
    cfg$data$cufes_qc_report_path <- flags
    cfg
  }
  expect_error(load_model_data(cfg = mk("hake")), "open CUFES review flags for taxon=hake")
  expect_no_error(load_model_data(cfg = mk("sardine")))
  expect_no_error(load_model_data(cfg = mk("anchovy")))
})
