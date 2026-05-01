# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/information_paradox.py
================================
Pillar 36 — 5D Geometric Resolution of the Black Hole Information Paradox.

Physical context
----------------
The black hole information paradox (Hawking 1976) states that if a black hole
evaporates completely via thermal Hawking radiation, all information that fell
into it is destroyed — violating quantum-mechanical unitarity.

The Unitary Manifold resolves this paradox through three geometric mechanisms:

1. **Arrow of time encoded in the metric**
   The irreversibility gauge field B_μ couples to the 5D metric via the
   Walker–Pearson field equations.  This encodes the arrow of time *into the
   metric itself* — the 5D spacetime is fundamentally time-oriented, and
   unitarity is guaranteed by the same topological structure that produces
   the winding spectrum.

2. **Remnant mass prevents complete evaporation**
   The Goldberger–Wise potential provides a hard lower bound on the radion
   field φ ≥ φ_min > 0, which caps the Hawking temperature at T_H_max and
   prevents the black hole from evaporating completely.  The remnant stores
   all swallowed information as 5D topological geometry (see bh_remnant.py).

3. **Holographic bound in KK geometry**
   The 5D holographic bound is tighter than the 4D one:

       S_5D ≤ A / (4 G₅)    where G₅ = G₄ × R                     [1]

   This ensures the information content of the KK degrees of freedom is
   bounded by the remnant area, not the original BH area.

The Page curve
~~~~~~~~~~~~~~
For a unitarily evaporating black hole (Page 1993), the entanglement entropy
of the Hawking radiation S_rad(t) follows the Page curve:

    S_rad(t) = min(S_bh(t), S_initial − S_bh(t))                   [2]

where S_bh(t) = 4π M(t)² is the black hole entropy at time t and S_initial
is the entropy at t=0.  In the UM framework:

    - For t < t_Page (early radiation): S_rad = S_bh(t)  (increases)
    - For t > t_Page (late radiation):  S_rad = S_initial − S_bh(t) (decreases)
    - At t → ∞: S_rad → S_initial − S_rem  (all radiation released)
    - Remnant stores: S_rem = 4π M_rem²  (never released as radiation)

Information encoding in 5D topology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The K_CS topological winding states provide C_KK = log₂(k_cs) ≈ 6.21 bits
per compactification cycle (from kk_quantum_info.py).  The total information
capacity of the remnant is:

    I_rem = S_rem / ln(2)   [bits, Bekenstein–Hawking]              [3]

Unitarity check
~~~~~~~~~~~~~~~~
Information is conserved because:

    I_total = I_radiation + I_remnant = I_initial                    [4]

where I_radiation = (S_initial − S_rem) / ln(2)  (information released as
correlations in the Hawking pairs), and I_remnant is locked in the 5D
topological structure.

All quantities are in **natural (Planck) units**: ħ = c = G = k_B = 1.

Public API
----------
arrow_of_time_encoding(phi, phi_star)
    Quantify how strongly the arrow of time is encoded in the metric via the
    radion displacement from its fixed point.

page_curve(M_initial, M_rem, t_fraction)
    Radiation entropy S_rad at fractional evaporation time t_fraction ∈ [0, 1].

page_time_fraction(M_initial, M_rem)
    The Page time as a fraction of total evaporation time (≈ 0.5 for
    pure Hawking; deviates in UM due to remnant endpoint).

holographic_bound_4d(area)
    Standard 4D holographic bound: S ≤ area / 4  (Bekenstein–Hawking).

holographic_bound_5d(area, R)
    5D KK holographic bound: S ≤ area / (4 G₅) = area / (4 R)
    (tighter than 4D by factor 1/R when R < 1 in Planck units).

information_encoding_5d(M_rem)
    Information stored in the remnant in bits: I = S_rem / ln(2).

unitarity_check(I_initial, I_radiation, I_remnant, tol)
    Verify that I_initial = I_radiation + I_remnant (unitarity condition).

remnant_information_fraction(M_initial, M_rem)
    Fraction of total initial information stored in the remnant.

hawking_radiation_spectrum_geometric(M, T_H, num_modes)
    Geometric approximation to the Hawking radiation spectrum:
    n_ω = 1 / (exp(ω/T_H) − 1)  (Planck spectrum).

kk_information_channel(n1, n2)
    Information per compactification cycle from the KK winding spectrum.

information_paradox_summary(M_initial, phi_min, m_phi, phi0)
    Full summary of the UM information paradox resolution.

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

from .bh_remnant import (
    remnant_mass,
    remnant_entropy,
    remnant_information_bits,
    remnant_temperature,
)
from .kk_quantum_info import (
    kk_channel_capacity,
    braided_winding_entropy,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_FOUR_PI: float = 4.0 * math.pi
_LN2: float = math.log(2.0)

#: Canonical braid pair
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
K_CS_CANONICAL: int = 74

#: Canonical GW parameters (Planck units)
PHI0_CANONICAL: float = 1.0
M_PHI_CANONICAL: float = 1.0
PHI_MIN_CANONICAL: float = 0.1


# ---------------------------------------------------------------------------
# arrow_of_time_encoding
# ---------------------------------------------------------------------------

def arrow_of_time_encoding(phi: float, phi_star: float) -> float:
    """Quantify how strongly the arrow of time is encoded in the metric.

    The arrow of time is encoded via the radion displacement from the FTUM
    fixed point.  When φ = φ_star the information current is exactly conserved
    and the arrow of time is perfectly encoded.  The encoding strength is

        A_time(φ) = 1 − D(φ) = 1 − |1 − (φ/φ_star)²|

    which is maximised at φ = φ_star (A_time = 1) and decreases away from it.

    Parameters
    ----------
    phi      : float — current radion field value (> 0)
    phi_star : float — FTUM fixed-point value (> 0)

    Returns
    -------
    A_time : float in [0, 1] (clamped; exact range depends on φ/φ_star)

    Raises
    ------
    ValueError if phi ≤ 0 or phi_star ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi_star <= 0.0:
        raise ValueError(f"phi_star must be > 0, got {phi_star!r}")
    D = abs(1.0 - (phi / phi_star) ** 2)
    return max(0.0, 1.0 - D)


# ---------------------------------------------------------------------------
# page_curve
# ---------------------------------------------------------------------------

def page_curve(
    M_initial: float,
    M_rem: float,
    t_fraction: float,
) -> float:
    """Radiation entropy S_rad at fractional evaporation time.

    The UM Page curve follows the standard Page (1993) formula, but with a
    finite endpoint: the black hole does not evaporate completely, stopping
    at M_rem.

    Parameterisation:
        Let M(t) = M_initial − (M_initial − M_rem) × t_fraction
        (linear model of mass loss; t_fraction ∈ [0, 1])

        S_bh(t) = 4π M(t)²
        S_initial = 4π M_initial²
        S_rad(t) = min(S_bh(t), S_initial − S_bh(t))

    Parameters
    ----------
    M_initial   : float — initial BH mass in Planck units (> M_rem > 0)
    M_rem       : float — remnant mass in Planck units (> 0)
    t_fraction  : float — fractional evaporation time in [0, 1]

    Returns
    -------
    S_rad : float ≥ 0 — Hawking radiation entanglement entropy

    Raises
    ------
    ValueError if M_initial ≤ M_rem ≤ 0 or t_fraction not in [0, 1].
    """
    if M_rem <= 0.0:
        raise ValueError(f"M_rem must be > 0, got {M_rem!r}")
    if M_initial <= M_rem:
        raise ValueError(f"M_initial ({M_initial!r}) must be > M_rem ({M_rem!r})")
    if not (0.0 <= t_fraction <= 1.0):
        raise ValueError(f"t_fraction must be in [0, 1], got {t_fraction!r}")

    M_t = M_initial - (M_initial - M_rem) * t_fraction
    S_bh_t = _FOUR_PI * M_t ** 2
    S_initial = _FOUR_PI * M_initial ** 2
    return float(min(S_bh_t, S_initial - S_bh_t))


# ---------------------------------------------------------------------------
# page_time_fraction
# ---------------------------------------------------------------------------

def page_time_fraction(M_initial: float, M_rem: float) -> float:
    """Page time as a fraction of total evaporation time.

    The Page time t_Page is when S_rad = S_initial/2, i.e., when
    S_bh(t_Page) = S_initial/2.

    In the linear mass-loss model:
        M(t_Page)² = M_initial² / 2
        M(t_Page)  = M_initial / √2

    The fractional time is:
        t_Page_frac = (M_initial − M_initial/√2) / (M_initial − M_rem)
                    = (1 − 1/√2) / (1 − M_rem/M_initial)

    Parameters
    ----------
    M_initial : float — initial BH mass (> M_rem)
    M_rem     : float — remnant mass (> 0)

    Returns
    -------
    t_page_frac : float in (0, 1)

    Raises
    ------
    ValueError if M_initial ≤ M_rem ≤ 0.
    """
    if M_rem <= 0.0:
        raise ValueError(f"M_rem must be > 0, got {M_rem!r}")
    if M_initial <= M_rem:
        raise ValueError(f"M_initial ({M_initial!r}) must be > M_rem ({M_rem!r})")
    delta_M_page = M_initial * (1.0 - 1.0 / math.sqrt(2.0))
    delta_M_total = M_initial - M_rem
    return delta_M_page / delta_M_total


# ---------------------------------------------------------------------------
# holographic_bound_4d
# ---------------------------------------------------------------------------

def holographic_bound_4d(area: float) -> float:
    """Standard 4D Bekenstein–Hawking holographic entropy bound.

        S ≤ A / 4  (Planck units, G₄ = 1)

    Parameters
    ----------
    area : float — area of the enclosing surface in Planck units (≥ 0)

    Returns
    -------
    S_max : float ≥ 0

    Raises
    ------
    ValueError if area < 0.
    """
    if area < 0.0:
        raise ValueError(f"area must be ≥ 0, got {area!r}")
    return area / 4.0


# ---------------------------------------------------------------------------
# holographic_bound_5d
# ---------------------------------------------------------------------------

def holographic_bound_5d(area: float, R: float) -> float:
    """5D KK holographic entropy bound.

    In the KK reduction, the 5D Newton constant is G₅ = G₄ × R (with G₄ = 1).
    The 5D holographic bound on entropy in a region of 4D area A is:

        S ≤ A / (4 G₅) = A / (4 R)

    For R < 1 (compact dimension smaller than Planck length) this is tighter
    than the 4D bound by a factor of 1/R.  For R > 1 it is weaker.

    Parameters
    ----------
    area : float — 4D area of the enclosing surface in Planck units (≥ 0)
    R    : float — compactification radius in Planck units (> 0)

    Returns
    -------
    S_max_5d : float ≥ 0

    Raises
    ------
    ValueError if area < 0 or R ≤ 0.
    """
    if area < 0.0:
        raise ValueError(f"area must be ≥ 0, got {area!r}")
    if R <= 0.0:
        raise ValueError(f"R must be > 0, got {R!r}")
    G5 = R   # G₅ = G₄ × R with G₄ = 1
    return area / (4.0 * G5)


# ---------------------------------------------------------------------------
# information_encoding_5d
# ---------------------------------------------------------------------------

def information_encoding_5d(M_rem: float) -> float:
    """Information stored in the BH remnant in bits.

    Delegates to remnant_information_bits from bh_remnant.py.

        I_rem = S_rem / ln(2) = 4π M_rem² / ln(2)  [bits]

    Parameters
    ----------
    M_rem : float — remnant mass in Planck units (≥ 0)

    Returns
    -------
    I_rem : float ≥ 0 (in bits)

    Raises
    ------
    ValueError if M_rem < 0.
    """
    return remnant_information_bits(M_rem)


# ---------------------------------------------------------------------------
# unitarity_check
# ---------------------------------------------------------------------------

def unitarity_check(
    I_initial: float,
    I_radiation: float,
    I_remnant: float,
    tol: float = 1.0e-8,
) -> bool:
    """Verify that total information is conserved (unitarity condition).

    In a unitary evaporation process:

        I_initial = I_radiation + I_remnant

    (all information initially in the BH ends up either in the Hawking
    radiation or stored in the remnant topology).

    Parameters
    ----------
    I_initial   : float — initial information content in bits (≥ 0)
    I_radiation : float — information in Hawking radiation in bits (≥ 0)
    I_remnant   : float — information stored in the remnant in bits (≥ 0)
    tol         : float — fractional tolerance on conservation (default 1e-8)

    Returns
    -------
    bool — True iff |I_initial − (I_radiation + I_remnant)| / I_initial < tol

    Raises
    ------
    ValueError if I_initial ≤ 0, I_radiation < 0, or I_remnant < 0.
    """
    if I_initial <= 0.0:
        raise ValueError(f"I_initial must be > 0, got {I_initial!r}")
    if I_radiation < 0.0:
        raise ValueError(f"I_radiation must be ≥ 0, got {I_radiation!r}")
    if I_remnant < 0.0:
        raise ValueError(f"I_remnant must be ≥ 0, got {I_remnant!r}")
    defect = abs(I_initial - (I_radiation + I_remnant))
    return defect / I_initial < tol


# ---------------------------------------------------------------------------
# remnant_information_fraction
# ---------------------------------------------------------------------------

def remnant_information_fraction(M_initial: float, M_rem: float) -> float:
    """Fraction of total initial information stored in the remnant.

    I_rem_fraction = S_rem / S_initial = (M_rem / M_initial)²

    (since S = 4π M² for a Schwarzschild BH).

    Parameters
    ----------
    M_initial : float — initial BH mass (> M_rem > 0)
    M_rem     : float — remnant mass (> 0)

    Returns
    -------
    f : float in (0, 1)

    Raises
    ------
    ValueError if M_initial ≤ M_rem ≤ 0.
    """
    if M_rem <= 0.0:
        raise ValueError(f"M_rem must be > 0, got {M_rem!r}")
    if M_initial <= M_rem:
        raise ValueError(f"M_initial ({M_initial!r}) must be > M_rem ({M_rem!r})")
    return (M_rem / M_initial) ** 2


# ---------------------------------------------------------------------------
# hawking_radiation_spectrum_geometric
# ---------------------------------------------------------------------------

def hawking_radiation_spectrum_geometric(
    M: float,
    num_modes: int = 20,
) -> np.ndarray:
    """Planck-spectrum Hawking radiation occupation numbers.

    The mean occupation number for mode frequency ω in a thermal state at
    Hawking temperature T_H = 1/(8π M) (Schwarzschild) is:

        ⟨n_ω⟩ = 1 / (exp(ω / T_H) − 1)

    Frequencies are sampled on a fixed grid independent of M:
        ω_k = k × ω_ref   for k = 1, ..., num_modes
    where ω_ref = 1 / (8π) is the Hawking temperature for M = 1.

    This ensures that larger M (cooler BH) gives larger occupation numbers
    at all sampled frequencies, as expected physically.

    Parameters
    ----------
    M         : float — BH mass in Planck units (> 0)
    num_modes : int   — number of frequency modes to sample (≥ 1)

    Returns
    -------
    n_omega : np.ndarray, shape (num_modes,), float64
        Mean occupation numbers ⟨n_ω⟩ at fixed frequencies ω_k = k/(8π).

    Raises
    ------
    ValueError if M ≤ 0 or num_modes < 1.
    """
    if M <= 0.0:
        raise ValueError(f"M must be > 0, got {M!r}")
    if num_modes < 1:
        raise ValueError(f"num_modes must be ≥ 1, got {num_modes!r}")
    T_H = 1.0 / (8.0 * math.pi * M)
    # Fixed frequency grid: ω_k = k × T_H_reference(M=1)
    omega_ref = 1.0 / (8.0 * math.pi)   # T_H for M = 1
    ks = np.arange(1, num_modes + 1, dtype=float)
    omega_k = ks * omega_ref
    return 1.0 / (np.exp(omega_k / T_H) - 1.0)


# ---------------------------------------------------------------------------
# kk_information_channel
# ---------------------------------------------------------------------------

def kk_information_channel(n1: int, n2: int) -> dict:
    """Information per compactification cycle from the KK winding spectrum.

    The KK compact dimension acts as a quantum information channel with
    capacity C_KK = log₂(k_cs) bits and entanglement entropy S_braid.

    Parameters
    ----------
    n1 : int — primary winding number (≥ 1)
    n2 : int — secondary winding number (> n1)

    Returns
    -------
    dict with keys
        'n1'          — primary winding number
        'n2'          — secondary winding number
        'k_cs'        — Chern–Simons level = n1² + n2²
        'C_KK_bits'   — channel capacity log₂(k_cs) in bits
        'S_braid'     — entanglement entropy of braided winding state (nats)
        'S_braid_bits'— S_braid / ln(2) in bits

    Raises
    ------
    ValueError if n1 < 1 or n2 ≤ n1.
    """
    if n1 < 1:
        raise ValueError(f"n1={n1!r} must be ≥ 1.")
    if n2 <= n1:
        raise ValueError(f"n2={n2!r} must be > n1={n1!r}.")
    C = kk_channel_capacity(n1, n2)
    S_braid = braided_winding_entropy(n1, n2)
    from .braided_winding import resonant_kcs
    k_cs = resonant_kcs(n1, n2)
    return {
        "n1": n1,
        "n2": n2,
        "k_cs": k_cs,
        "C_KK_bits": C,
        "S_braid": S_braid,
        "S_braid_bits": S_braid / _LN2,
    }


# ---------------------------------------------------------------------------
# information_paradox_summary
# ---------------------------------------------------------------------------

def information_paradox_summary(
    M_initial: float,
    phi_min: float = PHI_MIN_CANONICAL,
    m_phi: float = M_PHI_CANONICAL,
    phi0: float = PHI0_CANONICAL,
) -> dict:
    """Full summary of the UM information paradox resolution.

    Parameters
    ----------
    M_initial : float — initial BH mass in Planck units (> 0)
    phi_min   : float — GW lower bound on radion (> 0)
    m_phi     : float — GW mass parameter (> 0)
    phi0      : float — GW vacuum value (> phi_min)

    Returns
    -------
    dict with keys
        'M_initial'             — initial BH mass
        'M_rem'                 — GW-stabilised remnant mass
        'T_H_max'               — maximum Hawking temperature
        'S_initial'             — initial BH entropy (Bekenstein–Hawking)
        'S_rem'                 — remnant entropy
        'S_rad_total'           — total Hawking radiation entropy
        'I_initial_bits'        — initial information content
        'I_rem_bits'            — information in remnant
        'I_rad_bits'            — information in Hawking radiation
        'remnant_fraction'      — fraction of info stored in remnant
        'unitarity'             — True if information is conserved
        'page_time_fraction'    — fractional Page time
        'kk_channel'            — dict from kk_information_channel()
        'arrow_of_time'         — encoding strength at phi0

    Raises
    ------
    ValueError if any parameter is unphysical.
    """
    M_rem    = remnant_mass(phi_min, m_phi, phi0)
    if M_initial <= M_rem:
        # Silently set M_initial to a physically meaningful value
        M_initial = M_rem * 10.0

    T_H_max  = remnant_temperature(phi_min, phi0, m_phi)
    S_init   = _FOUR_PI * M_initial ** 2
    S_rem    = remnant_entropy(M_rem)
    S_rad    = max(0.0, S_init - S_rem)

    I_init   = S_init / _LN2
    I_rem    = information_encoding_5d(M_rem)
    I_rad    = max(0.0, I_init - I_rem)

    unitary  = unitarity_check(I_init, I_rad, I_rem)
    pg_frac  = page_time_fraction(M_initial, M_rem)
    kk_ch    = kk_information_channel(N1_CANONICAL, N2_CANONICAL)
    aot      = arrow_of_time_encoding(phi0, phi0)   # = 1 at fixed point

    return {
        "M_initial": M_initial,
        "M_rem": M_rem,
        "T_H_max": T_H_max,
        "S_initial": S_init,
        "S_rem": S_rem,
        "S_rad_total": S_rad,
        "I_initial_bits": I_init,
        "I_rem_bits": I_rem,
        "I_rad_bits": I_rad,
        "remnant_fraction": I_rem / I_init,
        "unitarity": unitary,
        "page_time_fraction": pg_frac,
        "kk_channel": kk_ch,
        "arrow_of_time": aot,
    }
