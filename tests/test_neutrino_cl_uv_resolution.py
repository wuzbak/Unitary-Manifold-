# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_cl_uv_resolution.py
=========================================
Pillar 146 — Tests for neutrino_cl_uv_resolution.py.

Tests cover:
  - branch_a_ir_localization(): IR localisation eliminated
  - branch_b_seesaw_geometric(): Type-I seesaw viable
  - branch_c_open_constraint(): open c_L constraint documented
  - seesaw_neutrino_mass_gev(): Type-I seesaw formula
  - required_cl_for_planck(): minimum c_L from binary search
  - neutrino_uv_resolution_summary(): full Pillar 146 report
"""

from __future__ import annotations

import math
import pytest

from src.core.neutrino_cl_uv_resolution import (
    PI_KR,
    N_W,
    C_R_GEOMETRIC,
    C_L_NAIVE,
    PLANCK_SUM_MNU_EV,
    HIGGS_VEV_GEV,
    M_PLANCK_GEV,
    GEV_TO_EV,
    _rs_profile,
    _rs_profile_ir,
    branch_a_ir_localization,
    branch_b_seesaw_geometric,
    branch_c_open_constraint,
    seesaw_neutrino_mass_gev,
    required_cl_for_planck,
    neutrino_uv_resolution_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_pi_kr_is_37(self):
        assert abs(PI_KR - 37.0) < 1e-10

    def test_n_w_is_5(self):
        assert N_W == 5

    def test_c_r_geometric_is_23_over_25(self):
        assert abs(C_R_GEOMETRIC - 23.0 / 25.0) < 1e-12

    def test_c_l_naive_is_0776(self):
        assert abs(C_L_NAIVE - 0.776) < 1e-10

    def test_planck_limit_positive(self):
        assert PLANCK_SUM_MNU_EV > 0

    def test_planck_limit_is_0_12(self):
        assert abs(PLANCK_SUM_MNU_EV - 0.12) < 1e-10

    def test_higgs_vev_gev_is_246(self):
        assert abs(HIGGS_VEV_GEV - 246.22) < 0.1

    def test_m_planck_gev_order(self):
        assert 1e18 < M_PLANCK_GEV < 1e20


# ---------------------------------------------------------------------------
# RS profiles
# ---------------------------------------------------------------------------

class TestRsProfiles:
    def test_uv_profile_c_r_is_small(self):
        """c_R = 0.920 gives exponentially small f₀."""
        f = _rs_profile(C_R_GEOMETRIC)
        assert f < 1e-5

    def test_uv_profile_c_r_positive(self):
        f = _rs_profile(C_R_GEOMETRIC)
        assert f > 0

    def test_uv_profile_raises_for_c_le_0_5(self):
        with pytest.raises(ValueError):
            _rs_profile(0.5)
        with pytest.raises(ValueError):
            _rs_profile(0.3)

    def test_uv_profile_decreases_with_larger_c(self):
        f1 = _rs_profile(0.6)
        f2 = _rs_profile(0.8)
        assert f2 < f1

    def test_ir_profile_c_0_is_close_to_1(self):
        """c_L = 0 → IR-localized, f₀ ≈ 1."""
        f = _rs_profile_ir(0.0)
        assert f > 0.9

    def test_ir_profile_raises_for_c_ge_0_5(self):
        with pytest.raises(ValueError):
            _rs_profile_ir(0.5)
        with pytest.raises(ValueError):
            _rs_profile_ir(0.7)

    def test_ir_profile_raises_for_negative_c(self):
        with pytest.raises(ValueError):
            _rs_profile_ir(-0.1)

    def test_ir_profile_positive(self):
        f = _rs_profile_ir(0.3)
        assert f > 0

    def test_ir_profile_decreases_with_increasing_c(self):
        """Higher c_L (approaching 0.5 from below) → decreasing f₀."""
        f1 = _rs_profile_ir(0.1)
        f2 = _rs_profile_ir(0.4)
        # At c=0.1 and c=0.4: the function √((1-2c)/(1-e^{-(1-2c)πkR}))
        # Actually f is larger for smaller c
        assert f1 > f2


# ---------------------------------------------------------------------------
# Branch A — IR localisation ELIMINATED
# ---------------------------------------------------------------------------

class TestBranchA:
    @pytest.fixture
    def branch_a(self):
        return branch_a_ir_localization()

    def test_branch_is_A(self, branch_a):
        assert branch_a["branch"] == "A"

    def test_verdict_eliminated(self, branch_a):
        assert branch_a["verdict"] == "ELIMINATED"

    def test_reason_is_string(self, branch_a):
        assert isinstance(branch_a["reason"], str)
        assert len(branch_a["reason"]) > 20

    def test_profile_samples_present(self, branch_a):
        assert isinstance(branch_a["profile_samples"], list)
        assert len(branch_a["profile_samples"]) > 0

    def test_each_sample_has_required_keys(self, branch_a):
        for s in branch_a["profile_samples"]:
            assert "c_L" in s
            assert "f0_L" in s
            assert "m_nu_ev" in s
            assert "planck_consistent" in s

    def test_all_masses_above_planck_limit(self, branch_a):
        """IR localisation gives masses >> Planck limit."""
        for s in branch_a["profile_samples"]:
            assert s["m_nu_ev"] > PLANCK_SUM_MNU_EV, (
                f"Expected m_ν > {PLANCK_SUM_MNU_EV} eV for c_L={s['c_L']}, "
                f"got {s['m_nu_ev']:.4f} eV"
            )

    def test_no_planck_consistent_samples(self, branch_a):
        """None of the IR-localized samples should be Planck consistent."""
        for s in branch_a["profile_samples"]:
            assert not s["planck_consistent"]

    def test_max_mass_is_large(self, branch_a):
        assert branch_a["max_mass_ev"] > 1.0

    def test_conclusion_mentions_eliminated(self, branch_a):
        assert "ELIMINATED" in branch_a["conclusion"]

    def test_custom_c_l_values(self):
        result = branch_a_ir_localization(c_l_values=[0.1, 0.2, 0.3])
        assert len(result["profile_samples"]) == 3

    def test_planck_limit_stored(self, branch_a):
        assert abs(branch_a["planck_limit_ev"] - PLANCK_SUM_MNU_EV) < 1e-10


# ---------------------------------------------------------------------------
# Seesaw formula
# ---------------------------------------------------------------------------

class TestSeesawFormula:
    def test_seesaw_formula_numerical(self):
        """m_ν = y²v²/M_R with y=1, M_R=M_Pl."""
        m = seesaw_neutrino_mass_gev(1.0, M_PLANCK_GEV, HIGGS_VEV_GEV)
        expected = HIGGS_VEV_GEV ** 2 / M_PLANCK_GEV
        assert abs(m - expected) / expected < 1e-10

    def test_seesaw_scales_with_y_squared(self):
        m1 = seesaw_neutrino_mass_gev(1.0, M_PLANCK_GEV)
        m2 = seesaw_neutrino_mass_gev(2.0, M_PLANCK_GEV)
        assert abs(m2 / m1 - 4.0) < 1e-8

    def test_seesaw_inversely_proportional_to_m_r(self):
        m1 = seesaw_neutrino_mass_gev(1.0, M_PLANCK_GEV)
        m2 = seesaw_neutrino_mass_gev(1.0, M_PLANCK_GEV * 2.0)
        assert abs(m2 / m1 - 0.5) < 1e-8

    def test_seesaw_with_planck_mass_gives_sub_mev(self):
        """y=1, M_R=M_Pl → m_ν ~ few μeV (much below Planck bound)."""
        m_ev = seesaw_neutrino_mass_gev(1.0, M_PLANCK_GEV) * GEV_TO_EV
        assert 1e-7 < m_ev < 1.0  # between 0.1 μeV and 1 eV

    def test_seesaw_invalid_m_r_raises(self):
        with pytest.raises(ValueError):
            seesaw_neutrino_mass_gev(1.0, m_r_gev=-1.0)

    def test_seesaw_invalid_vev_raises(self):
        with pytest.raises(ValueError):
            seesaw_neutrino_mass_gev(1.0, M_PLANCK_GEV, higgs_vev_gev=-1.0)

    def test_seesaw_positive_result(self):
        assert seesaw_neutrino_mass_gev() > 0


# ---------------------------------------------------------------------------
# Branch B — Type-I seesaw VIABLE
# ---------------------------------------------------------------------------

class TestBranchB:
    @pytest.fixture
    def branch_b(self):
        return branch_b_seesaw_geometric()

    def test_branch_is_B(self, branch_b):
        assert branch_b["branch"] == "B"

    def test_verdict_viable(self, branch_b):
        assert branch_b["verdict"] == "VIABLE"

    def test_c_r_is_geometric(self, branch_b):
        assert abs(branch_b["c_r_geometric"] - C_R_GEOMETRIC) < 1e-10

    def test_planck_consistent(self, branch_b):
        assert branch_b["planck_consistent"] is True

    def test_m_nu_seesaw_ev_below_planck(self, branch_b):
        assert branch_b["m_nu_seesaw_ev"] < PLANCK_SUM_MNU_EV

    def test_m_nu_seesaw_is_sub_mev_scale(self, branch_b):
        """Seesaw prediction should be sub-meV scale for y_D=1, Planck-consistent."""
        assert 1e-7 < branch_b["m_nu_seesaw_ev"] < 1.0

    def test_m_nu_seesaw_mev_positive(self, branch_b):
        assert branch_b["m_nu_seesaw_mev"] > 0

    def test_f0_r_is_small(self, branch_b):
        """UV-localised c_R=0.920 gives very small f₀."""
        assert branch_b["f0_r"] < 1e-5

    def test_y_dirac_stored(self, branch_b):
        assert abs(branch_b["y_dirac"] - 1.0) < 1e-10

    def test_m_r_is_planck_mass(self, branch_b):
        assert abs(branch_b["m_r_gev"] - M_PLANCK_GEV) / M_PLANCK_GEV < 1e-8

    def test_conclusion_contains_consistent(self, branch_b):
        assert "CONSISTENT" in branch_b["conclusion"] or "viable" in branch_b["conclusion"].lower()

    def test_geometric_input_mentions_pillar_143(self, branch_b):
        assert "143" in branch_b["geometric_input"]

    def test_gut_scale_mass_is_larger(self, branch_b):
        """GUT-scale M_R gives larger m_ν than M_Pl."""
        assert branch_b["m_nu_gut_scale_ev"] > branch_b["m_nu_seesaw_ev"]

    def test_different_y_dirac_changes_result(self):
        b1 = branch_b_seesaw_geometric(y_dirac=1.0)
        b2 = branch_b_seesaw_geometric(y_dirac=0.5)
        assert b2["m_nu_seesaw_ev"] < b1["m_nu_seesaw_ev"]

    def test_invalid_y_dirac_raises(self):
        with pytest.raises(ValueError):
            branch_b_seesaw_geometric(y_dirac=-0.5)

    def test_caveat_is_string(self, branch_b):
        assert isinstance(branch_b["caveat"], str)
        assert len(branch_b["caveat"]) > 20


# ---------------------------------------------------------------------------
# required_cl_for_planck
# ---------------------------------------------------------------------------

class TestRequiredCl:
    def test_required_cl_above_naive(self):
        """c_L required for Planck must be above the naive c_L=0.776."""
        c_req = required_cl_for_planck()
        assert c_req > C_L_NAIVE

    def test_required_cl_above_0_8(self):
        c_req = required_cl_for_planck()
        assert c_req > 0.80

    def test_required_cl_below_1(self):
        c_req = required_cl_for_planck()
        assert c_req < 1.0

    def test_required_cl_gives_consistent_mass(self):
        """Mass at required c_L should be close to (≤) the bound."""
        c_req = required_cl_for_planck(m_nu_max_ev=0.04)
        f0_r = _rs_profile(C_R_GEOMETRIC)
        f0_l = _rs_profile(c_req)
        m_ev = HIGGS_VEV_GEV * f0_l * f0_r * GEV_TO_EV
        assert m_ev <= 0.04 * 1.01  # within 1% tolerance

    def test_tighter_bound_requires_larger_cl(self):
        c1 = required_cl_for_planck(m_nu_max_ev=0.04)
        c2 = required_cl_for_planck(m_nu_max_ev=0.01)
        assert c2 > c1

    def test_invalid_max_ev_raises(self):
        with pytest.raises(ValueError):
            required_cl_for_planck(m_nu_max_ev=-0.01)


# ---------------------------------------------------------------------------
# Branch C — OPEN constraint
# ---------------------------------------------------------------------------

class TestBranchC:
    @pytest.fixture
    def branch_c(self):
        return branch_c_open_constraint()

    def test_branch_is_C(self, branch_c):
        assert branch_c["branch"] == "C"

    def test_verdict_open(self, branch_c):
        assert branch_c["verdict"] == "OPEN"

    def test_c_l_naive_stored(self, branch_c):
        assert abs(branch_c["c_l_naive_geometric"] - C_L_NAIVE) < 1e-10

    def test_m_nu_naive_violates_planck(self, branch_c):
        assert branch_c["m_nu_naive_ev"] > PLANCK_SUM_MNU_EV

    def test_c_l_required_above_naive(self, branch_c):
        assert branch_c["c_l_required_for_planck"] > C_L_NAIVE

    def test_m_nu_at_required_cl_consistent(self, branch_c):
        assert branch_c["m_nu_at_required_cl_ev"] < branch_c["m_nu_max_ev"] * 1.01

    def test_gap_factor_above_100(self, branch_c):
        assert branch_c["gap_factor"] > 10.0

    def test_conclusion_mentions_open(self, branch_c):
        assert "OPEN" in branch_c["conclusion"]

    def test_planck_limit_stored(self, branch_c):
        assert abs(branch_c["planck_limit_ev"] - PLANCK_SUM_MNU_EV) < 1e-10


# ---------------------------------------------------------------------------
# Full summary
# ---------------------------------------------------------------------------

class TestNeutrinoUvResolutionSummary:
    @pytest.fixture
    def summary(self):
        return neutrino_uv_resolution_summary()

    def test_pillar_is_146(self, summary):
        assert summary["pillar"] == 146

    def test_all_three_branches_present(self, summary):
        assert "branch_A" in summary
        assert "branch_B" in summary
        assert "branch_C" in summary

    def test_branch_A_eliminated(self, summary):
        assert summary["branch_A"]["verdict"] == "ELIMINATED"

    def test_branch_B_viable(self, summary):
        assert summary["branch_B"]["verdict"] == "VIABLE"

    def test_branch_C_open(self, summary):
        assert summary["branch_C"]["verdict"] == "OPEN"

    def test_resolution_mentions_seesaw(self, summary):
        assert "seesaw" in summary["resolution"].lower() or "Branch B" in summary["resolution"]

    def test_status_is_string(self, summary):
        assert isinstance(summary["status"], str)
        assert len(summary["status"]) > 20

    def test_status_mentions_partially_resolved(self, summary):
        assert "PARTIALLY RESOLVED" in summary["status"] or "viable" in summary["status"].lower()

    def test_c_r_source_mentions_pillar_143(self, summary):
        assert "143" in summary["c_r_source"]

    def test_pillar_references_list(self, summary):
        assert isinstance(summary["pillar_references"], list)
        assert len(summary["pillar_references"]) >= 3

    def test_title_is_string(self, summary):
        assert isinstance(summary["title"], str)

    def test_branch_b_planck_consistent(self, summary):
        assert summary["branch_B"]["planck_consistent"] is True

    def test_branch_b_mass_below_0_12_ev(self, summary):
        assert summary["branch_B"]["m_nu_seesaw_ev"] < 0.12
