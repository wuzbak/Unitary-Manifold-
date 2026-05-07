# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Architecture Limits Registry (Pillar 218, Track A Session 1)."""

import pytest
from src.core.architecture_limits_registry import (
    ARCHITECTURE_LIMIT_REGISTRY,
    get_limit,
    list_limits,
    limits_by_dimension,
    count_by_status,
    limits_summary,
    architecture_limits_report,
)


class TestRegistryStructure:
    def test_registry_is_dict(self):
        assert isinstance(ARCHITECTURE_LIMIT_REGISTRY, dict)

    def test_registry_nonempty(self):
        assert len(ARCHITECTURE_LIMIT_REGISTRY) >= 10

    def test_all_entries_have_honest_status(self):
        for k, v in ARCHITECTURE_LIMIT_REGISTRY.items():
            assert "honest_status" in v, f"Missing honest_status for {k}"

    def test_all_entries_have_gap_description(self):
        for k, v in ARCHITECTURE_LIMIT_REGISTRY.items():
            assert "gap_description" in v, f"Missing gap_description for {k}"

    def test_all_entries_have_requires_dimension(self):
        for k, v in ARCHITECTURE_LIMIT_REGISTRY.items():
            assert "requires_dimension" in v, f"Missing requires_dimension for {k}"

    def test_all_entries_have_falsification(self):
        for k, v in ARCHITECTURE_LIMIT_REGISTRY.items():
            assert "falsification" in v, f"Missing falsification for {k}"


class TestSpecificEntries:
    def test_cc_entry_exists(self):
        assert "A-1_cosmological_constant" in ARCHITECTURE_LIMIT_REGISTRY

    def test_cc_residual_gap_58(self):
        entry = ARCHITECTURE_LIMIT_REGISTRY["A-1_cosmological_constant"]
        assert 50 <= entry["residual_gap_log10"] <= 65

    def test_cc_requires_10d(self):
        entry = ARCHITECTURE_LIMIT_REGISTRY["A-1_cosmological_constant"]
        assert entry["requires_dimension"] == 10

    def test_alpha_s_entry_exists(self):
        assert "A-2_strong_coupling_warp_anchor" in ARCHITECTURE_LIMIT_REGISTRY

    def test_fermion_masses_requires_6d(self):
        entry = ARCHITECTURE_LIMIT_REGISTRY["A-3_fermion_mass_hierarchy_light_generations"]
        assert entry["requires_dimension"] == 6

    def test_cp_violation_requires_6d(self):
        entry = ARCHITECTURE_LIMIT_REGISTRY["A-4_cp_violation_jarlskog"]
        assert entry["requires_dimension"] == 6

    def test_sugra_requires_11d(self):
        entry = ARCHITECTURE_LIMIT_REGISTRY["A-9_supersymmetry_breaking"]
        assert entry["requires_dimension"] == 11

    def test_gw_detection_technology_limit(self):
        entry = ARCHITECTURE_LIMIT_REGISTRY["A-5_gw_strain_detection"]
        # GW is a technology limit, not a dimensional limit
        assert entry["requires_dimension"] is None


class TestFunctions:
    def test_get_limit_returns_dict(self):
        result = get_limit("A-1_cosmological_constant")
        assert isinstance(result, dict)

    def test_get_limit_bad_key_raises(self):
        with pytest.raises(KeyError):
            get_limit("nonexistent_key")

    def test_list_limits_returns_list(self):
        result = list_limits()
        assert isinstance(result, list)
        assert len(result) >= 10

    def test_limits_by_dimension_6d(self):
        sixd_limits = limits_by_dimension(6)
        assert len(sixd_limits) >= 2
        for k in sixd_limits:
            assert ARCHITECTURE_LIMIT_REGISTRY[k]["requires_dimension"] == 6

    def test_limits_by_dimension_10d(self):
        tendim = limits_by_dimension(10)
        assert len(tendim) >= 2

    def test_limits_by_dimension_11d(self):
        elevendim = limits_by_dimension(11)
        assert len(elevendim) >= 1

    def test_count_by_status_returns_int(self):
        n = count_by_status("ARCHITECTURE_LIMIT")
        assert isinstance(n, int)
        assert n > 0

    def test_limits_summary_keys(self):
        s = limits_summary()
        assert "total_limits" in s
        assert "architecture_limit_count" in s
        assert "by_dimension" in s

    def test_limits_summary_total_positive(self):
        s = limits_summary()
        assert s["total_limits"] >= 10

    def test_architecture_limits_report_keys(self):
        report = architecture_limits_report()
        assert "version" in report
        assert "registry" in report
        assert "summary" in report
        assert "five_d_domain_statement" in report
        assert "genuine_5d_achievements" in report

    def test_genuine_achievements_nonempty(self):
        report = architecture_limits_report()
        assert len(report["genuine_5d_achievements"]) >= 5

    def test_all_architecture_limits_are_true(self):
        for k, v in ARCHITECTURE_LIMIT_REGISTRY.items():
            assert v["honest_status"] == "ARCHITECTURE_LIMIT", (
                f"Entry {k} has status {v['honest_status']}, expected ARCHITECTURE_LIMIT"
            )
