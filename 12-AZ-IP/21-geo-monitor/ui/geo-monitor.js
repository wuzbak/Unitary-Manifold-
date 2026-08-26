/**
 * public-site/js/20-geo-monitor.js
 * UM Geophysical Monitor — OSIRIS-inspired live disaster tracker
 * with Unitary Manifold φ-overlay (P806, P786, P16, P808)
 *
 * Live feeds (no API key required):
 *   USGS Significant Earthquakes (past 30 days) — GeoJSON
 *   NASA EONET v3 — wildfires, storms, volcanoes, floods
 *   NOAA Alerts (US severe weather) — optional overlay
 *
 * 🔵 ADJACENT TRACK — UM physics overlays are exploratory geometric
 * analogues applied to geophysics. Not hardgate claims.
 */

'use strict';

// ─── UM Physics Constants (mirror of pillar_geo_monitor.py) ───────────────
const UM = {
  WINDING_NUMBER: 5,
  K_CS: 74,                     // 5² + 7²
  BRAIDED_SOUND_SPEED: 12 / 37,
  PHI_0: 1.0,
  RADION_DELTA_PHI_PER_M5: -32.0,
  RADION_QCD_SUPPRESSION: 1e7,
  PHI_DEBT_DECAY_RATE: 0.15,
  PHI_DEBT_ALIGNMENT_FLOOR: 0.30,
  PLANCK_ENERGY_J: 1.9561e9,
  WILDFIRE_ENERGY_PER_HA_J: 8.0e10,
  HURRICANE_ENERGY_PER_CATEGORY_J: 5.0e18,
};
UM.RADION_COUPLING_ALPHA = Math.abs(UM.RADION_DELTA_PHI_PER_M5) / UM.K_CS;
UM.BASIN_DEPTH = (UM.WINDING_NUMBER ** 2) / UM.K_CS;

// ─── API Endpoints ──────────────────────────────────────────────────────────
const FEEDS = {
  USGS_EQ:    'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.geojson',
  EONET:      'https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=200&days=30',
};

// ─── App State ───────────────────────────────────────────────────────────────
const state = {
  map: null,
  events: [],          // all parsed GeoEvents with overlay
  layers: {
    eq:      { visible: true, ids: [] },
    fire:    { visible: true, ids: [] },
    storm:   { visible: true, ids: [] },
    volcano: { visible: true, ids: [] },
    phi:     { visible: true, ids: [] },
  },
  selectedId: null,
};

// ─── UM Physics Overlay Engine ───────────────────────────────────────────────
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
      return UM.HURRICANE_ENERGY_PER_CATEGORY_J * (magnitude ** 2);
    case 'volcano':
      return Math.pow(10, 3 * magnitude + 10);
    default:
      return Math.pow(10, 1.5 * magnitude + 4.8);
  }
}

function computeOverlay(kind, magnitude, lat, lon, depthKm, areaHa, energyJ) {
  const E_si = energySI(kind, magnitude, areaHa, energyJ);
  const E_planck = E_si / UM.PLANCK_ENERGY_J;
  const E_log = Math.log10(Math.max(E_si, 1.0));

  // Pillar 16 — φ-debt
  const decayArg = UM.PHI_DEBT_DECAY_RATE * E_log;
  const phiDebt = E_planck * (1.0 - Math.exp(-decayArg));
  let phiAlignment = Math.exp(-UM.PHI_DEBT_DECAY_RATE * E_planck);
  phiAlignment = Math.max(UM.PHI_DEBT_ALIGNMENT_FLOOR, Math.min(1.0, phiAlignment));

  // Pillar 806 — radion amplitude
  let radionAmp = UM.RADION_COUPLING_ALPHA * Math.abs(
    Math.log10(Math.max(E_si, 1.0) / UM.PLANCK_ENERGY_J)
  );
  if (kind === 'earthquake' && depthKm != null) {
    radionAmp *= Math.exp(-depthKm / 700.0);
  }
  const suppression = Math.min(Math.exp(UM.RADION_COUPLING_ALPHA * radionAmp), UM.RADION_QCD_SUPPRESSION);

  // Pillar 786 — winding basin
  const basinPert = radionAmp / UM.BASIN_DEPTH;
  const windingStab = Math.max(0.0, 1.0 - Math.min(basinPert, 1.0));

  // Pillar 808 — w_a local
  const wALocal = -radionAmp * (UM.BRAIDED_SOUND_SPEED ** 2);

  // Confidence
  let confidence = 'LOW';
  if (E_planck >= 1e-15) confidence = 'HIGH';
  else if (E_planck >= 1e-18) confidence = 'MEDIUM';

  return { phiDebt, phiAlignment, radionAmp, suppression, basinPert, windingStab, wALocal, confidence, E_si, E_planck };
}

// ─── USGS Parser ─────────────────────────────────────────────────────────────
function parseUSGS(geojson) {
  const out = [];
  for (const f of (geojson.features || [])) {
    const p = f.properties || {};
    const c = (f.geometry || {}).coordinates || [];
    if (p.mag == null || !c.length) continue;
    const mag = Number(p.mag);
    const lon = Number(c[0]), lat = Number(c[1]);
    const depth = c[2] != null ? Number(c[2]) : null;
    if (!isFinite(lon) || !isFinite(lat) || !isFinite(mag)) continue;
    const overlay = computeOverlay('earthquake', mag, lat, lon, depth, null, null);
    out.push({
      id: f.id || `eq-${out.length}`,
      kind: 'earthquake',
      layer: 'eq',
      magnitude: mag,
      lat, lon,
      depthKm: depth,
      place: p.place || '(unknown)',
      time: p.time ? new Date(p.time).toISOString() : null,
      url: p.url || null,
      overlay,
      icon: '⚡',
      color: '#22d3ee',
    });
  }
  return out;
}

// ─── EONET Parser ─────────────────────────────────────────────────────────────
const EONET_KIND_MAP = {
  wildfires: { kind: 'wildfire', layer: 'fire', icon: '🔥', color: '#f97316' },
  volcanoes: { kind: 'volcano',  layer: 'volcano', icon: '🌋', color: '#ef4444' },
  severeStorms: { kind: 'storm', layer: 'storm', icon: '🌀', color: '#a78bfa' },
  floods: { kind: 'flood', layer: 'storm', icon: '🌊', color: '#818cf8' },
  drought: { kind: 'drought', layer: 'storm', icon: '☀️', color: '#fbbf24' },
  dustHaze: { kind: 'storm', layer: 'storm', icon: '🌫️', color: '#94a3b8' },
  landslides: { kind: 'landslide', layer: 'storm', icon: '⛰️', color: '#78716c' },
  seaLakeIce: { kind: 'flood', layer: 'storm', icon: '🧊', color: '#67e8f9' },
  manOfTheMatch: { kind: 'storm', layer: 'storm', icon: '⚠️', color: '#fbbf24' },
};

function parseEONET(data) {
  const out = [];
  for (const ev of (data.events || [])) {
    const cats = ev.categories || [];
    if (!cats.length) continue;
    const catId = cats[0].id || '';
    const meta = EONET_KIND_MAP[catId] || { kind: 'storm', layer: 'storm', icon: '⚠️', color: '#94a3b8' };

    const geometry = ev.geometry || [];
    if (!geometry.length) continue;
    const lastGeom = geometry[geometry.length - 1];
    const coords = lastGeom.coordinates || [];
    if (!coords.length || coords[0] == null) continue;

    const lon = Number(coords[0]), lat = Number(coords[1]);
    if (!isFinite(lon) || !isFinite(lat)) continue;

    const mag = Number(ev.magnitudeValue || 5.0);
    const overlay = computeOverlay(meta.kind, mag, lat, lon, null, null, null);

    out.push({
      id: ev.id || `eonet-${out.length}`,
      kind: meta.kind,
      layer: meta.layer,
      magnitude: mag,
      lat, lon,
      depthKm: null,
      place: ev.title || catId,
      time: lastGeom.date || null,
      url: (ev.sources || []).map(s => s.url).filter(Boolean)[0] || null,
      overlay,
      icon: meta.icon,
      color: meta.color,
    });
  }
  return out;
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
    center: [0, 20],
    zoom: 1.8,
    minZoom: 1,
  });
  state.map.addControl(new maplibregl.NavigationControl(), 'top-right');
  state.map.on('load', loadAllFeeds);
}

// ─── Add / Refresh Map Layers ─────────────────────────────────────────────────
function buildGeoJSON(events, layer) {
  return {
    type: 'FeatureCollection',
    features: events
      .filter(e => e.layer === layer)
      .map(e => ({
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [e.lon, e.lat] },
        properties: {
          id: e.id, kind: e.kind, magnitude: e.magnitude,
          place: e.place, color: e.color,
          phiDebt: e.overlay.phiDebt,
          radionAmp: e.overlay.radionAmp,
          windingStab: e.overlay.windingStab,
          phiAlignment: e.overlay.phiAlignment,
          wALocal: e.overlay.wALocal,
          suppression: e.overlay.suppression,
          basinPert: e.overlay.basinPert,
          time: e.time,
        },
      })),
  };
}

function buildPhiGeoJSON(events) {
  // Phi overlay: all events, sized by phiDebt, coloured by winding stability
  return {
    type: 'FeatureCollection',
    features: events.map(e => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [e.lon, e.lat] },
      properties: {
        id: e.id,
        phiDebt: e.overlay.phiDebt,
        windingStab: e.overlay.windingStab,
      },
    })),
  };
}

const LAYER_DEFS = ['eq', 'fire', 'storm', 'volcano'];

function addOrUpdateLayers() {
  const map = state.map;
  const events = state.events;

  for (const layer of LAYER_DEFS) {
    const srcId = `src-${layer}`;
    const circleId = `lyr-${layer}-circle`;
    const labelId = `lyr-${layer}-label`;
    const gj = buildGeoJSON(events, layer);

    if (map.getSource(srcId)) {
      map.getSource(srcId).setData(gj);
    } else {
      map.addSource(srcId, { type: 'geojson', data: gj });
      map.addLayer({
        id: circleId, type: 'circle', source: srcId,
        layout: { visibility: state.layers[layer].visible ? 'visible' : 'none' },
        paint: {
          'circle-radius': [
            'interpolate', ['linear'], ['get', 'magnitude'],
            2, 5, 5, 10, 7, 18, 9, 28,
          ],
          'circle-color': ['get', 'color'],
          'circle-opacity': 0.82,
          'circle-stroke-width': 1.5,
          'circle-stroke-color': 'rgba(255,255,255,0.25)',
        },
      });
      map.addLayer({
        id: labelId, type: 'symbol', source: srcId,
        layout: {
          'text-field': ['concat', ['get', 'kind'], ' M', ['to-string', ['round', ['get', 'magnitude']]]],
          'text-font': ['Open Sans Regular'],
          'text-size': 9,
          'text-offset': [0, 1.4],
          'text-anchor': 'top',
          visibility: state.layers[layer].visible ? 'visible' : 'none',
        },
        paint: { 'text-color': 'rgba(200,220,240,0.6)', 'text-halo-color': '#000', 'text-halo-width': 1 },
      });

      // Popup on click
      map.on('click', circleId, e => onMarkerClick(e, layer));
      map.on('mouseenter', circleId, () => { map.getCanvas().style.cursor = 'pointer'; });
      map.on('mouseleave', circleId, () => { map.getCanvas().style.cursor = ''; });
    }
    state.layers[layer].ids = [circleId, labelId];
  }

  // Phi overlay layer (heatmap-style circle)
  const phiSrc = 'src-phi';
  const phiLyr = 'lyr-phi-circle';
  const phiGJ = buildPhiGeoJSON(events);
  if (map.getSource(phiSrc)) {
    map.getSource(phiSrc).setData(phiGJ);
  } else {
    map.addSource(phiSrc, { type: 'geojson', data: phiGJ });
    map.addLayer({
      id: phiLyr, type: 'circle', source: phiSrc,
      layout: { visibility: state.layers.phi.visible ? 'visible' : 'none' },
      paint: {
        'circle-radius': [
          'interpolate', ['linear'],
          ['get', 'phiDebt'],
          0, 8, 1e-17, 20, 1e-15, 35,
        ],
        'circle-color': [
          'interpolate', ['linear'],
          ['get', 'windingStab'],
          0.0, '#ef4444',
          0.5, '#f97316',
          0.8, '#22d3ee',
          1.0, '#34d399',
        ],
        'circle-opacity': 0.25,
        'circle-stroke-width': 0,
      },
    }, LAYER_DEFS.length ? `lyr-eq-circle` : undefined);
    state.layers.phi.ids = [phiLyr];
  }
}

// ─── Popup ────────────────────────────────────────────────────────────────────
let currentPopup = null;

function onMarkerClick(e, layer) {
  if (!e.features.length) return;
  const p = e.features[0].properties;
  const ev = state.events.find(x => x.id === p.id);
  if (ev) selectEvent(ev.id);

  if (currentPopup) currentPopup.remove();
  currentPopup = new maplibregl.Popup({ closeButton: true, maxWidth: '300px' })
    .setLngLat(e.lngLat)
    .setHTML(`
      <div class="popup-title">${p.kind ? p.kind.toUpperCase() : ''} ${p.icon || ''} M${Number(p.magnitude).toFixed(1)}</div>
      <div class="popup-row"><span class="popup-key">Location</span><span class="popup-val">${p.place || '—'}</span></div>
      <div class="popup-row"><span class="popup-key">φ-Debt</span><span class="popup-phi">${fmtSci(p.phiDebt)}</span></div>
      <div class="popup-row"><span class="popup-key">Radion |Δφ/φ₀|</span><span class="popup-val">${Number(p.radionAmp).toFixed(4)}</span></div>
      <div class="popup-row"><span class="popup-key">Basin Stab.</span><span class="popup-val">${Number(p.windingStab).toFixed(3)}</span></div>
      <div class="popup-adj">🔵 Adjacent Track — P806 · P786 · P16</div>
    `)
    .addTo(state.map);
}

// ─── Sidebar Event List ───────────────────────────────────────────────────────
function renderEventList() {
  const list = document.getElementById('event-list');
  if (!list) return;
  const events = [...state.events]
    .sort((a, b) => b.magnitude - a.magnitude)
    .slice(0, 80);

  if (!events.length) {
    list.innerHTML = '<div style="color:#475569;font-size:0.8rem;padding:0.8rem">No events loaded.</div>';
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

  document.getElementById('ev-total').textContent = `(${state.events.length})`;
}

function selectEvent(id) {
  state.selectedId = id;
  const ev = state.events.find(e => e.id === id);
  if (!ev) return;

  // Fly to event
  state.map.flyTo({ center: [ev.lon, ev.lat], zoom: 5, duration: 800 });

  // Update detail panel
  const panel = document.getElementById('geo-detail');
  if (panel) panel.style.display = 'grid';

  setText('det-kind', `${ev.icon} ${ev.kind.toUpperCase()}`);
  setText('det-loc', ev.place);
  setText('det-mag', `M${ev.magnitude.toFixed(2)}`);
  setText('det-depth', ev.depthKm != null ? `Depth: ${ev.depthKm.toFixed(1)} km` : (ev.time || ''));
  setText('det-phi', fmtSci(ev.overlay.phiDebt));
  setText('det-align', ev.overlay.phiAlignment.toFixed(3));
  setText('det-radion', ev.overlay.radionAmp.toFixed(5));
  setText('det-supp', fmtSci(ev.overlay.suppression));
  setText('det-stab', ev.overlay.windingStab.toFixed(4));
  setText('det-pert', ev.overlay.basinPert.toFixed(4));
  setText('det-wa', ev.overlay.wALocal.toExponential(3));

  // Update list highlight
  renderEventList();
}

// ─── Counts & Status ─────────────────────────────────────────────────────────
function updateCounts() {
  const byLayer = { eq: 0, fire: 0, storm: 0, volcano: 0 };
  for (const ev of state.events) {
    if (ev.layer in byLayer) byLayer[ev.layer]++;
  }
  setText('cnt-eq', String(byLayer.eq));
  setText('cnt-fire', String(byLayer.fire));
  setText('cnt-storm', String(byLayer.storm));
  setText('cnt-volcano', String(byLayer.volcano));
  setText('cnt-phi', String(state.events.length));
  setText('status-eq', `⚡ EQ: ${byLayer.eq}`);
  setText('status-fire', `🔥 Fire: ${byLayer.fire}`);
  setText('status-storm', `🌀 Storm: ${byLayer.storm}`);
  setText('last-updated', `Updated ${new Date().toUTCString()}`);

  // UM summary stats
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
  const layerState = state.layers[key];
  layerState.visible = !layerState.visible;
  const vis = layerState.visible ? 'visible' : 'none';
  for (const id of layerState.ids) {
    if (state.map.getLayer(id)) state.map.setLayoutProperty(id, 'visibility', vis);
  }
  const toggle = document.getElementById(`toggle-${key}`);
  if (toggle) {
    if (layerState.visible) toggle.classList.add('active');
    else toggle.classList.remove('active');
  }
}

// ─── Feed Loading ─────────────────────────────────────────────────────────────
async function loadAllFeeds() {
  const results = await Promise.allSettled([
    fetch(FEEDS.USGS_EQ).then(r => r.json()),
    fetch(FEEDS.EONET).then(r => r.json()),
  ]);

  let allEvents = [];

  if (results[0].status === 'fulfilled') {
    allEvents = allEvents.concat(parseUSGS(results[0].value));
  } else {
    console.warn('USGS feed failed:', results[0].reason);
  }

  if (results[1].status === 'fulfilled') {
    allEvents = allEvents.concat(parseEONET(results[1].value));
  } else {
    console.warn('EONET feed failed:', results[1].reason);
  }

  state.events = allEvents;
  addOrUpdateLayers();
  updateCounts();
  renderEventList();
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
});
