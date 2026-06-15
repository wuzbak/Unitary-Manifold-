# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 516 — KK backreaction architecture audit."""

from src.core.pillar516_kk_backreaction_architecture_audit import (
    PILLAR_ID,
    PILLAR_STATUS,
    kk_backreaction_architecture_report,
    regime_map,
)


class TestPillar516ArchitectureAudit:
    def test_pillar_id_is_516(self):
        assert PILLAR_ID == 516
        assert kk_backreaction_architecture_report()["pillar_id"] == 516

    def test_status_string_matches(self):
        assert PILLAR_STATUS == "KK_BACKREACTION_ARCHITECTURE_AUDIT_COMPLETE"
        assert kk_backreaction_architecture_report()["status"] == PILLAR_STATUS

    def test_architecture_limit_certified_true(self):
        assert kk_backreaction_architecture_report()["architecture_limit_certified"] is True

    def test_open_work_non_empty(self):
        open_work = kk_backreaction_architecture_report()["open_work"]
        assert isinstance(open_work, str)
        assert open_work.strip()

    def test_blocking_for_references_winding_or_geometry(self):
        blocking_for = kk_backreaction_architecture_report()["blocking_for"].lower()
        assert "winding" in blocking_for or "geometry" in blocking_for

    def test_falsifier_impact_mentions_lower_bound(self):
        impact = kk_backreaction_architecture_report()["falsifier_impact"].lower()
        assert "lower bound" in impact

    def test_estimated_closure_mentions_external_or_lattice(self):
        estimated = kk_backreaction_architecture_report()["estimated_closure"].lower()
        assert "external" in estimated or "lattice" in estimated

    def test_mathematical_gap_non_empty(self):
        gap = kk_backreaction_architecture_report()["mathematical_gap"]
        assert isinstance(gap, str)
        assert gap.strip()

    def test_regime_map_returns_all_four_keys(self):
        mapping = regime_map()
        assert set(mapping) == {
            "factory_ic",
            "solver_large_deviation",
            "backreaction_decoupled",
            "winding_tracking_live",
        }

    def test_regime_map_values_are_non_empty_strings(self):
        mapping = regime_map()
        for value in mapping.values():
            assert isinstance(value, str)
            assert value.strip()
