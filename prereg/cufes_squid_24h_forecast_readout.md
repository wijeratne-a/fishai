This is a pipeline validation check for market squid CUFES egg encounter. It is not a published forecast, not nowcast skill for operations, and not harvest or fishery advice.

Operational scores use physics_source damped_anomaly_proxy with operational_claim NOT_ISSUED_FORECAST. No issued WCOFS (or other) archive overlaps the egg record through 2022-04-27.

squid at 24 hours: the NOT_ISSUED_FORECAST proxy does not beat both baselines. That comparison uses 106 tows, 30 of them with eggs. AUC 0.792 versus persistence 0.738 and climatology 0.682. TSS 0.354 versus persistence 0.362 and climatology 0.127.

At 48 hours (79 tows, 20 with eggs) the NOT_ISSUED_FORECAST proxy AUC is 0.405, a change of -0.387 from 24 hours, and TSS is -0.121, a change of -0.476. At 72 hours (45 tows, 21 with eggs) the proxy AUC is 0.903, a change of +0.111, and TSS is 0.726, a change of +0.372.

If the analysed ocean state is treated as known (a retrospective ceiling, not the product), 24-hour AUC is 0.795 and TSS is 0.354. That ceiling is not the 72-hour product.
