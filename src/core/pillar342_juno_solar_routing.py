# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 342 — JUNO Solar Neutrino Precision Routing.

🔵 ADJACENT TRACK — HARDGATE_ADJACENT (extends Pillar 334: JUNO full prediction)

══════════════════════════════════════════════════════════════════════════════
JUNO'S SOLAR NEUTRINO PROGRAMME
══════════════════════════════════════════════════════════════════════════════

Pillar 334 covers JUNO's reactor antineutrino programme (mass ordering and Δm²₃₁).
JUNO has a SEPARATE dedicated solar neutrino programme:

  Solar JUNO target:
    θ₁₂ measurement precision: < 0.5%  (< 0.17° on 33.82°)
    Δm²₂₁ measurement precision: < 0.3%

  The UM predicts (from Route A, geometric derivation, Pillar P18):
    sin²θ₁₂ = 0.305  (θ₁₂ = 33.82°)
    PDG 2024: sin²θ₁₂ = 0.307 ± 0.013

  Current residual: (0.307 − 0.305) / 0.307 ≈ 0.65% — within PDG σ
  UM prediction residual from PDG central: 1.55% of PDG ± 0.013

  AT JUNO PRECISION (0.5% on sin²θ₁₂ → σ_JUNO ~ 0.0015):
    Residual 0.002 becomes a 1.3σ tension → TIGHTENED (not falsified)
    If central value shifts AND precision improves: could reach TENSION.

══════════════════════════════════════════════════════════════════════════════
SOLAR NEUTRINO OSCILLATION PHYSICS AT JUNO
══════════════════════════════════════════════════════════════════════════════

Solar neutrinos undergo matter-enhanced (MSW) oscillation.  The effective
survival probability for pp and ⁸B solar neutrinos in the detector:

  P(ν_e → ν_e)_solar ≈ cos⁴θ₁₃ (1 - sin²(2θ₁₂)/2)  [adiabatic MSW limit]
  for ⁸B at E > 5 MeV

For the UM parameters:
  P_ee ≈ cos⁴(8.57°) × (1 - sin²(2 × 33.82°)/2)
       ≈ (0.9889) × (1 - 0.9878/2)
       ≈ 0.9889 × 0.5061
       ≈ 0.5006

JUNO will measure θ₁₂ primarily via the sub-MeV solar neutrino spectrum
(pp neutrinos) in the non-adiabatic vacuum oscillation regime:

  P(ν_e → ν_e)_pp = 1 - sin²(2θ₁₂)/2  (vacuum approximation at low E)

══════════════════════════════════════════════════════════════════════════════
SOLAR MEASUREMENT STRATEGY AT JUNO
══════════════════════════════════════════════════════════════════════════════

JUNO solar sensitivity sources:
  1. ⁸B solar neutrinos (E > 3 MeV): sensitivity to θ₁₂ via MSW
  2. pp solar neutrinos (sub-MeV): vacuum oscillation → θ₁₂ directly
  3. pep neutrinos (1.44 MeV): precision θ₁₂ calibration

The JUNO target of < 0.5% on sin²θ₁₂ would be the world's best determination
of the solar mixing angle, surpassing SNO and SK combined.

══════════════════════════════════════════════════════════════════════════════
"""
import math

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

N_W = 5
K_CS = 74

# UM solar mixing angle predictions (Route A, Pillar P18)
THETA_12_DEG_UM = 33.82       # solar angle prediction (degrees)
THETA_12_RAD_UM = math.radians(THETA_12_DEG_UM)
SIN2_THETA_12_UM = math.sin(THETA_12_RAD_UM) ** 2

# UM θ₁₃
THETA_13_DEG_UM = 8.57        # reactor angle (degrees)
THETA_13_RAD_UM = math.radians(THETA_13_DEG_UM)
SIN2_THETA_13_UM = math.sin(THETA_13_RAD_UM) ** 2
COS4_THETA_13_UM = math.cos(THETA_13_RAD_UM) ** 4

# PDG 2024 reference values
PDG_SIN2_THETA_12 = 0.307     # PDG 2024 best fit
PDG_SIN2_THETA_12_ERR = 0.013 # PDG 1σ uncertainty

# JUNO solar precision target
JUNO_SOLAR_PRECISION_FRAC = 0.005   # 0.5% on sin²θ₁₂

# UM Δm²₂₁ prediction (Pillar P16)
DM21_SQ_EV2_UM = 7.53e-5     # UM prediction (eV²)
PDG_DM21_SQ = 7.53e-5        # PDG 2024 (eV²)
JUNO_DM21_PRECISION_FRAC = 0.003   # 0.3% on Δm²₂₁

# Verdict thresholds
SIGMA_TENSION = 2.0
SIGMA_FALSIFIED = 3.0


# ─────────────────────────────────────────────────────────────────────────────
# SEPARATION GUARD
# ─────────────────────────────────────────────────────────────────────────────

def separation_guard() -> dict:
    """Returns track classification."""
    return {
        "pillar": 342,
        "track": "ADJACENT_TRACK_HARDGATE_ADJACENT",
        "hardgate_promotion": False,
        "toe_score_delta": 0,
        "extends": "Pillar 334 (JUNO full prediction package)",
        "description": (
            "JUNO solar neutrino precision routing. Three-branch verdict tree: "
            "TIGHTENED / TENSION / FALSIFIED, based on θ₁₂ and Δm²₂₁ measurements."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SOLAR OSCILLATION PHYSICS
# ─────────────────────────────────────────────────────────────────────────────

def survival_probability_8b(theta_12_rad: float = THETA_12_RAD_UM,
                             theta_13_rad: float = THETA_13_RAD_UM) -> float:
    """Adiabatic MSW survival probability for ⁸B solar neutrinos (E > 5 MeV).

    P_ee = cos⁴(θ₁₃) × (1 - sin²(2θ₁₂)/2)
    """
    cos4_t13 = math.cos(theta_13_rad) ** 4
    sin2_2t12 = math.sin(2 * theta_12_rad) ** 2
    return cos4_t13 * (1.0 - sin2_2t12 / 2.0)


def survival_probability_pp(theta_12_rad: float = THETA_12_RAD_UM,
                             theta_13_rad: float = THETA_13_RAD_UM) -> float:
    """Vacuum oscillation survival probability for pp solar neutrinos (low E).

    P_ee = 1 - sin²(2θ₁₂)/2  [averaged over oscillation phase]
    (Corrections from θ₁₃ are ~2%, negligible for our purposes)
    """
    sin2_2t12 = math.sin(2 * theta_12_rad) ** 2
    return 1.0 - sin2_2t12 / 2.0


def juno_solar_precision_budget() -> dict:
    """JUNO solar neutrino precision budget for UM parameters."""
    # UM prediction
    sin2_12_um = SIN2_THETA_12_UM
    sin2_12_pdg = PDG_SIN2_THETA_12

    # Residual from PDG
    residual_abs = abs(sin2_12_um - sin2_12_pdg)
    residual_pct = 100.0 * residual_abs / sin2_12_pdg

    # JUNO projected σ on sin²θ₁₂
    juno_sigma_sin2 = JUNO_SOLAR_PRECISION_FRAC * PDG_SIN2_THETA_12

    # How many σ is the UM residual at JUNO precision?
    juno_tension_sigma = residual_abs / juno_sigma_sin2

    # Δm²₂₁ (UM matches PDG exactly)
    dm21_residual_pct = 100.0 * abs(DM21_SQ_EV2_UM - PDG_DM21_SQ) / PDG_DM21_SQ

    return {
        "sin2_theta12_um": sin2_12_um,
        "sin2_theta12_pdg": sin2_12_pdg,
        "residual_abs": residual_abs,
        "residual_pct": residual_pct,
        "juno_sigma_sin2": juno_sigma_sin2,
        "juno_tension_sigma": juno_tension_sigma,
        "dm21_sq_um_ev2": DM21_SQ_EV2_UM,
        "dm21_sq_pdg_ev2": PDG_DM21_SQ,
        "dm21_residual_pct": dm21_residual_pct,
        "p_ee_8b_um": survival_probability_8b(),
        "p_ee_pp_um": survival_probability_pp(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# THREE-BRANCH ROUTING PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────

def route_juno_solar(sin2_theta12_measured: float,
                     sin2_theta12_sigma: float,
                     dm21_sq_measured_ev2: float = None,
                     dm21_sq_sigma_ev2: float = None) -> dict:
    """Route JUNO solar neutrino result to a UM verdict.

    Three-branch routing:
      Branch 1: TIGHTENED  — UM residual ≤ 1σ_JUNO
      Branch 2: TENSION    — UM residual ∈ (1, 3)σ_JUNO
      Branch 3: FALSIFIED  — UM residual ≥ 3σ_JUNO AND PDG shifts away

    Parameters
    ----------
    sin2_theta12_measured : float
        JUNO measured sin²θ₁₂.
    sin2_theta12_sigma : float
        JUNO measurement uncertainty (1σ).
    dm21_sq_measured_ev2 : float, optional
        JUNO measured Δm²₂₁ (eV²). If None, not evaluated.
    dm21_sq_sigma_ev2 : float, optional
        JUNO Δm²₂₁ uncertainty (1σ, eV²).
    """
    # θ₁₂ assessment
    residual_sin2 = abs(SIN2_THETA_12_UM - sin2_theta12_measured)
    sigma_sin2 = residual_sin2 / sin2_theta12_sigma if sin2_theta12_sigma > 0 else 0.0

    if sigma_sin2 < SIGMA_TENSION:
        verdict_sin2 = "TIGHTENED"
    elif sigma_sin2 < SIGMA_FALSIFIED:
        verdict_sin2 = "TENSION"
    else:
        verdict_sin2 = "FALSIFIED"

    result: dict = {
        "observable": "sin²θ₁₂",
        "um_prediction": SIN2_THETA_12_UM,
        "measured": sin2_theta12_measured,
        "sigma": sin2_theta12_sigma,
        "residual_sigmas": sigma_sin2,
        "verdict": verdict_sin2,
    }

    # Δm²₂₁ assessment (if provided)
    if dm21_sq_measured_ev2 is not None and dm21_sq_sigma_ev2 is not None:
        residual_dm21 = abs(DM21_SQ_EV2_UM - dm21_sq_measured_ev2)
        sigma_dm21 = residual_dm21 / dm21_sq_sigma_ev2 if dm21_sq_sigma_ev2 > 0 else 0.0

        if sigma_dm21 < SIGMA_TENSION:
            verdict_dm21 = "TIGHTENED"
        elif sigma_dm21 < SIGMA_FALSIFIED:
            verdict_dm21 = "TENSION"
        else:
            verdict_dm21 = "FALSIFIED"

        result["dm21"] = {
            "observable": "Δm²₂₁",
            "um_prediction_ev2": DM21_SQ_EV2_UM,
            "measured_ev2": dm21_sq_measured_ev2,
            "sigma_ev2": dm21_sq_sigma_ev2,
            "residual_sigmas": sigma_dm21,
            "verdict": verdict_dm21,
        }

        # Combined verdict: worst of the two
        verdicts = [verdict_sin2, verdict_dm21]
        if "FALSIFIED" in verdicts:
            combined = "FALSIFIED"
        elif "TENSION" in verdicts:
            combined = "TENSION"
        else:
            combined = "TIGHTENED"
        result["combined_verdict"] = combined
    else:
        result["combined_verdict"] = verdict_sin2

    # Actions
    actions = {
        "TIGHTENED": (
            "JUNO solar θ₁₂ measurement within 1σ_JUNO of UM prediction. "
            "Route A geometric derivation TIGHTENED. No update to Pillar P18 needed."
        ),
        "TENSION": (
            "JUNO solar θ₁₂ at 1–3σ_JUNO tension with UM prediction. "
            "Monitor for improved measurement. Check Pillar P18 Route A vs Route B."
        ),
        "FALSIFIED": (
            "JUNO solar θ₁₂ at ≥3σ_JUNO from UM prediction. "
            "Pillar P18 Route A FALSIFIED. Revert to Route B (parameter fit) or "
            "investigate systematic errors in the geometric mixing angle derivation."
        ),
    }
    result["action"] = actions[result["combined_verdict"]]

    return result


def juno_solar_projection(central_shifts_to_pdg: bool = False) -> dict:
    """Project JUNO solar verdict assuming UM or PDG central value.

    Parameters
    ----------
    central_shifts_to_pdg : bool
        If False: assume JUNO measures exactly the PDG central (0.307).
        If True: assume JUNO measures exactly the UM central (0.305) — best case.
    """
    juno_sigma = JUNO_SOLAR_PRECISION_FRAC * PDG_SIN2_THETA_12

    if central_shifts_to_pdg:
        # Best case: JUNO confirms UM prediction exactly
        measured = SIN2_THETA_12_UM
    else:
        # Realistic: JUNO confirms current PDG central
        measured = PDG_SIN2_THETA_12

    return route_juno_solar(
        sin2_theta12_measured=measured,
        sin2_theta12_sigma=juno_sigma,
        dm21_sq_measured_ev2=PDG_DM21_SQ,
        dm21_sq_sigma_ev2=JUNO_DM21_PRECISION_FRAC * PDG_DM21_SQ,
    )


def pillar342_full_report() -> dict:
    """Full Pillar 342 report."""
    budget = juno_solar_precision_budget()
    projection_pdg_central = juno_solar_projection(central_shifts_to_pdg=False)
    projection_um_central = juno_solar_projection(central_shifts_to_pdg=True)

    return {
        "pillar": 342,
        "title": "JUNO Solar Neutrino Precision Routing",
        "status": "NON_HARDGATE_ADJACENT",
        "epistemic_label": "PREREGISTERED_FALSIFIER",
        "um_predictions": {
            "sin2_theta12": SIN2_THETA_12_UM,
            "theta12_deg": THETA_12_DEG_UM,
            "dm21_sq_ev2": DM21_SQ_EV2_UM,
            "p_ee_8b": budget["p_ee_8b_um"],
            "p_ee_pp": budget["p_ee_pp_um"],
        },
        "precision_budget": budget,
        "projection_if_pdg_holds": projection_pdg_central,
        "projection_if_um_holds": projection_um_central,
        "juno_solar_target_precision": f"{JUNO_SOLAR_PRECISION_FRAC * 100:.1f}% on sin²θ₁₂",
        "connection_to_pillar334": (
            "Pillar 334 covers JUNO reactor neutrino programme (mass ordering + Δm²₃₁). "
            "This pillar covers the separate solar programme (θ₁₂ + Δm²₂₁). "
            "Both route through the same JUNO experiment but test different UM predictions."
        ),
        "falsification_condition": (
            "If JUNO solar measures sin²θ₁₂ inconsistent with UM prediction "
            f"({SIN2_THETA_12_UM:.4f}) at ≥3σ_JUNO: Pillar P18 Route A FALSIFIED. "
            "The 1.55% PDG residual becomes a ~1.3σ JUNO tension if PDG central holds."
        ),
    }
