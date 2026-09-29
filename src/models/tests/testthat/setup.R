.fishai_tracked_repo_file_hashes <- function() {
  bases <- c(
    file.path(FISHAI_ROOT, "data", "provenance"),
    file.path(FISHAI_ROOT, "artifacts")
  )
  out <- character()
  for (base in bases) {
    if (!dir.exists(base)) {
      next
    }
    files <- list.files(base, recursive = TRUE, full.names = TRUE)
    files <- files[!file.info(files)$isdir]
    for (f in sort(files)) {
      rel <- sub(paste0("^", FISHAI_ROOT, "/?"), "", normalizePath(f, winslash = "/"))
      out[[rel]] <- as.character(tools::md5sum(f))
    }
  }
  out
}

FISHAI_REPO_TRACKED_BEFORE <- .fishai_tracked_repo_file_hashes()
