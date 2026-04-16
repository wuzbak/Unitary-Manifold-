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


# ---------------------------------------------------------------------------
# gap status strings
# ---------------------------------------------------------------------------

class TestGapStatusStrings:
    def test_gap1_status_mentions_resolved(self):
        s = gap1_status()
        assert 'RESOLVED' in s
        assert 'REMAINS' in s

    def test_gap3_status_mentions_resolved(self):
        s = gap3_status()
        assert 'RESOLVED' in s

    def test_gap1_mentions_postulate(self):
        s = gap1_status()
        assert 'postulate' in s.lower() or 'CCR' in s
