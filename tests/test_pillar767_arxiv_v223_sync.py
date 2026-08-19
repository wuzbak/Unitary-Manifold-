# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 767: arXiv v22.3 Sync."""
import pytest
from src.core.pillar767_arxiv_v223_sync import (
    arxiv_v223_sync, SPRINT_AG_SECTIONS, CROSS_REFS,
    PILLAR, STATUS, VERSION, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar(self): assert PILLAR == 767
    def test_status(self): assert STATUS == 'CLOSED'
    def test_version(self): assert VERSION == 'v22.3'
    def test_eight_sections(self): assert len(SPRINT_AG_SECTIONS) == 8
    def test_lean4_total(self): assert CROSS_REFS['lean4_total'] == 820
    def test_no_toe_score(self): import src.core.pillar767_arxiv_v223_sync as m; assert not hasattr(m, 'toe_score')


class TestSections:
    def test_p759_section_present(self):
        pillars = [v['pillar'] for v in SPRINT_AG_SECTIONS.values()]
        assert 759 in pillars

    def test_all_sections_have_pillar(self):
        for v in SPRINT_AG_SECTIONS.values():
            assert 'pillar' in v and isinstance(v['pillar'], int)

    def test_all_sections_have_content(self):
        for v in SPRINT_AG_SECTIONS.values():
            assert len(v.get('content', '')) > 5


class TestCrossRefs:
    def test_pillar_range(self): assert '768' in CROSS_REFS['pillar_range']
    def test_doi_present(self): assert 'doi' in CROSS_REFS
    def test_test_count_est(self): assert CROSS_REFS['test_count_est'].startswith('~')


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return arxiv_v223_sync()

    def test_pillar_field(self, result): assert result['pillar'] == 767
    def test_version_field(self, result): assert result['version'] == 'v22.3'
    def test_total_sections(self, result): assert result['total_new_sections'] == 8
    def test_honest_note(self, result): assert 'EXTERNAL_UNVERIFIED' in result['honest_note']
    def test_no_forbidden(self, result): assert 'toe_score' not in result
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestSymbols:
    def test_all_symbols(self):
        import src.core.pillar767_arxiv_v223_sync as m
        for s in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, s)
