"""Feature equation tests on analytic fields."""

from __future__ import annotations

import math

import numpy as np

from fishai.ingestion.physics.features import (
    PILOT_COAST_ANGLE_RAD,
    cayula_cornillon_fronts,
    compute_upwelling,
    eke_from_sla,
    sst_gradient,
)


def test_sst_gradient_constant_is_zero() -> None:
    lat = np.linspace(34.0, 35.0, 20)
    lon = np.linspace(-121.0, -120.0, 20)
    sst = np.ones((20, 20)) * 15.0
    g = sst_gradient(sst, lat, lon)
    assert np.nanmax(g) < 1e-6


def test_sst_gradient_linear_lat() -> None:
    lat = np.linspace(34.0, 35.0, 32)
    lon = np.linspace(-121.0, -120.0, 32)
    sst = np.broadcast_to(lat[:, None], (32, 32))
    g = sst_gradient(sst, lat, lon)
    assert np.nanmedian(g) > 0.005


def test_eke_from_sla_quadratic() -> None:
    lat = np.linspace(33.0, 34.0, 16)
    lon = np.linspace(-121.0, -120.0, 16)
    la, lo = np.meshgrid(lat, lon, indexing="ij")
    sla = 0.01 * (la - 33.5) ** 2
    _, _, eke = eke_from_sla(sla, lat, lon, lat0=33.5)
    assert np.nanmean(eke) > 0


def test_compute_upwelling_equatorward_alongshore_positive() -> None:
    speed = 10.0
    sc, sn = math.cos(PILOT_COAST_ANGLE_RAD), math.sin(PILOT_COAST_ANGLE_RAD)
    u10 = np.full((4, 5), -speed * sc)
    v10 = np.full((4, 5), -speed * sn)
    lat = np.linspace(33.0, 33.5, 4)
    ui = compute_upwelling(u10, v10, lat)
    assert float(np.nanmin(ui)) > 0.0


def test_cayula_cornillon_detects_edge() -> None:
    sst = np.ones((64, 64)) * 14.0
    sst[:, 32:] = 18.0
    prob = cayula_cornillon_fronts(sst, window=32, stride=16, theta_min=0.5)
    assert np.nanmax(prob) > 0
