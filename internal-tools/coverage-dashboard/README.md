# Internal coverage dashboard (counts only)

Static region/year coverage counts for Atlantic RVC frames on disk (from project status / protocol matrix). **No map points. No coordinates.**

## Files

| File | Role |
|---|---|
| `coverage_counts.md` | Markdown table of region × year counts |
| `coverage_counts.html` | Small static HTML view of the same counts |

## Source of counts

Years listed are those documented as on disk for Florida Keys, Puerto Rico, USVI, and Flower Garden Banks. Event counts come from `audit/multi-species/ATLANTIC_PROTOCOL_MATRIX.csv` `events` column (frame-level event totals, not species detections).

## Rules

- Counts only — no lat/lon, no GeoJSON, no map tiles.
- Does not read `data/raw/`.
- Does not promote internal models to published layers.
