# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 558 — Gen-1 c_L Derived from First Principles (AB Mechanism)."""
from __future__ import annotations

import math
import pytest
from src.core.pillar558_gen1_cl_ab_derived import (
    DELTA_C,
    FERMION_AB_TABLE,
    GEN1_CL_DERIVED,
    K_CS,
    K_PI_R,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    ab_fn_charge,
    ab_phase,
    derivation_certificate,
    fn_yukawa_from_ab,
    gen1_cl_derivation,
    mass_hierarchy_prediction,
    pillar_report,
    wilson_line_holonomy,
)

# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 558


def test_pillar_status():
    assert PILLAR_STATUS == "GEN1_CL_AHARONOV_BOHM_DERIVED"


def test_version():
    assert VERSION == "v19.2"


# ─── Constants ───────────────────────────────────────────────────────────────

def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_delta_c():
    assert abs(DELTA_C - 5/74) < 1e-12


def test_delta_c_exact():
    assert abs(DELTA_C - N_W / K_CS) < 1e-15


def test_k_pi_r():
    assert abs(K_PI_R - 37.0) < 1e-12


# ─── Wilson line holonomy ─────────────────────────────────────────────────────

def test_wilson_holonomy_gen3():
    """Gen-3 (ℓ=0): holonomy = 1 + 0j."""
    W = wilson_line_holonomy(0)
    assert abs(W - 1.0) < 1e-12


def test_wilson_holonomy_gen2():
    """Gen-2 (ℓ=1): holonomy has unit magnitude."""
    W = wilson_line_holonomy(1)
    assert abs(abs(W) - 1.0) < 1e-12


def test_wilson_holonomy_gen1():
    """Gen-1 (ℓ=2): holonomy has unit magnitude."""
    W = wilson_line_holonomy(2)
    assert abs(abs(W) - 1.0) < 1e-12


def test_wilson_holonomy_unit_magnitude():
    """All Wilson line holonomies have unit magnitude (on U(1))."""
    for ell in range(4):
        W = wilson_line_holonomy(ell)
        assert abs(abs(W) - 1.0) < 1e-12


# ─── AB phase ────────────────────────────────────────────────────────────────

def test_ab_phase_gen3():
    assert ab_phase(0) == 0.0


def test_ab_phase_gen2():
    assert abs(ab_phase(1) - 5/3) < 1e-12


def test_ab_phase_gen1():
    assert abs(ab_phase(2) - 10/3) < 1e-12


def test_ab_phase_linear_in_ell():
    """AB phase is linear in ℓ."""
    assert abs(ab_phase(2) - 2 * ab_phase(1)) < 1e-12


def test_ab_phase_formula():
    """AB phase = n_w × ℓ / 3."""
    for ell in range(5):
        assert abs(ab_phase(ell) - N_W * ell / 3) < 1e-12


# ─── FN charge from AB ───────────────────────────────────────────────────────

def test_ab_fn_charge_gen3():
    assert ab_fn_charge(0) == 0


def test_ab_fn_charge_gen2():
    assert ab_fn_charge(1) == 1


def test_ab_fn_charge_gen1():
    assert ab_fn_charge(2) == 2


def test_ab_fn_charge_equals_ell():
    """FN charge = lattice index ℓ (AB identification)."""
    for ell in range(5):
        assert ab_fn_charge(ell) == ell


# ─── FN Yukawa from AB ───────────────────────────────────────────────────────

def test_fn_yukawa_same_generation():
    """Same generation: no suppression (ε^0 = 1)."""
    assert abs(fn_yukawa_from_ab(0, 0) - 1.0) < 1e-12
    assert abs(fn_yukawa_from_ab(1, 1) - 1.0) < 1e-12
    assert abs(fn_yukawa_from_ab(2, 2) - 1.0) < 1e-12


def test_fn_yukawa_adjacent_generations():
    """Adjacent generations: suppression = Δc = 5/74."""
    assert abs(fn_yukawa_from_ab(0, 1) - DELTA_C) < 1e-12
    assert abs(fn_yukawa_from_ab(1, 2) - DELTA_C) < 1e-12


def test_fn_yukawa_gen3_to_gen1():
    """Gen-3 to gen-1: suppression = Δc² = (5/74)²."""
    expected = DELTA_C ** 2
    assert abs(fn_yukawa_from_ab(0, 2) - expected) < 1e-12


def test_fn_yukawa_symmetric():
    """Yukawa suppression is symmetric in i, j."""
    assert abs(fn_yukawa_from_ab(0, 2) - fn_yukawa_from_ab(2, 0)) < 1e-12


def test_fn_yukawa_hierarchy():
    """Y(0,0) > Y(0,1) > Y(0,2): strict hierarchy."""
    assert fn_yukawa_from_ab(0, 0) > fn_yukawa_from_ab(0, 1) > fn_yukawa_from_ab(0, 2)


# ─── Gen-1 c_L DERIVED ───────────────────────────────────────────────────────

def test_gen1_cl_value():
    expected = 2 * (5/74)
    assert abs(GEN1_CL_DERIVED["cl_value"] - expected) < 1e-12


def test_gen1_cl_exact():
    assert GEN1_CL_DERIVED["cl_exact"] == "10/74"


def test_gen1_cl_status_derived():
    assert GEN1_CL_DERIVED["status"] == "DERIVED"


def test_gen1_cl_lattice_position():
    assert GEN1_CL_DERIVED["lattice_position"] == 2


def test_gen1_fn_charge_from_ab():
    assert GEN1_CL_DERIVED["fn_charge_from_ab"] == 2


def test_gen1_cl_mechanism():
    mechanism = GEN1_CL_DERIVED["derivation_mechanism"]
    assert "Aharonov" in mechanism or "AB" in mechanism or "Wilson" in mechanism


# ─── Fermion table ───────────────────────────────────────────────────────────

def test_fermion_table_has_all_fermions():
    expected = {"t", "b", "tau", "c", "s", "mu", "u", "d", "e"}
    assert set(FERMION_AB_TABLE.keys()) == expected


def test_gen3_fermions_ell_0():
    for f in ("t", "b", "tau"):
        assert FERMION_AB_TABLE[f]["lattice_position"] == 0
        assert FERMION_AB_TABLE[f]["fn_charge_ab"] == 0


def test_gen2_fermions_ell_1():
    for f in ("c", "s", "mu"):
        assert FERMION_AB_TABLE[f]["lattice_position"] == 1
        assert FERMION_AB_TABLE[f]["fn_charge_ab"] == 1


def test_gen1_fermions_ell_2():
    for f in ("u", "d", "e"):
        assert FERMION_AB_TABLE[f]["lattice_position"] == 2
        assert FERMION_AB_TABLE[f]["fn_charge_ab"] == 2


def test_all_fermions_derived():
    for fermion, data in FERMION_AB_TABLE.items():
        assert data["pillar558_status"] == "DERIVED", f"{fermion} not DERIVED"


def test_gen1_cl_values_in_table():
    for f in ("u", "d", "e"):
        assert abs(FERMION_AB_TABLE[f]["cl_value"] - 2 * DELTA_C) < 1e-12


def test_fermion_cl_monotone():
    """Gen-3 < Gen-2 < Gen-1 c_L (further from IR = larger c_L)."""
    cl_gen3 = FERMION_AB_TABLE["t"]["cl_value"]
    cl_gen2 = FERMION_AB_TABLE["c"]["cl_value"]
    cl_gen1 = FERMION_AB_TABLE["u"]["cl_value"]
    assert cl_gen3 < cl_gen2 < cl_gen1


# ─── gen1_cl_derivation ──────────────────────────────────────────────────────

def test_derivation_overall_status():
    d = gen1_cl_derivation()
    assert d["overall_status"] == "DERIVED"


def test_derivation_has_six_steps():
    d = gen1_cl_derivation()
    assert "step1_A_y_zero_mode" in d
    assert "step2_wilson_line_quantization" in d
    assert "step3_ab_phase" in d
    assert "step4_fn_charge_identification" in d
    assert "step5_cl_formula" in d
    assert "step6_gen1_conclusion" in d


def test_derivation_step4_blocking_resolved():
    d = gen1_cl_derivation()
    step4 = d["step4_fn_charge_identification"]
    assert "resolved" in step4["blocking_assumption_resolved"].lower() or \
           "DERIVED" in step4["status"]


def test_derivation_gen1_cl():
    d = gen1_cl_derivation()
    assert abs(d["step6_gen1_conclusion"]["cl_value"] - 2 * DELTA_C) < 1e-12
    assert d["step6_gen1_conclusion"]["cl_exact"] == "10/74"


# ─── Mass hierarchy prediction ───────────────────────────────────────────────

def test_mass_hierarchy_gen3_to_gen2_ratio():
    mh = mass_hierarchy_prediction()
    expected = math.exp(-DELTA_C * K_PI_R)
    assert abs(mh["gen3_to_gen2_ratio"] - expected) < 1e-12


def test_mass_hierarchy_gen3_to_gen1_ratio():
    mh = mass_hierarchy_prediction()
    expected = math.exp(-2 * DELTA_C * K_PI_R)
    assert abs(mh["gen3_to_gen1_ratio"] - expected) < 1e-12


def test_mass_hierarchy_gen3_to_gen1_smaller_than_gen2():
    mh = mass_hierarchy_prediction()
    assert mh["gen3_to_gen1_ratio"] < mh["gen3_to_gen2_ratio"]


def test_mass_hierarchy_no_free_parameters():
    mh = mass_hierarchy_prediction()
    assert "no free parameters" in mh["note"].lower()


def test_mass_hierarchy_exponents():
    mh = mass_hierarchy_prediction()
    gen2_exp = (1 * DELTA_C - 0.5) * K_PI_R
    gen1_exp = (2 * DELTA_C - 0.5) * K_PI_R
    assert abs(mh["gen2_exponent"] - gen2_exp) < 1e-10
    assert abs(mh["gen1_exponent"] - gen1_exp) < 1e-10


# ─── Derivation certificate ──────────────────────────────────────────────────

def test_certificate_pillar():
    cert = derivation_certificate()
    assert cert["pillar"] == 558


def test_certificate_status():
    cert = derivation_certificate()
    assert cert["status"] == "GEN1_CL_AHARONOV_BOHM_DERIVED"


def test_certificate_gen1_cl():
    cert = derivation_certificate()
    assert cert["gen1_cl_exact"] == "10/74"
    assert abs(cert["gen1_cl_numeric"] - 2 * DELTA_C) < 1e-12


def test_certificate_all_generated_derived():
    cert = derivation_certificate()
    assert cert["all_generations_now_derived"] is True


def test_certificate_three_generations():
    cert = derivation_certificate()
    assert len(cert["generations"]) == 3


def test_certificate_what_claimed():
    cert = derivation_certificate()
    assert any("Q_FN" in s for s in cert["what_is_claimed"])
    assert any("10/74" in s for s in cert["what_is_claimed"])


def test_certificate_not_absolute_masses():
    cert = derivation_certificate()
    assert any("mass" in s.lower() or "absolute" in s.lower()
               for s in cert["what_is_NOT_claimed"])


# ─── Pillar report ───────────────────────────────────────────────────────────

def test_pillar_report_keys():
    r = pillar_report()
    assert r["pillar"] == 558
    assert r["status"] == "GEN1_CL_AHARONOV_BOHM_DERIVED"
    assert r["toe_score_delta"] == 0.5
    assert r["hardgate_score_delta"] == 0.5
    assert r["parent_pillar"] == 550
    assert r["closes_candidate_from"] == 550


def test_pillar_report_no_adjacent_track():
    r = pillar_report()
    assert r["adjacent_track"] is False
