# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from browser_contract_helpers import launch_browser_or_skip, playwright_sync_api, running_server
from geo_monitor.app.server import build_server
from geo_monitor.engine.feeds import EONETFeedParser, NOAAAlertsFeedParser, NWACFeedParser, USGSFeedParser


USGS_FIXTURE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"mag": 6.4, "place": "Offshore test quake", "time": 1788998400000, "url": "https://example.invalid/usgs"},
            "geometry": {"type": "Point", "coordinates": [-123.1, 47.6, 12.0]},
            "id": "usgs-1",
        },
        {
            "type": "Feature",
            "properties": {"mag": 5.2, "place": "<img src=x onerror=window.feedInjected=true>", "time": 1788998400000, "url": "https://example.invalid/usgs"},
            "geometry": {"type": "Point", "coordinates": [-122.8, 47.4, 9.0]},
            "id": "usgs-2",
        },
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
def test_geo_monitor_browser_contract(browser_name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    sync_api = playwright_sync_api()
    monkeypatch.delenv("FIRMS_MAP_KEY", raising=False)
    monkeypatch.setattr(USGSFeedParser, "fetch", lambda self, url: USGS_FIXTURE)
    monkeypatch.setattr(EONETFeedParser, "fetch", lambda self, **kwargs: EONET_FIXTURE)
    monkeypatch.setattr(NOAAAlertsFeedParser, "fetch", lambda self, area=None: NWS_FIXTURE)
    monkeypatch.setattr(NWACFeedParser, "fetch", lambda self: NWAC_FIXTURE)
    monkeypatch.setattr("geo_monitor.app.server.fetch_kp_index", lambda: {
        "kp": 2.0, "observed_time": "2026-09-10 00:00:00", "source": "https://example.invalid/kp",
    })
    with running_server(
        lambda: build_server(port=0)
    ) as base_url:
        with sync_api.sync_playwright() as playwright:
            browser = launch_browser_or_skip(playwright, browser_name)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            try:
                page.add_init_script(MAPLIBRE_STUB)
                page.goto(base_url, wait_until="domcontentloaded")
                page.wait_for_function("document.getElementById('cnt-eq').textContent.trim() !== '—'")
                assert "UM Geophysical Monitor" in page.title()
                assert "Offshore test quake" in (page.locator("#event-list").text_content() or "")
                assert page.locator("#event-list img").count() == 0
                assert page.evaluate("window.feedInjected || false") is False
                assert "<img src=x onerror=window.feedInjected=true>" in (page.locator("#event-list").text_content() or "")
                page.locator("#event-list .event-item").first.click()
                page.wait_for_function("document.getElementById('geo-detail').style.display === 'grid'")
                page.locator("#toggle-fire").click()
                assert "M6.40" in (page.locator("#det-mag").text_content() or "")
                assert len(page.screenshot(full_page=True)) > 10_000
            finally:
                browser.close()
