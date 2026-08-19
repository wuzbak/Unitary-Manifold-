# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 760: Lean4 800 Milestone."""
import pytest
from src.core.pillar760_lean4_800_milestone_theorems import (
    lean4_800_milestone, ALL_THEOREM_GROUPS,
    KK_SPECTRUM_THEOREMS, FTUM_CONTRACTION_THEOREMS,
    BRAID_ORTHOGONALITY_THEOREMS, INFLATION_BOUND_THEOREMS,
    PILLAR, STATUS, LEAN4_TOTAL, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar(self): assert PILLAR == 760
    def test_status(self): assert STATUS == 'CLOSED'
    def test_lean4_total(self): assert LEAN4_TOTAL == 812
    def test_no_toe_score(self): import src.core.pillar760_lean4_800_milestone_theorems as m; assert not hasattr(m, 'toe_score')


class TestTheoremGroups:
    def test_kk_spectrum_count(self): assert len(KK_SPECTRUM_THEOREMS) == 8
    def test_ftum_count(self): assert len(FTUM_CONTRACTION_THEOREMS) == 8
    def test_braid_count(self): assert len(BRAID_ORTHOGONALITY_THEOREMS) == 8
    def test_inflation_count(self): assert len(INFLATION_BOUND_THEOREMS) == 8
    def test_all_groups_count(self): assert sum(len(v) for v in ALL_THEOREM_GROUPS.values()) == 32
    def test_no_duplicates(self):
        all_t = [t for v in ALL_THEOREM_GROUPS.values() for t in v]
        assert len(all_t) == len(set(all_t))


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return lean4_800_milestone()

    def test_pillar_field(self, result): assert result['pillar'] == 760
    def test_label(self, result): assert '800' in result['label']
    def test_new_theorems(self, result): assert result['lean4']['new_theorems'] == 32
    def test_new_total(self, result): assert result['lean4']['new_total'] == 812
    def test_milestone_passed(self, result): assert result['lean4']['milestone'] == '800_PASSED'
    def test_groups_sum(self, result): assert sum(result['lean4']['groups'].values()) == 32
    def test_no_forbidden(self, result): assert 'toe_score' not in result
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestSymbols:
    def test_all_symbols(self):
        import src.core.pillar760_lean4_800_milestone_theorems as m
        for s in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, s)
