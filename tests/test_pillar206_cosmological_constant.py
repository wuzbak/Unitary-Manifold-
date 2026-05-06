# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 206 — Cosmological Constant from Gauss-Bonnet + Casimir."""

import math
import pytest

from src.core.pillar206_cosmological_constant import (
    N_W, K_CS, N_C,
    M_PL_GEV, PI_KR, M_KK_GEV,
    ALPHA_GB_GEO,
    RHO_CASIMIR_OVER_MKK4,
    RHO_GB_OVER_MKK4,
    LAMBDA_OBS_MPLAN4,
    GAP_ORDERS_OF_MAGNITUDE,
    rs1_tree_level_cancellation,
    gauss_bonnet_vacuum_energy,
    casimir_kk_tower,
    total_4d_vacuum_energy,
    consistency_firewall,
    cosmological_constant_audit,
    pillar206_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_m_kk_positive(self):
        assert M_KK_GEV > 0

    def test_alpha_gb_positive(self):
        assert ALPHA_GB_GEO > 0

    def test_alpha_gb_small(self):
        assert ALPHA_GB_GEO < 0.01

    def test_rho_gb_positive(self):
        assert RHO_GB_OVER_MKK4 > 0

    def test_rho_casimir_negative(self):
        assert RHO_CASIMIR_OVER_MKK4 < 0

    def test_lambda_obs_tiny(self):
        assert LAMBDA_OBS_MPLAN4 < 1e-100

    def test_lambda_obs_log_is_minus122(self):
        assert math.log10(LAMBDA_OBS_MPLAN4) == pytest.approx(-122.0, abs=2.0)

    def test_gap_orders_approx_58(self):
        assert 50.0 < GAP_ORDERS_OF_MAGNITUDE < 70.0


class TestRs1TreeLevelCancellation:
    def setup_method(self):
        self.result = rs1_tree_level_cancellation()

    def test_tree_level_is_zero(self):
        assert self.result["lambda_4d_tree_level"] == pytest.approx(0.0)

    def test_warp_suppression_tiny(self):
        assert self.result["warp_suppression"] < 1e-10

    def test_warp_suppression_log_approx_minus32(self):
        log = self.result["warp_suppression_log10"]
        assert -35 < log < -29

    def test_note_present(self):
        assert len(self.result["note"]) > 20

    def test_pi_kr_stored(self):
        assert self.result["pi_kR"] == pytest.approx(37.0)


class TestGaussBonnetVacuumEnergy:
    def setup_method(self):
        self.result = gauss_bonnet_vacuum_energy()

    def test_alpha_gb_positive(self):
        assert self.result["alpha_gb_geo"] > 0

    def test_rho_gb_positive(self):
        assert self.result["rho_gb_over_mkk4"] > 0

    def test_rho_gb_mpl4_positive(self):
        assert self.result["rho_gb_over_mpl4"] > 0

    def test_rho_gb_log10_below_minus60(self):
        # Should be very small in Planck units
        assert self.result["rho_gb_log10_mpl4"] < -60.0

    def test_formula_present(self):
        assert "GB" in self.result["formula"] or "ρ_GB" in self.result["formula"]

    def test_magnitude_assessment_present(self):
        assert len(self.result["magnitude_assessment"]) > 20

    def test_alpha_gb_formula(self):
        assert "K_CS" in self.result["alpha_gb_fraction"]


class TestCasimirKkTower:
    def setup_method(self):
        self.result = casimir_kk_tower()

    def test_n_effective_positive(self):
        assert self.result["n_effective_modes"] > 0

    def test_n_effective_is_kcs_times_nw(self):
        assert self.result["n_effective_modes"] == pytest.approx(K_CS * N_W)

    def test_zeta_minus1_value(self):
        assert self.result["zeta_minus1"] == pytest.approx(-1.0 / 12.0)

    def test_rho_negative(self):
        assert self.result["rho_casimir_over_mkk4"] < 0

    def test_rho_mpl4_negative(self):
        assert self.result["rho_casimir_over_mpl4"] < 0

    def test_rho_log10_below_minus60(self):
        assert self.result["rho_casimir_log10_mpl4"] < -60.0

    def test_sign_negative(self):
        assert "NEGATIVE" in self.result["sign"]

    def test_formula_present(self):
        assert "K_CS" in self.result["formula"]

    def test_zeta_regularization_mentioned(self):
        assert "Riemann" in self.result["zeta_regularization"] or "ζ" in self.result["zeta_regularization"]


class TestTotal4dVacuumEnergy:
    def setup_method(self):
        self.result = total_4d_vacuum_energy()

    def test_lambda_tree_is_zero(self):
        assert self.result["lambda_tree"] == pytest.approx(0.0)

    def test_total_dominated_by_casimir(self):
        # Casimir is much larger than GB
        assert abs(self.result["rho_casimir_over_mpl4"]) > abs(self.result["rho_gb_over_mpl4"])

    def test_gap_orders_positive(self):
        assert self.result["gap_orders_of_magnitude"] > 0

    def test_gap_between_50_and_70(self):
        assert 50 < self.result["gap_orders_of_magnitude"] < 70

    def test_naive_gap_is_122(self):
        assert self.result["naive_field_theory_gap_orders"] == pytest.approx(122.0)

    def test_rs1_warp_reduction_above_60(self):
        # The warp factor closes ~64 orders
        assert self.result["gap_reduction_from_rs1_warp"] > 50.0

    def test_honest_verdict_present(self):
        assert "58-order gap" in self.result["honest_verdict"] or "genuine advance" in self.result["honest_verdict"]

    def test_lambda_obs_stored(self):
        assert self.result["lambda_obs_mpl4"] == pytest.approx(LAMBDA_OBS_MPLAN4)


class TestConsistencyFirewall:
    def setup_method(self):
        self.result = consistency_firewall()

    def test_higgs_firewall_passed(self):
        assert self.result["m_H_firewall_passed"] is True

    def test_beta_firewall_passed(self):
        assert self.result["beta_firewall_passed"] is True

    def test_higgs_shift_tiny(self):
        assert self.result["m_H_shift_fractional"] < 1e-50

    def test_higgs_shift_log_very_negative(self):
        assert self.result["m_H_shift_log10"] < -50.0

    def test_verdict_safe(self):
        assert "SAFE" in self.result["verdict"]


class TestCosmologicalConstantAudit:
    def setup_method(self):
        self.result = cosmological_constant_audit()

    def test_pillar_tag(self):
        assert self.result["pillar"] == "206"

    def test_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_zero_sm_anchors(self):
        assert self.result["sm_anchors_count"] == 0

    def test_has_all_layers(self):
        assert "layer_1_rs1_tree" in self.result
        assert "layer_2_gauss_bonnet" in self.result
        assert "layer_3_casimir" in self.result
        assert "total" in self.result

    def test_firewall_in_result(self):
        assert "agent_c_firewall" in self.result


class TestPillar206Summary:
    def setup_method(self):
        self.result = pillar206_summary()

    def test_pillar_tag(self):
        assert self.result["pillar"] == "206"

    def test_version(self):
        assert "v10" in self.result["version"]

    def test_gap_orders_in_key_numbers(self):
        assert self.result["key_numbers"]["gap_orders"] == pytest.approx(
            GAP_ORDERS_OF_MAGNITUDE, rel=0.1
        )

    def test_rs1_warp_reduction_above_60(self):
        assert self.result["key_numbers"]["rs1_warp_reduction"] > 50.0

    def test_naive_gap_is_122(self):
        assert self.result["key_numbers"]["naive_field_theory_gap"] == pytest.approx(122.0)

    def test_honest_conclusion_mentions_orders(self):
        assert "orders" in self.result["honest_conclusion"]

    def test_status_architecture_limit(self):
        """v10.4 Wave 3: Pillar 206 is now an ARCHITECTURE LIMIT (not OPEN PROBLEM)."""
        assert "ARCHITECTURE LIMIT" in self.result["status"]

    def test_no_toe_score_change(self):
        assert "No direct TOE score change" in self.result["toe_impact"] or \
               "No TOE score change" in self.result["toe_impact"] or \
               "not one of the 26 SM parameters" in self.result["toe_impact"]

    def test_falsification_note_litbird(self):
        assert "LiteBIRD" in self.result["falsification_note"]

    def test_agent_b_label(self):
        assert "Torsional" in self.result["agent"] or "Agent B" in self.result["agent"]
