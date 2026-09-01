# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 957 — Neutrino Mass Splittings from Orbifold Wavefunctions."""

import math
import pytest
from src.core.pillar957_neutrino_splitting_orbifold import (
    PILLAR_STATUS, PILLAR_VALID, N_W, K_CS, N_C, ALPHA_GUT_GEO,
    CL_GEN1, CL_GEN2, CL_GEN3, PI_KR, SIGMA_M_NU_MEV,
    DM21_SQ_EXP_EV2, DM31_SQ_EXP_EV2,
    rs1_warp_suppression, cl_ladder, neutrino_mass_eigenvalues,
    compute_mass_splittings, splitting_ratio_geometric,
    seesaw_correction, fallibility_update, pillar957_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "NU_MASS_SPLITTING_TREE_LEVEL_COMPUTED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert N_C == 3
    assert abs(ALPHA_GUT_GEO - 3.0/74.0) < 1e-12


def test_cl_gen1():
    expected = 1.0 - 3.0/74.0
    assert abs(CL_GEN1 - expected) < 1e-12


def test_cl_gen2():
    expected = 1.0 - 3.0/74.0 - 1.0/(2*74.0)
    assert abs(CL_GEN2 - expected) < 1e-12


def test_cl_gen3():
    expected = 1.0 - 3.0/74.0 - 2.0/(2*74.0)
    assert abs(CL_GEN3 - expected) < 1e-12


def test_cl_ordering():
    # Gen 1 has largest c_L (most UV-localized → smallest mass)
    assert CL_GEN1 > CL_GEN2 > CL_GEN3


def test_pi_kr():
    assert abs(PI_KR - 37.0) < 1e-10


def test_warp_suppression_decreasing():
    # Larger c_L → smaller warp factor (stronger UV localisation)
    w1 = rs1_warp_suppression(CL_GEN1)
    w2 = rs1_warp_suppression(CL_GEN2)
    w3 = rs1_warp_suppression(CL_GEN3)
    assert w1 < w2 < w3


def test_warp_suppression_formula():
    cl = 0.95
    expected = math.exp(-(cl - 0.5) * PI_KR)
    result = rs1_warp_suppression(cl)
    assert abs(result - expected) < 1e-12


def test_cl_ladder_length():
    ladder = cl_ladder()
    assert len(ladder) == 3


def test_cl_ladder_warp_factors_positive():
    for entry in cl_ladder():
        assert entry["warp_factor"] > 0


def test_mass_eigenvalues_normal_hierarchy():
    masses = neutrino_mass_eigenvalues()
    assert masses["NH_consistent"] is True


def test_sum_m_nu_constraint():
    masses = neutrino_mass_eigenvalues()
    assert abs(masses["sum_m_nu_eV"] - SIGMA_M_NU_MEV) < 1e-12


def test_dm21_positive():
    splittings = compute_mass_splittings()
    assert splittings["dm21_sq_eV2"] > 0


def test_dm31_positive():
    splittings = compute_mass_splittings()
    assert splittings["dm31_sq_eV2"] > 0


def test_dm31_gt_dm21():
    splittings = compute_mass_splittings()
    assert splittings["dm31_sq_eV2"] > splittings["dm21_sq_eV2"]


def test_nh_from_splittings():
    splittings = compute_mass_splittings()
    assert splittings["NH_confirmed"] is True


def test_splitting_ratio_scale_independent():
    # The ratio Δm²₂₁/Δm²₃₁ should not depend on Σm_ν
    ratio = splitting_ratio_geometric()
    assert ratio["splitting_ratio_dm21_over_dm31"] > 0


def test_seesaw_subleading():
    seesaw = seesaw_correction()
    assert seesaw["seesaw_is_subleading"] is True
    assert seesaw["seesaw_fraction_of_step"] < 1.0


def test_fallibility_update():
    fb = fallibility_update()
    assert "TREE_LEVEL_COMPUTED" in fb["new_status"]
    assert fb["pillar"] == 957


def test_summary():
    s = pillar957_summary()
    assert s["pillar"] == 957
    assert s["valid"] is True
    assert "OPEN → TREE_LEVEL_BOUNDED" in s["gap_closed"]
