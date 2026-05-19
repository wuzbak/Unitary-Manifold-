# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 285 — Dark Energy Extension Specification (v2.0 contingency architecture).

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

════════════════════════════════════════════════════════════════════════════════
PURPOSE
════════════════════════════════════════════════════════════════════════════════
The Unitary Manifold (UM) predicts wₐ = 0 exactly from the frozen Goldberger-
Wise (GW) radion: the KK radion mass m_r >> H₀ (ratio ~10⁶⁰), preventing any
cosmological evolution.  DESI DR2 (arXiv:2503.14738) reports wₐ ≈ −0.55 ± 0.20
(combined), a tension of 2.75σ — well below the 3σ falsification threshold.

This pillar provides the pre-specified theoretical extension architecture that
would be required if DESI DR3/Y5 (~2027) crosses the 3σ threshold and formally
falsifies the frozen-radion mechanism.  It is NOT a rescue or weakening of the
current prediction — it is the honest scientific response to potential
falsification: specifying *in advance* what a v2.0 revision would need.

This is equivalent to a pre-registration:  if wₐ ≠ 0 is confirmed at ≥ 3σ,
the repository's theoretical response is already specified here in executable,
falsifiable terms.  The specification covers four candidate extensions, each
with quantitative constraints on the new parameters they require.

════════════════════════════════════════════════════════════════════════════════
CURRENT STATUS (DESI DR2 — NOT FALSIFIED)
════════════════════════════════════════════════════════════════════════════════
- wₐ-only tension:         2.75σ (combined BAO+CMB+SNe) — HIGH_TENSION
- Covariance-corrected:    2.82σ (ρ = −0.80) — HIGH_TENSION
- Falsification threshold: 3.0σ
- Framework status:        NOT FALSIFIED

════════════════════════════════════════════════════════════════════════════════
FOUR CANDIDATE EXTENSIONS (if DR3 falsifies wₐ = 0)
════════════════════════════════════════════════════════════════════════════════

EXTENSION 1 — New Bulk Scalar (quintessence in the RS1 bulk)
  A canonically normalised bulk scalar φ̃ with potential V(φ̃) rolling on the
  Hubble timescale.  Requirements: sub-Planckian displacement (Δφ̃/M_Pl < 1),
  Breitenlöhner-Freedman bound (m₅² > −4k² in AdS₅), no destabilisation of
  the GW stabiliser.  The coupling ε_φ̃ to the GW sector must be < 0.01.

EXTENSION 2 — Cosmological Radion (light-mass scenario)
  Relax the GW stabilisation to allow a cosmologically light radion m_r ~ H₀.
  This directly contradicts the hierarchy solution (M_Pl vs 1 TeV) — the
  framework would need a new stabilisation mechanism or an explicit hierarchy
  revision.  This is the most drastic option; it dismantles the RS1 solution.

EXTENSION 3 — k-Essence / Modified Kinetic Term
  A bulk scalar with a non-canonical kinetic term X^n (k-essence) in the RS1
  geometry.  Can produce wₐ ≠ 0 with sub-Planckian displacements if n > 1.
  The sound speed c_s² = 1/(2n−1) must remain positive (stability) and must
  not conflict with the braided sound speed c_s = 12/37 from Pillar 27.

EXTENSION 4 — Coupled Dark Energy (KK–dark sector interaction)
  Introduce an explicit coupling between the KK dark-energy sector and dark
  matter, parametrised by a coupling β_DE.  Produces an effective wₐ_eff ≠ 0
  even with a frozen radion.  Requires β_DE < 0.1 from CMB growth-rate bounds
  and must not violate equivalence-principle tests.

════════════════════════════════════════════════════════════════════════════════
LINKAGE
════════════════════════════════════════════════════════════════════════════════
- src/core/pillar_desi_tension_monitor.py   — corrected tension monitor (v11.x)
- src/core/pillar266_desi_wa_frozen_radion.py — frozen-radion wₐ bound
- src/core/desi_dr2_gap_report.py           — DR2 routing execution
- src/core/desi_dr3_full_analysis.py        — DR3 scenario projections
- src/core/desi_dr3_decision_matrix.py      — DR3 decision matrix
- src/core/desi_dr3_publication_day_runbook.py — publication-day protocol
- docs/CLAIM_MASTER_BOARD.md (Lane C, T1)  — canonical tension tracking
- docs/TRUTH_LAYER.md §3 T1                — full derivation context
- FALLIBILITY.md                            — honest gap accounting

════════════════════════════════════════════════════════════════════════════════

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

__all__ = [
    # Constants
    "UM_WA_PREDICTION",
    "FALSIFICATION_THRESHOLD_SIGMA",
    "DESI_DR2_COMBINED",
    "DESI_DR3_FORECAST_SIGMA",
    # Physics bounds
    "GW_COUPLING_BOUND",
    "BF_BOUND_ADS5",
    "SUPER_PLANCKIAN_THRESHOLD",
    "BRAIDED_SOUND_SPEED",
    # Extension functions
    "bulk_scalar_extension_constraints",
    "cosmological_radion_constraints",
    "k_essence_extension_constraints",
    "coupled_dark_energy_constraints",
    "dr3_falsification_check",
    "extension_viability_ranking",
    "extension_specification_report",
]

# ─────────────────────────────────────────────────────────────────────────────
# Physical constants and baseline data
# ─────────────────────────────────────────────────────────────────────────────

UM_WA_PREDICTION: float = 0.0        # Frozen GW radion: wₐ ≡ 0 exactly
FALSIFICATION_THRESHOLD_SIGMA: float = 3.0  # Honest: ≥ 3σ → FALSIFIED

# DESI DR2 BAO+CMB+SNe combined (arXiv:2503.14738, 2025)
DESI_DR2_COMBINED: Dict = {
    "release": "DESI DR2",
    "wa_central": -0.55,
    "wa_sigma": 0.20,
    "w0_central": -0.90,
    "w0_sigma": 0.055,
    "wa_tension_sigma": 2.75,   # wₐ-only: |−0.55|/0.20
    "status": "HIGH_TENSION",
    "reference": "DESI Collaboration (2025), arXiv:2503.14738",
}

# DESI Y5 / DR3 forecast precision (~2027)
DESI_DR3_FORECAST_SIGMA: float = 0.15  # Expected σ_wₐ improvement from DR2 0.20

# ─────────────────────────────────────────────────────────────────────────────
# RS1 geometry constraints (any extension must respect these)
# ─────────────────────────────────────────────────────────────────────────────

#: Maximum allowed coupling of any new field to the GW stabiliser (dimensionless).
#: Exceeding this destabilises the GW mechanism.
GW_COUPLING_BOUND: float = 0.01

#: Breitenlöhner-Freedman bound for a bulk scalar in AdS₅.
#: m₅² > −4k²; we parametrise this as m₅²/k² > −4.
BF_BOUND_ADS5: float = -4.0

#: Super-Planckian displacement threshold (in units of M_Pl).
#: Δφ̃/M_Pl ≥ 1 signals EFT breakdown.
SUPER_PLANCKIAN_THRESHOLD: float = 1.0

#: Braided sound speed from Pillar 27 (c_s = 12/37).
#: Any new extension must not conflict with this measured/derived value.
BRAIDED_SOUND_SPEED: float = 12.0 / 37.0   # ≈ 0.3243


# ─────────────────────────────────────────────────────────────────────────────
# Extension 1: New bulk scalar in RS1 geometry
# ─────────────────────────────────────────────────────────────────────────────

def bulk_scalar_extension_constraints(
    wa_target: float = -0.55,
    sigma_wa: float = 0.20,
    gw_coupling: float = GW_COUPLING_BOUND,
) -> Dict:
    """Constraints on a new canonically-normalised bulk scalar that generates wₐ ≠ 0.

    To produce wₐ ≈ wa_target via a canonical quintessence field φ̃ rolling in
    the RS1 bulk, we need:

        (1 + w) ≈ φ̃̇² / (2V) → require (1+w) = |wₐ|/2 for tracker solution
        Δφ̃/M_Pl ≥ √(2·|wₐ|/2) = √|wₐ|

    The field must satisfy:
        - Sub-Planckian displacement: Δφ̃/M_Pl < 1
        - BF bound: m₅² > −4k²
        - GW coupling ε_φ̃ < GW_COUPLING_BOUND (no destabilisation)
        - KK spectrum of φ̃ must not produce collider-excluded light states

    Parameters
    ----------
    wa_target : float
        Target wₐ to be explained (e.g. DESI DR2 combined central value −0.55).
    sigma_wa : float
        Observational uncertainty on wₐ.
    gw_coupling : float
        Assumed coupling of the new field to the GW stabiliser.

    Returns
    -------
    dict
        Quantitative constraints, viability, and conclusions.
    """
    required_one_plus_w = abs(wa_target) / 2.0
    required_field_displacement = math.sqrt(2.0 * required_one_plus_w)
    is_super_planckian = required_field_displacement >= SUPER_PLANCKIAN_THRESHOLD

    # BF-bound check: mass of new scalar in AdS₅
    # For a tracker field with slow-roll parameter ε ~ (1+w)/2 ~ |wₐ|/4,
    # the 5D mass squared m₅² ~ −|wₐ|·k²; must satisfy m₅²/k² > −4 (BF bound)
    m5_squared_over_k2 = -abs(wa_target)
    bf_bound_satisfied = m5_squared_over_k2 > BF_BOUND_ADS5

    # GW stability: coupling must be small
    gw_stable = gw_coupling < GW_COUPLING_BOUND + 1e-10

    # Minimum 5D mass for KK spectrum to avoid m_0 < 100 GeV (collider excluded)
    # First KK mode of new scalar: m₁^KK = k·exp(−πkR) × √(m₅²/k²+4)
    # with πkR = 37: exp(−37) ≈ 8.53×10⁻¹⁷
    rs_factor = math.exp(-37.0)
    k_gev = 1e18  # IR brane scale ~M_Pl
    m1_kk_gev = k_gev * rs_factor * math.sqrt(max(m5_squared_over_k2 + 4.0, 0.001))
    collider_safe = m1_kk_gev > 100.0  # above LEP bound

    viable = bf_bound_satisfied and gw_stable and not is_super_planckian

    return {
        "extension": "BULK_SCALAR_QUINTESSENCE",
        "wa_target": wa_target,
        "required_one_plus_w": required_one_plus_w,
        "required_field_displacement_mpl": required_field_displacement,
        "is_super_planckian": is_super_planckian,
        "super_planckian_threshold": SUPER_PLANCKIAN_THRESHOLD,
        "m5_squared_over_k2": m5_squared_over_k2,
        "bf_bound_ads5": BF_BOUND_ADS5,
        "bf_bound_satisfied": bf_bound_satisfied,
        "gw_coupling_input": gw_coupling,
        "gw_coupling_bound": GW_COUPLING_BOUND,
        "gw_stable": gw_stable,
        "m1_kk_gev": m1_kk_gev,
        "collider_safe": collider_safe,
        "viable": viable,
        "viability_gate": "sub-Planckian + BF + GW-stable",
        "conclusion": (
            f"To generate wₐ ≈ {wa_target}, a new bulk scalar requires "
            f"Δφ̃/M_Pl ≥ {required_field_displacement:.3f}. "
            + ("SUPER-PLANCKIAN: EFT breakdown. " if is_super_planckian else "Sub-Planckian: EFT valid. ")
            + ("BF bound: SATISFIED. " if bf_bound_satisfied else "BF bound: VIOLATED. ")
            + ("GW: STABLE. " if gw_stable else "GW: DESTABILISED. ")
            + f"Overall viability: {'VIABLE (contingent)' if viable else 'NOT VIABLE'}."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Extension 2: Cosmological radion (relaxed GW stabilisation)
# ─────────────────────────────────────────────────────────────────────────────

def cosmological_radion_constraints(
    m_radion_over_hubble_target: float = 1.0,
    m_kk_gev: float = 1e3,
) -> Dict:
    """Constraints if the radion were cosmologically light (m_r ~ H₀).

    The standard GW mechanism gives m_r/H₀ ~ 10⁶⁰, completely freezing the
    radion.  For wₐ ≠ 0, one would need m_r ~ H₀, which requires either:
        (a) A GW tuning to ε_GW ~ (H₀/M_KK)² ~ 10⁻¹²²
        (b) An entirely new stabilisation mechanism that allows light radion

    This is the most drastic extension — it dismantles the RS1 hierarchy
    solution and requires a fundamentally different stabilisation mechanism.
    The cosmological constant problem returns in a new form (tuning ε_GW).

    Parameters
    ----------
    m_radion_over_hubble_target : float
        Target ratio m_r/H₀ (default 1.0 for maximal rolling).
    m_kk_gev : float
        KK mass scale in GeV (default 1 TeV).

    Returns
    -------
    dict
        Required GW tuning, hierarchy implications, and viability verdict.
    """
    h0_gev = 1.44e-42  # H₀ in GeV

    # Required radion mass
    m_r_gev_target = m_radion_over_hubble_target * h0_gev

    # Standard GW radion mass: m_r = √ε_GW × M_KK
    # For m_r = h0: ε_GW = (H₀/M_KK)²
    eps_gw_required = (m_r_gev_target / m_kk_gev) ** 2

    # Standard GW value: ε_GW ~ 0.01 (i.e. m_r ~ 0.1 M_KK)
    eps_gw_standard = 0.01
    tuning_severity = eps_gw_standard / max(eps_gw_required, 1e-300)

    # Does this reintroduce the hierarchy problem?
    hierarchy_maintained = m_kk_gev >= 1e3  # need M_KK ~ TeV for hierarchy

    # Phenomenological constraint: light radion couples to SM via Brans-Dicke
    # parameter ω_BD. For m_r ~ H₀ the field is still on cosmological timescales
    # but the Brans-Dicke constraint requires ω_BD > 40,000 (Cassini bound).
    # This translates to: (φ_0/M_Pl)² < 1/(2ω_BD) < 1.25×10⁻⁵
    # — a severe constraint on the RS1 zero-mode coupling.
    brans_dicke_constraint = "φ₀/M_Pl < 3.5×10⁻³ (Cassini bound ω_BD > 40,000)"

    return {
        "extension": "COSMOLOGICAL_RADION",
        "m_radion_over_hubble_target": m_radion_over_hubble_target,
        "m_r_gev_required": m_r_gev_target,
        "m_kk_gev": m_kk_gev,
        "eps_gw_standard": eps_gw_standard,
        "eps_gw_required_for_light_radion": eps_gw_required,
        "tuning_severity_factor": tuning_severity,
        "hierarchy_maintained": hierarchy_maintained,
        "viable": False,  # Fundamentally incompatible with RS1 hierarchy solution
        "brans_dicke_constraint": brans_dicke_constraint,
        "conclusion": (
            "A cosmologically light radion (m_r ~ H₀) requires ε_GW ≈ "
            f"{eps_gw_required:.2e}, tuned by a factor {tuning_severity:.2e} "
            "relative to the standard GW value. This directly dismantles the "
            "RS1 hierarchy solution and reintroduces the naturalness problem "
            "in a new form. This extension is NOT VIABLE within the current "
            "UM framework — it would require a fundamentally new stabilisation "
            "mechanism and a new framework-level response."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Extension 3: k-Essence with non-canonical kinetic term
# ─────────────────────────────────────────────────────────────────────────────

def k_essence_extension_constraints(
    n_kinetic: float = 2.0,
    wa_target: float = -0.55,
) -> Dict:
    """Constraints on a k-essence bulk scalar with kinetic term X^n.

    For a k-essence Lagrangian L = X^n − V in the RS1 bulk, the equation of
    state is:
        w = (2n − 1)X^n − V) / ((2n−1)X^n + V)
        c_s² = 1 / (2n − 1)

    For n = 1: reduces to canonical scalar (c_s² = 1).
    For n > 1: c_s² < 1, can produce |wₐ| ~ O(1) with sub-Planckian displacement.

    Constraint: c_s² must be positive (stability) and must not conflict with
    the measured braided sound speed c_s = 12/37 from Pillar 27.

    Parameters
    ----------
    n_kinetic : float
        Power of kinetic term X^n (n = 1 is canonical; n > 1 is k-essence).
    wa_target : float
        Target wₐ value.

    Returns
    -------
    dict
        Sound speed, stability, conflict with Pillar 27, and viability.
    """
    if n_kinetic < 1.0:
        raise ValueError("n_kinetic must be >= 1.0 (n=1 is canonical scalar).")

    # k-essence sound speed
    cs_squared = 1.0 / (2.0 * n_kinetic - 1.0)
    cs = math.sqrt(max(cs_squared, 0.0))

    # Stability: c_s² > 0 (gradient stability)
    gradient_stable = cs_squared > 0.0

    # Causality: c_s ≤ 1
    causal = cs <= 1.0 + 1e-9

    # Conflict with braided sound speed c_s = 12/37?
    # The Pillar 27 derivation ties the observed c_s to the (5,7) braid resonance.
    # A k-essence field with a different c_s would need to be decoupled from the
    # braided inflation sector.  Tolerance: |c_s − 12/37| > 0.05 is discriminable.
    cs_conflict = abs(cs - BRAIDED_SOUND_SPEED) < 0.05 and n_kinetic != 1.0

    # Required displacement for wₐ generation (reduced vs canonical because X^n enhances
    # the kinetic contribution): Δφ̃/M_Pl ≥ √(|wₐ|/(2n−1))
    required_displacement = math.sqrt(abs(wa_target) / (2.0 * n_kinetic - 1.0))
    is_super_planckian = required_displacement >= SUPER_PLANCKIAN_THRESHOLD

    viable = gradient_stable and causal and not is_super_planckian and not cs_conflict

    return {
        "extension": "K_ESSENCE_BULK_SCALAR",
        "n_kinetic": n_kinetic,
        "wa_target": wa_target,
        "cs_squared": cs_squared,
        "cs": cs,
        "gradient_stable": gradient_stable,
        "causal": causal,
        "braided_sound_speed": BRAIDED_SOUND_SPEED,
        "cs_conflict_with_pillar27": cs_conflict,
        "required_field_displacement_mpl": required_displacement,
        "is_super_planckian": is_super_planckian,
        "viable": viable,
        "conclusion": (
            f"k-Essence with n={n_kinetic}: c_s² = {cs_squared:.4f} (c_s = {cs:.4f}). "
            + ("Gradient stable. " if gradient_stable else "UNSTABLE (c_s² ≤ 0). ")
            + ("Causal. " if causal else "SUPERLUMINAL. ")
            + ("Pillar-27 conflict. " if cs_conflict else "No Pillar-27 conflict. ")
            + f"Required displacement: {required_displacement:.3f} M_Pl "
            + ("(super-Planckian). " if is_super_planckian else "(sub-Planckian). ")
            + f"Viability: {'VIABLE (contingent)' if viable else 'NOT VIABLE'}."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Extension 4: Coupled dark energy (KK–dark matter interaction)
# ─────────────────────────────────────────────────────────────────────────────

def coupled_dark_energy_constraints(
    beta_de: float = 0.05,
    wa_target: float = -0.55,
) -> Dict:
    """Constraints on a coupled dark energy model (KK + dark matter interaction).

    An explicit coupling β_DE between the KK dark-energy sector and dark matter
    produces an effective wₐ_eff ≠ 0 even with a frozen radion.  The effective
    equation of state evolves as:

        wₐ_eff ≈ −6β_DE² × Ω_m(z=0)      [leading order in β_DE]

    Observational constraints:
        - CMB growth-rate (f·σ₈): β_DE < 0.1 (Planck 2018 + galaxy surveys)
        - Equivalence principle: β_DE < 0.05 (clock-comparison tests)
        - ISW effect: β_DE < 0.2 (conservative)

    Parameters
    ----------
    beta_de : float
        Dimensionless coupling strength between KK dark energy and dark matter.
    wa_target : float
        Target wₐ_eff (DESI DR2 combined central value −0.55).

    Returns
    -------
    dict
        Constraints, required coupling, viability, and conclusions.
    """
    omega_m = 0.315  # Planck 2018

    # Effective wₐ from coupling
    wa_eff = -6.0 * beta_de**2 * omega_m

    # Required coupling to match target wₐ
    # |wa_target| = 6 β_DE² Ω_m → β_DE = √(|wa_target| / (6 Ω_m))
    beta_required = math.sqrt(abs(wa_target) / (6.0 * omega_m))

    # Observational bounds on β_DE
    cmb_growth_bound = 0.10       # from CMB f·σ₈ + galaxy surveys
    equivalence_principle_bound = 0.05  # from solar-system / clock tests
    isw_bound = 0.20

    cmb_safe = beta_required < cmb_growth_bound
    ep_safe = beta_required < equivalence_principle_bound
    isw_safe = beta_required < isw_bound

    viable = cmb_safe  # minimum: CMB growth-rate constraint

    return {
        "extension": "COUPLED_DARK_ENERGY",
        "beta_de_input": beta_de,
        "wa_eff_from_input_beta": wa_eff,
        "wa_target": wa_target,
        "beta_de_required_for_target": beta_required,
        "omega_m": omega_m,
        "cmb_growth_bound": cmb_growth_bound,
        "equivalence_principle_bound": equivalence_principle_bound,
        "isw_bound": isw_bound,
        "cmb_growth_safe": cmb_safe,
        "equivalence_principle_safe": ep_safe,
        "isw_safe": isw_safe,
        "viable": viable,
        "conclusion": (
            f"Coupled dark energy (β_DE = {beta_de}): "
            f"wₐ_eff ≈ {wa_eff:.4f} from input coupling. "
            f"To match wₐ_target = {wa_target}, need β_DE ≈ {beta_required:.4f}. "
            + ("CMB growth: SAFE. " if cmb_safe else "CMB growth: EXCLUDED. ")
            + ("Equiv-principle: SAFE. " if ep_safe else "Equiv-principle: CONSTRAINED. ")
            + f"Viability: {'VIABLE (contingent)' if viable else 'NOT VIABLE'}."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# DR3 falsification check
# ─────────────────────────────────────────────────────────────────────────────

def dr3_falsification_check(
    wa_dr3: float,
    sigma_dr3: float,
) -> Dict:
    """Check whether a hypothetical DESI DR3/Y5 result falsifies wₐ = 0.

    Parameters
    ----------
    wa_dr3 : float
        DESI DR3 central value of wₐ.
    sigma_dr3 : float
        DESI DR3 1σ uncertainty on wₐ.

    Returns
    -------
    dict
        Tension in sigma, verdict (PASS / TENSION / HIGH_TENSION / FALSIFIED),
        and required action.
    """
    if sigma_dr3 <= 0:
        raise ValueError("sigma_dr3 must be positive.")
    tension = abs(wa_dr3 - UM_WA_PREDICTION) / sigma_dr3
    if tension >= FALSIFICATION_THRESHOLD_SIGMA:
        verdict = "FALSIFIED"
        action = (
            "IMMEDIATE: Update CLAIM_MASTER_BOARD.md (T1 → FALSIFIED), "
            "TRUTH_LAYER.md §3, GATEKEEPER_SUMMARY.md, WAVE_CHANGELOG.md, "
            "and OBSERVATION_TRACKER.md same day. "
            "Activate extension specification from Pillar 285. "
            "Specify which extension (1–4) to pursue and begin v2.0 architecture."
        )
        extension_activated = True
    elif tension >= 2.5:
        verdict = "HIGH_TENSION"
        action = "Escalate monitoring. Update all T1 status fields to HIGH_TENSION."
        extension_activated = False
    elif tension >= 2.1:
        verdict = "TENSION"
        action = "Maintain HIGH_TENSION. Continue DESI monitoring cycle."
        extension_activated = False
    else:
        verdict = "RESOLVED"
        action = "Downgrade T1 to PASS. Record resolution in WAVE_CHANGELOG.md."
        extension_activated = False

    return {
        "wa_dr3": wa_dr3,
        "sigma_dr3": sigma_dr3,
        "wa_prediction": UM_WA_PREDICTION,
        "tension_sigma": tension,
        "falsification_threshold": FALSIFICATION_THRESHOLD_SIGMA,
        "verdict": verdict,
        "extension_activated": extension_activated,
        "action": action,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Extension viability ranking
# ─────────────────────────────────────────────────────────────────────────────

def extension_viability_ranking(wa_target: float = -0.55) -> List[Dict]:
    """Rank the four extensions by theoretical viability if wₐ ≠ 0 is confirmed.

    Parameters
    ----------
    wa_target : float
        Observed wₐ to be explained (default: DESI DR2 combined −0.55).

    Returns
    -------
    list[dict]
        Extensions sorted from most to least viable, with rankings.
    """
    ext1 = bulk_scalar_extension_constraints(wa_target=wa_target)
    ext2 = cosmological_radion_constraints()
    ext3 = k_essence_extension_constraints(n_kinetic=3.0, wa_target=wa_target)
    ext4 = coupled_dark_energy_constraints(beta_de=0.05, wa_target=wa_target)

    ranked = [
        {
            "rank": None,
            "name": ext1["extension"],
            "viable": ext1["viable"],
            "viability_note": (
                "Sub-Planckian if |wₐ| < 1; BF-bound satisfied for typical CPL values; "
                "requires new action term beyond current 5D UM action."
            ),
            "disruption_level": "MODERATE",
            "detail": ext1,
        },
        {
            "rank": None,
            "name": ext3["extension"],
            "viable": ext3["viable"],
            "viability_note": (
                "k-Essence with n≥2 allows sub-Planckian displacement and c_s² > 0; "
                "must not conflict with braided sound speed (Pillar 27)."
            ),
            "disruption_level": "MODERATE",
            "detail": ext3,
        },
        {
            "rank": None,
            "name": ext4["extension"],
            "viable": ext4["viable"],
            "viability_note": (
                "Coupled dark energy can produce wₐ_eff ≠ 0 from frozen radion; "
                "CMB growth-rate and equivalence-principle bounds are tight."
            ),
            "disruption_level": "LOW_TO_MODERATE",
            "detail": ext4,
        },
        {
            "rank": None,
            "name": ext2["extension"],
            "viable": ext2["viable"],
            "viability_note": (
                "Cosmological radion requires enormous GW tuning (~10¹²² fine-tuning); "
                "dismantles RS1 hierarchy solution — framework-level revision needed."
            ),
            "disruption_level": "EXTREME",
            "detail": ext2,
        },
    ]

    # Assign ranks: prefer viable + lower disruption
    disruption_order = {"LOW_TO_MODERATE": 0, "MODERATE": 1, "EXTREME": 2}
    ranked.sort(key=lambda x: (not x["viable"], disruption_order.get(x["disruption_level"], 9)))
    for i, ext in enumerate(ranked):
        ext["rank"] = i + 1

    return ranked


# ─────────────────────────────────────────────────────────────────────────────
# Full extension specification report
# ─────────────────────────────────────────────────────────────────────────────

def extension_specification_report(
    wa_target: float = DESI_DR2_COMBINED["wa_central"],
) -> Dict:
    """Complete Pillar 285 extension specification report.

    Generates the full pre-specified v2.0 contingency architecture,
    including DR3 scenario analysis, extension rankings, and action protocol.

    Parameters
    ----------
    wa_target : float
        Observed wₐ to be explained (default: DESI DR2 combined −0.55).

    Returns
    -------
    dict
        Complete report for archival, documentation, and decision-making.
    """
    # Current status
    current_tension = abs(wa_target - UM_WA_PREDICTION) / DESI_DR2_COMBINED["wa_sigma"]
    current_verdict = "FALSIFIED" if current_tension >= FALSIFICATION_THRESHOLD_SIGMA else (
        "HIGH_TENSION" if current_tension >= 2.5 else "TENSION"
    )

    # DR3 scenarios: will the same central value falsify with tighter error?
    dr3_same_central = dr3_falsification_check(wa_target, DESI_DR3_FORECAST_SIGMA)
    dr3_bao_central = dr3_falsification_check(-0.62, DESI_DR3_FORECAST_SIGMA)

    # Extension analysis
    extensions = extension_viability_ranking(wa_target=wa_target)

    return {
        "pillar": "P268",
        "title": "Dark Energy Extension Specification — v2.0 Contingency Architecture",
        "status": "PRE_SPECIFIED_CONTINGENCY",
        "current_status": {
            "wa_central_desi_dr2": wa_target,
            "wa_sigma_desi_dr2": DESI_DR2_COMBINED["wa_sigma"],
            "tension_sigma": current_tension,
            "verdict": current_verdict,
            "not_yet_falsified": current_tension < FALSIFICATION_THRESHOLD_SIGMA,
        },
        "dr3_projections": {
            "combined_central_held": dr3_same_central,
            "bao_central_held": dr3_bao_central,
            "dr3_sigma_forecast": DESI_DR3_FORECAST_SIGMA,
            "note": (
                f"If DESI DR3/Y5 reports σ_wₐ ≈ {DESI_DR3_FORECAST_SIGMA} and the "
                f"combined central value {wa_target} is unchanged, tension reaches "
                f"{dr3_same_central['tension_sigma']:.2f}σ → "
                f"{dr3_same_central['verdict']}."
            ),
        },
        "extension_ranking": extensions,
        "recommended_extension_if_falsified": (
            "Extension 1 (BULK_SCALAR_QUINTESSENCE) is the least disruptive "
            "theoretically-viable option: it preserves the GW stabilisation, "
            "the RS1 hierarchy, and the frozen-radion sector, while adding a "
            "new sub-Planckian bulk scalar.  The new action term is specified "
            "in bulk_scalar_extension_constraints() and must satisfy "
            "Δφ̃/M_Pl < 1, m₅² > −4k², and ε_φ̃ < 0.01."
        ),
        "protocol_if_falsified": (
            "1. Update CLAIM_MASTER_BOARD.md (T1 → FALSIFIED) same day. "
            "2. Update TRUTH_LAYER.md §3 T1 with exact DR3 numbers. "
            "3. Update GATEKEEPER_SUMMARY.md, OBSERVATION_TRACKER.md, WAVE_CHANGELOG.md. "
            "4. Open a new hardgate pillar (v2.0 dark energy sector) using "
            "the pre-specification from Pillar 285 as the starting architecture. "
            "5. Do NOT declare the full framework falsified — only the "
            "frozen-radion dark-energy prediction is under revision. "
            "All other pillars (birefringence β, nₛ, r, SM parameters) remain "
            "valid and untouched."
        ),
        "falsification_boundary": {
            "threshold": FALSIFICATION_THRESHOLD_SIGMA,
            "statement": (
                "The frozen-radion wₐ=0 prediction is falsified if and only if "
                "a future DESI/CMB/SNe dataset gives |wₐ|/σ_wₐ ≥ 3.0σ "
                "for the wₐ-only single-parameter metric. "
                "This statement must not be weakened."
            ),
        },
        "reference_modules": [
            "src/core/pillar_desi_tension_monitor.py",
            "src/core/pillar266_desi_wa_frozen_radion.py",
            "src/core/desi_dr2_gap_report.py",
            "src/core/desi_dr3_full_analysis.py",
            "src/core/desi_dr3_decision_matrix.py",
            "src/core/desi_dr3_publication_day_runbook.py",
        ],
    }
