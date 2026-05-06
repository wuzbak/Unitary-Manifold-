# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_bmu_ghost_stability.py
===================================
Tests for Pillar 198 — B_μ Ghost-Free Proof and Proca Stability.
"""
import math
import pytest
from src.core.bmu_ghost_stability import (
    bmu_kinetic_sign_proof,
    aps_ghost_protection,
    proca_stability_audit,
    lorentz_invariance_status,
    bmu_ghost_stability_verdict,
    bmu_pillar198_summary,
    ETA_BAR_NW5,
    ETA_BAR_NW7,
    M_KK_GEV,
    M_PL_GEV,
    ALPHA_RS1,
    LAMBDA_5D_GEV,
    N_W,
)


class TestKineticSignProof:
    def setup_method(self):
        self.result = bmu_kinetic_sign_proof()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 198

    def test_claim_ghost_free(self):
        assert "ghost" in self.result["claim"].lower() or "positive" in self.result["claim"].lower()

    def test_kinetic_sign_positive(self):
        assert self.result["kinetic_coefficient_sign"] == "POSITIVE"

    def test_phi_sq_positive(self):
        assert self.result["phi_sq_is_positive"] is True

    def test_has_five_steps(self):
        assert len(self.result["steps"]) == 5

    def test_conclusion_ghost_free(self):
        assert "GHOST-FREE" in self.result["conclusion"]

    def test_kinetic_coefficient_positive(self):
        assert self.result["numerical_coefficient"] > 0


class TestAPSGhostProtection:
    def test_nw5_non_trivial(self):
        result = aps_ghost_protection(5)
        assert abs(result["eta_bar"] - 0.5) < 1e-10

    def test_nw7_trivial(self):
        result = aps_ghost_protection(7)
        assert abs(result["eta_bar"] - 0.0) < 1e-10

    def test_nw5_path_integral_phase_is_i(self):
        result = aps_ghost_protection(5)
        # exp(iπ×½) = exp(iπ/2) = i → Re=0, Im=1
        assert abs(result["path_integral_phase_Re"]) < 1e-10
        assert abs(result["path_integral_phase_Im"] - 1.0) < 1e-10

    def test_nw5_path_integral_phase_is_i_flag(self):
        result = aps_ghost_protection(5)
        assert result["path_integral_phase_is_i"] is True

    def test_nw7_path_integral_phase_is_real(self):
        result = aps_ghost_protection(7)
        # exp(0) = 1 → Re=1, Im=0
        assert abs(result["path_integral_phase_Re"] - 1.0) < 1e-10
        assert abs(result["path_integral_phase_Im"]) < 1e-10

    def test_nw5_protected(self):
        result = aps_ghost_protection(5)
        assert "PROTECTED" in result["ghost_protection_status"]

    def test_nw7_vulnerable(self):
        result = aps_ghost_protection(7)
        assert "VULNERABLE" in result["ghost_protection_status"]

    def test_eta_bar_values_correct(self):
        assert ETA_BAR_NW5 == 0.5
        assert ETA_BAR_NW7 == 0.0

    def test_unknown_nw_raises_value_error(self):
        with pytest.raises(ValueError, match="not in the supported set"):
            aps_ghost_protection(3)


class TestProcaStabilityAudit:
    def setup_method(self):
        self.result = proca_stability_audit(M_KK_GEV, LAMBDA_5D_GEV)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 198

    def test_proca_stable(self):
        assert self.result["proca_stable"] is True

    def test_safety_margin_positive(self):
        assert self.result["safety_margin_ratio"] > 1.0

    def test_log10_margin_large(self):
        # M_Pl/m_KK ≈ 1.221e19 / 1040 ≈ 1.2e16 → log10 ≈ 16
        # Divided by 2π → log10 ≈ 15.2
        assert self.result["log10_safety_margin"] > 14.0

    def test_mass_origin_stuckelberg(self):
        assert "Stückelberg" in self.result["mass_origin"] or "KK" in self.result["mass_origin"]

    def test_ghost_mass_much_larger_than_bmu(self):
        assert self.result["m_ghost_gev"] > self.result["m_bmu_gev"]

    def test_verdict_stable(self):
        assert "STABLE" in self.result["verdict"]

    def test_zero_mass_infinite_margin(self):
        result = proca_stability_audit(0.0, LAMBDA_5D_GEV)
        assert result["safety_margin_ratio"] == math.inf


class TestLorentzInvarianceStatus:
    def setup_method(self):
        self.result = lorentz_invariance_status()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 198

    def test_5d_action_is_lorentz_invariant(self):
        assert self.result["5d_action_lorentz_invariant"] is True

    def test_breaking_is_spontaneous(self):
        assert "SPONTANEOUS" in self.result["breaking_type"]

    def test_no_explicit_breaking(self):
        assert self.result["explicit_breaking"] is False

    def test_4d_poincare_preserved(self):
        assert self.result["4d_poincare_preserved"] is True

    def test_arrow_of_time_conjectural(self):
        # Arrow-of-time identification is explicitly labeled conjectural
        assert "CONJECTURAL" in self.result["arrow_of_time_origin"].upper()

    def test_has_frw_analogy(self):
        assert "FRW" in self.result["comparison"] or "cosmological" in self.result["comparison"].lower()

    def test_verdict_preserved(self):
        assert "PRESERVED" in self.result["verdict"].upper()


class TestGhostStabilityVerdict:
    def setup_method(self):
        self.result = bmu_ghost_stability_verdict()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 198

    def test_version(self):
        assert self.result["version"] == "v10.2"

    def test_ghost_free(self):
        assert self.result["ghost_free"] is True

    def test_proca_stable(self):
        assert self.result["proca_stable"] is True

    def test_lorentz_5d_preserved(self):
        assert self.result["lorentz_5d_preserved"] is True

    def test_aps_protects_ghost(self):
        assert self.result["aps_protects_ghost"] is True

    def test_overall_safe(self):
        assert self.result["overall_safe"] is True

    def test_verdict_pass(self):
        assert "PASS" in self.result["overall_verdict"]

    def test_has_all_four_proofs(self):
        assert "kinetic_proof" in self.result
        assert "aps_proof" in self.result
        assert "proca_proof" in self.result
        assert "lorentz_proof" in self.result


class TestPillar198Summary:
    def setup_method(self):
        self.result = bmu_pillar198_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 198

    def test_name_correct(self):
        assert "Ghost" in self.result["name"] or "ghost" in self.result["name"].lower()

    def test_verdict_triple(self):
        verdict = self.result["verdict"]
        assert "GHOST-FREE" in verdict
        assert "PROCA-STABLE" in verdict
        assert "LORENTZ-PRESERVED" in verdict

    def test_aps_connection_stated(self):
        assert "η̄" in self.result["aps_connection"] or "eta" in self.result["aps_connection"].lower()

    def test_next_attack_documented(self):
        assert "next_attack_anticipated" in self.result
        assert "loop" in self.result["next_attack_anticipated"].lower()

    def test_loop_correction_answer_provided(self):
        answer = self.result["next_attack_anticipated"]
        # Should mention that APS is non-perturbative
        assert "non-perturbative" in answer.lower() or "topological" in answer.lower()


class TestPhysicalConsistency:
    """Cross-module consistency checks for Pillar 198."""

    def test_alpha_matches_rs1_value(self):
        assert abs(ALPHA_RS1 - 1.0 / math.sqrt(6.0)) < 1e-10

    def test_nw_is_5(self):
        assert N_W == 5

    def test_kk_mass_positive(self):
        assert M_KK_GEV > 0

    def test_planck_mass_larger_than_kk(self):
        assert M_PL_GEV > M_KK_GEV

    def test_aps_half_integer_for_nw5(self):
        # η̄ = ½ is half-integer → (2η̄) is odd integer
        two_eta = round(2.0 * ETA_BAR_NW5)
        assert abs(2.0 * ETA_BAR_NW5 - two_eta) < 1e-10  # exact representation
        assert two_eta % 2 == 1  # odd → non-trivial spin structure

    def test_aps_integer_for_nw7(self):
        # η̄ = 0 is integer → trivial spin structure
        assert abs(ETA_BAR_NW7 % 1) < 1e-10
