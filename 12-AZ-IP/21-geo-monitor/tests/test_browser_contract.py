# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.browser_contract_helpers import launch_browser_or_skip, playwright_sync_api, reserve_port, running_server


USGS_FIXTURE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"mag": 6.4, "place": "Offshore test quake", "time": 1725926400000, "url": "https://example.invalid/usgs"},
            "geometry": {"type": "Point", "coordinates": [-123.1, 47.6, 12.0]},
            "id": "usgs-1",
        }
    ],
}

EONET_FIXTURE = {
    "events": [
        {
            "id": "eonet-1",
            "title": "Test Wildfire Cluster",
            "categories": [{"id": "wildfires"}],
            "geometry": [{"date": "2026-09-10T00:00:00Z", "coordinates": [-121.8, 46.9]}],
            "sources": [{"url": "https://example.invalid/eonet"}],
        }
    ]
}

NWS_FIXTURE = {
    "features": [
        {
            "type": "Feature",
            "properties": {"event": "Flood Warning", "severity": "Moderate", "headline": "Test flood warning", "sent": "2026-09-10T00:00:00Z"},
            "geometry": {"type": "Point", "coordinates": [-122.2, 47.5]},
        }
    ]
}

NWAC_FIXTURE = {
    "data": [
        {
            "forecast_zone": "west-slopes-central",
            "danger_level": 3,
            "published_time": "2026-09-10T00:00:00Z",
            "url": "https://example.invalid/nwac"
        }
    ]
}

MAPLIBRE_STUB = """
window.maplibregl = {
  NavigationControl: function NavigationControl() {},
  Popup: function Popup() {
    return {
      setLngLat() { return this; },
      setHTML() { return this; },
      addTo() { return this; },
      remove() {}
    };
  },
  Map: function Map() {
    const sources = new globalThis.Map();
    return {
      addControl() {},
      on(event, layerOrHandler, maybeHandler) {
        const handler = typeof layerOrHandler === 'function' ? layerOrHandler : maybeHandler;
        if (event === 'load' && typeof handler === 'function') {
          setTimeout(() => handler(), 0);
        }
      },
      addSource(id, source) {
        const record = {
          data: source.data,
          setData(next) { this.data = next; }
        };
        sources.set(id, record);
      },
      getSource(id) { return sources.get(id) || null; },
      addLayer() {},
      getLayer() { return true; },
      setLayoutProperty() {},
      flyTo() {},
      getCanvas() { return { style: {} }; }
    };
  }
};
"""


@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_geo_monitor_browser_contract(browser_name: str) -> None:
    sync_api = playwright_sync_api()
    port = reserve_port()
    base_url = f"http://127.0.0.1:{port}/"
    with running_server(PRODUCT_ROOT, ["run.py", "serve", "--port", str(port), "--no-open"], base_url=base_url):
        with sync_api.sync_playwright() as playwright:
            browser = launch_browser_or_skip(playwright, browser_name)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            try:
                page.add_init_script(MAPLIBRE_STUB)
                page.route("**/earthquake.usgs.gov/**", lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(USGS_FIXTURE)))
                page.route("**/eonet.gsfc.nasa.gov/**", lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(EONET_FIXTURE)))
                page.route("**/api.weather.gov/**", lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(NWS_FIXTURE)))
                page.route("**/api.avalanche.org/**", lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(NWAC_FIXTURE)))
                page.goto(base_url, wait_until="domcontentloaded")
                page.wait_for_function("document.getElementById('cnt-eq').textContent.trim() !== '—'")
                assert "UM Geophysical Monitor" in page.title()
                assert "Offshore test quake" in (page.locator("#event-list").text_content() or "")
                page.locator("#event-list .event-item").first.click()
                page.wait_for_function("document.getElementById('geo-detail').style.display === 'grid'")
                page.locator("#toggle-fire").click()
                assert "M6.40" in (page.locator("#det-mag").text_content() or "")
                assert len(page.screenshot(full_page=True)) > 10_000
            finally:
                browser.close()
