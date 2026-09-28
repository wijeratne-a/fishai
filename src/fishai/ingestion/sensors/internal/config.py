"""Load ``config/sensors.yaml``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "sensors.yaml"


def load_sensors_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or DEFAULT_CONFIG_PATH
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("sensors config must be a mapping")
    return data


def pilot_bbox(cfg: dict[str, Any] | None = None) -> tuple[float, float, float, float]:
    c = cfg or load_sensors_config()
    b = c["bbox"]
    return (float(b["lat_min"]), float(b["lat_max"]), float(b["lon_min"]), float(b["lon_max"]))
