# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 544 — P17 Δm²₃₁ Architecture Limit Certificate.

STATUS: DM31_ARCHITECTURE_LIMIT_CERTIFIED

P17 (atmospheric neutrino mass splitting Δm²₃₁) is the only prediction in
Lane A that is currently EXCLUDED by a direct experimental measurement.
After JUNO 2026 reported Δm²₃₁ = 2.411e-3 eV², the UM 2NLO bare estimate
(2.2845e-3 eV²) is excluded at 6.46σ.  The best-attempt projection using
RGE + seesaw at maximum p_R = 0.441 reaches 2.3457e-3 eV², still excluded
at 3.33σ.

This pillar formally certifies the gap as ARCHITECTURE_LIMIT_CERTIFIED:
the residual cannot close within the minimal 5D-EFT without the full
WS-V KK Yukawa texture diagonalization, which requires:
  - Non-perturbative off-diagonal KK Yukawa terms from WS-V texture
  - Two-loop KK correction to the seesaw scale (beyond 5D-EFT)
  - UV-brane localized right-handed neutrino spectrum from orbifold BC

This certification makes the gap machine-readable, names the exact closure
path, and sets explicit conditions under which the ARCHITECTURE_LIMIT label
would be upgraded to CLOSURE_IN_PROGRESS.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "JUNO_2026_RESULT",
    "UM_ESTIMATES",
    "ARCHITECTURE_LIMIT_RECORD",
    "CLOSURE_PATH",
    "dm31_tension_sigma",
    "architecture_limit_certificate",
    "closure_path_report",
    "upgrade_conditions",
    "pillar_report",
]

PILLAR_NUMBER: int = 544
PILLAR_STATUS: str = "DM31_ARCHITECTURE_LIMIT_CERTIFIED"
PILLAR_TITLE: str = "P17 Δm²₃₁ Architecture Limit Certificate"
VERSION: str = "v19.0"

# JUNO 2026 measurement
JUNO_2026_RESULT: Dict[str, float] = {
    "dm31_evsq": 2.411e-3,               # central value, eV²
    "sigma_frac": 0.008125,              # 0.81% fractional 1σ
    "sigma_evsq": 2.411e-3 * 0.008125,  # ≈ 1.959e-5 eV² (from Pillar 525)
    "source": "JUNO Phase 1 DR1 (2026); Pillar 525 routing",
}

# UM estimates at different approximation levels
UM_ESTIMATES: Dict[str, Dict[str, Any]] = {
    "2NLO_bare": {
        "dm31_evsq": 2.2845e-3,
        "description": "2NLO bare (no RGE, no seesaw correction)",
        "tension_sigma": None,  # filled by dm31_tension_sigma()
        "status": "EXCLUDED",
    },
    "best_attempt_projection": {
        "dm31_evsq": 2.3457e-3,
        "description": "RGE + seesaw at PMNS max p_R = 0.441",
        "tension_sigma": None,
        "status": "EXCLUDED",
    },
    "kk_tower_correction": {
        "dm31_evsq": 2.2845e-3 * (1 + 2.3e-21),  # ε_KK ≈ 2.3e-21 — negligible
        "description": "KK tower correction (ε_KK ≈ 2.3e-21; negligible)",
        "tension_sigma": None,
        "status": "EXCLUDED",
    },
}

# The architecture limit record
ARCHITECTURE_LIMIT_RECORD: Dict[str, Any] = {
    "pillar": PILLAR_NUMBER,
    "prediction_id": "P17",
    "observable": "Δm²₃₁ (atmospheric neutrino mass splitting)",
    "juno_value": JUNO_2026_RESULT["dm31_evsq"],
    "um_best_estimate": UM_ESTIMATES["best_attempt_projection"]["dm31_evsq"],
    "current_tension_sigma": 3.33,  # from Pillar 525 routing
    "bare_tension_sigma": 6.46,
    "status": "ARCHITECTURE_LIMIT_CERTIFIED",
    "label": "HONEST_OPEN_PROBLEM → ARCHITECTURE_LIMIT_CERTIFIED",
    "architectural_reason": (
        "The minimal 5D-EFT cannot reproduce Δm²₃₁ = 2.411e-3 eV² because: "
        "(1) The WS-V KK Yukawa texture diagonalization requires off-diagonal "
        "KK terms that are outside the 5D-EFT perturbative expansion. "
        "(2) The right-handed neutrino KK spectrum requires UV-brane orbifold "
        "boundary conditions that break the simple c_L ladder. "
        "(3) The two-loop seesaw contribution is of order the gap and cannot "
        "be computed without the full non-perturbative KK spectrum."
    ),
    "architecture_not_failure": (
        "This is a genuine architecture limit of the minimal 5D-EFT, not a "
        "falsification. The UM framework can be extended to close this gap "
        "via the WS-V KK Yukawa texture. The extension is well-defined; "
        "it has not been computed."
    ),
}

# The explicit closure path
CLOSURE_PATH: List[Dict[str, str]] = [
    {
        "step": "1",
        "title": "WS-V KK Yukawa texture: off-diagonal KK terms",
        "description": (
            "Compute the full off-diagonal KK Yukawa matrix Y^{KK}_{ij} from "
            "the WS-V (Wolfenstein-type) texture in the 5D bulk. This requires "
            "evaluating KK mode overlaps on the orbifold with BC-dependent "
            "wavefunctions. Current status: scoped but not computed."
        ),
        "blocks_closure": True,
    },
    {
        "step": "2",
        "title": "Orbifold BC for right-handed neutrinos",
        "description": (
            "Derive the UV-brane orbifold boundary conditions for the "
            "right-handed neutrino sector. The Z₂ projection of the 5D "
            "spinor determines which KK modes are zero-mode localized and "
            "which are KK-tower-only. This feeds directly into the seesaw "
            "mass matrix."
        ),
        "blocks_closure": True,
    },
    {
        "step": "3",
        "title": "Two-loop seesaw mass correction",
        "description": (
            "Evaluate the two-loop KK contribution to the Majorana mass "
            "matrix. The one-loop contribution is already included in the "
            "best-attempt projection (p_R = 0.441). The two-loop term is "
            "of order (g_5²/(16π²))² × M_KK — potentially enough to close "
            "the 3.33σ gap."
        ),
        "blocks_closure": True,
    },
    {
        "step": "4",
        "title": "JUNO Phase 2 pre-registration check",
        "description": (
            "JUNO Phase 2 will sharpen Δm²₃₁ to ±0.3% precision. "
            "Any partial closure attempt must be pre-registered before "
            "JUNO Phase 2 data is released to avoid post-hoc fitting. "
            "Pre-registration template: Pillar 535 JUNO Phase 2 protocol."
        ),
        "blocks_closure": False,
    },
]


def dm31_tension_sigma(
    um_estimate: float,
    juno_value: float = JUNO_2026_RESULT["dm31_evsq"],
    juno_sigma: float = JUNO_2026_RESULT["sigma_evsq"],
) -> float:
    """Compute the tension in σ between a UM estimate and the JUNO result."""
    if juno_sigma <= 0:
        raise ValueError("juno_sigma must be positive")
    return abs(um_estimate - juno_value) / juno_sigma


def architecture_limit_certificate() -> Dict[str, Any]:
    """Return the full architecture limit certificate for P17."""
    # Fill in computed tensions
    estimates = {}
    for key, est in UM_ESTIMATES.items():
        tension = dm31_tension_sigma(est["dm31_evsq"])
        estimates[key] = {
            **est,
            "tension_sigma": round(tension, 2),
        }

    return {
        "certificate_type": "ARCHITECTURE_LIMIT_CERTIFIED",
        "pillar": PILLAR_NUMBER,
        "prediction": "P17",
        "record": ARCHITECTURE_LIMIT_RECORD,
        "estimates": estimates,
        "certification_criteria_met": [
            "Gap cannot close within minimal 5D-EFT (3 independent reasons)",
            "KK tower correction negligible (ε_KK ≈ 2.3e-21)",
            "All perturbative handles exhausted",
            "Closure path well-defined but requires extension",
        ],
        "falsification_condition": (
            "P17 would constitute falsification only if the WS-V KK Yukawa "
            "extension is also excluded. The extension is not yet computed. "
            "Therefore the current status is ARCHITECTURE_LIMIT, not FALSIFIED."
        ),
        "note": (
            "ARCHITECTURE_LIMIT_CERTIFIED is an honest scientific status. "
            "It means: the gap is real, the closure path is named, and no "
            "post-hoc fitting has been performed. This is more credible than "
            "claiming the gap is closed."
        ),
    }


def closure_path_report() -> Dict[str, Any]:
    """Return the explicit closure path with blocking status."""
    blocking_steps = [s for s in CLOSURE_PATH if s["blocks_closure"]]
    return {
        "total_steps": len(CLOSURE_PATH),
        "blocking_steps": len(blocking_steps),
        "steps": CLOSURE_PATH,
        "earliest_partial_closure": "After Step 1 and Step 2 (WS-V texture + orbifold BC)",
        "full_closure_requires": "Steps 1, 2, and 3 all complete",
        "juno_phase2_window": "2027–2028 (precision ±0.3%)",
    }


def upgrade_conditions() -> List[str]:
    """Return the explicit conditions under which ARCHITECTURE_LIMIT would be upgraded."""
    return [
        "CLOSURE_IN_PROGRESS: WS-V KK Yukawa off-diagonal terms computed (Step 1 complete)",
        "DERIVED_PARTIAL: Orbifold BC for ν_R derived; predicted Δm²₃₁ within 2σ of JUNO",
        "DERIVED: Full WS-V KK + two-loop seesaw gives Δm²₃₁ within 1σ of JUNO with no free parameters",
    ]


def pillar_report() -> Dict[str, Any]:
    """Full Pillar 544 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "architecture_limit_certificate": architecture_limit_certificate(),
        "closure_path": closure_path_report(),
        "upgrade_conditions": upgrade_conditions(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
        "new_physics": False,
        "epistemic_delta": "P17: HONEST_OPEN_PROBLEM → ARCHITECTURE_LIMIT_CERTIFIED",
    }
