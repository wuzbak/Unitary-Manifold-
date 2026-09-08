# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.lean4_index import (
    LEAN4_THEOREM_COUNT,
    LEAN4_THEOREM_SAMPLE,
    get_theorem_count,
    get_theorems_by_pillar,
    search_theorems,
)
from ox_navigator.engine.pillar_graph import (
    PILLAR_DEPENDENCY_GRAPH,
    find_critical_path,
    get_dependencies,
    get_dependents,
)


def test_theorem_count_constant():
    assert LEAN4_THEOREM_COUNT == 2186


def test_get_theorem_count_matches_constant():
    assert get_theorem_count() == LEAN4_THEOREM_COUNT


def test_theorem_sample_has_20_real_entries():
    assert len(LEAN4_THEOREM_SAMPLE) == 20
    assert 'APS_T2Z2_NgenBridge' in LEAN4_THEOREM_SAMPLE
    assert 'MasterTheoremDimensionalChain' in LEAN4_THEOREM_SAMPLE


def test_theorem_sample_entries_are_unique():
    assert len(LEAN4_THEOREM_SAMPLE) == len(set(LEAN4_THEOREM_SAMPLE))


def test_search_theorems_is_case_insensitive():
    assert search_theorems('aps_t2z2') == ['APS_T2Z2_NgenBridge']


def test_search_theorems_supports_blank_query():
    assert search_theorems('') == LEAN4_THEOREM_SAMPLE


def test_search_theorems_uses_custom_theorem_list():
    sample = ['Alpha', 'Beta', 'Gamma']
    assert search_theorems('a', sample) == ['Alpha', 'Beta', 'Gamma']


def test_search_theorems_returns_empty_when_no_match():
    assert search_theorems('nonexistent theorem') == []


def test_search_theorems_finds_braid_entries():
    matches = search_theorems('braid')
    assert 'BraidUniqueness' in matches
    assert 'BraidUniquenessAlgebraic' in matches


def test_get_theorems_by_pillar_returns_dirac_mapping():
    matches = get_theorems_by_pillar(837)
    assert 'DiracOrbifoldSpectrum' in matches


def test_get_theorems_by_pillar_returns_empty_for_unknown_pillar():
    assert get_theorems_by_pillar(9999) == []


def test_get_theorems_by_pillar_returns_copy():
    items = get_theorems_by_pillar(839)
    items.append('Mutated')
    assert 'Mutated' not in get_theorems_by_pillar(839)


def test_pillar_graph_covers_sprint_ba_range():
    assert all(pillar in PILLAR_DEPENDENCY_GRAPH for pillar in range(837, 861))


def test_get_dependencies_for_phase_certificate():
    assert get_dependencies(842) == [838, 839, 840, 841]


def test_get_dependencies_unknown_pillar_is_empty():
    assert get_dependencies(9999) == []


def test_get_dependents_for_837_include_phase_one_work():
    dependents = get_dependents(837)
    assert 839 in dependents
    assert 840 in dependents


def test_get_dependents_for_858_returns_859_only():
    assert get_dependents(858) == [859]


def test_find_critical_path_same_start_end():
    assert find_critical_path(842, 842) == [842]


def test_find_critical_path_through_phase_one_to_master():
    path = find_critical_path(837, 860)
    assert path == [837, 839, 842, 858, 859, 860]


def test_find_critical_path_across_mid_chain():
    assert find_critical_path(843, 852) == [843, 846, 849, 852]


def test_find_critical_path_returns_empty_when_unreachable():
    assert find_critical_path(845, 860) == []


def test_find_critical_path_returns_empty_for_unknown_nodes():
    assert find_critical_path(1, 860) == []


def test_reverse_lookup_for_terminal_node_is_empty():
    assert get_dependents(860) == []
