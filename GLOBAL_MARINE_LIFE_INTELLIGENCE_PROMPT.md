# GLOBAL MARINE LIFE INTELLIGENCE SYSTEM

## Unified prompt (persisted excerpt)

This file stores core scientific-honesty rules from the unified autonomous prompt, plus **section 32** (USER-CENTERED UI, UX, AND GLOBE INTERACTION) in full. It is guidance for builders — not a claim that a planetary digital twin, live animal tracker, or published likelihood/forecast product already exists.

Do not invent live-animal density from SST, chlorophyll, AIS, or empty water. Empty cells mean **don't know**, not absence. Current location and forecast playback require a **PUBLISHED** model card. Past reports are historical detections, not "where it is right now."

---

2. SCIENTIFIC HONESTY, SAFETY, AND LIMITS
================================================================================

You must never:

  - claim exact location of every individual fish, shellfish, or marine organism;
  - claim an exact wild population count without an appropriate survey/census method;
  - infer fish abundance from vessel density alone;
  - infer direct presence from satellite-derived temperature/chlorophyll alone;
  - confuse “not detected” with “absent”;
  - confuse habitat suitability with current occurrence;
  - confuse current occurrence with future forecast;
  - confuse direct observation of an individual with population-level distribution;
  - imply safe or legal harvesting based on a biological map;
  - give navigation, maritime-safety, legal, food-safety, or regulatory authorization;
  - hide data gaps;
  - use restricted data without documented rights;
  - expose precise sensitive locations;
  - treat a model estimate as confirmed reality.

All public and internal outputs must distinguish:

  OBSERVED:
    Direct evidence exists.

  INFERRED:
    A model estimates the state from evidence and environmental context.

  FORECAST:
    A model predicts a future state.

  UNKNOWN:
    The evidence is insufficient.

================================================================================

---

## Placement note

Section 32 belongs **after** the visualization / globe section (**21. GLOBAL 3D/4D GLOBE AND VISUAL INTELLIGENCE SYSTEM**) in the full unified prompt. It is persisted here in full so the UX contract is not lost.

---

32. USER-CENTERED UI, UX, AND GLOBE INTERACTION
================================================================================

This system must be usable and understandable by non-scientists.

Primary UI goal:

  “Google Earth–style interactive globe for marine life, with the most granular
   geospatial detail the data supports, and a clear, human-friendly way to see
   where species are likely to be now and in the future.”

The interface must:

  - behave like familiar globe tools (pan, zoom, tilt, fly-to search);
  - present a simple, clear answer first;
  - visually separate observed data, model estimates, and forecasts;
  - show depth and time without overwhelming the user;
  - expose scientific detail only when requested;
  - scale from planetary overview to fine-grained local detail.

--------------------------------------------------------------------
A. GLOBAL LAYOUT AND PRIMARY PANELS
--------------------------------------------------------------------

Use a structure inspired by Google Earth’s UI:
a main 3D viewer, navigation controls, and side panels for search and layers.[web:16][web:17][web:19]

Required layout:

  LEFT SIDEBAR (PRIMARY CONTROLS)
    - Species search
    - Location and time controls
    - Favorites / saved views
    - Layer toggles (species, environment, observations, forecasts)
    - Simple filters (species group, life stage, depth band)
    - Quick presets (e.g., “Surface fish”, “Deep species”, “Spawning”, “Nursery”)

  CENTER: MAIN 3D/4D VIEWER
    - Interactive globe / map
    - Current species distribution
    - Forecast animation
    - Depth slices and vertical transects
    - Environmental overlays (when toggled)
    - 2D map fallback (for low-bandwidth or simpler use)

  RIGHT SIDEBAR (DETAILS, COLLAPSIBLE)
    - Plain-English summary (“answer” section)
    - Confidence indicator
    - “Why here?” explanation
    - Evidence panel (observations, surveys, tags, eDNA, etc.)
    - Model card link
    - Advanced scientific details (optional Expert Mode)

  TOP BAR
    - Simple description of the tool (“Marine Life Globe”)
    - Global search box (species, place, coordinates)
    - Mode selector:
        Find Species
        Explore Ocean
        Evidence & Data
        Learn & Methods
    - Settings and Help

  BOTTOM STATUS BAR
    - Coordinates
    - Depth band
    - Time/forecast horizon
    - Data freshness
    - Imagery/model loading status

All primary controls must be labeled in plain language.

--------------------------------------------------------------------
B. FIRST-RUN EXPERIENCE AND CORE FLOW
--------------------------------------------------------------------

A new user must be able to:

  1. Search for a species.
  2. Choose a rough region or accept a default.
  3. See where it is likely to be now.
  4. See a simple forecast for the near future.
  5. Understand confidence and depth.
  6. Understand why the system thinks this.
  7. Optionally explore detailed evidence.

Design the first screen to show:

  - A single featured species in a featured region.
  - A short summary:
      “Today, [Species] is most likely in these highlighted areas.”
  - A simple legend:
      “More likely” / “Less likely” / “Unknown” / “Observed”
  - A time slider defaulting to “Now” with “Tomorrow” and “Next 7 days” visible.
  - A depth selector with a small number of meaningful options (e.g. “Surface”,
    “Midwater”, “Near seafloor”, “All depths”).

Include an optional guided tour overlay:

  - “Step 1: Search for a species”
  - “Step 2: Drag the globe and zoom to your region”
  - “Step 3: Move the time slider to see forecast”
  - “Step 4: Click ‘Why here?’ to see key ocean conditions”
  - “Step 5: Click ‘Evidence’ to see actual observations”

Do not show advanced controls before the user sees a basic answer.

--------------------------------------------------------------------
C. PRIMARY USER MODES
--------------------------------------------------------------------

Define four top-level modes. Modes must be obvious and easy to switch.

MODE 1 — FIND SPECIES (DEFAULT)

  - Search for a species.
  - Select a general region (or use auto-region based on species range).
  - Show:
      current likelihood map,
      short-horizon forecast,
      depth band,
      confidence,
      “Why here?” explanation.

  Layout emphasis:
    answer summary → globe → time/depth controls → evidence.

MODE 2 — EXPLORE OCEAN

  - See global ocean conditions (currents, temperature, productivity, habitat).
  - Toggle species overlays.
  - Animate environmental layers.
  - Explore vertical sections and environmental gradients.
  - Use split-screen comparisons (e.g. “species vs. temperature”, “species vs. habitat”).

MODE 3 — EVIDENCE & DATA

  - For specialists and skeptics.
  - Show:
      all recent observations,
      surveys,
      tags,
      acoustic/eDNA detections,
      detection effort,
      data gaps.
  - Provide filters by:
      method,
      time,
      depth,
      source,
      quality,
      license.
  - Allow export in scientific formats (subject to rights).

MODE 4 — LEARN & METHODS

  - Species cards (biology, behavior, climate response).
  - Model cards (inputs, validation, limitations).
  - Methodology explained in plain language.
  - FAQs:
      “Is this tracking?”
      “How accurate is it?”
      “What do the colors mean?”
      “Why does the map sometimes say ‘unknown’?”

Only MODE 1 should be present on initial use; others appear after the first species is selected or via a simple tab change.

--------------------------------------------------------------------
D. INTERACTION PATTERNS (GLOBE, MAP, NAVIGATION)
--------------------------------------------------------------------

Navigation must feel familiar:

  - Click-and-drag to pan the globe.
  - Mouse scroll / pinch to zoom.
  - Mouse/gesture to tilt between top-down and horizon views.
  - Compass ring to rotate, with a “North up” reset.
  - Keyboard arrows for pan; +/- or scroll for zoom.[web:19][web:21]

Core interactions:

  - Hover:
      preview basic info (species, likelihood, depth, time).
  - Click:
      open Evidence Explorer panel for that location.
  - Shift + drag or explicit controls:
      tilt/rotate view.
  - Drag time slider:
      animate distribution and ocean conditions over time.
  - Drag depth slider:
      see distributions at different depth slices.

Provide:

  - A 3D globe for exploration and movement/migration visualization.
  - A 2D map option (flat projection) for simpler tasks and low-bandwidth users.
  - Smooth animation, but allow motion-reduction/“no animation” mode.

Always display an explicit legend for:

  - species likelihood;
  - observed vs inferred vs forecast;
  - depth band;
  - uncertainty;
  - environmental layer.

--------------------------------------------------------------------
E. GRANULAR GEOSPATIAL DETAIL
--------------------------------------------------------------------

The system must support the most granular geospatial representation justified by:

  - data resolution;
  - computational constraints;
  - privacy/ecological safety;
  - visualization performance.

Requirements:

  - Use a global spatial index (e.g., fine grid cells) capable of sub-kilometre or finer resolution where data supports it.
  - At zoomed-out levels:
      aggregate cells into coarser tiles,
      show averages or summaries,
      encode uncertainty and data coverage.
  - At zoomed-in levels:
      show fine-resolution cells with:
        probability,
        abundance index,
        depth, and
        confidence.
  - At local zoom, expose detailed features:
      reef structures,
      seafloor terrain,
      habitat polygons,
      survey transects,
      sensor locations,
      observation footprints,
      where safe and permitted.

Ensure level-of-detail and tiling:

  - global overview: coarse grid, low data density visualization;
  - regional view: medium grid, explicit data coverage and uncertainty;
  - local view: fine grid, detailed layers, but still respecting privacy and sensitivity.

Granular data must never be used to expose exact sensitive locations (e.g., precise spawning grounds, private fishing spots, protected species nesting sites); use coarsening/delay where needed.

--------------------------------------------------------------------
F. INFORMATION HIERARCHY AND LANGUAGE
--------------------------------------------------------------------

Primary answer hierarchy:

  1. Plain-language answer:
       “Where is this species most likely to be?”
       “How certain is this?”
       “At what depth?”
       “What will likely change soon?”

  2. Visual map/globe:
       highlighted zones, clear legends, intuitive colors.

  3. Simple controls:
       time, depth, species, region.

  4. “Why here?”:
       top 3–5 ocean conditions or ecological factors, in plain language.

  5. Confidence:
       high / medium / low, with a short explanation.

  6. Evidence:
       shows observed data separately from model estimates.

  7. Advanced science:
       methodology, variables, model architecture, validation, uncertainty math.

Language rules in primary UI:

  - Avoid jargon like “covariate”, “spatiotemporal posterior”, “CPUE”.
  - Use:
      “ocean conditions that matter”,
      “likelihood of presence”,
      “relative concentration compared to normal”,
      “catch rate adjusted for effort”.
  - Always label:
      “Confirmed observation”,
      “Model estimate”,
      “Forecast”,
      “Unknown/not enough data”,
      “Favorable habitat—not confirmed presence”.
  - Never say “the fish are here now” unless backed by direct, recent observation.

Place scientific terms in expandable panels:

  - Methodology
  - Model card
  - “Show details” toggle
  - “Expert mode” switch

--------------------------------------------------------------------
G. ACCESSIBILITY, PERFORMANCE, AND COGNITIVE LOAD
--------------------------------------------------------------------

Accessibility:

  - Colorblind-safe palettes.
  - Do not rely on color alone; use patterns/textures for uncertainty and data gaps.
  - Readable fonts and sufficient contrast.
  - Keyboard navigation for core interactions.
  - Screen-reader labels for main results and map summary.
  - Motion-reduction options (disable or simplify animations).
  - Low-bandwidth mode:
      static map images,
      reduced layers,
      fewer animations,
      precomputed summaries.

Performance:

  - Progressive loading:
      show skeleton states and simple maps quickly, refine as data arrives.
  - Streaming/tiling architecture:
      load only needed tiles/layers at current zoom and region.
  - Lazy-loading of heavy datasets:
      only when user opens advanced panels.
  - Clear loading indicators:
      e.g., “Updating ocean conditions…”, “Loading observations…”.

Cognitive load:

  - Minimize simultaneous visible layers.
  - Avoid crowded legends and overlapping colors.
  - Group controls into logical sections:
      species,
      place,
      time,
      depth,
      layers.
  - Hide rare-use advanced controls behind “Advanced” toggles.
  - Provide presets for typical questions:
      “Today near me”,
      “This season in [region]”,
      “Deep ocean view”,
      “Migration paths”.

--------------------------------------------------------------------
H. FLAGSHIP DEMO FLOW (GOOGLE EARTH FOR MARINE LIFE)
--------------------------------------------------------------------

Design a flagship demo experience for one species in one region that shows:

  1. A rotating globe with ocean currents.
  2. Highlighted zones of likely presence now (top-down view).
  3. Simple time slider showing 3–7 days of forecast movement.
  4. Depth slider revealing changes in vertical distribution.
  5. Toggle to overlay one key ocean condition (e.g. temperature or chlorophyll).
  6. Clear confidence indicator (e.g. “Confidence: medium—few recent observations here”).
  7. A click on a hot spot opening the Evidence Explorer.
  8. A side panel explaining:
       - “This is a probability estimate, not live tracking.”
       - “Based on ocean conditions, historical observations, and validated models.”
       - “Observed data points are shown as separate icons.”

The demo must feel like:

  “Google Earth, but instead of just satellite imagery and terrain, it shows where
   marine life is most likely to be—and why.”

It must be impressive visually, but conservative scientifically.

--------------------------------------------------------------------
I. UI/UX REVIEW AND ITERATION
--------------------------------------------------------------------

Create a dedicated UX Review Agent that:

  - audits all screens and flows;
  - ensures the primary flow answers:
      “Where is [species] likely to be now or soon?” in under 30 seconds;
  - checks that observed vs inferred vs forecast is always clear;
  - checks that depth, time, and confidence are visible and understandable;
  - flags jargon and replaces it with plain-language copy;
  - identifies clutter, unnecessary controls, and confusing legends;
  - recommends simplified layouts and progressive disclosure.

The system must treat UX as a first-class scientific tool:

  Clear understanding by users is part of scientific honesty.

================================================================================
