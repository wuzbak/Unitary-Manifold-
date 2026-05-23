# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 387 — Formal Z₂-odd G_{μ5} Derivation from 5D Lagrangian."""

import math
import pytest
from src.core.pillar387_z2_odd_gmu5_derivation import (
    N_W, K_CS, K_R,
    Z2_PARITY_TABLE,
    metric_determinant_z2_constraint,
    cs_action_z2_constraint,
    action_consistency_derivation,
    z2_parity_derivation_table,
    admission_3_status_closure,
    pillar387_full_report,
)


class TestZ2ParityTable:
    def test_g_mu_nu_even(self):
        assert Z2_PARITY_TABLE["g_mu_nu"] == +1

    def test_phi_even(self):
        assert Z2_PARITY_TABLE["phi"] == +1

    def test_B_mu_odd(self):
        assert Z2_PARITY_TABLE["B_mu"] == -1

    def test_G_mu5_odd(self):
        assert Z2_PARITY_TABLE["G_mu5"] == -1

    def test_G_55_even(self):
        assert Z2_PARITY_TABLE["G_55"] == +1

    def test_phi_sq_Bmu_even(self):
        # φ² B_μ B_ν: even × odd × odd = even ✓
        assert Z2_PARITY_TABLE["phi_sq_Bmu"] == +1

    def test_G_mu5_equals_lambda_phi_Bmu(self):
        # G_{μ5} = λφB_μ: even × odd = odd → matches
        phi_parity = Z2_PARITY_TABLE["phi"]
        B_mu_parity = Z2_PARITY_TABLE["B_mu"]
        G_mu5_expected = phi_parity * B_mu_parity  # +1 × -1 = -1
        assert Z2_PARITY_TABLE["G_mu5"] == G_mu5_expected


class TestMetricDeterminantConstraint:
    @pytest.fixture
    def result(self):
        return metric_determinant_z2_constraint()

    def test_passed(self, result):
        assert result["passed"] is True

    def test_conclusion_mentions_B_mu_odd(self, result):
        conclusion = result["conclusion"]
        assert "Z₂-odd" in conclusion or "odd" in conclusion.lower()

    def test_has_phi_constraint(self, result):
        assert "phi" in result["phi_constraint"].lower() or "φ" in result["phi_constraint"]

    def test_has_B_mu_constraint(self, result):
        assert "B_mu" in result["B_mu_constraint"] or "B_μ" in result["B_mu_constraint"]

    def test_action_description(self, result):
        assert "S₅" in result["constraint"] or "Einstein" in result["constraint"]


class TestCSActionConstraint:
    @pytest.fixture
    def result(self):
        return cs_action_z2_constraint()

    def test_passed(self, result):
        assert result["passed"] is True

    def test_triangular_number(self, result):
        # T(5) = 15
        assert result["triangular_number"] == 15

    def test_eta_bar(self, result):
        # η̄(5) = T(5)/2 mod 1 = 15/2 mod 1 = 7.5 mod 1 = 0.5
        assert abs(result["eta_bar"] - 0.5) < 1e-10

    def test_cs_level_contribution(self, result):
        # K_CS × η̄ = 74 × 0.5 = 37
        assert abs(result["cs_level_contribution"] - 37.0) < 1e-10

    def test_parity_check_odd(self, result):
        # 37 is odd → n_w = 5 ✓
        assert result["parity_check"] is True

    def test_z2_odd_modes_mentioned(self, result):
        assert "odd" in result["z2_odd_modes"].lower()

    def test_zero_mode_argument(self, result):
        assert "zero mode" in result["z2_even_would_give"].lower()


class TestActionConsistencyDerivation:
    @pytest.fixture
    def result(self):
        return action_consistency_derivation()

    def test_both_constraints_pass(self, result):
        assert result["both_independent_constraints"] is True

    def test_admission_3_closed(self, result):
        assert result["admission_3_status"] == "FORMALLY_CLOSED"

    def test_conclusion_mentions_G_mu5(self, result):
        assert "G_{μ5}" in result["conclusion"] or "G_mu5" in result["conclusion"]

    def test_conclusion_mentions_derived(self, result):
        assert "DERIVED" in result["conclusion"]

    def test_residual_mentioned(self, result):
        assert "quantum" in result["residual_open"].lower() or "future" in result["residual_open"].lower()


class TestParityDerivationTable:
    @pytest.fixture
    def table(self):
        return z2_parity_derivation_table()

    def test_pillar_number(self, table):
        assert table["pillar"] == 387

    def test_all_components_present(self, table):
        expected = ["g_mu_nu", "phi", "B_mu", "G_mu5", "G_55"]
        for comp in expected:
            assert comp in table["components"]

    def test_B_mu_status_derived(self, table):
        assert "DERIVED" in table["components"]["B_mu"]["status"]

    def test_B_mu_prior_status_convention(self, table):
        assert "CONVENTION" in table["components"]["B_mu"]["prior_status"]

    def test_B_mu_parity_odd(self, table):
        assert table["components"]["B_mu"]["parity"] == -1

    def test_phi_parity_even(self, table):
        assert table["components"]["phi"]["parity"] == +1

    def test_G_55_parity_even(self, table):
        assert table["components"]["G_55"]["parity"] == +1

    def test_G_mu5_parity_odd(self, table):
        assert table["components"]["G_mu5"]["parity"] == -1


class TestAdmission3Closure:
    @pytest.fixture
    def cert(self):
        return admission_3_status_closure()

    def test_admission_number(self, cert):
        assert cert["admission_number"] == 3

    def test_pillar(self, cert):
        assert cert["pillar"] == 387

    def test_new_status_closed(self, cert):
        assert cert["new_status"] == "FORMALLY_CLOSED"

    def test_prior_status_convention(self, cert):
        assert "CONVENTION" in cert["prior_status"]

    def test_two_derivation_methods(self, cert):
        assert len(cert["derivation_method"]) == 2

    def test_nw_chain_complete(self, cert):
        assert "COMPLETE" in cert["nw_uniqueness_chain"]

    def test_impact_on_nw5_chain(self, cert):
        impact = cert["impact_on_nw5_chain"]
        assert "70-D" in impact

    def test_cs_constraint_present(self, cert):
        assert "cs_constraint" in cert

    def test_det_constraint_present(self, cert):
        assert "det_constraint" in cert


class TestFullReport:
    @pytest.fixture
    def report(self):
        return pillar387_full_report()

    def test_pillar_number(self, report):
        assert report["pillar"] == 387

    def test_status(self, report):
        assert report["status"] == "ADMISSION_3_FORMALLY_CLOSED"

    def test_epistemic_upgrade(self, report):
        assert "CONVENTION" in report["epistemic_upgrade"]
        assert "DERIVED" in report["epistemic_upgrade"]

    def test_key_result_mentions_5d(self, report):
        assert "5D" in report["key_result"] or "EH" in report["key_result"]

    def test_n_w_chain_status(self, report):
        assert "COMPLETE" in report["n_w_chain_status"]

    def test_classical_level_closed(self, report):
        assert "classical" in report["n_w_chain_status"].lower()

    def test_residual_quantum(self, report):
        assert "quantum" in report["residual"].lower()

    def test_action_derivation_present(self, report):
        assert "action_derivation" in report

    def test_parity_table_present(self, report):
        assert "parity_table" in report


class TestNW5ChainClosure:
    """Tests that verify the full n_w=5 derivation chain is now closed."""

    def test_chain_entry_g_mu5_z2_odd(self):
        # G_{μ5} must be Z₂-odd for the chain to work
        table = z2_parity_derivation_table()
        assert table["components"]["G_mu5"]["parity"] == -1

    def test_cs_level_contribution_odd(self):
        # k_CS × η̄ must be odd for n_w=5
        result = cs_action_z2_constraint()
        assert int(result["cs_level_contribution"]) % 2 == 1

    def test_eta_bar_half_integer(self):
        # η̄(5) = 0.5 (non-trivial spin structure)
        result = cs_action_z2_constraint()
        assert abs(result["eta_bar"] - 0.5) < 1e-10

    def test_cs_holonomy_non_zero(self):
        result = cs_action_z2_constraint()
        assert result["holonomy"] > 0

    def test_both_independent_constraints_pass(self):
        result = action_consistency_derivation()
        assert result["both_independent_constraints"] is True

    def test_admission_3_closed_certificate(self):
        cert = admission_3_status_closure()
        assert cert["new_status"] == "FORMALLY_CLOSED"
