# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 473 — truth-surface sync checker for v14."""
from __future__ import annotations

from src.core.pillar473_truth_surface_sync_v14 import (
    PILLAR_STATUS,
    VERSION,
    V14_SYNC_MANIFEST,
    check_claim_master_board_sync,
    check_derivation_status_sync,
    check_fallibility_sync,
    check_gatekeeper_sync,
    check_mas_tracker_sync,
    check_truth_layer_sync,
    full_sync_report,
    pillar_report,
    sync_discrepancies,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'TRUTH_SURFACE_SYNC_V14_COMPLETE'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_manifest_has_six_surfaces(self):
        assert len(V14_SYNC_MANIFEST) == 6

    def test_manifest_has_truth_layer(self):
        assert 'truth_layer' in V14_SYNC_MANIFEST

    def test_manifest_has_derivation_status(self):
        assert 'derivation_status' in V14_SYNC_MANIFEST


class TestIndividualChecks:
    def test_truth_layer_returns_dict(self):
        assert isinstance(check_truth_layer_sync(), dict)

    def test_truth_layer_surface_name(self):
        assert check_truth_layer_sync()['surface'] == 'truth_layer'

    def test_fallibility_surface_name(self):
        assert check_fallibility_sync()['surface'] == 'fallibility'

    def test_derivation_status_surface_name(self):
        assert check_derivation_status_sync()['surface'] == 'derivation_status'

    def test_gatekeeper_surface_name(self):
        assert check_gatekeeper_sync()['surface'] == 'gatekeeper'

    def test_claim_master_surface_name(self):
        assert check_claim_master_board_sync()['surface'] == 'claim_master_board'

    def test_mas_tracker_surface_name(self):
        assert check_mas_tracker_sync()['surface'] == 'mas_tracker'

    def test_derivation_status_synced(self):
        assert check_derivation_status_sync()['synced'] is True

    def test_gatekeeper_synced(self):
        assert check_gatekeeper_sync()['synced'] is True

    def test_mas_tracker_synced(self):
        assert check_mas_tracker_sync()['synced'] is True

    def test_truth_layer_not_yet_synced(self):
        assert check_truth_layer_sync()['synced'] is False

    def test_fallibility_not_yet_synced(self):
        assert check_fallibility_sync()['synced'] is False

    def test_claim_master_not_yet_synced(self):
        assert check_claim_master_board_sync()['synced'] is False

    def test_unsynced_surface_has_missing_tokens(self):
        assert check_truth_layer_sync()['missing_tokens']

    def test_synced_surface_has_no_missing_tokens(self):
        assert check_gatekeeper_sync()['missing_tokens'] == []


class TestFullReport:
    def setup_method(self):
        self.report = full_sync_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_version(self):
        assert self.report['version'] == 'v14.0'

    def test_surface_count(self):
        assert self.report['n_surfaces'] == 6

    def test_synced_count(self):
        assert self.report['n_synced'] == 3

    def test_unsynced_count(self):
        assert self.report['n_unsynced'] == 3

    def test_all_synced_false(self):
        assert self.report['all_synced'] is False

    def test_unsynced_surfaces(self):
        assert set(self.report['unsynced_surfaces']) == {'truth_layer', 'fallibility', 'claim_master_board'}


class TestDiscrepancies:
    def test_returns_list(self):
        assert isinstance(sync_discrepancies(), list)

    def test_length_matches_unsynced(self):
        assert len(sync_discrepancies()) == 3

    def test_contains_truth_layer(self):
        assert any(item['surface'] == 'truth_layer' for item in sync_discrepancies())

    def test_contains_missing_tokens_key(self):
        assert all('missing_tokens' in item for item in sync_discrepancies())


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 473

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_contains_manifest(self):
        assert 'manifest' in self.report

    def test_contains_sync_report(self):
        assert 'sync_report' in self.report

    def test_contains_discrepancies(self):
        assert 'discrepancies' in self.report
