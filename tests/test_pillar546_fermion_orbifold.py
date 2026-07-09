# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 546 — Fermion Bulk Mass c_L Orbifold Derivation."""
from __future__ import annotations

import math
import pytest
from src.core.pillar546_fermion_orbifold_cl import (
    DELTA_C,
    K_CS,
    N_W,
    NINE_CL_VALUES,
    PI_K_R,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SECTOR_WEIGHTS,
    VERSION,
    derived_cl_nine,
    generation_ladder,
    hierarchy_derivation_status,
    mass_prediction,
    open_problems,
    orbifold_bc_constraint,
    pillar_report,
    yukawa_from_cl,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 546


def test_pillar_status():
    assert "ORBIFOLD" in PILLAR_STATUS


def test_version():
    assert VERSION == "v19.0"


# ─── Fundamental constants ───────────────────────────────────────────────────

def test_delta_c():
    assert DELTA_C == pytest.approx(5 / 74)


def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_pi_k_r():
    assert PI_K_R == pytest.approx(37.0)


# ─── Nine c_L values ─────────────────────────────────────────────────────────

def test_nine_cl_values_count():
    assert len(NINE_CL_VALUES) == 9


def test_nine_cl_fermion_names():
    expected = {"t", "c", "u", "b", "s", "d", "tau", "mu", "e"}
    assert set(NINE_CL_VALUES.keys()) == expected


def test_third_gen_cl_zero():
    # Third generation is IR-localized: c_L = 0
    for fermion in ["t", "b", "tau"]:
        assert NINE_CL_VALUES[fermion]["cl"] == pytest.approx(0.0), (
            f"{fermion}: expected c_L = 0, got {NINE_CL_VALUES[fermion]['cl']}"
        )


def test_second_gen_cl_one_delta():
    # Second generation is one lattice step from IR brane: c_L = 5/74
    for fermion in ["c", "s", "mu"]:
        assert NINE_CL_VALUES[fermion]["cl"] == pytest.approx(DELTA_C), (
            f"{fermion}: expected c_L = Δc = {DELTA_C}"
        )


def test_first_gen_cl_two_delta():
    # First generation is two lattice steps: c_L = 10/74
    for fermion in ["u", "d", "e"]:
        assert NINE_CL_VALUES[fermion]["cl"] == pytest.approx(2 * DELTA_C), (
            f"{fermion}: expected c_L = 2Δc = {2 * DELTA_C}"
        )


def test_cl_values_non_negative():
    for fermion, data in NINE_CL_VALUES.items():
        assert data["cl"] >= 0.0, f"{fermion}: c_L must be non-negative"


# ─── Sector assignments ──────────────────────────────────────────────────────

def test_up_sector_fermions():
    for f in ["t", "c", "u"]:
        assert NINE_CL_VALUES[f]["sector"] == "up_quark"


def test_down_sector_fermions():
    for f in ["b", "s", "d"]:
        assert NINE_CL_VALUES[f]["sector"] == "down_quark"


def test_lepton_sector_fermions():
    for f in ["tau", "mu", "e"]:
        assert NINE_CL_VALUES[f]["sector"] == "lepton"


# ─── Orbifold BC constraint ──────────────────────────────────────────────────

def test_orbifold_bc_valid_lattice_point():
    result = orbifold_bc_constraint(DELTA_C, z3_sector=0)
    assert result["is_allowed"] is True
    assert result["lattice_index"] == 1


def test_orbifold_bc_zero_allowed():
    result = orbifold_bc_constraint(0.0, z3_sector=0)
    # c_L = 0 is the global minimum, lattice index 0
    assert result["nearest_allowed_cl"] == pytest.approx(0.0)


def test_orbifold_bc_invalid_sector():
    with pytest.raises(ValueError):
        orbifold_bc_constraint(DELTA_C, z3_sector=3)


def test_orbifold_bc_negative_cl():
    result = orbifold_bc_constraint(-0.1)
    assert result["is_allowed"] is False


# ─── Generation ladder ───────────────────────────────────────────────────────

def test_generation_ladder_up_quark():
    ladder = generation_ladder("up_quark")
    assert len(ladder) == 3


def test_generation_ladder_third_gen_zero():
    ladder = generation_ladder("lepton")
    gen3 = [l for l in ladder if l["generation"] == 3][0]
    assert gen3["cl"] == pytest.approx(0.0)


def test_generation_ladder_spacing():
    ladder = generation_ladder("down_quark")
    cls = sorted([l["cl"] for l in ladder])
    assert cls[1] - cls[0] == pytest.approx(DELTA_C)
    assert cls[2] - cls[1] == pytest.approx(DELTA_C)


def test_generation_ladder_invalid_sector():
    with pytest.raises(ValueError):
        generation_ladder("neutrino")


# ─── Yukawa coupling ─────────────────────────────────────────────────────────

def test_yukawa_third_gen_largest():
    y_t = yukawa_from_cl(0.0, sector="up_quark")
    y_c = yukawa_from_cl(DELTA_C, sector="up_quark")
    assert y_t > y_c


def test_yukawa_exponential_suppression():
    y3 = yukawa_from_cl(0.0, sector="up_quark")
    y2 = yukawa_from_cl(DELTA_C, sector="up_quark")
    y1 = yukawa_from_cl(2 * DELTA_C, sector="up_quark")
    ratio_32 = y3 / y2
    ratio_21 = y2 / y1
    # Each step gives same exponential suppression
    assert ratio_32 == pytest.approx(ratio_21, rel=1e-6)


def test_yukawa_positive():
    for c_L in [0.0, DELTA_C, 2 * DELTA_C]:
        assert yukawa_from_cl(c_L) > 0


# ─── Mass predictions ────────────────────────────────────────────────────────

def test_mass_prediction_top_quark():
    pred = mass_prediction("t")
    assert pred["within_tolerance"] is True


def test_mass_prediction_all_return_dict():
    for fermion in NINE_CL_VALUES:
        pred = mass_prediction(fermion)
        assert "predicted_mass_gev" in pred
        assert "observed_mass_gev" in pred


def test_mass_prediction_unknown_fermion():
    with pytest.raises(KeyError):
        mass_prediction("W_boson")


# ─── Hierarchy derivation status ─────────────────────────────────────────────

def test_hierarchy_total_fermions():
    status = hierarchy_derivation_status()
    assert status["total_fermions"] == 9


def test_hierarchy_third_gen_within_tolerance():
    status = hierarchy_derivation_status()
    for f in ["t", "b", "tau"]:
        assert status["predictions"][f]["within_tolerance"] is True, (
            f"{f}: expected within_tolerance"
        )


def test_hierarchy_some_within_tolerance():
    status = hierarchy_derivation_status()
    assert status["within_1pt5_dex"] >= 3  # At minimum the 3rd-gen should pass


# ─── Open problems ───────────────────────────────────────────────────────────

def test_open_problems_count():
    assert len(open_problems()) == 4


def test_open_problems_ids():
    ids = [p["id"] for p in open_problems()]
    assert "OPC-1" in ids
    assert "OPC-4" in ids


# ─── Full report ─────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    assert report["pillar"] == 546
    assert report["toe_score_delta"] == 0.0
    assert "orbifold" in report["epistemic_delta"].lower()
    assert len(report["nine_cl_values"]) == 9
