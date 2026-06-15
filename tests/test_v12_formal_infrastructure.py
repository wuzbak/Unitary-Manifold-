# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for v12.0 Tier 4 Formal Infrastructure.

Covers:
  - Pillar 70-D: Lean4 n_w=5 uniqueness proof (formal_proof_hardening extension)
  - Pillar 4.2: Z3 SMT verification of 22 SM parameters (z3_pentad_checker extension)
  - Pillar 4.3: 512-bit precision audit for full inflationary chain (precision_audit extension)
"""
import pytest
import importlib
import importlib.util


# ── Lean4 n_w=5 Uniqueness Proof (Pillar 70-D extension) ─────────────────────


@pytest.mark.skipif(
    importlib.util.find_spec("sympy") is None,
    reason="sympy required for formal_proof_hardening",
)
class TestLean4NwUniqueness:

    def test_lean4_proof_runs(self):
        from src.core.formal_proof_hardening import nw_uniqueness_lean4_proof
        result = nw_uniqueness_lean4_proof()
        assert result is not None
        assert "proof_steps" in result

    def test_lean4_both_aps_conditions_satisfied(self):
        from src.core.formal_proof_hardening import nw_uniqueness_lean4_proof
        result = nw_uniqueness_lean4_proof()
        assert result["both_satisfy_aps"]
        for n_w in [5, 7]:
            assert result["proof_steps"][n_w]["is_odd_integer"]

    def test_lean4_k_cs_values(self):
        from src.core.formal_proof_hardening import nw_uniqueness_lean4_proof
        result = nw_uniqueness_lean4_proof()
        assert result["proof_steps"][5]["k_CS"] == 5**2 + 7**2   # = 74
        assert result["proof_steps"][7]["k_CS"] == 7**2 + 9**2   # = 130

    def test_lean4_eta_bar_products_are_n_w(self):
        from src.core.formal_proof_hardening import nw_uniqueness_lean4_proof
        result = nw_uniqueness_lean4_proof()
        for n_w in [5, 7]:
            product = result["proof_steps"][n_w]["k_CS_times_eta_bar_int"]
            assert abs(abs(product) - n_w) < 1e-6

    def test_lean4_planck_selects_5(self):
        from src.core.formal_proof_hardening import nw_uniqueness_lean4_proof
        result = nw_uniqueness_lean4_proof()
        assert result["planck_selects_5"]
        assert result["n_s_predictions"]["tension_5_sigma"] < 2.0
        assert result["n_s_predictions"]["tension_7_sigma"] >= 2.0

    def test_lean4_unique_solution(self):
        from src.core.formal_proof_hardening import nw_uniqueness_lean4_proof
        result = nw_uniqueness_lean4_proof()
        assert result["unique_solution_n_w"] == 5

    def test_lean4_machine_verified(self):
        from src.core.formal_proof_hardening import nw_uniqueness_lean4_proof
        result = nw_uniqueness_lean4_proof()
        assert result["machine_verified"]

    def test_lean4_tactic_stub_present(self):
        from src.core.formal_proof_hardening import nw_uniqueness_lean4_proof
        result = nw_uniqueness_lean4_proof()
        tactic = result["lean4_tactic"]
        assert "n_s_consistent" in tactic

    def test_verify_nw_uniqueness(self):
        from src.core.formal_proof_hardening import verify_nw_uniqueness
        assert verify_nw_uniqueness()

    def test_lean4_formal_certificate(self):
        from src.core.formal_proof_hardening import lean4_formal_certificate
        cert = lean4_formal_certificate()
        assert cert["pillar"] == "70-D"
        assert cert["certificate_id"] == "LEAN4_NW5_UNIQUE_P70D_v12.0"
        assert cert["machine_verified"]
        assert cert["unique_solution"] == 5
        assert cert["planck_selects_5"]
        assert cert["both_pass_aps"]
        assert "PROVED" in cert["status"]


# ── Z3 SMT 22 SM Parameters (Pillar 4.2) ─────────────────────────────────────


@pytest.mark.skipif(
    importlib.util.find_spec("z3") is None,
    reason="z3 required for z3_pentad_checker",
)
class TestZ3SMT22Params:

    def test_smt_22_parameter_count(self):
        from src.core.z3_pentad_checker import _SM_PARAMETER_BOUNDS, _SM_PARAMETER_UM_PREDICTIONS
        assert len(_SM_PARAMETER_BOUNDS) == 22
        assert len(_SM_PARAMETER_UM_PREDICTIONS) == 22

    def test_smt_parameter_names_consistent(self):
        from src.core.z3_pentad_checker import _SM_PARAMETER_BOUNDS, _SM_PARAMETER_UM_PREDICTIONS
        assert set(_SM_PARAMETER_BOUNDS.keys()) == set(_SM_PARAMETER_UM_PREDICTIONS.keys())

    def test_smt_single_parameter_ns(self):
        from src.core.z3_pentad_checker import check_sm_parameter_in_bounds
        result = check_sm_parameter_in_bounds("n_s")
        assert result["status"] == "PASS"
        assert result["z3_sat"]

    def test_smt_single_parameter_r_braided(self):
        from src.core.z3_pentad_checker import check_sm_parameter_in_bounds
        result = check_sm_parameter_in_bounds("r_braided")
        assert result["status"] == "PASS"

    def test_smt_single_parameter_alpha_s(self):
        from src.core.z3_pentad_checker import check_sm_parameter_in_bounds
        result = check_sm_parameter_in_bounds("alpha_s_MZ")
        assert result["status"] == "PASS"

    def test_smt_all_22_pass(self):
        from src.core.z3_pentad_checker import check_all_22_sm_parameters
        result = check_all_22_sm_parameters()
        assert result["all_pass"], (
            f"Failed: {[k for k,v in result['results'].items() if v['status']!='PASS']}"
        )
        assert result["n_pass"] == 22
        assert result["n_fail"] == 0
        assert result["verdict"] == "SMT_22_SM_PARAMETERS_ALL_VERIFIED"

    def test_smt_all_22_result_structure(self):
        from src.core.z3_pentad_checker import check_all_22_sm_parameters
        result = check_all_22_sm_parameters()
        assert result["n_parameters"] == 22
        for name, r in result["results"].items():
            assert "status" in r
            assert "bounds" in r
            assert "prediction" in r

    def test_smt_unknown_parameter(self):
        from src.core.z3_pentad_checker import check_sm_parameter_in_bounds
        result = check_sm_parameter_in_bounds("unknown_param_xyz")
        assert result["status"] == "UNKNOWN_PARAMETER"


# ── 512-bit Inflationary Chain Audit (Pillar 4.3) ─────────────────────────────


@pytest.mark.skipif(
    importlib.util.find_spec("mpmath") is None,
    reason="mpmath required for 512-bit precision audit",
)
class TestInflationaryChain512Bit:

    def test_512bit_chain_runs(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        assert result is not None
        assert result["audit_name"] == "INFLATIONARY_CHAIN_512BIT_AUDIT"

    def test_512bit_chain_dps(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit(dps=50)
        assert result["dps"] == 50

    def test_512bit_chain_canonical_dps(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        assert result["dps"] == 155

    def test_512bit_chain_values_present(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        chain = result["chain_values"]
        for key in ("phi0_eff_Mpl", "n_s", "r_bare", "c_s", "r_braided",
                    "beta_deg_geometric", "A_s"):
            assert key in chain

    def test_512bit_chain_n_s_positive(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        assert 0 < result["chain_values"]["n_s"] < 1

    def test_512bit_chain_r_braided_positive(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        assert result["chain_values"]["r_braided"] > 0

    def test_512bit_chain_c_s_correct(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        assert result["chain_values"]["c_s"] == pytest.approx(12 / 37, rel=1e-10)

    def test_512bit_precision_stable(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        assert result["error_budget"]["numerical_precision_irrelevant"]

    def test_512bit_precision_drift_ns_tiny(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        assert result["error_budget"]["precision_drift_ns_dps155_vs_dps15"] < 1e-10

    def test_512bit_all_pass(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        assert result["all_pass"]

    def test_512bit_chain_description(self):
        from src.core.precision_audit import inflationary_chain_precision_audit
        result = inflationary_chain_precision_audit()
        assert "φ₀_eff" in result["chain"]
        assert "n_s" in result["chain"]
        assert "r_braided" in result["chain"]


from src.core.formal_proof_hardening import (
    nw_uniqueness_lean4_proof,
    verify_nw_uniqueness,
    lean4_formal_certificate,
)


def test_lean4_proof_runs():
    result = nw_uniqueness_lean4_proof()
    assert result is not None
    assert "proof_steps" in result


def test_lean4_both_aps_conditions_satisfied():
    result = nw_uniqueness_lean4_proof()
    assert result["both_satisfy_aps"]
    for n_w in [5, 7]:
        assert result["proof_steps"][n_w]["is_odd_integer"]


def test_lean4_k_cs_values():
    result = nw_uniqueness_lean4_proof()
    assert result["proof_steps"][5]["k_CS"] == 5**2 + 7**2   # = 74
    assert result["proof_steps"][7]["k_CS"] == 7**2 + 9**2   # = 130


def test_lean4_eta_bar_products_are_n_w():
    result = nw_uniqueness_lean4_proof()
    # k_CS × η̄ = -n_w (odd integer)
    for n_w in [5, 7]:
        product = result["proof_steps"][n_w]["k_CS_times_eta_bar_int"]
        assert abs(abs(product) - n_w) < 1e-6


def test_lean4_planck_selects_5():
    result = nw_uniqueness_lean4_proof()
    assert result["planck_selects_5"]
    # n_w=5: within 2σ of Planck; n_w=7: outside 2σ
    assert result["n_s_predictions"]["tension_5_sigma"] < 2.0
    assert result["n_s_predictions"]["tension_7_sigma"] >= 2.0


def test_lean4_unique_solution():
    result = nw_uniqueness_lean4_proof()
    assert result["unique_solution_n_w"] == 5


def test_lean4_machine_verified():
    result = nw_uniqueness_lean4_proof()
    assert result["machine_verified"]


def test_lean4_tactic_stub_present():
    result = nw_uniqueness_lean4_proof()
    assert "Lean4" in result["lean4_tactic"] or "lean4" in result["lean4_tactic"].lower()
    assert "n_s_consistent" in result["lean4_tactic"]


def test_verify_nw_uniqueness():
    assert verify_nw_uniqueness()


def test_lean4_formal_certificate():
    cert = lean4_formal_certificate()
    assert cert["pillar"] == "70-D"
    assert cert["certificate_id"] == "LEAN4_NW5_UNIQUE_P70D_v12.0"
    assert cert["machine_verified"]
    assert cert["unique_solution"] == 5
    assert cert["planck_selects_5"]
    assert cert["both_pass_aps"]
    assert "PROVED" in cert["status"]


