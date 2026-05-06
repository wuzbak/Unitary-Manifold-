# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_equivalence_principle_guard.py
==========================================
Tests for Pillar 186 — Equivalence Principle Guard (src/core/equivalence_principle_guard.py).

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.core.equivalence_principle_guard import (
    ALPHA_RS1, M_KK_GEV, M_PL_GEV, CASSINI_DGAMMA_LIMIT, EOTVOS_LIMIT,
    AU_METRES, ET_ALPHA_LIMIT,
    ew_radion_yukawa_range, ppn_delta_gamma, ew_radion_cassini_check,
    eotvos_check, radion_mass_frequency_hz, et_scalar_mode_check,
    coupling_origin, ep_guard_summary, pillar186_summary,
)


class TestModuleConstants:
    def test_alpha_rs1_value(self):
        assert ALPHA_RS1 == pytest.approx(1.0 / math.sqrt(6.0), rel=1e-9)

    def test_alpha_rs1_magnitude(self):
        assert 0.4 < ALPHA_RS1 < 0.42

    def test_m_kk_gev(self):
        assert M_KK_GEV == pytest.approx(1040.0, rel=1e-6)

    def test_cassini_limit(self):
        assert CASSINI_DGAMMA_LIMIT == pytest.approx(2.3e-5, rel=1e-6)

    def test_eotvos_limit(self):
        assert EOTVOS_LIMIT == pytest.approx(2.0e-13, rel=1e-6)


class TestEWRadionYukawaRange:
    def test_yukawa_range_finite(self):
        r = ew_radion_yukawa_range()
        assert r["lambda_r_m"] > 0

    def test_yukawa_range_small(self):
        r = ew_radion_yukawa_range()
        # For M_KK = 1040 GeV, lambda_r << 1 AU
        assert r["lambda_r_m"] < 1e-10  # less than 1 angstrom

    def test_au_over_lambda_large(self):
        r = ew_radion_yukawa_range()
        assert r["au_over_lambda"] > 1e20

    def test_yukawa_at_au_zero(self):
        r = ew_radion_yukawa_range()
        assert r["yukawa_at_au"] == pytest.approx(0.0, abs=1e-100)

    def test_force_not_visible_at_au(self):
        r = ew_radion_yukawa_range()
        assert r["force_visible_at_au"] is False

    def test_heavier_mass_shorter_range(self):
        r1 = ew_radion_yukawa_range(1040.0)
        r2 = ew_radion_yukawa_range(2080.0)
        assert r1["lambda_r_m"] > r2["lambda_r_m"]


class TestPPNDeltaGamma:
    def test_delta_gamma_negative(self):
        r = ppn_delta_gamma()
        assert r["delta_gamma"] < 0

    def test_delta_gamma_formula(self):
        alpha = ALPHA_RS1
        expected = -2.0 * alpha**2 / (1.0 + alpha**2)
        r = ppn_delta_gamma(alpha)
        assert r["delta_gamma"] == pytest.approx(expected, rel=1e-9)

    def test_massless_limit_violates_cassini(self):
        # In massless limit, alpha=1/sqrt(6) violates Cassini
        r = ppn_delta_gamma(ALPHA_RS1)
        assert r["violates_cassini"] is True
        assert r["violation_ratio"] > 1.0

    def test_small_alpha_safe(self):
        r = ppn_delta_gamma(1e-6)
        assert r["violates_cassini"] is False

    def test_note_present(self):
        r = ppn_delta_gamma()
        assert "Yukawa" in r["note"] or "massive" in r["note"].lower()


class TestEWRadionCassiniCheck:
    def test_ew_radion_massive_safe(self):
        r = ew_radion_cassini_check()
        assert r["violates_cassini_massive"] is False

    def test_ew_radion_massless_violates(self):
        # Massless limit violates (this is expected — shows why mass is needed)
        r = ew_radion_cassini_check()
        assert r["violates_cassini_massless"] is True

    def test_yukawa_at_au_zero(self):
        r = ew_radion_cassini_check()
        assert r["yukawa_at_1au"] == pytest.approx(0.0, abs=1e-100)

    def test_effective_delta_gamma_zero(self):
        r = ew_radion_cassini_check()
        assert r["delta_gamma_effective"] == pytest.approx(0.0, abs=1e-200)

    def test_verdict_safe(self):
        r = ew_radion_cassini_check()
        assert "SAFE" in r["verdict"]

    def test_screening_mechanism(self):
        r = ew_radion_cassini_check()
        assert "Yukawa" in r["screening_mechanism"] or "mass" in r["screening_mechanism"].lower()

    def test_alpha_origin_not_free(self):
        r = ew_radion_cassini_check()
        assert "NOT" in r["alpha_origin"] or "not" in r["alpha_origin"].lower()


class TestEotvosCheck:
    def test_ew_radion_safe(self):
        r = eotvos_check()
        assert r["violates_eotvos"] is False

    def test_delta_g_over_g_tiny(self):
        r = eotvos_check()
        assert r["delta_g_over_g"] < EOTVOS_LIMIT

    def test_verdict_safe(self):
        r = eotvos_check()
        assert "SAFE" in r["verdict"]

    def test_r_over_lambda_large(self):
        r = eotvos_check()
        assert r["r_over_lambda"] > 1e10


class TestRadionFrequency:
    def test_frequency_positive(self):
        f = radion_mass_frequency_hz()
        assert f > 0

    def test_frequency_very_large(self):
        # TeV-scale mass → very high frequency
        f = radion_mass_frequency_hz(1040.0)
        assert f > 1e20

    def test_heavier_mass_higher_freq(self):
        assert radion_mass_frequency_hz(2000.0) > radion_mass_frequency_hz(1000.0)


class TestETScalarModeCheck:
    def test_not_in_et_band(self):
        r = et_scalar_mode_check()
        assert r["in_et_band"] is False

    def test_above_et_band(self):
        r = et_scalar_mode_check()
        assert r["frequency_above_et"] is True

    def test_frequency_far_above_et(self):
        r = et_scalar_mode_check()
        # Should be many orders of magnitude above ET
        assert r["frequency_hz"] > r["et_band_high_hz"] * 1e15

    def test_verdict_not_in_band(self):
        r = et_scalar_mode_check()
        assert "NOT in ET band" in r["verdict"]


class TestCouplingOrigin:
    def test_not_free_parameter(self):
        r = coupling_origin()
        assert "NO" in r["is_free_parameter"] or "not" in r["is_free_parameter"].lower()

    def test_not_tuned(self):
        r = coupling_origin()
        assert "NO" in r["is_tuned_to_avoid_cassini"]

    def test_alpha_formula(self):
        r = coupling_origin()
        assert "1/√6" in r["alpha_formula"] or "1/sqrt(6)" in r["alpha_formula"]

    def test_source_present(self):
        r = coupling_origin()
        assert "Goldberger" in r["source"] or "Csaki" in r["source"]


class TestEPGuardSummary:
    def setup_method(self):
        self.s = ep_guard_summary()

    def test_pillar_number(self):
        assert self.s["pillar"] == 186

    def test_alpha_not_free(self):
        assert self.s["alpha_is_free_parameter"] is False

    def test_ew_radion_safe(self):
        assert self.s["cassini_check"]["ew_radion_safe"] is True

    def test_de_radion_eliminated(self):
        assert "ELIMINATED" in self.s["cassini_check"]["de_radion_status"]

    def test_eotvos_safe(self):
        assert self.s["eotvos_check"]["ew_radion_safe"] is True

    def test_et_not_in_band(self):
        assert self.s["et_check"]["in_et_band"] is False

    def test_audit_response_closed(self):
        assert "CLOSED" in self.s["audit_response"]

    def test_status_contains_safe(self):
        assert "SAFE" in self.s["status"]

    def test_status_contains_eliminated(self):
        assert "ELIMINATED" in self.s["status"]

    def test_version_v9_39(self):
        assert "9.39" in self.s["version"]
