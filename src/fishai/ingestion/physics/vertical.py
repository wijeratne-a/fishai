"""ROMS vertical coordinate transforms and depth-resolved diagnostics."""

from __future__ import annotations

import numpy as np

EARTH_RADIUS_KM = 6371.0

# CUFES egg-stage covariates sample tracers at exactly 3 m (linear in z, never nearest-level).
CUFES_SAMPLE_DEPTH_M = 3.0


def cs_r_vstretching4(s: np.ndarray, theta_s: float, theta_b: float) -> np.ndarray:
    """Vstretching=4 stretching function C(s) on s in [-1, 0]."""
    s = np.asarray(s, dtype=float)
    c = (1.0 - np.cosh(theta_s * s)) / (np.cosh(theta_s) - 1.0)
    if theta_b > 0:
        c = (np.exp(theta_b * c) - 1.0) / (1.0 - np.exp(-theta_b))
    return c


def s_to_z(
    h: np.ndarray,
    zeta: np.ndarray,
    s_rho: np.ndarray,
    hc: float,
    *,
    theta_s: float = 8.0,
    theta_b: float = 3.0,
    cs_r: np.ndarray | None = None,
) -> np.ndarray:
    """
    ROMS Vtransform=2 depth (negative downward) at rho-points.

    z = zeta + (zeta + h) * S,  S = (hc*s + h*C(s)) / (hc + h)
    """
    h = np.asarray(h, dtype=float)
    zeta = np.asarray(zeta, dtype=float)
    s_rho = np.asarray(s_rho, dtype=float)
    if cs_r is None:
        cs_r = cs_r_vstretching4(s_rho, theta_s, theta_b)
    else:
        cs_r = np.asarray(cs_r, dtype=float)
    s_term = (hc * s_rho[:, None, None] + h[None, ...] * cs_r[:, None, None]) / (hc + h[None, ...])
    return zeta[None, ...] + (zeta[None, ...] + h[None, ...]) * s_term


def interp_tracer_at_depth(
    z: np.ndarray,
    tracer: np.ndarray,
    depth_m: float = CUFES_SAMPLE_DEPTH_M,
) -> float:
    """
    Linear interpolation of a tracer to a target depth (positive metres below surface).

    ``z`` is ROMS-style (negative downward). Uses linear interpolation in depth,
    never nearest-level selection.
    """
    z = np.asarray(z, dtype=float)
    tracer = np.asarray(tracer, dtype=float)
    mask = np.isfinite(z) & np.isfinite(tracer)
    if mask.sum() < 2:
        return float("nan")
    depth = -z[mask]
    values = tracer[mask]
    order = np.argsort(depth)
    depth_s = depth[order]
    values_s = values[order]
    target = abs(depth_m)
    if target < depth_s[0] or target > depth_s[-1]:
        return float("nan")
    return float(np.interp(target, depth_s, values_s))


def interp_at_depth_from_z_levels(
    z_levels_m: np.ndarray,
    values: np.ndarray,
    depth_m: float = CUFES_SAMPLE_DEPTH_M,
) -> float:
    """GLORYS-style fixed z-level columns (depths positive down, e.g. 2.6 m, 3.8 m)."""
    z_levels_m = np.asarray(z_levels_m, dtype=float)
    values = np.asarray(values, dtype=float)
    return interp_tracer_at_depth(-z_levels_m, values, depth_m=depth_m)


def interp_at_depth_from_wcofs_column(
    h: float,
    zeta: float,
    s_rho: np.ndarray,
    hc: float,
    tracer: np.ndarray,
    *,
    cs_r: np.ndarray | None = None,
    depth_m: float = CUFES_SAMPLE_DEPTH_M,
) -> float:
    """WCOFS s-level column converted to z, then linear interpolation to ``depth_m``."""
    z = s_to_z(
        np.array([[h]]),
        np.array([[zeta]]),
        s_rho,
        hc,
        cs_r=cs_r,
    )[:, 0, 0]
    return interp_tracer_at_depth(z, tracer, depth_m=depth_m)


def bottom_layer(temp: np.ndarray, salt: np.ndarray | None = None) -> dict[str, np.ndarray]:
    """Bottom rho-layer tracers (k=0 in ROMS bottom-first ordering)."""
    t_b = np.asarray(temp[0], dtype=float)
    out: dict[str, np.ndarray] = {"bottom_temp": t_b}
    if salt is not None:
        out["bottom_salt"] = np.asarray(salt[0], dtype=float)
    return out


MLD_NOT_REACHED = "mld_not_reached"


def _mld_depth_from_z_column(
    zz: np.ndarray,
    tt: np.ndarray,
    *,
    dT: float,
    zref_m: float,
) -> tuple[float | None, str | None]:
    """
    Shared MLD kernel for model columns and glider profiles.

    ``zz`` / ``tt`` are ROMS-style z (negative down), bottom-first ordering.
    Returns positive depth in metres, or ``(None, MLD_NOT_REACHED)``.
    """
    if not np.isfinite(tt).all():
        return None, MLD_NOT_REACHED
    zu, tu = zz[::-1], tt[::-1]
    zref = -abs(zref_m)
    if zu[-1] > zref:
        return None, MLD_NOT_REACHED
    t10 = np.interp(-zref, -zu, tu)
    below = np.where((zu < zref) & (tu < t10 - dT))[0]
    if not below.size:
        return None, MLD_NOT_REACHED
    k = int(below[0])
    z1, z2, t1, t2 = zu[k - 1], zu[k], tu[k - 1], tu[k]
    if t2 != t1:
        zc = z1 + (t10 - dT - t1) * (z2 - z1) / (t2 - t1)
    else:
        zc = z2
    return float(-zc), None


def mld_from_profile(
    depth_m: np.ndarray,
    temp_c: np.ndarray,
    *,
    dT: float = 0.2,
    zref_m: float = 10.0,
) -> tuple[float | None, str | None]:
    """
    Temperature-threshold MLD for a single glider/model profile (depth positive down).
    """
    depth_m = np.asarray(depth_m, dtype=float)
    temp_c = np.asarray(temp_c, dtype=float)
    ok = np.isfinite(depth_m) & np.isfinite(temp_c)
    if ok.sum() < 2:
        return None, MLD_NOT_REACHED
    order = np.argsort(depth_m[ok])
    d = depth_m[ok][order]
    t = temp_c[ok][order]
    # ROMS bottom-first z column (deepest level at index 0).
    zz = -d[::-1]
    tt = t[::-1]
    return _mld_depth_from_z_column(zz, tt, dT=dT, zref_m=zref_m)


def mld(
    z: np.ndarray,
    temp: np.ndarray,
    *,
    dT: float = 0.2,
    zref_m: float = 10.0,
) -> np.ndarray:
    """
    Temperature-threshold MLD (positive depth in metres).

    Shared by WCOFS, GLORYS columns, and glider holdout scoring. When the 0.2 °C
    criterion is not met before the deepest valid level, the cell is NaN
    (``mld_not_reached``).
    """
    z = np.asarray(z, dtype=float)
    temp = np.asarray(temp, dtype=float)
    ny, nx = temp.shape[1], temp.shape[2]
    out = np.full((ny, nx), np.nan, dtype=float)
    for j in range(ny):
        for i in range(nx):
            depth_m, _reason = _mld_depth_from_z_column(
                z[:, j, i], temp[:, j, i], dT=dT, zref_m=zref_m
            )
            if depth_m is not None:
                out[j, i] = depth_m
    return out


def thermocline_depth(
    z: np.ndarray,
    temp: np.ndarray,
    *,
    zmin_m: float = 5.0,
    zmax_m: float = 300.0,
    min_grad: float = 0.05,
) -> np.ndarray:
    """Depth of maximum -dT/dz within [zmin_m, zmax_m] (positive metres)."""
    z = np.asarray(z, dtype=float)
    temp = np.asarray(temp, dtype=float)
    dz = np.diff(z, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        dTdz = np.diff(temp, axis=0) / dz
    zm = 0.5 * (z[1:] + z[:-1])
    mask = (zm <= -zmin_m) & (zm >= -zmax_m)
    dTdz = np.where(mask, dTdz, np.nan)
    allnan = np.all(~np.isfinite(dTdz), axis=0)
    k = np.nanargmax(np.where(np.isfinite(dTdz), dTdz, -np.inf), axis=0)
    zt = -np.take_along_axis(zm, k[None], axis=0)[0]
    weak = np.nanmax(dTdz, axis=0) < min_grad
    zt[allnan | weak] = np.nan
    return zt
