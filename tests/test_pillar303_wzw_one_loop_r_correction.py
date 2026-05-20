# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 303 — WZW One-Loop r Correction."""
import math
import pytest
from src.core.pillar303_wzw_one_loop_r_correction import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N1,
    N2,
    K_CS,
    RHO_BRAID,
    C_S_TREE,
    R_BARE,
    R_LO,
    DELTA_LOOP,
    RHO_EFF_NLO,
    C_S_NLO,
    R_NLO,
    ACT_DR6_R_LIMIT_95CL,
    ACT_DR6_STATUS,
    LOOPS_NEEDED_FOR_ACT,
    separation_guard,
    kinetic_mixing_rho,
    tree_level_sound_speed,
    one_loop_delta,
    rho_eff_nlo,
    c_s_nlo,
    r_nlo,
    nloop_r,
    loops_needed_to_reach_r,
    act_dr6_tension_certificate,
    wzw_loop_correction_report,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 303

def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

def test_act_dr6_status_irreducible():
    assert "IRREDUCIBLE" in ACT_DR6_STATUS


# ── Core constants ─────────────────────────────────────────────────────────────

def test_n1_n2():
    assert N1 == 5
    assert N2 == 7

def test_k_cs():
    assert K_CS == 74

def test_rho_braid():
    expected = 2.0 * 5 * 7 / 74
    assert RHO_BRAID == pytest.approx(expected, rel=1e-10)

def test_rho_braid_less_than_one():
    assert 0 < RHO_BRAID < 1

def test_c_s_tree_12_37():
    expected = 12.0 / 37.0
    # c_s = sqrt(1 - ρ²) should be close to 12/37
    assert C_S_TREE == pytest.approx(expected, rel=1e-3)

def test_r_lo_canonical():
    assert R_LO == pytest.approx(0.0315, rel=1e-6)

def test_act_dr6_limit():
    assert ACT_DR6_R_LIMIT_95CL == pytest.approx(0.016, rel=1e-6)


# ── NLO correction constants ───────────────────────────────────────────────────

def test_delta_loop_formula():
    expected = (RHO_BRAID / (4.0 * math.pi)) ** 2
    assert DELTA_LOOP == pytest.approx(expected, rel=1e-10)

def test_delta_loop_small():
    # Perturbative: δ_loop ≪ 1
    assert DELTA_LOOP < 0.01

def test_rho_eff_nlo_smaller():
    # NLO kinetic mixing < tree-level
    assert RHO_EFF_NLO < RHO_BRAID

def test_c_s_nlo_positive():
    assert C_S_NLO > 0

def test_r_nlo_less_than_lo():
    # NLO r < LO r (loop correction reduces r)
    assert R_NLO < R_LO

def test_r_nlo_sub_percent_shift():
    shift_pct = abs(R_NLO - R_LO) / R_LO * 100
    assert shift_pct < 1.0  # sub-percent

def test_r_nlo_still_above_act():
    # Even at NLO, r > ACT DR6 limit
    assert R_NLO > ACT_DR6_R_LIMIT_95CL

def test_loops_needed_large():
    # Needs ~87 loops to reach ACT limit — far beyond perturbativity
    assert LOOPS_NEEDED_FOR_ACT > 50


# ── separation_guard ───────────────────────────────────────────────────────────

def test_separation_guard_pillar():
    g = separation_guard()
    assert g["pillar"] == 303

def test_separation_guard_not_hardgate():
    g = separation_guard()
    assert g["is_hardgate"] is False

def test_separation_guard_closes_gap():
    g = separation_guard()
    assert "WZW_LOOP_CAVEAT" in g["closes_gap"]

def test_separation_guard_certifies():
    g = separation_guard()
    assert "ACT_DR6" in g["certifies"]


# ── kinetic_mixing_rho ────────────────────────────────────────────────────────

def test_rho_5_7_74():
    rho = kinetic_mixing_rho(5, 7, 74)
    assert rho == pytest.approx(70.0 / 74.0, rel=1e-10)

def test_rho_range():
    for n1, n2, k in [(3, 5, 34), (5, 7, 74), (7, 9, 130)]:
        rho = kinetic_mixing_rho(n1, n2, k)
        assert 0 < rho < 1


# ── tree_level_sound_speed ────────────────────────────────────────────────────

def test_c_s_formula():
    rho = 70.0 / 74.0
    cs = tree_level_sound_speed(rho)
    assert cs == pytest.approx(math.sqrt(1 - rho**2), rel=1e-10)

def test_c_s_invalid_rho():
    with pytest.raises(ValueError):
        tree_level_sound_speed(1.5)

def test_c_s_zero_rho():
    cs = tree_level_sound_speed(0.0)
    assert cs == pytest.approx(1.0)


# ── one_loop_delta ─────────────────────────────────────────────────────────────

def test_delta_formula():
    rho = RHO_BRAID
    delta = one_loop_delta(rho)
    expected = (rho / (4 * math.pi)) ** 2
    assert delta == pytest.approx(expected, rel=1e-10)

def test_delta_small():
    assert one_loop_delta(RHO_BRAID) < 0.01

def test_delta_positive():
    assert one_loop_delta(0.5) > 0


# ── rho_eff_nlo ────────────────────────────────────────────────────────────────

def test_rho_eff_less_than_tree():
    rho_eff = rho_eff_nlo(RHO_BRAID)
    assert rho_eff < RHO_BRAID

def test_rho_eff_formula():
    rho = RHO_BRAID
    delta = one_loop_delta(rho)
    expected = rho * (1.0 - delta)
    assert rho_eff_nlo(rho) == pytest.approx(expected, rel=1e-10)


# ── c_s_nlo ───────────────────────────────────────────────────────────────────

def test_c_s_nlo_slightly_larger():
    # Reduced rho_eff → slightly larger c_s
    assert c_s_nlo(RHO_BRAID) > C_S_TREE

def test_c_s_nlo_positive():
    assert c_s_nlo(RHO_BRAID) > 0


# ── r_nlo ─────────────────────────────────────────────────────────────────────

def test_r_nlo_formula():
    r = r_nlo(R_LO, RHO_BRAID)
    delta = one_loop_delta(RHO_BRAID)
    expected = R_LO * (1.0 - delta)
    assert r == pytest.approx(expected, rel=1e-10)

def test_r_nlo_less_than_lo():
    r = r_nlo(0.0315, RHO_BRAID)
    assert r < 0.0315

def test_r_nlo_sub_percent():
    lo = 0.0315
    nlo = r_nlo(lo, RHO_BRAID)
    pct = abs(nlo - lo) / lo * 100
    assert pct < 1.0


# ── nloop_r ────────────────────────────────────────────────────────────────────

def test_nloop_r_1_loop():
    r1 = nloop_r(R_LO, RHO_BRAID, 1)
    assert abs(r1 - R_NLO) < 1e-10

def test_nloop_r_monotone():
    for n1, n2 in [(1, 2), (2, 5), (5, 10)]:
        r1 = nloop_r(R_LO, RHO_BRAID, n1)
        r2 = nloop_r(R_LO, RHO_BRAID, n2)
        assert r2 < r1

def test_nloop_r_breakdown():
    with pytest.raises(ValueError):
        nloop_r(R_LO, RHO_BRAID, 200)  # 200 loops: N × δ > 1


# ── loops_needed_to_reach_r ────────────────────────────────────────────────────

def test_loops_to_act_large():
    n = loops_needed_to_reach_r(R_LO, RHO_BRAID, ACT_DR6_R_LIMIT_95CL)
    assert n > 50

def test_loops_to_lo_itself_zero():
    n = loops_needed_to_reach_r(R_LO, RHO_BRAID, R_LO)
    assert n == 0.0

def test_loops_to_larger_target_zero():
    n = loops_needed_to_reach_r(R_LO, RHO_BRAID, R_LO + 0.01)
    assert n == 0.0


# ── act_dr6_tension_certificate ────────────────────────────────────────────────

def test_cert_returns_dict():
    cert = act_dr6_tension_certificate()
    assert isinstance(cert, dict)

def test_cert_type():
    cert = act_dr6_tension_certificate()
    assert cert["certificate_type"] == "IRREDUCIBILITY_CERTIFICATE"

def test_cert_gap_closed():
    cert = act_dr6_tension_certificate()
    assert cert["gap_closed"] == "WZW_LOOP_CAVEAT_PILLAR97B"

def test_cert_wzw_closed():
    cert = act_dr6_tension_certificate()
    assert cert["wzw_loop_caveat_closed"] is True

def test_cert_still_high_tension():
    cert = act_dr6_tension_certificate()
    assert cert["act_dr6_still_high_tension_at_nlo"] is True

def test_cert_r_nlo():
    cert = act_dr6_tension_certificate()
    assert cert["r_nlo"] == pytest.approx(R_NLO, rel=1e-6)

def test_cert_delta_loop():
    cert = act_dr6_tension_certificate()
    assert cert["delta_loop"] == pytest.approx(DELTA_LOOP, rel=1e-6)

def test_cert_closure_stamp_final():
    cert = act_dr6_tension_certificate()
    assert "FINAL" in cert["closure_stamp"]

def test_cert_r_nlo_shift_sub_percent():
    cert = act_dr6_tension_certificate()
    assert cert["r_nlo_shift_pct"] < 1.0

def test_cert_loops_above_50():
    cert = act_dr6_tension_certificate()
    assert cert["loops_needed_to_reach_act_limit"] > 50


# ── wzw_loop_correction_report ────────────────────────────────────────────────

def test_report_returns_string():
    r = wzw_loop_correction_report()
    assert isinstance(r, str)

def test_report_contains_nlo():
    r = wzw_loop_correction_report()
    assert "NLO" in r or "1-loop" in r or "one-loop" in r.lower()

def test_report_contains_act():
    r = wzw_loop_correction_report()
    assert "ACT" in r

def test_report_contains_irreducible():
    r = wzw_loop_correction_report()
    assert "IRREDUCIBLE" in r

def test_report_contains_final():
    r = wzw_loop_correction_report()
    assert "FINAL" in r
