"""Preferential-sampling diagnostic (report-only; does not change model fits)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class PreferentialSamplingReport:
    """Summary comparing sampled locations to the reference grid."""

    n_sampled: int
    n_grid: int
    mean_covariate_sampled: float
    mean_covariate_grid: float
    sampling_intensity_ratio: float
    sampled_to_grid_mean_ratio: float
    label: str = "preferential_sampling_diagnostic_report_only"

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "n_sampled": self.n_sampled,
            "n_grid": self.n_grid,
            "mean_covariate_sampled": self.mean_covariate_sampled,
            "mean_covariate_grid": self.mean_covariate_grid,
            "sampling_intensity_ratio": self.sampling_intensity_ratio,
            "sampled_to_grid_mean_ratio": self.sampled_to_grid_mean_ratio,
            "note": "Reporting only; no change to sdmTMB fit.",
        }


def compute_preferential_sampling_report(
    covariate_at_sampled: np.ndarray,
    covariate_on_grid: np.ndarray,
    *,
    sampling_weights: np.ndarray | None = None,
    grid_weights: np.ndarray | None = None,
) -> PreferentialSamplingReport:
    """
    Compare covariate / latent-proxy values at sampled vs grid locations.

    ``sampling_intensity_ratio`` is total sampled weight divided by total grid
    weight (uniform weights when omitted). Values far from 1 with divergent means
    suggest preferential sampling relative to the latent field proxy.
    """
    samp = np.asarray(covariate_at_sampled, dtype=float).ravel()
    grid = np.asarray(covariate_on_grid, dtype=float).ravel()
    if samp.size == 0 or grid.size == 0:
        raise ValueError("covariate arrays must be non-empty")
    w_s = np.ones(samp.shape[0], dtype=float)
    w_g = np.ones(grid.shape[0], dtype=float)
    if sampling_weights is not None:
        w_s = np.asarray(sampling_weights, dtype=float).ravel()
    if grid_weights is not None:
        w_g = np.asarray(grid_weights, dtype=float).ravel()
    if w_s.shape != samp.shape or w_g.shape != grid.shape:
        raise ValueError("weight shapes must match covariate arrays")
    mean_s = float(np.average(samp, weights=w_s))
    mean_g = float(np.average(grid, weights=w_g))
    intensity = float(w_s.sum() / w_g.sum())
    ratio = mean_s / mean_g if mean_g != 0.0 else float("nan")
    return PreferentialSamplingReport(
        n_sampled=int(samp.size),
        n_grid=int(grid.size),
        mean_covariate_sampled=mean_s,
        mean_covariate_grid=mean_g,
        sampling_intensity_ratio=intensity,
        sampled_to_grid_mean_ratio=ratio,
    )
