"""Per-stratum nowcast-forcing verdict combination (pass_fail_thresholds.cutoffs)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from fishai.evaluation.harmonization_prereg import load_harmonization_prereg, pass_fail_thresholds_cutoffs

StratumVerdict = Literal["PASS", "DEGRADED", "UNKNOWN", "FAIL"]

NO_INDEPENDENT_OBS_CHECK = "no_independent_obs_check"
NO_INDEPENDENT_VALIDATION = "no_independent_validation"


@dataclass(frozen=True)
class StratumCombinationRules:
    combination_rule: str
    verdict_rank_worst_first: tuple[StratumVerdict, ...]
    input_verdict_variables: tuple[str, ...]
    failed_input_stratum_verdict: StratumVerdict
    not_gradable_cap_verdict: StratumVerdict
    not_gradable_cap_reason: str
    no_independent_validation_verdict: StratumVerdict
    no_independent_validation_reason: str


@dataclass(frozen=True)
class StratumCombinationInput:
    """Buoy and input verdicts for one stratum before combination."""

    has_independent_graded_variable: bool
    buoy_gradable: bool
    buoy_verdict: StratumVerdict | None
    input_verdicts: dict[str, StratumVerdict]


@dataclass(frozen=True)
class StratumCombinationResult:
    verdict: StratumVerdict
    reason: str | None = None


def stratum_combination_rules_from_prereg(
    doc: dict[str, Any] | None = None,
) -> StratumCombinationRules:
    raw = doc if doc is not None else load_harmonization_prereg()
    cutoffs = pass_fail_thresholds_cutoffs(raw)
    rule = cutoffs.get("combination_rule")
    if rule != "worst_of":
        raise ValueError(f"unsupported pass_fail_thresholds.cutoffs.combination_rule: {rule!r}")
    rank = tuple(cutoffs["verdict_rank_worst_first"])
    inputs = tuple(cutoffs["input_verdict_variables"])
    cap = cutoffs["not_gradable_cap"]
    niv = cutoffs["no_independent_validation"]
    return StratumCombinationRules(
        combination_rule=str(rule),
        verdict_rank_worst_first=rank,
        input_verdict_variables=inputs,
        failed_input_stratum_verdict=str(cutoffs["failed_input_stratum_verdict"]),
        not_gradable_cap_verdict=str(cap["verdict"]),
        not_gradable_cap_reason=str(cap["reason"]),
        no_independent_validation_verdict=str(niv["all_strata_verdict"]),
        no_independent_validation_reason=str(niv["reason"]),
    )


def _worst_verdict(
    verdicts: tuple[StratumVerdict, ...],
    rank: tuple[StratumVerdict, ...],
) -> StratumVerdict:
    if not verdicts:
        return "PASS"
    order = {v: i for i, v in enumerate(rank)}

    def key(v: StratumVerdict) -> int:
        if v not in order:
            raise ValueError(f"verdict {v!r} not in verdict_rank_worst_first")
        return order[v]

    return min(verdicts, key=key)


def combine_stratum_verdict(
    ctx: StratumCombinationInput,
    *,
    rules: StratumCombinationRules | None = None,
    doc: dict[str, Any] | None = None,
) -> StratumCombinationResult:
    """
    Apply auditbot1 ``combination_rule: worst_of`` for one stratum.

    A failed input (``FAIL`` or ``UNKNOWN``) forces stratum ``UNKNOWN``. When the
    buoy stratum is not gradable but every input passes, the not_gradable cap yields
    ``DEGRADED`` with ``no_independent_obs_check``.
    """
    r = rules if rules is not None else stratum_combination_rules_from_prereg(doc)
    missing = set(r.input_verdict_variables) - set(ctx.input_verdicts)
    if missing:
        raise ValueError(f"missing input verdicts for: {sorted(missing)}")
    extra = set(ctx.input_verdicts) - set(r.input_verdict_variables)
    if extra:
        raise ValueError(f"unexpected input verdict keys: {sorted(extra)}")

    if not ctx.has_independent_graded_variable:
        return StratumCombinationResult(
            verdict=r.no_independent_validation_verdict,
            reason=r.no_independent_validation_reason,
        )

    for var in r.input_verdict_variables:
        iv = ctx.input_verdicts[var]
        if iv in ("FAIL", "UNKNOWN"):
            return StratumCombinationResult(verdict=r.failed_input_stratum_verdict)

    input_only = tuple(ctx.input_verdicts[v] for v in r.input_verdict_variables)
    inputs_worst = _worst_verdict(input_only, r.verdict_rank_worst_first)

    if not ctx.buoy_gradable:
        if inputs_worst == "PASS":
            return StratumCombinationResult(
                verdict=r.not_gradable_cap_verdict,
                reason=r.not_gradable_cap_reason,
            )
        return StratumCombinationResult(verdict=inputs_worst)

    if ctx.buoy_verdict is None:
        raise ValueError("buoy_verdict required when buoy_gradable is True")

    combined = _worst_verdict(
        (ctx.buoy_verdict, *input_only),
        r.verdict_rank_worst_first,
    )
    if combined == "FAIL":
        return StratumCombinationResult(verdict=r.failed_input_stratum_verdict)
    return StratumCombinationResult(verdict=combined)
