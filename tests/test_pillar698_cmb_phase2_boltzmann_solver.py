# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 698 — CMB Phase 2 Boltzmann solver."""
from __future__ import annotations

import pytest

from src.core.pillar698_cmb_phase2_boltzmann_solver import (
    A_S_LCDM,
    C_S,
    DELTA_KK,
    ELL_MAX,
    H0_KM_S_MPC,
    HIERARCHY_MODE,
    K_CS,
    N_S,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TAU_REC_MPC,
    Z_REC,
    cl_from_hierarchy,
    phase2_amplitude_audit,
    solve_boltzmann_kk,
)

SOLUTION = solve_boltzmann_kk(0.02, n_tau_steps=80)
CL_200 = cl_from_hierarchy(200, n_k=8)
CL_540 = cl_from_hierarchy(540, n_k=8)
AUDIT = phase2_amplitude_audit()


def test_constants_match_task():
    assert PILLAR_NUMBER == 698
    assert N_W == 5
    assert K_CS == 74
    assert C_S == 12.0 / 37.0
    assert DELTA_KK == 8.0e-4


def test_cosmology_constants_match_task():
    assert Z_REC == 1100
    assert TAU_REC_MPC == 282.0
    assert H0_KM_S_MPC == 67.4
    assert A_S_LCDM == 2.10e-9
    assert N_S == 0.9649


def test_status_and_mode_labels():
    assert "PHASE2" in PILLAR_STATUS
    assert HIERARCHY_MODE == "SIMPLIFIED_HIERARCHY"


def test_solver_returns_dict():
    assert isinstance(SOLUTION, dict)


def test_solver_tau_grid_length():
    assert len(SOLUTION["tau_grid"]) == 80


def test_solver_history_length():
    assert len(SOLUTION["theta_history"]) == 80


def test_solver_ell_max():
    assert SOLUTION["ell_max"] == ELL_MAX == 10


def test_solver_final_multipoles_count():
    assert len(SOLUTION["theta_final"]) == ELL_MAX + 1


def test_solver_monopole_starts_nonzero():
    assert SOLUTION["theta_history"][0][0] == 1.0


def test_solver_keeps_finite_values():
    assert all(abs(value) < 1.0e8 for value in SOLUTION["theta_history"][-1])


def test_solver_rejects_nonpositive_k():
    with pytest.raises(ValueError):
        solve_boltzmann_kk(0.0)


def test_solver_rejects_too_few_steps():
    with pytest.raises(ValueError):
        solve_boltzmann_kk(0.02, n_tau_steps=10)


def test_cl_200_positive():
    assert CL_200["c_ell"] > 0.0


def test_cl_540_positive():
    assert CL_540["c_ell"] > 0.0


def test_cl_200_exceeds_cl_540():
    assert CL_200["c_ell"] > CL_540["c_ell"]


def test_cl_reports_peak_window():
    assert CL_200["k_min_mpc"] < CL_200["k_peak_mpc"] < CL_200["k_max_mpc"]


def test_cl_rejects_low_ell():
    with pytest.raises(ValueError):
        cl_from_hierarchy(1)


def test_cl_rejects_too_few_k_samples():
    with pytest.raises(ValueError):
        cl_from_hierarchy(200, n_k=3)


def test_audit_contains_peak_ratio():
    assert AUDIT["peak_ratio_2_to_1"] > 0.0


def test_audit_is_honest_about_approximation():
    assert AUDIT["honesty_label"] == "SIMPLIFIED_HIERARCHY"


# ---------------------------------------------------------------------------
# Gap-closure sprint: CMB suppression floor analytic tests
# ---------------------------------------------------------------------------

import sys as _sys
import os as _os
import math as _math
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))

from src.core.pillar698_cmb_phase2_boltzmann_solver import (
    eta_suppression_ratio,
    cmb_suppression_floor_audit,
    C_S,
    N_W,
    DELTA_KK,
    TAU_REC_MPC,
    D_A_LAST_SCATTERING_MPC,
)


class TestEtaSuppression:
    def test_returns_dict(self):
        result = eta_suppression_ratio(k_mpc=0.02)
        assert isinstance(result, dict)

    def test_eta_less_than_one_for_positive_k(self):
        for k in [0.005, 0.015, 0.04, 0.08]:
            result = eta_suppression_ratio(k_mpc=k)
            assert result["eta_suppression"] < 1.0, f"η ≥ 1 at k={k}"

    def test_eta_greater_than_zero(self):
        for k in [0.01, 0.05]:
            result = eta_suppression_ratio(k_mpc=k)
            assert result["eta_suppression"] > 0.0

    def test_suppression_necessary_flag(self):
        result = eta_suppression_ratio(k_mpc=0.03)
        assert result["suppression_is_necessary"] is True

    def test_eta_less_than_one_flag(self):
        result = eta_suppression_ratio(k_mpc=0.03)
        assert result["eta_less_than_one"] is True

    def test_delta_kk_analytic_positive(self):
        result = eta_suppression_ratio(k_mpc=0.03)
        assert result["delta_kk_analytic"] > 0.0

    def test_eta_decreases_with_k(self):
        # Higher k → more suppression → lower η
        eta_low = eta_suppression_ratio(k_mpc=0.01)["eta_suppression"]
        eta_high = eta_suppression_ratio(k_mpc=0.05)["eta_suppression"]
        assert eta_high < eta_low

    def test_floor_theorem_string(self):
        result = eta_suppression_ratio(k_mpc=0.02)
        assert "SUPPRESSION_FLOOR_PROVED_ANALYTIC" in result["floor_theorem"]

    def test_status_field(self):
        result = eta_suppression_ratio(k_mpc=0.02)
        assert result["status"] == "SUPPRESSION_FLOOR_PROVED_ANALYTIC"

    def test_k_ratio_computed(self):
        result = eta_suppression_ratio(k_mpc=0.05)
        assert result["k_ratio"] > 0.0

    def test_suppression_integral_positive(self):
        result = eta_suppression_ratio(k_mpc=0.03)
        assert result["suppression_integral"] > 0.0


class TestCMBSuppressionFloorAudit:
    def setup_method(self):
        self.result = cmb_suppression_floor_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_all_three_peaks_present(self):
        peaks = self.result["per_peak"]
        assert "peak_1" in peaks
        assert "peak_2" in peaks
        assert "peak_3" in peaks

    def test_all_peaks_suppressed(self):
        assert self.result["all_peaks_suppressed"] is True

    def test_all_peak_eta_less_than_one(self):
        for name, peak in self.result["per_peak"].items():
            assert peak["eta"] < 1.0, f"Peak {name} has η ≥ 1"

    def test_all_suppression_necessary(self):
        for name, peak in self.result["per_peak"].items():
            assert peak["suppression_is_necessary"] is True, f"Peak {name} not marked necessary"

    def test_status_field(self):
        assert self.result["status"] == "SUPPRESSION_FLOOR_PROVED_ANALYTIC"

    def test_theorem_mentions_kk(self):
        assert "KK" in self.result["theorem"] or "kk" in self.result["theorem"].lower()

    def test_lean4_proxy_bound_present(self):
        assert len(self.result["lean4_proxy_bound"]) > 30

    def test_epistemic_upgrade_present(self):
        assert len(self.result["epistemic_upgrade"]) > 30

    def test_peak2_more_suppressed_than_peak1(self):
        peaks = self.result["per_peak"]
        assert peaks["peak_2"]["eta"] < peaks["peak_1"]["eta"]

    def test_peak3_most_suppressed(self):
        peaks = self.result["per_peak"]
        assert peaks["peak_3"]["eta"] < peaks["peak_2"]["eta"]
