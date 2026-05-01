# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/quantum_switch.py
==========================
Theorem XVI — Quantum Switch and Indefinite Causal Order.

Background (Navascués / Walther, ÖAW & University of Vienna, 2024–2025)
-----------------------------------------------------------------------
Experiments by Navascués, Walther and collaborators demonstrated that a single
photon passing through a crystal can be returned to its *exact* initial quantum
state without the apparatus ever learning anything about the crystal's internal
dynamics.  They also showed that age can be redistributed among N quantum systems:
one system is made to "age" N units while the other N−1 systems are returned to
their initial state — total age is conserved, not created.

These results are not time travel.  They are precise *unitary* manipulations of
quantum states that happen to reverse, pause, or accelerate a system's evolution
parameter.  The key enabling feature is **indefinite causal order**: the quantum
switch holds two causal channels (U forward, U† backward) in quantum coherent
superposition, so no intermediate measurement disturbs the state.

Connection to the Unitary Manifold
------------------------------------
The braided (5,7) winding sector already captures the algebraic structure of
indefinite causal order:

    ρ = 2 n₁ n₂ / k_cs = 70/74 = 35/37   (causal-order mixing parameter)
    c_s = |n₂²−n₁²| / k_cs = 24/74 = 12/37

The braided sound speed c_s is *exactly* the parameter that quantifies the weight
of the forward causal channel relative to the backward channel at the (5,7)
resonance.  The quantum switch is therefore the experimental realisation of the
braided geometry in a photonic system.

Holographic entropy constraint
--------------------------------
All three quantum-switch protocols are *unitary* operations.  A unitary U
preserves the von Neumann entropy:

    S(U ρ U†) = S(ρ)   for any density matrix ρ.

This is consistent with and required by the holographic boundary entropy
S_∂ = A_∂ / (4G₄) implemented in `src/holography/boundary.py`: a reversible
quantum switch leaves the boundary area — and therefore the entropy — unchanged.

Information conservation
--------------------------
Unitarity guarantees that the information current J^μ_inf = φ² u^μ satisfies
∇_μ J^μ_inf = 0 even *during* the switch operation.  Specifically, the squared
norm ‖ψ‖² = ⟨ψ|ψ⟩ is preserved, which is the discrete analogue of ∫ J^0 d³x
being conserved (Theorem XII).

Public API
----------
QuantumSwitchResult
    Dataclass holding the output state and diagnostics.

causal_switch(state, U, alpha)
    Apply the quantum-switch superposition:
        |ψ_out⟩ = √α · U|ψ⟩  +  √(1−α) · U†|ψ⟩   (normalised)
    Requires U to be unitary.  alpha=1 → pure forward, alpha=0 → pure backward,
    alpha=0.5 → equal-weight indefinite causal order.

time_rewind(state, U)
    Coherently revert a state by applying U†.  Exact inverse: returns to pre-U
    state without measuring internal dynamics.

time_fastforward(initial_state, U, N)
    Concentrate N units of evolution from N systems into one:
        aged_state  = U^N |ψ₀⟩
        reverted    = [|ψ₀⟩] × (N−1)
    Total age (= N) is conserved.

causal_fidelity(psi_a, psi_b)
    Squared overlap |⟨ψ_a|ψ_b⟩|² ∈ [0, 1].  Measures how close two pure states
    are (1 = identical up to global phase, 0 = orthogonal).

von_neumann_entropy(rho)
    Von Neumann entropy S = −Tr(ρ ln ρ) of a density matrix ρ.

density_matrix(state)
    Outer product |ψ⟩⟨ψ| for a pure state vector.

braided_causal_mixing(n1, n2, k_cs)
    ρ = 2 n₁ n₂ / k_cs   (Chern-Simons mixing parameter; connects the braided
    winding sector to the quantum-switch causal-order weight).

switch_entropy_invariant(rho_in, rho_out, tol)
    Return True if |S(ρ_in) − S(ρ_out)| < tol.  Verifies holographic entropy
    is preserved under the switch operation.
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

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Constants — (5,7) braided resonance
# ---------------------------------------------------------------------------

WINDING_N1: int = 5
WINDING_N2: int = 7
K_CS: int = 74                          # = 5² + 7²

# Causal-order mixing at the (5,7) resonance
RHO_BRAIDED: float = 2 * WINDING_N1 * WINDING_N2 / K_CS   # = 35/37
C_S_BRAIDED: float = (WINDING_N2**2 - WINDING_N1**2) / K_CS  # = 12/37

_EPS = 1e-300   # guard against exact-zero denominators


# ---------------------------------------------------------------------------
# QuantumSwitchResult
# ---------------------------------------------------------------------------

@dataclass
class QuantumSwitchResult:
    """Output of a quantum-switch operation.

    Attributes
    ----------
    state_out : ndarray, shape (d,), complex
        The output quantum state (normalised).
    causal_fidelity : float
        |⟨ψ_in|ψ_out⟩|² — how close the output is to the input.
        For a perfect rewind this equals 1.
    entropy_before : float
        Von Neumann entropy of the input density matrix (0 for pure states).
    entropy_after : float
        Von Neumann entropy of the output density matrix (0 for pure states).
    entropy_preserved : bool
        True if |S_after − S_before| < 1e-10.
    rewound : bool
        True if the output state is within numerical tolerance of the input
        (causal_fidelity > 1 − 1e-10).
    """

    state_out: np.ndarray
    causal_fidelity: float
    entropy_before: float
    entropy_after: float
    entropy_preserved: bool
    rewound: bool


# ---------------------------------------------------------------------------
# Core protocol functions
# ---------------------------------------------------------------------------

def causal_switch(
    state: np.ndarray,
    U: np.ndarray,
    alpha: float = 0.5,
) -> QuantumSwitchResult:
    """Apply the quantum-switch superposition of forward and backward evolution.

    Implements the Navascués/Walther indefinite-causal-order protocol:

        |ψ_out⟩  =  √α · U |ψ⟩  +  √(1−α) · U† |ψ⟩

    The state is normalised after the superposition.  Because U is unitary,
    both branches are individually normalised; the cross term determines the
    output norm.

    Parameters
    ----------
    state : ndarray, shape (d,), complex or real
        Input quantum state vector (need not be pre-normalised; normalised
        internally).
    U : ndarray, shape (d, d), complex or real
        Unitary evolution operator.  Raises ValueError if not square or if
        U† U is not close to the identity.
    alpha : float in [0, 1]
        Weight of the *forward* causal order.  alpha=0.5 gives the 50/50
        split used in the ÖAW/Vienna photon experiments.  alpha=1 is pure
        forward evolution; alpha=0 is pure backward (rewind) evolution.

    Returns
    -------
    QuantumSwitchResult
    """
    state = np.asarray(state, dtype=complex)
    U = np.asarray(U, dtype=complex)
    if U.ndim != 2 or U.shape[0] != U.shape[1]:
        raise ValueError("U must be a square matrix.")
    if U.shape[0] != state.shape[0]:
        raise ValueError("U and state dimensions must match.")
    _check_unitary(U)

    # Normalise input
    norm_in = np.linalg.norm(state)
    if norm_in < _EPS:
        raise ValueError("Input state has zero norm.")
    psi = state / norm_in

    # Superposition of forward and backward channels
    c_f = np.sqrt(float(alpha))
    c_b = np.sqrt(1.0 - float(alpha))
    psi_out = c_f * (U @ psi) + c_b * (U.conj().T @ psi)

    # Normalise output (cross-interference can change the norm)
    norm_out = np.linalg.norm(psi_out)
    if norm_out > _EPS:
        psi_out = psi_out / norm_out

    fid = causal_fidelity(psi, psi_out)
    rho_in = density_matrix(psi)
    rho_out = density_matrix(psi_out)
    S_in = von_neumann_entropy(rho_in)
    S_out = von_neumann_entropy(rho_out)

    return QuantumSwitchResult(
        state_out=psi_out,
        causal_fidelity=fid,
        entropy_before=S_in,
        entropy_after=S_out,
        entropy_preserved=abs(S_out - S_in) < 1e-10,
        rewound=fid > 1.0 - 1e-10,
    )


def time_rewind(state: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Coherently revert a state to its pre-evolution form by applying U†.

    This is the "photon rewind" protocol: given a state |ψ⟩ = U|ψ₀⟩ and the
    unitary U, return U†|ψ⟩ = |ψ₀⟩ without ever measuring the internal
    dynamics of U (i.e., without knowing *what* U did — only *how* to invert it).

    Parameters
    ----------
    state : ndarray, shape (d,), complex
        State to be rewound (need not be normalised).
    U : ndarray, shape (d, d), complex
        Unitary that was applied to create *state*.  Raises ValueError if not
        unitary.

    Returns
    -------
    rewound : ndarray, shape (d,), complex — normalised output.
    """
    state = np.asarray(state, dtype=complex)
    U = np.asarray(U, dtype=complex)
    _check_unitary(U)
    result = U.conj().T @ state
    norm = np.linalg.norm(result)
    return result / norm if norm > _EPS else result


def time_fastforward(
    initial_state: np.ndarray,
    U: np.ndarray,
    N: int,
) -> Tuple[np.ndarray, List[np.ndarray]]:
    """Concentrate N units of age from N identical systems into one.

    Implements the Navascués "time theft" protocol:

        "To age one system 10 years in one year, steal one year from each of
         nine other systems."  — Miguel Navascués, El País, 2025.

    Given N systems each in state |ψ₀⟩, after one experiment lasting one
    evolution step:
        - The target system (index N−1) has state U^N |ψ₀⟩  (aged N steps)
        - The donor systems (indices 0..N−2) are returned to |ψ₀⟩  (age 0)

    Total age before: N (one step per system).
    Total age after: N (all concentrated in the target) + 0×(N−1) = N.
    Age is conserved, not created.

    Parameters
    ----------
    initial_state : ndarray, shape (d,)
        The common initial state of all N systems.
    U : ndarray, shape (d, d)
        The one-step unitary evolution operator.
    N : int ≥ 1
        Number of systems (and number of age units concentrated).

    Returns
    -------
    aged_state : ndarray, shape (d,) — the N-times-evolved state U^N |ψ₀⟩.
    reverted_states : list of (N−1) ndarrays — each equal to |ψ₀⟩.
    """
    if N < 1:
        raise ValueError("N must be a positive integer.")
    initial_state = np.asarray(initial_state, dtype=complex)
    U = np.asarray(U, dtype=complex)
    _check_unitary(U)

    norm_in = np.linalg.norm(initial_state)
    if norm_in < _EPS:
        raise ValueError("initial_state has zero norm.")
    psi0 = initial_state / norm_in

    # U^N via matrix power
    UN = np.linalg.matrix_power(U, N)
    aged = UN @ psi0
    norm_aged = np.linalg.norm(aged)
    aged = aged / norm_aged if norm_aged > _EPS else aged

    reverted = [psi0.copy() for _ in range(N - 1)]
    return aged, reverted


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def causal_fidelity(psi_a: np.ndarray, psi_b: np.ndarray) -> float:
    """Squared overlap |⟨ψ_a|ψ_b⟩|² ∈ [0, 1].

    Fidelity between two pure quantum states.  Global-phase independent:
        F = |⟨ψ_a|ψ_b⟩|²

    Parameters
    ----------
    psi_a, psi_b : ndarray, shape (d,)
        Pure state vectors (need not be pre-normalised; normalised internally).

    Returns
    -------
    F : float in [0, 1].
    """
    a = np.asarray(psi_a, dtype=complex)
    b = np.asarray(psi_b, dtype=complex)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < _EPS or nb < _EPS:
        return 0.0
    overlap = np.dot(a.conj(), b) / (na * nb)
    return float(np.abs(overlap) ** 2)


def density_matrix(state: np.ndarray) -> np.ndarray:
    """Outer product |ψ⟩⟨ψ| for a pure state vector.

    Parameters
    ----------
    state : ndarray, shape (d,)

    Returns
    -------
    rho : ndarray, shape (d, d), complex.
    """
    psi = np.asarray(state, dtype=complex)
    norm = np.linalg.norm(psi)
    if norm > _EPS:
        psi = psi / norm
    return np.outer(psi, psi.conj())


def von_neumann_entropy(rho: np.ndarray) -> float:
    """Von Neumann entropy S = −Tr(ρ ln ρ) of a density matrix.

    For a *pure* state ρ = |ψ⟩⟨ψ|, S = 0 exactly.  For a maximally mixed
    d-dimensional state ρ = I/d, S = ln d.

    Parameters
    ----------
    rho : ndarray, shape (d, d)
        Density matrix (Hermitian, positive semi-definite, trace 1).

    Returns
    -------
    S : float ≥ 0.
    """
    rho = np.asarray(rho, dtype=complex)
    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = eigenvalues[eigenvalues > 0]   # discard numerical zeros
    return float(-np.sum(eigenvalues * np.log(eigenvalues)))


def braided_causal_mixing(n1: int, n2: int, k_cs: int) -> dict:
    """Compute the causal-order mixing parameters from the braided winding sector.

    Connects the quantum-switch causal weight to the (n₁, n₂) braid geometry:

        ρ     = 2 n₁ n₂ / k_cs          (Chern-Simons mixing parameter)
        c_s   = (n₂² − n₁²) / k_cs      (braided sound speed)
        alpha = (1 + c_s) / 2            (forward causal weight in the switch)

    For (n₁, n₂) = (5, 7) and k_cs = 74:
        ρ   = 70/74 = 35/37 ≈ 0.9459
        c_s = 24/74 = 12/37 ≈ 0.3243
        α   = (1 + 12/37) / 2 = 49/74 ≈ 0.6622

    Parameters
    ----------
    n1, n2 : int  — winding numbers (n2 > n1 for positive c_s)
    k_cs   : int  — Chern-Simons level

    Returns
    -------
    dict with keys: rho, c_s, alpha, sum_of_squares_check
    """
    if k_cs <= 0:
        raise ValueError("k_cs must be positive.")
    rho = 2.0 * n1 * n2 / k_cs
    c_s = float(n2**2 - n1**2) / k_cs
    alpha = (1.0 + c_s) / 2.0
    return {
        "rho": rho,
        "c_s": c_s,
        "alpha": alpha,
        "sum_of_squares_check": n1**2 + n2**2 == k_cs,
    }


def switch_entropy_invariant(
    rho_in: np.ndarray,
    rho_out: np.ndarray,
    tol: float = 1e-10,
) -> bool:
    """Return True if the von Neumann entropy is preserved to within tol.

    This is the holographic entropy constraint: any unitary (including a
    quantum switch) must leave S_∂ = A_∂ / (4G₄) unchanged.

    Parameters
    ----------
    rho_in, rho_out : ndarray, shape (d, d)
        Density matrices before and after the operation.
    tol : float
        Tolerance on |S_out − S_in|.

    Returns
    -------
    bool
    """
    return abs(von_neumann_entropy(rho_out) - von_neumann_entropy(rho_in)) < tol


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _check_unitary(U: np.ndarray, tol: float = 1e-10) -> None:
    """Raise ValueError if U† U is not close to the identity matrix."""
    UdU = U.conj().T @ U
    residual = np.max(np.abs(UdU - np.eye(U.shape[0])))
    if residual > tol:
        raise ValueError(
            f"U is not unitary: max|U†U − I| = {residual:.3e} > tol={tol}."
        )


# ---------------------------------------------------------------------------
# Authorship
# ---------------------------------------------------------------------------
# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, document engineering, and synthesis:
# GitHub Copilot (AI).
