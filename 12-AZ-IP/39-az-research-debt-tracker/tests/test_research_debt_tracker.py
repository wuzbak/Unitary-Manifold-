# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_research_debt_tracker import (
    StatusTaxonomy,
    DEFAULT_TAXONOMY,
    WorkItem,
    ResearchDebtTracker,
    load_um_gaps_into_tracker,
)


def _make_tracker():
    tracker = ResearchDebtTracker()
    tracker.add_item(WorkItem("a", "first item", "DERIVED", "minor"))
    tracker.add_item(WorkItem("b", "second item", "OPEN", "critical"))
    tracker.add_item(WorkItem("c", "third item", "PARTIALLY_CLOSED", "significant"))
    return tracker


def test_add_item_rejects_unknown_status():
    tracker = ResearchDebtTracker()
    with pytest.raises(ValueError):
        tracker.add_item(WorkItem("x", "bad", "NOT_A_REAL_STATUS", "minor"))


def test_open_and_closed_items_split_correctly():
    tracker = _make_tracker()
    assert {i.item_id for i in tracker.open_items()} == {"b", "c"}
    assert {i.item_id for i in tracker.closed_items()} == {"a"}


def test_health_score_fractions():
    tracker = _make_tracker()
    score = tracker.health_score()
    assert score.total_items == 3
    assert score.n_closed == 1
    assert score.n_open == 2
    assert score.closed_fraction == pytest.approx(1 / 3)
    assert score.open_fraction == pytest.approx(2 / 3)


def test_validate_closure_passes_for_valid_closed_item():
    tracker = _make_tracker()
    result = tracker.validate_closure("a", tests_passed=10, tests_failed=0, has_documentation_entry=True)
    assert result.overall_valid is True
    assert result.issues == []


def test_validate_closure_fails_for_open_item():
    tracker = _make_tracker()
    result = tracker.validate_closure("b", tests_passed=10, tests_failed=0, has_documentation_entry=True)
    assert result.overall_valid is False
    assert any("does not resolve to 'closed'" in issue for issue in result.issues)


def test_validate_closure_fails_for_unknown_item():
    tracker = _make_tracker()
    result = tracker.validate_closure("nonexistent", tests_passed=5, tests_failed=0, has_documentation_entry=True)
    assert result.overall_valid is False


def test_validate_closure_fails_for_failing_tests():
    tracker = _make_tracker()
    result = tracker.validate_closure("a", tests_passed=5, tests_failed=2, has_documentation_entry=True)
    assert result.overall_valid is False
    assert any("failing tests" in issue for issue in result.issues)


def test_custom_taxonomy_can_be_supplied():
    taxonomy = StatusTaxonomy(closed_statuses=frozenset({"DONE"}), open_statuses=frozenset({"TODO"}))
    tracker = ResearchDebtTracker(taxonomy=taxonomy)
    tracker.add_item(WorkItem("x", "custom", "DONE", "minor"))
    assert tracker.health_score().n_closed == 1


def test_load_um_gaps_into_tracker_is_real_not_synthetic():
    tracker = load_um_gaps_into_tracker()
    all_items = tracker.all_items()
    assert len(all_items) == 6
    item_ids = {i.item_id for i in all_items}
    assert "litebird_birefringence" in item_ids
    assert "desi_wa_tension" in item_ids


def test_um_gaps_all_classify_as_open():
    tracker = load_um_gaps_into_tracker()
    score = tracker.health_score()
    assert score.n_open == score.total_items
    assert score.n_closed == 0
