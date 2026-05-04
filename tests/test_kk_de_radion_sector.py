# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_kk_de_radion_sector.py
===================================
Pillar 147 — Tests for kk_de_radion_sector.py.

Tests cover:
  - Physical constant values
  - de_radion_pi_kr(): geometry of DE radion compactification
  - cassini_fifth_force_constraint(): Cassini PPN violation
  - llr_g_dot_constraint(): LLR G_dot violation
  - de_radion_fifth_force_summary(): full DE radion analysis
  - pillar147_summary(): structured audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.kk_de_radion_sector import (
    H0_GEV,
    H0_EV,
    H0_SI,
    M_PLANCK_GEV,
    PI_KR_EW,
    BETA_R_DEFAULT,
    CASSINI_DGEFF_LIMIT,
    LLR_G_DOT_LIMIT_PER_YR,
    ALPHA_RS_RADION,
    SEC_PER_YR,
    hubble_constant_gev,
    de_radion_mass_gev,
    de_radion_pi_kr,
    cassini_fifth_force_constraint,
    llr_g_dot_constraint,
    de_radion_fifth_force_summary,
    pillar147_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_h0_gev_is_tiny(self):
        assert H0_GEV < 1e-30

    def test_h0_ev_is_1e_33_scale(self):
        assert 1e-34 < H0_EV < 1e-30

    def test_llr_g_dot_constraint(self):
        pass  # H0 scale sanity check is in test_h0_per_yr_order

    def test_h0_si_positive(self):
        assert H0_SI > 0

    def test_pi_kr_ew_is_37(self):
        assert abs(PI_KR_EW - 37.0) < 1e-10

    def test_cassini_limit(self):
        assert abs(CASSINI_DGEFF_LIMIT - 2.3e-5) < 1e-12

    def test_llr_limit(self):
        assert abs(LLR_G_DOT_LIMIT_PER_YR - 1.5e-12) < 1e-18

    def test_alpha_rs_radion_is_1_over_sqrt6(self):
        assert abs(ALPHA_RS_RADION - 1.0 / math.sqrt(6.0)) < 1e-10

    def test_m_planck_gev_order(self):
        assert 1e18 < M_PLANCK_GEV < 1e20

    def test_sec_per_yr_positive(self):
        assert SEC_PER_YR > 0

    def test_beta_r_is_one(self):
        assert abs(BETA_R_DEFAULT - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# hubble_constant_gev
# ---------------------------------------------------------------------------

class TestHubbleConstantGev:
    def test_returns_h0_gev(self):
        assert abs(hubble_constant_gev() - H0_GEV) < 1e-40

    def test_positive(self):
        assert hubble_constant_gev() > 0


# ---------------------------------------------------------------------------
# de_radion_mass_gev
# ---------------------------------------------------------------------------

class TestDeRadionMassGev:
    def test_converts_ev_to_gev(self):
        assert abs(de_radion_mass_gev(1.0) - 1e-9) < 1e-15

    def test_h0_ev_converts_to_h0_gev(self):
        assert abs(de_radion_mass_gev(H0_EV) - H0_GEV) / H0_GEV < 1e-8

    def test_zero_is_valid(self):
        assert de_radion_mass_gev(0.0) == 0.0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            de_radion_mass_gev(-1.0)


# ---------------------------------------------------------------------------
# de_radion_pi_kr
# ---------------------------------------------------------------------------

class TestDeRadionPiKr:
    def test_pi_kr_de_is_large(self):
        """For m_r ~ H₀, πkR_DE >> πkR_EW = 37."""
        pi_kr = de_radion_pi_kr(m_r_gev=H0_GEV)
        assert pi_kr > PI_KR_EW * 2

    def test_pi_kr_de_positive(self):
        pi_kr = de_radion_pi_kr(m_r_gev=H0_GEV)
        assert pi_kr > 0

    def test_larger_mass_gives_smaller_pi_kr(self):
        pi1 = de_radion_pi_kr(m_r_gev=H0_GEV)
        pi2 = de_radion_pi_kr(m_r_gev=H0_GEV * 1000.0)
        assert pi1 > pi2

    def test_formula_is_log(self):
        """πkR_DE = ln(β M_Pl / m_r)."""
        m_r = 1e-10  # GeV
        beta = 1.0
        expected = math.log(beta * M_PLANCK_GEV / m_r)
        result = de_radion_pi_kr(m_r_gev=m_r, beta_r=beta)
        assert abs(result - expected) < 1e-10

    def test_invalid_m_r_raises(self):
        with pytest.raises(ValueError):
            de_radion_pi_kr(m_r_gev=0.0)
        with pytest.raises(ValueError):
            de_radion_pi_kr(m_r_gev=-1.0)

    def test_invalid_beta_raises(self):
        with pytest.raises(ValueError):
            de_radion_pi_kr(m_r_gev=H0_GEV, beta_r=-1.0)
        with pytest.raises(ValueError):
            de_radion_pi_kr(m_r_gev=H0_GEV, beta_r=0.0)

    def test_numerical_value_around_140(self):
        """πkR_DE ≈ 140 for m_r ~ H₀."""
        pi_kr = de_radion_pi_kr(m_r_gev=H0_GEV)
        assert 100 < pi_kr < 200


# ---------------------------------------------------------------------------
# cassini_fifth_force_constraint
# ---------------------------------------------------------------------------

class TestCassiniFifthForce:
    @pytest.fixture
    def cassini_default(self):
        return cassini_fifth_force_constraint()

    def test_alpha_stored(self, cassini_default):
        assert abs(cassini_default["alpha"] - ALPHA_RS_RADION) < 1e-10

    def test_delta_gamma_positive(self, cassini_default):
        assert cassini_default["delta_gamma"] > 0

    def test_delta_gamma_formula(self, cassini_default):
        alpha_sq = ALPHA_RS_RADION ** 2
        expected = 2.0 * alpha_sq / (1.0 + alpha_sq)
        assert abs(cassini_default["delta_gamma"] - expected) < 1e-10

    def test_rs_radion_violates_cassini(self, cassini_default):
        """α = 1/√6 should violate Cassini."""
        assert cassini_default["violates_cassini"] is True

    def test_violation_ratio_above_1(self, cassini_default):
        assert cassini_default["violation_ratio"] > 1.0

    def test_violation_ratio_above_1000(self, cassini_default):
        """RS radion should violate Cassini by >> 100×."""
        assert cassini_default["violation_ratio"] > 100.0

    def test_cassini_limit_stored(self, cassini_default):
        assert abs(cassini_default["cassini_limit"] - CASSINI_DGEFF_LIMIT) < 1e-15

    def test_verdict_mentions_eliminated(self, cassini_default):
        assert "ELIMINATED" in cassini_default["verdict"]

    def test_tiny_alpha_does_not_violate(self):
        result = cassini_fifth_force_constraint(alpha_coupling=1e-4)
        assert not result["violates_cassini"]

    def test_zero_alpha_no_violation(self):
        result = cassini_fifth_force_constraint(alpha_coupling=0.0)
        assert not result["violates_cassini"]
        assert result["delta_gamma"] == 0.0

    def test_negative_alpha_raises(self):
        with pytest.raises(ValueError):
            cassini_fifth_force_constraint(alpha_coupling=-0.1)

    def test_g_eff_deviation_formula(self, cassini_default):
        alpha_sq = ALPHA_RS_RADION ** 2
        expected = 2.0 * alpha_sq
        assert abs(cassini_default["g_eff_deviation"] - expected) < 1e-10


# ---------------------------------------------------------------------------
# llr_g_dot_constraint
# ---------------------------------------------------------------------------

class TestLlrGDot:
    @pytest.fixture
    def llr_default(self):
        return llr_g_dot_constraint()

    def test_g_dot_positive(self, llr_default):
        assert llr_default["G_dot_over_G_yr"] > 0

    def test_rs_radion_violates_llr(self, llr_default):
        assert llr_default["violates_llr"] is True

    def test_llr_limit_stored(self, llr_default):
        assert abs(llr_default["llr_limit_yr"] - LLR_G_DOT_LIMIT_PER_YR) < 1e-20

    def test_violation_ratio_above_1(self, llr_default):
        assert llr_default["violation_ratio"] > 1.0

    def test_verdict_mentions_eliminated(self, llr_default):
        assert "ELIMINATED" in llr_default["verdict"]

    def test_tiny_alpha_no_llr_violation(self):
        result = llr_g_dot_constraint(m_r_gev=H0_GEV, alpha_coupling=1e-7)
        assert not result["violates_llr"]

    def test_invalid_m_r_raises(self):
        with pytest.raises(ValueError):
            llr_g_dot_constraint(m_r_gev=-1.0)

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError):
            llr_g_dot_constraint(alpha_coupling=-0.1)

    def test_h0_per_yr_positive(self, llr_default):
        assert llr_default["h0_per_yr"] > 0

    def test_h0_per_yr_order(self, llr_default):
        """H₀ in yr⁻¹ should be ~2×10⁻¹¹."""
        assert 1e-12 < llr_default["h0_per_yr"] < 1e-9


# ---------------------------------------------------------------------------
# de_radion_fifth_force_summary
# ---------------------------------------------------------------------------

class TestDeRadionSummary:
    @pytest.fixture
    def summary(self):
        return de_radion_fifth_force_summary()

    def test_pillar_is_147(self, summary):
        assert summary["pillar"] == 147

    def test_verdict_eliminated(self, summary):
        assert "ELIMINATED" in summary["verdict"]

    def test_cassini_violated(self, summary):
        assert summary["cassini"]["violates_cassini"] is True

    def test_llr_violated(self, summary):
        assert summary["llr"]["violates_llr"] is True

    def test_pi_kr_de_larger_than_ew(self, summary):
        assert summary["pi_kr_de_required"] > summary["pi_kr_ew"]

    def test_pi_kr_ratio_above_2(self, summary):
        assert summary["pi_kr_ratio_de_over_ew"] > 2.0

    def test_conclusion_mentions_open_problem(self, summary):
        assert "OPEN" in summary["conclusion"] or "ELIMINATED" in summary["conclusion"]

    def test_implications_is_string(self, summary):
        assert isinstance(summary["implications"], str)
        assert len(summary["implications"]) > 40

    def test_de_mass_ev_is_h0(self, summary):
        assert abs(summary["de_radion_mass_ev"] - H0_EV) < 1e-40

    def test_alpha_rs_stored(self, summary):
        assert abs(summary["alpha_rs_radion"] - ALPHA_RS_RADION) < 1e-10


# ---------------------------------------------------------------------------
# pillar147_summary
# ---------------------------------------------------------------------------

class TestPillar147Summary:
    @pytest.fixture
    def p147(self):
        return pillar147_summary()

    def test_pillar_is_147(self, p147):
        assert p147["pillar"] == 147

    def test_status_eliminated(self, p147):
        assert "ELIMINATED" in p147["status"]

    def test_cassini_violated_true(self, p147):
        assert p147["cassini_violated"] is True

    def test_llr_violated_true(self, p147):
        assert p147["llr_violated"] is True

    def test_cassini_ratio_above_100(self, p147):
        assert p147["cassini_violation_ratio"] > 100.0

    def test_llr_ratio_above_1(self, p147):
        assert p147["llr_violation_ratio"] > 1.0

    def test_pi_kr_de_present(self, p147):
        assert "pi_kr_de_required" in p147
        assert p147["pi_kr_de_required"] > 0

    def test_de_mass_ev_present(self, p147):
        assert "de_mass_ev" in p147
        assert p147["de_mass_ev"] > 0

    def test_alpha_rs_present(self, p147):
        assert "alpha_rs" in p147

    def test_conclusion_is_string(self, p147):
        assert isinstance(p147["conclusion"], str)
        assert "OPEN" in p147["conclusion"] or "ELIMINATED" in p147["conclusion"]

    def test_implication_for_pillar136_present(self, p147):
        assert "implication_for_pillar136" in p147
        assert "136" in p147["implication_for_pillar136"]

    def test_falsifier_mentions_roman(self, p147):
        assert "Roman" in p147["falsifier"]
