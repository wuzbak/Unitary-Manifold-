# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Executable variational (gradient-flow / Helmholtz) audit of the implemented flow.

Framing
-------
The implemented evolution (``src.core.evolution``) is first order in a flow
parameter ``t`` that is explicitly *not* coordinate time x⁰.  A first-order
flow cannot be the second-order Euler-Lagrange system of a Lorentzian action in
x⁰, so the variational class it can belong to is a gradient flow

    ∂_t X = −G⁻¹ δE/δX ,

i.e. the flow vector is the Euler-Lagrange expression of a functional E with
respect to a field-space metric G, and fixed points of the flow are stationary
points of E.  For a constant (state-independent) metric G a necessary condition
is the Helmholtz/integrability condition: G·J must be symmetric, where J is the
Jacobian of the discrete right-hand side.

What this module checks
-----------------------
1. Scalar sector with (g, B) frozen and the curvature contraction R and the
   source S[H] treated as external fields: the implemented ∂_t φ equals
   −(1/dx) ∂E_φ/∂φ for an explicit discrete functional E_φ.
2. Gauge sector with g frozen: the implemented ∂_t B equals
   −(1/dx) ∂E_B/∂B for the discrete Maxwell energy E_B = ¼λ² Σ dx H_ab H^ab at
   interior grid points; one-sided boundary stencils break the match.
3. Coupled system: ∂F_B/∂φ ≡ 0 (the B equation contains no φ) while
   ∂F_φ/∂B ≠ 0 whenever H ≠ 0 (through S[H] = ½|H|²).  For any constant
   block-diagonal positive-definite G this violates the Helmholtz condition,
   so the implemented coupled flow is not a gradient flow of any C² functional
   with respect to any such metric.
4. Optional (expensive) interior blockwise Jacobian asymmetry table under the
   trace (component L²) metric.

Scope guard: these are statements about the discretised implemented flow on
the stated 1-D domain.  They do not exclude state-dependent or non
block-diagonal field-space metrics, and they do not earn closure.  The result
replaces template alignment with an executable mismatch certificate; it is a
refutation in the stated class, not a derivation.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List, Tuple

import numpy as np

from src.core.evolution import FieldState, _compute_rhs_python_reference
from src.core.metric import compute_curvature, field_strength

AUDIT_N: int = 12
AUDIT_DX: float = 0.2
AUDIT_SEED: int = 7
FD_STEP: float = 1e-6
MATCH_TOLERANCE: float = 1e-6
INTERIOR_MARGIN: int = 4

_IU = np.triu_indices(4)


def audit_reference_state(N: int = AUDIT_N, dx: float = AUDIT_DX, seed: int = AUDIT_SEED) -> FieldState:
    """Return the deterministic non-trivial state used by the audit.

    The state has a perturbed metric, non-zero gauge field (so H ≠ 0), a
    non-constant radion, an active stabilisation mass, and the KK-tower
    backreaction source disabled (that mean-field source is outside the
    audited perimeter).
    """
    rng = np.random.default_rng(seed)
    state = FieldState.flat(N=N, dx=dx, rng=rng)
    g = state.g + 0.01 * rng.standard_normal((N, 4, 4))
    g = 0.5 * (g + g.transpose(0, 2, 1))
    return FieldState(
        g=g,
        B=0.05 * rng.standard_normal((N, 4)),
        phi=1.0 + 0.05 * rng.standard_normal(N),
        dx=dx,
        lam=1.0,
        alpha=0.1,
        phi0=1.0,
        m_phi=0.3,
        n_kk_modes=0,
        kk_backreaction_coupling=0.0,
    )


def _with_fields(state: FieldState, g: np.ndarray, B: np.ndarray, phi: np.ndarray) -> FieldState:
    return FieldState(
        g=g, B=B, phi=phi, t=state.t, dx=state.dx, lam=state.lam, alpha=state.alpha,
        phi0=state.phi0, m_phi=state.m_phi, n_kk_modes=state.n_kk_modes,
        kk_backreaction_coupling=state.kk_backreaction_coupling,
    )


# ---------------------------------------------------------------------------
# Sector functionals
# ---------------------------------------------------------------------------

def scalar_sector_functional(state: FieldState, phi: np.ndarray, R: np.ndarray, S: np.ndarray) -> float:
    """Discrete E_φ = Σ dx [½(Δ⁺φ)² − ½αRφ² − Sφ + ½m²(φ−φ₀)²] (periodic forward difference)."""
    dphi = (np.roll(phi, -1) - phi) / state.dx
    density = (
        0.5 * dphi ** 2
        - 0.5 * state.alpha * R * phi ** 2
        - S * phi
        + 0.5 * state.m_phi ** 2 * (phi - state.phi0) ** 2
    )
    return float(state.dx * np.sum(density))


def gauge_sector_functional(state: FieldState, B: np.ndarray) -> float:
    """Discrete Maxwell energy E_B = ¼λ² Σ dx H_ab H^ab at frozen g."""
    H = field_strength(B, state.dx)
    g_inv = np.linalg.inv(state.g)
    H_up = np.einsum('nai,nbj,nij->nab', g_inv, g_inv, H)
    return float(0.25 * state.lam ** 2 * state.dx * np.sum(H * H_up))


def _fd_gradient(fun, x: np.ndarray, h: float = FD_STEP) -> np.ndarray:
    flat = x.ravel()
    grad = np.zeros_like(flat)
    for j in range(flat.size):
        e = np.zeros_like(flat)
        e[j] = h
        grad[j] = (fun((flat + e).reshape(x.shape)) - fun((flat - e).reshape(x.shape))) / (2.0 * h)
    return grad.reshape(x.shape)


def scalar_sector_gradient_check(state: FieldState | None = None) -> Dict[str, Any]:
    """Check ∂_t φ = −(1/dx) ∂E_φ/∂φ with R and S[H] frozen."""
    state = state or audit_reference_state()
    if state.kk_backreaction_coupling > 0.0 and state.n_kk_modes > 0:
        raise ValueError('scalar-sector audit requires the KK backreaction source to be disabled')
    _, _, _, R = compute_curvature(state.g, state.B, state.phi, state.dx, lam=state.lam)
    H = field_strength(state.B, state.dx)
    S = 0.5 * np.einsum('nij,nij->n', H, H)
    grad = _fd_gradient(lambda p: scalar_sector_functional(state, p, R, S), state.phi)
    implemented = _compute_rhs_python_reference(state)[2]
    residual = implemented + grad / state.dx
    scale = float(np.max(np.abs(implemented))) or 1.0
    max_rel = float(np.max(np.abs(residual)) / scale)
    return {
        'sector': 'scalar',
        'frozen_background': ['g_μν', 'B_μ', 'R (legacy contraction)', 'S[H]'],
        'functional': 'E_φ = ∫ dx [½(∂φ)² − ½ α R φ² − S[H] φ + ½ m_φ² (φ − φ₀)²]',
        'max_abs_residual': float(np.max(np.abs(residual))),
        'max_relative_residual': max_rel,
        'gradient_flow_match': bool(max_rel < MATCH_TOLERANCE),
        'scope_note': (
            'Match holds only with R and S[H] treated as external. In the coupled flow R depends on φ '
            'through G_55 = φ², which the frozen-background functional does not capture.'
        ),
    }


def gauge_sector_gradient_check(state: FieldState | None = None) -> Dict[str, Any]:
    """Check ∂_t B = −(1/dx) ∂E_B/∂B at frozen g; report interior and boundary residuals."""
    state = state or audit_reference_state()
    grad = _fd_gradient(lambda b: gauge_sector_functional(state, b), state.B)
    implemented = _compute_rhs_python_reference(state)[1]
    residual = implemented + grad / state.dx
    N = state.B.shape[0]
    interior = slice(INTERIOR_MARGIN - 1, N - INTERIOR_MARGIN + 1)
    scale = float(np.max(np.abs(implemented))) or 1.0
    interior_rel = float(np.max(np.abs(residual[interior])) / scale)
    boundary_rows = np.r_[0:INTERIOR_MARGIN - 1, N - INTERIOR_MARGIN + 1:N]
    boundary_rel = float(np.max(np.abs(residual[boundary_rows])) / scale)
    return {
        'sector': 'gauge',
        'frozen_background': ['g_μν', 'φ'],
        'functional': 'E_B = ¼ λ² ∫ dx H_ab H^ab',
        'interior_max_relative_residual': interior_rel,
        'boundary_max_relative_residual': boundary_rel,
        'interior_gradient_flow_match': bool(interior_rel < MATCH_TOLERANCE),
        'boundary_gradient_flow_match': bool(boundary_rel < MATCH_TOLERANCE),
        'scope_note': (
            'Interior match is exact up to finite-difference error. The one-sided edge_order=2 stencils in '
            'np.gradient are not adjoint to themselves, so boundary rows are not a gradient; the scalar '
            'Laplacian is periodic while H uses non-periodic stencils, a boundary-convention inconsistency.'
        ),
    }


# ---------------------------------------------------------------------------
# Coupled-system obstruction
# ---------------------------------------------------------------------------

def _rhs_parts(state: FieldState, g: np.ndarray, B: np.ndarray, phi: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    return _compute_rhs_python_reference(_with_fields(state, g, B, phi))


def cross_coupling_obstruction(state: FieldState | None = None) -> Dict[str, Any]:
    """Exhibit ∂F_B/∂φ = 0 together with ∂F_φ/∂B ≠ 0 on the audit state.

    For a constant block-diagonal SPD metric G = diag(G_g, G_B, G_φ), the
    Helmholtz condition requires G_B ∂F_B/∂φ = (G_φ ∂F_φ/∂B)ᵀ.  The left side
    is zero, so ∂F_φ/∂B would have to vanish; a single non-zero directional
    derivative of F_φ along B therefore refutes the gradient-flow form.
    """
    state = state or audit_reference_state()
    g, B, phi = state.g, state.B, state.phi
    h = FD_STEP
    N = phi.size

    max_dFB_dphi = 0.0
    for j in range(N):
        e = np.zeros(N)
        e[j] = h
        dB_plus = _rhs_parts(state, g, B, phi + e)[1]
        dB_minus = _rhs_parts(state, g, B, phi - e)[1]
        max_dFB_dphi = max(max_dFB_dphi, float(np.max(np.abs(dB_plus - dB_minus)) / (2.0 * h)))

    direction = np.zeros_like(B)
    direction[:, 2] = np.sin(2.0 * np.pi * np.arange(N) / N)
    dphi_plus = _rhs_parts(state, g, B + h * direction, phi)[2]
    dphi_minus = _rhs_parts(state, g, B - h * direction, phi)[2]
    dFphi_dB_dir = (dphi_plus - dphi_minus) / (2.0 * h)
    norm_dFphi_dB = float(np.max(np.abs(dFphi_dB_dir)))

    H = field_strength(B, state.dx)
    H_nonzero = bool(np.max(np.abs(H)) > 0.0)
    refuted = bool(max_dFB_dphi == 0.0 and norm_dFphi_dB > 1e-8 and H_nonzero)
    return {
        'max_abs_dF_B_dphi': max_dFB_dphi,
        'max_abs_dF_phi_dB_directional': norm_dFphi_dB,
        'H_nonzero': H_nonzero,
        'metric_class_excluded': 'constant (state-independent) block-diagonal positive-definite field-space metrics',
        'gradient_flow_refuted_in_class': refuted,
        'mechanism': (
            'S[H] = ½|H|² sources ∂_t φ, but the B equation has no compensating φ-dependent term; '
            'an action containing −∫ S[H] φ would force a back-reaction ∂_x(φ H_{x·})-type term in ∂_t B.'
        ),
        'not_excluded': [
            'state-dependent field-space metrics G(X)',
            'non-block-diagonal field-space metrics coupling B and φ',
            'flows that are gradient only after field redefinition or added terms',
        ],
    }


def _pack(g: np.ndarray, B: np.ndarray, phi: np.ndarray) -> np.ndarray:
    return np.concatenate([g[:, _IU[0], _IU[1]].ravel(), B.ravel(), phi])


def coupled_block_asymmetry_table(state: FieldState | None = None) -> Dict[str, Any]:
    """Full finite-difference Jacobian Helmholtz table (expensive: 2·15N RHS evaluations).

    Uses the trace inner product (off-diagonal metric components weighted 2)
    and reports interior-restricted blockwise asymmetry ‖(WJ)_ab − (WJ)_baᵀ‖_max.
    """
    state = state or audit_reference_state()
    N = state.phi.size
    ng, nb = 10 * N, 4 * N

    def unpack(v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        gu = v[:ng].reshape(N, 10)
        g = np.zeros((N, 4, 4))
        g[:, _IU[0], _IU[1]] = gu
        g[:, _IU[1], _IU[0]] = gu
        return g, v[ng:ng + nb].reshape(N, 4), v[ng + nb:]

    def F(v: np.ndarray) -> np.ndarray:
        return _pack(*_rhs_parts(state, *unpack(v)))

    x0 = _pack(state.g, state.B, state.phi)
    n = x0.size
    J = np.zeros((n, n))
    for j in range(n):
        e = np.zeros(n)
        e[j] = FD_STEP
        J[:, j] = (F(x0 + e) - F(x0 - e)) / (2.0 * FD_STEP)

    g_weights = np.where(_IU[0] == _IU[1], 1.0, 2.0)
    W = np.concatenate([np.tile(g_weights, N), np.ones(nb + N)])
    WJ = W[:, None] * J

    interior = list(range(INTERIOR_MARGIN, N - INTERIOR_MARGIN))

    def idx(block: str) -> np.ndarray:
        if block == 'g':
            return np.concatenate([np.arange(p * 10, (p + 1) * 10) for p in interior])
        if block == 'B':
            return ng + np.concatenate([np.arange(p * 4, (p + 1) * 4) for p in interior])
        return ng + nb + np.array(interior)

    rows: List[Dict[str, Any]] = []
    blocks = ['g', 'B', 'phi']
    for i, a in enumerate(blocks):
        for b in blocks[i:]:
            A = WJ[np.ix_(idx(a), idx(b))]
            Bt = WJ[np.ix_(idx(b), idx(a))].T
            scale = max(float(np.max(np.abs(A))), float(np.max(np.abs(Bt))), 1e-300)
            asym = float(np.max(np.abs(A - Bt)))
            rows.append({
                'block_pair': f'{a}-{b}',
                'max_abs_asymmetry': asym,
                'relative_asymmetry': asym / scale,
                'symmetric_within_tolerance': bool(asym / scale < 1e-5),
            })
    return {
        'grid_points': N,
        'interior_points': interior,
        'inner_product': 'trace (component L²) metric, off-diagonal g components weighted 2',
        'rows': rows,
        'l2_gradient_flow': all(row['symmetric_within_tolerance'] for row in rows),
    }


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------

ACTION_FORCED_TERMS: List[Dict[str, str]] = [
    {
        'sector': 'gauge',
        'term': 'δ/δB_μ of −∫ S[H] φ  →  φ-weighted divergence ∂_x(φ H_x^μ)-type back-reaction',
        'implemented': 'absent',
    },
    {
        'sector': 'metric',
        'term': 'scalar stress ∂_μφ ∂_νφ − ½ g_μν (∂φ)² in T_μν',
        'implemented': 'absent: _stress_energy ignores φ although the surface labels it T_μν[B, φ]',
    },
    {
        'sector': 'metric',
        'term': 'variation of −½ α R φ² with respect to g_μν (nonminimal-coupling stress)',
        'implemented': 'absent',
    },
    {
        'sector': 'scalar',
        'term': 'φ-dependence of R through G_55 = φ² in the variation of −½ α R φ²',
        'implemented': 'treated as external in the scalar equation',
    },
    {
        'sector': 'metric',
        'term': '−2 R_μν is Ricci-flow-like; Ricci flow is not an L² gradient flow (Perelman: gradient only modulo diffeomorphisms with an auxiliary dilaton)',
        'implemented': 'present without the compensating construction',
    },
]


@lru_cache(maxsize=1)
def gradient_flow_audit_certificate() -> Dict[str, Any]:
    """Return the cached executable gradient-flow audit certificate (cheap checks only)."""
    scalar = scalar_sector_gradient_check()
    gauge = gauge_sector_gradient_check()
    obstruction = cross_coupling_obstruction()
    refuted = bool(obstruction['gradient_flow_refuted_in_class'])
    return {
        'status': (
            'GRADIENT_FLOW_FORM_REFUTED_FOR_IMPLEMENTED_COUPLED_FLOW_IN_STATED_CLASS'
            if refuted else 'GRADIENT_FLOW_AUDIT_INCONCLUSIVE'
        ),
        'variational_class': 'gradient flow ∂_t X = −G⁻¹ δE/δX (t is not coordinate time)',
        'audit_state': {
            'grid_points': AUDIT_N, 'dx': AUDIT_DX, 'seed': AUDIT_SEED,
            'kk_backreaction_source': 'disabled (outside audited perimeter)',
        },
        'sector_checks': {'scalar': scalar, 'gauge': gauge},
        'coupled_obstruction': obstruction,
        'action_forced_terms_missing_from_implementation': list(ACTION_FORCED_TERMS),
        'summary': {
            'scalar_sector_frozen_background_gradient_flow': bool(scalar['gradient_flow_match']),
            'gauge_sector_interior_gradient_flow': bool(gauge['interior_gradient_flow_match']),
            'gauge_sector_boundary_gradient_flow': bool(gauge['boundary_gradient_flow_match']),
            'coupled_flow_gradient_form_refuted_in_class': refuted,
            'euler_lagrange_match_verified': False,
            'closure_earned': False,
        },
        'consequence': (
            'The implemented coupled flow cannot be promoted as action-derived in the stated class. '
            'Lane 1 can close only by replacing the flow with the gradient flow of an explicit functional '
            '(which changes numerical outputs and needs steward approval) or by retaining the '
            'phenomenological label.'
        ),
        'guardrail': (
            'Sector-level matches are conditional on frozen backgrounds and do not certify the coupled flow. '
            'The refutation covers constant block-diagonal field-space metrics only.'
        ),
    }


__all__ = [
    'ACTION_FORCED_TERMS',
    'audit_reference_state',
    'coupled_block_asymmetry_table',
    'cross_coupling_obstruction',
    'gauge_sector_functional',
    'gauge_sector_gradient_check',
    'gradient_flow_audit_certificate',
    'scalar_sector_functional',
    'scalar_sector_gradient_check',
]
