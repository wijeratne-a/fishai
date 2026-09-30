#' Load cruise/taxon review flags from CUFES QC report JSON (#4).
#' @export
load_cufes_review_flags <- function(path) {
  if (is.null(path) || !nzchar(path)) {
    return(NULL)
  }
  root <- Sys.getenv("FISHAI_ROOT", unset = normalizePath(getwd()))
  if (!grepl("^/", path)) {
    path <- file.path(root, path)
  }
  if (!file.exists(path)) {
    stop("cufes review flags path not found: ", path, call. = FALSE)
  }
  raw <- jsonlite::read_json(path, simplifyVector = TRUE)
  flags <- raw$cruise_taxon_review_flags
  if (is.null(flags)) {
    stop("QC report missing cruise_taxon_review_flags", call. = FALSE)
  }
  if (is.data.frame(flags)) {
    return(flags)
  }
  if (length(flags) == 0L) {
    return(data.frame(cruise = character(), taxon = character(), reason = character()))
  }
  do.call(rbind, lapply(flags, function(x) {
    data.frame(
      cruise = as.character(x$cruise),
      taxon = as.character(x$taxon),
      reason = as.character(x$reason),
      stringsAsFactors = FALSE
    )
  }))
}

#' Stop if the species taxon has any open review flag entries.
#' @export
assert_no_open_review_flags <- function(cfg) {
  path <- cfg$data$cufes_qc_report_path %||% cfg$data$review_flags_path
  if (is.null(path) || !nzchar(path)) {
    return(invisible(NULL))
  }
  taxon <- cfg$species$taxon
  if (is.null(taxon) || !nzchar(taxon)) {
    return(invisible(NULL))
  }
  flags <- load_cufes_review_flags(path)
  if (!nrow(flags)) {
    return(invisible(NULL))
  }
  hit <- flags[flags$taxon == taxon, , drop = FALSE]
  if (!nrow(hit)) {
    return(invisible(NULL))
  }
  cruises <- sort(unique(hit$cruise))
  stop(
    "open CUFES review flags for taxon=",
    taxon,
    " cruises: ",
    paste(cruises, collapse = ", "),
    call. = FALSE
  )
}
