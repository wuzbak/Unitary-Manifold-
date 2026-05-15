# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/desi_dr3_decision_matrix.py
======================================
DESI DR3 Strategic Decision Matrix — UM Preparedness Framework.

This module provides concrete, actionable strategic guidance for the
Unitary Manifold team in response to DESI DR3 outcomes (~2027).

CONTEXT
-------
The UM predicts wₐ = 0 exactly (frozen GW-stabilised radion).
DESI DR2 (arXiv:2503.14738) gives wₐ = −0.62 ± 0.30 (~2.1σ tension).
DESI DR3 is expected ~2027 and will either resolve or sharpen this tension.

Current status is HONEST OPEN PROBLEM — not falsified but under tension.
The correct scientific path is: submit, document honestly, monitor continuously.

DECISION LOGIC
--------------
  tension < 2σ   → CONSISTENT  : promote wₐ = 0 claim
  2σ ≤ t < 3σ   → TENSION     : document and monitor
  t ≥ 3σ        → FALSIFIED   : initiate modification roadmap

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

from src.core.desi_dr3_full_analysis import (
    DESI_DR2,
    UM_WA_PREDICTION,
    UM_W0_PREDICTION,
    falsification_verdict,
    wa_tension_sigma,
)

__all__ = [
    "SUBMISSION_STRATEGY_PRE_DR3",
    "modification_roadmap_if_falsified",
    "modification_roadmap_if_tension_increases",
    "modification_roadmap_if_consistent",
    "release_day_action_protocol",
    "desi_dr3_strategic_summary",
]


# ---------------------------------------------------------------------------
# Pre-DR3 submission strategy
# ---------------------------------------------------------------------------

def SUBMISSION_STRATEGY_PRE_DR3() -> Dict:  # noqa: N802
    """Concrete recommendation on whether to submit arXiv before DESI DR3.

    Factors considered:
    1. Current tension: ~2.1σ — documented honestly, NOT falsified.
    2. Scientific integrity: honest submission with tension documented is the
       correct path; hiding open problems is not acceptable.
    3. Priority: submitting before DR3 establishes UM predictions as a priori,
       preventing post-hoc rationalisation accusations.
    4. Risk: if DR3 falsifies, the preprint will be permanently associated with
       a falsified claim — but this is preferable to not publishing at all,
       since the tension is known and documented.
    5. Community norms: 2σ tensions are routinely published with honest caveats.

    Returns
    -------
    dict
        strategy='SUBMIT_BEFORE_DR3' with full rationale.
    """
    current_tension_sigma = wa_tension_sigma(
        DESI_DR2["wa_central"], DESI_DR2["wa_sigma"], UM_WA_PREDICTION
    )

    return {
        "strategy": "SUBMIT_BEFORE_DR3",
        "recommendation": "SUBMIT arXiv preprint BEFORE DESI DR3 release.",
        "rationale": (
            "The UM wₐ = 0 prediction is a genuine a-priori prediction from the "
            "Goldberger-Wise radion stabilisation mechanism. The ~2.1σ tension "
            "with DESI DR2 is documented honestly in the manuscript as an open "
            "problem. Submitting before DR3: (1) establishes the prediction as "
            "a priori, not post-hoc; (2) allows the community to evaluate the "
            "full framework on its merits; (3) is consistent with scientific norms "
            "for 2σ-level tensions. NOT submitting would be withholding a result "
            "that passes all other consistency checks."
        ),
        "current_wa_tension_sigma": current_tension_sigma,
        "is_falsified": current_tension_sigma >= 3.0,
        "is_tension_publishable": current_tension_sigma < 3.0,
        "required_manuscript_statements": [
            (
                "wₐ = 0 is the UM prediction (frozen GW radion at m_r >> H₀). "
                "DESI DR2 gives wₐ = −0.62 ± 0.30, a ~2.1σ tension. "
                "This is documented as an honest open problem."
            ),
            (
                "The KK multi-mode correction gives |wₐ^KK| < 10⁻³² — negligible. "
                "Resolution requires either new DESI systematics or a new bulk "
                "field sector beyond the current 5D action."
            ),
            (
                "DESI DR3 (~2027) is expected to reduce σ_wₐ by ~40%. If the "
                "central value is maintained, tension will increase. This is "
                "explicitly tracked as a UM falsification condition."
            ),
        ],
        "submission_timeline": {
            "recommended_window": "Before DESI DR3 release (~2027)",
            "key_milestone": "Submit to arXiv after peer review of core claims",
            "monitoring": "Update arXiv preprint immediately upon DR3 release",
        },
        "key_falsification_condition": (
            "wₐ ≠ 0 at ≥3σ in DESI DR3 would require a new bulk field sector. "
            "This condition is explicitly stated in the submission."
        ),
    }


# ---------------------------------------------------------------------------
# Modification roadmap: if FALSIFIED (≥3σ)
# ---------------------------------------------------------------------------

def modification_roadmap_if_falsified() -> Dict:
    """If DR3 gives wₐ ≠ 0 at ≥3σ, what specifically must change in the UM?

    Maps the falsification consequence to concrete model modifications:
    (a) New bulk field sector required in the 5D action.
    (b) Which pillar would need to be opened and what constraints apply.
    (c) What observational constraints already exist on new bulk fields.

    Returns
    -------
    dict
        Concrete, complete modification roadmap with pillar mapping.
    """
    return {
        "trigger_condition": "wₐ ≠ 0 at ≥ 3σ in DESI DR3",
        "new_sector_required": True,
        "new_sector_description": (
            "A new canonically-normalised bulk scalar field Φ_Q in the RS geometry, "
            "distinct from the GW radion, with a shallow quintessence potential "
            "V(Φ_Q) and mass m_Q ~ O(H₀). This field must be consistent with:"
            "\n  (a) Breitenlohner-Freedman stability bound: m₅² > −4k²"
            "\n  (b) Absence of coupling to SM gauge sector at tree level"
            "\n  (c) KK spectrum of Φ_Q not conflicting with collider bounds"
            "\n  (d) Consistent GW minimisation: ε_GW correction remains small"
        ),
        "pillars_to_open": {
            "Pillar_155_kk_de_wa_cpl": {
                "current_status": "ANALYSED — wₐ = 0",
                "new_status": "OPEN — wₐ ≠ 0 requires new sector",
                "action": (
                    "Re-open Pillar 155. Compute wₐ from new bulk quintessence field. "
                    "The radion itself remains frozen; new field provides wₐ."
                ),
                "file": "src/core/kk_de_wa_cpl.py",
            },
            "Pillar_156_new_bulk_quintessence": {
                "current_status": "DOES NOT EXIST",
                "new_status": "MUST BE CREATED",
                "action": (
                    "Create Pillar 156: bulk_quintessence_de.py. Derive wₐ from "
                    "5D bulk field with RS warped geometry. Compute KK spectrum. "
                    "Ensure consistency with Pillar 151 (w₀) and Pillar 155 (wₐ)."
                ),
                "file": "src/core/bulk_quintessence_de.py (to be created)",
            },
            "Pillar_5D_action": {
                "current_status": "Contains GW radion only",
                "new_status": "Must be extended with bulk quintessence term",
                "action": (
                    "Add S_Q = −∫d⁵x √g [½(∂Φ_Q)² + V(Φ_Q)] to 5D action. "
                    "Verify 5D Einstein equations remain consistent. "
                    "Check backreaction on RS metric is negligible (δΩ/Ω < 10⁻³)."
                ),
            },
        },
        "existing_observational_constraints_on_new_bulk_fields": {
            "LHC_bounds": (
                "KK excitations of Φ_Q with m_KK ~ TeV would have been produced "
                "at LHC if they couple to SM. Coupling must be < 10⁻³ (indirect). "
                "Direct production cross-section bound: σ < 1 fb at √s = 13 TeV."
            ),
            "fifth_force_bounds": (
                "Sub-mm gravity experiments (Eöt-Wash) require any new scalar with "
                "m < 10⁻³ eV to have gravitational-strength coupling or weaker. "
                "The quintessence field mass m_Q ~ H₀ ~ 10⁻³³ eV satisfies this "
                "trivially as it mediates no measurable force at lab scales."
            ),
            "bbn_bounds": (
                "Extra light degrees of freedom from the new field KK tower must "
                "not exceed ΔN_eff < 0.3 (Planck 2018). For m_KK >> MeV this is "
                "automatically satisfied — KK modes are not in equilibrium at BBN."
            ),
            "cmb_isocurvature": (
                "If Φ_Q is light during inflation, it generates isocurvature "
                "perturbations. Current bound: β_iso < 0.038 (Planck 2018). "
                "Quintessence with m_Q >> H_inf avoids this constraint."
            ),
        },
        "timeline_for_modification": {
            "immediate_0_7_days": [
                "Update OBSERVATION_TRACKER.md with DR3 falsification result",
                "Issue public statement acknowledging falsification",
                "Re-open Pillar 155 as OPEN/FALSIFIED in kk_de_wa_cpl.py",
                "Update STATUS.md and FALLIBILITY.md",
            ],
            "short_term_1_3_months": [
                "Derive 5D action with bulk quintessence field",
                "Compute wₐ from bulk field slow-roll in RS geometry",
                "Check RS KK spectrum of new field against LHC bounds",
                "Write Pillar 156 module and test suite",
            ],
            "medium_term_3_12_months": [
                "Submit revised manuscript with new bulk quintessence sector",
                "Ensure w₀ is not disrupted by new sector (must remain ~−0.93)",
                "Cross-check with Pillar 5 (FTUM fixed point) for consistency",
                "Compute dark energy perturbations for CMB spectrum update",
            ],
        },
        "conclusion": (
            "Falsification at ≥3σ does NOT falsify the entire UM framework — "
            "it falsifies only the 'wₐ = 0 from radion alone' sub-claim. "
            "The geometric structure (Pillars 1–154, 156–208) remains intact. "
            "A new bulk quintessence sector would be a model extension, not a "
            "fundamental revision."
        ),
    }


# ---------------------------------------------------------------------------
# Modification roadmap: if tension increases (2–3σ)
# ---------------------------------------------------------------------------

def modification_roadmap_if_tension_increases() -> Dict:
    """2–3σ scenario: what monitoring is required; when does retraction become appropriate?

    This covers the case where DR3 increases tension from ~2.1σ to 2–3σ but
    does not reach the 3σ falsification threshold.

    Returns
    -------
    dict
        Monitoring requirements, escalation thresholds, retraction criteria.
    """
    return {
        "trigger_condition": "2.0σ ≤ tension_DR3 < 3.0σ",
        "status": "TENSION_INCREASED — not yet falsified",
        "monitoring_required": [
            "Track each new DESI data release immediately upon publication",
            "Monitor ACT/SPT CMB lensing measurements for systematic cross-checks",
            "Monitor Euclid weak lensing constraints on wₐ (first results ~2026)",
            "Monitor DESI ELG/LRG systematics publications from DESI collaboration",
            "Update desi_year3_monitor.py with every new release",
            "Re-run kk_tower_wa_exact() to confirm KK contribution remains negligible",
        ],
        "escalation_thresholds": {
            "2.0_to_2.5_sigma": {
                "action": "DOCUMENT — update all tracking files; continue monitoring",
                "retraction_appropriate": False,
                "additional_action": "Publish updated arXiv preprint with DR3 values",
            },
            "2.5_to_3.0_sigma": {
                "action": "ALERT — notify co-authors; increase monitoring frequency",
                "retraction_appropriate": False,
                "additional_action": (
                    "Request independent systematic analysis from DESI collaboration. "
                    "Begin preparing the modification roadmap (Pillar 156)."
                ),
            },
        },
        "retraction_criteria": {
            "threshold_for_retraction": "≥ 3.0σ in a ≥3-dataset combination",
            "datasets_required": [
                "DESI DR3 (BAO + galaxy power spectrum)",
                "Euclid Year 1 (weak lensing + clustering)",
                "CMB Stage-4 (ACT/Simons Obs cross-correlation)",
            ],
            "note": (
                "A single-dataset ≥3σ tension warrants strong TENSION status but "
                "retraction is premature if other datasets remain <2σ. "
                "Concordance across multiple independent probes is required "
                "before retraction of the wₐ = 0 prediction."
            ),
            "retraction_mechanism": (
                "Update arXiv preprint with explicit statement: "
                "'The UM wₐ = 0 prediction is excluded at Xσ by [datasets]. "
                "A new bulk quintessence sector is required (see Pillar 156).' "
                "Do NOT delete the preprint — this would violate scientific norms."
            ),
        },
        "wording_for_preprint_update": (
            "DESI DR3 gives wₐ = [value] ± [sigma], increasing the tension with "
            "the UM wₐ = 0 prediction to [X]σ. This is documented as an escalated "
            "open problem. The UM framework is not falsified at this significance "
            "level, but we note the increasing pressure and are developing a "
            "modified sector (Pillar 156) to address this tension."
        ),
    }


# ---------------------------------------------------------------------------
# Modification roadmap: if consistent (<2σ)
# ---------------------------------------------------------------------------

def modification_roadmap_if_consistent() -> Dict:
    """If DR3 reduces tension to <2σ — what claims can be updated?

    Returns
    -------
    dict
        Claim updates, documentation changes, and wₐ = 0 promotion actions.
    """
    return {
        "trigger_condition": "tension_DR3 < 2.0σ",
        "status": "CONSISTENT — DR2 tension resolved by DR3",
        "claim_updates": {
            "Pillar_155_status": {
                "from": "⚠️ OPEN TENSION (wₐ = 0 vs DESI DR2 at ~2.1σ)",
                "to": "✅ CONSISTENT (wₐ = 0 consistent with DESI DR3 at <2σ)",
                "action": "Update kk_de_wa_cpl.py pillar155_summary() status field",
            },
            "OBSERVATION_TRACKER": {
                "action": (
                    "Update 3-FALSIFICATION/OBSERVATION_TRACKER.md entry P4 "
                    "from TENSION to CONSISTENT. Record DR3 measurement."
                ),
            },
            "FALLIBILITY_md": {
                "action": (
                    "Move wₐ tension from 'Admission 4 — open' to "
                    "'Resolved by DESI DR3' section. Document DR3 measurement."
                ),
            },
        },
        "wording_for_preprint_update": (
            "DESI DR3 gives wₐ = [value] ± [sigma], reducing the tension with "
            "the UM wₐ = 0 prediction to [X]σ (<2σ). The UM prediction is now "
            "observationally consistent with DESI DR3. The wₐ = 0 frozen radion "
            "mechanism (Pillar 155) is confirmed as observationally consistent."
        ),
        "promotion_of_wa_claim": {
            "can_claim_confirmed": False,
            "rationale": (
                "A <2σ consistency does not constitute confirmation. "
                "We can claim 'observationally consistent' but NOT 'confirmed'. "
                "LiteBIRD (~2032) birefringence remains the primary confirmation pathway."
            ),
            "appropriate_language": [
                "CONSISTENT: wₐ = 0 is not excluded by DESI DR3",
                "The tension present in DR2 is not confirmed by DR3",
                "The UM frozen radion prediction remains viable",
            ],
            "inappropriate_language": [
                "CONFIRMED: wₐ = 0 is confirmed by DESI DR3",
                "The DESI wₐ tension has been resolved",
            ],
        },
        "additional_actions": [
            "Update STATUS.md with CONSISTENT verdict for Pillar 155",
            "Issue brief arXiv update note with DR3 measurement",
            "Continue monitoring future DESI releases for confirmation",
            "Cross-check with Euclid weak lensing wₐ constraints",
        ],
        "interpretation_caution": (
            "A single <2σ result after a prior 2σ tension may reflect statistical "
            "fluctuation. Multiple independent dataset consistency is needed before "
            "strong language. Continue monitoring."
        ),
    }


# ---------------------------------------------------------------------------
# Release-day action protocol
# ---------------------------------------------------------------------------

def release_day_action_protocol(wa_dr3: float, sigma_dr3: float) -> Dict:
    """Exactly what to do on the day DESI DR3 is published.

    Step-by-step protocol conditioned on the DR3 measurement.

    Parameters
    ----------
    wa_dr3 : float
        DR3 wₐ central value (from the DESI DR3 paper).
    sigma_dr3 : float
        DR3 wₐ uncertainty (1σ).

    Returns
    -------
    dict
        action: str (top-level action code)
        steps: list of step-by-step actions
        verdict: dict (from falsification_verdict)
        files_to_update_immediately: list
        timeline_hours: dict
    """
    verdict = falsification_verdict(wa_dr3, sigma_dr3)
    tension = verdict["tension_sigma"]
    top_action = verdict["verdict"]

    if top_action == "FALSIFIED":
        action_code = "INITIATE_FALSIFICATION_PROTOCOL"
        immediate_steps = [
            "STEP 1 [0h]: Read the DESI DR3 paper in full; extract wₐ, σ_wₐ, datasets used.",
            "STEP 2 [0h]: Run falsification_verdict(wa_dr3, sigma_dr3) to confirm ≥3σ.",
            "STEP 3 [1h]: Update 3-FALSIFICATION/OBSERVATION_TRACKER.md — record DR3 values.",
            "STEP 4 [1h]: Update src/core/kk_de_wa_cpl.py pillar155_summary() status to FALSIFIED.",
            "STEP 5 [2h]: Update src/core/desi_year3_monitor.py with DR3 baseline.",
            "STEP 6 [2h]: Update STATUS.md — Pillar 155 status to FALSIFIED.",
            "STEP 7 [4h]: Update FALLIBILITY.md — add Admission: wₐ = 0 excluded at ≥3σ.",
            "STEP 8 [6h]: Draft arXiv preprint update note (not retraction — update).",
            "STEP 9 [12h]: Begin Pillar 156 design: bulk quintessence field in RS geometry.",
            "STEP 10 [24h]: Post arXiv update with explicit falsification acknowledgement.",
            "STEP 11 [48h]: Begin modified model development (bulk quintessence sector).",
        ]
        communication = (
            "Public statement: 'DESI DR3 gives wₐ = {:.3f} ± {:.3f}, excluding "
            "the UM wₐ = 0 prediction at {:.1f}σ. This falsifies the frozen-radion "
            "dark energy sub-claim. We are extending the UM with a new bulk "
            "quintessence sector (Pillar 156). The core UM geometric framework "
            "(Pillars 1–154, 156–208) is unaffected.'"
        ).format(wa_dr3, sigma_dr3, tension)
    elif top_action == "HIGH_TENSION":
        action_code = "INITIATE_HIGH_TENSION_PROTOCOL"
        immediate_steps = [
            "STEP 1 [0h]: Read DR3 paper; extract wₐ, σ_wₐ, dataset combination.",
            "STEP 2 [0h]: Run falsification_verdict() to confirm 2.5–3.0σ HIGH_TENSION.",
            "STEP 3 [2h]: Update OBSERVATION_TRACKER.md with DR3 HIGH_TENSION status.",
            "STEP 4 [2h]: Update kk_de_wa_cpl.py with DR3 values and HIGH_TENSION verdict.",
            "STEP 5 [4h]: Update STATUS.md: Pillar 155 → HIGH_TENSION ⚠️",
            "STEP 6 [8h]: Post arXiv update noting HIGH_TENSION and continued monitoring.",
            "STEP 7 [24h]: Begin Pillar 156 design as contingency.",
            "STEP 8 [1w]: Request DESI collaboration systematics breakdown.",
        ]
        communication = (
            "Public statement: 'DESI DR3 gives wₐ = {:.3f} ± {:.3f}, maintaining "
            "high tension ({:.1f}σ) with the UM wₐ = 0 prediction. The UM is not "
            "yet falsified at this significance. We are monitoring closely and "
            "developing contingency modifications.'"
        ).format(wa_dr3, sigma_dr3, tension)
    elif top_action == "TENSION":
        action_code = "DOCUMENT_TENSION"
        immediate_steps = [
            "STEP 1 [0h]: Read DR3 paper; extract wₐ, σ_wₐ.",
            "STEP 2 [1h]: Run falsification_verdict() to confirm 2.0–2.5σ TENSION.",
            "STEP 3 [2h]: Update OBSERVATION_TRACKER.md with DR3 values.",
            "STEP 4 [4h]: Update kk_de_wa_cpl.py with DR3 values.",
            "STEP 5 [8h]: Post arXiv update with DR3 measurement and tension level.",
            "STEP 6 [24h]: Continue routine monitoring schedule.",
        ]
        communication = (
            "Public statement: 'DESI DR3 gives wₐ = {:.3f} ± {:.3f}, a {:.1f}σ "
            "tension with the UM wₐ = 0 prediction — similar to DR2. This remains "
            "an honest open problem. Continued monitoring with future releases.'"
        ).format(wa_dr3, sigma_dr3, tension)
    else:  # CONSISTENT
        action_code = "DOCUMENT_CONSISTENCY"
        immediate_steps = [
            "STEP 1 [0h]: Read DR3 paper; extract wₐ, σ_wₐ.",
            "STEP 2 [1h]: Run falsification_verdict() to confirm <2σ CONSISTENT.",
            "STEP 3 [2h]: Update OBSERVATION_TRACKER.md: P4 → CONSISTENT.",
            "STEP 4 [2h]: Update kk_de_wa_cpl.py: Pillar 155 status → CONSISTENT ✅",
            "STEP 5 [4h]: Update FALLIBILITY.md: resolve open admission for wₐ.",
            "STEP 6 [8h]: Post arXiv update noting DR2 tension not confirmed by DR3.",
        ]
        communication = (
            "Public statement: 'DESI DR3 gives wₐ = {:.3f} ± {:.3f}, reducing the "
            "tension with the UM wₐ = 0 prediction to {:.1f}σ. The UM frozen-radion "
            "dark energy mechanism (Pillar 155) is observationally consistent with "
            "DESI DR3. The DR2 tension is not confirmed by DR3.'"
        ).format(wa_dr3, sigma_dr3, tension)

    return {
        "action": action_code,
        "verdict": verdict,
        "tension_sigma": tension,
        "wa_dr3": wa_dr3,
        "sigma_dr3": sigma_dr3,
        "steps": immediate_steps,
        "communication_template": communication,
        "files_to_update_immediately": [
            "3-FALSIFICATION/OBSERVATION_TRACKER.md",
            "src/core/kk_de_wa_cpl.py",
            "src/core/desi_year3_monitor.py",
            "STATUS.md",
        ],
        "files_to_update_within_48h": [
            "FALLIBILITY.md",
            "README.md (if status changes significantly)",
            "src/core/canonical_falsifier_evidence_feed.py",
            "6-MONOGRAPH/MCP_INGEST.md",
        ],
        "run_tests_after_update": (
            "python -m pytest tests/test_desi_dr3_full_analysis.py "
            "tests/test_desi_dr3_decision_matrix.py -v"
        ),
    }


# ---------------------------------------------------------------------------
# Strategic summary
# ---------------------------------------------------------------------------

def desi_dr3_strategic_summary() -> Dict:
    """Complete summary for a human director.

    Returns a comprehensive, structured summary of:
    - Current status
    - UM prediction
    - DESI DR2 tension
    - DR3 projected outcomes
    - Recommended strategy
    - Falsification conditions
    - Key files

    Returns
    -------
    dict
        All expected keys for a complete strategic picture.
    """
    # Current tension
    current_tension = wa_tension_sigma(
        DESI_DR2["wa_central"], DESI_DR2["wa_sigma"], UM_WA_PREDICTION
    )

    # Pre-DR3 strategy
    strategy = SUBMISSION_STRATEGY_PRE_DR3()

    return {
        "title": "DESI DR3 Strategic Preparedness Summary — Unitary Manifold",
        "date_prepared": "2026",
        "current_status": {
            "um_wa_prediction": UM_WA_PREDICTION,
            "um_w0_prediction": UM_W0_PREDICTION,
            "desi_dr2_wa_central": DESI_DR2["wa_central"],
            "desi_dr2_wa_sigma": DESI_DR2["wa_sigma"],
            "current_tension_sigma": current_tension,
            "verdict": "TENSION ⚠️" if 2.0 <= current_tension < 3.0 else "CONSISTENT ✅",
            "is_falsified": current_tension >= 3.0,
            "reference": DESI_DR2["reference"],
        },
        "um_mechanism": {
            "description": (
                "The UM KK radion with Goldberger-Wise stabilisation has "
                "m_r >> H₀ (mass ratio ~10⁶⁰). The field is frozen at its "
                "potential minimum, giving wₐ = 0 exactly to precision << 10⁻³²."
            ),
            "kk_tower_wa_upper_bound": 1e-32,
            "mechanism_status": "FROZEN_RADION",
        },
        "dr3_projection": {
            "expected_dr3_sigma_wa": DESI_DR2["wa_sigma"] * 0.6,
            "tension_if_central_unchanged": abs(DESI_DR2["wa_central"]) / (DESI_DR2["wa_sigma"] * 0.6),
            "expected_dr3_release": "~2027",
        },
        "submission_strategy": strategy["strategy"],
        "submission_rationale": strategy["rationale"],
        "falsification_conditions": {
            "primary_falsifier": "wₐ ≠ 0 at ≥ 3σ in DESI DR3",
            "threshold_sigma": 3.0,
            "consequence": "New bulk quintessence sector required (Pillar 156)",
            "kk_tower_cannot_explain": True,
            "resolution_paths": {
                "A": "Multi-component KK spectrum — computed: |wₐ^KK| < 10⁻³², negligible",
                "B": "Bulk quintessence field — outside current 5D action, would require Pillar 156",
                "C": "DESI systematic effects — estimated <0.1 total, insufficient",
                "D": "Modified radion mass (m_r ~ H₀) — contradicts RS hierarchy",
            },
        },
        "scenario_responses": {
            "FALSIFIED_geq_3sigma": "Initiate Pillar 156; update all tracking files; arXiv update",
            "HIGH_TENSION_2p5_to_3sigma": "Alert; monitor; begin Pillar 156 design as contingency",
            "TENSION_2_to_2p5sigma": "Document; monitor; no model modification",
            "CONSISTENT_lt_2sigma": "Update tracking; promote wₐ = 0 to CONSISTENT",
        },
        "key_files": {
            "analysis": "src/core/desi_dr3_full_analysis.py",
            "decisions": "src/core/desi_dr3_decision_matrix.py",
            "monitoring": "src/core/desi_year3_monitor.py",
            "pillar_155": "src/core/kk_de_wa_cpl.py",
            "tracker": "3-FALSIFICATION/OBSERVATION_TRACKER.md",
            "tests_analysis": "tests/test_desi_dr3_full_analysis.py",
            "tests_decisions": "tests/test_desi_dr3_decision_matrix.py",
        },
        "immediate_action": (
            "SUBMIT arXiv preprint BEFORE DESI DR3. Document wₐ = 0 prediction "
            "and ~2.1σ tension honestly. Monitor DR3 release (~2027)."
        ),
    }
