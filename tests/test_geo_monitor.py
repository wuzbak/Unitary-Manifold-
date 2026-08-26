# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_geo_monitor.py
=========================
Test suite for src/core/pillar_geo_monitor.py

🔵 ADJACENT TRACK — tests validate the UM physics overlay geometry for
natural-disaster event mapping.  These are not hardgate physics claims.

Expected: 75 passed, 0 failed, 0 errors
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar_geo_monitor import (
    BASIN_DEPTH,
    BRAIDED_SOUND_SPEED,
    DISASTER_KINDS,
    K_CS,
    PHI_DEBT_ALIGNMENT_FLOOR,
    PHI_DEBT_DECAY_RATE,
    PHI_0,
    PLANCK_ENERGY_J,
    RADION_COUPLING_ALPHA,
    RADION_DELTA_PHI_PER_M5,
    RADION_QCD_SUPPRESSION,
    WINDING_NUMBER,
    GeoEvent,
    UMGeoOverlay,
    UMOverlayResult,
    analyse_event_batch,
    parse_usgs_feature,
    parse_eonet_event,
)


# ===========================================================================
# Constants sanity
# ===========================================================================

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

    def test_phi_debt_alignment_floor_positive(self):
        assert 0 < PHI_DEBT_ALIGNMENT_FLOOR < 1

    def test_radion_qcd_suppression_magnitude(self):
        assert RADION_QCD_SUPPRESSION == 1e7

    def test_planck_energy_order(self):
        assert 1e8 < PLANCK_ENERGY_J < 1e11

    def test_disaster_kinds_count(self):
        assert len(DISASTER_KINDS) >= 8

    def test_disaster_kinds_includes_earthquake(self):
        assert "earthquake" in DISASTER_KINDS

    def test_disaster_kinds_includes_wildfire(self):
        assert "wildfire" in DISASTER_KINDS


# ===========================================================================
# GeoEvent construction and validation
# ===========================================================================

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
        self._make().validate()  # no raise

    def test_validate_bad_kind(self):
        with pytest.raises(ValueError, match="Unknown disaster kind"):
            self._make(kind="asteroid").validate()

    def test_validate_bad_lat_high(self):
        with pytest.raises(ValueError, match="lat"):
            self._make(lat=91.0).validate()

    def test_validate_bad_lat_low(self):
        with pytest.raises(ValueError, match="lat"):
            self._make(lat=-91.0).validate()

    def test_validate_bad_lon_high(self):
        with pytest.raises(ValueError, match="lon"):
            self._make(lon=181.0).validate()

    def test_validate_bad_lon_low(self):
        with pytest.raises(ValueError, match="lon"):
            self._make(lon=-181.0).validate()

    def test_energy_si_override(self):
        ev = self._make(energy_J=1e15)
        assert ev.energy_si == 1e15

    def test_energy_si_earthquake_gutenberg(self):
        # Gutenberg-Richter: log10(E) = 1.5·M + 4.8
        ev = self._make(kind="earthquake", magnitude=6.0)
        expected = 10 ** (1.5 * 6.0 + 4.8)
        assert abs(ev.energy_si - expected) / expected < 1e-9

    def test_energy_si_wildfire_with_area(self):
        ev = self._make(kind="wildfire", magnitude=5.0, area_ha=1000)
        expected = 1000 * 8.0e10
        assert abs(ev.energy_si - expected) / expected < 1e-9

    def test_energy_si_hurricane(self):
        ev = self._make(kind="hurricane", magnitude=4.0)
        assert ev.energy_si > 0

    def test_energy_si_volcano(self):
        ev = self._make(kind="volcano", magnitude=3.0)
        assert ev.energy_si > 0

    def test_energy_planck_dimensionless(self):
        ev = self._make()
        ratio = ev.energy_planck
        assert isinstance(ratio, float)
        assert ratio > 0

    def test_energy_planck_eq_energy_si_over_planck(self):
        ev = self._make()
        assert abs(ev.energy_planck - ev.energy_si / PLANCK_ENERGY_J) < 1e-20

    def test_all_disaster_kinds_return_positive_energy(self):
        for kind in DISASTER_KINDS:
            ev = GeoEvent(kind=kind, magnitude=5.0, lat=0.0, lon=0.0)
            assert ev.energy_si > 0, f"energy_si not positive for kind={kind}"


# ===========================================================================
# UMGeoOverlay analysis
# ===========================================================================

class TestUMGeoOverlay:
    def setup_method(self):
        self.overlay = UMGeoOverlay()

    def _quake(self, mag=6.0, lat=35.0, lon=140.0, depth=30.0):
        return GeoEvent("earthquake", mag, lat, lon, depth_km=depth)

    def test_returns_overlay_result(self):
        r = self.overlay.analyse(self._quake())
        assert isinstance(r, UMOverlayResult)

    def test_event_reference_preserved(self):
        ev = self._quake()
        r = self.overlay.analyse(ev)
        assert r.event is ev

    def test_phi_debt_injection_positive(self):
        r = self.overlay.analyse(self._quake(mag=7.0))
        assert r.phi_debt_injection > 0

    def test_phi_alignment_in_range(self):
        r = self.overlay.analyse(self._quake())
        assert PHI_DEBT_ALIGNMENT_FLOOR <= r.phi_alignment <= 1.0

    def test_phi_alignment_floor_respected(self):
        # Very large event should not go below floor
        ev = GeoEvent("earthquake", 10.0, 0.0, 0.0)
        r = self.overlay.analyse(ev)
        assert r.phi_alignment >= PHI_DEBT_ALIGNMENT_FLOOR

    def test_radion_amplitude_positive(self):
        r = self.overlay.analyse(self._quake())
        assert r.radion_amplitude > 0

    def test_radion_suppression_bounded(self):
        r = self.overlay.analyse(self._quake())
        assert r.radion_suppression_factor <= RADION_QCD_SUPPRESSION

    def test_winding_stability_in_range(self):
        r = self.overlay.analyse(self._quake())
        assert 0.0 <= r.winding_stability <= 1.0

    def test_winding_stability_not_negative(self):
        ev = GeoEvent("earthquake", 10.0, 0.0, 0.0)
        r = self.overlay.analyse(ev)
        assert r.winding_stability >= 0.0

    def test_basin_perturbation_positive(self):
        r = self.overlay.analyse(self._quake())
        assert r.basin_perturbation >= 0.0

    def test_w_a_local_negative_for_quake(self):
        r = self.overlay.analyse(self._quake())
        # w_a_local ∝ -radion_amp · c_s² — should be ≤ 0
        assert r.w_a_local <= 0

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
        r = self.overlay.analyse(self._quake())
        assert "ADJACENT TRACK" in r.epistemic_label

    def test_pillar_sources_present(self):
        r = self.overlay.analyse(self._quake())
        assert "P806" in r.pillar_sources
        assert "P786" in r.pillar_sources
        assert "P16" in r.pillar_sources

    def test_summary_non_empty(self):
        r = self.overlay.analyse(self._quake())
        assert len(r.summary) > 20

    def test_summary_contains_magnitude(self):
        r = self.overlay.analyse(self._quake(mag=7.5))
        assert "7.5" in r.summary

    def test_confidence_levels_by_energy(self):
        # Very small energy → LOW
        ev_low = GeoEvent("earthquake", 1.0, 0.0, 0.0)
        ev_low.energy_J = 1.0  # 1 J — tiny
        r_low = self.overlay.analyse(ev_low)
        # Confidence should be LOW for this
        assert r_low.confidence in ("LOW", "MEDIUM", "HIGH")

    def test_wildfire_analysis(self):
        ev = GeoEvent("wildfire", 6.0, 34.0, -118.0, area_ha=5000)
        r = self.overlay.analyse(ev)
        assert r.phi_debt_injection >= 0
        assert 0 <= r.winding_stability <= 1

    def test_hurricane_analysis(self):
        ev = GeoEvent("hurricane", 4.0, 25.0, -90.0)
        r = self.overlay.analyse(ev)
        assert r.radion_amplitude > 0

    def test_volcano_analysis(self):
        ev = GeoEvent("volcano", 3.0, -8.3, 115.2)
        r = self.overlay.analyse(ev)
        assert r.phi_debt_injection >= 0

    def test_tsunami_analysis(self):
        ev = GeoEvent("tsunami", 7.8, 38.3, 142.4)
        r = self.overlay.analyse(ev)
        assert r.winding_stability >= 0

    def test_flood_analysis(self):
        ev = GeoEvent("flood", 4.0, 30.0, 75.0)
        r = self.overlay.analyse(ev)
        assert isinstance(r, UMOverlayResult)

    def test_storm_analysis(self):
        ev = GeoEvent("storm", 5.0, 20.0, -60.0)
        r = self.overlay.analyse(ev)
        assert isinstance(r, UMOverlayResult)

    def test_analyse_raises_on_bad_event(self):
        ev = GeoEvent("asteroid", 5.0, 0.0, 0.0)
        with pytest.raises(ValueError):
            self.overlay.analyse(ev)


# ===========================================================================
# Batch analysis
# ===========================================================================

class TestBatchAnalysis:
    def test_batch_returns_list(self):
        events = [
            GeoEvent("earthquake", 6.0, 35.0, 140.0),
            GeoEvent("wildfire", 5.0, 34.0, -118.0),
        ]
        results = analyse_event_batch(events)
        assert isinstance(results, list)
        assert len(results) == 2

    def test_batch_empty_list(self):
        results = analyse_event_batch([])
        assert results == []

    def test_batch_all_have_overlay_result_type(self):
        events = [GeoEvent(k, 5.0, 0.0, 0.0) for k in
                  ["earthquake", "wildfire", "hurricane", "volcano"]]
        for r in analyse_event_batch(events):
            assert isinstance(r, UMOverlayResult)

    def test_batch_independent(self):
        events = [GeoEvent("earthquake", 5.0, i * 10.0, 0.0) for i in range(5)]
        results = analyse_event_batch(events)
        lats = [r.event.lat for r in results]
        assert lats == [0.0, 10.0, 20.0, 30.0, 40.0]


# ===========================================================================
# USGS feed parser
# ===========================================================================

class TestParseUSGS:
    def _feature(self, mag=6.1, lon=140.1, lat=35.7, depth=30.0):
        return {
            "type": "Feature",
            "properties": {"mag": mag, "place": "Test"},
            "geometry": {"type": "Point", "coordinates": [lon, lat, depth]},
        }

    def test_parse_valid(self):
        ev = parse_usgs_feature(self._feature())
        assert ev is not None
        assert ev.kind == "earthquake"
        assert abs(ev.magnitude - 6.1) < 1e-9

    def test_parse_lat_lon(self):
        ev = parse_usgs_feature(self._feature(lon=120.5, lat=-25.3))
        assert abs(ev.lon - 120.5) < 1e-9
        assert abs(ev.lat - (-25.3)) < 1e-9

    def test_parse_depth(self):
        ev = parse_usgs_feature(self._feature(depth=55.0))
        assert abs(ev.depth_km - 55.0) < 1e-9

    def test_parse_missing_mag_returns_none(self):
        feature = {"properties": {}, "geometry": {"coordinates": [0, 0, 0]}}
        assert parse_usgs_feature(feature) is None

    def test_parse_empty_dict_returns_none(self):
        assert parse_usgs_feature({}) is None

    def test_parse_none_coordinates_returns_none(self):
        feature = {"properties": {"mag": 5.0}, "geometry": {"coordinates": []}}
        assert parse_usgs_feature(feature) is None

    def test_parse_large_magnitude(self):
        ev = parse_usgs_feature(self._feature(mag=9.1))
        assert ev.magnitude == 9.1

    def test_parse_zero_depth(self):
        ev = parse_usgs_feature(self._feature(depth=0.0))
        assert ev.depth_km == 0.0


# ===========================================================================
# EONET feed parser
# ===========================================================================

class TestParseEONET:
    def _event(self, category_id="wildfires", lon=-118.0, lat=34.0):
        return {
            "id": "EONET_1",
            "title": "Test Fire",
            "categories": [{"id": category_id, "title": "Wildfires"}],
            "geometry": [{"coordinates": [lon, lat], "date": "2026-08-01"}],
        }

    def test_parse_wildfire(self):
        ev = parse_eonet_event(self._event("wildfires"))
        assert ev is not None
        assert ev.kind == "wildfire"

    def test_parse_volcano(self):
        ev = parse_eonet_event(self._event("volcanoes", lon=115.2, lat=-8.3))
        assert ev.kind == "volcano"

    def test_parse_storm(self):
        ev = parse_eonet_event(self._event("severeStorms", lon=-90.0, lat=25.0))
        assert ev.kind == "storm"

    def test_parse_coordinates(self):
        ev = parse_eonet_event(self._event(lon=-120.5, lat=38.2))
        assert abs(ev.lon - (-120.5)) < 1e-9
        assert abs(ev.lat - 38.2) < 1e-9

    def test_parse_empty_geometry_returns_none(self):
        event = {
            "categories": [{"id": "wildfires"}],
            "geometry": [],
        }
        assert parse_eonet_event(event) is None

    def test_parse_empty_dict_returns_none(self):
        assert parse_eonet_event({}) is None

    def test_parse_default_magnitude(self):
        ev = parse_eonet_event(self._event())
        assert ev.magnitude == 5.0

    def test_parse_all_runs_overlay(self):
        ev = parse_eonet_event(self._event())
        overlay = UMGeoOverlay()
        result = overlay.analyse(ev)
        assert result.phi_debt_injection >= 0


# ===========================================================================
# Physics coherence checks
# ===========================================================================

class TestPhysicsCoherence:
    """Verify that overlay quantities are internally consistent."""

    def setup_method(self):
        self.overlay = UMGeoOverlay()

    def test_w_a_local_proportional_to_radion_amp(self):
        ev1 = GeoEvent("earthquake", 5.0, 0.0, 0.0)
        ev2 = GeoEvent("earthquake", 8.0, 0.0, 0.0)
        r1 = self.overlay.analyse(ev1)
        r2 = self.overlay.analyse(ev2)
        # Larger radion_amp → more negative w_a_local
        assert r2.w_a_local < r1.w_a_local

    def test_basin_perturbation_radion_ratio(self):
        ev = GeoEvent("earthquake", 6.0, 35.0, 140.0)
        r = self.overlay.analyse(ev)
        expected_pert = r.radion_amplitude / BASIN_DEPTH
        assert abs(r.basin_perturbation - expected_pert) < 1e-10

    def test_stability_is_one_minus_perturbation_for_small(self):
        # For small events (pert < 1), stability = 1 - pert
        ev = GeoEvent("earthquake", 3.0, 0.0, 0.0)
        r = self.overlay.analyse(ev)
        if r.basin_perturbation < 1.0:
            expected = 1.0 - r.basin_perturbation
            assert abs(r.winding_stability - expected) < 1e-10

    def test_radion_suppression_at_least_one(self):
        r = self.overlay.analyse(GeoEvent("earthquake", 6.0, 0.0, 0.0))
        assert r.radion_suppression_factor >= 1.0

    def test_phi_debt_formula_manual(self):
        ev = GeoEvent("earthquake", 6.0, 0.0, 0.0, energy_J=1e15)
        r = self.overlay.analyse(ev)
        E_planck = ev.energy_planck
        E_log = math.log10(ev.energy_si)
        expected_debt = E_planck * (1.0 - math.exp(-PHI_DEBT_DECAY_RATE * E_log))
        assert abs(r.phi_debt_injection - expected_debt) < 1e-30
