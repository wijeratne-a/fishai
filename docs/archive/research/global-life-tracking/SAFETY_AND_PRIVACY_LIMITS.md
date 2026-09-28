# Safety and privacy limits

## Principle

The more precise and current a location is, the more harm it can cause. Precision, freshness, and sensitivity trade against each other. For some species the only safe output is none.

## Documented risks

- **Tracking data can be used to find and harm animals.** Researchers have described cases and risks of telemetry being exploited (Cooke et al. 2017, S84) and proposed frameworks to protect animal data (Lennox et al. 2020, S85).
- **Biodiversity portals generalize sensitive locations** before public release (Chapman 2020, S86).
- **Model outputs leak.** A high-probability cell for an aggregating species can reveal a spawning site. Repeated queries at fine resolution can triangulate points. Combining a coarse map with outside knowledge, such as known wreck locations, can recover a site.

## Human privacy as an analogy

FishAI does not process human location data. The analogy only informs design.

- Four spatiotemporal points were enough to uniquely identify 95 percent of individuals in a large mobility dataset (de Montjoye et al. 2013, S87). Sparse points are more identifying than they look.
- **k-anonymity** requires every released group to contain at least k records (Sweeney 2002, S89). The FishAI analogue is a minimum number of survey events behind any displayed cell.
- **Differential privacy** adds calibrated noise so that one record cannot be inferred from outputs (Dwork 2006, S88). The FishAI analogue is coarsening and delay for sensitive taxa.
- Project documents record the U.S. practice of releasing confidential fishery data only when aggregated from at least three vessels.

## Controls

| Control | Use |
|---|---|
| Withhold | Sensitive taxa such as goliath grouper and white shark; spawning, nursery, wreck, and aggregation sites |
| Coarsen | Public cells chosen with a sensitivity review, never finer than the evidence supports |
| Delay | Recent detections of sensitive species shown only after a delay, if at all |
| Aggregation threshold | Minimum number of survey events per displayed cell |
| Access tiers | Raw coordinates only in protected storage; never in the browser, fixtures, or reports |
| No real-time display | For sensitive species under any circumstance |
| No tracks or receivers | Individual tracks and receiver locations are never shown |
| Query limits | Prevent reconstruction by repeated fine queries |
| Evidence labels | Every output says what it is and what it is not |

## Current FishAI rules

- Goliath grouper and white shark locations are withheld.
- Raw survey coordinates stay in gitignored folders, and the sensitivity scan passed.
- AIS is never used as fish location.
- No fishing, harvest, or spearing guidance is given.
- Unpublished model cards cannot draw probability layers.

## Limits that engineering cannot remove

- Published data cannot be recalled.
- Aggregates can be combined with outside knowledge to recover sites.
- A coarse map of an aggregating species can still guide harvest.

For those cases, withholding is the control that works.
