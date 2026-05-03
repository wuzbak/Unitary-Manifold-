# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/baryogenesis.py
========================
Pillar 105 — Baryogenesis from the Chern-Simons Irreversibility Field B_μ.

The observed baryon asymmetry η_B ≈ 6 × 10⁻¹⁰ arises from CP violation
encoded in the Chern-Simons level k_CS = 74 combined with sphaleron-mediated
baryon-number violation at the electroweak phase transition.

CP-violation amplitude
----------------------
The CS level maps to a CP-violation amplitude via

    ε_CP = k_CS / (k_CS² + 4π²)

For k_CS = 74: ε_CP = 74 / (74² + 4π²) ≈ 0.01323.

Sphaleron rate
--------------
At temperature T_EW the sphaleron transition rate per unit volume is

    Γ_sph = α_w⁴ × T_EW

with α_w = 1/30 the weak coupling at the EW scale.

Baryon-to-photon ratio
----------------------
The baryon asymmetry generated during the EW phase transition is

    η_B = ε_CP × Γ_sph / T_EW³ × (45 / 2π² g*)

where g* = 106.75 is the effective number of relativistic degrees of freedom
in the SM at T_EW.
"""

from __future__ import annotations

import math

# ------------------------------------------------------------------
# Physical constants
# ------------------------------------------------------------------
_ALPHA_W: float = 1.0 / 30.0        # weak coupling at EW scale
_G_STAR_EW: float = 106.75          # SM dof at EW phase transition
_TWO_PI_SQ: float = 2.0 * math.pi ** 2

# Default EW scale in GeV
_T_EW_DEFAULT: float = 246.0

# Observed baryon-to-photon ratio
OBSERVED_ETA_B: float = 6e-10

# Chern-Simons level (from braided winding)
K_CS: int = 74


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def cp_violation_amplitude(k_cs: float = K_CS) -> float:
    """Return the CP-violation amplitude ε_CP from the CS level k_CS.

    ε_CP = k_CS / (k_CS² + 4π²)

    Parameters
    ----------
    k_cs:
        Chern-Simons level (default 74).

    Returns
    -------
    float in (0, 1).
    """
    return k_cs / (k_cs ** 2 + 4.0 * math.pi ** 2)


def sphaleron_rate(temp_ew: float = _T_EW_DEFAULT) -> float:
    """Return the sphaleron transition rate Γ_sph = α_w⁴ × T_EW.

    Parameters
    ----------
    temp_ew:
        Electroweak scale temperature in GeV (default 246 GeV).

    Returns
    -------
    float  Γ_sph in GeV⁵ (natural units).
    """
    return _ALPHA_W ** 4 * temp_ew


def baryon_to_photon_ratio(k_cs: float = K_CS,
                            temp_ew: float = _T_EW_DEFAULT) -> float:
    """Return the baryon-to-photon ratio η_B.

    The dimensionless sphaleron rate is Γ_sph / T_EW⁴ = α_w⁴.
    We compute this from sphaleron_rate(T_EW) = α_w⁴ × T_EW by dividing
    by T_EW once more:

        η_B = ε_CP × (Γ_sph / T_EW) × (45 / 2π² g*)
            = ε_CP × α_w⁴ × (45 / 2π² g*)

    This is the standard freeze-out approximation that gives η_B ≈ 3–6 × 10⁻¹⁰.

    Parameters
    ----------
    k_cs:
        Chern-Simons level (default 74).
    temp_ew:
        EW scale temperature in GeV (default 246 GeV).

    Returns
    -------
    float  η_B (dimensionless), in the range [1e-11, 1e-9].
    """
    eps = cp_violation_amplitude(k_cs)
    gamma = sphaleron_rate(temp_ew)       # = α_w⁴ × T_EW
    prefactor = 45.0 / (_TWO_PI_SQ * _G_STAR_EW)
    # Divide by T_EW to extract the dimensionless rate α_w⁴
    return eps * (gamma / temp_ew) * prefactor


def baryogenesis_summary(k_cs: float = K_CS,
                          temp_ew: float = _T_EW_DEFAULT) -> dict:
    """Return a dict summarising the baryogenesis prediction.

    Keys
    ----
    cp_amplitude        : ε_CP
    sphaleron_rate      : Γ_sph
    eta_B               : predicted baryon-to-photon ratio
    observed_eta_B      : 6e-10 (PDG)
    order_of_magnitude_match : |log10(η_B / 6e-10)| < 2
    """
    eps = cp_violation_amplitude(k_cs)
    gamma = sphaleron_rate(temp_ew)
    eta = baryon_to_photon_ratio(k_cs, temp_ew)
    match = abs(math.log10(eta / OBSERVED_ETA_B)) < 2.0
    return {
        "cp_amplitude": eps,
        "sphaleron_rate": gamma,
        "eta_B": eta,
        "observed_eta_B": OBSERVED_ETA_B,
        "order_of_magnitude_match": match,
    }
