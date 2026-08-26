# hf-spaces/geo-monitor/app.py
# UM Geophysical Monitor — Hugging Face Space (Gradio)
#
# Full multi-hazard live monitor with Unitary Manifold φ-overlay.
# Sources: USGS (earthquakes), NASA EONET (wildfires/storms/volcanoes),
#          NOAA NWS (severe weather, tsunamis, fire weather),
#          NWAC (avalanche danger ratings — WA + N. Oregon Cascades)
#
# Hazard authority network reference (Pacific Northwest):
#   Earthquakes  → PNSN / USGS Earthquake Hazards
#   Avalanches   → NWAC / USFS
#   Volcanoes    → USGS Cascades Volcano Observatory (CVO)
#   Tsunamis     → NOAA NTWC / WA DNR
#   Landslides   → USGS Landslide Hazards Program
#   Fire/Weather → NOAA NWS
#
# 🔵 ADJACENT TRACK — UM physics overlays are geometric analogues.
#    Not hardgate physics claims.
#
# AxiomZero Technologies & Consulting, SPC — UBI 606 239 876

from __future__ import annotations

import json
import math
import urllib.request
import urllib.parse
from typing import Any

try:
    import gradio as gr
    GRADIO_OK = True
except ImportError:
    GRADIO_OK = False

try:
    import pandas as pd
    PANDAS_OK = True
except ImportError:
    PANDAS_OK = False

# ── UM Physics Constants ───────────────────────────────────────────────────────
WINDING_NUMBER               = 5
K_CS                         = 74           # 5² + 7²
BRAIDED_SOUND_SPEED          = 12 / 37
PHI_0                        = 1.0
RADION_DELTA_PHI_PER_M5      = -32.0
RADION_QCD_SUPPRESSION       = 1e7
RADION_COUPLING_ALPHA        = abs(RADION_DELTA_PHI_PER_M5) / K_CS   # ≈ 0.432
BASIN_DEPTH                  = WINDING_NUMBER**2 / K_CS               # ≈ 0.338
PHI_DEBT_DECAY_RATE          = 0.15
PHI_DEBT_ALIGNMENT_FLOOR     = 0.30
PLANCK_ENERGY_J              = 1.9561e9
WILDFIRE_ENERGY_PER_HA_J     = 8.0e10
HURRICANE_ENERGY_PER_CAT_J   = 5.0e18
AVALANCHE_ENERGY_PER_LVL_J   = 5.0e11

VERSION = "v2.0"
EPISTEMIC = (
    "\n\n---\n"
    "*🔵 ADJACENT TRACK — UM physics overlays are geometric analogues applied to "
    "geophysics. Not hardgate physics claims. Sources: P806, P786, P16, P808.*\n"
    f"*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876 · {VERSION}*"
)

# ── Feed URLs ──────────────────────────────────────────────────────────────────
USGS_EQ_URL  = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.geojson"
EONET_URL    = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=200&days=30"
NOAA_NWS_URL = "https://api.weather.gov/alerts/active"
NWAC_URL     = "https://api.avalanche.org/v2/public/products?avalanche_center_id=NWAC"

HEADERS = {
    "User-Agent": "UM-GeoMonitor-HF/2.0 (open-science; axiomzero.com)",
    "Accept": "application/geo+json, application/json",
}


def _fetch_json(url: str) -> Any:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())


# ── UM Overlay Engine ──────────────────────────────────────────────────────────

def _energy_si(kind: str, magnitude: float) -> float:
    k = kind.lower()
    if k in ("earthquake", "tsunami"):
        return 10 ** (1.5 * magnitude + 4.8)
    if k == "wildfire":
        return (10 ** (magnitude - 1)) * WILDFIRE_ENERGY_PER_HA_J
    if k in ("hurricane", "storm", "tornado", "nws_alert"):
        return HURRICANE_ENERGY_PER_CAT_J * (magnitude ** 1.5)
    if k == "volcano":
        return 10 ** (3 * magnitude + 10)
    if k == "avalanche":
        return AVALANCHE_ENERGY_PER_LVL_J * (magnitude ** 2)
    return 10 ** (1.5 * magnitude + 4.8)


def _compute_overlay(kind: str, magnitude: float, depth_km: float | None = None) -> dict:
    E_si     = _energy_si(kind, magnitude)
    E_planck = E_si / PLANCK_ENERGY_J
    E_log    = math.log10(max(E_si, 1.0))

    phi_debt      = E_planck * (1.0 - math.exp(-PHI_DEBT_DECAY_RATE * E_log))
    phi_alignment = max(PHI_DEBT_ALIGNMENT_FLOOR, min(1.0, math.exp(-PHI_DEBT_DECAY_RATE * E_planck)))

    radion_amp = RADION_COUPLING_ALPHA * abs(math.log10(max(E_si, 1.0) / PLANCK_ENERGY_J))
    if kind.lower() == "earthquake" and depth_km:
        radion_amp *= math.exp(-depth_km / 700.0)

    suppression   = min(math.exp(RADION_COUPLING_ALPHA * radion_amp), RADION_QCD_SUPPRESSION)
    basin_pert    = radion_amp / BASIN_DEPTH
    winding_stab  = max(0.0, 1.0 - min(basin_pert, 1.0))
    w_a_local     = -radion_amp * (BRAIDED_SOUND_SPEED ** 2)

    confidence = "LOW"
    if E_planck >= 1e-15:
        confidence = "HIGH"
    elif E_planck >= 1e-18:
        confidence = "MEDIUM"

    return {
        "phi_debt":       phi_debt,
        "phi_alignment":  phi_alignment,
        "radion_amp":     radion_amp,
        "suppression":    suppression,
        "basin_pert":     basin_pert,
        "winding_stab":   winding_stab,
        "w_a_local":      w_a_local,
        "confidence":     confidence,
    }


# ── Feed Parsers ───────────────────────────────────────────────────────────────

def _parse_usgs(data: dict) -> list[dict]:
    rows = []
    for f in data.get("features", []):
        p, c = f.get("properties", {}), (f.get("geometry") or {}).get("coordinates", [])
        if p.get("mag") is None or len(c) < 2:
            continue
        mag = float(p["mag"])
        lon, lat = float(c[0]), float(c[1])
        depth = float(c[2]) if len(c) > 2 and c[2] is not None else None
        ov = _compute_overlay("earthquake", mag, depth)
        rows.append({
            "hazard": "⚡ Earthquake", "kind": "earthquake",
            "magnitude": mag, "lat": lat, "lon": lon, "depth_km": depth,
            "place": p.get("place", "—"),
            "time": p.get("time", ""),
            "source": "USGS EQ Hazards",
            **{f"um_{k}": v for k, v in ov.items()},
        })
    return rows


EONET_MAP = {
    "wildfires":    ("🔥 Wildfire",   "wildfire",  "NASA EONET"),
    "volcanoes":    ("🌋 Volcano",    "volcano",   "NASA EONET / USGS CVO"),
    "severeStorms": ("🌀 Storm",      "storm",     "NASA EONET"),
    "floods":       ("🌊 Flood",      "flood",     "NASA EONET"),
    "landslides":   ("⛰️ Landslide",  "landslide", "NASA EONET / USGS LHP"),
    "drought":      ("☀️ Drought",    "drought",   "NASA EONET"),
    "dustHaze":     ("🌫️ Dust/Haze", "storm",     "NASA EONET"),
    "seaLakeIce":   ("🧊 Sea Ice",    "flood",     "NASA EONET"),
}


def _parse_eonet(data: dict) -> list[dict]:
    rows = []
    for ev in data.get("events", []):
        cats = ev.get("categories", [])
        cat_id = cats[0]["id"] if cats else ""
        label, kind, source = EONET_MAP.get(cat_id, ("⚠️ Hazard", "storm", "NASA EONET"))
        geo = ev.get("geometry", [])
        if not geo:
            continue
        coords = geo[-1].get("coordinates", [])
        if len(coords) < 2 or coords[0] is None:
            continue
        lon, lat = float(coords[0]), float(coords[1])
        mag = float(ev.get("magnitudeValue") or 5.0)
        ov = _compute_overlay(kind, mag)
        rows.append({
            "hazard": label, "kind": kind,
            "magnitude": mag, "lat": lat, "lon": lon, "depth_km": None,
            "place": ev.get("title", cat_id),
            "time": geo[-1].get("date", ""),
            "source": source,
            **{f"um_{k}": v for k, v in ov.items()},
        })
    return rows


NWS_SEV_MAG   = {"Extreme": 4.0, "Severe": 3.0, "Moderate": 2.0, "Minor": 1.0, "Unknown": 1.5}
NWS_KIND_KEYS = {
    "tsunami": "tsunami", "red flag": "wildfire", "fire weather": "wildfire",
    "tornado": "tornado", "severe thunderstorm": "storm", "flash flood": "flood",
    "flood": "flood", "winter storm": "storm", "blizzard": "storm",
    "high wind": "storm", "excessive heat": "storm",
}
NWS_ICONS = {
    "tsunami": "🌊", "wildfire": "🔥", "tornado": "🌪️",
    "flood": "🌊", "storm": "🌀", "nws_alert": "⚠️",
}


def _centroid(geom: dict) -> tuple[float, float] | None:
    gtype = geom.get("type", "")
    coords = geom.get("coordinates")
    if not coords:
        return None
    try:
        if gtype == "Point":
            return float(coords[1]), float(coords[0])
        if gtype == "Polygon" and coords[0]:
            ring = coords[0]
            return (sum(c[1] for c in ring) / len(ring),
                    sum(c[0] for c in ring) / len(ring))
        if gtype == "MultiPolygon" and coords[0] and coords[0][0]:
            ring = coords[0][0]
            return (sum(c[1] for c in ring) / len(ring),
                    sum(c[0] for c in ring) / len(ring))
    except (TypeError, ZeroDivisionError):
        return None
    return None


def _parse_nws(data: dict) -> list[dict]:
    rows = []
    for f in data.get("features", []):
        p = f.get("properties") or {}
        ev_type = (p.get("event") or "").lower()
        severity = p.get("severity", "Unknown")
        kind = "nws_alert"
        for kw, k in NWS_KIND_KEYS.items():
            if kw in ev_type:
                kind = k
                break
        icon = NWS_ICONS.get(kind, "⚠️")
        mag = NWS_SEV_MAG.get(severity, 1.5)
        geom = f.get("geometry") or {}
        pt = _centroid(geom)
        if pt is None:
            continue
        lat, lon = pt
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            continue
        ov = _compute_overlay(kind, mag)
        headline = p.get("headline") or p.get("areaDesc") or ev_type
        rows.append({
            "hazard": f"{icon} {kind.replace('_',' ').title()}",
            "kind": kind,
            "magnitude": mag, "lat": lat, "lon": lon, "depth_km": None,
            "place": headline[:80],
            "time": p.get("sent") or p.get("effective") or "",
            "source": f"NOAA NWS · {p.get('senderName', 'NWS')}",
            **{f"um_{k}": v for k, v in ov.items()},
        })
    return rows


NWAC_ZONE_COORDS = {
    "olympics": (47.80, -123.70), "west-slopes-south": (47.22, -121.56),
    "west-slopes-central": (47.70, -121.40), "west-slopes-north": (48.50, -121.20),
    "east-slopes-south": (46.85, -120.65), "east-slopes-central": (47.60, -120.70),
    "east-slopes-north": (48.40, -120.50), "mt-hood": (45.37, -121.70),
    "central-oregon": (44.00, -121.60), "mt-baker": (48.78, -121.81),
    "snoqualmie-pass": (47.43, -121.41),
}
DANGER_LABEL = ["", "Low ❶", "Limited ❷", "Considerable ❸", "High ❹", "Extreme ❺"]


def _parse_nwac(data: Any) -> list[dict]:
    rows = []
    items = data if isinstance(data, list) else (data.get("data") or [])
    seen: set[str] = set()
    for product in items:
        zone = (product.get("forecast_zone") or product.get("zone_name") or "").lower().replace(" ", "-")
        if zone in seen:
            continue
        seen.add(zone)
        danger_list = product.get("danger") or []
        max_d = max(
            (int(band.get("level") or band.get("danger") or 1) for band in danger_list),
            default=1
        )
        top = int(product.get("danger_level") or product.get("overall_danger") or 0)
        max_d = max(max_d, top)
        max_d = max(1, min(5, max_d))

        coords = (47.5, -121.5)
        for key, c in NWAC_ZONE_COORDS.items():
            if key in zone or zone.split("-")[0] in key:
                coords = c
                break
        lat, lon = coords
        ov = _compute_overlay("avalanche", float(max_d))
        dlabel = DANGER_LABEL[max_d] if max_d <= 5 else f"Level {max_d}"
        rows.append({
            "hazard": "❄️ Avalanche",
            "kind": "avalanche",
            "magnitude": float(max_d), "lat": lat, "lon": lon, "depth_km": None,
            "place": f"NWAC: {product.get('forecast_zone') or zone} — {dlabel}",
            "time": product.get("published_time") or product.get("date") or "",
            "source": "NWAC / USFS",
            **{f"um_{k}": v for k, v in ov.items()},
        })
    return rows


# ── Data Loader ────────────────────────────────────────────────────────────────

def load_all_events(pnw_only: bool = False) -> tuple[list[dict], str]:
    """Fetch all feeds and return (rows, status_message)."""
    errors = []
    rows: list[dict] = []

    try:
        rows += _parse_usgs(_fetch_json(USGS_EQ_URL))
    except Exception as e:
        errors.append(f"USGS: {e}")

    try:
        rows += _parse_eonet(_fetch_json(EONET_URL))
    except Exception as e:
        errors.append(f"EONET: {e}")

    try:
        rows += _parse_nws(_fetch_json(NOAA_NWS_URL))
    except Exception as e:
        errors.append(f"NOAA NWS: {e}")

    try:
        rows += _parse_nwac(_fetch_json(NWAC_URL))
    except Exception as e:
        errors.append(f"NWAC: {e}")

    if pnw_only:
        rows = [r for r in rows
                if 42.0 <= r["lat"] <= 49.5 and -125.0 <= r["lon"] <= -110.5]

    status = f"✅ {len(rows)} events loaded"
    if errors:
        status += f" | ⚠️ Partial: {'; '.join(errors[:3])}"
    return rows, status


# ── Summary Helpers ────────────────────────────────────────────────────────────

def _fmt_sci(v: float) -> str:
    if not math.isfinite(v):
        return "—"
    return f"{v:.3e}"


def build_table(rows: list[dict], kind_filter: str) -> Any:
    """Return a DataFrame or list-of-lists for the Gradio Dataframe."""
    if kind_filter != "All":
        rows = [r for r in rows if r["hazard"].endswith(kind_filter) or r["kind"] == kind_filter.lower()]

    if not rows:
        return [] if not PANDAS_OK else __import__("pandas").DataFrame()

    cols = ["hazard", "magnitude", "lat", "lon", "place", "um_phi_debt",
            "um_radion_amp", "um_winding_stab", "um_confidence", "source", "time"]

    if PANDAS_OK:
        import pandas as pd
        df = pd.DataFrame(rows)[cols].copy()
        df["um_phi_debt"]    = df["um_phi_debt"].apply(_fmt_sci)
        df["um_radion_amp"]  = df["um_radion_amp"].apply(lambda v: f"{v:.5f}")
        df["um_winding_stab"]= df["um_winding_stab"].apply(lambda v: f"{v:.3f}")
        df["lat"]            = df["lat"].apply(lambda v: f"{v:.3f}")
        df["lon"]            = df["lon"].apply(lambda v: f"{v:.3f}")
        df.columns = ["Hazard","Mag","Lat","Lon","Location","φ-Debt","Radion|Δφ/φ₀|","Winding Stab","Confidence","Source","Time"]
        return df
    else:
        headers = ["Hazard","Mag","Lat","Lon","Location","φ-Debt","Radion|Δφ/φ₀|","Winding Stab","Confidence","Source"]
        result = [headers]
        for r in rows[:200]:
            result.append([
                r["hazard"], f"{r['magnitude']:.1f}",
                f"{r['lat']:.2f}", f"{r['lon']:.2f}",
                r["place"][:50],
                _fmt_sci(r["um_phi_debt"]),
                f"{r['um_radion_amp']:.5f}",
                f"{r['um_winding_stab']:.3f}",
                r["um_confidence"],
                r["source"],
            ])
        return result


def build_summary_md(rows: list[dict], status: str) -> str:
    if not rows:
        return f"### No events\n{status}"
    by_kind: dict[str, int] = {}
    total_phi = 0.0
    max_radion = 0.0
    min_stab = 1.0
    for r in rows:
        h = r["hazard"]
        by_kind[h] = by_kind.get(h, 0) + 1
        total_phi  += r["um_phi_debt"]
        if r["um_radion_amp"] > max_radion: max_radion = r["um_radion_amp"]
        if r["um_winding_stab"] < min_stab: min_stab = r["um_winding_stab"]

    lines = [f"## {status}", "", "### Event Counts"]
    for k, v in sorted(by_kind.items(), key=lambda x: -x[1]):
        lines.append(f"- **{k}**: {v}")
    lines += [
        "",
        "### UM Physics Overlay (Aggregate)",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Total φ-Debt (P16 analogue) | `{_fmt_sci(total_phi)}` Planck units |",
        f"| Max Radion \\|Δφ/φ₀\\| (P806) | `{max_radion:.5f}` |",
        f"| Min Winding Stability (P786) | `{min_stab:.4f}` |",
        "",
        "### Hazard Authority Networks (Pacific Northwest)",
        "| Hazard | Authoritative Network | Live Data |",
        "|---|---|---|",
        "| ⚡ Earthquakes | [PNSN](https://pnsn.org) / [USGS](https://earthquake.usgs.gov) | ShakeAlert, M2.5+ real-time |",
        "| ❄️ Avalanches | [NWAC](https://nwac.us) / USFS | Daily danger ratings, zone forecasts |",
        "| 🌋 Volcanoes | [USGS CVO](https://www.usgs.gov/observatories/cvo) | Alert levels, aviation codes, lahar warnings |",
        "| 🌊 Tsunamis | [NOAA NTWC](https://tsunami.gov) / [WA DNR](https://dnr.wa.gov/washington-geological-survey/geologic-hazards-and-environment/tsunamis) | Watches, inundation maps |",
        "| ⛰️ Landslides | [USGS LHP](https://www.usgs.gov/programs/landslide-hazards) | Slope stability, event catalog |",
        "| 🔥 Fire/Weather | [NOAA NWS](https://weather.gov) | Red Flag warnings, severe storm alerts |",
        "",
        EPISTEMIC,
    ]
    return "\n".join(lines)


def build_map_html(rows: list[dict]) -> str:
    """Build a lightweight SVG world-map dot plot (no external dependencies)."""
    if not rows:
        return "<p style='color:#888'>No events to display.</p>"

    # Simple equirectangular projection
    W, H = 800, 400
    def project(lat, lon):
        x = int((lon + 180) / 360 * W)
        y = int((90 - lat) / 180 * H)
        return x, y

    KIND_COLOR = {
        "earthquake": "#22d3ee", "wildfire": "#f97316", "storm": "#a78bfa",
        "volcano": "#ef4444", "tsunami": "#38bdf8", "avalanche": "#60a5fa",
        "nws_alert": "#fbbf24", "flood": "#818cf8", "landslide": "#78716c",
        "tornado": "#c4b5fd", "hurricane": "#a78bfa", "drought": "#fbbf24",
    }
    dots = []
    for r in rows:
        x, y = project(r["lat"], r["lon"])
        color = KIND_COLOR.get(r["kind"], "#94a3b8")
        r_px = max(3, min(12, int(r["magnitude"] * 1.5)))
        tooltip = f"{r['hazard']} M{r['magnitude']:.1f} — {r['place'][:50]}"
        dots.append(
            f'<circle cx="{x}" cy="{y}" r="{r_px}" fill="{color}" '
            f'fill-opacity="0.75" stroke="#fff" stroke-width="0.5" stroke-opacity="0.3">'
            f'<title>{tooltip}</title></circle>'
        )

    legend_items = [
        ("⚡", "#22d3ee", "Earthquake"), ("🔥", "#f97316", "Wildfire"),
        ("🌋", "#ef4444", "Volcano"),    ("🌊", "#38bdf8", "Tsunami"),
        ("❄️", "#60a5fa", "Avalanche"),  ("🌀", "#a78bfa", "Storm"),
        ("⚠️", "#fbbf24", "NWS Alert"),  ("⛰️", "#78716c", "Landslide"),
    ]
    legend_svg = ""
    for i, (icon, color, label) in enumerate(legend_items):
        lx = 10 + (i % 4) * 200
        ly = H + 20 + (i // 4) * 20
        legend_svg += f'<circle cx="{lx+6}" cy="{ly}" r="6" fill="{color}" fill-opacity="0.8"/>'
        legend_svg += f'<text x="{lx+16}" y="{ly+4}" fill="#94a3b8" font-size="11">{icon} {label}</text>'

    total_h = H + 20 + (len(legend_items) // 4 + 1) * 20 + 10
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {total_h}"
              style="background:#05080d;border-radius:8px;width:100%;max-width:{W}px">
  <!-- World outline approximation -->
  <rect x="0" y="0" width="{W}" height="{H}" fill="#05080d"/>
  <rect x="0" y="{H//2-1}" width="{W}" height="2" fill="#162030" opacity="0.5"/>
  <rect x="{W//2-1}" y="0" width="2" height="{H}" fill="#162030" opacity="0.5"/>
  {''.join(dots)}
  {legend_svg}
  <text x="5" y="{H-5}" fill="#334155" font-size="9">Equirectangular · {len(rows)} events</text>
</svg>'''
    return svg


# ── Gradio App ─────────────────────────────────────────────────────────────────

_CACHE: tuple[list[dict], str] | None = None


def run_monitor(
    pnw_focus: bool,
    kind_filter: str,
    min_mag: float,
    reload: bool,
) -> tuple[Any, str, str]:
    global _CACHE
    if reload or _CACHE is None:
        rows, status = load_all_events(pnw_only=pnw_focus)
        _CACHE = (rows, status)
    else:
        rows, status = _CACHE
        if pnw_focus:
            rows = [r for r in rows if 42.0 <= r["lat"] <= 49.5 and -125.0 <= r["lon"] <= -110.5]

    rows = [r for r in rows if r["magnitude"] >= min_mag]
    table  = build_table(rows, kind_filter)
    summary = build_summary_md(rows, status)
    map_svg = build_map_html(rows)
    return table, summary, map_svg


def analyse_single(kind: str, magnitude: float, lat: float, lon: float, depth_km: float) -> str:
    """Compute UM overlay for a single event entered manually."""
    depth = depth_km if depth_km > 0 else None
    ov = _compute_overlay(kind, magnitude, depth)
    lines = [
        f"## UM Overlay — {kind.upper()} M{magnitude:.1f}",
        f"Location: ({lat:.3f}°, {lon:.3f}°)",
        "",
        "| Metric | Value | Pillar |",
        "|---|---|---|",
        f"| φ-Debt injection | `{_fmt_sci(ov['phi_debt'])}` Planck units | P16 |",
        f"| φ-Alignment | `{ov['phi_alignment']:.4f}` | P16 |",
        f"| Radion \\|Δφ/φ₀\\| | `{ov['radion_amp']:.5f}` | P806 |",
        f"| Radion suppression | `{_fmt_sci(ov['suppression'])}` | P806 |",
        f"| Winding stability | `{ov['winding_stab']:.4f}` | P786 |",
        f"| Basin perturbation | `{ov['basin_pert']:.4f}` | P786 |",
        f"| w_a local | `{ov['w_a_local']:.5e}` | P808 |",
        f"| Confidence | **{ov['confidence']}** | — |",
        "",
        EPISTEMIC,
    ]
    return "\n".join(lines)


HAZARD_NETWORKS_MD = """
## Hazard Authority Networks — Pacific Northwest

| Hazard | Authoritative Network | What They Track |
|---|---|---|
| ⚡ Earthquakes | [PNSN](https://pnsn.org) / [USGS EQ Hazards](https://earthquake.usgs.gov) | ShakeAlert early warning, epicenters, tremor maps |
| ❄️ Avalanches | [NWAC](https://nwac.us) / US Forest Service | Daily avalanche danger ratings, mountain weather, zone forecasts |
| 🌋 Volcanoes | [USGS Cascades Volcano Observatory](https://www.usgs.gov/observatories/cvo) | Alert levels, aviation color codes, lahar warnings (Rainier, St. Helens, etc.) |
| 🌊 Tsunamis | [NOAA NTWC](https://tsunami.gov) / [WA DNR](https://dnr.wa.gov/washington-geological-survey/geologic-hazards-and-environment/tsunamis) | Tsunami watches/warnings, coastal inundation maps, evacuation routing |
| ⛰️ Landslides | [USGS Landslide Hazards Program](https://www.usgs.gov/programs/landslide-hazards) | Slope stability maps, major ground movement tracking |
| 🔥 Wildfires & Weather | [NOAA NWS](https://weather.gov) | Red Flag warnings, severe storm alerts, fire weather watches |

### Real-Time Data Provided

| Hazard | Real-Time Product | Frequency |
|---|---|---|
| Earthquakes | ShakeAlert EEW, M2.5+ GeoJSON | Continuous / 5 min |
| Avalanches | Zone danger ratings (1–5) | Daily |
| Volcanoes | Alert level + aviation color code | Event-driven |
| Tsunamis | Tsunami watches / advisories | Event-driven |
| Landslides | Event catalog | Near real-time |
| Fire/Weather | Active NWS alerts (GeoJSON) | Continuous |

*Data in this app: USGS (earthquakes), NASA EONET (wildfires/storms/volcanoes), NOAA NWS (severe weather / tsunamis), NWAC (avalanche forecasts).*
"""


if not GRADIO_OK:
    print("gradio not installed. Run: pip install gradio pandas")
    raise SystemExit(1)


KIND_CHOICES = ["All", "Earthquake", "Wildfire", "Volcano", "Storm",
                "Tsunami", "Avalanche", "NWS Alert", "Flood", "Landslide"]

with gr.Blocks(title="UM Geophysical Monitor", theme=gr.themes.Base()) as demo:
    gr.Markdown(
        "# 🌍 UM Geophysical Monitor\n"
        "**Live multi-hazard globe** — USGS · NASA EONET · NOAA NWS · NWAC Avalanche · "
        "Unitary Manifold φ-overlay (🔵 Adjacent Track)"
    )

    with gr.Tabs():

        with gr.Tab("Live Monitor"):
            with gr.Row():
                pnw_focus   = gr.Checkbox(label="📍 PNW Focus (WA/OR/ID/MT)", value=False)
                kind_filter = gr.Dropdown(KIND_CHOICES, value="All", label="Hazard Type")
                min_mag     = gr.Slider(0, 8, value=0, step=0.5, label="Min Magnitude")
                reload_btn  = gr.Checkbox(label="🔄 Reload Feeds", value=True)
            run_btn = gr.Button("▶ Load / Refresh Monitor", variant="primary")

            map_out     = gr.HTML(label="Event Map")
            summary_out = gr.Markdown(label="Summary")
            table_out   = gr.Dataframe(label="Event Table", wrap=True)

            run_btn.click(
                run_monitor,
                inputs=[pnw_focus, kind_filter, min_mag, reload_btn],
                outputs=[table_out, summary_out, map_out],
            )

        with gr.Tab("Single Event Analysis"):
            gr.Markdown("### Compute UM overlay for a single event")
            with gr.Row():
                s_kind  = gr.Dropdown(
                    ["earthquake","wildfire","storm","volcano","tsunami",
                     "avalanche","nws_alert","flood","landslide","hurricane","tornado"],
                    value="earthquake", label="Hazard Kind"
                )
                s_mag   = gr.Slider(0.1, 10, value=6.0, step=0.1, label="Magnitude")
                s_lat   = gr.Number(value=47.6, label="Latitude")
                s_lon   = gr.Number(value=-122.3, label="Longitude")
                s_depth = gr.Number(value=0.0,  label="Depth km (0 = surface)")
            s_btn = gr.Button("Analyse", variant="primary")
            s_out = gr.Markdown()
            s_btn.click(analyse_single, inputs=[s_kind, s_mag, s_lat, s_lon, s_depth], outputs=s_out)

        with gr.Tab("Hazard Networks"):
            gr.Markdown(HAZARD_NETWORKS_MD)

    gr.Markdown(
        f"*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876 · {VERSION}*\n\n"
        "*License: Defensive Public Commons v1.0 — All content public domain.*"
    )

if __name__ == "__main__":
    demo.launch()
