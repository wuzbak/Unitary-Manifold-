# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Cross-pillar regression guard for foundational hardening modules."""

from __future__ import annotations

from src.core.pillar_nw_uniqueness_hardening import preferred_winding_from_spectral_residuals
from src.core.pillar_cmb_peak_hardening import CMB_PEAK_RESIDUAL_FACTOR, combined_residual_report
from src.core.pillar_phi0_cross_check import PHI0_CROSS_CHECK_RELATIVE_ERROR, phi0_cross_check_summary
from src.core.pillar_desi_tension_monitor import DESI_TENSION_SIGMA, monitor_desi_tension
from src.core.pillar_kcs_robustness import (
    K_CS_CANONICAL,
    BRAID_PAIR_CANONICAL,
    assert_unique_solution_at_k74,
    birefringence_beta_deg_from_kcs,
)


def test_cross_pillar_chain_consistency():
    nw = preferred_winding_from_spectral_residuals()
    kcs = assert_unique_solution_at_k74()
    phi0 = phi0_cross_check_summary()
    cmb = combined_residual_report()
    desi = monitor_desi_tension()

    assert nw["preferred_n_w"] == 5
    assert kcs["canonical_pair"] == BRAID_PAIR_CANONICAL == (5, 7)
    assert K_CS_CANONICAL == 74
    assert phi0["agreement_lt_1pct"] is True
    assert PHI0_CROSS_CHECK_RELATIVE_ERROR < 0.01
    assert cmb["max_combined_residual"] == CMB_PEAK_RESIDUAL_FACTOR
    assert cmb["combined_reduces_below_x2"] is True
    assert DESI_TENSION_SIGMA == desi["desi_tension_sigma"]


def test_chain_winding_to_ns_preference():
    nw = preferred_winding_from_spectral_residuals()
    assert nw["preferred_n_w"] == 5
    assert nw["best_chi2"] < nw["runner_up_chi2"]


def test_chain_to_birefringence_monotonicity():
    beta73 = birefringence_beta_deg_from_kcs(73)
    beta74 = birefringence_beta_deg_from_kcs(74)
    beta75 = birefringence_beta_deg_from_kcs(75)
    assert beta73 < beta74 < beta75


def test_chain_to_desi_flag_defined():
    desi = monitor_desi_tension()
    assert desi["flag"] in {"PASS", "WARNING", "CRITICAL"}
