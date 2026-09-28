# Fix now

1. Block SST offsets after survey date (LEAK-001).
2. Refuse missing depth/visibility (SEM-001).
3. Train only on explicit TRAIN_YEARS (ML-006).
4. Reject non-finite logistic coefficients (ML-001).
5. Rename UI “Where now” (UI-001).
6. Mark CURRENT_STATUS stale (UI-004).
7. Quarantine disagreed score tables (SEM-002).
8. Tests that make 1–4 fail the build if reintroduced.

Do not rescore 2023. Do not retune MUR. Do not publish.
