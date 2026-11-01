# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 900 — neutrino ordering."""
from __future__ import annotations

import pytest

from src.sevend.pillar900_neutrino_mass_ordering import (
    DELTA_M21_SQ,
    DELTA_M31_SQ,
    MASS_ORDERING,
    ORDERING_GATE,
    PDG_PREFERENCE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    heavy_neutrino_scales_gev,
    light_neutrino_masses_ev,
    neutrino_ordering_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 900

def test_gate_string(): assert PILLAR_GATE == "NEUTRINO_MASS_ORDERING_AUDIT"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_heavy_scales_length(): assert len(heavy_neutrino_scales_gev()) == 3

def test_heavy_scales_descend():
    m1, m2, m3 = heavy_neutrino_scales_gev()
    assert m1 > m2 > m3 > 0.0


def test_light_masses_length(): assert len(light_neutrino_masses_ev()) == 3

def test_light_masses_ascend():
    m1, m2, m3 = light_neutrino_masses_ev()
    assert 0.0 < m1 < m2 < m3


def test_delta21_positive(): assert DELTA_M21_SQ > 0.0

def test_delta31_positive(): assert DELTA_M31_SQ > 0.0

def test_delta31_scale(): assert DELTA_M31_SQ == pytest.approx(2.49e-3, rel=0.1)

def test_ordering_normal(): assert MASS_ORDERING == "NORMAL"

def test_pdg_preference_normal(): assert PDG_PREFERENCE == "NORMAL"

def test_gate_recovered(): assert ORDERING_GATE == "NORMAL_ORDERING_RECOVERED"

def test_summary_gate(): assert neutrino_ordering_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert neutrino_ordering_summary()["pillar"] == 900

def test_summary_status(): assert neutrino_ordering_summary()["status_label"] == STATUS_LABEL

def test_summary_result_gate(): assert neutrino_ordering_summary()["result_gate"] == ORDERING_GATE

def test_summary_heavy_count(): assert len(neutrino_ordering_summary()["heavy_neutrino_scales_gev"]) == 3

def test_summary_light_count(): assert len(neutrino_ordering_summary()["light_neutrino_masses_ev"]) == 3

def test_summary_mass_ordering(): assert neutrino_ordering_summary()["mass_ordering"] == "NORMAL"

def test_summary_pdg_preference(): assert neutrino_ordering_summary()["pdg_preference"] == "NORMAL"

def test_no_toe_language(): assert "TOE" not in neutrino_ordering_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in neutrino_ordering_summary()
    return _test

globals()['test_generated_key_heavy_neutrino_scales_gev_0'] = _generated_key_test_factory('heavy_neutrino_scales_gev')
globals()['test_generated_key_light_neutrino_masses_ev_1'] = _generated_key_test_factory('light_neutrino_masses_ev')
globals()['test_generated_key_pdg_delta_m21_sq_2'] = _generated_key_test_factory('pdg_delta_m21_sq')
globals()['test_generated_key_pdg_delta_m31_sq_3'] = _generated_key_test_factory('pdg_delta_m31_sq')
