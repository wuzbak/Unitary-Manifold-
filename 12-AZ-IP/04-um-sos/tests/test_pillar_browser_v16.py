# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from um_sos.engine.lean4_browser import LEAN4_COUNT, get_theorem_by_pillar, search_lean4_theorems
from um_sos.engine.pillar_browser_v16 import (
    SPRINT_BA_PILLARS,
    get_closed_pillars,
    get_gap_closure_dashboard,
    get_open_pillars,
    get_pillar,
)


def test_sprint_ba_pillars_cover_full_range():
    ids = [pillar['id'] for pillar in SPRINT_BA_PILLARS]
    assert ids == list(range(837, 861))


def test_each_pillar_has_required_fields():
    for pillar in SPRINT_BA_PILLARS:
        assert set(pillar) == {'id', 'name', 'status', 'gap_type', 'lean4_ref', 'description'}


def test_get_pillar_returns_copy():
    pillar = get_pillar(859)
    pillar['name'] = 'mutated'
    assert get_pillar(859)['name'] != 'mutated'


def test_get_pillar_859():
    pillar = get_pillar(859)
    assert pillar['status'] == 'CLOSED'
    assert 'MasterTheoremDimensionalChain.lean' in pillar['lean4_ref']


def test_get_pillar_unknown_rejected():
    with pytest.raises(KeyError):
        get_pillar(999)


def test_open_pillars_all_open():
    assert all(pillar['status'] == 'OPEN' for pillar in get_open_pillars())


def test_closed_pillars_all_closed():
    assert all(pillar['status'] == 'CLOSED' for pillar in get_closed_pillars())


def test_open_pillar_ids():
    assert [pillar['id'] for pillar in get_open_pillars()] == [845, 847, 848, 851, 857]


def test_dashboard_counts_sum_to_total():
    dashboard = get_gap_closure_dashboard()
    assert dashboard['closed_count'] + dashboard['partial_count'] + dashboard['open_count'] == dashboard['total'] == 24


def test_dashboard_closed_fraction_bounded():
    dashboard = get_gap_closure_dashboard()
    assert 0.0 < dashboard['closed_fraction'] < 1.0


def test_dashboard_partial_ids_sorted():
    dashboard = get_gap_closure_dashboard()
    assert dashboard['partial_ids'] == sorted(dashboard['partial_ids'])


def test_lean4_count_constant():
    assert LEAN4_COUNT == 2186


def test_search_lean4_theorems_by_known_symbol():
    results = search_lean4_theorems('masterchain_lean4_total')
    assert any(path.endswith('MasterTheoremDimensionalChain.lean') for path in results)


def test_search_lean4_theorems_empty_query():
    assert search_lean4_theorems('   ') == []


def test_get_theorem_by_pillar_859():
    results = get_theorem_by_pillar(859)
    assert any(path.endswith('MasterTheoremDimensionalChain.lean') for path in results)


def test_get_theorem_by_pillar_unknown_is_empty():
    assert get_theorem_by_pillar(99999) == []
