# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 493 — admission closure certificate v15."""
from __future__ import annotations

import pytest

from src.core.pillar493_admission_closure_cert_v15 import (
    ADMISSION_REGISTRY,
    PILLAR_LABEL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    closure_certificate,
    count_by_status,
    get_admission,
    status_report,
    unresolved_admissions,
)


class TestConstants:
    def test_label(self):
        assert PILLAR_LABEL == 'ADMISSION_CLOSURE_CERTIFICATE_V15'

    def test_status(self):
        assert PILLAR_STATUS == PILLAR_LABEL

    def test_number(self):
        assert PILLAR_NUMBER == 493

    def test_version(self):
        assert VERSION == 'v15.0'

    def test_registry_size(self):
        assert len(ADMISSION_REGISTRY) == 13

    def test_numbers_cover_range(self):
        assert [entry['number'] for entry in ADMISSION_REGISTRY] == list(range(1, 14))


@pytest.mark.parametrize(
    'number, status',
    [
        (1, 'OBSERVATIONALLY_SELECTED'),
        (2, 'ALGEBRAICALLY_DERIVED'),
        (3, 'RESOLVED'),
        (4, 'ANALYTICALLY_CLOSED'),
        (5, 'DERIVED'),
        (6, 'FREE_PARAMETER'),
        (7, 'ARCHITECTURE_LIMIT'),
        (8, 'ASSESSED'),
        (9, 'EW_RADION_SAFE'),
        (10, 'CONSTRAINED_BOUNDED'),
        (11, 'CLOSED'),
        (12, 'CLOSED'),
        (13, 'CLOSED'),
    ],
)
def test_specific_admission_statuses(number, status):
    assert get_admission(number)['status'] == status


class TestSelectors:
    def test_unresolved_admissions(self):
        assert unresolved_admissions() == [6, 7, 10]

    def test_status_counts_closed(self):
        assert count_by_status()['CLOSED'] == 3

    def test_status_counts_free_parameter(self):
        assert count_by_status()['FREE_PARAMETER'] == 1

    def test_status_counts_architecture_limit(self):
        assert count_by_status()['ARCHITECTURE_LIMIT'] == 1

    def test_status_counts_assessed(self):
        assert count_by_status()['ASSESSED'] == 1

    def test_lookup_unknown_raises(self):
        with pytest.raises(KeyError):
            get_admission(99)


class TestCertificate:
    def test_total_admissions(self):
        assert closure_certificate()['total_admissions'] == 13

    def test_honest_gap_count(self):
        assert closure_certificate()['honest_gap_count'] == 3

    def test_unresolved_numbers(self):
        assert closure_certificate()['unresolved_admissions'] == [6, 7, 10]

    def test_headline_mentions_thirteen(self):
        assert 'thirteen admissions' in closure_certificate()['headline']

    def test_status_counts_roundtrip(self):
        assert closure_certificate()['status_counts'] == count_by_status()


class TestStatusReport:
    def test_report_pillar(self):
        assert status_report()['pillar'] == 493

    def test_report_label(self):
        assert status_report()['label'] == PILLAR_LABEL

    def test_report_status(self):
        assert status_report()['status'] == PILLAR_STATUS

    def test_report_version(self):
        assert status_report()['version'] == VERSION

    def test_report_contains_certificate(self):
        assert status_report()['certificate']['honest_gap_count'] == 3
