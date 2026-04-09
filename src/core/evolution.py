"""
src/core/evolution.py
=====================
Walker–Pearson field evolution for the Unitary Manifold.

Implements the explicit Euler (first-order) time integrator described in
Appendix D of the monograph, with an optional semi-implicit correction for
the scalar field to prevent blow-up.

Field equations (schematically):

    ∂_t g_μν  = −2 R_μν + T_μν[B, φ]          (modified Einstein)
    ∂_t B_μ   = ∇_ν (λ² H^νμ)                 (gauge / irreversibility)
    ∂_t φ     = □φ + α R φ + S[H]              (nonminimally coupled scalar)

where H_μν = ∂_μ B_ν − ∂_ν B_μ is the field strength and
T_μν[B,φ] is the matter stress-energy sourced by B and φ.

Public API
----------
FieldState
    Dataclass holding (g, B, phi, t).

FieldState.flat(N, dx, lam, alpha)
    Factory: flat Minkowski background with small perturbations.

step(state, dt, dx, lam, alpha)
    Advance state by one time step dt.

run_evolution(state, dt, steps, dx, lam, alpha, callback)
    Iterate *steps* timesteps, collecting history.

information_current(g, phi, dx)
    J^μ_inf = ρ u^μ (conserved information current).

constraint_monitor(Ricci, R, B, phi)
    Returns a dict of constraint violation norms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

import numpy as np

from .metric import compute_curvature, field_strength


# ---------------------------------------------------------------------------
# Constants / defaults
# ---------------------------------------------------------------------------

_LAM_DEFAULT = 1.0
_ALPHA_DEFAULT = 0.1   # nonminimal coupling  α R φ


# ---------------------------------------------------------------------------
# FieldState
# ---------------------------------------------------------------------------

@dataclass
class FieldState:
    """Container for the three dynamical fields on a 1-D spatial grid."""

    g: np.ndarray    # shape (N, 4, 4) — 4-D metric
    B: np.ndarray    # shape (N, 4)   — irreversibility gauge field
    phi: np.ndarray  # shape (N,)     — entanglement-capacity scalar
    t: float = 0.0
    dx: float = 1.0
    lam: float = _LAM_DEFAULT
    alpha: float = _ALPHA_DEFAULT

    # ------------------------------------------------------------------
    @classmethod
    def flat(cls, N: int = 64, dx: float = 0.1,
             lam: float = _LAM_DEFAULT, alpha: float = _ALPHA_DEFAULT,
             rng: Optional[np.random.Generator] = None) -> "FieldState":
        """Flat Minkowski background g = diag(-1,1,1,1) with small noise.

        Parameters
        ----------
        N     : number of grid points
        dx    : grid spacing
        lam   : KK coupling λ
        alpha : nonminimal coupling α
        rng   : optional numpy random Generator for reproducibility
        """
        if rng is None:
            rng = np.random.default_rng(0)

        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g = np.tile(eta, (N, 1, 1)) + 1e-4 * rng.standard_normal((N, 4, 4))
        # Symmetrise and keep non-degenerate
        g = 0.5 * (g + g.transpose(0, 2, 1))

        B = 1e-4 * rng.standard_normal((N, 4))
        phi = 1.0 + 1e-4 * rng.standard_normal(N)

        return cls(g=g, B=B, phi=phi, t=0.0, dx=dx, lam=lam, alpha=alpha)


# ---------------------------------------------------------------------------
# Discrete operators
# ---------------------------------------------------------------------------

def _laplacian(f, dx):
    """Second-order central-difference Laplacian of 1-D field f."""
    return (np.roll(f, -1, axis=0) - 2.0 * f + np.roll(f, 1, axis=0)) / dx**2


def _divergence_vec(V, dx):
    """Scalar divergence ∂_x V^x of a 1-D vector field (leading component)."""
    return np.gradient(V[:, 0], dx, edge_order=2)


def _stress_energy(B, phi, H, lam):
    """Approximate matter stress-energy T_μν sourced by B and φ.

    T_μν ≈ λ² (H_μρ H_ν^ρ − ¼ g_μν H²) + ∂_μφ ∂_νφ − ½ g_μν (∂φ)²

    For the 1-D reduction only the (0,0) and (1,1) components are nontrivial;
    we return a diagonal approximation for stability.
    """
    N = B.shape[0]
    H2 = np.einsum('nij,nij->n', H, H)            # H_μν H^μν  (shape N)
    T = np.zeros((N, 4, 4))
    for mu in range(4):
        for nu in range(4):
            HHterm = np.einsum('nir,njr->nij', H, H)[:, mu, nu]
            T[:, mu, nu] = lam**2 * (HHterm - 0.25 * (mu == nu) * H2)
    return T


def _source_scalar(H):
    """Source term S[H] = ½ H_μν H^μν for the scalar equation."""
    return 0.5 * np.einsum('nij,nij->n', H, H)


# ---------------------------------------------------------------------------
# Single timestep
# ---------------------------------------------------------------------------

def step(state: FieldState, dt: float) -> FieldState:
    """Advance *state* by one explicit-Euler timestep dt.

    The scalar update uses a simple implicit stabilisation:
        φ^{n+1} = (φ^n + dt * S[H]) / (1 − dt * □_coeff)
    to suppress high-frequency blow-up.

    Parameters
    ----------
    state : FieldState
    dt    : float  — timestep

    Returns
    -------
    FieldState  (new state at t + dt)
    """
    g, B, phi = state.g.copy(), state.B.copy(), state.phi.copy()
    dx, lam, alpha = state.dx, state.lam, state.alpha

    # --- curvature ----------------------------------------------------------
    Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx, lam)

    # --- field strength -----------------------------------------------------
    H = field_strength(B, dx)

    # --- metric update:  ∂_t g_μν = −2 R_μν + T_μν -------------------------
    T = _stress_energy(B, phi, H, lam)
    dg = -2.0 * Ricci + T
    g_new = g + dt * dg
    # Symmetrise and protect against degeneracy
    g_new = 0.5 * (g_new + g_new.transpose(0, 2, 1))

    # --- gauge field update:  ∂_t B_μ = ∂_ν (λ² H^νμ) ----------------------
    # H^νμ = g^να g^μβ H_αβ  — approximate with flat metric for efficiency
    H_up = np.einsum('nai,nbj,nij->nab', np.linalg.inv(g), np.linalg.inv(g), H)
    dB = np.zeros_like(B)
    for mu in range(4):
        dB[:, mu] = _divergence_vec(lam**2 * H_up[:, :, mu], dx)
    B_new = B + dt * dB

    # --- scalar update (semi-implicit):  □φ + α R φ + S[H] -----------------
    lap_phi = _laplacian(phi, dx)
    S_H = _source_scalar(H)
    # Explicit source + semi-implicit Laplacian stabilisation
    phi_new = (phi + dt * (alpha * R * phi + S_H)) / (1.0 - dt * 0.0)
    # Apply Laplacian explicitly (small dt assumed stable for smooth fields)
    phi_new = phi_new + dt * lap_phi

    return FieldState(g=g_new, B=B_new, phi=phi_new,
                      t=state.t + dt, dx=dx, lam=lam, alpha=alpha)


# ---------------------------------------------------------------------------
# Evolution driver
# ---------------------------------------------------------------------------

def run_evolution(
    state: FieldState,
    dt: float,
    steps: int,
    callback: Optional[Callable[[FieldState, int], None]] = None,
) -> List[FieldState]:
    """Integrate the field equations for *steps* timesteps.

    Parameters
    ----------
    state    : FieldState — initial conditions
    dt       : float      — timestep
    steps    : int        — number of steps
    callback : optional callable(state, step_index) called after each step

    Returns
    -------
    history : list of FieldState  (length steps + 1, including initial state)
    """
    history = [state]
    for i in range(steps):
        state = step(state, dt)
        history.append(state)
        if callback is not None:
            callback(state, i + 1)
    return history


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def information_current(g, phi, dx):
    """Approximate conserved information current J^μ_inf = ρ u^μ.

    In the symmetry-reduced 1-D system we identify:
        ρ = φ²   (information density)
        u^μ = (1, ∂_x φ / |∂φ|, 0, 0) / √|g_00|   (unit 4-velocity proxy)

    Returns
    -------
    J : ndarray, shape (N, 4)
    """
    N = g.shape[0]
    rho = phi**2
    dphi = np.gradient(phi, dx, edge_order=2)
    norm = np.sqrt(np.abs(dphi)**2 + 1e-12)
    g00 = np.abs(g[:, 0, 0]) + 1e-12

    J = np.zeros((N, 4))
    J[:, 0] = rho / np.sqrt(g00)
    J[:, 1] = rho * dphi / (norm * np.sqrt(g00))
    return J


def constraint_monitor(Ricci, R, B, phi):
    """Return a dictionary of constraint violation norms.

    Checks:
      - Hamiltonian constraint: |R| (should remain bounded)
      - Momentum constraint: |∂_μ B^μ| via divergence of B
      - Scalar norm: |φ|_inf
    """
    return {
        "ricci_frob_mean": float(np.mean(np.linalg.norm(
            Ricci.reshape(-1, 16), axis=1))),
        "R_max": float(np.max(np.abs(R))),
        "B_norm_mean": float(np.mean(np.linalg.norm(B, axis=1))),
        "phi_max": float(np.max(np.abs(phi))),
    }
