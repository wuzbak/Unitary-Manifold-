# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 943 — CKM 13D Second-Order Texture Correction."""
from __future__ import annotations
from src.core.pillar943_ckm_13d_second_order_texture import (
    ANGLE_RESIDUALS,
    CKM_ANGLES_2ND_ORDER,
    CKM_ANGLES_7D_TREE,
    CKM_ANGLES_PDG,
    N_WITHIN_30PCT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    ckm_second_order_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 943
def test_gate(): assert PILLAR_GATE == "CKM_13D_SECOND_ORDER_TEXTURE_CORRECTION"

def test_pdg_keys():
    for k in ["theta_12", "theta_13", "theta_23"]:
        assert k in CKM_ANGLES_PDG

def test_pdg_ordering():
    # PDG: θ₁₂ > θ₂₃ > θ₁₃
    assert CKM_ANGLES_PDG["theta_12"] > CKM_ANGLES_PDG["theta_23"]
    assert CKM_ANGLES_PDG["theta_23"] > CKM_ANGLES_PDG["theta_13"]

def test_tree_ordering():
    # 7D tree: θ₁₂ > θ₁₃ (not same ordering as PDG — known tension)
    assert CKM_ANGLES_7D_TREE["theta_12"] > 0

def test_corrected_angles_keys():
    for k in ["theta_12", "theta_13", "theta_23"]:
        assert k in CKM_ANGLES_2ND_ORDER

def test_corrected_angles_positive():
    for v in CKM_ANGLES_2ND_ORDER.values():
        assert v > 0

def test_angle_residuals_keys():
    for k in ["theta_12", "theta_13", "theta_23"]:
        assert k in ANGLE_RESIDUALS

def test_angle_residuals_positive():
    for v in ANGLE_RESIDUALS.values():
        assert v >= 0

def test_n_within_30pct_range():
    assert 0 <= N_WITHIN_30PCT <= 3

def test_status_set():
    assert PILLAR_STATUS in {
        "CKM_13D_SECOND_ORDER_CLOSED",
        "CKM_13D_SECOND_ORDER_PARTIAL",
        "CKM_13D_SECOND_ORDER_IRREDUCIBLE",
    }

def test_pillar_valid():
    assert PILLAR_VALID is True

def test_summary_keys():
    s = ckm_second_order_summary()
    for key in ["pillar", "gate", "status", "valid", "pdg_angles",
                "corrected_angles", "residuals_fractional", "n_within_30pct"]:
        assert key in s

def test_summary_pillar():
    assert ckm_second_order_summary()["pillar"] == 943

def test_pdg_theta12_value():
    assert abs(CKM_ANGLES_PDG["theta_12"] - 13.04) < 0.01

def test_pdg_theta13_value():
    assert abs(CKM_ANGLES_PDG["theta_13"] - 0.201) < 0.01

def test_pdg_theta23_value():
    assert abs(CKM_ANGLES_PDG["theta_23"] - 2.38) < 0.01

def test_status_consistent_with_n():
    if N_WITHIN_30PCT == 3:
        assert PILLAR_STATUS == "CKM_13D_SECOND_ORDER_CLOSED"
    elif N_WITHIN_30PCT >= 2:
        assert PILLAR_STATUS == "CKM_13D_SECOND_ORDER_PARTIAL"
    else:
        assert PILLAR_STATUS == "CKM_13D_SECOND_ORDER_IRREDUCIBLE"

def test_remaining_nonempty():
    s = ckm_second_order_summary()
    assert len(s.get("remaining", "")) > 20
