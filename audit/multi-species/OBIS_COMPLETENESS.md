# OBIS completeness

The occurrence API ignored `skip`, `offset`, `from`, and `page` on this query. The same first record came back.

The 672-record total was recovered by four sequential date windows, each small enough to return in one response:

| Window | Reported | Returned |
|---|---:|---:|
| 2026-06-26 to 2026-07-02 | 161 | 161 |
| 2026-07-03 to 2026-07-09 | 167 | 167 |
| 2026-07-10 to 2026-07-16 | 254 | 254 |
| 2026-07-17 to 2026-07-23 | 90 | 90 |

Unique records saved: 672. Reported total for 2026-06-26 onward: 672. Nothing in the box is dated after 2026-07-23.

These records were not added to the RVC training table.
