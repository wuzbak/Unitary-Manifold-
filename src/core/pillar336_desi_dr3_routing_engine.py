# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 336 — DESI DR3 Real-Time Routing Engine.

🔵 ADJACENT TRACK — HARDGATE_ADJACENT (extends P4 / CLAIM_MASTER_BOARD wₐ=0)

══════════════════════════════════════════════════════════════════════════════
THE DARK ENERGY EQUATION OF STATE: UM PREDICTION AND CURRENT TENSION
══════════════════════════════════════════════════════════════════════════════

The Unitary Manifold predicts:

    wₐ = 0    (frozen radion mechanism)
    w₀ = -1   (cosmological constant to lowest order in radion perturbation)

This is derived from the Randall-Sundrum warped extra dimension:
  - The radion field φ(x) governs the Kaluza-Klein scale
  - Stability requires φ at the Goldberger-Wise minimum: φ₀ = fixed
  - A frozen radion means δφ = 0 → no dark energy evolution → wₐ = 0
  - The RS1 potential provides a KK cosmological constant: w₀ = -1

STATUS (v11.17):
  - DESI DR2 BAO-only: 2.07σ tension with wₐ=0
  - DESI DR2 combined: 2.75σ tension with wₐ=0
  - NOT yet falsified (threshold: ≥3σ MEASURED at ≥3σ significance)

Pillar 301 (v11.11) CERTIFIED this as ARCHITECTURE_LIMIT:
  No rolling-radion 5D-EFT solution can produce wₐ ≈ -0.55 without
  destroying the RS1 hierarchy (ε_GW ~ 10⁻⁸⁸ fine-tuning required).
  This is an honest architecture constraint, not a free-parameter gap.

══════════════════════════════════════════════════════════════════════════════
DESI DR3 ROUTING PROTOCOL (FORMAL PREREGISTRATION)
══════════════════════════════════════════════════════════════════════════════

DESI DR3 (~2027) will be the definitive test of wₐ=0 vs wₐ≠0:
  - DR3 adds Year 3 BAO data (LRG + BGS + QSO + Ly-α)
  - Expected precision: σ(wₐ) ~ 0.15–0.20 (factor ~1.5× better than DR2)
  - If current tension is real: DR3 should see ≥3σ signal
  - If tension is statistical fluctuation: DR3 should RESOLVE to <2σ

THREE-BRANCH ROUTING (execute on DR3 publication day):

  Branch 1: FALSIFIED   — wₐ ≠ 0 at ≥3σ measured in DR3
    → Frozen radion mechanism FALSIFIED
    → Required: mark P4 / CLAIM_MASTER_BOARD wₐ=0 as FALSIFIED same day

  Branch 2: HIGH_TENSION — wₐ tension maintained at 2.1–3.0σ in DR3
    → Not falsified; escalated monitoring; await DR4 / CMB-S4

  Branch 3: RESOLVED     — tension drops to <2.1σ in DR3
    → DR2 tension was statistical; wₐ=0 CONSISTENT

══════════════════════════════════════════════════════════════════════════════
BAYESIAN UPDATE MACHINERY
══════════════════════════════════════════════════════════════════════════════

Given DESI DR3 measurements (wₐ_meas, σ_wₐ):

  Likelihood: L(wₐ | data) = exp(-0.5 ((wₐ - wₐ_meas) / σ_wₐ)²)

  UM prior: P(wₐ) = δ(wₐ)   [point mass at wₐ = 0]
    → P(data | wₐ=0) = exp(-0.5 (wₐ_meas / σ_wₐ)²)

  ΛCDM prior: P(wₐ) = flat over [-2, 2]
    → P(data | ΛCDM) = ∫ L(wₐ | data) × 1/4 dwₐ

  Bayes factor (wₐ=0 vs ΛCDM wₐ-free):
    B_UM = P(data | wₐ=0) / P(data | ΛCDM-free)

══════════════════════════════════════════════════════════════════════════════
"""
import math

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

# UM predictions
N_W = 5
K_CS = 74
W_A_UM = 0.0           # frozen radion: no dark energy evolution
W_0_UM = -1.0          # cosmological constant to lowest order

# DESI DR2 results (published 2024)
WA_DESI_DR2_BAO_ONLY = -0.79
WA_DESI_DR2_BAO_ONLY_SIGMA = 0.38
WA_DESI_DR2_COMBINED = -0.55
WA_DESI_DR2_COMBINED_SIGMA = 0.20
TENSION_DR2_BAO_ONLY = 2.07     # σ from wₐ=0
TENSION_DR2_COMBINED = 2.75     # σ from wₐ=0

# DESI DR3 projected sensitivity
WA_SIGMA_DR3_PROJECTED = 0.17   # σ(wₐ) projected for DR3

# Routing thresholds
FALSIFIED_SIGMA = 3.0           # ≥3σ → FALSIFIED
TENSION_SIGMA_LOW = 2.1         # <2.1σ → RESOLVED
TENSION_SIGMA_HIGH = 3.0        # ≥3σ → FALSIFIED

# CPL parametrization prior range for ΛCDM
WA_PRIOR_LOW = -2.0
WA_PRIOR_HIGH = 2.0

# Architecture limit from Pillar 301
ARCHITECTURE_LIMIT_NOTE = (
    "Pillar 301 (v11.11): ARCHITECTURE_LIMIT_CERTIFIED. "
    "No rolling-radion 5D-EFT can produce wₐ ≈ -0.55 without ε_GW ~ 10⁻⁸⁸ "
    "fine-tuning (destroying RS1 hierarchy). wₐ = 0 is the only consistent "
    "frozen-radion prediction."
)


# ─────────────────────────────────────────────────────────────────────────────
# SEPARATION GUARD
# ─────────────────────────────────────────────────────────────────────────────

def separation_guard() -> str:
    return ("🔵 ADJACENT TRACK — HARDGATE_ADJACENT. Pillar 336 implements the "
            "preregistered DESI DR3 routing engine for the P4 wₐ=0 prediction. "
            "No new physics claims beyond P4 (HARDGATE DERIVED). "
            "Epistemic status: DERIVED (wₐ=0). HIGH_TENSION at 2.75σ (DESI DR2). "
            "Falsifier: DESI DR3 ~2027.")


# ─────────────────────────────────────────────────────────────────────────────
# CURRENT TENSION ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def current_tension_analysis() -> dict:
    """Return the current tension state from DESI DR2."""
    return {
        "um_prediction_wa": W_A_UM,
        "desi_dr2_bao_only": {
            "wa_central": WA_DESI_DR2_BAO_ONLY,
            "wa_sigma": WA_DESI_DR2_BAO_ONLY_SIGMA,
            "tension_sigma": TENSION_DR2_BAO_ONLY,
            "verdict": "HIGH_TENSION",
        },
        "desi_dr2_combined": {
            "wa_central": WA_DESI_DR2_COMBINED,
            "wa_sigma": WA_DESI_DR2_COMBINED_SIGMA,
            "tension_sigma": TENSION_DR2_COMBINED,
            "verdict": "HIGH_TENSION",
        },
        "falsification_condition": (
            "DESI DR3 wₐ ≠ 0 at ≥3σ measured significance → FALSIFIED"
        ),
        "architecture_limit": ARCHITECTURE_LIMIT_NOTE,
        "status": "HIGH_TENSION — not yet falsified",
    }


def tension_from_wa(wa_measured: float, wa_sigma: float) -> float:
    """Return tension in σ between wₐ=0 and a measurement.

    Args:
        wa_measured: Central value of measured wₐ.
        wa_sigma: 1σ uncertainty on wₐ.

    Returns:
        Tension in σ (|wₐ_meas - 0| / σ_wₐ).
    """
    return abs(wa_measured - W_A_UM) / wa_sigma


# ─────────────────────────────────────────────────────────────────────────────
# BAYESIAN UPDATE
# ─────────────────────────────────────────────────────────────────────────────

def log_likelihood_wa_zero(wa_measured: float, wa_sigma: float) -> float:
    """Return log-likelihood of wₐ=0 given measurement.

    log L(wₐ=0 | data) = -0.5 × (wₐ_meas / σ_wₐ)²
    """
    return -0.5 * (wa_measured / wa_sigma) ** 2


def log_evidence_lcdm_wa_free(wa_measured: float,
                               wa_sigma: float,
                               wa_prior_low: float = WA_PRIOR_LOW,
                               wa_prior_high: float = WA_PRIOR_HIGH) -> float:
    """Return log-evidence for ΛCDM with wₐ free (flat prior over [wa_low, wa_high]).

    Uses analytic Gaussian integral:
    Z_ΛCDM = ∫ exp(-0.5 (wₐ - wₐ_meas)²/σ²) × 1/(wa_high-wa_low) dwₐ
           = √(2π) σ / (wa_high - wa_low) × [Φ(u_high) - Φ(u_low)]
    where Φ is the CDF and u = (wa - wa_meas) / σ.
    """
    prior_width = wa_prior_high - wa_prior_low
    # Gaussian integral over the prior range
    def _norm_cdf(x: float) -> float:
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    u_high = (wa_prior_high - wa_measured) / wa_sigma
    u_low = (wa_prior_low - wa_measured) / wa_sigma
    cdf_fraction = _norm_cdf(u_high) - _norm_cdf(u_low)
    sqrt_2pi = math.sqrt(2 * math.pi)
    evidence = sqrt_2pi * wa_sigma * cdf_fraction / prior_width
    if evidence <= 0:
        return -1e30
    return math.log(evidence)


def log_bayes_factor_um_vs_lcdm(wa_measured: float,
                                  wa_sigma: float) -> float:
    """Return log Bayes factor ln(B) = ln(Z_UM / Z_ΛCDM).

    Positive: UM favoured; Negative: ΛCDM favoured.
    """
    log_z_um = log_likelihood_wa_zero(wa_measured, wa_sigma)
    log_z_lcdm = log_evidence_lcdm_wa_free(wa_measured, wa_sigma)
    return log_z_um - log_z_lcdm


def jeffreys_scale(log_bf: float) -> str:
    """Classify Bayes factor strength using Jeffreys scale."""
    abs_lbf = abs(log_bf)
    direction = "UM" if log_bf > 0 else "ΛCDM"
    if abs_lbf < 1.0:
        strength = "not_worth_a_bare_mention"
    elif abs_lbf < 2.5:
        strength = "substantial"
    elif abs_lbf < 5.0:
        strength = "strong"
    else:
        strength = "decisive"
    return f"{strength} evidence for {direction}"


def posterior_probability_wa_zero(wa_measured: float,
                                   wa_sigma: float,
                                   prior_p_um: float = 0.5) -> float:
    """Return P(wₐ=0 | data) using Bayes theorem.

    P(UM | D) = P(D | UM) P(UM) / [P(D | UM) P(UM) + P(D | ΛCDM) P(ΛCDM)]

    Args:
        wa_measured: Measured wₐ central value.
        wa_sigma: 1σ uncertainty.
        prior_p_um: Prior probability of UM (default 0.5).

    Returns:
        Posterior probability P(wₐ=0 | data) ∈ [0, 1].
    """
    log_bf = log_bayes_factor_um_vs_lcdm(wa_measured, wa_sigma)
    # B = Z_UM / Z_ΛCDM; posterior = B × prior_um / (B × prior_um + prior_lcdm)
    B = math.exp(log_bf)
    p_lcdm = 1.0 - prior_p_um
    denom = B * prior_p_um + p_lcdm
    if denom <= 0:
        return 0.0
    return B * prior_p_um / denom


# ─────────────────────────────────────────────────────────────────────────────
# THREE-BRANCH ROUTING
# ─────────────────────────────────────────────────────────────────────────────

def route_desi_dr3(wa_measured: float,
                   wa_sigma: float,
                   data_label: str = "DESI DR3") -> dict:
    """Route a DESI DR3 result to a verdict.

    Args:
        wa_measured: Measured wₐ central value.
        wa_sigma: 1σ uncertainty on wₐ.
        data_label: Label for the data release (default "DESI DR3").

    Returns:
        Dict with verdict, Bayesian analysis, and required actions.
    """
    tension = tension_from_wa(wa_measured, wa_sigma)
    log_bf = log_bayes_factor_um_vs_lcdm(wa_measured, wa_sigma)
    post_p_um = posterior_probability_wa_zero(wa_measured, wa_sigma)
    j_scale = jeffreys_scale(log_bf)

    # Three-branch routing
    if tension >= FALSIFIED_SIGMA:
        verdict = "FALSIFIED"
        actions = [
            f"Mark P4 wₐ=0 prediction FALSIFIED in CLAIM_MASTER_BOARD.md ({data_label})",
            f"wₐ = {wa_measured:.3f} ± {wa_sigma:.3f} at {tension:.1f}σ from zero",
            "Mark Pillar 301 ARCHITECTURE_LIMIT note as TENSION_CONFIRMED",
            "Update OBSERVATION_TRACKER.md P4 same day",
            "Update WAVE_CHANGELOG.md with FALSIFIED entry",
            "Open retraction issue for P4 DERIVED status",
        ]
    elif tension >= TENSION_SIGMA_LOW:
        verdict = "HIGH_TENSION"
        actions = [
            f"Update OBSERVATION_TRACKER.md P4: tension now {tension:.2f}σ ({data_label})",
            f"wₐ = {wa_measured:.3f} ± {wa_sigma:.3f} — not yet falsified at ≥3σ",
            "Escalate monitoring. Note in CLAIM_MASTER_BOARD.md header.",
            "Await DESI DR4 / CMB-S4 for definitive resolution.",
        ]
    else:
        verdict = "RESOLVED"
        actions = [
            f"Update OBSERVATION_TRACKER.md P4: tension RESOLVED to {tension:.2f}σ ({data_label})",
            "DR2 tension was statistical fluctuation. wₐ=0 CONSISTENT.",
            "Update CLAIM_MASTER_BOARD.md P4 note: tension resolved.",
        ]

    return {
        "pillar": 336,
        "experiment": data_label,
        "wa_measured": wa_measured,
        "wa_sigma": wa_sigma,
        "wa_um_prediction": W_A_UM,
        "tension_sigma": round(tension, 3),
        "verdict": verdict,
        "log_bayes_factor": round(log_bf, 3),
        "jeffreys_scale": j_scale,
        "posterior_p_um": round(post_p_um, 4),
        "required_actions": actions,
        "routing_protocol": "Pillar 336 v11.18",
    }


# ─────────────────────────────────────────────────────────────────────────────
# DR3 SCENARIO ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def dr3_scenario_matrix() -> dict:
    """Compute routing verdicts for representative DR3 scenarios."""
    scenarios = [
        {"wa": -0.80, "sigma": WA_SIGMA_DR3_PROJECTED, "label": "tension_increased"},
        {"wa": -0.55, "sigma": WA_SIGMA_DR3_PROJECTED, "label": "tension_maintained"},
        {"wa": -0.40, "sigma": WA_SIGMA_DR3_PROJECTED, "label": "tension_reduced"},
        {"wa": -0.20, "sigma": WA_SIGMA_DR3_PROJECTED, "label": "tension_resolved"},
        {"wa": 0.00, "sigma": WA_SIGMA_DR3_PROJECTED, "label": "exact_um_prediction"},
    ]

    results = {}
    for sc in scenarios:
        route = route_desi_dr3(sc["wa"], sc["sigma"], f"DESI DR3 ({sc['label']})")
        results[sc["label"]] = {
            "wa": sc["wa"],
            "tension_sigma": route["tension_sigma"],
            "verdict": route["verdict"],
            "log_bf": route["log_bayes_factor"],
            "posterior_p_um": route["posterior_p_um"],
        }
    return results


def desi_dr3_readiness_report() -> dict:
    """Return the DR3 readiness status."""
    tension = current_tension_analysis()
    scenarios = dr3_scenario_matrix()

    # Check if wₐ=-0.55 at DR3 precision is falsifying
    route_maintained = route_desi_dr3(WA_DESI_DR2_COMBINED, WA_SIGMA_DR3_PROJECTED)

    return {
        "pillar": 336,
        "title": "DESI DR3 Real-Time Routing Engine",
        "adjacency": "HARDGATE_ADJACENT",
        "current_tension": tension,
        "dr3_scenario_matrix": scenarios,
        "if_tension_maintained_at_dr3_precision": route_maintained,
        "um_prediction": {"wa": W_A_UM, "w0": W_0_UM},
        "architecture_limit": ARCHITECTURE_LIMIT_NOTE,
        "execution": "Call route_desi_dr3(wa_measured, wa_sigma) on DR3 publication day",
        "separation_guard": separation_guard(),
    }


def desi_full_report() -> dict:
    """Return the complete Pillar 336 DESI DR3 routing engine report."""
    return desi_dr3_readiness_report()
