# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Standalone product tests for the UM Geophysical Monitor."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT))

from geo_monitor.app.server import UIRequestHandler, ui_directory
from geo_monitor.engine.feeds import EONETFeedParser, USGSFeedParser, get_combined_events
from geo_monitor.engine.overlay import compute_overlay, format_result_json, summary_stats
from geo_monitor.engine.physics import (
    BASIN_DEPTH,
    BASIN_WIDTH_RAD,
    BRAIDED_SOUND_SPEED,
    DISASTER_KINDS,
    HURRICANE_ENERGY_PER_CATEGORY_J,
    JOULES_PER_RICHTER_UNIT,
    K_CS,
    PHI_DEBT_ALIGNMENT_FLOOR,
    PHI_DEBT_DECAY_RATE,
    PHI_0,
    PLANCK_ENERGY_J,
    RADION_COUPLING_ALPHA,
    RADION_DELTA_PHI_PER_M5,
    RADION_QCD_SUPPRESSION,
    RICHTER_REF_ENERGY_J,
    WILDFIRE_ENERGY_PER_HA_J,
    WINDING_NUMBER,
    GeoEvent,
    UMGeoOverlay,
    UMOverlayResult,
    analyse_event_batch,
    parse_eonet_event,
    parse_usgs_feature,
)
from run import SAMPLE_EVENTS, build_parser


class MockHTTPResponse:
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TestConstants:
    def test_winding_number(self):
        assert WINDING_NUMBER == 5

    def test_k_cs_value(self):
        assert K_CS == 74
        assert K_CS == 5 ** 2 + 7 ** 2

    def test_braided_sound_speed(self):
        assert abs(BRAIDED_SOUND_SPEED - 12 / 37) < 1e-12

    def test_phi_0_normalised(self):
        assert PHI_0 == 1.0

    def test_radion_coupling_alpha(self):
        expected = abs(RADION_DELTA_PHI_PER_M5) / K_CS
        assert abs(RADION_COUPLING_ALPHA - expected) < 1e-12

    def test_basin_depth(self):
        expected = WINDING_NUMBER ** 2 / K_CS
        assert abs(BASIN_DEPTH - expected) < 1e-12

    def test_basin_width_rad(self):
        assert abs(BASIN_WIDTH_RAD - (2 * math.pi / WINDING_NUMBER)) < 1e-12

    def test_phi_debt_alignment_floor_positive(self):
        assert 0 < PHI_DEBT_ALIGNMENT_FLOOR < 1

    def test_phi_debt_decay_rate_positive(self):
        assert PHI_DEBT_DECAY_RATE > 0

    def test_radion_qcd_suppression_magnitude(self):
        assert RADION_QCD_SUPPRESSION == 1e7

    def test_planck_energy_order(self):
        assert 1e8 < PLANCK_ENERGY_J < 1e11

    def test_joules_per_richter_unit(self):
        assert JOULES_PER_RICHTER_UNIT == 10 ** 1.5

    def test_richter_reference_energy(self):
        assert RICHTER_REF_ENERGY_J == 10 ** 4.8

    def test_wildfire_energy_per_hectare(self):
        assert WILDFIRE_ENERGY_PER_HA_J == 8.0e10

    def test_hurricane_energy_per_category(self):
        assert HURRICANE_ENERGY_PER_CATEGORY_J == 5.0e18

    def test_disaster_kinds_count(self):
        assert len(DISASTER_KINDS) == 10

    def test_disaster_kinds_contains_expected(self):
        for kind in ["earthquake", "wildfire", "hurricane", "storm", "volcano"]:
            assert kind in DISASTER_KINDS


class TestGeoEvent:
    def _make(self, **kw):
        defaults = dict(kind="earthquake", magnitude=6.0, lat=35.0, lon=140.0)
        defaults.update(kw)
        return GeoEvent(**defaults)

    def test_basic_construction(self):
        ev = self._make()
        assert ev.kind == "earthquake"
        assert ev.magnitude == 6.0

    def test_validate_valid(self):
        self._make().validate()

    def test_validate_bad_kind(self):
        with pytest.raises(ValueError, match="Unknown disaster kind"):
            self._make(kind="asteroid").validate()

    @pytest.mark.parametrize("lat", [91.0, -91.0])
    def test_validate_bad_lat(self, lat):
        with pytest.raises(ValueError, match="lat"):
            self._make(lat=lat).validate()

    @pytest.mark.parametrize("lon", [181.0, -181.0])
    def test_validate_bad_lon(self, lon):
        with pytest.raises(ValueError, match="lon"):
            self._make(lon=lon).validate()

    def test_validate_case_insensitive_kind(self):
        GeoEvent(kind="Earthquake", magnitude=6.0, lat=0.0, lon=0.0).validate()

    def test_energy_si_override(self):
        ev = self._make(energy_J=1e15)
        assert ev.energy_si == 1e15

    def test_energy_si_earthquake_gutenberg(self):
        ev = self._make(kind="earthquake", magnitude=6.0)
        expected = 10 ** (1.5 * 6.0 + 4.8)
        assert abs(ev.energy_si - expected) / expected < 1e-9

    def test_energy_si_wildfire_with_area(self):
        ev = self._make(kind="wildfire", magnitude=5.0, area_ha=1000)
        expected = 1000 * WILDFIRE_ENERGY_PER_HA_J
        assert abs(ev.energy_si - expected) / expected < 1e-9

    def test_energy_si_wildfire_default_area_proxy(self):
        ev = self._make(kind="wildfire", magnitude=5.0)
        expected = (10 ** (5.0 - 1)) * WILDFIRE_ENERGY_PER_HA_J
        assert abs(ev.energy_si - expected) / expected < 1e-9

    @pytest.mark.parametrize("kind", ["hurricane", "tornado", "storm"])
    def test_energy_si_storm_family(self, kind):
        ev = self._make(kind=kind, magnitude=4.0)
        assert ev.energy_si == HURRICANE_ENERGY_PER_CATEGORY_J * 16

    def test_energy_si_tsunami_formula(self):
        ev = self._make(kind="tsunami", magnitude=7.0)
        expected = 10 ** (1.5 * 7.0 + 4.8)
        assert abs(ev.energy_si - expected) / expected < 1e-9

    def test_energy_si_volcano(self):
        ev = self._make(kind="volcano", magnitude=3.0)
        assert ev.energy_si == 10 ** (3 * 3.0 + 10)

    def test_energy_si_generic_branch(self):
        ev = self._make(kind="drought", magnitude=2.0)
        expected = 10 ** (1.5 * 2.0 + 4.8)
        assert abs(ev.energy_si - expected) / expected < 1e-9

    def test_energy_planck_dimensionless(self):
        ev = self._make()
        assert isinstance(ev.energy_planck, float)
        assert ev.energy_planck > 0

    def test_energy_planck_eq_energy_si_over_planck(self):
        ev = self._make()
        assert abs(ev.energy_planck - ev.energy_si / PLANCK_ENERGY_J) < 1e-20

    def test_all_disaster_kinds_return_positive_energy(self):
        for kind in DISASTER_KINDS:
            ev = GeoEvent(kind=kind, magnitude=5.0, lat=0.0, lon=0.0)
            assert ev.energy_si > 0


class TestUMGeoOverlay:
    def setup_method(self):
        self.overlay = UMGeoOverlay()

    def _quake(self, mag=6.0, lat=35.0, lon=140.0, depth=30.0):
        return GeoEvent("earthquake", mag, lat, lon, depth_km=depth)

    def test_returns_overlay_result(self):
        assert isinstance(self.overlay.analyse(self._quake()), UMOverlayResult)

    def test_event_reference_preserved(self):
        ev = self._quake()
        assert self.overlay.analyse(ev).event is ev

    def test_phi_debt_injection_positive(self):
        assert self.overlay.analyse(self._quake(mag=7.0)).phi_debt_injection > 0

    def test_phi_alignment_in_range(self):
        r = self.overlay.analyse(self._quake())
        assert PHI_DEBT_ALIGNMENT_FLOOR <= r.phi_alignment <= 1.0

    def test_phi_alignment_floor_respected(self):
        r = self.overlay.analyse(GeoEvent("earthquake", 10.0, 0.0, 0.0))
        assert r.phi_alignment >= PHI_DEBT_ALIGNMENT_FLOOR

    def test_radion_amplitude_positive(self):
        assert self.overlay.analyse(self._quake()).radion_amplitude > 0

    def test_radion_suppression_bounded(self):
        assert self.overlay.analyse(self._quake()).radion_suppression_factor <= RADION_QCD_SUPPRESSION

    def test_radion_suppression_at_least_one(self):
        assert self.overlay.analyse(self._quake()).radion_suppression_factor >= 1.0

    def test_winding_stability_in_range(self):
        r = self.overlay.analyse(self._quake())
        assert 0.0 <= r.winding_stability <= 1.0

    def test_basin_perturbation_positive(self):
        assert self.overlay.analyse(self._quake()).basin_perturbation >= 0.0

    def test_w_a_local_negative_for_quake(self):
        assert self.overlay.analyse(self._quake()).w_a_local <= 0

    def test_larger_magnitude_higher_phi_debt(self):
        r5 = self.overlay.analyse(self._quake(mag=5.0))
        r8 = self.overlay.analyse(self._quake(mag=8.0))
        assert r8.phi_debt_injection > r5.phi_debt_injection

    def test_larger_magnitude_higher_radion_amplitude(self):
        r5 = self.overlay.analyse(self._quake(mag=5.0))
        r8 = self.overlay.analyse(self._quake(mag=8.0))
        assert r8.radion_amplitude > r5.radion_amplitude

    def test_deeper_earthquake_smaller_radion_amplitude(self):
        r_shallow = self.overlay.analyse(self._quake(depth=10.0))
        r_deep = self.overlay.analyse(self._quake(depth=600.0))
        assert r_deep.radion_amplitude < r_shallow.radion_amplitude

    def test_epistemic_label_present(self):
        assert "ADJACENT TRACK" in self.overlay.analyse(self._quake()).epistemic_label

    def test_pillar_sources_present(self):
        r = self.overlay.analyse(self._quake())
        for pillar in ["P806", "P786", "P16", "P808", "P22"]:
            assert pillar in r.pillar_sources

    def test_summary_non_empty(self):
        assert len(self.overlay.analyse(self._quake()).summary) > 20

    def test_summary_contains_magnitude(self):
        assert "7.5" in self.overlay.analyse(self._quake(mag=7.5)).summary

    def test_confidence_low_for_tiny_energy(self):
        ev = GeoEvent("earthquake", 1.0, 0.0, 0.0, energy_J=1e-12)
        assert self.overlay.analyse(ev).confidence == "LOW"

    def test_confidence_high_for_large_energy(self):
        ev = GeoEvent("earthquake", 9.5, 0.0, 0.0)
        assert self.overlay.analyse(ev).confidence == "HIGH"

    @pytest.mark.parametrize("kind", sorted(DISASTER_KINDS))
    def test_analysis_for_each_disaster_type(self, kind):
        ev = GeoEvent(kind, 5.0, 10.0, 20.0)
        r = self.overlay.analyse(ev)
        assert isinstance(r, UMOverlayResult)
        assert r.epistemic_label

    def test_analyse_raises_on_bad_event(self):
        with pytest.raises(ValueError):
            self.overlay.analyse(GeoEvent("asteroid", 5.0, 0.0, 0.0))

    def test_phi_debt_formula_manual(self):
        ev = GeoEvent("earthquake", 6.0, 0.0, 0.0, energy_J=1e15)
        r = self.overlay.analyse(ev)
        expected = ev.energy_planck * (1.0 - math.exp(-PHI_DEBT_DECAY_RATE * math.log10(ev.energy_si)))
        assert abs(r.phi_debt_injection - expected) < 1e-30

    def test_basin_perturbation_matches_ratio(self):
        ev = self._quake()
        r = self.overlay.analyse(ev)
        assert abs(r.basin_perturbation - r.radion_amplitude / BASIN_DEPTH) < 1e-12

    def test_stability_one_minus_perturbation_for_small_events(self):
        r = self.overlay.analyse(GeoEvent("earthquake", 3.0, 0.0, 0.0))
        if r.basin_perturbation < 1:
            assert abs(r.winding_stability - (1.0 - r.basin_perturbation)) < 1e-12


class TestBatchAnalysis:
    def test_batch_returns_list(self):
        events = [GeoEvent("earthquake", 6.0, 35.0, 140.0), GeoEvent("wildfire", 5.0, 34.0, -118.0)]
        results = analyse_event_batch(events)
        assert isinstance(results, list)
        assert len(results) == 2

    def test_batch_empty_list(self):
        assert analyse_event_batch([]) == []

    def test_batch_all_have_overlay_result_type(self):
        events = [GeoEvent(k, 5.0, 0.0, 0.0) for k in ["earthquake", "wildfire", "hurricane", "volcano"]]
        assert all(isinstance(r, UMOverlayResult) for r in analyse_event_batch(events))

    def test_batch_independent(self):
        events = [GeoEvent("earthquake", 5.0, i * 10.0, 0.0) for i in range(5)]
        assert [r.event.lat for r in analyse_event_batch(events)] == [0.0, 10.0, 20.0, 30.0, 40.0]


class TestParseUSGS:
    def _feature(self, mag=6.1, lon=140.1, lat=35.7, depth=30.0):
        return {
            "type": "Feature",
            "properties": {"mag": mag, "place": "Test"},
            "geometry": {"type": "Point", "coordinates": [lon, lat, depth]},
        }

    def test_parse_valid(self):
        ev = parse_usgs_feature(self._feature())
        assert ev is not None and ev.kind == "earthquake" and abs(ev.magnitude - 6.1) < 1e-9

    def test_parse_lat_lon(self):
        ev = parse_usgs_feature(self._feature(lon=120.5, lat=-25.3))
        assert abs(ev.lon - 120.5) < 1e-9 and abs(ev.lat + 25.3) < 1e-9

    def test_parse_depth(self):
        ev = parse_usgs_feature(self._feature(depth=55.0))
        assert abs(ev.depth_km - 55.0) < 1e-9

    def test_parse_missing_mag_returns_none(self):
        assert parse_usgs_feature({"properties": {}, "geometry": {"coordinates": [0, 0, 0]}}) is None

    def test_parse_empty_dict_returns_none(self):
        assert parse_usgs_feature({}) is None

    def test_parse_none_coordinates_returns_none(self):
        assert parse_usgs_feature({"properties": {"mag": 5.0}, "geometry": {"coordinates": []}}) is None

    def test_parse_large_magnitude(self):
        assert parse_usgs_feature(self._feature(mag=9.1)).magnitude == 9.1

    def test_parse_zero_depth(self):
        assert parse_usgs_feature(self._feature(depth=0.0)).depth_km == 0.0


class TestParseEONET:
    def _event(self, category_id="wildfires", lon=-118.0, lat=34.0, magnitude=None):
        payload = {
            "id": "EONET_1",
            "title": "Test Event",
            "categories": [{"id": category_id, "title": category_id}],
            "geometry": [{"coordinates": [lon, lat], "date": "2026-08-01"}],
        }
        if magnitude is not None:
            payload["magnitudeValue"] = magnitude
        return payload

    def test_parse_wildfire(self):
        assert parse_eonet_event(self._event("wildfires")).kind == "wildfire"

    def test_parse_volcano(self):
        assert parse_eonet_event(self._event("volcanoes", lon=115.2, lat=-8.3)).kind == "volcano"

    def test_parse_storm(self):
        assert parse_eonet_event(self._event("severeStorms", lon=-90.0, lat=25.0)).kind == "storm"

    def test_parse_coordinates(self):
        ev = parse_eonet_event(self._event(lon=-120.5, lat=38.2))
        assert abs(ev.lon + 120.5) < 1e-9 and abs(ev.lat - 38.2) < 1e-9

    def test_parse_empty_geometry_returns_none(self):
        assert parse_eonet_event({"categories": [{"id": "wildfires"}], "geometry": []}) is None

    def test_parse_empty_dict_returns_none(self):
        assert parse_eonet_event({}) is None

    def test_parse_default_magnitude(self):
        assert parse_eonet_event(self._event()).magnitude == 5.0

    def test_parse_explicit_magnitude(self):
        assert parse_eonet_event(self._event(magnitude=6.2)).magnitude == 6.2

    def test_parse_all_runs_overlay(self):
        ev = parse_eonet_event(self._event())
        assert UMGeoOverlay().analyse(ev).phi_debt_injection >= 0


class TestUSGSFeedParser:
    def test_feed_url_constants(self):
        assert USGSFeedParser.USGS_FEED_URL_PAST_DAY.endswith("all_day.geojson")
        assert USGSFeedParser.USGS_FEED_URL_PAST_HOUR.endswith("all_hour.geojson")

    def test_parse_geojson_with_mock_data(self):
        parser = USGSFeedParser()
        data = {
            "features": [
                {"properties": {"mag": 6.0}, "geometry": {"coordinates": [140.0, 35.0, 20.0]}},
                {"properties": {"mag": None}, "geometry": {"coordinates": [0.0, 0.0, 0.0]}},
            ]
        }
        events = parser.parse_geojson(data)
        assert len(events) == 1 and events[0].kind == "earthquake"

    def test_parse_geojson_empty(self):
        assert USGSFeedParser().parse_geojson({"features": []}) == []

    def test_fetch_parses_json(self, monkeypatch):
        monkeypatch.setattr("geo_monitor.engine.feeds.request.urlopen", lambda url, timeout=20: MockHTTPResponse({"features": []}))
        assert USGSFeedParser().fetch("https://example.com")["features"] == []


class TestEONETFeedParser:
    def test_api_url_constant(self):
        assert EONETFeedParser.EONET_API_URL.startswith("https://eonet.gsfc.nasa.gov")

    def test_parse_events_with_mock_data(self):
        parser = EONETFeedParser()
        data = {
            "events": [
                {"categories": [{"id": "wildfires"}], "geometry": [{"coordinates": [-118.0, 34.0]}]},
                {"categories": [{"id": "volcanoes"}], "geometry": [{"coordinates": [115.2, -8.3]}]},
                {"categories": [{"id": "wildfires"}], "geometry": []},
            ]
        }
        events = parser.parse_events(data)
        assert [event.kind for event in events] == ["wildfire", "volcano"]

    def test_parse_events_empty(self):
        assert EONETFeedParser().parse_events({"events": []}) == []

    def test_fetch_builds_query_and_parses_json(self, monkeypatch):
        seen = {}

        def fake_urlopen(url, timeout=20):
            seen["url"] = url
            return MockHTTPResponse({"events": []})

        monkeypatch.setattr("geo_monitor.engine.feeds.request.urlopen", fake_urlopen)
        payload = EONETFeedParser().fetch(limit=12, days=3)
        assert payload["events"] == []
        assert "limit=12" in seen["url"]
        assert "days=3" in seen["url"]


class TestCombinedEvents:
    def test_get_combined_events_with_mock_data(self):
        data = {
            "usgs": {"features": [{"properties": {"mag": 6.5}, "geometry": {"coordinates": [140.0, 35.0, 10.0]}}]},
            "eonet": {"events": [{"categories": [{"id": "wildfires"}], "geometry": [{"coordinates": [-118.0, 34.0]}]}]},
        }
        events = get_combined_events(mock_data=data)
        assert len(events) == 2
        assert {event.kind for event in events} == {"earthquake", "wildfire"}

    def test_get_combined_events_with_partial_mock_data(self):
        events = get_combined_events(mock_data={"usgs": {"features": []}})
        assert events == []

    def test_get_combined_events_without_mock_uses_fetchers(self, monkeypatch):
        monkeypatch.setattr(USGSFeedParser, "fetch", lambda self, url: {"features": [{"properties": {"mag": 5.0}, "geometry": {"coordinates": [0.0, 0.0, 5.0]}}]})
        monkeypatch.setattr(EONETFeedParser, "fetch", lambda self, limit=50, days=7: {"events": [{"categories": [{"id": "volcanoes"}], "geometry": [{"coordinates": [10.0, 20.0]}]}]})
        events = get_combined_events()
        assert len(events) == 2


class TestOverlayHelpers:
    def test_format_result_json_returns_dict(self):
        result = UMGeoOverlay().analyse(GeoEvent("earthquake", 6.0, 35.0, 140.0))
        payload = format_result_json(result)
        assert isinstance(payload, dict)
        for key in ["kind", "event", "phi_debt_injection", "winding_stability", "epistemic_label"]:
            assert key in payload

    def test_format_result_json_is_json_serializable(self):
        result = UMGeoOverlay().analyse(GeoEvent("wildfire", 5.0, 34.0, -118.0, area_ha=50))
        text = json.dumps(format_result_json(result), sort_keys=True)
        assert "wildfire" in text

    def test_compute_overlay_returns_list_of_dicts(self):
        payload = compute_overlay(SAMPLE_EVENTS[:2])
        assert isinstance(payload, list)
        assert len(payload) == 2
        assert all(isinstance(item, dict) for item in payload)

    def test_compute_overlay_includes_event_metadata(self):
        payload = compute_overlay([GeoEvent("earthquake", 6.0, 35.0, 140.0)])[0]
        assert payload["kind"] == "earthquake"
        assert payload["lat"] == 35.0
        assert payload["lon"] == 140.0

    def test_summary_stats_empty(self):
        stats = summary_stats([])
        assert stats == {"total": 0, "by_kind": {}, "avg_phi_debt": 0.0, "avg_winding_stability": 0.0, "high_severity_count": 0}

    def test_summary_stats_aggregate(self):
        results = compute_overlay([
            GeoEvent("earthquake", 6.0, 35.0, 140.0),
            GeoEvent("wildfire", 5.0, 34.0, -118.0, area_ha=10),
            GeoEvent("wildfire", 6.0, 33.0, -117.0, area_ha=20),
        ])
        stats = summary_stats(results)
        assert stats["total"] == 3
        assert stats["by_kind"]["wildfire"] == 2
        assert stats["avg_phi_debt"] > 0
        assert 0 <= stats["avg_winding_stability"] <= 1

    def test_summary_stats_high_severity_count(self):
        results = compute_overlay([GeoEvent("earthquake", 9.4, 10.0, 10.0), GeoEvent("earthquake", 3.0, 0.0, 0.0)])
        stats = summary_stats(results)
        assert stats["high_severity_count"] >= 1


class TestServerAndArtifacts:
    def test_ui_directory_exists(self):
        assert ui_directory().is_dir()

    def test_ui_handler_type(self):
        assert issubclass(UIRequestHandler, object)

    def test_ui_index_exists(self):
        assert (PRODUCT_ROOT / "ui" / "index.html").is_file()

    def test_ui_js_exists(self):
        assert (PRODUCT_ROOT / "ui" / "geo-monitor.js").is_file()

    def test_run_py_exists(self):
        assert (PRODUCT_ROOT / "run.py").is_file()

    def test_readme_is_large_enough(self):
        readme = (PRODUCT_ROOT / "README.md").read_text(encoding="utf-8")
        assert len(readme) >= 1000
        assert len(readme.splitlines()) >= 600


class TestRunCLI:
    def test_build_parser_defaults(self):
        args = build_parser().parse_args(["serve"])
        assert args.port == 8021

    def test_build_parser_analyse(self):
        args = build_parser().parse_args(["analyse", "--kind", "earthquake", "--magnitude", "7.4", "--lat", "35.7", "--lon", "140.1"])
        assert args.kind == "earthquake"
        assert args.magnitude == 7.4

    def test_analyse_subprocess(self):
        proc = subprocess.run(
            [sys.executable, "run.py", "analyse", "--kind", "earthquake", "--magnitude", "7.4", "--lat", "35.7", "--lon", "140.1"],
            cwd=PRODUCT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(proc.stdout)
        assert payload["kind"] == "earthquake"
        assert "epistemic_label" in payload

    def test_demo_subprocess(self):
        proc = subprocess.run(
            [sys.executable, "run.py", "demo"],
            cwd=PRODUCT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(proc.stdout)
        assert len(payload["results"]) == 5
        assert payload["summary"]["total"] == 5
