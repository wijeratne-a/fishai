#!/usr/bin/env python3
"""
Build prereg/cufes_24h_wcofs_prediction_scores.json when full R refits are unavailable.

When every cutoff predates the public WCOFS fields archive (egg record ends before
2024-07), operational metrics match the pre-registered damped-anomaly proxy from
PR #38. This script copies those 24 h pooled metrics with honest forcing labels.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from fishai.models.cufes_24h_wcofs_forcing import (  # noqa: E402
    pooled_forcing_label,
    resolve_24h_forcing,
)


def _git_sha() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _transform_species(sp: dict) -> dict:
    pooled = sp.get("pooled") or {}
    h24 = pooled.get("24") or pooled.get(24)
    if not h24:
        return sp
    op_proxy = h24.get("operational_proxy") or {}
    out_h24 = {
        "horizon_hours": 24,
        "n_common_support": h24.get("n_common_support"),
        "oracle": h24.get("oracle"),
        "operational": {
            **op_proxy,
            "physics_source": sp.get("physics_source"),
            "operational_claim": sp.get("operational_claim"),
        },
        "persistence": h24.get("persistence"),
        "climatology": h24.get("climatology"),
    }
    return {
        "label": sp.get("label"),
        "taxon": sp.get("taxon"),
        "model_config": sp.get("model_config"),
        "forcing_source": "proxy_fallback",
        "n_cutoffs": sp.get("n_cutoffs"),
        "n_eligible_cutoffs": sp.get("n_eligible_cutoffs"),
        "fit_status": sp.get("fit_status"),
        "pass_24h": sp.get("pass_24h"),
        "pass_rule": (
            "operational (WCOFS or proxy_fallback) AUC and TSS at 24h strictly greater "
            "than persistence and climatology, with at least 6 eligible cutoffs"
        ),
        "pooled": {"24": out_h24},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-scores",
        type=Path,
        default=REPO / "prereg/cufes_forecast_temporal_holdout_scores.json",
    )
    parser.add_argument(
        "--out-scores",
        type=Path,
        default=REPO / "prereg/cufes_24h_wcofs_prediction_scores.json",
    )
    parser.add_argument(
        "--out-readout",
        type=Path,
        default=REPO / "prereg/cufes_24h_wcofs_prediction_readout.md",
    )
    args = parser.parse_args()

    src = json.loads(args.source_scores.read_text(encoding="utf-8"))
    cutoffs = [dt.date.fromisoformat(c) for c in src.get("cutoffs") or []]
    forcing = pooled_forcing_label(cutoffs)
    per_cutoff = {
        c.isoformat(): resolve_24h_forcing(c, c + dt.timedelta(days=1)).source for c in cutoffs
    }

    manifest = {
        "status": src.get("status"),
        "claim": "24h egg-encounter forecast with WCOFS-first forcing",
        "forcing_source": forcing,
        "wcofs_lead_tag": "f024",
        "proxy_physics_source": src.get("physics_source"),
        "operational_claim": src.get("operational_claim"),
        "code_sha": _git_sha(),
        "design": "prereg/cufes_forecast_temporal_holdout_design.md",
        "test_end": src.get("test_end"),
        "cutoffs": src.get("cutoffs"),
        "cutoff_forcing_resolution": per_cutoff,
        "note": (
            "Egg scoring ends before public WCOFS fields archives; every cutoff uses "
            "proxy_fallback (damped-anomaly). Operational 24 h metrics match "
            "cufes_forecast_temporal_holdout_scores.json operational_proxy until "
            "WCOFS-overlap egg labels exist."
        ),
        "species": [_transform_species(sp) for sp in src.get("species") or []],
        "pass_24h": src.get("pass_24h"),
    }

    args.out_scores.parent.mkdir(parents=True, exist_ok=True)
    args.out_scores.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# CUFES 24 h WCOFS-first prediction — readout",
        "",
        "Egg-encounter validation only (not adult fish, not harvest advice).",
        "",
        f"**Forcing label (pooled):** `{forcing}` (WCOFS lead `f024` when reachable).",
        "",
        "Public WCOFS `fields.*` archives begin 2024-07; CUFES egg scoring ends "
        f"{src.get('test_end')}. Historical cutoffs cannot use issued WCOFS; "
        "operational scores use the pre-declared GLORYS-based damped-anomaly proxy.",
        "",
    ]
    for sp in manifest["species"]:
        h24 = sp["pooled"]["24"]
        op = h24["operational"]
        per = h24["persistence"]
        clim = h24["climatology"]
        verdict = "PASS" if sp.get("pass_24h") else "FAIL"
        lines.extend(
            [
                f"## {sp['label']}",
                "",
                f"- **24 h verdict:** {verdict}",
                f"- AUC: operational {op.get('auc')} vs persistence {per.get('auc')} vs climatology {clim.get('auc')}",
                f"- TSS: operational {op.get('tss')} vs persistence {per.get('tss')} vs climatology {clim.get('tss')}",
                "",
            ]
        )
        if not sp.get("pass_24h"):
            lines.append(
                "Maps from this pipeline are a **demonstration only** until validation passes; "
                "they are not a validated prediction product."
            )
            lines.append("")

    args.out_readout.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.out_scores} and {args.out_readout}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
