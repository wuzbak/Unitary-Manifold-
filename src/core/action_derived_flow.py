# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Action-derived field equations and relaxation flow for the KK zero-mode sector.

Action
------
The starting point is the 5D Einstein-Hilbert action on the corrected
Kaluza-Klein ansatz (the same ansatz assembled by
``src.core.metric.assemble_5d_metric``)::

    S₅ = ∫ d⁵x √(−G) R⁽⁵⁾[G] ,
    G_μν = g_μν + λ²φ² B_μ B_ν ,   G_μ5 = λφ² B_μ ,   G_55 = φ² ,

restricted to y-independent zero modes.  With the Einstein-frame metric
g^E_μν = φ g_μν and ψ = ln φ, the reduction is (per unit circle length, up to
a total derivative)::

    √(−G) R⁽⁵⁾ = √(−g_E) [ R_E − (3/2)(∂ψ)² − ¼ λ² φ³ F_μν F^μν ] + ∂(…) ,

with F = dB and all contractions taken with the Lorentzian g_E.  The
identity is checked symbolically by :func:`symbolic_kk_reduction_check`:
the Euler operator of the difference vanishes identically.

An optional radion potential is an *added assumption*, not part of S₅: a 5D
term −∫√(−G) V(φ) with V = ½m_φ²(φ−φ₀)² reduces to −√(−g_E) U with U = V/φ.
It is switched off when ``m_phi = 0``.

Euler-Lagrange equations (Einstein frame, trace-reversed metric form)
---------------------------------------------------------------------
::

    𝓔_μν ≡ R^E_μν − (3/2) ∂_μψ ∂_νψ − ½λ²φ³(F_μα F_ν^α − ¼ g^E_μν F²) − ½ U g^E_μν = 0
    ∇^E_μ (λ² φ³ F^μν) = 0
    3 □_E ψ − ¾ λ² φ³ F² − dU/dψ = 0

Consequences relative to the legacy phenomenological flow: the curvature is
the 4D Einstein-frame Ricci tensor (not the legacy g^μν R^(5)_μν contraction),
there is no free nonminimal coupling α, the gauge coupling is φ³-weighted, the
radion has kinetic normalisation 3/2 and is sourced by the Lorentzian F², and
the scalar stress (3/2)∂ψ∂ψ appears in the metric equation.

Relaxation flow
---------------
The parameter t is not coordinate time, so the action does not supply a
t-evolution.  The flow below is a declared relaxation procedure whose fixed
points are exactly the solutions of the Euler-Lagrange equations::

    ∂_t g^E_μν = −2 𝓔_μν
    ∂_t B_ν    = g^E_νρ ∇^E_μ (λ² φ³ F^μρ)
    ∂_t ψ      = □_E ψ − ¼ λ² φ³ F² − ⅓ dU/dψ

and is mapped to the state variables (g = g_E/φ, φ = e^ψ) by the chain rule.
The zero-mode truncation of the U(1) Kaluza-Klein reduction is a consistent
truncation; higher KK modes are not evolved.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Tuple

import numpy as np

COORD: int = 1


def _grad(f: np.ndarray, dx: float) -> np.ndarray:
    """Second-order central difference on the periodic grid x ∈ S¹ (axis 0)."""
    return (np.roll(f, -1, axis=0) - np.roll(f, 1, axis=0)) / (2.0 * dx)


def _christoffel(g: np.ndarray, g_inv: np.ndarray, dx: float) -> np.ndarray:
    """Γ^σ_μν for a metric depending only on x (index 1)."""
    N, D, _ = g.shape
    dg = np.zeros((N, D, D, D))  # dg[n, ρ, μ, ν] = ∂_ρ g_μν
    dg[:, COORD] = _grad(g, dx)
    term_a = dg                                           # ∂_μ g_νρ  as [n, μ, ν, ρ]
    term_b = dg.transpose(0, 2, 1, 3)                     # ∂_ν g_μρ  as [n, μ, ν, ρ]
    term_c = dg.transpose(0, 2, 3, 1)                     # ∂_ρ g_μν  as [n, μ, ν, ρ]
    combo = term_a + term_b - term_c
    return 0.5 * np.einsum('nsr,nmvr->nsmv', g_inv, combo)


def _ricci(g: np.ndarray, g_inv: np.ndarray, dx: float) -> np.ndarray:
    """R_σν = ∂_ρ Γ^ρ_νσ − ∂_ν Γ^ρ_ρσ + Γ^ρ_ρλ Γ^λ_νσ − Γ^ρ_νλ Γ^λ_ρσ (x-only derivatives)."""
    Gam = _christoffel(g, g_inv, dx)
    N, D = g.shape[0], g.shape[1]
    dGam = _grad(Gam, dx)
    term1 = dGam[:, COORD]                                  # ∂_x Γ^x_νσ  [n, ν, σ]
    trace = np.einsum('nrrs->ns', dGam)                     # ∂_x Γ^ρ_ρσ  [n, σ]
    term2 = np.zeros((N, D, D))
    term2[:, COORD, :] = trace
    contracted = np.einsum('nrrl->nl', Gam)                 # Γ^ρ_ρλ
    term3 = np.einsum('nl,nlvs->nvs', contracted, Gam)
    term4 = np.einsum('nrvl,nlrs->nvs', Gam, Gam)
    ric_vs = term1 - term2 + term3 - term4
    ric = ric_vs.transpose(0, 2, 1)
    return 0.5 * (ric + ric.transpose(0, 2, 1))


def _field_strength(B: np.ndarray, dx: float) -> np.ndarray:
    N, D = B.shape
    F = np.zeros((N, D, D))
    dB = _grad(B, dx)
    F[:, COORD, :] = dB
    F[:, :, COORD] -= dB
    return F


def radion_potential(phi: np.ndarray, m_phi: float, phi0: float) -> Tuple[np.ndarray, np.ndarray]:
    """Return (U, dU/dψ) for U = ½m²(φ−φ₀)²/φ (added assumption; zero when m_phi = 0)."""
    if m_phi == 0.0:
        zero = np.zeros_like(phi)
        return zero, zero
    m2 = m_phi ** 2
    U = 0.5 * m2 * (phi - phi0) ** 2 / phi
    dU_dphi = m2 * (phi - phi0) / phi - 0.5 * m2 * (phi - phi0) ** 2 / phi ** 2
    return U, phi * dU_dphi


def action_derived_field_equations(
    g: np.ndarray,
    B: np.ndarray,
    phi: np.ndarray,
    dx: float,
    lam: float = 1.0,
    m_phi: float = 0.0,
    phi0: float = 1.0,
) -> Dict[str, np.ndarray]:
    """Evaluate the Euler-Lagrange expressions of the reduced action on the grid.

    Returns Einstein-frame quantities:

    ``E_metric``        𝓔_μν (trace-reversed metric equation, lower indices)
    ``G_minus_half_T``  𝓔_μν − ½ g^E_μν tr𝓔 = G_μν − ½T_μν (δS/δg^E_μν = −√|g_E| (G−½T)^μν)
    ``E_gauge_up``      ∇_μ(λ²φ³F^μν)       (δS/δB_ν = √|g_E| · this)
    ``E_psi``           3□ψ − ¾λ²φ³F² − dU/dψ (δS/δψ = √|g_E| · this)
    """
    if np.any(phi <= 0.0):
        raise ValueError('action-derived equations require φ > 0 everywhere (G_55 = φ²).')
    gE = phi[:, None, None] * g
    gE_inv = np.linalg.inv(gE)
    sqrt_g = np.sqrt(np.abs(np.linalg.det(gE)))
    psi = np.log(phi)
    dpsi = np.zeros_like(B)
    dpsi[:, COORD] = _grad(psi, dx)

    ric = _ricci(gE, gE_inv, dx)
    F = _field_strength(B, dx)
    F_up = np.einsum('nai,nbj,nij->nab', gE_inv, gE_inv, F)
    F2 = np.einsum('nij,nij->n', F, F_up)
    FF = np.einsum('nma,nab,nvb->nmv', F, gE_inv, F)
    w = lam ** 2 * phi ** 3
    U, dU_dpsi = radion_potential(phi, m_phi, phi0)

    E_metric = (
        ric
        - 1.5 * np.einsum('nm,nv->nmv', dpsi, dpsi)
        - 0.5 * w[:, None, None] * (FF - 0.25 * gE * F2[:, None, None])
        - 0.5 * U[:, None, None] * gE
    )
    trace = np.einsum('nij,nij->n', gE_inv, E_metric)
    G_minus_half_T = E_metric - 0.5 * gE * trace[:, None, None]

    E_gauge_up = _grad(sqrt_g[:, None] * w[:, None] * F_up[:, COORD, :], dx) / sqrt_g[:, None]
    box_psi = _grad(sqrt_g * np.einsum('nm,nm->n', gE_inv[:, COORD, :], dpsi), dx) / sqrt_g
    E_psi = 3.0 * box_psi - 0.75 * w * F2 - dU_dpsi

    return {
        'g_E': gE,
        'g_E_inv': gE_inv,
        'sqrt_abs_g_E': sqrt_g,
        'E_metric': E_metric,
        'G_minus_half_T': G_minus_half_T,
        'E_gauge_up': E_gauge_up,
        'E_psi': E_psi,
        'F2_lorentzian': F2,
    }


def action_derived_rhs(state: Any) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (∂_t g, ∂_t B, ∂_t φ) for the action-derived relaxation flow."""
    if getattr(state, 'n_kk_modes', 0) > 0 and getattr(state, 'kk_backreaction_coupling', 0.0) > 0.0:
        raise ValueError(
            'The KK-tower backreaction source is not a term of the reduced action; '
            'use flow_law="phenomenological_legacy" to include it.'
        )
    eq = action_derived_field_equations(
        state.g, state.B, state.phi, state.dx,
        lam=state.lam, m_phi=state.m_phi, phi0=state.phi0,
    )
    phi = state.phi
    dgE = -2.0 * eq['E_metric']
    dB = np.einsum('nvr,nr->nv', eq['g_E'], eq['E_gauge_up'])
    dpsi = eq['E_psi'] / 3.0
    dphi = phi * dpsi
    dg = dgE / phi[:, None, None] - state.g * dpsi[:, None, None]
    dg = 0.5 * (dg + dg.transpose(0, 2, 1))
    return dg, dB, dphi


def action_derived_flow_surface() -> Dict[str, Any]:
    """Machine-readable description of the derived flow (replaces the legacy term list)."""
    return {
        'status': 'ACTION_DERIVED_FIELD_EQUATIONS_WITH_DECLARED_RELAXATION_FLOW',
        'action': 'S₅ = ∫ d⁵x √(−G) R⁽⁵⁾[G] on G_μν = g_μν + λ²φ²B_μB_ν, G_μ5 = λφ²B_μ, G_55 = φ²',
        'reduced_action': 'S₄ = ∫ d⁴x √(−g_E) [R_E − (3/2)(∂ ln φ)² − ¼ λ² φ³ F² − U(φ)],  g_E = φ g',
        'added_assumptions': [
            'Optional radion potential U = ½ m_φ² (φ − φ₀)² / φ from a 5D V(φ); not part of S₅ (off when m_phi = 0).',
            'y-independent zero modes only (consistent truncation of the U(1) KK reduction).',
            'Fields depend on the single coordinate x (index 1) on a periodic grid x ∈ S¹; x⁰ is gauge-fixed.',
        ],
        'equations': {
            'metric': {
                'lhs': '∂_t g^E_μν',
                'rhs_terms': ['-2 R^E_μν', '3 ∂_μψ ∂_νψ', 'λ²φ³(F_μα F_ν^α − ¼ g^E_μν F²)', 'U g^E_μν'],
                'classification': 'trace_reversed_euler_lagrange_expression',
            },
            'gauge': {
                'lhs': '∂_t B_ν',
                'rhs_terms': ['g^E_νρ ∇_μ(λ² φ³ F^μρ)'],
                'classification': 'euler_lagrange_expression',
            },
            'scalar': {
                'lhs': '∂_t ψ  (ψ = ln φ)',
                'rhs_terms': ['□_E ψ', '-¼ λ² φ³ F²', '-⅓ dU/dψ'],
                'classification': 'euler_lagrange_expression_divided_by_3',
            },
        },
        'fixed_point_property': 'RHS = 0 at every grid point ⇔ the discretised Euler-Lagrange equations hold.',
        'flow_parameter_note': (
            't is a relaxation parameter, not coordinate time; the action fixes the field equations '
            '(the fixed-point set), not the t-dynamics.'
        ),
        'removed_legacy_elements': [
            'legacy g^μν R^(5)_μν contraction replaced by Einstein-frame R^E_μν',
            'free nonminimal coupling α removed (no α R φ term in the reduced action)',
            'Euclidean component norms replaced by Lorentzian contractions',
            'phenomenological source S[H] replaced by −¼λ²φ³F²',
            'KK-tower backreaction source excluded (not a term of the action)',
        ],
    }


# ---------------------------------------------------------------------------
# Symbolic verification (SymPy)
# ---------------------------------------------------------------------------

def _symbolic_setup(full: bool):
    import sympy as sp

    x = sp.symbols('x')
    lam = sp.symbols('lambda', positive=True)
    if full:
        a, b, c, d, p = [sp.Function(n, positive=True)(x) for n in ['a', 'b', 'c', 'd', 'p']]
        B0, B2 = [sp.Function(n, real=True)(x) for n in ['B0', 'B2']]
        fields = [a, b, c, d, p, B0, B2]
    else:
        a, b, p = [sp.Function(n, positive=True)(x) for n in ['a', 'b', 'p']]
        B2 = sp.Function('B2', real=True)(x)
        c = d = sp.Integer(1)
        B0 = sp.Integer(0)
        fields = [a, b, p, B2]
    coords = [sp.Symbol('t'), x, sp.Symbol('z'), sp.Symbol('w'), sp.Symbol('y')]
    gE = sp.diag(-a, b, c, d)
    Bv = sp.Matrix([B0, 0, B2, 0])
    return sp, x, lam, (a, b, c, d, p, B0, B2), fields, coords, gE, Bv


def _sym_ricci_scalar(sp, G, coords):
    n = G.shape[0]
    Gi = sp.simplify(G.inv())
    dG = [[[sp.diff(G[i, j], coords[k]) for k in range(n)] for j in range(n)] for i in range(n)]
    Gam = [[[sp.simplify(sum(Gi[s, l] * (dG[l][m][q] + dG[l][q][m] - dG[m][q][l]) for l in range(n)) / 2)
             for q in range(n)] for m in range(n)] for s in range(n)]
    R = 0
    for m in range(n):
        for q in range(n):
            ric = 0
            for s in range(n):
                ric += sp.diff(Gam[s][m][q], coords[s]) - sp.diff(Gam[s][m][s], coords[q])
                for l in range(n):
                    ric += Gam[s][s][l] * Gam[l][m][q] - Gam[s][q][l] * Gam[l][m][s]
            R += Gi[m, q] * ric
    return R


def _sym_reduced_lagrangian(sp, x, lam, gE, Bv, p, coords):
    gi = gE.inv()
    F = sp.zeros(4, 4)
    for mu in range(4):
        for nu in range(4):
            F[mu, nu] = (sp.diff(Bv[nu], x) if mu == COORD else 0) - (sp.diff(Bv[mu], x) if nu == COORD else 0)
    F2 = sum(F[m, n] * F[r, s] * gi[m, r] * gi[n, s]
             for m in range(4) for n in range(4) for r in range(4) for s in range(4))
    psi = sp.log(p)
    return sp.sqrt(-gE.det()) * (
        _sym_ricci_scalar(sp, gE, coords[:4])
        - sp.Rational(3, 2) * gi[COORD, COORD] * sp.diff(psi, x) ** 2
        - sp.Rational(1, 4) * lam ** 2 * p ** 3 * F2
    )


def _test_profiles(sp, x, syms):
    a, b, c, d, p, B0, B2 = syms
    prof = {
        a: 1 + sp.sin(x) / 5, b: sp.exp(sp.cos(x) / 7), c: 1 + x ** 2 / 9,
        d: 2 - sp.cos(2 * x) / 4, p: 1 + sp.sin(3 * x) / 6, B0: sp.sin(x) / 3, B2: sp.cos(2 * x) / 5,
    }
    return {k: v for k, v in prof.items() if isinstance(k, sp.Expr) and not k.is_number}


@lru_cache(maxsize=4)
def symbolic_kk_reduction_check(full: bool = False, exact: bool = False) -> Dict[str, Any]:
    """Verify √(−G)R⁽⁵⁾ − √(−g_E)[R_E − (3/2)(∂ψ)² − ¼λ²φ³F²] is a total derivative.

    Uses the Euler operator: a Lagrangian difference is a total derivative iff
    its Euler-Lagrange expressions vanish identically.  The expressions are
    evaluated (30 significant digits) on smooth test profiles at sample points.
    ``full=True`` uses g_E = diag(−a,b,c,d), B = (B0,0,B2,0) (≈30 s);
    the default reduced ansatz uses g_E = diag(−a,b,1,1), B = (0,0,B2,0).
    ``exact=True`` additionally simplifies every Euler expression symbolically
    and reports whether each is identically zero (≈15 s on the reduced ansatz).
    """
    from sympy.calculus.euler import euler_equations

    sp, x, lam, syms, fields, coords, gE, Bv = _symbolic_setup(full)
    p = syms[4]
    g_jordan = gE / p
    G = sp.zeros(5, 5)
    G[:4, :4] = g_jordan + lam ** 2 * p ** 2 * Bv * Bv.T
    for i in range(4):
        G[i, 4] = G[4, i] = lam * p ** 2 * Bv[i]
    G[4, 4] = p ** 2
    L5 = sp.sqrt(-G.det()) * _sym_ricci_scalar(sp, G, coords)
    L4 = _sym_reduced_lagrangian(sp, x, lam, gE, Bv, p, coords)
    eqs = euler_equations(L5 - L4, fields, x)
    prof = _test_profiles(sp, x, syms)
    max_abs = 0.0
    for eq in eqs:
        expr = eq.lhs.subs(prof).doit()
        for xv in (0.3, 1.1, -0.7):
            val = complex(expr.subs({x: xv, lam: sp.Rational(7, 10)}).evalf(30))
            max_abs = max(max_abs, abs(val))
    exact_zero = None
    if exact:
        exact_zero = all(sp.simplify(eq.lhs) == 0 for eq in eqs)
    return {
        'ansatz': 'full_diagonal_two_component' if full else 'reduced_diagonal_one_component',
        'fields_varied': [str(f.func) for f in fields],
        'max_abs_euler_operator_of_difference': max_abs,
        'reduction_verified': bool(max_abs < 1e-10),
        'exact_simplification_performed': bool(exact),
        'exact_identity_verified': exact_zero,
    }


@lru_cache(maxsize=1)
def numeric_euler_lagrange_match(N: int = 160, half_width: float = 1.0) -> Dict[str, Any]:
    """Compare the numerical EL expressions with SymPy's δS₄/δ(field) on smooth profiles.

    Uses the reduced ansatz (g_E = diag(−a,b,1,1), B = (0,0,B2,0)).  The
    numerical side uses second-order finite differences, so the interior
    residual should fall as dx²; the result reports two resolutions.
    """
    from sympy.calculus.euler import euler_equations

    sp, x, lam, syms, fields, coords, gE, Bv = _symbolic_setup(False)
    a, b, _c, _d, p, _B0, B2 = syms
    L4 = _sym_reduced_lagrangian(sp, x, lam, gE, Bv, p, coords)
    eqs = euler_equations(L4, fields, x)
    prof = _test_profiles(sp, x, syms)
    lam_val = 0.7
    exact = {}
    for field, eq in zip(fields, eqs):
        expr = eq.lhs.subs(prof).doit().subs(lam, lam_val)
        exact[str(field.func)] = sp.lambdify(x, expr, 'numpy')
    prof_fns = {str(k.func): sp.lambdify(x, v, 'numpy') for k, v in prof.items()}

    def residuals(n: int) -> Dict[str, float]:
        xs = np.linspace(-half_width, half_width, n)
        dx = float(xs[1] - xs[0])
        av, bv, pv, B2v = (np.broadcast_to(prof_fns[k](xs), xs.shape).astype(float) for k in ('a', 'b', 'p', 'B2'))
        gEn = np.zeros((n, 4, 4))
        gEn[:, 0, 0] = -av
        gEn[:, 1, 1] = bv
        gEn[:, 2, 2] = 1.0
        gEn[:, 3, 3] = 1.0
        Bn = np.zeros((n, 4))
        Bn[:, 2] = B2v
        eq = action_derived_field_equations(gEn / pv[:, None, None], Bn, pv, dx, lam=lam_val)
        s = eq['sqrt_abs_g_E']
        GmT_up = np.einsum('nai,nbj,nij->nab', eq['g_E_inv'], eq['g_E_inv'], eq['G_minus_half_T'])
        numeric = {
            'a': s * GmT_up[:, 0, 0],          # g00 = −a ⇒ δS/δa = +√|g| (G−½T)^00
            'b': -s * GmT_up[:, 1, 1],
            'p': s * eq['E_psi'] / pv,
            'B2': s * eq['E_gauge_up'][:, 2],
        }
        interior = slice(4, n - 4)
        out = {}
        for key, val in numeric.items():
            ref = np.broadcast_to(exact[key](xs), xs.shape).astype(float)
            scale = max(float(np.max(np.abs(ref[interior]))), 1e-12)
            out[key] = float(np.max(np.abs(val[interior] - ref[interior])) / scale)
        return out

    coarse = residuals(N)
    fine = residuals(2 * N - 1)
    orders = {k: float(np.log2(coarse[k] / fine[k])) if fine[k] > 0 else float('inf') for k in coarse}
    return {
        'ansatz': 'reduced_diagonal_one_component',
        'fields': list(coarse),
        'relative_residual_coarse': coarse,
        'relative_residual_fine': fine,
        'observed_convergence_order': orders,
        'match_verified': bool(all(v < 1e-3 for v in fine.values()) and all(o > 1.5 for o in orders.values())),
    }


@lru_cache(maxsize=1)
def numeric_ricci_crosscheck(N: int = 64) -> Dict[str, Any]:
    """Compare :func:`_ricci` with an exact-derivative Ricci tensor on a non-diagonal metric.

    The test metric is a periodic Lorentzian perturbation of η with off-diagonal
    (0,1), (0,2), (1,2) and (2,3) components, so the check covers the general
    index structure that the diagonal EL checks do not exercise.
    """
    import sympy as sp

    x = sp.symbols('x')
    G = sp.Matrix([
        [-1 + sp.sin(x) / 6, sp.cos(x) / 9, sp.sin(2 * x) / 10, 0],
        [sp.cos(x) / 9, 1 + sp.cos(2 * x) / 7, sp.sin(x) / 8, 0],
        [sp.sin(2 * x) / 10, sp.sin(x) / 8, 1 + sp.sin(x) / 5, sp.cos(3 * x) / 11],
        [0, 0, sp.cos(3 * x) / 11, 1 - sp.cos(x) / 6],
    ])
    g_fn = sp.lambdify(x, G, 'numpy')
    d1_fn = sp.lambdify(x, G.diff(x), 'numpy')
    d2_fn = sp.lambdify(x, G.diff(x, 2), 'numpy')

    def exact_ricci(xv: float) -> np.ndarray:
        # Explicit-loop reference with exact x-derivatives (no finite differences).
        g = np.asarray(g_fn(xv), dtype=float)
        gi = np.linalg.inv(g)
        d1 = np.zeros((4, 4, 4))           # d1[k, i, j] = ∂_k g_ij
        d1[COORD] = np.asarray(d1_fn(xv), dtype=float)
        d2 = np.asarray(d2_fn(xv), dtype=float)
        dgi = -gi @ d1[COORD] @ gi         # ∂_x g^ij
        gam = np.zeros((4, 4, 4))
        dgam = np.zeros((4, 4, 4))         # ∂_x Γ^s_mq
        for s_ in range(4):
            for m in range(4):
                for q in range(4):
                    for l in range(4):
                        c = d1[m, l, q] + d1[q, l, m] - d1[l, m, q]
                        dc = ((COORD == m) * d2[l, q] + (COORD == q) * d2[l, m]
                              - (COORD == l) * d2[m, q])
                        gam[s_, m, q] += 0.5 * gi[s_, l] * c
                        dgam[s_, m, q] += 0.5 * (dgi[s_, l] * c + gi[s_, l] * dc)
        ric = np.zeros((4, 4))
        for m in range(4):
            for q in range(4):
                val = dgam[COORD, m, q] - (COORD == q) * sum(dgam[s_, m, s_] for s_ in range(4))
                for s_ in range(4):
                    for l in range(4):
                        val += gam[s_, s_, l] * gam[l, m, q] - gam[s_, q, l] * gam[l, m, s_]
                ric[m, q] = val
        return ric

    def max_err(n: int) -> float:
        xs = np.arange(n) * (2.0 * np.pi / n)
        dx = float(xs[1] - xs[0])
        g = np.stack([np.asarray(g_fn(xv), dtype=float) for xv in xs])
        ref = np.stack([exact_ricci(xv) for xv in xs])
        num = _ricci(g, np.linalg.inv(g), dx)
        return float(np.max(np.abs(num - ref)) / max(float(np.max(np.abs(ref))), 1e-12))

    coarse = max_err(N)
    fine = max_err(2 * N)
    order = float(np.log2(coarse / fine)) if fine > 0 else float('inf')
    return {
        'metric': 'periodic non-diagonal Lorentzian perturbation of η (x ∈ [0, 2π))',
        'relative_error_coarse': coarse,
        'relative_error_fine': fine,
        'observed_convergence_order': order,
        'ricci_verified': bool(fine < 1e-2 and order > 1.5),
    }


__all__ = [
    'action_derived_field_equations',
    'action_derived_flow_surface',
    'action_derived_rhs',
    'numeric_euler_lagrange_match',
    'numeric_ricci_crosscheck',
    'radion_potential',
    'symbolic_kk_reduction_check',
]
