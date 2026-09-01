# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 919 — CKM 13D Yukawa texture audit."""
from __future__ import annotations
import numpy as np
from src.core.pillar919_ckm_13d_yukawa_texture_audit import (
    N_W, K_CS, EPSILON_FN, PDG_THETA_12, PDG_THETA_23, PDG_THETA_13,
    PDG_JARLSKOG, PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    build_yukawa_texture, ckm_from_texture, jarlskog_invariant,
    ckm_13d_yukawa_audit, ckm_13d_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 919
def test_gate(): assert PILLAR_GATE == "CKM_13D_YUKAWA_TEXTURE_AUDIT"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74
def test_epsilon_fn_range(): assert 0 < EPSILON_FN < 1
def test_epsilon_fn_value(): assert abs(EPSILON_FN - K_CS**(-0.25)) < 1e-12

def test_pdg_theta_ordering():
    """PDG angles satisfy θ₁₂ > θ₂₃ > θ₁₃."""
    assert PDG_THETA_12 > PDG_THETA_23 > PDG_THETA_13 > 0

def test_pdg_jarlskog_positive(): assert PDG_JARLSKOG > 0

def test_build_yukawa_texture_shape():
    qu = (4.0, 3.0, 2.0)
    qd = (4.5, 3.5, 2.5)
    Yu, Yd = build_yukawa_texture(qu, qd)
    assert Yu.shape == (3, 3)
    assert Yd.shape == (3, 3)

def test_build_yukawa_texture_positive():
    qu = (4.0, 3.0, 2.0)
    qd = (4.5, 3.5, 2.5)
    Yu, Yd = build_yukawa_texture(qu, qd)
    assert np.all(Yu > 0)
    assert np.all(Yd > 0)

def test_build_yukawa_texture_symmetric():
    qu = (4.0, 3.0, 2.0)
    qd = (4.0, 3.0, 2.0)
    Yu, _ = build_yukawa_texture(qu, qd)
    assert np.allclose(Yu, Yu.T)

def test_ckm_from_texture_shape():
    qu = (4.0, 3.0, 2.0)
    qd = (4.5, 3.5, 2.5)
    Yu, Yd = build_yukawa_texture(qu, qd)
    V = ckm_from_texture(Yu, Yd)
    assert V.shape == (3, 3)

def test_jarlskog_nonneg():
    qu = (4.0, 3.0, 2.0)
    qd = (4.5, 3.5, 2.5)
    Yu, Yd = build_yukawa_texture(qu, qd)
    V = ckm_from_texture(Yu, Yd)
    J = jarlskog_invariant(V)
    assert J >= 0

def test_audit_returns_dict():
    r = ckm_13d_yukawa_audit()
    assert isinstance(r, dict)

def test_audit_has_status():
    r = ckm_13d_yukawa_audit()
    assert r["status"] in {"CLOSED", "PARTIAL_TENSION", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}

def test_audit_pillar():
    r = ckm_13d_yukawa_audit()
    assert r["pillar"] == 919

def test_audit_gate():
    r = ckm_13d_yukawa_audit()
    assert r["gate"] == "CKM_13D_YUKAWA_TEXTURE_AUDIT"

def test_audit_n_scan():
    r = ckm_13d_yukawa_audit()
    assert r["n_scan_candidates"] == 25

def test_audit_epsilon_fn():
    r = ckm_13d_yukawa_audit()
    assert abs(r["epsilon_fn"] - EPSILON_FN) < 1e-12

def test_audit_pdg_sin12():
    r = ckm_13d_yukawa_audit()
    assert abs(r["pdg_sin12"] - 0.22650) < 1e-5

def test_audit_pdg_jarlskog():
    r = ckm_13d_yukawa_audit()
    assert abs(r["pdg_jarlskog"] - 3.08e-5) < 1e-8

def test_audit_interpretation_nonempty():
    r = ckm_13d_yukawa_audit()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 20

def test_audit_references():
    r = ckm_13d_yukawa_audit()
    assert isinstance(r["references"], list) and len(r["references"]) >= 3

def test_pillar_status_valid():
    assert PILLAR_STATUS in {"CLOSED", "PARTIAL_TENSION", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}

def test_summary_returns_dict():
    s = ckm_13d_summary()
    assert isinstance(s, dict)

def test_summary_pillar():
    s = ckm_13d_summary()
    assert s["pillar"] == 919

def test_summary_has_status():
    s = ckm_13d_summary()
    assert s["status"] == PILLAR_STATUS
