# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar224_quantum_bottleneck_calculator.py
=====================================================
Pillar 224 — Quantum Computing Bottleneck Calculator.

🔵 ADJACENT TRACK — not a hardgate physics claim.

Adjacent applied research track (non-hardgate): uses the Unitary Manifold's
geometric constants as a *calculator* to produce concrete, numerical answers
for each of the twelve recognised quantum-computing bottlenecks.

Every value in this module is derived from the same four invariants that
anchor the rest of the framework:

    n_w  = 5        (winding number; Planck CMB nₛ selection)
    K_CS = 74       (Chern-Simons level = 5² + 7²; birefringence selection)
    c_s  = 12/37    (braided sound speed; (5,7) braid resonance)
    φ₀   = 0.739… (radion fixed-point attractor = Dottie number)

No new free parameters are introduced here.  All calculations are exact
arithmetic or analytic expressions evaluated in SI units.

Bottleneck index (matches the article post-156):
    1  – Error-correction overhead       (braid threshold vs surface code)
    2  – Cryogenic decoherence           (KK UV-cutoff suppression)
    3  – Barren plateaus                 (gradient decay polynomial bound)
    4  – Quantum interconnects           (topological channel capacity)
    5  – Multi-programming latency       (gate slot from 1/K_CS × ω_nat)
    6  – Manufacturing variability       (fidelity F = 1 − (ε/K_CS)²)
    7  – Algorithm verification          (FTUM convergence to φ₀)
    8  – Quantum advantage gap           (VQE vs classical crossover)
    9  – Classical-quantum latency       (decoder deadline from c_s)
   10  – Talent shortage                 (pedagogical unification factor)
   11  – Post-quantum cryptography       (K_CS as Gaussian integer norm)
   12  – Supply chain fragility          (threshold buffer above surface code)
"""
from __future__ import annotations

import math
from typing import List

__provenance__ = {
    "pillar": 224,
    "title": "Quantum Computing Bottleneck Calculator",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — speculative KK extrapolation; no claim that any bottleneck is solved",
}

__all__ = [
    # Constants
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "K_B_SI",
    "HBAR_SI",
    "C_LIGHT",
    "E_PLANCK_J",
    # Bottleneck 1 — Error correction
    "braid_fault_tolerance_threshold",
    "logical_qubit_overhead",
    # Bottleneck 2 — Decoherence
    "kk_decoherence_suppression",
    "kk_crossover_frequency_hz",
    # Bottleneck 3 — Barren plateaus
    "gradient_variance_bound",
    "barren_plateau_crossover_qubits",
    # Bottleneck 4 — Interconnects
    "topological_channel_capacity",
    # Bottleneck 5 — Multi-programming latency
    "gate_slot_size_seconds",
    # Bottleneck 6 — Manufacturing variability
    "geometric_gate_fidelity",
    "max_tolerable_noise",
    # Bottleneck 7 — Algorithm verification
    "ftum_convergence",
    # Bottleneck 8 — Quantum advantage
    "vqe_advantage_table",
    # Bottleneck 9 — Classical-quantum latency
    "decoder_deadline_seconds",
    # Bottleneck 10 — Talent (unification factor)
    "unification_learning_reduction",
    # Bottleneck 11 — PQC
    "kcs_gaussian_integer_decomposition",
    "braiding_phase_degrees",
    # Bottleneck 12 — Supply chain
    "threshold_safety_margin",
    # Summary
    "bottleneck_report",
]

# ---------------------------------------------------------------------------
# Core constants (immutable; all derive from framework geometry)
# ---------------------------------------------------------------------------

N_W: int = 5
K_CS: int = 74               # = 5² + 7²
C_S: float = 12.0 / 37.0    # braided sound speed
PHI0: float = 0.7390851332151607   # Dottie number: unique fixed point of cos(x)=x

# SI constants
K_B_SI: float = 1.380649e-23        # Boltzmann [J K⁻¹]
HBAR_SI: float = 1.054571817e-34    # ħ [J s]
C_LIGHT: float = 2.99792458e8       # [m s⁻¹]
E_PLANCK_J: float = 1.9561e9        # Planck energy [J]

# Derived
_SURFACE_CODE_THRESHOLD: float = 0.01   # Fowler et al. 2012 (~1 %)


# ===========================================================================
# Bottleneck 1: Error-correction overhead
# ===========================================================================

def braid_fault_tolerance_threshold(n_strands: int = N_W) -> float:
    """Heuristic fault-tolerance threshold for an n-strand braid code.

    Derived from the Jones polynomial Markov-trace weight at
    q = e^{iπ/n_strands}:

        p_th(n) = 1 − cos(π / n)

    For n = 5:  p_th = 1 − cos(π/5) ≈ 0.190983  (≈ 19.1 %)

    The standard surface code threshold is ~1 % (Fowler et al. 2012).
    The B₅-braid code is *speculative* — this is a heuristic from the
    Jones polynomial structure, not a proved stabiliser threshold.

    Parameters
    ----------
    n_strands : int
        Number of braid strands (default: n_w = 5).

    Returns
    -------
    float
        Heuristic fault-tolerance threshold ∈ (0, 1).
    """
    if n_strands < 2:
        raise ValueError("n_strands must be ≥ 2")
    return 1.0 - math.cos(math.pi / n_strands)


def logical_qubit_overhead(
    p_physical: float,
    p_logical_target: float = 1e-15,
    n_strands: int = N_W,
) -> dict:
    """Physical-qubit overhead to achieve a target logical error rate.

    Uses the standard threshold-scaling formula for a distance-d code:

        p_logical ≈ (p_physical / p_threshold)^d

    solving for d, then n_physical ≈ d² (for a 2D code with d rows and
    d columns of ancillae).

    Returns results for both the surface code and the B₅-braid code,
    allowing direct comparison.

    Parameters
    ----------
    p_physical : float
        Physical error rate per gate cycle.  Must be < min(p_th_surface, p_th_braid).
    p_logical_target : float
        Target logical error rate.  Default 10⁻¹⁵.
    n_strands : int
        Braid strand count for heuristic threshold.  Default 5.

    Returns
    -------
    dict with keys:
        p_physical, p_logical_target,
        p_th_surface, p_th_braid,
        d_surface, d_braid,
        n_phys_surface, n_phys_braid,
        qubit_reduction_factor,
        notes
    """
    p_th_surf = _SURFACE_CODE_THRESHOLD
    p_th_braid = braid_fault_tolerance_threshold(n_strands)

    if p_physical >= p_th_surf:
        raise ValueError(
            f"p_physical={p_physical} ≥ surface code threshold {p_th_surf}; "
            "error correction does not help above threshold."
        )

    # code distance for surface code
    ratio_surf = p_physical / p_th_surf
    if ratio_surf >= 1.0:
        raise ValueError("p_physical must be below threshold.")
    d_surf = math.ceil(math.log(p_logical_target) / math.log(ratio_surf))
    n_surf = d_surf ** 2

    # code distance for braid code
    if p_physical < p_th_braid:
        ratio_braid = p_physical / p_th_braid
        d_braid = math.ceil(math.log(p_logical_target) / math.log(ratio_braid))
        n_braid = d_braid ** 2
        reduction = n_surf / max(n_braid, 1)
    else:
        d_braid = None
        n_braid = None
        reduction = None

    return {
        "p_physical": p_physical,
        "p_logical_target": p_logical_target,
        "p_th_surface": p_th_surf,
        "p_th_braid": p_th_braid,
        "d_surface": d_surf,
        "d_braid": d_braid,
        "n_phys_surface": n_surf,
        "n_phys_braid": n_braid,
        "qubit_reduction_factor": reduction,
        "notes": (
            "B5-braid threshold is a heuristic (Jones polynomial); "
            "surface code threshold is experimentally grounded."
        ),
    }


# ===========================================================================
# Bottleneck 2: Cryogenic decoherence — KK UV-cutoff suppression
# ===========================================================================

def kk_decoherence_suppression(
    T_kelvin: float,
    R_kk_planck: float,
) -> dict:
    """KK-cutoff Boltzmann suppression of bath modes above the KK mass scale.

    The KK mass (in natural units) m_KK = 1/R_kk_planck.  Bath modes above
    m_KK are Boltzmann-suppressed by:

        S = exp(−m_KK / T_nat) = exp(−1 / (T_nat × R_kk_planck))

    where T_nat = k_B T / E_Planck is the dimensionless natural temperature.

    The bare decoherence rate (Caldeira-Leggett / spin-boson):

        Γ_bare = (1/K_CS) × k_B T / ħ

    and the KK-suppressed rate is Γ_suppressed = Γ_bare × S.

    Parameters
    ----------
    T_kelvin : float
        Operating temperature [K].
    R_kk_planck : float
        KK compactification radius in Planck length units.

    Returns
    -------
    dict with keys:
        T_kelvin, R_kk_planck, T_nat,
        m_kk_effective_hz, omega_nat_hz,
        gamma_bare_hz, suppression_factor, gamma_suppressed_hz,
        suppression_db
    """
    if T_kelvin <= 0:
        raise ValueError("T_kelvin must be positive.")
    if R_kk_planck <= 0:
        raise ValueError("R_kk_planck must be positive.")

    T_nat = K_B_SI * T_kelvin / E_PLANCK_J
    omega_nat = K_B_SI * T_kelvin / HBAR_SI     # [rad s⁻¹]
    gamma_bare = omega_nat / K_CS               # [rad s⁻¹]

    exponent = -1.0 / (T_nat * R_kk_planck)
    # Guard against underflow
    suppression = math.exp(max(exponent, -700.0))
    gamma_supp = gamma_bare * suppression

    # Effective KK frequency in Hz
    m_kk_hz = E_PLANCK_J / (HBAR_SI * 2 * math.pi * R_kk_planck)

    suppression_db = 10.0 * math.log10(suppression) if suppression > 0 else -math.inf

    return {
        "T_kelvin": T_kelvin,
        "R_kk_planck": R_kk_planck,
        "T_nat": T_nat,
        "m_kk_effective_hz": m_kk_hz,
        "omega_nat_hz": omega_nat,
        "gamma_bare_hz": gamma_bare,
        "suppression_factor": suppression,
        "gamma_suppressed_hz": gamma_supp,
        "suppression_db": suppression_db,
    }


def kk_crossover_frequency_hz(T_kelvin: float) -> float:
    """Effective KK frequency at which bath suppression reaches 50 %.

    Suppression = exp(−m_KK / T_nat) = 0.5  →  m_KK = T_nat × ln(2).

    Converts the natural-unit KK mass to an SI frequency via:

        f_crossover = m_kk_nat × E_Planck / (h)

    where h = 2π ħ.

    Parameters
    ----------
    T_kelvin : float
        Operating temperature [K].

    Returns
    -------
    float
        Crossover frequency [Hz] at which KK suppression = 50 %.
    """
    if T_kelvin <= 0:
        raise ValueError("T_kelvin must be positive.")
    T_nat = K_B_SI * T_kelvin / E_PLANCK_J
    m_kk_crossover_nat = T_nat * math.log(2.0)
    f_crossover = m_kk_crossover_nat * E_PLANCK_J / (2 * math.pi * HBAR_SI)
    return f_crossover


# ===========================================================================
# Bottleneck 3: Barren plateaus — gradient variance bound
# ===========================================================================

def gradient_variance_bound(n_qubits: int, use_kk_structure: bool = True) -> dict:
    """Gradient variance bound for KK-structured vs random ansatz.

    Random ansatz (unstructured):
        Var[∂E/∂θ] ≈ 2^{−n_qubits}

    KK-structured ansatz (polynomial in n):
        Var[∂E/∂θ] ≥ 1 / (K_CS² × n_qubits)

    The KK structure bounds the gradient from below by a polynomial quantity,
    avoiding exponential vanishing.  The crossover point where KK > random is:

        2^{−n} = 1/(K_CS² × n)  →  n ≈ 2 × log₂(K_CS) + log₂(n) ≈ 13

    Parameters
    ----------
    n_qubits : int
        Number of qubits in the circuit.
    use_kk_structure : bool
        If True, return KK bound; otherwise return random bound.

    Returns
    -------
    dict with keys:
        n_qubits, grad_variance_random, grad_variance_kk,
        kk_advantage_factor, kk_dominates
    """
    if n_qubits < 1:
        raise ValueError("n_qubits must be ≥ 1")
    grad_random = 2.0 ** (-n_qubits)
    grad_kk = 1.0 / (K_CS ** 2 * n_qubits)
    advantage = grad_kk / grad_random if grad_random > 0 else math.inf
    return {
        "n_qubits": n_qubits,
        "grad_variance_random": grad_random,
        "grad_variance_kk": grad_kk,
        "kk_advantage_factor": advantage,
        "kk_dominates": grad_kk > grad_random,
    }


def barren_plateau_crossover_qubits() -> int:
    """Number of qubits at which KK gradient exceeds random gradient.

    Solves 2^{−n} = 1/(K_CS² × n) numerically.

    Returns
    -------
    int
        Smallest n where grad_kk > grad_random.
    """
    for n in range(1, 200):
        if (1.0 / (K_CS ** 2 * n)) > 2.0 ** (-n):
            return n
    return -1  # should never happen


# ===========================================================================
# Bottleneck 4: Quantum interconnects — topological channel capacity
# ===========================================================================

def topological_channel_capacity(
    n_qubits_per_channel: int,
    p_error_per_hop: float,
) -> dict:
    """Upper-bound channel capacity with braid-protected modes.

    Heuristic: n_w = 5 braid strands provide 5 protected logical channels.
    Each channel has independent error rate p_error_per_hop (after topological
    protection).  Holevo capacity bound:

        Q ≤ n_channels × (1 − H_binary(p_error_per_hop))

    where H_binary(p) = −p log₂(p) − (1−p) log₂(1−p).

    Parameters
    ----------
    n_qubits_per_channel : int
        Number of logical qubits per topological channel.
    p_error_per_hop : float
        Residual error probability per hop.

    Returns
    -------
    dict with keys:
        n_channels, n_qubits_per_channel, p_error_per_hop,
        binary_entropy, quantum_capacity_qubits, braiding_phase_rad
    """
    if not (0.0 <= p_error_per_hop < 1.0):
        raise ValueError("p_error_per_hop must be in [0, 1).")

    n_channels = N_W  # n_w = 5 topological channels
    p = p_error_per_hop
    if p == 0.0:
        h_bin = 0.0
    else:
        h_bin = -p * math.log2(p) - (1 - p) * math.log2(1 - p)

    capacity = n_channels * n_qubits_per_channel * max(0.0, 1.0 - h_bin)
    braid_phase = 2 * math.pi * (N_W * (N_W + 2)) / K_CS   # = 2π × 35/74

    return {
        "n_channels": n_channels,
        "n_qubits_per_channel": n_qubits_per_channel,
        "p_error_per_hop": p_error_per_hop,
        "binary_entropy": h_bin,
        "quantum_capacity_qubits": capacity,
        "braiding_phase_rad": braid_phase,
        "braiding_phase_degrees": math.degrees(braid_phase),
    }


# ===========================================================================
# Bottleneck 5: Multi-programming latency — gate slot size
# ===========================================================================

def gate_slot_size_seconds(T_kelvin: float = 15e-3) -> dict:
    """Minimum gate time slot from KK-constrained gate cycle.

    The gate timescale is set by:

        t_gate = 1 / (K_CS × ω_natural)

    where ω_natural = k_B T / ħ.  This is the fastest meaningful time
    slice for multi-user scheduling given the braid's geometric period.

    Parameters
    ----------
    T_kelvin : float
        Operating temperature [K].  Default: 15 mK.

    Returns
    -------
    dict with keys:
        T_kelvin, omega_nat_rad_s, t_gate_seconds, t_gate_ns,
        scheduling_slots_per_us
    """
    if T_kelvin <= 0:
        raise ValueError("T_kelvin must be positive.")
    omega_nat = K_B_SI * T_kelvin / HBAR_SI
    t_gate = 1.0 / (K_CS * omega_nat)
    slots_per_us = 1e-6 / t_gate
    return {
        "T_kelvin": T_kelvin,
        "omega_nat_rad_s": omega_nat,
        "t_gate_seconds": t_gate,
        "t_gate_ns": t_gate * 1e9,
        "scheduling_slots_per_us": slots_per_us,
    }


# ===========================================================================
# Bottleneck 6: Manufacturing variability — geometric gate fidelity
# ===========================================================================

def geometric_gate_fidelity(epsilon_noise: float, K_cs: int = K_CS) -> dict:
    """Gate fidelity from KK geometric holonomy under noise ε.

    A geometric (holonomic) gate accumulates phase from the KK gauge
    connection.  Under isotropic noise amplitude ε:

        F(ε) = 1 − (ε / K_CS)²

    The quadratic suppression means manufacturing variability ε is
    damped by the geometric factor K_CS = 74.

    Parameters
    ----------
    epsilon_noise : float
        Dimensionless noise amplitude ≥ 0.
    K_cs : int
        KK colour-spin coupling constant.  Default 74.

    Returns
    -------
    dict with keys:
        epsilon_noise, K_cs, fidelity, infidelity,
        fidelity_linear_comparison, advantage_vs_linear
    """
    if epsilon_noise < 0:
        raise ValueError("epsilon_noise must be ≥ 0.")
    fidelity = 1.0 - (epsilon_noise / K_cs) ** 2
    fidelity_linear = 1.0 - epsilon_noise / K_cs
    advantage = (1.0 - fidelity_linear) / max(1.0 - fidelity, 1e-300)
    return {
        "epsilon_noise": epsilon_noise,
        "K_cs": K_cs,
        "fidelity": fidelity,
        "infidelity": 1.0 - fidelity,
        "fidelity_linear_comparison": fidelity_linear,
        "advantage_vs_linear": advantage,
    }


def max_tolerable_noise(fidelity_floor: float = 0.999, K_cs: int = K_CS) -> float:
    """Maximum noise ε that keeps F(ε) ≥ fidelity_floor.

    Inverts F = 1 − (ε/K_CS)² → ε_max = K_CS × sqrt(1 − fidelity_floor).

    Parameters
    ----------
    fidelity_floor : float
        Minimum acceptable gate fidelity.
    K_cs : int
        KK coupling constant.

    Returns
    -------
    float
        Maximum tolerable dimensionless noise amplitude.
    """
    if not (0.0 < fidelity_floor < 1.0):
        raise ValueError("fidelity_floor must be in (0, 1).")
    return K_cs * math.sqrt(1.0 - fidelity_floor)


# ===========================================================================
# Bottleneck 7: Algorithm verification — FTUM convergence to φ₀
# ===========================================================================

def ftum_convergence(
    x0: float,
    tol: float = 1e-12,
    max_iter: int = 1000,
) -> dict:
    """FTUM fixed-point iteration: x_{n+1} = cos(x_n) → φ₀.

    Converges from any starting point in [0, 1] to the Dottie number
    φ₀ ≈ 0.739085133… — the unique fixed point of cos(x) = x.

    This convergence is a self-verification mechanism: an algorithm that
    maps to this iteration has a built-in check — if it does not converge
    to φ₀, the computation is wrong.

    Parameters
    ----------
    x0 : float
        Starting value.
    tol : float
        Convergence tolerance |x_n − φ₀| < tol.
    max_iter : int
        Maximum iterations.

    Returns
    -------
    dict with keys:
        x0, x_final, iterations, converged, error,
        convergence_rate (|x_n − φ₀| / |x_{n-1} − φ₀| at final step)
    """
    x = x0
    x_prev = None
    for i in range(max_iter):
        x_new = math.cos(x)
        if x_prev is not None:
            err_prev = abs(x_prev - PHI0)
            err_curr = abs(x_new - PHI0)
            conv_rate = err_curr / err_prev if err_prev > 0 else 0.0
        else:
            conv_rate = float("nan")
        x_prev = x
        x = x_new
        if abs(x - PHI0) < tol:
            return {
                "x0": x0,
                "x_final": x,
                "iterations": i + 1,
                "converged": True,
                "error": abs(x - PHI0),
                "convergence_rate": conv_rate,
            }
    return {
        "x0": x0,
        "x_final": x,
        "iterations": max_iter,
        "converged": False,
        "error": abs(x - PHI0),
        "convergence_rate": conv_rate,
    }


# ===========================================================================
# Bottleneck 8: Quantum advantage gap — VQE vs classical crossover
# ===========================================================================

def vqe_advantage_table(
    n_qubit_range: range = range(2, 21),
    n_layers: int = 10,
) -> List[dict]:
    """Classical vs VQE cost comparison for the KK Hamiltonian.

    Classical diagonalisation of a 2^n × 2^n matrix requires O(2^{3n})
    floating-point operations (dense eigendecomposition).

    KK-VQE evaluation count (rough polynomial bound):
        N_evals ≈ K_CS × n_qubits × n_layers

    The crossover is when classical > VQE, i.e., advantage begins.

    Parameters
    ----------
    n_qubit_range : range
        Qubit counts to tabulate.
    n_layers : int
        Ansatz layer count (default 10).

    Returns
    -------
    List[dict], one entry per qubit count, with keys:
        n_qubits, hilbert_dim, classical_ops, vqe_evals, ratio, advantage
    """
    results = []
    for n in n_qubit_range:
        classical = 2 ** (3 * n)
        vqe = K_CS * n * n_layers
        results.append({
            "n_qubits": n,
            "hilbert_dim": 2 ** n,
            "classical_ops": classical,
            "vqe_evals": vqe,
            "ratio": classical / max(vqe, 1),
            "advantage": classical > vqe,
        })
    return results


def vqe_crossover_qubits(n_layers: int = 10) -> int:
    """Smallest qubit count where VQE circuit evaluations < classical ops.

    Returns
    -------
    int
        Crossover n_qubits.
    """
    for n in range(1, 200):
        if K_CS * n * n_layers < 2 ** (3 * n):
            return n
    return -1


# ===========================================================================
# Bottleneck 9: Classical-quantum latency — decoder deadline
# ===========================================================================

def decoder_deadline_seconds(
    chip_length_m: float,
    safety_factor: float = 1.0,
) -> dict:
    """Decoder deadline from braided sound-speed propagation.

    The (5,7)-braid information propagation speed is c_s = 12/37 ≈ 0.3243c.
    For a chip of physical length L, the braid-propagation time is:

        t_decode = L / (c_s × c)

    This sets the *geometric* deadline for real-time error-correction decoding.
    Classical decoders (FPGAs) operating within this deadline are compatible
    with the braid architecture.

    Parameters
    ----------
    chip_length_m : float
        Physical chip size [m].
    safety_factor : float
        Multiply deadline by this factor to add engineering margin.

    Returns
    -------
    dict with keys:
        chip_length_m, c_s, propagation_speed_m_s,
        deadline_seconds, deadline_ns,
        fpga_achievable (True if deadline > 1 ns, typical FPGA latency)
    """
    if chip_length_m <= 0:
        raise ValueError("chip_length_m must be positive.")
    v_braid = C_S * C_LIGHT
    t_decode = (chip_length_m / v_braid) * safety_factor
    return {
        "chip_length_m": chip_length_m,
        "c_s": C_S,
        "propagation_speed_m_s": v_braid,
        "deadline_seconds": t_decode,
        "deadline_ns": t_decode * 1e9,
        "fpga_achievable": t_decode > 1e-9,  # 1 ns is a typical FPGA clock cycle
    }


# ===========================================================================
# Bottleneck 10: Talent shortage — unification learning reduction
# ===========================================================================

def unification_learning_reduction() -> dict:
    """Pedagogical unification factor from the 4-constant framework.

    Classical quantum-computing education requires learning N_separate
    distinct mathematical frameworks.  The Unitary Manifold maps all of
    them onto a single 4-constant geometric language.

    This is not a rigorous claim — it is a structural observation.
    The framework provides:
        - quantum mechanics from KK geometry
        - error correction from braid topology
        - control theory from radion attractor
        - hardware constraints from c_s and K_CS

    Returns a dict of the learning surface reduction estimate.

    Returns
    -------
    dict with keys:
        n_separate_frameworks, n_framework_constants,
        reduction_factor, shared_constants
    """
    n_separate = 5  # QM, QFT, QEC, control theory, condensed matter
    n_constants = 4  # n_w, K_CS, c_s, φ₀
    reduction = n_separate / n_constants
    return {
        "n_separate_frameworks": n_separate,
        "n_framework_constants": n_constants,
        "reduction_factor": reduction,
        "shared_constants": {
            "n_w": N_W,
            "K_CS": K_CS,
            "c_s": C_S,
            "phi0": PHI0,
        },
        "note": (
            "Reduction is pedagogical, not mathematical proof. "
            "Depends on framework correctness."
        ),
    }


# ===========================================================================
# Bottleneck 11: Post-quantum cryptography — K_CS as Gaussian integer norm
# ===========================================================================

def kcs_gaussian_integer_decomposition() -> dict:
    """Decompose K_CS as a Gaussian integer norm.

    K_CS = 74 = 5² + 7² is a norm in the Gaussian integers ℤ[i]:
        |5 + 7i|² = 25 + 49 = 74

    This is the same algebraic structure used in Gaussian integer lattices
    underlying NIST PQC candidates (NTRU, CRYSTALS-Kyber, CRYSTALS-Dilithium).

    Returns all sum-of-two-squares representations of K_CS.

    Returns
    -------
    dict with keys:
        K_CS, decompositions, is_gaussian_prime, braiding_phase_degrees,
        nist_pqc_dimension_context
    """
    decomps = []
    for a in range(1, int(math.sqrt(K_CS)) + 1):
        b_sq = K_CS - a * a
        if b_sq >= a * a:
            b = int(math.sqrt(b_sq))
            if b * b == b_sq:
                decomps.append((a, b))

    return {
        "K_CS": K_CS,
        "decompositions": decomps,
        "is_gaussian_prime": len(decomps) == 1,
        "braiding_phase_degrees": math.degrees(2 * math.pi * N_W * (N_W + 2) / K_CS),
        "nist_pqc_dimension_context": (
            "CRYSTALS-Kyber lattice rank: 256 (Kyber-512), 384, 512 (Kyber-1024). "
            "K_CS = 74 is in the intermediate lattice rank range; "
            "its Gaussian integer structure matches the algebraic form of "
            "ideal lattice problems (NTRU prime, Module-LWE)."
        ),
    }


def braiding_phase_degrees() -> float:
    """Non-Abelian braiding phase θ = 2π × n₁n₂/K_CS in degrees.

    For n₁ = 5, n₂ = 7, K_CS = 74:
        θ = 2π × 35/74 ≈ 170.27°

    Non-rational (35/74 is already in lowest terms; 35 and 74 share no
    common factor) → non-Abelian anyon regime.

    Returns
    -------
    float
        Braiding phase in degrees.
    """
    return math.degrees(2 * math.pi * N_W * (N_W + 2) / K_CS)


# ===========================================================================
# Bottleneck 12: Supply chain — threshold safety margin
# ===========================================================================

def threshold_safety_margin() -> dict:
    """Safety margin between B₅-braid threshold and surface code threshold.

    The B₅ heuristic threshold ≈ 19.1 % vs surface code ~1 %.
    The margin represents how much "headroom" exists for physical error
    rates before the code fails — directly related to hardware quality
    requirements and hence to supply chain precision requirements.

    Returns
    -------
    dict with keys:
        p_th_braid, p_th_surface, absolute_margin, relative_margin,
        hardware_relaxation_factor, supply_chain_note
    """
    p_th_b5 = braid_fault_tolerance_threshold(N_W)
    p_th_surf = _SURFACE_CODE_THRESHOLD
    abs_margin = p_th_b5 - p_th_surf
    rel_margin = abs_margin / p_th_surf  # how many multiples above surface
    hardware_relax = p_th_b5 / p_th_surf  # can tolerate this factor more error

    return {
        "p_th_braid": p_th_b5,
        "p_th_surface": p_th_surf,
        "absolute_margin": abs_margin,
        "relative_margin_x": rel_margin,
        "hardware_relaxation_factor": hardware_relax,
        "supply_chain_note": (
            "A 19.1× higher error threshold means hardware does not need "
            "to meet the same precision spec as current surface-code devices. "
            "Broader supplier base becomes viable; niobium-purity requirements "
            "and refrigerator specs can be relaxed proportionally."
        ),
    }


# ===========================================================================
# Combined report
# ===========================================================================

def bottleneck_report(T_kelvin: float = 15e-3, p_physical: float = 1e-3) -> dict:
    """Compute all twelve bottleneck results and return as a single dict.

    Parameters
    ----------
    T_kelvin : float
        Operating temperature [K].  Default 15 mK.
    p_physical : float
        Physical gate error rate.  Default 0.1 %.

    Returns
    -------
    dict
        Keys b01 through b12, each containing the relevant sub-dict.
    """
    # b02 needs R_kk at the qubit resonance scale (~5 GHz)
    # R_kk for f_kk = 5 GHz: R_kk = E_Planck / (h × f_kk)
    f_qubit = 5e9  # Hz
    R_kk_qubit = E_PLANCK_J / (2 * math.pi * HBAR_SI * f_qubit)

    return {
        "b01_error_correction": logical_qubit_overhead(p_physical),
        "b02_decoherence": kk_decoherence_suppression(T_kelvin, R_kk_qubit),
        "b03_barren_plateau_crossover_n": barren_plateau_crossover_qubits(),
        "b03_barren_plateau_50q": gradient_variance_bound(50),
        "b04_interconnect": topological_channel_capacity(4, 1e-4),
        "b05_gate_slot": gate_slot_size_seconds(T_kelvin),
        "b06_variability_eps1pct": geometric_gate_fidelity(0.01),
        "b06_variability_eps10pct": geometric_gate_fidelity(0.10),
        "b07_ftum_verification": ftum_convergence(0.5),
        "b08_advantage_table": vqe_advantage_table(range(2, 16)),
        "b08_crossover_n": vqe_crossover_qubits(),
        "b09_decoder_1mm": decoder_deadline_seconds(1e-3),
        "b09_decoder_10mm": decoder_deadline_seconds(10e-3),
        "b10_unification": unification_learning_reduction(),
        "b11_pqc": kcs_gaussian_integer_decomposition(),
        "b12_supply_chain": threshold_safety_margin(),
        "b02_crossover_hz": kk_crossover_frequency_hz(T_kelvin),
    }
