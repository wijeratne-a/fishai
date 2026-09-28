# Failure-recovery audit notes

Policy source: `operations/SCIENTIFIC_FAILURE_POLICY.md`.

## Verified by tests

- Safe tokens: `UNKNOWN`, `UNAVAILABLE`, `INSUFFICIENT_DATA`, `STALE`, `UNSUPPORTED`, `WITHHELD`.
- Failed model for species X must not be replaced by species Y.
- Safe tokens are not numeric probabilities.

## Not claimed

- No production globe wiring of these tokens in this workstream.
- No restore/backup success.
