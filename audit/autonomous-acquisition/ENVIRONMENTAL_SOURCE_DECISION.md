# Environmental source decision

Biological events exist. External ocean fields are not joined to them.

| Source | What was done | Decision |
|---|---|---|
| Survey depth, visibility, habitat code | Used in the internal logistic baseline | Keep |
| MUR analysed SST, CoastWatch ERDDAP `jplMURSST41` | Metadata returned HTTP 200. A 0.1-degree box for 2022-06-15 was saved under `data/raw/environmental/` (5,186 bytes, SHA-256 `2a756464a59df45fed508433e6b89accbde8ba03d22d152913779ae0e890f385`) | Not joined. One day and a small box do not cover the three survey seasons |
| WCOFS | Not subset | Still a candidate after a biological join plan exists |
| Copernicus | No credentials in this run | `ACCOUNT_ACTION_REQUIRED` |

Survey habitat codes are the habitat layer for this feasibility fit. GEBCO was not downloaded. Reef presence was not inferred from bathymetry.

Next environmental action: extract SST, and a depth-relevant temperature if a public grid supports it, at the survey dates, inside protected storage, and score whether it beats the survey-only baseline on the same spatial blocks.
