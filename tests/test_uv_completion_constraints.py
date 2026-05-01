# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_uv_completion_constraints.py
==========================================
Test suite for Pillar 79 — UV Completion Constraints
(src/core/uv_completion_constraints.py).

Covers:
  - Module constants
  - aps_boundary_condition: η̄ values, selection, status labels
  - kk_graviton_mass_spectrum: structure, mass ordering, unitarity
  - back_reaction_convergence: converges at canonical params, keys
  - anomaly_cancellation_constraint: k_eff = n1²+n2² identity
  - irreversibility_lower_bound: dS/dt ≥ 0, total > zero mode
  - holographic_unitarity_bound: all Δ_n ≥ 1
  - m_theory_identification: structure, topology match, open labels
  - wilsonian_rg_flow_check: RG-protected parameters
  - uv_constraints_audit: all constraints present, summary keys

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.uv_completion_constraints import (
    N_W, N1, N2, K_CS, C_S, PHI0_BARE, PHI0_EFF,
    M_PL, M_KK_PLANCK, DELTA_UNITARITY_BOUND,
    aps_boundary_condition,
    kk_graviton_mass_spectrum,
    back_reaction_convergence,
    anomaly_cancellation_constraint,
    irreversibility_lower_bound,
    holographic_unitarity_bound,
    m_theory_identification,
    wilsonian_rg_flow_check,
    uv_constraints_audit,
    derive_uv_embedding,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n1_n2(self):
        assert N1 == 5
        assert N2 == 7

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-10

    def test_phi0_bare(self):
        assert PHI0_BARE == 1.0

    def test_phi0_eff(self):
        assert abs(PHI0_EFF - 5 * 2 * math.pi) < 1e-10

    def test_m_pl(self):
        assert M_PL == 1.0

    def test_m_kk_planck_positive(self):
        assert M_KK_PLANCK > 0

    def test_delta_unitarity_bound(self):
        assert DELTA_UNITARITY_BOUND == 1.0


# ---------------------------------------------------------------------------
# aps_boundary_condition
# ---------------------------------------------------------------------------

class TestApsBoundaryCondition:
    def test_keys(self):
        result = aps_boundary_condition(5)
        for key in ("n_w", "triangular_number", "eta_bar",
                    "satisfies_sm_chirality_requirement", "status", "uv_constraint"):
            assert key in result

    def test_n_w_5_eta_half(self):
        """n_w=5 → T(5)=15 (odd) → η̄ = ½."""
        result = aps_boundary_condition(5)
        assert abs(result["eta_bar"] - 0.5) < 1e-10

    def test_n_w_7_eta_zero(self):
        """n_w=7 → T(7)=28 (even) → η̄ = 0."""
        result = aps_boundary_condition(7)
        assert abs(result["eta_bar"] - 0.0) < 1e-10

    def test_n_w_5_satisfies_sm(self):
        assert aps_boundary_condition(5)["satisfies_sm_chirality_requirement"] is True

    def test_n_w_7_does_not_satisfy(self):
        assert aps_boundary_condition(7)["satisfies_sm_chirality_requirement"] is False

    def test_triangular_number_5(self):
        assert aps_boundary_condition(5)["triangular_number"] == 15

    def test_triangular_number_7(self):
        assert aps_boundary_condition(7)["triangular_number"] == 28

    def test_status_derived_for_nw5(self):
        assert "DERIVED" in aps_boundary_condition(5)["status"]

    def test_status_excluded_for_nw7(self):
        assert "EXCLUDED" in aps_boundary_condition(7)["status"]

    def test_uv_constraint_mentions_eta(self):
        assert "η̄" in aps_boundary_condition(5)["uv_constraint"] or \
               "eta" in aps_boundary_condition(5)["uv_constraint"].lower()


# ---------------------------------------------------------------------------
# kk_graviton_mass_spectrum
# ---------------------------------------------------------------------------

class TestKKGravitonMassSpectrum:
    def test_keys(self):
        result = kk_graviton_mass_spectrum()
        for key in ("modes", "masses_planck", "spectral_weights",
                    "conformal_dimensions", "R_KK_planck", "k_cs",
                    "massless_graviton", "uv_constraint"):
            assert key in result

    def test_zero_mode_massless(self):
        """n=0 mode has mass 0."""
        result = kk_graviton_mass_spectrum()
        assert result["masses_planck"][0] == 0.0

    def test_mass_increasing(self):
        """Masses m_n increase with n."""
        result = kk_graviton_mass_spectrum(n_max=5)
        masses = result["masses_planck"]
        for i in range(len(masses) - 1):
            assert masses[i + 1] > masses[i]

    def test_spectral_weights_decreasing(self):
        """Gaussian weights decrease with n."""
        result = kk_graviton_mass_spectrum(n_max=5)
        w = result["spectral_weights"]
        for i in range(len(w) - 1):
            assert w[i] >= w[i + 1]

    def test_weights_at_most_one(self):
        result = kk_graviton_mass_spectrum()
        assert all(0 < wi <= 1.0 for wi in result["spectral_weights"])

    def test_conformal_dims_above_two(self):
        """Δ_n = 2 + √(4 + ...) ≥ 2 for all n."""
        result = kk_graviton_mass_spectrum()
        assert all(d >= 2.0 for d in result["conformal_dimensions"])

    def test_n_modes_count(self):
        result = kk_graviton_mass_spectrum(n_max=7)
        assert len(result["modes"]) == 8  # 0 through 7


# ---------------------------------------------------------------------------
# back_reaction_convergence
# ---------------------------------------------------------------------------

class TestBackReactionConvergence:
    def test_keys(self):
        result = back_reaction_convergence()
        for key in ("phi0_bare", "phi0_corrected", "fractional_shift",
                    "n_modes", "converges", "status", "uv_constraint"):
            assert key in result

    def test_converges_at_canonical(self):
        """At canonical parameters, back-reaction should converge (Pillar 72)."""
        result = back_reaction_convergence()
        assert result["converges"] is True

    def test_phi0_corrected_near_bare(self):
        """Corrected φ₀ should be close to the bare value."""
        result = back_reaction_convergence()
        assert abs(result["phi0_corrected"] - result["phi0_bare"]) < 0.1

    def test_fractional_shift_small(self):
        """Fractional shift < 10% for convergence."""
        result = back_reaction_convergence()
        assert result["fractional_shift"] < 0.10

    def test_status_contains_converges(self):
        assert "CONVERGES" in back_reaction_convergence()["status"]

    def test_more_modes_larger_shift(self):
        """More KK modes → larger (but still small) shift."""
        r5 = back_reaction_convergence(n_modes=5)
        r10 = back_reaction_convergence(n_modes=10)
        assert r10["fractional_shift"] >= r5["fractional_shift"]


# ---------------------------------------------------------------------------
# anomaly_cancellation_constraint
# ---------------------------------------------------------------------------

class TestAnomalyCancellationConstraint:
    def test_keys(self):
        result = anomaly_cancellation_constraint()
        for key in ("n1", "n2", "k_primary", "delta_k_Z2",
                    "k_eff_derived", "k_eff_expected", "identity_holds",
                    "status", "uv_constraint"):
            assert key in result

    def test_identity_holds_for_canonical(self):
        """k_eff = n1² + n2² for (n1, n2) = (5, 7)."""
        result = anomaly_cancellation_constraint(5, 7)
        assert result["identity_holds"] is True

    def test_k_eff_equals_74(self):
        """5² + 7² = 25 + 49 = 74."""
        result = anomaly_cancellation_constraint(5, 7)
        assert result["k_eff_expected"] == 74
        assert result["k_eff_derived"] == 74

    def test_status_algebraic_theorem(self):
        assert "ALGEBRAIC" in anomaly_cancellation_constraint()["status"] or \
               "THEOREM" in anomaly_cancellation_constraint()["status"]

    def test_custom_pair(self):
        """For (n1, n2) = (3, 4): k_eff = 9 + 16 = 25."""
        result = anomaly_cancellation_constraint(3, 4)
        assert result["k_eff_expected"] == 25


# ---------------------------------------------------------------------------
# irreversibility_lower_bound
# ---------------------------------------------------------------------------

class TestIrreversibilityLowerBound:
    def test_keys(self):
        result = irreversibility_lower_bound()
        for key in ("n_modes", "kappa_n", "dS_dt_per_mode",
                    "dS_dt_total", "dS_dt_zero_mode",
                    "lower_bound_holds", "total_exceeds_zero_mode",
                    "status", "uv_constraint"):
            assert key in result

    def test_lower_bound_holds(self):
        """All dS/dt ≥ 0 (Pillar 72 proof)."""
        result = irreversibility_lower_bound()
        assert result["lower_bound_holds"] is True

    def test_total_exceeds_zero_mode(self):
        """Total dS/dt ≥ zero-mode dS/dt (more modes → more entropy production)."""
        result = irreversibility_lower_bound()
        assert result["total_exceeds_zero_mode"] is True

    def test_status_proved(self):
        assert "PROVED" in irreversibility_lower_bound()["status"]

    def test_all_kappa_nonnegative(self):
        result = irreversibility_lower_bound()
        assert all(k >= 0 for k in result["kappa_n"])

    def test_all_ds_dt_nonnegative(self):
        result = irreversibility_lower_bound()
        assert all(d >= 0 for d in result["dS_dt_per_mode"])

    def test_ds_dt_total_positive(self):
        result = irreversibility_lower_bound()
        assert result["dS_dt_total"] > 0


# ---------------------------------------------------------------------------
# holographic_unitarity_bound
# ---------------------------------------------------------------------------

class TestHolographicUnitarityBound:
    def test_keys(self):
        result = holographic_unitarity_bound()
        for key in ("modes_checked", "conformal_dimensions", "unitarity_bound",
                    "all_satisfy_bound", "status", "uv_constraint"):
            assert key in result

    def test_all_satisfy(self):
        """All conformal dimensions Δ_n ≥ 1."""
        result = holographic_unitarity_bound()
        assert result["all_satisfy_bound"] is True

    def test_dims_all_above_bound(self):
        result = holographic_unitarity_bound()
        for d in result["conformal_dimensions"]:
            assert d >= DELTA_UNITARITY_BOUND

    def test_status_satisfied(self):
        assert "SATISFIED" in holographic_unitarity_bound()["status"]

    def test_zero_mode_dim_equals_two(self):
        """n=0 mode: m_0=0 → Δ_0 = 2 + √4 = 4."""
        result = holographic_unitarity_bound()
        assert abs(result["conformal_dimensions"][0] - 4.0) < 0.01


# ---------------------------------------------------------------------------
# m_theory_identification
# ---------------------------------------------------------------------------

class TestMTheoryIdentification:
    def test_keys(self):
        result = m_theory_identification()
        for key in ("identification", "topology", "field_matching",
                    "status", "consequence", "testable_prediction"):
            assert key in result

    def test_topology_match(self):
        """Topology label should mention 'STRUCTURAL MATCH'."""
        result = m_theory_identification()
        assert "MATCH" in result["status"]["topology"].upper()

    def test_field_matching_has_metric(self):
        result = m_theory_identification()
        assert "UM_metric_G_AB" in result["field_matching"]

    def test_identification_mentions_horava_witten(self):
        result = m_theory_identification()
        assert "Horava" in result["identification"] or "M-theory" in result["identification"]

    def test_consequence_not_empty(self):
        result = m_theory_identification()
        assert len(result["consequence"]) > 30

    def test_testable_prediction_not_empty(self):
        result = m_theory_identification()
        assert len(result["testable_prediction"]) > 30

    def test_some_status_open(self):
        """Some identification steps should be labelled CONJECTURED or OPEN."""
        result = m_theory_identification()
        status_vals = list(result["status"].values())
        has_open = any("CONJECT" in s.upper() or "OPEN" in s.upper() for s in status_vals)
        assert has_open


# ---------------------------------------------------------------------------
# wilsonian_rg_flow_check
# ---------------------------------------------------------------------------

class TestWilsonianRGFlowCheck:
    def test_keys(self):
        result = wilsonian_rg_flow_check()
        for key in ("mu_UV", "mu_IR", "log_mu_IR_over_UV",
                    "n_w", "k_cs", "c_s", "conclusion"):
            assert key in result

    def test_n_w_exact(self):
        """n_w does not run."""
        result = wilsonian_rg_flow_check()
        assert result["n_w"]["UV"] == result["n_w"]["IR"]

    def test_k_cs_exact(self):
        """k_CS does not run (topological)."""
        result = wilsonian_rg_flow_check()
        assert result["k_cs"]["UV"] == result["k_cs"]["IR"]

    def test_c_s_derived(self):
        """c_s is derived, not running independently."""
        result = wilsonian_rg_flow_check()
        assert result["c_s"]["UV"] == result["c_s"]["IR"]

    def test_status_exact_for_n_w(self):
        assert "EXACT" in wilsonian_rg_flow_check()["n_w"]["status"].upper()

    def test_status_exact_for_k_cs(self):
        assert "EXACT" in wilsonian_rg_flow_check()["k_cs"]["status"].upper()

    def test_log_running_correct_sign(self):
        """mu_IR < mu_UV → log < 0."""
        result = wilsonian_rg_flow_check(mu_UV=1.0, mu_IR=0.1)
        assert result["log_mu_IR_over_UV"] < 0


# ---------------------------------------------------------------------------
# uv_constraints_audit
# ---------------------------------------------------------------------------

class TestUVConstraintsAudit:
    def test_keys(self):
        result = uv_constraints_audit()
        for key in ("title", "constraints", "m_theory_identification",
                    "rg_flow", "summary", "open_problems"):
            assert key in result

    def test_constraints_length(self):
        """Should have at least 5 constraints listed."""
        result = uv_constraints_audit()
        assert len(result["constraints"]) >= 5

    def test_summary_keys(self):
        result = uv_constraints_audit()
        summary = result["summary"]
        assert "APS_constraint" in summary
        assert "anomaly_cancellation" in summary
        assert "irreversibility" in summary

    def test_open_problems_not_empty(self):
        result = uv_constraints_audit()
        assert len(result["open_problems"]) >= 2

    def test_title_not_empty(self):
        assert len(uv_constraints_audit()["title"]) > 10

    def test_m_theory_in_audit(self):
        result = uv_constraints_audit()
        assert "identification" in result["m_theory_identification"]


# ---------------------------------------------------------------------------
# TestDeriveUVEmbedding  (Pillar 92 — UV embedding chain)
# ---------------------------------------------------------------------------

class TestDeriveUVEmbedding:
    """Tests for derive_uv_embedding() — Pillar 92."""

    def setup_method(self):
        self.res = derive_uv_embedding()

    def test_returns_dict(self):
        assert isinstance(self.res, dict)

    def test_pillar_is_92(self):
        assert self.res["pillar"] == 92

    def test_n_w_is_5(self):
        assert self.res["n_w"] == N_W

    def test_k_cs_is_74(self):
        assert self.res["k_cs"] == K_CS

    def test_phi0_is_1(self):
        assert abs(self.res["phi0"] - PHI0_BARE) < 1e-12

    def test_steps_keys_present(self):
        for key in ("step1_aps_eta", "step2_anomaly_cancellation",
                    "step3_ftum_fixed_point", "step4_flux_matching"):
            assert key in self.res["steps"]

    def test_step1_aps_proved(self):
        assert "PROVED" in self.res["steps"]["step1_aps_eta"]

    def test_step2_anomaly_algebraic(self):
        assert "ALGEBRAIC" in self.res["steps"]["step2_anomaly_cancellation"]

    def test_step3_ftum_proved(self):
        assert "PROVED" in self.res["steps"]["step3_ftum_fixed_point"]

    def test_step4_is_proved(self):
        """Step 4 is now PROVED by the G₄-flux Bianchi identity."""
        assert "PROVED" in self.res["steps"]["step4_flux_matching"]

    def test_step4_not_open(self):
        """Step 4 is no longer OPEN — Bianchi identity closes it."""
        assert "OPEN" not in self.res["steps"]["step4_flux_matching"]

    def test_all_steps_closed(self):
        assert self.res.get("all_steps_closed") is True

    def test_overall_status_steps_1_3_closed(self):
        assert "1" in self.res["overall_status"] or "CLOSED" in self.res["overall_status"]

    def test_remaining_gap_nonempty(self):
        assert len(self.res["remaining_gap"]) > 20

    def test_remaining_gap_mentions_open_questions(self):
        """Remaining gap now lists holonomy/quark/SUSY open questions."""
        gap = self.res["remaining_gap"].lower()
        assert "holonomy" in gap or "quark" in gap or "susy" in gap
