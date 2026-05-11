# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for Pillar 109 — 3D minisuperspace Wheeler-DeWitt extension."""

from __future__ import annotations

import numpy as np
import pytest

from src.core.wdw_three_field import (
    N_W,
    K_CS,
    PI_KR,
    PHI0,
    CHI0,
    build_3d_wdw_hamiltonian,
    solve_3d_wdw_spectrum,
    wdw_three_field_report,
)


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert PI_KR == 37.0
    assert PHI0 == 1.0
    assert CHI0 == 1.0


def test_hamiltonian_shape():
    h = build_3d_wdw_hamiltonian(n_a=4, n_phi=5, n_chi=6)
    assert h.shape == (4 * 5 * 6, 4 * 5 * 6)


def test_hamiltonian_symmetric():
    h = build_3d_wdw_hamiltonian(n_a=4, n_phi=4, n_chi=4)
    assert np.allclose(h, h.T, atol=1e-12)


def test_hamiltonian_finite():
    h = build_3d_wdw_hamiltonian(n_a=4, n_phi=4, n_chi=4)
    assert np.all(np.isfinite(h))


def test_hamiltonian_requires_min_grid():
    with pytest.raises(ValueError):
        build_3d_wdw_hamiltonian(n_a=2, n_phi=4, n_chi=4)


def test_spectrum_keys():
    res = solve_3d_wdw_spectrum(n_a=4, n_phi=4, n_chi=4, n_eigvals=4)
    for key in ("eigenvalues", "ground_state_wavefunction", "grid_shape"):
        assert key in res


def test_spectrum_eigenvalues_sorted():
    res = solve_3d_wdw_spectrum(n_a=4, n_phi=4, n_chi=4, n_eigvals=4)
    vals = res["eigenvalues"]
    assert np.all(np.diff(vals) >= 0)


def test_spectrum_wavefunction_shape():
    res = solve_3d_wdw_spectrum(n_a=4, n_phi=5, n_chi=6, n_eigvals=3)
    assert res["ground_state_wavefunction"].shape == (4, 5, 6)


def test_spectrum_respects_n_eigvals():
    res = solve_3d_wdw_spectrum(n_a=4, n_phi=4, n_chi=4, n_eigvals=5)
    assert len(res["eigenvalues"]) == 5


def test_report_keys():
    report = wdw_three_field_report()
    for key in ("pillar", "module", "status", "description", "residual_unknowns", "epistemic_label"):
        assert key in report


def test_report_semantics():
    report = wdw_three_field_report()
    assert report["pillar"] == 109
    assert report["module"] == "wdw_three_field"
    assert "SUBSTANTIALLY_CLOSED" in report["status"]
    assert len(report["residual_unknowns"]) > 0

