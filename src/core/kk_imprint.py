# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_imprint.py
======================
Pillar 32 — KK Geometric Imprint in Matter.

Background: the Quantum Imprint Question
-----------------------------------------
After 5D → 4D compactification, the surviving 4D fields { g_μν, A_μ, φ }
are not arbitrary: they carry a residual "imprint" of the full 5D KK geometry.
Specifically, the projection onto the 7 surviving degrees of freedom (Pillar 30:
5 zero-mode + 2 braid-locked) leaves a characteristic pattern in field space
that is unique to the (n₁, n₂) braid vacuum.

This module makes that imprint explicit and operational.  The core operations
mirror the QIQD (Quantum Imprint Query and Design) arc:

    Store   → imprint_signature    — encode the KK geometric imprint vector
    Compare → imprint_fidelity     — measure overlap between two imprints
    Extract → photonic_readout_coupling — couple to a probing photon
    Search  → optimize_imprint     — find the best-matching candidate config
    Protect → imprint_stability    — assess thermal decoherence

Imprint vector
--------------
The imprint is a 7-component real vector I ∈ ℝ⁷ built from the surviving
moduli DOF:

    I = [w(0) · φ,                   (zero-mode radion weight)
         w(0) · A[0], w(0) · A[1],   (zero-mode KK photon, 2 transverse DOF)
         w(0) · A[2], w(0) · A[3],   (zero-mode KK photon, remaining)
         w(n₁) · c_s · n₁,           (braid-locked mode n₁, softened by c_s)
         w(n₂) · c_s · n₂]           (braid-locked mode n₂, softened by c_s)

where w(n) = mode_survival_weight(n, n₁, n₂, k_cs) from Pillar 30, and c_s is
the braided sound speed from Pillar 1.

The 7 components correspond exactly to the 7 surviving physical DOF established
in moduli_dof_count():
    - zero-mode:   4D graviton (2) + KK photon (2) + radion (1) = 5
    - braid-locked: n₁ mode (1) + n₂ mode (1)                  = 2
    Total: 7

Imprint fidelity
----------------
The fidelity between two imprint configurations A and B is the squared cosine
similarity of their normalised imprint vectors:

    F = |⟨I_A | I_B⟩|² / (|I_A|² |I_B|²) = cos²(θ_AB)

This is identical in structure to the metric_fidelity in Pillar 31
(kk_quantum_info.py), and reduces to it when the full 5×5 metric is projected
onto the surviving 7 DOF.

Photonic readout coupling
-------------------------
The Aerisian effect (Δθ_WP = α ℓ_P² ∫ R H dr) establishes that the KK
geometric curvature leaves a polarisation rotation in passing photons.  For an
imprint held in a material system, the coupling coefficient between the imprint
vector I and a probing photon of wavelength λ is

    κ(I, λ) = α_fine × (ℓ_P / λ) × |I|²

where α_fine ≈ 1/137 is the fine-structure constant (which sets the
photon–geometry coupling strength in the KK framework; see aerisian_rotation_angle
in aerisian.py) and ℓ_P = 1 in Planck units.  The factor |I|² is the total
imprint power (summed squared moduli components) that couples to the photon.

Physical interpretation: a stronger or more highly-weighted imprint (larger |I|)
produces a larger photonic polarisation shift; shorter wavelengths probe the
geometry more sensitively (∝ 1/λ).

Imprint stability (thermal decoherence)
----------------------------------------
The imprint survives thermal noise if the thermal energy k_B T (with k_B = 1 in
Planck units) remains below the threshold set by the Goldberger–Wise mass:

    Stable iff  k_B T < T_H_max = m_phi × Δφ / (2π φ_min)

where m_phi is the GW mass parameter, Δφ = φ_star − φ_min is the GW stabilisation
range, and φ_min is the GW floor on the radion (see bh_remnant.py, Pillar 28).

The stability fraction quantifies how far the system is from the decoherence
threshold:

    S_frac = 1 − k_B T / T_H_max    (clamped to [0, 1])

S_frac = 1 → perfectly stable (T = 0).
S_frac = 0 → at the decoherence threshold (T = T_H_max).
S_frac < 0 → imprint destroyed; we clamp to 0.

Imprint optimisation
---------------------
Given a target KK geometry signature I_target and a list of candidate
(φ, A_μ, n₁, n₂) configurations, optimize_imprint returns the index of the
candidate whose imprint_fidelity with I_target is maximised.  This is the
"D-Wave QPU" analogue: the 5D geometric loss function L from the branch catalog
implicitly constrains which candidates are physically admissible (only lossless
branches with L = 0 can produce a perfect fidelity of 1.0).

Public API
----------
ImprintConfig
    Dataclass: (phi, A_mu, n1, n2) — the minimal description of a KK
    configuration needed to compute its imprint.

imprint_signature(phi, A_mu, n1, n2) -> np.ndarray
    Compute the 7-component KK geometric imprint vector.

imprint_fidelity(config_a, config_b) -> float
    Squared cosine similarity of two imprint vectors.  Range [0, 1].

photonic_readout_coupling(imprint, wavelength) -> float
    Coupling coefficient κ between the imprint and a probing photon (> 0).

optimize_imprint(target_signature, candidates) -> int
    Index of the candidate configuration that maximises imprint fidelity.

imprint_stability(imprint, T, m_phi, phi_min, phi_star) -> dict
    Thermal stability assessment: T_H_max, stability fraction, stable flag.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
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
from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .braided_winding import resonant_kcs, braided_sound_speed
from .moduli_survival import mode_survival_weight
from .bh_remnant import remnant_temperature


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Canonical braid pair (n₁, n₂)
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
#: k_cs = n₁² + n₂² for the canonical (5, 7) pair
K_CS_CANONICAL: int = 74
#: Braided sound speed c_s = 12/37 for (5, 7)
C_S_CANONICAL: float = 12.0 / 37.0
#: Number of surviving propagating DOF in the 4D effective theory
N_SURVIVING_DOF: int = 7

#: Fine-structure constant (photon–geometry coupling; Planck units)
ALPHA_FINE: float = 1.0 / 137.035999084

#: Planck length in Planck units (= 1 by definition)
PLANCK_LENGTH: float = 1.0

_EPS = 1e-300


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class ImprintConfig:
    """Minimal description of a KK field configuration for imprint computation.

    Attributes
    ----------
    phi  : float          — radion scalar φ (> 0, in Planck units)
    A_mu : array-like (4,) — KK gauge field A_μ (4 components)
    n1   : int            — primary braid winding number (≥ 1)
    n2   : int            — secondary braid winding number (> n1)
    """

    phi: float
    A_mu: Sequence[float]
    n1: int = N1_CANONICAL
    n2: int = N2_CANONICAL


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def imprint_signature(
    phi: float,
    A_mu: Sequence[float],
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
) -> np.ndarray:
    """Compute the 7-component KK geometric imprint vector.

    Projects the full KK metric configuration (φ, A_μ) onto the 7 surviving
    physical degrees of freedom established by Pillar 30 (moduli_survival.py).

    The imprint vector I ∈ ℝ⁷ is:

        I[0]   = w(0)  × φ                   (radion zero mode)
        I[1:5] = w(0)  × A_μ                 (KK photon zero modes, 4 DOF)
        I[5]   = w(n₁) × c_s × n₁            (braid-locked mode n₁)
        I[6]   = w(n₂) × c_s × n₂            (braid-locked mode n₂)

    where w(n) = mode_survival_weight(n, n₁, n₂, k_cs) and c_s is the
    braided sound speed.

    Parameters
    ----------
    phi  : float           — radion scalar (> 0)
    A_mu : array-like (4,) — KK gauge field
    n1   : int             — primary winding number (default 5)
    n2   : int             — secondary winding number (default 7)

    Returns
    -------
    I : np.ndarray, shape (7,), float64 — KK geometric imprint vector

    Raises
    ------
    ValueError if phi ≤ 0, A_mu not length 4, or n1/n2 invalid.
    """
    if phi <= 0.0:
        raise ValueError(f"phi={phi!r} must be > 0.")
    A = np.asarray(A_mu, dtype=float).ravel()
    if A.shape != (4,):
        raise ValueError(f"A_mu must have length 4, got shape {A.shape}.")
    _validate_pair(n1, n2)

    k_cs = resonant_kcs(n1, n2)
    c_s  = braided_sound_speed(n1, n2, k_cs)

    w0  = mode_survival_weight(0,  n1, n2, k_cs)   # = 1.0 always
    wn1 = mode_survival_weight(n1, n1, n2, k_cs)   # = 1.0 (braid-locked)
    wn2 = mode_survival_weight(n2, n1, n2, k_cs)   # = 1.0 (braid-locked)

    I = np.empty(7, dtype=float)
    I[0]   = w0  * phi          # radion
    I[1:5] = w0  * A            # KK photon (4 components)
    I[5]   = wn1 * c_s * n1    # braid-locked mode n₁
    I[6]   = wn2 * c_s * n2    # braid-locked mode n₂
    return I


def imprint_fidelity(
    config_a: ImprintConfig,
    config_b: ImprintConfig,
) -> float:
    """Squared cosine similarity between two KK imprint vectors.

    Measures how closely two molecular/atomic configurations share the same
    KK geometric imprint.  Uses the bipartite entanglement structure of
    Pillar 31 (kk_quantum_info.py) projected onto the 7 surviving DOF.

        F = |⟨I_A | I_B⟩|² / (|I_A|² |I_B|²)   ∈ [0, 1]

    F = 1 → identical imprints (same KK geometry).
    F = 0 → orthogonal imprints (no shared geometric content).

    Parameters
    ----------
    config_a, config_b : ImprintConfig — two KK field configurations

    Returns
    -------
    F : float in [0, 1]

    Raises
    ------
    ValueError if either imprint has zero norm (trivial configuration).
    """
    Ia = imprint_signature(config_a.phi, config_a.A_mu, config_a.n1, config_a.n2)
    Ib = imprint_signature(config_b.phi, config_b.A_mu, config_b.n1, config_b.n2)

    norm_a = float(np.linalg.norm(Ia))
    norm_b = float(np.linalg.norm(Ib))

    if norm_a < _EPS:
        raise ValueError("Config A produces a zero-norm imprint vector.")
    if norm_b < _EPS:
        raise ValueError("Config B produces a zero-norm imprint vector.")

    overlap = float(np.dot(Ia, Ib))
    return (overlap ** 2) / (norm_a ** 2 * norm_b ** 2)


def photonic_readout_coupling(
    imprint: np.ndarray,
    wavelength: float,
) -> float:
    """Coupling coefficient between a KK imprint and a probing photon.

    Extends the Aerisian polarisation-rotation effect (Δθ_WP = α ℓ_P² ∫ R H dr)
    to a material imprint context.  For an imprint vector I held in a molecular
    or atomic system, the coupling coefficient to a photon of wavelength λ is:

        κ(I, λ) = α_fine × (ℓ_P / λ) × |I|²

    where α_fine = 1/137 is the fine-structure constant, ℓ_P = 1 (Planck units),
    and |I|² is the total imprint power (summed squared components).

    Physical interpretation:
    - Larger imprint power → stronger photonic coupling.
    - Shorter wavelength → finer geometric resolution (higher κ).
    - α_fine sets the overall photon–geometry interaction strength.

    Parameters
    ----------
    imprint    : np.ndarray, shape (7,) — KK imprint vector from imprint_signature
    wavelength : float                  — photon wavelength in Planck units (> 0)

    Returns
    -------
    kappa : float (> 0)

    Raises
    ------
    ValueError if imprint has wrong shape, zero norm, or wavelength ≤ 0.
    """
    imprint = np.asarray(imprint, dtype=float).ravel()
    if imprint.shape != (7,):
        raise ValueError(f"imprint must have shape (7,), got {imprint.shape}.")
    if wavelength <= 0.0:
        raise ValueError(f"wavelength={wavelength!r} must be > 0.")

    imprint_power = float(np.dot(imprint, imprint))   # |I|²
    if imprint_power < _EPS:
        raise ValueError("imprint has zero norm — no geometric content to couple.")

    kappa = ALPHA_FINE * (PLANCK_LENGTH / wavelength) * imprint_power
    return kappa


def optimize_imprint(
    target_signature: np.ndarray,
    candidates: Sequence[ImprintConfig],
) -> int:
    """Find the candidate configuration that maximises imprint fidelity.

    Given a target KK geometry signature I_target and a list of candidate
    configurations, returns the index of the candidate whose imprint is most
    similar to the target (maximises the squared cosine similarity).

    This is the "D-Wave QPU" analogue in the QIQD framework: the 5D geometric
    loss function L from the branch catalog implicitly constrains which candidates
    can reach perfect fidelity 1.0 (only lossless branches with L = 0 can).

    Parameters
    ----------
    target_signature : np.ndarray, shape (7,) — target KK imprint vector
    candidates       : sequence of ImprintConfig — candidate configurations

    Returns
    -------
    best_idx : int — index into candidates of the configuration with highest
               imprint fidelity to the target

    Raises
    ------
    ValueError if candidates is empty, target has wrong shape/zero norm, or any
               candidate produces a zero-norm imprint.
    """
    target = np.asarray(target_signature, dtype=float).ravel()
    if target.shape != (7,):
        raise ValueError(f"target_signature must have shape (7,), got {target.shape}.")
    target_norm = float(np.linalg.norm(target))
    if target_norm < _EPS:
        raise ValueError("target_signature has zero norm.")

    if len(candidates) == 0:
        raise ValueError("candidates must be a non-empty sequence.")

    best_idx = -1
    best_fidelity = -1.0

    for idx, cfg in enumerate(candidates):
        I = imprint_signature(cfg.phi, cfg.A_mu, cfg.n1, cfg.n2)
        norm_I = float(np.linalg.norm(I))
        if norm_I < _EPS:
            raise ValueError(
                f"Candidate {idx} produces a zero-norm imprint vector."
            )
        overlap = float(np.dot(target, I))
        fidelity = (overlap ** 2) / (target_norm ** 2 * norm_I ** 2)
        if fidelity > best_fidelity:
            best_fidelity = fidelity
            best_idx = idx

    return best_idx


def imprint_stability(
    imprint: np.ndarray,
    T: float,
    m_phi: float = 1.0,
    phi_min: float = 0.1,
    phi_star: float = 1.0,
) -> dict:
    """Assess the thermal stability of a KK geometric imprint.

    The imprint survives thermal decoherence if the thermal energy k_B T
    (k_B = 1 in Planck units) remains below the threshold set by the
    Goldberger–Wise stabilisation (Pillar 28, bh_remnant.py):

        Stable iff   T < T_H_max = m_phi × Δφ / (2π φ_min)

    where Δφ = φ_star − φ_min.

    The stability fraction is:

        S_frac = 1 − T / T_H_max     (clamped to [0, 1])

    S_frac = 1 → perfectly stable (T = 0).
    S_frac = 0 → at the decoherence threshold.
    S_frac < 0 → imprint is destroyed (clamped to 0).

    Parameters
    ----------
    imprint  : np.ndarray, shape (7,) — KK imprint vector
    T        : float — temperature in Planck units (≥ 0)
    m_phi    : float — Goldberger–Wise mass parameter (> 0, default 1.0)
    phi_min  : float — GW stabilisation floor on φ (> 0, default 0.1)
    phi_star : float — GW vacuum expectation value (> phi_min, default 1.0)

    Returns
    -------
    result : dict with keys
        'T_H_max'          — float — maximum Hawking temperature (decoherence threshold)
        'stability_fraction' — float — S_frac ∈ [0, 1] (1 = fully stable)
        'stable'           — bool  — True iff T < T_H_max
        'imprint_power'    — float — |I|² (total imprint power)
        'effective_coupling' — float — imprint_power × S_frac (usable imprint signal)

    Raises
    ------
    ValueError if imprint has wrong shape, T < 0, or GW parameters are invalid.
    """
    imprint = np.asarray(imprint, dtype=float).ravel()
    if imprint.shape != (7,):
        raise ValueError(f"imprint must have shape (7,), got {imprint.shape}.")
    if T < 0.0:
        raise ValueError(f"T={T!r} must be ≥ 0.")
    if m_phi <= 0.0:
        raise ValueError(f"m_phi={m_phi!r} must be > 0.")
    if phi_min <= 0.0:
        raise ValueError(f"phi_min={phi_min!r} must be > 0.")
    if phi_star <= phi_min:
        raise ValueError(
            f"phi_star={phi_star!r} must be strictly greater than phi_min={phi_min!r}."
        )

    T_H_max = remnant_temperature(phi_min, phi_star, m_phi)
    stability_fraction = max(0.0, 1.0 - T / T_H_max)
    stable = T < T_H_max

    imprint_power = float(np.dot(imprint, imprint))
    effective_coupling = imprint_power * stability_fraction

    return {
        "T_H_max": T_H_max,
        "stability_fraction": stability_fraction,
        "stable": stable,
        "imprint_power": imprint_power,
        "effective_coupling": effective_coupling,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_pair(n1: int, n2: int) -> None:
    """Raise ValueError for unphysical (n1, n2) braid pairs."""
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be a positive integer.")
    if n2 <= n1:
        raise ValueError(f"n2={n2!r} must be strictly greater than n1={n1!r}.")


# ---------------------------------------------------------------------------
# Authorship
# ---------------------------------------------------------------------------
# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, document engineering, and synthesis:
# GitHub Copilot (AI).
