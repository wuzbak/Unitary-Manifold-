# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/metric.py
==================
Kaluza–Klein metric ansatz and curvature computation for the Unitary Manifold.

The 5D parent metric G_AB is assembled from the 4D metric g_μν, the
irreversibility gauge field B_μ, and the scalar (entanglement capacity / radion) φ:

    ┌                               ┐
    │  g_μν + λ²φ² B_μ B_ν   λφ² B_μ │
G = │                               │
    │  λφ² B_ν                  φ²  │
    └                               ┘

G_55 = φ² so that φ plays the role of the KK radion; the 4D fields are
obtained by dimensional reduction from the 5D Einstein equations.

Curvature tensors are computed on a 1-D spatial grid using second-order
central finite differences.  The convention follows MTW (Misner, Thorne,
Wheeler) with signature (−, +, +, +) for the 4D block.

Pipeline: 4D (g, B, φ) → assemble G_AB (5D) → 5D Christoffel/Riemann/Ricci
          → project 4D block → return 4D Gamma, Riemann, Ricci, R.

Public API
----------
field_strength(B, dx)
    Compute the antisymmetric field-strength tensor H_μν = ∂_μ B_ν − ∂_ν B_μ.

assemble_5d_metric(g, B, phi, lam)
    Build the 5×5 KK metric G_AB at every grid point.

christoffel(g, dx)
    Christoffel symbols Γ^σ_μν from an arbitrary D×D metric on a 1-D grid.

compute_curvature(g, B, phi, dx, lam)
    Return (Gamma, Riemann, Ricci, R) — the full curvature hierarchy computed
    via the 5D metric and projected back to the 4D block.

extract_alpha_from_curvature(g, B, phi, dx, lam)
    Return the tree-level Einstein–Hilbert coefficient of R H² (zero)
    and the cross-block Riemann diagnostic; inverse radius is not this coupling.

assemble_warped_5d_metric(g, B, phi, r_c_field, k, lam)
    Build the 5×5 warped Randall–Sundrum KK metric with a **dynamical**
    compactification radius r_c(x) promoted to an independent field.
    G_55 = r_c(x)² rather than φ².  The entanglement scalar φ and the
    radion r_c are coupled through the Goldberger–Wise radion potential
    V(φ, r_c) = λ_GW φ²(r_c − r_c*)² (implemented in inflation.py).
"""

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}


from typing import Any, Dict, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Z₂ parity clarification (Pillar 56-B / peer-review addition)
# ---------------------------------------------------------------------------

def z2_parity_clarification() -> Dict[str, Any]:
    """State the orbifold obstruction, not a fictitious boundary photon.

    A smooth odd field vanishes at both fixed planes and has no constant
    zero mode. Multiplying by an even radion does not change that fact.
    The circle connection A = λB is not an independently added boundary field.
    """
    return {
        "referee_question": (
            "If B_μ is Z₂-odd, it has no massless zero mode.  "
            "The zero mode of an electromagnetic field is Z₂-even, not Z₂-odd."
        ),
        "B_mu_parity": (
            "Z₂-ODD. Under y → −y: B_μ → −B_μ (fifth-component sign from "
            "tensor transformation). B_μ's zero mode vanishes at orbifold fixed "
            "planes. The metric vector cannot supply an orbifold photon zero mode."
        ),
        "phi_parity": (
            "Z₂-EVEN. φ² = G_{55} is invariant under y → −y because "
            "the tensor transformation has two fifth indices. A positive radius "
            "φ is even; its zero mode is allowed, not necessarily massless."
        ),
        "A_mu_photon_parity": (
            "Z₂-ODD: A_μ = G_{μ5}/G_{55} = λB_μ. Even radion factors "
            "also leave a composite odd. Its fixed-plane value is zero."
        ),
        "g_munu_parity": (
            "Z₂-EVEN. The 4D metric block g_μν is invariant under y → −y "
            "and has a massless zero mode (the 4D graviton)."
        ),
        "G_mu5_parity": (
            "Z₂-ODD. G_{μ5} = λφ²B_μ inherits the odd parity of B_μ. "
            "Its zero mode vanishes — consistent with the orbifold boundary "
            "conditions that remove the B_μ Neumann modes."
        ),
        "G_55_parity": (
            "Z₂-EVEN. G_{55} = φ² is even under y → −y. The radion φ "
            "has an allowed zero mode; stabilization can give it a mass."
        ),
        "resolution": (
            "The objection is valid. Smooth odd B_μ and any even-radion multiple "
            "vanish at orbifold fixed planes. A boundary projection cannot create "
            "a photon. An independent even bulk or boundary gauge sector, or a "
            "different compactification, would need an action and spectrum. "
            "Neither is derived here: photon origin remains OPEN."
        ),
        "status": "OPEN (orbifold photon origin)",
        "fields_are_distinct": False,
        "photon_zero_mode": False,
        "fixed_plane_value": 0.0,
        "code_references": [
            "src/core/metric.py: assemble_5d_metric (G_{μ5} = λφ²B_μ)",
            "src/core/kk_geodesic_reduction.py: Lorentz force = cross-term −2Γ^μ_{ν5}",
            "src/core/geometric_chirality_uniqueness.py: bmu_z2_parity_forces_chirality",
            "1-THEORY/DERIVATION_STATUS.md: Part V, Z₂ Parity Clarification section",
        ],
    }




def _grad(f, dx, axis=0):
    """Central finite-difference gradient of array f along *axis*."""
    return np.gradient(f, dx, axis=axis, edge_order=2)


# ---------------------------------------------------------------------------
# Field strength
# ---------------------------------------------------------------------------

def field_strength(B, dx, coordinate_index=1):
    """Return H_μν = ∂_μ B_ν − ∂_ν B_μ  (shape: N × 4 × 4).

    Parameters
    ----------
    B : ndarray, shape (N, 4)
        Gauge field B_μ sampled on N grid points.
    dx : float
        Grid spacing. Coordinates are (t, x, z, w); the default grid is x.
    coordinate_index : int
        The only coordinate with nonzero derivatives (default 1).
        Use 0 explicitly for a time-dependent homogeneous background.

    Returns
    -------
    H : ndarray, shape (N, 4, 4)
        Antisymmetric field-strength tensor.
    """
    N, D = B.shape
    H = np.zeros((N, D, D))
    _validate_coordinate_index(coordinate_index, D)
    dB = _grad(B, dx)
    H[:, coordinate_index, :] = dB
    H[:, :, coordinate_index] -= dB
    return H


def _validate_coordinate_index(coordinate_index, dimension):
    if not isinstance(coordinate_index, (int, np.integer)) or not 0 <= coordinate_index < dimension:
        raise ValueError("coordinate_index must select a metric coordinate")


# ---------------------------------------------------------------------------
# 5-D metric assembly
# ---------------------------------------------------------------------------

def assemble_5d_metric(g, B, phi, lam=1.0):
    """Assemble the 5×5 Kaluza–Klein metric G_AB at each grid point.

    The KK ansatz with φ as the radion field:

        G_μν = g_μν + λ²φ² B_μ B_ν
        G_μ5 = G_5μ = λφ² B_μ
        G_55 = φ²        (radion; NOT fixed to 1)

    Parameters
    ----------
    g   : ndarray, shape (N, 4, 4)
    B   : ndarray, shape (N, 4)
    phi : ndarray, shape (N,)
    lam : float, KK coupling constant λ (default 1).

    Returns
    -------
    G5 : ndarray, shape (N, 5, 5)
    """
    N = g.shape[0]
    G5 = np.zeros((N, 5, 5))

    lam_phi = lam * phi                          # shape (N,)
    lam_phi_B = (lam * phi**2)[:, None] * B     # shape (N, 4)

    # 4×4 block: g_μν + λ²φ² B_μ B_ν
    G5[:, :4, :4] = g + (lam_phi**2)[:, None, None] * np.einsum('ni,nj->nij', B, B)
    # Off-diagonal from φ²(dy + λ B_μ dx^μ)².
    G5[:, :4, 4] = lam_phi_B
    G5[:, 4, :4] = lam_phi_B
    # G_55 = φ² (radion equals scalar field — not fixed to unity)
    G5[:, 4, 4] = phi**2
    return G5


# ---------------------------------------------------------------------------
# Christoffel symbols (4-D)
# ---------------------------------------------------------------------------

def christoffel(g, dx, coordinate_index=1):
    """Christoffel symbols Γ^σ_μν from a D×D metric on a 1-D grid.

    Only coordinate_index is differentiated: x (index 1) by default, while
    index 0 is time. All other derivatives are zero, not inferred from x.
    This is a one-coordinate ansatz, not a general 1+1 spacetime solver.
    Works for any D (4 for the 4D block, 5 for the full KK metric).

    Parameters
    ----------
    g  : ndarray, shape (N, D, D)
    dx : float

    Returns
    -------
    Gamma : ndarray, shape (N, D, D, D)
        Gamma[n, sigma, mu, nu]
    """
    N, D, _ = g.shape
    _validate_coordinate_index(coordinate_index, D)
    # Guard against near-singular metrics before inversion.
    cond = np.linalg.cond(g)                    # (N,) condition numbers
    bad = np.where(cond > 1e12)[0]
    if bad.size > 0:
        raise ValueError(
            f"Near-singular metric: condition number {cond[bad[0]]:.3e} > 1e12 "
            f"at grid point {bad[0]}. Check for degenerate or zero-component metrics."
        )
    # Inverse metric
    g_inv = np.linalg.inv(g)                    # (N, D, D)

    # Partial derivatives ∂_ρ g_μν  — only x-component is non-trivial on 1-D grid
    # The array's grid axis and the metric's coordinate index are distinct.
    dg = np.zeros((N, D, D, D))
    for mu in range(D):
        for nu in range(D):
            dg[:, coordinate_index, mu, nu] = _grad(g[:, mu, nu], dx)

    # Γ^σ_μν = ½ g^{σρ} (∂_μ g_{νρ} + ∂_ν g_{μρ} − ∂_ρ g_{μν})
    Gamma = np.zeros((N, D, D, D))
    for sigma in range(D):
        for mu in range(D):
            for nu in range(D):
                s = np.zeros(N)
                for rho in range(D):
                    s += g_inv[:, sigma, rho] * (
                        dg[:, mu, nu, rho] +
                        dg[:, nu, mu, rho] -
                        dg[:, rho, mu, nu]
                    )
                Gamma[:, sigma, mu, nu] = 0.5 * s
    return Gamma


# ---------------------------------------------------------------------------
# Riemann, Ricci, Ricci scalar
# ---------------------------------------------------------------------------

def _riemann_from_christoffel(Gamma, dx, coordinate_index=1):
    """R^ρ_σμν from Christoffel symbols (1-D grid, x-direction only).

    R^ρ_σμν = ∂_μ Γ^ρ_νσ − ∂_ν Γ^ρ_μσ + Γ^ρ_μλ Γ^λ_νσ − Γ^ρ_νλ Γ^λ_μσ
    """
    N, D = Gamma.shape[0], Gamma.shape[1]
    _validate_coordinate_index(coordinate_index, D)
    Riem = np.zeros((N, D, D, D, D))

    dGamma = np.zeros_like(Gamma)              # ∂_x Gamma only
    for s in range(D):
        for m in range(D):
            for n in range(D):
                dGamma[:, s, m, n] = _grad(Gamma[:, s, m, n], dx)

    for rho in range(D):
        for sigma in range(D):
            for mu in range(D):
                for nu in range(D):
                    term1 = dGamma[:, rho, nu, sigma] if mu == coordinate_index else np.zeros(N)
                    term2 = dGamma[:, rho, mu, sigma] if nu == coordinate_index else np.zeros(N)
                    # Quadratic terms
                    quad = np.zeros(N)
                    for lam in range(D):
                        quad += (Gamma[:, rho, mu, lam] * Gamma[:, lam, nu, sigma] -
                                 Gamma[:, rho, nu, lam] * Gamma[:, lam, mu, sigma])
                    Riem[:, rho, sigma, mu, nu] = term1 - term2 + quad
    return Riem


def compute_5d_curvature(g, B, phi, dx, lam=1.0, coordinate_index=1):
    """Return full (Γ₅, Riemann₅, Ricci₅, R₅), without discarding mixed blocks.

    Cylinder condition ∂₅=0 is assumed; coordinate_index selects one of the
    four base coordinates. R₅ contracts Ricci₅ with the full inverse metric.
    """
    _validate_coordinate_index(coordinate_index, 4)
    G5 = assemble_5d_metric(g, B, phi, lam)
    Gamma = christoffel(G5, dx, coordinate_index)
    Riemann = _riemann_from_christoffel(Gamma, dx, coordinate_index)
    Ricci = np.einsum("ncacb->nab", Riemann)
    R = np.einsum("nab,nab->n", np.linalg.inv(G5), Ricci)
    return Gamma, Riemann, Ricci, R


def inverse_5d_metric(g, B, phi, lam=1.0):
    """Exact inverse: G^μν=g^μν, G^μ5=−λB^μ, G^55=φ⁻²+λ²B²."""
    g_inv = np.linalg.inv(g)
    B_up = np.einsum("nij,nj->ni", g_inv, B)
    inverse = np.zeros((g.shape[0], 5, 5))
    inverse[:, :4, :4] = g_inv
    inverse[:, :4, 4] = -lam * B_up
    inverse[:, 4, :4] = -lam * B_up
    inverse[:, 4, 4] = 1.0 / phi**2 + lam**2 * np.einsum("ni,ni->n", B, B_up)
    return inverse


def compute_curvature(g, B, phi, dx, lam=1.0, coordinate_index=1):
    """Legacy coordinate blocks of 5D curvature, NOT intrinsic 4D curvature.

    These are coordinate slices, not a gauge-invariant horizontal projection.
    In particular the last output g^μν R^(5)_μν is neither R₄ nor R₅.
    Retained for the phenomenological evolution model; use
    compute_5d_curvature for the scalar entering the Einstein–Hilbert action.

    Steps
    -----
    1. Assemble the 5×5 Kaluza–Klein metric G_AB from (g, B, φ).
    2. Compute 5D Christoffel symbols and Riemann tensor from G_AB.
    3. Extract the 4D Ricci tensor and scalar from the 5D Ricci by
       contracting over the 5D indices and projecting onto the 4D block.

    Parameters
    ----------
    g   : ndarray, shape (N, 4, 4)  — 4-D metric
    B   : ndarray, shape (N, 4)     — irreversibility gauge field
    phi : ndarray, shape (N,)       — scalar / radion (entanglement capacity)
    dx  : float                     — grid spacing
    lam : float                     — KK coupling constant λ

    Returns
    -------
    Gamma  : ndarray, shape (N, 4, 4, 4)   — 4D Christoffel (from 5D projection)
    Riemann: ndarray, shape (N, 4, 4, 4, 4) — 4D Riemann block
    Ricci  : ndarray, shape (N, 4, 4)       — 4D Ricci (projected from 5D)
    R      : ndarray, shape (N,)            — 4D Ricci scalar
    """
    N = g.shape[0]

    # Step 1: assemble full 5D metric
    G5 = assemble_5d_metric(g, B, phi, lam)          # (N, 5, 5)

    # Step 2: 5D Christoffel and Riemann
    _validate_coordinate_index(coordinate_index, 4)
    Gamma5  = christoffel(G5, dx, coordinate_index)
    Riem5   = _riemann_from_christoffel(Gamma5, dx, coordinate_index)

    # Step 3: project 5D Riemann → 4D Ricci and scalar
    # 5D Ricci: Ricci5_{AB} = R^C_{ACB}  (contract index 0 and 2)
    Ricci5 = np.zeros((N, 5, 5))
    for A in range(5):
        for Bx in range(5):
            for C in range(5):
                Ricci5[:, A, Bx] += Riem5[:, C, A, C, Bx]

    # Legacy coordinate block, not the intrinsic or horizontal 4D Ricci.
    Ricci = Ricci5[:, :4, :4]                         # (N, 4, 4)

    # Legacy contraction, neither the intrinsic R4 nor the full R5.
    g_inv = np.linalg.inv(g)
    R = np.einsum('nij,nij->n', g_inv, Ricci)         # (N,)

    # Return 4D Christoffel (4D block of the 5D Gamma) and 4D Riemann block
    Gamma   = Gamma5[:, :4, :4, :4]                   # (N, 4, 4, 4)
    Riemann = Riem5[:, :4, :4, :4, :4]                # (N, 4, 4, 4, 4)

    return Gamma, Riemann, Ricci, R


# ---------------------------------------------------------------------------
# α derivation from 5D Riemann cross-block term
# ---------------------------------------------------------------------------

def extract_alpha_from_curvature(g, B, phi, dx, lam=1.0, coordinate_index=1):
    """Return (0.0, R^μ_{5ν5}) for the two-derivative circle EH truncation.

    R₅ = R₄ − λ²φ²H²/4 − 2□φ/φ generates no R H² operator.
    The former return value mean(φ⁻²) was an inverse-radius diagnostic, not
    an action coefficient. Higher-derivative/quantum/boundary contributions
    to a nonminimal coupling require a separate action-level derivation.
    """
    G5 = assemble_5d_metric(g, B, phi, lam)
    _validate_coordinate_index(coordinate_index, 4)
    Gamma5 = christoffel(G5, dx, coordinate_index)
    Riem5 = _riemann_from_christoffel(Gamma5, dx, coordinate_index)

    # Cross-block Riemann: R^μ_{5ν5} where μ,ν ∈ {0,1,2,3} and 5 → index 4.
    # Convention: Riem5[n, rho, sigma, mu, nu] = R^ρ_σμν
    # So R^μ_{5ν5} = Riem5[n, mu, 4, nu, 4]  with mu,nu ∈ 0..3
    cross_block_riem = Riem5[:, :4, 4, :4, 4].copy()  # (N, 4, 4)

    return 0.0, cross_block_riem


# ---------------------------------------------------------------------------
# [COMPLETION 3]  Index-theorem route to n_w
# ---------------------------------------------------------------------------
#
# Physical location: n_w is a topological invariant of the 5D Dirac operator
# defined on the compactification manifold.  It belongs in the *metric* layer
# because it is derived from the geometry of the compact space, not from any
# inflationary potential or boundary-theory observable.
#
# ---------------------------------------------------------------------------

def derive_nw_index_theorem(
    n_generations: int = 3,
    z2_removes: int = 1,
) -> Tuple[int, Dict[str, Any]]:
    """Construct n_w under two model-dependent assumptions from index-theorem input.

    In the 5D theory compactified on S¹/Z₂ the Dirac operator D₅ acting on
    bulk spinors has a topological index (Atiyah–Singer):

        Index(D₅) = n_L − n_R = n_generations

    where n_L and n_R are the numbers of left- and right-chiral zero modes
    localised on the two fixed-point boundaries of S¹/Z₂.  With three
    observed SM generations:

        Index(D₅) = 3

    The orbifold doubling rule: winding modes come in Z₂-paired copies because
    the S¹/Z₂ boundary conditions identify (y, −y), so each topological
    winding insertion contributes *twice* before the Z₂ projection:

        n_w_before_projection = 2 × Index(D₅) = 6

    n_before = 6 is the shadow-pair parent integer (Pillar 537,
    pillar537_shadow_pair_parent_derivation.py).  The observable braid pair
    (5, 7) = (n_before − z2_removes, n_before + z2_removes) and the
    Chern-Simons level K_CS = (n_before−1)²+(n_before+1)² = 2(n_before²+1) = 74
    follow directly from this single integer — without observational input.

    The Z₂ projection removes one linear combination (the odd-parity mode
    that does not satisfy the orbifold boundary condition):

        n_w = n_w_before_projection − z2_removes = 6 − 1 = 5

    Assumptions (model-dependent; listed explicitly)
    -------------------------------------------------
    (i)  Index(D₅) equals the number of observed SM generations (n_generations).
         This is an identification, not a derivation from first principles.
    (ii) Orbifold doubling ×2: each topological winding insertion contributes
         twice before Z₂ projection.  This is the standard orbifold rule for
         S¹/Z₂ but is model-dependent for other compactifications.
    (iii) Z₂ removes exactly one mode (z2_removes = 1).  The number of modes
          removed depends on the specific boundary conditions imposed and is a
          free input parameter here.

    Parameters
    ----------
    n_generations : int — number of SM generations = Index(D₅) (default 3)
    z2_removes    : int — winding modes removed by the Z₂ projection (default 1)

    Returns
    -------
    (n_w, details) : (int, dict)
        n_w     — constructed winding number (= 5 for standard inputs)
        details — construction trace with keys:
                  ``n_generations``, ``index_D5``, ``n_w_before_Z2``,
                  ``z2_removes``, ``n_w``, ``is_derived`` (legacy bool, kept for
                  API compatibility; the ``assumptions`` key carries the
                  conditionality that ``is_derived`` alone cannot express),
                  ``assumptions``, ``construction_summary``

    Raises
    ------
    ValueError
        If n_generations < 1 or z2_removes < 0 or the resulting n_w < 1.
    """
    if n_generations < 1:
        raise ValueError(
            f"n_generations={n_generations!r} must be a positive integer."
        )
    if z2_removes < 0:
        raise ValueError(
            f"z2_removes={z2_removes!r} must be non-negative."
        )

    n_w_before = 2 * n_generations       # orbifold doubling
    n_w = n_w_before - z2_removes        # Z₂ projection removal

    if n_w < 1:
        raise ValueError(
            f"Resulting n_w={n_w} < 1 for n_generations={n_generations}, "
            f"z2_removes={z2_removes}.  Check input parameters."
        )

    details: Dict[str, Any] = {
        "n_generations":     int(n_generations),
        "index_D5":          int(n_generations),
        "n_w_before_Z2":     int(n_w_before),
        "z2_removes":        int(z2_removes),
        "n_w":               int(n_w),
        "is_derived":        True,   # legacy key; see 'assumptions' key for conditionality
        "assumptions": [
            "Index(D5) = n_generations [identification, not first-principles derivation]",
            "Orbifold doubling x2 [standard S1/Z2 rule; model-dependent]",
            f"Z2 removes exactly {z2_removes} mode(s) [free input parameter]",
        ],
        "construction_summary": (
            "Index(D₅)={ng}  (3 SM generations, assumption i)\n"
            "  →  n_w_raw = 2×{ng} = {nb}  (doubling, assumption ii)\n"
            "  →  Z₂ removes {z2}  (assumption iii)\n"
            "  →  n_w = {nw}  (conditional on all three assumptions)"
        ).format(ng=n_generations, nb=n_w_before, z2=z2_removes, nw=n_w),
        # Legacy key retained for API compatibility
        "derivation_summary": (
            "Index(D₅)={ng}  (3 SM generations)\n"
            "  →  n_w_raw = 2×{ng} = {nb}\n"
            "  →  Z₂ projection removes {z2}\n"
            "  →  n_w = {nw}  (conditional on assumptions; see 'assumptions' key)"
        ).format(ng=n_generations, nb=n_w_before, z2=z2_removes, nw=n_w),
    }
    return int(n_w), details


# ---------------------------------------------------------------------------
# Warped (Randall–Sundrum) 5D metric with dynamical compactification radius
# ---------------------------------------------------------------------------

def assemble_warped_5d_metric(
    g,
    B,
    phi,
    r_c_field,
    k: float = 1.0,
    lam: float = 1.0,
    y: float = 0.0,
):
    """Assemble the 5×5 warped KK metric G_AB with a dynamical compactification
    radius r_c(x), promoting the "frozen scaffold" to a breathing manifold.

    This is a local slice of the warped bundle ansatz:

        ds² = e^{−2k|y|r_c(x)} g_μν dx^μ dx^ν
              + r_c(x)² (dy + λ B_μ dx^μ)²

    In the zero-mode (y-integrated) projection the warp factor is encoded by
    ``jacobian_rs_orbifold``; the on-slice 5×5 metric assembles as:

        G_μν = e^{−2k|y|r_c} g_μν + λ²r_c² B_μ B_ν
        G_μ5 = G_5μ = λr_c² B_μ
        G_55 = r_c(x)²                  (radion size — NOW a separate field)

    The critical difference from :func:`assemble_5d_metric` (where G_55 = φ²)
    is that here *r_c* and *φ* are **independent** fields coupled through the
    Goldberger–Wise radion potential

        V(φ, r_c) = λ_GW φ² (r_c − r_c*)²

    implemented in ``src.core.inflation.goldberger_wise_radion_potential``.

    **Flat-limit recovery**: in the limit r_c(x) → φ(x) (i.e., when the
    compactification radius equals the entanglement scalar) this function
    reduces exactly to :func:`assemble_5d_metric`, recovering G_55 = φ²
    at y=0. No nonminimal R H² coupling is inferred. The warped variant keeps
    r_c and φ as independent degrees of freedom, which is the physically
    motivated choice for RS radion stabilisation.

    Parameters
    ----------
    g         : ndarray, shape (N, 4, 4) — 4D metric tensor
    B         : ndarray, shape (N, 4)    — irreversibility gauge field B_μ
    phi       : ndarray, shape (N,)      — entanglement scalar φ (NOT r_c)
    r_c_field : ndarray, shape (N,)      — local compactification radius [M_Pl⁻¹]
    k         : float                    — AdS curvature scale (default 1)
    lam       : float                    — KK coupling constant λ (default 1)
    y         : float                    — slice coordinate (default 0)

    This does not integrate over y, compute y derivatives, or impose Israel
    junction conditions. The cylinder-condition curvature routines cannot
    establish a warped/orbifold action or its boundary terms from this slice.

    Returns
    -------
    G5 : ndarray, shape (N, 5, 5)
        Full 5×5 warped KK metric at each grid point.

    Raises
    ------
    ValueError
        If any entry of r_c_field is non-positive (compactification radius
        must be positive for the RS geometry to be well-defined).
    """
    r_c_arr = np.asarray(r_c_field, dtype=float)
    if np.any(r_c_arr <= 0.0):
        raise ValueError(
            "r_c_field must be strictly positive at every grid point; "
            f"got min(r_c_field) = {float(np.min(r_c_arr))!r}."
        )

    radius = np.broadcast_to(r_c_arr, (g.shape[0],))
    warp = np.exp(-2.0 * k * abs(y) * radius)
    return assemble_5d_metric(warp[:, None, None] * g, B, radius, lam)
