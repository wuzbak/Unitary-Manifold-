# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 466 — admission closure certificate."""
from __future__ import annotations

import pytest

from src.core.pillar466_admission_closure_certificate import (
    ADMISSION_REGISTRY,
    PILLAR_STATUS,
    VERSION,
    admissions_by_status,
    closure_certificate,
    count_by_closure_type,
    count_closed,
    get_admission,
    open_admissions,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'ADMISSION_CLOSURE_CERTIFICATE_V14_COMPLETE'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_registry_size(self):
        assert len(ADMISSION_REGISTRY) == 13

    def test_numbers_cover_range(self):
        assert [entry['number'] for entry in ADMISSION_REGISTRY] == list(range(1, 14))


class TestSpecificAdmissions:
    def test_admission_one_closed(self):
        assert get_admission(1)['status'] == 'CLOSED'

    def test_admission_seven_architecture_limit(self):
        assert get_admission(7)['closure_type'] == 'ARCHITECTURE_LIMIT'

    def test_admission_eight_irreducible(self):
        assert get_admission(8)['closure_type'] == 'OPEN_IRREDUCIBLE'

    def test_admission_eleven_conditional(self):
        assert get_admission(11)['closure_type'] == 'CONDITIONALLY_CLOSED'

    def test_admission_thirteen_named_residual(self):
        assert get_admission(13)['closure_type'] == 'NAMED_RESIDUAL'

    def test_open_item_has_target(self):
        assert get_admission(10)['min_observational_target']['experiment'] == 'HL-LHC'

    def test_closed_item_has_no_target(self):
        assert get_admission(4)['min_observational_target'] is None


class TestSelectors:
    def test_admissions_by_status_closed(self):
        assert len(admissions_by_status('CLOSED')) == 7

    def test_count_closed(self):
        assert count_closed() == 7

    def test_counts_sum(self):
        counts = count_by_closure_type()
        assert sum(counts.values()) == 13

    def test_closed_count_in_counts(self):
        assert count_by_closure_type()['CLOSED'] == 7

    def test_architecture_count(self):
        assert count_by_closure_type()['ARCHITECTURE_LIMIT'] == 2

    def test_conditional_count(self):
        assert count_by_closure_type()['CONDITIONALLY_CLOSED'] == 2

    def test_named_residual_count(self):
        assert count_by_closure_type()['NAMED_RESIDUAL'] == 1

    def test_open_admissions_size(self):
        assert len(open_admissions()) == 6

    def test_open_admissions_exclude_closed(self):
        assert all(entry['closure_type'] != 'CLOSED' for entry in open_admissions())

    def test_lookup_unknown_raises(self):
        with pytest.raises(KeyError):
            get_admission(99)


class TestCertificate:
    def setup_method(self):
        self.certificate = closure_certificate()

    def test_total_admissions(self):
        assert self.certificate['total_admissions'] == 13

    def test_fully_closed(self):
        assert self.certificate['fully_closed'] == 7

    def test_open_admission_numbers(self):
        assert self.certificate['open_admissions'] == [7, 8, 10, 11, 12, 13]

    def test_headline_mentions_v14(self):
        assert 'v14' in self.certificate['headline']


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 466

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_registry_present(self):
        assert len(self.report['admission_registry']) == 13

    def test_certificate_present(self):
        assert 'certificate' in self.report
