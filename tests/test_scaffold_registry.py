# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_scaffold_registry.py
=================================
Tests for src/core/scaffold_registry.py — v10.0 Scaffold Registry.
"""

from __future__ import annotations

import pytest

from src.core.scaffold_registry import (
    SCAFFOLD_REGISTRY,
    DERIVATION_REGISTRY,
    VERSION,
    scaffold_entry,
    derivation_entry,
    two_tier_audit_summary,
    scaffold_registry_summary,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_version_is_v10(self):
        assert VERSION == "v10.0"

    def test_scaffold_registry_is_dict(self):
        assert isinstance(SCAFFOLD_REGISTRY, dict)

    def test_derivation_registry_is_dict(self):
        assert isinstance(DERIVATION_REGISTRY, dict)

    def test_scaffold_registry_nonempty(self):
        assert len(SCAFFOLD_REGISTRY) >= 4

    def test_derivation_registry_nonempty(self):
        assert len(DERIVATION_REGISTRY) >= 4


# ===========================================================================
# Scaffold registry structure
# ===========================================================================

class TestScaffoldRegistry:
    def test_p1_fermion_cl_present(self):
        assert "P-1_fermion_cl_quantization" in SCAFFOLD_REGISTRY

    def test_p2_lambda_qcd_present(self):
        assert "P-2_lambda_qcd_gut_rge" in SCAFFOLD_REGISTRY

    def test_p3_goldberger_wise_present(self):
        assert "P-3_goldberger_wise" in SCAFFOLD_REGISTRY

    def test_p4_ckm_braid_present(self):
        assert "P-4_ckm_braid_lagrangian" in SCAFFOLD_REGISTRY

    def test_each_entry_has_module(self):
        for k, v in SCAFFOLD_REGISTRY.items():
            assert "module" in v, f"Key {k} missing 'module'"

    def test_each_entry_has_status(self):
        for k, v in SCAFFOLD_REGISTRY.items():
            assert "status" in v, f"Key {k} missing 'status'"

    def test_each_entry_has_gap_description(self):
        for k, v in SCAFFOLD_REGISTRY.items():
            assert "gap_description" in v, f"Key {k} missing 'gap_description'"

    def test_each_entry_has_derivation_module(self):
        for k, v in SCAFFOLD_REGISTRY.items():
            assert "derivation_module" in v, f"Key {k} missing 'derivation_module'"

    def test_p1_status_is_parameterized_constrained(self):
        assert "PARAMETERIZED" in SCAFFOLD_REGISTRY["P-1_fermion_cl_quantization"]["status"]

    def test_p2_status_is_constrained(self):
        assert "CONSTRAINED" in SCAFFOLD_REGISTRY["P-2_lambda_qcd_gut_rge"]["status"]

    def test_p3_status_is_optional(self):
        assert "OPTIONAL" in SCAFFOLD_REGISTRY["P-3_goldberger_wise"]["status"]

    def test_p4_pillar_is_184(self):
        assert SCAFFOLD_REGISTRY["P-4_ckm_braid_lagrangian"]["pillar"] == 184

    def test_p2_pillar_is_153(self):
        assert SCAFFOLD_REGISTRY["P-2_lambda_qcd_gut_rge"]["pillar"] == 153


# ===========================================================================
# Derivation registry structure
# ===========================================================================

class TestDerivationRegistry:
    def test_d1_rge_running_present(self):
        assert "D-1_rge_running" in DERIVATION_REGISTRY

    def test_d2_bulk_eigenvalues_present(self):
        assert "D-2_bulk_eigenvalues" in DERIVATION_REGISTRY

    def test_d3_gw_stabilizer_present(self):
        assert "D-3_gw_stabilizer" in DERIVATION_REGISTRY

    def test_d4_action_minimizer_present(self):
        assert "D-4_action_minimizer" in DERIVATION_REGISTRY

    def test_each_entry_has_title(self):
        for k, v in DERIVATION_REGISTRY.items():
            assert "title" in v, f"Key {k} missing 'title'"

    def test_each_entry_has_epistemic_status(self):
        for k, v in DERIVATION_REGISTRY.items():
            assert "epistemic_status" in v, f"Key {k} missing 'epistemic_status'"

    def test_each_entry_has_scaffold_replaced(self):
        for k, v in DERIVATION_REGISTRY.items():
            assert "scaffold_replaced" in v, f"Key {k} missing 'scaffold_replaced'"

    def test_each_entry_has_residual_gap(self):
        for k, v in DERIVATION_REGISTRY.items():
            assert "residual_gap" in v, f"Key {k} missing 'residual_gap'"

    def test_d1_status_is_geometric(self):
        assert "GEOMETRIC" in DERIVATION_REGISTRY["D-1_rge_running"]["epistemic_status"]

    def test_d3_status_is_proved(self):
        assert "PROVED" in DERIVATION_REGISTRY["D-3_gw_stabilizer"]["epistemic_status"]

    def test_d4_status_is_consistency_check(self):
        assert "CONSISTENCY" in DERIVATION_REGISTRY["D-4_action_minimizer"]["epistemic_status"]

    def test_d2_scaffold_replaced_is_p1(self):
        assert "P-1" in str(DERIVATION_REGISTRY["D-2_bulk_eigenvalues"]["scaffold_replaced"])

    def test_d1_scaffold_replaced_is_p2(self):
        assert "P-2" in str(DERIVATION_REGISTRY["D-1_rge_running"]["scaffold_replaced"])


# ===========================================================================
# scaffold_entry function
# ===========================================================================

class TestScaffoldEntry:
    def test_returns_dict(self):
        result = scaffold_entry("P-1_fermion_cl_quantization")
        assert isinstance(result, dict)

    def test_correct_key_returned(self):
        result = scaffold_entry("P-2_lambda_qcd_gut_rge")
        assert "status" in result
        assert "CONSTRAINED" in result["status"]

    def test_raises_keyerror_for_bad_key(self):
        with pytest.raises(KeyError):
            scaffold_entry("NONEXISTENT_KEY")

    def test_p3_module_points_to_goldberger_wise(self):
        result = scaffold_entry("P-3_goldberger_wise")
        assert "goldberger_wise" in result["module"]


# ===========================================================================
# derivation_entry function
# ===========================================================================

class TestDerivationEntry:
    def test_returns_dict(self):
        result = derivation_entry("D-1_rge_running")
        assert isinstance(result, dict)

    def test_correct_key_returned(self):
        result = derivation_entry("D-4_action_minimizer")
        assert "CONSISTENCY" in result["epistemic_status"]

    def test_raises_keyerror_for_bad_key(self):
        with pytest.raises(KeyError):
            derivation_entry("INVALID_KEY")

    def test_d3_module_points_to_gw_stabilizer(self):
        result = derivation_entry("D-3_gw_stabilizer")
        assert "gw_stabilizer" in result["module"]


# ===========================================================================
# two_tier_audit_summary
# ===========================================================================

class TestTwoTierAuditSummary:
    def setup_method(self):
        self.result = two_tier_audit_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_version_correct(self):
        assert self.result["version"] == VERSION

    def test_strategy_present(self):
        assert "strategy" in self.result
        assert len(self.result["strategy"]) > 20

    def test_n_scaffold_entries_correct(self):
        assert self.result["n_scaffold_entries"] == len(SCAFFOLD_REGISTRY)

    def test_n_derivation_entries_correct(self):
        assert self.result["n_derivation_entries"] == len(DERIVATION_REGISTRY)

    def test_pairs_present(self):
        assert "pairs" in self.result
        assert len(self.result["pairs"]) == len(DERIVATION_REGISTRY)

    def test_each_pair_has_keys(self):
        for pair in self.result["pairs"]:
            for key in [
                "scaffold_key", "derivation_key", "audit_finding_addressed", "residual_gap"
            ]:
                assert key in pair, f"Missing key '{key}' in pair"

    def test_what_is_not_changed_present(self):
        assert "what_is_not_changed" in self.result
        assert len(self.result["what_is_not_changed"]) >= 9

    def test_overall_upgrade_present(self):
        assert "overall_epistemic_upgrade" in self.result
        assert "v10.0" in self.result["overall_epistemic_upgrade"]

    def test_strategy_mentions_add_dont_lose(self):
        assert "ADD" in self.result["strategy"].upper()

    def test_phi0_closure_retained(self):
        retained = "\n".join(self.result["what_is_not_changed"])
        assert "phi0_closure" in retained

    def test_fermion_laplacian_retained(self):
        retained = "\n".join(self.result["what_is_not_changed"])
        assert "laplacian" in retained.lower()


# ===========================================================================
# scaffold_registry_summary
# ===========================================================================

class TestScaffoldRegistrySummary:
    def setup_method(self):
        self.result = scaffold_registry_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_version_v10(self):
        assert self.result["version"] == "v10.0"

    def test_n_scaffold_entries_geq_4(self):
        assert self.result["n_scaffold_entries"] >= 4

    def test_n_derivation_entries_geq_4(self):
        assert self.result["n_derivation_entries"] >= 4

    def test_scaffold_statuses_dict(self):
        assert isinstance(self.result["scaffold_statuses"], dict)

    def test_derivation_statuses_dict(self):
        assert isinstance(self.result["derivation_statuses"], dict)

    def test_all_scaffold_retained_true(self):
        assert self.result["all_scaffold_retained"] is True

    def test_all_tests_preserved_true(self):
        assert self.result["all_tests_preserved"] is True

    def test_derivation_modules_has_all_four(self):
        modules = self.result["derivation_modules"]
        assert any("rge_running" in v for v in modules.values())
        assert any("bulk_eigenvalues" in v for v in modules.values())
        assert any("gw_stabilizer" in v for v in modules.values())
        assert any("action_minimizer" in v for v in modules.values())
