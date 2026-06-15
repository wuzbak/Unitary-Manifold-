# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 456 — formal status of conjectural quantum theorems."""
import pytest

from src.core.pillar456_quantum_theorem_formal_status import (
    PILLAR_STATUS,
    VERSION,
    ccr_formal_conjecture,
    er_epr_formal_conjecture,
    conjecture_registry,
    check_no_unformalized_conjectures,
    pillar_report,
)

REQUIRED_KEYS = {
    'statement',
    'hypothesis',
    'conclusion',
    'obstruction',
    'proof_criteria',
    'experimental_handle',
    'status',
}


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'CONJECTURAL_THEOREMS_FORMALLY_STATED'

    def test_version(self):
        assert VERSION == 'v14.0'


class TestCCRFormalConjecture:
    def test_required_keys(self):
        assert set(ccr_formal_conjecture()) == REQUIRED_KEYS

    def test_status_conjectural(self):
        assert ccr_formal_conjecture()['status'] == 'CONJECTURAL'

    def test_obstruction_exact(self):
        assert 'Moyal *-product in RS1 KK background not computed' in ccr_formal_conjecture()['obstruction']

    def test_proof_criteria_mentions_star_product(self):
        assert 'star product' in ccr_formal_conjecture()['proof_criteria']

    def test_experimental_handle_mentions_quantum_optics(self):
        assert 'quantum optics' in ccr_formal_conjecture()['experimental_handle']

    @pytest.mark.parametrize('key', sorted(REQUIRED_KEYS))
    def test_all_fields_nonempty(self, key):
        assert ccr_formal_conjecture()[key]


class TestEREPRFormalConjecture:
    def test_required_keys(self):
        assert set(er_epr_formal_conjecture()) == REQUIRED_KEYS

    def test_status_conjectural(self):
        assert er_epr_formal_conjecture()['status'] == 'CONJECTURAL'

    def test_obstruction_exact(self):
        assert 'Ryu-Takayanagi formula not derived in RS1 KK bulk' in er_epr_formal_conjecture()['obstruction']

    def test_proof_criteria_mentions_large_n(self):
        assert 'large-N' in er_epr_formal_conjecture()['proof_criteria']

    def test_experimental_handle_mentions_hl_lhc(self):
        assert 'HL-LHC' in er_epr_formal_conjecture()['experimental_handle']

    @pytest.mark.parametrize('key', sorted(REQUIRED_KEYS))
    def test_all_fields_nonempty(self, key):
        assert er_epr_formal_conjecture()[key]


class TestRegistry:
    def test_registry_count(self):
        assert conjecture_registry()['count'] == 2

    def test_registry_keys(self):
        assert set(conjecture_registry()['conjectures']) == {'ccr', 'er_epr'}

    def test_registry_status(self):
        assert conjecture_registry()['status'] == PILLAR_STATUS

    def test_required_keys_listed(self):
        assert set(conjecture_registry()['all_required_keys']) == REQUIRED_KEYS

    @pytest.mark.parametrize('name', ['ccr', 'er_epr'])
    def test_each_registered_conjecture_complete(self, name):
        assert set(conjecture_registry()['conjectures'][name]) == REQUIRED_KEYS


class TestFormalizationCheck:
    def test_no_unformalized_conjectures(self):
        assert check_no_unformalized_conjectures() is True


class TestRegistryCrossChecks:
    def test_ccr_and_er_epr_both_conjectural(self):
        registry = conjecture_registry()['conjectures']
        assert registry['ccr']['status'] == 'CONJECTURAL'
        assert registry['er_epr']['status'] == 'CONJECTURAL'

    def test_ccr_statement_mentions_commutator(self):
        assert 'commutator' in ccr_formal_conjecture()['conclusion']

    def test_er_epr_statement_mentions_bridge(self):
        assert 'bridge' in er_epr_formal_conjecture()['conclusion']


class TestPillarReport:
    def test_pillar_number(self):
        assert pillar_report()['pillar'] == 456

    def test_status(self):
        assert pillar_report()['status'] == PILLAR_STATUS

    def test_registry_in_report(self):
        assert 'registry' in pillar_report()

    def test_all_conjectures_formalized(self):
        assert pillar_report()['all_conjectures_formalized'] is True
