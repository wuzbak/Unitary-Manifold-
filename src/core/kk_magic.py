# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_magic.py
=====================
Pillar 101 — KK Magic Power & Quantum Circuit Complexity.

Background: Robin–Savage arXiv:2604.26376
------------------------------------------
Robin and Savage (2026) review how *quantum complexity* — specifically the
concept of **quantum magic** (non-stabilizerness) — quantifies the computational
resources needed to simulate nuclear and high-energy physics on a quantum
computer.  "Magic" is the resource that enables universal quantum computation
beyond what stabilizer circuits can do cheaply.  For a pure state |ψ⟩ the
*stabilizer Rényi entropy* (SRE) M₂ and the *Mana* (Wigner function negativity)
are two complementary measures.

Connection to the Unitary Manifold
-------------------------------------
Pillar 31 (`kk_quantum_info.py`) already computes the **entanglement entropy**
of the braided winding state

    |ψ_braid⟩ = √p₁ |00⟩ + √p₂ |11⟩,   p₁ = 49/74,  p₂ = 25/74

where p₁ = (1 + c_s)/2, p₂ = (1 − c_s)/2 and c_s = 12/37.

This state is NOT a stabilizer state: it is an asymmetric Bell state with
unequal weights.  Equal-weight Bell states (p₁ = p₂ = ½) are *maximally
entangled* stabilizer states; perturbing the weights immediately generates
non-zero magic.

This Pillar computes the magic content and the associated quantum circuit
complexity, providing the bridge between:

    Geometry (braided KK winding) → Quantum information → Nuclear simulation cost

Magic measures implemented
--------------------------
1. **Stabilizer Rényi Entropy M₂** (Leone, Oliviero, Hamma 2022)

   For a pure n-qubit state |ψ⟩ the stabilizer Rényi entropy of order 2 is

       M₂(ψ) = − log₂[ Σ_{P∈Pₙ} Tr(P|ψ⟩⟨ψ|)⁴ ] − n             [1]

   equivalently written in terms of the characteristic function Ξ_ψ(P):

       Ξ_ψ(P) = ⟨ψ|P|ψ⟩²,   Σ_P Ξ_ψ(P) = 2^n (normalisation)

       M₂(ψ) = − log₂[ Σ_P Ξ_ψ(P)² / 2^n ] − n                  [2]

   For the 2-qubit braided state we enumerate all 4² = 16 Pauli operators
   {I, X, Y, Z}⊗{I, X, Y, Z} and sum Ξ²(P).

2. **Mana / Wigner negativity** (Veitch et al. 2012; Bravyi et al. 2016)

   For odd-prime dimensions the Wigner function is well-defined; for
   qubits (dimension 2) one uses the *discrete Wigner function* via the
   phase-space formulation of Gibbons, Hoffman & Wootters.  The Mana is

       M(ψ) = log₂[ Σ_{q,p} |W_ψ(q,p)| ]                         [3]

   where W_ψ(q,p) is the discrete Wigner function evaluated at phase-space
   point (q, p).  For a product state W ≥ 0 everywhere; for a magic state
   W takes negative values.

   For a single-qubit pure state ρ = |ψ⟩⟨ψ|:
       W(0,0) = (1 + ⟨Z⟩)/2,   W(0,1) = (1 − ⟨Z⟩)/2
       W(1,0) = (1 + ⟨X⟩)/2,   W(1,1) = (1 − ⟨X⟩)/2
   (Wootters 1987 discrete Wigner convention for qubits)

   For the 2-qubit braided state we use the tensor-product extension:
       W_{AB}(q_A, p_A, q_B, p_B) = W_A(q_A, p_A) × W_B(q_B, p_B)
   is NO LONGER valid (state is entangled); instead we compute the 2-qubit
   discrete Wigner function directly from the Hilbert-Schmidt expansion:

       W_ψ(α) = (1/4) Tr(A_α ρ)   where A_α are the phase-point operators.

3. **T-gate lower bound (circuit complexity)**

   For a target precision ε on an n-qubit unitary, the Solovay–Kitaev theorem
   and the resource theory of magic imply that the number of T-gates required
   scales as

       T_count ≥ max[ 2^(M₂/n) , 1 ]  (resource-theoretic lower bound)

   For the UM: M₂(ψ_braid) provides the minimum T-gate overhead needed to
   prepare the braided winding state |ψ_braid⟩ from a stabilizer state.

   The total information cost of the KK channel (Pillar 31):
       C_KK = log₂(k_cs) bits
   sets the classical information register required alongside the quantum
   circuit.  The combined classical+quantum simulation cost is

       cost_total = C_KK  [classical bits]  +  T_count  [T-gates]       [4]

4. **Robin–Savage nuclear bridge**

   For the UM-modified nuclear S-factor (cold_fusion.py / lattice_dynamics.py)
   the 5D geometric modification replaces the standard Gamow factor by

       G_5D = G_bare × exp(−Φ_φ)

   where Φ_φ encodes φ-enhanced tunneling.  The *magic power* of the S-matrix
   state associated with this geometric modification is a monotone function of
   the magic content of the input state:

       magic_power_S(ψ_nuc) ∝ M₂(ψ_braid) × (r_braided / r_bare)

   This is the dimensional bridge: the braided winding magic M₂ sets the
   non-classical overhead needed to simulate the φ-modified nuclear reaction
   rate on a quantum computer.

Public API
----------
Pauli operators (2-qubit)
    PAULI_2Q : list[np.ndarray] — all 16 two-qubit Pauli operators.

characteristic_function(state) -> np.ndarray
    ⟨ψ|P|ψ⟩² for all Pauli P; shape (16,).

stabilizer_renyi_entropy_m2(state) -> float
    M₂ stabilizer Rényi entropy of a 2-qubit pure state (bits).

phase_point_operators_2q() -> list[np.ndarray]
    16 discrete phase-point operators A_α for 2-qubit Hilbert space.

discrete_wigner_function(state) -> np.ndarray
    Discrete Wigner function values W(α) for all 16 phase-space points;
    shape (16,).

wigner_negativity(state) -> float
    Total Wigner negativity = Σ_α max(0, −W_ψ(α)); ≥ 0.

mana(state) -> float
    Mana M(ψ) = log₂(Σ_α |W(α)|) ≥ 0 (bits).

t_gate_lower_bound(m2) -> float
    Lower bound on the number of T-gates to prepare a state with M₂ magic.

kk_magic_summary(n1, n2) -> dict
    Full magic-power summary for the (n1,n2) braided winding state.

magic_power_nuclear_bridge(n1, n2, r_ratio) -> dict
    Robin–Savage bridge: magic overhead for simulating the φ-modified
    nuclear S-factor on a quantum computer.

nuclear_simulation_cost(n1, n2) -> dict
    Combined classical + quantum simulation cost: C_KK bits + T-gate count.

is_stabilizer_state(state, tol) -> bool
    Return True if M₂ ≈ 0 (state lies in the stabilizer polytope).
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
from typing import Dict, List

import numpy as np

from .braided_winding import resonant_kcs, braided_sound_speed
from .kk_quantum_info import (
    braided_winding_state,
    braided_winding_entropy,
    kk_channel_capacity,
    N1_CANONICAL,
    N2_CANONICAL,
    K_CS_CANONICAL,
    C_S_CANONICAL,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: r_braided / r_bare ratio at one-loop (from braided_winding.r_one_loop_bound)
R_RATIO_CANONICAL: float = 1.0 - 1.78e-4     # ≈ 0.9998  (one-loop suppression)

#: Pillar identity
PILLAR: int = 101

_EPS = 1e-300


# ---------------------------------------------------------------------------
# Single-qubit Pauli matrices (complex for generality, though state is real)
# ---------------------------------------------------------------------------

_I2 = np.eye(2, dtype=complex)
_X  = np.array([[0, 1], [1, 0]], dtype=complex)
_Y  = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z  = np.array([[1, 0], [0, -1]], dtype=complex)

_PAULIS_1Q: List[np.ndarray] = [_I2, _X, _Y, _Z]
_PAULI_LABELS_1Q: List[str] = ["I", "X", "Y", "Z"]


def _build_pauli_2q() -> List[np.ndarray]:
    """Build all 16 two-qubit Pauli operators P₁ ⊗ P₂."""
    ops = []
    for a in _PAULIS_1Q:
        for b in _PAULIS_1Q:
            ops.append(np.kron(a, b))
    return ops


#: All 16 two-qubit Pauli operators in lexicographic order II, IX, IY, IZ, XI, ...
PAULI_2Q: List[np.ndarray] = _build_pauli_2q()

#: Labels for the 16 Pauli operators
PAULI_2Q_LABELS: List[str] = [
    a + b for a in _PAULI_LABELS_1Q for b in _PAULI_LABELS_1Q
]


# ---------------------------------------------------------------------------
# Characteristic function
# ---------------------------------------------------------------------------

def characteristic_function(state: np.ndarray) -> np.ndarray:
    """Compute the squared Pauli expectation values (characteristic function).

    For a pure 2-qubit state |ψ⟩ (4-component vector, real or complex)
    returns

        Ξ(P) = ⟨ψ|P|ψ⟩²

    for all 16 two-qubit Pauli operators P.  These are real (expectation
    values of Hermitian operators are real for pure states, so squaring
    keeps them real and non-negative).

    Parameters
    ----------
    state : array_like, shape (4,) — normalised 2-qubit state vector (complex or real)

    Returns
    -------
    xi : np.ndarray, shape (16,), float64 — Ξ(P) for all 16 Paulis

    Raises
    ------
    ValueError if state does not have shape (4,) or is not normalised.
    """
    psi = np.asarray(state, dtype=complex).ravel()
    _validate_2qubit_state(psi)
    xi = np.empty(16, dtype=float)
    for k, P in enumerate(PAULI_2Q):
        exp_val = float(np.real(psi.conj() @ P @ psi))
        xi[k] = exp_val ** 2
    return xi


# ---------------------------------------------------------------------------
# Stabilizer Rényi entropy M₂
# ---------------------------------------------------------------------------

def stabilizer_renyi_entropy_m2(state: np.ndarray) -> float:
    """Stabilizer Rényi entropy M₂ of a 2-qubit pure state.

    Uses the definition of Leone, Oliviero & Hamma (2022):

        M₂(ψ) = − log₂[ Σ_{P} Ξ_ψ(P) / 2^n ] − n       (n = 2 qubits)

    where Ξ_ψ(P) = ⟨ψ|P|ψ⟩² and n = 2.  The normalisation factor 2^n = 4
    ensures M₂ = 0 for any stabilizer state.

    Physical interpretation: M₂ is the magic-order analogue of the Rényi-2
    entropy.  A stabilizer state (M₂ = 0) can be prepared with zero T-gates.
    A generic quantum state has M₂ > 0, and its preparation requires T-gates
    whose count grows with M₂.

    Parameters
    ----------
    state : array_like, shape (4,) — normalised 2-qubit state

    Returns
    -------
    M2 : float ≥ 0 (bits)

    Raises
    ------
    ValueError if state not (4,) or not normalised.
    """
    xi = characteristic_function(state)
    n = 2
    # Correct SRE-M₂ formula (Leone, Oliviero & Hamma 2022):
    #   M₂(ψ) = n − log₂( Σ_P ⟨P⟩⁴ )
    # where xi[k] = ⟨P⟩² so xi[k]² = ⟨P⟩⁴.
    # Derivation — Leone et al. define a normalised characteristic function
    #   χ_P = 2^{-n} ⟨P⟩²  and the SRE at order α as (1/(1-α)) log₂(Σ_P χ_P^α).
    # At α=2:
    #   M₂ = (1/(1-2)) log₂(Σ_P [2^{-n}⟨P⟩²]²)
    #       = -log₂( 2^{-2n} Σ_P ⟨P⟩⁴ )
    #       = -log₂(Σ_P ⟨P⟩⁴) + 2n
    # The Leone convention subtracts n to make stabilizer states give M₂=0:
    #   M₂ = (-log₂(Σ_P ⟨P⟩⁴) + 2n) - n = n - log₂(Σ_P ⟨P⟩⁴)
    # Sanity: |00⟩ has 2^n=4 stabilisers with ⟨P⟩²=1, rest 0 → Σ⟨P⟩⁴=4=2^n
    #   → M₂ = n − log₂(2^n) = n − n = 0  ✓
    sum_xi_sq = float(np.sum(xi ** 2))          # = Σ_P ⟨P⟩⁴
    M2 = n - math.log2(max(sum_xi_sq, _EPS))
    return max(M2, 0.0)   # clamp floating-point rounding noise


# ---------------------------------------------------------------------------
# Discrete Wigner function (2-qubit)
# ---------------------------------------------------------------------------

def phase_point_operators_2q() -> List[np.ndarray]:
    """Build the 16 discrete phase-point operators for a 2-qubit system.

    Following the Hilbert-Schmidt decomposition approach (Wootters 1987 /
    Gibbons–Hoffman–Wootters 2004 extended to 2 qubits via tensor product):

        A_α = (1/4) Σ_{P} (-1)^{f(α,P)} P

    where the exponent f(α, P) is determined by the symplectic inner product
    of the phase-space point α with the Pauli index.

    For the 2-qubit case with phase-space Z₂ × Z₂ × Z₂ × Z₂ (four bits:
    q₁, p₁, q₂, p₂ each ∈ {0,1}), the phase-point operator at index
    α = (q₁, p₁, q₂, p₂) is defined as

        A_α = A_{(q₁,p₁)} ⊗ A_{(q₂,p₂)}

    where the single-qubit phase-point operators are

        A_{(0,0)} = (I + Z + X + Y) / 2
        A_{(1,0)} = (I − Z + X − Y) / 2
        A_{(0,1)} = (I + Z − X − Y) / 2
        A_{(1,1)} = (I − Z − X + Y) / 2

    (standard discrete-phase-space construction for d=2).

    Returns
    -------
    ops : list of 16 arrays, each shape (4, 4), complex
        Ordered as (q₁,p₁,q₂,p₂) with (0,0,0,0) first; lexicographic order.
    """
    # Single-qubit phase-point operators
    A_sq = {
        (0, 0): (_I2 + _Z + _X + _Y) / 2.0,
        (1, 0): (_I2 - _Z + _X - _Y) / 2.0,
        (0, 1): (_I2 + _Z - _X - _Y) / 2.0,
        (1, 1): (_I2 - _Z - _X + _Y) / 2.0,
    }
    ops = []
    for q1 in range(2):
        for p1 in range(2):
            for q2 in range(2):
                for p2 in range(2):
                    ops.append(np.kron(A_sq[(q1, p1)], A_sq[(q2, p2)]))
    return ops


_PHASE_POINT_OPS: List[np.ndarray] = phase_point_operators_2q()


def discrete_wigner_function(state: np.ndarray) -> np.ndarray:
    """Discrete Wigner function for a 2-qubit pure state.

    Computes

        W_ψ(α) = (1/4) Tr(A_α ρ)     ρ = |ψ⟩⟨ψ|

    at all 16 phase-space points α.  The result sums to 1 (normalisation)
    and takes values in R.  Negative values indicate quantum magic (non-
    stabilizerness).

    Parameters
    ----------
    state : array_like, shape (4,) — normalised 2-qubit state

    Returns
    -------
    W : np.ndarray, shape (16,), float64
        Discrete Wigner function values; sum = 1; may include negatives.
    """
    psi = np.asarray(state, dtype=complex).ravel()
    _validate_2qubit_state(psi)
    rho = np.outer(psi, psi.conj())  # |ψ⟩⟨ψ|
    W = np.empty(16, dtype=float)
    for k, A in enumerate(_PHASE_POINT_OPS):
        W[k] = float(np.real(np.trace(A @ rho))) / 4.0
    return W


def wigner_negativity(state: np.ndarray) -> float:
    """Total Wigner negativity of a 2-qubit pure state.

    Defined as

        N(ψ) = Σ_{α : W(α) < 0}  |W_ψ(α)|

    i.e. the sum of the absolute values of all negative Wigner function
    entries.  N(ψ) = 0 iff |ψ⟩ is a stabilizer state.

    Parameters
    ----------
    state : array_like, shape (4,) — normalised 2-qubit state

    Returns
    -------
    neg : float ≥ 0
    """
    W = discrete_wigner_function(state)
    return float(np.sum(np.abs(W[W < 0.0])))


def mana(state: np.ndarray) -> float:
    """Mana of a 2-qubit pure state (Wigner-function-based magic measure).

    The Mana is

        M(ψ) = log₂( Σ_α |W_ψ(α)| )       (bits)

    where W_ψ is the discrete Wigner function.  For a stabilizer state all
    Wigner values are non-negative, so |W| sums to 1 and M = log₂(1) = 0.
    For a magic state negative entries inflate the ℓ¹ norm above 1, giving
    M > 0.

    Parameters
    ----------
    state : array_like, shape (4,) — normalised 2-qubit state

    Returns
    -------
    M : float ≥ 0 (bits)
    """
    W = discrete_wigner_function(state)
    l1_norm = float(np.sum(np.abs(W)))
    if l1_norm < _EPS:
        return 0.0
    return max(math.log2(l1_norm), 0.0)


# ---------------------------------------------------------------------------
# T-gate lower bound
# ---------------------------------------------------------------------------

def t_gate_lower_bound(m2: float) -> float:
    """Resource-theoretic lower bound on the T-gate count to prepare a 2-qubit state.

    From the resource theory of magic (Bravyi & Gosset 2016; Campbell et al.
    2017), the number of T-gates needed to prepare a state |ψ⟩ from the
    computational basis using a stabilizer circuit plus T-gates satisfies

        T_count ≥ 2^(M₂ / n)                                         [T-bound]

    where M₂ is the stabilizer Rényi entropy in bits and n = 2 is the
    number of qubits.

    For M₂ = 0 (stabilizer state): T_count ≥ 1 (one T-gate or zero, but
    we report the bound as 1).  For M₂ > 0 the bound grows exponentially
    with magic content.

    Parameters
    ----------
    m2 : float — M₂ stabilizer Rényi entropy (bits), ≥ 0.

    Returns
    -------
    T_lb : float ≥ 1
    """
    if m2 < 0.0:
        raise ValueError(f"m2={m2!r} must be ≥ 0.")
    n = 2
    return max(2.0 ** (m2 / n), 1.0)


# ---------------------------------------------------------------------------
# KK magic summary
# ---------------------------------------------------------------------------

def kk_magic_summary(n1: int, n2: int) -> Dict:
    """Complete magic-power summary for the (n1, n2) braided winding state.

    Computes all magic measures and circuit-complexity bounds for the
    canonical Bell-like braided winding state

        |ψ_braid⟩ = √p₁ |00⟩ + √p₂ |11⟩,
        p₁ = (1 + c_s)/2,  p₂ = (1 − c_s)/2.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    summary : dict with keys
        'n1', 'n2' : winding numbers
        'k_cs'     : Chern–Simons level k_cs = n1² + n2²
        'c_s'      : braided sound speed
        'p1', 'p2' : Schmidt weights
        'S_entanglement' : entanglement entropy (nats) from Pillar 31
        'S_entanglement_bits' : entanglement entropy (bits)
        'M2'       : stabilizer Rényi entropy M₂ (bits)
        'mana'     : Mana (bits)
        'wigner_negativity' : total Wigner negativity
        'T_gate_lower_bound' : T-gate count lower bound
        'C_KK_bits' : KK channel capacity log₂(k_cs) from Pillar 31
        'is_stabilizer' : bool (True only when M₂ ≈ 0)

    Raises
    ------
    ValueError if n1 < 1 or n2 ≤ n1.
    """
    _validate_pair(n1, n2)
    k_cs = resonant_kcs(n1, n2)
    c_s  = braided_sound_speed(n1, n2, k_cs)
    p1 = (1.0 + c_s) / 2.0
    p2 = (1.0 - c_s) / 2.0

    psi = braided_winding_state(n1, n2)
    psi_cx = psi.astype(complex)   # promote to complex for Pauli ops

    S_ent_nats = braided_winding_entropy(n1, n2)
    S_ent_bits = S_ent_nats / math.log(2.0)

    M2_val  = stabilizer_renyi_entropy_m2(psi_cx)
    mana_val = mana(psi_cx)
    wig_neg  = wigner_negativity(psi_cx)
    T_lb     = t_gate_lower_bound(M2_val)
    C_KK     = kk_channel_capacity(n1, n2)

    return {
        "n1": n1,
        "n2": n2,
        "k_cs": k_cs,
        "c_s": c_s,
        "p1": p1,
        "p2": p2,
        "S_entanglement": S_ent_nats,
        "S_entanglement_bits": S_ent_bits,
        "M2": M2_val,
        "mana": mana_val,
        "wigner_negativity": wig_neg,
        "T_gate_lower_bound": T_lb,
        "C_KK_bits": C_KK,
        "is_stabilizer": M2_val < 1e-10,
    }


# ---------------------------------------------------------------------------
# Robin–Savage nuclear bridge
# ---------------------------------------------------------------------------

def magic_power_nuclear_bridge(
    n1: int,
    n2: int,
    r_ratio: float = R_RATIO_CANONICAL,
) -> Dict:
    """Robin–Savage bridge: magic overhead for simulating φ-modified nuclear reactions.

    Robin & Savage (arXiv:2604.26376) introduce the concept of *magic power*
    of the S-matrix:  how much non-stabilizer resource does the nuclear
    S-matrix inject into an initially stabilizer state of colliding nucleons?

    In the Unitary Manifold the nuclear S-factor is modified by the 5D
    radion field φ (Pillar 15, `cold_fusion.py`):

        G_5D = G_bare × exp(−Φ_φ)

    The braided winding state encodes the geometric modification.  The
    magic power of the UM-modified S-matrix acting on an input state |ψ_in⟩
    is bounded from below by the magic content of the braided winding state
    itself (by the monotonicity of M₂ under free operations):

        ΔM₂_min ≥ M₂(ψ_braid) × r_ratio

    where r_ratio = r_braided/r_bare ≈ 1 accounts for the one-loop
    braiding correction (Pillar 97-C).

    This is the dimensional bridge: M₂(ψ_braid) × r_ratio is the minimum
    magic injected into a nuclear wavefunction by the 5D geometric
    modification, setting the minimum T-gate overhead for simulating it.

    Parameters
    ----------
    n1 : int       — primary winding number
    n2 : int       — secondary winding number
    r_ratio: float — r_braided/r_bare (default: 1 − δr ≈ 0.9998 at one-loop)

    Returns
    -------
    bridge : dict with keys
        'M2_braid'             : M₂ of the braided winding state (bits)
        'r_ratio'              : r_braided/r_bare
        'delta_M2_min'         : minimum magic injected by the S-matrix modification
        'T_gate_overhead_min'  : T-gate overhead from the UM geometric modification
        'C_KK_bits'            : classical information register (log₂(k_cs) bits)
        'robin_savage_context' : str description linking to arXiv:2604.26376
    """
    _validate_pair(n1, n2)
    if not (0.0 < r_ratio <= 1.0):
        raise ValueError(f"r_ratio={r_ratio!r} must be in (0, 1].")
    summary = kk_magic_summary(n1, n2)
    M2_braid = summary["M2"]
    delta_M2_min = M2_braid * r_ratio
    T_overhead = t_gate_lower_bound(delta_M2_min)
    return {
        "M2_braid": M2_braid,
        "r_ratio": r_ratio,
        "delta_M2_min": delta_M2_min,
        "T_gate_overhead_min": T_overhead,
        "C_KK_bits": summary["C_KK_bits"],
        "robin_savage_context": (
            "Robin & Savage arXiv:2604.26376: magic power quantifies the "
            "T-gate cost of simulating nuclear S-matrix elements beyond "
            "stabilizer circuits.  For the UM the braided winding state "
            "|ψ_braid⟩ = √(49/74)|00⟩ + √(25/74)|11⟩ is the geometric "
            "proxy for the nuclear quantum state modification; its M₂ sets "
            "the minimum non-classical computational overhead."
        ),
    }


# ---------------------------------------------------------------------------
# Nuclear simulation cost
# ---------------------------------------------------------------------------

def nuclear_simulation_cost(n1: int, n2: int) -> Dict:
    """Combined classical + quantum cost for simulating UM-modified nuclear physics.

    The total simulation resource requirement has two components:

    1. **Classical bits**: C_KK = log₂(k_cs) bits from Pillar 31 — the
       information bandwidth of the compact KK dimension needed as a
       classical side channel.

    2. **T-gates**: T_count ≥ 2^(M₂/2) from the resource theory of magic —
       the minimum non-Clifford gate overhead to prepare the braided winding
       state.

    Together these quantify the full hybrid classical/quantum simulation
    cost for any nuclear reaction rate modified by the UM geometry.

    Parameters
    ----------
    n1 : int — primary winding number
    n2 : int — secondary winding number

    Returns
    -------
    cost : dict with keys
        'C_KK_bits'      : classical information register (bits)
        'M2'             : stabilizer Rényi entropy (bits)
        'T_gate_lb'      : T-gate lower bound
        'hybrid_cost'    : C_KK + T_gate_lb (total classical+quantum overhead)
        'efficiency_ratio': C_KK / (C_KK + T_gate_lb) (fraction from classical channel)
        'n_qubits'       : 2 (always — the braided winding is a 2-qubit state)
    """
    _validate_pair(n1, n2)
    summary = kk_magic_summary(n1, n2)
    C_KK = summary["C_KK_bits"]
    M2   = summary["M2"]
    T_lb = summary["T_gate_lower_bound"]
    hybrid = C_KK + T_lb
    eff = C_KK / hybrid if hybrid > 0.0 else 1.0
    return {
        "C_KK_bits": C_KK,
        "M2": M2,
        "T_gate_lb": T_lb,
        "hybrid_cost": hybrid,
        "efficiency_ratio": eff,
        "n_qubits": 2,
    }


# ---------------------------------------------------------------------------
# Stabilizer state check
# ---------------------------------------------------------------------------

def is_stabilizer_state(state: np.ndarray, tol: float = 1e-10) -> bool:
    """Return True if |ψ⟩ is (approximately) a stabilizer state.

    A state is a stabilizer state iff its stabilizer Rényi entropy M₂ = 0,
    equivalently iff the characteristic function satisfies
    Σ_P Ξ(P) = 2^n (the maximum value, achieved only by stabilizer states).

    Parameters
    ----------
    state : array_like, shape (4,) — 2-qubit normalised state
    tol   : float — tolerance for M₂ ≈ 0 (default 1e-10)

    Returns
    -------
    bool
    """
    M2 = stabilizer_renyi_entropy_m2(np.asarray(state, dtype=complex))
    return M2 < tol


# ---------------------------------------------------------------------------
# Convenience: canonical summary
# ---------------------------------------------------------------------------

def canonical_summary() -> Dict:
    """Return the full magic summary for the canonical (5, 7) braid pair.

    This is the central result of Pillar 101: the complete quantum information
    and circuit-complexity profile of the braided winding state selected by
    the Unitary Manifold's (5,7) resonance.

    Returns
    -------
    dict — same structure as kk_magic_summary(5, 7), plus human-readable
    'notes' key explaining the Robin–Savage connection.
    """
    result = kk_magic_summary(N1_CANONICAL, N2_CANONICAL)
    result["notes"] = (
        "Pillar 101 canonical result: "
        f"M₂ = {result['M2']:.6f} bits, "
        f"Mana = {result['mana']:.6f} bits, "
        f"Wigner negativity = {result['wigner_negativity']:.6f}, "
        f"T-gate lower bound ≥ {result['T_gate_lower_bound']:.4f}, "
        f"C_KK = {result['C_KK_bits']:.4f} bits. "
        "The braided winding state is NOT a stabilizer state: it carries "
        "non-zero magic content that sets the minimum T-gate overhead for "
        "simulating the UM-modified nuclear S-factor on a quantum computer "
        "(Robin & Savage arXiv:2604.26376)."
    )
    return result


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_2qubit_state(psi: np.ndarray) -> None:
    """Raise ValueError for a state that is not a normalised 2-qubit vector."""
    if psi.shape != (4,):
        raise ValueError(f"State must have shape (4,), got {psi.shape}.")
    norm = float(np.abs(np.linalg.norm(psi)))
    if abs(norm - 1.0) > 1e-8:
        raise ValueError(
            f"State is not normalised: ‖ψ‖ = {norm:.6f} (expected 1.0 ± 1e-8)."
        )


def _validate_pair(n1: int, n2: int) -> None:
    """Raise ValueError for unphysical (n1, n2) pairs."""
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be a positive integer.")
    if n2 <= n1:
        raise ValueError(f"n2={n2!r} must be strictly greater than n1={n1!r}.")
