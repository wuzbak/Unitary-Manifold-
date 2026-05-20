# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 302 — Two-Radius GW Moduli Stability."""
import math
import pytest
from src.core.pillar302_two_radius_gw_moduli_stability import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N1,
    N2,
    K_CS,
    PI_KR,
    U0,
    GW_EPSILON,
    ETA_BAR_N1,
    ETA_BAR_N2,
    U1_GW_MIN,
    U2_GW_MIN,
    R_RATIO,
    CONVENTION_279_3_STATUS,
    GAP_CYCLE_UNIQUENESS_STATUS,
    separation_guard,
    triangular_number,
    eta_bar,
    gw_potential_simplified,
    gw_winding_correction,
    two_radius_gw_minimum,
    radius_ordering,
    aps_cycle_assignment,
    convention_279_3_derivation,
    cycle_uniqueness_certificate,
    two_radius_report,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 302

def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

def test_convention_279_3_derived():
    assert CONVENTION_279_3_STATUS == "DERIVED"

def test_gap_closed():
    assert GAP_CYCLE_UNIQUENESS_STATUS == "CLOSED"


# ── UM constants ───────────────────────────────────────────────────────────────

def test_n1_n2():
    assert N1 == 5
    assert N2 == 7

def test_k_cs_identity():
    assert K_CS == N1**2 + N2**2

def test_pi_kr():
    assert PI_KR == 37

def test_u0():
    assert U0 == float(PI_KR)

def test_gw_epsilon_small():
    assert 0 < GW_EPSILON < 0.1


# ── APS eta-bar invariants ─────────────────────────────────────────────────────

def test_eta_bar_n1():
    # η̄(5) = T(5)/2 mod 1 = 15/2 mod 1 = 0.5
    assert ETA_BAR_N1 == pytest.approx(0.5)

def test_eta_bar_n2():
    # η̄(7) = T(7)/2 mod 1 = 28/2 mod 1 = 0.0
    assert ETA_BAR_N2 == pytest.approx(0.0)

def test_eta_bar_n1_nontrivial():
    # η̄(5) ≠ 0 is the Z₂-non-trivial condition
    assert ETA_BAR_N1 != 0.0

def test_eta_bar_n2_trivial():
    assert ETA_BAR_N2 == 0.0


# ── Two-radius GW minimum ──────────────────────────────────────────────────────

def test_u1_u2_positive():
    assert U1_GW_MIN > 0
    assert U2_GW_MIN > 0

def test_u2_less_than_u1():
    # n=7 (more winding) → smaller kR (more winding tension)
    assert U2_GW_MIN < U1_GW_MIN

def test_r_ratio_less_than_one():
    # R(n=7)/R(n=5) < 1
    assert R_RATIO < 1.0

def test_r_ratio_positive():
    assert R_RATIO > 0


# ── triangular_number ──────────────────────────────────────────────────────────

def test_T5():
    assert triangular_number(5) == 15

def test_T7():
    assert triangular_number(7) == 28

def test_T_formula():
    for n in range(1, 10):
        assert triangular_number(n) == n * (n + 1) // 2


# ── eta_bar ────────────────────────────────────────────────────────────────────

def test_eta_bar_5():
    assert eta_bar(5) == pytest.approx(0.5)

def test_eta_bar_7():
    assert eta_bar(7) == pytest.approx(0.0)

def test_eta_bar_range():
    for n in range(1, 20):
        eb = eta_bar(n)
        assert eb in (0.0, 0.5)


# ── gw_potential_simplified ────────────────────────────────────────────────────

def test_gw_potential_positive():
    assert gw_potential_simplified(37.0, 0.01) > 0

def test_gw_potential_invalid_u():
    with pytest.raises(ValueError):
        gw_potential_simplified(0.0, 0.01)

def test_gw_potential_decreases_with_epsilon():
    v1 = gw_potential_simplified(37.0, 0.01)
    v2 = gw_potential_simplified(37.0, 0.05)
    # Larger epsilon → stronger decay → smaller potential at same u
    assert v2 < v1


# ── gw_winding_correction ──────────────────────────────────────────────────────

def test_winding_correction_positive():
    assert gw_winding_correction(5, 37.0, 0.01) > 0

def test_winding_correction_n2_larger():
    c1 = gw_winding_correction(5, 37.0, 0.01)
    c2 = gw_winding_correction(7, 37.0, 0.01)
    assert c2 > c1  # n=7 has larger correction

def test_winding_correction_monotone_n():
    for n1, n2 in [(3, 5), (5, 7), (7, 9)]:
        c1 = gw_winding_correction(n1, 37.0, 0.01)
        c2 = gw_winding_correction(n2, 37.0, 0.01)
        assert c2 > c1


# ── two_radius_gw_minimum ──────────────────────────────────────────────────────

def test_two_radius_returns_tuple():
    u1, u2 = two_radius_gw_minimum(5, 7)
    assert u1 > 0
    assert u2 > 0

def test_two_radius_ordering():
    u1, u2 = two_radius_gw_minimum(5, 7)
    # n=5 has larger kR (less winding correction)
    assert u1 > u2

def test_two_radius_consistency():
    # Manual check
    u1, u2 = two_radius_gw_minimum(5, 7, U0, GW_EPSILON)
    assert abs(u1 - U1_GW_MIN) < 1e-10
    assert abs(u2 - U2_GW_MIN) < 1e-10


# ── radius_ordering ────────────────────────────────────────────────────────────

def test_radius_ordering_returns_dict():
    r = radius_ordering(N1, N2)
    assert isinstance(r, dict)

def test_radius_ordering_n2_shorter_kR():
    r = radius_ordering(5, 7)
    assert r["shorter_kR_cycle_n"] == 7

def test_radius_ordering_n1_longer_kR():
    r = radius_ordering(5, 7)
    assert r["longer_kR_cycle_n"] == 5

def test_radius_ordering_ratio_less_one():
    r = radius_ordering(5, 7)
    assert r["r_ratio_u2_over_u1"] < 1.0

def test_radius_ordering_aps_nontrivial_n1():
    r = radius_ordering(5, 7)
    assert r["braid_short_is_aps_nontrivial"] is True


# ── aps_cycle_assignment ───────────────────────────────────────────────────────

def test_aps_returns_dict():
    a = aps_cycle_assignment()
    assert isinstance(a, dict)

def test_aps_primary_is_n1():
    a = aps_cycle_assignment(5, 7)
    assert a["aps_primary_n_w"] == 5

def test_aps_secondary_is_n2():
    a = aps_cycle_assignment(5, 7)
    assert a["aps_secondary_n_m"] == 7

def test_aps_etabar_n1():
    a = aps_cycle_assignment(5, 7)
    assert a["etabar_n1"] == pytest.approx(0.5)

def test_aps_etabar_n2():
    a = aps_cycle_assignment(5, 7)
    assert a["etabar_n2"] == pytest.approx(0.0)

def test_aps_z2_odd_phase_n1():
    a = aps_cycle_assignment(5, 7)
    # k_CS(5) × η̄(5) = 74 × 0.5 = 37 (ODD)
    assert a["z2_odd_cs_phase_n1_odd"] is True


# ── convention_279_3_derivation ────────────────────────────────────────────────

def test_derivation_returns_dict():
    d = convention_279_3_derivation()
    assert isinstance(d, dict)

def test_derivation_status_derived():
    d = convention_279_3_derivation()
    assert d["current_status"] == "DERIVED"

def test_derivation_gap_closed():
    d = convention_279_3_derivation()
    assert d["gap_cycle_radion_coupling_uniqueness"] == "CLOSED"

def test_derivation_gw_aps_agreement():
    d = convention_279_3_derivation()
    assert d["gw_aps_agreement"] is True

def test_derivation_chain_length():
    d = convention_279_3_derivation()
    assert len(d["derivation_chain"]) >= 5

def test_derivation_closing_statement():
    d = convention_279_3_derivation()
    assert "DERIVED" in d["closing_statement"]
    assert "CLOSED" in d["closing_statement"]


# ── cycle_uniqueness_certificate ───────────────────────────────────────────────

def test_cert_returns_dict():
    cert = cycle_uniqueness_certificate()
    assert isinstance(cert, dict)

def test_cert_type():
    cert = cycle_uniqueness_certificate()
    assert cert["certificate_type"] == "GAP_CLOSURE_CERTIFICATE"

def test_cert_gap_name():
    cert = cycle_uniqueness_certificate()
    assert cert["gap_name"] == "CYCLE_RADION_COUPLING_UNIQUENESS"

def test_cert_new_status_derived():
    cert = cycle_uniqueness_certificate()
    assert cert["new_status"] == "DERIVED"

def test_cert_closure_stamp_final():
    cert = cycle_uniqueness_certificate()
    assert "FINAL" in cert["closure_stamp"]

def test_cert_aps_primary():
    cert = cycle_uniqueness_certificate()
    assert cert["aps_primary"] == 5

def test_cert_gw_shorter_n2():
    cert = cycle_uniqueness_certificate()
    assert cert["gw_shorter_kR_n"] == 7

def test_cert_z2_odd_satisfied_by_n1():
    cert = cycle_uniqueness_certificate()
    assert cert["z2_odd_cs_phase_satisfied_by"] == 5


# ── two_radius_report ──────────────────────────────────────────────────────────

def test_report_returns_string():
    r = two_radius_report()
    assert isinstance(r, str)

def test_report_contains_derived():
    r = two_radius_report()
    assert "DERIVED" in r

def test_report_contains_closed():
    r = two_radius_report()
    assert "CLOSED" in r

def test_report_contains_final():
    r = two_radius_report()
    assert "FINAL" in r
