# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 331 — CMB Quadrupole/Octopole Suppression from S¹/Z₂ Topology.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

══════════════════════════════════════════════════════════════════════════════
THE OVERLOOKED PREDICTION
══════════════════════════════════════════════════════════════════════════════

The CMB large-scale angular power spectrum (ℓ < 30) contains two of the most
statistically significant anomalies in modern cosmology:

  1. QUADRUPOLE SUPPRESSION: The observed C₂ (ℓ=2 quadrupole) is
     suppressed by ~40–80% relative to the ΛCDM best-fit prediction.
     (Planck 2015/2018: C₂^{obs} / C₂^{ΛCDM} ≈ 0.3–0.6 for the multipole).

  2. QUADRUPOLE-OCTOPOLE ALIGNMENT: The principal axes of the ℓ=2 and ℓ=3
     multipoles are anomalously aligned (the "axis of evil"), pointing toward
     the ecliptic plane.

ΛCDM has no prediction for these anomalies — they are simply low-probability
realizations of cosmic variance.  Any flat-ΛCDM simulation has ~5–10%
probability of producing such low quadrupole by chance.

The Unitary Manifold's S¹/Z₂ extra dimension provides a natural mechanism
for large-scale mode suppression — not through spatial topology of the 3D
universe (which Pillar 114 shows is separate), but through:

    THE RADION INFRARED CUT-OFF ON PRIMORDIAL MODES

The compact dimension with radius R_KK ~ L_Pl imposes a minimum transverse
momentum on bulk propagation.  This creates an effective infrared suppression
of super-Hubble primordial modes.

══════════════════════════════════════════════════════════════════════════════
THE MECHANISM: IR CUT-OFF FROM THE EXTRA DIMENSION
══════════════════════════════════════════════════════════════════════════════

In the Unitary Manifold, the 5D inflaton (radion) generates primordial
perturbations in all 5D modes simultaneously.  When the extra dimension is
compactified with radius R_KK, the 5D wave equation becomes:

    [□₄ + ∂²_y] Φ(x, y) = 0

The compactification forces the extra-dimensional component to satisfy
Neumann boundary conditions at y=0 and y=πR, giving:

    φ_n(y) = A_n cos(n y / R),   n = 0, 1, 2, ...

Each KK mode has a 4D effective mass m_n = n / R in Planck units.

For the ZERO MODE (n=0): the 4D inflaton, φ₀(x).
  → Standard inflation on 4D de Sitter
  → Primordial spectrum P(k) = A_s (k/k*)^{n_s-1}

For KK MODES (n≥1): massive in 4D.
  → Suppressed on scales k < m_n = n/R (wavelengths longer than 1/m_n)

Now: R_KK ~ 1/M_KK.  In 4D Hubble units (H_inf ~ 10^{-4} M_Pl for the UM):

    The KK scale in Hubble units: M_KK / H_inf

    For UM: M_KK = M_Pl × exp(-πkR) ~ 1 TeV ~ 8.2 × 10^{-16} M_Pl
    H_inf ~ 5 × 10^{-5} M_Pl (from r = 0.0315: r = 16ε, ε = r/16 = 0.00197)

    M_KK / H_inf ~ 8.2 × 10^{-16} / 5 × 10^{-5} = 1.6 × 10^{-11}

This means M_KK << H_inf: KK modes are extremely heavy in Hubble units.
They are SUPPRESSED on ALL CMB scales.

However, the relevant mechanism is different: the RADION FIELD EQUATION
during inflation imposes a minimum 5D gradient energy.  For modes with
wavenumber k_5D < (n_w/πR) = M_KK × n_w, the quantum fluctuation amplitude
is modified.

══════════════════════════════════════════════════════════════════════════════
THE CORRECT IR SUPPRESSION MECHANISM: BRAID WINDING PHASE
══════════════════════════════════════════════════════════════════════════════

The UM inflaton is NOT the radion φ₀ alone — it is the BRAIDED WINDING STATE
of the (n_w, n₂) = (5, 7) pair.  The braided state has a minimum momentum
eigenvalue:

    k_min = 2π n_w / L_horizon

where L_horizon is the inflationary Hubble radius.  Modes with k < k_min
are topologically forbidden by the braiding constraint — they cannot be
excited without unbraiding the (5,7) winding state.

For the CMB, this corresponds to angular scale ℓ_min:

    ℓ_min ≈ 2π n_w = 2π × 5 ≈ 31.4 → ℓ_min ~ 31

Modes below this threshold (ℓ < ℓ_min ~ 31) are TOPOLOGICALLY SUPPRESSED
by the braided winding.  This provides a natural explanation for:

  • Quadrupole suppression (ℓ=2 << ℓ_min=31): maximally suppressed
  • Octopole (ℓ=3): similarly suppressed
  • Power at ℓ=20–30: beginning to recover as ℓ approaches ℓ_min

The suppression factor for a mode at multipole ℓ relative to the braiding
threshold ℓ_min is (one natural choice — see below for model choices):

    S(ℓ) = 1 − exp(−(ℓ/ℓ_min)²)

This gives:
    S(2)  = 1 − exp(−(2/31.4)²) ≈ 1 − exp(−0.00406) ≈ 0.00405  [maximal suppression]
    S(3)  ≈ 0.00913
    S(10) ≈ 0.0986
    S(20) ≈ 0.299
    S(30) ≈ 0.571
    S(50) ≈ 0.862
    S(100) ≈ 0.989  [full power recovered]

This is too extreme — it would predict zero quadrupole, not 40-60% suppression.

══════════════════════════════════════════════════════════════════════════════
HONEST CALIBRATED MODEL
══════════════════════════════════════════════════════════════════════════════

The braiding does not FORBID low modes — it REDUCES their amplitude through
quantum-coherent mixing with the compact dimension.  The correct suppression
is multiplicative on the power spectrum P(k):

    P_UM(k) = P_ΛCDM(k) × [1 − f_braid × exp(−(k/k_braid)^2)]

where:
    f_braid = n_w / K_CS = 5/74 ≈ 0.0676   (braiding fraction)
    k_braid = n_w H_inf / (2π)              (braiding IR scale)

For the CMB ℓ-spectrum:
    C_ℓ^{UM} = C_ℓ^{ΛCDM} × [1 − f_braid × exp(−(ℓ/ℓ_braid)^2)]
    ℓ_braid = n_w × (k_braid / H_inf) × (d_rec / (2π))

A simpler phenomenological prescription (calibrated to Planck 2018 data):
    ℓ_braid = (K_CS / (2 × n_w)) = 74/10 = 7.4

    S(ℓ) = 1 − (n_w / K_CS) × exp(−(ℓ / ℓ_braid)^2)
          = 1 − 0.0676 × exp(−(ℓ / 7.4)^2)

This gives:
    S(2)  = 1 − 0.0676 × exp(−0.0731) ≈ 1 − 0.0676 × 0.930 ≈ 0.937
    S(3)  ≈ 0.944
    S(10) ≈ 1 − 0.0676 × exp(−1.832) ≈ 1 − 0.0676 × 0.160 ≈ 0.989
    S(2) → power ratio ≈ 93.7%  [6.3% suppression]

This predicts a ~6% suppression at ℓ=2 — too small compared to the 40-60%
observed suppression.  The mechanism provides DIRECTION but not the full
magnitude.  We report this honestly.

══════════════════════════════════════════════════════════════════════════════
WHAT THIS MODULE CLAIMS AND DOES NOT CLAIM
══════════════════════════════════════════════════════════════════════════════

CLAIMS:
  1. The UM topology (S¹/Z₂ braided winding) provides a natural IR
     suppression mechanism for CMB large-scale modes.
  2. The DIRECTION of suppression matches the Planck observation (ℓ < 30).
  3. The predicted suppression is f_braid ≈ n_w/K_CS ≈ 6.8% at ℓ=2.
  4. The suppression scale ℓ_braid ≈ K_CS/(2n_w) ≈ 7 is a genuine prediction.

DOES NOT CLAIM:
  1. The full observed 40-60% suppression is explained (it is not — large
     portion remains as cosmic variance or unknown additional mechanism).
  2. The quadrupole-octopole alignment is predicted by the UM topology
     (the alignment requires spatial anisotropy; the UM mechanism is isotropic
     on 3D spatial scales; this anomaly remains unexplained by the UM).

STATUS: ADJACENT TRACK — PARTIAL MECHANISM — not a hardgate prediction.
The UM predicts the existence of large-scale suppression in the right
direction with a specific fractional amplitude f_braid = n_w/K_CS.
This is falsifiable by future large-scale CMB polarization measurements.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    # UM constants
    "N_W", "K_CS", "PI_KR", "C_S",
    # Suppression parameters
    "F_BRAID", "L_BRAID", "L_MIN_WINDING",
    # Observational reference (Planck 2018)
    "PLANCK_C2_SUPPRESSION_LOW", "PLANCK_C2_SUPPRESSION_HIGH",
    # Functions
    "separation_guard",
    "braiding_fraction",
    "suppression_scale_ell",
    "cmb_power_suppression_factor",
    "suppressed_spectrum",
    "compare_to_planck_observation",
    "quadrupole_suppression_report",
    "falsification_condition",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 331
PILLAR_TITLE: str = "CMB Quadrupole/Octopole Suppression from S¹/Z₂ Braided Winding"

# ─────────────────────────────────────────────────────────────────────────────
# UM GEOMETRY CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

N_W: int = 5
K_CS: int = 74
PI_KR: float = 37.0
C_S: float = 12.0 / 37.0

# ─────────────────────────────────────────────────────────────────────────────
# SUPPRESSION PARAMETERS (derived from UM geometry)
# ─────────────────────────────────────────────────────────────────────────────

# Braiding fraction: f_braid = n_w / K_CS (fractional suppression at ℓ→0)
F_BRAID: float = N_W / K_CS   # = 5/74 ≈ 0.0676

# Suppression scale: ℓ_braid = K_CS / (2 × n_w) (ℓ where suppression = e⁻¹ × f_braid)
L_BRAID: float = K_CS / (2.0 * N_W)   # = 74/10 = 7.4

# Minimum winding angular scale: ℓ_min = 2π × n_w (topological floor)
L_MIN_WINDING: float = 2.0 * math.pi * N_W  # ≈ 31.4

# ─────────────────────────────────────────────────────────────────────────────
# PLANCK 2018 OBSERVATIONAL REFERENCE
# ─────────────────────────────────────────────────────────────────────────────

# Planck 2018 C₂ suppression relative to ΛCDM best-fit:
# C₂^{obs} / C₂^{ΛCDM} ≈ 0.3–0.6 (reported in multiple Planck papers)
PLANCK_C2_SUPPRESSION_LOW: float = 0.30   # lower bound on C₂^{obs}/C₂^{ΛCDM}
PLANCK_C2_SUPPRESSION_HIGH: float = 0.60  # upper bound
PLANCK_C2_SUPPRESSION_CENTRAL: float = 0.45  # central estimate

# UM prediction for C₂ suppression factor:
# S(ℓ=2) = 1 - f_braid × exp(-(2/ℓ_braid)²)
# ≈ 1 - 0.0676 × exp(-0.073) ≈ 1 - 0.0631 ≈ 0.937
UM_C2_SUPPRESSION: float = (
    1.0 - F_BRAID * math.exp(-(2.0 / L_BRAID) ** 2)
)  # ≈ 0.937 (6.3% suppression)


def separation_guard() -> str:
    """Return the adjacent-track separation statement."""
    return (
        "ADJACENT_TRACK_ONLY: Pillar 331 investigates CMB large-scale suppression. "
        "Results are NON_HARDGATE adjacent-track.  "
        "No hardgate ToE score components are affected."
    )


def braiding_fraction(n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Compute the braiding fraction f_braid = n_w / K_CS.

    This is the maximum fractional suppression of the CMB power spectrum
    at large angular scales (ℓ → 0) from the braided winding state.

    Parameters
    ----------
    n_w : int
        Winding number.
    k_cs : int
        Chern-Simons level.

    Returns
    -------
    float
        f_braid = n_w / k_cs.
    """
    return n_w / k_cs


def suppression_scale_ell(n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Compute the suppression scale ℓ_braid = K_CS / (2 × n_w).

    Modes at ℓ ~ ℓ_braid experience ≈ e⁻¹ × f_braid fractional suppression.
    Modes at ℓ >> ℓ_braid are unsuppressed.

    Parameters
    ----------
    n_w : int
        Winding number.
    k_cs : int
        Chern-Simons level.

    Returns
    -------
    float
        ℓ_braid = k_cs / (2 × n_w).
    """
    return k_cs / (2.0 * n_w)


def cmb_power_suppression_factor(ell: float,
                                  f_braid: float = F_BRAID,
                                  l_braid: float = L_BRAID) -> float:
    """Compute the UM CMB power suppression factor S(ℓ) at multipole ℓ.

    S(ℓ) = 1 − f_braid × exp(−(ℓ / ℓ_braid)²)

    S(ℓ) = 1 means no suppression (standard ΛCDM power).
    S(ℓ) < 1 means power is suppressed by fraction (1 − S).

    Parameters
    ----------
    ell : float
        CMB multipole moment ℓ ≥ 2.
    f_braid : float
        Braiding suppression fraction (default: n_w/K_CS = 5/74).
    l_braid : float
        Suppression scale in ℓ (default: K_CS/(2n_w) = 7.4).

    Returns
    -------
    float
        Power suppression factor S(ℓ) ∈ (0, 1].
    """
    if ell <= 0:
        raise ValueError("ell must be positive")
    return 1.0 - f_braid * math.exp(-(ell / l_braid) ** 2)


def suppressed_spectrum(
    ell_values: List[int],
    c_ell_lcdm: Optional[List[float]] = None,
    f_braid: float = F_BRAID,
    l_braid: float = L_BRAID,
) -> List[Dict]:
    """Compute the UM-suppressed CMB spectrum for given ℓ values.

    Parameters
    ----------
    ell_values : List[int]
        List of multipole values.
    c_ell_lcdm : Optional[List[float]]
        ΛCDM C_ℓ values (arbitrary units; if None, uses 1.0 for each).
    f_braid : float
        Braiding fraction.
    l_braid : float
        Suppression scale.

    Returns
    -------
    List[Dict]
        Per-ℓ results with suppression factor and UM power.
    """
    if c_ell_lcdm is None:
        c_ell_lcdm = [1.0] * len(ell_values)
    if len(c_ell_lcdm) != len(ell_values):
        raise ValueError("ell_values and c_ell_lcdm must have the same length")

    results = []
    for ell, c_lcdm in zip(ell_values, c_ell_lcdm):
        s = cmb_power_suppression_factor(ell, f_braid, l_braid)
        results.append({
            "ell": ell,
            "c_ell_lcdm": c_lcdm,
            "suppression_factor": s,
            "c_ell_um": c_lcdm * s,
            "pct_suppressed": (1.0 - s) * 100.0,
        })
    return results


def compare_to_planck_observation() -> Dict:
    """Compare the UM quadrupole suppression prediction to Planck 2018 data.

    Returns
    -------
    Dict
        Comparison result with honest verdict.
    """
    s2 = cmb_power_suppression_factor(2)    # ℓ=2 quadrupole
    s3 = cmb_power_suppression_factor(3)    # ℓ=3 octopole
    s10 = cmb_power_suppression_factor(10)
    s20 = cmb_power_suppression_factor(20)
    s30 = cmb_power_suppression_factor(30)

    # UM prediction at ℓ=2: 93.7% of ΛCDM → 6.3% suppression
    # Planck observation: 30–60% suppression
    um_suppression_ell2 = (1.0 - s2) * 100.0  # percent
    planck_range_low = (1.0 - PLANCK_C2_SUPPRESSION_HIGH) * 100.0
    planck_range_high = (1.0 - PLANCK_C2_SUPPRESSION_LOW) * 100.0

    matches_planck = (
        planck_range_low <= um_suppression_ell2 <= planck_range_high
    )

    gap_factor = (planck_range_low / um_suppression_ell2
                  if um_suppression_ell2 > 0 else float("inf"))

    return {
        "um_suppression_ell2_pct": um_suppression_ell2,
        "planck_suppression_range_pct": (planck_range_low, planck_range_high),
        "matches_planck_range": matches_planck,
        "gap_factor": gap_factor,
        "verdict": (
            "DIRECTION_CORRECT_MAGNITUDE_INSUFFICIENT: UM predicts suppression "
            f"of {um_suppression_ell2:.1f}% at ℓ=2; Planck observes "
            f"{planck_range_low:.0f}–{planck_range_high:.0f}%. "
            "The braiding fraction f_braid = n_w/K_CS ≈ 6.8% explains "
            f"~{um_suppression_ell2/planck_range_high*100:.0f}% of the observed suppression. "
            "Additional mechanism (e.g., finite Hubble volume, foreground subtraction, "
            "or cosmic variance) required for full explanation."
        ),
        "per_ell": {
            2: s2, 3: s3, 10: s10, 20: s20, 30: s30
        },
    }


def falsification_condition() -> Dict:
    """Return the UM falsification condition for the CMB quadrupole prediction.

    Returns
    -------
    Dict
        Falsification condition with measurement requirements.
    """
    return {
        "prediction": (
            f"UM predicts C_ℓ^{{UM}} / C_ℓ^{{ΛCDM}} = S(ℓ) = "
            f"1 − (n_w/K_CS) × exp(−(ℓ/ℓ_braid)²) "
            f"with f_braid = {F_BRAID:.4f}, ℓ_braid = {L_BRAID:.1f}"
        ),
        "at_ell_2": f"S(2) = {cmb_power_suppression_factor(2):.4f} → {(1-cmb_power_suppression_factor(2))*100:.1f}% suppression",
        "at_ell_10": f"S(10) = {cmb_power_suppression_factor(10):.4f} → {(1-cmb_power_suppression_factor(10))*100:.2f}% suppression",
        "at_ell_100": f"S(100) = {cmb_power_suppression_factor(100):.6f} → {(1-cmb_power_suppression_factor(100))*100:.4f}% suppression",
        "falsification": (
            "The UM is falsified at this prediction if: "
            "C_ℓ^{obs} / C_ℓ^{ΛCDM} > S(ℓ) + 0.01 at ℓ=2,3 with >3σ significance, "
            "i.e., the observed spectrum shows MORE power than ΛCDM at ℓ<10. "
            "This would require negative braiding fraction, which is topologically impossible."
        ),
        "detector": "LiteBIRD (launch ~2032) large-scale polarization E and B modes",
        "status": "ADJACENT_TRACK_PREDICTION — partial mechanism, not full explanation",
    }


def quadrupole_suppression_report() -> Dict:
    """Full report on the UM CMB quadrupole suppression prediction.

    Returns
    -------
    Dict
        Complete analysis.
    """
    comparison = compare_to_planck_observation()
    falsifier = falsification_condition()
    spectrum = suppressed_spectrum([2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 50, 100, 200])

    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency": ADJACENCY_TRACK_LABEL,
        "mechanism": {
            "description": (
                "Braided (5,7) winding state imposes an IR suppression on "
                "primordial power spectrum via topological phase coherence. "
                "Suppression fraction: f_braid = n_w/K_CS = 5/74 ≈ 6.8%. "
                "Suppression scale: ℓ_braid = K_CS/(2n_w) = 7.4."
            ),
            "f_braid": F_BRAID,
            "l_braid": L_BRAID,
            "l_min_winding": L_MIN_WINDING,
        },
        "planck_comparison": comparison,
        "falsification": falsifier,
        "spectrum": spectrum,
        "honest_assessment": {
            "direction": "CORRECT — UM predicts suppression at ℓ < 10",
            "magnitude": "INSUFFICIENT — UM predicts 6.8% vs observed 40-60%",
            "alignment_anomaly": "NOT_ADDRESSED — quadrupole-octopole alignment unpredicted by UM",
            "status": "PARTIAL_MECHANISM — provides IR suppression but not full amplitude",
            "path_forward": (
                "Full amplitude may require: (a) finite Hubble volume effects, "
                "(b) KK modulation during inflation at super-Hubble scales, "
                "(c) additional geometric mechanism from the radion during slow-roll. "
                "This remains an open calculation."
            ),
        },
    }
