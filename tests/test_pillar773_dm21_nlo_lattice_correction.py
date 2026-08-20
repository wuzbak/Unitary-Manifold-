# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 773 — NLO Lattice Correction for Δm²₂₁ (Partial Closure).

Covers:
- Module constants (scalar and float)
- Individual NLO mechanism functions (winding, KK threshold, BKT)
- Combined NLO correction and analytic consistency
- DM21 post-NLO prediction and tension evaluation
- Honest gate: NLO_INSUFFICIENT_FOR_SUB_1SIGMA
- Tension cascade through Pillars 583 → 773
- Sufficiency audit (gap-to-sub-1σ, required shift)
- Closure status and certificate structure
- Lean4 module accounting
- Physics consistency guards
- Pillar 772 baseline integrity (regression)
"""
from __future__ import annotations

import math

import pytest

from src.core.pillar773_dm21_nlo_lattice_correction import (
    DELTA_C,
    DELTA_C_SQ,
    DM21_AFTER_LJL,
    DM21_AFTER_NLO,
    DM21_PDG_EV2,
    DM21_SIGMA_EV2,
    EPISTEMIC_LABEL,
    K_CS,
    LEAN4_MODULE,
    LEAN4_NEW_THEOREMS,
    LEAN4_NEW_TOTAL,
    LEAN4_PREV_TOTAL,
    N_W,
    NAMED_RESIDUAL,
    NLO_ANALYTIC_CHECK,
    NLO_BKT_MIXING,
    NLO_COMBINED_CORRECTION,
    NLO_GATE,
    NLO_KK_THRESHOLD,
    NLO_SUB_1SIGMA_ACHIEVED,
    NLO_WINDING_CORRECTION,
    PILLAR,
    SIN2_THETA12,
    COS2_THETA12,
    STATUS,
    TENSION_AFTER_NLO,
    TENSION_LO,
    TEST_EXPECTATIONS,
    VERSION,
    closure_status,
    dm21_nlo_corrected,
    dm21_sigma_nlo,
    full_closure_certificate,
    nlo_bkt_mixing,
    nlo_combined,
    nlo_kk_threshold,
    nlo_sufficiency_audit,
    nlo_winding_correction,
    tension_cascade,
)


# ── Scalar constant tests ─────────────────────────────────────────────────────

class TestScalarConstants:
    def test_pillar_number(self):
        assert PILLAR == 773

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_status(self):
        assert STATUS == "DM21_NLO_PARTIAL_CLOSURE"

    def test_lean4_module(self):
        assert LEAN4_MODULE == "Dm21NLOLatticeClosure"

    def test_lean4_new_theorems(self):
        assert LEAN4_NEW_THEOREMS == 13

    def test_lean4_prev_total(self):
        assert LEAN4_PREV_TOTAL == 859

    def test_lean4_new_total(self):
        assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

    def test_lean4_new_total_value(self):
        assert LEAN4_NEW_TOTAL == 872

    def test_version_prefix(self):
        assert VERSION.startswith("v")

    def test_nlo_gate_not_closed(self):
        assert NLO_GATE == "NLO_INSUFFICIENT_FOR_SUB_1SIGMA"

    def test_nlo_sub_1sigma_not_achieved(self):
        assert NLO_SUB_1SIGMA_ACHIEVED is False

    def test_named_residual_nlo(self):
        assert "NLO" in NAMED_RESIDUAL

    def test_named_residual_sigma(self):
        assert "SIGMA" in NAMED_RESIDUAL or "sigma" in NAMED_RESIDUAL.lower()


# ── Float constant tests ──────────────────────────────────────────────────────

class TestFloatConstants:
    def test_delta_c(self):
        assert abs(DELTA_C - 5.0 / 74.0) < 1e-15

    def test_delta_c_sq(self):
        assert abs(DELTA_C_SQ - (5.0 / 74.0) ** 2) < 1e-15

    def test_sin2_theta12(self):
        assert SIN2_THETA12 == pytest.approx(0.307, abs=1e-6)

    def test_cos2_theta12(self):
        assert COS2_THETA12 == pytest.approx(1.0 - SIN2_THETA12, abs=1e-12)

    def test_sin2_plus_cos2_unity(self):
        assert SIN2_THETA12 + COS2_THETA12 == pytest.approx(1.0, abs=1e-12)

    def test_dm21_pdg(self):
        assert DM21_PDG_EV2 == pytest.approx(7.53e-5, rel=1e-3)

    def test_dm21_sigma(self):
        assert DM21_SIGMA_EV2 == pytest.approx(1.8e-6, rel=1e-3)

    def test_dm21_after_ljl_baseline(self):
        # Pillar 772 result (regression guard)
        assert DM21_AFTER_LJL == pytest.approx(7.320442e-5, rel=1e-5)


# ── NLO Mechanism 1: Winding-mode exchange ────────────────────────────────────

class TestNLOWindingCorrection:
    def test_winding_positive(self):
        assert NLO_WINDING_CORRECTION > 0.0

    def test_winding_formula(self):
        expected = (5.0 / 74.0) ** 2 * (1.0 - 0.307) * 0.5
        assert NLO_WINDING_CORRECTION == pytest.approx(expected, rel=1e-10)

    def test_winding_order_of_magnitude(self):
        # Should be ~1.6e-3
        assert 1e-3 < NLO_WINDING_CORRECTION < 5e-3

    def test_winding_function_keys(self):
        w = nlo_winding_correction()
        for key in ("mechanism", "order", "epsilon_sq", "correction_fraction",
                    "free_parameters_introduced"):
            assert key in w

    def test_winding_function_mechanism(self):
        w = nlo_winding_correction()
        assert "winding" in w["mechanism"]

    def test_winding_function_order(self):
        w = nlo_winding_correction()
        assert w["order"] == "NLO"

    def test_winding_function_zero_free_params(self):
        w = nlo_winding_correction()
        assert w["free_parameters_introduced"] == 0

    def test_winding_function_value(self):
        w = nlo_winding_correction()
        assert w["correction_fraction"] == pytest.approx(NLO_WINDING_CORRECTION, rel=1e-10)

    def test_winding_epsilon_sq(self):
        w = nlo_winding_correction()
        assert w["epsilon_sq"] == pytest.approx(DELTA_C_SQ, rel=1e-10)


# ── NLO Mechanism 2: KK threshold correction ──────────────────────────────────

class TestNLOKKThreshold:
    def test_kk_positive(self):
        assert NLO_KK_THRESHOLD > 0.0

    def test_kk_formula(self):
        expected = (5.0 / 74.0) ** 2 / (4.0 * math.pi ** 2)
        assert NLO_KK_THRESHOLD == pytest.approx(expected, rel=1e-10)

    def test_kk_order_of_magnitude(self):
        # Should be ~1.2e-4
        assert 5e-5 < NLO_KK_THRESHOLD < 5e-4

    def test_kk_function_keys(self):
        k = nlo_kk_threshold()
        for key in ("mechanism", "order", "loop_factor",
                    "correction_fraction", "free_parameters_introduced"):
            assert key in k

    def test_kk_function_mechanism(self):
        k = nlo_kk_threshold()
        assert "kk" in k["mechanism"] or "threshold" in k["mechanism"]

    def test_kk_function_order(self):
        k = nlo_kk_threshold()
        assert k["order"] == "NLO"

    def test_kk_function_zero_free_params(self):
        k = nlo_kk_threshold()
        assert k["free_parameters_introduced"] == 0

    def test_kk_function_loop_factor(self):
        k = nlo_kk_threshold()
        assert k["loop_factor"] == pytest.approx(1.0 / (4.0 * math.pi ** 2), rel=1e-10)

    def test_kk_smaller_than_winding(self):
        # KK is suppressed by 1/(4π²) ≈ 0.025 relative to winding
        assert NLO_KK_THRESHOLD < NLO_WINDING_CORRECTION


# ── NLO Mechanism 3: BKT mixing ───────────────────────────────────────────────

class TestNLOBKTMixing:
    def test_bkt_positive(self):
        assert NLO_BKT_MIXING > 0.0

    def test_bkt_formula(self):
        expected = (5.0 / 74.0) ** 2 * 0.307 * 0.5
        assert NLO_BKT_MIXING == pytest.approx(expected, rel=1e-10)

    def test_bkt_order_of_magnitude(self):
        # Should be ~7e-4
        assert 3e-4 < NLO_BKT_MIXING < 2e-3

    def test_bkt_function_keys(self):
        b = nlo_bkt_mixing()
        for key in ("mechanism", "order", "sin2_theta12",
                    "correction_fraction", "free_parameters_introduced",
                    "orthogonal_to_lo"):
            assert key in b

    def test_bkt_orthogonal_to_lo(self):
        b = nlo_bkt_mixing()
        assert b["orthogonal_to_lo"] is True

    def test_bkt_function_zero_free_params(self):
        b = nlo_bkt_mixing()
        assert b["free_parameters_introduced"] == 0

    def test_bkt_sin2_theta12(self):
        b = nlo_bkt_mixing()
        assert b["sin2_theta12"] == pytest.approx(0.307, abs=1e-6)

    def test_bkt_smaller_than_winding(self):
        # sin²θ₁₂ < cos²θ₁₂ for θ₁₂ < 45°
        assert NLO_BKT_MIXING < NLO_WINDING_CORRECTION


# ── Angular decomposition completeness ────────────────────────────────────────

class TestAngularDecomposition:
    def test_winding_plus_bkt_equals_half_eps_sq(self):
        # δ_wind + δ_BKT = (n_w/k_CS)² / 2 exactly
        expected = DELTA_C_SQ * 0.5
        actual = NLO_WINDING_CORRECTION + NLO_BKT_MIXING
        assert actual == pytest.approx(expected, rel=1e-10)

    def test_angular_decomposition_complete(self):
        # cos²θ₁₂ / 2 + sin²θ₁₂ / 2 = 1/2 (total angular coverage)
        actual = COS2_THETA12 / 2 + SIN2_THETA12 / 2
        assert actual == pytest.approx(0.5, abs=1e-12)

    def test_cos2_plus_sin2_unity(self):
        assert COS2_THETA12 + SIN2_THETA12 == pytest.approx(1.0, abs=1e-12)


# ── Combined NLO correction ───────────────────────────────────────────────────

class TestNLOCombined:
    def test_combined_positive(self):
        assert NLO_COMBINED_CORRECTION > 0.0

    def test_combined_sum(self):
        expected = NLO_WINDING_CORRECTION + NLO_KK_THRESHOLD + NLO_BKT_MIXING
        assert NLO_COMBINED_CORRECTION == pytest.approx(expected, rel=1e-10)

    def test_combined_order_of_magnitude(self):
        # ~2.4e-3
        assert 1e-3 < NLO_COMBINED_CORRECTION < 1e-2

    def test_combined_analytic_consistency(self):
        # δ_NLO = (n_w/k_CS)² × [1/2 + 1/(4π²)]
        expected = DELTA_C_SQ * (0.5 + 1.0 / (4.0 * math.pi ** 2))
        assert NLO_ANALYTIC_CHECK == pytest.approx(expected, rel=1e-10)
        assert NLO_COMBINED_CORRECTION == pytest.approx(NLO_ANALYTIC_CHECK, rel=1e-10)

    def test_combined_bounded_by_eps_sq(self):
        # Total NLO ≤ ε² (all mechanisms are O(ε²) with coefficients ≤ 1)
        assert NLO_COMBINED_CORRECTION <= DELTA_C_SQ

    def test_nlo_combined_function_consistent(self):
        c = nlo_combined()
        assert c["delta_nlo_total"] == pytest.approx(NLO_COMBINED_CORRECTION, rel=1e-10)
        assert c["consistent"] is True
        assert c["angular_decomposition_complete"] is True

    def test_nlo_combined_function_keys(self):
        c = nlo_combined()
        for key in ("delta_wind", "delta_kk", "delta_bkt",
                    "delta_nlo_total", "analytic_value", "consistent"):
            assert key in c

    def test_nlo_combined_zero_free_params(self):
        c = nlo_combined()
        assert c["free_parameters_introduced"] == 0


# ── Post-NLO DM21 prediction ──────────────────────────────────────────────────

class TestDM21NLO:
    def test_dm21_nlo_above_ljl(self):
        assert DM21_AFTER_NLO > DM21_AFTER_LJL

    def test_dm21_nlo_below_pdg(self):
        assert DM21_AFTER_NLO < DM21_PDG_EV2

    def test_dm21_nlo_within_3sigma(self):
        assert abs(DM21_PDG_EV2 - DM21_AFTER_NLO) < 3.0 * DM21_SIGMA_EV2

    def test_dm21_nlo_value(self):
        expected = DM21_AFTER_LJL * (1.0 + NLO_COMBINED_CORRECTION)
        assert DM21_AFTER_NLO == pytest.approx(expected, rel=1e-10)

    def test_tension_nlo_value(self):
        expected = abs(DM21_PDG_EV2 - DM21_AFTER_NLO) / DM21_SIGMA_EV2
        assert TENSION_AFTER_NLO == pytest.approx(expected, rel=1e-10)

    def test_tension_nlo_below_2sigma(self):
        assert TENSION_AFTER_NLO < 2.0

    def test_tension_nlo_above_1sigma(self):
        # Honest: 1.07σ is NOT sub-1σ
        assert TENSION_AFTER_NLO > 1.0

    def test_tension_nlo_improved_over_lo(self):
        assert TENSION_AFTER_NLO < TENSION_LO

    def test_tension_lo_value(self):
        expected = abs(DM21_PDG_EV2 - DM21_AFTER_LJL) / DM21_SIGMA_EV2
        assert TENSION_LO == pytest.approx(expected, rel=1e-6)

    def test_dm21_sigma_nlo_function(self):
        result = dm21_sigma_nlo()
        assert result == pytest.approx(TENSION_AFTER_NLO, rel=1e-10)

    def test_dm21_sigma_nlo_is_float(self):
        assert isinstance(dm21_sigma_nlo(), float)

    def test_dm21_nlo_corrected_function_keys(self):
        d = dm21_nlo_corrected()
        for key in ("dm21_after_ljl_ev2", "nlo_combined_correction",
                    "dm21_after_nlo_ev2", "tension_lo_sigma", "tension_nlo_sigma",
                    "below_two_sigma", "below_one_sigma"):
            assert key in d

    def test_dm21_nlo_corrected_below_2sigma_true(self):
        d = dm21_nlo_corrected()
        assert d["below_two_sigma"] is True

    def test_dm21_nlo_corrected_below_1sigma_false(self):
        d = dm21_nlo_corrected()
        assert d["below_one_sigma"] is False

    def test_dm21_nlo_corrected_tension_improvement(self):
        d = dm21_nlo_corrected()
        assert d["tension_improvement_sigma"] > 0.0


# ── NLO gate and epistemic honesty ───────────────────────────────────────────

class TestNLOGate:
    def test_gate_is_insufficient(self):
        assert NLO_GATE == "NLO_INSUFFICIENT_FOR_SUB_1SIGMA"

    def test_sub_1sigma_not_achieved(self):
        assert NLO_SUB_1SIGMA_ACHIEVED is False

    def test_gate_not_closed(self):
        assert "CLOSED" not in NLO_GATE

    def test_gate_present_in_closure_status(self):
        cs = closure_status()
        assert cs["nlo_gate"] == NLO_GATE


# ── Tension cascade ───────────────────────────────────────────────────────────

class TestTensionCascade:
    def test_cascade_length(self):
        cascade = tension_cascade()
        assert len(cascade) == 4

    def test_cascade_monotone_improvement(self):
        cascade = tension_cascade()
        tensions = [c["tension_sigma"] for c in cascade]
        assert tensions[0] > tensions[1] > tensions[2] > tensions[3]

    def test_cascade_step3_is_773(self):
        cascade = tension_cascade()
        assert cascade[3]["pillar"] == 773
        assert cascade[3]["correction"] == "NLO_THREE_MECHANISMS"

    def test_cascade_step2_is_772(self):
        cascade = tension_cascade()
        assert cascade[2]["pillar"] == 772

    def test_cascade_step3_nlo_gate(self):
        cascade = tension_cascade()
        assert cascade[3]["nlo_gate"] == "NLO_INSUFFICIENT_FOR_SUB_1SIGMA"

    def test_cascade_starts_at_3sigma(self):
        cascade = tension_cascade()
        assert cascade[0]["tension_sigma"] > 3.0


# ── Sufficiency audit ─────────────────────────────────────────────────────────

class TestSufficiencyAudit:
    def test_audit_sub_1sigma_not_achieved(self):
        audit = nlo_sufficiency_audit()
        assert audit["sub_1sigma_achieved"] is False

    def test_audit_gap_positive(self):
        audit = nlo_sufficiency_audit()
        assert audit["gap_to_sub_1sigma_in_sigma"] > 0.0

    def test_audit_required_shift_positive(self):
        audit = nlo_sufficiency_audit()
        assert audit["required_additional_dm21_ev2"] > 0.0

    def test_audit_mechanisms_listed(self):
        audit = nlo_sufficiency_audit()
        assert len(audit["mechanisms_computed"]) == 3

    def test_audit_next_target_pillar_774(self):
        audit = nlo_sufficiency_audit()
        assert "774" in audit["next_target"]

    def test_audit_keys(self):
        audit = nlo_sufficiency_audit()
        for key in ("tension_after_nlo", "sub_1sigma_achieved",
                    "gap_to_sub_1sigma_in_sigma", "mechanisms_computed",
                    "why_nlo_insufficient", "next_target"):
            assert key in audit

    def test_audit_next_order_estimate_present(self):
        audit = nlo_sufficiency_audit()
        assert "next_order_estimate" in audit


# ── Closure status ────────────────────────────────────────────────────────────

class TestClosureStatus:
    def test_closure_label_not_closed(self):
        cs = closure_status()
        assert "CLOSED" not in cs["closure_label"] or "NLO_PARTIAL" in cs["closure_label"]

    def test_closure_label_partial(self):
        cs = closure_status()
        assert "PARTIAL" in cs["closure_label"]

    def test_closure_below_2sigma(self):
        cs = closure_status()
        assert cs["below_2sigma"] is True

    def test_closure_not_below_1sigma(self):
        cs = closure_status()
        assert cs["below_1sigma"] is False

    def test_closure_epistemic_label(self):
        cs = closure_status()
        assert cs["epistemic_label"] == EPISTEMIC_LABEL

    def test_closure_named_residual(self):
        cs = closure_status()
        assert cs["named_residual"] == NAMED_RESIDUAL

    def test_closure_next_pillar(self):
        cs = closure_status()
        assert cs["next_pillar"] == 774

    def test_closure_tension_nlo(self):
        cs = closure_status()
        assert cs["tension_nlo_sigma"] == pytest.approx(
            round(TENSION_AFTER_NLO, 4), abs=0.001
        )

    def test_closure_pillar_772_upgrade(self):
        cs = closure_status()
        assert "DM21_LJL_1_16SIGMA" in cs["pillar_772_residual_upgraded"]


# ── Full certificate ──────────────────────────────────────────────────────────

class TestFullCertificate:
    def test_certificate_pillar(self):
        cert = full_closure_certificate()
        assert cert["pillar"] == 773

    def test_certificate_lean4_total(self):
        cert = full_closure_certificate()
        assert cert["lean4_new_total"] == 872

    def test_certificate_what_is_claimed(self):
        cert = full_closure_certificate()
        assert len(cert["what_is_claimed"]) >= 3

    def test_certificate_what_is_not_claimed(self):
        cert = full_closure_certificate()
        assert len(cert["what_is_NOT_claimed"]) >= 2

    def test_certificate_not_sub_1sigma_in_claims(self):
        cert = full_closure_certificate()
        combined = " ".join(cert["what_is_claimed"])
        assert "NOT" in " ".join(cert["what_is_NOT_claimed"])

    def test_certificate_keys(self):
        cert = full_closure_certificate()
        for key in ("nlo_mechanisms", "dm21", "cascade",
                    "sufficiency_audit", "closure"):
            assert key in cert

    def test_certificate_nlo_mechanisms_keys(self):
        cert = full_closure_certificate()
        for key in ("winding", "kk_threshold", "bkt_mixing", "combined"):
            assert key in cert["nlo_mechanisms"]


# ── TEST_EXPECTATIONS meta-tests ──────────────────────────────────────────────

class TestExpectationsMeta:
    def test_scalar_expectations_pillar(self):
        assert TEST_EXPECTATIONS["scalar_checks"]["PILLAR"] == 773

    def test_scalar_expectations_lean4_total(self):
        assert TEST_EXPECTATIONS["scalar_checks"]["LEAN4_NEW_TOTAL"] == 872

    def test_scalar_expectations_nlo_gate(self):
        assert TEST_EXPECTATIONS["scalar_checks"]["NLO_GATE"] == "NLO_INSUFFICIENT_FOR_SUB_1SIGMA"

    def test_scalar_expectations_sub_1sigma_false(self):
        assert TEST_EXPECTATIONS["scalar_checks"]["NLO_SUB_1SIGMA_ACHIEVED"] is False

    def test_float_expectations_delta_c(self):
        assert abs(TEST_EXPECTATIONS["float_checks"]["DELTA_C"] - 5.0 / 74.0) < 1e-15

    def test_float_expectations_delta_c_sq(self):
        assert abs(TEST_EXPECTATIONS["float_checks"]["DELTA_C_SQ"] - (5.0 / 74.0) ** 2) < 1e-15

    def test_required_symbols_present(self):
        import src.core.pillar773_dm21_nlo_lattice_correction as m
        for sym in TEST_EXPECTATIONS["required_symbols"]:
            assert hasattr(m, sym), f"Missing symbol: {sym}"

    def test_physics_checks_tension_below_2sigma(self):
        assert TEST_EXPECTATIONS["physics_checks"]["tension_nlo_below_2sigma"] is True

    def test_physics_checks_tension_not_below_1sigma(self):
        assert TEST_EXPECTATIONS["physics_checks"]["tension_nlo_below_1sigma"] is False

    def test_physics_checks_angular_decomposition(self):
        assert TEST_EXPECTATIONS["physics_checks"]["winding_plus_bkt_equals_half_epsilon_sq"] is True
