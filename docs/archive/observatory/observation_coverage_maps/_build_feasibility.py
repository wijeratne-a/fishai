#!/usr/bin/env python3
"""Generate taxa_modality_feasibility.csv. Catalog-only; no data ingest."""
from __future__ import annotations

import csv
from pathlib import Path

TAXA = [
    ("finfish", "Finfish (teleosts)"),
    ("sharks_rays", "Sharks and rays (elasmobranchs)"),
    ("shellfish", "Shellfish (bivalves/gastropods)"),
    ("crustaceans", "Crustaceans"),
    ("cephalopods", "Cephalopods"),
    ("marine_mammals", "Marine mammals"),
    ("turtles", "Sea turtles"),
    ("seabirds", "Seabirds"),
    ("plankton", "Plankton (phyto/zoo, not microbes-only)"),
    ("jellyfish", "Jellyfish and other gelatinous zooplankton"),
    ("corals", "Corals"),
    ("benthos", "Benthos (other invertebrates)"),
    ("plants_algae", "Marine plants and macroalgae"),
    ("microbes", "Microbes (bacteria/archaea/picoeukaryotes)"),
    ("larvae", "Larval stages (all metazoa)"),
]

MODS = [
    ("M01", "satellite_remote_sensing"),
    ("M02", "aerial_drone"),
    ("M03", "underwater_optical_imaging"),
    ("M04", "active_acoustics_sonar"),
    ("M05", "passive_acoustics"),
    ("M06", "eDNA_genomics_molecular"),
    ("M07", "tagging_telemetry"),
    ("M08", "autonomous_platforms"),
    ("M09", "fixed_sensors_buoys"),
    ("M10", "commercial_vessels_opportunistic"),
    ("M11", "subsea_cables_DAS_DTS"),
    ("M12", "chemical_biological_physical_proxies"),
    ("M13", "human_community_observations"),
]

# Compact cell: dict with required keys. Missing keys filled from EMPTY.
EMPTY = {
    "primary_class": "MIXED",
    "direct_today": "NO",
    "inferred_today": "NO",
    "forecast_today": "NO",
    "needs_new_infra": "NO",
    "unproven": "NO",
    "speculative": "NO",
    "impossible_now": "NO",
    "what_directly_observed": "",
    "what_inferred": "",
    "what_forecast": "",
    "what_needs_infra": "",
    "unproven_or_speculative": "",
    "physically_impossible_or_not_measurable": "",
    "confidence": "MEDIUM",
    "key_citations": "",
    "notes": "",
}


def C(**kwargs):
    d = dict(EMPTY)
    d.update(kwargs)
    return d


# Citation shortcuts
SAT = "NOAA CoastWatch VIIRS; CMEMS GlobColour; NASA PACE MOANA; DFO 2022 Megafauna from Space; Williamson 2019 Front Mar Sci; CRW 5km; USF SaWS / NOAA SIR"
AC = "ICES CRR 344; Korneliussen ICES JMS; Jones et al NOAA broadband pollock"
ED = "Harrison 2019 PRSB; edn3.405; Front Mar Sci 2025 eDNA spatial bound; edn3.70140"
TEL = "IOOS ATN; Sequeira 2021 MEE tracking bias; AniBOS GOOS"
DAS = "Bouffaut 2022; Rorstadbotnen 2023; ITU-T G.9730.2; Howe 2019 SMART"
PAM = "NCEI PAM; ONMS Sound; SanctSound"
ARGO = "Argo UCSD status; BGC-Argo mission ~$100k CITED; NOAA AOML Argo"
OBIS = "OBIS.org 224M obs accessed 2026-09-18; OBIS 2019 Front Mar Sci biases"
VES = "NMFS VMS 06-101; Global Fishing Watch AIS factsheet; MSA confidentiality"
CARE = "CARE Principles; commercial privacy policy alignment"

# --- cells[taxon][mod] ---
cells: dict[str, dict[str, dict]] = {t: {} for t, _ in TAXA}

# ========== FINFISH ==========
cells["finfish"]["M01"] = C(
    primary_class="INFERRED",
    direct_today="NO",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    needs_new_infra="YES",
    unproven="YES",
    speculative="YES",
    impossible_now="YES",
    what_directly_observed="None as individuals or schools at ocean-color/SST resolution. Sardine 'potential habitat' maps are habitat not fish (NOAA VIIRS applications).",
    what_inferred="Thermal/color/SSH habitat volume; fronts/eddies as encounter covariates. NEVER abundance from chl or AIS.",
    what_forecast="Seasonal habitat envelopes; 24-72 h relative encounter ONLY if fused with local CPUE labels and depth. Skill UNKNOWN globally.",
    what_needs_infra="Directed glider EK/eDNA at satellite fronts; 3D assimilation of Argo; opportunistic vessel acoustics.",
    unproven_or_speculative="UNPROVEN: VHR of surface schools in exceptional clarity. SPECULATIVE: nighttime bioluminescence as biomass.",
    physically_impossible_or_not_measurable="Imaging individuals below optical depth from 300 m-4 km pixels; census of mesopelagic fishes from space.",
    confidence="HIGH",
    key_citations=SAT,
    notes="Indirect path is the product: satellite physics + acoustics/tags/eDNA/vessels.",
)
cells["finfish"]["M02"] = C(
    primary_class="LIMITED",
    direct_today="LIMITED",
    inferred_today="YES",
    forecast_today="NO",
    needs_new_infra="YES",
    what_directly_observed="Surface schools in clear shallow water; spawning aggregations from aircraft in some fisheries; menhaden-like surface schools CONDITIONAL.",
    what_inferred="Habitat from concurrent SST/color; effort from vessel sightings.",
    what_forecast="Not from aerial alone at 24-72 h.",
    what_needs_infra="Routine BVLOS UAV + ML for surface aggregations.",
    unproven_or_speculative="UNPROVEN global UAV fish patrols.",
    physically_impossible_or_not_measurable="Deep and most subsurface fishes.",
    confidence="HIGH",
    key_citations="Standard aerial survey practice; optical-depth limit same as satellite.",
)
cells["finfish"]["M03"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="NO",
    needs_new_infra="YES",
    what_directly_observed="Individuals/species in camera FOV (BRUV, ROV, AUV, EM, divers). Stereo lengths CONDITIONAL.",
    what_inferred="Relative composition; density only with detectability model.",
    what_forecast="None without repeat stations.",
    what_needs_infra="AUV fleets + ML in mesopelagic and shelves.",
    physically_impossible_or_not_measurable="Ocean-volume census; turbid/night without lights (lights bias).",
    confidence="HIGH",
    key_citations=OBIS,
)
cells["finfish"]["M04"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    needs_new_infra="YES",
    unproven="YES",
    what_directly_observed="Calibrated backscatter of swimbladdered pelagics and many groundfish off-bottom; biomass after ID haul.",
    what_inferred="Acoustic classes (bladder vs mackerel vs plankton). Species ID often NOT unique (ICES CRR 344).",
    what_forecast="Short-horizon distribution if survey+model; 24 h school waypoints NOT supported.",
    what_needs_infra="Calibrated opportunistic fishing-vessel EK networks.",
    unproven_or_speculative="UNPROVEN: broadband ML as general species classifier (NOAA pollock study negative among swimbladder fishes).",
    physically_impossible_or_not_measurable="Linnaean ID from overlapping TS; near-surface and dead-zone animals.",
    confidence="HIGH",
    key_citations=AC,
)
cells["finfish"]["M05"] = C(
    primary_class="LIMITED",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    forecast_today="NO",
    needs_new_infra="YES",
    what_directly_observed="Soniferous species choruses (croakers, groupers, some toadfish, etc.) when catalogs exist.",
    what_inferred="Spawning-season occupancy; not biomass.",
    what_needs_infra="Broader hydrophone grids; call libraries.",
    physically_impossible_or_not_measurable="Silent species; density without cue rates.",
    confidence="MEDIUM",
    key_citations=PAM,
)
cells["finfish"]["M06"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="LIMITED",
    needs_new_infra="YES",
    unproven="YES",
    what_directly_observed="DNA/RNA of taxa with primers/references (molecules, not fish GPS).",
    what_inferred="Occupancy in a transport kernel (0.3-39 km / hours-day; models often > field).",
    what_forecast="Occupancy persistence if time series exist (rare).",
    what_needs_infra="Autonomous samplers on SOOP/IOOS; reference genomes; paired trawl calibration.",
    unproven_or_speculative="UNPROVEN: uncalibrated reads as biomass; eRNA as operational kernel.",
    physically_impossible_or_not_measurable="Headcount from one uncalibrated sample; distinguishing adult vs larval DNA without extra info.",
    confidence="HIGH",
    key_citations=ED,
)
cells["finfish"]["M07"] = C(
    primary_class="DIRECT",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    needs_new_infra="YES",
    what_directly_observed="Tracks of tagged large/coastal fishes (tunas, salmon, some reef/gadoids).",
    what_inferred="Vertical habitat and movement kernels (biased subset).",
    what_forecast="Seasonal migration envelopes; 24 h only if model validated (usually UNKNOWN).",
    what_needs_infra="Cheap acoustic tags + arrays for small pelagics.",
    physically_impossible_or_not_measurable="Tagging all herring; tags as census.",
    confidence="HIGH",
    key_citations=TEL,
)
cells["finfish"]["M08"] = C(
    primary_class="NEEDS_INFRA",
    direct_today="LIMITED",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    needs_new_infra="YES",
    what_directly_observed="Only if AUV/glider carries camera/EK/eDNA. Core Argo: ZERO fish.",
    what_inferred="3D T/O2 habitat from Argo/gliders.",
    what_forecast="Habitat volume 24-72 h via ocean models assimilating Argo.",
    what_needs_infra="EK/eDNA/optical glider networks cued by satellite fronts.",
    physically_impossible_or_not_measurable="Argo float as fish counter.",
    confidence="HIGH",
    key_citations=ARGO,
)
cells["finfish"]["M09"] = C(
    primary_class="INFERRED",
    direct_today="LIMITED",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    needs_new_infra="YES",
    what_directly_observed="Only if camera/PAM/eDNA on the mooring.",
    what_inferred="Catchability/habitat from T, O2, waves, currents.",
    what_forecast="Physical fields yes; fish no without labels.",
    what_needs_infra="Biology payloads on existing buoys.",
    confidence="HIGH",
    key_citations="NDBC; IOOS; OceanSITES",
)
cells["finfish"]["M10"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    needs_new_infra="YES",
    what_directly_observed="Catch/bycatch ID and effort; opportunistic EK; underway eDNA if fitted.",
    what_inferred="CPUE as catchability-confounded index. AIS/VMS = effort not N.",
    what_forecast="Next-trip CPUE only with partner labels and coarsening.",
    what_needs_infra="Privacy-preserving e-log + EK contribution networks.",
    physically_impossible_or_not_measurable="Unfished ocean; secret-spot public maps (policy-forbidden).",
    confidence="HIGH",
    key_citations=VES,
)
cells["finfish"]["M11"] = C(
    primary_class="UNPROVEN",
    direct_today="NO",
    inferred_today="NO",
    unproven="YES",
    speculative="YES",
    impossible_now="YES",
    what_directly_observed="None demonstrated for named fishes.",
    unproven_or_speculative="UNPROVEN: some low-frequency fish sounds on DAS. SPECULATIVE: general fish monitoring on cables.",
    physically_impossible_or_not_measurable="Species biomass of silent/high-frequency fishes along armored cable.",
    confidence="MEDIUM",
    key_citations=DAS,
)
cells["finfish"]["M12"] = C(
    primary_class="INFERRED",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    what_inferred="T, O2, fronts, prey-field proxies (chl). SST is not adult Chinook location (vertical refuge).",
    what_forecast="Physics 24-72 h; biological translation needs labels.",
    physically_impossible_or_not_measurable="Abundance from SST/chl/AIS.",
    confidence="HIGH",
    key_citations=SAT + "; marine-domain model_limitations.md alignment",
)
cells["finfish"]["M13"] = C(
    primary_class="DIRECT",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    forecast_today="NO",
    what_directly_observed="Landings reports, creel, community photos, TEK if licensed.",
    what_inferred="Phenology, presence.",
    physically_impossible_or_not_measurable="Publishing secret spots or Indigenous sites without consent.",
    confidence="HIGH",
    key_citations=CARE,
)

# ========== SHARKS / RAYS ==========
cells["sharks_rays"]["M01"] = C(
    primary_class="MIXED",
    direct_today="LIMITED",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    unproven="YES",
    impossible_now="YES",
    what_directly_observed="Rare VHR in clear shallow water (basking shark class; DFO 2022). NOT Sentinel-2 operational.",
    what_inferred="SST/productivity habitat — the dominant published 'satellite shark' use (Williamson 2019).",
    what_forecast="Seasonal habitat suitability, not N.",
    unproven_or_speculative="UNPROVEN: routine VHR+ML shark watch.",
    physically_impossible_or_not_measurable="Most species most of the time; turbid/deep.",
    confidence="HIGH",
    key_citations=SAT,
)
cells["sharks_rays"]["M02"] = C(
    primary_class="DIRECT",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    what_directly_observed="Aerial counts of basking sharks, some rays, whale sharks in clear water.",
    what_inferred="Habitat.",
    physically_impossible_or_not_measurable="Deep sharks.",
    confidence="HIGH",
    key_citations="DFO 2022; standard aerial surveys",
)
cells["sharks_rays"]["M03"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    needs_new_infra="YES",
    what_directly_observed="BRUV/ROV/AUV/divers: presence, relative abundance with design.",
    what_inferred="Community composition.",
    what_needs_infra="Standardized BRUV grids globally.",
    confidence="HIGH",
    key_citations=OBIS,
)
cells["sharks_rays"]["M04"] = C(
    primary_class="LIMITED",
    direct_today="LIMITED",
    inferred_today="YES",
    what_directly_observed="Occasional large targets; not assessment-standard for most sharks.",
    what_inferred="Co-occurring prey backscatter.",
    physically_impossible_or_not_measurable="Species ID of most elasmobranchs by EK.",
    confidence="MEDIUM",
    key_citations=AC,
)
cells["sharks_rays"]["M05"] = C(
    primary_class="IMPOSSIBLE",
    impossible_now="YES",
    what_directly_observed="Generally none (not vocal).",
    physically_impossible_or_not_measurable="PAM as shark census.",
    confidence="HIGH",
    key_citations=PAM,
)
cells["sharks_rays"]["M06"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    needs_new_infra="YES",
    unproven="YES",
    what_directly_observed="eDNA occupancy (qPCR/metabarcoding) when references exist.",
    what_inferred="Plume-scale presence.",
    what_needs_infra="Time series + hydrodynamics.",
    unproven_or_speculative="Uncalibrated abundance.",
    physically_impossible_or_not_measurable="Exact individual locations from DNA.",
    confidence="HIGH",
    key_citations=ED,
)
cells["sharks_rays"]["M07"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    what_directly_observed="Satellite/acoustic tracks — among best-tagged taxa.",
    what_inferred="Movement kernels (tagging-location bias).",
    what_forecast="Seasonal corridors.",
    physically_impossible_or_not_measurable="Population N from tagged subset.",
    confidence="HIGH",
    key_citations=TEL,
)
cells["sharks_rays"]["M08"] = C(
    primary_class="NEEDS_INFRA",
    direct_today="LIMITED",
    inferred_today="YES",
    needs_new_infra="YES",
    what_directly_observed="AUV cameras/BRUV-style; glider eDNA.",
    what_inferred="Habitat T/O2.",
    what_needs_infra="Directed AUV surveys at satellite fronts/seamounts.",
    confidence="MEDIUM",
    key_citations=ARGO,
)
cells["sharks_rays"]["M09"] = C(
    primary_class="INFERRED",
    direct_today="LIMITED",
    inferred_today="YES",
    what_directly_observed="Acoustic receivers (telemetry); rare cameras.",
    what_inferred="Habitat.",
    confidence="MEDIUM",
    key_citations=TEL,
)
cells["sharks_rays"]["M10"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    what_directly_observed="Catch/bycatch (often sensitive); some EM.",
    what_inferred="CPUE biased by targeting/avoidance.",
    notes="Listed/prohibited sharks: NEVER_PUBLISH fine locations.",
    confidence="HIGH",
    key_citations=VES,
)
cells["sharks_rays"]["M11"] = C(
    primary_class="IMPOSSIBLE",
    impossible_now="YES",
    physically_impossible_or_not_measurable="DAS does not image sharks.",
    confidence="HIGH",
    key_citations=DAS,
)
cells["sharks_rays"]["M12"] = C(
    primary_class="INFERRED",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    what_inferred="SST/chl/SSH habitat only.",
    what_forecast="Seasonal suitability.",
    physically_impossible_or_not_measurable="SST as shark count.",
    confidence="HIGH",
    key_citations=SAT,
)
cells["sharks_rays"]["M13"] = C(
    primary_class="DIRECT",
    direct_today="CONDITIONAL",
    what_directly_observed="Beach sightings, dive logs, landings — effort-biased; sensitive spp.",
    confidence="MEDIUM",
    key_citations=CARE,
)

# ========== SHELLFISH ==========
cells["shellfish"]["M01"] = C(
    primary_class="INFERRED",
    direct_today="LIMITED",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    impossible_now="YES",
    what_directly_observed="Intertidal beds/aquaculture structures CONDITIONAL on S2/VHR at low tide; not individuals.",
    what_inferred="Heat/turbidity proxies; NOT mortality; NOT NSSP harvest legality.",
    what_forecast="Heat-at-low-tide physics if fused with tides/air T (oyster stress analogue).",
    physically_impossible_or_not_measurable="Subtidal individual census; OA as 72 h adult killer from space.",
    confidence="HIGH",
    key_citations="CRW not applicable to oysters; Sentinel-2 habitat papers; commercial wedge C1 alignment",
)
cells["shellfish"]["M02"] = C(
    primary_class="LIMITED",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    what_directly_observed="Intertidal beds, farm gear, some HABs/wrack.",
    what_inferred="Emersion/heat context with tide model.",
    confidence="HIGH",
)
cells["shellfish"]["M03"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    what_directly_observed="Diver/ROV/quadrat/farm counts.",
    what_needs_infra="Repeat subtidal imagery grids.",
    confidence="HIGH",
    key_citations=OBIS,
)
cells["shellfish"]["M04"] = C(
    primary_class="LIMITED",
    direct_today="LIMITED",
    what_directly_observed="MBES/seabed classification of reef/bed habitat NOT species biomass of infauna.",
    physically_impossible_or_not_measurable="Pelagic EK as oyster N.",
    confidence="HIGH",
    key_citations=AC,
)
cells["shellfish"]["M05"] = C(
    primary_class="IMPOSSIBLE",
    impossible_now="YES",
    physically_impossible_or_not_measurable="Bivalves not PAM targets.",
    confidence="HIGH",
)
cells["shellfish"]["M06"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    unproven="YES",
    what_directly_observed="eDNA occupancy; larval DNA mixed with adults.",
    what_inferred="Plume presence.",
    unproven_or_speculative="eDNA as set forecast.",
    confidence="MEDIUM",
    key_citations=ED,
)
cells["shellfish"]["M07"] = C(
    primary_class="LIMITED",
    direct_today="LIMITED",
    what_directly_observed="Rare; sessile adults need marked plots not tags.",
    physically_impossible_or_not_measurable="Satellite tags on oysters.",
    confidence="HIGH",
    key_citations=TEL,
)
cells["shellfish"]["M08"] = C(
    primary_class="INFERRED",
    inferred_today="YES",
    needs_new_infra="YES",
    what_inferred="O2/T/S from gliders in estuaries.",
    what_needs_infra="Estuarine glider/AUV DO grids (Willapa vs Hood Canal non-transfer).",
    confidence="HIGH",
    key_citations=ARGO,
)
cells["shellfish"]["M09"] = C(
    primary_class="DIRECT",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    forecast_today="YES",
    what_directly_observed="Farm DO/T/salinity — environment of cultured stock (PRIVATE).",
    what_inferred="Stress risk.",
    what_forecast="24-72 h work/stress windows with tide+air T (highest commercial-wedge fit).",
    notes="Aligns with C1 oyster; DOH closures are NOT this label.",
    confidence="HIGH",
    key_citations="NANOOS Shellfish Growers; CO-OPS tides",
)
cells["shellfish"]["M10"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    what_directly_observed="Dredge/farm harvest (PRIVATE performance).",
    confidence="HIGH",
    key_citations=VES,
)
cells["shellfish"]["M11"] = C(
    primary_class="INFERRED",
    inferred_today="LIMITED",
    what_inferred="DTS/SMART T along cables — not beds.",
    physically_impossible_or_not_measurable="DAS as clam finder.",
    confidence="HIGH",
    key_citations=DAS,
)
cells["shellfish"]["M12"] = C(
    primary_class="INFERRED",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    what_inferred="Heat, DO, salinity, OA (larvae >> adults).",
    what_forecast="Physics of emersion heat; HAB is a split label (food safety vs stress).",
    confidence="HIGH",
    key_citations="Raymond 2022 Ecology heatwave; Cheney 2000",
)
cells["shellfish"]["M13"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    what_directly_observed="Grower reports, tribal harvest knowledge (sovereignty), intertidal walkers.",
    notes="CARE; NEVER_PUBLISH TEK by default.",
    confidence="HIGH",
    key_citations=CARE,
)

# ========== CRUSTACEANS ==========
for m, spec in {
    "M01": C(
        primary_class="IMPOSSIBLE",
        inferred_today="LIMITED",
        forecast_today="NO",
        impossible_now="YES",
        what_inferred="Surface SST is the WRONG temperature for lobster/crab. Weak color/habitat only.",
        physically_impossible_or_not_measurable="Lobster abundance from satellite SST/chl (explicit marine-domain prohibition).",
        confidence="HIGH",
        key_citations="ASMFC 2025 peer review bottom T vs SST; Williamson not applicable",
    ),
    "M02": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Subsurface crustaceans from air except rare clear-water large crabs UNPROVEN.", confidence="HIGH"),
    "M03": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="ROV/AUV/traps on camera; BRUV poor for many crabs.", needs_new_infra="YES", what_needs_infra="Benthic imaging time series.", confidence="HIGH", key_citations=OBIS),
    "M04": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Krill/zooplankton multifrequency YES; benthic lobster NO (dead zone).", physically_impossible_or_not_measurable="Trap-caught lobster N from pelagic EK.", confidence="HIGH", key_citations=AC),
    "M05": C(primary_class="LIMITED", direct_today="CONDITIONAL", what_directly_observed="Snapping shrimp as habitat sound; not lobster PAM.", confidence="MEDIUM", key_citations=PAM),
    "M06": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", unproven="YES", what_directly_observed="eDNA occupancy.", unproven_or_speculative="Reads as legal CPUE.", confidence="MEDIUM", key_citations=ED),
    "M07": C(primary_class="DIRECT", direct_today="CONDITIONAL", inferred_today="YES", what_directly_observed="Acoustic tags on lobster/crab in some studies; not stock-wide.", physically_impossible_or_not_measurable="Tagged subset as GOM abundance.", confidence="HIGH", key_citations=TEL),
    "M08": C(primary_class="INFERRED", inferred_today="YES", needs_new_infra="YES", what_inferred="Bottom T/O2 from gliders — first-order catchability.", what_needs_infra="Shelf glider bottom-T networks (eMOLT analogue at scale).", confidence="HIGH", key_citations=ARGO + "; eMOLT"),
    "M09": C(primary_class="INFERRED", inferred_today="YES", forecast_today="CONDITIONAL", what_inferred="Moored bottom T/O2.", what_forecast="Seasonal phenology (Mills 2017 class) NOT next-haul pounds.", confidence="HIGH", key_citations="NERACOOS; eMOLT"),
    "M10": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", forecast_today="CONDITIONAL", what_directly_observed="Trap haul catch (PRIVATE). Ventless surveys are survey not 24 h.", what_inferred="CPUE != N.", what_forecast="Next-trip CPUE with partner labels (wedge C3).", confidence="HIGH", key_citations=VES + "; ASMFC 2025"),
    "M11": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="DAS as lobster sonar.", confidence="HIGH", key_citations=DAS),
    "M12": C(primary_class="INFERRED", inferred_today="YES", forecast_today="CONDITIONAL", what_inferred="Bottom T, hypoxia, molt phenology priors.", physically_impossible_or_not_measurable="Moon as proven v1 driver (tier 4 in marine-domain).", confidence="HIGH", key_citations="Mills 2017 Front Mar Sci"),
    "M13": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Harvester knowledge (confidential sets).", notes="Rule-of-3 coarsen; whale entanglement geography NEVER_PUBLISH.", confidence="HIGH", key_citations=CARE),
}.items():
    cells["crustaceans"][m] = spec

# ========== CEPHALOPODS ==========
for m, spec in {
    "M01": C(primary_class="INFERRED", inferred_today="LIMITED", impossible_now="YES", what_inferred="Weak SST/chl habitat.", physically_impossible_or_not_measurable="Squid census from VIIRS.", confidence="HIGH", key_citations=SAT),
    "M02": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Rare surface aggregations.", confidence="LOW"),
    "M03": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="ROV/AUV/jig-camera.", confidence="HIGH", key_citations=OBIS),
    "M04": C(primary_class="LIMITED", direct_today="CONDITIONAL", what_directly_observed="Some aggregations on EK; ID uncertain.", confidence="MEDIUM", key_citations=AC),
    "M05": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not a PAM stock tool.", confidence="MEDIUM"),
    "M06": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", what_directly_observed="eDNA occupancy if references exist (gaps).", confidence="MEDIUM", key_citations=ED),
    "M07": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Occasional tags; high mortality/tag loss.", confidence="MEDIUM", key_citations=TEL),
    "M08": C(primary_class="NEEDS_INFRA", needs_new_infra="YES", inferred_today="YES", what_inferred="Mesopelagic habitat from BGC/O2.", what_needs_infra="AUV cameras in oxygen minimum / seamount features.", confidence="MEDIUM", key_citations=ARGO),
    "M09": C(primary_class="INFERRED", inferred_today="YES", what_inferred="T/O2 points.", confidence="LOW"),
    "M10": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="Jig/trawl catch; effort-biased.", confidence="HIGH", key_citations=VES),
    "M11": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="DAS not squid sonar.", confidence="HIGH"),
    "M12": C(primary_class="INFERRED", inferred_today="YES", what_inferred="T/O2/fronts weak.", confidence="MEDIUM"),
    "M13": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Fisher reports.", confidence="MEDIUM", key_citations=CARE),
}.items():
    cells["cephalopods"][m] = spec

# ========== MARINE MAMMALS ==========
cells["marine_mammals"]["M01"] = C(
    primary_class="MIXED",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    forecast_today="LIMITED",
    needs_new_infra="YES",
    unproven="YES",
    impossible_now="YES",
    what_directly_observed="VHR (~0.3-1 m) surface whales and ice/land pinnipeds in good sea state (Cubaynes; Fretwell; DFO 2022). NOT VIIRS/OLCI.",
    what_inferred="Prey/habitat from SST/chl/SSH.",
    what_forecast="Coarse migration envelopes; not real-time global tracks.",
    what_needs_infra="Operational VHR+ML with availability-bias models — still not global completeness.",
    unproven_or_speculative="UNPROVEN species ID for all mysticetes from space; density without dive-bias correction.",
    physically_impossible_or_not_measurable="All individuals all oceans all hours; subsurface animals; 750 m pixels.",
    confidence="HIGH",
    key_citations=SAT,
    notes="Public products must coarsen ESA/MMPA aggregations.",
)
cells["marine_mammals"]["M02"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="NO",
    what_directly_observed="Line-transect aerial/UAV counts; IR at surface.",
    what_inferred="Density with availability models.",
    physically_impossible_or_not_measurable="Global continuous.",
    confidence="HIGH",
    key_citations="NOAA aerial survey programs",
)
cells["marine_mammals"]["M03"] = C(
    primary_class="LIMITED",
    direct_today="LIMITED",
    what_directly_observed="ROV/AUV chance encounters; animal-borne cameras.",
    confidence="HIGH",
)
cells["marine_mammals"]["M04"] = C(
    primary_class="LIMITED",
    direct_today="LIMITED",
    what_directly_observed="Not a survey target; may avoid vessel; mapping sonars are a take risk.",
    confidence="HIGH",
    key_citations=AC,
)
cells["marine_mammals"]["M05"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="LIMITED",
    needs_new_infra="YES",
    what_directly_observed="Calls/clicks when vocalizing; NCEI/ONMS archives.",
    what_inferred="Occupancy; density only with cue rates (often UNKNOWN).",
    what_forecast="Seasonal presence in monitored basins.",
    what_needs_infra="Real-time cabled/glider PAM; call-rate studies.",
    physically_impossible_or_not_measurable="Silent animals; absence from one hydrophone.",
    confidence="HIGH",
    key_citations=PAM,
)
cells["marine_mammals"]["M06"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    what_directly_observed="eDNA occupancy (contamination from vessels/colonies).",
    notes="Fine-scale listed-species hits: coarsen.",
    confidence="MEDIUM",
    key_citations=ED,
)
cells["marine_mammals"]["M07"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    what_directly_observed="Satellite/acoustic tags; AniBOS T/S profiles.",
    what_inferred="Movement kernels (severe subset bias).",
    physically_impossible_or_not_measurable="N from tags; public NARW-precision tracks.",
    confidence="HIGH",
    key_citations=TEL,
)
cells["marine_mammals"]["M08"] = C(
    primary_class="MIXED",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    what_directly_observed="Glider PAM; ASV hydrophones.",
    what_inferred="Habitat.",
    what_needs_infra="More PAM gliders in chokepoints.",
    confidence="HIGH",
    key_citations=PAM + "; " + ARGO,
)
cells["marine_mammals"]["M09"] = C(
    primary_class="DIRECT",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    what_directly_observed="Sanctuary hydrophones; cabled cams rare.",
    confidence="HIGH",
    key_citations=PAM,
)
cells["marine_mammals"]["M10"] = C(
    primary_class="DIRECT",
    direct_today="CONDITIONAL",
    inferred_today="YES",
    what_directly_observed="Observer/EM bycatch; whale-watch logs. AIS of ships is strike-risk context NOT whales.",
    notes="Never invert vessel density to whale density.",
    confidence="HIGH",
    key_citations=VES,
)
cells["marine_mammals"]["M11"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="NO",
    needs_new_infra="YES",
    unproven="YES",
    what_directly_observed="Low-frequency baleen calls on DAS (demonstrated fin/blue/Omura class); localization ~100 m in Arctic experiment; band often <100-150 Hz.",
    what_inferred="Tracks along cable sections with coupling/SNR limits (40-95 km from interrogator in Svalbard example).",
    what_needs_infra="Owner access to dark fiber globally; hydrophone calibration.",
    unproven_or_speculative="UNPROVEN operational conservation product vs hydrophones; odontocetes generally too high frequency.",
    physically_impossible_or_not_measurable="Silent / HF species; uncoupled cable sections.",
    confidence="HIGH",
    key_citations=DAS,
)
cells["marine_mammals"]["M12"] = C(
    primary_class="INFERRED",
    inferred_today="YES",
    forecast_today="LIMITED",
    what_inferred="Prey/physics habitat; noise from ships as stressor not count.",
    physically_impossible_or_not_measurable="Chl as whale N.",
    confidence="HIGH",
    key_citations=SAT,
)
cells["marine_mammals"]["M13"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    what_directly_observed="Strandings, watches, Indigenous knowledge (sovereignty).",
    notes="Precise locations NEVER_PUBLISH.",
    confidence="HIGH",
    key_citations=CARE,
)

# ========== TURTLES ==========
for m, spec in {
    "M01": C(primary_class="INFERRED", direct_today="NO", inferred_today="YES", forecast_today="LIMITED", unproven="YES", impossible_now="YES", what_inferred="SST corridors.", what_forecast="Nesting-season terrestrial products are not in-water turtles.", unproven_or_speculative="Anecdotal VHR in-water.", physically_impossible_or_not_measurable="Pelagic census from OLCI.", confidence="HIGH", key_citations=SAT),
    "M02": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Aerial in clear water; nesting-beach surveys (sensitive).", confidence="HIGH"),
    "M03": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="ROV/BRUV rare; in-water video.", confidence="MEDIUM", key_citations=OBIS),
    "M04": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not an EK survey target.", confidence="HIGH"),
    "M05": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not vocal.", confidence="HIGH"),
    "M06": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", what_directly_observed="eDNA occupancy.", notes="Listed species coarsen.", confidence="MEDIUM", key_citations=ED),
    "M07": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", forecast_today="CONDITIONAL", what_directly_observed="Satellite tags — primary in-water tool.", physically_impossible_or_not_measurable="N from tags.", confidence="HIGH", key_citations=TEL),
    "M08": C(primary_class="INFERRED", inferred_today="YES", what_inferred="T habitat from Argo/gliders.", confidence="MEDIUM", key_citations=ARGO),
    "M09": C(primary_class="INFERRED", inferred_today="YES", what_inferred="Coastal T.", confidence="LOW"),
    "M10": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Bycatch (highly sensitive); observer programs.", confidence="HIGH", key_citations=VES),
    "M11": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="DAS not turtles.", confidence="HIGH"),
    "M12": C(primary_class="INFERRED", inferred_today="YES", forecast_today="LIMITED", what_inferred="SST.", confidence="HIGH"),
    "M13": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="Nest counts, strandings — nest GPS NEVER_PUBLISH.", confidence="HIGH", key_citations=CARE),
}.items():
    cells["turtles"][m] = spec

# ========== SEABIRDS ==========
for m, spec in {
    "M01": C(primary_class="MIXED", direct_today="CONDITIONAL", inferred_today="YES", forecast_today="LIMITED", what_directly_observed="Colonies/guano (Landsat/S2/VHR); penguins stains. At-sea individuals generally NO.", what_inferred="Forage habitat SST/chl.", physically_impossible_or_not_measurable="Global at-sea census of small alcids from VIIRS.", confidence="HIGH", key_citations=SAT),
    "M02": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="Colony and at-sea aerial; drone disturbance risk.", confidence="HIGH"),
    "M03": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Dive-cam prey; surface cameras rare.", confidence="MEDIUM"),
    "M04": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not EK targets at sea.", confidence="HIGH"),
    "M05": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Air-vocal; not underwater PAM stock tool.", confidence="HIGH"),
    "M06": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Possible eDNA near colonies (contamination).", confidence="LOW", key_citations=ED),
    "M07": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", forecast_today="CONDITIONAL", what_directly_observed="GPS/GLS tags extensive.", physically_impossible_or_not_measurable="All individuals.", confidence="HIGH", key_citations=TEL),
    "M08": C(primary_class="INFERRED", inferred_today="YES", what_inferred="Prey-field physics.", confidence="MEDIUM"),
    "M09": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Colony cameras.", confidence="MEDIUM"),
    "M10": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Bycatch; at-sea observer bird counts.", confidence="HIGH", key_citations=VES),
    "M11": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="DAS not birds.", confidence="HIGH"),
    "M12": C(primary_class="INFERRED", inferred_today="YES", forecast_today="LIMITED", what_inferred="Forage proxies.", confidence="HIGH", key_citations=SAT),
    "M13": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="eBird, colony monitors, Indigenous harvest knowledge (sovereignty).", confidence="HIGH", key_citations=CARE),
}.items():
    cells["seabirds"][m] = spec

# ========== PLANKTON ==========
cells["plankton"]["M01"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    needs_new_infra="YES",
    unproven="YES",
    what_directly_observed="Chl-a, some PFTs, blooms, transparency (VIIRS/OLCI/PACE). Surface-weighted.",
    what_inferred="Primary production algorithms; zooplankton NOT in the pixel.",
    what_forecast="Regional HAB/bloom nowcasts; global skill UNKNOWN.",
    what_needs_infra="PACE MOANA validation + BGC-Argo density to design 1000.",
    unproven_or_speculative="Species-level diatom maps from space.",
    physically_impossible_or_not_measurable="Most zooplankton taxa; cells below optical depth without floats.",
    confidence="HIGH",
    key_citations=SAT + "; " + ARGO,
)
cells["plankton"]["M02"] = C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Surface slicks/HABs/discoloration.", confidence="MEDIUM")
cells["plankton"]["M03"] = C(primary_class="DIRECT", direct_today="YES", needs_new_infra="YES", what_directly_observed="UVP/ISIIS/Zooglider/microscopy.", what_needs_infra="More imaging profilers.", confidence="HIGH")
cells["plankton"]["M04"] = C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", what_directly_observed="Zooplankton/krill multifrequency backscatter; siphonophore resonance confusion.", physically_impossible_or_not_measurable="Phytoplankton cells on 38 kHz.", confidence="HIGH", key_citations=AC)
cells["plankton"]["M05"] = C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not PAM.", confidence="HIGH")
cells["plankton"]["M06"] = C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", what_directly_observed="18S/COI metabarcoding; reference gaps.", confidence="HIGH", key_citations=ED)
cells["plankton"]["M07"] = C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Individual plankton tags.", confidence="HIGH")
cells["plankton"]["M08"] = C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", forecast_today="CONDITIONAL", needs_new_infra="YES", what_directly_observed="BGC-Argo chl/particles/irradiance; glider optics.", what_inferred="Productivity/export proxies.", what_needs_infra="1000 BGC floats (CITED design).", confidence="HIGH", key_citations=ARGO)
cells["plankton"]["M09"] = C(primary_class="DIRECT", direct_today="CONDITIONAL", inferred_today="YES", what_directly_observed="Moored fluorometers.", confidence="HIGH", key_citations="OceanSITES; IOOS")
cells["plankton"]["M10"] = C(primary_class="DIRECT", direct_today="YES", what_directly_observed="CPR along shipping routes; ferrybox chl; ballast (sensitive).", confidence="HIGH", key_citations="CPR survey")
cells["plankton"]["M11"] = C(primary_class="INFERRED", inferred_today="LIMITED", what_inferred="SMART T only; not plankton.", confidence="HIGH", key_citations=DAS)
cells["plankton"]["M12"] = C(primary_class="INFERRED", inferred_today="YES", forecast_today="CONDITIONAL", what_inferred="Nutrients, light, mixed-layer physics.", confidence="HIGH", key_citations=ARGO)
cells["plankton"]["M13"] = C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Discolored water / HAB reports; Sargassum photos (macroalgae overlap).", confidence="MEDIUM", key_citations="NOAA SIR community form")

# ========== JELLYFISH ==========
for m, spec in {
    "M01": C(primary_class="UNPROVEN", direct_today="LIMITED", unproven="YES", speculative="YES", what_directly_observed="Rare large surface aggregations in color/VHR.", unproven_or_speculative="Operational jellyfish satellite product.", physically_impossible_or_not_measurable="Most subsurface blooms from VIIRS.", confidence="MEDIUM", key_citations=SAT),
    "M02": C(primary_class="LIMITED", direct_today="CONDITIONAL", what_directly_observed="Surface slicks from air.", confidence="MEDIUM"),
    "M03": C(primary_class="DIRECT", direct_today="YES", needs_new_infra="YES", what_directly_observed="Cameras/UVP/ROV — best direct tool.", what_needs_infra="AUV imaging grids.", confidence="HIGH", key_citations=OBIS),
    "M04": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Weak/mixed TS; siphonophores confound fish.", confidence="MEDIUM", key_citations=AC),
    "M05": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not vocal.", confidence="HIGH"),
    "M06": C(primary_class="DIRECT", direct_today="CONDITIONAL", inferred_today="YES", what_directly_observed="eDNA if primers/references (uneven).", confidence="MEDIUM", key_citations=ED),
    "M07": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Routine tagging of scyphozoans not ops.", confidence="HIGH"),
    "M08": C(primary_class="NEEDS_INFRA", needs_new_infra="YES", direct_today="LIMITED", what_directly_observed="Occasional AUV/glider cameras.", what_needs_infra="Imaging payload programs.", confidence="MEDIUM"),
    "M09": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Intake screens; cameras.", confidence="MEDIUM"),
    "M10": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Bycatch; clogging reports.", confidence="MEDIUM", key_citations=VES),
    "M11": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="DAS not jellies.", confidence="HIGH"),
    "M12": C(primary_class="INFERRED", inferred_today="LIMITED", what_inferred="T/salinity hypotheses; weak.", confidence="LOW"),
    "M13": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="Beach strandings, swimmer reports.", confidence="HIGH", key_citations=CARE),
}.items():
    cells["jellyfish"][m] = spec

# ========== CORALS ==========
for m, spec in {
    "M01": C(primary_class="MIXED", direct_today="CONDITIONAL", inferred_today="YES", forecast_today="YES", what_directly_observed="Shallow reef HABITAT (S2/Landsat/VHR) not polyps.", what_inferred="CRW DHW heat stress PROXY.", what_forecast="Bleaching outlook from heat (not community composition).", physically_impossible_or_not_measurable="Deep corals; global polyp census.", confidence="HIGH", key_citations="NOAA CRW 5km v3.1; Nagel 2022 Remote Sensing"),
    "M02": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Shallow reef mosaics from UAV.", confidence="HIGH"),
    "M03": C(primary_class="DIRECT", direct_today="YES", needs_new_infra="YES", what_directly_observed="Divers/ROV photoquadrats — gold standard.", what_needs_infra="Repeat deep ROV time series.", confidence="HIGH", key_citations=OBIS),
    "M04": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="MBES reef structure not species.", confidence="HIGH"),
    "M05": C(primary_class="LIMITED", direct_today="CONDITIONAL", what_directly_observed="Soundscape (snapping shrimp) as habitat indicator not coral N.", confidence="MEDIUM", key_citations=PAM),
    "M06": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", what_directly_observed="eDNA/symbiont omics; AOML coral omics program.", confidence="HIGH", key_citations="NOAA AOML Omics; " + ED),
    "M07": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Movement tags N/A.", confidence="HIGH"),
    "M08": C(primary_class="DIRECT", direct_today="CONDITIONAL", needs_new_infra="YES", what_directly_observed="ROV/AUV imagery.", what_inferred="Heat/O2 from gliders.", confidence="HIGH"),
    "M09": C(primary_class="INFERRED", inferred_today="YES", forecast_today="YES", what_inferred="Moored T; CRW virtual stations.", what_forecast="DHW alerts.", confidence="HIGH", key_citations="CRW"),
    "M10": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Aquarium/ornamental (regulated); damage reports.", confidence="MEDIUM"),
    "M11": C(primary_class="INFERRED", inferred_today="LIMITED", what_inferred="SMART seafloor T if on reef cables — rare.", confidence="LOW", key_citations=DAS),
    "M12": C(primary_class="INFERRED", inferred_today="YES", forecast_today="YES", what_inferred="Heat, light, OA.", what_forecast="Heat-stress outlook.", notes="DHW is not % bleached live coral.", confidence="HIGH", key_citations="CRW methodology"),
    "M13": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="Reef rangers, citizen reef checks; Indigenous reef knowledge (sovereignty).", confidence="HIGH", key_citations=CARE),
}.items():
    cells["corals"][m] = spec

# ========== BENTHOS ==========
for m, spec in {
    "M01": C(primary_class="LIMITED", direct_today="CONDITIONAL", inferred_today="YES", what_directly_observed="Shallow habitat classes only.", physically_impossible_or_not_measurable="Abyssal fauna from space.", confidence="HIGH", key_citations=SAT),
    "M02": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Intertidal only.", confidence="HIGH"),
    "M03": C(primary_class="DIRECT", direct_today="YES", needs_new_infra="YES", what_directly_observed="Grabs, cores, ROV — primary tool.", what_needs_infra="Repeated AUV grids in ABNJ.", confidence="HIGH", key_citations=OBIS + "; CCZ synthesis via OBIS"),
    "M04": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Seabed classification; not species.", confidence="HIGH", key_citations="ICES seabed classification CRR"),
    "M05": C(primary_class="LIMITED", direct_today="CONDITIONAL", what_directly_observed="Snapping shrimp/soundscape.", confidence="MEDIUM"),
    "M06": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", what_directly_observed="Sediment eDNA — high leverage for invisible infauna.", confidence="HIGH", key_citations=ED),
    "M07": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Rare acoustic tags on large mobile benthos.", confidence="MEDIUM"),
    "M08": C(primary_class="DIRECT", direct_today="CONDITIONAL", needs_new_infra="YES", what_directly_observed="ROV/AUV.", what_needs_infra="Sustained deep imaging observatories.", confidence="HIGH"),
    "M09": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Cabled cams at OOI/ONC-class sites.", confidence="MEDIUM"),
    "M10": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Dredge bycatch; trawl surveys.", confidence="HIGH", key_citations=VES),
    "M11": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="DAS as infauna census.", confidence="HIGH"),
    "M12": C(primary_class="INFERRED", inferred_today="YES", what_inferred="Substrate, O2, T.", confidence="MEDIUM"),
    "M13": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Intertidal citizen science.", confidence="MEDIUM", key_citations=CARE),
}.items():
    cells["benthos"][m] = spec

# ========== PLANTS / ALGAE ==========
cells["plants_algae"]["M01"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    unproven="YES",
    what_directly_observed="Pelagic Sargassum (SaWS/SIR); kelp/seagrass/Ulva canopies in clear shallow water (S2/Landsat/VHR).",
    what_inferred="Biomass indices; subcanopy C uncertain.",
    what_forecast="Sargassum inundation RISK (SIR experimental per NOAA).",
    unproven_or_speculative="Nearshore mixed-pixel Sargassum always.",
    physically_impossible_or_not_measurable="Sub-canopy global carbon from 10 m pixels in turbid water.",
    confidence="HIGH",
    key_citations="USF SaWS; NOAA SIR v1.5; Nagel 2022",
)
for m, spec in {
    "M02": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="UAV kelp/seagrass mosaics; Sargassum beaching.", confidence="HIGH"),
    "M03": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="Diver/ROV quadrats.", confidence="HIGH"),
    "M04": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Maybe canopy scattering; not standard.", confidence="LOW"),
    "M05": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not PAM.", confidence="HIGH"),
    "M06": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", what_directly_observed="eDNA/eRNA of algae; HABs molecular.", confidence="HIGH", key_citations=ED),
    "M07": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="N/A movement tags.", confidence="HIGH"),
    "M08": C(primary_class="LIMITED", direct_today="LIMITED", inferred_today="YES", what_directly_observed="Glider optics for blooms.", confidence="MEDIUM", key_citations=ARGO),
    "M09": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Fluorometers; farm kelp sensors PRIVATE.", confidence="MEDIUM"),
    "M10": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Harvest; fouling reports.", confidence="MEDIUM"),
    "M11": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="DAS not kelp.", confidence="HIGH"),
    "M12": C(primary_class="INFERRED", inferred_today="YES", forecast_today="CONDITIONAL", what_inferred="Nutrients/light/T.", confidence="HIGH"),
    "M13": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="Sargassum photos (NOAA form); beach wrack; guardian kelp monitoring.", confidence="HIGH", key_citations="NOAA SIR page community form; " + CARE),
}.items():
    cells["plants_algae"][m] = spec

# ========== MICROBES ==========
cells["microbes"]["M01"] = C(
    primary_class="DIRECT",
    direct_today="YES",
    inferred_today="YES",
    forecast_today="LIMITED",
    needs_new_infra="YES",
    unproven="YES",
    what_directly_observed="Bulk pigments; PACE MOANA picoplankton groups (provisional).",
    what_inferred="PFT algorithms; not functions.",
    what_forecast="Limited bloom-associated.",
    what_needs_infra="Global MOANA validation; hyperspectral ops.",
    unproven_or_speculative="Pathogen maps from space.",
    physically_impossible_or_not_measurable="Individual cells; most taxa.",
    confidence="HIGH",
    key_citations="NASA PACE MOANA 3.1; SWOT-PACE Oceanography 2025",
)
for m, spec in {
    "M02": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Surface discoloration only.", confidence="MEDIUM"),
    "M03": C(primary_class="DIRECT", direct_today="YES", what_directly_observed="Microscopy/flow cytometry on samples — lab not landscape cameras.", confidence="HIGH"),
    "M04": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="EK does not resolve microbes.", confidence="HIGH"),
    "M05": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not PAM.", confidence="HIGH"),
    "M06": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", needs_new_infra="YES", what_directly_observed="Metagenomes/16S — strongest modality.", what_needs_infra="Standardized omics time series (NOAA Omics plan).", confidence="HIGH", key_citations="NOAA Omics; PMEL OME; " + ED),
    "M07": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="No tags.", confidence="HIGH"),
    "M08": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", needs_new_infra="YES", what_directly_observed="BGC-Argo chl/O2/NO3/pH as process proxies.", what_needs_infra="Design-density BGC array CITED $25M/yr.", confidence="HIGH", key_citations=ARGO),
    "M09": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Moored bio-optics; omics autosamplers emerging.", confidence="MEDIUM", key_citations="AOML autosamplers"),
    "M10": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Ballast/underway omics; SOOP.", confidence="MEDIUM"),
    "M11": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="DAS not microbes.", confidence="HIGH"),
    "M12": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", forecast_today="CONDITIONAL", what_directly_observed="O2, NO3, pH, DIC — microbial process signatures.", what_forecast="BGC models (skill regional).", confidence="HIGH", key_citations=ARGO),
    "M13": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Water-quality labs; not citizen microscopy at scale.", confidence="LOW"),
}.items():
    cells["microbes"][m] = spec

# ========== LARVAE ==========
cells["larvae"]["M01"] = C(
    primary_class="INFERRED",
    direct_today="NO",
    inferred_today="YES",
    forecast_today="CONDITIONAL",
    speculative="YES",
    impossible_now="YES",
    what_inferred="Spawn-habitat physics; particle tracking of WATER.",
    what_forecast="Dispersal of water parcels; larvae only if a coupled IBM is validated (usually UNKNOWN).",
    unproven_or_speculative="SPECULATIVE: overlay 'larvae' on SWOT eddies without in situ.",
    physically_impossible_or_not_measurable="Imaging a named larva from orbit.",
    confidence="HIGH",
    key_citations=SAT,
)
for m, spec in {
    "M02": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not aerial-resolvable.", confidence="HIGH"),
    "M03": C(primary_class="DIRECT", direct_today="YES", needs_new_infra="YES", what_directly_observed="ISIIS/UVP/nets — few platforms.", what_needs_infra="Imaging-profiler network.", confidence="HIGH"),
    "M04": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Maybe as mixed plankton scatter; not named larvae.", confidence="MEDIUM", key_citations=AC),
    "M05": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Not vocal.", confidence="HIGH"),
    "M06": C(primary_class="DIRECT", direct_today="YES", inferred_today="YES", unproven="YES", what_directly_observed="eDNA/eRNA presence — mixed with adult DNA.", unproven_or_speculative="Separating life stages from water DNA alone.", physically_impossible_or_not_measurable="Larval GPS from one filter.", confidence="MEDIUM", key_citations=ED),
    "M07": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="Routine individual larval tags not available.", confidence="HIGH"),
    "M08": C(primary_class="NEEDS_INFRA", needs_new_infra="YES", inferred_today="YES", direct_today="LIMITED", what_directly_observed="Occasional imaging payloads.", what_inferred="Transport from models+Argo.", what_needs_infra="Glider imaging/eDNA in spawn seasons.", confidence="MEDIUM", key_citations=ARGO),
    "M09": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Intake samples; light traps.", confidence="MEDIUM"),
    "M10": C(primary_class="DIRECT", direct_today="CONDITIONAL", what_directly_observed="Ichthyoplankton bycatch/science of opportunity; CPR some stages.", confidence="MEDIUM"),
    "M11": C(primary_class="IMPOSSIBLE", impossible_now="YES", physically_impossible_or_not_measurable="DAS not larvae.", confidence="HIGH"),
    "M12": C(primary_class="INFERRED", inferred_today="YES", forecast_today="CONDITIONAL", what_inferred="Currents, T, OA (calcifiers).", what_forecast="Particle-tracking skill is oceanography not biology unless validated.", confidence="HIGH"),
    "M13": C(primary_class="LIMITED", direct_today="LIMITED", what_directly_observed="Rare (aquarium/hatchery reports) — not wild maps.", confidence="LOW"),
}.items():
    cells["larvae"][m] = spec

# Sanity: every taxon x mod present
missing = []
for t, _ in TAXA:
    for mid, _ in MODS:
        if mid not in cells[t]:
            missing.append((t, mid))
if missing:
    raise SystemExit(f"Missing cells: {missing}")

FIELDS = [
    "taxon_class",
    "taxon_label",
    "modality_id",
    "modality_name",
    "primary_class",
    "direct_today",
    "inferred_today",
    "forecast_today",
    "needs_new_infra",
    "unproven",
    "speculative",
    "impossible_now",
    "what_directly_observed",
    "what_inferred",
    "what_forecast",
    "what_needs_infra",
    "unproven_or_speculative",
    "physically_impossible_or_not_measurable",
    "confidence",
    "key_citations",
    "notes",
    "as_of_date",
]


def main():
    out = Path(__file__).with_name("taxa_modality_feasibility.csv")
    rows = []
    for t, label in TAXA:
        for mid, mname in MODS:
            d = cells[t][mid]
            row = {
                "taxon_class": t,
                "taxon_label": label,
                "modality_id": mid,
                "modality_name": mname,
                "as_of_date": "2026-09-18",
            }
            for k in FIELDS:
                if k in row:
                    continue
                row[k] = d.get(k, EMPTY.get(k, ""))
            rows.append(row)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
