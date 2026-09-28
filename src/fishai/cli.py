"""CLI stubs for pilot ingestion and modeling entrypoints."""

from __future__ import annotations

import argparse
import sys


def _not_implemented(name: str) -> int:
    print(f"{name}: not implemented", file=sys.stderr)
    return 1


def main_bio(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-bio", description="Biology ingestion (CalCOFI CUFES)")
    parser.parse_args(argv)
    return _not_implemented("fishai-bio")


def main_physics(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-physics", description="Physics ingestion (WCOFS/GLORYS)")
    parser.parse_args(argv)
    return _not_implemented("fishai-physics")


def main_sensors(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-sensors", description="Sensor consistency ingestion")
    parser.parse_args(argv)
    return _not_implemented("fishai-sensors")


def main_models(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fishai-models", description="sdmTMB modeling wrapper")
    parser.parse_args(argv)
    return _not_implemented("fishai-models")
