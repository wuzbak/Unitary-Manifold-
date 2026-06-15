# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 494 — arXiv v15 external package."""
from __future__ import annotations

import pytest

from src.core.pillar494_arxiv_v15_package import (
    PILLAR_LABEL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    V15_PACKAGE_SCOPE,
    VERSION,
    abstract_v15,
    falsification_protocol,
    prediction_table,
    reviewer_briefing,
    status_report,
    submission_readiness_checklist,
)


class TestConstants:
    def test_label(self):
        assert PILLAR_LABEL == 'ARXIV_V15_EXTERNAL_PACKAGE'

    def test_status(self):
        assert PILLAR_STATUS == PILLAR_LABEL

    def test_number(self):
        assert PILLAR_NUMBER == 494

    def test_version(self):
        assert VERSION == 'v15.0'

    def test_scope_versions(self):
        assert V15_PACKAGE_SCOPE['from_version'] == 'v14.2'
        assert V15_PACKAGE_SCOPE['to_version'] == 'v15.0'

    def test_scope_range(self):
        assert V15_PACKAGE_SCOPE['pillar_range'] == (488, 494)


class TestAbstract:
    def test_mentions_p488(self):
        assert 'P488' in abstract_v15()

    def test_mentions_p494(self):
        assert 'P494' in abstract_v15()

    def test_mentions_peak3(self):
        assert 'peak-3 residual' in abstract_v15()

    def test_mentions_ccr(self):
        assert 'CCR' in abstract_v15()


class TestReviewerBriefing:
    def test_returns_multiple_items(self):
        assert len(reviewer_briefing()) == 5

    def test_mentions_fallibility(self):
        assert 'FALLIBILITY.md' in reviewer_briefing()[0]

    def test_mentions_alpha_s(self):
        assert any('α_s' in item for item in reviewer_briefing())

    def test_mentions_litebird(self):
        assert any('LiteBIRD' in item for item in reviewer_briefing())


class TestFalsificationProtocol:
    def test_primary_falsifier(self):
        assert falsification_protocol()['primary_falsifier'] == 'LiteBIRD cosmic birefringence beta window'

    def test_allowed_window(self):
        assert falsification_protocol()['allowed_window_deg'] == [0.22, 0.38]

    def test_forbidden_gap(self):
        assert falsification_protocol()['forbidden_gap_deg'] == [0.29, 0.31]

    def test_has_secondary_checks(self):
        assert len(falsification_protocol()['secondary_checks']) == 3


class TestPredictionTable:
    def test_length(self):
        assert len(prediction_table()) == 4

    def test_contains_primary_falsifier(self):
        assert prediction_table()[0]['status'] == 'PRIMARY_FALSIFIER'

    def test_contains_irreducible_within_5d(self):
        assert any(row['status'] == 'IRREDUCIBLE_WITHIN_5D' for row in prediction_table())

    def test_contains_bound_check(self):
        assert any(row['status'] == 'BOUND_CHECK' for row in prediction_table())


class TestChecklistAndReport:
    def test_checklist_length(self):
        assert len(submission_readiness_checklist()) == 7

    def test_checklist_mentions_pytest(self):
        assert any('pytest gate' in item for item in submission_readiness_checklist())

    def test_report_pillar(self):
        assert status_report()['pillar'] == 494

    def test_report_label(self):
        assert status_report()['label'] == PILLAR_LABEL

    def test_report_status(self):
        assert status_report()['status'] == PILLAR_STATUS

    def test_report_version(self):
        assert status_report()['version'] == VERSION

    def test_report_contains_scope(self):
        assert status_report()['scope']['to_version'] == 'v15.0'

    def test_report_contains_prediction_table(self):
        assert len(status_report()['prediction_table']) == 4
