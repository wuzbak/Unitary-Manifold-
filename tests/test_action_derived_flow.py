# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for the action-derived KK zero-mode flow (src/core/action_derived_flow.py)."""

from dataclasses import replace

import numpy as np
import pytest

from src.core.action_derived_flow import (
    action_derived_field_equations,
    action_derived_flow_surface,
    action_derived_rhs,
    numeric_euler_lagrange_match,
    numeric_ricci_crosscheck,
    radion_potential,
    symbolic_kk_reduction_check,
)
from src.core.evolution import (
    DEFAULT_FLOW_LAW,
    FLOW_LAW_ACTION_DERIVED,
    FLOW_LAW_LEGACY,
    FieldState,
    run_evolution,
    step,
)

pytest.importorskip("sympy")


def _minkowski_state(N=32, dx=0.1, **kw):
    g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
    return FieldState(g=g, B=np.zeros((N, 4)), phi=np.ones(N), dx=dx, **kw)


class TestFixedPoints:
    def test_minkowski_constant_radion_is_exact_fixed_point(self):
        dg, dB, dphi = action_derived_rhs(_minkowski_state())
        assert np.max(np.abs(dg)) == 0.0
        assert np.max(np.abs(dB)) == 0.0
        assert np.max(np.abs(dphi)) == 0.0

    def test_constant_gauge_potential_is_fixed_point(self):
        s = _minkowski_state()
        s.B[:] = np.array([0.3, 0.0, -0.2, 0.1])
        dg, dB, dphi = action_derived_rhs(s)
        assert max(np.max(np.abs(dg)), np.max(np.abs(dB)), np.max(np.abs(dphi))) < 1e-14

    def test_radion_potential_minimum_is_fixed_point(self):
        s = _minkowski_state(m_phi=1.0, phi0=1.0)
        _, _, dphi = action_derived_rhs(s)
        assert np.max(np.abs(dphi)) < 1e-14

    def test_radion_potential_restoring(self):
        U, dU = radion_potential(np.array([1.2]), 1.0, 1.0)
        assert U[0] > 0.0 and dU[0] > 0.0
        U0, dU0 = radion_potential(np.array([1.2]), 0.0, 1.0)
        assert U0[0] == 0.0 and dU0[0] == 0.0


class TestStructure:
    def test_default_flow_law_is_action_derived(self):
        assert DEFAULT_FLOW_LAW == FLOW_LAW_ACTION_DERIVED
        assert FieldState.flat(N=8).flow_law == FLOW_LAW_ACTION_DERIVED

    def test_invalid_flow_law_rejected(self):
        with pytest.raises(ValueError):
            FieldState.flat(N=8, flow_law="not_a_law")

    def test_nonpositive_radion_rejected(self):
        s = _minkowski_state()
        s.phi[3] = 0.0
        with pytest.raises(ValueError):
            action_derived_field_equations(s.g, s.B, s.phi, s.dx)

    def test_kk_backreaction_rejected_under_derived_law(self):
        s = FieldState.flat(N=16, n_kk_modes=3, kk_backreaction_coupling=0.1)
        with pytest.raises(ValueError):
            action_derived_rhs(s)

    def test_no_alpha_dependence(self):
        s = FieldState.flat(N=16, rng=np.random.default_rng(3))
        r1 = action_derived_rhs(s)
        r2 = action_derived_rhs(replace(s, alpha=s.alpha + 5.0))
        for a, b in zip(r1, r2):
            assert np.array_equal(a, b)

    def test_rhs_symmetric_metric(self):
        s = FieldState.flat(N=16, rng=np.random.default_rng(4))
        dg, _, _ = action_derived_rhs(s)
        assert np.allclose(dg, dg.transpose(0, 2, 1))

    def test_surface_declares_flow_as_relaxation(self):
        surf = action_derived_flow_surface()
        assert surf["status"].startswith("ACTION_DERIVED")
        assert "not coordinate time" in surf["flow_parameter_note"]
        assert any("α" in item for item in surf["removed_legacy_elements"])


class TestVerification:
    def test_ricci_crosscheck_non_diagonal(self):
        res = numeric_ricci_crosscheck()
        assert res["ricci_verified"]
        assert res["observed_convergence_order"] > 1.8

    def test_numeric_el_match(self):
        res = numeric_euler_lagrange_match()
        assert res["match_verified"]
        for order in res["observed_convergence_order"].values():
            assert order > 1.8

    def test_symbolic_reduction_reduced_ansatz(self):
        res = symbolic_kk_reduction_check(full=False)
        assert res["reduction_verified"]
        assert res["max_abs_euler_operator_of_difference"] < 1e-10

    @pytest.mark.slow
    def test_symbolic_reduction_full_ansatz(self):
        res = symbolic_kk_reduction_check(full=True)
        assert res["reduction_verified"]


class TestDynamics:
    def test_flat_noise_relaxes_and_stays_finite(self):
        s0 = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(7))
        hist = run_evolution(s0, dt=1e-3, steps=200)
        s1 = hist[-1]
        for arr in (s1.g, s1.B, s1.phi):
            assert np.all(np.isfinite(arr))
        assert np.std(s1.phi) < np.std(s0.phi)

    def test_step_preserves_flow_law(self):
        s0 = FieldState.flat(N=16, flow_law=FLOW_LAW_LEGACY)
        assert step(s0, 1e-3).flow_law == FLOW_LAW_LEGACY
        s1 = FieldState.flat(N=16)
        assert step(s1, 1e-3).flow_law == FLOW_LAW_ACTION_DERIVED
