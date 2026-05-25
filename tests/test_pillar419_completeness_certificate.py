# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 419 — Completeness Certificate v13.4."""
import math
import pytest

from src.core.pillar419_completeness_certificate import (
    PILLAR_STATUS,
    COMPLETION_STATUS,
    N_ADMISSIONS,
    N_ADMISSIONS_CLOSED,
    N_POSTULATES,
    N_POSTULATES_DERIVED,
    admissions_registry,
    architecture_limits_registry,
    postulates_registry,
    completeness_verdict,
    completion_report,
)

ADMISSIONS = admissions_registry()
POSTULATES = postulates_registry()
LIMITS = architecture_limits_registry()


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'COMPLETION_CERTIFIED'

    def test_completion_status(self):
        assert COMPLETION_STATUS == 'MATHEMATICALLY_COMPLETE_IN_MINIMAL_5D_EFT'

    def test_n_admissions(self):
        assert N_ADMISSIONS == 13

    def test_n_admissions_closed(self):
        assert N_ADMISSIONS_CLOSED == 13

    def test_n_postulates(self):
        assert N_POSTULATES == 8

    def test_n_postulates_derived(self):
        assert N_POSTULATES_DERIVED == 8


class TestAdmissionsRegistry:
    def test_returns_thirteen_entries(self):
        assert len(ADMISSIONS) == 13

    @pytest.mark.parametrize('number', list(range(1, 14)))
    def test_each_admission_number_present(self, number):
        assert any(item['number'] == number for item in ADMISSIONS)

    @pytest.mark.parametrize('index', list(range(13)))
    def test_each_entry_has_status(self, index):
        assert 'status' in ADMISSIONS[index]

    @pytest.mark.parametrize('index', list(range(13)))
    def test_each_entry_has_closing_pillar(self, index):
        assert 'closing_pillar' in ADMISSIONS[index]

    @pytest.mark.parametrize('index', list(range(13)))
    def test_no_entry_open(self, index):
        assert ADMISSIONS[index]['status'] != 'OPEN'

    def test_admission7_closed(self):
        item = next(row for row in ADMISSIONS if row['number'] == 7)
        assert item['status'] == 'CLOSED'

    def test_admission10_bounded(self):
        item = next(row for row in ADMISSIONS if row['number'] == 10)
        assert item['status'] == 'CONSTRAINED_BOUNDED'


class TestArchitectureLimitsRegistry:
    def test_has_at_least_five_entries(self):
        assert len(LIMITS) >= 5

    @pytest.mark.parametrize('index', list(range(9)))
    def test_each_entry_has_name(self, index):
        assert 'name' in LIMITS[index]

    @pytest.mark.parametrize('index', list(range(9)))
    def test_each_entry_has_domain(self, index):
        assert 'domain' in LIMITS[index]

    @pytest.mark.parametrize('index', list(range(9)))
    def test_each_entry_has_honest_status(self, index):
        assert 'honest_status' in LIMITS[index]

    def test_contains_structural_open_entry(self):
        assert any(item['honest_status'] == 'STRUCTURAL_OPEN' for item in LIMITS)


class TestPostulatesRegistry:
    def test_returns_eight_entries(self):
        assert len(POSTULATES) == 8

    @pytest.mark.parametrize('postulate', ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8'])
    def test_each_postulate_present(self, postulate):
        assert any(item['postulate'] == postulate for item in POSTULATES)

    @pytest.mark.parametrize('index', list(range(8)))
    def test_each_postulate_has_status(self, index):
        assert POSTULATES[index]['status'] in {'DERIVED', 'OBSERVATIONALLY_SELECTED'}

    @pytest.mark.parametrize('index', list(range(8)))
    def test_each_postulate_has_derivation_pillar(self, index):
        assert 'derivation_pillar' in POSTULATES[index]


class TestCompletenessVerdict:
    @pytest.mark.parametrize('key', ['status', 'all_admissions_closed', 'all_postulates_derived', 'dag_acyclic', 'primary_falsifier', 'framework_completeness'])
    def test_expected_keys_present(self, key):
        assert key in completeness_verdict()

    def test_status(self):
        assert completeness_verdict()['status'] == 'COMPLETION_CERTIFIED'

    def test_all_admissions_closed(self):
        assert completeness_verdict()['all_admissions_closed'] is True

    def test_all_postulates_derived(self):
        assert completeness_verdict()['all_postulates_derived'] is True

    def test_dag_acyclic(self):
        assert completeness_verdict()['dag_acyclic'] is True

    def test_framework_status(self):
        assert completeness_verdict()['framework_completeness'] == 'MATHEMATICALLY_COMPLETE_IN_MINIMAL_5D_EFT'

    def test_primary_falsifier_mentions_litebird(self):
        assert 'LiteBIRD' in completeness_verdict()['primary_falsifier']


class TestCompletionReport:
    def test_returns_string(self):
        assert isinstance(completion_report(), str)

    def test_non_empty(self):
        assert completion_report().strip()

    def test_contains_completion_certified(self):
        assert 'COMPLETION_CERTIFIED' in completion_report()

    def test_contains_framework_status(self):
        assert 'MATHEMATICALLY_COMPLETE_IN_MINIMAL_5D_EFT' in completion_report()

    def test_contains_primary_falsifier(self):
        assert 'LiteBIRD' in completion_report()
