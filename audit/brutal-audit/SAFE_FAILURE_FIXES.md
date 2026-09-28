# Safe failure fixes

Applied this audit:

1. SST join refuses offsets after the survey date.
2. Feature design refuses missing depth or visibility instead of inventing 15.
3. Training mask is `year in TRAIN_YEARS`, not `year < holdout`.
4. Logistic fit rejects non-finite coefficients.
5. UI label is not “Where now.”
6. CURRENT_STATUS marked STALE.
7. Disagreed score tables quarantined as UNTRUSTED_RESULT.

Not applied (requires scientific re-run, forbidden on 2023):

- Re-score locked species after removing future SST.
- Re-fit 16 species with L2.
- Independent holdout year.
- Event-location SST.
- Year-list completeness checksum against publisher list file.
