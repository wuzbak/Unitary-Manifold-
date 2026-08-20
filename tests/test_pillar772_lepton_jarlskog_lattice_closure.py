# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 772 — Lepton-Sector Jarlskog-Lattice Closure.

Covers:
- Module constants (scalar and float)
- Orbifold lattice position derivation for neutrinos
- FN charge derivation (n_FN_lepton = 1, DERIVED not ASSUMED)
- J_PMNS full computation and J_PMNS/J_CKM ratio
- Lepton-lattice mass-ratio correction
- DM21 cascade and tension evaluation
- Closure status and certificate structure
- Lean4 module accounting
- Physics consistency guards
- Pillar 585 NAMED_RESIDUAL upgrade
"""
from __future__ import annotations

import math

import pytest

from src.core.pillar772_lepton_jarlskog_lattice_closure import (
    DELTA_C,
    DELTA_CP_DEG,
    DM21_AFTER_LJL,
    DM21_AFTER_RGE,
    DM21_PDG_EV2,
    DM21_SIGMA_EV2,
    DM31_PDG_EV2,
    EPISTEMIC_LABEL,
    J_CKM_PDG,
    J_PMNS,
    J_PMNS_ABS,
    J_RATIO,
    K_CS,
    L_NU1,
    L_NU2,
    L_NU3,
    LEAN4_MODULE,
    LEAN4_NEW_THEOREMS,
    LEAN4_NEW_TOTAL,
    LEAN4_PREV_TOTAL,
    LEPTON_LJL_CORRECTION_FRAC,
    N_FN_LEPTON,
    N_W,
    NAMED_RESIDUAL,
    PILLAR,
    PILLAR_591_LABEL_UPGRADE,
    RATIO_BRAID,
    RATIO_PDG,
    SIN2_THETA12,
    SIN2_THETA13,
    SIN2_THETA23,
    STATUS,
    TENSION_AFTER_LJL,
    TEST_EXPECTATIONS,
    VERSION,
    COS2_THETA12,
    closure_status,
    dm21_after_lepton_lattice,
    full_closure_certificate,
    j_lepton_to_ckm_ratio,
    j_pmns_full,
    lepton_fn_charge,
    lepton_lattice_mass_ratio_correction,
    neutrino_lattice_positions,
    tension_cascade,
)


# ── Scalar constant tests ─────────────────────────────────────────────────────

class TestScalarConstants:
    def test_pillar_number(self):
        assert PILLAR == 772

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_status(self):
        assert STATUS == "LEPTON_JARLSKOG_LATTICE_DERIVED"

    def test_lean4_module(self):
        assert LEAN4_MODULE == "LeptonJarlskogLatticeClosure"

    def test_lean4_new_theorems(self):
        assert LEAN4_NEW_THEOREMS == 15

    def test_lean4_prev_total(self):
        assert LEAN4_PREV_TOTAL == 844

    def test_lean4_new_total(self):
        assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

    def test_lean4_new_total_value(self):
        assert LEAN4_NEW_TOTAL == 859

    def test_version_prefix(self):
        assert VERSION.startswith("v")

    def test_named_residual_not_needed(self):
        # The old DM21_RATIO_FN_CORRECTION_NEEDED residual is retired
        assert "NEEDED" not in NAMED_RESIDUAL

    def test_named_residual_contains_ljl(self):
        assert "LJL" in NAMED_RESIDUAL

    def test_pillar_591_label_upgrade(self):
        assert PILLAR_591_LABEL_UPGRADE == "FN_CHARGE_DERIVED"


# ── Float constant tests ──────────────────────────────────────────────────────

class TestFloatConstants:
    def test_delta_c(self):
        assert abs(DELTA_C - 5.0 / 74.0) < 1e-15

    def test_sin2_theta12(self):
        assert SIN2_THETA12 == pytest.approx(0.307, abs=1e-6)

    def test_sin2_theta13(self):
        assert SIN2_THETA13 == pytest.approx(0.02220, abs=1e-5)

    def test_sin2_theta23(self):
        assert SIN2_THETA23 == pytest.approx(0.546, abs=1e-4)

    def test_delta_cp_deg(self):
        assert DELTA_CP_DEG == pytest.approx(197.0, abs=0.1)

    def test_dm21_pdg(self):
        assert DM21_PDG_EV2 == pytest.approx(7.53e-5, rel=1e-3)

    def test_dm21_sigma(self):
        assert DM21_SIGMA_EV2 == pytest.approx(1.8e-6, rel=1e-3)

    def test_dm31_pdg(self):
        assert DM31_PDG_EV2 == pytest.approx(2.4109e-3, rel=1e-3)

    def test_j_ckm_pdg(self):
        assert J_CKM_PDG == pytest.approx(3.08e-5, rel=1e-3)

    def test_cos2_theta12_consistency(self):
        assert COS2_THETA12 == pytest.approx(1.0 - SIN2_THETA12, abs=1e-12)


# ── Neutrino lattice positions ────────────────────────────────────────────────

class TestNeutrinoLatticePositions:
    def test_l_nu3_is_zero(self):
        assert L_NU3 == 0

    def test_l_nu2_is_one(self):
        assert L_NU2 == 1

    def test_l_nu1_is_two(self):
        assert L_NU1 == 2

    def test_ordering_strictly_uv(self):
        assert L_NU1 > L_NU2 > L_NU3

    def test_neutrino_lattice_positions_function(self):
        pos = neutrino_lattice_positions()
        assert pos["l_nu3"] == 0
        assert pos["l_nu2"] == 1
        assert pos["l_nu1"] == 2
        assert pos["delta_l_nu12"] == 1
        assert pos["delta_l_nu23"] == 1
        assert pos["delta_l_nu13"] == 2

    def test_lattice_ordering_label(self):
        pos = neutrino_lattice_positions()
        assert "Normal Hierarchy" in pos["ordering"]

    def test_bc_type_label(self):
        pos = neutrino_lattice_positions()
        assert "Dirichlet" in pos["bc_type"]


# ── FN charge derivation ──────────────────────────────────────────────────────

class TestLeptonFNCharge:
    def test_n_fn_lepton_is_one(self):
        assert N_FN_LEPTON == 1

    def test_fn_charge_function(self):
        charge = lepton_fn_charge()
        assert charge["n_fn_lepton"] == 1
        assert charge["l_nu1"] == 2
        assert charge["l_nu2"] == 1
        assert charge["delta_c"] == pytest.approx(5.0 / 74.0, abs=1e-12)

    def test_fn_charge_derivation_status(self):
        charge = lepton_fn_charge()
        assert charge["derivation_status"] == "DERIVED"

    def test_fn_charge_not_assumed(self):
        charge = lepton_fn_charge()
        assert "ASSUMED" not in charge["derivation_status"]

    def test_fn_charge_pillar591_consistency(self):
        charge = lepton_fn_charge()
        assert charge["pillar_591_fn_charge"] == 1

    def test_epsilon_fn_equals_delta_c(self):
        charge = lepton_fn_charge()
        assert charge["epsilon_fn"] == pytest.approx(DELTA_C, abs=1e-12)


# ── J_PMNS computation ────────────────────────────────────────────────────────

class TestJPMNS:
    def test_j_pmns_nonzero(self):
        assert J_PMNS != 0.0

    def test_j_pmns_abs_positive(self):
        assert J_PMNS_ABS > 0.0

    def test_j_pmns_sign(self):
        # δ_CP = 197° → sin(197°) < 0 → J_PMNS < 0
        assert J_PMNS < 0.0

    def test_j_pmns_abs_order_of_magnitude(self):
        # J_PMNS ≈ 9.8×10⁻³ — much larger than J_CKM ≈ 3.1×10⁻⁵
        assert 5e-3 < J_PMNS_ABS < 2e-2

    def test_j_pmns_greater_than_j_ckm(self):
        assert J_PMNS_ABS > J_CKM_PDG

    def test_j_ratio_large(self):
        # J_PMNS/J_CKM ≈ 318
        assert J_RATIO > 100.0

    def test_j_ratio_value(self):
        assert J_RATIO == pytest.approx(J_PMNS_ABS / J_CKM_PDG, rel=1e-6)

    def test_j_pmns_full_function_keys(self):
        jdict = j_pmns_full()
        for key in ("sin2_theta12", "sin2_theta13", "sin2_theta23",
                    "delta_cp_deg", "J_PMNS", "J_PMNS_abs"):
            assert key in jdict

    def test_j_pmns_full_abs_consistent(self):
        jdict = j_pmns_full()
        assert jdict["J_PMNS_abs"] == pytest.approx(abs(jdict["J_PMNS"]), rel=1e-10)

    def test_j_ratio_function(self):
        ratio = j_lepton_to_ckm_ratio()
        assert ratio["ratio"] == pytest.approx(J_RATIO, rel=1e-6)
        assert ratio["is_parameter_free_prediction"] is True

    def test_j_ratio_log10_positive(self):
        ratio = j_lepton_to_ckm_ratio()
        assert ratio["log10_ratio"] > 0.0


# ── Mass ratio correction ─────────────────────────────────────────────────────

class TestMassRatioCorrection:
    def test_correction_fraction_positive(self):
        assert LEPTON_LJL_CORRECTION_FRAC > 0.0

    def test_correction_fraction_value(self):
        expected = 1 * (5.0 / 74.0) * (1.0 - 0.307)
        assert LEPTON_LJL_CORRECTION_FRAC == pytest.approx(expected, rel=1e-8)

    def test_correction_fraction_percent(self):
        # Should be ~4.7%
        assert 3.0 < 100.0 * LEPTON_LJL_CORRECTION_FRAC < 7.0

    def test_mass_ratio_correction_function(self):
        corr = lepton_lattice_mass_ratio_correction()
        assert corr["n_fn_lepton"] == 1
        assert corr["correction_fraction"] == pytest.approx(LEPTON_LJL_CORRECTION_FRAC, rel=1e-10)
        assert corr["correction_percent"] > 0.0

    def test_ratio_pdg_value(self):
        assert RATIO_PDG == pytest.approx(DM21_PDG_EV2 / DM31_PDG_EV2, rel=1e-6)

    def test_ratio_braid_value(self):
        assert abs(1.0 / RATIO_BRAID - 1.0 / 36) < 1e-12

    def test_ratio_error_pct_reduced_by_correction(self):
        corr = lepton_lattice_mass_ratio_correction()
        assert corr["ratio_after_error_pct"] < corr["ratio_error_pct_before"]


# ── DM21 cascade tests ────────────────────────────────────────────────────────

class TestDM21Cascade:
    def test_dm21_after_ljl_above_rge(self):
        assert DM21_AFTER_LJL > DM21_AFTER_RGE

    def test_dm21_after_ljl_below_pdg(self):
        assert DM21_AFTER_LJL < DM21_PDG_EV2

    def test_dm21_after_ljl_within_3sigma(self):
        assert abs(DM21_PDG_EV2 - DM21_AFTER_LJL) < 3.0 * DM21_SIGMA_EV2

    def test_tension_value(self):
        expected = abs(DM21_PDG_EV2 - DM21_AFTER_LJL) / DM21_SIGMA_EV2
        assert TENSION_AFTER_LJL == pytest.approx(expected, rel=1e-6)

    def test_tension_below_2sigma(self):
        assert TENSION_AFTER_LJL < 2.0

    def test_tension_above_1sigma(self):
        # Honest: 1.16σ is NOT sub-1σ
        assert TENSION_AFTER_LJL > 1.0

    def test_dm21_function_keys(self):
        d = dm21_after_lepton_lattice()
        for key in ("dm21_after_rge_ev2", "lepton_ljl_correction_frac",
                    "dm21_after_ljl_ev2", "tension_sigma",
                    "below_two_sigma", "below_one_sigma"):
            assert key in d

    def test_dm21_function_below_2sigma_true(self):
        d = dm21_after_lepton_lattice()
        assert d["below_two_sigma"] is True

    def test_dm21_function_below_1sigma_false(self):
        d = dm21_after_lepton_lattice()
        assert d["below_one_sigma"] is False

    def test_tension_cascade_length(self):
        cascade = tension_cascade()
        assert len(cascade) == 3

    def test_tension_cascade_monotone_improvement(self):
        cascade = tension_cascade()
        tensions = [c["tension_sigma"] for c in cascade]
        # Each step reduces tension
        assert tensions[0] > tensions[1] > tensions[2]

    def test_tension_cascade_step2_is_772(self):
        cascade = tension_cascade()
        assert cascade[2]["pillar"] == 772
        assert cascade[2]["fn_charge_status"] == "DERIVED"


# ── Closure status tests ──────────────────────────────────────────────────────

class TestClosureStatus:
    def test_closure_status_label(self):
        cs = closure_status()
        assert cs["closure_label"] == "QUANTIFIED_RESIDUAL_BELOW_2SIGMA"

    def test_closure_status_epistemic_label(self):
        cs = closure_status()
        assert cs["epistemic_label"] == EPISTEMIC_LABEL

    def test_closure_named_residual(self):
        cs = closure_status()
        assert cs["named_residual"] == NAMED_RESIDUAL

    def test_closure_residual_retired(self):
        cs = closure_status()
        assert "NEEDED" not in cs["named_residual"]

    def test_closure_pillar_585_upgrade(self):
        cs = closure_status()
        assert "DM21_RATIO_FN_CORRECTION_NEEDED" in cs["pillar_585_residual_upgrade"]

    def test_closure_pillar_591_upgrade(self):
        cs = closure_status()
        assert "DERIVED" in cs["pillar_591_label_upgrade"]

    def test_closure_below_2sigma(self):
        cs = closure_status()
        assert cs["below_2sigma"] is True

    def test_closure_not_below_1sigma(self):
        cs = closure_status()
        assert cs["below_1sigma"] is False


# ── Full certificate tests ────────────────────────────────────────────────────

class TestFullCertificate:
    def test_certificate_pillar(self):
        cert = full_closure_certificate()
        assert cert["pillar"] == 772

    def test_certificate_lean4_total(self):
        cert = full_closure_certificate()
        assert cert["lean4_new_total"] == 859

    def test_certificate_what_is_claimed(self):
        cert = full_closure_certificate()
        assert len(cert["what_is_claimed"]) >= 3

    def test_certificate_what_is_not_claimed(self):
        cert = full_closure_certificate()
        assert len(cert["what_is_NOT_claimed"]) >= 2

    def test_certificate_not_sub_1sigma_claimed(self):
        cert = full_closure_certificate()
        combined = " ".join(cert["what_is_claimed"])
        assert "sub-1" not in combined.lower() or "NOT" in combined

    def test_certificate_keys(self):
        cert = full_closure_certificate()
        for key in ("neutrino_lattice", "lepton_fn_charge", "j_pmns",
                    "j_ratio", "mass_ratio_correction", "dm21",
                    "cascade", "closure"):
            assert key in cert


# ── TEST_EXPECTATIONS meta-tests ──────────────────────────────────────────────

class TestExpectationsMeta:
    def test_scalar_expectations_pillar(self):
        assert TEST_EXPECTATIONS["scalar_checks"]["PILLAR"] == 772

    def test_scalar_expectations_n_fn(self):
        assert TEST_EXPECTATIONS["scalar_checks"]["N_FN_LEPTON"] == 1

    def test_scalar_expectations_lean4_total(self):
        assert TEST_EXPECTATIONS["scalar_checks"]["LEAN4_NEW_TOTAL"] == 859

    def test_float_expectations_delta_c(self):
        assert abs(TEST_EXPECTATIONS["float_checks"]["DELTA_C"] - 5.0 / 74.0) < 1e-15

    def test_required_symbols_present(self):
        import src.core.pillar772_lepton_jarlskog_lattice_closure as m
        for sym in TEST_EXPECTATIONS["required_symbols"]:
            assert hasattr(m, sym), f"Missing symbol: {sym}"

    def test_physics_checks_tension_below_2sigma(self):
        assert TEST_EXPECTATIONS["physics_checks"]["tension_below_2sigma"] is True

    def test_physics_checks_tension_not_below_1sigma(self):
        assert TEST_EXPECTATIONS["physics_checks"]["tension_below_1sigma"] is False

    def test_physics_checks_n_fn_is_one(self):
        assert TEST_EXPECTATIONS["physics_checks"]["n_fn_lepton_equals_one"] is True
