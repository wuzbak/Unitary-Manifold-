# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 282 — Convention 279.3 Derivation from Radion / GW Ground-State Braid."""
from __future__ import annotations

import math
import pytest

from src.core.pillar282_convention279_3_radion_derivation import (
    ADJACENCY_TRACK_LABEL,
    K_CS,
    MW,
    NW,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    KR_C,
    convention_279_3_derivation_certificate,
    ground_state_braid_scan,
    ground_state_braid_theorem_282_1,
    kk_mass_squared_braid,
    pillar282_report,
    remaining_soft_residual,
    separation_guard,
    uv_brane_anisotropy_ratio,
    uv_brane_anisotropy_theorem_282_2,
)


# ---------------------------------------------------------------------------
# Identity and metadata
# ---------------------------------------------------------------------------

def test_pillar_identity():
    assert PILLAR_NUMBER == 282
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_canonical_constants():
    assert K_CS == 74
    assert NW == 5
    assert MW == 7
    assert NW ** 2 + MW ** 2 == K_CS
    assert KR_C == 37.0


def test_separation_guard():
    g = separation_guard()
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
    assert g["derives_convention_279_3_from_first_principles"] is True
    assert g["upgrades_pillar_279_residual"] is True


# ---------------------------------------------------------------------------
# kk_mass_squared_braid
# ---------------------------------------------------------------------------

def test_kk_mass_squared_basic():
    # n=5 on R1=1, m=7 on R2=2: m² = 25/1 + 49/4 = 25 + 12.25 = 37.25
    result = kk_mass_squared_braid(5, 7, R1=1.0, R2=2.0)
    assert abs(result - (25.0 / 1.0 + 49.0 / 4.0)) < 1.0e-12


def test_kk_mass_squared_symmetric():
    # Equal radii → m²(5,7) ≠ m²(7,5) only if R1 ≠ R2
    m2_sym_57 = kk_mass_squared_braid(5, 7, R1=1.0, R2=1.0)
    m2_sym_75 = kk_mass_squared_braid(7, 5, R1=1.0, R2=1.0)
    assert abs(m2_sym_57 - m2_sym_75) < 1.0e-12  # equal when R1 = R2 and K_CS symmetric


def test_kk_mass_squared_validation():
    with pytest.raises(ValueError):
        kk_mass_squared_braid(5, 7, R1=-1.0, R2=2.0)
    with pytest.raises(ValueError):
        kk_mass_squared_braid(5, 7, R1=1.0, R2=0.0)
    with pytest.raises(ValueError):
        kk_mass_squared_braid(-1, 7, R1=1.0, R2=2.0)


# ---------------------------------------------------------------------------
# Theorem 282.1 — Ground-State Braid (exact)
# ---------------------------------------------------------------------------

def test_theorem_282_1_canonical():
    """Main result: n_w=5 on R1=1 < R2=2 is the ground state."""
    cert = ground_state_braid_theorem_282_1(n=5, m=7, R1=1.0, R2=2.0)
    assert cert["theorem_holds"] is True
    assert cert["delta_m2_A_minus_B"] < 0.0
    assert cert["analytic_consistent"] is True
    assert cert["ground_state"] == "ASSIGNMENT_A_SMALLER_N_ON_SHORT_CYCLE"


def test_theorem_282_1_analytic_formula():
    """Verify the exact algebraic formula Δ = (n²-m²)(1/R₁²-1/R₂²)."""
    n, m, R1, R2 = 5, 7, 1.0, 3.0
    cert = ground_state_braid_theorem_282_1(n=n, m=m, R1=R1, R2=R2)
    expected_delta = (n ** 2 - m ** 2) * (1.0 / R1 ** 2 - 1.0 / R2 ** 2)
    assert abs(cert["delta_analytic"] - expected_delta) < 1.0e-12
    assert abs(cert["delta_m2_A_minus_B"] - expected_delta) < 1.0e-12


def test_theorem_282_1_requires_R1_lt_R2():
    with pytest.raises(ValueError):
        ground_state_braid_theorem_282_1(n=5, m=7, R1=2.0, R2=1.0)
    with pytest.raises(ValueError):
        ground_state_braid_theorem_282_1(n=5, m=7, R1=1.0, R2=1.0)


def test_theorem_282_1_requires_n_lt_m():
    with pytest.raises(ValueError):
        ground_state_braid_theorem_282_1(n=7, m=5, R1=1.0, R2=2.0)


def test_theorem_282_1_various_ratios():
    """Theorem holds for all R2/R1 > 1."""
    for ratio in (1.01, 1.1, 1.5, 2.0, 5.0, 10.0, 7.0 / 5.0):
        cert = ground_state_braid_theorem_282_1(n=5, m=7, R1=1.0, R2=ratio)
        assert cert["theorem_holds"] is True, f"Theorem failed at R2/R1={ratio}"


def test_ground_state_braid_scan():
    """Scan confirms theorem holds for all tested ratios."""
    results = ground_state_braid_scan()
    assert len(results) >= 4
    for r in results:
        assert r["theorem_holds"] is True
        assert r["delta_m2"] < 0.0


# ---------------------------------------------------------------------------
# Theorem 282.2 — UV-Brane Anisotropy
# ---------------------------------------------------------------------------

def test_uv_brane_anisotropy_ratio_default():
    """Default coefficients give R2/R1 > 1."""
    ratio = uv_brane_anisotropy_ratio()
    assert ratio > 1.0


def test_uv_brane_anisotropy_ratio_symmetric():
    """With c_brane = 0, the ratio should be 1 (symmetric point)."""
    ratio = uv_brane_anisotropy_ratio(c_uv=1.0, c_brane=0.0)
    assert abs(ratio - 1.0) < 1.0e-10


def test_uv_brane_anisotropy_ratio_monotone():
    """Larger c_brane → larger R2/R1."""
    r0 = uv_brane_anisotropy_ratio(c_uv=1.0, c_brane=0.0)
    r1 = uv_brane_anisotropy_ratio(c_uv=1.0, c_brane=0.3)
    r2 = uv_brane_anisotropy_ratio(c_uv=1.0, c_brane=0.6)
    assert r0 <= r1 <= r2


def test_uv_brane_anisotropy_ratio_validation():
    with pytest.raises(ValueError):
        uv_brane_anisotropy_ratio(c_uv=0.0, c_brane=0.5)
    with pytest.raises(ValueError):
        uv_brane_anisotropy_ratio(c_uv=-1.0, c_brane=0.5)
    with pytest.raises(ValueError):
        uv_brane_anisotropy_ratio(c_uv=1.0, c_brane=-0.1)


def test_uv_brane_anisotropy_theorem_282_2_default():
    cert = uv_brane_anisotropy_theorem_282_2()
    assert cert["theorem_holds"] is True
    assert cert["R2_over_R1"] > 1.0
    assert cert["derivation_status"] == "DERIVED_CONDITIONAL"
    assert "UV-brane" in cert["conditional_on"]


def test_uv_brane_anisotropy_no_hardgate_drift():
    cert = uv_brane_anisotropy_theorem_282_2()
    assert "c_brane > 0" in cert["conditional_on"]
    assert "C_BRANE_FROM_5D_ACTION" in cert["residual"]


# ---------------------------------------------------------------------------
# Convention 279.3 full derivation certificate
# ---------------------------------------------------------------------------

def test_convention_279_3_certificate_structure():
    cert = convention_279_3_derivation_certificate()
    assert cert["pillar"] == 282
    assert cert["K_CS"] == 74
    assert cert["n_w_selected"] == 5
    assert cert["m_w_selected"] == 7
    assert cert["convention_derived"] is True
    assert cert["planck_data_used"] is False


def test_convention_279_3_residual_upgrade():
    cert = convention_279_3_derivation_certificate()
    upgrade = cert["pillar_279_residual_upgrade"]
    assert "SHORT_LONG_CYCLE_ASSIGNMENT_DERIVATION" in upgrade["before"]
    assert "C_BRANE_FROM_5D_ACTION" in upgrade["after"]
    assert "SOFT OPEN" in upgrade["after"]
    assert "qualitative" in upgrade["nature_of_upgrade"].lower() or "soft" in upgrade["nature_of_upgrade"].lower()


def test_convention_279_3_certificate_requires_R2_gt_R1():
    with pytest.raises(ValueError):
        convention_279_3_derivation_certificate(R2_over_R1=0.9)


# ---------------------------------------------------------------------------
# Remaining soft residual
# ---------------------------------------------------------------------------

def test_remaining_soft_residual_structure():
    r = remaining_soft_residual()
    assert r["id"] == "C_BRANE_FROM_5D_ACTION"
    assert "SOFT_OPEN" in r["nature"]
    assert "cannot reverse" in r["impact_on_n_w_selection"].lower()


def test_remaining_soft_residual_not_qualitative_blocker():
    r = remaining_soft_residual()
    # Confirm the soft residual cannot reverse n_w = 5 selection
    assert "Zero" in r["impact_on_n_w_selection"] or "cannot reverse" in r["impact_on_n_w_selection"]


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def test_pillar282_report_structure():
    report = pillar282_report()
    assert report["pillar"] == 282
    assert report["certificate"]["convention_derived"] is True
    assert len(report["ground_state_braid_scan"]) >= 4
    assert all(s["theorem_holds"] for s in report["ground_state_braid_scan"])
    assert report["remaining_soft_residual"]["id"] == "C_BRANE_FROM_5D_ACTION"


def test_pillar282_report_no_hardgate_drift():
    report = pillar282_report()
    g = report["separation_guard"]
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
