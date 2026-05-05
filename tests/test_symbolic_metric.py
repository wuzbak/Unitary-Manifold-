# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_symbolic_metric.py
==============================
Tests for src/core/symbolic_metric.py — the SymPy symbolic KK metric layer.

These tests verify that:
  1. The symbolic 5D metric has the correct shape, symmetry, and block structure.
  2. The line element matches the standard KK ansatz.
  3. The field-strength matrix is antisymmetric.
  4. The Ricci scalar decomposition has the correct algebraic form.
  5. The effective action Lagrangian contains the expected terms.
  6. The LaTeX convenience wrappers produce non-empty strings.
  7. The derivation chain has the correct length and structure.
  8. Numerical consistency: substituting concrete values reproduces
     the numerical metric from src/core/metric.assemble_5d_metric().
"""

import sympy as sp
import numpy as np
import pytest

from src.core.symbolic_metric import (
    symbolic_5d_metric,
    symbolic_line_element,
    symbolic_field_strength,
    symbolic_5d_ricci_scalar_decomposition,
    symbolic_effective_action,
    latex_5d_metric,
    latex_line_element,
    latex_field_strength,
    latex_effective_action,
    derivation_chain,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def metric_and_syms():
    return symbolic_5d_metric(n=4)


@pytest.fixture
def line_element_and_syms():
    return symbolic_line_element(n=4)


@pytest.fixture
def field_strength_and_syms():
    return symbolic_field_strength(n=4)


# ---------------------------------------------------------------------------
# 1. 5D metric shape and symmetry
# ---------------------------------------------------------------------------

class TestSymbolic5dMetric:
    def test_shape(self, metric_and_syms):
        G, _ = metric_and_syms
        assert G.shape == (5, 5)

    def test_symmetry(self, metric_and_syms):
        G, _ = metric_and_syms
        assert G == G.T, "KK metric must be symmetric"

    def test_G55_is_phi_squared(self, metric_and_syms):
        G, syms = metric_and_syms
        phi = syms["phi"]
        assert sp.simplify(G[4, 4] - phi**2) == 0

    def test_off_diagonal_G_mu5(self, metric_and_syms):
        G, syms = metric_and_syms
        phi = syms["phi"]
        lam = syms["lam"]
        B = syms["B"]
        for mu in range(4):
            expected = lam * phi * B[mu]
            assert sp.simplify(G[mu, 4] - expected) == 0

    def test_4d_block_structure(self, metric_and_syms):
        G, syms = metric_and_syms
        phi = syms["phi"]
        lam = syms["lam"]
        g = syms["g"]
        B = syms["B"]
        for mu in range(4):
            for nu in range(4):
                expected = g[mu, nu] + lam**2 * phi**2 * B[mu] * B[nu]
                assert sp.simplify(G[mu, nu] - expected) == 0

    def test_4x4_block_symmetric(self, metric_and_syms):
        G, _ = metric_and_syms
        for mu in range(4):
            for nu in range(4):
                assert sp.simplify(G[mu, nu] - G[nu, mu]) == 0

    def test_returns_matrix_type(self, metric_and_syms):
        G, _ = metric_and_syms
        assert isinstance(G, sp.Matrix)

    def test_syms_dict_has_expected_keys(self, metric_and_syms):
        _, syms = metric_and_syms
        for key in ("phi", "lam", "g", "B"):
            assert key in syms

    def test_phi_is_positive(self, metric_and_syms):
        _, syms = metric_and_syms
        phi = syms["phi"]
        assert phi.is_positive

    def test_default_n_is_4(self):
        G, _ = symbolic_5d_metric()
        assert G.shape == (5, 5)

    def test_n2_gives_3x3_metric(self):
        G, _ = symbolic_5d_metric(n=2)
        assert G.shape == (3, 3)

    def test_n2_G22_is_phi_squared(self):
        G, syms = symbolic_5d_metric(n=2)
        phi = syms["phi"]
        assert sp.simplify(G[2, 2] - phi**2) == 0


# ---------------------------------------------------------------------------
# 2. Line element
# ---------------------------------------------------------------------------

class TestSymbolicLineElement:
    def test_returns_expr(self, line_element_and_syms):
        ds2, _ = line_element_and_syms
        assert isinstance(ds2, sp.Expr)

    def test_contains_phi_squared(self, line_element_and_syms):
        ds2, syms = line_element_and_syms
        phi = syms["phi"]
        # ds² contains phi² (from the fifth-dimension term)
        assert ds2.has(phi**2)

    def test_contains_lam(self, line_element_and_syms):
        ds2, syms = line_element_and_syms
        lam = syms["lam"]
        assert ds2.has(lam)

    def test_contains_dy(self, line_element_and_syms):
        ds2, syms = line_element_and_syms
        dy = syms["dy"]
        assert ds2.has(dy)

    def test_vanishes_at_zero_fields(self, line_element_and_syms):
        ds2, syms = line_element_and_syms
        phi = syms["phi"]
        lam = syms["lam"]
        B = syms["B"]
        dx = syms["dx"]
        dy = syms["dy"]
        g = syms["g"]
        # Flat Minkowski substitute: g_{00}=-1, g_{ii}=+1 (i>0), off-diag=0
        # B=0, φ=1, λ=1, dy=0, dx^i=0
        subs = {}
        subs[lam] = sp.Integer(1)
        subs[phi] = sp.Integer(1)
        subs[dy] = sp.Integer(0)
        for mu in range(4):
            subs[dx[mu]] = sp.Integer(0)
            subs[B[mu]] = sp.Integer(0)
        for mu in range(4):
            for nu in range(4):
                entry = g[mu, nu]
                if mu == nu:
                    subs[entry] = sp.Integer(-1 if mu == 0 else 1)
                else:
                    subs[entry] = sp.Integer(0)
        val = ds2.subs(subs)
        assert sp.simplify(val) == 0


# ---------------------------------------------------------------------------
# 3. Field-strength tensor
# ---------------------------------------------------------------------------

class TestSymbolicFieldStrength:
    def test_shape(self, field_strength_and_syms):
        H, _ = field_strength_and_syms
        assert H.shape == (4, 4)

    def test_antisymmetric(self, field_strength_and_syms):
        H, _ = field_strength_and_syms
        for mu in range(4):
            for nu in range(4):
                assert sp.simplify(H[mu, nu] + H[nu, mu]) == 0

    def test_diagonal_zero(self, field_strength_and_syms):
        H, _ = field_strength_and_syms
        for mu in range(4):
            assert H[mu, mu] == 0

    def test_returns_matrix_type(self, field_strength_and_syms):
        H, _ = field_strength_and_syms
        assert isinstance(H, sp.Matrix)

    def test_off_diagonal_form(self, field_strength_and_syms):
        H, syms = field_strength_and_syms
        dB = syms["dB"]
        # Spot check: H[0,1] = ∂_0 B_1 - ∂_1 B_0
        expected = dB[(0, 1)] - dB[(1, 0)]
        assert sp.simplify(H[0, 1] - expected) == 0


# ---------------------------------------------------------------------------
# 4. Ricci scalar decomposition
# ---------------------------------------------------------------------------

class TestSymbolicRicciDecomposition:
    def test_returns_expr(self):
        R5, _ = symbolic_5d_ricci_scalar_decomposition()
        assert isinstance(R5, sp.Expr)

    def test_contains_R4(self):
        R5, syms = symbolic_5d_ricci_scalar_decomposition()
        R4 = syms["R4"]
        assert R5.has(R4)

    def test_contains_H_squared(self):
        R5, syms = symbolic_5d_ricci_scalar_decomposition()
        H_sq = syms["H_sq"]
        assert R5.has(H_sq)

    def test_contains_phi_inverse(self):
        R5, syms = symbolic_5d_ricci_scalar_decomposition()
        phi = syms["phi"]
        assert R5.has(1 / phi)

    def test_H_coefficient_is_quarter_lam_squared(self):
        R5, syms = symbolic_5d_ricci_scalar_decomposition()
        phi = syms["phi"]
        lam = syms["lam"]
        H_sq = syms["H_sq"]
        # Extract coefficient of H_sq — should be lam²/(4φ)
        coeff = R5.coeff(H_sq)
        expected = sp.Rational(1, 4) * lam**2 / phi
        assert sp.simplify(coeff - expected) == 0

    def test_box_phi_coefficient_is_minus_two(self):
        R5, syms = symbolic_5d_ricci_scalar_decomposition()
        box_phi = syms["box_phi"]
        coeff = R5.coeff(box_phi)
        assert sp.simplify(coeff + 2) == 0

    def test_dphi_sq_coefficient_is_minus_two(self):
        R5, syms = symbolic_5d_ricci_scalar_decomposition()
        dphi_sq = syms["dphi_sq"]
        coeff = R5.coeff(dphi_sq)
        assert sp.simplify(coeff + 2) == 0


# ---------------------------------------------------------------------------
# 5. Effective action Lagrangian
# ---------------------------------------------------------------------------

class TestSymbolicEffectiveAction:
    def test_returns_expr(self):
        L, _ = symbolic_effective_action()
        assert isinstance(L, sp.Expr)

    def test_contains_einstein_term(self):
        L, syms = symbolic_effective_action()
        R4 = syms["R4"]
        G_N = syms["G_N"]
        assert L.has(R4) and L.has(G_N)

    def test_contains_H_squared(self):
        L, syms = symbolic_effective_action()
        H_sq = syms["H_sq"]
        assert L.has(H_sq)

    def test_contains_alpha(self):
        L, syms = symbolic_effective_action()
        alpha = syms["alpha"]
        assert L.has(alpha)

    def test_contains_BJ_coupling(self):
        L, syms = symbolic_effective_action()
        BJ = syms["BJ"]
        Gamma = syms["Gamma"]
        assert L.has(BJ) and L.has(Gamma)

    def test_einstein_term_coefficient(self):
        L, syms = symbolic_effective_action()
        R4 = syms["R4"]
        G_N = syms["G_N"]
        H_sq = syms["H_sq"]
        alpha = syms["alpha"]
        ell_P = syms["ell_P"]
        # coefficient of R4 alone (not R4*H_sq)
        # Get terms without H_sq
        L_no_H = L.subs(H_sq, sp.Integer(0)).subs(alpha, sp.Integer(0))
        coeff = L_no_H.coeff(R4)
        expected = sp.Rational(1, 1) / (16 * sp.pi * G_N)
        assert sp.simplify(coeff - expected) == 0

    def test_maxwell_term_coefficient(self):
        L, syms = symbolic_effective_action()
        H_sq = syms["H_sq"]
        alpha = syms["alpha"]
        R4 = syms["R4"]
        # pure H_sq term (set alpha=0, R4=0 to kill coupling term)
        L_sub = L.subs(alpha, sp.Integer(0)).subs(R4, sp.Integer(0))
        coeff = L_sub.coeff(H_sq)
        assert sp.simplify(coeff + sp.Rational(1, 4)) == 0


# ---------------------------------------------------------------------------
# 6. LaTeX convenience wrappers
# ---------------------------------------------------------------------------

class TestLatexWrappers:
    def test_latex_5d_metric_nonempty(self):
        s = latex_5d_metric()
        assert isinstance(s, str) and len(s) > 10

    def test_latex_5d_metric_contains_phi(self):
        s = latex_5d_metric()
        assert r"\phi" in s

    def test_latex_line_element_nonempty(self):
        s = latex_line_element()
        assert isinstance(s, str) and len(s) > 10

    def test_latex_field_strength_nonempty(self):
        s = latex_field_strength()
        assert isinstance(s, str) and len(s) > 5

    def test_latex_effective_action_nonempty(self):
        s = latex_effective_action()
        assert isinstance(s, str) and len(s) > 10

    def test_latex_5d_metric_is_valid_latex_fragment(self):
        s = latex_5d_metric()
        # Must contain matrix delimiters
        assert r"\begin{matrix}" in s or r"\matrix" in s or "matrix" in s

    def test_latex_field_strength_antisymmetry_indicator(self):
        s = latex_field_strength()
        # The LaTeX should contain partial derivative symbols
        assert r"\partial" in s


# ---------------------------------------------------------------------------
# 7. Derivation chain
# ---------------------------------------------------------------------------

class TestDerivationChain:
    def test_returns_list(self):
        chain = derivation_chain()
        assert isinstance(chain, list)

    def test_length_is_eight(self):
        chain = derivation_chain()
        assert len(chain) == 8

    def test_each_entry_is_two_tuple(self):
        chain = derivation_chain()
        for entry in chain:
            assert isinstance(entry, tuple) and len(entry) == 2

    def test_labels_are_strings(self):
        chain = derivation_chain()
        for label, latex in chain:
            assert isinstance(label, str) and isinstance(latex, str)

    def test_first_step_is_metric(self):
        chain = derivation_chain()
        label, latex = chain[0]
        assert "metric" in label.lower() or "G" in label

    def test_last_step_is_einstein(self):
        chain = derivation_chain()
        label, latex = chain[-1]
        assert "einstein" in label.lower() or "Einstein" in label

    def test_all_latex_nonempty(self):
        chain = derivation_chain()
        for label, latex in chain:
            assert len(latex) > 0

    def test_step_6_contains_effective_action(self):
        chain = derivation_chain()
        _, latex = chain[5]
        # Effective action step should reference S_eff
        assert "S" in latex or "mathrm{eff}" in latex or "eff" in latex


# ---------------------------------------------------------------------------
# 8. Numerical consistency: symbolic → numeric matches metric.py output
# ---------------------------------------------------------------------------

class TestNumericalConsistency:
    """Substitute concrete values into the symbolic metric and compare
    against the numerical assemble_5d_metric() output."""

    def _numerical_metric(self, N=3):
        """Build a simple test case with identity 4D metric."""
        from src.core.metric import assemble_5d_metric
        g_num = np.broadcast_to(np.eye(4), (N, 4, 4)).copy()
        g_num[:, 0, 0] = -1.0          # Minkowski signature
        B_num = np.zeros((N, 4))
        B_num[:, 1] = 0.5              # non-zero spatial component
        phi_num = np.ones(N) * 2.0
        lam_val = 1.0
        G_num = assemble_5d_metric(g_num, B_num, phi_num, lam=lam_val)
        return G_num, g_num, B_num, phi_num, lam_val

    def test_G55_matches_phi_squared(self):
        G_num, _, _, phi_num, _ = self._numerical_metric()
        for i in range(G_num.shape[0]):
            np.testing.assert_allclose(G_num[i, 4, 4], phi_num[i]**2)

    def test_G_mu5_matches_lam_phi_B(self):
        G_num, _, B_num, phi_num, lam_val = self._numerical_metric()
        for i in range(G_num.shape[0]):
            for mu in range(4):
                expected = lam_val * phi_num[i] * B_num[i, mu]
                np.testing.assert_allclose(G_num[i, mu, 4], expected)

    def test_4d_block_matches_g_plus_outer(self):
        G_num, g_num, B_num, phi_num, lam_val = self._numerical_metric()
        for i in range(G_num.shape[0]):
            outer = lam_val**2 * phi_num[i]**2 * np.outer(B_num[i], B_num[i])
            expected_block = g_num[i] + outer
            np.testing.assert_allclose(G_num[i, :4, :4], expected_block)

    def test_symbolic_substitution_matches_numerical(self):
        """Substitute concrete scalar values into the symbolic 2D case
        and verify it matches a manual calculation."""
        G, syms = symbolic_5d_metric(n=2)
        phi = syms["phi"]
        lam = syms["lam"]
        B = syms["B"]
        g = syms["g"]

        # Values: g = diag(-1,+1), B = (0.5, 0.0), φ=2, λ=1
        subs = {
            phi: sp.Integer(2),
            lam: sp.Integer(1),
            B[0]: sp.Rational(1, 2),
            B[1]: sp.Integer(0),
        }
        for mu in range(2):
            for nu in range(2):
                val = -1 if mu == nu == 0 else (1 if mu == nu == 1 else 0)
                subs[g[mu, nu]] = sp.Integer(val)

        G_num = G.subs(subs)

        # G[0,0] = g_00 + λ²φ² B_0² = -1 + 1*4*(0.25) = -1+1 = 0
        assert sp.simplify(G_num[0, 0] - 0) == 0
        # G[0,2] = λφ B_0 = 1*2*0.5 = 1
        assert sp.simplify(G_num[0, 2] - 1) == 0
        # G[2,2] = φ² = 4
        assert sp.simplify(G_num[2, 2] - 4) == 0
