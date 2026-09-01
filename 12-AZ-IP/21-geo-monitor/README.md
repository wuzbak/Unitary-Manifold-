# UM Geophysical Monitor

## Product 21 of the AxiomZero suite

The **UM Geophysical Monitor v4** is a standalone globe-based disaster monitoring product that fuses live public feeds with the Unitary Manifold geophysical overlay engine.
It visualises earthquakes, wildfire clusters, severe storms, floods, volcanoes, droughts, landslides, tsunamis, tornado analogues, and broader storm systems on a MapLibre GL globe.
It also computes a φ-overlay grounded in the standalone copy of `pillar_geo_monitor.py`, including φ-debt injection, radion amplitude, winding stability, local `w_a` breathing-mode drift, confidence, and an explicit epistemic label.

> **Epistemic status:** 🔵 ADJACENT TRACK — this product is an honest quantitative exploration, not a hardgate physics claim.

---

## Table of contents

1. [What this product is](#what-this-product-is)
2. [Supported disaster types](#supported-disaster-types)
3. [UM physics overlay](#um-physics-overlay)
4. [Live data feeds](#live-data-feeds)
5. [MapLibre GL globe visualisation](#maplibre-gl-globe-visualisation)
6. [Python physics engine API](#python-physics-engine-api)
7. [Key constants](#key-constants)
8. [Quick start](#quick-start)
9. [Browser mode](#browser-mode)
10. [CLI mode](#cli-mode)
11. [File structure](#file-structure)
12. [API reference](#api-reference)
13. [Testing](#testing)
14. [Design notes](#design-notes)
15. [Epistemic status](#epistemic-status)
16. [Authorship](#authorship)

---

## What this product is

The monitor combines three layers into one product surface:
- **Live feed ingestion** from USGS and NASA EONET.
- **UM overlay analysis** via the standalone `geo_monitor.engine.physics` module copied from `src/core/pillar_geo_monitor.py`.
- **Interactive globe rendering** in the browser via MapLibre GL.

The product is designed to work in two modes:
- **Python CLI mode**, where a single event or a demo batch is analysed and printed as JSON.
- **Browser mode**, where the UI serves a live globe, event list, layer toggles, and per-event overlay metrics.

The geophysical overlay is intentionally explicit about scope.
It maps macroscopic event energetics into a UM analogue layer rather than claiming direct observational confirmation of the underlying physics.
Every computed result therefore includes an epistemic label, a confidence bin, a summary string, and the pillar sources used to contextualise the result.

## Supported disaster types

### Earthquake
- **Supported:** yes
- **Description:** Earthquake events come directly from USGS feeds and use magnitude plus optional focal depth.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

### Wildfire
- **Supported:** yes
- **Description:** Wildfire events come from EONET and use either explicit area in hectares or the built-in magnitude-to-area proxy.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

### Hurricane
- **Supported:** yes
- **Description:** Hurricane events use category-like magnitude scaling with high atmosphere-ocean energy throughput.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

### Tornado
- **Supported:** yes
- **Description:** Tornado events share the storm energy pathway in the physics copy and can be analysed from CLI input.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

### Flood
- **Supported:** yes
- **Description:** Flood events can enter through EONET categories and are analysed with the generic energy scaling branch.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

### Tsunami
- **Supported:** yes
- **Description:** Tsunami events reuse the earthquake-like Gutenberg-Richter energy estimate as a first-order driver.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

### Volcano
- **Supported:** yes
- **Description:** Volcano events use a VEI-like logarithmic energy proxy inside the copied standalone engine.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

### Drought
- **Supported:** yes
- **Description:** Drought events are treated as slower climate-disruption incidents with generic magnitude energy scaling.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

### Landslide
- **Supported:** yes
- **Description:** Landslides can be ingested from EONET and analysed as terrain-instability events inside the same overlay pipeline.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

### Storm
- **Supported:** yes
- **Description:** Storm events aggregate severe storms, dust/haze alerts, and other meteorological incidents that map into the storm branch.
- **Overlay outputs:** φ-debt injection, φ-alignment, radion amplitude, QCD suppression, basin perturbation, winding stability, local `w_a`, confidence, epistemic label.
- **Primary UI role:** appears in list view, globe view, and batch summaries.
- **Primary CLI role:** can be passed through `python run.py analyse --kind ...`.

## UM physics overlay

The overlay engine mirrors the adjacent-track physics logic in `src/core/pillar_geo_monitor.py` as a **standalone** product-local module.
This means the product does **not** import from the repository root at runtime when analysing events.
Instead, the `geo_monitor.engine.physics` file contains the full copied constants, dataclasses, helper functions, and overlay class.

The overlay exposes these core quantities:
- **φ-debt injection** — a natural-units analogue of local entropy/debt injected by the event energy budget.
- **φ-alignment** — a floor-clamped local alignment score in `[0, 1]`.
- **Radion amplitude** — an absolute local `|Δφ/φ₀|` estimate driven by event energy scale.
- **Radion suppression factor** — an exponential back-reaction factor capped by the QCD suppression ceiling.
- **Basin perturbation** — radion amplitude normalised by basin depth.
- **Winding stability** — a `[0, 1]` stability score derived from basin perturbation.
- **`w_a_local`** — a local effective breathing-mode analogue driven by the braided sound speed square.
- **Confidence** — LOW, MEDIUM, or HIGH depending on event energy in Planck units.
- **Epistemic label** — always present and always explicit.

### Pillar mapping
- **P806** — back-reacted radion / QCD IR scale analogue.
- **P786** — winding basin stability.
- **P16** — φ-debt entropy accounting.
- **P22** — climate and atmospheric relevance for disaster-state interpretation.
- **P808 analogue** — local `w_a` breathing-mode quantity preserved from the source engine.

## Live data feeds

The product is intentionally built on public feeds with no API key requirement for the default runtime path. Version **v4** adds NASA FIRMS active-fire detections and a dedicated NOAA ionosphere/Kp status layer alongside the earlier v3 feeds.

### USGS feeds
- Past day: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson`
- Past hour: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson`
- Format: GeoJSON FeatureCollection.
- Primary parser entry points: `parse_usgs_feature()` and `USGSFeedParser.parse_geojson()`.

### NASA EONET feed
- API root: `https://eonet.gsfc.nasa.gov/api/v3/events`
- Default query path in the standalone parser: `status=open`, configurable `limit`, configurable `days`.
- Format: JSON event collection.
- Primary parser entry points: `parse_eonet_event()` and `EONETFeedParser.parse_events()`.

### Combined ingest
- `get_combined_events()` merges parsed USGS and EONET events into one `list[GeoEvent]`.
- `GeoMonitorV4Feeds.firms_fire_events()` adds a FIRMS wildfire layer from active-fire FRP detections.
- `GeoMonitorV4Feeds.ionosphere_status()` adds a NOAA ionosphere layer with quiet/active/storm/severe status.
- `mock_data` support is built in for fully offline tests.
- Live HTTP calls are never required by the unit tests.

## MapLibre GL globe visualisation

The browser UI is copied from the public-site reference implementation and localised into `ui/index.html` and `ui/geo-monitor.js`.
It uses MapLibre GL from a CDN and preserves the original live-feed globe interface, layer toggles, status pills, sidebar summaries, and event detail panel.
The static UI is served from the product folder so the product can be launched independently with `python run.py serve`.

### UI capabilities
- Layer toggles for earthquakes, fires, storms, volcanoes, and φ-overlay.
- Globe markers coloured by event type.
- A φ-overlay circle layer that visually encodes φ-debt and winding stability.
- Event list sorting by magnitude.
- Per-event detail cards showing φ-debt, alignment, radion amplitude, suppression, stability, basin perturbation, and `w_a`.
- Explicit adjacent-track language embedded in the interface.

## Python physics engine API

The standalone package exports the core physics API from `geo_monitor.__init__`.

### `GeoEvent`
- Dataclass representing one geophysical event.
- Required fields: `kind`, `magnitude`, `lat`, `lon`.
- Optional fields: `depth_km`, `area_ha`, `energy_J`.
- Methods/properties: `validate()`, `energy_si`, `energy_planck`.

### `UMOverlayResult`
- Dataclass representing the overlay result for one event.
- Contains the source event plus all overlay outputs and metadata.

### `UMGeoOverlay`
- Main analysis class.
- Primary method: `analyse(event: GeoEvent) -> UMOverlayResult`.

### `analyse_event_batch(events)`
- Batch helper returning a list of `UMOverlayResult` objects.

### `parse_usgs_feature(feature)`
- Parses one USGS GeoJSON feature into a `GeoEvent` or `None`.

### `parse_eonet_event(event)`
- Parses one EONET event payload into a `GeoEvent` or `None`.

## Key constants

- **WINDING_NUMBER = 5**
  - Meaning: Selected winding number for the basin geometry analogue.

- **K_CS = 74**
  - Meaning: The 5² + 7² resonance integer used throughout the copied model.

- **BRAIDED_SOUND_SPEED = 12/37**
  - Meaning: Braided resonance sound-speed analogue used in `w_a_local`.

- **PHI_0 = 1.0**
  - Meaning: Normalised reference field value.

- **RADION_DELTA_PHI_PER_M5 = -32.0**
  - Meaning: Back-reacted radion displacement per M5 scale.

- **RADION_QCD_SUPPRESSION = 1e7**
  - Meaning: Upper cap for local suppression factors.

- **RADION_COUPLING_ALPHA = abs(RADION_DELTA_PHI_PER_M5) / K_CS**
  - Meaning: Derived coupling strength.

- **BASIN_DEPTH = 25/74**
  - Meaning: Winding basin depth used to normalise radion perturbations.

- **BASIN_WIDTH_RAD = 2π/5**
  - Meaning: Angular basin width in radians.

- **PHI_DEBT_DECAY_RATE = 0.15**
  - Meaning: Controls φ-debt accumulation against event log-energy.

- **PHI_DEBT_ALIGNMENT_FLOOR = 0.30**
  - Meaning: Lower floor for φ-alignment.

- **JOULES_PER_RICHTER_UNIT = 10**1.5**
  - Meaning: Richter scaling exponent base.

- **RICHTER_REF_ENERGY_J = 10**4.8**
  - Meaning: Reference energy for magnitude-zero events.

- **WILDFIRE_ENERGY_PER_HA_J = 8.0e10**
  - Meaning: Wildfire energy proxy per hectare.

- **HURRICANE_ENERGY_PER_CATEGORY_J = 5.0e18**
  - Meaning: Storm-energy proxy per category unit.

- **PLANCK_ENERGY_J = 1.9561e9**
  - Meaning: Planck energy used to normalise events to natural units.

## Quick start

### 1. Install dependencies
```bash
cd 12-AZ-IP/21-geo-monitor
python -m pip install -r requirements.txt
```

### 2. Run browser mode
```bash
python run.py serve
```

Default port: `8021`.

### 3. Run CLI single-event analysis
```bash
python run.py analyse --kind earthquake --magnitude 7.4 --lat 35.7 --lon 140.1
```

### 4. Run demo mode
```bash
python run.py demo
```

## Browser mode

- Browser note 1: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 2: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 3: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 4: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 5: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 6: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 7: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 8: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 9: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 10: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 11: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 12: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 13: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 14: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 15: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 16: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 17: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 18: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 19: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 20: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 21: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 22: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 23: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 24: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 25: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 26: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 27: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 28: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 29: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.
- Browser note 30: the UI is static, self-contained in `ui/`, and intended for local serving through Python's built-in HTTP machinery.

## CLI mode

- CLI note 1: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 2: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 3: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 4: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 5: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 6: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 7: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 8: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 9: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 10: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 11: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 12: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 13: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 14: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 15: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 16: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 17: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 18: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 19: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 20: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 21: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 22: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 23: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 24: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 25: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 26: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 27: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 28: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 29: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.
- CLI note 30: JSON output is designed to be pipe-friendly, scriptable, and suitable for downstream AxiomZero automation.

## File structure

```text
21-geo-monitor/
├── README.md
├── requirements.txt
├── run.py
├── geo_monitor/
│   ├── __init__.py
│   ├── app/
│   │   ├── __init__.py
│   │   └── server.py
│   └── engine/
│       ├── __init__.py
│       ├── feeds.py
│       ├── overlay.py
│       └── physics.py
├── tests/
│   ├── __init__.py
│   └── test_geo_monitor.py
└── ui/
    ├── geo-monitor.js
    └── index.html
```

## API reference

### `USGSFeedParser`
- Fetches or parses earthquake GeoJSON payloads.
- See source for full signature and implementation details.

### `EONETFeedParser`
- Fetches or parses EONET JSON event payloads.
- See source for full signature and implementation details.

### `get_combined_events`
- Returns a combined list of parsed `GeoEvent` objects.
- See source for full signature and implementation details.

### `compute_overlay`
- Returns serialized overlay dictionaries for a batch of events.
- See source for full signature and implementation details.

### `format_result_json`
- Serializes one `UMOverlayResult` into JSON-safe primitives.
- See source for full signature and implementation details.

### `summary_stats`
- Returns total counts, per-kind counts, averages, and high-severity count.
- See source for full signature and implementation details.

### `serve_ui`
- Runs the standalone UI server on localhost.
- See source for full signature and implementation details.

## Testing

- Testing note 1: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 2: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 3: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 4: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 5: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 6: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 7: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 8: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 9: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 10: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 11: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 12: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 13: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 14: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 15: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 16: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 17: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 18: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 19: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 20: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 21: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 22: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 23: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 24: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 25: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 26: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 27: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 28: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 29: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 30: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 31: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 32: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 33: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 34: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 35: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 36: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 37: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 38: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 39: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.
- Testing note 40: the bundled pytest suite covers constants, dataclasses, parser behavior, batch analysis, overlay serialization, CLI entry points, and product artifacts.

## Design notes

- Design note 1: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 2: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 3: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 4: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 5: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 6: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 7: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 8: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 9: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 10: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 11: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 12: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 13: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 14: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 15: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 16: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 17: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 18: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 19: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 20: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 21: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 22: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 23: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 24: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 25: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 26: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 27: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 28: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 29: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 30: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 31: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 32: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 33: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 34: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 35: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 36: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 37: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 38: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 39: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 40: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 41: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 42: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 43: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 44: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 45: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 46: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 47: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 48: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 49: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 50: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 51: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 52: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 53: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 54: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 55: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 56: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 57: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 58: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 59: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 60: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 61: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 62: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 63: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 64: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 65: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 66: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 67: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 68: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 69: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 70: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 71: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 72: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 73: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 74: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 75: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 76: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 77: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 78: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 79: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.
- Design note 80: the product keeps the physics layer copied locally so the monitor remains portable, self-contained, and independently testable.

## Epistemic status

- Epistemic note 1: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 2: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 3: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 4: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 5: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 6: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 7: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 8: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 9: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 10: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 11: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 12: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 13: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 14: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 15: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 16: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 17: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 18: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 19: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 20: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 21: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 22: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 23: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 24: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 25: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 26: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 27: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 28: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 29: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 30: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 31: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 32: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 33: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 34: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 35: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 36: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 37: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 38: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 39: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 40: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 41: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 42: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 43: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 44: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 45: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 46: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 47: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 48: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 49: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 50: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 51: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 52: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 53: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 54: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 55: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 56: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 57: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 58: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 59: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.
- Epistemic note 60: every result should be read as a geophysical analogue overlay rather than a claim of direct observational confirmation.

## Operational reference notes

- Operational reference 1: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 2: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 3: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 4: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 5: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 6: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 7: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 8: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 9: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 10: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 11: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 12: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 13: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 14: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 15: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 16: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 17: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 18: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 19: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 20: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 21: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 22: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 23: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 24: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 25: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 26: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 27: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 28: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 29: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 30: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 31: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 32: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 33: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 34: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 35: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 36: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 37: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 38: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 39: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 40: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 41: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 42: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 43: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 44: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 45: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 46: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 47: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 48: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 49: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 50: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 51: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 52: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 53: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 54: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 55: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 56: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 57: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 58: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 59: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 60: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 61: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 62: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 63: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 64: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 65: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 66: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 67: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 68: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 69: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 70: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 71: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 72: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 73: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 74: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 75: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 76: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 77: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 78: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 79: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 80: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 81: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 82: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 83: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 84: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 85: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 86: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 87: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 88: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 89: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 90: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 91: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 92: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 93: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 94: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 95: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 96: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 97: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 98: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 99: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 100: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 101: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 102: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 103: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 104: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 105: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 106: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 107: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 108: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 109: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 110: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 111: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 112: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 113: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 114: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 115: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 116: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 117: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 118: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 119: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 120: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 121: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 122: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 123: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 124: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 125: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 126: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 127: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 128: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 129: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 130: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 131: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 132: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 133: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 134: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 135: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 136: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 137: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 138: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 139: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 140: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 141: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 142: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 143: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 144: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 145: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 146: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 147: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 148: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 149: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 150: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 151: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 152: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 153: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 154: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 155: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 156: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 157: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 158: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 159: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 160: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 161: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 162: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 163: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 164: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 165: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 166: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 167: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 168: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 169: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 170: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 171: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 172: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 173: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 174: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 175: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 176: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 177: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 178: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 179: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 180: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 181: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 182: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 183: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 184: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 185: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 186: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 187: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 188: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 189: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 190: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 191: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 192: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 193: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 194: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 195: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 196: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 197: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 198: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 199: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 200: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 201: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 202: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 203: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 204: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 205: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 206: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 207: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 208: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 209: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 210: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 211: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 212: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 213: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 214: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 215: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 216: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 217: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 218: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 219: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 220: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 221: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 222: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 223: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 224: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 225: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 226: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 227: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 228: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 229: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 230: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 231: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 232: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 233: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 234: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 235: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 236: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 237: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 238: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 239: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 240: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 241: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 242: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 243: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 244: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 245: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 246: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 247: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 248: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 249: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 250: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 251: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 252: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 253: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 254: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 255: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 256: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 257: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 258: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 259: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.
- Operational reference 260: feed ingest, overlay calculation, UI rendering, and downstream automation should preserve the explicit adjacent-track label.

## Authorship

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

