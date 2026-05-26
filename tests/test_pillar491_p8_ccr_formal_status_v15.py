# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 491 — P8 / CCR formal status v15."""
from __future__ import annotations

import pytest

from src.core.pillar491_p8_ccr_formal_status_v15 import (
    PILLAR_LABEL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REQUIRED_KEYS,
    VERSION,
    ccr_formal_status,
    p8_formal_status,
    status_report,
    theorem_pair_status,
)


class TestConstants:
    def test_label(self):
        assert PILLAR_LABEL == 'P8_CCR_FORMAL_STATUS_V15'

    def test_status(self):
        assert PILLAR_STATUS == PILLAR_LABEL

    def test_number(self):
        assert PILLAR_NUMBER == 491

    def test_version(self):
        assert VERSION == 'v15.0'

    def test_required_key_count(self):
        assert len(REQUIRED_KEYS) == 6


@pytest.mark.parametrize('key', REQUIRED_KEYS)
def test_p8_has_required_keys(key):
    assert key in p8_formal_status()


@pytest.mark.parametrize('key', REQUIRED_KEYS)
def test_ccr_has_required_keys(key):
    assert key in ccr_formal_status()


class TestP8Status:
    def test_p8_status(self):
        assert p8_formal_status()['status'] == 'PROVED_OVER_INTEGER_LATTICE'

    def test_p8_domain(self):
        assert p8_formal_status()['domain'] == 'integer lattice'

    def test_p8_verdict(self):
        assert p8_formal_status()['verdict'] == 'PROVED_OVER_INTEGER_LATTICE__NAMED_RESIDUAL_FULL_FUNCTION_SPACE'

    def test_p8_full_function_space_residual(self):
        assert p8_formal_status()['full_function_space_status'] == 'NAMED_RESIDUAL'

    def test_p8_reference(self):
        assert p8_formal_status()['pillar_reference'] == 455


class TestCCRStatus:
    def test_ccr_status(self):
        assert ccr_formal_status()['status'] == 'CONJECTURAL'

    def test_ccr_domain(self):
        assert ccr_formal_status()['domain'] == 'discrete KK spectrum'

    def test_ccr_statement_mentions_commutator(self):
        assert '[q, p] = iħ' in ccr_formal_status()['statement']

    def test_ccr_statement_mentions_limit(self):
        assert 'dim(H_KK) → ∞' in ccr_formal_status()['statement']

    def test_ccr_limit_token(self):
        assert ccr_formal_status()['limit'] == 'dim(H_KK) -> infinity'


class TestRegistry:
    def test_all_required_keys_present(self):
        assert theorem_pair_status()['all_required_keys_present'] is True

    def test_proved_count(self):
        assert theorem_pair_status()['proved_count'] == 1

    def test_conjectural_count(self):
        assert theorem_pair_status()['conjectural_count'] == 1

    def test_registry_contains_p8(self):
        assert 'P8' in theorem_pair_status()['theorems']

    def test_registry_contains_ccr(self):
        assert 'CCR' in theorem_pair_status()['theorems']


class TestStatusReport:
    def test_report_pillar(self):
        assert status_report()['pillar'] == 491

    def test_report_label(self):
        assert status_report()['label'] == PILLAR_LABEL

    def test_report_status(self):
        assert status_report()['status'] == PILLAR_STATUS

    def test_report_required_keys(self):
        assert len(status_report()['required_keys']) == len(REQUIRED_KEYS)

    def test_report_registry(self):
        assert status_report()['registry']['all_required_keys_present'] is True
