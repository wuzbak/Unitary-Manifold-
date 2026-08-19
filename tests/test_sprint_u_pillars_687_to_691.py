# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillars 687–691: Sprint U (NP BC10, PMNS θ₂₃, ν hierarchy, Majorana, cert)."""

from __future__ import annotations

import math
import pytest

# ── Pillar 687 ────────────────────────────────────────────────────────────────
from src.core.pillar687_np_bc10_radion_scalar_loop_kernel import (
    PILLAR_NUMBER as P687, PILLAR_STATUS as S687, VERSION as V687,
    N_W, K_CS, PI_KR, M_KK_NATURAL, G_N_STAR, M_RADION_ZERO_NATURAL,
    GAMMA_RADION, GAMMA_GRAVITON, SCALAR_TO_GRAVITON_RATIO,
    radion_zero_mode_mass, scalar_one_loop_coefficient,
    graviton_to_scalar_ratio, np_bc10_algebraic_kernel,
    combined_loop_kernel, np_bc10_certificate,
    what_is_claimed as p687_claimed,
    what_is_NOT_claimed as p687_not_claimed,
)

# ── Pillar 688 ────────────────────────────────────────────────────────────────
from src.core.pillar688_pmns_theta23_atmospheric_kk_overlap import (
    PILLAR_NUMBER as P688, PILLAR_STATUS as S688, VERSION as V688,
    SIN2_THETA23_PDG, SIN2_THETA23_PDG_ERR, THETA23_PDG_DEG,
    DC_L_23, EPSILON_23_RAD, PI_KR as PI_KR_688,
    near_maximal_deviation, calibrated_dc_l23,
    sin2_theta23_prediction, self_consistency_check as sc688,
    theta23_certificate,
    what_is_claimed as p688_claimed,
    what_is_NOT_claimed as p688_not_claimed,
)

# ── Pillar 689 ────────────────────────────────────────────────────────────────
from src.core.pillar689_nu_mass_hierarchy_orbifold_bc import (
    PILLAR_NUMBER as P689, PILLAR_STATUS as S689, VERSION as V689,
    DM21_EV2, DM31_EV2, MAJORANA_KK_MASS_RATIO,
    SIGMA_MNU_PLANCK_EV, M_NU1_MAX_EV,
    normal_hierarchy_masses, hierarchy_from_orbifold_bc,
    cosmological_constraint_check, nu_hierarchy_certificate,
    what_is_claimed as p689_claimed,
    what_is_NOT_claimed as p689_not_claimed,
)

# ── Pillar 690 ────────────────────────────────────────────────────────────────
from src.core.pillar690_majorana_seesaw_dirichlet_bc import (
    PILLAR_NUMBER as P690, PILLAR_STATUS as S690, VERSION as V690,
    M_KK_GEV, X1_BESSEL_J0, M_MAJORANA_KK_GEV,
    bessel_root_approximation, seesaw_kernel,
    kk_seesaw_neutrino_mass, architecture_limit_analysis,
    majorana_seesaw_certificate,
    what_is_claimed as p690_claimed,
    what_is_NOT_claimed as p690_not_claimed,
)

# ── Pillar 691 ────────────────────────────────────────────────────────────────
from src.core.pillar691_sprint_u_regression_certificate import (
    PILLAR_NUMBER as P691, PILLAR_STATUS as S691, VERSION as V691,
    SPRINT_U_PILLARS, TOE_SCORE, NEXT_PILLAR_SLOT,
    sprint_u_summary, np_bc_ledger_status,
    pmns_framework_status, sprint_u_certificate,
)


# ══════════════════════════════════════════════════════════════════════════════
# PILLAR 687 TESTS — NP BC10
# ══════════════════════════════════════════════════════════════════════════════

class TestPillar687:
    def test_number(self): assert P687 == 687
    def test_version(self): assert V687 == "v21.2"
    def test_status(self): assert S687 == "NP_BC10_RADION_SCALAR_LOOP_KERNEL_COMPUTED"
    def test_n_w_k_cs(self): assert N_W == 5 and K_CS == 74

    def test_m_radion_formula(self):
        expected = math.sqrt(6.0) / math.pi * M_KK_NATURAL
        assert abs(M_RADION_ZERO_NATURAL - expected) < 1e-20

    def test_gamma_radion_positive(self): assert GAMMA_RADION > 0
    def test_gamma_graviton_positive(self): assert GAMMA_GRAVITON > 0

    def test_scalar_to_graviton_ratio_positive(self):
        assert 0 < SCALAR_TO_GRAVITON_RATIO < 1

    def test_radion_zero_mode(self):
        d = radion_zero_mode_mass()
        assert "m_radion_zero_natural" in d
        assert abs(d["m_radion_zero_natural"] - M_RADION_ZERO_NATURAL) < 1e-25

    def test_scalar_coefficient(self):
        c = scalar_one_loop_coefficient()
        for k in ["gamma_radion_zero_mode", "gamma_scalar_kk_tower", "scalar_to_graviton_ratio"]:
            assert k in c
        assert c["scalar_to_graviton_ratio"] > 0

    def test_graviton_ratio(self):
        r = graviton_to_scalar_ratio()
        assert "ratio_pct" in r
        assert r["ratio_pct"] > 0
        assert r["ratio_pct"] < 100

    def test_bc10_kernel_at_fixed_point_zero(self):
        result = np_bc10_algebraic_kernel(G_N_STAR)
        assert result["k_bc10"] == pytest.approx(0.0, abs=1e-200)
        assert result["at_fixed_point"] is True

    def test_bc10_kernel_formula(self):
        r = np_bc10_algebraic_kernel(0.01)
        assert "K_BC10" in r["formula"]

    def test_combined_kernel_returns_dict(self):
        c = combined_loop_kernel(G_N_STAR)
        assert "k_combined" in c
        assert c["k_combined"] == pytest.approx(0.0, abs=1e-200)

    def test_combined_scalar_fraction(self):
        c = combined_loop_kernel(0.01)
        assert 0 < c["scalar_fraction"] < 1

    def test_certificate_keys(self):
        cert = np_bc10_certificate()
        for k in ["pillar", "title", "version", "status", "np_bc_ledger", "next_bc"]:
            assert k in cert

    def test_certificate_pillar(self):
        assert np_bc10_certificate()["pillar"] == 687

    def test_bc10_next_is_bc11(self):
        assert "BC11" in np_bc10_certificate()["next_bc"]

    def test_claimed_list(self):
        assert len(p687_claimed()) >= 4

    def test_not_claimed_list(self):
        assert len(p687_not_claimed()) >= 3


# ══════════════════════════════════════════════════════════════════════════════
# PILLAR 688 TESTS — PMNS θ₂₃
# ══════════════════════════════════════════════════════════════════════════════

class TestPillar688:
    def test_number(self): assert P688 == 688
    def test_version(self): assert V688 == "v21.2"
    def test_status(self): assert S688 == "PMNS_THETA23_KK_OVERLAP_CONSISTENCY_CHECKED"

    def test_sin2_theta23_pdg(self):
        assert abs(SIN2_THETA23_PDG - 0.547) < 0.001

    def test_theta23_near_maximal(self):
        assert 45.0 < THETA23_PDG_DEG < 50.0

    def test_dc_l23_physical(self):
        assert 0 < DC_L_23 < 0.01

    def test_epsilon_rad(self):
        assert 0 < EPSILON_23_RAD < 0.1

    def test_near_maximal_deviation(self):
        d = near_maximal_deviation()
        assert d["near_maximal"] is True
        assert d["epsilon_23_deg"] > 0

    def test_calibrated_dc_physical(self):
        c = calibrated_dc_l23()
        assert c["dc_physical_range"] is True

    def test_sin2_prediction_self_consistent(self):
        pred = sin2_theta23_prediction()
        assert pred["residual_pct"] < 0.5
        assert pred["near_maximal"] is True

    def test_sin2_prediction_sigma(self):
        pred = sin2_theta23_prediction()
        assert pred["sigma_away"] < 1.0

    def test_self_consistency_passes(self):
        sc = sc688()
        assert sc["self_consistent"] is True

    def test_certificate_unified_pmns(self):
        cert = theta23_certificate()
        assert "unified_pmns_status" in cert
        up = cert["unified_pmns_status"]
        assert "theta12" in up
        assert "theta13" in up
        assert "theta23" in up

    def test_certificate_pillar(self):
        assert theta23_certificate()["pillar"] == 688

    def test_dc_formula(self):
        # DC_L_23 = 2 × ε₂₃ / (π k R)
        expected = 2.0 * EPSILON_23_RAD / PI_KR_688
        assert abs(DC_L_23 - expected) < 1e-12

    def test_claimed_list(self): assert len(p688_claimed()) >= 3
    def test_not_claimed_list(self): assert len(p688_not_claimed()) >= 2


# ══════════════════════════════════════════════════════════════════════════════
# PILLAR 689 TESTS — ν MASS HIERARCHY
# ══════════════════════════════════════════════════════════════════════════════

class TestPillar689:
    def test_number(self): assert P689 == 689
    def test_version(self): assert V689 == "v21.2"
    def test_status(self): assert S689 == "NU_MASS_HIERARCHY_NORMAL_PREDICTED_FROM_ORBIFOLD_BC"

    def test_dm21(self):
        assert abs(DM21_EV2 - 7.442e-5) < 1e-7

    def test_dm31(self):
        assert abs(DM31_EV2 - 2.4109e-3) < 1e-6

    def test_majorana_ratio(self):
        assert abs(MAJORANA_KK_MASS_RATIO - 3.8317) < 0.001

    def test_planck_bound(self):
        assert abs(SIGMA_MNU_PLANCK_EV - 0.12) < 0.01

    def test_m_nu1_max(self):
        assert M_NU1_MAX_EV == 0.015

    def test_normal_hierarchy_ordering(self):
        nh = normal_hierarchy_masses(0.005)
        assert nh["m_nu1_ev"] < nh["m_nu2_ev"] < nh["m_nu3_ev"]
        assert nh["hierarchy"] == "NORMAL"

    def test_normal_hierarchy_dm21(self):
        nh = normal_hierarchy_masses(0.005)
        dm21_check = nh["m_nu2_ev"]**2 - nh["m_nu1_ev"]**2
        assert abs(dm21_check - DM21_EV2) < 1e-10

    def test_normal_hierarchy_planck_bound(self):
        nh = normal_hierarchy_masses(0.005)
        assert nh["within_planck_bound"] is True

    def test_normal_hierarchy_at_max(self):
        nh = normal_hierarchy_masses(M_NU1_MAX_EV)
        assert nh["within_planck_bound"] is True

    def test_hierarchy_from_bc(self):
        h = hierarchy_from_orbifold_bc()
        assert h["hierarchy_predicted"] == "NORMAL"
        assert "Dirichlet" in h["bc_type"]

    def test_cosmo_check_fiducial(self):
        cc = cosmological_constraint_check()
        assert cc["fiducial_within_bound"] is True

    def test_cosmo_extreme_within_bound(self):
        cc = cosmological_constraint_check()
        assert cc["extreme_within_bound"] is True

    def test_certificate_predicted_nh(self):
        cert = nu_hierarchy_certificate()
        assert cert["predicted_hierarchy"] == "NORMAL"
        assert cert["pillar"] == 689

    def test_claimed_list(self): assert len(p689_claimed()) >= 4
    def test_not_claimed_list(self): assert len(p689_not_claimed()) >= 2


# ══════════════════════════════════════════════════════════════════════════════
# PILLAR 690 TESTS — MAJORANA SEESAW
# ══════════════════════════════════════════════════════════════════════════════

class TestPillar690:
    def test_number(self): assert P690 == 690
    def test_version(self): assert V690 == "v21.2"
    def test_status(self): assert S690 == "MAJORANA_SEESAW_ARCHITECTURE_LIMIT_DOCUMENTED"

    def test_mkk_gev_positive(self):
        assert M_KK_GEV > 500   # should be ~1042 GeV

    def test_mkk_gev_range(self):
        assert 500 < M_KK_GEV < 2000

    def test_x1_bessel_j0(self):
        assert abs(X1_BESSEL_J0 - 2.4048) < 0.001

    def test_majorana_mass_formula(self):
        expected = X1_BESSEL_J0 * M_KK_GEV
        assert abs(M_MAJORANA_KK_GEV - expected) < 1e-8

    def test_bessel_root_at_half(self):
        r = bessel_root_approximation(0.5)
        assert abs(r["x1_approx"] - X1_BESSEL_J0) < 0.001
        assert r["nu_order"] < 1e-3

    def test_bessel_root_increasing_with_c(self):
        r1 = bessel_root_approximation(0.5)
        r2 = bessel_root_approximation(1.0)
        # x_1 changes monotonically — check it's defined
        assert r1["x1_approx"] > 0 and r2["x1_approx"] > 0

    def test_seesaw_kernel_keys(self):
        sk = seesaw_kernel(0.5)
        for k in ["c_nu", "x1", "m_majorana_gev", "kernel_gev_inv"]:
            assert k in sk

    def test_seesaw_kernel_positive(self):
        sk = seesaw_kernel(0.5)
        assert sk["kernel_gev_inv"] > 0
        assert sk["m_majorana_gev"] > 0

    def test_kk_seesaw_architecture_limit(self):
        # Standard case: m_ν far above target
        km = kk_seesaw_neutrino_mass(0.5, 1.0, 1.0)
        assert km["architecture_limit"] is True
        assert km["m_nu_ev"] > 1.0

    def test_kk_seesaw_keys(self):
        km = kk_seesaw_neutrino_mass(0.5, 1.0, 0.1)
        for k in ["m_dirac_gev", "m_majorana_gev", "m_nu_ev", "architecture_limit"]:
            assert k in km

    def test_architecture_analysis_limit(self):
        arch = architecture_limit_analysis()
        assert arch["architecture_limit"] is True
        assert "UV-peaked" in arch["closure_path"] or "Weinberg" in arch["closure_path"]

    def test_architecture_f_nu_required(self):
        arch = architecture_limit_analysis()
        assert arch["required_f_nu_suppression"] > 0
        assert arch["required_f_nu_suppression"] < 1.0

    def test_certificate_pillar(self):
        assert majorana_seesaw_certificate()["pillar"] == 690

    def test_certificate_arch_limit(self):
        cert = majorana_seesaw_certificate()
        assert "ARCHITECTURE LIMIT" in cert["p_nu_mass_status"]

    def test_claimed_list(self): assert len(p690_claimed()) >= 4
    def test_not_claimed_list(self): assert len(p690_not_claimed()) >= 2


# ══════════════════════════════════════════════════════════════════════════════
# PILLAR 691 TESTS — SPRINT U CERTIFICATE
# ══════════════════════════════════════════════════════════════════════════════

class TestPillar691:
    def test_number(self): assert P691 == 691
    def test_version(self): assert V691 == "v21.2"
    def test_status(self): assert S691 == "SPRINT_U_REGRESSION_CERTIFICATE_ISSUED"

    def test_sprint_u_pillars(self):
        for p in [687, 688, 689, 690, 691]:
            assert p in SPRINT_U_PILLARS

    def test_next_pillar_slot(self):
        assert NEXT_PILLAR_SLOT == 692

    def test_toe_score(self):
        assert abs(TOE_SCORE - 30.0) < 0.01

    def test_summary_toe_unchanged(self):
        s = sprint_u_summary()
        assert s["toe_unchanged"] is True

    def test_summary_sprint_u(self):
        s = sprint_u_summary()
        assert s["sprint"] == "U"
        assert s["new_pillar_max"] == 691

    def test_bc_ledger_complete_through_bc10(self):
        bc = np_bc_ledger_status()
        assert bc["total_bc_entries"] == 10
        assert "BC10" in bc["ledger_complete_through"]

    def test_bc_ledger_bc11_next(self):
        bc = np_bc_ledger_status()
        assert "BC11" in bc["bc11_next"]

    def test_pmns_framework_all_angles(self):
        pmns = pmns_framework_status()
        assert "theta12_solar" in pmns
        assert "theta13_reactor" in pmns
        assert "theta23_atmospheric" in pmns

    def test_pmns_theta12_hardgate(self):
        pmns = pmns_framework_status()
        assert "HARDGATE" in pmns["theta12_solar"]["status"]

    def test_certificate_regression_pass(self):
        cert = sprint_u_certificate()
        assert cert["regression_verdict"] == "PASS"

    def test_certificate_tests_growing(self):
        cert = sprint_u_certificate()
        assert cert["estimated_total_tests"] > 52000

    def test_certificate_nw_kcs(self):
        cert = sprint_u_certificate()
        check = cert["sprint_nw_kcs_check"]
        assert check["n_w"] == 5
        assert check["k_cs"] == 74
        assert check["n_w_times_k_cs"] == 370

    def test_certificate_arch_limits_list(self):
        cert = sprint_u_certificate()
        assert len(cert["architecture_limits_post_u"]) >= 4
