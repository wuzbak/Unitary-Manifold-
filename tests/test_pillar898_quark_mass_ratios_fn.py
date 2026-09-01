# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 898 — quark mass ratios."""
from __future__ import annotations

from src.sevend.pillar898_quark_mass_ratios_fn import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    QUARK_DOWN_RATIOS,
    QUARK_RATIOS_GATE,
    QUARK_UP_RATIOS,
    STATUS_LABEL,
    quark_mass_ratios_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 898

def test_gate_string(): assert PILLAR_GATE == "QUARK_MASS_RATIOS_7D_FN"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_up_ratios_length(): assert len(QUARK_UP_RATIOS) == 3

def test_down_ratios_length(): assert len(QUARK_DOWN_RATIOS) == 3

def test_up_start_one(): assert QUARK_UP_RATIOS[0] == 1.0

def test_down_start_one(): assert QUARK_DOWN_RATIOS[0] == 1.0

def test_up_monotone(): assert QUARK_UP_RATIOS[2] > QUARK_UP_RATIOS[1] > QUARK_UP_RATIOS[0]

def test_down_monotone(): assert QUARK_DOWN_RATIOS[2] > QUARK_DOWN_RATIOS[1] > QUARK_DOWN_RATIOS[0]

def test_up_second_large(): assert QUARK_UP_RATIOS[1] > 1e6

def test_up_third_huge(): assert QUARK_UP_RATIOS[2] > 1e20

def test_down_second_large(): assert QUARK_DOWN_RATIOS[1] > 1e6

def test_gate_tension(): assert QUARK_RATIOS_GATE == "TENSION"

def test_summary_gate(): assert quark_mass_ratios_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert quark_mass_ratios_summary()["pillar"] == 898

def test_summary_status(): assert quark_mass_ratios_summary()["status_label"] == STATUS_LABEL

def test_summary_result_gate(): assert quark_mass_ratios_summary()["result_gate"] == QUARK_RATIOS_GATE

def test_summary_up_ratios_match(): assert quark_mass_ratios_summary()["quark_up_ratios"] == list(QUARK_UP_RATIOS)

def test_summary_down_ratios_match(): assert quark_mass_ratios_summary()["quark_down_ratios"] == list(QUARK_DOWN_RATIOS)

def test_summary_up_not_within_factor5(): assert quark_mass_ratios_summary()["up_within_factor5"] is False

def test_summary_down_not_within_factor5(): assert quark_mass_ratios_summary()["down_within_factor5"] is False

def test_no_toe_language(): assert "TOE" not in quark_mass_ratios_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in quark_mass_ratios_summary()
    return _test

globals()['test_generated_key_pdg_up_ratios_0'] = _generated_key_test_factory('pdg_up_ratios')
globals()['test_generated_key_pdg_down_ratios_1'] = _generated_key_test_factory('pdg_down_ratios')
globals()['test_generated_key_up_within_factor5_2'] = _generated_key_test_factory('up_within_factor5')
globals()['test_generated_key_down_within_factor5_3'] = _generated_key_test_factory('down_within_factor5')
