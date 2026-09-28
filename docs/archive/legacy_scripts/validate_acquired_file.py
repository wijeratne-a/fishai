#!/usr/bin/env python3
"""Validate an acquired gzip or CSV table: open, header, not HTML, row count.

Reports whether latitude/longitude headers exist as booleans only.
Does not print coordinate values. Does not modify the input file.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import sys
from pathlib import Path


HTML_MARKERS = ("<!DOCTYPE", "<html", "<HTML", "<head", "<BODY", "<body")


def open_text(path: Path):
    if path.suffix == ".gz" or path.name.endswith(".csv.gz"):
        return gzip.open(path, "rt", encoding="latin-1", newline="")
    return path.open("rt", encoding="latin-1", newline="")


def looks_like_html(sample: str) -> bool:
    head = sample.lstrip()[:200]
    return any(marker in head for marker in HTML_MARKERS)


def validate(path: Path) -> dict:
    result = {
        "path": str(path),
        "opens": False,
        "has_header": False,
        "is_html": False,
        "data_rows": 0,
        "has_latitude_header": False,
        "has_longitude_header": False,
        "n_columns": 0,
        "status": "INVALID",
        "warnings": [],
    }
    if not path.is_file():
        result["warnings"].append("file_not_found")
        return result

    try:
        with open_text(path) as handle:
            sample = handle.read(4096)
            if looks_like_html(sample):
                result["is_html"] = True
                result["opens"] = True
                result["warnings"].append("content_is_html")
                result["status"] = "INVALID"
                return result
            handle.seek(0)
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration:
                result["opens"] = True
                result["warnings"].append("empty_file")
                result["status"] = "INVALID"
                return result

            result["opens"] = True
            fields = [c.strip() for c in header]
            if not fields or all(f == "" for f in fields):
                result["warnings"].append("missing_header")
                result["status"] = "INVALID"
                return result

            result["has_header"] = True
            result["n_columns"] = len(fields)
            lower = {f.lower() for f in fields}
            result["has_latitude_header"] = "latitude" in lower
            result["has_longitude_header"] = "longitude" in lower

            # ERDDAP often emits a units row immediately after the header.
            first_data = True
            for row in reader:
                if not row or all(not (c or "").strip() for c in row):
                    continue
                if first_data:
                    first_data = False
                    # Skip units/NC_GLOBAL-style second header if first cell empty-ish
                    # or looks non-data (common ERDDAP pattern: UTC, degrees_north, ...)
                    joined = " ".join((c or "").strip().lower() for c in row[:4])
                    if any(
                        token in joined
                        for token in (
                            "degrees_north",
                            "degrees_east",
                            "unitless",
                            "seconds since",
                            "utc",
                        )
                    ) and not any(ch.isdigit() for ch in (row[0] or "")[:1]):
                        # Heuristic: treat as units row only when first field is not a timestamp digit start
                        # Prefer: if YEAR-like second column empty or units-ish
                        if not (row[0] or "").strip()[:1].isdigit():
                            result["warnings"].append("units_row_skipped")
                            continue
                result["data_rows"] += 1

    except OSError as exc:
        result["warnings"].append(f"open_error:{type(exc).__name__}")
        result["status"] = "INVALID"
        return result
    except csv.Error as exc:
        result["warnings"].append(f"csv_error:{type(exc).__name__}")
        result["status"] = "INVALID"
        return result

    if result["data_rows"] == 0:
        result["warnings"].append("zero_data_rows")
        result["status"] = "INVALID"
        return result

    if not result["has_latitude_header"] or not result["has_longitude_header"]:
        result["warnings"].append("missing_lat_lon_headers")
        result["status"] = "VALID_WITH_WARNINGS"
    elif result["warnings"]:
        result["status"] = "VALID_WITH_WARNINGS"
    else:
        result["status"] = "VALID"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to .csv or .csv.gz")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a single-line JSON object (still no coordinate values)",
    )
    args = parser.parse_args(argv)
    result = validate(args.path.resolve())

    if args.json:
        import json

        print(json.dumps(result, sort_keys=True))
    else:
        print(f"path={result['path']}")
        print(f"opens={result['opens']}")
        print(f"has_header={result['has_header']}")
        print(f"is_html={result['is_html']}")
        print(f"data_rows={result['data_rows']}")
        print(f"n_columns={result['n_columns']}")
        print(f"has_latitude_header={result['has_latitude_header']}")
        print(f"has_longitude_header={result['has_longitude_header']}")
        print(f"status={result['status']}")
        if result["warnings"]:
            print(f"warnings={';'.join(result['warnings'])}")
    return 0 if result["status"] in {"VALID", "VALID_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    sys.exit(main())
