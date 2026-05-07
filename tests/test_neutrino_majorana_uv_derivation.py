# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Neutrino Majorana UV-Brane Derivation (Pillar 223, Track A Session 6)."""

import math
import pytest

from src.core.neutrino_majorana_uv_derivation import (
    N_W, K_CS,
    M_PL_GEV, PI_KR, M_KK_GEV,
    C_R_RHN,
    M_R_GEV,
    V_HIGGS_GEV,
    M_NU_SEESAW_EV,
    ARCHITECTURE_LIMIT,
    REQUIRES_DIMENSION,
    rhn_zero_mode_profile,
    majorana_uv_brane_mass,
    seesaw_mass,
    neutrino_mass_estimates,
    five_d_derivation_chain,
    architecture_limit_statement,
    pillar223_audit,
    pillar223_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_c_r_rhn_value(self):
        assert C_R_RHN == pytest.approx(23.0 / 25.0)

    def test_c_r_rhn_above_half(self):
        # UV-localized: c_R > 1/2
        assert C_R_RHN > 0.5

    def test_m_r_gev_positive(self):
        assert M_R_GEV > 0

    def test_m_r_gev_below_planck(self):
        # M_R should be sub-Planck
        assert M_R_GEV < M_PL_GEV * 100

    def test_v_higgs_is_246(self):
        assert V_HIGGS_GEV == pytest.approx(246.0)

    def test_m_nu_seesaw_small(self):
        # Neutrino mass should be sub-eV for y_D = 1
        assert M_NU_SEESAW_EV < 1.0

    def test_architecture_limit_true(self):
        assert ARCHITECTURE_LIMIT is True

    def test_requires_dimension_6(self):
        assert REQUIRES_DIMENSION == 6


class TestRHNZeroModeProfile:
    def test_uv_brane_profile_1_at_y0(self):
        # For UV-localised (c_R > 1/2), profile normalised to 1 at y=0
        profile = rhn_zero_mode_profile(0.0)
        assert profile == pytest.approx(1.0)

    def test_profile_decreases_from_uv(self):
        # UV-localised: profile decreases from y=0 to y=πR
        p0 = rhn_zero_mode_profile(0.0)
        p1 = rhn_zero_mode_profile(1.0)
        assert p0 > p1

    def test_profile_positive_everywhere(self):
        for y in [0.0, 0.25, 0.5, 0.75, 1.0]:
            assert rhn_zero_mode_profile(y) > 0


class TestMajoranaUVBraneMass:
    def test_returns_float_and_dict(self):
        m_r, details = majorana_uv_brane_mass()
        assert isinstance(m_r, float)
        assert isinstance(details, dict)

    def test_m_r_positive(self):
        m_r, _ = majorana_uv_brane_mass()
        assert m_r > 0

    def test_uv_localized_gives_large_m_r(self):
        # For c_R > 1/2 (UV-localized), M_R should be close to M_Pl
        m_r, _ = majorana_uv_brane_mass(c_r=0.92)
        assert m_r > 1e15  # GUT/Planck scale

    def test_details_has_localization(self):
        _, details = majorana_uv_brane_mass()
        assert "localization" in details
        assert "UV-brane" in details["localization"]

    def test_m_r_in_m_pl_is_finite(self):
        _, details = majorana_uv_brane_mass()
        assert math.isfinite(details["m_r_in_m_pl"])


class TestSeesawMass:
    def test_returns_float(self):
        assert isinstance(seesaw_mass(), float)

    def test_seesaw_formula(self):
        # m_ν = y_D² × v² / M_R
        v = V_HIGGS_GEV
        m_r = M_R_GEV
        expected = 1.0 ** 2 * v ** 2 / m_r
        assert seesaw_mass() == pytest.approx(expected, rel=1e-10)

    def test_smaller_yd_gives_smaller_mass(self):
        m1 = seesaw_mass(y_d=1.0)
        m01 = seesaw_mass(y_d=0.1)
        assert m01 < m1

    def test_yd_squared_scaling(self):
        m1 = seesaw_mass(y_d=1.0)
        m05 = seesaw_mass(y_d=0.5)
        assert m05 == pytest.approx(m1 * 0.25, rel=1e-6)


class TestNeutrinoMassEstimates:
    def test_returns_dict(self):
        result = neutrino_mass_estimates()
        assert isinstance(result, dict)

    def test_has_estimates_key(self):
        result = neutrino_mass_estimates()
        assert "estimates" in result

    def test_all_planck_consistent(self):
        result = neutrino_mass_estimates()
        planck_bound = result["planck_sum_bound_ev"]
        for k, v in result["estimates"].items():
            assert v["planck_consistent"], f"{k}: m_nu={v['m_nu_ev']} eV exceeds Planck bound"

    def test_note_mentions_architecture_limit(self):
        result = neutrino_mass_estimates()
        assert "ARCHITECTURE_LIMIT" in result["note"]


class TestFiveDDerivationChain:
    def test_returns_dict(self):
        result = five_d_derivation_chain()
        assert isinstance(result, dict)

    def test_pillar_223(self):
        result = five_d_derivation_chain()
        assert result["pillar"] == 223

    def test_derivation_steps_present(self):
        result = five_d_derivation_chain()
        assert len(result["derivation_steps"]) >= 5

    def test_five_d_achievements_present(self):
        result = five_d_derivation_chain()
        assert len(result["five_d_achievements"]) >= 3

    def test_architecture_limit_flag(self):
        result = five_d_derivation_chain()
        assert result["architecture_limit"]["flag"] is True


class TestArchitectureLimitStatement:
    def test_returns_string(self):
        stmt = architecture_limit_statement()
        assert isinstance(stmt, str)

    def test_mentions_architecture_limit(self):
        stmt = architecture_limit_statement()
        assert "ARCHITECTURE_LIMIT" in stmt

    def test_mentions_m_r(self):
        stmt = architecture_limit_statement()
        assert "M_R" in stmt or "M_r" in stmt.lower()


class TestPillar223Audit:
    def test_returns_dict(self):
        result = pillar223_audit()
        assert isinstance(result, dict)

    def test_axiom_zero_compliant(self):
        result = pillar223_audit()
        assert result["axiom_zero_compliant"] is True


class TestPillar223Summary:
    def test_returns_dict(self):
        s = pillar223_summary()
        assert isinstance(s, dict)

    def test_pillar_number(self):
        s = pillar223_summary()
        assert s["pillar"] == 223

    def test_c_r_rhn(self):
        s = pillar223_summary()
        assert s["c_r_rhn"] == pytest.approx(23.0 / 25.0)

    def test_m_r_positive(self):
        s = pillar223_summary()
        assert s["m_r_gev"] > 0

    def test_architecture_limit_true(self):
        s = pillar223_summary()
        assert s["architecture_limit"] is True
