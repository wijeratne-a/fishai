# Restore verification

**As of:** 2026-09-26T23:06:33Z
**Status:** `PASS`
**Claim:** `BACKUP_VERIFIED`

## Findings

| Item | Value |
|---|---|
| Separate backup location | `/Users/wijeratne/dev/fishai-offrepo-snapshots/20260926T230633Z` |
| Last restore result | `PASS` |
| Claim allowed | **yes** |
| Raw survey copy performed | **no** |
| Coordinates in this report | **no** |

## Restored objects

| Object | Result | Detail |
|---|---|---|
| `data/metadata/noaa-rvc-erddap-metadata.csv` | `PASS` | sha256_match |
| `data/metadata/RESTORE_TEST_OBJECT.json` | `PASS` | sha256_match |

## Policy

Git ignore of `data/raw/` is isolation, not a backup.
A backup is claimed only after an off-repo restore checksum matches.
Survey coordinates were not copied into Git or this report.

