test_that("R model tests do not modify data/provenance or artifacts trees", {
  after <- .fishai_tracked_repo_file_hashes()
  expect_equal(sort(names(after)), sort(names(FISHAI_REPO_TRACKED_BEFORE)))
  expect_equal(after, FISHAI_REPO_TRACKED_BEFORE)
})
