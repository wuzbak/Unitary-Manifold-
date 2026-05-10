# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/kk_vqe.py
=====================
Variational Quantum Eigensolver (VQE) for the Kaluza–Klein mass eigenvalue
problem in the Unitary Manifold framework.

Physical Background
-------------------
The compact S¹ dimension of the Kaluza–Klein reduction supports a tower of
massive excitations — the KK modes.  On a circle of circumference 2π r_c
the mass spectrum is:

    m_n² = n² / r_c²        (n = 0, 1, 2, …)

with the (5,7) braided winding adding a Chern-Simons correction that mixes
the n=5 and n=7 sectors:

    δH = k_mix × |5⟩⟨7| + h.c.        k_mix = ρ/(r_c²),  ρ = 2 n₁ n₂/k_cs

The full KK Hamiltonian on the first 2^n_qubits modes is thus a matrix whose
diagonal encodes the free KK masses and whose off-diagonal encodes the (5,7)
mixing dictated by the Chern-Simons level k_cs = 74.

This module implements a classical simulation of a VQE circuit to find the
ground state and low-lying excited states of this Hamiltonian.  No quantum
hardware is needed — the circuit is represented as a unitary matrix built
from parameterised Ry rotations and CNOT gates (the hardware-efficient ansatz)
and evaluated entirely with numpy/scipy.  The module is designed to translate
directly to PennyLane or Qiskit circuits: each gate in the ansatz corresponds
1:1 to a quantum gate that can be executed on a real device.

VQE Algorithm (classical simulation)
--------------------------------------
1. Build the KK Hamiltonian matrix H (size 2^n_qubits × 2^n_qubits).
2. Prepare a parameterised ansatz state |ψ(θ)⟩ = U(θ)|0…0⟩ using a
   hardware-efficient circuit: L alternating layers of Ry rotations on all
   qubits + CNOT entangling ladder.
3. Evaluate the energy expectation E(θ) = ⟨ψ(θ)|H|ψ(θ)⟩.
4. Minimise E(θ) using scipy.optimize.minimize (BFGS).
5. Report the ground-state energy and wavefunction, together with the first
   few excited states computed by constrained orthogonal minimisation.

Braid Connection to Topological Quantum Computing
--------------------------------------------------
The (5,7) braid pair maps to a pair of anyons with braiding phase:

    θ_braid = 2π × n₁ n₂ / k_cs = 2π × 35/74 ≈ 2π × 0.4730

which is in the non-Abelian regime (not a rational fraction of 2π with small
denominator).  The KK Hamiltonian's off-diagonal correction can therefore be
interpreted as an anyon braiding interaction; the VQE ground state is the
minimal-energy anyon fusion channel.  See ``docs/TOPOLOGICAL_HARDWARE_ALIGNMENT.md``
for the full hardware mapping.

Public API
----------
kk_hamiltonian(r_c, n_qubits, n1, n2, k_cs, include_braid)
    Build the KK Hamiltonian matrix for the first 2^n_qubits modes.

ansatz_circuit(theta, n_qubits, n_layers)
    Return the unitary U(θ) for the hardware-efficient ansatz.

vqe_kk(r_c, n_qubits, n_layers, n1, n2, k_cs, n_excited, seed)
    Run the full VQE and return a VQEResult.

VQEResult
    Dataclass: ground_energy, ground_state, excited_energies,
    excited_states, n_qubits, n_layers, r_c, n1, n2, k_cs,
    exact_energies, fidelity.

Constants
---------
KK_N1, KK_N2, KK_KCS    canonical braid pair (5, 7, 74)
KK_R_C                   default r_c = φ₀ ≈ sqrt(74) × ℓ_Planck
"""
from __future__ import annotations

__all__ = [
    "kk_hamiltonian",
    "ansatz_circuit",
    "vqe_kk",
    "VQEResult",
    "KK_N1",
    "KK_N2",
    "KK_KCS",
    "KK_R_C",
]

import math
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize

# ---------------------------------------------------------------------------
# Canonical constants from the (5,7,74) braid architecture
# ---------------------------------------------------------------------------

KK_N1: int = 5
KK_N2: int = 7
KK_KCS: int = 74                           # = 5² + 7²
KK_R_C: float = math.sqrt(KK_KCS)         # ≈ 8.602 ℓ_Planck (from φ₀ closure)


# ---------------------------------------------------------------------------
# VQEResult dataclass
# ---------------------------------------------------------------------------

@dataclass
class VQEResult:
    """Output of :func:`vqe_kk`.

    Attributes
    ----------
    ground_energy : float
        VQE ground-state energy ⟨ψ₀|H|ψ₀⟩.
    ground_state : ndarray, shape (2^n_qubits,)
        Normalised ground-state wavefunction.
    excited_energies : list of float
        VQE energies for the first n_excited excited states.
    excited_states : list of ndarray
        Wavefunctions for the excited states.
    n_qubits : int
        Number of qubits.
    n_layers : int
        Number of ansatz layers.
    r_c : float
        Compactification radius (in Planck units).
    n1, n2, k_cs : int
        Braid pair and CS level used.
    exact_energies : ndarray
        Exact eigenvalues of H (from numpy.linalg.eigh) for comparison.
    fidelity : float
        |⟨ψ_VQE|ψ_exact⟩|² — overlap of VQE ground state with exact ground state.
    converged : bool
        Whether the scipy optimiser reported convergence.
    n_function_evals : int
        Number of energy evaluations made by the optimiser.
    """

    ground_energy: float
    ground_state: np.ndarray
    excited_energies: List[float]
    excited_states: List[np.ndarray]
    n_qubits: int
    n_layers: int
    r_c: float
    n1: int
    n2: int
    k_cs: int
    exact_energies: np.ndarray
    fidelity: float
    converged: bool = True
    n_function_evals: int = 0


# ---------------------------------------------------------------------------
# (b-1) KK Hamiltonian matrix
# ---------------------------------------------------------------------------

def kk_hamiltonian(
    r_c: float = KK_R_C,
    n_qubits: int = 3,
    n1: int = KK_N1,
    n2: int = KK_N2,
    k_cs: int = KK_KCS,
    include_braid: bool = True,
) -> np.ndarray:
    """Build the KK mass Hamiltonian for the first 2^n_qubits modes.

    The free KK Hamiltonian on the compact circle S¹ of radius r_c is
    diagonal in the mode-number basis:

        H_free = diag(m_0², m_1², …, m_{N-1}²)    where m_n = n / r_c

    The (n₁, n₂) braided winding correction introduces off-diagonal mixing
    between mode n₁ and mode n₂ at the Chern-Simons level k_cs:

        H_braid = k_mix × (|n₁⟩⟨n₂| + |n₂⟩⟨n₁|)

    where the mixing strength is k_mix = ρ / r_c² with

        ρ = 2 n₁ n₂ / k_cs           (kinetic mixing parameter)

    Parameters
    ----------
    r_c          : float — compactification radius in Planck units.
    n_qubits     : int  — number of qubits; Hilbert space has dim 2^n_qubits.
    n1, n2       : int  — winding numbers of the braid pair (default 5, 7).
    k_cs         : int  — Chern-Simons level (default 74 = 5²+7²).
    include_braid: bool — if True, add the off-diagonal braid correction.

    Returns
    -------
    H : ndarray, shape (dim, dim) — real symmetric Hamiltonian.

    Raises
    ------
    ValueError
        If n1 or n2 >= 2^n_qubits (mode not representable in the Hilbert space).
    """
    dim = 2 ** n_qubits
    if include_braid and (n1 >= dim or n2 >= dim):
        raise ValueError(
            f"Braid modes n1={n1}, n2={n2} exceed Hilbert space dimension {dim}. "
            f"Use n_qubits >= {max(n1, n2).bit_length()}."
        )

    # Free KK spectrum: H_n = n²/r_c²
    modes = np.arange(dim, dtype=float)
    H = np.diag(modes ** 2 / r_c ** 2)

    if include_braid:
        # Kinetic mixing parameter ρ = 2 n₁ n₂ / k_cs
        rho = 2.0 * n1 * n2 / k_cs
        # Mixing strength k_mix = ρ / r_c²
        k_mix = rho / r_c ** 2
        # Off-diagonal correction |n₁⟩⟨n₂| + |n₂⟩⟨n₁|
        H[n1, n2] += k_mix
        H[n2, n1] += k_mix

    return H


# ---------------------------------------------------------------------------
# (b-2) Parameterised ansatz circuit
# ---------------------------------------------------------------------------

def _ry_matrix(theta: float) -> np.ndarray:
    """2×2 rotation matrix Ry(θ) = [[cos θ/2, -sin θ/2], [sin θ/2, cos θ/2]]."""
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.array([[c, -s], [s, c]])


def _cnot_matrix(n_qubits: int, control: int, target: int) -> np.ndarray:
    """Full CNOT unitary on n_qubits qubits (control → target) as a dense matrix.

    Uses the computational basis ordering |q_{n-1} … q_1 q_0⟩ (qubit 0 is
    the least significant bit).
    """
    dim = 2 ** n_qubits
    U = np.eye(dim, dtype=complex)
    for basis_state in range(dim):
        # Check if the control qubit is |1⟩
        if (basis_state >> control) & 1:
            # Flip the target qubit
            flipped = basis_state ^ (1 << target)
            U[basis_state, basis_state] = 0.0
            U[flipped, basis_state] = 1.0
    return U


def _apply_ry_layer(state: np.ndarray, thetas: np.ndarray, n_qubits: int) -> np.ndarray:
    """Apply Ry(θ_i) to qubit i for all i, using tensor products."""
    result = state.reshape([2] * n_qubits)
    for qubit in range(n_qubits):
        Ry = _ry_matrix(thetas[qubit])
        # Contract along the qubit axis
        result = np.tensordot(Ry, result, axes=[[1], [qubit]])
        # tensordot puts the new axis first → move it back
        result = np.moveaxis(result, 0, qubit)
    return result.reshape(-1)


def ansatz_circuit(
    theta: np.ndarray,
    n_qubits: int,
    n_layers: int,
) -> np.ndarray:
    """Build the full ansatz unitary U(θ) as a complex matrix of shape (dim, dim).

    Hardware-efficient ansatz: L layers of
        1. Ry(θ_{l,q}) on every qubit q
        2. CNOT ladder: CNOT(0→1), CNOT(1→2), …, CNOT(n_qubits-2 → n_qubits-1)
    followed by a final Ry layer.

    The ansatz starts from |0…0⟩ and the circuit is expressed as a unitary so
    that U(θ)|0…0⟩ gives the trial state.  For n_qubits ≤ 5 this matrix is
    small enough to build explicitly; for larger systems use a statevector
    simulator.

    Parameters
    ----------
    theta     : array of float, shape (n_params,) where n_params = n_qubits*(n_layers+1)
    n_qubits  : int
    n_layers  : int

    Returns
    -------
    U : ndarray, shape (2^n_qubits, 2^n_qubits), complex
        Unitary matrix of the full ansatz circuit.

    Raises
    ------
    ValueError
        If len(theta) != n_qubits * (n_layers + 1).
    """
    n_params_expected = n_qubits * (n_layers + 1)
    if len(theta) != n_params_expected:
        raise ValueError(
            f"theta has {len(theta)} elements; expected {n_params_expected} "
            f"for n_qubits={n_qubits}, n_layers={n_layers}."
        )

    dim = 2 ** n_qubits
    # Build CNOT ladder matrix (fixed, independent of θ)
    cnot_ladder = np.eye(dim, dtype=complex)
    for q in range(n_qubits - 1):
        cnot_ladder = _cnot_matrix(n_qubits, q, q + 1) @ cnot_ladder

    # Build Ry layer unitaries as tensor products on the full space
    def _ry_full(thetas_layer):
        """Full unitary for Ry(θ_i) on qubit i (all qubits)."""
        # Start with identity in qubit-0 subspace
        U = _ry_matrix(thetas_layer[0])
        for q in range(1, n_qubits):
            U = np.kron(_ry_matrix(thetas_layer[q]), U)
        return U.astype(complex)

    # Assemble: L*(Ry_layer + CNOT_ladder) + final Ry_layer
    U = np.eye(dim, dtype=complex)
    for layer in range(n_layers):
        thetas_layer = theta[layer * n_qubits: (layer + 1) * n_qubits]
        U = _ry_full(thetas_layer) @ U
        U = cnot_ladder @ U
    # Final Ry layer
    thetas_last = theta[n_layers * n_qubits:]
    U = _ry_full(thetas_last) @ U

    return U


def _trial_state(theta: np.ndarray, n_qubits: int, n_layers: int) -> np.ndarray:
    """Return the trial state U(θ)|0…0⟩ without building the full unitary matrix.

    More efficient for large n_qubits: applies each gate sequentially to the
    state vector rather than constructing the O(dim²) unitary matrix.

    Parameters
    ----------
    theta    : array of float, shape (n_qubits*(n_layers+1),)
    n_qubits : int
    n_layers : int

    Returns
    -------
    psi : complex ndarray, shape (2^n_qubits,), normalised.
    """
    dim = 2 ** n_qubits
    psi = np.zeros(dim, dtype=complex)
    psi[0] = 1.0   # |0…0⟩

    cnots = [(q, q + 1) for q in range(n_qubits - 1)]

    for layer in range(n_layers):
        thetas_layer = theta[layer * n_qubits: (layer + 1) * n_qubits]
        psi = _apply_ry_layer(psi, thetas_layer, n_qubits)
        for ctrl, tgt in cnots:
            # CNOT: for each basis state with ctrl=|1⟩, flip the target qubit
            psi_next = np.zeros(dim, dtype=complex)
            for idx in range(dim):
                if (idx >> ctrl) & 1:
                    psi_next[idx ^ (1 << tgt)] += psi[idx]
                else:
                    psi_next[idx] += psi[idx]
            psi = psi_next

    # Final Ry layer
    thetas_last = theta[n_layers * n_qubits:]
    psi = _apply_ry_layer(psi, thetas_last, n_qubits)

    norm = np.linalg.norm(psi)
    return psi / norm if norm > 0 else psi


def _energy_expectation(theta: np.ndarray, H: np.ndarray,
                         n_qubits: int, n_layers: int,
                         orthogonal_states: Optional[List[np.ndarray]] = None,
                         penalty: float = 10.0) -> float:
    """Energy expectation value ⟨ψ(θ)|H|ψ(θ)⟩ with optional orthogonality penalty.

    Parameters
    ----------
    theta            : circuit parameters
    H                : Hamiltonian matrix
    n_qubits, n_layers : circuit shape
    orthogonal_states: list of already-found eigenstates; a penalty term
                       penalty × Σ_k |⟨ψ|k⟩|² is added to enforce orthogonality.
    penalty          : strength of the orthogonality penalty (default 10 × max eigenvalue).

    Returns
    -------
    energy : float
    """
    psi = _trial_state(theta, n_qubits, n_layers)
    energy = float(np.real(psi.conj() @ H @ psi))
    if orthogonal_states:
        for prev in orthogonal_states:
            overlap = abs(prev.conj() @ psi) ** 2
            energy += penalty * overlap
    return energy


# ---------------------------------------------------------------------------
# (b-3) VQE driver
# ---------------------------------------------------------------------------

def vqe_kk(
    r_c: float = KK_R_C,
    n_qubits: int = 3,
    n_layers: int = 2,
    n1: int = KK_N1,
    n2: int = KK_N2,
    k_cs: int = KK_KCS,
    n_excited: int = 2,
    seed: int = 42,
    include_braid: bool = True,
    max_iter: int = 500,
) -> VQEResult:
    """Run the VQE for the KK mass eigenvalue problem.

    Finds the ground state and the first n_excited excited states of the KK
    Hamiltonian by iterative orthogonal VQE (each excited state is found by
    minimising the energy with an orthogonality penalty enforcing it to be
    orthogonal to all previously found states).

    Parameters
    ----------
    r_c          : float — compactification radius (Planck units).  Default: √74.
    n_qubits     : int   — qubits / log₂ of Hilbert space dim.  Default: 3 (8 modes).
    n_layers     : int   — VQE ansatz depth.  Default: 2.
    n1, n2       : int   — braid pair (default 5, 7).
    k_cs         : int   — Chern-Simons level (default 74).
    n_excited    : int   — number of excited states to compute (default 2).
    seed         : int   — RNG seed for initial parameter guess.
    include_braid: bool  — whether to include the braid off-diagonal correction.
    max_iter     : int   — maximum BFGS iterations (default 500).

    Returns
    -------
    VQEResult
        Complete results including ground state, excited states, and comparison
        with the exact diagonalisation from numpy.linalg.eigh.
    """
    H = kk_hamiltonian(r_c=r_c, n_qubits=n_qubits, n1=n1, n2=n2,
                       k_cs=k_cs, include_braid=include_braid)
    dim = 2 ** n_qubits
    n_params = n_qubits * (n_layers + 1)

    # Exact diagonalisation for reference
    exact_vals, exact_vecs = np.linalg.eigh(H)

    rng = np.random.default_rng(seed)
    penalty = float(np.abs(exact_vals).max() * 10.0)

    found_states: List[np.ndarray] = []
    found_energies: List[float] = []
    converged_all = True
    total_fevals = 0

    for state_idx in range(n_excited + 1):
        # Fresh random initialisation for each state
        theta0 = rng.uniform(-np.pi, np.pi, n_params)

        res = minimize(
            _energy_expectation,
            theta0,
            args=(H, n_qubits, n_layers, found_states, penalty),
            method="BFGS",
            options={"maxiter": max_iter, "gtol": 1e-8},
        )
        total_fevals += res.nfev
        if not res.success:
            converged_all = False

        psi = _trial_state(res.x, n_qubits, n_layers)
        energy = float(np.real(psi.conj() @ H @ psi))
        found_states.append(psi)
        found_energies.append(energy)

    ground_energy = found_energies[0]
    ground_state  = found_states[0]
    excited_energies = found_energies[1:]
    excited_states   = found_states[1:]

    # Fidelity: |⟨ψ_VQE | ψ_exact⟩|²
    fidelity = float(abs(exact_vecs[:, 0].conj() @ ground_state) ** 2)

    return VQEResult(
        ground_energy=ground_energy,
        ground_state=ground_state,
        excited_energies=excited_energies,
        excited_states=excited_states,
        n_qubits=n_qubits,
        n_layers=n_layers,
        r_c=r_c,
        n1=n1,
        n2=n2,
        k_cs=k_cs,
        exact_energies=exact_vals,
        fidelity=fidelity,
        converged=converged_all,
        n_function_evals=total_fevals,
    )
