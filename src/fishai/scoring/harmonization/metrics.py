"""Bias, RMSE, Pearson r, and moving-block bootstrap CIs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class MetricResult:
    n: int
    bias: float
    rmse: float
    pearson_r: float
    bias_ci95: tuple[float, float]
    rmse_ci95: tuple[float, float]
    pearson_r_ci95: tuple[float, float]


def _pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2:
        return float("nan")
    xc = x - np.mean(x)
    yc = y - np.mean(y)
    denom = np.sqrt(np.sum(xc ** 2) * np.sum(yc ** 2))
    if denom == 0:
        return float("nan")
    return float(np.sum(xc * yc) / denom)


def point_metrics(obs: Sequence[float], pred: Sequence[float]) -> tuple[int, float, float, float]:
    o = np.asarray(obs, dtype=float)
    p = np.asarray(pred, dtype=float)
    mask = np.isfinite(o) & np.isfinite(p)
    o = o[mask]
    p = p[mask]
    n = int(o.size)
    if n == 0:
        return 0, float("nan"), float("nan"), float("nan")
    err = p - o
    bias = float(np.mean(err))
    rmse = float(math.sqrt(np.mean(err ** 2)))
    r = _pearson_r(o, p)
    return n, bias, rmse, r


def _block_indices(dates: np.ndarray, block_days: int) -> list[np.ndarray]:
    """Group observation indices into contiguous calendar-day blocks of length block_days."""
    if dates.size == 0:
        return []
    order = np.argsort(dates)
    sorted_dates = dates[order]
    blocks: list[list[int]] = []
    current: list[int] = [int(order[0])]
    block_start = sorted_dates[0]
    for pos in range(1, sorted_dates.size):
        idx = int(order[pos])
        d = sorted_dates[pos]
        if (d - block_start).astype("timedelta64[D]").astype(int) >= block_days:
            blocks.append(current)
            current = [idx]
            block_start = d
        else:
            current.append(idx)
    blocks.append(current)
    return [np.asarray(b, dtype=int) for b in blocks]


def moving_block_bootstrap_ci(
    obs: Sequence[float],
    pred: Sequence[float],
    dates: Sequence[np.datetime64],
    *,
    block_days: int,
    seed: int,
    n_boot: int = 500,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    o = np.asarray(obs, dtype=float)
    p = np.asarray(pred, dtype=float)
    d = np.asarray(dates, dtype="datetime64[D]")
    blocks = _block_indices(d, block_days)
    if not blocks:
        nan = (float("nan"), float("nan"))
        return nan, nan, nan
    rng = np.random.default_rng(seed)
    biases: list[float] = []
    rmses: list[float] = []
    rs: list[float] = []
    n_blocks = len(blocks)
    for _ in range(n_boot):
        chosen = rng.integers(0, n_blocks, size=n_blocks)
        idx = np.concatenate([blocks[int(c)] for c in chosen])
        _, b, r, pr = point_metrics(o[idx], p[idx])
        biases.append(b)
        rmses.append(r)
        rs.append(pr)
    def pct(arr: list[float], lo: float, hi: float) -> tuple[float, float]:
        a = np.asarray([x for x in arr if np.isfinite(x)], dtype=float)
        if a.size == 0:
            return (float("nan"), float("nan"))
        return (float(np.percentile(a, lo)), float(np.percentile(a, hi)))

    return pct(biases, 2.5, 97.5), pct(rmses, 2.5, 97.5), pct(rs, 2.5, 97.5)


def compute_metrics(
    obs: Sequence[float],
    pred: Sequence[float],
    dates: Sequence[np.datetime64],
    *,
    block_days: int,
    seed: int,
) -> MetricResult:
    n, bias, rmse, r = point_metrics(obs, pred)
    b_ci, r_ci, pr_ci = moving_block_bootstrap_ci(
        obs, pred, dates, block_days=block_days, seed=seed
    )
    return MetricResult(
        n=n,
        bias=bias,
        rmse=rmse,
        pearson_r=r,
        bias_ci95=b_ci,
        rmse_ci95=r_ci,
        pearson_r_ci95=pr_ci,
    )
