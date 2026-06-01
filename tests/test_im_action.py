"""tests/test_im_action.py
===========================
Tests for src/core/im_action.py

Verifies:
- Im(S₄) = ∫ Bμ J^μ d⁴x is computed correctly from KK fields
- The canonical momentum is correctly extracted
- The derivation step sequence is well-formed
- The gap status functions return honest summaries
"""

import numpy as np
import pytest

from src.core.im_action import (
    im_effective_action,
    im_action_from_kk_reduction,
    canonical_momentum_phi,
    ccr_residual,
    schrodinger_derivation_steps,
    gap3_forward_derivation_chain,
    stationary_phase_hamilton_jacobi_residual,
    polar_decomposition,
    polar_schrodinger_residuals,
    gap1_status,
    gap3_status,
)


# ---------------------------------------------------------------------------
# im_effective_action
# ---------------------------------------------------------------------------

class TestImEffectiveAction:
    def test_returns_float(self):
        N, dx = 8, 0.1
        B     = np.random.randn(N, 4) * 0.1
        J_inf = np.random.randn(N, 4) * 0.05
        result = im_effective_action(B, J_inf, dx)
        assert isinstance(result, float)

    def test_zero_for_zero_B(self):
        N, dx = 8, 0.1
        B     = np.zeros((N, 4))
        J_inf = np.ones((N, 4))
        assert im_effective_action(B, J_inf, dx) == 0.0

    def test_zero_for_zero_J(self):
        N, dx = 8, 0.1
        B     = np.ones((N, 4))
        J_inf = np.zeros((N, 4))
        assert im_effective_action(B, J_inf, dx) == 0.0

    def test_linearity_in_B(self):
        """Im(S₄) scales linearly with B amplitude."""
        N, dx = 16, 0.1
        B     = np.random.randn(N, 4) * 0.1
        J_inf = np.random.randn(N, 4) * 0.05
        s1 = im_effective_action(B,     J_inf, dx)
        s2 = im_effective_action(2 * B, J_inf, dx)
        np.testing.assert_allclose(s2, 2 * s1, rtol=1e-12)

    def test_antisymmetry_under_B_sign_flip(self):
        """Flipping sign of B flips sign of Im(S₄)."""
        N, dx = 8, 0.1
        B     = np.random.randn(N, 4) * 0.1
        J_inf = np.random.randn(N, 4) * 0.05
        np.testing.assert_allclose(
            im_effective_action(-B, J_inf, dx),
            -im_effective_action(B, J_inf, dx),
            rtol=1e-12,
        )

    def test_scales_with_dx(self):
        """Im(S₄) scales with grid spacing (volume element)."""
        N = 8
        B     = np.random.randn(N, 4) * 0.1
        J_inf = np.random.randn(N, 4) * 0.05
        s1 = im_effective_action(B, J_inf, dx=0.1)
        s2 = im_effective_action(B, J_inf, dx=0.2)
        np.testing.assert_allclose(s2, 2 * s1, rtol=1e-12)


# ---------------------------------------------------------------------------
# im_action_from_kk_reduction
# ---------------------------------------------------------------------------

class TestImActionFromKKReduction:
    def test_returns_float(self):
        N, dx = 8, 0.1
        B   = np.random.randn(N, 4) * 0.1
        phi = np.ones(N)
        u4  = np.zeros((N, 4)); u4[:, 0] = 1.0
        result = im_action_from_kk_reduction(B, phi, u4, dx)
        assert isinstance(result, float)

    def test_matches_im_effective_action(self):
        """Must be consistent with im_effective_action(B, φ²u, dx)."""
        N, dx = 8, 0.1
        B   = np.random.randn(N, 4) * 0.1
        phi = 1.5 * np.ones(N)
        u4  = np.zeros((N, 4)); u4[:, 0] = 1.0; u4[:, 1] = 0.2
        # Expected: J^μ = φ² u^μ
        J_inf = phi[:, None]**2 * u4
        expected = im_effective_action(B, J_inf, dx)
        result   = im_action_from_kk_reduction(B, phi, u4, dx)
        np.testing.assert_allclose(result, expected, rtol=1e-12)

    def test_scales_with_phi_squared(self):
        """Im(S₄) scales as φ² (since J^μ = φ²u^μ)."""
        N, dx = 8, 0.1
        B  = np.random.randn(N, 4) * 0.1
        u4 = np.zeros((N, 4)); u4[:, 0] = 1.0
        s1 = im_action_from_kk_reduction(B, np.ones(N),        u4, dx)
        s2 = im_action_from_kk_reduction(B, np.sqrt(2)*np.ones(N), u4, dx)
        np.testing.assert_allclose(s2, 2 * s1, rtol=1e-10)


# ---------------------------------------------------------------------------
# canonical_momentum_phi
# ---------------------------------------------------------------------------

class TestCanonicalMomentumPhi:
    def test_returns_copy(self):
        dphi = np.array([1.0, 2.0, 3.0])
        pi   = canonical_momentum_phi(dphi)
        assert pi is not dphi  # should be a copy
        np.testing.assert_allclose(pi, dphi)

    def test_values(self):
        dphi = np.linspace(0.1, 1.0, 10)
        pi   = canonical_momentum_phi(dphi)
        np.testing.assert_allclose(pi, dphi, rtol=1e-12)


# ---------------------------------------------------------------------------
# ccr_residual
# ---------------------------------------------------------------------------

class TestCCRResidual:
    def test_returns_dict(self):
        phi    = np.random.randn(16)
        pi_phi = np.random.randn(16)
        result = ccr_residual(phi, pi_phi, dx=0.1)
        assert 'diagonal_mean'   in result
        assert 'off_diag_mean'   in result
        assert 'canonical_ratio' in result

    def test_all_values_finite(self):
        phi    = np.random.randn(16)
        pi_phi = np.random.randn(16)
        result = ccr_residual(phi, pi_phi, dx=0.1)
        for v in result.values():
            assert np.isfinite(v), f"Non-finite CCR residual value: {v}"


# ---------------------------------------------------------------------------
# schrodinger_derivation_steps
# ---------------------------------------------------------------------------

class TestSchrodingerDerivationSteps:
    def test_returns_five_steps(self):
        steps = schrodinger_derivation_steps()
        assert len(steps) == 5

    def test_each_step_has_required_keys(self):
        required = {'step', 'name', 'input', 'output', 'type', 'location'}
        for s in schrodinger_derivation_steps():
            missing = required - set(s.keys())
            assert not missing, f"Step {s['step']} missing keys: {missing}"

    def test_exactly_one_postulate(self):
        """Only one step should be type=POSTULATE — the CCR."""
        steps = schrodinger_derivation_steps()
        postulates = [s for s in steps if s['type'] == 'POSTULATE']
        assert len(postulates) == 1, (
            f"Expected exactly 1 POSTULATE step, found {len(postulates)}"
        )

    def test_postulate_is_step_2(self):
        """The quantisation postulate must be step 2."""
        steps = schrodinger_derivation_steps()
        postulate = [s for s in steps if s['type'] == 'POSTULATE'][0]
        assert postulate['step'] == 2

    def test_step_1_is_derived(self):
        """Step 1 (KK reduction → Im(S₄)) must be DERIVED, not postulate."""
        steps = schrodinger_derivation_steps()
        step1 = [s for s in steps if s['step'] == 1][0]
        assert step1['type'] == 'DERIVED'

    def test_step_5_output_contains_schrodinger(self):
        steps = schrodinger_derivation_steps()
        step5 = [s for s in steps if s['step'] == 5][0]
        # Accept the equation itself or any spelling of Schrödinger
        out = step5['output']
        assert ('ψ' in out or 'psi' in out.lower() or
                'equation' in out.lower() or
                'SE' in out)


class TestGap3ExecutableMath:
    def test_forward_chain_marks_single_explicit_postulate(self):
        chain = gap3_forward_derivation_chain()
        assert chain['overall_status'] == 'PARTIALLY_RESOLVED_WITH_EXPLICIT_POSTULATE'
        assert chain['postulate_count'] == 1
        statuses = {step['status'] for step in chain['steps'].values()}
        assert 'POSTULATE' in statuses
        assert chain['steps'][1]['status'] == 'IMPLEMENTED'
        assert chain['steps'][4]['symbol'] == 'stationary_phase_hamilton_jacobi_residual'
        assert chain['steps'][5]['symbol'] == 'polar_schrodinger_residuals'

    def test_stationary_phase_hamilton_jacobi_free_particle(self):
        mass = 2.0
        momentum = 3.0
        grad_S = np.full(16, momentum)
        dS_dt = np.full(16, -(momentum**2) / (2.0 * mass))
        residual = stationary_phase_hamilton_jacobi_residual(
            dS_dt, grad_S, potential=0.0, mass=mass,
        )
        np.testing.assert_allclose(residual, 0.0, atol=1e-12)

    def test_stationary_phase_hamilton_jacobi_multi_gradient(self):
        mass = 5.0
        grad_S = np.array([[3.0, 4.0], [5.0, 12.0]])
        potential = np.array([1.0, -2.0])
        kinetic = np.array([25.0, 169.0]) / (2.0 * mass)
        dS_dt = -(kinetic + potential)
        residual = stationary_phase_hamilton_jacobi_residual(
            dS_dt, grad_S, potential=potential, mass=mass,
        )
        np.testing.assert_allclose(residual, 0.0, atol=1e-12)

    def test_polar_decomposition_recovers_amplitude_and_phase(self):
        x = np.linspace(0.0, 1.0, 32)
        amplitude = 1.0 + 0.1 * x
        phase = 0.25 + 0.5 * x
        psi = amplitude * np.exp(1j * phase)
        A, S = polar_decomposition(psi)
        np.testing.assert_allclose(A, amplitude, rtol=1e-12)
        np.testing.assert_allclose(S, phase, rtol=1e-12)

    def test_polar_schrodinger_residuals_free_plane_wave(self):
        mass = 2.0
        momentum = 3.0
        x = np.linspace(-1.0, 1.0, 81)
        dx = x[1] - x[0]
        amplitude = np.ones_like(x)
        phase = momentum * x
        dS_dt = np.full_like(x, -(momentum**2) / (2.0 * mass))
        residuals = polar_schrodinger_residuals(
            amplitude=amplitude,
            dA_dt=0.0,
            phase=phase,
            dS_dt=dS_dt,
            potential=0.0,
            dx=dx,
            mass=mass,
        )
        np.testing.assert_allclose(
            residuals['real_hamilton_jacobi_residual'], 0.0, atol=1e-12,
        )
        np.testing.assert_allclose(
            residuals['imaginary_continuity_residual'], 0.0, atol=1e-12,
        )
        np.testing.assert_allclose(residuals['quantum_potential'], 0.0, atol=1e-12)

    def test_polar_schrodinger_residuals_reject_zero_amplitude(self):
        with pytest.raises(ValueError, match='amplitude'):
            polar_schrodinger_residuals(
                amplitude=np.array([1.0, 0.0, 1.0]),
                dA_dt=0.0,
                phase=np.array([0.0, 0.1, 0.2]),
                dS_dt=0.0,
                potential=0.0,
                dx=0.1,
            )


# ---------------------------------------------------------------------------
# gap status strings
# ---------------------------------------------------------------------------

class TestGapStatusStrings:
    def test_gap1_status_mentions_resolved(self):
        s = gap1_status()
        assert 'RESOLVED' in s
        assert 'REMAINS' in s

    def test_gap3_status_matches_forward_chain_boundary(self):
        s = gap3_status()
        chain = gap3_forward_derivation_chain()
        assert 'PARTIALLY RESOLVED' in s
        assert 'executable residuals' in s
        assert 'single postulate' in s
        assert chain['overall_status'].startswith('PARTIALLY_RESOLVED')
        assert chain['postulate_count'] == 1
        implemented = [
            step for step in chain['steps'].values()
            if step['status'] == 'IMPLEMENTED'
        ]
        assert len(implemented) == 3

    def test_gap1_mentions_postulate(self):
        s = gap1_status()
        assert 'postulate' in s.lower() or 'CCR' in s
