# Zero semantics audit

## What the Atlantic RVC source actually is

`NUM` is a real-valued average per length-bin row on a completed stationary point count. Multiple rows per species exist because of length bins. Publisher zeros are on those rows.

Correct species-level construction (already stated in `labels/OBSERVATION_SEMANTICS.md`):

- Detection: any length-bin `NUM > 0` for a code on a completed event.
- Non-detection: the code is on that year’s list **and** every length-bin row is `NUM == 0`.
- Missing code with no year-list membership: `NOT_EVALUATED`, not a zero.

## What the modeling code actually does

`load_puerto_rico_events` / `load_region` walk every row, add the code to `universe[year]`, and add the code to `pos` if `NUM > 0`. Label is `1 if code in pos else 0` **if the code is in that year’s universe**.

That matches constructed survey non-detection **if and only if** the downloaded table contains the full year species list, including explicit zero rows. Atlantic ERDDAP extracts were previously shown to do that. Pacific COUNT extracts do not.

## Defects that survive

1. **Universe is inferred from whatever rows arrived**, not from an independent published species list. A truncated download that dropped zero rows would silently convert missing species to non-detections. There is no checksum-gated “list complete” assertion inside the fit scripts.
2. **A single length-bin zero is never stored as the species result** (good), but **`NUM` is never used as a magnitude** after the `> 0` test. That is correct for detection. It is incorrect if anyone later reads `train_detections` as abundance.
3. **Survey zero is still a 0/1 target named `y`.** Reports say “not ecological absence.” The numeric target is still fed to log loss as if it were a Bernoulli presence/absence process. The *claim* is detection; the *likelihood* is written as if the 0s were clean absences.
4. **RLS Method 1 sample and DATRAS HL** in the 50% path had **no explicit zero rows**. DFO `TOTNO==0` rows exist. Those programs must not share a zero constructor with Atlantic RVC.

## Invalidation

Puerto Rico 0/1 labels are **conditionally valid** on the Atlantic extracts remaining complete year-lists. They are **not** ecological absence. Any sentence that says the model “knows where the fish are not” is false.
