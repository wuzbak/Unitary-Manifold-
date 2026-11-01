# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 902 — fermion chain certificate."""
from __future__ import annotations

from src.sevend.pillar902_fermion_mass_chain_certificate import (
    FERMION_CHAIN_GATE,
    FERMION_PILLARS,
    FRACTION_CLOSED,
    FRACTION_TENSION,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    fermion_chain_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 902

def test_gate_string(): assert PILLAR_GATE == "FERMION_MASS_CHAIN_CERTIFICATE"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_chain_gate_string(): assert FERMION_CHAIN_GATE == "FERMION_CHAIN_PARTIAL"

def test_pillar_count(): assert len(FERMION_PILLARS) == 15

def test_first_pillar(): assert FERMION_PILLARS[0][0] == 887

def test_last_pillar(): assert FERMION_PILLARS[-1][0] == 901

def test_fraction_closed_interval(): assert 0.0 < FRACTION_CLOSED <= 1.0

def test_fraction_tension_interval(): assert 0.0 <= FRACTION_TENSION <= 1.0

def test_fraction_closed_gt_tension(): assert FRACTION_CLOSED > FRACTION_TENSION

def test_summary_gate(): assert fermion_chain_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert fermion_chain_summary()["pillar"] == 902

def test_summary_status(): assert fermion_chain_summary()["status_label"] == STATUS_LABEL

def test_summary_result_gate(): assert fermion_chain_summary()["result_gate"] == FERMION_CHAIN_GATE

def test_summary_pillars_len(): assert len(fermion_chain_summary()["fermion_pillars"]) == 15

def test_summary_fraction_closed(): assert fermion_chain_summary()["fraction_closed"] == FRACTION_CLOSED

def test_summary_fraction_tension(): assert fermion_chain_summary()["fraction_tension"] == FRACTION_TENSION

def test_no_toe_language(): assert "TOE" not in fermion_chain_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in fermion_chain_summary()
    return _test

globals()['test_generated_key_fermion_pillars_0'] = _generated_key_test_factory('fermion_pillars')
globals()['test_generated_key_fraction_closed_1'] = _generated_key_test_factory('fraction_closed')
globals()['test_generated_key_fraction_tension_2'] = _generated_key_test_factory('fraction_tension')
globals()['test_generated_key_epistemic_status_3'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_status_label_4'] = _generated_key_test_factory('status_label')
globals()['test_generated_key_result_gate_5'] = _generated_key_test_factory('result_gate')
globals()['test_generated_key_gate_6'] = _generated_key_test_factory('gate')
