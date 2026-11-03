# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
LithosOS — USGS measured-seismicity adapter tests (deterministic, no network).
"""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone

import pytest

from lithic.app.sync import usgs_seismicity as us
from lithic.app.sync.usgs_seismicity import (
    SeismicityQuery, SeismicityQueryError, USGSSeismicityAdapter,
    parse_feature_collection, format_report_markdown,
)

NOW = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)
NOW_MS = int(NOW.timestamp() * 1000)
SITE = dict(latitude=38.79, longitude=-122.76)  # The Geysers geothermal field, CA


def _feature(eid, mag, lon, lat, depth, minutes_ago, status="reviewed"):
    return {
        "type": "Feature",
        "id": eid,
        "properties": {
            "mag": mag, "place": f"near {eid}", "time": NOW_MS - minutes_ago * 60_000,
            "magType": "md", "status": status,
            "url": f"https://earthquake.usgs.gov/earthquakes/eventpage/{eid}",
        },
        "geometry": {"type": "Point", "coordinates": [lon, lat, depth]},
    }


def _payload(generated_ms=NOW_MS, features=None):
    if features is None:
        features = [
            _feature("nc001", 1.8, -122.80, 38.82, 2.1, 30),
            _feature("nc002", 2.6, -122.75, 38.78, 1.4, 600, status="automatic"),
            _feature("nc003", None, -122.70, 38.80, 3.0, 1200),
        ]
    return {
        "type": "FeatureCollection",
        "metadata": {"generated": generated_ms, "status": 200, "count": len(features)},
        "features": features,
    }


class FakeFetch:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, timeout_s):
        self.calls.append((url, timeout_s))
        r = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        if isinstance(r, BaseException):
            raise r
        return r if isinstance(r, bytes) else json.dumps(r).encode()


class Clock:
    def __init__(self, t=NOW):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def _blocked(*a, **k):
        raise AssertionError("tests must not touch the network")
    monkeypatch.setattr(us.urllib.request, "urlopen", _blocked)
    monkeypatch.setattr(socket.socket, "connect", _blocked)


def _adapter(tmp_path, fetch, clock=None, **kw):
    return USGSSeismicityAdapter(tmp_path / "s.db", fetch_fn=fetch, now_fn=clock or Clock(), **kw)


# ── query validation ────────────────────────────────────────────────────────

class TestQuery:
    @pytest.mark.parametrize("kw", [
        dict(latitude=91, longitude=0), dict(latitude=0, longitude=181),
        dict(latitude=0, longitude=0, radius_km=0), dict(latitude=0, longitude=0, days=91),
        dict(latitude=0, longitude=0, limit=0), dict(latitude=float("nan"), longitude=0),
        dict(latitude=0, longitude=0, min_magnitude=11),
    ])
    def test_out_of_bounds_rejected(self, kw):
        with pytest.raises(SeismicityQueryError):
            SeismicityQuery(**kw).validate()

    def test_url_is_usgs_fdsn_geojson(self):
        url = SeismicityQuery(**SITE, radius_km=50, days=7).to_url(NOW)
        p = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(p.query)
        assert p.scheme == "https" and p.hostname == "earthquake.usgs.gov"
        assert p.path == "/fdsnws/event/1/query"
        assert qs["format"] == ["geojson"]
        assert qs["maxradiuskm"] == ["50"]
        assert qs["starttime"] == ["2026-10-26T12:00:00"]

    def test_invalid_query_never_fetches(self, tmp_path):
        fetch = FakeFetch([_payload()])
        with pytest.raises(SeismicityQueryError):
            _adapter(tmp_path, fetch).get_seismicity(SeismicityQuery(latitude=100, longitude=0))
        assert fetch.calls == []

    def test_cache_key_matches_upstream_coordinate_precision(self):
        first = SeismicityQuery(latitude=38.7900, longitude=-122.7600)
        nearby = SeismicityQuery(latitude=38.7904, longitude=-122.7600)
        assert first.to_url(NOW) != nearby.to_url(NOW)
        assert first.cache_key() != nearby.cache_key()


# ── schema validation ──────────────────────────────────────────────────────

class TestSchema:
    q = SeismicityQuery(**SITE)

    @pytest.mark.parametrize("bad", [
        [], {"type": "Feature"},
        {"type": "FeatureCollection", "features": []},
        {"type": "FeatureCollection", "metadata": {"generated": "x"}, "features": []},
        {"type": "FeatureCollection", "metadata": {"generated": 1}, "features": {}},
    ])
    def test_bad_envelope_raises(self, bad):
        with pytest.raises(us.SeismicitySchemaError):
            parse_feature_collection(bad, self.q)

    def test_malformed_features_dropped_and_counted(self):
        good = _feature("ok1", 2.0, -122.8, 38.8, 1.0, 5)
        bad_coords = _feature("b1", 2.0, "x", 38.8, 1.0, 5)
        bad_mag = _feature("b2", "big", -122.8, 38.8, 1.0, 5)
        no_time = _feature("b3", 1.0, -122.8, 38.8, 1.0, 5)
        del no_time["properties"]["time"]
        no_id = _feature("", 1.0, -122.8, 38.8, 1.0, 5)
        events, meta = parse_feature_collection(
            _payload(features=[good, bad_coords, bad_mag, no_time, no_id, "junk"]), self.q)
        assert [e.event_id for e in events] == ["ok1"]
        assert meta["features_received"] == 6 and meta["features_rejected"] == 5

    def test_event_fields_and_distance(self):
        events, _ = parse_feature_collection(_payload(), self.q)
        assert [e.event_id for e in events] == ["nc001", "nc002", "nc003"]  # newest first
        e = events[0]
        assert e.time_utc == "2026-11-02T11:30:00Z"
        assert e.depth_km == 2.1 and e.magnitude == 1.8
        assert 0 < e.distance_km < 10
        assert events[2].magnitude is None


# ── status / provenance workflow ───────────────────────────────────────────

class TestAdapterStatus:
    def test_live_fetch_with_provenance(self, tmp_path):
        fetch = FakeFetch([_payload()])
        r = _adapter(tmp_path, fetch, timeout_s=3).get_seismicity(SeismicityQuery(**SITE))
        assert r.status == "live" and r.error == ""
        assert r.summary["event_count"] == 3 and r.summary["max_magnitude"] == 2.6
        assert r.summary["reviewed_fraction"] == pytest.approx(0.667)
        p = r.provenance
        assert p["source_url"] == fetch.calls[0][0]
        assert p["retrieved_at_utc"] == "2026-11-02T12:00:00Z"
        assert p["source_generated_utc"] == "2026-11-02T12:00:00Z"
        assert p["from_cache"] is False and p["data_age_s"] == 0
        assert "public domain" in p["license"]
        assert fetch.calls[0][1] == 3

    def test_timeout_is_clamped(self, tmp_path):
        assert _adapter(tmp_path, FakeFetch([_payload()]), timeout_s=999).timeout_s == us.MAX_TIMEOUT_S
        assert _adapter(tmp_path, FakeFetch([_payload()]), timeout_s=0).timeout_s == us.MIN_TIMEOUT_S

    def test_fresh_cache_served_without_fetch(self, tmp_path):
        clock = Clock()
        fetch = FakeFetch([_payload()])
        a = _adapter(tmp_path, fetch, clock)
        a.get_seismicity(SeismicityQuery(**SITE))
        clock.t = NOW + timedelta(minutes=5)
        r = a.get_seismicity(SeismicityQuery(**SITE))
        assert r.status == "cached" and r.provenance["from_cache"] is True
        assert len(fetch.calls) == 1

    def test_refresh_bypasses_cache(self, tmp_path):
        fetch = FakeFetch([_payload()])
        a = _adapter(tmp_path, fetch)
        a.get_seismicity(SeismicityQuery(**SITE))
        r = a.get_seismicity(SeismicityQuery(**SITE), refresh=True)
        assert r.status == "live" and len(fetch.calls) == 2

    def test_timeout_falls_back_to_stale_cache(self, tmp_path):
        clock = Clock()
        fetch = FakeFetch([_payload(), urllib.error.URLError(TimeoutError("timed out"))])
        a = _adapter(tmp_path, fetch, clock)
        a.get_seismicity(SeismicityQuery(**SITE))
        clock.t = NOW + timedelta(hours=3)
        r = a.get_seismicity(SeismicityQuery(**SITE))
        assert r.status == "stale"
        assert "timed out" in r.error
        assert r.summary["event_count"] == 3
        assert r.provenance["retrieved_at_utc"] == "2026-11-02T12:00:00Z"
        assert r.provenance["data_age_s"] == 3 * 3600

    def test_old_source_generation_marks_stale_even_when_live(self, tmp_path):
        old = NOW_MS - 2 * 3600 * 1000
        r = _adapter(tmp_path, FakeFetch([_payload(generated_ms=old)])).get_seismicity(SeismicityQuery(**SITE))
        assert r.status == "stale" and r.provenance["from_cache"] is False

    @pytest.mark.parametrize("failure,needle", [
        (TimeoutError(), "timed out"),
        (urllib.error.URLError("dns"), "unreachable"),
        (b"<html>not json</html>", "invalid JSON"),
        ({"type": "nope"}, "schema validation failed"),
    ])
    def test_unavailable_without_cache(self, tmp_path, failure, needle):
        r = _adapter(tmp_path, FakeFetch([failure])).get_seismicity(SeismicityQuery(**SITE))
        assert r.status == "unavailable" and needle in r.error
        assert r.events == [] and r.summary == {}
        assert r.provenance["source"] == us.SOURCE_NAME

    def test_offline_mode_never_fetches(self, tmp_path):
        fetch = FakeFetch([_payload()])
        r = _adapter(tmp_path, fetch, offline=True).get_seismicity(SeismicityQuery(**SITE))
        assert r.status == "unavailable" and "offline" in r.error and fetch.calls == []

    def test_offline_mode_serves_existing_cache_labelled(self, tmp_path):
        clock = Clock()
        _adapter(tmp_path, FakeFetch([_payload()]), clock).get_seismicity(SeismicityQuery(**SITE))
        clock.t = NOW + timedelta(days=1)
        fetch = FakeFetch([_payload()])
        r = _adapter(tmp_path, fetch, clock, offline=True).get_seismicity(SeismicityQuery(**SITE))
        assert r.status == "stale" and fetch.calls == []

    def test_empty_catalogue_is_live_not_unavailable(self, tmp_path):
        r = _adapter(tmp_path, FakeFetch([_payload(features=[])])).get_seismicity(SeismicityQuery(**SITE))
        assert r.status == "live" and r.summary["event_count"] == 0
        assert r.summary["max_magnitude"] is None

    def test_default_fetch_refuses_non_usgs_host(self):
        with pytest.raises(ValueError):
            us.default_fetch("https://example.com/x", 1.0)
        with pytest.raises(ValueError):
            us.default_fetch("http://earthquake.usgs.gov/x", 1.0)

    def test_cache_storage_errors_are_not_silently_ignored(self, tmp_path, monkeypatch):
        def fail_connect(*args, **kwargs):
            raise us.sqlite3.OperationalError("database unavailable")

        monkeypatch.setattr(us.sqlite3, "connect", fail_connect)
        adapter = _adapter(tmp_path, FakeFetch([_payload()]))
        with pytest.raises(us.sqlite3.OperationalError, match="database unavailable"):
            adapter.get_seismicity(SeismicityQuery(**SITE))

    def test_report_markdown_badges(self, tmp_path):
        live = _adapter(tmp_path, FakeFetch([_payload()])).get_seismicity(SeismicityQuery(**SITE))
        assert "LIVE" in format_report_markdown(live) and "USGS" in format_report_markdown(live)
        down = USGSSeismicityAdapter(None, fetch_fn=FakeFetch([TimeoutError()]), now_fn=Clock()) \
            .get_seismicity(SeismicityQuery(**SITE))
        assert "UNAVAILABLE" in format_report_markdown(down.as_dict())


# ── API + UI integration ───────────────────────────────────────────────────

@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("LITHOS_DB_PATH", str(tmp_path / "api.db"))
    import lithic.app.config as cfg_module
    cfg_module._config = None
    from fastapi.testclient import TestClient
    from lithic.app.main import create_app
    from lithic.app.api.routes import get_seismicity_adapter
    app = create_app()
    holder = {}

    def _use(fetch, clock=None, **kw):
        adapter = USGSSeismicityAdapter(tmp_path / "seis.db", fetch_fn=fetch, now_fn=clock or Clock(), **kw)
        app.dependency_overrides[get_seismicity_adapter] = lambda: adapter
        return adapter

    holder["use"] = _use
    with TestClient(app) as c:
        holder["client"] = c
        yield holder
    cfg_module._config = None


class TestSeismicityAPI:
    def test_live_response(self, api):
        api["use"](FakeFetch([_payload()]))
        r = api["client"].get("/api/v1/field/seismicity", params={"lat": 38.79, "lon": -122.76, "radius_km": 50})
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "live" and len(d["events"]) == 3
        assert d["provenance"]["source_url"].startswith(us.SOURCE_ENDPOINT)
        assert d["query"]["radius_km"] == 50

    def test_unavailable_still_200_with_status(self, api):
        api["use"](FakeFetch([urllib.error.URLError("down")]))
        d = api["client"].get("/api/v1/field/seismicity", params={"lat": 0, "lon": 0}).json()
        assert d["status"] == "unavailable" and d["events"] == []

    def test_stale_then_refresh(self, api):
        clock = Clock()
        fetch = FakeFetch([_payload(), urllib.error.URLError("down")])
        api["use"](fetch, clock)
        c = api["client"]
        assert c.get("/api/v1/field/seismicity", params={"lat": 38.79, "lon": -122.76}).json()["status"] == "live"
        clock.t = NOW + timedelta(hours=2)
        d = c.get("/api/v1/field/seismicity", params={"lat": 38.79, "lon": -122.76, "refresh": True}).json()
        assert d["status"] == "stale" and "unreachable" in d["error"]

    @pytest.mark.parametrize("params", [
        {"lat": 95, "lon": 0}, {"lat": 0, "lon": 0, "days": 365},
        {"lat": 0, "lon": 0, "radius_km": 5000}, {"lon": 0},
    ])
    def test_invalid_params_422(self, api, params):
        fetch = FakeFetch([_payload()])
        api["use"](fetch)
        assert api["client"].get("/api/v1/field/seismicity", params=params).status_code == 422
        assert fetch.calls == []


class TestUIHandler:
    def test_ui_handler_live(self, tmp_path):
        from lithic.app.pc.gradio_ui import run_seismicity_query
        a = _adapter(tmp_path, FakeFetch([_payload()]))
        md, data = run_seismicity_query(38.79, -122.76, 50, 30, 1.0, adapter=a)
        assert "LIVE" in md and data["status"] == "live"

    def test_ui_handler_invalid_input(self, tmp_path):
        from lithic.app.pc.gradio_ui import run_seismicity_query
        md, data = run_seismicity_query(200, 0, 50, 30, 1.0, adapter=_adapter(tmp_path, FakeFetch([_payload()])))
        assert "Invalid query" in md and data == {}
