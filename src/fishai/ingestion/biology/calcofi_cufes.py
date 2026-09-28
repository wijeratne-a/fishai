"""CalCOFI CUFES egg counts via ERDDAP ``erdCalCOFIcufes``.

Contract (not implemented):
- Pull sardine/anchovy egg-stage rows for the pilot bbox and time window.
- Emit normalized egg-stage evidence rows; never treat egg detections as adult
  fish presence.
- Respect ``data/SOURCES.yaml`` license and attribution fields.
"""

SOURCE_MODULE = "calcofi_cufes"
