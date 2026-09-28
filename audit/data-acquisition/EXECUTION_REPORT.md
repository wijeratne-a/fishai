NEW SOURCE ACQUIRED: erdCalCOFIcufes
BYTES: 39321
LICENSE NOTE: NC_GLOBAL.license allows free use/redistribution with disclaimer; no explicit public model publication grant → classified AUTO_ACQUIRE_INTERNAL_ONLY
WHY NOT A NOWCAST: Historical CalCOFI CUFES fish-egg sample from cruise 202204 (April 2022), not a real-time abundance or ocean forecast product.

## Local path

`data/raw/biological/new-sources/erdCalCOFIcufes/sample-cruise-202204.csv`

Companion license text: `data/raw/biological/new-sources/erdCalCOFIcufes/LICENSE_FROM_METADATA.txt`

`git check-ignore` matches `.gitignore:9:data/raw/` for the new CSV (exit 0 / ignored).

## Discovery (WS01)

- Script: `scripts/acquisition/discover_public_marine_sources.py`
- Family searched: **CalCOFI**
- NCEI ERDDAP search: HTTP **404** (no matching results)
- Fallback metadata search: NOAA CoastWatch ERDDAP (PFEG) → 28 CalCOFI dataset hits
- Manifest: `data/manifests/discovery-candidates.csv`

## Acquisition (WS02)

- Primary small-sample attempt used `orderByLimit("time,300")` without `-L`; curl saw HTTP **302** and wrote 0 bytes, then with `-L` returned a much larger-than-intended payload (orderByLimit semantics did not constrain to 300 rows as hoped).
- Kept alternate official subset instead: cruise `202204` constraint → HTTP **200**, **39321** bytes, **418** data rows (+ header/units).
- No NCRMP/RVC files re-downloaded or modified.
- Access class: **AUTO_ACQUIRE_INTERNAL_ONLY**
- Manifests updated: `acquisition-queue.csv`, `source-licenses.csv`, `global-file-inventory.csv`
