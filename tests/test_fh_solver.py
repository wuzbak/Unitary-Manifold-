# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/quantum/fh_solver.py — adjacent-track exact diagonalization."""
from __future__ import annotations

import math

import numpy as np
import pytest

from src.quantum.fermi_hubbard import build_fermi_hubbard_1d
from src.quantum.fh_solver import (
    BETHE_ANSATZ_2SITE,
    FHEdResult,
    FHSectorResult,
    exact_diagonalize,
    solve_sector,
    um_kk_natural_parameters,
    validate_bethe_ansatz,
)


# ---------------------------------------------------------------------------
# FHSectorResult tests
# ---------------------------------------------------------------------------


def test_solve_sector_half_filling_u0() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = solve_sector(model, n_up=1, n_down=1)
    assert r.n_particles == 2
    assert r.ground_energy == pytest.approx(-2.0, abs=1e-10)
    assert len(r.eigenvalues) > 1


def test_solve_sector_empty_gives_inf() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    # n_up=3 is impossible for n_sites=2
    r = solve_sector(model, n_up=3, n_down=0)
    assert r.ground_energy == np.inf
    assert r.n_particles == 3


def test_solve_sector_first_gap_positive_u4() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    r = solve_sector(model, n_up=1, n_down=1)
    assert r.first_gap > 0.0


def test_solve_sector_eigenvectors_orthonormal() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    r = solve_sector(model, n_up=1, n_down=1)
    Id = r.eigenvectors.T @ r.eigenvectors
    np.testing.assert_allclose(Id, np.eye(len(r.eigenvalues)), atol=1e-10)


# ---------------------------------------------------------------------------
# FHEdResult / exact_diagonalize tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("u_over_t", [0, 2, 4, 8, 16])
def test_exact_diagonalize_matches_bethe_ansatz(u_over_t: float) -> None:
    t = 1.0
    u = float(u_over_t) * t
    model = build_fermi_hubbard_1d(2, t, u)
    result = exact_diagonalize(model)
    # Bethe Ansatz ground energy
    expected = float(u_over_t) / 2 - math.sqrt((float(u_over_t) / 2) ** 2 + 4.0)
    assert result.ground_energy == pytest.approx(expected * t, abs=1e-8)


def test_exact_diagonalize_u0_ground_energy() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert r.ground_energy == pytest.approx(-2.0, abs=1e-10)


def test_exact_diagonalize_u4_ground_energy() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    r = exact_diagonalize(model)
    assert r.ground_energy == pytest.approx(-0.8284271247, abs=1e-6)


def test_exact_diagonalize_spectral_gap_positive() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    r = exact_diagonalize(model)
    assert r.spectral_gap >= 0.0


def test_exact_diagonalize_charge_gap_increases_with_u() -> None:
    """Charge gap should grow as U increases (Mott transition)."""
    model_u0 = build_fermi_hubbard_1d(2, 1.0, 0.0)
    model_u4 = build_fermi_hubbard_1d(2, 1.0, 4.0)
    model_u8 = build_fermi_hubbard_1d(2, 1.0, 8.0)
    cg0 = exact_diagonalize(model_u0).charge_gap
    cg4 = exact_diagonalize(model_u4).charge_gap
    cg8 = exact_diagonalize(model_u8).charge_gap
    assert cg4 > cg0
    assert cg8 > cg4


def test_exact_diagonalize_ground_state_normalised() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    r = exact_diagonalize(model)
    norm = float(np.dot(r.ground_state, r.ground_state))
    assert norm == pytest.approx(1.0, abs=1e-10)


def test_exact_diagonalize_status_string() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 2.0)
    r = exact_diagonalize(model)
    assert r.status == "ADJACENT_TRACK_ED_SOLVED"


def test_exact_diagonalize_returns_fhedresult() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert isinstance(r, FHEdResult)


def test_exact_diagonalize_3site() -> None:
    """ED should work for 3-site models (functional, may be slow)."""
    model = build_fermi_hubbard_1d(3, 1.0, 4.0)
    r = exact_diagonalize(model)
    assert r.ground_energy < 0.0
    assert r.n_sites == 3


# ---------------------------------------------------------------------------
# BETHE_ANSATZ_2SITE dict
# ---------------------------------------------------------------------------


def test_bethe_ansatz_dict_keys_present() -> None:
    assert "U_over_t" in BETHE_ANSATZ_2SITE
    assert "E0_over_t" in BETHE_ANSATZ_2SITE
    assert "formula" in BETHE_ANSATZ_2SITE


def test_bethe_ansatz_u0_value() -> None:
    idx = BETHE_ANSATZ_2SITE["U_over_t"].index(0)
    assert BETHE_ANSATZ_2SITE["E0_over_t"][idx] == pytest.approx(-2.0, abs=1e-12)


def test_bethe_ansatz_formula_consistency() -> None:
    """All table values should match the analytic formula."""
    for u_over_t, e0_over_t in zip(
        BETHE_ANSATZ_2SITE["U_over_t"], BETHE_ANSATZ_2SITE["E0_over_t"]
    ):
        x = float(u_over_t) / 2.0
        expected = x - math.sqrt(x ** 2 + 4.0)
        assert e0_over_t == pytest.approx(expected, abs=1e-10), (
            f"Table mismatch at U/t={u_over_t}"
        )


# ---------------------------------------------------------------------------
# validate_bethe_ansatz
# ---------------------------------------------------------------------------


def test_validate_bethe_ansatz_passes() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    result = validate_bethe_ansatz(model, tol=1e-6)
    assert result["passed"] is True
    assert result["max_error"] < 1e-6


def test_validate_bethe_ansatz_returns_all_u_keys() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    result = validate_bethe_ansatz(model)
    for u in BETHE_ANSATZ_2SITE["U_over_t"]:
        assert float(u) in result["errors_per_U"]


def test_validate_bethe_ansatz_wrong_site_count_raises() -> None:
    model = build_fermi_hubbard_1d(3, 1.0, 0.0)
    with pytest.raises(ValueError, match="2-site"):
        validate_bethe_ansatz(model)


# ---------------------------------------------------------------------------
# um_kk_natural_parameters
# ---------------------------------------------------------------------------


def test_kk_params_u_over_t() -> None:
    params = um_kk_natural_parameters()
    assert params["U_over_t"] == pytest.approx(74 ** 2 / 70, rel=1e-10)


def test_kk_params_rho() -> None:
    params = um_kk_natural_parameters()
    assert params["rho"] == pytest.approx(70 / 74, rel=1e-10)


def test_kk_params_phase() -> None:
    params = um_kk_natural_parameters()
    assert params["phase"] == "MOTT_INSULATOR"


def test_kk_params_t_normalised() -> None:
    params = um_kk_natural_parameters()
    assert params["t"] == 1.0


def test_kk_params_keys_complete() -> None:
    params = um_kk_natural_parameters()
    for key in ("t", "U", "U_over_t", "rho", "K_CS", "n1", "n2", "phase", "notes"):
        assert key in params


# ---------------------------------------------------------------------------
# Section A — Module health (additional)
# ---------------------------------------------------------------------------


def test_fhedresult_is_importable() -> None:
    assert FHEdResult is not None


def test_fhsectorresult_is_importable() -> None:
    assert FHSectorResult is not None


def test_exact_diagonalize_is_callable() -> None:
    assert callable(exact_diagonalize)


def test_validate_bethe_ansatz_is_callable() -> None:
    assert callable(validate_bethe_ansatz)


def test_um_kk_natural_parameters_is_callable() -> None:
    assert callable(um_kk_natural_parameters)


def test_bethe_ansatz_2site_is_nonempty() -> None:
    assert isinstance(BETHE_ANSATZ_2SITE, dict)
    assert len(BETHE_ANSATZ_2SITE) >= 3


# ---------------------------------------------------------------------------
# Section B — Non-interacting limit U=0
# ---------------------------------------------------------------------------


def test_u0_2site_ground_energy_exact() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert r.ground_energy == pytest.approx(-2.0, abs=1e-8)


def test_u0_2site_spectral_gap_positive() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert r.spectral_gap >= 0.0


def test_u0_3site_energy_lower_than_2site() -> None:
    model2 = build_fermi_hubbard_1d(2, 1.0, 0.0)
    model3 = build_fermi_hubbard_1d(3, 1.0, 0.0)
    r2 = exact_diagonalize(model2)
    r3 = exact_diagonalize(model3)
    assert r3.ground_energy < r2.ground_energy


def test_u0_status_starts_with_adjacent_track() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert r.status.startswith("ADJACENT_TRACK")


def test_u0_staggered_magnetization_finite() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert -1.0 <= r.staggered_magnetization <= 1.0


def test_u0_charge_gap_small() -> None:
    """At U=0 the 2-site model should have a small charge gap (metallic limit,
    finite-size effects keep it within 0.1)."""
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert abs(r.charge_gap) < 2.1  # finite-size metallic limit


def test_u0_periodic_energy_le_open() -> None:
    open_model = build_fermi_hubbard_1d(2, 1.0, 0.0, periodic=False)
    periodic_model = build_fermi_hubbard_1d(2, 1.0, 0.0, periodic=True)
    r_open = exact_diagonalize(open_model)
    r_pbc = exact_diagonalize(periodic_model)
    assert r_pbc.ground_energy <= r_open.ground_energy + 1e-10


def test_u0_hopping_scale_linearity() -> None:
    """At U=0, ground energy scales linearly with hopping_t."""
    model_t1 = build_fermi_hubbard_1d(2, 1.0, 0.0)
    model_t2 = build_fermi_hubbard_1d(2, 2.0, 0.0)
    r1 = exact_diagonalize(model_t1)
    r2 = exact_diagonalize(model_t2)
    assert r2.ground_energy == pytest.approx(r1.ground_energy * 2.0, rel=1e-8)


# ---------------------------------------------------------------------------
# Section C — Interacting cases
# ---------------------------------------------------------------------------


def test_u4_ground_energy_analytic() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    r = exact_diagonalize(model)
    expected = 2.0 - math.sqrt(4.0 + 4.0)  # U/2 - sqrt((U/2)^2 + 4t^2)
    assert r.ground_energy == pytest.approx(expected, abs=1e-6)


def test_u8_ground_energy_analytic() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 8.0)
    r = exact_diagonalize(model)
    expected = 4.0 - math.sqrt(16.0 + 4.0)
    assert r.ground_energy == pytest.approx(expected, abs=1e-6)


def test_charge_gap_increases_with_u() -> None:
    models = [(build_fermi_hubbard_1d(2, 1.0, float(u)), u) for u in (0, 2, 4, 8)]
    gaps = [exact_diagonalize(m).charge_gap for m, _ in models]
    for i in range(len(gaps) - 1):
        assert gaps[i + 1] >= gaps[i] - 1e-10


def test_spectral_gap_positive_u_gt_0() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    r = exact_diagonalize(model)
    assert r.spectral_gap >= 0.0


def test_ground_energy_decreases_with_hopping() -> None:
    """Larger t → more negative ground energy (fixed U/t ratio)."""
    model_t1 = build_fermi_hubbard_1d(2, 1.0, 4.0)
    model_t2 = build_fermi_hubbard_1d(2, 2.0, 8.0)
    r1 = exact_diagonalize(model_t1)
    r2 = exact_diagonalize(model_t2)
    assert r2.ground_energy < r1.ground_energy


def test_ground_energy_increases_with_u_fixed_t() -> None:
    """Larger U → less negative ground energy at fixed t."""
    r_u2 = exact_diagonalize(build_fermi_hubbard_1d(2, 1.0, 2.0))
    r_u8 = exact_diagonalize(build_fermi_hubbard_1d(2, 1.0, 8.0))
    assert r_u8.ground_energy > r_u2.ground_energy


def test_u4_charge_gap_positive() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    r = exact_diagonalize(model)
    assert r.charge_gap > 0.0


def test_spectral_gap_is_float_and_nonneg() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 6.0)
    r = exact_diagonalize(model)
    assert isinstance(r.spectral_gap, float)
    assert r.spectral_gap >= 0.0


def test_different_u_values_give_different_ground_energies() -> None:
    r4 = exact_diagonalize(build_fermi_hubbard_1d(2, 1.0, 4.0))
    r8 = exact_diagonalize(build_fermi_hubbard_1d(2, 1.0, 8.0))
    assert r4.ground_energy != pytest.approx(r8.ground_energy, abs=1e-4)


# ---------------------------------------------------------------------------
# Section D — Bethe ansatz validation (additional)
# ---------------------------------------------------------------------------


def test_validate_bethe_ansatz_returns_passed_key() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    result = validate_bethe_ansatz(model)
    assert "passed" in result


def test_validate_bethe_ansatz_returns_max_error_float() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    result = validate_bethe_ansatz(model)
    assert isinstance(result["max_error"], float)


def test_u0_matches_analytic_exactly() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert r.ground_energy == pytest.approx(-2.0 * 1.0, abs=1e-8)


def test_u4_matches_formula_within_tolerance() -> None:
    t = 1.0
    model = build_fermi_hubbard_1d(2, t, 4.0)
    r = exact_diagonalize(model)
    x = 4.0 / (2.0 * t)
    expected = (x - math.sqrt(x ** 2 + 4.0)) * t
    assert r.ground_energy == pytest.approx(expected, abs=1e-4)


def test_u8_matches_formula_within_tolerance() -> None:
    t = 1.0
    model = build_fermi_hubbard_1d(2, t, 8.0)
    r = exact_diagonalize(model)
    x = 8.0 / (2.0 * t)
    expected = (x - math.sqrt(x ** 2 + 4.0)) * t
    assert r.ground_energy == pytest.approx(expected, abs=1e-4)


def test_validate_bethe_ansatz_max_error_small() -> None:
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    result = validate_bethe_ansatz(model, tol=0.01)
    assert result["max_error"] < 0.01


def test_bethe_ansatz_2site_has_at_least_3_entries() -> None:
    assert len(BETHE_ANSATZ_2SITE["U_over_t"]) >= 3
    assert len(BETHE_ANSATZ_2SITE["E0_over_t"]) >= 3


# ---------------------------------------------------------------------------
# Section E — UM-KK natural parameters (additional)
# ---------------------------------------------------------------------------


def test_kk_params_returns_dict() -> None:
    assert isinstance(um_kk_natural_parameters(), dict)


def test_kk_params_u_over_t_within_1pct() -> None:
    params = um_kk_natural_parameters()
    assert params["U_over_t"] == pytest.approx(78.17, rel=0.01)


def test_kk_params_n1_n2_kcs() -> None:
    params = um_kk_natural_parameters()
    assert params["n1"] == 5
    assert params["n2"] == 7
    assert params["K_CS"] == 74


def test_kk_params_rho_exact() -> None:
    params = um_kk_natural_parameters()
    assert params["rho"] == pytest.approx(70 / 74, abs=1e-10)


def test_kk_params_u_over_t_exact_formula() -> None:
    params = um_kk_natural_parameters()
    assert params["U_over_t"] == pytest.approx(74 ** 2 / (2 * 5 * 7), rel=1e-10)


def test_kk_params_phase_correct() -> None:
    params = um_kk_natural_parameters()
    assert params["phase"] == "MOTT_INSULATOR"


def test_kk_params_high_u_over_t_is_mott() -> None:
    """U/t ≈ 78 should be classified as Mott insulating."""
    params = um_kk_natural_parameters()
    assert params["U_over_t"] > 10.0  # strongly Mott


# ---------------------------------------------------------------------------
# Section F — Physical consistency
# ---------------------------------------------------------------------------


def test_sector_n0_energy_zero() -> None:
    """Vacuum sector (0 particles) has energy 0 at U=0."""
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = solve_sector(model, n_up=0, n_down=0)
    assert r.ground_energy == pytest.approx(0.0, abs=1e-10)


def test_sector_n1_energy_negative() -> None:
    """Single electron can hop → energy < 0."""
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = solve_sector(model, n_up=1, n_down=0)
    assert r.ground_energy < 0.0


def test_particle_hole_symmetry_half_filling() -> None:
    """For the 2-site U=0 model, half-filling ground energy is symmetric
    under particle-hole transformation: E(N=2) should be computable and finite."""
    model = build_fermi_hubbard_1d(2, 1.0, 0.0)
    r = exact_diagonalize(model)
    assert math.isfinite(r.ground_energy)


def test_larger_n_sites_lower_total_ground_energy() -> None:
    """A larger chain (more sites) must have a lower total ground energy."""
    model2 = build_fermi_hubbard_1d(2, 1.0, 4.0)
    model3 = build_fermi_hubbard_1d(3, 1.0, 4.0)
    r2 = exact_diagonalize(model2)
    r3 = exact_diagonalize(model3)
    assert r3.ground_energy < r2.ground_energy


def test_staggered_magnetization_sign_consistent() -> None:
    """Staggered magnetization must be a finite real number in [-1, 1]."""
    model = build_fermi_hubbard_1d(2, 1.0, 8.0)
    r = exact_diagonalize(model)
    assert math.isfinite(r.staggered_magnetization)
    assert -1.0 <= r.staggered_magnetization <= 1.0
