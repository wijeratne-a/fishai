# Global bias and gaps

- Atlantic RVC non-detections are survey misses on a published species list, not ecological absence.
- Pacific RVC extracts are positive-only; treating missing taxa as zeros invents false absences.
- OBIS Keys records are presence reports with compiler and effort bias; they are not a live map and not interchangeable with RVC frames.
- Environmental SST (`jplMURSST41`) is probed but **not joined** to biological events, so models lack matched ocean context.
- Habitat is dive-observed (`HABITAT_CD`) only; bathymetry is not reef evidence and was not acquired.
- Cross-region pooling mixes incompatible zero semantics and protocols.
