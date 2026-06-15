# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 465 — theorem registry v14."""
from __future__ import annotations

import pytest

from src.core.pillar465_theorem_registry_v14 import (
    PILLAR_STATUS,
    THEOREM_REGISTRY,
    VERSION,
    conjectural_theorems,
    count_by_status,
    get_by_status,
    pillar_report,
    proved_theorems,
    registry_summary,
    theorem_by_id,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'THEOREM_REGISTRY_V14_COMPLETE'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_registry_has_at_least_thirty(self):
        assert len(THEOREM_REGISTRY) >= 30

    def test_ids_unique(self):
        ids = [entry['id'] for entry in THEOREM_REGISTRY]
        assert len(ids) == len(set(ids))

    def test_required_keys(self):
        required = {'id', 'name', 'status', 'claim', 'proof_module', 'test_file', 'falsification', 'pillar'}
        for entry in THEOREM_REGISTRY:
            assert required <= set(entry.keys())


class TestSpecificEntries:
    def test_t001_proved(self):
        assert theorem_by_id('T001')['status'] == 'PROVED'

    def test_t002_mentions_74(self):
        assert '74' in theorem_by_id('T002')['claim']

    def test_t004_closed(self):
        assert theorem_by_id('T004')['status'] == 'CLOSED'

    def test_t008_conjectural(self):
        assert theorem_by_id('T008')['status'] == 'CONJECTURAL'

    def test_t010_conjectural(self):
        assert theorem_by_id('T010')['status'] == 'CONJECTURAL'

    def test_t017_structural(self):
        assert theorem_by_id('T017')['status'] == 'DERIVED_STRUCTURAL'

    def test_t032_planned_module(self):
        assert '(planned)' in theorem_by_id('T032')['proof_module']


class TestStatusQueries:
    def test_get_by_status_proved_nonempty(self):
        assert len(get_by_status('PROVED')) >= 2

    def test_get_by_status_conjectural_nonempty(self):
        assert len(get_by_status('CONJECTURAL')) >= 3

    def test_proved_theorems_are_proved(self):
        assert all(entry['status'] == 'PROVED' for entry in proved_theorems())

    def test_conjectural_theorems_are_conjectural(self):
        assert all(entry['status'] == 'CONJECTURAL' for entry in conjectural_theorems())

    def test_count_by_status_total(self):
        counts = count_by_status()
        assert sum(counts.values()) == len(THEOREM_REGISTRY)

    def test_count_by_status_has_conjectural(self):
        assert count_by_status()['CONJECTURAL'] >= 3

    def test_count_by_status_has_conditional(self):
        assert count_by_status()['DERIVED_CONDITIONAL'] >= 10


class TestLookup:
    def test_lookup_returns_copy(self):
        entry = theorem_by_id('T001')
        entry['name'] = 'changed'
        assert theorem_by_id('T001')['name'] != 'changed'

    def test_lookup_unknown_raises(self):
        with pytest.raises(KeyError):
            theorem_by_id('T999')


class TestSummary:
    def test_summary_total(self):
        assert registry_summary()['total_theorems'] == len(THEOREM_REGISTRY)

    def test_summary_proved_fraction_range(self):
        summary = registry_summary()
        assert 0 < summary['proved_fraction'] < 1

    def test_summary_conjectural_count_matches(self):
        assert registry_summary()['conjectural_count'] == count_by_status().get('CONJECTURAL', 0)


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 465

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_contains_registry(self):
        assert len(self.report['theorem_registry']) == len(THEOREM_REGISTRY)

    def test_contains_summary(self):
        assert 'summary' in self.report
