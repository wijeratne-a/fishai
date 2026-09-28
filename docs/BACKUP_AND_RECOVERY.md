# Backup and recovery

## Policy

A backup is **not** claimed until a restore test succeeds. Git ignore of `data/raw/` isolates raw bytes from the repository; that isolation is **not** a backup.

## Current state

| Item | Value |
|------|-------|
| Last restore result | `PASS` |
| Last successful backup | `claimed after restore checksum match` |
| Restore test script | `scripts/storage/restore_test.py` |
| Off-repo snapshot | `/Users/wijeratne/dev/fishai-offrepo-snapshots/20260926T230633Z` |

## Procedure

1. Snapshot non-coordinate files with `scripts/storage/snapshot_non_coordinate.py`.
2. Restore one metadata file and one non-coordinate test object.
3. Compare SHA-256 to the working copies.
4. Record `PASS` or `FAIL` in `audit/storage/`.

Survey coordinates are not copied into Git or the snapshot allow-list.

