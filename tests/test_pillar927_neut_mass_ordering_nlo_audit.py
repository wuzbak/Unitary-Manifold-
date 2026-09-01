# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 927 — neutrino mass ordering NLO audit."""
from __future__ import annotations
from src.core.pillar927_neut_mass_ordering_nlo_audit import (
    N_W, K_CS, EPSILON_FN, DELTA_NLO, DELTA_M31_SQ_TREE, DELTA_M31_SQ_NLO,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    neutrino_ordering_nlo, pmns_ordering_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 927
def test_gate(): assert PILLAR_GATE == "NEUT_MASS_ORDERING_NLO_AUDIT"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74
def test_epsilon_fn_range(): assert 0 < EPSILON_FN < 1
def test_delta_nlo_small(): assert abs(DELTA_NLO) < 0.01
def test_delta_m31_sq_tree_positive(): assert DELTA_M31_SQ_TREE > 0
def test_pillar_status_valid():
    assert PILLAR_STATUS in {
        "PMNS_ORDERING_NO_NLO_STABLE",
        "PMNS_ORDERING_NLO_FLIP",
        "PMNS_ORDERING_NLO_INCONCLUSIVE",
    }

def test_ordering_dict():
    r = neutrino_ordering_nlo()
    assert isinstance(r, dict)

def test_ordering_pillar():
    r = neutrino_ordering_nlo()
    assert r["pillar"] == 927

def test_ordering_gate():
    r = neutrino_ordering_nlo()
    assert r["gate"] == "NEUT_MASS_ORDERING_NLO_AUDIT"

def test_ordering_status():
    r = neutrino_ordering_nlo()
    assert r["status"] == PILLAR_STATUS

def test_ordering_delta_nlo():
    r = neutrino_ordering_nlo()
    assert abs(r["delta_nlo"] - DELTA_NLO) < 1e-15

def test_ordering_delta_m31_nlo():
    r = neutrino_ordering_nlo()
    assert abs(r["delta_m31_sq_nlo"] - DELTA_M31_SQ_NLO) < 1e-15

def test_ordering_interpretation():
    r = neutrino_ordering_nlo()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 20

def test_ordering_references():
    r = neutrino_ordering_nlo()
    assert isinstance(r["references"], list) and len(r["references"]) >= 3

def test_ordering_open_item_closed():
    r = neutrino_ordering_nlo()
    assert isinstance(r["open_item_closed"], bool)

def test_summary_dict():
    s = pmns_ordering_summary()
    assert isinstance(s, dict)

def test_summary_pillar():
    s = pmns_ordering_summary()
    assert s["pillar"] == 927

def test_summary_status():
    s = pmns_ordering_summary()
    assert s["status"] == PILLAR_STATUS
