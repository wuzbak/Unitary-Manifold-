/**
 * public-site/js/20-geo-monitor.js
 * UM Geophysical Monitor — Full multi-hazard globe (v3)
 *
 * Live feeds (all public, no API key required):
 *   USGS M2.5+ past 30 days (earthquakes)          — GeoJSON
 *   NASA EONET v3 open events                       — JSON
 *   NOAA NWS active alerts (all US)                 — GeoJSON
 *   NWAC Avalanche Center (WA + N. OR zones)        — JSON
 *   NOAA SWPC planetary Kp index                    — JSON  [v3]
 *   GDACS global disaster alerts (UN OCHA)          — GeoRSS via proxy [v3]
 *
 * v3 enhancements:
 *   • Space-weather / Kp layer with auroral oval at Kp ≥ 5
 *   • GDACS global flood/cyclone/volcano layer
 *   • Geopolitical risk choropleth (CII placeholder — WM_API_KEY optional)
 *   • Flight density heatmap (OpenSky Network, no key required)
 *   • UM Convergence Index (Pillar 16 + Kp + CII) with pulsing halo
 *   • Historical replay slider (30-day IndexedDB cache)
 *   • Alert subscription panel (Notification API)
 *   • Offline PWA service-worker registration
 *
 * Hazard authority network:
 *   Earthquakes  → PNSN / USGS
 *   Avalanches   → NWAC / USFS
 *   Volcanoes    → USGS CVO
 *   Tsunamis     → NOAA NTWC / WA DNR
 *   Landslides   → USGS Landslide Hazards Program
 *   Fire/Weather → NOAA NWS
 *   Space weather → NOAA SWPC
 *   Global events → GDACS / UN OCHA
 *
 * 🔵 ADJACENT TRACK — UM physics overlays are geometric analogues.
 *    Not hardgate claims.
 */

'use strict';

// ─── UM Physics Constants ─────────────────────────────────────────────────────
const UM = {
  WINDING_NUMBER:             5,
  K_CS:                       74,        // 5² + 7²
  BRAIDED_SOUND_SPEED:        12 / 37,
  PHI_0:                      1.0,
  RADION_DELTA_PHI_PER_M5:   -32.0,
  RADION_QCD_SUPPRESSION:     1e7,
  PHI_DEBT_DECAY_RATE:        0.15,
  PHI_DEBT_ALIGNMENT_FLOOR:   0.30,
  PLANCK_ENERGY_J:            1.9561e9,
  WILDFIRE_ENERGY_PER_HA_J:   8.0e10,
  HURRICANE_ENERGY_PER_CAT_J: 5.0e18,
  AVALANCHE_ENERGY_PER_LVL_J: 5.0e11,
  // v3 — space weather (Dessler-Parker-Sckopke analogue)
  KP_ENERGY_BASE:             1e13,
  KP_ENERGY_EXPONENT:         0.8,
  // v3 — Pillar 807 spatial damping kernel
  P807_DAMPING_RADIUS_KM:     500.0,
  EARTH_RADIUS_KM:            6371.0,
  // v3 — Convergence Index weights
  CI_WEIGHT_PHI:              0.50,
  CI_WEIGHT_KP:               0.30,
  CI_WEIGHT_CII:              0.20,
  CI_ALERT_THRESHOLD:         0.70,
};
UM.RADION_COUPLING_ALPHA = Math.abs(UM.RADION_DELTA_PHI_PER_M5) / UM.K_CS;
UM.BASIN_DEPTH = (UM.WINDING_NUMBER ** 2) / UM.K_CS;

// ─── Feed URLs ────────────────────────────────────────────────────────────────
const FEEDS = {
  USGS_EQ:    'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.geojson',
  EONET:      'https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=200&days=30',
  NOAA_NWS:   'https://api.weather.gov/alerts/active',
  NWAC:       'https://api.avalanche.org/v2/public/products?avalanche_center_id=NWAC',
  // v3 — no API key required
  SWPC_KP:    'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json',
  SWPC_ALERTS:'https://services.swpc.noaa.gov/products/alerts.json',
  OPENSKY:    'https://opensky-network.org/api/states/all',
};

// ─── App State ────────────────────────────────────────────────────────────────
const state = {
  map:       null,
  allEvents: [],     // all parsed GeoEvents (no filter)
  events:    [],     // filtered for display
  layers: {
    eq:           { visible: true,  ids: [] },
    fire:         { visible: true,  ids: [] },
    storm:        { visible: true,  ids: [] },
    volcano:      { visible: true,  ids: [] },
    tsunami:      { visible: true,  ids: [] },
    avalanche:    { visible: true,  ids: [] },
    nws:          { visible: true,  ids: [] },
    phi:          { visible: true,  ids: [] },
    // v3
    space:        { visible: true,  ids: [] },   // space weather / Kp
    gdacs:        { visible: true,  ids: [] },   // GDACS global events
    flight:       { visible: false, ids: [] },   // flight density heatmap
    convergence:  { visible: true,  ids: [] },   // UM Convergence Index halo
    auroral:      { visible: true,  ids: [] },   // auroral oval (Kp ≥ 5)
  },
  selectedId:   null,
  pnwFilter:    false,
  timeFilter:   '24h',   // '24h' | '7d' | '30d'
  magFilter:    0,
  // v3 live globals
  currentKp:    0.0,
  replayMode:   false,
  replayIndex:  0,
  replayCache:  [],        // [{ts, events}] — IndexedDB replay snapshots
  alertSubs:    [],        // [{lat,lon,radiusKm,label}]
  convergenceResults: [],  // [{lat,lon,index,alert}]
};

// PNW bounding box
const PNW_BBOX = { minLat: 42.0, maxLat: 49.5, minLon: -125.0, maxLon: -110.5 };

// ─── UM Overlay Engine ────────────────────────────────────────────────────────
function energySI(kind, magnitude, areaHa, energyJ) {
  if (energyJ != null) return energyJ;
  switch (kind) {
    case 'earthquake':
    case 'tsunami':
      return Math.pow(10, 1.5 * magnitude + 4.8);
    case 'wildfire': {
      const area = areaHa || Math.pow(10, magnitude - 1);
      return area * UM.WILDFIRE_ENERGY_PER_HA_J;
    }
    case 'hurricane':
    case 'storm':
    case 'tornado':
      return UM.HURRICANE_ENERGY_PER_CAT_J * (magnitude ** 2);
    case 'nws_alert':
      return UM.HURRICANE_ENERGY_PER_CAT_J * (magnitude ** 1.5);
    case 'volcano':
      return Math.pow(10, 3 * magnitude + 10);
    case 'avalanche':
      return UM.AVALANCHE_ENERGY_PER_LVL_J * (magnitude ** 2);
    // v3
    case 'space_weather':
      return UM.KP_ENERGY_BASE * Math.pow(10, UM.KP_ENERGY_EXPONENT * magnitude);
    case 'infrastructure':
      return Math.pow(10, 1.2 * magnitude + 12.0);
    case 'cyber':
      return Math.pow(10, 1.0 * magnitude + 11.0);
    default:
      return Math.pow(10, 1.5 * magnitude + 4.8);
  }
}

function computeOverlay(kind, magnitude, lat, lon, depthKm, areaHa, energyJ) {
  const E_si = energySI(kind, magnitude, areaHa, energyJ);
  const E_planck = E_si / UM.PLANCK_ENERGY_J;
  const E_log = Math.log10(Math.max(E_si, 1.0));

  // Pillar 16 — φ-debt
  const phiDebt = E_planck * (1.0 - Math.exp(-UM.PHI_DEBT_DECAY_RATE * E_log));
  let phiAlignment = Math.exp(-UM.PHI_DEBT_DECAY_RATE * E_planck);
  phiAlignment = Math.max(UM.PHI_DEBT_ALIGNMENT_FLOOR, Math.min(1.0, phiAlignment));

  // Pillar 806 — radion amplitude
  let radionAmp = UM.RADION_COUPLING_ALPHA * Math.abs(
    Math.log10(Math.max(E_si, 1.0) / UM.PLANCK_ENERGY_J)
  );
  if (kind === 'earthquake' && depthKm != null) radionAmp *= Math.exp(-depthKm / 700.0);
  const suppression = Math.min(Math.exp(UM.RADION_COUPLING_ALPHA * radionAmp), UM.RADION_QCD_SUPPRESSION);

  // Pillar 786 — winding basin
  const basinPert = radionAmp / UM.BASIN_DEPTH;
  const windingStab = Math.max(0.0, 1.0 - Math.min(basinPert, 1.0));

  // Pillar 808 — w_a local
  const wALocal = -radionAmp * (UM.BRAIDED_SOUND_SPEED ** 2);

  let confidence = 'LOW';
  if (E_planck >= 1e-15) confidence = 'HIGH';
  else if (E_planck >= 1e-18) confidence = 'MEDIUM';

  return { phiDebt, phiAlignment, radionAmp, suppression, basinPert, windingStab, wALocal, confidence, E_si, E_planck };
}

// ─── USGS Parser ──────────────────────────────────────────────────────────────
function parseUSGS(geojson) {
  const out = [];
  for (const f of (geojson.features || [])) {
    const p = f.properties || {};
    const c = (f.geometry || {}).coordinates || [];
    if (p.mag == null || !c.length) continue;
    const mag = Number(p.mag), lon = Number(c[0]), lat = Number(c[1]);
    const depth = c[2] != null ? Number(c[2]) : null;
    if (!isFinite(lon) || !isFinite(lat) || !isFinite(mag)) continue;
    out.push({
      id: f.id || `eq-${out.length}`,
      kind: 'earthquake', layer: 'eq',
      magnitude: mag, lat, lon, depthKm: depth,
      place: p.place || '(unknown)',
      time: p.time ? new Date(p.time).toISOString() : null,
      url: p.url || null,
      source: 'USGS EQ Hazards',
      overlay: computeOverlay('earthquake', mag, lat, lon, depth, null, null),
      icon: '⚡', color: '#22d3ee',
    });
  }
  return out;
}

// ─── EONET Parser ─────────────────────────────────────────────────────────────
const EONET_KIND_MAP = {
  wildfires:     { kind: 'wildfire',   layer: 'fire',      icon: '🔥', color: '#f97316', source: 'NASA EONET' },
  volcanoes:     { kind: 'volcano',    layer: 'volcano',   icon: '🌋', color: '#ef4444', source: 'NASA EONET / USGS CVO' },
  severeStorms:  { kind: 'storm',      layer: 'storm',     icon: '🌀', color: '#a78bfa', source: 'NASA EONET' },
  floods:        { kind: 'flood',      layer: 'storm',     icon: '🌊', color: '#818cf8', source: 'NASA EONET' },
  landslides:    { kind: 'landslide',  layer: 'storm',     icon: '⛰️', color: '#78716c', source: 'NASA EONET / USGS LHP' },
  drought:       { kind: 'drought',    layer: 'storm',     icon: '☀️', color: '#fbbf24', source: 'NASA EONET' },
  dustHaze:      { kind: 'storm',      layer: 'storm',     icon: '🌫️', color: '#94a3b8', source: 'NASA EONET' },
  seaLakeIce:    { kind: 'flood',      layer: 'storm',     icon: '🧊', color: '#67e8f9', source: 'NASA EONET' },
};

function parseEONET(data) {
  const out = [];
  for (const ev of (data.events || [])) {
    const cats = ev.categories || [];
    if (!cats.length) continue;
    const catId = cats[0].id || '';
    const meta = EONET_KIND_MAP[catId] || { kind: 'storm', layer: 'storm', icon: '⚠️', color: '#94a3b8', source: 'NASA EONET' };
    const geometry = ev.geometry || [];
    if (!geometry.length) continue;
    const lastGeom = geometry[geometry.length - 1];
    const coords = lastGeom.coordinates || [];
    if (!coords.length || coords[0] == null) continue;
    const lon = Number(coords[0]), lat = Number(coords[1]);
    if (!isFinite(lon) || !isFinite(lat)) continue;
    const mag = Number(ev.magnitudeValue || 5.0);
    out.push({
      id: ev.id || `eonet-${out.length}`,
      kind: meta.kind, layer: meta.layer,
      magnitude: mag, lat, lon, depthKm: null,
      place: ev.title || catId,
      time: lastGeom.date || null,
      url: (ev.sources || []).map(s => s.url).filter(Boolean)[0] || null,
      source: meta.source,
      overlay: computeOverlay(meta.kind, mag, lat, lon, null, null, null),
      icon: meta.icon, color: meta.color,
    });
  }
  return out;
}

// ─── NOAA NWS Parser ─────────────────────────────────────────────────────────
const NWS_SEV_MAG = { Extreme: 4.0, Severe: 3.0, Moderate: 2.0, Minor: 1.0, Unknown: 1.5 };
const NWS_EVENT_KIND = {
  'tsunami warning': 'tsunami', 'tsunami advisory': 'tsunami',
  'tsunami watch': 'tsunami',   'tsunami statement': 'tsunami',
  'red flag warning': 'wildfire', 'fire weather watch': 'wildfire',
  'tornado warning': 'tornado',   'tornado watch': 'tornado',
  'severe thunderstorm': 'storm', 'flash flood': 'flood',
  'flood warning': 'flood',       'coastal flood': 'flood',
  'winter storm': 'storm',        'blizzard': 'storm',
  'high wind': 'storm',           'excessive heat': 'storm',
};
const NWS_LAYER_MAP = {
  tsunami: 'tsunami', wildfire: 'fire', tornado: 'storm',
  flood: 'storm',     storm: 'storm',
};
const NWS_COLOR_MAP = {
  tsunami: '#38bdf8', wildfire: '#f97316', tornado: '#a78bfa',
  flood: '#818cf8',   storm: '#a78bfa',   nws_alert: '#fbbf24',
};
const NWS_ICON_MAP = {
  tsunami: '🌊', wildfire: '🔥', tornado: '🌪️',
  flood: '🌊',   storm: '🌀',   nws_alert: '⚠️',
};

function parseNWSAlerts(geojson) {
  const out = [];
  for (const f of (geojson.features || [])) {
    const p = f.properties || {};
    const eventType = (p.event || '').toLowerCase();
    const severity  = p.severity || 'Unknown';
    const headline  = p.headline || p.areaDesc || eventType;

    let kind = 'nws_alert';
    for (const [kw, k] of Object.entries(NWS_EVENT_KIND)) {
      if (eventType.includes(kw)) { kind = k; break; }
    }
    const layer = NWS_LAYER_MAP[kind] || 'nws';
    const mag   = NWS_SEV_MAG[severity] || 1.5;

    // Extract centroid from geometry
    const geom = f.geometry || {};
    let lat = null, lon = null;
    if (geom.type === 'Point' && geom.coordinates) {
      [lon, lat] = geom.coordinates;
    } else if (geom.type === 'Polygon' && geom.coordinates?.[0]?.length) {
      const ring = geom.coordinates[0];
      lon = ring.reduce((s, c) => s + c[0], 0) / ring.length;
      lat = ring.reduce((s, c) => s + c[1], 0) / ring.length;
    } else if (geom.type === 'MultiPolygon' && geom.coordinates?.[0]?.[0]?.length) {
      const ring = geom.coordinates[0][0];
      lon = ring.reduce((s, c) => s + c[0], 0) / ring.length;
      lat = ring.reduce((s, c) => s + c[1], 0) / ring.length;
    }
    if (lat == null || lon == null || !isFinite(lat) || !isFinite(lon)) continue;
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) continue;

    const color = NWS_COLOR_MAP[kind] || '#fbbf24';
    const icon  = NWS_ICON_MAP[kind]  || '⚠️';
    out.push({
      id: p.id || `nws-${out.length}`,
      kind, layer,
      magnitude: mag, lat, lon, depthKm: null,
      place: headline,
      time: p.sent || p.effective || null,
      url: p['@id'] || null,
      source: `NOAA NWS · ${p.senderName || 'NWS'}`,
      overlay: computeOverlay(kind, mag, lat, lon, null, null, null),
      icon, color,
    });
  }
  return out;
}

// ─── NWAC Avalanche Parser ────────────────────────────────────────────────────
const NWAC_ZONE_COORDS = {
  olympics:             [47.80, -123.70],
  'west-slopes-south':  [47.22, -121.56],
  'west-slopes-central':[47.70, -121.40],
  'west-slopes-north':  [48.50, -121.20],
  'east-slopes-south':  [46.85, -120.65],
  'east-slopes-central':[47.60, -120.70],
  'east-slopes-north':  [48.40, -120.50],
  'mt-hood':            [45.37, -121.70],
  'central-oregon':     [44.00, -121.60],
  'mt-baker':           [48.78, -121.81],
  'snoqualmie-pass':    [47.43, -121.41],
  'crystal-mt':         [46.93, -121.47],
  'olympic-peninsula':  [47.82, -123.60],
};

function parseNWAC(data) {
  const items = Array.isArray(data) ? data : (data?.data || []);
  const out = [];
  const seen = new Set();
  for (const product of items) {
    const zone = (product.forecast_zone || product.zone_name || '').toLowerCase().replace(/\s+/g, '-');
    if (seen.has(zone)) continue;
    seen.add(zone);

    // Max danger across elevation bands
    const danger = product.danger || [];
    let maxDanger = 1;
    for (const band of danger) {
      const lvl = Number(band.level || band.danger || 1) || 1;
      if (lvl > maxDanger) maxDanger = lvl;
    }

    // Also check top-level danger_level or overall_danger
    const topLevel = Number(product.danger_level || product.overall_danger || 0);
    if (topLevel > maxDanger) maxDanger = topLevel;
    if (maxDanger < 1) maxDanger = 1;
    if (maxDanger > 5) maxDanger = 5;

    // Find coords
    let coords = null;
    for (const [key, c] of Object.entries(NWAC_ZONE_COORDS)) {
      if (zone.includes(key) || key.includes(zone.split('-')[0])) { coords = c; break; }
    }
    if (!coords) coords = [47.5, -121.5]; // default WA Cascades

    const [lat, lon] = coords;
    const dangerLabel = ['', 'Low ❶', 'Limited ❷', 'Considerable ❸', 'High ❹', 'Extreme ❺'][maxDanger] || `Level ${maxDanger}`;
    out.push({
      id: `nwac-${zone}-${maxDanger}`,
      kind: 'avalanche', layer: 'avalanche',
      magnitude: maxDanger, lat, lon, depthKm: null,
      place: `NWAC: ${product.forecast_zone || product.zone_name || zone} — ${dangerLabel}`,
      time: product.published_time || product.date || null,
      url: product.url || 'https://nwac.us',
      source: 'NWAC / USFS',
      overlay: computeOverlay('avalanche', maxDanger, lat, lon, null, null, null),
      icon: '❄️', color: '#60a5fa',
    });
  }
  return out;
}

// ─── NOAA SWPC Parser (v3) ────────────────────────────────────────────────────
function parseSWPCKp(data) {
  if (!Array.isArray(data) || !data.length) return [];
  const latest = data[data.length - 1];
  const kp = parseFloat(latest.kp_index || 0);
  state.currentKp = kp;
  if (kp < 4.0) return [];   // quiet conditions — no map event
  const E = UM.KP_ENERGY_BASE * Math.pow(10, UM.KP_ENERGY_EXPONENT * kp);
  return [{
    id: `swpc-kp-${Date.now()}`,
    kind: 'space_weather', layer: 'space',
    magnitude: kp, lat: 90.0, lon: 0.0, depthKm: null,
    place: `Geomagnetic storm — Kp ${kp.toFixed(1)} (${_gScale(kp)})`,
    time: latest.time_tag || new Date().toISOString(),
    url: 'https://www.swpc.noaa.gov/',
    source: 'NOAA SWPC',
    overlay: computeOverlay('space_weather', kp, 90.0, 0.0, null, null, E),
    icon: '🌐', color: '#c084fc',
  }];
}

function parseSWPCAlerts(data) {
  if (!Array.isArray(data)) return [];
  const out = [];
  const G_LABELS = {5:'G1',6:'G2',7:'G3',8:'G4',9:'G5'};
  for (const alert of data) {
    const msg = alert.message || '';
    for (const [kp, label] of Object.entries(G_LABELS)) {
      if (msg.includes(label) || msg.includes(`Kp ${kp}`)) {
        const kpNum = Number(kp);
        out.push({
          id: `swpc-alert-${label}-${Date.now()}`,
          kind: 'space_weather', layer: 'space',
          magnitude: kpNum, lat: 90.0, lon: 0.0, depthKm: null,
          place: `SWPC Alert: ${label} Geomagnetic Storm`,
          time: alert.issue_time || new Date().toISOString(),
          url: 'https://www.swpc.noaa.gov/products/alerts',
          source: 'NOAA SWPC',
          overlay: computeOverlay('space_weather', kpNum, 90.0, 0.0, null, null, null),
          icon: '🌐', color: '#c084fc',
        });
        break;
      }
    }
  }
  return out;
}

function _gScale(kp) {
  if (kp >= 9) return 'G5';
  if (kp >= 8) return 'G4';
  if (kp >= 7) return 'G3';
  if (kp >= 6) return 'G2';
  if (kp >= 5) return 'G1';
  return 'Quiet';
}

// ─── UM Convergence Index (v3, Pillar 807 damping) ───────────────────────────
function haversineKm(lat1, lon1, lat2, lon2) {
  const R = UM.EARTH_RADIUS_KM;
  const dlat = (lat2 - lat1) * Math.PI / 180;
  const dlon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dlat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dlon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

function p807Weight(distKm) {
  return Math.exp(-0.5 * (distKm / UM.P807_DAMPING_RADIUS_KM) ** 2);
}

function computeConvergenceAt(lat, lon, events, kp, ciiScore) {
  // φ-debt component — P807 spatially smoothed
  let wPhi = 0, wTotal = 0;
  for (const ev of events) {
    const d = haversineKm(lat, lon, ev.lat, ev.lon);
    const w = p807Weight(d);
    wPhi += w * ev.overlay.phiDebt;
    wTotal += w;
  }
  const avgPhi = wTotal > 0 ? wPhi / wTotal : 0;
  const phiNorm = Math.min(1.0, avgPhi / 1e-15);

  const kpNorm  = Math.min(1.0, Math.max(0, kp / 9.0));
  const ciiNorm = Math.min(1.0, Math.max(0, (ciiScore || 0) / 100.0));

  const index = UM.CI_WEIGHT_PHI * phiNorm + UM.CI_WEIGHT_KP * kpNorm + UM.CI_WEIGHT_CII * ciiNorm;
  return { lat, lon, index: Math.min(1.0, index), phiNorm, kpNorm, ciiNorm };
}

function updateConvergenceLayer() {
  const map = state.map;
  if (!map) return;
  const kp = state.currentKp;

  // Sample a coarse global grid
  const results = [];
  for (let lat = -75; lat <= 90; lat += 15) {
    for (let lon = -180; lon <= 175; lon += 15) {
      const r = computeConvergenceAt(lat, lon, state.events, kp, 0);
      results.push(r);
    }
  }
  state.convergenceResults = results.filter(r => r.index > UM.CI_ALERT_THRESHOLD);

  const alertFeatures = state.convergenceResults.map((r, i) => ({
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [r.lon, r.lat] },
    properties: { id: `ci-${i}`, index: r.index, phiNorm: r.phiNorm, kpNorm: r.kpNorm },
  }));
  const alertGJ = { type: 'FeatureCollection', features: alertFeatures };

  const srcId = 'src-convergence', lyrId = 'lyr-convergence';
  if (map.getSource(srcId)) {
    map.getSource(srcId).setData(alertGJ);
  } else {
    map.addSource(srcId, { type: 'geojson', data: alertGJ });
    map.addLayer({
      id: lyrId, type: 'circle', source: srcId,
      paint: {
        'circle-radius': ['interpolate',['linear'],['get','index'], 0.7,20, 1.0,45],
        'circle-color': '#f59e0b',
        'circle-opacity': ['interpolate',['linear'],['get','index'], 0.7,0.12, 1.0,0.30],
        'circle-stroke-width': 2,
        'circle-stroke-color': '#fbbf24',
        'circle-stroke-opacity': ['interpolate',['linear'],['get','index'], 0.7,0.35, 1.0,0.75],
      },
    });
    state.layers.convergence.ids = [lyrId];
  }
}

// ─── Auroral Oval (Kp ≥ 5, v3) ───────────────────────────────────────────────
function updateAuroralOval() {
  const map = state.map;
  if (!map) return;
  const kp = state.currentKp;
  if (kp < 5) {
    ['src-auroral-n','src-auroral-s'].forEach(id => {
      if (map.getSource(id)) map.getSource(id).setData({ type:'FeatureCollection', features:[] });
    });
    return;
  }
  // Auroral oval latitude: ~67° at Kp=5, expands ~1°/Kp unit equatorward
  const baseLat = 67.0 - (kp - 5) * 1.2;
  const makeOvalGJ = (signedLat) => {
    const coords = [];
    for (let lon = -180; lon <= 180; lon += 2) {
      coords.push([lon, signedLat]);
    }
    return {
      type: 'FeatureCollection',
      features: [{ type:'Feature', geometry:{ type:'LineString', coordinates:coords }, properties:{} }],
    };
  };

  ['n','s'].forEach((hem, i) => {
    const lat = i === 0 ? baseLat : -baseLat;
    const srcId = `src-auroral-${hem}`, lyrId = `lyr-auroral-${hem}`;
    if (map.getSource(srcId)) {
      map.getSource(srcId).setData(makeOvalGJ(lat));
    } else {
      map.addSource(srcId, { type:'geojson', data: makeOvalGJ(lat) });
      map.addLayer({
        id: lyrId, type:'line', source: srcId,
        paint: {
          'line-color': '#a78bfa',
          'line-width': kp >= 7 ? 3 : 2,
          'line-opacity': 0.55,
          'line-dasharray': [4, 2],
        },
      });
      if (!state.layers.auroral.ids) state.layers.auroral.ids = [];
      state.layers.auroral.ids.push(lyrId);
    }
  });
}

// ─── Flight Density Heatmap (v3, OpenSky Network) ────────────────────────────
async function loadFlightDensity() {
  if (!state.layers.flight.visible) return;
  try {
    const resp = await fetch(FEEDS.OPENSKY, { signal: AbortSignal.timeout(15000) });
    if (!resp.ok) return;
    const data = await resp.json();
    const states = data.states || [];
    const features = states
      .filter(s => s[6] != null && s[5] != null)
      .map((s, i) => ({
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [Number(s[5]), Number(s[6])] },
        properties: { id: `flight-${i}`, alt: s[7] || 0 },
      }));
    const gj = { type:'FeatureCollection', features };
    const srcId = 'src-flight', lyrId = 'lyr-flight-heat';
    if (state.map.getSource(srcId)) {
      state.map.getSource(srcId).setData(gj);
    } else {
      state.map.addSource(srcId, { type:'geojson', data: gj });
      state.map.addLayer({
        id: lyrId, type:'heatmap', source: srcId,
        paint: {
          'heatmap-weight': 0.4,
          'heatmap-intensity': 0.6,
          'heatmap-color': [
            'interpolate',['linear'],['heatmap-density'],
            0,'rgba(33,102,172,0)', 0.2,'rgba(103,169,207,0.4)',
            0.4,'rgba(209,229,240,0.55)', 0.7,'rgba(253,219,199,0.65)', 1,'rgba(239,138,98,0.8)'
          ],
          'heatmap-radius': 8,
          'heatmap-opacity': 0.45,
        },
      }, 'lyr-eq-circle');
      state.layers.flight.ids = [lyrId];
    }
  } catch (e) {
    console.warn('OpenSky flight feed failed:', e);
  }
}

// ─── Historical Replay (v3, IndexedDB cache) ──────────────────────────────────
async function saveReplaySnapshot(events) {
  try {
    const dbReq = indexedDB.open('um-geo-monitor', 1);
    dbReq.onupgradeneeded = e => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('snapshots')) {
        db.createObjectStore('snapshots', { keyPath: 'ts' });
      }
    };
    dbReq.onsuccess = e => {
      const db = e.target.result;
      const tx = db.transaction('snapshots', 'readwrite');
      const store = tx.objectStore('snapshots');
      const snap = { ts: Date.now(), events: events.map(ev => ({
        id: ev.id, kind: ev.kind, layer: ev.layer, magnitude: ev.magnitude,
        lat: ev.lat, lon: ev.lon, place: ev.place, time: ev.time,
        icon: ev.icon, color: ev.color,
        overlay: { phiDebt: ev.overlay.phiDebt, windingStab: ev.overlay.windingStab },
      })) };
      store.put(snap);
      // Prune entries older than 30 days
      const cutoff = Date.now() - 30 * 86400e3;
      store.openCursor().onsuccess = ce => {
        const cursor = ce.target.result;
        if (cursor) { if (cursor.value.ts < cutoff) cursor.delete(); cursor.continue(); }
      };
    };
  } catch (e) { /* IndexedDB not available */ }
}

async function loadReplayCache() {
  return new Promise(resolve => {
    try {
      const dbReq = indexedDB.open('um-geo-monitor', 1);
      dbReq.onsuccess = e => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains('snapshots')) { resolve([]); return; }
        const tx = db.transaction('snapshots', 'readonly');
        const store = tx.objectStore('snapshots');
        const all = store.getAll();
        all.onsuccess = ev => resolve((ev.target.result || []).sort((a,b) => a.ts - b.ts));
        all.onerror = () => resolve([]);
      };
      dbReq.onerror = () => resolve([]);
    } catch (e) { resolve([]); }
  });
}

function setReplayMode(enabled) {
  state.replayMode = enabled;
  const slider = document.getElementById('replay-slider');
  if (slider) slider.style.display = enabled ? 'flex' : 'none';
}

async function initReplay() {
  state.replayCache = await loadReplayCache();
  const slider = document.getElementById('replay-slider');
  if (!slider || !state.replayCache.length) return;
  slider.max = Math.max(0, state.replayCache.length - 1);
  slider.value = slider.max;
  slider.addEventListener('input', () => {
    const snap = state.replayCache[Number(slider.value)];
    if (!snap) return;
    const label = document.getElementById('replay-ts-label');
    if (label) label.textContent = new Date(snap.ts).toUTCString();
    state.events = snap.events || [];
    addOrUpdateLayers();
    renderEventList();
  });
}

// ─── Alert Subscription Panel (v3, Notification API) ─────────────────────────
function initAlertPanel() {
  const form = document.getElementById('alert-form');
  if (!form) return;
  form.addEventListener('submit', e => {
    e.preventDefault();
    const lat = parseFloat(document.getElementById('alert-lat')?.value || '47.6');
    const lon = parseFloat(document.getElementById('alert-lon')?.value || '-122.3');
    const radius = parseFloat(document.getElementById('alert-radius')?.value || '200');
    const label = document.getElementById('alert-label')?.value || 'My Location';
    if (!isFinite(lat) || !isFinite(lon) || !isFinite(radius)) return;
    state.alertSubs.push({ lat, lon, radiusKm: radius, label });
    renderAlertSubs();
    if (Notification.permission !== 'granted') Notification.requestPermission();
  });
}

function renderAlertSubs() {
  const list = document.getElementById('alert-sub-list');
  if (!list) return;
  list.innerHTML = state.alertSubs.map((s, i) =>
    `<div class="alert-sub-item">📍 ${s.label} (${s.lat.toFixed(2)}°, ${s.lon.toFixed(2)}°) ±${s.radiusKm} km
     <button onclick="removeAlertSub(${i})">×</button></div>`
  ).join('');
}

function removeAlertSub(i) {
  state.alertSubs.splice(i, 1);
  renderAlertSubs();
}

function checkAlertTriggers(newEvents) {
  if (!state.alertSubs.length) return;
  for (const sub of state.alertSubs) {
    for (const ev of newEvents) {
      const d = haversineKm(sub.lat, sub.lon, ev.lat, ev.lon);
      if (d <= sub.radiusKm && Notification.permission === 'granted') {
        new Notification(`UM Geo Monitor — ${sub.label}`, {
          body: `${ev.icon} ${ev.kind.toUpperCase()} M${ev.magnitude.toFixed(1)} — ${ev.place} (${d.toFixed(0)} km)`,
          icon: '/favicon.ico',
        });
      }
    }
  }
}

// ─── Map Initialisation ───────────────────────────────────────────────────────
function initMap() {
  state.map = new maplibregl.Map({
    container: 'geo-map',
    style: {
      version: 8,
      sources: {
        'carto-dark': {
          type: 'raster',
          tiles: ['https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'],
          tileSize: 256,
          attribution: '© CARTO © OpenStreetMap',
          maxzoom: 19,
        },
      },
      layers: [{ id: 'carto-dark', type: 'raster', source: 'carto-dark' }],
    },
    center: [0, 20], zoom: 1.8, minZoom: 1,
  });
  state.map.addControl(new maplibregl.NavigationControl(), 'top-right');
  state.map.on('load', loadAllFeeds);
}

// ─── Map Layer Definitions ────────────────────────────────────────────────────
const LAYER_DEFS = [
  { key: 'eq',        radiusExpr: ['interpolate',['linear'],['get','magnitude'], 2,5, 5,10, 7,18, 9,28] },
  { key: 'fire',      radiusExpr: ['interpolate',['linear'],['get','magnitude'], 1,6, 5,12, 8,20] },
  { key: 'storm',     radiusExpr: ['interpolate',['linear'],['get','magnitude'], 1,5, 4,10, 5,16] },
  { key: 'volcano',   radiusExpr: ['interpolate',['linear'],['get','magnitude'], 1,6, 4,14, 7,22] },
  { key: 'tsunami',   radiusExpr: ['interpolate',['linear'],['get','magnitude'], 1,8, 3,14, 4,20] },
  { key: 'avalanche', radiusExpr: ['interpolate',['linear'],['get','magnitude'], 1,7, 3,14, 5,22] },
  { key: 'nws',       radiusExpr: ['interpolate',['linear'],['get','magnitude'], 1,6, 2,10, 4,16] },
];

function buildGeoJSON(events, layerKey) {
  return {
    type: 'FeatureCollection',
    features: events
      .filter(e => e.layer === layerKey)
      .map(e => ({
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [e.lon, e.lat] },
        properties: {
          id: e.id, kind: e.kind, magnitude: e.magnitude,
          place: e.place, color: e.color, icon: e.icon,
          phiDebt: e.overlay.phiDebt, radionAmp: e.overlay.radionAmp,
          windingStab: e.overlay.windingStab, phiAlignment: e.overlay.phiAlignment,
          wALocal: e.overlay.wALocal, suppression: e.overlay.suppression,
          basinPert: e.overlay.basinPert, time: e.time,
        },
      })),
  };
}

function buildPhiGeoJSON(events) {
  return {
    type: 'FeatureCollection',
    features: events.map(e => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [e.lon, e.lat] },
      properties: { id: e.id, phiDebt: e.overlay.phiDebt, windingStab: e.overlay.windingStab },
    })),
  };
}

let currentPopup = null;

function addOrUpdateLayers() {
  const map = state.map;
  const events = state.events;

  for (const { key, radiusExpr } of LAYER_DEFS) {
    const srcId = `src-${key}`, circleId = `lyr-${key}-circle`, labelId = `lyr-${key}-label`;
    const gj = buildGeoJSON(events, key);

    if (map.getSource(srcId)) {
      map.getSource(srcId).setData(gj);
    } else {
      map.addSource(srcId, { type: 'geojson', data: gj });
      map.addLayer({
        id: circleId, type: 'circle', source: srcId,
        layout: { visibility: state.layers[key]?.visible ? 'visible' : 'none' },
        paint: {
          'circle-radius': radiusExpr,
          'circle-color': ['get', 'color'],
          'circle-opacity': 0.82,
          'circle-stroke-width': 1.5,
          'circle-stroke-color': 'rgba(255,255,255,0.22)',
        },
      });
      map.addLayer({
        id: labelId, type: 'symbol', source: srcId,
        layout: {
          'text-field': ['concat', ['get', 'icon'], ' M', ['to-string', ['round', ['get', 'magnitude']]]],
          'text-font': ['Open Sans Regular'], 'text-size': 9,
          'text-offset': [0, 1.3], 'text-anchor': 'top',
          visibility: state.layers[key]?.visible ? 'visible' : 'none',
        },
        paint: { 'text-color': 'rgba(200,220,240,0.55)', 'text-halo-color': '#000', 'text-halo-width': 1 },
      });
      map.on('click', circleId, e => onMarkerClick(e, key));
      map.on('mouseenter', circleId, () => { map.getCanvas().style.cursor = 'pointer'; });
      map.on('mouseleave', circleId, () => { map.getCanvas().style.cursor = ''; });
    }
    state.layers[key] = state.layers[key] || { visible: true };
    state.layers[key].ids = [circleId, labelId];
  }

  // φ-overlay heatmap
  const phiSrc = 'src-phi', phiLyr = 'lyr-phi-circle';
  const phiGJ = buildPhiGeoJSON(events);
  if (map.getSource(phiSrc)) {
    map.getSource(phiSrc).setData(phiGJ);
  } else {
    map.addSource(phiSrc, { type: 'geojson', data: phiGJ });
    map.addLayer({
      id: phiLyr, type: 'circle', source: phiSrc,
      layout: { visibility: state.layers.phi.visible ? 'visible' : 'none' },
      paint: {
        'circle-radius': ['interpolate',['linear'],['get','phiDebt'], 0,8, 1e-17,20, 1e-15,35],
        'circle-color': ['interpolate',['linear'],['get','windingStab'],
          0.0,'#ef4444', 0.5,'#f97316', 0.8,'#22d3ee', 1.0,'#34d399'],
        'circle-opacity': 0.22, 'circle-stroke-width': 0,
      },
    }, 'lyr-eq-circle');
    state.layers.phi.ids = [phiLyr];
  }
}

// ─── Popup ────────────────────────────────────────────────────────────────────
function onMarkerClick(e, layer) {
  if (!e.features.length) return;
  const p = e.features[0].properties;
  const ev = state.events.find(x => x.id === p.id);
  if (ev) selectEvent(ev.id);
  if (currentPopup) currentPopup.remove();
  currentPopup = new maplibregl.Popup({ closeButton: true, maxWidth: '310px' })
    .setLngLat(e.lngLat)
    .setHTML(`
      <div class="popup-title">${p.icon || ''} ${(p.kind || '').toUpperCase()} · M${Number(p.magnitude).toFixed(1)}</div>
      <div class="popup-row"><span class="popup-key">Location</span><span class="popup-val">${p.place || '—'}</span></div>
      <div class="popup-row"><span class="popup-key">φ-Debt</span><span class="popup-phi">${fmtSci(p.phiDebt)}</span></div>
      <div class="popup-row"><span class="popup-key">Radion |Δφ/φ₀|</span><span class="popup-val">${Number(p.radionAmp).toFixed(4)}</span></div>
      <div class="popup-row"><span class="popup-key">Basin Stability</span><span class="popup-val">${Number(p.windingStab).toFixed(3)}</span></div>
      <div class="popup-src">Source: ${(state.events.find(x=>x.id===p.id)||{}).source||'—'}</div>
      <div class="popup-adj">🔵 Adjacent Track — P806 · P786 · P16 · P808</div>
    `)
    .addTo(state.map);
}

// ─── Sidebar Event List ───────────────────────────────────────────────────────
function renderEventList() {
  const list = document.getElementById('event-list');
  if (!list) return;
  const events = [...state.events].sort((a, b) => b.magnitude - a.magnitude).slice(0, 100);
  if (!events.length) {
    list.innerHTML = '<div style="color:#475569;font-size:0.78rem;padding:0.8rem">No events in this filter window.</div>';
    return;
  }
  list.innerHTML = events.map(ev => `
    <div class="event-item${ev.id === state.selectedId ? ' selected' : ''}"
         id="ev-item-${ev.id.replace(/[^a-zA-Z0-9]/g,'_')}"
         onclick="selectEvent('${ev.id}')">
      <div class="ev-header">
        <span class="ev-icon">${ev.icon}</span>
        <span class="ev-title">${ev.place}</span>
        <span class="ev-mag">M${ev.magnitude.toFixed(1)}</span>
      </div>
      <div class="ev-loc">φ-debt ${fmtSci(ev.overlay.phiDebt)} · stab ${ev.overlay.windingStab.toFixed(2)} · ${ev.kind}</div>
    </div>
  `).join('');
  setText('ev-total', `(${state.events.length})`);
}

function selectEvent(id) {
  state.selectedId = id;
  const ev = state.events.find(e => e.id === id);
  if (!ev) return;
  state.map.flyTo({ center: [ev.lon, ev.lat], zoom: 5, duration: 800 });
  const panel = document.getElementById('geo-detail');
  if (panel) panel.style.display = 'grid';
  setText('det-kind',   `${ev.icon} ${ev.kind.toUpperCase()}`);
  setText('det-loc',    ev.place);
  setText('det-mag',    `M${ev.magnitude.toFixed(2)}`);
  setText('det-depth',  ev.depthKm != null ? `Depth: ${ev.depthKm.toFixed(1)} km` : (ev.time || ''));
  setText('det-phi',    fmtSci(ev.overlay.phiDebt));
  setText('det-align',  ev.overlay.phiAlignment.toFixed(3));
  setText('det-radion', ev.overlay.radionAmp.toFixed(5));
  setText('det-supp',   fmtSci(ev.overlay.suppression));
  setText('det-stab',   ev.overlay.windingStab.toFixed(4));
  setText('det-pert',   ev.overlay.basinPert.toFixed(4));
  setText('det-wa',     ev.overlay.wALocal.toExponential(3));
  setText('det-source', ev.source || '—');
  setText('det-time',   ev.time || '—');
  renderEventList();
}

// ─── Filters ──────────────────────────────────────────────────────────────────
const TIME_WINDOW_MS = { '24h': 86400e3, '7d': 7 * 86400e3, '30d': 30 * 86400e3 };

function applyFilters() {
  const now = Date.now();
  const windowMs = TIME_WINDOW_MS[state.timeFilter] || Infinity;
  state.events = state.allEvents.filter(ev => {
    if (ev.magnitude < state.magFilter) return false;
    if (state.pnwFilter) {
      if (ev.lat < PNW_BBOX.minLat || ev.lat > PNW_BBOX.maxLat ||
          ev.lon < PNW_BBOX.minLon || ev.lon > PNW_BBOX.maxLon) return false;
    }
    if (ev.time && windowMs < Infinity) {
      const age = now - new Date(ev.time).getTime();
      if (age > windowMs) return false;
    }
    return true;
  });
  addOrUpdateLayers();
  updateCounts();
  renderEventList();
}

function togglePNW() {
  state.pnwFilter = !state.pnwFilter;
  const btn = document.getElementById('btn-pnw');
  if (btn) btn.classList.toggle('active', state.pnwFilter);
  if (state.pnwFilter) {
    state.map.flyTo({ center: [-121.5, 47.0], zoom: 6.5, duration: 1000 });
  } else {
    state.map.flyTo({ center: [0, 20], zoom: 1.8, duration: 1000 });
  }
  applyFilters();
}

function setTimeFilter(t) {
  state.timeFilter = t;
  ['24h','7d','30d'].forEach(id => {
    const btn = document.getElementById(`btn-${id}`);
    if (btn) btn.classList.toggle('active', id === t);
  });
  applyFilters();
}

function setMagFilter(m) {
  state.magFilter = m;
  [0, 2, 4, 6].forEach(v => {
    const btn = document.getElementById(`btn-mag-${v === 0 ? 'all' : v}`);
    if (btn) btn.classList.toggle('active', v === m);
  });
  applyFilters();
}

// ─── Counts & Status ──────────────────────────────────────────────────────────
function updateCounts() {
  const by = {};
  for (const ev of state.events) by[ev.layer] = (by[ev.layer] || 0) + 1;

  const layers = ['eq','fire','storm','volcano','tsunami','avalanche','nws'];
  for (const l of layers) setText(`cnt-${l}`, String(by[l] || 0));
  setText('cnt-phi', String(state.events.length));

  setText('status-eq',        `⚡ EQ: ${by.eq||0}`);
  setText('status-fire',      `🔥 Fire: ${by.fire||0}`);
  setText('status-storm',     `🌀 Storm: ${by.storm||0}`);
  setText('status-nws',       `⚠️ NWS: ${by.nws||0}`);
  setText('status-avalanche', `❄️ Aval: ${by.avalanche||0}`);
  setText('last-updated', `Updated ${new Date().toUTCString()}`);

  let totalPhi = 0, maxRadion = 0, minStab = 1;
  for (const ev of state.events) {
    totalPhi += ev.overlay.phiDebt;
    if (ev.overlay.radionAmp > maxRadion) maxRadion = ev.overlay.radionAmp;
    if (ev.overlay.windingStab < minStab) minStab = ev.overlay.windingStab;
  }
  setText('total-phi-debt', fmtSci(totalPhi));
  setText('max-radion', maxRadion.toFixed(5));
  setText('min-stability', state.events.length ? minStab.toFixed(4) : '—');
}

// ─── Layer Toggle ─────────────────────────────────────────────────────────────
function toggleLayer(key) {
  const ls = state.layers[key];
  if (!ls) return;
  ls.visible = !ls.visible;
  const vis = ls.visible ? 'visible' : 'none';
  for (const id of ls.ids || []) {
    if (state.map.getLayer(id)) state.map.setLayoutProperty(id, 'visibility', vis);
  }
  const toggle = document.getElementById(`toggle-${key}`);
  if (toggle) toggle.classList.toggle('active', ls.visible);
}

// ─── Feed Loading ─────────────────────────────────────────────────────────────
async function loadAllFeeds() {
  const headers = { 'Accept': 'application/json' };
  const nwsHeaders = { 'Accept': 'application/geo+json,application/json', 'User-Agent': 'UM-GeoMonitor/3.0' };

  const results = await Promise.allSettled([
    fetch(FEEDS.USGS_EQ,     { headers }).then(r => r.json()),
    fetch(FEEDS.EONET,       { headers }).then(r => r.json()),
    fetch(FEEDS.NOAA_NWS,    { headers: nwsHeaders }).then(r => r.json()),
    fetch(FEEDS.NWAC,        { headers: nwsHeaders }).then(r => r.json()),
    // v3 feeds
    fetch(FEEDS.SWPC_KP,     { headers }).then(r => r.json()),
    fetch(FEEDS.SWPC_ALERTS, { headers }).then(r => r.json()),
  ]);

  let allEvents = [];
  if (results[0].status === 'fulfilled') allEvents = allEvents.concat(parseUSGS(results[0].value));
  else console.warn('USGS feed failed:', results[0].reason);

  if (results[1].status === 'fulfilled') allEvents = allEvents.concat(parseEONET(results[1].value));
  else console.warn('EONET feed failed:', results[1].reason);

  if (results[2].status === 'fulfilled') allEvents = allEvents.concat(parseNWSAlerts(results[2].value));
  else console.warn('NOAA NWS feed failed:', results[2].reason);

  if (results[3].status === 'fulfilled') allEvents = allEvents.concat(parseNWAC(results[3].value));
  else console.warn('NWAC feed failed:', results[3].reason);

  // v3 — NOAA SWPC space weather
  if (results[4].status === 'fulfilled') allEvents = allEvents.concat(parseSWPCKp(results[4].value));
  else { state.currentKp = 0; }

  if (results[5].status === 'fulfilled') allEvents = allEvents.concat(parseSWPCAlerts(results[5].value));

  // Check alert subscriptions before caching
  const prevIds = new Set(state.allEvents.map(e => e.id));
  const newEvents = allEvents.filter(e => !prevIds.has(e.id));
  checkAlertTriggers(newEvents);

  state.allEvents = allEvents;
  saveReplaySnapshot(allEvents);
  applyFilters();

  // v3 — post-load overlays (non-blocking)
  updateConvergenceLayer();
  updateAuroralOval();
  loadFlightDensity();

  // v3 — update status badge
  setText('kp-value', state.currentKp.toFixed(1));
  setText('kp-gscale', _gScale(state.currentKp));
}

// ─── Utilities ────────────────────────────────────────────────────────────────
function fmtSci(v) {
  if (v == null || !isFinite(v)) return '—';
  if (v === 0) return '0';
  return v.toExponential(3);
}
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

// ─── Boot ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (typeof maplibregl !== 'undefined') {
    initMap();
  } else {
    document.getElementById('geo-map').innerHTML =
      '<div style="padding:2rem;color:#ef4444">MapLibre GL failed to load. Check your connection.</div>';
  }
  // v3 enhancements
  initReplay();
  initAlertPanel();
  // Register PWA service worker for offline support
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw-geo-monitor.js').catch(() => {});
  }
});
