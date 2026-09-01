# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 955 — SU(3) Kawamura Matrix from UM Z₂ CS Boundary Phase."""

import math
import pytest
from src.core.pillar955_su3_kawamura_cs_derivation import (
    PILLAR_STATUS, PILLAR_VALID, K_CS, N_W, N_2, ETA_BAR_NW5, CS_BOUNDARY_PRODUCT,
    KAWAMURA_EIGENVALUES, SU5_DIM, SM_GENERATORS, XY_GENERATORS,
    cs_boundary_product, su5_generator_cs_phases, derive_kawamura_matrix_from_cs_phase,
    su5_breaking_spectrum, cs_boundary_uniqueness_proof, fallibility_update,
    pillar955_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "SU3_KAWAMURA_DERIVED_FROM_CS_BOUNDARY"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_k_cs_value():
    assert K_CS == 74


def test_n_w_value():
    assert N_W == 5


def test_eta_bar():
    assert abs(ETA_BAR_NW5 - 0.5) < 1e-10


def test_cs_boundary_product_value():
    assert CS_BOUNDARY_PRODUCT == 37


def test_cs_boundary_product_is_odd():
    assert CS_BOUNDARY_PRODUCT % 2 == 1


def test_cs_boundary_product_equals_k_cs_times_eta_bar():
    assert abs(K_CS * ETA_BAR_NW5 - CS_BOUNDARY_PRODUCT) < 1e-10


def test_cs_boundary_product_function():
    result = cs_boundary_product()
    assert result["is_odd_integer"] is True
    assert result["product_int"] == 37
    assert result["status"] == "ODD_INTEGER_CONFIRMED"


def test_kawamura_eigenvalues_tuple():
    assert KAWAMURA_EIGENVALUES == (+1, +1, +1, -1, -1)


def test_kawamura_det_is_one():
    det = 1
    for v in KAWAMURA_EIGENVALUES:
        det *= v
    assert det == 1


def test_kawamura_p_squared_is_identity():
    for v in KAWAMURA_EIGENVALUES:
        assert v * v == 1


def test_su5_generator_count():
    assert SU5_DIM == 24
    assert SM_GENERATORS == 12
    assert XY_GENERATORS == 12
    assert SM_GENERATORS + XY_GENERATORS == SU5_DIM


def test_su5_generator_phases_structure():
    phases = su5_generator_cs_phases()
    assert len(phases) == 4
    classes = [p["generator_class"] for p in phases]
    assert any("SU(3)" in c for c in classes)
    assert any("SU(2)" in c for c in classes)
    assert any("U(1)" in c for c in classes)
    assert any("X,Y" in c for c in classes)


def test_su3_generators_survive():
    phases = su5_generator_cs_phases()
    su3 = [p for p in phases if "SU(3)" in p["generator_class"]][0]
    assert su3["zero_mode_survives"] is True
    assert su3["p_eigenvalue_in_block"] == +1


def test_su2_generators_survive():
    phases = su5_generator_cs_phases()
    su2 = [p for p in phases if "SU(2)" in p["generator_class"]][0]
    assert su2["zero_mode_survives"] is True


def test_xy_generators_projected_out():
    phases = su5_generator_cs_phases()
    xy = [p for p in phases if "X,Y" in p["generator_class"]][0]
    assert xy["zero_mode_survives"] is False


def test_derive_kawamura_matrix_all_conditions():
    result = derive_kawamura_matrix_from_cs_phase()
    assert result["det_ok"] is True
    assert result["P_squared_is_identity"] is True
    assert result["su3_block_eigenvalue_plus1"] is True
    assert result["su2_block_eigenvalue_minus1"] is True
    assert result["xy_generators_anticommute_with_P"] is True
    assert result["su3_generators_commute_with_P"] is True
    assert result["su2_generators_commute_with_P"] is True
    assert result["all_conditions_satisfied"] is True


def test_derive_kawamura_no_external_input():
    result = derive_kawamura_matrix_from_cs_phase()
    assert result["external_input_required"] is False


def test_kawamura_status():
    result = derive_kawamura_matrix_from_cs_phase()
    assert result["status"] == "KAWAMURA_MATRIX_UNIQUELY_DERIVED"


def test_su5_breaking_spectrum():
    spec = su5_breaking_spectrum()
    assert spec["sm_generators_surviving"] == 12
    assert spec["xy_projected_out"] == 12
    assert spec["su5_total_generators"] == 24
    assert spec["kawamura_derivation_status"] == "DERIVED_FROM_UM_GEOMETRY"


def test_uniqueness_proof():
    uniq = cs_boundary_uniqueness_proof()
    assert uniq["unique_canonical_sm_breaking"] is True
    assert uniq["canonical_matrix"] == (1, 1, 1, -1, -1)
    assert uniq["status"] == "UNIQUENESS_PROVED"


def test_fallibility_update():
    fb = fallibility_update()
    assert "CLOSED" in fb["new_status"]
    assert fb["pillar"] == 955


def test_summary_keys():
    s = pillar955_summary()
    assert s["pillar"] == 955
    assert s["valid"] is True
    assert s["gap_closed"] is not None
    assert len(s["derivation_chain"]) >= 6
