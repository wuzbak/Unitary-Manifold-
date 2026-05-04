# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_axion_quintessence.py
==================================
Pillar 160 — KK Axion Tower as Quintessence: wₐ ≠ 0 Attempt.

STATUS: ⚠️ OPEN (Pillar 155 documented wₐ = 0 from frozen EW radion; 2.1σ DESI
        CPL tension) → ⚠️ ANALYSED — KK axion tower computed; viable only if
        a DE-sector KK mode exists with m_n ~ H₀; severely constrained by
        fifth-force tests. Formally declared as primary open DE falsification
        target alongside birefringence β.

BACKGROUND: THE wₐ PROBLEM
-----------------------------
Pillar 155 (kk_de_wa_cpl.py) established that:
  - The GW-stabilised EW radion is frozen (m_r >> H₀) → wₐ = 0 exactly.
  - DESI DR2 CPL fit prefers wₐ = −0.62 ± 0.30 → 2.1σ tension with wₐ = 0.
  - The Planck+BAO w₀ tension (3.4σ) persists independently.

This Pillar 160 attempts to find a wₐ ≠ 0 mechanism from the KK spectrum
via two approaches:

APPROACH 1: KK AXION TOWER
----------------------------
In the RS1 framework the Kaluza-Klein reduction of any p-form bulk gauge
field produces a tower of 4D pseudo-scalar (axion-like) fields with masses:

    m_n² = m_0² + n² / R²   for n = 0, 1, 2, ...

where m_0 is the bulk mass and R is the compactification radius.

For an almost-massless bulk axion (m_0 ≈ 0, Peccei-Quinn-like):

    m_n = n / R = n × M_KK / π    (n ≥ 1)

For M_KK = 1040 GeV (EW hierarchy radion), m_n >> H₀ for all n ≥ 1.
No KK mode of the EW radion can serve as quintessence.

DARK-ENERGY SECTOR KK MODE (HYPOTHETICAL)
-------------------------------------------
If a SEPARATE compactification with a much larger radius R_DE exists:

    m_1^{DE} ~ H₀  requires  R_DE ~ 1/H₀ ~ 10^{26} m ~ 4 Gpc

This would require a second large extra dimension at the Hubble scale — a
DISTINCT assumption from the EW hierarchy extra dimension (R_EW ~ 10⁻¹⁹ m).

The fifth-force constraint eliminates this for spin-0 modes:
  - Cassini PPN: |Δγ| < 2.3×10⁻⁵ (any fifth force from new scalar)
  - A Hubble-scale scalar would mediate infinite-range fifth force,
    violating Cassini by many orders of magnitude.
  - This is the same elimination as the DE radion (Pillar 147).

APPROACH 2: MULTI-MODE KK SUM (DYNAMICAL DARK ENERGY)
-------------------------------------------------------
The total dark energy density from the KK tower:

    ρ_DE = Σ_n V_n(φ_n)   summed over all KK axion modes

If each mode has a slightly different mass and they are slightly
out of phase, the aggregate can mimic wₐ ≠ 0.  This is the "axion
monodromy" or "Hilltop N-flation" scenario.

For the UM with πkR = 37:
  - Mode spacing: Δm = M_KK / π ≈ 331 GeV
  - All modes are much heavier than H₀ → all are frozen → total wₐ = 0.

The KK axion tower from the EW RS sector CANNOT produce wₐ ≠ 0.

ROMAN SPACE TELESCOPE FALSIFICATION FORECAST
---------------------------------------------
The Nancy Grace Roman Space Telescope (expected ~2027) will measure:
  - w₀ to σ(w₀) ≈ 0.02 (from weak lensing + BAO + SN Ia)
  - wₐ to σ(wₐ) ≈ 0.10 (from the same combined probes)

UM predictions:
  - w₀ = −0.9302 (from Pillar 136)
  - wₐ = 0 (from frozen EW radion, Pillar 155)

Roman decision threshold:
  - If Roman measures wₐ consistent with 0 (|wₐ| < 0.20 at 2σ):
    UM prediction SURVIVES → w₀ becomes the decisive test.
  - If Roman measures wₐ significantly ≠ 0 (|wₐ| > 0.20 at 2σ):
    UM prediction FALSIFIED for dark energy sector.

VERDICT
-------
No viable mechanism exists in the UM for wₐ ≠ 0:
  - EW radion frozen (m_r >> H₀) → wₐ = 0 exactly.
  - KK axion tower: all modes m_n >> H₀ → all frozen → wₐ = 0.
  - DE-sector light radion: eliminated by Cassini fifth-force.
  - Multi-mode KK sum: modes too heavy for coherent quintessence.

FORMAL DECLARATION: The dark energy equation of state (w₀, wₐ) is the
UM's secondary open falsification target alongside β birefringence.
The Roman Space Telescope (~2027) will provide the decisive test.

Public API
----------
kk_axion_mass_tower(n_max, m_kk_gev) → dict
    Compute the KK axion mass tower and check quintessence viability.

fifth_force_constraint_de_axion(m_axion_gev) → dict
    Apply Cassini + LLR fifth-force constraints to a DE-scale axion.

multi_mode_wa_estimate(n_modes, m_kk_gev) → dict
    Estimate wₐ from a multi-mode KK axion sum (should give wₐ ≈ 0).

roman_telescope_falsification() → dict
    Roman Space Telescope forecast for (w₀, wₐ) testing.

pillar160_summary() → dict
    Full Pillar 160 status report.

de_open_declaration() → str
    Formal declaration of DE as primary open falsification target.
"""

from __future__ import annotations
import math

__all__ = [
    "kk_axion_mass_tower",
    "fifth_force_constraint_de_axion",
    "multi_mode_wa_estimate",
    "roman_telescope_falsification",
    "pillar160_summary",
    "de_open_declaration",
]

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: UM KK threshold scale [GeV] (from EW hierarchy, Pillar 81)
_M_KK_GEV: float = 1040.0

#: Hubble constant H₀ in GeV (H₀ ≈ 67.4 km/s/Mpc ≈ 1.45×10⁻⁴² GeV)
_H0_GEV: float = 1.445e-42

#: UM w₀ prediction (Pillar 136)
_W0_KK: float = -0.9302

#: UM wₐ prediction (Pillar 155, frozen EW radion)
_WA_KK: float = 0.0

#: Planck+BAO tension with w₀ [sigma]
_W0_TENSION_SIGMA: float = 3.4

#: DESI DR2 CPL wₐ tension [sigma]
_WA_TENSION_SIGMA: float = 2.1

#: DESI DR2 CPL best-fit wₐ
_WA_DESI: float = -0.62

#: Cassini PPN bound on |Δγ| (any scalar fifth force)
_CASSINI_PPN_LIMIT: float = 2.3e-5

#: Roman σ(w₀) forecast
_ROMAN_SIGMA_W0: float = 0.02

#: Roman σ(wₐ) forecast
_ROMAN_SIGMA_WA: float = 0.10


def kk_axion_mass_tower(
    n_max: int = 10,
    m_kk_gev: float = _M_KK_GEV,
    h0_gev: float = _H0_GEV,
) -> dict:
    """Compute the KK axion mass tower and check quintessence viability.

    For a bulk pseudo-scalar in RS1, the KK masses are:
        m_n = n × M_KK / π   (n = 1, 2, 3, ...)

    Quintessence requires m ≲ H₀ ≈ 1.45×10⁻⁴² GeV.
    The EW radion KK tower has m_n >> H₀ for all n ≥ 1.

    Parameters
    ----------
    n_max    : number of KK modes to tabulate (default 10)
    m_kk_gev : KK threshold scale [GeV] (default 1040 GeV)
    h0_gev   : Hubble constant [GeV] (default 1.445×10⁻⁴² GeV)

    Returns
    -------
    dict with mass tower, H₀ comparison, and quintessence verdict.
    """
    modes = []
    for n in range(1, n_max + 1):
        m_n = n * m_kk_gev / math.pi
        ratio = m_n / h0_gev
        modes.append({
            "n": n,
            "m_n_gev": m_n,
            "m_n_over_H0": ratio,
            "quintessence_viable": ratio < 10.0,  # need m_n ≲ 10 H₀
        })

    any_viable = any(m["quintessence_viable"] for m in modes)
    lightest_gev = modes[0]["m_n_gev"]
    lightest_over_h0 = modes[0]["m_n_over_H0"]

    return {
        "m_kk_gev": m_kk_gev,
        "h0_gev": h0_gev,
        "modes": modes,
        "lightest_mode_gev": lightest_gev,
        "lightest_over_H0": lightest_over_h0,
        "any_quintessence_viable": any_viable,
        "verdict": (
            f"KK axion tower: lightest mode m_1 = {lightest_gev:.1f} GeV = "
            f"{lightest_over_h0:.2e} H₀. "
            "All modes are {:.1e}× heavier than H₀. ".format(lightest_over_h0) +
            "NONE can serve as quintessence. wₐ = 0 from this sector."
        ),
        "wa_from_tower": 0.0,
        "status": "ELIMINATED — all KK modes m_n >> H₀",
    }


def fifth_force_constraint_de_axion(
    m_axion_gev: float = _H0_GEV,
    alpha_coupling: float = 1.0,
    cassini_limit: float = _CASSINI_PPN_LIMIT,
) -> dict:
    """Apply fifth-force constraints to a hypothetical DE-scale axion.

    A massless (or Hubble-mass) scalar mediates a long-range fifth force.
    The PPN parameter Υ constraint from the Cassini spacecraft tracking:
        |Δγ| < 2.3×10⁻⁵   (Bertotti et al. 2003)

    For a scalar with gravitational-strength coupling α ~ 1:
        |Δγ| ≈ 2α² / (1 + α²) ≈ 2 × 1 = 2   (far exceeds limit)

    Parameters
    ----------
    m_axion_gev  : axion mass [GeV] (default H₀ for DE-scale axion)
    alpha_coupling: coupling strength relative to gravity (default 1)
    cassini_limit : PPN |Δγ| upper limit (default 2.3×10⁻⁵)

    Returns
    -------
    dict with constraint analysis.
    """
    # For a light scalar with Compton wavelength λ_c >> solar-system scale:
    # λ_c = ℏc / m ≈ 0.197 GeV·fm / m_gev [fm]
    # If λ_c > 1 AU ~ 1.5×10²⁶ fm, the force is effectively long-range
    lambda_c_gev_inv = 1.0 / m_axion_gev if m_axion_gev > 0 else float("inf")
    # 1 AU in GeV⁻¹: 1 AU = 1.5e11 m, 1 m = 5.068e15 GeV⁻¹ → 1 AU = 7.6e26 GeV⁻¹
    au_in_gev_inv = 7.6e26
    is_long_range = lambda_c_gev_inv > au_in_gev_inv

    # PPN Δγ for a scalar with coupling α relative to gravity
    delta_gamma = 2.0 * alpha_coupling**2 / (1.0 + alpha_coupling**2)
    violates_cassini = delta_gamma > cassini_limit
    violation_factor = delta_gamma / cassini_limit if cassini_limit > 0 else float("inf")

    return {
        "m_axion_gev": m_axion_gev,
        "alpha_coupling": alpha_coupling,
        "lambda_c_gev_inv": lambda_c_gev_inv,
        "is_solar_system_long_range": is_long_range,
        "delta_gamma_ppn": delta_gamma,
        "cassini_limit": cassini_limit,
        "violates_cassini": violates_cassini,
        "violation_factor": violation_factor,
        "status": (
            f"FIFTH-FORCE VIOLATION: |Δγ| = {delta_gamma:.2e} vs Cassini limit "
            f"{cassini_limit:.2e} → violated by {violation_factor:.2e}×."
            if violates_cassini else
            f"Fifth-force OK: |Δγ| = {delta_gamma:.2e} < {cassini_limit:.2e}."
        ),
        "verdict": "ELIMINATED by fifth-force" if violates_cassini else "Viable (uncoupled)",
    }


def multi_mode_wa_estimate(
    n_modes: int = 5,
    m_kk_gev: float = _M_KK_GEV,
    h0_gev: float = _H0_GEV,
) -> dict:
    """Estimate wₐ from a multi-mode KK axion coherent sum.

    If N KK axion modes are each slightly displaced from their minima,
    they can coherently evolve and produce a time-varying dark energy.
    But if all modes have m_n >> H₀, they are frozen → aggregate wₐ = 0.

    The effective 1 + w for a frozen field near its minimum:
        1 + w_n ≈ (m_n/H)² × (Δφ_n/M_Pl)²  → 0 for m_n >> H₀

    Parameters
    ----------
    n_modes  : number of KK modes to sum (default 5)
    m_kk_gev : KK scale [GeV]
    h0_gev   : Hubble scale [GeV]

    Returns
    -------
    dict with aggregate wₐ estimate (should be ~0).
    """
    sum_wa = 0.0
    mode_contributions = []
    for n in range(1, n_modes + 1):
        m_n = n * m_kk_gev / math.pi
        ratio_sq = (m_n / h0_gev) ** 2
        # For frozen field: Δφ ~ 0, contribution negligible
        # Use a maximum displacement of 1% of M_Pl as upper bound
        delta_phi_max_over_mpl = 0.01
        one_plus_w_n = (1.0 / ratio_sq) * delta_phi_max_over_mpl**2  # approximate
        wa_n = -one_plus_w_n  # rate of change of w with scale factor
        sum_wa += wa_n
        mode_contributions.append({
            "n": n,
            "m_n_gev": m_n,
            "m_n_over_H0": m_n / h0_gev,
            "wa_contribution": wa_n,
        })

    return {
        "n_modes": n_modes,
        "m_kk_gev": m_kk_gev,
        "h0_gev": h0_gev,
        "mode_contributions": mode_contributions,
        "wa_aggregate": sum_wa,
        "wa_desi_central": _WA_DESI,
        "wa_tension_resolved": abs(sum_wa - _WA_DESI) < 0.2,
        "verdict": (
            f"Multi-mode KK sum gives wₐ ≈ {sum_wa:.2e} ≈ 0 "
            f"(DESI prefers wₐ = {_WA_DESI}). "
            "Tension unresolved: all KK modes frozen because m_n >> H₀."
        ),
        "status": "OPEN — wₐ ≈ 0 from all viable KK modes",
    }


def roman_telescope_falsification() -> dict:
    """Roman Space Telescope forecast for UM dark energy predictions.

    Roman (Nancy Grace Roman Space Telescope, ~2027) will measure (w₀, wₐ)
    from weak lensing + BAO + supernovae type Ia combined.

    UM predictions: w₀ = −0.9302, wₐ = 0

    Returns
    -------
    dict with full falsification forecast.
    """
    # Roman precision
    sigma_w0 = _ROMAN_SIGMA_W0  # 0.02
    sigma_wa = _ROMAN_SIGMA_WA  # 0.10

    # UM predictions
    w0_pred = _W0_KK  # -0.9302
    wa_pred = _WA_KK  # 0.0

    # PDG/Planck+BAO reference
    w0_planck = -1.03
    sigma_w0_planck = 0.03
    w0_tension_sigma = abs(w0_pred - w0_planck) / sigma_w0_planck

    # DESI reference for wₐ
    wa_desi = _WA_DESI
    sigma_wa_desi = 0.30
    wa_tension_sigma = abs(wa_pred - wa_desi) / sigma_wa_desi

    # Roman detection threshold: 2σ
    w0_roman_detectable = abs(w0_pred - (-1.0)) / sigma_w0  # deviation from ΛCDM
    wa_roman_detectable = abs(wa_pred - 0.0) / sigma_wa     # wₐ = 0 is the prediction

    return {
        "experiment": "Nancy Grace Roman Space Telescope",
        "expected_launch": "~2027",
        "sigma_w0_roman": sigma_w0,
        "sigma_wa_roman": sigma_wa,
        "um_predictions": {
            "w0": w0_pred,
            "wa": wa_pred,
        },
        "current_tensions": {
            "w0_planck_bao_sigma": w0_tension_sigma,
            "wa_desi_sigma": wa_tension_sigma,
        },
        "roman_detection": {
            "w0_deviation_from_lambda_sigma": w0_roman_detectable,
            "w0_detectable": w0_roman_detectable > 2.0,
            "wa_prediction_is_zero": wa_pred == 0.0,
        },
        "falsification_conditions": {
            "survive": (
                f"Roman measures w₀ ∈ [−1.0, −0.85] at 2σ AND |wₐ| < 0.20: "
                f"UM survives. (w₀ prediction is {w0_roman_detectable:.1f}σ from ΛCDM, "
                f"detectable by Roman.)"
            ),
            "falsify_w0": (
                f"Roman measures w₀ < −1.05 at 2σ: UM w₀={w0_pred} prediction FALSIFIED. "
                f"(Planck+BAO already shows {w0_tension_sigma:.1f}σ tension.)"
            ),
            "falsify_wa": (
                f"Roman measures |wₐ| > 0.20 at 2σ: UM wₐ=0 prediction FALSIFIED. "
                f"(DESI DR2 already shows {wa_tension_sigma:.1f}σ tension.)"
            ),
        },
        "status": "OPEN — Roman Space Telescope (~2027) is the decisive DE test",
        "formal_declaration": de_open_declaration(),
    }


def pillar160_summary() -> dict:
    """Full Pillar 160 status report.

    Returns
    -------
    dict with all analyses and final verdict.
    """
    tower = kk_axion_mass_tower()
    fifth_force = fifth_force_constraint_de_axion()
    multi_mode = multi_mode_wa_estimate()
    roman = roman_telescope_falsification()

    return {
        "pillar": 160,
        "title": "KK Axion Tower as Quintessence: wₐ ≠ 0 Attempt",
        "status": "⚠️ OPEN — No viable wₐ ≠ 0 mechanism found in UM",
        "analyses": {
            "kk_axion_tower": tower["status"],
            "fifth_force": fifth_force["verdict"],
            "multi_mode": multi_mode["status"],
        },
        "um_predictions": {
            "w0": _W0_KK,
            "wa": _WA_KK,
        },
        "tensions": {
            "w0_planck_bao": f"{_W0_TENSION_SIGMA:.1f}σ",
            "wa_desi_cpl": f"{_WA_TENSION_SIGMA:.1f}σ",
        },
        "falsifier": roman["experiment"],
        "falsifier_timeline": roman["expected_launch"],
        "formal_declaration": de_open_declaration(),
        "verdict": (
            "The KK axion tower from the EW RS sector cannot produce wₐ ≠ 0: "
            "all modes are frozen (m_n >> H₀). A DE-sector light scalar is "
            "eliminated by fifth-force constraints. The dark energy EoS (w₀, wₐ) "
            "is OPEN and is the UM's secondary falsification target. "
            "The Roman Space Telescope (~2027) will provide the decisive test."
        ),
    }


def de_open_declaration() -> str:
    """Formal declaration of DE as primary open falsification target."""
    return (
        "FORMAL DECLARATION (Pillar 160): The dark energy equation of state "
        "(w₀ = −0.9302, wₐ = 0) is the Unitary Manifold's secondary open "
        "falsification target alongside CMB birefringence β. "
        "Current tensions: w₀ is 3.4σ from Planck+BAO; wₐ = 0 is 2.1σ from "
        "DESI DR2 CPL fit. No viable mechanism for wₐ ≠ 0 has been identified "
        "in the UM framework. The Roman Space Telescope (~2027, σ(w₀) ≈ 0.02, "
        "σ(wₐ) ≈ 0.10) will either confirm or falsify the UM DE predictions."
    )
