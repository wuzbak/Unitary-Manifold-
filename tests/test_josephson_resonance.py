# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_josephson_resonance.py
===================================
Tests for src/core/josephson_resonance.py — Pillar 195.
"""

from __future__ import annotations

import math

import pytest

from src.core.josephson_resonance import (
    N_W,
    N_INV,
    K_CS,
    XI_C,
    BRAID_FREQ_RATIO,
    GEO_SHIFT_RATIO,
    BEAT_FREQ_RATIO,
    F_PLASMA_CANONICAL_GHZ,
    E_CHARGE_C,
    HBAR_JS,
    josephson_plasma_frequency,
    braid_resonance_frequency,
    geometric_frequency_shift,
    squid_detection_window,
    lab_prediction,
    pillar195_summary,
)


# ===========================================================================
# Module Constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_n_inv_is_7(self):
        assert N_INV == 7

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_xi_c_value(self):
        assert XI_C == pytest.approx(35.0 / 74.0, rel=1e-9)

    def test_xi_c_is_n_w_times_n_inv_over_k_cs(self):
        assert XI_C == pytest.approx(N_W * N_INV / K_CS, rel=1e-9)

    def test_braid_freq_ratio_equals_xi_c(self):
        assert BRAID_FREQ_RATIO == pytest.approx(XI_C, rel=1e-9)

    def test_braid_freq_ratio_exact(self):
        assert BRAID_FREQ_RATIO == pytest.approx(35.0 / 74.0, rel=1e-9)

    def test_geo_shift_ratio_exact(self):
        assert GEO_SHIFT_RATIO == pytest.approx(5.0 / 74.0, rel=1e-9)

    def test_geo_shift_ratio_is_n_w_over_k_cs(self):
        assert GEO_SHIFT_RATIO == pytest.approx(N_W / K_CS, rel=1e-9)

    def test_beat_freq_ratio_exact(self):
        assert BEAT_FREQ_RATIO == pytest.approx(44.0 / 74.0, rel=1e-9)

    def test_beat_freq_ratio_is_22_over_37(self):
        assert BEAT_FREQ_RATIO == pytest.approx(22.0 / 37.0, rel=1e-9)

    def test_f_plasma_canonical_is_5ghz(self):
        assert F_PLASMA_CANONICAL_GHZ == pytest.approx(5.0, rel=1e-9)

    def test_e_charge_order(self):
        assert 1.5e-19 < E_CHARGE_C < 1.7e-19

    def test_hbar_order(self):
        assert 1.0e-34 < HBAR_JS < 1.2e-34

    def test_n_w_sq_plus_n_inv_sq_eq_k_cs(self):
        assert N_W**2 + N_INV**2 == K_CS

    def test_braid_plus_geo_lt_one(self):
        # 35/74 + 5/74 = 40/74 < 1
        assert BRAID_FREQ_RATIO + GEO_SHIFT_RATIO < 1.0

    def test_braid_and_geo_ratios_from_same_integers(self):
        assert BRAID_FREQ_RATIO == pytest.approx(N_W * N_INV / K_CS, rel=1e-9)
        assert GEO_SHIFT_RATIO == pytest.approx(N_W / K_CS, rel=1e-9)


# ===========================================================================
# josephson_plasma_frequency
# ===========================================================================

class TestJosephsonPlasmaFrequency:
    def test_canonical_gives_5ghz(self):
        r = josephson_plasma_frequency(32.5, 100.0)
        assert r["f_plasma_ghz"] == pytest.approx(5.0, rel=0.02)

    def test_in_squid_range(self):
        r = josephson_plasma_frequency(32.5, 100.0)
        assert r["in_squid_range"] is True

    def test_formula_key(self):
        r = josephson_plasma_frequency()
        assert "f = sqrt" in r["formula"]

    def test_omega_positive(self):
        r = josephson_plasma_frequency(32.5, 100.0)
        assert r["omega_rad_per_s"] > 0.0

    def test_f_plasma_hz_consistent(self):
        r = josephson_plasma_frequency(32.5, 100.0)
        assert r["f_plasma_hz"] == pytest.approx(r["f_plasma_ghz"] * 1e9, rel=1e-9)

    def test_i_c_passthrough(self):
        r = josephson_plasma_frequency(30.0, 100.0)
        assert r["i_c_na"] == pytest.approx(30.0, rel=1e-9)

    def test_c_j_passthrough(self):
        r = josephson_plasma_frequency(32.5, 150.0)
        assert r["c_j_ff"] == pytest.approx(150.0, rel=1e-9)

    def test_scales_with_sqrt_ic(self):
        r1 = josephson_plasma_frequency(32.5, 100.0)
        r2 = josephson_plasma_frequency(130.0, 100.0)
        # f ∝ √I_c, so 4× I_c → 2× f
        assert r2["f_plasma_ghz"] == pytest.approx(2.0 * r1["f_plasma_ghz"], rel=0.01)

    def test_scales_inversely_with_sqrt_cj(self):
        r1 = josephson_plasma_frequency(32.5, 100.0)
        r2 = josephson_plasma_frequency(32.5, 400.0)
        # f ∝ 1/√C_J, so 4× C_J → ½ f
        assert r2["f_plasma_ghz"] == pytest.approx(0.5 * r1["f_plasma_ghz"], rel=0.01)

    def test_note_present(self):
        r = josephson_plasma_frequency()
        assert len(r["note"]) > 20


# ===========================================================================
# braid_resonance_frequency
# ===========================================================================

class TestBraidResonanceFrequency:
    def test_ratio_is_35_over_74(self):
        r = braid_resonance_frequency(5.0)
        assert r["braid_freq_ratio"] == pytest.approx(35.0 / 74.0, rel=1e-9)

    def test_f_braid_for_5ghz(self):
        r = braid_resonance_frequency(5.0)
        assert r["f_braid_ghz"] == pytest.approx(5.0 * 35.0 / 74.0, rel=1e-6)

    def test_f_braid_approx_2365ghz(self):
        r = braid_resonance_frequency(5.0)
        assert r["f_braid_ghz"] == pytest.approx(2.365, abs=0.01)

    def test_f_plasma_passthrough(self):
        r = braid_resonance_frequency(7.0)
        assert r["f_plasma_ghz"] == pytest.approx(7.0, rel=1e-9)

    def test_f_braid_scales_linearly(self):
        r1 = braid_resonance_frequency(5.0)
        r2 = braid_resonance_frequency(10.0)
        assert r2["f_braid_ghz"] == pytest.approx(2.0 * r1["f_braid_ghz"], rel=1e-9)

    def test_xi_c_connection_present(self):
        r = braid_resonance_frequency(5.0)
        assert "ξ_c" in r["xi_c_connection"] or "xi_c" in r["xi_c_connection"].lower()

    def test_ratio_exact_string(self):
        r = braid_resonance_frequency(5.0)
        assert "35/74" in r["braid_freq_ratio_exact"]

    def test_physical_interpretation_present(self):
        r = braid_resonance_frequency(5.0)
        assert len(r["physical_interpretation"]) > 20

    def test_detection_method_present(self):
        r = braid_resonance_frequency(5.0)
        assert len(r["detection_method"]) > 20

    def test_braid_less_than_plasma(self):
        r = braid_resonance_frequency(5.0)
        assert r["f_braid_ghz"] < r["f_plasma_ghz"]


# ===========================================================================
# geometric_frequency_shift
# ===========================================================================

class TestGeometricFrequencyShift:
    def test_shift_ratio_is_5_over_74(self):
        r = geometric_frequency_shift(5.0)
        assert r["geo_shift_ratio"] == pytest.approx(5.0 / 74.0, rel=1e-9)

    def test_delta_f_for_5ghz(self):
        r = geometric_frequency_shift(5.0)
        assert r["delta_f_ghz"] == pytest.approx(5.0 * 5.0 / 74.0, rel=1e-6)

    def test_f_geo_for_5ghz(self):
        r = geometric_frequency_shift(5.0)
        assert r["f_geo_ghz"] == pytest.approx(5.0 * 79.0 / 74.0, rel=1e-6)

    def test_f_geo_ratio_79_over_74(self):
        r = geometric_frequency_shift(5.0)
        assert r["f_geo_ghz"] / r["f_plasma_ghz"] == pytest.approx(79.0 / 74.0, rel=1e-6)

    def test_beat_ratio_22_over_37(self):
        r = geometric_frequency_shift(5.0)
        assert r["beat_ratio"] == pytest.approx(22.0 / 37.0, rel=1e-6)

    def test_beat_freq_positive(self):
        r = geometric_frequency_shift(5.0)
        assert r["f_beat_ghz"] > 0.0

    def test_delta_f_mhz_consistent(self):
        r = geometric_frequency_shift(5.0)
        assert r["delta_f_mhz"] == pytest.approx(r["delta_f_ghz"] * 1e3, rel=1e-9)

    def test_shift_ratio_exact_string(self):
        r = geometric_frequency_shift(5.0)
        assert "5/74" in r["geo_shift_ratio_exact"]

    def test_f_geo_gt_f_braid(self):
        r = geometric_frequency_shift(5.0)
        assert r["f_geo_ghz"] > r["f_braid_ghz"]

    def test_honest_note_present(self):
        r = geometric_frequency_shift(5.0)
        assert len(r["honest_note"]) > 20

    def test_scales_linearly_with_f_plasma(self):
        r1 = geometric_frequency_shift(5.0)
        r2 = geometric_frequency_shift(10.0)
        assert r2["delta_f_ghz"] == pytest.approx(2.0 * r1["delta_f_ghz"], rel=1e-9)


# ===========================================================================
# squid_detection_window
# ===========================================================================

class TestSQUIDDetectionWindow:
    def test_f_braid_is_35_over_74_times_f_plasma(self):
        r = squid_detection_window(5.0)
        assert r["f_braid_ghz"] == pytest.approx(5.0 * 35.0 / 74.0, rel=1e-6)

    def test_window_straddles_f_braid(self):
        r = squid_detection_window(5.0, 1.0)
        assert r["window_low_ghz"] < r["f_braid_ghz"] < r["window_high_ghz"]

    def test_resolvable_by_squid(self):
        r = squid_detection_window(5.0)
        assert r["resolvable_by_squid"] is True

    def test_braid_ratio_exact_string(self):
        r = squid_detection_window(5.0)
        assert "35/74" in r["braid_ratio_exact"]

    def test_detection_protocol_present(self):
        r = squid_detection_window(5.0)
        assert len(r["detection_protocol"]) > 20

    def test_falsification_condition_present(self):
        r = squid_detection_window(5.0)
        assert "FALSIFIED" in r["falsification_condition"]

    def test_window_width_positive(self):
        r = squid_detection_window(5.0, 1.0)
        assert r["window_width_mhz"] > 0.0

    def test_precision_affects_window(self):
        r1 = squid_detection_window(5.0, 1.0)
        r2 = squid_detection_window(5.0, 2.0)
        assert r2["window_width_mhz"] == pytest.approx(2.0 * r1["window_width_mhz"], rel=1e-6)

    def test_braid_ratio_value(self):
        r = squid_detection_window(5.0)
        assert r["braid_ratio"] == pytest.approx(35.0 / 74.0, rel=1e-9)


# ===========================================================================
# lab_prediction
# ===========================================================================

class TestLabPrediction:
    @pytest.fixture(autouse=True)
    def result(self):
        self._r = lab_prediction(5.0, "Test Lab")

    def test_returns_dict(self):
        assert isinstance(self._r, dict)

    def test_pillar_is_195(self):
        assert self._r["pillar"] == 195

    def test_lab_name(self):
        assert self._r["lab"] == "Test Lab"

    def test_primary_prediction_ratio(self):
        p = self._r["primary_prediction"]
        assert "35/74" in p["ratio_exact"]

    def test_primary_freq_value(self):
        p = self._r["primary_prediction"]
        assert p["frequency_ghz"] == pytest.approx(5.0 * 35.0 / 74.0, rel=1e-6)

    def test_ratio_decimal_has_many_digits(self):
        p = self._r["primary_prediction"]
        assert len(p["ratio_decimal"]) >= 5

    def test_secondary_prediction_present(self):
        assert "secondary_prediction" in self._r
        s = self._r["secondary_prediction"]
        assert "5/74" in s["ratio_exact"]

    def test_detection_protocol_present(self):
        assert len(self._r["detection_protocol"]) > 20

    def test_falsification_condition_present(self):
        assert "FALSIFIED" in self._r["falsification_condition"]

    def test_connection_to_pentad_present(self):
        assert len(self._r["connection_to_pentad"]) > 20

    def test_honest_status_present(self):
        assert len(self._r["honest_status"]) > 20

    def test_junction_type_al(self):
        assert "Al" in self._r["junction_type"]

    def test_canonical_freq(self):
        assert self._r["canonical_plasma_freq_ghz"] == pytest.approx(5.0, rel=1e-9)


# ===========================================================================
# pillar195_summary
# ===========================================================================

class TestPillar195Summary:
    @pytest.fixture(autouse=True)
    def result(self):
        self._r = pillar195_summary()

    def test_pillar_is_195(self):
        assert self._r["pillar"] == 195

    def test_version(self):
        assert self._r["version"] == "v10.2"

    def test_status(self):
        assert "GEOMETRIC PREDICTION" in self._r["status"]

    def test_braid_ratio(self):
        assert self._r["key_predictions"]["braid_freq_ratio"] == pytest.approx(35.0 / 74.0, rel=1e-9)

    def test_braid_ratio_exact(self):
        assert "35/74" in self._r["key_predictions"]["braid_freq_ratio_exact"]

    def test_geo_shift_ratio(self):
        assert self._r["key_predictions"]["geo_shift_ratio"] == pytest.approx(5.0 / 74.0, rel=1e-9)

    def test_beat_ratio(self):
        assert self._r["key_predictions"]["beat_ratio"] == pytest.approx(22.0 / 37.0, rel=1e-6)

    def test_for_5ghz_f_braid(self):
        p = self._r["key_predictions"]["for_f_plasma_5ghz"]
        assert p["f_braid_ghz"] == pytest.approx(5.0 * 35.0 / 74.0, rel=1e-6)

    def test_derived_from_geometry_list(self):
        assert len(self._r["derived_from_geometry"]) >= 3

    def test_honest_limitations_list(self):
        assert len(self._r["honest_limitations"]) >= 3

    def test_near_term_proxy(self):
        assert self._r["near_term_proxy"] is True

    def test_litebird_independence(self):
        assert self._r["litebird_independence"] is True

    def test_falsification_present(self):
        assert len(self._r["falsification"]) > 20

    def test_lab_target_present(self):
        assert len(self._r["lab_target"]) > 20


# ===========================================================================
# Cross-consistency checks
# ===========================================================================

class TestCrossConsistency:
    def test_braid_plus_shift_equals_geo(self):
        # f_braid = 35/74, f_geo = 79/74; 79/74 - 35/74 = 44/74 = beat
        shift = geometric_frequency_shift(5.0)
        assert abs(shift["f_geo_ghz"] - shift["f_braid_ghz"]) == pytest.approx(
            shift["f_beat_ghz"], rel=1e-6
        )

    def test_braid_ratio_plus_geo_shift_is_79_over_74(self):
        # (35/74) + (5/74) = 40/74, not 79/74; geo is multiplicative
        # f_geo/f_plasma = 1 + 5/74 = 79/74
        assert 1.0 + GEO_SHIFT_RATIO == pytest.approx(79.0 / 74.0, rel=1e-9)

    def test_xi_c_consistency_physics_and_governance(self):
        # Same constant in both physics (braid) and governance (Pentad)
        from src.governance.resonance_audit import XI_C as XI_C_GOV
        assert XI_C == pytest.approx(XI_C_GOV, rel=1e-9)

    def test_k_cs_consistency(self):
        from src.governance.resonance_audit import K_CS as K_CS_GOV
        assert K_CS == K_CS_GOV

    def test_braid_freq_less_than_plasma(self):
        r = braid_resonance_frequency(5.0)
        assert r["f_braid_ghz"] < 5.0

    def test_geo_freq_greater_than_plasma(self):
        r = geometric_frequency_shift(5.0)
        assert r["f_geo_ghz"] > 5.0

    def test_all_ratios_from_n_w_k_cs(self):
        assert BRAID_FREQ_RATIO == pytest.approx(N_W * N_INV / K_CS, rel=1e-9)
        assert GEO_SHIFT_RATIO == pytest.approx(N_W / K_CS, rel=1e-9)
