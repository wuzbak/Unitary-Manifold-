# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 440 — arXiv Manuscript Update v13.7."""
from __future__ import annotations

import pytest

from src.core.pillar440_arxiv_v137_update import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    VERSION,
    SPRINT_PILLARS,
    EPISTEMIC_DELTA_TABLE,
    v137_manifest,
    epistemic_delta_table,
    preregistration_registry,
    v137_sync_report,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'ARXIV_V137_READY'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 440

    def test_version(self):
        assert VERSION == 'v13.7'

    def test_sprint_pillars_length(self):
        assert len(SPRINT_PILLARS) == 7

    def test_pillar_range(self):
        numbers = [p['pillar'] for p in SPRINT_PILLARS]
        assert min(numbers) == 434
        assert max(numbers) == 440

    def test_epistemic_delta_table_length(self):
        assert len(EPISTEMIC_DELTA_TABLE) == 7


class TestV137Manifest:
    def setup_method(self):
        self.manifest = v137_manifest()

    def test_returns_dict(self):
        assert isinstance(self.manifest, dict)

    def test_version(self):
        assert self.manifest['version'] == 'v13.7'

    def test_pillar_range(self):
        assert self.manifest['pillar_range'] == (434, 440)

    def test_n_pillars(self):
        assert self.manifest['n_pillars'] == 7

    def test_n_preregistrations(self):
        assert self.manifest['n_preregistrations'] == 3

    def test_gap_closed(self):
        assert self.manifest['gap_closed'] == 'ADM_LAPSE_BSSN_CLOSED'

    def test_pillars_list(self):
        assert len(self.manifest['pillars']) == 7


class TestEpistemicDeltaTable:
    def setup_method(self):
        self.table = epistemic_delta_table()

    def test_returns_list(self):
        assert isinstance(self.table, list)

    def test_length(self):
        assert len(self.table) == 7

    def test_required_keys(self):
        for row in self.table:
            for key in ['item', 'before', 'after', 'pillar']:
                assert key in row

    def test_adm_lapse_closed(self):
        adm_rows = [r for r in self.table if 'ADM' in r['item']]
        assert len(adm_rows) == 1
        assert adm_rows[0]['after'] == 'ADM_LAPSE_BSSN_CLOSED'

    def test_spherex_preregistered(self):
        spherex = [r for r in self.table if 'SPHEREx' in r['item'] or 'f_NL' in r['item']]
        assert len(spherex) == 1
        assert 'FNLPREREGISTERED_SPHEREX' in spherex[0]['after']

    def test_all_pillars_in_range(self):
        for row in self.table:
            assert 434 <= row['pillar'] <= 440


class TestPreregistrationRegistry:
    def setup_method(self):
        self.registry = preregistration_registry()

    def test_returns_list(self):
        assert isinstance(self.registry, list)

    def test_three_preregistrations(self):
        assert len(self.registry) == 3

    def test_required_keys(self):
        for entry in self.registry:
            for key in ['pillar', 'experiment', 'observable', 'prediction', 'date', 'module']:
                assert key in entry

    def test_pillars(self):
        pillars = [e['pillar'] for e in self.registry]
        assert 435 in pillars
        assert 436 in pillars
        assert 437 in pillars

    def test_spherex_has_sha256(self):
        spherex = [e for e in self.registry if e['pillar'] == 437][0]
        assert spherex.get('sha256_committed') is True

    def test_all_dated_2026(self):
        for e in self.registry:
            assert '2026' in e['date']


class TestV137SyncReport:
    def setup_method(self):
        self.report = v137_sync_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar(self):
        assert self.report['pillar'] == 440

    def test_status(self):
        assert self.report['status'] == 'ARXIV_V137_READY'

    def test_version(self):
        assert self.report['version'] == 'v13.7'

    def test_next_slot(self):
        assert self.report['next_pillar_slot'] == 441

    def test_failures_zero(self):
        assert self.report['failures'] == 0

    def test_ledger_updates_keys(self):
        lu = self.report['ledger_updates']
        assert 'STATUS.md' in lu
        assert 'FALLIBILITY.md' in lu
        assert 'docs/WAVE_CHANGELOG.md' in lu

    def test_preregistrations_count(self):
        assert len(self.report['preregistrations']) == 3

    def test_epistemic_deltas_count(self):
        assert len(self.report['epistemic_deltas']) == 7
