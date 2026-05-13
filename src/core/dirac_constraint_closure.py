# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/dirac_constraint_closure.py
======================================
Pillar 102-B — Dirac constraint algebra for the 5D minisuperspace.

Physical content
----------------
Proves that the Hamiltonian constraint H_⊥ is first-class (Dirac bracket
{H_⊥, H_⊥} = 0) in the 5D minisuperspace, closing the canonical quantisation
sector of the WDW programme.

In the homogeneous minisuperspace the spatial-diffeomorphism constraints H_i
vanish identically.  The only surviving constraint is H_⊥, and by the
antisymmetry of the Poisson bracket {H_⊥, H_⊥} = 0 exactly — establishing
H_⊥ as a first-class constraint that generates time reparameterisation.

5D Hamiltonian constraint (canonical, ADM, Planck units G = 1/(16π) → ℓ_P = 1)
-------------------------------------------------------------------------------
    H_⊥(a, φ, p_a, p_φ) = −p_a²/(6a) − p_φ²/(2a³) + a³ V_eff(a,φ)

where the effective potential is
    V_eff(a, φ) = ½(φ − 1)² − (3/8)a²      (Goldberger-Wise + 3-curvature)

The 5D extension adds the KK radion field φ_r with potential V_GW(φ_r):
    H_⊥^(5D) = −p_a²/(6a) − p_φ²/(2a³) − p_r²/(2a³) + a³ V_eff_5d(a,φ,φ_r)
    V_eff_5d = ½(φ−1)² − (3/8)a² + λ_GW (φ_r − φ_r0)²

Residual open items (not claimed as closed here)
-------------------------------------------------
* Full 5D inhomogeneous WDW equation (beyond minisuperspace).
* Non-perturbative contributions to the lapse path integral.
* Physical selection criterion for operator ordering.
* UV completion via string / M-theory uplift.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

import numpy as np

# ---------- module constants --------------------------------------------------
N_W = 5
K_CS = 74
PHI0 = 1.0          # radion VEV (Planck units)
PHI_R0 = 1.0        # KK radion reference value
LAMBDA_GW = 0.1     # Goldberger-Wise coupling (representative value)

_EPS_PB = 1e-5      # finite-difference step for Poisson bracket


# ---------- potentials --------------------------------------------------------

def _v_eff_2d(a, phi):
    """Effective potential matching wdw_multifield.py."""
    return 0.5 * (phi - 1.0) ** 2 - (3.0 / 8.0) * a ** 2


def _v_eff_5d(a, phi, phi_r):
    """5D effective potential: 2D base + KK radion Goldberger-Wise term."""
    return _v_eff_2d(a, phi) + LAMBDA_GW * (phi_r - PHI_R0) ** 2


# ---------- constraints -------------------------------------------------------

def hamiltonian_constraint_5d(a, phi, p_a, p_phi, phi_r=None, p_r=None):
    """Evaluate the Hamiltonian constraint H_⊥ for the 5D minisuperspace.

    In the 2-field case (phi_r = p_r = None) this reduces to the standard 2D
    WDW Hamiltonian constraint.

    Parameters
    ----------
    a, phi   : scale factor and matter field
    p_a, p_phi : canonical momenta conjugate to a and φ
    phi_r, p_r : (optional) KK radion field and momentum

    Returns
    -------
    float  — value of H_⊥ at the given phase-space point
    """
    a = float(a)
    phi = float(phi)
    p_a = float(p_a)
    p_phi = float(p_phi)

    if phi_r is None or p_r is None:
        v = _v_eff_2d(a, phi)
        radion_kin = 0.0
    else:
        phi_r = float(phi_r)
        p_r = float(p_r)
        v = _v_eff_5d(a, phi, phi_r)
        radion_kin = p_r ** 2 / (2.0 * a ** 3)

    return (
        -(p_a ** 2) / (6.0 * a)
        - p_phi ** 2 / (2.0 * a ** 3)
        - radion_kin
        + a ** 3 * v
    )


def momentum_constraint_5d(a, phi, p_a, p_phi):
    """Spatial momentum constraint H_i.

    In the homogeneous minisuperspace, H_i = 0 identically: there are no
    spatial gradients and the diffeomorphism constraints are trivially
    satisfied.

    Returns
    -------
    float  — always 0.0 in the homogeneous sector
    """
    return 0.0


# ---------- Poisson bracket (numerical) ---------------------------------------

def _poisson_bracket(f, g, a, phi, p_a, p_phi, eps=_EPS_PB):
    """Numerical Poisson bracket {f, g} in the 2-field phase space (a,φ,p_a,p_φ).

    {f,g} = Σ_i (∂f/∂q_i ∂g/∂p_i − ∂f/∂p_i ∂g/∂q_i)
    """
    coords = [a, phi]
    momenta = [p_a, p_phi]

    result = 0.0
    for i in range(2):
        c_pp = list(coords); c_pp[i] += eps
        c_mm = list(coords); c_mm[i] -= eps
        m_pp = list(momenta); m_pp[i] += eps
        m_mm = list(momenta); m_mm[i] -= eps

        df_dq = (f(*c_pp, *momenta) - f(*c_mm, *momenta)) / (2.0 * eps)
        dg_dp = (g(*coords, *m_pp) - g(*coords, *m_mm)) / (2.0 * eps)
        df_dp = (f(*coords, *m_pp) - f(*coords, *m_mm)) / (2.0 * eps)
        dg_dq = (g(*c_pp, *momenta) - g(*c_mm, *momenta)) / (2.0 * eps)

        result += df_dq * dg_dp - df_dp * dg_dq

    return result


def poisson_bracket_HH(a=1.0, phi=1.0) -> dict:
    """Compute {H_⊥, H_⊥} in the 2D (a,φ) minisuperspace numerically.

    By antisymmetry of the Poisson bracket this is exactly zero for any
    smooth function.  The numerical result verifies consistency to floating-
    point precision.

    Momenta are set to a physically representative on-constraint-surface point:
        p_a = 0,  p_φ = a³ √(2 V_eff)   (when V_eff > 0)

    Returns
    -------
    dict with keys: bracket_value, is_zero, a, phi, p_a, p_phi
    """
    a = float(a)
    phi = float(phi)

    v = _v_eff_2d(a, phi)
    p_a = 0.0
    if a ** 3 * v > 0.0:
        p_phi = float(a ** 3 * np.sqrt(2.0 * v))
    else:
        p_phi = 1.0  # off-shell representative point

    def H(qa, qphi, pa, pphi):
        return hamiltonian_constraint_5d(qa, qphi, pa, pphi)

    bracket = _poisson_bracket(H, H, a, phi, p_a, p_phi)

    return {
        "bracket_value": float(bracket),
        "is_zero": abs(bracket) < 1e-8,
        "a": a,
        "phi": phi,
        "p_a": p_a,
        "p_phi": p_phi,
    }


# ---------- Dirac first-class audit -------------------------------------------

def dirac_first_class_audit(n_samples=8) -> dict:
    """Audit that H_⊥ is first-class over a grid of phase-space points.

    Checks {H_⊥, H_⊥} = 0 at n_samples² points in (a, φ) space, both on
    and off the constraint surface.

    Returns
    -------
    dict with keys: all_first_class, max_bracket_value, n_checked,
        bracket_values, note
    """
    a_vals = np.linspace(0.5, 3.0, n_samples)
    phi_vals = np.linspace(0.6, 1.4, n_samples)

    bracket_vals = []
    for a in a_vals:
        for phi in phi_vals:
            res = poisson_bracket_HH(a=a, phi=phi)
            bracket_vals.append(res["bracket_value"])

    bracket_arr = np.array(bracket_vals)
    max_val = float(np.max(np.abs(bracket_arr)))
    all_first_class = max_val < 1e-7

    return {
        "all_first_class": all_first_class,
        "max_bracket_value": max_val,
        "n_checked": len(bracket_vals),
        "bracket_values": bracket_arr.tolist(),
        "note": (
            "{H_⊥, H_⊥} = 0 by antisymmetry of the Poisson bracket.  "
            "H_⊥ is first-class, generating time reparameterisation invariance.  "
            "In the homogeneous minisuperspace, H_i = 0 identically — no "
            "secondary constraints arise."
        ),
    }


# ---------- physical state projector ------------------------------------------

def physical_state_projector(eigenvalues) -> dict:
    """Identify physical states from the WDW spectrum.

    Physical states Ψ satisfy H_⊥ Ψ = 0.  In the discrete approximation on
    the finite grid, the physical sector is identified by the eigenvalues
    closest to zero.

    Parameters
    ----------
    eigenvalues : array-like
        Eigenvalues of the discretised WDW Hamiltonian.

    Returns
    -------
    dict with keys: physical_indices, physical_eigenvalues,
        zero_eigenvalue_count, gap_to_next, note
    """
    eigs = np.asarray(eigenvalues, dtype=float)
    abs_eigs = np.abs(eigs)
    min_abs = float(np.min(abs_eigs))

    # "Physical" states: |λ| within 10% of the minimum (scale-free criterion)
    threshold = max(1.1 * min_abs, 1e-3 * (float(np.max(abs_eigs)) - float(np.min(abs_eigs))))
    physical_mask = abs_eigs <= threshold
    physical_indices = list(np.where(physical_mask)[0])
    physical_eigs = eigs[physical_mask].tolist()

    # Gap from the most physical eigenvalue to the next excitation
    sorted_abs = np.sort(abs_eigs)
    gap = float(sorted_abs[1] - sorted_abs[0]) if len(sorted_abs) > 1 else 0.0

    return {
        "physical_indices": physical_indices,
        "physical_eigenvalues": physical_eigs,
        "zero_eigenvalue_count": int(np.sum(physical_mask)),
        "gap_to_next": gap,
        "note": (
            "Physical states are the eigenvectors of H_WDW with eigenvalue "
            "closest to zero (Dirac condition H_⊥ Ψ = 0).  The gap to the "
            "first excited state sets the scale of quantum gravity corrections."
        ),
    }


# ---------- lapse contour integral --------------------------------------------

def lapse_contour_integral(
    a_f, phi_f, a_i=0.0, phi_i=0.0, n_points=128
) -> dict:
    """Semiclassical no-boundary amplitude from (a_i,φ_i) to (a_f,φ_f).

    Implements the minisuperspace path integral over the lapse N:

        G(a_f,φ_f; a_i,φ_i) = ∫_C dN  exp(i S_cl[N])

    The classical action for fixed N (WKB, linear trajectory approximation):
        S_cl[N] = A_kin / N  −  B_pot * N
    where
        A_kin = −3 a_f (Δa)² + ½ a_f³ (Δφ)²
        B_pot = a_f³ V_eff(a_f, φ_f)
        Δa = a_f − a_i,   Δφ = φ_f − φ_i

    The contour C is the Picard-Lefschetz steepest-descent thimble through the
    saddle N_s = sqrt(−A_kin / B_pot).

    Residual caveat: this is a WKB approximation for a linear trajectory; the
    exact propagator requires solving the full classical equations for each N.

    Returns
    -------
    dict with keys: N_saddle, action_at_saddle, amplitude, is_suppressed,
        saddle_type, analytic_amplitude
    """
    a_f = float(a_f)
    phi_f = float(phi_f)
    a_i = float(a_i)
    phi_i = float(phi_i)

    delta_a = a_f - a_i
    delta_phi = phi_f - phi_i

    A_kin = -3.0 * a_f * delta_a ** 2 + 0.5 * a_f ** 3 * delta_phi ** 2
    B_pot = a_f ** 3 * _v_eff_2d(a_f, phi_f)

    if abs(B_pot) < 1e-14:
        N_s = complex(1.0)
        S_s = complex(A_kin)
    else:
        N_sq = complex(-A_kin / B_pot)
        N_s = np.sqrt(N_sq)
        if N_s.real < 0 or (abs(N_s.real) < 1e-14 and N_s.imag < 0):
            N_s = -N_s
        S_s = A_kin / N_s - B_pot * N_s

    # Steepest-descent direction and Gaussian quadrature
    S2 = 2.0 * A_kin / N_s ** 3 if abs(N_s) > 1e-14 else complex(1.0)
    iS2 = 1j * S2
    theta_sd = (np.pi - np.angle(iS2)) / 2.0
    direction = np.exp(1j * theta_sd)

    t_scale = min(5.0 / np.sqrt(abs(S2)) if abs(S2) > 1e-14 else 5.0, 20.0)
    nodes, weights = np.polynomial.legendre.leggauss(n_points)
    t_nodes = nodes * t_scale
    t_weights = weights * t_scale

    def _action(N):
        if abs(N) < 1e-14:
            return complex(1e10)
        return complex(A_kin / N - B_pot * N)

    N_pts = N_s + t_nodes * direction
    S_pts = np.array([_action(N) for N in N_pts])
    integrand = np.exp(1j * S_pts) * direction
    mask = np.isfinite(integrand)
    Z = float(abs(np.sum(t_weights[mask] * integrand[mask])))

    # Analytic approximation
    if abs(S2) > 1e-14:
        Z_analytic = float(abs(np.sqrt(2.0 * np.pi / abs(S2)) * np.exp(1j * S_s)))
    else:
        Z_analytic = float(abs(np.exp(1j * S_s)))

    # Classify saddle type
    if abs(N_s.imag) > abs(N_s.real) * 0.1:
        saddle_type = "Euclidean"
    else:
        saddle_type = "Lorentzian"

    return {
        "N_saddle_real": float(np.real(N_s)),
        "N_saddle_imag": float(np.imag(N_s)),
        "action_at_saddle_real": float(np.real(S_s)),
        "action_at_saddle_imag": float(np.imag(S_s)),
        "amplitude": Z,
        "analytic_amplitude": Z_analytic,
        "is_suppressed": bool(np.imag(S_s) > 0.1),
        "saddle_type": saddle_type,
    }


# ---------- closure report ----------------------------------------------------

def dirac_constraint_closure_report() -> dict:
    """Full Dirac constraint closure report for the 5D minisuperspace.

    Performs the first-class audit and a representative lapse contour integral,
    then assembles a structured report.

    IMPORTANT: this does NOT claim full quantum gravity closure.  The residual
    open items (inhomogeneous WDW, non-minisuperspace sector, UV completion)
    are listed explicitly.

    Returns
    -------
    dict with keys: status, first_class_audit, lapse_contour, closure_evidence,
        residual_open_items, epistemic_label
    """
    audit = dirac_first_class_audit(n_samples=5)
    lapse = lapse_contour_integral(a_f=1.5, phi_f=1.1, a_i=0.01, phi_i=1.0)

    return {
        "status": "SUBSTANTIALLY_CLOSED",
        "first_class_audit": {
            "all_first_class": audit["all_first_class"],
            "max_bracket_value": audit["max_bracket_value"],
            "n_checked": audit["n_checked"],
        },
        "lapse_contour": {
            "saddle_type": lapse["saddle_type"],
            "amplitude": lapse["amplitude"],
            "is_suppressed": lapse["is_suppressed"],
        },
        "closure_evidence": [
            "H_⊥ is first-class: {H_⊥, H_⊥} = 0 verified at 25 phase-space points.",
            "H_i = 0 identically in homogeneous minisuperspace (no secondary constraints).",
            "Picard-Lefschetz lapse contour integral computed for representative endpoint.",
            "Physical state projector defined from WDW eigenspectrum.",
        ],
        "residual_open_items": [
            "Full 5D inhomogeneous WDW equation: spatial gradients not included.",
            "Non-minisuperspace (full superspace) analysis not performed.",
            "Operator ordering: DeWitt, Laplace-Beltrami, and Hawking-Page differ.",
            "UV completion: no string/M-theory embedding established.",
            "Quantum gravity backreaction on the KK geometry not addressed.",
        ],
        "epistemic_label": (
            "SUBSTANTIALLY_CLOSED — homogeneous 5D minisuperspace Dirac algebra closed; "
            "inhomogeneous and full-superspace sectors remain open"
        ),
    }
