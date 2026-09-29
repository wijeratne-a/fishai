#!/usr/bin/env python3
"""Read WCOFS avg.nowcast ocean_time for every overlap cycle via HTTP range requests.

Does not download the full ~361 MB grids. Key layout matches
``fishai.ingestion.physics.wcofs_pds_store.layout_prefixes`` and
``avg_nowcast_basename``. Cycle pairing matches
``wcofs_cycle_date_for_glorys_day`` (next-day cycle).

Requires the optional reader ``pyfive`` (not a FishAI runtime dependency).
"""

from __future__ import annotations

import datetime as dt
import json
import struct
import sys
import threading
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fishai.ingestion.physics.wcofs_glorys_overlap import (  # noqa: E402
    load_overlap_config,
    overlap_dates,
    wcofs_cycle_date_for_glorys_day,
)
from fishai.ingestion.physics.wcofs_pds_store import (  # noqa: E402
    NEW_STYLE_PREFER_END,
    NEW_STYLE_PREFER_START,
    WCOFS_S3_HOST,
    avg_nowcast_basename_candidates,
    layout_prefixes,
)

NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
BLOCK = 4 << 20


class HttpRangeFile:
    """Seekable file over HTTP Range requests, cached in fixed-size blocks."""

    def __init__(self, url: str, size: int, block: int = BLOCK) -> None:
        self.url = url
        self.size = size
        self.block = block
        self.pos = 0
        self.cache: dict[int, bytes] = {}
        self.closed = False
        self.bytes_fetched = 0

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            self.pos = offset
        elif whence == 1:
            self.pos += offset
        elif whence == 2:
            self.pos = self.size + offset
        else:
            raise OSError(f"unsupported whence {whence}")
        return self.pos

    def tell(self) -> int:
        return self.pos

    def _fetch_block(self, index: int) -> bytes:
        cached = self.cache.get(index)
        if cached is not None:
            return cached
        start = index * self.block
        end = min(self.size, start + self.block) - 1
        last_err: Exception | None = None
        for _attempt in range(4):
            try:
                req = urllib.request.Request(
                    self.url, headers={"Range": f"bytes={start}-{end}"}
                )
                with urllib.request.urlopen(req, timeout=90) as response:
                    data = response.read()
                break
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                last_err = exc
        else:
            raise RuntimeError(f"range read failed {self.url} {start}-{end}") from last_err
        self.cache[index] = data
        self.bytes_fetched += len(data)
        return data

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            n = self.size - self.pos
        out = bytearray()
        while n > 0 and self.pos < self.size:
            index = self.pos // self.block
            block = self._fetch_block(index)
            offset = self.pos - index * self.block
            take = min(n, len(block) - offset)
            if take <= 0:
                break
            out += block[offset : offset + take]
            self.pos += take
            n -= take
        return bytes(out)

    def close(self) -> None:
        self.closed = True


def _list_prefix(prefix: str) -> list[str]:
    keys: list[str] = []
    token: str | None = None
    while True:
        query = f"list-type=2&prefix={prefix}&max-keys=1000"
        if token:
            from urllib.parse import quote

            query += "&continuation-token=" + quote(token, safe="")
        url = f"https://{WCOFS_S3_HOST}/?{query}"
        with urllib.request.urlopen(url, timeout=60) as response:
            root = ET.fromstring(response.read())
        for node in root.findall("s3:Contents/s3:Key", NS):
            if node.text:
                keys.append(node.text)
        truncated = root.findtext("s3:IsTruncated", default="false", namespaces=NS)
        if truncated != "true":
            break
        token = root.findtext("s3:NextContinuationToken", default=None, namespaces=NS)
        if not token:
            break
    return keys


def _listable_prefixes(days: list[dt.date]) -> list[str]:
    """Monthly (and YYYYMM) prefixes cover the per-day folders, so list those only."""
    raw: list[str] = []
    seen: set[str] = set()
    for day in days:
        for prefix in layout_prefixes(day):
            # Skip YYYY/MM/DD prefixes; the YYYY/MM prefix lists those keys.
            parts = prefix.strip("/").split("/")
            # wcofs/netcdf/YYYY/MM/DD has 5 parts; monthly prefixes are shorter.
            if len(parts) >= 5:
                continue
            if prefix not in seen:
                seen.add(prefix)
                raw.append(prefix)
    return raw


def resolve_keys(days: list[dt.date]) -> dict[dt.date, str]:
    prefixes = _listable_prefixes(days)
    by_prefix: dict[str, list[str]] = {}
    for prefix in prefixes:
        by_prefix[prefix] = _list_prefix(prefix)
        print(f"listed {prefix} keys={len(by_prefix[prefix])}", flush=True)
    resolved: dict[dt.date, str] = {}
    for day in days:
        new_base, old_base = avg_nowcast_basename_candidates(day)
        chosen_key: str | None = None
        for wanted in layout_prefixes(day):
            found: list[tuple[str, str]] = []
            for listed_prefix, keys in by_prefix.items():
                if not (wanted.startswith(listed_prefix) or listed_prefix.startswith(wanted)):
                    continue
                for key in keys:
                    if not key.startswith(wanted):
                        continue
                    base = key.rsplit("/", 1)[-1]
                    if base == new_base:
                        found.append((key, "new"))
                    elif base == old_base:
                        found.append((key, "old"))
            if not found:
                continue
            styles = {style for _key, style in found}
            if NEW_STYLE_PREFER_START <= day <= NEW_STYLE_PREFER_END and "new" in styles:
                picked = [key for key, style in found if style == "new"]
            else:
                picked = [key for key, _style in found]
            unique = sorted(set(picked))
            if len(unique) != 1:
                raise RuntimeError(
                    f"no unique avg.nowcast for {day.isoformat()} under {wanted}: {unique[:5]}"
                )
            chosen_key = unique[0]
            break
        if chosen_key is None:
            raise RuntimeError(f"no avg.nowcast for {day.isoformat()}")
        resolved[day] = chosen_key
    return resolved


def _head(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as response:
        return int(response.headers["Content-Length"])


def _nc3_align(offset: int) -> int:
    return (offset + 3) & ~3


class _Nc3Reader:
    """Cursor over a NetCDF classic header buffer (big-endian)."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.i = 0

    def i32(self) -> int:
        value = struct.unpack_from(">i", self.data, self.i)[0]
        self.i += 4
        return value

    def u64(self) -> int:
        value = struct.unpack_from(">Q", self.data, self.i)[0]
        self.i += 8
        return value

    def name(self) -> str:
        length = self.i32()
        text = self.data[self.i : self.i + length].decode("ascii", "replace")
        self.i += length
        self.i = _nc3_align(self.i)
        return text


def _nc3_attrs(reader: _Nc3Reader, tag: int) -> dict[str, str]:
    if tag == 0:
        return {}
    if tag != 12:
        raise RuntimeError(f"unexpected netcdf attribute tag {tag}")
    count = reader.i32()
    attrs: dict[str, str] = {}
    sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 4, 6: 8}
    for _ in range(count):
        name = reader.name()
        typ = reader.i32()
        nelems = reader.i32()
        nbytes = nelems * sizes[typ]
        raw = reader.data[reader.i : reader.i + nbytes]
        reader.i += nbytes
        reader.i = _nc3_align(reader.i)
        if typ == 2:
            attrs[name] = raw.decode("ascii", "replace").rstrip("\x00")
    return attrs


def read_nc3_ocean_time(handle: HttpRangeFile) -> tuple[float, str, str | None]:
    """ocean_time from a CDF-1/CDF-2 header plus one ranged value read."""
    header = handle.read(2_097_152)
    if len(header) < 16 or header[:3] != b"CDF":
        raise RuntimeError("not a NetCDF classic file")
    offset_bytes = 8 if header[3] == 2 else 4
    reader = _Nc3Reader(header)
    reader.i = 4
    _numrecs = reader.i32()
    tag = reader.i32()
    if tag == 10:
        for _ in range(reader.i32()):
            reader.name()
            reader.i32()
    elif tag != 0:
        raise RuntimeError(f"unexpected dimension tag {tag}")
    tag = reader.i32()
    _nc3_attrs(reader, tag)
    tag = reader.i32()
    if tag != 11:
        raise RuntimeError("netcdf file has no variables")
    nvars = reader.i32()
    ocean_begin: int | None = None
    units = ""
    calendar: str | None = None
    typ = 0
    for _ in range(nvars):
        name = reader.name()
        for _dim in range(reader.i32()):
            reader.i32()
        atag = reader.i32()
        attrs = _nc3_attrs(reader, atag)
        typ = reader.i32()
        reader.i32()  # vsize
        begin = reader.u64() if offset_bytes == 8 else reader.i32()
        if name == "ocean_time":
            ocean_begin = int(begin)
            units = attrs.get("units", "")
            calendar = attrs.get("calendar")
            break
    if ocean_begin is None:
        raise RuntimeError("ocean_time variable not in NetCDF classic header")
    if typ != 6:
        raise RuntimeError(f"ocean_time type {typ} is not NC_DOUBLE")
    handle.seek(ocean_begin)
    raw = handle.read(8)
    seconds = float(struct.unpack(">d", raw)[0])
    return seconds, units, calendar


def read_ocean_time(key: str) -> dict[str, object]:
    url = f"https://{WCOFS_S3_HOST}/{key}"
    size = _head(url)
    handle = HttpRangeFile(url, size)
    try:
        magic = handle.read(4)
        handle.seek(0)
        if magic == b"\x89HDF":
            from pyfive import File

            dataset = File(handle)
            values = dataset["ocean_time"][:]
            units = dataset["ocean_time"].attrs.get("units")
            calendar = dataset["ocean_time"].attrs.get("calendar")
            if hasattr(units, "decode"):
                units = units.decode()
            if hasattr(calendar, "decode"):
                calendar = calendar.decode()
            seconds = float(values.reshape(-1)[0])
            dataset.close()
            units_text = str(units)
            calendar_text = str(calendar) if calendar is not None else None
        elif magic[:3] == b"CDF":
            seconds, units_text, calendar_text = read_nc3_ocean_time(handle)
        else:
            raise RuntimeError(f"unrecognized file magic {magic!r} for {key}")
    finally:
        handle.close()
    base = dt.datetime(2016, 1, 1, tzinfo=dt.timezone.utc)
    if not units_text.startswith("seconds since 2016-01-01"):
        raise RuntimeError(f"unexpected ocean_time units {units_text!r} for {key}")
    stamp = base + dt.timedelta(seconds=seconds)
    return {
        "s3_key": key,
        "content_length": size,
        "ocean_time_seconds": seconds,
        "ocean_time_units": units_text,
        "ocean_time_calendar": calendar_text,
        "ocean_time_utc": stamp.isoformat(),
        "bytes_fetched": handle.bytes_fetched,
        "container": "hdf5" if magic == b"\x89HDF" else "netcdf3",
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inspect_overlap_ocean_times.py OUT.jsonl", file=sys.stderr)
        return 2
    out_path = Path(sys.argv[1])
    cfg = load_overlap_config()
    glorys_days = overlap_dates(cfg)
    cycle_days = sorted(
        {day for day in glorys_days}
        | {wcofs_cycle_date_for_glorys_day(day, cfg) for day in glorys_days}
    )
    print(f"glorys_days={len(glorys_days)} cycle_days={len(cycle_days)}", flush=True)
    keys = resolve_keys(cycle_days)
    done: set[str] = set()
    if out_path.is_file():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                done.add(json.loads(line)["cycle_date"])
    pending = [day for day in cycle_days if day.isoformat() not in done]
    print(f"pending={len(pending)} already={len(done)}", flush=True)
    lock = threading.Lock()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def _one(day: dt.date) -> dict[str, object]:
        record = read_ocean_time(keys[day])
        record["cycle_date"] = day.isoformat()
        return record

    errors: list[str] = []
    with out_path.open("a", encoding="utf-8") as handle:
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(_one, day): day for day in pending}
            finished = 0
            for future in as_completed(futures):
                day = futures[future]
                try:
                    record = future.result()
                except Exception as exc:  # noqa: BLE001 — keep scanning the other days
                    errors.append(f"{day.isoformat()}: {exc}")
                    print(f"ERROR {day.isoformat()} {exc}", flush=True)
                    continue
                line = json.dumps(record, sort_keys=True) + "\n"
                with lock:
                    handle.write(line)
                    handle.flush()
                    finished += 1
                    if finished % 25 == 0 or finished == len(pending):
                        print(
                            f"read {finished}/{len(pending)} last={day.isoformat()} "
                            f"ocean_time={record['ocean_time_utc']}",
                            flush=True,
                        )
    if errors:
        print(f"errors={len(errors)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
