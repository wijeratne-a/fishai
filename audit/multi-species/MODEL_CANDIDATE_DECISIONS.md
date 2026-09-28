# Model candidate decisions

Candidates were ranked inside each region. Training years exclude the latest year. A species needed at least 40 training detections, 8 holdout detections, prevalence between 0.05 and 0.90, and positives in at least two training blocks. Goliath grouper was excluded.

Fitted models use depth, visibility, year, and up to six habitat codes. The logistic model is compared with the training-set prevalence. It is accepted only when spatial-block Brier is better than prevalence and the untouched holdout is better on both Brier and log loss.

## Accepted

- Puerto Rico, *Stegastes partitus*, train 2016/2019/2021, holdout 2023. Holdout Brier 0.1953 versus prevalence 0.2046.
- Puerto Rico, *Sparisoma aurofrenatum*, same years. Holdout Brier 0.2324 versus prevalence 0.2484.

## Rejected

Florida Keys species were common in training and still failed. *Stegastes partitus*, *Sparisoma aurofrenatum*, and *Scarus iseri* lost to prevalence inside spatial blocks. *Acanthurus bahianus* and *Halichoeres bivittatus* lost on the 2024 holdout. *Halichoeres garnoti* was essentially tied and slightly worse on holdout Brier (0.1721 versus 0.1717).

USVI fits produced non-numeric scores. Those four models are rejected. They are not evidence of skill.

Flower Garden Banks has 38 events in 2024. *Stegastes planifrons* lost on spatial blocks. *Paranthias furcifer* lost on the holdout. Neither is accepted.

No environmental covariate was joined, so none of these models is a nowcast.
