# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 474 — arXiv v14 update metadata package."""
from __future__ import annotations

from src.core.pillar474_arxiv_v14_update import (
    PILLAR_STATUS,
    VERSION,
    V14_CHANGELOG,
    abstract_v14,
    admission_updates_v14,
    arxiv_metadata,
    free_parameter_updates_v14,
    key_equations_v14,
    new_theorems_v14,
    pillar_report,
    submission_checklist,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'ARXIV_V14_UPDATE_READY'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_changelog_versions(self):
        assert V14_CHANGELOG['from_version'] == 'v13.8'
        assert V14_CHANGELOG['to_version'] == 'v14.0'

    def test_changelog_range(self):
        assert V14_CHANGELOG['pillar_range'] == (455, 474)


class TestNewTheorems:
    def test_returns_list(self):
        assert isinstance(new_theorems_v14(), list)

    def test_has_multiple_entries(self):
        assert len(new_theorems_v14()) >= 7

    def test_mentions_p455(self):
        assert any('P455' in item for item in new_theorems_v14())

    def test_mentions_p470(self):
        assert any('P470' in item for item in new_theorems_v14())

    def test_mentions_p472(self):
        assert any('P472' in item for item in new_theorems_v14())


class TestAdmissionUpdates:
    def setup_method(self):
        self.result = admission_updates_v14()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_mentions_p455_residual(self):
        assert 'P455' in self.result['P8 residual']

    def test_mentions_conjectural_status(self):
        assert 'CONJECTURAL' in self.result['Quantum theorem overclaiming']

    def test_mentions_named_irreducible(self):
        assert 'L2_FINAL_2PCT_NAMED_IRREDUCIBLE' in self.result['Gamma budget']


class TestFreeParameterUpdates:
    def setup_method(self):
        self.result = free_parameter_updates_v14()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_mentions_lambda(self):
        assert 'lambda' in self.result['metric_ansatz_lambda']

    def test_mentions_p464(self):
        assert 'P464' in self.result['free_parameter_census']

    def test_mentions_pmns_residual(self):
        assert 'PMNS_PR_NAMED_RESIDUAL' in self.result['pmns_pR']


class TestAbstract:
    def test_returns_string(self):
        assert isinstance(abstract_v14(), str)

    def test_mentions_p455(self):
        assert 'P455' in abstract_v14()

    def test_mentions_p465(self):
        assert 'P465' in abstract_v14()

    def test_mentions_p470(self):
        assert 'P470' in abstract_v14()

    def test_mentions_p472(self):
        assert 'P472' in abstract_v14()


class TestKeyEquations:
    def test_returns_list(self):
        assert isinstance(key_equations_v14(), list)

    def test_has_six_entries(self):
        assert len(key_equations_v14()) == 6

    def test_contains_tau_equation(self):
        assert any('tau_p >=' in item for item in key_equations_v14())

    def test_contains_unitarity_equation(self):
        assert any('|a_J| <= 1' in item for item in key_equations_v14())


class TestMetadata:
    def setup_method(self):
        self.result = arxiv_metadata()

    def test_title_mentions_v14(self):
        assert 'v14.0' in self.result['title']

    def test_version(self):
        assert self.result['version'] == 'v14.0'

    def test_has_three_categories(self):
        assert len(self.result['categories']) == 3

    def test_keywords_include_proton_decay(self):
        assert 'proton decay' in self.result['keywords']


class TestChecklist:
    def test_returns_list(self):
        assert isinstance(submission_checklist(), list)

    def test_has_multiple_items(self):
        assert len(submission_checklist()) >= 7

    def test_mentions_theorem_registry(self):
        assert any('theorem registry' in item for item in submission_checklist())

    def test_mentions_full_pytest(self):
        assert any('full repository pytest gate' in item for item in submission_checklist())


class TestReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 474

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_contains_changelog(self):
        assert 'changelog' in self.report

    def test_contains_abstract(self):
        assert self.report['abstract'] == abstract_v14()

    def test_contains_metadata(self):
        assert self.report['metadata']['version'] == 'v14.0'
