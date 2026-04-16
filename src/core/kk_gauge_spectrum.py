"""kk_gauge_spectrum.py
=======================
Kaluza–Klein gauge spectrum: what this 5D theory actually produces.

**This module addresses Gap 5 of UNIFICATION_PROOF.md §XII.**

Gap 5 claimed: "KK tower = Standard Model" but the Standard Model gauge
group SU(3)×SU(2)×U(1) and chiral fermions are not derived from 5D KK.

This module:
1. Shows what the 5D KK construction over S¹ DOES produce (U(1))
2. Shows what additional structure is needed for the full SM
3. Gives the Witten (1981) dimensional lower bound
4. Provides a spectrum calculator for the current 5D theory

Correct claim (replacing the overclaim in UNIFICATION_PROOF.md Part VIII)
--------------------------------------------------------------------------
The 5D KK construction with compact S¹ produces:

    - Zero mode: one massless U(1) gauge boson  →  photon  ✓
    - KK tower: massive U(1) modes at m_n = n/R  →  heavy, not SM bosons

To obtain the full Standard Model gauge structure requires:

    - For U(1)_Y: already present (zero mode)
    - For SU(2)_L: requires additional compact dimensions (≥1 extra)
    - For SU(3)_c: requires a further compact space with SU(3) isometry
    - Chiral fermions: require orbifold construction or D-brane structure

Witten (1981) proved: the minimum number of extra dimensions required to
accommodate the Standard Model gauge group with chiral fermions is 7,
giving a total spacetime dimension of 4+7 = 11.

The current theory (5D = 4+1) produces U(1) electromagnetism exactly.
That is a genuine result.  The overclaim that it also produces SU(2)×SU(3)
without additional structure is corrected here.

Public API
----------
kk_spectrum_1d(R, lam, n_modes)
    KK mass spectrum and gauge charges from 5D S¹ compactification.

gauge_group_from_5d()
    Returns the gauge group actually produced by the 5D construction.

sm_dimensional_requirements()
    Documents what additional dimensions are needed for each SM force.

kk_mode_mass(n, R)
    Mass of the n-th KK mode.

photon_identification()
    Shows the zero-mode identification with the photon.
"""

import numpy as np
from dataclasses import dataclass
from typing import List


# ---------------------------------------------------------------------------
# KK mass spectrum
# ---------------------------------------------------------------------------

@dataclass
class KKMode:
    """A single KK mode in the tower."""
    n:          int     # mode number (0 = zero mode, ±1, ±2, ...)
    mass:       float   # mass in units of 1/R (Planck units if R = ℓ_P)
    charge:     int     # KK charge = n (units of 1/R)
    gauge_group: str    # gauge group this mode transforms under
    label:      str     # physical identification


def kk_mode_mass(n: int, R: float, lam: float = 1.0) -> float:
    """Mass of the n-th KK mode.

    m_n = |n| / R

    In the current 5D theory, R = φ₀ ℓ_P (set by the radion vacuum value).
    For φ₀ ~ 1 (Planck units), m₁ ~ m_Planck ~ 1.2 × 10¹⁹ GeV.

    This is consistent with the non-observation of KK resonances at LHC.

    Parameters
    ----------
    n   : int    KK mode number
    R   : float  compactification radius
    lam : float  KK coupling (affects interaction strength, not mass)

    Returns
    -------
    mass : float   mass in units of [1/R]
    """
    return abs(n) / R


def kk_spectrum_1d(R: float = 1.0, lam: float = 1.0,
                   n_modes: int = 5) -> List[KKMode]:
    """KK mass spectrum from 5D S¹ compactification.

    Returns the tower of KK modes, each transforming as a massive U(1) boson.

    Note: ALL modes (n≠0) transform under U(1), not SU(2) or SU(3).
    The Standard Model W/Z bosons transform under SU(2)_L, which is NOT
    present in the 5D construction.

    Parameters
    ----------
    R       : float   compactification radius (φ₀ ℓ_P in Planck units)
    lam     : float   KK coupling
    n_modes : int     number of modes to include in each direction

    Returns
    -------
    modes : list of KKMode
    """
    modes = []
    for n in range(-n_modes, n_modes + 1):
        mass = kk_mode_mass(n, R, lam)
        if n == 0:
            label = 'photon (zero mode, massless U(1) gauge boson)'
            gauge = 'U(1)'
        else:
            label = f'KK mode n={n}: massive U(1) boson at m = {mass:.3f}/R'
            gauge = 'U(1)_KK'
        modes.append(KKMode(
            n=n, mass=mass, charge=n,
            gauge_group=gauge, label=label
        ))
    return modes


def gauge_group_from_5d() -> dict:
    """Gauge group produced by the 5D KK construction.

    Returns an honest statement of what is and is not produced.
    """
    return {
        'produced': 'U(1)',
        'produced_physical': 'One massless U(1) gauge boson (photon)',
        'NOT_produced': ['SU(2)_L', 'SU(3)_c'],
        'explanation': (
            "5D KK compactification on S¹ yields U(1) gauge symmetry "
            "from the isometry group of S¹, which is U(1) = SO(2). "
            "To obtain SU(2) you need the isometry group of S²  (n=2 sphere). "
            "To obtain SU(3) you need CP² or a 5-sphere. "
            "The minimum internal space for SU(3)×SU(2)×U(1) is 7-dimensional "
            "(Witten 1981), giving total 4+7 = 11 dimensions."
        ),
        'what_this_means_for_current_theory': (
            "The current 5D theory correctly produces electromagnetism. "
            "The claim in UNIFICATION_PROOF.md Part VIII that the KK tower "
            "yields the Standard Model gauge structure is an overclaim. "
            "A correct (reduced) claim: the theory geometrises electromagnetism. "
            "The weak and strong forces require additional structure."
        ),
    }


def sm_dimensional_requirements() -> List[dict]:
    """Minimum extra dimensions needed for each Standard Model force.

    Based on: Witten, E. (1981). 'Search for a realistic Kaluza-Klein theory.'
    Nuclear Physics B, 186(3), 412-428.

    Returns
    -------
    list of dicts, one per gauge sector
    """
    return [
        {
            'force': 'Electromagnetism',
            'gauge_group': 'U(1)',
            'extra_dims_needed': 1,
            'compact_space': 'S¹',
            'isometry_group': 'U(1) = SO(2)',
            'status_in_5d_theory': '✓ PRESENT (zero mode of Bμ)',
        },
        {
            'force': 'Weak force',
            'gauge_group': 'SU(2)_L',
            'extra_dims_needed': 3,
            'compact_space': 'S³ (3-sphere)',
            'isometry_group': 'SU(2) × SU(2)',
            'status_in_5d_theory': '✗ NOT PRESENT in current 5D theory',
            'note': 'Chirality (L subscript) requires orbifold, adding cost',
        },
        {
            'force': 'Strong force',
            'gauge_group': 'SU(3)_c',
            'extra_dims_needed': 5,
            'compact_space': 'CP² (complex projective plane)',
            'isometry_group': 'SU(3)',
            'status_in_5d_theory': '✗ NOT PRESENT in current 5D theory',
        },
        {
            'force': 'Chiral fermions (required for SM)',
            'gauge_group': 'SU(2)_L acts on left-handed only',
            'extra_dims_needed': 7,
            'compact_space': 'CP² × S²/Z₂ or similar orbifold',
            'isometry_group': 'SU(3) × SU(2) × U(1)',
            'status_in_5d_theory': '✗ NOT PRESENT — requires 11D total',
            'note': 'Witten (1981): 11 = 4 + 7 is the minimum',
        },
    ]


def photon_identification(lam: float = 1.0, phi0: float = 1.0) -> dict:
    """Show the photon identification: zero-mode of Bμ = photon.

    This identification IS valid and rigorous:
    - The zero KK mode (n=0) is massless
    - It has U(1) gauge symmetry
    - Its field strength H_μν = ∂_μBν − ∂_νBμ has Maxwell-form dynamics
    - Charge quantisation follows from the compactness of S¹

    Returns
    -------
    dict with photon properties from the KK spectrum
    """
    m_zero = kk_mode_mass(0, R=phi0)
    m_first_kk = kk_mode_mass(1, R=phi0)

    return {
        'zero_mode_mass':           m_zero,           # exactly 0
        'zero_mode_gauge_symmetry': 'U(1)',
        'zero_mode_field_strength': 'F_μν = λ H_μν = λ(∂_μBν − ∂_νBμ)',
        'electromagnetic_potential': f'A_μ = {lam} × Bμ',
        'first_kk_mass':            m_first_kk,       # 1/φ₀ ≈ m_Planck
        'identification_valid':     True,
        'identification_basis':     'Massless, U(1)-charged, Maxwell dynamics',
        'note': (
            'The photon identification is rigorous. '
            'The W/Z/gluon identifications in UNIFICATION_PROOF.md Part VIII '
            'are not — they require additional compact dimensions.'
        ),
    }


def gap5_status() -> str:
    """Return the honest status of Gap 5 after this module."""
    return (
        "GAP 5 STATUS: PARTIALLY RESOLVED\n"
        "\n"
        "RESOLVED: U(1) electromagnetism IS produced by the 5D KK construction.\n"
        "          The photon is the zero mode of Bμ. This is rigorous.\n"
        "\n"
        "REMAINS: SU(2)_L and SU(3)_c are NOT produced by the current 5D theory.\n"
        "         Getting the full SM requires at minimum 7 extra dimensions\n"
        "         (Witten 1981). The current overclaim in UNIFICATION_PROOF.md\n"
        "         Part VIII is corrected by this module.\n"
        "\n"
        "CORRECT REDUCED CLAIM: This 5D theory geometrises electromagnetism.\n"
        "         Extension to the full SM is an open problem requiring\n"
        "         additional compact dimensions.\n"
    )
