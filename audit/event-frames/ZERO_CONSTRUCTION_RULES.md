# Zero construction rules

## Atlantic RVC (Florida Keys, Puerto Rico, USVI, Flower Garden Banks)

- Frame status: `CONSTRUCTIBLE_NONDETECTION` at species level.
- `NUM` is a real-valued average, not an integer fish count.
- Length bins produce multiple rows per species on one event. Detection = any row for that species code has `NUM > 0`. Non-detection = the code is on that year’s species list and every row for the code has `NUM == 0`.
- Do not sum `NUM` across length bins.
- A survey non-detection is not ecological absence.
- A code is a non-detection only in years that list it.

## Pacific RVC (Hawaii, American Samoa, CNMI/Guam, PRIAs)

- Downloaded `COUNT` tables contained no zero rows.
- Status: `PRESENCE_ONLY` / `COUNT_MODEL_ONLY`.
- Do not invent non-detections from species that never appear; the search universe is not published in these extracts.

## OBIS Keys extract

- Presence reports only. Not equivalent to RVC zeros. Do not use as absence.
