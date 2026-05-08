# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/next_five_tiers_programme.py."""
from __future__ import annotations

import pytest

from src.core.next_five_tiers_programme import (
    PROGRAMME_DATE,
    PROGRAMME_VERSION,
    TIER_CATALOGUE,
    TIER_EXECUTION_ORDER,
    get_tier,
    list_tiers,
    programme_summary,
    projected_toe_uplift_bounds,
    tier_parameter_targets,
)


class TestProgrammeMetadata:
    def test_programme_version(self):
        assert PROGRAMME_VERSION == "v10.22"

    def test_programme_date(self):
        assert PROGRAMME_DATE == "2026-05-08"


class TestTierCatalogue:
    def test_has_five_tiers(self):
        assert len(TIER_CATALOGUE) == 5

    def test_ids_match_execution_order(self):
        assert set(TIER_CATALOGUE.keys()) == set(TIER_EXECUTION_ORDER)

    def test_required_tiers_present(self):
        for tier_id in ("Tier-1", "Tier-2", "Tier-3", "Tier-4", "Tier-5"):
            assert tier_id in TIER_CATALOGUE

    def test_required_fields_present(self):
        required = {
            "title",
            "target_parameters",
            "current_status",
            "target_status",
            "priority",
            "acceptance_gates",
            "mas_reopen_allowed",
        }
        for tier_id, tier in TIER_CATALOGUE.items():
            assert required <= set(tier.keys()), f"Missing fields in {tier_id}"

    def test_all_tiers_keep_mas_closed(self):
        assert all(not tier["mas_reopen_allowed"] for tier in TIER_CATALOGUE.values())

    def test_tier_targets_match_plan(self):
        assert TIER_CATALOGUE["Tier-1"]["target_parameters"] == ["P3", "P5"]
        assert TIER_CATALOGUE["Tier-2"]["target_parameters"] == ["P17", "P18"]
        assert TIER_CATALOGUE["Tier-3"]["target_parameters"] == ["P19", "P20"]
        assert TIER_CATALOGUE["Tier-4"]["target_parameters"] == ["P7", "P8", "P9", "P10"]
        assert TIER_CATALOGUE["Tier-5"]["target_parameters"] == ["P27", "P28"]


class TestGetTier:
    def test_returns_copy(self):
        t1 = get_tier("Tier-1")
        t2 = get_tier("Tier-1")
        t1["title"] = "MUTATED"
        assert t2["title"] != "MUTATED"

    def test_unknown_tier_raises(self):
        with pytest.raises(KeyError, match="Tier-9"):
            get_tier("Tier-9")


class TestListTiers:
    def test_returns_execution_order(self):
        assert list_tiers() == TIER_EXECUTION_ORDER


class TestTargetsAndUplift:
    def test_tier_parameter_targets(self):
        targets = tier_parameter_targets()
        assert targets["Tier-1"] == ["P3", "P5"]
        assert targets["Tier-4"] == ["P7", "P8", "P9", "P10"]

    def test_uplift_bounds(self):
        uplift = projected_toe_uplift_bounds()
        assert uplift["tier_1_to_4_upper_bound"] == pytest.approx(3.4, abs=1e-9)
        assert uplift["tier_5_assumed_uplift"] == pytest.approx(0.0, abs=1e-9)
        assert uplift["all_tiers_upper_bound"] == pytest.approx(3.4, abs=1e-9)


class TestProgrammeSummary:
    def test_required_summary_keys(self):
        s = programme_summary()
        required = {
            "programme_version",
            "programme_date",
            "tier_count",
            "tier_ids",
            "targets_by_tier",
            "unique_target_parameters",
            "unique_target_parameter_count",
            "mas_reopen_allowed",
            "scope_rule",
            "anti_recycle_rule",
            "projected_uplift_bounds",
            "note",
        }
        assert required <= set(s.keys())

    def test_summary_values(self):
        s = programme_summary()
        assert s["tier_count"] == 5
        assert s["tier_ids"] == TIER_EXECUTION_ORDER
        assert s["mas_reopen_allowed"] is False
        assert s["unique_target_parameter_count"] == 12
        assert "hardgates" in s["note"].lower()

