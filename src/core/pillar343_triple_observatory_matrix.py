# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 343 — 2027 Triple-Observatory Unified Decision Matrix.

🔵 ADJACENT TRACK — HARDGATE_ADJACENT (extends ORD, Pillars 334/335/336)

══════════════════════════════════════════════════════════════════════════════
THE 2027 MOMENT: THREE EXPERIMENTS, ONE VERDICT
══════════════════════════════════════════════════════════════════════════════

The Observatory Routing Daemon (v11.18) handles each 2027 experiment
independently:
  - Simons Observatory (SO): routes r measurement → P2/P3 verdict
  - DESI DR3: routes wₐ measurement → P4/wₐ=0 verdict
  - JUNO: routes mass ordering → P42/P11 verdict

This pillar builds the JOINT Bayesian decision node.  Given simultaneous
outcomes from all three experiments, what is the combined framework verdict?

This is the pre-computation of the "2027 moment" — the joint verdict matrix
and Bayes factor tree are ready on publication day for any combination of
results.

══════════════════════════════════════════════════════════════════════════════
JOINT OUTCOME SPACE
══════════════════════════════════════════════════════════════════════════════

Each experiment has three possible outcomes:
  SO:   CONFIRMED (r ≈ 0.03) | CONSISTENT (r ∈ [0.01, 0.05]) | FALSIFIED (r < 0.01)
  DESI: RESOLVED (wₐ < 2σ)  | HIGH_TENSION (2–3σ)           | FALSIFIED (wₐ ≥ 3σ)
  JUNO: CONFIRMED (normal)   | CONSISTENT                    | FALSIFIED (inverted)

Binary simplification for the 8-scenario matrix:
  SO:   PASS (r not excluded at > 3σ) | FAIL (r < 0.010 at ≥ 3σ)
  DESI: PASS (wₐ = 0 not 3σ-excluded) | FAIL (wₐ ≠ 0 at ≥ 3σ)
  JUNO: PASS (normal ordering or inconclusive) | FAIL (inverted at ≥ 3σ)

Eight joint scenarios (3 binary variables → 2³ = 8 outcomes):

  #  SO   DESI  JUNO  |  Framework verdict
  1  PASS PASS  PASS  |  STANDING — all three pass; continue to LiteBIRD
  2  PASS PASS  FAIL  |  PARTIALLY_FALSIFIED — neutrino sector fails; core survives
  3  PASS FAIL  PASS  |  HIGH_TENSION — dark energy fails; ACT+DESI converge
  4  PASS FAIL  FAIL  |  SUBSTANTIALLY_FALSIFIED — two pillars fail
  5  FAIL PASS  PASS  |  HIGH_TENSION — r sector fails; dark energy and ν survive
  6  FAIL PASS  FAIL  |  SUBSTANTIALLY_FALSIFIED — two independent sectors fail
  7  FAIL FAIL  PASS  |  SUBSTANTIALLY_FALSIFIED — two independent sectors fail
  8  FAIL FAIL  FAIL  |  FALSIFIED — all three fail; framework FALSIFIED

══════════════════════════════════════════════════════════════════════════════
BAYES FACTOR COMPUTATION
══════════════════════════════════════════════════════════════════════════════

For each experiment, the Bayes factor (UM vs ΛCDM free-parameter model):

  SO (r measurement):
    B_r = P(data | r_UM = 0.0315) / P(data | r_ΛCDM free)
        = L(r_meas | r=0.0315) / ∫ L(r_meas | r) × π(r) dr
    where π(r) is flat prior on r ∈ [0, 0.2]

  DESI (wₐ measurement):
    B_wₐ = P(data | wₐ=0) / P(data | wₐ free)

  JUNO (mass ordering):
    B_ord = P(data | NO) / P(data | NO + IO uniform prior)
           = 2 if NO confirmed, = 0 if IO confirmed

  Joint Bayes factor:
    B_joint = B_r × B_wₐ × B_ord  [assuming independent measurements]

══════════════════════════════════════════════════════════════════════════════
"""
import math

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

N_W = 5
K_CS = 74

# UM predictions (inputs to joint verdict)
R_UM = 0.0315             # tensor-to-scalar ratio
R_UM_SIGMA = 0.002        # UM theory uncertainty on r
WA_UM = 0.0               # dark energy wₐ prediction
MASS_ORDERING_UM = "NORMAL"  # neutrino mass ordering

# Current tensions (from v11.18)
WA_CURRENT_SIGMA = 2.75   # DESI DR2 combined wₐ tension
R_ACT_UPPER = 0.016       # ACT DR6 95% CL upper bound on r

# DESI DR3 projected precision
DESI_DR3_SIGMA_WA = 0.18  # projected σ(wₐ) DESI DR3
DESI_DR3_CENTRAL = -0.55  # DESI DR2 central wₐ

# Simons Observatory projected precision
SO_SIGMA_R = 0.003        # SO 5-year σ(r)

# Falsification thresholds
SIGMA_FALSIFIED = 3.0

# Prior ranges for Bayes factor computation
R_PRIOR_MAX = 0.20        # flat prior on r ∈ [0, 0.20]
WA_PRIOR_RANGE = 4.0      # flat prior on wₐ ∈ [-2, 2]


# ─────────────────────────────────────────────────────────────────────────────
# SEPARATION GUARD
# ─────────────────────────────────────────────────────────────────────────────

def separation_guard() -> dict:
    """Returns track classification."""
    return {
        "pillar": 343,
        "track": "ADJACENT_TRACK_HARDGATE_ADJACENT",
        "hardgate_promotion": False,
        "toe_score_delta": 0,
        "extends": "Observatory Routing Daemon (v11.18) + Pillars 334/335/336",
        "description": (
            "2027 Triple-Observatory Unified Decision Matrix. "
            "Joint Bayesian decision node for SO + DESI DR3 + JUNO simultaneous results."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# PER-EXPERIMENT BAYES FACTORS
# ─────────────────────────────────────────────────────────────────────────────

def bayes_factor_r(r_measured: float, sigma_r: float) -> float:
    """Bayes factor B_r = P(data | r_UM) / P(data | r_free).

    P(data | r_UM) = Gaussian likelihood at r = R_UM.
    P(data | r_free) = marginal likelihood with flat prior on [0, R_PRIOR_MAX].
    """
    # Likelihood at UM point
    chi2_um = (r_measured - R_UM) ** 2 / sigma_r ** 2
    log_like_um = -0.5 * chi2_um

    # Marginal likelihood (flat prior) — Gaussian integral over [0, R_PRIOR_MAX]
    # Normalisation: 1/R_PRIOR_MAX × integral of Gaussian over [0, R_MAX]
    # ≈ 1/(R_PRIOR_MAX × sqrt(2π) × sigma_r) for sigma_r << R_PRIOR_MAX
    log_marginal = math.log(
        math.sqrt(2 * math.pi) * sigma_r / R_PRIOR_MAX
    )
    # But log of likelihood at UM point is offset by log_like_um
    log_bf_r = log_like_um - (-log_marginal)
    # Equivalently: log B = log P(d|UM) - log P(d|free)
    # log P(d|free) = log(1/R_PRIOR_MAX) + log(integral of L over prior)
    # For Gaussian centred at r_measured with prior >> sigma:
    # log P(d|free) ≈ log(1/R_PRIOR_MAX) (Occam factor)
    log_bf_r = log_like_um + math.log(R_PRIOR_MAX / (math.sqrt(2 * math.pi) * sigma_r))

    return math.exp(log_bf_r)


def bayes_factor_wa(wa_measured: float, sigma_wa: float) -> float:
    """Bayes factor B_wₐ = P(data | wₐ=0) / P(data | wₐ_free)."""
    # Likelihood at wₐ = 0
    chi2_um = (wa_measured - WA_UM) ** 2 / sigma_wa ** 2
    log_like_um = -0.5 * chi2_um

    # Marginal likelihood with flat prior over [-2, 2] (range 4)
    log_bf_wa = log_like_um + math.log(WA_PRIOR_RANGE / (math.sqrt(2 * math.pi) * sigma_wa))

    return math.exp(log_bf_wa)


def bayes_factor_ordering(ordering_result: str) -> float:
    """Bayes factor for neutrino mass ordering.

    B_ord = P(data | NO) / P(data | uniform prior NO+IO)
          = 2 if JUNO confirms NO at ≥3σ
          = 0 if JUNO confirms IO at ≥3σ
          = 1 if inconclusive
    """
    if ordering_result.upper() in ("NORMAL", "NO", "PASS"):
        return 2.0
    elif ordering_result.upper() in ("INVERTED", "IO", "FAIL"):
        return 0.0
    else:
        return 1.0


def joint_bayes_factor(r_measured: float, sigma_r: float,
                        wa_measured: float, sigma_wa: float,
                        ordering: str) -> float:
    """Joint Bayes factor: B_joint = B_r × B_wₐ × B_ordering."""
    b_r = bayes_factor_r(r_measured, sigma_r)
    b_wa = bayes_factor_wa(wa_measured, sigma_wa)
    b_ord = bayes_factor_ordering(ordering)
    return b_r * b_wa * b_ord


# ─────────────────────────────────────────────────────────────────────────────
# JOINT VERDICT MATRIX (8 SCENARIOS)
# ─────────────────────────────────────────────────────────────────────────────

SCENARIO_VERDICTS = {
    # (so_pass, desi_pass, juno_pass) → (verdict, description)
    (True, True, True): (
        "STANDING",
        "All three 2027 experiments pass. Framework STANDING. "
        "Continue to LiteBIRD 2032 as primary falsifier. "
        "Bayes factor: strongly positive from SO r confirmation."
    ),
    (True, True, False): (
        "PARTIALLY_FALSIFIED",
        "Neutrino sector (JUNO inverted ordering) falsifies Pillar 42/332. "
        "Core dark energy and inflation predictions survive. "
        "Required: mark Pillar 42 FALSIFIED; initiate neutrino sector review."
    ),
    (True, False, True): (
        "HIGH_TENSION",
        "Dark energy wₐ≠0 at ≥3σ (DESI DR3). Pillar P4/wₐ=0 FALSIFIED. "
        "r prediction survives (if SO confirms r≈0.03). "
        "Required: mark wₐ=0 FALSIFIED; frozen radion mechanism examined. "
        "LiteBIRD 2032 remains as partial arbiter."
    ),
    (True, False, False): (
        "SUBSTANTIALLY_FALSIFIED",
        "Two independent sectors fail: dark energy (DESI) and neutrino ordering (JUNO). "
        "Only inflation (SO) passes. Framework substantially falsified. "
        "Required: full retraction protocol for Pillars 42, P4."
    ),
    (False, True, True): (
        "HIGH_TENSION",
        "Inflation sector (SO r < 0.010) falsified. Dark energy and ν survive. "
        "r prediction is the most IRREDUCIBLE tension (Pillar 303). "
        "Required: mark r=0.0315 FALSIFIED; examine ACT+SO combined."
    ),
    (False, True, False): (
        "SUBSTANTIALLY_FALSIFIED",
        "Two independent sectors fail: inflation (SO) and neutrino ordering (JUNO). "
        "Framework substantially falsified. Required: Pillars 2, 42 retraction."
    ),
    (False, False, True): (
        "SUBSTANTIALLY_FALSIFIED",
        "Two independent sectors fail: inflation (SO) and dark energy (DESI). "
        "Framework substantially falsified. Required: Pillars 2, P4 retraction."
    ),
    (False, False, False): (
        "FALSIFIED",
        "All three 2027 experiments fail. Framework FALSIFIED by three independent tests. "
        "Full retraction protocol: archive repository; publish falsification notice. "
        "Birefringence prediction (LiteBIRD) no longer relevant as primary arbiter."
    ),
}


def classify_so_result(r_measured: float, sigma_r: float) -> tuple:
    """Classify SO result as PASS or FAIL.

    PASS: r prediction not excluded at ≥3σ.
    FAIL: r < 0.010 measured at ≥3σ.
    """
    # Check if UM prediction r=0.0315 is excluded
    if r_measured < 0.010 and (0.010 - r_measured) / sigma_r >= SIGMA_FALSIFIED:
        return False, "FALSIFIED", r_measured, sigma_r
    # Also check if r is dramatically above UM prediction
    if r_measured > 0.060:
        return False, "TENSION_HIGH", r_measured, sigma_r
    return True, "CONSISTENT", r_measured, sigma_r


def classify_desi_result(wa_measured: float, sigma_wa: float) -> tuple:
    """Classify DESI DR3 result as PASS or FAIL."""
    sigma_tension = abs(wa_measured - WA_UM) / sigma_wa
    if sigma_tension >= SIGMA_FALSIFIED:
        return False, "FALSIFIED", wa_measured, sigma_wa
    return True, "CONSISTENT", wa_measured, sigma_wa


def classify_juno_result(ordering: str, sigma: float = 0.0) -> tuple:
    """Classify JUNO ordering result as PASS or FAIL."""
    if ordering.upper() in ("INVERTED", "IO") and sigma >= SIGMA_FALSIFIED:
        return False, "FALSIFIED", ordering, sigma
    return True, "CONSISTENT", ordering, sigma


def run_joint_verdict(r_measured: float, sigma_r: float,
                      wa_measured: float, sigma_wa: float,
                      ordering: str, ordering_sigma: float = 0.0) -> dict:
    """Run the full joint verdict for the 2027 triple-observatory scenario.

    Parameters
    ----------
    r_measured : float
        SO measured r value.
    sigma_r : float
        SO measurement uncertainty.
    wa_measured : float
        DESI DR3 measured wₐ.
    sigma_wa : float
        DESI DR3 wₐ uncertainty.
    ordering : str
        JUNO mass ordering result ("NORMAL" or "INVERTED").
    ordering_sigma : float
        JUNO ordering significance.
    """
    so_pass, so_verdict, _, _ = classify_so_result(r_measured, sigma_r)
    desi_pass, desi_verdict, _, _ = classify_desi_result(wa_measured, sigma_wa)
    juno_pass, juno_verdict, _, _ = classify_juno_result(ordering, ordering_sigma)

    scenario_key = (so_pass, desi_pass, juno_pass)
    joint_verdict, joint_description = SCENARIO_VERDICTS[scenario_key]

    b_joint = joint_bayes_factor(r_measured, sigma_r, wa_measured, sigma_wa, ordering)

    return {
        "scenario_key": str(scenario_key),
        "so_result": {"r_measured": r_measured, "sigma_r": sigma_r, "pass": so_pass,
                      "verdict": so_verdict},
        "desi_result": {"wa_measured": wa_measured, "sigma_wa": sigma_wa,
                        "pass": desi_pass, "verdict": desi_verdict},
        "juno_result": {"ordering": ordering, "sigma": ordering_sigma,
                        "pass": juno_pass, "verdict": juno_verdict},
        "joint_verdict": joint_verdict,
        "joint_description": joint_description,
        "bayes_factor_joint": b_joint,
        "log10_bayes": math.log10(b_joint) if b_joint > 0 else float("-inf"),
        "action": joint_description,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PRE-COMPUTED SCENARIO TABLE
# ─────────────────────────────────────────────────────────────────────────────

def precompute_all_scenarios() -> list:
    """Pre-compute all 8 joint scenarios with representative input values."""
    scenarios = []

    # Representative values for pass/fail
    so_configs = [
        (0.0315, SO_SIGMA_R, True),   # PASS: r ≈ 0.03, detected
        (0.005, SO_SIGMA_R, False),   # FAIL: r ≈ 0.005, excludes UM
    ]
    desi_configs = [
        (0.0, DESI_DR3_SIGMA_WA, True),    # PASS: wₐ = 0 consistent
        (-0.55, DESI_DR3_SIGMA_WA, False), # FAIL: wₐ = -0.55 at 3σ
    ]
    juno_configs = [
        ("NORMAL", 4.0, True),    # PASS: normal ordering confirmed
        ("INVERTED", 3.5, False), # FAIL: inverted ordering confirmed
    ]

    for so_r, so_sig, so_p in so_configs:
        for desi_wa, desi_sig, desi_p in desi_configs:
            for juno_ord, juno_sig, juno_p in juno_configs:
                result = run_joint_verdict(
                    r_measured=so_r, sigma_r=so_sig,
                    wa_measured=desi_wa, sigma_wa=desi_sig,
                    ordering=juno_ord, ordering_sigma=juno_sig,
                )
                scenarios.append({
                    "so_pass": so_p,
                    "desi_pass": desi_p,
                    "juno_pass": juno_p,
                    "joint_verdict": result["joint_verdict"],
                    "log10_bayes": result["log10_bayes"],
                })

    return scenarios


def best_case_scenario() -> dict:
    """Best case: all three pass. Scenario #1."""
    return run_joint_verdict(
        r_measured=0.0315, sigma_r=SO_SIGMA_R,
        wa_measured=0.0, sigma_wa=DESI_DR3_SIGMA_WA,
        ordering="NORMAL", ordering_sigma=4.0,
    )


def worst_case_scenario() -> dict:
    """Worst case: all three fail. Scenario #8.

    Uses r=0.001 with σ=0.001 so that (0.010−0.001)/0.001 = 9σ — clearly
    below the SO detection threshold → SO fails (FALSIFIED).
    """
    return run_joint_verdict(
        r_measured=0.001, sigma_r=0.001,
        wa_measured=-0.90, sigma_wa=DESI_DR3_SIGMA_WA,
        ordering="INVERTED", ordering_sigma=3.5,
    )


def desi_fails_only_scenario() -> dict:
    """DESI fails, SO and JUNO pass. Scenario #3."""
    return run_joint_verdict(
        r_measured=0.0315, sigma_r=SO_SIGMA_R,
        wa_measured=DESI_DR3_CENTRAL, sigma_wa=DESI_DR3_SIGMA_WA,
        ordering="NORMAL", ordering_sigma=4.0,
    )


def so_fails_only_scenario() -> dict:
    """SO fails, DESI and JUNO pass. Scenario #5.

    Uses r=0.001 with σ=0.001 so that (0.010−0.001)/0.001 = 9σ → SO fails.
    """
    return run_joint_verdict(
        r_measured=0.001, sigma_r=0.001,
        wa_measured=0.0, sigma_wa=DESI_DR3_SIGMA_WA,
        ordering="NORMAL", ordering_sigma=4.0,
    )


def pillar343_full_report() -> dict:
    """Full Pillar 343 report."""
    all_scenarios = precompute_all_scenarios()
    best = best_case_scenario()
    worst = worst_case_scenario()

    return {
        "pillar": 343,
        "title": "2027 Triple-Observatory Unified Decision Matrix",
        "status": "NON_HARDGATE_ADJACENT",
        "epistemic_label": "PREREGISTERED_JOINT_VERDICT",
        "experiments": {
            "SIMONS_OBSERVATORY": {
                "observable": "r (tensor-to-scalar ratio)",
                "um_prediction": R_UM,
                "sigma_projected": SO_SIGMA_R,
                "falsification": "r < 0.010 at ≥3σ",
            },
            "DESI_DR3": {
                "observable": "wₐ (dark energy EoS evolution)",
                "um_prediction": WA_UM,
                "sigma_projected": DESI_DR3_SIGMA_WA,
                "current_tension_sigma": WA_CURRENT_SIGMA,
                "falsification": "wₐ ≠ 0 at ≥3σ",
            },
            "JUNO": {
                "observable": "neutrino mass ordering",
                "um_prediction": MASS_ORDERING_UM,
                "falsification": "inverted ordering at ≥3σ",
            },
        },
        "joint_scenario_count": len(all_scenarios),
        "all_scenarios_summary": all_scenarios,
        "scenario_1_all_pass": best["joint_verdict"],
        "scenario_8_all_fail": worst["joint_verdict"],
        "best_case_log10_bayes": best["log10_bayes"],
        "worst_case_log10_bayes": worst["log10_bayes"],
        "execution_protocol": (
            "On publication day for any 2027 experiment: "
            "(1) Extract measured values and uncertainties; "
            "(2) Call run_joint_verdict() with all three results; "
            "(3) Read joint_verdict and execute action; "
            "(4) Update CLAIM_MASTER_BOARD.md and STATUS.md within 24 hours."
        ),
        "priority_date": "2027 (SO DR1 expected first; DESI DR3 and JUNO may follow)",
    }
