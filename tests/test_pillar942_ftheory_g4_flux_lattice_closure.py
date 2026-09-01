# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 942 — F-theory G₄ Flux Lattice Closure."""
from __future__ import annotations
import math
from src.core.pillar942_ftheory_g4_flux_lattice_closure import (
    B3_G4_REMAINING,
    C2_HALF_INTEGER_SHIFT,
    CHI_CY4,
    G4_FLUX_SQUARED_HALF,
    G4_TADPOLE_TREE,
    HALF_INT_RESIDUE,
    METHOD_A_STATUS,
    METHOD_B_STATUS,
    METHOD_C_STATUS,
    N_D3_EFFECTIVE,
    N_D3_TREE,
    N_KAHLER_GENERATORS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    g4_flux_lattice_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 942
def test_gate(): assert PILLAR_GATE == "FTHEORY_G4_FLUX_LATTICE_CLOSURE"
def test_chi_cy4(): assert CHI_CY4 == 1820
def test_n_kahler_generators(): assert N_KAHLER_GENERATORS == 3

def test_g4_tadpole_tree():
    assert abs(G4_TADPOLE_TREE - 1820 / 24) < 1e-12

def test_g4_flux_sq_half():
    assert abs(G4_FLUX_SQUARED_HALF - 74.0) < 1e-12

def test_n_d3_tree():
    assert abs(N_D3_TREE - (1820 / 24 - 74)) < 1e-12

def test_c2_half_integer_shift():
    assert abs(C2_HALF_INTEGER_SHIFT - 20 / 24) < 1e-12

def test_half_int_residue():
    # residue between N_D3_tree fractional part and c2 shift should be ~0
    assert HALF_INT_RESIDUE < 1e-10

def test_n_d3_effective_integer():
    assert abs(N_D3_EFFECTIVE - round(N_D3_EFFECTIVE)) < 1e-9

def test_n_d3_effective_value():
    assert abs(N_D3_EFFECTIVE - 1.0) < 1e-6

def test_n_d3_effective_nonneg():
    assert N_D3_EFFECTIVE >= 0

def test_method_a_primitive():
    assert METHOD_A_STATUS == "G4_PRIMITIVE_IN_KAHLER_CONE"

def test_method_b_integer():
    assert "INTEGER" in METHOD_B_STATUS

def test_method_c_abstract():
    assert "FREED_HOPKINS" in METHOD_C_STATUS

def test_pillar_status_set():
    assert PILLAR_STATUS in {
        "B3_G4_FLUX_LATTICE_PARTIAL_CONSISTENT",
        "B3_G4_FLUX_LATTICE_CONSISTENT",
        "B3_G4_FLUX_IRREDUCIBLE",
    }

def test_pillar_valid():
    assert PILLAR_VALID is True

def test_remaining_nonempty():
    assert len(B3_G4_REMAINING) > 20

def test_summary_keys():
    s = g4_flux_lattice_summary()
    for key in ["pillar", "gate", "status", "valid", "chi_cy4",
                "method_a", "method_b", "method_c", "n_d3_effective"]:
        assert key in s

def test_summary_pillar():
    assert g4_flux_lattice_summary()["pillar"] == 942

def test_summary_valid():
    assert g4_flux_lattice_summary()["valid"] is True

def test_chi_mod_24():
    # χ mod 24 ≠ 0 → half-integer shift required
    assert CHI_CY4 % 24 == 20

def test_c2_shift_fraction():
    assert abs(C2_HALF_INTEGER_SHIFT - 20 / 24) < 1e-12

def test_three_methods_evaluated():
    s = g4_flux_lattice_summary()
    assert s["method_a"] != ""
    assert s["method_b"] != ""
    assert s["method_c"] != ""
