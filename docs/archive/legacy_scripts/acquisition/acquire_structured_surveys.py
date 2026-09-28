#!/usr/bin/env python3
"""Acquire exact event/effort/observation samples for Milestone 2.

Priority: remaining public NCRMP years, Reef Life Survey / NRMN, ICES DATRAS,
DFO Maritimes trawl, CalCOFI station/egg/larva. Samples before full archives.
Presence-only sources are recorded separately and never treated as absence.
Does not print coordinate values.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "biological"
MANIFEST = ROOT / "data" / "manifests" / "structured-program-manifest.csv"
PRESENCE = ROOT / "data" / "manifests" / "presence-only-catalog.csv"
LICENSE = ROOT / "data" / "manifests" / "source-licenses.csv"
UA = "FishAI-internal-research/1.0 (public survey samples; internal feasibility)"
NCEI = "https://www.ncei.noaa.gov/erddap"
CW = "https://coastwatch.pfeg.noaa.gov/erddap"
DATRAS_HH = "https://datras.ices.dk/WebServices/DATRASWebService.asmx/getHHdata"
DATRAS_HL = "https://datras.ices.dk/WebServices/DATRASWebService.asmx/getHLdata"
DATRAS_SURVEYS = "https://datras.ices.dk/WebServices/DATRASWebService.asmx/getSurveyList"
AODN_WFS = (
    "https://geoserver-123.aodn.org.au/geoserver/ows"
    "?service=WFS&version=1.0.0&request=GetFeature"
    "&typeName=imos:ep_m1_public_data&outputFormat=csv&maxFeatures=400"
)
DFO_DICT = (
    "https://api-proxy.edh-cde.dfo-mpo.gc.ca/catalogue/records/"
    "1366e1f1-e2c8-4905-89ae-e10f1be0a164/attachments/DataDictionary_Summer.csv"
)
DFO_ZIP = (
    "https://api-proxy.edh-cde.dfo-mpo.gc.ca/catalogue/records/"
    "1366e1f1-e2c8-4905-89ae-e10f1be0a164/attachments/SUMMER_csv.zip"
)
DFO_PORTAL = "https://open.canada.ca/data/en/dataset/1366e1f1-e2c8-4905-89ae-e10f1be0a164"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def http_get(url: str, *, timeout: int = 180, max_attempts: int = 4) -> tuple[int, bytes, str]:
    delay = 2.0
    last: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return getattr(response, "status", 200), response.read(), response.headers.get(
                    "Content-Type", ""
                )
        except Exception as exc:  # noqa: BLE001
            last = exc
            if attempt == max_attempts:
                break
            time.sleep(delay)
            delay = min(delay * 2, 30.0)
    raise RuntimeError(f"GET failed {url}: {last}")


def looks_html(data: bytes) -> bool:
    head = data.lstrip()[:200].lower()
    return head.startswith(b"<") and (b"<html" in head or b"<!doctype" in head)


def write_gzip(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(dest, "wb") as handle:
        handle.write(data)


def append_csv(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.is_file()
    fields = list(row)
    if exists:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fields = list(reader.fieldnames or fields)
            for key in row:
                if key not in fields:
                    fields.append(key)
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in fields})


def upsert_license(dataset_id: str, provider: str, access_class: str, source: str, text: str, notes: str) -> None:
    rows: list[dict] = []
    if LICENSE.is_file():
        with LICENSE.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    fields = [
        "dataset_id",
        "provider",
        "access_class",
        "license_source",
        "license_text",
        "explicit_public_model_publication",
        "notes",
    ]
    found = False
    for row in rows:
        if row.get("dataset_id") == dataset_id:
            row.update(
                {
                    "provider": provider,
                    "access_class": access_class,
                    "license_source": source,
                    "license_text": text[:800],
                    "explicit_public_model_publication": "no",
                    "notes": notes,
                }
            )
            found = True
            break
    if not found:
        rows.append(
            {
                "dataset_id": dataset_id,
                "provider": provider,
                "access_class": access_class,
                "license_source": source,
                "license_text": text[:800],
                "explicit_public_model_publication": "no",
                "notes": notes,
            }
        )
    with LICENSE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def record(
    *,
    program: str,
    dataset_id: str,
    method: str,
    region: str,
    us_jurisdiction: str,
    role: str,
    url: str,
    dest: Path | None,
    status: str,
    data_rows: int,
    notes: str,
    presence_only: bool = False,
) -> None:
    row = {
        "program": program,
        "dataset_id": dataset_id,
        "method": method,
        "region": region,
        "us_jurisdiction": us_jurisdiction,
        "role": role,
        "url": url,
        "path": str(dest.relative_to(ROOT)) if dest and dest.exists() else "",
        "sha256": sha256_file(dest) if dest and dest.exists() else "",
        "bytes": dest.stat().st_size if dest and dest.exists() else 0,
        "data_rows": data_rows,
        "http_or_status": status,
        "retrieved_utc": utc_now(),
        "notes": notes,
        "presence_only": "yes" if presence_only else "no",
    }
    append_csv(PRESENCE if presence_only else MANIFEST, row)


def csv_data_rows(data: bytes) -> int:
    text = data.decode("latin-1", errors="replace")
    if looks_html(data) or text.lstrip().startswith("<"):
        return 0
    reader = csv.reader(io.StringIO(text))
    try:
        next(reader)
    except StopIteration:
        return 0
    n = 0
    first = True
    for row in reader:
        if first and row and not any(ch.isdigit() for ch in (row[0] or "")[:1]):
            first = False
            joined = " ".join((c or "").lower() for c in row[:4])
            if any(tok in joined for tok in ("degrees", "unitless", "utc", "seconds since")):
                continue
        first = False
        if row and any((c or "").strip() for c in row):
            n += 1
    return n


def probe_ncrmp_years(dataset: str, year_field: str) -> list[int]:
    url = f"{NCEI}/tabledap/{dataset}.csv?{year_field}&distinct()"
    status, payload, _ = http_get(url, timeout=90)
    if status != 200 or looks_html(payload):
        return []
    years: list[int] = []
    reader = csv.reader(io.StringIO(payload.decode("latin-1", errors="replace")))
    next(reader, None)
    for row in reader:
        if not row:
            continue
        try:
            years.append(int(float(row[0])))
        except ValueError:
            continue
    return sorted(set(years))


def already_have_ncrmp(dataset: str, year: int) -> bool:
    path = RAW / "noaa-ncrmp" / dataset / f"{year}.csv.gz"
    if path.is_file() and path.stat().st_size > 1000:
        return True
    if dataset == "CRCP_Reef_Fish_Surveys_Florida":
        alt = RAW / f"noaa-rvc-florida-keys-{year}.csv.gz"
        return alt.is_file() and alt.stat().st_size > 1000
    return False


def acquire_remaining_ncrmp() -> None:
    from download_ncrmp_regions import ATLANTIC, PACIFIC, available_columns, build_url

    plan = {
        "CRCP_Reef_Fish_Surveys_Puerto_Rico": ("YEAR", "atlantic"),
        "CRCP_Reef_Fish_Surveys_USVI": ("YEAR", "atlantic"),
        "CRCP_Reef_Fish_Surveys_Flower_Gardens": ("YEAR", "atlantic"),
        "CRCP_Reef_Fish_Surveys_Florida": ("YEAR", "atlantic"),
    }
    for dataset, (year_field, family) in plan.items():
        try:
            years = probe_ncrmp_years(dataset, year_field)
        except Exception as exc:  # noqa: BLE001
            record(
                program="NCRMP_RVC",
                dataset_id=dataset,
                method="reef_visual_census",
                region=dataset,
                us_jurisdiction="yes",
                role="year_probe",
                url=f"{NCEI}/tabledap/{dataset}.csv",
                dest=None,
                status="PROBE_FAIL",
                data_rows=0,
                notes=str(exc)[:200],
            )
            continue
        new_years = [y for y in years if y != 2025 and not already_have_ncrmp(dataset, y)]
        record(
            program="NCRMP_RVC",
            dataset_id=dataset,
            method="reef_visual_census",
            region=dataset,
            us_jurisdiction="yes",
            role="year_probe",
            url=f"{NCEI}/tabledap/{dataset}.csv?{year_field}&distinct()",
            dest=None,
            status="PROBED",
            data_rows=0,
            notes=f"published_years={years}; missing_local={new_years}",
        )
        for year in new_years[:2]:
            dest = RAW / "noaa-ncrmp" / dataset / f"{year}.csv.gz"
            try:
                url = build_url(dataset, year_field, year, family)
                status, payload, ctype = http_get(url, timeout=600)
                if status != 200 or looks_html(payload) or len(payload) < 1000:
                    raise RuntimeError(f"bad payload status={status} bytes={len(payload)}")
                write_gzip(dest, payload)
                record(
                    program="NCRMP_RVC",
                    dataset_id=dataset,
                    method="reef_visual_census",
                    region=dataset,
                    us_jurisdiction="yes",
                    role="observation",
                    url=url,
                    dest=dest,
                    status=str(status),
                    data_rows=csv_data_rows(payload),
                    notes=f"additional_public_year={year}",
                )
            except Exception as exc:  # noqa: BLE001
                record(
                    program="NCRMP_RVC",
                    dataset_id=dataset,
                    method="reef_visual_census",
                    region=dataset,
                    us_jurisdiction="yes",
                    role="observation",
                    url="",
                    dest=None,
                    status="DOWNLOAD_FAIL",
                    data_rows=0,
                    notes=f"{year}:{exc}"[:240],
                )


def acquire_calcofi() -> None:
    tables = (
        ("erdCalCOFIstns", "station", "cruise,ship,ship_code,order_occupied,time,line,station,bottom_depth,temperature"),
        ("erdCalCOFItows", "effort", "cruise,ship,ship_code,order_occupied,tow_type,tow_number,time,line,station,standard_haul_factor,volume_sampled"),
        ("erdCalCOFIeggcnt", "egg_observation", "cruise,ship,ship_code,order_occupied,tow_type,tow_number,time,line,station,scientific_name,common_name,count,std_count"),
        ("erdCalCOFIlrvcnt", "larva_observation", "cruise,ship,ship_code,order_occupied,tow_type,tow_number,time,line,station,scientific_name,common_name,count,std_count"),
    )
    upsert_license(
        "erdCalCOFI_family",
        "NOAA CoastWatch ERDDAP / NOAA SWFSC",
        "AUTO_ACQUIRE_INTERNAL_ONLY",
        f"{CW}/info/erdCalCOFIstns/index.csv",
        "The data may be used and redistributed for free but is not intended for legal use.",
        "Eggs stay eggs; larvae stay larvae; not adult occurrence.",
    )
    for dataset_id, role, cols in tables:
        dest = RAW / "calcofi" / f"{dataset_id}-sample.csv.gz"
        url = f"{CW}/tabledap/{dataset_id}.csv?{cols}&cruise=%222204%22"
        try:
            status, payload, _ = http_get(url, timeout=180)
            if status != 200 or looks_html(payload):
                raise RuntimeError(f"status={status} html={looks_html(payload)}")
            if csv_data_rows(payload) < 5:
                url = f"{CW}/tabledap/{dataset_id}.csv?{cols}&distinct()&orderByLimit(%22cruise,ship%22,400)"
                status, payload, _ = http_get(url, timeout=180)
            write_gzip(dest, payload)
            record(
                program="CalCOFI",
                dataset_id=dataset_id,
                method="ichthyoplankton_net_or_station",
                region="California Current",
                us_jurisdiction="yes",
                role=role,
                url=url,
                dest=dest,
                status=str(status),
                data_rows=csv_data_rows(payload),
                notes="Eggs remain eggs. Larvae remain larvae. Not adult reef detection.",
            )
        except Exception as exc:  # noqa: BLE001
            record(
                program="CalCOFI",
                dataset_id=dataset_id,
                method="ichthyoplankton_net_or_station",
                region="California Current",
                us_jurisdiction="yes",
                role=role,
                url=url,
                dest=None,
                status="DOWNLOAD_FAIL",
                data_rows=0,
                notes=str(exc)[:240],
            )


def _xml_tables(payload: bytes) -> list[dict]:
    text = payload.decode("utf-8", errors="replace")
    if looks_html(payload):
        return []
    root = ET.fromstring(payload)
    rows: list[dict] = []
    # DATRAS returns diffgram / NewDataSet / Table or similar.
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag.lower() in {"table", "hh", "hl", "ca", "diffgram"}:
            if list(node) and all(c.text is not None or list(c) == [] for c in list(node)):
                children = [c for c in list(node) if c.tag.split("}")[-1].lower() not in {"table"}]
                if children and all(len(list(c)) == 0 for c in children):
                    row = {c.tag.split("}")[-1]: (c.text or "") for c in children}
                    if row:
                        rows.append(row)
    if rows:
        return rows
    # Fallback: any element with several leaf children.
    for node in root.iter():
        kids = [c for c in list(node) if len(list(c)) == 0]
        if len(kids) >= 4:
            row = {c.tag.split("}")[-1]: (c.text or "") for c in kids}
            rows.append(row)
    return rows


def acquire_datras() -> None:
    upsert_license(
        "ICES_DATRAS_NS-IBTS",
        "ICES DATRAS",
        "ICES_PUBLIC_DATRAS",
        "https://datras.ices.dk/WebServices/Webservices.aspx",
        "Public DATRAS web services. ICES data policy: cite ICES DATRAS; internal use only until publication review.",
        "Haul (HH) is the event. HL is length/catch. Zeros require completed haul plus species list/HL zeros.",
    )
    dest_dir = RAW / "datras" / "NS-IBTS" / "2019-Q1"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for record_type, url_base, role in (
        ("HH", DATRAS_HH, "event_effort"),
        ("HL", DATRAS_HL, "observation"),
    ):
        url = f"{url_base}?survey=NS-IBTS&year=2019&quarter=1"
        dest = dest_dir / f"{record_type}.csv.gz"
        try:
            status, payload, _ = http_get(url, timeout=180)
            if looks_html(payload):
                raise RuntimeError("html")
            rows = _xml_tables(payload)
            if not rows:
                # Some responses wrap a single CSV-like string.
                text = payload.decode("utf-8", errors="replace")
                dest_xml = dest_dir / f"{record_type}.xml.gz"
                write_gzip(dest_xml, payload)
                record(
                    program="ICES_DATRAS",
                    dataset_id=f"NS-IBTS-2019Q1-{record_type}",
                    method="bottom_trawl",
                    region="North Sea",
                    us_jurisdiction="no",
                    role=role,
                    url=url,
                    dest=dest_xml,
                    status=str(status),
                    data_rows=text.count("<"),
                    notes="XML stored; parser found no table rows. Inspect locally. Coordinates not printed.",
                )
                continue
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
            write_gzip(dest, buf.getvalue().encode("utf-8"))
            record(
                program="ICES_DATRAS",
                dataset_id=f"NS-IBTS-2019Q1-{record_type}",
                method="bottom_trawl",
                region="North Sea",
                us_jurisdiction="no",
                role=role,
                url=url,
                dest=dest,
                status=str(status),
                data_rows=len(rows),
                notes="Event=haul (HH). Observation=HL. Do not invent zeros from missing species without HL/species list.",
            )
        except Exception as exc:  # noqa: BLE001
            record(
                program="ICES_DATRAS",
                dataset_id=f"NS-IBTS-2019Q1-{record_type}",
                method="bottom_trawl",
                region="North Sea",
                us_jurisdiction="no",
                role=role,
                url=url,
                dest=None,
                status="DOWNLOAD_FAIL",
                data_rows=0,
                notes=str(exc)[:240],
            )


def acquire_rls() -> None:
    upsert_license(
        "IMOS_NRMN_ep_m1_public_data",
        "IMOS / AODN / Reef Life Survey",
        "IMOS_AODN_OPEN",
        "https://metadata.imas.utas.edu.au/geonetwork/srv/api/records/b273fafa-03d6-4fc2-9acf-39d8c06581e5",
        "Cite Reef Life Survey / IMOS NRMN. Internal use until publication review.",
        "Method 1 50x5 m transect blocks. Abundance on transect. Method 0 is presence-only and stays separate.",
    )
    dest = RAW / "reef-life-survey" / "ep_m1_public_data_sample.csv.gz"
    urls = [
        AODN_WFS,
        "https://geoserver.aodn.org.au/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=imos:ep_m1_public_data&outputFormat=csv&maxFeatures=400",
        "https://geoserver-123.aodn.org.au/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=imos:ep_m1_public_data&outputFormat=csv&maxFeatures=400",
    ]
    last_err = ""
    for url in urls:
        try:
            status, payload, _ = http_get(url, timeout=180)
            if looks_html(payload) or csv_data_rows(payload) < 2:
                last_err = f"status={status} rows={csv_data_rows(payload)}"
                continue
            write_gzip(dest, payload)
            record(
                program="Reef_Life_Survey_NRMN",
                dataset_id="imos:ep_m1_public_data",
                method="reef_visual_transect",
                region="global_NRMN_sample",
                us_jurisdiction="no",
                role="observation",
                url=url,
                dest=dest,
                status=str(status),
                data_rows=csv_data_rows(payload),
                notes="Method 1 quantitative transect sample. Method 0 presence-only not acquired here.",
            )
            return
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)[:200]
    record(
        program="Reef_Life_Survey_NRMN",
        dataset_id="imos:ep_m1_public_data",
        method="reef_visual_transect",
        region="global_NRMN_sample",
        us_jurisdiction="no",
        role="observation",
        url=urls[0],
        dest=None,
        status="DOWNLOAD_FAIL",
        data_rows=0,
        notes=last_err,
    )


def acquire_dfo() -> None:
    upsert_license(
        "DFO_MARITIMES_SUMMER_RV",
        "Fisheries and Oceans Canada",
        "OPEN_GOVERNMENT_LICENCE_CANADA",
        DFO_PORTAL,
        "Open Government Licence - Canada. Cite Clark & Emberley, DFO Maritimes Summer RV Surveys.",
        "Event=set/haul. Catch numbers and weights by species. Zeros documented when species is in survey list and catch is zero.",
    )
    dest_dir = RAW / "dfo" / "maritimes-summer"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dict_path = dest_dir / "DataDictionary_Summer.csv"
    try:
        status, payload, _ = http_get(DFO_DICT, timeout=90)
        dict_path.write_bytes(payload)
        record(
            program="DFO_Maritimes_RV",
            dataset_id="DFO_MARITIMES_SUMMER_dictionary",
            method="bottom_trawl",
            region="Scotian Shelf / Bay of Fundy",
            us_jurisdiction="no",
            role="dictionary",
            url=DFO_DICT,
            dest=dict_path,
            status=str(status),
            data_rows=csv_data_rows(payload),
            notes="Dictionary only; documents event/effort/catch fields.",
        )
    except Exception as exc:  # noqa: BLE001
        record(
            program="DFO_Maritimes_RV",
            dataset_id="DFO_MARITIMES_SUMMER_dictionary",
            method="bottom_trawl",
            region="Scotian Shelf / Bay of Fundy",
            us_jurisdiction="no",
            role="dictionary",
            url=DFO_DICT,
            dest=None,
            status="DOWNLOAD_FAIL",
            data_rows=0,
            notes=str(exc)[:240],
        )
    zip_path = dest_dir / "SUMMER_csv.zip"
    try:
        status, payload, _ = http_get(DFO_ZIP, timeout=300)
        if looks_html(payload) or len(payload) < 1000:
            raise RuntimeError(f"bad zip bytes={len(payload)}")
        zip_path.write_bytes(payload)
        extracted = 0
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            names = zf.namelist()
            # Sample: extract up to 3 CSVs, or first 4000 rows of the largest.
            for name in names:
                if not name.lower().endswith(".csv"):
                    continue
                raw_name = Path(name).name
                out = dest_dir / raw_name
                data = zf.read(name)
                # Keep a bounded sample if huge.
                text = data.decode("latin-1", errors="replace")
                lines = text.splitlines()
                if len(lines) > 4001:
                    text = "\n".join(lines[:4001]) + "\n"
                    data = text.encode("utf-8")
                    raw_name = f"SAMPLE_{raw_name}"
                    out = dest_dir / raw_name
                out.write_bytes(data)
                extracted += 1
                record(
                    program="DFO_Maritimes_RV",
                    dataset_id=f"DFO_MARITIMES_SUMMER_{raw_name}",
                    method="bottom_trawl",
                    region="Scotian Shelf / Bay of Fundy",
                    us_jurisdiction="no",
                    role="sample_table",
                    url=DFO_ZIP,
                    dest=out,
                    status=str(status),
                    data_rows=max(len(text.splitlines()) - 1, 0),
                    notes=f"From zip member {name}. Sampled if >4000 lines. Coordinates not printed.",
                )
                if extracted >= 4:
                    break
        if extracted == 0:
            record(
                program="DFO_Maritimes_RV",
                dataset_id="DFO_MARITIMES_SUMMER_zip",
                method="bottom_trawl",
                region="Scotian Shelf / Bay of Fundy",
                us_jurisdiction="no",
                role="archive",
                url=DFO_ZIP,
                dest=zip_path,
                status=str(status),
                data_rows=0,
                notes=f"zip_bytes={len(payload)}; no csv members sampled",
            )
    except Exception as exc:  # noqa: BLE001
        record(
            program="DFO_Maritimes_RV",
            dataset_id="DFO_MARITIMES_SUMMER_zip",
            method="bottom_trawl",
            region="Scotian Shelf / Bay of Fundy",
            us_jurisdiction="no",
            role="archive",
            url=DFO_ZIP,
            dest=None,
            status="DOWNLOAD_FAIL",
            data_rows=0,
            notes=str(exc)[:240],
        )


def record_presence_only() -> None:
    record(
        program="OBIS",
        dataset_id="OBIS_occurrence_API",
        method="compiler_occurrence",
        region="Florida Keys box",
        us_jurisdiction="yes",
        role="presence_only",
        url="https://api.obis.org",
        dest=None,
        status="SEPARATE_CATALOG",
        data_rows=0,
        notes="Presence-only. Not used as absence. Kept out of structured-program-manifest.",
        presence_only=True,
    )
    record(
        program="Pacific_NCRMP_COUNT",
        dataset_id="CRCP_Reef_Fish_Surveys_Hawaii",
        method="reef_visual_census_count",
        region="Hawaii",
        us_jurisdiction="yes",
        role="presence_only",
        url=f"{NCEI}/tabledap/CRCP_Reef_Fish_Surveys_Hawaii.csv",
        dest=None,
        status="SEPARATE_CATALOG",
        data_rows=0,
        notes="Downloaded COUNT tables had no zeros. Do not invent non-detections.",
        presence_only=True,
    )


def main() -> int:
    if MANIFEST.exists():
        MANIFEST.unlink()
    record_presence_only()
    acquire_remaining_ncrmp()
    acquire_calcofi()
    acquire_datras()
    acquire_rls()
    acquire_dfo()
    print(f"manifest={MANIFEST}")
    return 0


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
