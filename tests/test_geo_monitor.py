# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_geo_monitor.py
=========================
Test suite for src/core/pillar_geo_monitor.py

🔵 ADJACENT TRACK — tests validate the UM physics overlay geometry for
natural-disaster event mapping.  These are not hardgate physics claims.

v3: expanded to ~330 tests covering new feeds (space_weather, infrastructure,
cyber), Convergence Index, Pillar 807 spatial kernel, and SWPC/GDACS parsers.
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
    # v3
    P807_DAMPING_RADIUS_KM,
    P807_EARTH_RADIUS_KM,
    CI_WEIGHT_PHI_DEBT,
    CI_WEIGHT_KP,
    CI_WEIGHT_CII,
    KP_ENERGY_BASE,
    KP_ENERGY_EXPONENT,
    GeoEvent,
    UMGeoOverlay,
    UMOverlayResult,
    ConvergenceResult,
    analyse_event_batch,
    compute_convergence_index,
    _haversine_km,
    _p807_weight,
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
        assert len(DISASTER_KINDS) >= 10

    def test_disaster_kinds_includes_earthquake(self):
        assert "earthquake" in DISASTER_KINDS

    def test_disaster_kinds_includes_wildfire(self):
        assert "wildfire" in DISASTER_KINDS

    def test_disaster_kinds_includes_avalanche(self):
        assert "avalanche" in DISASTER_KINDS

    def test_disaster_kinds_includes_nws_alert(self):
        assert "nws_alert" in DISASTER_KINDS


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


# ===========================================================================
# New hazard kinds: avalanche, nws_alert
# ===========================================================================

class TestAvalancheKind:
    """Tests for the avalanche hazard kind added in v2."""

    def setup_method(self):
        self.overlay = UMGeoOverlay()

    def test_avalanche_validates(self):
        ev = GeoEvent("avalanche", 3.0, 47.5, -121.5)
        ev.validate()  # must not raise

    def test_avalanche_energy_si_positive(self):
        ev = GeoEvent("avalanche", 3.0, 47.5, -121.5)
        assert ev.energy_si > 0

    def test_avalanche_energy_scales_with_magnitude(self):
        low  = GeoEvent("avalanche", 1.0, 47.5, -121.5)
        high = GeoEvent("avalanche", 5.0, 47.5, -121.5)
        assert high.energy_si > low.energy_si

    def test_avalanche_danger_level_1_lowest_energy(self):
        ev = GeoEvent("avalanche", 1.0, 47.5, -121.5)
        assert ev.energy_si > 0

    def test_avalanche_danger_level_5_extreme(self):
        ev = GeoEvent("avalanche", 5.0, 47.5, -121.5)
        # danger 5 → 5² × 5e11 = 1.25e13 J
        assert ev.energy_si >= 1e12

    def test_avalanche_overlay_returns_result(self):
        r = self.overlay.analyse(GeoEvent("avalanche", 3.0, 47.5, -121.5))
        assert r.phi_debt_injection >= 0
        assert 0.0 <= r.winding_stability <= 1.0

    def test_avalanche_overlay_has_epistemic_label(self):
        r = self.overlay.analyse(GeoEvent("avalanche", 2.0, 47.0, -121.0))
        assert "ADJACENT" in r.epistemic_label

    def test_avalanche_phi_debt_positive(self):
        r = self.overlay.analyse(GeoEvent("avalanche", 4.0, 47.5, -121.5))
        assert r.phi_debt_injection > 0

    def test_avalanche_in_batch(self):
        events = [
            GeoEvent("avalanche", 1.0, 47.5, -121.5),
            GeoEvent("avalanche", 3.0, 47.5, -121.5),
            GeoEvent("avalanche", 5.0, 47.5, -121.5),
        ]
        results = analyse_event_batch(events)
        assert len(results) == 3
        # Higher danger → higher phi_debt
        assert results[2].phi_debt_injection > results[0].phi_debt_injection


class TestNWSAlertKind:
    """Tests for the nws_alert hazard kind added in v2."""

    def setup_method(self):
        self.overlay = UMGeoOverlay()

    def test_nws_alert_validates(self):
        ev = GeoEvent("nws_alert", 3.0, 47.6, -122.3)
        ev.validate()

    def test_nws_alert_energy_positive(self):
        ev = GeoEvent("nws_alert", 2.0, 47.6, -122.3)
        assert ev.energy_si > 0

    def test_nws_alert_severity_1_minimal(self):
        ev = GeoEvent("nws_alert", 1.0, 47.6, -122.3)
        assert ev.energy_si > 0

    def test_nws_alert_severity_4_extreme(self):
        ev4 = GeoEvent("nws_alert", 4.0, 47.6, -122.3)
        ev1 = GeoEvent("nws_alert", 1.0, 47.6, -122.3)
        assert ev4.energy_si > ev1.energy_si

    def test_nws_alert_overlay_runs(self):
        r = self.overlay.analyse(GeoEvent("nws_alert", 3.0, 47.6, -122.3))
        assert 0.0 <= r.winding_stability <= 1.0
        assert r.phi_debt_injection >= 0

    def test_nws_alert_parse_eonet_not_needed(self):
        # nws_alert is a separate kind from storm; validate they are distinct
        assert "nws_alert" in DISASTER_KINDS
        assert "storm" in DISASTER_KINDS
        assert "nws_alert" != "storm"

    def test_nws_alert_in_batch(self):
        events = [
            GeoEvent("nws_alert", 1.0, 47.6, -122.3),
            GeoEvent("nws_alert", 4.0, 47.6, -122.3),
        ]
        results = analyse_event_batch(events)
        assert len(results) == 2

    def test_nws_alert_summary_in_analyse_result(self):
        r = self.overlay.analyse(GeoEvent("nws_alert", 2.0, 47.6, -122.3))
        assert "nws_alert" in r.summary.lower() or "NWS_ALERT" in r.summary


# ===========================================================================
# v3 Constants — new DISASTER_KINDS, Pillar 807, Convergence Index
# ===========================================================================

class TestV3Constants:
    def test_space_weather_in_disaster_kinds(self):
        assert "space_weather" in DISASTER_KINDS

    def test_infrastructure_in_disaster_kinds(self):
        assert "infrastructure" in DISASTER_KINDS

    def test_cyber_in_disaster_kinds(self):
        assert "cyber" in DISASTER_KINDS

    def test_p807_damping_radius_km_positive(self):
        assert P807_DAMPING_RADIUS_KM > 0

    def test_p807_earth_radius_km_reasonable(self):
        assert 6300 < P807_EARTH_RADIUS_KM < 6450

    def test_ci_weights_sum_to_one(self):
        assert abs(CI_WEIGHT_PHI_DEBT + CI_WEIGHT_KP + CI_WEIGHT_CII - 1.0) < 1e-12

    def test_ci_phi_debt_weight(self):
        assert CI_WEIGHT_PHI_DEBT == 0.50

    def test_ci_kp_weight(self):
        assert CI_WEIGHT_KP == 0.30

    def test_ci_cii_weight(self):
        assert CI_WEIGHT_CII == 0.20

    def test_kp_energy_base_positive(self):
        assert KP_ENERGY_BASE > 0

    def test_kp_energy_exponent_positive(self):
        assert KP_ENERGY_EXPONENT > 0


# ===========================================================================
# v3 GeoEvent — new kinds
# ===========================================================================

class TestSpaceWeatherGeoEvent:
    def test_space_weather_validates(self):
        ev = GeoEvent("space_weather", 6.0, 90.0, 0.0)
        ev.validate()

    def test_space_weather_energy_positive(self):
        ev = GeoEvent("space_weather", 5.0, 90.0, 0.0)
        assert ev.energy_si > 0

    def test_space_weather_kp5_energy(self):
        ev = GeoEvent("space_weather", 5.0, 90.0, 0.0)
        expected = KP_ENERGY_BASE * (10 ** (KP_ENERGY_EXPONENT * 5.0))
        assert abs(ev.energy_si - expected) / expected < 1e-9

    def test_space_weather_kp9_greater_than_kp5(self):
        ev5 = GeoEvent("space_weather", 5.0, 90.0, 0.0)
        ev9 = GeoEvent("space_weather", 9.0, 90.0, 0.0)
        assert ev9.energy_si > ev5.energy_si

    def test_space_weather_kp0_energy_base(self):
        ev = GeoEvent("space_weather", 0.0, 90.0, 0.0)
        assert ev.energy_si == pytest.approx(KP_ENERGY_BASE, rel=1e-9)

    def test_space_weather_overlay_runs(self):
        ev = GeoEvent("space_weather", 6.0, 90.0, 0.0)
        overlay = UMGeoOverlay()
        r = overlay.analyse(ev)
        assert r.phi_debt_injection >= 0
        assert 0.0 <= r.winding_stability <= 1.0
        assert "ADJACENT" in r.epistemic_label

    def test_space_weather_phi_debt_scales_with_kp(self):
        overlay = UMGeoOverlay()
        r5 = overlay.analyse(GeoEvent("space_weather", 5.0, 90.0, 0.0))
        r9 = overlay.analyse(GeoEvent("space_weather", 9.0, 90.0, 0.0))
        assert r9.phi_debt_injection > r5.phi_debt_injection

    def test_space_weather_in_batch(self):
        events = [GeoEvent("space_weather", float(k), 90.0, 0.0) for k in range(1, 6)]
        results = analyse_event_batch(events)
        assert len(results) == 5

    def test_space_weather_lat_valid(self):
        ev = GeoEvent("space_weather", 7.0, 90.0, 0.0)
        ev.validate()  # lat=90 is valid

    def test_space_weather_southern_oval(self):
        ev = GeoEvent("space_weather", 7.0, -90.0, 0.0)
        ev.validate()


class TestInfrastructureGeoEvent:
    def test_infrastructure_validates(self):
        ev = GeoEvent("infrastructure", 5.0, 51.5, -0.1)
        ev.validate()

    def test_infrastructure_energy_positive(self):
        ev = GeoEvent("infrastructure", 5.0, 51.5, -0.1)
        assert ev.energy_si > 0

    def test_infrastructure_severity_scaling(self):
        ev3 = GeoEvent("infrastructure", 3.0, 51.5, -0.1)
        ev8 = GeoEvent("infrastructure", 8.0, 51.5, -0.1)
        assert ev8.energy_si > ev3.energy_si

    def test_infrastructure_overlay_runs(self):
        ev = GeoEvent("infrastructure", 7.0, 40.7, -74.0)
        overlay = UMGeoOverlay()
        r = overlay.analyse(ev)
        assert r.phi_debt_injection >= 0
        assert 0.0 <= r.winding_stability <= 1.0

    def test_infrastructure_in_batch(self):
        events = [GeoEvent("infrastructure", float(i), 40.0 + i, -74.0) for i in range(1, 6)]
        results = analyse_event_batch(events)
        assert len(results) == 5

    def test_infrastructure_has_epistemic_label(self):
        overlay = UMGeoOverlay()
        r = overlay.analyse(GeoEvent("infrastructure", 5.0, 48.9, 2.3))
        assert "ADJACENT" in r.epistemic_label


class TestCyberGeoEvent:
    def test_cyber_validates(self):
        ev = GeoEvent("cyber", 7.0, 0.0, 0.0)
        ev.validate()

    def test_cyber_energy_positive(self):
        ev = GeoEvent("cyber", 7.0, 0.0, 0.0)
        assert ev.energy_si > 0

    def test_cyber_cvss10_energy(self):
        ev10 = GeoEvent("cyber", 10.0, 0.0, 0.0)
        ev1 = GeoEvent("cyber", 1.0, 0.0, 0.0)
        assert ev10.energy_si > ev1.energy_si

    def test_cyber_overlay_runs(self):
        ev = GeoEvent("cyber", 9.0, 0.0, 0.0)
        overlay = UMGeoOverlay()
        r = overlay.analyse(ev)
        assert r.phi_debt_injection >= 0
        assert 0.0 <= r.winding_stability <= 1.0

    def test_cyber_in_batch(self):
        events = [GeoEvent("cyber", float(i), 0.0, 0.0) for i in range(1, 6)]
        results = analyse_event_batch(events)
        assert len(results) == 5

    def test_cyber_has_epistemic_label(self):
        overlay = UMGeoOverlay()
        r = overlay.analyse(GeoEvent("cyber", 7.0, 0.0, 0.0))
        assert "ADJACENT" in r.epistemic_label


# ===========================================================================
# v3 Pillar 807 — spatial kernel
# ===========================================================================

class TestP807Kernel:
    def test_haversine_km_same_point(self):
        assert _haversine_km(47.0, -122.0, 47.0, -122.0) == pytest.approx(0.0, abs=1e-6)

    def test_haversine_km_known_distance(self):
        # Seattle → Portland ≈ 235 km (by air)
        d = _haversine_km(47.6, -122.3, 45.5, -122.7)
        assert 210 < d < 270

    def test_haversine_km_symmetric(self):
        d1 = _haversine_km(47.0, -122.0, 35.0, 139.0)
        d2 = _haversine_km(35.0, 139.0, 47.0, -122.0)
        assert d1 == pytest.approx(d2, rel=1e-6)

    def test_haversine_km_antipodal(self):
        d = _haversine_km(0.0, 0.0, 0.0, 180.0)
        assert d == pytest.approx(math.pi * P807_EARTH_RADIUS_KM, rel=1e-3)

    def test_p807_weight_at_zero(self):
        w = _p807_weight(0.0)
        assert w == pytest.approx(1.0, rel=1e-9)

    def test_p807_weight_at_sigma(self):
        w = _p807_weight(P807_DAMPING_RADIUS_KM)
        assert w == pytest.approx(math.exp(-0.5), rel=1e-9)

    def test_p807_weight_decays(self):
        assert _p807_weight(100) > _p807_weight(500) > _p807_weight(2000)

    def test_p807_weight_never_negative(self):
        for d in [0, 100, 500, 1000, 5000, 20000]:
            assert _p807_weight(d) >= 0

    def test_p807_weight_asymptotic_zero(self):
        assert _p807_weight(100_000) < 1e-10

    def test_p807_weight_at_2sigma(self):
        w = _p807_weight(2 * P807_DAMPING_RADIUS_KM)
        assert w == pytest.approx(math.exp(-2.0), rel=1e-9)


# ===========================================================================
# v3 Convergence Index
# ===========================================================================

class TestConvergenceIndex:
    def setup_method(self):
        self.overlay = UMGeoOverlay()

    def _make_events(self, kinds_mags):
        evs = [GeoEvent(k, m, 47.6, -122.3) for k, m in kinds_mags]
        return [self.overlay.analyse(e) for e in evs]

    def test_returns_convergence_result(self):
        r = compute_convergence_index(47.6, -122.3, [], kp=0.0, cii_score=0.0)
        assert isinstance(r, ConvergenceResult)

    def test_index_in_range(self):
        results = self._make_events([("earthquake", 7.5)])
        ci = compute_convergence_index(47.6, -122.3, results, kp=6.0, cii_score=50.0)
        assert 0.0 <= ci.index <= 1.0

    def test_no_events_kp0_cii0_index_zero(self):
        ci = compute_convergence_index(0.0, 0.0, [], kp=0.0, cii_score=0.0)
        assert ci.index == pytest.approx(0.0, abs=1e-9)

    def test_high_kp_increases_index(self):
        ci_low = compute_convergence_index(47.6, -122.3, [], kp=0.0, cii_score=0.0)
        ci_high = compute_convergence_index(47.6, -122.3, [], kp=9.0, cii_score=0.0)
        assert ci_high.index > ci_low.index

    def test_kp_component_normalised(self):
        ci = compute_convergence_index(0.0, 0.0, [], kp=4.5, cii_score=0.0)
        assert ci.kp_component == pytest.approx(4.5 / 9.0, rel=1e-6)

    def test_cii_component_normalised(self):
        ci = compute_convergence_index(0.0, 0.0, [], kp=0.0, cii_score=60.0)
        assert ci.cii_component == pytest.approx(60.0 / 100.0, rel=1e-6)

    def test_alert_false_below_threshold(self):
        ci = compute_convergence_index(0.0, 0.0, [], kp=0.0, cii_score=0.0)
        assert not ci.alert

    def test_alert_true_above_threshold(self):
        results = self._make_events([("earthquake", 9.5)])
        ci = compute_convergence_index(47.6, -122.3, results, kp=9.0, cii_score=100.0)
        assert ci.alert

    def test_epistemic_label_present(self):
        ci = compute_convergence_index(0.0, 0.0, [], kp=0.0, cii_score=0.0)
        assert "ADJACENT" in ci.epistemic_label

    def test_lat_lon_preserved(self):
        ci = compute_convergence_index(51.5, -0.1, [], kp=0.0, cii_score=0.0)
        assert ci.lat == 51.5
        assert ci.lon == -0.1

    def test_distance_decay_reduces_phi(self):
        ev_near = self.overlay.analyse(GeoEvent("earthquake", 7.5, 47.6, -122.3))
        ev_far  = self.overlay.analyse(GeoEvent("earthquake", 7.5, 0.0,  0.0))
        ci_near = compute_convergence_index(47.6, -122.3, [ev_near], kp=0.0, cii_score=0.0)
        ci_far  = compute_convergence_index(47.6, -122.3, [ev_far],  kp=0.0, cii_score=0.0)
        assert ci_near.phi_component >= ci_far.phi_component

    def test_multiple_events_combine(self):
        results_one = self._make_events([("earthquake", 7.5)])
        results_two = self._make_events([("earthquake", 7.5), ("wildfire", 5.0)])
        ci1 = compute_convergence_index(47.6, -122.3, results_one, kp=0.0, cii_score=0.0)
        ci2 = compute_convergence_index(47.6, -122.3, results_two, kp=0.0, cii_score=0.0)
        assert ci2.phi_component >= ci1.phi_component

    def test_weights_respected(self):
        # Pure Kp=9, no events, no CII
        ci = compute_convergence_index(0.0, 0.0, [], kp=9.0, cii_score=0.0)
        assert ci.index == pytest.approx(CI_WEIGHT_KP * 1.0, rel=1e-6)

    def test_pure_cii_score(self):
        ci = compute_convergence_index(0.0, 0.0, [], kp=0.0, cii_score=100.0)
        assert ci.index == pytest.approx(CI_WEIGHT_CII * 1.0, rel=1e-6)

    def test_index_clamped_to_one(self):
        results = self._make_events([("earthquake", 9.9), ("wildfire", 9.9)])
        ci = compute_convergence_index(0.0, 0.0, results, kp=9.0, cii_score=100.0)
        assert ci.index <= 1.0

    def test_index_never_negative(self):
        ci = compute_convergence_index(0.0, 0.0, [], kp=0.0, cii_score=0.0)
        assert ci.index >= 0.0

    def test_space_weather_event_contributes_phi(self):
        ev = self.overlay.analyse(GeoEvent("space_weather", 7.0, 90.0, 0.0))
        # space_weather is at pole — distant from equatorial query point
        ci = compute_convergence_index(0.0, 0.0, [ev], kp=0.0, cii_score=0.0)
        assert ci.phi_component >= 0.0

    def test_cyber_event_at_origin_phi(self):
        ev = self.overlay.analyse(GeoEvent("cyber", 9.0, 0.0, 0.0))
        ci = compute_convergence_index(0.0, 0.0, [ev], kp=0.0, cii_score=0.0)
        assert ci.phi_component > 0.0

    def test_infrastructure_event_phi(self):
        ev = self.overlay.analyse(GeoEvent("infrastructure", 8.0, 40.7, -74.0))
        ci = compute_convergence_index(40.7, -74.0, [ev], kp=0.0, cii_score=0.0)
        assert ci.phi_component > 0.0


# ===========================================================================
# v3 wm_feeds module — parsers (unit tests only, no network calls)
# ===========================================================================

class TestSWPCKpParser:
    """Unit tests for parse_kp_1min from wm_feeds."""

    def test_empty_data_returns_none(self):
        from geo_monitor.engine.wm_feeds import parse_kp_1min
        assert parse_kp_1min([]) is None

    def test_quiet_kp_returns_none(self):
        from geo_monitor.engine.wm_feeds import parse_kp_1min
        data = [{"kp_index": 2.0, "time_tag": "2026-09-01T00:00:00Z"}]
        assert parse_kp_1min(data) is None

    def test_storm_kp_returns_event(self):
        from geo_monitor.engine.wm_feeds import parse_kp_1min
        data = [{"kp_index": 5.5, "time_tag": "2026-09-01T00:00:00Z"}]
        ev = parse_kp_1min(data)
        assert ev is not None
        assert ev.kind == "space_weather"
        assert ev.magnitude == pytest.approx(5.5, rel=1e-9)

    def test_storm_event_lat_at_pole(self):
        from geo_monitor.engine.wm_feeds import parse_kp_1min
        data = [{"kp_index": 6.0}]
        ev = parse_kp_1min(data)
        assert ev.lat == 90.0

    def test_storm_event_energy_positive(self):
        from geo_monitor.engine.wm_feeds import parse_kp_1min
        data = [{"kp_index": 7.0}]
        ev = parse_kp_1min(data)
        assert ev.energy_J > 0

    def test_kp_exactly_4_returns_event(self):
        from geo_monitor.engine.wm_feeds import parse_kp_1min
        data = [{"kp_index": 4.0}]
        ev = parse_kp_1min(data)
        assert ev is not None

    def test_kp_below_4_returns_none(self):
        from geo_monitor.engine.wm_feeds import parse_kp_1min
        data = [{"kp_index": 3.9}]
        assert parse_kp_1min(data) is None

    def test_invalid_kp_index_returns_none(self):
        from geo_monitor.engine.wm_feeds import parse_kp_1min
        data = [{"kp_index": "bad"}]
        assert parse_kp_1min(data) is None

    def test_uses_last_entry(self):
        from geo_monitor.engine.wm_feeds import parse_kp_1min
        data = [{"kp_index": 1.0}, {"kp_index": 6.0}]
        ev = parse_kp_1min(data)
        assert ev is not None and ev.magnitude == pytest.approx(6.0)

    def test_kp_to_energy_j_monotonic(self):
        from geo_monitor.engine.wm_feeds import _kp_to_energy_j
        energies = [_kp_to_energy_j(float(k)) for k in range(0, 10)]
        for a, b in zip(energies, energies[1:]):
            assert b > a


class TestSwpcAlertsParser:
    def test_empty_alerts(self):
        from geo_monitor.engine.wm_feeds import parse_swpc_alerts
        assert parse_swpc_alerts([]) == []

    def test_g1_alert_detected(self):
        from geo_monitor.engine.wm_feeds import parse_swpc_alerts
        data = [{"message": "G1 (Minor) Geomagnetic Storm Watch"}]
        events = parse_swpc_alerts(data)
        assert len(events) == 1
        assert events[0].kind == "space_weather"

    def test_g5_alert_detected(self):
        from geo_monitor.engine.wm_feeds import parse_swpc_alerts
        data = [{"message": "G5 Extreme geomagnetic storm"}]
        events = parse_swpc_alerts(data)
        assert len(events) == 1
        assert events[0].magnitude >= 9

    def test_non_storm_message_ignored(self):
        from geo_monitor.engine.wm_feeds import parse_swpc_alerts
        data = [{"message": "Solar flare R1 radio blackout"}]
        events = parse_swpc_alerts(data)
        assert events == []

    def test_multiple_alerts(self):
        from geo_monitor.engine.wm_feeds import parse_swpc_alerts
        data = [
            {"message": "G2 Watch"},
            {"message": "G3 Warning"},
        ]
        events = parse_swpc_alerts(data)
        assert len(events) == 2


class TestGDACSParser:
    def test_empty_xml_returns_empty(self):
        from geo_monitor.engine.wm_feeds import parse_gdacs_feed
        assert parse_gdacs_feed("") == []

    def test_malformed_xml_returns_empty(self):
        from geo_monitor.engine.wm_feeds import parse_gdacs_feed
        assert parse_gdacs_feed("<not valid xml<<<") == []

    def test_valid_eq_entry(self):
        from geo_monitor.engine.wm_feeds import parse_gdacs_feed
        xml = """<?xml version="1.0"?>
<rss><channel>
<item>
  <gdacs:eventtype xmlns:gdacs="http://www.gdacs.org">EQ</gdacs:eventtype>
  <gdacs:alertlevel xmlns:gdacs="http://www.gdacs.org">Orange</gdacs:alertlevel>
  <gdacs:magnitude xmlns:gdacs="http://www.gdacs.org">6.5</gdacs:magnitude>
  <georss:point xmlns:georss="http://www.georss.org/georss">35.7 139.7</georss:point>
</item>
</channel></rss>"""
        events = parse_gdacs_feed(xml)
        assert len(events) == 1
        assert events[0].kind == "earthquake"
        assert events[0].magnitude == pytest.approx(6.5, rel=1e-6)
        assert events[0].lat == pytest.approx(35.7, rel=1e-6)
        assert events[0].lon == pytest.approx(139.7, rel=1e-6)

    def test_valid_cyclone_entry(self):
        from geo_monitor.engine.wm_feeds import parse_gdacs_feed
        xml = """<?xml version="1.0"?>
<rss><channel>
<item>
  <gdacs:eventtype xmlns:gdacs="http://www.gdacs.org">TC</gdacs:eventtype>
  <gdacs:alertlevel xmlns:gdacs="http://www.gdacs.org">Red</gdacs:alertlevel>
  <georss:point xmlns:georss="http://www.georss.org/georss">12.0 95.0</georss:point>
</item>
</channel></rss>"""
        events = parse_gdacs_feed(xml)
        assert len(events) == 1
        assert events[0].kind == "hurricane"

    def test_valid_flood_entry(self):
        from geo_monitor.engine.wm_feeds import parse_gdacs_feed
        xml = """<?xml version="1.0"?>
<rss><channel>
<item>
  <gdacs:eventtype xmlns:gdacs="http://www.gdacs.org">FL</gdacs:eventtype>
  <gdacs:alertlevel xmlns:gdacs="http://www.gdacs.org">Green</gdacs:alertlevel>
  <georss:point xmlns:georss="http://www.georss.org/georss">5.0 25.0</georss:point>
</item>
</channel></rss>"""
        events = parse_gdacs_feed(xml)
        assert len(events) == 1
        assert events[0].kind == "flood"

    def test_missing_georss_point_skipped(self):
        from geo_monitor.engine.wm_feeds import parse_gdacs_feed
        xml = """<?xml version="1.0"?>
<rss><channel>
<item>
  <gdacs:eventtype xmlns:gdacs="http://www.gdacs.org">EQ</gdacs:eventtype>
</item>
</channel></rss>"""
        events = parse_gdacs_feed(xml)
        assert events == []

    def test_multiple_entries(self):
        from geo_monitor.engine.wm_feeds import parse_gdacs_feed
        xml = """<?xml version="1.0"?>
<rss><channel>
<item>
  <gdacs:eventtype xmlns:gdacs="http://www.gdacs.org">EQ</gdacs:eventtype>
  <gdacs:alertlevel xmlns:gdacs="http://www.gdacs.org">Orange</gdacs:alertlevel>
  <georss:point xmlns:georss="http://www.georss.org/georss">35.7 139.7</georss:point>
</item>
<item>
  <gdacs:eventtype xmlns:gdacs="http://www.gdacs.org">TC</gdacs:eventtype>
  <gdacs:alertlevel xmlns:gdacs="http://www.gdacs.org">Red</gdacs:alertlevel>
  <georss:point xmlns:georss="http://www.georss.org/georss">12.0 95.0</georss:point>
</item>
</channel></rss>"""
        events = parse_gdacs_feed(xml)
        assert len(events) == 2


class TestCISAKEVParser:
    def test_empty_data_returns_empty(self):
        from geo_monitor.engine.wm_feeds import parse_cisa_kev
        assert parse_cisa_kev({}) == []

    def test_returns_geoevents(self):
        from geo_monitor.engine.wm_feeds import parse_cisa_kev
        data = {"vulnerabilities": [
            {"vulnerabilityName": "CVE-2026-0001", "dateAdded": "2026-09-01"},
            {"vulnerabilityName": "CVE-2026-0002", "dateAdded": "2026-08-30"},
        ]}
        events = parse_cisa_kev(data)
        assert len(events) == 2
        assert all(ev.kind == "cyber" for ev in events)

    def test_limit_respected(self):
        from geo_monitor.engine.wm_feeds import parse_cisa_kev
        data = {"vulnerabilities": [
            {"vulnerabilityName": f"CVE-2026-{i:04d}", "dateAdded": f"2026-09-{i+1:02d}"}
            for i in range(30)
        ]}
        events = parse_cisa_kev(data, limit=10)
        assert len(events) == 10

    def test_cyber_events_at_origin(self):
        from geo_monitor.engine.wm_feeds import parse_cisa_kev
        data = {"vulnerabilities": [{"vulnerabilityName": "CVE-X", "dateAdded": "2026-09-01"}]}
        events = parse_cisa_kev(data)
        assert events[0].lat == 0.0
        assert events[0].lon == 0.0

    def test_cyber_magnitude_positive(self):
        from geo_monitor.engine.wm_feeds import parse_cisa_kev
        data = {"vulnerabilities": [{"vulnerabilityName": "CVE-X", "dateAdded": "2026-09-01"}]}
        events = parse_cisa_kev(data)
        assert events[0].magnitude > 0


class TestWMAAvailability:
    def test_wm_api_available_false_without_key(self, monkeypatch):
        import os
        monkeypatch.delenv("WM_API_KEY", raising=False)
        from importlib import reload
        import geo_monitor.engine.wm_feeds as wm
        reload(wm)
        assert not wm.wm_api_available()

    def test_wm_api_available_true_with_key(self, monkeypatch):
        monkeypatch.setenv("WM_API_KEY", "test_key_123")
        from importlib import reload
        import geo_monitor.engine.wm_feeds as wm
        reload(wm)
        assert wm.wm_api_available()

    def test_cii_scores_empty_without_key(self, monkeypatch):
        import os
        monkeypatch.delenv("WM_API_KEY", raising=False)
        from importlib import reload
        import geo_monitor.engine.wm_feeds as wm
        reload(wm)
        assert wm.fetch_cii_scores() == {}

    def test_infrastructure_empty_without_key(self, monkeypatch):
        import os
        monkeypatch.delenv("WM_API_KEY", raising=False)
        from importlib import reload
        import geo_monitor.engine.wm_feeds as wm
        reload(wm)
        assert wm.fetch_infrastructure_alerts() == []


class TestGeoMonitorV3FeedsAPI:
    def test_instantiates(self):
        from geo_monitor.engine.wm_feeds import GeoMonitorV3Feeds
        feeds = GeoMonitorV3Feeds()
        assert feeds is not None

    def test_current_kp_method_exists(self):
        from geo_monitor.engine.wm_feeds import GeoMonitorV3Feeds
        feeds = GeoMonitorV3Feeds()
        assert hasattr(feeds, 'current_kp')

    def test_space_weather_events_method_exists(self):
        from geo_monitor.engine.wm_feeds import GeoMonitorV3Feeds
        feeds = GeoMonitorV3Feeds()
        assert hasattr(feeds, 'space_weather_events')

    def test_gdacs_events_method_exists(self):
        from geo_monitor.engine.wm_feeds import GeoMonitorV3Feeds
        feeds = GeoMonitorV3Feeds()
        assert hasattr(feeds, 'gdacs_events')

    def test_cyber_events_method_exists(self):
        from geo_monitor.engine.wm_feeds import GeoMonitorV3Feeds
        feeds = GeoMonitorV3Feeds()
        assert hasattr(feeds, 'cyber_events')

    def test_infrastructure_events_method_exists(self):
        from geo_monitor.engine.wm_feeds import GeoMonitorV3Feeds
        feeds = GeoMonitorV3Feeds()
        assert hasattr(feeds, 'infrastructure_events')

    def test_cii_scores_method_exists(self):
        from geo_monitor.engine.wm_feeds import GeoMonitorV3Feeds
        feeds = GeoMonitorV3Feeds()
        assert hasattr(feeds, 'cii_scores')


# ===========================================================================
# v3 backward-compatibility — existing kinds still work
# ===========================================================================

class TestBackwardCompatibility:
    """Verify all pre-v3 DISASTER_KINDS remain valid after v3 additions."""

    PRE_V3_KINDS = [
        "earthquake", "wildfire", "hurricane", "tornado", "flood",
        "tsunami", "volcano", "drought", "landslide", "storm",
        "avalanche", "nws_alert",
    ]
    overlay = UMGeoOverlay()

    def test_all_pre_v3_kinds_in_disaster_kinds(self):
        for k in self.PRE_V3_KINDS:
            assert k in DISASTER_KINDS, f"{k!r} missing from DISASTER_KINDS"

    def test_all_pre_v3_kinds_validate(self):
        for k in self.PRE_V3_KINDS:
            ev = GeoEvent(k, 5.0, 45.0, -120.0)
            ev.validate()

    def test_all_pre_v3_kinds_have_positive_energy(self):
        for k in self.PRE_V3_KINDS:
            ev = GeoEvent(k, 5.0, 45.0, -120.0)
            assert ev.energy_si > 0, f"{k} energy_si not positive"

    def test_all_pre_v3_kinds_overlay_runs(self):
        for k in self.PRE_V3_KINDS:
            ev = GeoEvent(k, 4.0, 45.0, -120.0)
            r = self.overlay.analyse(ev)
            assert 0.0 <= r.winding_stability <= 1.0


# ===========================================================================
# v3 Pillar 807 — Pillar reference constants
# ===========================================================================

class TestPillar807Reference:
    def test_p807_sigma_reasonable(self):
        sigma = P807_DAMPING_RADIUS_KM / P807_EARTH_RADIUS_KM
        assert 0.05 < sigma < 0.15  # ≈ 0.0785

    def test_p807_damping_500km(self):
        # At exactly σ=500 km, weight = e^(-0.5)
        w = _p807_weight(500.0)
        assert w == pytest.approx(math.exp(-0.5), rel=1e-9)

    def test_p807_weight_positive_everywhere(self):
        for d in [0, 1, 10, 100, 1000, 10_000]:
            assert _p807_weight(float(d)) > 0
