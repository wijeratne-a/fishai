# Data storage architecture

FishAI keeps survey and environmental **raw** bytes out of Git and treats them as immutable once acquired.

## Zones

| Zone | Path | Role |
|------|------|------|
| Raw (immutable) | `data/raw/` | Original downloads; gitignored; never rewritten in place to “fix” validation |
| Interim / staging | `data/interim/` | Working transforms; gitignored |
| Restricted | `data/restricted/` | Rights-limited or sensitive extracts; gitignored |
| Processed | `data/processed/` | Derived tables safe for internal use under policy |
| Metadata | `data/metadata/` | Non-coordinate metadata extracts |
| Manifests | `data/manifests/` | Provenance, checksums, queue state (no raw coordinate columns) |
| Quarantine | `data/quarantine/` | Failed model-eligibility copies; raw zone is never edited |

## Rules

1. **Raw is immutable and gitignored.** `.gitignore` lists `data/raw/`, `data/interim/`, and `data/restricted/`.
2. **Checksums live in manifests**, not as a claim that Git holds the bytes.
3. **Do not force raw files into Git.** Content-addressed or external backup may be added later; this document does not assert that a backup already exists.
4. **Tracked trees must not carry raw lat/lon CSV headers** (see `security/`).

## Verification

Use `scripts/storage/verify_checksums.py` against acquisition and structured-survey manifests when those files exist.
