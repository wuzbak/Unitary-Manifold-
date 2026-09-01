# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 860 — Sprint BA master certificate."""
from __future__ import annotations

from src.core.pillar860_sprint_ba_regression_certificate import (
    ARCHITECTURE_LIMITS_CERTIFIED,
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    PILLARS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SPRINT_NAME,
    SPRINT_VALID,
    SPRINT_VERSION,
    cross_dimensional_coverage_check,
    sprint_ba_summary,
    validate_sprint,
)


class TestPillar860Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 860
    def test_gate(self): assert PILLAR_GATE == "SPRINT_BA_REGRESSION_CERTIFICATE"
    def test_sprint_name(self): assert "Sprint BA" in SPRINT_NAME
    def test_sprint_version(self): assert SPRINT_VERSION == "v25.5"
    def test_lean4_start(self): assert LEAN4_START == 1821
    def test_lean4_end(self): assert LEAN4_END == 2186
    def test_lean4_delta(self): assert LEAN4_DELTA == 365
    def test_pillar_registry_size(self): assert len(PILLARS) == 18
    def test_remaining_open_size(self): assert len(REMAINING_OPEN) == 10
    def test_architecture_limits_size(self): assert len(ARCHITECTURE_LIMITS_CERTIFIED) == 5
    def test_sprint_valid(self): assert SPRINT_VALID is True


class TestPillar860Registry:
    def test_phases_present(self):
        assert {p["phase"] for p in PILLARS} == {1, 2, 3, 4, 5}

    def test_numbers_present(self):
        numbers = [p["number"] for p in PILLARS]
        for n in (837, 838, 839, 840, 841, 842, 843, 844, 846, 849, 850, 852, 853, 854, 855, 856, 858, 859):
            assert n in numbers

    def test_gate_858_present(self):
        assert any(p["gate"] == "CROSS_DIMENSIONAL_CHAIN_CLOSED" for p in PILLARS)

    def test_gate_859_present(self):
        assert any(p["gate"] == "LEAN4_MASTER_THEOREM_11D_TO_4D" for p in PILLARS)

    def test_total_lean4_matches(self):
        assert sum(p["lean4_theorems"] for p in PILLARS) == 365


class TestPillar860OpenItems:
    def test_kklt_item_present(self):
        assert any(item.startswith("KKLT_NONPERTURBATIVE_COMPLETION_OPEN") for item in REMAINING_OPEN)

    def test_e8_item_present(self):
        assert any(item.startswith("E8_BREAKING_PATTERN_OPEN") for item in REMAINING_OPEN)

    def test_cmb_item_present(self):
        assert any(item.startswith("CMB_PEAK_AMPLITUDE_OPEN") for item in REMAINING_OPEN)

    def test_litebird_item_present(self):
        assert any(item.startswith("LITEBIRD_BIREFRINGENCE_OPEN") for item in REMAINING_OPEN)

    def test_qg_item_present(self):
        assert any(item.startswith("NON_PERTURBATIVE_QG_OPEN") for item in REMAINING_OPEN)


class TestPillar860ArchitectureLimits:
    def test_higgs_limit_present(self):
        assert any(item.startswith("HIGGS_5D_ARCHITECTURE_LIMIT") for item in ARCHITECTURE_LIMITS_CERTIFIED)

    def test_ngen_limit_present(self):
        assert any(item.startswith("NGEN_5D_EFT_NOGO_PROVED") for item in ARCHITECTURE_LIMITS_CERTIFIED)

    def test_alpha_s_limit_present(self):
        assert any(item.startswith("ALPHA_S_5D_ARCHITECTURE_LIMIT") for item in ARCHITECTURE_LIMITS_CERTIFIED)

    def test_cc_limit_present(self):
        assert any(item.startswith("CC_KK_HIERARCHY_ARCHITECTURE_LIMIT") for item in ARCHITECTURE_LIMITS_CERTIFIED)

    def test_dm21_limit_present(self):
        assert any(item.startswith("DM21_NNLO_ARCHITECTURE_LIMIT") for item in ARCHITECTURE_LIMITS_CERTIFIED)


class TestPillar860Validation:
    def test_coverage_check_returns_dict(self): assert isinstance(cross_dimensional_coverage_check(), dict)
    def test_coverage_has_seven_steps(self): assert cross_dimensional_coverage_check()["n_chain_steps"] == 7
    def test_coverage_passes(self): assert cross_dimensional_coverage_check()["coverage_pass"] is True
    def test_validation_returns_dict(self): assert isinstance(validate_sprint(), dict)
    def test_validation_passed(self): assert validate_sprint()["passed"] is True
    def test_validation_no_errors(self): assert validate_sprint()["errors"] == []
    def test_validation_pillar_count(self): assert validate_sprint()["n_pillars"] == 18
    def test_validation_remaining_open_count(self): assert validate_sprint()["n_remaining_open"] == 10
    def test_validation_architecture_limit_count(self): assert validate_sprint()["n_architecture_limits_certified"] == 5


class TestPillar860Summary:
    def test_returns_dict(self): assert isinstance(sprint_ba_summary(), dict)
    def test_summary_complete(self): assert sprint_ba_summary()["sprint_complete"] is True
    def test_summary_gate(self): assert sprint_ba_summary()["gate"] == PILLAR_GATE
    def test_summary_lean4_total(self): assert sprint_ba_summary()["lean4_total"] == 2186
    def test_summary_lean4_delta(self): assert sprint_ba_summary()["lean4_delta"] == 365
    def test_summary_pillar_count(self): assert sprint_ba_summary()["n_pillars"] == 18
