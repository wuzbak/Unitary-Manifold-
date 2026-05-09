# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/five_tier_execution_framework.py."""
from __future__ import annotations

import pytest

from src.core.five_tier_execution_framework import (
    EVIDENCE_PIPELINE,
    FRAMEWORK_DATE,
    FRAMEWORK_VERSION,
    FULL_REGRESSION_GATE_COMMAND,
    NEXT_THREE_PRS,
    OPERATING_MODEL,
    THROUGHPUT_PLAN,
    TIER_PACKAGES,
    TIER_PRIORITY_ORDER,
    evidence_pipeline_spec,
    framework_summary,
    get_operating_model,
    get_tier_package,
    list_tier_packages,
    next_three_pr_sequence,
    throughput_sequence,
)


class TestFrameworkMetadata:
    def test_framework_version(self):
        assert FRAMEWORK_VERSION == "v10.31"

    def test_framework_date(self):
        assert FRAMEWORK_DATE == "2026-05-09"

    def test_tier_priority_order(self):
        assert TIER_PRIORITY_ORDER == ["Tier-1", "Tier-2", "Tier-3", "Tier-4", "Tier-5"]
        assert list_tier_packages() == TIER_PRIORITY_ORDER


class TestOperatingModel:
    def test_operating_model_keeps_mas_closed(self):
        assert OPERATING_MODEL["mas_reopen_allowed"] is False
        assert OPERATING_MODEL["recycle_into_mas_allowed"] is False

    def test_hardgate_only_promotion_policy(self):
        assert OPERATING_MODEL["promotion_policy"] == "hardgate_only"
        assert "all_required_gates_must_pass" in OPERATING_MODEL["status_change_rule"]

    def test_get_operating_model_returns_copy(self):
        m1 = get_operating_model()
        m2 = get_operating_model()
        m1["promotion_policy"] = "MUTATED"
        assert m2["promotion_policy"] == "hardgate_only"


class TestTierPackages:
    def test_has_five_tier_packages(self):
        assert set(TIER_PACKAGES.keys()) == set(TIER_PRIORITY_ORDER)

    def test_tier1_targets_p3_p5(self):
        t1 = get_tier_package("Tier-1")
        assert t1["parameters"] == ["P3", "P5"]
        assert "robustness_sweep_pass" in t1["required_gates"]
        assert "axiomzero_purity_pass" in t1["required_gates"]

    def test_tier2_and_tier3_parallel_group(self):
        t2 = get_tier_package("Tier-2")
        t3 = get_tier_package("Tier-3")
        assert t2["parallel_group"] == "Tier-2-and-Tier-3"
        assert t3["parallel_group"] == "Tier-2-and-Tier-3"

    def test_tier4_has_four_subpackages(self):
        t4 = get_tier_package("Tier-4")
        assert set(t4["subpackages"].keys()) == {
            "P7_subpackage",
            "P8_subpackage",
            "P9_subpackage",
            "P10_subpackage",
        }
        assert "cross_generation_consistency_pass" in t4["required_gates"]

    def test_tier5_preserves_no_score_inflation(self):
        t5 = get_tier_package("Tier-5")
        assert t5["parameters"] == ["P27", "P28"]
        assert t5["score_policy"] == "no_score_inflation_without_hardgate"
        assert "falsifier_integrity_preserved" in t5["required_gates"]

    def test_unknown_tier_raises(self):
        with pytest.raises(KeyError, match="Tier-9"):
            get_tier_package("Tier-9")

    def test_get_tier_package_returns_copy(self):
        t1 = get_tier_package("Tier-1")
        t2 = get_tier_package("Tier-1")
        t1["title"] = "MUTATED"
        assert t2["title"] != "MUTATED"


class TestEvidencePipeline:
    def test_pipeline_patterns_and_ledger(self):
        p = evidence_pipeline_spec()
        assert p["certifier_module_pattern"] == "src/core/*_hardgate_cert.py"
        assert p["test_pattern"] == "tests/test_core_*_hardgate_cert.py"
        assert p["canonical_status_ledger"] == "docs/mas_tracker.yml"
        assert p["no_inflation_guard_module"] == "src/core/no_inflation_evidence_guard.py"

    def test_pipeline_requires_full_regression(self):
        p = evidence_pipeline_spec()
        assert p["regression_command"] == FULL_REGRESSION_GATE_COMMAND
        assert "pytest tests/ recycling/" in p["regression_command"]
        assert "test_symbolic_metric.py" in p["regression_command"]

    def test_evidence_pipeline_returns_copy(self):
        p1 = evidence_pipeline_spec()
        p2 = evidence_pipeline_spec()
        p1["tracker_format"] = "MUTATED"
        assert p2["tracker_format"] == EVIDENCE_PIPELINE["tracker_format"]


class TestThroughputAndPRSequence:
    def test_throughput_has_integration_rule(self):
        seq = throughput_sequence()
        integration = [x for x in seq if x["type"] == "integration_pr"]
        assert len(integration) == 2
        assert integration[0]["batch_rule"] == "integration_checkpoint_after_pr_1_and_pr_2"
        assert integration[1]["batch_rule"] == "full_regression_and_tracker_sync_required"

    def test_throughput_sequence_returns_copy(self):
        s1 = throughput_sequence()
        s2 = throughput_sequence()
        s1[0]["type"] = "MUTATED"
        assert s2[0]["type"] == THROUGHPUT_PLAN[0]["type"]

    def test_next_three_prs_cover_continuation_sprint(self):
        prs = next_three_pr_sequence()
        assert [p["pr_id"] for p in prs] == ["PR-CONT-1", "PR-CONT-2", "PR-CONT-3"]
        assert [p["scope"] for p in prs] == [
            "11D continuation — vacuum selection + bridge burn",
            "Neutrino branch policy",
            "ToE promotion frontier",
        ]

    def test_pr1_scope_definition_has_required_deliverables(self):
        pr1 = next_three_pr_sequence()[0]
        deliverables = " ".join(pr1["deliverables"]).lower()
        assert "vacuum" in pr1["title"].lower()
        assert "vacuum-selection" in deliverables
        assert "boundary contract" in deliverables
        assert "g4-flux" in deliverables

    def test_next_three_pr_sequence_returns_copy(self):
        p1 = next_three_pr_sequence()
        p2 = next_three_pr_sequence()
        p1[0]["scope"] = "MUTATED"
        assert p2[0]["scope"] == NEXT_THREE_PRS[0]["scope"]


class TestFrameworkSummary:
    def test_summary_shape(self):
        s = framework_summary()
        required = {
            "framework_version",
            "framework_date",
            "tier_count",
            "tier_priority_order",
            "operating_model",
            "evidence_pipeline",
            "throughput_step_count",
            "next_three_pr_ids",
            "integration_rule",
            "no_overclaim_policy",
        }
        assert required <= set(s.keys())

    def test_summary_values(self):
        s = framework_summary()
        assert s["tier_count"] == 5
        assert s["tier_priority_order"] == TIER_PRIORITY_ORDER
        assert s["next_three_pr_ids"] == ["PR-CONT-1", "PR-CONT-2", "PR-CONT-3"]
        assert s["no_overclaim_policy"] is True
