---
title: UM Geophysical Monitor
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.0"
app_file: app.py
pinned: false
license: other
---

# UM Geophysical Monitor

**Live multi-hazard globe** with Unitary Manifold φ-overlay.

## Data Sources

| Hazard | Feed |
|---|---|
| ⚡ Earthquakes | USGS M2.5+ GeoJSON feed |
| 🔥 Wildfires | NASA EONET v3 open events |
| 🌋 Volcanoes | NASA EONET v3 + USGS CVO |
| 🌀 Severe Weather | NASA EONET + NOAA NWS active alerts |
| 🌊 Tsunamis | NOAA NWS alerts (Tsunami Warning/Advisory) |
| ❄️ Avalanches | NWAC (Northwest Avalanche Center) danger forecasts |
| ⛰️ Landslides | NASA EONET |
| ⚠️ NWS Alerts | NOAA weather.gov active alerts API |

## Pacific Northwest Hazard Authority Networks

| Hazard | Network | Data |
|---|---|---|
| Earthquakes | [PNSN](https://pnsn.org) / USGS | ShakeAlert, epicenters, tremor maps |
| Avalanches | [NWAC](https://nwac.us) / USFS | Daily danger ratings, mountain weather |
| Volcanoes | [USGS CVO](https://www.usgs.gov/observatories/cvo) | Alert levels, aviation codes, lahar warnings |
| Tsunamis | [NOAA NTWC](https://tsunami.gov) / [WA DNR](https://dnr.wa.gov) | Watches, inundation maps |
| Landslides | [USGS LHP](https://www.usgs.gov/programs/landslide-hazards) | Slope stability maps, event catalog |
| Fire/Weather | [NOAA NWS](https://weather.gov) | Red Flag warnings, severe storm alerts |

## UM Physics Overlay (🔵 Adjacent Track)

Applies Unitary Manifold geometric analogues to geophysical events:

- **P16** — φ-debt entropy injection (recycling module analogue)
- **P806** — back-reacted radion amplitude |Δφ/φ₀|
- **P786** — winding-basin stability score [0,1]
- **P808** — local w_a CPL breathing-mode analogue

**Epistemic status:** 🔵 ADJACENT TRACK — these are geometric analogues applied to
geophysics, not hardgate physics claims. Not to be cited as formal UM predictions.

## Features

- **Live Monitor tab** — fetch all feeds, filter by hazard type, magnitude, PNW region
- **Single Event Analysis** — compute full UM overlay for any custom event
- **Hazard Networks tab** — reference table of authoritative PNW hazard networks

## Deploy

```
pip install gradio pandas
python app.py
```

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
