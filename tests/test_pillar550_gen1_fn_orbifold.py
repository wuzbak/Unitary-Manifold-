# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 550 — Gen-1 FN Charge = Orbifold Winding Derivation."""
from __future__ import annotations

import math
import pytest
from src.core.pillar550_gen1_fn_orbifold import (
    DELTA_C,
    FERMION_FN_TABLE,
    FN_IDENTIFICATION,
    GEN1_CL_CANDIDATE,
    K_CS,
    K_PI_R,
    LATTICE_POSITIONS,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    fn_charge_from_lattice,
    fn_epsilon,
    fn_orbifold_consistency,
    fn_yukawa_suppression,
    gen1_derivation_status,
    mass_ratio_prediction,
    orbifold_yukawa_overlap,
    pillar_report,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 550


def test_pillar_status():
    assert "FN_ORBIFOLD" in PILLAR_STATUS


def test_version():
    assert VERSION == "v19.1"


# ─── Constants ───────────────────────────────────────────────────────────────

def test_delta_c():
    assert DELTA_C == pytest.approx(5.0 / 74.0)


def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_k_pi_r():
    assert K_PI_R == pytest.approx(37.0)


# ─── Lattice positions ───────────────────────────────────────────────────────

def test_gen3_lattice_zero():
    for f in ["t", "b", "tau"]:
        assert LATTICE_POSITIONS[f] == 0


def test_gen2_lattice_one():
    for f in ["c", "s", "mu"]:
        assert LATTICE_POSITIONS[f] == 1


def test_gen1_lattice_two():
    for f in ["u", "d", "e"]:
        assert LATTICE_POSITIONS[f] == 2


# ─── Gen-1 candidate ─────────────────────────────────────────────────────────

def test_gen1_cl_value():
    assert GEN1_CL_CANDIDATE["cl_value"] == pytest.approx(10.0 / 74.0)


def test_gen1_fn_charge():
    assert GEN1_CL_CANDIDATE["fn_charge"] == 2


def test_gen1_lattice_position():
    assert GEN1_CL_CANDIDATE["lattice_position"] == 2


def test_gen1_consistent_with_p546():
    assert GEN1_CL_CANDIDATE["consistent_with_pillar546"] is True


def test_gen1_status_candidate():
    assert GEN1_CL_CANDIDATE["status"] == "FIRST_PRINCIPLES_CANDIDATE"


# ─── FN identification ───────────────────────────────────────────────────────

def test_fn_identification_status():
    assert FN_IDENTIFICATION["status"] == "CANDIDATE — not proved"


def test_fn_blocking_assumptions_nonempty():
    assert len(FN_IDENTIFICATION["blocking_assumptions"]) >= 3


def test_fn_epsilon_identification():
    assert "Δc" in FN_IDENTIFICATION["epsilon_identification"] or \
           "n_w" in FN_IDENTIFICATION["epsilon_identification"]


# ─── fn_charge_from_lattice ──────────────────────────────────────────────────

def test_fn_charge_from_lattice_zero():
    assert fn_charge_from_lattice(0) == 0


def test_fn_charge_from_lattice_one():
    assert fn_charge_from_lattice(1) == 1


def test_fn_charge_from_lattice_two():
    assert fn_charge_from_lattice(2) == 2


# ─── fn_epsilon ──────────────────────────────────────────────────────────────

def test_fn_epsilon_value():
    assert fn_epsilon() == pytest.approx(5.0 / 74.0)


def test_fn_epsilon_positive():
    assert fn_epsilon() > 0


def test_fn_epsilon_less_than_one():
    assert fn_epsilon() < 1.0


# ─── fn_yukawa_suppression ───────────────────────────────────────────────────

def test_fn_suppression_same_charge():
    assert fn_yukawa_suppression(0, 0) == pytest.approx(1.0)
    assert fn_yukawa_suppression(2, 2) == pytest.approx(1.0)


def test_fn_suppression_delta1():
    eps = fn_epsilon()
    assert fn_yukawa_suppression(0, 1) == pytest.approx(eps)


def test_fn_suppression_delta2():
    eps = fn_epsilon()
    assert fn_yukawa_suppression(0, 2) == pytest.approx(eps ** 2)


def test_fn_suppression_symmetric():
    assert fn_yukawa_suppression(0, 1) == pytest.approx(fn_yukawa_suppression(1, 0))
    assert fn_yukawa_suppression(0, 2) == pytest.approx(fn_yukawa_suppression(2, 0))


# ─── orbifold_yukawa_overlap ─────────────────────────────────────────────────

def test_orbifold_overlap_same_position():
    assert orbifold_yukawa_overlap(0, 0) == pytest.approx(1.0)


def test_orbifold_overlap_decreases_with_separation():
    o1 = orbifold_yukawa_overlap(0, 1)
    o2 = orbifold_yukawa_overlap(0, 2)
    assert o1 > o2


def test_orbifold_overlap_positive():
    for i in range(3):
        for j in range(3):
            assert orbifold_yukawa_overlap(i, j) > 0


# ─── fn_orbifold_consistency ─────────────────────────────────────────────────

def test_fn_orbifold_consistency_keys():
    result = fn_orbifold_consistency(1, 0)
    for key in ["fn_suppression", "orbifold_overlap", "ratio_fn_over_orbifold", "consistent"]:
        assert key in result


def test_fn_orbifold_consistency_gen2_gen3():
    result = fn_orbifold_consistency(1, 0)
    # Both should be positive
    assert result["fn_suppression"] > 0
    assert result["orbifold_overlap"] > 0


def test_fn_orbifold_same_gives_ratio_1():
    result = fn_orbifold_consistency(0, 0)
    assert result["ratio_fn_over_orbifold"] == pytest.approx(1.0)


# ─── Fermion FN table ────────────────────────────────────────────────────────

def test_fermion_table_count():
    assert len(FERMION_FN_TABLE) == 9


def test_fermion_table_gen3_pillar546_derived():
    for f in ["t", "b", "tau"]:
        assert FERMION_FN_TABLE[f]["pillar546_status"] == "DERIVED"


def test_fermion_table_gen2_pillar546_derived():
    for f in ["c", "s", "mu"]:
        assert FERMION_FN_TABLE[f]["pillar546_status"] == "DERIVED"


def test_fermion_table_gen1_pillar546_natural():
    for f in ["u", "d", "e"]:
        assert FERMION_FN_TABLE[f]["pillar546_status"] == "NATURAL"


def test_fermion_table_gen1_pillar550_candidate():
    for f in ["u", "d", "e"]:
        assert "CANDIDATE" in FERMION_FN_TABLE[f]["pillar550_status"]


def test_fermion_table_cl_values():
    for f, row in FERMION_FN_TABLE.items():
        ell = row["lattice_position"]
        assert row["cl_value"] == pytest.approx(ell * DELTA_C)


# ─── gen1_derivation_status ──────────────────────────────────────────────────

def test_gen1_derivation_keys():
    status = gen1_derivation_status()
    for key in ["gen1_cl", "fn_charge", "status_pillar546", "status_pillar550",
                "identification", "advance"]:
        assert key in status


def test_gen1_status_upgraded():
    status = gen1_derivation_status()
    assert "NATURAL" in status["status_pillar546"]
    assert "CANDIDATE" in status["status_pillar550"]


def test_gen1_cl_correct():
    status = gen1_derivation_status()
    assert status["gen1_cl"] == pytest.approx(10.0 / 74.0)


# ─── mass_ratio_prediction ───────────────────────────────────────────────────

def test_mass_ratio_keys():
    pred = mass_ratio_prediction()
    for key in ["epsilon", "ratio_gen2_over_gen3_predicted",
                "ratio_gen1_over_gen3_predicted", "status"]:
        assert key in pred


def test_mass_ratio_gen2_gen3():
    pred = mass_ratio_prediction()
    eps = fn_epsilon()
    assert pred["ratio_gen2_over_gen3_predicted"] == pytest.approx(eps)


def test_mass_ratio_gen1_gen3():
    pred = mass_ratio_prediction()
    eps = fn_epsilon()
    assert pred["ratio_gen1_over_gen3_predicted"] == pytest.approx(eps ** 2)


def test_mass_ratio_status_candidate():
    pred = mass_ratio_prediction()
    assert "CANDIDATE" in pred["status"] or "ORDER" in pred["status"]


# ─── Full report ─────────────────────────────────────────────────────────────

def test_pillar_report_structure():
    report = pillar_report()
    assert report["pillar"] == 550
    assert report["parent_pillar"] == 546
    assert report["toe_score_delta"] == pytest.approx(0.0)
    assert report["adjacent_track"] is False


def test_pillar_report_epistemic_delta():
    report = pillar_report()
    assert "NATURAL" in report["epistemic_delta"]
    assert "CANDIDATE" in report["epistemic_delta"]
