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
