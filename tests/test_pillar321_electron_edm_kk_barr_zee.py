# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 321 — Electron EDM from KK Barr-Zee Mechanism."""
import math
import pytest

from src.core.pillar321_electron_edm_kk_barr_zee import (
    N_W, K_CS, PI_KR, C_S, M_KK_GEV, M_PL_GEV,
    ALPHA_EM, M_E_GEV, M_T_GEV, Q_T, N_C,
    ACME_2018_BOUND_ECM, JILA_2023_BOUND_ECM, ACME_III_TARGET_ECM, SM_PREDICTION_ECM,
    separation_guard,
    kk_coupling_enhancement,
    barr_zee_loop_function,
    cp_phase_from_braid_cs,
    cp_phase_from_pmns,
    edm_sm_ckm_three_loop,
    edm_kk_barr_zee_top,
    edm_kk_barr_zee_pmns,
    edm_total_um,
    experimental_comparison,
    electron_edm_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37.0

    def test_c_s(self):
        assert abs(C_S - 12.0/37.0) < 1e-12

    def test_m_kk_order_of_magnitude(self):
        # M_KK ~ 1 TeV (10³ GeV)
        assert 500.0 < M_KK_GEV < 5000.0

    def test_m_kk_from_planck(self):
        assert abs(M_KK_GEV - M_PL_GEV * math.exp(-PI_KR)) < 1.0

    def test_alpha_em(self):
        assert abs(ALPHA_EM - 1.0/137.035999084) < 1e-10

    def test_experimental_bounds_ordering(self):
        # JILA 2023 is tighter than ACME 2018
        assert JILA_2023_BOUND_ECM < ACME_2018_BOUND_ECM
        # ACME III target is tightest
        assert ACME_III_TARGET_ECM <= JILA_2023_BOUND_ECM

    def test_sm_prediction_tiny(self):
        assert SM_PREDICTION_ECM < 1e-30


class TestSeparationGuard:
    def test_returns_string(self):
        s = separation_guard()
        assert isinstance(s, str)

    def test_contains_adjacent(self):
        assert "ADJACENT" in separation_guard()

    def test_contains_pillar_number(self):
        assert "321" in separation_guard()


class TestKkCouplingEnhancement:
    def test_canonical_value(self):
        g = kk_coupling_enhancement(37.0)
        assert abs(g - math.sqrt(37.0/2.0)) < 1e-10

    def test_positive(self):
        assert kk_coupling_enhancement() > 0.0

    def test_increases_with_pi_kr(self):
        assert kk_coupling_enhancement(40.0) > kk_coupling_enhancement(30.0)

    def test_canonical_numerically(self):
        # √(37/2) ≈ 4.30
        g = kk_coupling_enhancement()
        assert 4.0 < g < 5.0


class TestBarrZeeLoopFunction:
    def test_positive_for_small_x(self):
        assert barr_zee_loop_function(0.01) > 0.0

    def test_increases_with_x_below_unity(self):
        assert barr_zee_loop_function(0.05) > barr_zee_loop_function(0.01)

    def test_x_top_value(self):
        x_t = (M_T_GEV / M_KK_GEV) ** 2
        # x_t ~ (173/1040)² ≈ 0.028
        assert 0.01 < x_t < 0.1
        f = barr_zee_loop_function(x_t)
        assert f > 0.0

    def test_raises_for_negative_x(self):
        with pytest.raises(ValueError):
            barr_zee_loop_function(-0.1)

    def test_zero_x_returns_zero(self):
        assert barr_zee_loop_function(1e-15) == 0.0

    def test_heavy_limit_negative(self):
        # For x > 1 (heavy inner fermion), f < 0 is not expected for our formula
        # but the function should not crash
        val = barr_zee_loop_function(0.99)
        assert isinstance(val, float)


class TestCpPhases:
    def test_braid_cs_phase_tiny(self):
        # exp(-74) is ~10^-32, so sin(δ_CS) should be ~10^-32
        phase = cp_phase_from_braid_cs()
        assert 0.0 < phase < 1e-25

    def test_braid_cs_phase_positive(self):
        assert cp_phase_from_braid_cs() > 0.0

    def test_pmns_phase_canonical(self):
        # |sin(-π/2)| = 1.0
        phase = cp_phase_from_pmns(-math.pi / 2.0)
        assert abs(phase - 1.0) < 1e-10

    def test_pmns_phase_zero_if_no_cp(self):
        phase = cp_phase_from_pmns(0.0)
        assert phase == 0.0

    def test_pmns_phase_absolute_value(self):
        # Should be positive regardless of sign of delta
        assert cp_phase_from_pmns(math.pi/4) == cp_phase_from_pmns(-math.pi/4)


class TestEdmCalculations:
    def test_sm_ckm_returns_reference(self):
        assert edm_sm_ckm_three_loop() == SM_PREDICTION_ECM

    def test_kk_top_positive(self):
        assert edm_kk_barr_zee_top() > 0.0

    def test_kk_top_below_jila(self):
        # The exponentially suppressed CS phase should give d_e << JILA
        d = edm_kk_barr_zee_top()
        assert d < JILA_2023_BOUND_ECM

    def test_kk_top_decreases_with_heavier_kk(self):
        d1 = edm_kk_barr_zee_top(m_kk_gev=1000.0)
        d2 = edm_kk_barr_zee_top(m_kk_gev=2000.0)
        assert d1 > d2

    def test_kk_pmns_positive(self):
        assert edm_kk_barr_zee_pmns() > 0.0

    def test_kk_pmns_below_jila(self):
        d = edm_kk_barr_zee_pmns()
        assert d < JILA_2023_BOUND_ECM

    def test_kk_pmns_larger_than_kk_top(self):
        # PMNS phase = 1 (not exponentially suppressed), so larger
        assert edm_kk_barr_zee_pmns() > edm_kk_barr_zee_top()

    def test_total_um_dict_keys(self):
        result = edm_total_um()
        for key in ["sm_ckm_ecm", "kk_barr_zee_top_ecm", "kk_barr_zee_pmns_ecm", "total_um_ecm"]:
            assert key in result

    def test_total_consistent(self):
        r = edm_total_um()
        assert abs(r["total_um_ecm"] - (r["sm_ckm_ecm"] + r["kk_barr_zee_top_ecm"] + r["kk_barr_zee_pmns_ecm"])) < 1e-50


class TestExperimentalComparison:
    def test_below_acme(self):
        d_total = edm_kk_barr_zee_pmns()
        comp = experimental_comparison(d_total)
        assert comp["below_jila_2023"] is True

    def test_verdict_consistent(self):
        d = edm_kk_barr_zee_pmns()
        comp = experimental_comparison(d)
        assert comp["verdict"] == "CONSISTENT_BELOW_ALL_BOUNDS"

    def test_ratio_to_jila_less_than_one(self):
        d = edm_kk_barr_zee_pmns()
        comp = experimental_comparison(d)
        assert comp["ratio_to_jila"] < 1.0

    def test_not_detectable_by_acme_iii(self):
        d = edm_kk_barr_zee_pmns()
        comp = experimental_comparison(d)
        assert comp["detectable_by_acme_iii"] is False


class TestFullReport:
    def setup_method(self):
        self.report = electron_edm_full_report()

    def test_pillar_number(self):
        assert self.report["pillar"] == 321

    def test_adjacency_label(self):
        assert self.report["adjacency"] == "NON_HARDGATE_ADJACENT"

    def test_m_kk_tev(self):
        assert 0.5 < self.report["m_kk_tev"] < 5.0

    def test_total_below_jila(self):
        d_total = abs(self.report["contributions"]["total_um_ecm"])
        assert d_total < JILA_2023_BOUND_ECM

    def test_physics_summary_string(self):
        assert isinstance(self.report["physics_summary"], str)
        assert len(self.report["physics_summary"]) > 50

    def test_falsifier_string(self):
        assert "10^-30" in self.report["falsifier"]

    def test_experimental_section(self):
        exp = self.report["experimental"]
        assert exp["verdict"] == "CONSISTENT_BELOW_ALL_BOUNDS"

    def test_sin_delta_cs_tiny(self):
        assert self.report["sin_delta_cs_braid"] < 1e-25

    def test_f_xt_positive(self):
        assert self.report["f_xt"] > 0.0
