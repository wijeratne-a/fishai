"""NOAA WCOFS fields from public S3/THREDDS endpoints.

Contract (not implemented):
- Fetch gridded physics for the pilot bbox; store outside git under
  ``data/processed/``.
- Attach valid-time and issue-time metadata for temporal integrity checks.
"""

SOURCE_MODULE = "wcofs"
