"""Advection–taxis post-processing for gridded SDM suitability (24 h GLORYS currents)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter


@dataclass(frozen=True)
class AdvectionGrid:
    """Regular grid in UTM km (EPSG:32611)."""

    x_km: np.ndarray  # shape (nx,)
    y_km: np.ndarray  # shape (ny,)
    s: np.ndarray  # suitability S, shape (ny, nx)
    u_ms: np.ndarray  # eastward velocity, shape (ny, nx)
    v_ms: np.ndarray  # northward velocity, shape (ny, nx)

    @property
    def dx_km(self) -> float:
        if self.x_km.size < 2:
            return 10.0
        return float(np.median(np.diff(self.x_km)))

    @property
    def dy_km(self) -> float:
        if self.y_km.size < 2:
            return 10.0
        return float(np.median(np.diff(self.y_km)))


def _bilinear_at(x: float, y: float, grid: AdvectionGrid, field: np.ndarray) -> float:
    xs = grid.x_km
    ys = grid.y_km
    if x < xs[0] or x > xs[-1] or y < ys[0] or y > ys[-1]:
        return float("nan")
    ix = int(np.searchsorted(xs, x) - 1)
    iy = int(np.searchsorted(ys, y) - 1)
    ix = max(0, min(ix, len(xs) - 2))
    iy = max(0, min(iy, len(ys) - 2))
    x0, x1 = xs[ix], xs[ix + 1]
    y0, y1 = ys[iy], ys[iy + 1]
    tx = 0.0 if x1 == x0 else (x - x0) / (x1 - x0)
    ty = 0.0 if y1 == y0 else (y - y0) / (y1 - y0)
    v00 = field[iy, ix]
    v10 = field[iy, ix + 1]
    v01 = field[iy + 1, ix]
    v11 = field[iy + 1, ix + 1]
    return float(
        (1 - tx) * (1 - ty) * v00
        + tx * (1 - ty) * v10
        + (1 - tx) * ty * v01
        + tx * ty * v11
    )


def advection_taxis_field(
    grid: AdvectionGrid,
    *,
    sigma_km: float,
    alpha: float,
    hours: float = 24.0,
) -> np.ndarray:
    """
    p(x) ∝ ∫ K(x - x' - Δ(x'); σ) S(x')^α dx' on the discrete grid.

    Δ is integrated velocity over ``hours`` (GLORYS daily mean u,v in m/s).
    """
    if sigma_km <= 0 or not math.isfinite(sigma_km):
        raise ValueError("sigma_km must be positive and finite")
    s = np.clip(grid.s, 0.0, 1.0)
    weights = np.power(s, alpha, where=s > 0, out=np.zeros_like(s))
    dt_s = hours * 3600.0
    dx_adv = grid.u_ms * dt_s / 1000.0
    dy_adv = grid.v_ms * dt_s / 1000.0

    ny, nx = weights.shape
    x2, y2 = np.meshgrid(grid.x_km, grid.y_km, indexing="xy")
    x_src = x2 - dx_adv
    y_src = y2 - dy_adv
    interp = RegularGridInterpolator(
        (grid.y_km, grid.x_km),
        weights,
        bounds_error=False,
        fill_value=0.0,
    )
    deposited = interp(np.stack([y_src.ravel(), x_src.ravel()], axis=-1)).reshape((ny, nx))

    sigma_px_x = max(sigma_km / grid.dx_km, 1e-6)
    sigma_px_y = max(sigma_km / grid.dy_km, 1e-6)
    smoothed = gaussian_filter(deposited, sigma=(sigma_px_y, sigma_px_x), mode="nearest")
    total = float(np.nansum(smoothed))
    if total <= 0 or not math.isfinite(total):
        return np.zeros_like(smoothed)
    return smoothed / total


def persistence_at_point(grid: AdvectionGrid, x_km: float, y_km: float) -> float:
    """S(x, t) at the same location (no advection or dispersal)."""
    return _bilinear_at(x_km, y_km, grid, np.clip(grid.s, 0.0, 1.0))


def advection_at_point(
    grid: AdvectionGrid,
    x_km: float,
    y_km: float,
    *,
    sigma_km: float,
    alpha: float,
    hours: float = 24.0,
) -> float:
    field = advection_taxis_field(grid, sigma_km=sigma_km, alpha=alpha, hours=hours)
    return _bilinear_at(x_km, y_km, grid, field)
