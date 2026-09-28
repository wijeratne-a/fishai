#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path
OUT = Path(__file__).resolve().parents[1]

def wcsv(name, fieldnames, rows):
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        wr.writeheader()
        for r in rows:
            for k in fieldnames:
                r.setdefault(k, "")
            wr.writerow(r)
    parsed = list(csv.DictReader(path.open(encoding="utf-8")))
    assert parsed and all(len(r) == len(fieldnames) for r in parsed)
    print(name, len(parsed))

COLS = ["Guild", "Variable", "Variable type", "Mechanism", "Evidence strength",
        "Example species/region/life stage", "Depth layer", "Spatial scale", "Temporal scale",
        "Relevant lag", "Expected nonlinearity", "Likely interactions", "Historical availability (dataset)",
        "Nowcast availability (dataset and latency)", "Forecast availability (dataset and lead)",
        "Not available at forecast time? (yes/no/partial)", "Surface as bottom proxy acceptable? (with evidence)",
        "Key evidence gaps", "sources"]

rows = []

def add(g, var, typ, mech, ev, ex, depth, spat, temp, lag, nl, inter, hist, now, fc, na, proxy, gap, src):
    rows.append({
        "Guild": g, "Variable": var, "Variable type": typ, "Mechanism": mech, "Evidence strength": ev,
        "Example species/region/life stage": ex, "Depth layer": depth, "Spatial scale": spat,
        "Temporal scale": temp, "Relevant lag": lag, "Expected nonlinearity": nl, "Likely interactions": inter,
        "Historical availability (dataset)": hist, "Nowcast availability (dataset and latency)": now,
        "Forecast availability (dataset and lead)": fc, "Not available at forecast time? (yes/no/partial)": na,
        "Surface as bottom proxy acceptable? (with evidence)": proxy, "Key evidence gaps": gap, "sources": src,
    })

# reef
add("reef fish", "habitat code / benthic class", "habitat", "Shelter and foraging substrate change detection and occurrence",
    "STRONG_REPLICATED", "Keys STE PART habitat+depth+vis beat prevalence 2022", "survey band", "patch-reef", "survey",
    "0", "habitat-specific intercepts", "depth x habitat", "RVC HABITAT_CD", "only if mapped habitat rasters", "no (static ok)",
    "no if static map used", "no — habitat is not SST", "no public habitat rasters on disk", "Keys model; BEHAVIOR catalog")
add("reef fish", "depth", "physical", "Occupancy and detectability vary with depth band",
    "STRONG_REPLICATED", "Keys STE PART", "occupied m", "site", "survey", "0", "nonlinear", "vis, habitat",
    "RVC DEPTH", "bathymetry raster", "static", "no", "n/a", "SBC has no per-transect depth", "Keys model")
add("reef fish", "underwater visibility", "observation", "Optical detectability; not a preference for clear water",
    "STRONG_REPLICATED", "Keys vis in design", "optical", "dive", "minutes-hours", "0", "threshold in turbid water",
    "complexity", "RVC field", "not forecastable as ecology", "no", "yes", "n/a", "same-day only", "Keys model; catalog optical_detectability")
add("reef fish", "depth-resolved temperature", "physical", "Physiology at occupied depth; surface SST often wrong layer",
    "LIMITED", "Keys: HYCOM at depth no CV gain so dropped; SBC kelp bass CV gain then 2022 fail", "occupied m", "km", "days",
    "0 to days", "thermal window", "year/heatwave confound", "HYCOM GOFS 3.1 historical", "ESPC-D-V02 ~48h (P001)", "RTOFS days if archived",
    "partial (product shift)", "NO — Keys test used depth T not SST; SST-as-bottom unsupported", "nonstationary warm-year confound", "P001; P009")
add("reef fish", "SST", "physical", "Sometimes correlates; often proxy for season or surface only",
    "LIMITED", "PR MUR/OISST untrusted (future-day); EcoCast pelagic not reef", "surface", "km", "days", "0",
    "thermal", "season", "MUR/OISST", "MUR ~1d", "RTOFS SST", "no for SST", "NO without evidence", "reef fish at 5-20 m", "brutal-audit; S74")
add("reef fish", "rugosity / complexity", "habitat", "Shelter; also hides fish from divers",
    "MODERATE", "Keys RUGOSITY_CD candidate not in STE PART v1", "bottom", "meters-patch", "static-slow", "0",
    "threshold", "vis", "survey code; no raster", "none on disk", "no", "yes if no map", "n/a", "empty data/raw/habitat", "catalog structural_shelter")
add("reef fish", "kelp canopy", "habitat", "SBC same-day kelp is a survey covariate; Landsat kelp is a map",
    "MODERATE", "SBC knb-lter-sbc.18.30", "surface canopy / 0-2 m", "transect to km", "days-season", "0 for same-day",
    "threshold", "temp", "SBC kelp counts", "Landsat delayed", "no same-day kelp at forecast", "yes for same-day counts",
    "n/a", "same-day kelp not a forecast input", "socal SUMMARY")
add("reef fish", "chlorophyll", "prey_productivity", "Prey proxy; lag; bottom contamination in shallow water",
    "WEAK", "Keys VIIRS weekly often masked", "optical surface", "km", "weeks", "weeks if used",
    "unknown", "fronts", "VIIRS SQ weekly", "days-week", "poor coastal", "partial", "NO", "unusable over Keys reef", "historical-environment-manifest")

add("demersal fish", "bottom temperature", "physical", "Thermal habitat at depth of gear/fish",
    "MODERATE", "trawl indices generally use bottom T not SST", "bottom", "10s km", "days-season", "0-days",
    "window", "oxygen", "HYCOM/GLORYS 3D", "ESPC/GLORYS days", "RTOFS 3D", "partial", "NO — literature default is bottom T",
    "FishAI has no trawl time series", "S72")
add("demersal fish", "dissolved oxygen / metabolic index", "physical", "Avoidance of low O2",
    "MODERATE", "OMZ margin taxa", "bottom/mid", "10s km", "days", "0", "threshold", "T x O2",
    "not in repo", "sparse gliders/models", "limited", "yes often", "NO", "not joined", "BEHAVIOR catalog oxygen_at_depth")
add("demersal fish", "substrate / bathymetry", "habitat", "Gear catchability and true habitat",
    "STRONG_REPLICATED", "trawl untrawlable vs soft", "bottom", "km", "static", "0", "categorical",
    "gear", "not in repo", "static maps", "static", "no", "n/a", "empty habitat dir", "S72")
add("demersal fish", "SST", "physical", "Weak proxy", "WEAK", "only if well mixed", "surface", "km", "days", "0",
    "misleading", "season", "MUR", "1d", "days", "no", "NO without mixing evidence", "do not use alone", "S75")

add("coastal pelagic fish", "SST", "physical", "Thermal habitat for epipelagic schools",
    "MODERATE", "sardine/anchovy CCS; skill can collapse in heatwave (P009)", "surface", "10s km", "days", "0-days",
    "window; nonstationary", "chl lag", "MUR/OISST", "1d", "seasonal SST some skill", "no",
    "sometimes — they occupy surface mixed layer; still not a location", "nonstationary SST-catch (P009)", "P009; S75")
add("coastal pelagic fish", "chlorophyll lag", "prey_productivity", "Prey after bloom",
    "MODERATE", "CCS CPS", "surface", "10s km", "weeks", "weeks", "lag peak", "SST",
    "VIIRS", "days-week", "poor", "partial", "surface ok for epipelagic", "lag length unknown a priori", "S75")
add("coastal pelagic fish", "fronts / SSH / EKE", "physical", "Aggregation at gradients",
    "MODERATE", "EcoCast-class pelagics", "surface", "10s km", "days", "0-days", "threshold", "SST",
    "DUACS/SST gradient", "days", "days", "no", "surface ok", "not fish; preferential sampling if from catch", "S74; S75")
add("coastal pelagic fish", "upwelling (CUTI/BEUTI)", "physical", "Nutrient supply CCS",
    "MODERATE", "California Current", "surface-mid", "100 km", "days-season", "days", "nonlinear", "SST",
    "not in repo", "indices delayed", "seasonal", "partial", "n/a", "not joined", "S75")

add("oceanic pelagic fish", "SST", "physical", "Thermal habitat",
    "MODERATE", "tuna/swordfish habitat models S75", "surface", "10s-100 km", "days", "0",
    "window", "fronts", "MUR", "1d", "RTOFS/seasonal", "no", "often yes for surface-associated tunas; still habitat not location",
    "tag bias", "S75")
add("oceanic pelagic fish", "SSH / eddies / fronts", "physical", "Forage concentration",
    "MODERATE", "EcoCast S74", "surface", "10s km", "days", "0-days", "nonlinear", "SST",
    "altimetry", "days", "days", "no", "surface", "validation vs observer not GBIF", "S74")
add("oceanic pelagic fish", "mixed-layer / thermocline depth", "physical", "Vertical habitat",
    "MODERATE", "tuna", "upper 200 m", "10s km", "days", "0", "threshold", "oxygen",
    "HYCOM/GLORYS", "days", "days", "partial", "SST insufficient", "not tested in FishAI", "S75")

add("estuarine fish", "salinity", "physical", "Bounded windows by stage",
    "MODERATE", "diadromous juveniles", "surface-mixing", "estuary", "tidal-season", "hours-days",
    "window", "tide", "not in repo", "WCOFS/ROMS", "days", "partial", "surface often OK in well-mixed estuary",
    "not acquired", "BEHAVIOR salinity_window")
add("estuarine fish", "tide / river discharge", "physical", "Access and transport",
    "MODERATE", "mangrove/estuary", "shallow", "km", "hours-days", "hours", "periodic", "salinity",
    "not in repo", "tide models; USGS discharge", "tides yes", "no for tides", "n/a", "not acquired", "catalog tidal_phase")

add("deep-sea fish", "oxygen and temperature at depth", "physical", "Metabolic constraints",
    "MODERATE", "OMZ associates", "deep", "10s km", "season", "0", "thresholds", "T x O2",
    "HYCOM/GLORYS deep", "days", "limited", "partial", "NO", "no FishAI surveys", "catalog")
add("deep-sea fish", "SST", "physical", "Usually irrelevant", "WEAK", "n/a", "surface", "basin", "days", "0",
    "none", "none", "MUR", "1d", "days", "no", "NO", "do not use", "catalog")

add("polar fish", "ice and temperature", "physical", "Habitat loss/gain",
    "MODERATE", "polar cod literature", "surface-mid", "100 km", "season", "0", "threshold", "ice",
    "not in repo", "NSIDC/HYCOM ice", "seasonal", "partial", "sometimes mixed layer", "out of FishAI domains", "literature")

add("sharks and rays", "SST / depth-resolved T", "physical", "Thermal habitat; species-specific",
    "MODERATE", "tag-based habitat models; EcoCast sharks S74", "surface to occupied", "10s km", "days", "0",
    "window", "fronts, depth", "MUR + HYCOM", "days", "days", "partial", "only if occupied layer is surface",
    "tags restricted; sensitive species withhold", "S74; S85")
add("sharks and rays", "fronts / SSH", "physical", "Foraging", "MODERATE", "EcoCast", "surface", "10s km", "days", "0",
    "nonlinear", "SST", "altimetry", "days", "days", "no", "surface for some spp", "do not publish aggregations", "S74; S85")

add("eggs and larvae", "currents at larval depth", "physical", "Advection",
    "STRONG_REPLICATED", "CalCOFI; CMS S63", "PLD depths", "km-100 km", "days of PLD", "0 during drift",
    "n/a", "vertical behavior", "HYCOM/ROMS", "days", "days", "partial", "NO — need 3D velocity",
    "one cruise 202204; no PLD table", "S62; S63")
add("eggs and larvae", "temperature", "physical", "Development rate / PLD",
    "STRONG_REPLICATED", "ichthyoplankton", "occupied", "km", "days", "days", "rate functions", "food",
    "HYCOM", "days", "days", "partial", "layer must match spawn depth", "no adult inference", "S62")
add("eggs and larvae", "SST", "physical", "Sometimes spawn habitat",
    "MODERATE", "CUFES eggs near surface", "surface", "km", "days", "0", "window", "currents",
    "MUR", "1d", "days", "no", "only for neustonic eggs", "eggs stay eggs", "CUFES holdings")

add("juveniles", "nursery habitat (seagrass/mangrove/estuary)", "habitat", "Stage-specific occupancy",
    "MODERATE", "many reef fishes", "shallow", "patch", "season", "0", "threshold", "salinity",
    "not in repo (sensitive)", "static maps", "static", "no", "n/a", "do not publish pins", "catalog nursery; S86")
add("juveniles", "SST/bottom T", "physical", "Growth windows", "LIMITED", "stage-specific", "occupied", "km", "days", "0",
    "window", "habitat", "HYCOM", "days", "days", "partial", "match depth", "RVC mixes sizes unless split", "LIFE STAGE rules")

add("spawning adults", "season / photoperiod", "timing", "Reproductive timing",
    "MODERATE", "aggregating spawners", "occupied", "region", "weeks-month", "0", "seasonal peak", "T",
    "calendar", "calendar", "calendar", "no", "n/a", "do not map aggregations", "S85; SAFETY")
add("spawning adults", "temperature", "physical", "Cue or constraint",
    "LIMITED", "species-specific", "occupied", "km", "days-weeks", "days", "threshold", "season",
    "HYCOM", "days", "days", "partial", "match depth", "WITHHOLD aggregation sites", "S84; S85")

wcsv("FISH_BEHAVIOR_VARIABLE_MATRIX.csv", COLS, rows)

CCOLS = ["Tool", "Category", "Vendor or operator", "Inputs used", "Direct vs inferred", "Real output",
         "Claimed spatial resolution", "Claimed temporal resolution", "Uncertainty handling",
         "Performance evidence (independent | vendor_only | none_found)", "Evidence detail",
         "Marketing claims not independently validated", "Scientifically useful components",
         "Components FishAI must not adopt", "Status checked (date and whether product still exists)", "sources"]

tools = []
def t(**k):
    tools.append(k)

t(Tool="Fishbrain", Category="crowd-sourced catch-report", **{"Vendor or operator": "Fishbrain",
  "Inputs used": "user catches, photos, some location", "Direct vs inferred": "direct catch reports; inferred hotspots",
  "Real output": "social catch map and tips", "Claimed spatial resolution": "point to site",
  "Claimed temporal resolution": "near real-time user posts", "Uncertainty handling": "none scientific",
  "Performance evidence (independent | vendor_only | none_found)": "none_found",
  "Evidence detail": "no peer-reviewed ecological skill vs surveys found this pass",
  "Marketing claims not independently validated": "better fishing via app data",
  "Scientifically useful components": "none without complete effort+zeros",
  "Components FishAI must not adopt": "catch pins, hotspots, where-to-fish",
  "Status checked (date and whether product still exists)": "2026-09-27 public product exists (not logged-in audit)",
  "sources": "vendor_documentation; SAFETY"})
t(Tool="Navionics SonarChart", Category="bathymetric chart", **{"Vendor or operator": "Navionics/Garmin",
  "Inputs used": "official charts + crowd sonar", "Direct vs inferred": "direct depths; interpolated bathy",
  "Real output": "navigable bathymetry", "Claimed spatial resolution": "higher than official in places",
  "Claimed temporal resolution": "updated with uploads", "Uncertainty handling": "quality varies; not probabilistic",
  "Performance evidence (independent | vendor_only | none_found)": "vendor_only",
  "Evidence detail": "sonar bathymetry is a measurement of depth not fish",
  "Marketing claims not independently validated": "fishing contour marketing",
  "Scientifically useful components": "bathymetry as habitat covariate with quality flags",
  "Components FishAI must not adopt": "fishing-spot overlays",
  "Status checked (date and whether product still exists)": "2026-09-27 product line exists",
  "sources": "vendor_documentation"})
t(Tool="C-MAP Genesis", Category="bathymetric chart", **{"Vendor or operator": "C-MAP/Navico",
  "Inputs used": "crowd sonar + charts", "Direct vs inferred": "direct depths",
  "Real output": "bathy maps", "Claimed spatial resolution": "fine contours",
  "Claimed temporal resolution": "user uploads", "Uncertainty handling": "unspecified",
  "Performance evidence (independent | vendor_only | none_found)": "vendor_only",
  "Evidence detail": "depth not fish", "Marketing claims not independently validated": "fishing maps",
  "Scientifically useful components": "bathy hypothesis", "Components FishAI must not adopt": "target contours as fish",
  "Status checked (date and whether product still exists)": "2026-09-27 exists", "sources": "vendor_documentation"})
t(Tool="Garmin ActiveCaptain / Quickdraw", Category="navigational + crowd bathy", **{"Vendor or operator": "Garmin",
  "Inputs used": "user sonar, POIs, weather", "Direct vs inferred": "depths direct; fish inferred by users",
  "Real output": "charts, community layers", "Claimed spatial resolution": "varies",
  "Claimed temporal resolution": "community", "Uncertainty handling": "none",
  "Performance evidence (independent | vendor_only | none_found)": "none_found",
  "Evidence detail": "navigation tool", "Marketing claims not independently validated": "community fishing intel",
  "Scientifically useful components": "bathy", "Components FishAI must not adopt": "community bite layers",
  "Status checked (date and whether product still exists)": "2026-09-27 exists", "sources": "vendor_documentation"})
t(Tool="Simrad echosounders", Category="onboard sonar", **{"Vendor or operator": "Navico/Simrad",
  "Inputs used": "active acoustics under the boat", "Direct vs inferred": "direct backscatter; inferred fish",
  "Real output": "water-column display", "Claimed spatial resolution": "under-keel",
  "Claimed temporal resolution": "real-time", "Uncertainty handling": "operator interpretation",
  "Performance evidence (independent | vendor_only | none_found)": "vendor_only",
  "Evidence detail": "backscatter is not species without TS/trawl", "Marketing claims not independently validated": "AI fish ID claims need independent tests",
  "Scientifically useful components": "none for FishAI public product", "Components FishAI must not adopt": "real-time targeting display",
  "Status checked (date and whether product still exists)": "2026-09-27 exists", "sources": "vendor_documentation"})
t(Tool="Furuno echosounders", Category="onboard sonar", **{"Vendor or operator": "Furuno",
  "Inputs used": "acoustics", "Direct vs inferred": "backscatter direct",
  "Real output": "sonar image", "Claimed spatial resolution": "under-keel",
  "Claimed temporal resolution": "real-time", "Uncertainty handling": "operator",
  "Performance evidence (independent | vendor_only | none_found)": "vendor_only",
  "Evidence detail": "same as Simrad", "Marketing claims not independently validated": "species/size AI if advertised",
  "Scientifically useful components": "none public", "Components FishAI must not adopt": "targeting",
  "Status checked (date and whether product still exists)": "2026-09-27 exists", "sources": "vendor_documentation"})
t(Tool="TimeZero / MaxSea", Category="navigational software", **{"Vendor or operator": "Furuno/MaxSea lineage",
  "Inputs used": "charts, radar, AIS, optional SST overlays", "Direct vs inferred": "nav direct; SST inferred habitat",
  "Real output": "plotter software", "Claimed spatial resolution": "chart + overlay",
  "Claimed temporal resolution": "nav real-time; SST delayed", "Uncertainty handling": "none ecological",
  "Performance evidence (independent | vendor_only | none_found)": "none_found",
  "Evidence detail": "plotter", "Marketing claims not independently validated": "ocean overlays as fish",
  "Scientifically useful components": "issue-time discipline for overlays if timestamps shown", "Components FishAI must not adopt": "fishing modules",
  "Status checked (date and whether product still exists)": "2026-09-27 TimeZero exists", "sources": "vendor_documentation"})
t(Tool="SatFish", Category="satellite ocean-condition / fishing forecast", **{"Vendor or operator": "SatFish",
  "Inputs used": "SST, chlorophyll, altimetry (typical of class)", "Direct vs inferred": "env direct; fish inferred",
  "Real output": "maps of ocean conditions marketed to anglers", "Claimed spatial resolution": "km-class satellite",
  "Claimed temporal resolution": "daily-ish", "Uncertainty handling": "typically none",
  "Performance evidence (independent | vendor_only | none_found)": "none_found",
  "Evidence detail": "no FishAI-verified Brier vs surveys", "Marketing claims not independently validated": "where fish will be",
  "Scientifically useful components": "SST/chl/fronts as covariate hypotheses", "Components FishAI must not adopt": "fishing forecast branding",
  "Status checked (date and whether product still exists)": "2026-09-27 class exists; page not logged-in",
  "sources": "vendor_documentation"})
t(Tool="Terrafin", Category="satellite ocean-condition", **{"Vendor or operator": "Terrafin",
  "Inputs used": "SST, chlorophyll", "Direct vs inferred": "env direct; fish inferred",
  "Real output": "temp/color charts", "Claimed spatial resolution": "km",
  "Claimed temporal resolution": "daily", "Uncertainty handling": "none",
  "Performance evidence (independent | vendor_only | none_found)": "none_found",
  "Evidence detail": "charts of SST/chl", "Marketing claims not independently validated": "bite prediction",
  "Scientifically useful components": "SST/chl visualization", "Components FishAI must not adopt": "bite maps",
  "Status checked (date and whether product still exists)": "2026-09-27 exists historically; not re-verified login",
  "sources": "vendor_documentation"})
t(Tool="ROFFS", Category="dynamic habitat / fishing forecast", **{"Vendor or operator": "Roffer's Ocean Fishing Forecasting Service",
  "Inputs used": "SST, color, currents, fishery knowledge (described publicly as oceanographic analyses)", "Direct vs inferred": "env + expert inference",
  "Real output": "forecast charts for paying clients", "Claimed spatial resolution": "regional charts",
  "Claimed temporal resolution": "short-term", "Uncertainty handling": "not a published Brier",
  "Performance evidence (independent | vendor_only | none_found)": "vendor_only",
  "Evidence detail": "commercial success ≠ ecological validation (preferential sampling)",
  "Marketing claims not independently validated": "find fish", "Scientifically useful components": "front/current analysis as hypotheses",
  "Components FishAI must not adopt": "paid hotspot forecasts",
  "Status checked (date and whether product still exists)": "2026-09-27 company known to exist; not a scientific benchmark",
  "sources": "vendor_documentation; SAFETY"})
t(Tool="Hilton's Realtime-Navigator", Category="satellite ocean-condition", **{"Vendor or operator": "Hilton's",
  "Inputs used": "SST/color class", "Direct vs inferred": "env",
  "Real output": "charts", "Claimed spatial resolution": "km",
  "Claimed temporal resolution": "daily", "Uncertainty handling": "none",
  "Performance evidence (independent | vendor_only | none_found)": "none_found",
  "Evidence detail": "not surveyed this pass beyond class", "Marketing claims not independently validated": "fishing charts",
  "Scientifically useful components": "SST", "Components FishAI must not adopt": "hotspots",
  "Status checked (date and whether product still exists)": "2026-09-27 not independently confirmed live",
  "sources": "vendor_documentation"})
t(Tool="OceanPlus", Category="satellite ocean-condition", **{"Vendor or operator": "unclear/ambiguous name",
  "Inputs used": "unknown", "Direct vs inferred": "unknown",
  "Real output": "unknown", "Claimed spatial resolution": "unknown",
  "Claimed temporal resolution": "unknown", "Uncertainty handling": "unknown",
  "Performance evidence (independent | vendor_only | none_found)": "none_found",
  "Evidence detail": "name collides with multiple products; not uniquely identified",
  "Marketing claims not independently validated": "n/a", "Scientifically useful components": "none identified",
  "Components FishAI must not adopt": "n/a",
  "Status checked (date and whether product still exists)": "2026-09-27 NOT uniquely identified",
  "sources": "none"})
t(Tool="Global Fishing Watch", Category="vessel intelligence", **{"Vendor or operator": "GFW / research partners",
  "Inputs used": "AIS, VIIRS lights, SAR (Paolo et al. 2024 class)", "Direct vs inferred": "vessels direct; fishing inferred",
  "Real output": "apparent fishing effort maps", "Claimed spatial resolution": "km cells",
  "Claimed temporal resolution": "hours-days", "Uncertainty handling": "papers discuss classification error",
  "Performance evidence (independent | vendor_only | none_found)": "independent",
  "Evidence detail": "Kroodsma et al. 2018 Science on AIS fishing; later SAR papers; this is vessel effort not fish",
  "Marketing claims not independently validated": "n/a as science org", "Scientifically useful components": "effort as bias covariate; IUU research",
  "Components FishAI must not adopt": "AIS as fish location; public targeting of boats",
  "Status checked (date and whether product still exists)": "2026-09-27 GFW public maps exist",
  "sources": "S01; literature Kroodsma 2018"})
t(Tool="CLS CatSat", Category="tuna-fleet decision support", **{"Vendor or operator": "CLS",
  "Inputs used": "satellite ocean + fleet tools (public marketing)", "Direct vs inferred": "env + fleet",
  "Real output": "ocean products for tuna fleets", "Claimed spatial resolution": "km",
  "Claimed temporal resolution": "daily-class", "Uncertainty handling": "vendor",
  "Performance evidence (independent | vendor_only | none_found)": "vendor_only",
  "Evidence detail": "fleet tools are not survey likelihoods", "Marketing claims not independently validated": "find tuna",
  "Scientifically useful components": "ocean layers", "Components FishAI must not adopt": "fleet targeting",
  "Status checked (date and whether product still exists)": "2026-09-27 CLS marine services exist",
  "sources": "vendor_documentation"})
t(Tool="FAD echosounder buoys (Satlink/Marine Instruments/Zunibal class)", Category="onboard/remote sonar", **{"Vendor or operator": "buoy vendors + tuna fleets",
  "Inputs used": "acoustic biomass under FADs", "Direct vs inferred": "backscatter direct; species mix inferred",
  "Real output": "biomass index at FAD", "Claimed spatial resolution": "FAD-scale",
  "Claimed temporal resolution": "hours", "Uncertainty handling": "research papers discuss TS mix",
  "Performance evidence (independent | vendor_only | none_found)": "independent",
  "Evidence detail": "scientific literature uses buoy acoustics as relative abundance research; not a public FishAI layer",
  "Marketing claims not independently validated": "exact tons of yellowfin", "Scientifically useful components": "sensor-based index research example",
  "Components FishAI must not adopt": "public FAD-level targeting",
  "Status checked (date and whether product still exists)": "2026-09-27 industry products exist",
  "sources": "literature; SAFETY"})
t(Tool="EcoCast", Category="scientific conservation DOM", **{"Vendor or operator": "NOAA/partners",
  "Inputs used": "observer+tag models + daily satellite ocean S74", "Direct vs inferred": "inferred habitat/bycatch risk",
  "Real output": "daily fishing-suitability vs bycatch risk", "Claimed spatial resolution": "regional grid",
  "Claimed temporal resolution": "daily", "Uncertainty handling": "paper discusses; not a fish pin",
  "Performance evidence (independent | vendor_only | none_found)": "independent",
  "Evidence detail": "Hazen et al. 2018: dynamic closures 2-10x smaller than static while protecting bycatch (S74 checked in prior research pass)",
  "Marketing claims not independently validated": "n/a", "Scientifically useful components": "validation, daily ocean, separate species models, management not targeting of protected spp",
  "Components FishAI must not adopt": "turning it into a public bite map",
  "Status checked (date and whether product still exists)": "2026-09-27 EcoCast is a documented NOAA research/management tool",
  "sources": "S74"})
t(Tool="TurtleWatch", Category="scientific conservation DOM", **{"Vendor or operator": "NOAA",
  "Inputs used": "SST habitat for turtles", "Direct vs inferred": "habitat inferred",
  "Real output": "avoidance guidance for fishers (conservation)", "Claimed spatial resolution": "regional",
  "Claimed temporal resolution": "operational product class", "Uncertainty handling": "habitat not location",
  "Performance evidence (independent | vendor_only | none_found)": "independent",
  "Evidence detail": "published NOAA product literature (Howell et al. lineage); not re-scored here",
  "Marketing claims not independently validated": "n/a", "Scientifically useful components": "thermal habitat + conservation framing",
  "Components FishAI must not adopt": "inverting into 'go here for turtles'",
  "Status checked (date and whether product still exists)": "2026-09-27 known NOAA product class",
  "sources": "S77"})
t(Tool="WhaleWatch", Category="scientific conservation DOM", **{"Vendor or operator": "NOAA/partners",
  "Inputs used": "tag-derived habitat + ocean S76", "Direct vs inferred": "habitat",
  "Real output": "blue whale habitat likelihood", "Claimed spatial resolution": "regional",
  "Claimed temporal resolution": "dynamic", "Uncertainty handling": "model-based",
  "Performance evidence (independent | vendor_only | none_found)": "independent",
  "Evidence detail": "Hazen et al. 2017 S76", "Marketing claims not independently validated": "n/a",
  "Scientifically useful components": "tag+ocean with stated question", "Components FishAI must not adopt": "fine whale pins",
  "Status checked (date and whether product still exists)": "2026-09-27 documented",
  "sources": "S76"})
t(Tool="Maxar maritime / dark vessel", Category="vessel intelligence", **{"Vendor or operator": "Maxar (ex DigitalGlobe)",
  "Inputs used": "commercial SAR/optical", "Direct vs inferred": "vessels",
  "Real output": "ship detection", "Claimed spatial resolution": "meters-class imagery",
  "Claimed temporal resolution": "tasked", "Uncertainty handling": "vendor",
  "Performance evidence (independent | vendor_only | none_found)": "vendor_only",
  "Evidence detail": "ships not fish", "Marketing claims not independently validated": "maritime domain awareness as fish finding",
  "Scientifically useful components": "none for ecology", "Components FishAI must not adopt": "vessel hunting",
  "Status checked (date and whether product still exists)": "2026-09-27 Maxar maritime services exist",
  "sources": "vendor_documentation"})

wcsv("COMMERCIAL_TOOL_CAPABILITY_MATRIX.csv", CCOLS, tools)
print("behavior+commercial", len(rows), len(tools))
