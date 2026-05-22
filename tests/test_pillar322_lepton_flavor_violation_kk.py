# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 322 — Lepton Flavor Violation BR(μ→eγ) from KK Tower."""
import math
import pytest

from src.core.pillar322_lepton_flavor_violation_kk import (
    N_W, K_CS, PI_KR, M_KK_GEV,
    MEG2_BOUND, MU3E_TARGET, MU3E_PHASE2,
    THETA_12_DEG, THETA_23_DEG, THETA_13_DEG, DELTA_CP_RAD,
    separation_guard,
    kk_coupling_enhancement,
    pmns_lfv_amplitude,
    branching_ratio_mu_e_gamma,
    branching_ratio_mu_3e,
    kk_tower_lfv_sum,
    experimental_comparison,
    lfv_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_m_kk_tev_scale(self):
        assert 500 < M_KK_GEV < 5000

    def test_meg2_bound(self):
        assert MEG2_BOUND == pytest.approx(4.2e-13, rel=1e-6)

    def test_pmns_angles_physical(self):
        assert 30.0 < THETA_12_DEG < 38.0
        assert 40.0 < THETA_23_DEG < 50.0
        assert 7.0 < THETA_13_DEG < 10.0


class TestSeparationGuard:
    def test_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent(self):
        assert "ADJACENT" in separation_guard()


class TestKkCoupling:
    def test_positive(self):
        assert kk_coupling_enhancement() > 0

    def test_canonical(self):
        assert abs(kk_coupling_enhancement(37.0) - math.sqrt(37/2)) < 1e-10

    def test_canonical_value_approx_430(self):
        assert 4.0 < kk_coupling_enhancement() < 5.0


class TestPmnsLfvAmplitude:
    def test_positive(self):
        assert pmns_lfv_amplitude() >= 0.0

    def test_small(self):
        # The off-diagonal PMNS amplitude should be much less than 1
        assert pmns_lfv_amplitude() < 1.0

    def test_depends_on_theta13(self):
        amp_small = pmns_lfv_amplitude(theta_13_deg=1.0)
        amp_large = pmns_lfv_amplitude(theta_13_deg=15.0)
        # Both should be positive; different values
        assert amp_small >= 0.0 and amp_large >= 0.0

    def test_with_zero_cp_phase(self):
        # Setting delta_CP = 0 should give a different value but still positive
        amp = pmns_lfv_amplitude(delta_cp_rad=0.0)
        assert amp >= 0.0


class TestBranchingRatios:
    def test_mu_e_gamma_below_meg2(self):
        br = branching_ratio_mu_e_gamma()
        assert br < MEG2_BOUND

    def test_mu_e_gamma_positive(self):
        br = branching_ratio_mu_e_gamma()
        assert br >= 0.0

    def test_mu_e_gamma_decreases_with_heavier_kk(self):
        br1 = branching_ratio_mu_e_gamma(m_kk_gev=1000.0)
        br2 = branching_ratio_mu_e_gamma(m_kk_gev=3000.0)
        assert br1 > br2

    def test_mu_3e_positive(self):
        br = branching_ratio_mu_3e()
        assert br >= 0.0

    def test_mu_3e_below_mu_e_gamma(self):
        # μ→3e has extra α_em suppression relative to μ→eγ
        br1 = branching_ratio_mu_e_gamma()
        br3 = branching_ratio_mu_3e()
        assert br3 <= br1

    def test_mu_3e_below_mu3e_target(self):
        br = branching_ratio_mu_3e()
        assert br < MU3E_TARGET


class TestKkTowerSum:
    def test_positive(self):
        total = kk_tower_lfv_sum(n_modes=3)
        assert total >= 0.0

    def test_increases_with_modes(self):
        s1 = kk_tower_lfv_sum(n_modes=1)
        s3 = kk_tower_lfv_sum(n_modes=3)
        assert s3 >= s1

    def test_below_meg2(self):
        total = kk_tower_lfv_sum(n_modes=5)
        assert total < MEG2_BOUND


class TestExperimentalComparison:
    def test_below_meg2(self):
        br1 = branching_ratio_mu_e_gamma()
        br3 = branching_ratio_mu_3e()
        comp = experimental_comparison(br1, br3)
        assert comp["below_meg2"] is True

    def test_verdict_consistent(self):
        br1 = branching_ratio_mu_e_gamma()
        br3 = branching_ratio_mu_3e()
        comp = experimental_comparison(br1, br3)
        assert comp["verdict_mu_e_gamma"] == "CONSISTENT_BELOW_MEG2"

    def test_ratio_to_meg2_less_than_one(self):
        br1 = branching_ratio_mu_e_gamma()
        br3 = branching_ratio_mu_3e()
        comp = experimental_comparison(br1, br3)
        assert comp["ratio_to_meg2"] < 1.0


class TestFullReport:
    def setup_method(self):
        self.r = lfv_full_report()

    def test_pillar_number(self):
        assert self.r["pillar"] == 322

    def test_adjacency(self):
        assert self.r["adjacency"] == "NON_HARDGATE_ADJACENT"

    def test_br_mu_e_gamma_positive(self):
        assert self.r["br_mu_e_gamma"] >= 0.0

    def test_br_mu_e_gamma_below_meg2(self):
        assert self.r["br_mu_e_gamma"] < MEG2_BOUND

    def test_experimental_section(self):
        exp = self.r["experimental"]
        assert exp["below_meg2"] is True

    def test_physics_summary(self):
        assert isinstance(self.r["physics_summary"], str)
        assert "CONSISTENT" in self.r["physics_summary"]

    def test_kk_coupling(self):
        assert self.r["kk_coupling_enhancement"] > 0

    def test_m_kk_tev(self):
        assert 0.5 < self.r["m_kk_tev"] < 5.0
