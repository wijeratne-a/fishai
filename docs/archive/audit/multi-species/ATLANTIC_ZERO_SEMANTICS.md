# Atlantic zero semantics

Status for every validated Atlantic year: `MODEL_READY_WITH_RESTRICTIONS`.

Restrictions:

- A zero row means that species code was on the year’s survey list and the published `NUM` for that row was 0.
- Several rows can belong to one species because of length. The species was detected if any of those rows had `NUM > 0`.
- `NUM` is not an integer count of fish.
- A survey non-detection is not ecological absence.
- Cross-year models may use a species only when its code is on each year’s list.

No Atlantic year in this set had an unresolved event key or a missing zero pattern inside the year.
