# ATTRIBUTION.md — UM Geo Monitor v3

## Data Sources & Attribution

This product integrates data from the following open-science and public-domain sources.
All sources are consumed via public REST APIs or open feeds; no proprietary source
code is copied into this repository.

---

### 1. USGS Earthquake Hazards Feed
- **URL:** https://earthquake.usgs.gov/earthquakes/feed/v1.0/
- **Licence:** Public domain (US Government)
- **Usage:** M2.5+ earthquakes, past 30 days / 24 hours

### 2. NASA EONET v3
- **URL:** https://eonet.gsfc.nasa.gov/api/v3/
- **Licence:** Public domain (NASA / US Government)
- **Usage:** Wildfires, severe storms, volcanoes, floods, landslides

### 3. NOAA NWS Active Alerts
- **URL:** https://api.weather.gov/alerts/active
- **Licence:** Public domain (US Government, NOAA)
- **Usage:** Severe weather, fire weather, tornado, tsunami, flood alerts

### 4. NWAC Avalanche Center
- **URL:** https://api.avalanche.org/v2/public/
- **Licence:** Open (Northwest Avalanche Center / USFS)
- **Usage:** Avalanche danger ratings for WA + N. Oregon Cascades

### 5. NOAA SWPC — Space Weather Prediction Center *(v3)*
- **URL:** https://www.swpc.noaa.gov/ ; https://services.swpc.noaa.gov/
- **Licence:** Public domain (US Government, NOAA)
- **Usage:** Real-time planetary Kp index (1-minute resolution), geomagnetic storm alerts
- **No API key required**

### 6. GDACS — Global Disaster Alert and Coordination System *(v3)*
- **URL:** https://www.gdacs.org/
- **Provider:** United Nations OCHA / European Commission
- **Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Usage:** Global flood, cyclone, earthquake, volcano, drought alerts via GeoRSS
- **Citation:** Colombo R., Bello M., et al., *GDACS* (2003-present). UN Office for
  the Coordination of Humanitarian Affairs.

### 7. CISA KEV — Known Exploited Vulnerabilities Catalog *(v3)*
- **URL:** https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- **Licence:** Public domain (US Government, CISA)
- **Usage:** Recent cyber vulnerability events; magnitude proxy from CVSS
- **No API key required**

### 8. OpenSky Network — Flight Density *(v3, flight layer)*
- **URL:** https://opensky-network.org/apidoc/
- **Licence:** OpenSky Network Terms of Use (free for non-commercial research)
- **Usage:** Real-time ADS-B flight state vectors for global density heatmap
- **No API key required for anonymous access**

### 9. WorldMonitor (koala73/worldmonitor) *(v3, optional)*
- **URL:** https://worldmonitor.app / https://api.worldmonitor.app
- **GitHub:** https://github.com/koala73/worldmonitor
- **Licence:** [AGPL v3](https://www.gnu.org/licenses/agpl-3.0)
- **Usage:** Country Instability Index (CII v8) and infrastructure alerts
  via the public REST API and official `worldmonitor-sdk` Python package.
- **Integration posture:** We consume WorldMonitor's public REST API only.
  No WorldMonitor source code is copied or distributed in this repository.
  Our own integration code (`wm_feeds.py`) is published under the
  Defensive Public Commons v1.0 licence.  WM_API_KEY environment variable
  required; the integration degrades gracefully when absent.
- **AGPL compatibility note:** Our use is API-level integration (data consumer),
  not code-level incorporation.  We acknowledge WorldMonitor's AGPL licence and
  encourage users to review its terms at the link above.

---

## This Repository

**Licence:** Defensive Public Commons v1.0 (2026) — irrevocably public domain.

**Authors:**
- Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**
- Code architecture, test suites, document engineering: **GitHub Copilot** (AI)

**Epistemic note:** UM physics overlays in this product are 🔵 ADJACENT TRACK
geometric analogues, not hardgate physics claims.  See
[FALLIBILITY.md](../../FALLIBILITY.md) for honest limitations.
