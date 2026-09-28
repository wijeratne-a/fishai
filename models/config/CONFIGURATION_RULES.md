# Model experiment configuration rules

**Schema:** `models/config/MODEL_EXPERIMENT_SCHEMA.json`  
**Template:** `models/config/EXPERIMENT_TEMPLATE.yaml`  
**Status:** Declarative contracts only. **Do not run a real experiment from these files.**

## Hard rejects

| Rule | Reject when |
|---|---|
| Presence-only is not absence | `label_semantics=PRESENCE_ONLY_NO_ABSENCE` and `treat_presence_only_as_absence=true`, or inventing zeros from presence-only gaps |
| Baseline required | `baseline` missing, or `baseline_id` / `baseline_kind` empty |
| No tune on final holdout | `holdout_year` appears in `tuning_years`, or `allow_tune_on_holdout=true` |
| Protocols are not mixed | `mix_protocols=true`, or `additional_protocol_ids` is non-empty |
| Run manifest required | `require_run_manifest` is missing or false |

## Locked example holdout

**Puerto Rico 2023** is the locked example holdout in the template comments and default `holdout_year`. It is for one-shot scoring of accepted internal baselines only — **not a refit**, not a tuning fold, not a publication trigger.

## Publication

Template configs remain `publish_status=NOT_PUBLISHED`. Internal baselines are not published nowcasts.
