# Account actions required

No account was created. No identity was invented.

| Source | What happened | Action |
|---|---|---|
| GBIF occurrence search | `GET /v1/occurrence/search` returned a count without credentials | Bulk occurrence download still needs a GBIF account. Mark `ACCOUNT_ACTION_REQUIRED` for a bulk job. Do not download millions of rows through the search API. |
| Copernicus Marine | No credentials in the environment | Leave unused |
| NOAA ERDDAP reef-fish tables | No account required | Already used |
| OBIS occurrence API | No account required for the bounded request | Already used |
| CoastWatch RTOFS search | HTTP 404, not an authentication wall | Find a current forecast dataset id before another attempt |
