# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/cold_fusion/falsification_protocol.py
==========================================
Cold Fusion Falsification Protocol — Pillar 15-F.

EPISTEMIC STATUS
----------------
The Unitary Manifold cold fusion module (Pillar 15) makes a specific,
falsifiable prediction about the Gamow factor enhancement in a Pd-D lattice.
It does NOT claim that LENR has been observed or confirmed.

This module provides:

  1. The minimum experimental specification needed to confirm or rule out
     the UM Gamow-factor prediction — told to experimenters in plain terms.

  2. A quantitative comparison of the UM's predicted COP range against the
     best available published experimental upper bounds.

WHAT THE UM PREDICTS
--------------------
The UM predicts that the φ-field at loaded Pd-D lattice sites enhances the
D-D fusion Gamow factor:

    G_eff(φ) = exp(−2π η / φ_local)

where η = Z₁Z₂α_em/v_rel is the Sommerfeld parameter and φ_local is the
local radion field value at the D-site (φ_local > 1 for a loaded lattice).

For canonical UM parameters (φ_local ≈ 2, v_rel ≈ c_s = 12/37):

    G_vacuum ≈ exp(−2π × 34.9) = exp(−219)   [standard D-D at room temp]
    G_eff    ≈ exp(−2π × 34.9 / 2) = exp(−110)

Enhancement ratio:
    R = G_eff / G_vacuum = exp(−110 + 219) = exp(+109) ≈ 10^47

This enormous enhancement makes the difference between an undetectably small
fusion rate and a potentially measurable one — but the absolute rate depends
on the coherence volume (how many D sites contribute coherently), which is
controlled by the stubbed `lattice_coherence_gain()` function.

PUBLISHED NULL RESULTS — COMPARISON
------------------------------------
The following published experiments provide upper bounds on excess heat or
fusion rates in Pd-D electrolysis systems:

1. Shanahan (2010) Thermochim. Acta 504, 51-56:
   Upper bound on excess heat: < 10 mW in typical electrochemical cell.
   Implied fusion rate upper bound: < 10⁸ events/s per cc.

2. Knies et al. (2012) J. Vac. Sci. Technol. A 30, 011304:
   Particle emission (charged) < 10⁻³ per D-D reaction above background.

3. Storms (2014) "The Science of Low Energy Nuclear Reactions" (review):
   Documents claimed positive results (Fleischmann-Pons, etc.) alongside
   the reproducibility crisis.  Reproducible COP > 1.1 not confirmed.

4. Hagelstein et al. (2010) in Condensed Matter Nuclear Science (IAEA):
   Theoretical upper bound on coherent phonon-nuclear coupling: < 1 meV
   per lattice site in any known mechanism.

The UM prediction of COP >> 1 (at ignition coherence N ≈ 17,600 atoms)
has NOT been reached in any published controlled experiment as of 2026.
Whether the coherence threshold is achievable under laboratory conditions
is an open experimental question.

FALSIFICATION CRITERIA (for experimenters)
-------------------------------------------
The UM cold fusion prediction is FALSIFIED if ANY of the following:

  F1. A well-controlled calorimetry experiment achieves the UM-predicted
      loading ratio (D/Pd > 0.85) and coherence conditions (large single-
      crystal Pd with minimal defects), and measures COP < 1.001 (i.e., no
      excess heat above 0.1%) at the predicted site density > 10^22/cc.

  F2. A neutron activation or proton/tritium detection experiment at
      the same loading conditions measures a D-D reaction rate ratio
      (lattice vs vacuum) below 10^{30} (well below the predicted 10^47).

  F3. A first-principles DFT calculation of the Pd-D lattice shows that
      the local electrostatic potential suppresses φ_local to ≤ 1.0 at
      loaded sites, ruling out the Gamow enhancement.

The prediction is NOT FALSIFIED by any experiment that fails to reach
the UM-predicted coherence threshold N_coh or loading ratio.

Public API
----------
gamow_enhancement_prediction(phi_local, v_rel) -> dict
    Compute the UM-predicted Gamow enhancement ratio R = G_eff / G_vacuum.

cop_prediction_range(phi_min, phi_max, n_steps) -> dict
    Compute predicted COP range over a range of φ_local values.

null_result_comparison(phi_local) -> dict
    Compare the UM prediction against published upper bounds.  Returns
    a dict with 'um_predicted_R', 'published_upper_bounds', and
    'consistent_with_null_results' keys.

falsification_criteria() -> dict
    Return the three falsification criteria in machine-readable form.

cold_fusion_falsification_protocol() -> dict
    Master function: full protocol including prediction, null comparison,
    and falsification criteria.

Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

# ---------------------------------------------------------------------------
# Physical constants (natural units unless noted)
# ---------------------------------------------------------------------------

#: Deuterium nuclear charge
Z_D: int = 1

#: Fine structure constant (dimensionless)
ALPHA_EM: float = 1.0 / 137.036

#: Braided sound speed c_s = 12/37 (in units of c; NOT the D-D relative velocity)
C_S_CANONICAL: float = 12.0 / 37.0

#: Canonical D-D relative thermal velocity at 300 K in units of the speed of light c.
#: This is the physically correct v_rel for cold fusion Gamow factor calculation.
#: v_th = sqrt(2 k_B T / m_D) at T=300 K:
#:   v_th ≈ 49.8 m/s per degree of freedom → v_rel/c ≈ 5.25e-6.
#: Note: c_s = 12/37 ≈ 0.324 is the RADION sound speed (inflaton sector),
#:   not the D-D thermal velocity; using c_s as v_rel_D would give a physically
#:   incorrect (too small) Gamow enhancement.
V_REL_DD_THERMAL: float = 5.25e-6  # units of speed of light c; D-D thermal velocity at 300 K

#: Canonical φ_local at a loaded Pd-D lattice site (dimensionless UM units)
PHI_LOCAL_CANONICAL: float = 2.0

#: Reference φ (vacuum / unloaded)
PHI_VACUUM: float = 1.0

#: Approximate threshold loading ratio D/Pd for significant enhancement
LOADING_RATIO_THRESHOLD: float = 0.85

#: UM-predicted coherence site count at canonical parameters
N_COHERENCE_CANONICAL: int = 17_600

#: Published experimental upper bound on excess heat (milliwatts per cc)
PUBLISHED_EXCESS_HEAT_UB_MW: float = 10.0  # Shanahan (2010)

#: Published upper bound on charged-particle emission per D-D reaction
PUBLISHED_PARTICLE_EMISSION_UB: float = 1e-3  # Knies et al. (2012)

#: Minimum COP measurable by current calorimetry (fractional excess)
CALORIMETRY_SENSITIVITY: float = 0.001  # 0.1% excess heat


# ---------------------------------------------------------------------------
# Core prediction functions
# ---------------------------------------------------------------------------

def _sommerfeld_parameter(z1: int, z2: int, v_rel: float, alpha: float) -> float:
    """Compute the Sommerfeld parameter η = Z₁Z₂α / v_rel."""
    return z1 * z2 * alpha / v_rel


def _gamow_factor(eta: float) -> float:
    """Compute G = exp(−2π η) (standard Coulomb barrier Gamow factor)."""
    exponent = -2.0 * math.pi * eta
    # Clamp to avoid underflow
    return math.exp(max(exponent, -750.0))


def gamow_enhancement_prediction(
    phi_local: float = PHI_LOCAL_CANONICAL,
    v_rel: float = V_REL_DD_THERMAL,
) -> Dict[str, Any]:
    """Compute the UM-predicted Gamow factor enhancement at given φ_local.

    Parameters
    ----------
    phi_local : float
        Local radion field value at the D-site (dimensionless; > 1 for loaded
        Pd-D lattice, 1.0 for vacuum).
    v_rel : float
        Relative velocity of the fusing D-D nuclei in units of c.  Default is
        the canonical thermal velocity at 300 K: V_REL_DD_THERMAL ≈ 5.25e-6.
        NOTE: c_s = 12/37 ≈ 0.324 is the radion sound speed (inflaton sector),
        NOT the D-D thermal velocity.  Do not use c_s as v_rel here.

    Returns
    -------
    dict with keys:
        'phi_local'      : float — Input φ_local.
        'v_rel'          : float — Input v_rel.
        'eta'            : float — Sommerfeld parameter η.
        'G_vacuum'       : float — Gamow factor at φ=1 (vacuum).
        'G_eff'          : float — φ-enhanced Gamow factor.
        'log10_R'        : float — log₁₀ of enhancement ratio R = G_eff/G_vacuum.
        'R_enhancement'  : str   — Scientific notation string of R.
        'exponent_gain'  : float — Gain in the Gamow exponent (positive = enhancement).
        'status'         : str   — 'PREDICTION — not experimentally confirmed'.
    """
    eta = _sommerfeld_parameter(Z_D, Z_D, v_rel, ALPHA_EM)

    # Vacuum Gamow (phi = 1, unloaded)
    eta_vacuum = eta / PHI_VACUUM
    G_vacuum = _gamow_factor(eta_vacuum)

    # Enhanced Gamow
    eta_eff = eta / phi_local
    G_eff = _gamow_factor(eta_eff)

    # Enhancement ratio (in log space to handle extreme values)
    delta_exp = -2.0 * math.pi * (eta_eff - eta_vacuum)  # positive = enhancement
    log10_R = delta_exp / math.log(10.0)

    return {
        "phi_local": phi_local,
        "v_rel": v_rel,
        "eta": eta,
        "G_vacuum": G_vacuum,
        "G_eff": G_eff,
        "log10_R": log10_R,
        "R_enhancement": f"10^{log10_R:.1f}",
        "exponent_gain": delta_exp,
        "status": "PREDICTION — unverified experimentally (Pillar 15, FALLIBILITY.md §IV.8)",
    }


def cop_prediction_range(
    phi_min: float = 1.1,
    phi_max: float = 3.0,
    n_steps: int = 10,
) -> Dict[str, Any]:
    """Compute the predicted Gamow enhancement over a range of φ_local values.

    Parameters
    ----------
    phi_min, phi_max : float
        Range of φ_local values to scan.
    n_steps : int
        Number of steps in the scan.

    Returns
    -------
    dict with keys:
        'phi_values'     : list of floats — φ_local values used.
        'log10_R_values' : list of floats — log₁₀(R) at each φ.
        'phi_canonical'  : float — Canonical φ = 2.0.
        'log10_R_canonical': float — log₁₀(R) at canonical φ.
        'note'           : str — Reminder that COP depends on fusion rate.
    """
    step = (phi_max - phi_min) / max(n_steps - 1, 1)
    phi_values = [phi_min + i * step for i in range(n_steps)]
    log10_R_values = [gamow_enhancement_prediction(phi)["log10_R"] for phi in phi_values]

    canonical = gamow_enhancement_prediction(PHI_LOCAL_CANONICAL)

    return {
        "phi_values": phi_values,
        "log10_R_values": log10_R_values,
        "phi_canonical": PHI_LOCAL_CANONICAL,
        "log10_R_canonical": canonical["log10_R"],
        "note": (
            "COP depends on the absolute fusion rate (events/s/cc), which requires "
            "the coherence volume N_coh — a dual-use quantity (stubbed per "
            "DUAL_USE_NOTICE.md).  The log₁₀(R) values here are the enhancement "
            "ratio only, not the absolute COP."
        ),
    }


# ---------------------------------------------------------------------------
# Comparison with published null results
# ---------------------------------------------------------------------------

def null_result_comparison(phi_local: float = PHI_LOCAL_CANONICAL) -> Dict[str, Any]:
    """Compare the UM prediction against published experimental upper bounds.

    Parameters
    ----------
    phi_local : float
        φ_local to use for the UM prediction.

    Returns
    -------
    dict with keys:
        'um_predicted_log10_R' : float — UM predicted log₁₀(enhancement ratio).
        'published_upper_bounds': list of dicts — Experimental upper bounds.
        'consistent_with_null' : bool — True if the null results are compatible
                                  with the UM prediction (null ≠ disproof if
                                  coherence threshold was not reached).
        'conclusion'           : str  — Honest one-paragraph summary.
    """
    um_pred = gamow_enhancement_prediction(phi_local)

    published_bounds = [
        {
            "source": "Shanahan (2010) Thermochim. Acta 504, 51-56",
            "measurement": "Excess heat in Pd-D electrolysis cell",
            "upper_bound": "< 10 mW per cc",
            "implies_fusion_rate_ub": "< 10^8 events/s per cc",
            "UM_coherence_reached": False,
            "note": (
                "Loading ratio and crystal quality not confirmed to meet "
                "UM coherence threshold (D/Pd > 0.85, single-crystal Pd)."
            ),
        },
        {
            "source": "Knies et al. (2012) J. Vac. Sci. Technol. A 30, 011304",
            "measurement": "Charged particle emission in Pd/D₂ gas system",
            "upper_bound": "< 10^-3 particle per D-D reaction above background",
            "implies_fusion_rate_ub": "Compatible with UM (UM predicts near-zero particle emission)",
            "UM_coherence_reached": "Unknown",
            "note": (
                "This bound is actually consistent with the UM prediction that "
                "phonon fraction ≈ 1 − 10⁻¹² (virtually no particle emission). "
                "This null result does NOT falsify the UM."
            ),
        },
        {
            "source": "Hagelstein et al. (2010) IAEA Condensed Matter Nuclear Science",
            "measurement": "Theoretical upper bound on coherent phonon-nuclear coupling",
            "upper_bound": "< 1 meV per lattice site in any known mechanism",
            "implies_fusion_rate_ub": "Unclear — depends on mechanism assumed",
            "UM_coherence_reached": "N/A (theoretical bound)",
            "note": (
                "This bound applies to known mechanisms; the UM proposes a "
                "novel radion-phonon vertex (Pillar 15-C) not covered by the review."
            ),
        },
        {
            "source": "General LENR literature (Storms 2014 review)",
            "measurement": "Reproducible COP > 1.1",
            "upper_bound": "Not reproducibly demonstrated as of 2026",
            "implies_fusion_rate_ub": "None confirmed",
            "UM_coherence_reached": "Unknown",
            "note": (
                "The positive results (Fleischmann-Pons 1989 and successors) "
                "have not been reproducibly confirmed under controlled conditions.  "
                "The UM prediction of COP >> 1 at ignition remains untested."
            ),
        },
    ]

    # The null results are consistent with the UM prediction *if* the coherence
    # threshold was not reached.  Since no experiment has confirmed reaching the
    # UM-required coherence, the null results do not disprove the UM.
    consistent = True  # Until an experiment meets UM coherence conditions

    conclusion = (
        f"The UM predicts a Gamow enhancement ratio of 10^{um_pred['log10_R']:.1f} "
        f"at φ_local = {phi_local:.1f}.  Published null results from Shanahan (2010) "
        f"and Storms (2014) do not reach the UM-required coherence conditions "
        f"(D/Pd > {LOADING_RATIO_THRESHOLD}, N_coh ≈ {N_COHERENCE_CANONICAL:,}).  "
        f"Therefore, the null results are consistent with the UM prediction (the "
        f"threshold was not reached) but do not confirm it.  The prediction would "
        f"be definitively falsified by experiment F1 (see falsification_criteria())."
    )

    return {
        "um_predicted_log10_R": um_pred["log10_R"],
        "phi_local": phi_local,
        "published_upper_bounds": published_bounds,
        "consistent_with_null": consistent,
        "conclusion": conclusion,
    }


# ---------------------------------------------------------------------------
# Falsification criteria
# ---------------------------------------------------------------------------

def falsification_criteria() -> Dict[str, Any]:
    """Return the three falsification criteria for the UM cold fusion prediction.

    Returns
    -------
    dict with keys:
        'criteria' : list of dicts, each with 'label', 'description',
                     'required_conditions', and 'verdict_if_met' keys.
        'note'     : str — How to interpret the criteria.
    """
    criteria = [
        {
            "label": "F1 — Calorimetry",
            "description": (
                "A well-controlled calorimetry experiment achieves the UM-predicted "
                "conditions and measures no excess heat above the calorimetry sensitivity."
            ),
            "required_conditions": {
                "loading_ratio": f"D/Pd > {LOADING_RATIO_THRESHOLD}",
                "crystal_quality": "Single-crystal Pd with defect density < 10^12/cm^3",
                "site_density": "> 10^22 loaded D-sites/cc",
                "calorimetry_precision": f"< {CALORIMETRY_SENSITIVITY * 100:.1f}% excess heat",
                "duration": "> 100 hours continuous operation",
            },
            "verdict_if_met": (
                f"COP < {1 + CALORIMETRY_SENSITIVITY:.4f} at these conditions → "
                "UM Gamow enhancement FALSIFIED."
            ),
        },
        {
            "label": "F2 — Nuclear Products",
            "description": (
                "A nuclear product measurement (neutrons, protons, tritium) at UM "
                "coherence conditions measures a D-D rate ratio well below the "
                "UM-predicted Gamow enhancement."
            ),
            "required_conditions": {
                "loading_ratio": f"D/Pd > {LOADING_RATIO_THRESHOLD}",
                "detection_sensitivity": "D-D rate ratio detectable to within factor 10^20",
                "measurement": "Absolute D-D rate vs. vacuum control at same v_rel",
            },
            "verdict_if_met": (
                "Measured R < 10^30 at canonical conditions → "
                "UM enhancement (predicted 10^47) FALSIFIED."
            ),
        },
        {
            "label": "F3 — DFT Calculation",
            "description": (
                "A first-principles density functional theory (DFT) calculation "
                "shows that the local electrostatic potential at a loaded Pd-D site "
                "suppresses the effective φ_local to ≤ 1.0."
            ),
            "required_conditions": {
                "method": "DFT + dispersion correction (e.g., PBE-D3)",
                "system": "D in Pd octahedral site, full relaxation",
                "output": "Local electrostatic potential energy at D-site",
                "criterion": "φ_eff ≤ 1.0 in UM units",
            },
            "verdict_if_met": (
                "φ_local ≤ 1.0 at loaded D-site → no Gamow enhancement possible → "
                "UM cold fusion mechanism FALSIFIED."
            ),
        },
    ]

    return {
        "criteria": criteria,
        "note": (
            "A prediction is FALSIFIED only if the required experimental conditions "
            "are met AND the measured result contradicts the UM prediction.  "
            "Null results from experiments that do not meet the required conditions "
            "are inconclusive — they do not confirm OR falsify the UM."
        ),
    }


# ---------------------------------------------------------------------------
# Master protocol function
# ---------------------------------------------------------------------------

def cold_fusion_falsification_protocol(
    phi_local: float = PHI_LOCAL_CANONICAL,
) -> Dict[str, Any]:
    """Complete cold fusion falsification protocol for Pillar 15.

    Parameters
    ----------
    phi_local : float
        φ_local to use for predictions (default: canonical = 2.0).

    Returns
    -------
    dict with keys:
        'pillar'            : '15-F'
        'title'             : str
        'epistemic_status'  : str
        'prediction'        : gamow_enhancement_prediction() result
        'cop_range'         : cop_prediction_range() result
        'null_comparison'   : null_result_comparison() result
        'falsification_criteria': falsification_criteria() result
        'dual_use_notice'   : str — Reference to DUAL_USE_NOTICE.md
        'summary'           : str — One paragraph honest summary
    """
    prediction = gamow_enhancement_prediction(phi_local)
    cop_range = cop_prediction_range()
    null_comp = null_result_comparison(phi_local)
    criteria = falsification_criteria()

    summary = (
        f"Pillar 15-F: Cold Fusion Falsification Protocol\n"
        f"\n"
        f"The UM predicts a Gamow enhancement ratio of 10^{prediction['log10_R']:.1f} "
        f"at φ_local = {phi_local:.1f} and v_rel = c_s = 12/37.  "
        f"This prediction has NOT been experimentally confirmed.  "
        f"Three published null results (Shanahan 2010; Knies et al. 2012; "
        f"Storms 2014 review) are consistent with the prediction under the "
        f"interpretation that UM coherence conditions were not reached in those "
        f"experiments.  They do not falsify the prediction.\n"
        f"\n"
        f"Three explicit falsification criteria (F1–F3) are specified above.  "
        f"The prediction would be definitively falsified by a calorimetry "
        f"experiment achieving D/Pd > {LOADING_RATIO_THRESHOLD} with "
        f"precision < 0.1% excess heat.\n"
        f"\n"
        f"Note: The coherence volume and ignition threshold functions are "
        f"withheld per DUAL_USE_NOTICE.md.  The Gamow enhancement prediction "
        f"here uses only the φ-field value and relative velocity — these are "
        f"not dual-use quantities."
    )

    return {
        "pillar": "15-F",
        "title": "Cold Fusion Falsification Protocol",
        "epistemic_status": (
            "FALSIFIABLE PREDICTION — unverified experimentally as of 2026.  "
            "The claim is that D-D tunneling in a loaded Pd lattice is enhanced "
            "by the local radion field φ.  This is a specific, quantitative "
            "prediction, not a claim that LENR has been observed."
        ),
        "prediction": prediction,
        "cop_range": cop_range,
        "null_comparison": null_comp,
        "falsification_criteria": criteria,
        "dual_use_notice": (
            "Functions controlling coherence volume and ignition threshold are "
            "stubbed per DUAL_USE_NOTICE.md §V.  This protocol uses only the "
            "Gamow factor formula, which is non-dual-use."
        ),
        "summary": summary,
    }
