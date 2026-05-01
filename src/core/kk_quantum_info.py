# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_quantum_info.py
============================
Pillar 31 — Quantum Information Structure of the Kaluza-Klein Metric.

Background: the Page of Swords problem
-----------------------------------------
The Unitary Manifold treats the 5D metric g_MN as a classical geometric
object.  This module asks the deeper question: what is the *quantum
information content* of the KK metric?  Specifically, when we decompose

    g_MN  (5D) → { g_μν , A_μ , φ }  (4D)

via the KK ansatz

    ds² = g_μν dx^μ dx^ν + φ² (dy + A_μ dx^μ)²

how much quantum information is entangled between the 4D spacetime sector
{ g_μν } and the compact dimension sector { A_μ, φ }?

Answer: precisely the entanglement entropy of the 5×5 KK metric matrix
treated as a bipartite quantum state in R^5 ⊗ R^5.

Quantum state of the KK metric
-------------------------------
The full 5D KK metric in matrix form is:

    ⎡ g_μν + φ² A_μ A_ν   φ² A_μ ⎤
    ⎣      φ² A_ν          φ²     ⎦

This is a 5×5 real symmetric positive-definite matrix (for a physical
metric).  It lives naturally in R^25 (or in the 15-dimensional symmetric
subspace), but for bipartite entanglement we use the full 5×5 matrix M as a
vector in R^5 ⊗ R^5 via vectorisation:

    |ψ_g⟩  =  vec(M) / ‖M‖_F  ∈  R^25

The "row" subsystem A = R^5 corresponds to the five 4D directions (μ=0..3
plus the compact direction index), and the "column" subsystem B = R^5
corresponds to the same.  The bipartite entanglement is computed via the
SVD of M:

    M = Σ_i σ_i u_i v_i^T   (SVD, σ_i ≥ 0)

The normalised Schmidt coefficients are λ_i = σ_i² / ‖M‖_F² and the
entanglement entropy is

    S(ρ_A) = −Σ_i λ_i ln λ_i                                        [1]

Physical interpretation
------------------------
- When A_μ = 0 and φ = const: M is diagonal → zero off-diagonal mixing →
  S = S_diag (minimal entanglement, depends only on g_μν eigenvalues and φ).

- When A_μ ≠ 0: the off-diagonal blocks couple the 4D metric sector to the
  compact dimension → entanglement increases.  KK photon excitation = metric
  entanglement.

- The braided winding state (n₁, n₂) encodes the two winding modes as a
  2-qubit Bell-like state:

      |ψ_braid⟩ = √p₁ |0,0⟩ + √p₂ |1,1⟩

  where p₁ = (1 + c_s)/2, p₂ = (1 − c_s)/2, c_s = braided sound speed.
  Entanglement entropy:
      S_braid = −p₁ ln p₁ − p₂ ln p₂                                [2]

  At c_s = 12/37 (canonical (5,7)):
      p₁ = 49/74,  p₂ = 25/74
      S_braid ≈ 0.661 nats ≈ 0.953 bits

KK information channel capacity
----------------------------------
The compact dimension acts as a quantum information channel.  Its capacity
is set by the Chern–Simons level k_cs which determines how many
distinguishable winding states fit in the channel:

    C_KK(n₁, n₂) = log₂(k_cs)   [bits]                             [3]

For (5, 7): C_KK = log₂(74) ≈ 6.21 bits.

This is the number of bits that can be transmitted through the compact
dimension per compactification cycle, consistent with the holographic bound
S_BH = A / 4G.

Quantum discord
---------------
For a bipartite pure state |ψ_AB⟩ the quantum discord equals the von Neumann
entropy of either subsystem:

    Q_discord(ρ) = S(ρ_A)   for a pure global state

which equals the entanglement entropy computed via SVD.  For the KK metric
state this quantifies the genuinely quantum (non-classical) correlations
between the 4D metric and the compact dimension.

Public API
----------
kk_metric_matrix(g4, A, phi) -> np.ndarray
    Construct the full 5×5 KK metric matrix from its 4D components.

metric_state_vector(g4, A, phi) -> np.ndarray
    Vectorise and normalise the 5×5 KK metric → unit vector in R^25.

metric_entanglement_entropy(g4, A, phi) -> float
    Bipartite entanglement entropy S(ρ_A) via SVD of the 5×5 metric matrix.

kk_channel_capacity(n1, n2) -> float
    Information channel capacity log₂(k_cs) in bits.

metric_fidelity(g4a, Aa, phia, g4b, Ab, phib) -> float
    Fidelity |⟨ψ_a|ψ_b⟩|² between two metric quantum states.

braided_winding_state(n1, n2) -> np.ndarray
    2-qubit Bell-like state |ψ_braid⟩ encoding the (n₁, n₂) winding pair.

braided_winding_entropy(n1, n2) -> float
    Entanglement entropy of the braided winding state S_braid (eq. [2]).

metric_mutual_information(g4, A, phi) -> float
    Quantum mutual information I(A:B) = 2 S(ρ_A) for the pure KK metric state.

metric_reduced_density_matrix(g4, A, phi) -> np.ndarray
    Reduced density matrix ρ_A of the row subsystem (shape 5×5).

kk_metric_von_neumann_entropy(g4) -> float
    Von Neumann entropy of the 4D metric g_μν treated as a density matrix:
    ρ_g = |g_μν| / Tr(|g_μν|).  Measures geometric "mixedness."

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

import math

import numpy as np

from .braided_winding import (
    resonant_kcs,
    braided_sound_speed,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Canonical braid pair
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
K_CS_CANONICAL: int = 74
C_S_CANONICAL: float = 12.0 / 37.0

_EPS = 1e-300


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def kk_metric_matrix(
    g4: np.ndarray,
    A: np.ndarray,
    phi: float,
) -> np.ndarray:
    """Construct the full 5×5 KK metric matrix.

    The KK ansatz gives:

        g_MN = ⎡ g_μν + φ² A_μ A_ν   φ² A_μ ⎤
               ⎣      φ² A_ν          φ²     ⎦

    where μ, ν = 0, 1, 2, 3.

    Parameters
    ----------
    g4  : array_like, shape (4, 4) — 4D metric tensor g_μν (real, symmetric)
    A   : array_like, shape (4,)   — KK gauge field A_μ (real)
    phi : float                    — radion scalar φ (> 0)

    Returns
    -------
    M : np.ndarray, shape (5, 5), float64

    Raises
    ------
    ValueError if g4 not 4×4, A not length-4, or phi ≤ 0.
    """
    g4 = np.asarray(g4, dtype=float)
    A  = np.asarray(A,  dtype=float).ravel()
    if g4.shape != (4, 4):
        raise ValueError(f"g4 must have shape (4,4), got {g4.shape}.")
    if A.shape != (4,):
        raise ValueError(f"A must have length 4, got {A.shape}.")
    if phi <= 0.0:
        raise ValueError(f"phi={phi!r} must be > 0.")

    phi2 = float(phi) ** 2
    M = np.zeros((5, 5), dtype=float)
    # Upper-left 4×4: g_μν + φ² A_μ A_ν
    M[:4, :4] = g4 + phi2 * np.outer(A, A)
    # Upper-right 4×1 column: φ² A_μ
    M[:4, 4] = phi2 * A
    # Lower-left 1×4 row: φ² A_ν
    M[4, :4] = phi2 * A
    # Lower-right 1×1: φ²
    M[4, 4] = phi2
    return M


def metric_state_vector(
    g4: np.ndarray,
    A: np.ndarray,
    phi: float,
) -> np.ndarray:
    """Vectorise and normalise the 5×5 KK metric into a unit state vector.

    Produces |ψ_g⟩ = vec(M) / ‖M‖_F ∈ R^25.

    Parameters
    ----------
    g4  : array_like, shape (4, 4) — 4D metric tensor
    A   : array_like, shape (4,)   — KK gauge field
    phi : float                    — radion (> 0)

    Returns
    -------
    psi : np.ndarray, shape (25,), float64 — normalised state vector

    Raises
    ------
    ValueError if the metric has zero Frobenius norm.
    """
    M   = kk_metric_matrix(g4, A, phi)
    vec = M.ravel()
    norm = np.linalg.norm(vec)
    if norm < _EPS:
        raise ValueError("KK metric matrix has zero Frobenius norm.")
    return vec / norm


def metric_reduced_density_matrix(
    g4: np.ndarray,
    A: np.ndarray,
    phi: float,
) -> np.ndarray:
    """Reduced density matrix ρ_A for the 'row' (spacetime) subsystem.

    Treats the normalised 5×5 metric matrix as a pure bipartite state in
    R^5 ⊗ R^5 and traces out the column ('compact') subsystem:

        ρ_A = M M^T / ‖M‖_F²

    Eigenvalues of ρ_A are the squared Schmidt coefficients λ_i = σ_i²/‖M‖².

    Parameters
    ----------
    g4, A, phi : see kk_metric_matrix()

    Returns
    -------
    rho_A : np.ndarray, shape (5, 5), float64 — positive semi-definite,
            trace 1.
    """
    M    = kk_metric_matrix(g4, A, phi)
    norm2 = float(np.sum(M ** 2))
    if norm2 < _EPS:
        raise ValueError("KK metric matrix has zero Frobenius norm.")
    return (M @ M.T) / norm2


def metric_entanglement_entropy(
    g4: np.ndarray,
    A: np.ndarray,
    phi: float,
) -> float:
    """Bipartite entanglement entropy of the KK metric state.

    Computed via SVD of the normalised 5×5 metric matrix:

        M̃ = M / ‖M‖_F
        SVD: M̃ = Σ_i σ_i u_i v_i^T
        λ_i = σ_i²  (squared singular values of M̃, sum to 1)
        S = −Σ_i λ_i ln λ_i

    Measures the quantum entanglement between the 4D spacetime (row)
    subsystem and the compact dimension (column) subsystem.

    Parameters
    ----------
    g4, A, phi : see kk_metric_matrix()

    Returns
    -------
    S : float (≥ 0)
    """
    M     = kk_metric_matrix(g4, A, phi)
    norm  = np.linalg.norm(M, 'fro')
    if norm < _EPS:
        raise ValueError("KK metric matrix has zero Frobenius norm.")
    M_norm = M / norm
    sv = np.linalg.svd(M_norm, compute_uv=False)   # singular values of M̃
    lam = sv ** 2                                   # squared → λ_i
    lam = lam[lam > 0.0]
    return float(-np.sum(lam * np.log(lam)))


def kk_channel_capacity(n1: int, n2: int) -> float:
    """Information channel capacity of the compact KK dimension.

    The Chern–Simons level k_cs = n₁² + n₂² sets the number of
    distinguishable winding states that can be encoded in the compact
    dimension per compactification cycle:

        C_KK = log₂(k_cs)   [bits]

    For (5, 7): C_KK = log₂(74) ≈ 6.21 bits.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    C_KK : float (> 0)

    Raises
    ------
    ValueError if n1 < 1 or n2 ≤ n1.
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    return math.log2(float(k_cs))


def metric_fidelity(
    g4a: np.ndarray, Aa: np.ndarray, phia: float,
    g4b: np.ndarray, Ab: np.ndarray, phib: float,
) -> float:
    """Fidelity |⟨ψ_a|ψ_b⟩|² between two KK metric quantum states.

    Parameters
    ----------
    g4a, Aa, phia : components of metric state A
    g4b, Ab, phib : components of metric state B

    Returns
    -------
    F : float in [0, 1]
    """
    psi_a = metric_state_vector(g4a, Aa, phia)
    psi_b = metric_state_vector(g4b, Ab, phib)
    overlap = float(np.dot(psi_a, psi_b))
    return overlap ** 2


def braided_winding_state(n1: int, n2: int) -> np.ndarray:
    """2-qubit Bell-like state encoding the (n₁, n₂) braid winding pair.

    Before braiding the two winding modes are uncorrelated.  After the CS
    coupling locks, they form the entangled state:

        |ψ_braid⟩ = √p₁ |0,0⟩ + √p₂ |1,1⟩

    where
        p₁ = (1 + c_s) / 2   (adiabatic weight)
        p₂ = (1 − c_s) / 2   (isocurvature weight)

    Basis: {|00⟩, |01⟩, |10⟩, |11⟩} in the computational basis.

    For (5, 7): c_s = 12/37  →  |ψ⟩ = √(49/74)|00⟩ + √(25/74)|11⟩.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    psi : np.ndarray, shape (4,), float64 — normalised 2-qubit state vector
        entries indexed [|00⟩, |01⟩, |10⟩, |11⟩]

    Raises
    ------
    ValueError if n1 < 1 or n2 ≤ n1.
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    c_s  = braided_sound_speed(n1, n2, k_cs)
    p1 = (1.0 + c_s) / 2.0   # weight on |00⟩
    p2 = (1.0 - c_s) / 2.0   # weight on |11⟩
    psi = np.zeros(4, dtype=float)
    psi[0] = math.sqrt(p1)   # |00⟩
    psi[3] = math.sqrt(p2)   # |11⟩
    return psi


def braided_winding_entropy(n1: int, n2: int) -> float:
    """Entanglement entropy of the braided winding 2-qubit state.

    For the Bell-like state |ψ_braid⟩ = √p₁|00⟩ + √p₂|11⟩ the
    entanglement entropy equals the Shannon entropy of (p₁, p₂):

        S_braid = −p₁ ln p₁ − p₂ ln p₂

    where  p₁ = (1 + c_s)/2,  p₂ = (1 − c_s)/2.

    For (5, 7): S_braid ≈ 0.661 nats ≈ 0.953 bits.
    Maximum (c_s = 0): S_braid = ln 2 ≈ 0.693 nats.
    Minimum (c_s → 1): S_braid → 0 (product state).

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    S_braid : float (≥ 0)
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    c_s  = braided_sound_speed(n1, n2, k_cs)
    p1 = (1.0 + c_s) / 2.0
    p2 = (1.0 - c_s) / 2.0
    S = 0.0
    for p in (p1, p2):
        if p > 0.0:
            S -= p * math.log(p)
    return S


def metric_mutual_information(
    g4: np.ndarray,
    A: np.ndarray,
    phi: float,
) -> float:
    """Quantum mutual information I(A:B) for the KK metric state.

    For a pure global state |ψ_AB⟩ the mutual information is

        I(A:B) = S(ρ_A) + S(ρ_B) − S(ρ_AB) = 2 S(ρ_A)

    because S(ρ_AB) = 0 (pure state) and S(ρ_A) = S(ρ_B) by Schmidt
    symmetry.

    Parameters
    ----------
    g4, A, phi : see kk_metric_matrix()

    Returns
    -------
    I : float (≥ 0)
    """
    return 2.0 * metric_entanglement_entropy(g4, A, phi)


def kk_metric_von_neumann_entropy(g4: np.ndarray) -> float:
    """Von Neumann entropy of the 4D metric treated as a density matrix.

    The absolute-value matrix |g_μν| (positive semi-definite) is normalised
    to unit trace and treated as a density matrix:

        ρ_g = |g_μν| / Tr(|g_μν|)

    The von Neumann entropy S = −Tr(ρ_g ln ρ_g) measures the geometric
    "mixedness" of the 4D metric.

    For Minkowski η_μν = diag(−1, 1, 1, 1):
        |η| = diag(1, 1, 1, 1) → ρ_g = I/4 → S = ln 4 (maximally mixed).

    Parameters
    ----------
    g4 : array_like, shape (4, 4) — 4D metric tensor (real, symmetric)

    Returns
    -------
    S : float (≥ 0)

    Raises
    ------
    ValueError if g4 does not have shape (4, 4) or has zero trace norm.
    """
    g4 = np.asarray(g4, dtype=float)
    if g4.shape != (4, 4):
        raise ValueError(f"g4 must have shape (4,4), got {g4.shape}.")
    abs_g = np.abs(g4)
    tr = float(np.trace(abs_g))
    if tr < _EPS:
        raise ValueError("g4 has zero trace in absolute value.")
    rho_g = abs_g / tr
    eigenvalues = np.linalg.eigvalsh(rho_g)
    eigenvalues = eigenvalues[eigenvalues > 0.0]
    return float(-np.sum(eigenvalues * np.log(eigenvalues)))


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_pair(n1: int, n2: int) -> None:
    """Raise ValueError for unphysical (n1, n2) pairs."""
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be a positive integer.")
    if n2 <= n1:
        raise ValueError(f"n2={n2!r} must be strictly greater than n1={n1!r}.")
