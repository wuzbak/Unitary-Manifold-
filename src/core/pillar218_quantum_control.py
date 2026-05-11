# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar218_quantum_control.py
======================================
Pillar 218 — Quantum Computing & Control Systems.

Adjacent applied research track (non-hardgate): applies Kaluza-Klein geometry
insights from the Unitary Manifold to fault-tolerant quantum computation and
quantum control.  Physical claims are speculative extrapolations; they are
clearly labelled as such.

Key insight: the (5,7)-braid structure of the manifold (K_CS = 74 = 5²+7²)
maps naturally to topological quantum error correction.  The winding number
n_w = 5 and braid group B_5 suggest a 5-strand topological code whose
threshold is close to the φ₀ radion attractor (φ₀ ≈ 0.739).
"""
from __future__ import annotations

import math

__provenance__ = {
    "pillar": 218,
    "title": "Quantum Computing & Control Systems",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — speculative extrapolation",
}

__all__ = [
    "N_W",
    "K_CS",
    "BRAIDED_SOUND_SPEED",
    "PHI0",
    "SURFACE_CODE_THRESHOLD",
    "K_B_SI",
    "HBAR_SI",
    "decoherence_rate_from_kk",
    "braid_error_threshold",
    "kk_gate_fidelity",
    "control_hamiltonian_from_kk",
    "topological_code_distance",
    "quantum_capacity_bound",
    "pillar218_summary",
]

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------
N_W: int = 5                         # winding number; KK compactification
K_CS: int = 74                       # = 5² + 7²; birefringence selection
BRAIDED_SOUND_SPEED: float = 12 / 37 # c_s from (5,7) braid resonance
PHI0: float = 0.739085133            # radion fixed-point attractor (Dottie number)
SURFACE_CODE_THRESHOLD: float = 0.01 # ~1 % physical error threshold (Fowler 2012)
K_B_SI: float = 1.380649e-23         # Boltzmann constant [J K⁻¹]
HBAR_SI: float = 1.054571817e-34     # reduced Planck constant [J s]

# Derived constants
_KK_STRAND_COUNT: int = N_W          # B_5 braid group rank
_CODE_DISTANCE_DEFAULT: int = math.floor(K_CS / N_W**2)  # floor(74/25) = 2


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def decoherence_rate_from_kk(T_kelvin: float, R_kk_planck: float) -> dict:
    """KK-inspired decoherence rate with UV suppression from compact dimension.

    The KK compactification radius R introduces a UV cutoff at the first KK
    mass m_KK ~ 1/R (in natural units).  High-frequency bath modes above
    m_KK are exponentially suppressed by the Boltzmann factor.  This yields
    a *speculative* suppression of the bare Ohmic decoherence rate.

    The bare rate follows the standard Caldeira-Leggett / spin-boson result:
        Γ_bare = α k_B T / ħ
    where α = 1/(K_CS) is a dimensionless coupling set by the manifold
    geometry.  The KK suppression factor is:
        S = exp(- ħ / (m_KK k_B T R_kk_planck))
    Note: R_kk_planck is R in Planck length units.  Since ħ = l_Pl = 1 in
    natural units the suppression is exp(-1 / (k_B_nat T_nat R_kk_planck))
    where the natural temperature is T_nat = k_B T_kelvin / E_Pl with
    E_Pl ~ 1.956e9 J.

    Parameters
    ----------
    T_kelvin : float
        Physical temperature [K].  Must be > 0.
    R_kk_planck : float
        KK radius in Planck length units.  Must be > 0.

    Returns
    -------
    dict with keys:
        gamma_bare_hz        – bare rate [Hz] (order-of-magnitude estimate)
        suppression_factor   – dimensionless S in (0, 1]
        gamma_suppressed_hz  – KK-suppressed rate [Hz]
        coupling_alpha       – geometric coupling α = 1/K_CS
        notes                – epistemic caveat string
    """
    if T_kelvin <= 0:
        raise ValueError("T_kelvin must be positive.")
    if R_kk_planck <= 0:
        raise ValueError("R_kk_planck must be positive.")

    alpha = 1.0 / K_CS
    gamma_bare = alpha * K_B_SI * T_kelvin / HBAR_SI

    # Natural units: Planck energy E_Pl = sqrt(ħ c^5 / G) ≈ 1.9561e9 J
    E_PL_J = 1.9561e9
    T_nat = K_B_SI * T_kelvin / E_PL_J  # dimensionless natural temperature

    # KK mass in natural units: m_KK = 1 / R_kk_planck
    m_kk_nat = 1.0 / R_kk_planck

    # Boltzmann suppression of modes above m_KK
    exponent = -m_kk_nat / max(T_nat, 1e-300)
    suppression = math.exp(max(exponent, -700.0))  # avoid underflow

    gamma_suppressed = gamma_bare * suppression

    return {
        "gamma_bare_hz": gamma_bare,
        "suppression_factor": suppression,
        "gamma_suppressed_hz": gamma_suppressed,
        "coupling_alpha": alpha,
        "notes": (
            "Speculative KK UV suppression. Bare rate uses Caldeira-Leggett "
            "coupling α=1/K_CS. Suppression is exponential in m_KK/T_nat."
        ),
    }


def braid_error_threshold(n_strands: int = N_W) -> dict:
    """Topological error threshold for an n-strand braid code.

    For the standard surface code the threshold p_th ≈ 1 % (Fowler et al.
    2012, Phys. Rev. A 86, 032324).  The Markov-trace weight for a closed
    n-braid on the Jones polynomial at the specialisation q = e^{iπ/n}
    provides a heuristic threshold estimate.  For n = 5 this gives:

        p_th(n) ≈ 1 - cos(π / n)

    yielding p_th(5) ≈ 1 - cos(π/5) = 1 - (1 + √5)/4 ≈ 0.1910.

    **Caution**: this is a heuristic motivated by the Jones polynomial
    Jones-Wenzl projector structure, NOT a proven fault-tolerance threshold.
    For n_w = 5 the value ≈ 19 % is notably larger than the surface-code
    1 %, suggesting (speculatively) that a B_5-based code could be more
    robust.  The exact threshold of any concrete code must be established
    by rigorous analysis.

    The φ₀ ≈ 0.739 attractor appears as the radion fixed-point; it is NOT
    the error threshold itself but marks the natural operating point of the
    KK field that *selects* the n_w = 5 braid.

    Parameters
    ----------
    n_strands : int
        Number of braid strands (default N_W = 5).  Must be >= 2.

    Returns
    -------
    dict with keys:
        n_strands           – input
        threshold_heuristic – p_th(n) = 1 - cos(π/n)
        surface_code_threshold – 0.01 (literature reference)
        ratio_vs_surface    – threshold_heuristic / surface_code_threshold
        phi0_attractor      – φ₀ ≈ 0.739 (radion fixed-point, context only)
        notes               – epistemic caveat string
    """
    if n_strands < 2:
        raise ValueError("n_strands must be >= 2 for a non-trivial braid.")

    p_th = 1.0 - math.cos(math.pi / n_strands)

    return {
        "n_strands": n_strands,
        "threshold_heuristic": p_th,
        "surface_code_threshold": SURFACE_CODE_THRESHOLD,
        "ratio_vs_surface": p_th / SURFACE_CODE_THRESHOLD,
        "phi0_attractor": PHI0,
        "notes": (
            "Heuristic Jones-polynomial Markov trace estimate. "
            "NOT a proven fault-tolerance threshold. "
            "φ₀ is the radion attractor that selects n_w=5, not the code threshold."
        ),
    }


def kk_gate_fidelity(epsilon_noise: float, K_cs: int = K_CS) -> dict:
    """Geometric gate fidelity from KK holonomy.

    A geometric (holonomic) gate accumulates a phase from the holonomy of the
    KK gauge connection.  Under small isotropic noise ε the fidelity is:

        F = 1 - (ε / K_CS)²

    This is motivated by the fact that K_CS = 74 acts as an effective
    enhancement factor suppressing the noise-to-signal ratio.  For ε = 0
    the gate is perfect (F = 1).

    Parameters
    ----------
    epsilon_noise : float
        Dimensionless noise amplitude.  0 ≤ ε < K_CS.
    K_cs : int
        KK colour-spin coupling constant (default 74).

    Returns
    -------
    dict with keys:
        fidelity          – F in [0, 1]
        infidelity        – 1 - F = (ε/K_CS)²
        epsilon_noise     – input ε
        K_cs              – input K_CS
        notes             – epistemic caveat string
    """
    if epsilon_noise < 0:
        raise ValueError("epsilon_noise must be >= 0.")
    if K_cs <= 0:
        raise ValueError("K_cs must be positive.")

    infidelity = (epsilon_noise / K_cs) ** 2
    fidelity = 1.0 - infidelity
    fidelity = max(0.0, fidelity)  # clamp at 0

    return {
        "fidelity": fidelity,
        "infidelity": infidelity,
        "epsilon_noise": epsilon_noise,
        "K_cs": K_cs,
        "notes": (
            "Holonomic gate fidelity F = 1 - (ε/K_CS)². "
            "K_CS=74 suppresses noise quadratically. Speculative KK extrapolation."
        ),
    }


def control_hamiltonian_from_kk(omega_drive: float, phi0: float = PHI0) -> dict:
    """KK-inspired control Hamiltonian driving system toward φ₀ attractor.

    The KK radion effective potential near its fixed-point φ₀ is locally
    quadratic:
        V(φ) ≈ ½ m_rad² (φ - φ₀)²

    The corresponding control Hamiltonian in qubit frame is:

        H_ctrl = ħ ω_drive × [cos(φ₀) σ_x + sin(φ₀) σ_z]

    where σ_x, σ_z are Pauli matrices.  This drives the Bloch-sphere
    trajectory toward the attractor direction defined by φ₀.

    Returns the components as dimensionless multiples of ħ ω_drive.

    Parameters
    ----------
    omega_drive : float
        Drive angular frequency [rad s⁻¹ or dimensionless natural units].
    phi0 : float
        Radion fixed-point attractor (default PHI0 ≈ 0.739).

    Returns
    -------
    dict with keys:
        H_x              – coefficient of σ_x  (= cos(φ₀))
        H_z              – coefficient of σ_z  (= sin(φ₀))
        omega_drive      – input ω
        phi0             – attractor value
        H_norm           – |H| / (ħ ω), should equal 1 by construction
        attractor_angle_deg – φ₀ in degrees (orientation on Bloch sphere)
        notes            – epistemic caveat string
    """
    if omega_drive <= 0:
        raise ValueError("omega_drive must be positive.")

    H_x = math.cos(phi0)
    H_z = math.sin(phi0)
    H_norm = math.sqrt(H_x**2 + H_z**2)  # = 1 by Pythagoras

    return {
        "H_x": H_x,
        "H_z": H_z,
        "omega_drive": omega_drive,
        "phi0": phi0,
        "H_norm": H_norm,
        "attractor_angle_deg": math.degrees(phi0),
        "notes": (
            "H_ctrl = ħω[cos(φ₀) σ_x + sin(φ₀) σ_z]. "
            "Drives Bloch-sphere trajectory toward KK radion attractor direction. "
            "Speculative control-theory application of KK geometry."
        ),
    }


def topological_code_distance(n_w: int = N_W, K_cs: int = K_CS) -> dict:
    """Code distance for a KK-motivated topological code.

    Heuristic: code distance d = floor(K_CS / n_w²).

    For default parameters:
        d = floor(74 / 25) = 2

    A distance-2 code detects (but does not correct) any single error.
    Distance-3 is the minimum for single-error correction.

    This formula is *not* derived from a concrete stabiliser construction;
    it is motivated by the fact that K_CS = n_w² + (n_w+2)² = 5²+7² sets
    the two characteristic braid lengths, and their ratio K_CS/n_w² is the
    simplest dimensionless distance measure.

    Parameters
    ----------
    n_w : int
        Winding number / braid strand count (default 5).
    K_cs : int
        KK coupling constant (default 74).

    Returns
    -------
    dict with keys:
        code_distance     – d = floor(K_CS / n_w²)
        n_w               – input
        K_cs              – input
        corrects_errors   – number of errors correctable = floor((d-1)/2)
        detects_errors    – number of errors detectable = d - 1
        notes             – epistemic caveat string
    """
    if n_w < 1:
        raise ValueError("n_w must be >= 1.")
    if K_cs < 1:
        raise ValueError("K_cs must be >= 1.")

    d = math.floor(K_cs / n_w**2)
    corrects = math.floor((d - 1) / 2)
    detects = d - 1

    return {
        "code_distance": d,
        "n_w": n_w,
        "K_cs": K_cs,
        "corrects_errors": corrects,
        "detects_errors": detects,
        "notes": (
            "d = floor(K_CS/n_w²). Heuristic: NOT derived from a concrete "
            "stabiliser code. d=2 detects single errors but cannot correct them. "
            "A real KK-code construction would need explicit stabiliser analysis."
        ),
    }


def quantum_capacity_bound(
    n_qubits: int,
    T_kelvin: float,
    R_kk_planck: float = 1e-32,
) -> dict:
    """Upper bound on quantum channel capacity with KK decoherence suppression.

    Uses the heuristic bound:
        Q ≤ n_qubits × (1 - p_err)

    where the per-qubit error probability p_err is estimated from the
    KK-suppressed decoherence rate via:
        p_err = 1 - exp(-γ_suppressed × t_gate)

    with t_gate = 1 / (K_CS × ω_natural) and ω_natural = k_B T / ħ.

    This gives a rough estimate of how much quantum information survives a
    single gate cycle in a KK-geometry environment.

    Parameters
    ----------
    n_qubits : int
        Number of logical qubits.
    T_kelvin : float
        Operating temperature [K].
    R_kk_planck : float
        KK radius in Planck units (default 1e-32, typical string-scale value).

    Returns
    -------
    dict with keys:
        n_qubits            – input
        T_kelvin            – input
        p_error_per_qubit   – estimated per-qubit error probability
        capacity_upper_bound – Q ≤ n_qubits × (1 - p_err)
        gamma_suppressed_hz – KK-suppressed decoherence rate [Hz]
        t_gate_s            – estimated gate time [s]
        notes               – epistemic caveat string
    """
    if n_qubits < 1:
        raise ValueError("n_qubits must be >= 1.")
    if T_kelvin <= 0:
        raise ValueError("T_kelvin must be positive.")
    if R_kk_planck <= 0:
        raise ValueError("R_kk_planck must be positive.")

    dec = decoherence_rate_from_kk(T_kelvin, R_kk_planck)
    gamma = dec["gamma_suppressed_hz"]

    omega_nat = K_B_SI * T_kelvin / HBAR_SI
    t_gate = 1.0 / (K_CS * max(omega_nat, 1e-300))

    p_err = 1.0 - math.exp(-gamma * t_gate)
    p_err = min(max(p_err, 0.0), 1.0)

    capacity = n_qubits * (1.0 - p_err)

    return {
        "n_qubits": n_qubits,
        "T_kelvin": T_kelvin,
        "p_error_per_qubit": p_err,
        "capacity_upper_bound": capacity,
        "gamma_suppressed_hz": gamma,
        "t_gate_s": t_gate,
        "notes": (
            "Heuristic bound Q ≤ n(1-p_err). p_err from KK-suppressed Caldeira-Leggett "
            "rate and gate time t = 1/(K_CS ω_nat). Speculative; not a rigorous "
            "quantum Shannon-theoretic capacity."
        ),
    }


def pillar218_summary() -> dict:
    """Return a summary dict of Pillar 218 key results.

    Returns
    -------
    dict with keys:
        pillar, title, status, n_w, K_cs, phi0,
        code_distance_default, braid_threshold_n5,
        surface_code_threshold, ratio_vs_surface,
        gate_fidelity_at_eps1, notes
    """
    bt = braid_error_threshold(N_W)
    cd = topological_code_distance(N_W, K_CS)
    gf = kk_gate_fidelity(1.0, K_CS)

    return {
        "pillar": 218,
        "title": "Quantum Computing & Control Systems",
        "status": "ADJACENT RESEARCH TRACK — speculative KK extrapolation",
        "n_w": N_W,
        "K_cs": K_CS,
        "phi0": PHI0,
        "code_distance_default": cd["code_distance"],
        "braid_threshold_n5": bt["threshold_heuristic"],
        "surface_code_threshold": SURFACE_CODE_THRESHOLD,
        "ratio_vs_surface": bt["ratio_vs_surface"],
        "gate_fidelity_at_eps1": gf["fidelity"],
        "braided_sound_speed": BRAIDED_SOUND_SPEED,
        "notes": (
            "All results are heuristic extrapolations from KK geometry. "
            "No concrete stabiliser code has been constructed. "
            "Threshold and capacity bounds require independent quantum-information verification."
        ),
    }
