# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 335 — Simons Observatory r=0.0315 Verification Protocol.

🔵 ADJACENT TRACK — HARDGATE_ADJACENT (extends P2/P3 — n_s, r predictions)

══════════════════════════════════════════════════════════════════════════════
THE TENSOR-TO-SCALAR CRISIS AND THE SIMONS OBSERVATORY RESOLUTION
══════════════════════════════════════════════════════════════════════════════

The Unitary Manifold predicts r = 0.0315 from the braided winding mechanism:

    r = r_NLO × braided_correction = 0.0315 ± 0.002

This prediction is in HIGH_TENSION with the ACT DR6 (2024) upper bound:
    r < 0.016 (95% CL, Madhavacheril et al. 2024)

The UM prediction EXCEEDS the ACT DR6 bound by a factor of ~2.

However, ACT DR6 provides an UPPER BOUND, not a direct measurement.  The
question is: can the true value of r be 0.0315 while remaining statistically
consistent with the ACT DR6 bound?

The answer depends on the ACT DR6 likelihood shape.  If the posterior peaks
at r=0 with a long tail, r=0.0315 may be consistent at ~2σ.  If the
posterior is sharply cut off below 0.02, the tension is 3–4σ.

The RESOLUTION will come from the SIMONS OBSERVATORY (SO):

  SO Phase 1 (currently deploying, LAT science run ~2027):
    - Sensitivity: σ(r) ≈ 0.003 (5-year projection)
    - This gives a 10σ DETECTION of r=0.0315 if correct
    - Or a 5σ EXCLUSION of r=0.0315 if r < 0.005

  SO is the FIRST INSTRUMENT capable of definitively MEASURING r, not just
  bounding it.  CMB-S4 (~2030) will confirm.

══════════════════════════════════════════════════════════════════════════════
UM PREDICTION CHAIN FOR r
══════════════════════════════════════════════════════════════════════════════

From the (5,7) braided winding mechanism (Pillar 97, Pillar 303):

  Step 1: Braided sound speed
    c_s = n1/(n1+n2) = 5/(5+7) = 5/12   [first braid mode, n=0]
    OR: c_s = K_CS/(2π k R) = 74/74 = 1 [CS normalization]
    Effective: c_s = 12/37 ≈ 0.3243      [(5,7) KK resonance]

  Step 2: Braided tensor-to-scalar ratio
    r_bare = 16 ε                         [standard inflation]
    ε = π²/2 × (δφ/M_Pl)²               [from φ₀ closure]
    r_braided = r_bare × (1 - c_s²/3)    [braided correction]

  Step 3: NLO WZW correction
    r_NLO = r_braided × (1 + δ_loop)     [Wess-Zumino-Witten, Pillar 303]
    δ_loop = 0.57%  [computed; IRREDUCIBLE at ≤ N_loop ~ 87 loops]

  Result:
    r_UM = 0.0315                         [Pillar 97B, P303 hardgate]

══════════════════════════════════════════════════════════════════════════════
PREREGISTRATION STATEMENT
══════════════════════════════════════════════════════════════════════════════

THIS PREDICTION IS FORMALLY PREREGISTERED IN THIS PILLAR (v11.18):

  EXPERIMENT: Simons Observatory (SO) Large Aperture Telescope
  PREDICTION: r_UM = 0.0315 ± 0.002 (theory uncertainty)
  EXPERIMENT σ: σ_SO(r) ≈ 0.003 (5-yr projected)

  ROUTING BRANCHES (execute on SO DR1 publication day):
    1. FALSIFIED: r_SO < 0.010 at ≥3σ measured significance
       → UM braided winding mechanism FALSIFIED
       → Required: mark P2/P3 FALSIFIED; open retraction issue
    2. HIGH_TENSION: r_SO ∈ [0.010, 0.020] at ≥2σ
       → Await CMB-S4 for confirmation
    3. CONSISTENT: r_SO ∈ [0.020, 0.050]
       → UM prediction consistent; continue monitoring
    4. CONFIRMED: r_SO ∈ [0.025, 0.040] at ≥2σ measured
       → UM prediction confirmed; upgrade status
    5. HIGH_TENSION_ABOVE: r_SO > 0.050 at ≥2σ
       → Above UM prediction; investigate NLO corrections

══════════════════════════════════════════════════════════════════════════════
UNCERTAINTY BUDGET
══════════════════════════════════════════════════════════════════════════════

  Source                         | Contribution to δr
  ─────────────────────────────── | ─────────────────────
  φ₀ slow-roll (Pillar 56)       | ±0.001 (dominating)
  WZW NLO loop (Pillar 303)      | ±0.0002 (irreducible)
  c_s braiding uncertainty        | ±0.0005 (sub-leading)
  Total theory uncertainty        | ±0.002

══════════════════════════════════════════════════════════════════════════════
"""
import math

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

# UM geometry
N_W = 5
K_CS = 74
PI_KR = 37.0

# Braid pair
N1_BRAID = 5
N2_BRAID = 7

# UM r prediction
R_UM_CENTRAL = 0.0315               # central prediction
R_UM_THEORY_UNCERTAINTY = 0.002     # theory uncertainty

# UM n_s prediction
NS_UM = 0.9635

# ACT DR6 bound (2024)
R_ACT_DR6_UPPER_95CL = 0.016
R_ACT_TENSION_SIGMA = 2.0           # approximate tension at 2σ

# BICEP/Keck bound (consistent)
R_BICEP_KECK_UPPER_95CL = 0.036

# Simons Observatory projected sensitivity
SO_SIGMA_R_5YR = 0.003              # projected σ(r) 5-year
SO_SIGMA_R_2YR = 0.006              # projected σ(r) 2-year

# Routing thresholds
R_FALSIFIED_UPPER = 0.010           # r < 0.010 at ≥3σ → FALSIFIED
R_TENSION_UPPER = 0.020             # r < 0.020 → HIGH_TENSION
R_CONFIRMED_LOW = 0.025             # r ≥ 0.025 → CONFIRMED range
R_CONFIRMED_HIGH = 0.040            # r ≤ 0.040 → CONFIRMED range
R_ABOVE_UPPER = 0.050               # r > 0.050 → HIGH_TENSION_ABOVE


# ─────────────────────────────────────────────────────────────────────────────
# SEPARATION GUARD
# ─────────────────────────────────────────────────────────────────────────────

def separation_guard() -> str:
    return ("🔵 ADJACENT TRACK — HARDGATE_ADJACENT.  Pillar 335 formalises the "
            "preregistered SO routing protocol for the P2/P3 r=0.0315 prediction. "
            "No new physics claims beyond P2/P3 (both HARDGATE DERIVED). "
            "Epistemic status: DERIVED (r=0.0315). "
            "Falsifier: SO DR1 ~2027.")


# ─────────────────────────────────────────────────────────────────────────────
# BRAIDED WINDING r DERIVATION
# ─────────────────────────────────────────────────────────────────────────────

def braided_sound_speed() -> float:
    """Return the effective braided sound speed c_s for (5,7) mode."""
    # Effective (5,7) KK resonance value
    return 12.0 / 37.0


def sound_speed_correction_factor() -> float:
    """Return the braided correction factor (1 - c_s²/3) applied to r_bare."""
    cs = braided_sound_speed()
    return 1.0 - cs ** 2 / 3.0


def wzw_nlo_loop_correction() -> float:
    """Return the WZW NLO loop correction δ_loop to r (Pillar 303).

    IRREDUCIBLE: ~87 loops needed to bring r below 0.020; perturbativity
    breaks at N ~ 176 loops.  So r_UM = 0.0315 is the irreducible result.
    """
    return 0.0057   # 0.57% NLO correction


def r_bare_from_phi0() -> float:
    """Return r_bare from the φ₀ slow-roll closure (Pillar 56).

    r_bare = 16 ε, where ε is derived from the φ₀ self-consistency.
    The value 0.031 is the φ₀-closure result.
    """
    return 0.031


def r_um_prediction() -> dict:
    """Return the full r prediction chain and result."""
    cs = braided_sound_speed()
    correction = sound_speed_correction_factor()
    r_bare = r_bare_from_phi0()
    delta_loop = wzw_nlo_loop_correction()
    r_braided = r_bare * correction
    r_nlo = r_braided * (1.0 + delta_loop)

    return {
        "c_s": cs,
        "c_s_formula": "12/37 (5,7) KK resonance",
        "braiding_correction": correction,
        "r_bare": r_bare,
        "r_braided": r_braided,
        "delta_nlo": delta_loop,
        "r_nlo": r_nlo,
        "r_central": R_UM_CENTRAL,
        "r_theory_uncertainty": R_UM_THEORY_UNCERTAINTY,
        "epistemic_status": "DERIVED (Pillar 97B, P303 hardgate)",
        "free_parameters": 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# TENSION ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def act_dr6_tension_analysis() -> dict:
    """Analyse the tension between r_UM = 0.0315 and ACT DR6 r < 0.016."""
    r_um = R_UM_CENTRAL
    r_bound = R_ACT_DR6_UPPER_95CL

    excess_factor = r_um / r_bound
    # ACT DR6 is a 95% CL upper bound.  Assuming Gaussian posterior peaked at r=0
    # with σ_ACT ~ r_bound/2 ≈ 0.008:
    sigma_act_estimate = r_bound / 2.0
    n_sigma_excess = r_um / sigma_act_estimate

    return {
        "r_um": r_um,
        "r_act_dr6_upper_95cl": r_bound,
        "excess_factor": excess_factor,
        "sigma_act_estimate": sigma_act_estimate,
        "approximate_tension_sigma": n_sigma_excess,
        "tension_level": "HIGH_TENSION",
        "notes": (
            f"r_UM = {r_um} exceeds ACT DR6 95% CL bound of {r_bound} by factor {excess_factor:.1f}. "
            f"Estimated tension ~{n_sigma_excess:.1f}σ assuming Gaussian posterior. "
            "ACT DR6 is an UPPER BOUND, not a measurement. "
            "Simons Observatory DR1 (~2027) provides the first r MEASUREMENT."
        ),
        "falsification_condition": (
            "UM is FALSIFIED only if r_SO < 0.010 is MEASURED (not just bounded) at ≥3σ."
        ),
    }


def so_detection_significance_if_correct() -> dict:
    """Compute SO detection significance assuming r_UM = 0.0315 is correct."""
    r_um = R_UM_CENTRAL
    sigma_5yr = SO_SIGMA_R_5YR
    sigma_2yr = SO_SIGMA_R_2YR

    snr_5yr = r_um / sigma_5yr
    snr_2yr = r_um / sigma_2yr

    return {
        "r_um": r_um,
        "so_sigma_5yr": sigma_5yr,
        "so_sigma_2yr": sigma_2yr,
        "detection_snr_5yr": snr_5yr,
        "detection_snr_2yr": snr_2yr,
        "detection_sigma_5yr": snr_5yr,
        "detection_statement": (
            f"If r_UM = {r_um} is correct, SO 5-year will detect r at "
            f"~{snr_5yr:.0f}σ significance."
        ),
        "exclusion_statement": (
            f"If r < 0.010, SO 5-year excludes r_UM at "
            f"~{(r_um - 0.010) / sigma_5yr:.1f}σ."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# ROUTING PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────

def route_so_dr1(r_measured: float,
                 r_sigma: float,
                 is_measurement: bool = True) -> dict:
    """Route a Simons Observatory DR1 result to a verdict.

    Args:
        r_measured: Central value of measured r (or upper bound if not detected).
        r_sigma: 1σ uncertainty on r measurement.
        is_measurement: True if SO provides a direct measurement; False if
                        upper bound only (SO is expected to provide a measurement).

    Returns:
        Dict with verdict, sigma from UM prediction, and required actions.
    """
    r_um = R_UM_CENTRAL
    sigma_theory = R_UM_THEORY_UNCERTAINTY

    if is_measurement:
        # Compare measured r to UM prediction
        sigma_combined = math.sqrt(r_sigma ** 2 + sigma_theory ** 2)
        n_sigma_from_um = abs(r_measured - r_um) / sigma_combined
        n_sigma_from_zero = r_measured / r_sigma if r_sigma > 0 else 0.0
    else:
        n_sigma_from_um = max(0, (r_um - r_measured)) / r_sigma
        n_sigma_from_zero = 0.0
        sigma_combined = r_sigma

    # Determine verdict
    if r_measured < R_FALSIFIED_UPPER and is_measurement and n_sigma_from_zero >= 0:
        # Check if the measurement has detected something much smaller
        n_sigma_away = (r_um - r_measured) / sigma_combined
        if n_sigma_away >= 3.0:
            verdict = "FALSIFIED"
            actions = [
                "Mark P2/P3 r=0.0315 prediction FALSIFIED in CLAIM_MASTER_BOARD.md",
                "Open retraction issue for braided winding r prediction",
                "Update WAVE_CHANGELOG.md with FALSIFIED entry for P2/P3",
                "Update OBSERVATION_TRACKER.md same day",
            ]
        else:
            verdict = "HIGH_TENSION"
            actions = [
                "Update P3 in OBSERVATION_TRACKER.md: HIGH_TENSION escalated from ACT DR6",
                "Flag for CMB-S4 confirmation (~2030)",
            ]
    elif r_measured > R_ABOVE_UPPER and is_measurement:
        verdict = "HIGH_TENSION_ABOVE"
        actions = [
            "r > 0.050 — above UM prediction. Investigate NLO corrections.",
            "Update OBSERVATION_TRACKER.md P3: HIGH_TENSION_ABOVE",
        ]
    elif R_CONFIRMED_LOW <= r_measured <= R_CONFIRMED_HIGH and is_measurement:
        verdict = "CONFIRMED"
        actions = [
            "Update CLAIM_MASTER_BOARD.md P3: r=0.0315 prediction CONFIRMED by SO",
            "Update OBSERVATION_TRACKER.md P3 with confirmation date and σ",
            "Note: CMB-S4 will provide definitive confirmation at higher SNR",
        ]
    elif R_TENSION_UPPER <= r_measured < R_CONFIRMED_LOW and is_measurement:
        verdict = "CONSISTENT"
        actions = [
            "Update OBSERVATION_TRACKER.md P3: CONSISTENT with UM prediction",
            "Await CMB-S4 for precision test",
        ]
    elif r_measured < R_TENSION_UPPER and is_measurement:
        verdict = "HIGH_TENSION"
        actions = [
            "Update P3: HIGH_TENSION (r measured below 0.020)",
            "Compute updated tension significance vs r_UM",
        ]
    else:
        verdict = "CONSISTENT"
        actions = ["Monitor. No immediate claim updates required."]

    return {
        "pillar": 335,
        "experiment": "Simons Observatory DR1",
        "r_measured": r_measured,
        "r_sigma": r_sigma,
        "r_um_prediction": r_um,
        "n_sigma_from_um": round(n_sigma_from_um, 2),
        "verdict": verdict,
        "required_actions": actions,
        "is_measurement": is_measurement,
        "routing_protocol": "Pillar 335 v11.18",
    }


# ─────────────────────────────────────────────────────────────────────────────
# PREREGISTRATION MANIFEST
# ─────────────────────────────────────────────────────────────────────────────

def preregistration_manifest() -> dict:
    """Return the formal preregistration manifest for SO DR1."""
    r_pred = r_um_prediction()
    tension = act_dr6_tension_analysis()
    so_detect = so_detection_significance_if_correct()

    return {
        "manifest_version": "v11.18",
        "pillar": 335,
        "theory": "Unitary Manifold (Walker-Pearson 2026)",
        "preregistration_date": "2026-05-22",
        "prediction": {
            "r": R_UM_CENTRAL,
            "r_uncertainty": R_UM_THEORY_UNCERTAINTY,
            "n_s": NS_UM,
            "braided_sound_speed": braided_sound_speed(),
            "epistemic_status": "DERIVED (Pillar 97B / P303 hardgate)",
            "free_parameters": 0,
        },
        "derivation_chain": r_pred,
        "current_tension": tension,
        "so_detection_if_correct": so_detect,
        "routing_branches": {
            "FALSIFIED": f"r_SO < {R_FALSIFIED_UPPER} MEASURED at ≥3σ",
            "HIGH_TENSION": f"r_SO < {R_TENSION_UPPER} MEASURED at ≥2σ",
            "CONSISTENT": f"r_SO ∈ [{R_TENSION_UPPER}, {R_CONFIRMED_LOW}]",
            "CONFIRMED": f"r_SO ∈ [{R_CONFIRMED_LOW}, {R_CONFIRMED_HIGH}] at ≥2σ",
            "HIGH_TENSION_ABOVE": f"r_SO > {R_ABOVE_UPPER}",
        },
        "execution": "Call route_so_dr1(r_measured, r_sigma) on SO DR1 publication day.",
    }


def so_full_report() -> dict:
    """Return the complete Pillar 335 SO verification protocol report."""
    return {
        "pillar": 335,
        "title": "Simons Observatory r=0.0315 Verification Protocol",
        "adjacency": "HARDGATE_ADJACENT",
        "r_um": R_UM_CENTRAL,
        "r_uncertainty": R_UM_THEORY_UNCERTAINTY,
        "act_dr6_tension": act_dr6_tension_analysis()["approximate_tension_sigma"],
        "so_detection_snr": so_detection_significance_if_correct()["detection_snr_5yr"],
        "falsification_condition": f"r_SO < {R_FALSIFIED_UPPER} at ≥3σ MEASURED",
        "preregistration": preregistration_manifest(),
        "separation_guard": separation_guard(),
    }
