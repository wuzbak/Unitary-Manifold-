# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar384_metric_ansatz_uniqueness.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar384_metric_ansatz_uniqueness import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    separation_guard,
    count_metric_components,
    z2_parity_constraint,
    kk_gauge_covariance_constraint,
    radion_normalization_constraint,
    einstein_hilbert_stationarity,
    check_ansatz_uniqueness,
    uniqueness_proof,
    metric_ansatz_upgrade_certificate,
    pillar384_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 384
    def test_status(self): assert PILLAR_STATUS == "DERIVED_UNIQUE"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_derived_unique(self): assert "DERIVED_UNIQUE" in separation_guard()
    def test_metric_ansatz(self): assert "G_AB" in separation_guard() or "metric" in separation_guard().lower()


class TestCountMetricComponents:
    def test_returns_dict(self): assert isinstance(count_metric_components(), dict)

    def test_total_components(self):
        r = count_metric_components()
        assert r["total_g_ab_components"] == 15

    def test_physical_components(self):
        r = count_metric_components()
        assert r["physical_components"] == 10

    def test_decomposition_consistent(self):
        r = count_metric_components()
        assert r["decomposition_consistent"] is True

    def test_unique_decomposition(self):
        r = count_metric_components()
        assert r["unique_decomposition"] is True

    def test_component_sum(self):
        r = count_metric_components()
        assert r["decomposition_total"] == 10

    def test_field_total_offshell(self):
        r = count_metric_components()
        assert r["field_total_offshell"] == 15

    def test_g_munu_components(self):
        r = count_metric_components()
        assert r["g_munu_components"] == 10

    def test_b_mu_components(self):
        r = count_metric_components()
        assert r["b_mu_components"] == 4

    def test_phi_components(self):
        r = count_metric_components()
        assert r["phi_components"] == 1


class TestZ2ParityConstraint:
    def test_returns_dict(self): assert isinstance(z2_parity_constraint(), dict)

    def test_constraint_satisfied(self):
        r = z2_parity_constraint()
        assert r["constraint_satisfied"] is True

    def test_g_munu_even(self):
        r = z2_parity_constraint()
        assert r["g_munu"]["parity"] == "Z2-EVEN"
        assert r["g_munu"]["valid"] is True

    def test_g_mu5_odd(self):
        r = z2_parity_constraint()
        assert r["g_mu5"]["parity"] == "Z2-ODD"
        assert r["g_mu5"]["valid"] is True

    def test_g_55_even(self):
        r = z2_parity_constraint()
        assert r["g_55"]["parity"] == "Z2-EVEN"
        assert r["g_55"]["valid"] is True

    def test_dirichlet_bc_in_g_mu5(self):
        r = z2_parity_constraint()
        assert "0" in r["g_mu5"]["bc"]

    def test_eliminates_parity_violating(self):
        r = z2_parity_constraint()
        assert "parity" in r["eliminates"].lower()


class TestKKGaugeCovariance:
    def test_returns_dict(self): assert isinstance(kk_gauge_covariance_constraint(), dict)

    def test_selected_power_is_1(self):
        r = kk_gauge_covariance_constraint()
        assert r["selected_power"] == 1

    def test_selected_form(self):
        r = kk_gauge_covariance_constraint()
        assert "φ B_μ" in r["selected_form"] or "phi B_mu" in r["selected_form"]

    def test_uniqueness(self):
        r = kk_gauge_covariance_constraint()
        assert "UNIQUE" in r["uniqueness"]

    def test_valid(self):
        r = kk_gauge_covariance_constraint()
        assert r["valid"] is True

    def test_alternative_powers_tested(self):
        r = kk_gauge_covariance_constraint()
        assert "n_1" in r["alternative_powers_tested"]
        assert "n_0" in r["alternative_powers_tested"]

    def test_n1_canonical(self):
        r = kk_gauge_covariance_constraint()
        assert r["alternative_powers_tested"]["n_1"]["canonical_gauge_kinetic"] is True

    def test_n2_not_canonical(self):
        r = kk_gauge_covariance_constraint()
        assert r["alternative_powers_tested"]["n_2"]["canonical_gauge_kinetic"] is False


class TestRadionNormalization:
    def test_returns_dict(self): assert isinstance(radion_normalization_constraint(), dict)

    def test_selected_power_is_2(self):
        r = radion_normalization_constraint()
        assert r["selected_power"] == 2

    def test_selected_form(self):
        r = radion_normalization_constraint()
        assert "φ²" in r["selected_form"] or "phi^2" in r["selected_form"]

    def test_uniqueness(self):
        r = radion_normalization_constraint()
        assert "UNIQUE" in r["uniqueness"]

    def test_valid(self):
        r = radion_normalization_constraint()
        assert r["valid"] is True

    def test_alternative_n1_not_canonical(self):
        r = radion_normalization_constraint()
        assert r["alternative_powers_tested"]["n_1"]["canonical_form"] is False

    def test_n2_canonical(self):
        r = radion_normalization_constraint()
        assert r["alternative_powers_tested"]["n_2"]["canonical_form"] is True

    def test_n3_not_canonical(self):
        r = radion_normalization_constraint()
        assert r["alternative_powers_tested"]["n_3"]["canonical_form"] is False


class TestEinsteinHilbertStationarity:
    def test_returns_dict(self): assert isinstance(einstein_hilbert_stationarity(), dict)

    def test_selected_c_is_1(self):
        r = einstein_hilbert_stationarity()
        assert abs(r["selected_c"] - 1.0) < 1e-10

    def test_uniqueness(self):
        r = einstein_hilbert_stationarity()
        assert "UNIQUE" in r["uniqueness"]

    def test_valid(self):
        r = einstein_hilbert_stationarity()
        assert r["valid"] is True

    def test_c1_canonical(self):
        r = einstein_hilbert_stationarity()
        assert r["alternative_c_tested"]["c_1.0"]["canonical_gauge_kinetic"] is True

    def test_c05_not_canonical(self):
        r = einstein_hilbert_stationarity()
        assert r["alternative_c_tested"]["c_0.5"]["canonical_gauge_kinetic"] is False


class TestCheckAnsatzUniqueness:
    def test_returns_dict(self): assert isinstance(check_ansatz_uniqueness(), dict)

    def test_all_constraints_satisfied(self):
        r = check_ansatz_uniqueness()
        assert r["all_constraints_satisfied"] is True

    def test_uniqueness_verdict(self):
        r = check_ansatz_uniqueness()
        assert "UNIQUE" in r["uniqueness_verdict"]

    def test_all_four_constraints_present(self):
        r = check_ansatz_uniqueness()
        assert "c1_eh_stationarity" in r
        assert "c2_kk_gauge_covariance" in r
        assert "c3_z2_parity" in r
        assert "c4_radion_normalization" in r


class TestUniquenessProof:
    def test_returns_dict(self): assert isinstance(uniqueness_proof(), dict)

    def test_theorem_present(self):
        r = uniqueness_proof()
        assert "theorem" in r
        assert "UNIQUE" in r["theorem"]

    def test_four_proof_steps(self):
        r = uniqueness_proof()
        assert len(r["proof_steps"]) == 4

    def test_steps_numbered(self):
        r = uniqueness_proof()
        for i, step in enumerate(r["proof_steps"], 1):
            assert step["step"] == i

    def test_final_result_present(self):
        r = uniqueness_proof()
        assert "final_result" in r
        assert "φ²" in r["final_result"] or "phi^2" in r["final_result"]

    def test_uniqueness_guarantee(self):
        r = uniqueness_proof()
        assert "uniqueness_guarantee" in r

    def test_steps_cover_all_constraints(self):
        r = uniqueness_proof()
        constraints = [s["constraint"] for s in r["proof_steps"]]
        assert any("C1" in c for c in constraints)
        assert any("C2" in c for c in constraints)
        assert any("C3" in c for c in constraints)
        assert any("C4" in c for c in constraints)


class TestMetricAnsatzUpgradeCertificate:
    def test_returns_dict(self): assert isinstance(metric_ansatz_upgrade_certificate(), dict)

    def test_all_conditions_met(self):
        r = metric_ansatz_upgrade_certificate()
        assert r["all_conditions_met"] is True

    def test_new_status(self):
        r = metric_ansatz_upgrade_certificate()
        assert r["new_status"] == "DERIVED_UNIQUE"

    def test_certificate_status(self):
        r = metric_ansatz_upgrade_certificate()
        assert "METRIC_ANSATZ_DERIVED_UNIQUE" in r["certificate_status"]

    def test_proof_theorem_present(self):
        r = metric_ansatz_upgrade_certificate()
        assert "proof_theorem" in r
        assert len(r["proof_theorem"]) > 50

    def test_uniqueness_method_present(self):
        r = metric_ansatz_upgrade_certificate()
        assert "uniqueness_method" in r

    def test_residual_present(self):
        r = metric_ansatz_upgrade_certificate()
        assert "residual" in r


class TestPillar384Summary:
    def test_returns_dict(self): assert isinstance(pillar384_summary(), dict)

    def test_pillar_number(self):
        r = pillar384_summary()
        assert r["pillar_number"] == PILLAR_NUMBER

    def test_status(self):
        r = pillar384_summary()
        assert r["status"] == "DERIVED_UNIQUE"

    def test_key_result(self):
        r = pillar384_summary()
        assert "UNIQUE" in r["key_result"]
        assert "C1" in r["key_result"] or "EH" in r["key_result"]

    def test_previous_status(self):
        r = pillar384_summary()
        assert "DERIVED" in r["previous_status"]

    def test_new_status(self):
        r = pillar384_summary()
        assert r["new_status"] == "DERIVED_UNIQUE"

    def test_falsification_present(self):
        r = pillar384_summary()
        assert "falsification" in r
