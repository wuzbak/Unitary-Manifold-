# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.error import HTTPError

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from geo_monitor.engine.firms_feed import FIRMS_DEMO_KEY, fetch_firms_active_fires
from geo_monitor.engine.ionosphere_feed import fetch_kp_index, get_ionospheric_status
from geo_monitor.engine.physics import GeoEvent
from geo_monitor.engine.wm_feeds import GeoMonitorV3Feeds, GeoMonitorV4Feeds


class _Response:
    def __init__(self, body: str):
        self.body = body.encode('utf-8')

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_firms_demo_key_constant() -> None:
    assert FIRMS_DEMO_KEY == 'd3efa5f4db12f5f3f61f8ae4e2c0d7c9'


def test_firms_fetch_parses_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    csv_text = 'latitude,longitude,frp,acq_date,confidence\n34.5,-118.2,12.5,2026-09-01,h\n'
    monkeypatch.setattr('geo_monitor.engine.firms_feed.request.urlopen', lambda req, timeout=20: _Response(csv_text))
    events = fetch_firms_active_fires()
    assert events == [{'lat': 34.5, 'lon': -118.2, 'frp': 12.5, 'acq_date': '2026-09-01', 'confidence': 'h'}]


def test_firms_fetch_uses_custom_bbox_and_days(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = {}

    def fake_urlopen(req, timeout=20):
        seen['url'] = req.full_url
        return _Response('latitude,longitude,frp,acq_date,confidence\n')

    monkeypatch.setattr('geo_monitor.engine.firms_feed.request.urlopen', fake_urlopen)
    fetch_firms_active_fires(bbox=(-10, -20, 10, 20), days=3)
    assert '/-10,-20,10,20/3' in seen['url']


def test_firms_fetch_returns_empty_on_403(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(req, timeout=20):
        raise HTTPError(req.full_url, 403, 'Forbidden', hdrs=None, fp=None)

    monkeypatch.setattr('geo_monitor.engine.firms_feed.request.urlopen', boom)
    assert fetch_firms_active_fires() == []


def test_firms_fetch_returns_empty_on_429(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(req, timeout=20):
        raise HTTPError(req.full_url, 429, 'Rate limited', hdrs=None, fp=None)

    monkeypatch.setattr('geo_monitor.engine.firms_feed.request.urlopen', boom)
    assert fetch_firms_active_fires() == []


def test_firms_fetch_returns_empty_on_bad_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('geo_monitor.engine.firms_feed.request.urlopen', lambda req, timeout=20: _Response('not,csv\na,b\n'))
    assert fetch_firms_active_fires() == []


def test_kp_fetch_parses_json_table(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = json.dumps([['time_tag', 'kp'], ['2026-09-01 00:00:00.000', '5.33']])
    monkeypatch.setattr('geo_monitor.engine.ionosphere_feed.request.urlopen', lambda req, timeout=20: _Response(payload))
    result = fetch_kp_index()
    assert result['kp'] == pytest.approx(5.33)
    assert result['observed_time'] == '2026-09-01 00:00:00.000'


def test_kp_fetch_offline_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('geo_monitor.engine.ionosphere_feed.request.urlopen', lambda req, timeout=20: (_ for _ in ()).throw(RuntimeError('offline')))
    assert fetch_kp_index()['kp'] == 0


@pytest.mark.parametrize(
    ('kp', 'level', 'alert'),
    [
        (0, 'quiet', False),
        (4.0, 'active', False),
        (5.0, 'storm', True),
        (7.0, 'severe', True),
    ],
)
def test_ionosphere_status_bands(monkeypatch: pytest.MonkeyPatch, kp: float, level: str, alert: bool) -> None:
    monkeypatch.setattr('geo_monitor.engine.ionosphere_feed.fetch_kp_index', lambda: {'kp': kp, 'observed_time': '2026-09-01'})
    result = get_ionospheric_status()
    assert result['storm_level'] == level
    assert result['space_weather_alert'] is alert


def test_ionosphere_status_offline_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('geo_monitor.engine.ionosphere_feed.fetch_kp_index', lambda: {'kp': 'bad'})
    assert get_ionospheric_status() == {'kp': 0, 'storm_level': 'quiet', 'space_weather_alert': False}


def test_v4_feeds_alias_preserved() -> None:
    assert GeoMonitorV3Feeds is GeoMonitorV4Feeds


def test_v4_current_kp_uses_swpc_first(monkeypatch: pytest.MonkeyPatch) -> None:
    feeds = GeoMonitorV4Feeds()
    monkeypatch.setattr(feeds._swpc, 'get_current_kp_value', lambda: 4.2)
    assert feeds.current_kp() == pytest.approx(4.2)


def test_v4_current_kp_falls_back_to_ionosphere(monkeypatch: pytest.MonkeyPatch) -> None:
    feeds = GeoMonitorV4Feeds()
    monkeypatch.setattr(feeds._swpc, 'get_current_kp_value', lambda: 0.0)
    monkeypatch.setattr('geo_monitor.engine.wm_feeds.get_ionospheric_status', lambda: {'kp': 3.5, 'storm_level': 'quiet', 'space_weather_alert': False})
    assert feeds.current_kp() == pytest.approx(3.5)


def test_v4_ionosphere_status_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('geo_monitor.engine.wm_feeds.get_ionospheric_status', lambda: {'kp': 6, 'storm_level': 'storm', 'space_weather_alert': True})
    assert GeoMonitorV4Feeds().ionosphere_status()['storm_level'] == 'storm'


def test_v4_firms_fire_events_maps_to_geoevents(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('geo_monitor.engine.wm_feeds.fetch_firms_active_fires', lambda bbox=(-180, -90, 180, 90), days=1: [{'lat': 10.0, 'lon': 20.0, 'frp': 15.0, 'acq_date': '2026-09-01', 'confidence': 'n'}])
    events = GeoMonitorV4Feeds().firms_fire_events()
    assert len(events) == 1
    assert isinstance(events[0], GeoEvent)
    assert events[0].kind == 'wildfire'


def test_v4_firms_fire_events_ignores_bad_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('geo_monitor.engine.wm_feeds.fetch_firms_active_fires', lambda bbox=(-180, -90, 180, 90), days=1: [{'lat': 'bad', 'lon': 20.0, 'frp': 15.0}])
    assert GeoMonitorV4Feeds().firms_fire_events() == []


def test_v4_space_weather_events_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    feeds = GeoMonitorV4Feeds()
    sample = GeoEvent('space_weather', 5.0, 90.0, 0.0)
    monkeypatch.setattr(feeds._swpc, 'get_current_kp_event', lambda: sample)
    monkeypatch.setattr(feeds._swpc, 'get_alert_events', lambda: [])
    events = feeds.space_weather_events()
    assert events == [sample]


def test_readme_mentions_v4() -> None:
    text = (PRODUCT_ROOT / 'README.md').read_text(encoding='utf-8')
    assert 'v4' in text


def test_readme_mentions_firms_and_ionosphere() -> None:
    text = (PRODUCT_ROOT / 'README.md').read_text(encoding='utf-8')
    assert 'FIRMS' in text
    assert 'ionosphere' in text.lower()


def test_v4_firms_magnitude_scales_from_frp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('geo_monitor.engine.wm_feeds.fetch_firms_active_fires', lambda bbox=(-180, -90, 180, 90), days=1: [{'lat': 1.0, 'lon': 2.0, 'frp': 5.0, 'acq_date': '2026-09-01', 'confidence': 'h'}])
    event = GeoMonitorV4Feeds().firms_fire_events()[0]
    assert event.magnitude == pytest.approx(1.0)


def test_v4_firms_energy_proxy_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('geo_monitor.engine.wm_feeds.fetch_firms_active_fires', lambda bbox=(-180, -90, 180, 90), days=1: [{'lat': 1.0, 'lon': 2.0, 'frp': 9.0, 'acq_date': '2026-09-01', 'confidence': 'h'}])
    event = GeoMonitorV4Feeds().firms_fire_events()[0]
    assert event.energy_J == pytest.approx(9.0e9)
