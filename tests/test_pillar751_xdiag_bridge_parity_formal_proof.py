# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 751 — xdiag_bridge_parity_formal_proof.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""
from __future__ import annotations

import importlib
import math

import pytest

module = importlib.import_module('src.core.pillar751_xdiag_bridge_parity_formal_proof')
EXPECT = module.TEST_EXPECTATIONS
MAIN = getattr(module, EXPECT['main_function'])
RESULT = MAIN()


@pytest.mark.parametrize('name, expected', list(EXPECT.get('scalar_checks', {}).items()))
def test_scalar_checks(name, expected):
    assert getattr(module, name) == expected


@pytest.mark.parametrize('name, expected', list(EXPECT.get('float_checks', {}).items()))
def test_float_checks(name, expected):
    assert getattr(module, name) == pytest.approx(expected, rel=1e-9, abs=1e-12)


@pytest.mark.parametrize('symbol', EXPECT.get('required_symbols', []))
def test_required_symbols(symbol):
    assert hasattr(module, symbol)


@pytest.mark.parametrize('key', EXPECT.get('required_keys', []))
def test_required_keys(key):
    assert key in RESULT


@pytest.mark.parametrize('key', list(RESULT.keys()))
def test_result_keys_are_populated(key):
    assert RESULT[key] is not None


def test_main_returns_dict():
    assert isinstance(RESULT, dict)


def test_pillar_matches_result():
    assert RESULT['pillar'] == module.PILLAR


def test_status_matches_result():
    assert RESULT['status'] == module.STATUS


def test_epistemic_label_matches_result():
    assert RESULT['epistemic_label'] == module.EPISTEMIC_LABEL


def test_honest_note_present():
    assert isinstance(RESULT['honest_note'], str)
    assert len(RESULT['honest_note']) > 10


def test_forbidden_keys_absent():
    for key in EXPECT.get('forbidden_keys', []):
        assert key not in RESULT


def test_module_docstring_present():
    assert module.__doc__
    assert 'Theory: ThomasCory Walker-Pearson (2026)' in module.__doc__
    assert 'Code: GitHub Copilot (AI)' in module.__doc__
