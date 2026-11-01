# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 899 — lepton mass ratios."""
from __future__ import annotations

from src.sevend.pillar899_lepton_mass_ratios_fn import (
    LEPTON_RATIOS,
    LEPTON_RATIOS_GATE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    lepton_mass_ratios_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 899

def test_gate_string(): assert PILLAR_GATE == "LEPTON_MASS_RATIOS_7D_FN"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_ratios_length(): assert len(LEPTON_RATIOS) == 3

def test_ratios_start_one(): assert LEPTON_RATIOS[0] == 1.0

def test_ratios_monotone(): assert LEPTON_RATIOS[2] > LEPTON_RATIOS[1] > LEPTON_RATIOS[0]

def test_second_ratio_large(): assert LEPTON_RATIOS[1] > 1e6

def test_third_ratio_huge(): assert LEPTON_RATIOS[2] > 1e10

def test_gate_tension(): assert LEPTON_RATIOS_GATE == "TENSION"

def test_summary_gate(): assert lepton_mass_ratios_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert lepton_mass_ratios_summary()["pillar"] == 899

def test_summary_status(): assert lepton_mass_ratios_summary()["status_label"] == STATUS_LABEL

def test_summary_result_gate(): assert lepton_mass_ratios_summary()["result_gate"] == LEPTON_RATIOS_GATE

def test_summary_ratios_match(): assert lepton_mass_ratios_summary()["lepton_ratios"] == list(LEPTON_RATIOS)

def test_summary_factor5_false(): assert lepton_mass_ratios_summary()["within_factor5"] is False

def test_no_toe_language(): assert "TOE" not in lepton_mass_ratios_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in lepton_mass_ratios_summary()
    return _test

globals()['test_generated_key_pdg_lepton_ratios_0'] = _generated_key_test_factory('pdg_lepton_ratios')
globals()['test_generated_key_within_factor5_1'] = _generated_key_test_factory('within_factor5')
globals()['test_generated_key_epistemic_status_2'] = _generated_key_test_factory('epistemic_status')
globals()['test_generated_key_status_label_3'] = _generated_key_test_factory('status_label')
globals()['test_generated_key_result_gate_4'] = _generated_key_test_factory('result_gate')
globals()['test_generated_key_gate_5'] = _generated_key_test_factory('gate')
globals()['test_generated_key_pillar_6'] = _generated_key_test_factory('pillar')
globals()['test_generated_key_lepton_ratios_7'] = _generated_key_test_factory('lepton_ratios')
globals()['test_generated_key_ratio_span_8'] = _generated_key_test_factory('ratio_span')
