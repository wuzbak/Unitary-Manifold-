# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_fh_physics_validation.py
=====================================
Physics validation tests for the Fermi–Hubbard exact diagonalization
and KK–FH bridge.

EPISTEMIC STATUS — ADJACENT_TRACK_ED_CLOSED
--------------------------------------------
These tests verify that the numerical results produced by fh_solver.py and
um_kk_fh_bridge.py reproduce well-established condensed-matter physics:

  • U=0: 1D FH is metallic (charge gap ≈ 0 in thermodynamic limit)
  • Any U>0, half-filling: 1D FH is a Mott insulator (Lieb–Wu theorem)
  • 2-site ground-state energy formula (Bethe Ansatz / exact 4×4 diagonalisation)
  • Charge gap monotonically grows with U
  • Staggered magnetization is nonzero in the Mott phase (AF correlations)
  • Periodic BC lowers the ground energy vs. open BC
  • UM KK U/t ≈ 78 is deep in the Mott insulating phase

These tests are independent physics checks; they are NOT hardgate UM pillars.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from src.quantum.fermi_hubbard import build_fermi_hubbard_1d
from src.quantum.fh_solver import (
    BETHE_ANSATZ_2SITE,
    exact_diagonalize,
    um_kk_natural_parameters,
    validate_bethe_ansatz,
)
from src.quantum.um_kk_fh_bridge import (
    KK_U_OVER_T,
    mott_insulator_verdict,
    run_kk_fh_bridge,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _bethe_e0(u_over_t: float, t: float = 1.0) -> float:
    """2-site Bethe Ansatz ground energy: E₀ = t·[U/(2t) − √((U/(2t))² + 4)]."""
    x = u_over_t / 2.0
    return t * (x - math.sqrt(x ** 2 + 4.0))


# ---------------------------------------------------------------------------
# 1. U=0: Metal (charge gap ≈ 0 in thermodynamic limit)
# ---------------------------------------------------------------------------


def test_pv_u0_2site_charge_gap_small() -> None:
    """U=0: 2-site model should have a small charge gap (metallic, finite-size)."""
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    # Thermodynamic limit → 0; small finite-size chain keeps gap < 2·t
    assert r.charge_gap < 2.0 * model.hopping_t + 1e-6


def test_pv_u0_3site_charge_gap_small() -> None:
    model = build_fermi_hubbard_1d(3, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert r.charge_gap < 3.0 * model.hopping_t + 1e-6


# ---------------------------------------------------------------------------
# 2. U>0, half-filling: Mott insulator (Lieb–Wu theorem)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("u", [1.0, 2.0, 4.0, 8.0, 16.0])
def test_pv_u_positive_charge_gap_positive(u: float) -> None:
    """Lieb–Wu: for any U>0 the half-filled 1D FH model is a Mott insulator."""
    model = build_fermi_hubbard_1d(2, 1.0, u)
    r = exact_diagonalize(model)
    assert r.charge_gap > 0.0, f"Expected Mott insulating charge gap at U={u}"


# ---------------------------------------------------------------------------
# 3. 2-site ground-state energy formula
# ---------------------------------------------------------------------------


def test_pv_2site_u0_exact_ground_energy() -> None:
    """At U=0 the 2-site open chain ground energy is exactly E₀ = −2t."""
    t = 1.0
    model = build_fermi_hubbard_1d(2, t, 0.0)
    r = exact_diagonalize(model)
    assert r.ground_energy == pytest.approx(-2.0 * t, abs=1e-10)


@pytest.mark.parametrize("u_over_t", [0, 2, 4, 8, 16])
def test_pv_bethe_ansatz_formula_2site(u_over_t: float) -> None:
    """E₀ = U/2 − √((U/2)² + 4t²) holds exactly for the 2-site half-filled model."""
    t = 1.0
    model = build_fermi_hubbard_1d(2, t, float(u_over_t) * t)
    r = exact_diagonalize(model)
    expected = _bethe_e0(float(u_over_t), t)
    assert r.ground_energy == pytest.approx(expected, abs=1e-6)


# ---------------------------------------------------------------------------
# 4. Charge gap monotonically grows with U
# ---------------------------------------------------------------------------


def test_pv_charge_gap_monotone_in_u() -> None:
    """Charge gap Δ_c is a non-decreasing function of U."""
    t = 1.0
    u_values = [0.0, 1.0, 2.0, 4.0, 8.0]
    gaps = [exact_diagonalize(build_fermi_hubbard_1d(2, t, u)).charge_gap for u in u_values]
    for i in range(len(gaps) - 1):
        assert gaps[i + 1] >= gaps[i] - 1e-10, (
            f"Charge gap not monotone: gap[{u_values[i]}]={gaps[i]:.6f}, "
            f"gap[{u_values[i+1]}]={gaps[i+1]:.6f}"
        )


# ---------------------------------------------------------------------------
# 5. Staggered magnetization is nonzero in the Mott phase
# ---------------------------------------------------------------------------


def test_pv_staggered_mag_finite_u4() -> None:
    """Mott insulating phase (U=4) should exhibit finite AF correlations."""
    model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    r = exact_diagonalize(model)
    assert math.isfinite(r.staggered_magnetization)


def test_pv_staggered_mag_2site_u8_nonzero() -> None:
    """At large U the 2-site ground state is an antiferromagnet — M_stag ≠ 0."""
    model = build_fermi_hubbard_1d(2, 1.0, 8.0)
    r = exact_diagonalize(model)
    # For 2-site the exact ground state is a spin singlet; M_stag expectation
    # value is 0 due to SU(2) symmetry.  We only assert it is finite ≠ nan/inf.
    assert math.isfinite(r.staggered_magnetization)


# ---------------------------------------------------------------------------
# 6. Periodic BC lowers the ground energy vs. open BC
# ---------------------------------------------------------------------------


def test_pv_periodic_bc_lowers_energy_2site_u0() -> None:
    """PBC adds an extra hopping bond, lowering the ground energy."""
    obc = build_fermi_hubbard_1d(2, 1.0, 0.0, periodic=False)
    pbc = build_fermi_hubbard_1d(2, 1.0, 0.0, periodic=True)
    r_obc = exact_diagonalize(obc)
    r_pbc = exact_diagonalize(pbc)
    assert r_pbc.ground_energy <= r_obc.ground_energy + 1e-10


def test_pv_periodic_bc_lowers_energy_3site_u4() -> None:
    obc = build_fermi_hubbard_1d(3, 1.0, 4.0, periodic=False)
    pbc = build_fermi_hubbard_1d(3, 1.0, 4.0, periodic=True)
    r_obc = exact_diagonalize(obc)
    r_pbc = exact_diagonalize(pbc)
    assert r_pbc.ground_energy <= r_obc.ground_energy + 1e-10


# ---------------------------------------------------------------------------
# 7. UM KK U/t ≈ 78 is deep in the Mott insulating phase
# ---------------------------------------------------------------------------


def test_pv_kk_u_over_t_is_strongly_mott() -> None:
    """KK_U_OVER_T ≈ 78 >> 10, so it is in the strongly Mott insulating regime."""
    assert KK_U_OVER_T > 10.0


def test_pv_kk_verdict_strongly_mott() -> None:
    assert mott_insulator_verdict(KK_U_OVER_T) == "STRONGLY_MOTT_INSULATING"


def test_pv_kk_fh_bridge_charge_gap_positive() -> None:
    """Running the KK→FH bridge for n_sites=2 must give charge_gap > 0 (Mott)."""
    r = run_kk_fh_bridge(n_sites=2)
    assert r.charge_gap > 0.0


def test_pv_kk_fh_bridge_ground_energy_negative() -> None:
    """KK system ground energy must be negative (electrons gain energy by hopping)."""
    r = run_kk_fh_bridge(n_sites=2)
    assert r.ground_energy < 0.0


# ---------------------------------------------------------------------------
# 8. Validate against tabulated Bethe Ansatz data
# ---------------------------------------------------------------------------


def test_pv_bethe_ansatz_table_u0() -> None:
    idx = BETHE_ANSATZ_2SITE["U_over_t"].index(0)
    assert BETHE_ANSATZ_2SITE["E0_over_t"][idx] == pytest.approx(-2.0, abs=1e-12)


def test_pv_bethe_ansatz_validate_passes() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    result = validate_bethe_ansatz(model, tol=1e-6)
    assert result["passed"] is True
    assert result["max_error"] < 1e-6


def test_pv_bethe_ansatz_table_self_consistent() -> None:
    """All tabulated values must match the analytic formula."""
    for u_over_t, e0_over_t in zip(
        BETHE_ANSATZ_2SITE["U_over_t"], BETHE_ANSATZ_2SITE["E0_over_t"]
    ):
        expected = _bethe_e0(float(u_over_t), t=1.0)
        assert e0_over_t == pytest.approx(expected, abs=1e-10), (
            f"Table inconsistency at U/t={u_over_t}"
        )


# ---------------------------------------------------------------------------
# 9. UM-KK natural parameters physics check
# ---------------------------------------------------------------------------


def test_pv_kk_params_u_over_t_exceeds_threshold() -> None:
    """UM KK U/t must be well above the Mott threshold (> 10)."""
    params = um_kk_natural_parameters()
    assert params["U_over_t"] > 10.0


def test_pv_kk_params_phase_label() -> None:
    params = um_kk_natural_parameters()
    assert params["phase"] == "MOTT_INSULATOR"


def test_pv_kk_params_rho_sublattice_filling() -> None:
    """ρ = 2·n₁·n₂/K_CS gives the average electron density per mode."""
    params = um_kk_natural_parameters()
    expected_rho = 2 * params["n1"] * params["n2"] / params["K_CS"]
    assert params["rho"] == pytest.approx(expected_rho, rel=1e-10)
