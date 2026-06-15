# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for Pillar 391 — Signal-vs-Noise Filter.

Validates triage classification, the canonical item registry,
batch triage, and the pillar status function.
"""

import pytest

from src.core.signal_noise_filter import (
    TriageClass,
    TriageResult,
    ItemType,
    RepositoryItem,
    TriageReport,
    ACTIVE_DECISION_WINDOWS,
    ACTIVE_HIGH_TENSION_SIGNALS,
    classify_item,
    triage_items,
    get_canonical_item_registry,
    pillar_391_status,
)


# ──────────────────────────────────────────────────────────────────────────────
# Active registries
# ──────────────────────────────────────────────────────────────────────────────

class TestActiveRegistries:

    def test_desi_dr3_in_decision_windows(self):
        assert "DESI_DR3" in ACTIVE_DECISION_WINDOWS

    def test_litebird_in_decision_windows(self):
        assert "LITEBIRD" in ACTIVE_DECISION_WINDOWS

    def test_juno_in_decision_windows(self):
        assert "JUNO" in ACTIVE_DECISION_WINDOWS

    def test_so_dr1_in_decision_windows(self):
        assert "SO_DR1" in ACTIVE_DECISION_WINDOWS

    def test_desi_wa_in_tensions(self):
        assert "DESI_WA" in ACTIVE_HIGH_TENSION_SIGNALS

    def test_act_dr6_r_in_tensions(self):
        assert "ACT_DR6_R" in ACTIVE_HIGH_TENSION_SIGNALS


# ──────────────────────────────────────────────────────────────────────────────
# Individual item classification
# ──────────────────────────────────────────────────────────────────────────────

class TestClassifyItem:

    def _item(self, **kwargs) -> RepositoryItem:
        defaults = dict(
            name="test_item",
            item_type=ItemType.PREDICTION,
            linked_falsifier=None,
            linked_tension=None,
            decision_window_years=None,
            is_consistent_with_data=True,
            has_preregistered_routing=False,
            is_speculative_extension=False,
            has_no_near_term_test=False,
            is_superseded=False,
        )
        defaults.update(kwargs)
        return RepositoryItem(**defaults)

    def test_superseded_item_is_archival_noise(self):
        item = self._item(is_superseded=True)
        result = classify_item(item)
        assert result.classification == TriageClass.ARCHIVAL_NOISE

    def test_speculative_no_falsifier_no_window_is_noise(self):
        item = self._item(
            is_speculative_extension=True,
            has_no_near_term_test=True,
        )
        result = classify_item(item)
        assert result.classification == TriageClass.ARCHIVAL_NOISE

    def test_speculative_with_tension_is_signal(self):
        item = self._item(
            is_speculative_extension=True,
            linked_tension="DESI_WA",
        )
        result = classify_item(item)
        assert result.classification == TriageClass.ACTIONABLE_SIGNAL

    def test_high_tension_link_is_signal(self):
        item = self._item(linked_tension="DESI_WA")
        result = classify_item(item)
        assert result.classification == TriageClass.ACTIONABLE_SIGNAL

    def test_active_decision_window_is_signal(self):
        item = self._item(linked_falsifier="LITEBIRD", decision_window_years=2032)
        result = classify_item(item)
        assert result.classification == TriageClass.ACTIONABLE_SIGNAL

    def test_near_term_decision_window_is_signal(self):
        item = self._item(
            linked_falsifier="DESI_DR3",
            decision_window_years=2027,
            has_preregistered_routing=True,
        )
        result = classify_item(item)
        assert result.classification == TriageClass.ACTIONABLE_SIGNAL

    def test_falsifier_without_routing_is_signal(self):
        item = self._item(
            linked_falsifier="DESI_DR3",
            has_preregistered_routing=False,
        )
        result = classify_item(item)
        assert result.classification == TriageClass.ACTIONABLE_SIGNAL

    def test_consistent_no_links_is_monitor_only(self):
        item = self._item(is_consistent_with_data=True)
        result = classify_item(item)
        assert result.classification == TriageClass.MONITOR_ONLY

    def test_ambiguous_item_escalates_to_signal(self):
        # Not consistent, not speculative, no falsifier → conservative escalation
        item = self._item(is_consistent_with_data=False)
        result = classify_item(item)
        assert result.classification == TriageClass.ACTIONABLE_SIGNAL

    def test_result_has_reasons(self):
        item = self._item(linked_tension="ACT_DR6_R")
        result = classify_item(item)
        assert len(result.reasons) > 0

    def test_result_has_recommended_action(self):
        item = self._item(is_superseded=True)
        result = classify_item(item)
        assert len(result.recommended_action) > 0


# ──────────────────────────────────────────────────────────────────────────────
# Canonical registry
# ──────────────────────────────────────────────────────────────────────────────

class TestCanonicalRegistry:

    def test_registry_not_empty(self):
        registry = get_canonical_item_registry()
        assert len(registry) > 0

    def test_registry_contains_desi_tension(self):
        registry = get_canonical_item_registry()
        names = [i.name for i in registry]
        assert "DESI_WA_TENSION" in names

    def test_registry_contains_litebird(self):
        registry = get_canonical_item_registry()
        names = [i.name for i in registry]
        assert "LITEBIRD_BIREFRINGENCE" in names

    def test_registry_contains_juno(self):
        registry = get_canonical_item_registry()
        names = [i.name for i in registry]
        assert "JUNO_DM31_PREDICTION" in names

    def test_registry_has_tensions(self):
        registry = get_canonical_item_registry()
        tensions = [i for i in registry if i.item_type == ItemType.TENSION]
        assert len(tensions) >= 2

    def test_registry_has_governance_item(self):
        registry = get_canonical_item_registry()
        governance = [i for i in registry if i.item_type == ItemType.GOVERNANCE]
        assert len(governance) >= 1

    def test_all_items_have_names(self):
        registry = get_canonical_item_registry()
        for item in registry:
            assert item.name != ""


# ──────────────────────────────────────────────────────────────────────────────
# Batch triage
# ──────────────────────────────────────────────────────────────────────────────

class TestBatchTriage:

    def test_all_canonical_items_classified(self):
        registry = get_canonical_item_registry()
        report   = triage_items(registry)
        assert len(report.results) == len(registry)

    def test_report_has_actionable_items(self):
        registry = get_canonical_item_registry()
        report   = triage_items(registry)
        assert len(report.actionable) > 0

    def test_report_summary_structure(self):
        registry = get_canonical_item_registry()
        report   = triage_items(registry)
        s = report.summary()
        assert "total_items" in s
        assert "actionable_signal" in s
        assert "monitor_only" in s
        assert "archival_noise" in s
        assert "signal_fraction" in s

    def test_noise_fraction_below_threshold(self):
        registry = get_canonical_item_registry()
        report   = triage_items(registry)
        s = report.summary()
        noise_fraction = s["archival_noise"] / s["total_items"] if s["total_items"] else 0
        assert noise_fraction <= 0.30, (
            f"Archival-noise fraction {noise_fraction:.1%} exceeds 30% — "
            f"canonical registry needs cleanup"
        )

    def test_desi_tension_is_actionable(self):
        registry = get_canonical_item_registry()
        report   = triage_items(registry)
        desi_results = [
            r for r in report.results if r.item.name == "DESI_WA_TENSION"
        ]
        assert len(desi_results) == 1
        assert desi_results[0].classification == TriageClass.ACTIONABLE_SIGNAL

    def test_act_dr6_tension_is_actionable(self):
        registry = get_canonical_item_registry()
        report   = triage_items(registry)
        act_results = [
            r for r in report.results if r.item.name == "ACT_DR6_R_TENSION"
        ]
        assert len(act_results) == 1
        assert act_results[0].classification == TriageClass.ACTIONABLE_SIGNAL

    def test_litebird_is_actionable(self):
        registry = get_canonical_item_registry()
        report   = triage_items(registry)
        lb = [r for r in report.results if r.item.name == "LITEBIRD_BIREFRINGENCE"]
        assert len(lb) == 1
        assert lb[0].classification == TriageClass.ACTIONABLE_SIGNAL

    def test_noise_reduction_recommendations_are_strings(self):
        registry = get_canonical_item_registry()
        report   = triage_items(registry)
        recs = report.noise_reduction_recommendations()
        for rec in recs:
            assert isinstance(rec, str)

    def test_empty_registry_gives_zero_summary(self):
        report = triage_items([])
        s = report.summary()
        assert s["total_items"] == 0
        assert s["signal_fraction"] == 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Pillar status
# ──────────────────────────────────────────────────────────────────────────────

class TestPillar391Status:

    def test_status_structure(self):
        status = pillar_391_status()
        assert status["pillar"] == 391
        assert status["label"] == "ADJACENT_TRACK"
        assert status["hils_status"] == "ACTIVE"

    def test_triage_summary_in_status(self):
        status = pillar_391_status()
        assert "triage_summary" in status
        assert "total_items" in status["triage_summary"]

    def test_active_windows_in_status(self):
        status = pillar_391_status()
        assert "DESI_DR3" in status["active_decision_windows"]
        assert "LITEBIRD" in status["active_decision_windows"]

    def test_triage_classes_complete(self):
        status = pillar_391_status()
        classes = status["triage_classes"]
        assert "ACTIONABLE_SIGNAL" in classes
        assert "MONITOR_ONLY" in classes
        assert "ARCHIVAL_NOISE" in classes
