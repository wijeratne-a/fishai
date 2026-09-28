"""Minimal S3 list helper for WCOFS PDS (optional; not used in CI unit tests)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import requests

from fishai.ingestion.physics.http_util import _CONNECT_TIMEOUT, _READ_TIMEOUT
WCOFS_S3_HOST = "noaa-nos-ofs-pds.s3.amazonaws.com"


def list_keys_under_prefix(prefix: str) -> list[str]:
    """List object keys under ``prefix`` using anonymous S3 ListObjectsV2."""
    prefix = prefix.lstrip("/")
    keys: list[str] = []
    token: str | None = None
    while True:
        params: dict[str, str] = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            params["continuation-token"] = token
        url = f"https://{WCOFS_S3_HOST}/"
        resp = requests.get(url, params=params, timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT))
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        for contents in root.findall("s3:Contents", ns):
            key_el = contents.find("s3:Key", ns)
            if key_el is not None and key_el.text:
                keys.append(key_el.text)
        truncated = root.find("s3:IsTruncated", ns)
        if truncated is not None and truncated.text == "true":
            next_tok = root.find("s3:NextContinuationToken", ns)
            token = next_tok.text if next_tok is not None else None
            if not token:
                break
        else:
            break
    return keys
