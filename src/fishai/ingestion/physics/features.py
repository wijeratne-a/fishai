"""Derived physics features (gradients, fronts, EKE, Ekman, along-track sampling)."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np
from scipy import ndimage

EARTH_RADIUS_M = 6371000.0
OMEGA = 7.2921e-5
GRAVITY = 9.81
RHO0 = 1025.0
RHO_AIR = 1.22

# Southern California Bight mainland shoreline tangent (CCW from east), pilot box 32–35°N / 117–121°W.
# Derived from the mean orientation of the mainland coast between Point Conception and the US–Mexico
# border (~145°), consistent with qualitative Bakun upwelling geometry for this bight.
PILOT_COAST_ANGLE_DEG = 145.0
PILOT_COAST_ANGLE_RAD = math.radians(PILOT_COAST_ANGLE_DEG)
UPWELLING_FORMULA_ID = "ekman_coastal_ui_v1"


def _fill_nan_mean(field: np.ndarray) -> np.ndarray:
    f = np.where(np.isfinite(field), field, np.nan)
    m = np.nanmean(f)
    return np.where(np.isfinite(f), f, m)


def sst_gradient(
    sst: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray | None = None,
    *,
    pm: np.ndarray | None = None,
    pn: np.ndarray | None = None,
) -> np.ndarray:
    """
    |grad SST| in degC/km.

    Uses ROMS curvilinear metrics ``pm``/``pn`` (1/m) when provided; otherwise
    regular lat/lon spacing.
    """
    sst = np.asarray(sst, dtype=float)
    filled = _fill_nan_mean(sst)
    if pm is not None and pn is not None:
        pm = np.asarray(pm, dtype=float)
        pn = np.asarray(pn, dtype=float)
        dx_km = 1.0 / (pm * 1000.0)
        dy_km = 1.0 / (pn * 1000.0)
        gx = ndimage.sobel(filled, axis=1) / (8.0 * np.nanmean(dx_km))
        gy = ndimage.sobel(filled, axis=0) / (8.0 * np.nanmean(dy_km))
    else:
        lat = np.asarray(lat, dtype=float)
        if lat.ndim == 1:
            dy_km = abs(float(lat[1] - lat[0])) * 111.32
            lat2d = np.broadcast_to(lat[:, None], sst.shape)
        else:
            dy_km = abs(float(np.nanmean(np.diff(lat, axis=0)))) * 111.32
            lat2d = lat
        if lon is not None and np.ndim(lon) == 1:
            dx_km = dy_km * np.cos(np.radians(float(np.nanmean(lat))))
        else:
            dx_km = dy_km * np.cos(np.radians(float(np.nanmean(lat2d))))
        gx = ndimage.sobel(filled, axis=1) / (8.0 * dx_km)
        gy = ndimage.sobel(filled, axis=0) / (8.0 * dy_km)
    g = np.hypot(gx, gy)
    g[~np.isfinite(sst)] = np.nan
    return g


def _bimodality_score(values: np.ndarray, n_bins: int = 32) -> tuple[float, float | None]:
    v = values[np.isfinite(values)]
    if v.size < 10:
        return 0.0, None
    hist, edges = np.histogram(v, bins=n_bins)
    hist = hist.astype(float)
    n = hist.sum()
    if n <= 0:
        return 0.0, None
    mu = v.mean()
    var = v.var()
    if var <= 0:
        return 0.0, None
    best_j = 0.0
    best_tau: float | None = None
    for k in range(1, n_bins):
        left = v[v <= edges[k]]
        right = v[v > edges[k]]
        if left.size == 0 or right.size == 0:
            continue
        w1 = left.size / n
        w2 = right.size / n
        if w1 < 0.25 or w2 < 0.25:
            continue
        mu1, mu2 = left.mean(), right.mean()
        jb = w1 * w2 * (mu1 - mu2) ** 2
        if jb > best_j:
            best_j = jb
            best_tau = float(edges[k])
    theta = best_j / var if var > 0 else 0.0
    return theta, best_tau


def cayula_cornillon_fronts(
    sst: np.ndarray,
    *,
    window: int = 32,
    stride: int = 16,
    theta_min: float = 0.76,
) -> np.ndarray:
    """Windowed histogram bimodality front probability (0..1 per pixel)."""
    sst = np.asarray(sst, dtype=float)
    ny, nx = sst.shape
    hits = np.zeros_like(sst, dtype=float)
    counts = np.zeros_like(sst, dtype=float)
    half = window // 2
    for j0 in range(0, ny - window + 1, stride):
        for i0 in range(0, nx - window + 1, stride):
            patch = sst[j0 : j0 + window, i0 : i0 + window]
            valid = patch[np.isfinite(patch)]
            if valid.size < 100:
                continue
            theta, _ = _bimodality_score(valid)
            if theta < theta_min:
                continue
            sl = slice(j0, j0 + window)
            si = slice(i0, i0 + window)
            hits[sl, si] += 1.0
            counts[sl, si] += 1.0
    with np.errstate(invalid="ignore"):
        prob = np.where(counts > 0, hits / counts, 0.0)
    prob[~np.isfinite(sst)] = np.nan
    return prob


def eke_from_sla(
    sla: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    *,
    lat0: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Geostrophic anomaly velocities and EKE = 0.5(u'^2 + v'^2) from SLA."""
    sla = np.asarray(sla, dtype=float)
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    if lat.ndim == 1 and lon.ndim == 1:
        lat2d, lon2d = np.meshgrid(lat, lon, indexing="ij")
    else:
        lat2d, lon2d = lat, lon
    phi = np.radians(lat2d if lat0 is None else lat0)
    f = 2.0 * OMEGA * np.sin(phi)
    f = np.where(np.abs(f) < 1e-10, np.nan, f)
    dlat = np.gradient(lat2d, axis=0)
    dlon = np.gradient(lon2d, axis=1)
    dy = np.radians(dlat) * EARTH_RADIUS_M
    dx = np.radians(dlon) * EARTH_RADIUS_M * np.cos(np.radians(lat2d))
    deta_dy = np.gradient(sla, axis=0) / np.where(dy == 0, np.nan, dy)
    deta_dx = np.gradient(sla, axis=1) / np.where(dx == 0, np.nan, dx)
    u = -(GRAVITY / f) * deta_dy
    v = (GRAVITY / f) * deta_dx
    eke = 0.5 * (u ** 2 + v ** 2)
    return u, v, eke


def _wind_stress(u10: np.ndarray, v10: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    spd = np.hypot(u10, v10)
    cd = np.where(spd < 11.0, 1.2e-3, (0.49 + 0.065 * spd) * 1e-3)
    cd = np.where(spd < 4.0, 1.2e-3, cd)
    tau_x = RHO_AIR * cd * spd * u10
    tau_y = RHO_AIR * cd * spd * v10
    return tau_x, tau_y


def compute_upwelling(
    u10: np.ndarray,
    v10: np.ndarray,
    lat: np.ndarray,
    *,
    coast_angle_rad: float | None = None,
) -> np.ndarray:
    """
    Coastal upwelling index (m²/s per m of coast) from 10 m winds.

    Uses ``ekman_upwelling`` with :data:`PILOT_COAST_ANGLE_RAD` as the mainland-shore
    **tangent** (CCW from east). The returned index is negated so that **positive**
    values match offshore Ekman transport under equatorward alongshore winds on the
    US west coast (upwelling-favourable in the Southern California Bight).
    """
    angle = coast_angle_rad if coast_angle_rad is not None else PILOT_COAST_ANGLE_RAD
    ui = ekman_upwelling(u10, v10, lat, coast_angle_rad=angle)["coastal_upwelling_index"]
    return -ui


def upwelling_covariate_metadata(wind_source_id: str) -> dict[str, float | str]:
    return {
        "upwelling_formula": UPWELLING_FORMULA_ID,
        "upwelling_wind_source": wind_source_id,
        "upwelling_coast_angle_deg": PILOT_COAST_ANGLE_DEG,
    }


def ekman_upwelling(
    u10: np.ndarray,
    v10: np.ndarray,
    lat: np.ndarray,
    *,
    coast_angle_rad: float | None = None,
) -> dict[str, np.ndarray]:
    """
    Wind stress, Ekman transport, optional coastal UI, and Ekman pumping w_E.
    """
    u10 = np.asarray(u10, dtype=float)
    v10 = np.asarray(v10, dtype=float)
    lat = np.asarray(lat, dtype=float)
    if lat.ndim == 1:
        lat2d = np.broadcast_to(lat[:, None], u10.shape)
    else:
        lat2d = lat
    phi = np.radians(lat2d)
    f = 2.0 * OMEGA * np.sin(phi)
    f = np.where(np.abs(f) < 1e-10, np.nan, f)
    tau_x, tau_y = _wind_stress(u10, v10)
    mx = tau_y / (RHO0 * f)
    my = -tau_x / (RHO0 * f)
    lon_idx = np.arange(u10.shape[1], dtype=float)
    dlon = np.broadcast_to(np.gradient(lon_idx), u10.shape)
    dlat = np.gradient(lat2d, axis=0)
    dx = np.radians(dlon) * EARTH_RADIUS_M * np.cos(phi)
    dy = np.radians(dlat) * EARTH_RADIUS_M
    dtau_y_dx = np.gradient(tau_y, axis=1) / np.where(dx == 0, np.nan, dx)
    dtau_x_dy = np.gradient(tau_x, axis=0) / np.where(dy == 0, np.nan, dy)
    beta = 2.0 * OMEGA * np.cos(phi) / EARTH_RADIUS_M
    w_e = (dtau_y_dx - dtau_x_dy) / (RHO0 * f) + beta * tau_x / (RHO0 * f ** 2)
    out = {
        "tau_x": tau_x,
        "tau_y": tau_y,
        "ekman_mx": mx,
        "ekman_my": my,
        "ekman_pumping": w_e,
    }
    if coast_angle_rad is not None:
        sc, sn = math.cos(coast_angle_rad), math.sin(coast_angle_rad)
        ui = (tau_x * sc + tau_y * sn) / (RHO0 * f)
        out["coastal_upwelling_index"] = ui
    return out


def front_distance_km(
    sst_grad: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    *,
    grad_threshold: float | None = None,
) -> np.ndarray:
    """
    Distance (km) from each grid cell to the nearest SST-gradient front.

    Front cells are those with ``sst_grad`` at or above ``grad_threshold`` (defaults
    to the 90th percentile of finite gradients on the field).
    """
    sst_grad = np.asarray(sst_grad, dtype=float)
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    if lat.ndim == 1 and lon.ndim == 1:
        lat2d, lon2d = np.meshgrid(lat, lon, indexing="ij")
    else:
        lat2d, lon2d = lat, lon
    finite = np.isfinite(sst_grad)
    if not finite.any():
        return np.full(sst_grad.shape, np.nan, dtype=float)
    thr = (
        float(grad_threshold)
        if grad_threshold is not None
        else float(np.nanpercentile(sst_grad[finite], 90))
    )
    front = finite & (sst_grad >= thr)
    if not front.any():
        return np.full(sst_grad.shape, np.nan, dtype=float)
    fj, fi = np.where(front)
    out = np.full(sst_grad.shape, np.nan, dtype=float)
    for j in range(sst_grad.shape[0]):
        for i in range(sst_grad.shape[1]):
            if not finite[j, i]:
                continue
            dists = _haversine_km(lat2d[j, i], lon2d[j, i], lat2d[fj, fi], lon2d[fj, fi])
            out[j, i] = float(np.min(dists))
    return out


def _haversine_km(lat1: float, lon1: float, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    p1, p2 = math.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dlam = np.radians(lon2 - lon1)
    hav = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlam / 2) ** 2
    return 2 * EARTH_RADIUS_M / 1000.0 * np.arcsin(np.sqrt(hav))


def sample_along_track(
    field: np.ndarray,
    z: np.ndarray,
    temp: np.ndarray,
    lat_rho: np.ndarray,
    lon_rho: np.ndarray,
    start: tuple[float, float],
    stop: tuple[float, float],
    valid_times: Sequence[float],
    field_time_index: int,
    *,
    spacing_km: float = 1.0,
    target_z_m: float = -3.0,
) -> dict[str, float]:
    """
    CUFES-style along-track samples: points every ``spacing_km``, interpolate to
    ``target_z_m`` and in time; return aggregate mean and SD (no point coords).
    """
    lat0, lon0 = start
    lat1, lon1 = stop
    dist_total = _haversine_km(lat0, lon0, np.array([lat1]), np.array([lon1]))[0]
    n_pts = max(2, int(dist_total / spacing_km) + 1)
    frac = np.linspace(0.0, 1.0, n_pts)
    lats = lat0 + frac * (lat1 - lat0)
    lons = lon0 + frac * (lon1 - lon0)
    from scipy.interpolate import RegularGridInterpolator

    lat_1d = np.unique(lat_rho)
    lon_1d = np.unique(lon_rho)
    if lat_1d.size < 2 or lon_1d.size < 2:
        # curvilinear: nearest neighbour on rho grid
        samples = []
        for la, lo in zip(lats, lons, strict=True):
            j, i = np.unravel_index(
                np.argmin((lat_rho - la) ** 2 + (lon_rho - lo) ** 2), lat_rho.shape
            )
            col_z, col_t = z[:, j, i], temp[:, j, i]
            if np.isfinite(col_t).any():
                val = np.interp(-target_z_m, -col_z[::-1], col_t[::-1])
                samples.append(val)
        arr = np.array(samples, dtype=float)
    else:
        interp = RegularGridInterpolator(
            (lat_1d, lon_1d), field, bounds_error=False, fill_value=np.nan
        )
        arr = interp(np.column_stack([lats, lons]))
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {"mean": np.nan, "sd": np.nan}
    return {
        "mean": float(np.mean(arr)),
        "sd": float(np.std(arr)),
    }
