# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 936 — Δm²₂₁ NLO Loop Closure."""
from __future__ import annotations
from src.core.pillar936_nu_mass_splitting_nlo import (
    N_W, K_CS, EPSILON_FN, DELTA_M21_SQ_PDG, SIGMA_DELTA_M21,
    DELTA_M21_TREE_PROXY, DELTA_NLO_CORRECTION, DELTA_M21_NLO_PROXY,
    PULL_TREE, PULL_NLO,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    delta_m21_nlo, delta_m21_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 936
def test_gate(): assert PILLAR_GATE == "NU_MASS_SPLITTING_NLO"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74
def test_epsilon_fn_range(): assert 0 < EPSILON_FN < 1

def test_pdg_value_positive(): assert DELTA_M21_SQ_PDG > 0
def test_sigma_positive(): assert SIGMA_DELTA_M21 > 0

def test_pull_tree_approx(): assert abs(PULL_TREE - 0.81) < 0.2  # ≈ 0.81σ

def test_nlo_correction_positive(): assert DELTA_NLO_CORRECTION > 0
def test_nlo_correction_less_than_1(): assert DELTA_NLO_CORRECTION < 1.0

def test_nlo_proxy_less_than_tree(): assert DELTA_M21_NLO_PROXY < DELTA_M21_TREE_PROXY

def test_pull_nlo_greater_than_2sigma(): assert PULL_NLO > 2.0  # NLO overcorrects — architecture limit

def test_status_valid():
    valid = {"DELTA_M21_NLO_CLOSED", "DELTA_M21_NLO_TENSION", "DELTA_M21_NLO_IRREDUCIBLE"}
    assert PILLAR_STATUS in valid

def test_status_irreducible(): assert PILLAR_STATUS == "DELTA_M21_NLO_IRREDUCIBLE"

def test_nlo_dict_keys():
    res = delta_m21_nlo()
    assert "pull_nlo_sigma" in res
    assert "status" in res
    assert "note" in res

def test_summary_pillar():
    s = delta_m21_summary()
    assert s["pillar"] == 936

def test_summary_pull_nlo_positive():
    s = delta_m21_summary()
    assert s["pull_nlo_sigma"] > 0.0  # irreducible — NLO pull recorded
