# Structured program status

Aggregates only. No coordinates. Presence-only sources stay in `data/manifests/presence-only-catalog.csv`.

- Programs: 5 (CalCOFI, DFO_Maritimes_RV, ICES_DATRAS, NCRMP_RVC, Reef_Life_Survey_NRMN)
- Methods: 4 (bottom_trawl, ichthyoplankton_net_or_station, reef_visual_census, reef_visual_transect)
- Non-US regions: 3 (North Sea, Scotian Shelf / Bay of Fundy, global_NRMN_sample)
- Files with event frames: 20
- Files with valid zeros: 13
- Milestone 2 bar (5 programs / 3 methods / 2 non-US + tested frames): **PASS**

| Program | Method | Region | File | Events | Zeros | Status |
|---|---|---|---|---:|---:|---|
| NCRMP_RVC | reef_visual_census | Puerto Rico | `2016.csv.gz` | 240 | 61253 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | Puerto Rico | `2019.csv.gz` | 203 | 106837 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | Puerto Rico | `2021.csv.gz` | 234 | 61540 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | Puerto Rico | `2023.csv.gz` | 248 | 130575 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | USVI | `2017.csv.gz` | 418 | 92724 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | USVI | `2019.csv.gz` | 636 | 294574 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | USVI | `2021.csv.gz` | 313 | 70441 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | USVI | `2023.csv.gz` | 562 | 264278 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | Flower Garden Banks | `2018.csv.gz` | 37 | 19610 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | Flower Garden Banks | `2022.csv.gz` | 53 | 28112 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | Flower Garden Banks | `2023.csv.gz` | 74 | 39695 | `VALID_ZEROS_AND_EVENTS` |
| NCRMP_RVC | reef_visual_census | Flower Garden Banks | `2024.csv.gz` | 38 | 5937 | `VALID_ZEROS_AND_EVENTS` |
| CalCOFI | ichthyoplankton_net_or_station | California Current | `erdCalCOFIeggcnt-202204.csv.gz` | 32 | 0 | `EVENT_FRAME_PRESENT` |
| CalCOFI | ichthyoplankton_net_or_station | California Current | `erdCalCOFIlrvcnt-202204.csv.gz` | 32 | 0 | `EVENT_FRAME_PRESENT` |
| CalCOFI | ichthyoplankton_net_or_station | California Current | `erdCalCOFIstns-202204.csv.gz` | 101 | 0 | `EVENT_FRAME_PRESENT` |
| CalCOFI | ichthyoplankton_net_or_station | California Current | `erdCalCOFItows-202204.csv.gz` | 32 | 0 | `EVENT_FRAME_PRESENT` |
| ICES_DATRAS | bottom_trawl | North Sea | `HH.csv.gz` | 76 | 0 | `EVENT_FRAME_PRESENT` |
| ICES_DATRAS | bottom_trawl | North Sea | `HL.csv.gz` | 75 | 0 | `EVENTS_WITHOUT_EXPLICIT_ZEROS` |
| Reef_Life_Survey_NRMN | reef_visual_transect | global_NRMN_sample | `ep_m1_public_data_sample.csv.gz` | 15 | 0 | `EVENTS_WITHOUT_EXPLICIT_ZEROS` |
| DFO_Maritimes_RV | bottom_trawl | Scotian Shelf / Bay of Fundy | `SAMPLE_SUMMER_2023_GSCAT.csv` | 3122 | 106 | `VALID_ZEROS_AND_EVENTS` |
| DFO_Maritimes_RV | bottom_trawl | Scotian Shelf / Bay of Fundy | `SAMPLE_SUMMER_2023_GSINF.csv` | 4000 | 0 | `EVENT_FRAME_PRESENT` |
| DFO_Maritimes_RV | bottom_trawl | Scotian Shelf / Bay of Fundy | `SUMMER_2023_GSDET.csv` |  |  | `HEADER_ONLY_OR_UNPARSED` |
| DFO_Maritimes_RV | bottom_trawl | Scotian Shelf / Bay of Fundy | `SUMMER_2023_GSMISSIONS.csv` | 94 | 0 | `EVENT_FRAME_PRESENT` |
| DFO_Maritimes_RV | bottom_trawl | Scotian Shelf / Bay of Fundy | `SUMMER_2023_GSSPECIES.csv` |  |  | `HEADER_ONLY_OR_UNPARSED` |

