# Sensitive data policy

Short rules for FishAI acquisition and repository hygiene.

1. **Do not commit raw coordinates.** Precise survey, receiver, wreck, nursery, spawning, aggregation, or telemetry locations belong only under gitignored zones (`data/raw/`, `data/interim/`, `data/restricted/`), never in tracked audit, docs, scripts, manifests, processed, or metadata trees.
2. **Do not commit credentials.** No API tokens, passwords, private URLs with embedded secrets, `.env` contents, or key material in git.
3. **Do not commit telemetry tracks or sensitive site lists.** Spawning aggregations, nursery habitat, wrecks, artificial reefs, and private fishing locations are withholdable; do not publish point maps of them.
4. **Environmental fields are not fish.** SST, chlorophyll, currents, and habitat layers are conditions—not biological observations or abundance.
5. **No fishing guidance.** Do not provide harvest, catch, spearing, or “where to fish” advice from maps or models.
6. **No nowcast claims during acquisition.** Acquiring or validating files is not a published nowcast or forecast.

Run `security/precommit_sensitive_scan.py` before commits. Fail closed on credential patterns or latitude/longitude CSV headers outside protected data zones.
