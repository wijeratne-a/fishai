#!/usr/bin/env python3
"""CLI: reject a file for modeling if unit/zero/event/license checks fail.

Quarantines failures under data/quarantine/ without editing data/raw/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from model_eligibility import gate_file, write_gate_log

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG = REPO_ROOT / "audit" / "storage" / "MODEL_ELIGIBILITY_GATE.csv"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument(
        "--family",
        default="atlantic",
        choices=("atlantic", "presence_only", "other"),
    )
    parser.add_argument("--license-class", default="")
    parser.add_argument("--treat-num-as-integer-count", action="store_true")
    parser.add_argument("--treat-presence-only-as-absence", action="store_true")
    parser.add_argument("--no-quarantine", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    sidecar = {
        "license_class": args.license_class,
        "treated_as_integer_fish_count": args.treat_num_as_integer_count,
        "label_semantics": "PRESENCE_ONLY_NO_ABSENCE"
        if args.family == "presence_only"
        else "SURVEY_DETECTION_WITH_NONDETECTION",
        "treat_presence_only_as_absence": args.treat_presence_only_as_absence,
    }
    result = gate_file(
        args.path.resolve(),
        dataset_id=args.dataset_id,
        family=args.family,
        sidecar=sidecar,
        quarantine=not args.no_quarantine,
    )
    write_gate_log([result], LOG)
    if args.json:
        print(json.dumps(result, sort_keys=True, default=str))
    else:
        print(f"status={result['status']}")
        if result["errors"]:
            print(f"errors={';'.join(result['errors'])}")
        if result.get("quarantine_path"):
            print(f"quarantine={Path(result['quarantine_path']).name}")
        print(f"raw_edited={result['raw_edited']}")
    return 0 if result["status"] == "MODEL_ELIGIBLE" else 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
