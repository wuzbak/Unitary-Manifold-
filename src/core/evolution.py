# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/evolution.py
=====================
Walker–Pearson field evolution for the Unitary Manifold.

Implements the classical fourth-order Runge–Kutta (RK4) time integrator for
the coupled field equations described in Appendix D of the monograph.  A
first-order Euler integrator is also provided for accuracy benchmarking.

Field equations (schematically):

    ∂_t g_μν  = −2 R_μν + T_μν[B, φ]                   (modified Einstein)
    ∂_t B_μ   = ∇_ν (λ² H^νμ)                          (gauge / irreversibility)
    ∂_t φ     = □φ + α R φ + S[H] − m²_φ (φ − φ₀)     (stabilised radion scalar)

where H_μν = ∂_μ B_ν − ∂_ν B_μ is the field strength,
T_μν[B,φ] is the matter stress-energy sourced by B and φ, and the last
term is a Goldberger–Wise–style mass potential that pins the KK radion φ
to its background value φ₀, preventing both the collapse (φ → 0) and the
run-away (φ → ∞) instabilities identified in the Gemini peer review.  The
mass m_phi = 0 (default) recovers the original mass-less equation.

**Time-synchronisation note (Gemini Issue 4 / ADM gap — documented in FALLIBILITY.md §III)**

The evolution parameter *t* here acts as the flow parameter λ that drives
the irreversibility (analogous to Ricci-flow time), not as the coordinate
time x⁰ embedded inside the metric tensor.  A fully diffeomorphism-invariant
treatment would require an ADM 3+1 decomposition with lapse and shift; the
present symmetry-reduced (1-D spatial grid) formulation treats x⁰ as a fixed
gauge choice and evolves all fields in the single remaining spatial direction.
Consumers of this code should be aware that the "double-counting" of time
described in the review is therefore present by construction: λ and x⁰ are
related but not formally synchronised within the current framework.

**Partial correction:** Pillar 41 (`src/core/delay_field.py`) provides a
correction factor Ω(φ) = 1/φ connecting the flow parameter to the proper-time
lapse in the non-relativistic limit.  This is a first-order correction, not a
full ADM 3+1 decomposition.  The full ADM treatment remains an open gap for the
"arrow of time is geometric" claim; see FALLIBILITY.md §III (ADM gap section)
and DERIVATION_STATUS.md Part I for the precise epistemic status.

**KK information-recovery note (Gemini Issue 2)**
The simulation tracks only the zero-mode (4D) fields; higher Kaluza–Klein
modes are truncated.  Apparent entropy increase visible in the zero-mode
sector may therefore correspond to information encoded in the truncated KK
tower rather than true, irreversible loss.  To verify physical irreversibility
one would need to show the KK tower information is inaccessible, which is not
established here.

Public API
----------
FieldState
    Dataclass holding (g, B, phi, t).

FieldState.flat(N, dx, lam, alpha, phi0, m_phi)
    Factory: flat Minkowski background with small perturbations.

step(state, dt)
    Advance state by one RK4 timestep dt.  O(dt⁴) local truncation error.
    A metric volume-preservation projection is applied after each step to
    suppress numerical drift of the spacetime volume element (det g).

step_euler(state, dt)
    Advance state by one first-order Euler timestep (for benchmarking).

cfl_timestep(state, cfl)
    Estimate a CFL-stable timestep for the scalar diffusion term.

_check_cfl(state, dt, cfl)
    Check whether dt satisfies the CFL stability condition.  Returns a
    dict with keys ok, dt_given, dt_max, dx, ratio, message.

run_evolution(state, dt, steps, callback, check_cfl)
    Iterate *steps* RK4 timesteps, collecting history.

information_current(g, phi, dx)
    J^μ_inf = ρ u^μ (conserved information current).

conjugate_momentum_phi(state)
    π_φ = ∂_t φ — canonical conjugate momentum of the scalar field.
    Encodes the CCR [φ̂, π̂_φ] = iℏ δ³(x−y) (QUANTUM_THEOREMS.md §XIII).

hawking_temperature(state)
    T_H = |∂_r φ / φ| / (2π) — Hawking temperature profile from the
    scalar gradient (QUANTUM_THEOREMS.md §XIV).

constraint_monitor(Ricci, R, B, phi, g=None)
    Returns a dict of constraint violation norms.  Pass g to also obtain
    the det_g_violation diagnostic (max deviation of det g from −1).
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

from dataclasses import dataclass
from typing import Callable, List, Optional

import numpy as np

from .metric import compute_curvature, field_strength


# ---------------------------------------------------------------------------
# Constants / defaults
# ---------------------------------------------------------------------------

_LAM_DEFAULT = 1.0
_ALPHA_DEFAULT = 0.1   # nonminimal coupling  α R φ
_PHI0_DEFAULT = 1.0    # background radion value for stabilization potential
_M_PHI_DEFAULT = 0.0   # dilaton mass; 0 = unstabilised (backward-compatible)
_NUMERICAL_EPSILON = 1e-30  # guard against exact-zero denominators / norms


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
    phi0: float = _PHI0_DEFAULT   # background radion value φ₀ for V(φ) potential
    m_phi: float = _M_PHI_DEFAULT # dilaton mass m_φ; 0 disables stabilization

    # ------------------------------------------------------------------
    @classmethod
    def flat(cls, N: int = 64, dx: float = 0.1,
             lam: float = _LAM_DEFAULT, alpha: float = _ALPHA_DEFAULT,
             phi0: float = _PHI0_DEFAULT, m_phi: float = _M_PHI_DEFAULT,
             rng: Optional[np.random.Generator] = None) -> "FieldState":
        """Flat Minkowski background g = diag(-1,1,1,1) with small noise.

        Parameters
        ----------
        N     : number of grid points
        dx    : grid spacing
        lam   : KK coupling λ
        alpha : nonminimal coupling α
        phi0  : background radion value φ₀ for the stabilization potential
                V(φ) = ½ m²_φ (φ − φ₀)² (default 1.0)
        m_phi : dilaton mass m_φ; set > 0 to activate radion stabilization and
                suppress the "fifth force" from a massless dilaton (default 0.0)
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

        return cls(g=g, B=B, phi=phi, t=0.0, dx=dx, lam=lam, alpha=alpha,
                   phi0=phi0, m_phi=m_phi)


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
# Field equation right-hand sides
# ---------------------------------------------------------------------------

def _compute_rhs(state: FieldState) -> tuple:
    """Evaluate the field equation right-hand sides at the current state.

    Returns
    -------
    dg   : ndarray, shape (N, 4, 4) — ∂_t g_μν  (symmetrised)
    dB   : ndarray, shape (N, 4)   — ∂_t B_μ
    dphi : ndarray, shape (N,)     — ∂_t φ
    """
    g, B, phi = state.g, state.B, state.phi
    dx, lam, alpha = state.dx, state.lam, state.alpha
    phi0, m_phi = state.phi0, state.m_phi

    _, _, Ricci, R = compute_curvature(g, B, phi, dx, lam)
    H = field_strength(B, dx)

    # ∂_t g_μν = −2 R_μν + T_μν
    T = _stress_energy(B, phi, H, lam)
    dg = -2.0 * Ricci + T
    dg = 0.5 * (dg + dg.transpose(0, 2, 1))

    # ∂_t B_μ = ∂_ν (λ² H^νμ)
    g_inv = np.linalg.inv(g)
    H_up = np.einsum('nai,nbj,nij->nab', g_inv, g_inv, H)
    dB = np.zeros_like(B)
    for mu in range(4):
        dB[:, mu] = _divergence_vec(lam**2 * H_up[:, :, mu], dx)

    # ∂_t φ = □φ + α R φ + S[H] − m²_φ (φ − φ₀)
    # The last term is the Goldberger–Wise stabilization potential gradient
    # V'(φ) = m²_φ (φ − φ₀), which provides a restoring force that pins the
    # KK radion to its background value φ₀.  With m_phi=0 (default) this
    # term vanishes and the original mass-less equation is recovered.
    dphi = (_laplacian(phi, dx) + alpha * R * phi + _source_scalar(H)
            - m_phi**2 * (phi - phi0))

    return dg, dB, dphi


def _advance_fields(state: FieldState,
                    dg: np.ndarray,
                    dB: np.ndarray,
                    dphi: np.ndarray,
                    dt: float,
                    t_new: float) -> FieldState:
    """Return a new FieldState with each field advanced by dt * derivative."""
    g_new = state.g + dt * dg
    g_new = 0.5 * (g_new + g_new.transpose(0, 2, 1))
    return FieldState(g=g_new,
                      B=state.B + dt * dB,
                      phi=state.phi + dt * dphi,
                      t=t_new,
                      dx=state.dx, lam=state.lam, alpha=state.alpha,
                      phi0=state.phi0, m_phi=state.m_phi)


# ---------------------------------------------------------------------------
# Metric volume-preservation projection
# ---------------------------------------------------------------------------

def _project_metric_volume(g: np.ndarray,
                            det_target: float = -1.0) -> np.ndarray:
    """Rescale each grid-point metric to enforce det(g) = det_target.

    Suppresses numerical drift of the spacetime volume element that
    accumulates over many RK4 steps (Gemini Issue 5 — numerical dissipation).
    For Lorentzian signature (−,+,+,+), det_target = −1 corresponds to unit
    Minkowski volume.

    Each grid-point metric g_n is rescaled by a scalar factor

        s_n = (det_target / det(g_n))^{1/4}

    so that det(s_n · g_n) = s_n^4 · det(g_n) = det_target exactly.
    The signature and symmetry of the metric are preserved; only the
    overall volume element is corrected.

    Parameters
    ----------
    g          : ndarray, shape (N, 4, 4)
    det_target : float — target determinant value (default −1 for Lorentzian)

    Returns
    -------
    g_projected : ndarray, shape (N, 4, 4)
    """
    dets = np.linalg.det(g)                              # (N,)
    # Guard against exactly-zero determinants (degenerate metric)
    safe_dets = np.where(np.abs(dets) > 1e-15, dets, det_target)
    scales = (det_target / safe_dets) ** 0.25            # (N,)
    return g * scales[:, None, None]


# ---------------------------------------------------------------------------
# Integrators
# ---------------------------------------------------------------------------

def step(state: FieldState, dt: float) -> FieldState:
    """Advance *state* by one RK4 timestep dt.

    Uses the classical fourth-order Runge–Kutta method, giving O(dt⁴) local
    truncation error per step for all three dynamical fields (g_μν, B_μ, φ).

    A metric volume-preservation projection (_project_metric_volume) is applied
    to the final result to enforce det(g) = −1 at every grid point, preventing
    the accumulation of numerical drift in the spacetime volume element.  The
    projection is NOT applied to intermediate RK4 stages (k2, k3, k4) so that
    the fourth-order accuracy of the integration is preserved.

    Parameters
    ----------
    state : FieldState
    dt    : float  — timestep

    Returns
    -------
    FieldState  (new state at t + dt)
    """
    t0 = state.t
    half_dt = 0.5 * dt

    k1g, k1B, k1phi = _compute_rhs(state)

    s2 = _advance_fields(state, k1g, k1B, k1phi, half_dt, t0 + half_dt)
    k2g, k2B, k2phi = _compute_rhs(s2)

    s3 = _advance_fields(state, k2g, k2B, k2phi, half_dt, t0 + half_dt)
    k3g, k3B, k3phi = _compute_rhs(s3)

    s4 = _advance_fields(state, k3g, k3B, k3phi, dt, t0 + dt)
    k4g, k4B, k4phi = _compute_rhs(s4)

    dg   = (k1g   + 2.0*k2g   + 2.0*k3g   + k4g)   / 6.0
    dB   = (k1B   + 2.0*k2B   + 2.0*k3B   + k4B)   / 6.0
    dphi = (k1phi + 2.0*k2phi + 2.0*k3phi + k4phi) / 6.0

    result = _advance_fields(state, dg, dB, dphi, dt, t0 + dt)
    # Enforce metric volume conservation to separate physical irreversibility
    # from numerical dissipation (det-drift).
    out = FieldState(g=_project_metric_volume(result.g),
                     B=result.B, phi=result.phi, t=result.t,
                     dx=result.dx, lam=result.lam, alpha=result.alpha,
                     phi0=result.phi0, m_phi=result.m_phi)
    # NaN/Inf guard: detect numerical blow-up caused by CFL violation or
    # chaotic initial conditions, and raise immediately with a clear message.
    if (not np.all(np.isfinite(out.phi)) or
            not np.all(np.isfinite(out.B)) or
            not np.all(np.isfinite(out.g))):
        raise RuntimeError(
            "CFL violation detected mid-integration: fields are NaN/Inf after "
            f"RK4 step at t={t0:.6g} + dt={dt:.6g}.  "
            f"CFL-stable dt_max = {0.4 * state.dx ** 2:.4g} for dx={state.dx:.4g}.  "
            "Reduce dt or increase grid spacing dx."
        )
    return out


def step_euler(state: FieldState, dt: float) -> FieldState:
    """Advance *state* by one first-order Euler timestep dt.

    Retained for accuracy benchmarking against the default RK4 integrator.
    For production use, prefer :func:`step` (RK4).  The same metric
    volume-preservation projection as in :func:`step` is applied to the
    result for consistency.

    Parameters
    ----------
    state : FieldState
    dt    : float

    Returns
    -------
    FieldState  (new state at t + dt)
    """
    dg, dB, dphi = _compute_rhs(state)
    result = _advance_fields(state, dg, dB, dphi, dt, state.t + dt)
    return FieldState(g=_project_metric_volume(result.g),
                      B=result.B, phi=result.phi, t=result.t,
                      dx=result.dx, lam=result.lam, alpha=result.alpha,
                      phi0=result.phi0, m_phi=result.m_phi)


def cfl_timestep(state: FieldState, cfl: float = 0.4) -> float:
    """Estimate a CFL-stable timestep for the scalar field equation.

    The 1-D explicit stability condition for □φ requires
        dt  ≤  cfl * dx²
    The default safety factor cfl = 0.4 gives comfortable margin for RK4.

    Parameters
    ----------
    state : FieldState
    cfl   : float — CFL safety factor (default 0.4)

    Returns
    -------
    dt_max : float
    """
    return float(cfl * state.dx**2)


def _check_cfl(state: FieldState, dt: float, cfl: float = 0.4) -> dict:
    """Check whether *dt* satisfies the CFL stability condition.

    The scalar field diffusion term □φ requires
        dt  ≤  cfl × dx²
    for the explicit RK4 scheme to be numerically stable.

    Parameters
    ----------
    state : FieldState
    dt    : float — proposed timestep
    cfl   : float — CFL safety factor (default 0.4)

    Returns
    -------
    dict with keys:
        ``ok``        : bool  — True iff dt ≤ dt_max
        ``dt_given``  : float — the proposed timestep
        ``dt_max``    : float — CFL-stable upper bound (cfl × dx²)
        ``dx``        : float — grid spacing
        ``ratio``     : float — dt / dt_max  (must be ≤ 1 for stability)
        ``message``   : str   — human-readable status
    """
    dt_max = cfl_timestep(state, cfl)
    ok = dt <= dt_max
    ratio = dt / dt_max if dt_max > 0.0 else float("inf")
    msg = (
        f"CFL OK: dt={dt:.4g} ≤ dt_max={dt_max:.4g} (cfl×dx²={cfl}×{state.dx}²)"
        if ok else
        f"CFL VIOLATION: dt={dt:.4g} > dt_max={dt_max:.4g} (cfl×dx²={cfl}×{state.dx}²); "
        f"ratio={ratio:.2f}.  Reduce dt or increase dx."
    )
    return {
        "ok": ok,
        "dt_given": float(dt),
        "dt_max": dt_max,
        "dx": state.dx,
        "ratio": ratio,
        "message": msg,
    }


# ---------------------------------------------------------------------------
# Evolution driver
# ---------------------------------------------------------------------------

def run_evolution(
    state: FieldState,
    dt: float,
    steps: int,
    callback: Optional[Callable[[FieldState, int], None]] = None,
    check_cfl: bool = True,
) -> List[FieldState]:
    """Integrate the field equations for *steps* timesteps.

    Parameters
    ----------
    state     : FieldState — initial conditions
    dt        : float      — timestep
    steps     : int        — number of steps
    callback  : optional callable(state, step_index) called after each step
    check_cfl : bool       — if True (default), raise ValueError before the
                             first step when dt exceeds the CFL-stable limit
                             cfl_timestep(state) = 0.4 × dx².  Set False
                             to suppress the check (e.g. for benchmark tests).

    Returns
    -------
    history : list of FieldState  (length steps + 1, including initial state)

    Raises
    ------
    ValueError
        If check_cfl=True and dt > cfl_timestep(state).
    """
    if check_cfl:
        report = _check_cfl(state, dt)
        if not report["ok"]:
            raise ValueError(report["message"])

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


def conjugate_momentum_phi(state: FieldState) -> np.ndarray:
    """Canonical conjugate momentum π_φ = ∂_t φ of the scalar field.

    From the 4D effective action obtained by Kaluza-Klein reduction, the
    φ kinetic term yields the canonical momentum:

        π_φ(x)  =  ∂L / ∂(∂_t φ)  =  ∂_t φ

    The equal-time Poisson bracket

        { φ(x, t), π_φ(y, t) }  =  δ³(x − y)

    follows from the symplectic structure of the action and is the classical
    precursor of the quantum canonical commutation relation:

        [φ̂(x, t), π̂_φ(y, t)]  =  iℏ δ³(x − y)

    See QUANTUM_THEOREMS.md §XIII for the full derivation.

    Parameters
    ----------
    state : FieldState

    Returns
    -------
    pi_phi : ndarray, shape (N,)
        Canonical conjugate momentum at each grid point.  Evaluated by
        computing the RHS of the φ field equation (_compute_rhs).
    """
    _, _, pi_phi = _compute_rhs(state)
    return pi_phi


def hawking_temperature(state: FieldState) -> np.ndarray:
    """Hawking temperature profile T_H(x) = |∂_r φ / φ| / (2π).

    At a black-hole horizon the Unitary Manifold information current
    J^μ_inf = φ² u^μ must remain conserved (∇_μ J^μ_inf = 0) up to and
    across the horizon.  The surface gravity encoded in the scalar gradient
    gives the Unruh/Hawking temperature via (natural units ℏ = k_B = c = 1):

        κ(x)   =  |∂_r φ(x)| / |φ(x)|        (surface gravity per point)
        T_H(x) =  κ(x) / (2π)

    For a Schwarzschild black hole of mass M (φ ~ (1 − 2M/r)^{1/2} near the
    horizon) this reduces to Hawking's exact result T_H = 1/(8πM) in Planck
    units.  A small correction from the α R φ coupling shifts the result at
    the Planck scale (see QUANTUM_THEOREMS.md §XIV.2).

    Parameters
    ----------
    state : FieldState

    Returns
    -------
    T_H : ndarray, shape (N,)
        Hawking temperature at each spatial grid point.
        Units: Planck temperature (ℏ = k_B = c = G = 1).
    """
    dphi_dr = np.gradient(state.phi, state.dx, edge_order=2)
    kappa = np.abs(dphi_dr) / (np.abs(state.phi) + 1e-12)
    return kappa / (2.0 * np.pi)


def constraint_monitor(Ricci, R, B, phi, g=None):
    """Return a dictionary of constraint violation norms.

    Checks:
      - Hamiltonian constraint: |R| (should remain bounded)
      - Momentum constraint: |∂_μ B^μ| via divergence of B
      - Scalar norm: |φ|_inf
      - Volume drift: max |det(g) − (−1)| (only when g is supplied)

    Parameters
    ----------
    Ricci : ndarray, shape (N, 4, 4)
    R     : ndarray, shape (N,)
    B     : ndarray, shape (N, 4)
    phi   : ndarray, shape (N,)
    g     : ndarray, shape (N, 4, 4) or None
        Optional metric tensor.  When supplied, the ``det_g_violation``
        diagnostic is included in the output: it measures the maximum
        absolute deviation of det(g) from the Lorentzian target −1.  A
        non-zero value indicates accumulated numerical volume drift.
    """
    result = {
        "ricci_frob_mean": float(np.mean(np.linalg.norm(
            Ricci.reshape(-1, 16), axis=1))),
        "R_max": float(np.max(np.abs(R))),
        "B_norm_mean": float(np.mean(np.linalg.norm(B, axis=1))),
        "phi_max": float(np.max(np.abs(phi))),
    }
    if g is not None:
        dets = np.linalg.det(g)
        result["det_g_violation"] = float(np.max(np.abs(dets - (-1.0))))
    return result


# ---------------------------------------------------------------------------
# [COMPLETION 1]  KK wavefunction renormalisation  →  ε_eff, r_eff < 0.036
# ---------------------------------------------------------------------------
#
# Physical location: the slow-roll ε is field- and time-dependent (it changes
# as φ rolls during inflation), so its renormalisation by the KK wavefunction
# belongs here in the *evolution* layer, NOT in the observable/inflation layer.
#
# Fixed geometric power  p = 1  (no new free parameter):
#   The 5D kinetic term ∫ dy √G₅₅ f(φ(y)) with √G₅₅ = φ(y) and f = φ^p
#   gives p = 1 from the KK ansatz G₅₅ = φ².  This is fixed by the geometry
#   of the extra dimension and carries zero adjustable freedom.
#
# ---------------------------------------------------------------------------

#: Geometric power fixed by the KK ansatz G₅₅ = φ² → √G₅₅ = φ → p = 1.
_P_KK_FIXED: float = 1.0


def Z_kinetic(
    phi_profile: np.ndarray,
    p: float = _P_KK_FIXED,
) -> float:
    """KK wavefunction renormalisation factor from the current radion profile.

    Computes the compact-dimension integral

        Z_kinetic = (1/πRc) ∫₀^{πRc} √G₅₅(y) · φ(y)^p dy
                  ≈ ⟨φ⟩^p

    where for the zero mode on a flat S¹/Z₂ the profile is constant:
    φ(y) = φ₀ = ⟨φ⟩.  The spatial mean of *phi_profile* is used as the
    effective zero-mode amplitude φ₀.

    **No new free parameter**: p is fixed at 1 by the KK geometry (G₅₅ = φ²).

    Parameters
    ----------
    phi_profile : ndarray, shape (N,) — radion scalar field on the 4-D grid
    p           : float — integrand power (default _P_KK_FIXED = 1, geometric)

    Returns
    -------
    Z : float — renormalisation factor Z_kinetic ≥ 1 when ⟨φ⟩ ≥ 1
    """
    # Use magnitude: Z_kinetic = ⟨|φ|⟩^p must be real and positive for any
    # real power p.  Signed φ would give imaginary Z for non-integer p, which
    # is unphysical.  The background radion |φ₀| is always positive by definition.
    phi_mean = float(np.mean(np.abs(phi_profile)) + _NUMERICAL_EPSILON)
    return float(phi_mean ** p)


def epsilon_eff(
    epsilon: float,
    phi_profile: np.ndarray,
    p: float = _P_KK_FIXED,
) -> float:
    """Effective slow-roll parameter after KK wavefunction renormalisation.

        ε_eff = ε / Z_kinetic(φ, p)

    Decouples ε_eff from the bare ε while keeping η (and therefore nₛ)
    unchanged.  The tensor-to-scalar ratio r = 16 ε_eff is consequently
    reduced without shifting the spectral tilt.

    Parameters
    ----------
    epsilon     : float — bare slow-roll first parameter ε
    phi_profile : ndarray, shape (N,) — radion field (current FieldState.phi)
    p           : float — KK power (default _P_KK_FIXED = 1)

    Returns
    -------
    epsilon_eff : float
    """
    Z = Z_kinetic(phi_profile, p)
    if Z <= 0.0:
        return float(epsilon)
    return float(epsilon / Z)


def renormalize_slow_roll(
    state: "FieldState",
    epsilon: float,
    p: float = _P_KK_FIXED,
) -> float:
    """Apply KK wavefunction renormalisation to ε using the current field state.

    Called inside the evolution pipeline BEFORE inflation observables are
    exported.  The renormalised value is used in place of the bare ε when
    computing r = 16 ε_eff and any downstream quantity that uses the
    tensor-to-scalar ratio.

    Parameters
    ----------
    state   : FieldState — current dynamical state (provides phi_profile)
    epsilon : float — bare ε computed from the inflaton potential
    p       : float — KK power (default _P_KK_FIXED = 1, no free parameter)

    Returns
    -------
    epsilon_renormed : float — ε_eff = ε / Z_kinetic(state.phi)

    Example
    -------
    >>> eps_bare = slow_roll_params(phi_star, V, dV, d2V)[0]
    >>> eps_ren  = renormalize_slow_roll(state, eps_bare)
    >>> r_eff    = 16.0 * eps_ren          # < 0.036 when Z_kinetic ≥ 3
    """
    return epsilon_eff(epsilon, state.phi, p)
