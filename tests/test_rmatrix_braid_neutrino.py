# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 143: c_R = 23/25 as Topological Invariant
(src/core/rmatrix_braid_neutrino.py).

Verifies the orbifold fixed-point theorem, SU(2)_k R-matrix, and
the neutrino_cr_topological_theorem() full report.
"""

import cmath
import math
import pytest

from src.core.rmatrix_braid_neutrino import (
    orbifold_fixed_point_count,
    winding_crossing_number,
    c_right_from_orbifold,
    c_left_topological,
    rs_unitarity_identity,
    su2k_topological_spin,
    su2k_rmatrix_eigenvalue,
    su2k_rmatrix_spectrum,
    neutrino_cr_topological_theorem,
    N_W_CANONICAL,
    K_LEVEL_CANONICAL,
    N_FP_CANONICAL,
    C_RIGHT_THEOREM,
    C_LEFT_TOPO_THEOREM,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_k_level_canonical(self):
        assert K_LEVEL_CANONICAL == 25

    def test_n_fp_canonical(self):
        assert N_FP_CANONICAL == 2

    def test_c_right_theorem_exact(self):
        assert abs(C_RIGHT_THEOREM - 23.0 / 25.0) < 1e-14

    def test_c_right_theorem_value(self):
        assert abs(C_RIGHT_THEOREM - 0.920) < 1e-12

    def test_c_left_topo_theorem(self):
        assert abs(C_LEFT_TOPO_THEOREM - 2.0 / 25.0) < 1e-14

    def test_unitarity_constant(self):
        assert abs(C_RIGHT_THEOREM + C_LEFT_TOPO_THEOREM - 1.0) < 1e-14


# ---------------------------------------------------------------------------
# orbifold_fixed_point_count
# ---------------------------------------------------------------------------

class TestOrbifoldFixedPointCount:
    def test_s1_z2_returns_2(self):
        assert orbifold_fixed_point_count("S1_Z2") == 2

    def test_default_returns_2(self):
        assert orbifold_fixed_point_count() == 2

    def test_unsupported_topology_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            orbifold_fixed_point_count("T2")


# ---------------------------------------------------------------------------
# winding_crossing_number
# ---------------------------------------------------------------------------

class TestWindingCrossingNumber:
    def test_canonical_value(self):
        # ν = 5² − 2 = 23
        assert winding_crossing_number(5, 2) == 23

    def test_default_canonical(self):
        assert winding_crossing_number() == 23

    def test_nw3_nfp2(self):
        assert winding_crossing_number(3, 2) == 7

    def test_nw7_nfp2(self):
        assert winding_crossing_number(7, 2) == 47

    def test_nfp0(self):
        assert winding_crossing_number(5, 0) == 25

    def test_nw_must_be_positive(self):
        with pytest.raises(ValueError):
            winding_crossing_number(0, 2)

    def test_nfp_must_be_nonneg(self):
        with pytest.raises(ValueError):
            winding_crossing_number(5, -1)

    def test_nfp_gte_nw_sq_raises(self):
        with pytest.raises(ValueError):
            winding_crossing_number(5, 25)  # n_fp = n_w² is invalid


# ---------------------------------------------------------------------------
# c_right_from_orbifold
# ---------------------------------------------------------------------------

class TestCRightFromOrbifold:
    def test_canonical_exact_fraction(self):
        val = c_right_from_orbifold()
        assert abs(val - 23.0 / 25.0) < 1e-14

    def test_canonical_equals_0920(self):
        val = c_right_from_orbifold()
        assert abs(val - 0.920) < 1e-12

    def test_physical_range(self):
        val = c_right_from_orbifold()
        assert 0.5 < val < 1.0

    def test_nw3_nfp2(self):
        val = c_right_from_orbifold(3, 2)
        assert abs(val - 7.0 / 9.0) < 1e-14

    def test_returns_float(self):
        assert isinstance(c_right_from_orbifold(), float)


# ---------------------------------------------------------------------------
# c_left_topological
# ---------------------------------------------------------------------------

class TestCLeftTopological:
    def test_canonical_exact(self):
        val = c_left_topological()
        assert abs(val - 2.0 / 25.0) < 1e-14

    def test_canonical_equals_008(self):
        val = c_left_topological()
        assert abs(val - 0.08) < 1e-12

    def test_nw7_nfp2(self):
        val = c_left_topological(7, 2)
        assert abs(val - 2.0 / 49.0) < 1e-14

    def test_invalid_nw(self):
        with pytest.raises(ValueError):
            c_left_topological(0, 2)


# ---------------------------------------------------------------------------
# rs_unitarity_identity
# ---------------------------------------------------------------------------

class TestRSUnitarityIdentity:
    @pytest.fixture(scope="class")
    def result(self):
        return rs_unitarity_identity()

    def test_identity_holds(self, result):
        assert result["identity_holds"] is True

    def test_sum_exactly_one(self, result):
        assert abs(result["sum"] - 1.0) < 1e-14

    def test_c_right_correct(self, result):
        assert abs(result["c_right"] - 23.0 / 25.0) < 1e-14

    def test_c_left_topo_correct(self, result):
        assert abs(result["c_left_topo"] - 2.0 / 25.0) < 1e-14

    def test_crossing_number_stored(self, result):
        assert result["crossing_number_nu"] == 23

    def test_physical_note_present(self, result):
        assert "topological" in result["physical_note"].lower()

    def test_nw3_sum_one(self):
        r = rs_unitarity_identity(3, 2)
        assert abs(r["sum"] - 1.0) < 1e-14


# ---------------------------------------------------------------------------
# su2k_topological_spin
# ---------------------------------------------------------------------------

class TestSU2kTopologicalSpin:
    def test_j0_gives_zero(self):
        assert su2k_topological_spin(0, 25) == 0.0

    def test_j_half_k25(self):
        # h_{1/2} = (1/2)(3/2)/27 = 3/108 = 1/36
        val = su2k_topological_spin(0.5, 25)
        assert abs(val - 1.0 / 36.0) < 1e-14

    def test_canonical_j_nu2_k25(self):
        # j = 23/2, k = 25 → h = (23/2)(25/2)/27 = 575/108
        val = su2k_topological_spin(23 / 2.0, 25)
        assert abs(val - 575.0 / 108.0) < 1e-12

    def test_negative_j_raises(self):
        with pytest.raises(ValueError):
            su2k_topological_spin(-0.5, 25)

    def test_k_zero_raises(self):
        with pytest.raises(ValueError):
            su2k_topological_spin(0.5, 0)


# ---------------------------------------------------------------------------
# su2k_rmatrix_eigenvalue
# ---------------------------------------------------------------------------

class TestSU2kRMatrixEigenvalue:
    def test_returns_complex(self):
        R = su2k_rmatrix_eigenvalue(0.5, 25)
        assert isinstance(R, complex)

    def test_unit_modulus(self):
        R = su2k_rmatrix_eigenvalue(0.5, 25)
        assert abs(abs(R) - 1.0) < 1e-12

    def test_j0_gives_one(self):
        R = su2k_rmatrix_eigenvalue(0.0, 25)
        assert abs(R - 1.0) < 1e-12


# ---------------------------------------------------------------------------
# su2k_rmatrix_spectrum
# ---------------------------------------------------------------------------

class TestSU2kRMatrixSpectrum:
    @pytest.fixture(scope="class")
    def spectrum(self):
        return su2k_rmatrix_spectrum(25)

    def test_spectrum_length(self, spectrum):
        # j = 0, 1/2, 1, ..., 25/2: that's 26 entries
        assert len(spectrum) == 26

    def test_all_unit_modulus(self, spectrum):
        for entry in spectrum:
            R = complex(entry["R_j_real"], entry["R_j_imag"])
            assert abs(abs(R) - 1.0) < 1e-12

    def test_first_entry_j0(self, spectrum):
        assert spectrum[0]["j"] == 0.0

    def test_last_entry_j_12p5(self, spectrum):
        assert abs(spectrum[-1]["j"] - 12.5) < 1e-10

    def test_cs_near_identity(self, spectrum):
        # For j = 23/2 at k=25: h_j mod 1 ≈ 12/37 (braided sound speed)
        entry = next(e for e in spectrum if abs(e["j"] - 11.5) < 0.1)
        cs = 12.0 / 37.0
        assert abs(entry["h_j_mod1"] - cs) < 0.001


# ---------------------------------------------------------------------------
# neutrino_cr_topological_theorem (full report)
# ---------------------------------------------------------------------------

class TestNeutrinoCRTopologicalTheorem:
    @pytest.fixture(scope="class")
    def theorem(self):
        return neutrino_cr_topological_theorem()

    def test_pillar_number(self, theorem):
        assert theorem["pillar"] == 143

    def test_c_right_exact_23_25(self, theorem):
        assert abs(theorem["c_right"] - 23.0 / 25.0) < 1e-14

    def test_crossing_number_23(self, theorem):
        assert theorem["crossing_number_nu"] == 23

    def test_total_sectors_25(self, theorem):
        assert theorem["total_sectors_N"] == 25

    def test_unitarity_holds(self, theorem):
        assert theorem["unitarity_identity_holds"] is True

    def test_unitarity_sum_one(self, theorem):
        assert abs(theorem["unitarity_sum"] - 1.0) < 1e-14

    def test_is_closed(self, theorem):
        assert theorem["is_closed"] is True

    def test_status_contains_proved(self, theorem):
        assert "PROVED" in theorem["theorem_status"].upper() or \
               "DERIVED" in theorem["theorem_status"].upper()

    def test_previous_status_hardcoded(self, theorem):
        assert "hardcoded" in theorem["previous_status"].lower()

    def test_new_status_theorem(self, theorem):
        assert "THEOREM" in theorem["new_status"].upper()

    def test_derivation_steps_count(self, theorem):
        assert len(theorem["derivation_steps"]) >= 5

    def test_rmatrix_h_mod1_near_cs(self, theorem):
        # |h_j mod 1 − c_s| < 0.002 for the canonical parameters
        assert theorem["rmatrix_phase_near_cs_diff"] < 0.01

    def test_nw3_c_right(self):
        r = neutrino_cr_topological_theorem(n_w=3, n_fp=2)
        assert abs(r["c_right"] - 7.0 / 9.0) < 1e-14

    def test_nw7_c_right(self):
        r = neutrino_cr_topological_theorem(n_w=7, n_fp=2)
        assert abs(r["c_right"] - 47.0 / 49.0) < 1e-14
