# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 488 — v15 ledger audit completion certificate."""
from __future__ import annotations

import pytest

from src.core.pillar488_v15_ledger_audit import (
    ADMISSION_COUNT,
    CANONICAL_LEDGER_PATHS,
    NEXT_PILLAR_SLOT,
    ONBOARDING_DOC_PATHS,
    PILLAR_LABEL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SPRINT_PILLARS,
    VERSION,
    admission_and_pillar_counts,
    doc_sync_certificate,
    onboarding_doc_targets,
    status_report,
    synchronized_ledgers,
    version_consistency_certificate,
)


class TestConstants:
    def test_label(self):
        assert PILLAR_LABEL == 'V15_LEDGER_AUDIT_COMPLETE'

    def test_status(self):
        assert PILLAR_STATUS == PILLAR_LABEL

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 488

    def test_version(self):
        assert VERSION == 'v15.0'

    def test_admission_count(self):
        assert ADMISSION_COUNT == 13

    def test_next_pillar_slot(self):
        assert NEXT_PILLAR_SLOT == 495

    def test_sprint_size(self):
        assert len(SPRINT_PILLARS) == 7

    def test_onboarding_size(self):
        assert len(ONBOARDING_DOC_PATHS) == 8

    def test_canonical_size(self):
        assert len(CANONICAL_LEDGER_PATHS) == 6


@pytest.mark.parametrize(
    'path',
    CANONICAL_LEDGER_PATHS,
)
def test_canonical_paths_cover_live_ledgers(path):
    assert path.endswith(('.md', '.yml'))


@pytest.mark.parametrize(
    'path',
    ONBOARDING_DOC_PATHS,
)
def test_onboarding_paths_are_doc_like(path):
    assert path.endswith('.md')


class TestCertificates:
    def test_synchronized_ledgers_flag(self):
        assert synchronized_ledgers()['synchronized'] is True

    def test_synchronized_ledgers_count(self):
        assert synchronized_ledgers()['count'] == 6

    def test_doc_sync_version(self):
        assert doc_sync_certificate()['version'] == VERSION

    def test_doc_sync_ledgers(self):
        assert doc_sync_certificate()['ledgers_synchronized'] is True

    def test_doc_sync_onboarding(self):
        assert doc_sync_certificate()['onboarding_docs_synchronized'] is True

    def test_doc_sync_regression_gate(self):
        assert doc_sync_certificate()['regression_gate'] == 'DOC_DRIFT_FIXED'

    def test_version_target(self):
        assert version_consistency_certificate()['target_version'] == VERSION

    def test_version_live_ledgers(self):
        assert version_consistency_certificate()['all_live_ledgers_target_v15'] is True

    def test_counts_first_pillar(self):
        assert admission_and_pillar_counts()['first_pillar'] == 488

    def test_counts_last_pillar(self):
        assert admission_and_pillar_counts()['last_pillar'] == 494

    def test_counts_next_slot(self):
        assert admission_and_pillar_counts()['next_pillar_slot'] == 495

    def test_counts_admissions(self):
        assert admission_and_pillar_counts()['admission_count'] == 13

    def test_onboarding_targets_roundtrip(self):
        assert onboarding_doc_targets() == list(ONBOARDING_DOC_PATHS)


class TestStatusReport:
    def test_report_pillar(self):
        assert status_report()['pillar'] == 488

    def test_report_label(self):
        assert status_report()['label'] == PILLAR_LABEL

    def test_report_status(self):
        assert status_report()['status'] == PILLAR_STATUS

    def test_report_contains_sync(self):
        assert 'ledger_sync' in status_report()

    def test_report_contains_counts(self):
        assert 'counts' in status_report()

    def test_report_contains_docs(self):
        assert len(status_report()['onboarding_docs']) == 8
