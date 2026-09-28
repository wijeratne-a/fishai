#!/usr/bin/env python3
"""Print regional readiness. Does not rank incompatible methods as one global list."""

from __future__ import annotations

ROWS = [
    ("Florida Keys", "RVC NUM table", "Chaetodon capistratus", "READY_FOR_BASELINE", "internal logistic already fit"),
    ("Florida Keys", "RVC NUM table", "Epinephelus itajara", "INSUFFICIENT_DATA", "1, 1, and 6 detection events"),
    ("Puerto Rico", "RVC NUM table", "survey frame", "READY_FOR_REGIONAL_MODEL", "248 events in 2023, one species list, zeros present"),
    ("USVI", "RVC NUM table", "survey frame", "READY_FOR_REGIONAL_MODEL", "562 events in 2023, one species list, zeros present"),
    ("Flower Garden Banks", "RVC NUM table", "survey frame", "READY_FOR_REGIONAL_MODEL", "38 events in 2024, one species list, zeros present"),
    ("Hawaii", "Pacific fish count table", "detections only", "PRESENCE_LAYER_ONLY", "no zero counts in the 2024 download"),
    ("American Samoa", "Pacific fish count table", "detections only", "PRESENCE_LAYER_ONLY", "no zero counts in the 2023 download"),
    ("CNMI and Guam", "Pacific fish count table", "detections only", "PRESENCE_LAYER_ONLY", "no zero counts in the 2022 download"),
    ("Pacific Remote Islands", "Pacific fish count table", "detections only", "PRESENCE_LAYER_ONLY", "no zero counts in the 2023 download"),
    ("Florida Keys OBIS 90-day box", "occurrence API", "recent reports", "PRESENCE_LAYER_ONLY", "latest saved event date 2026-07-20; not live locations"),
]


def main() -> None:
    for row in ROWS:
        print("\t".join(row))


if __name__ == "__main__":
    main()
