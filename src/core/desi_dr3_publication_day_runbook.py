# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/desi_dr3_publication_day_runbook.py
=============================================
DESI DR3 Same-Day Publication Runbook — Machine-Readable Protocol.

When DESI DR3 is published (~2027), this module drives the same-day response:
it determines the verdict on the wₐ = 0 prediction, identifies every file
that must be updated, and enforces update-coverage auditing.

PHYSICS BACKGROUND
------------------
The Unitary Manifold predicts wₐ = 0 exactly (frozen GW-stabilised KK
radion, mass ratio m_r/H₀ ~ 10⁶⁰).  Any deviation from wₐ = 0 at ≥ 3σ
constitutes falsification of the radion dark-energy mechanism.

DESI DR2 baseline (arXiv:2503.14738):
  wₐ = −0.62 ± 0.30  →  2.07σ tension (BAO-only), 2.75σ (combined).

VERDICT THRESHOLDS
------------------
  σ < 2.0   → CONSISTENT      : update within 336 h (14 days)
  2.0 ≤ σ < 2.5 → TENSION    : update within 168 h (7 days)
  2.5 ≤ σ < 3.0 → HIGH_TENSION: update within 72 h (3 days)
  σ ≥ 3.0   → FALSIFIED       : same-day update within 24 h

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    # Constants
    "UM_WA_PREDICTION",
    "DESI_DR2_WA_CENTRAL",
    "DESI_DR2_WA_SIGMA",
    "CANONICAL_DOCS_TO_UPDATE",
    # Thresholds
    "THRESHOLD_CONSISTENT",
    "THRESHOLD_TENSION",
    "THRESHOLD_HIGH_TENSION",
    # Functions
    "publication_day_checklist",
    "verify_update_coverage",
    "mock_drill_scenario",
    "publication_day_runbook_report",
]

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: UM predicts wₐ = 0 exactly (frozen GW-stabilised radion).
UM_WA_PREDICTION: float = 0.0

#: DESI DR2 baseline wₐ central value (arXiv:2503.14738).
DESI_DR2_WA_CENTRAL: float = -0.62

#: DESI DR2 baseline wₐ 1σ uncertainty.
DESI_DR2_WA_SIGMA: float = 0.30

# ---------------------------------------------------------------------------
# Verdict thresholds (in units of σ)
# ---------------------------------------------------------------------------

#: Below this → CONSISTENT.
THRESHOLD_CONSISTENT: float = 2.0

#: At or above this and below HIGH_TENSION → TENSION.
THRESHOLD_TENSION: float = 2.0

#: At or above this and below FALSIFIED → HIGH_TENSION.
THRESHOLD_HIGH_TENSION: float = 2.5

#: At or above this → FALSIFIED.
THRESHOLD_FALSIFIED: float = 3.0

# ---------------------------------------------------------------------------
# Response deadlines (hours)
# ---------------------------------------------------------------------------

_HOURS_FALSIFIED: int = 24
_HOURS_HIGH_TENSION: int = 72
_HOURS_TENSION: int = 168
_HOURS_CONSISTENT: int = 336

# ---------------------------------------------------------------------------
# Canonical documents that MUST be updated on publication day
# ---------------------------------------------------------------------------

#: Every entry is a dict describing the file, its purpose, its priority, and
#: the expected update action for each verdict.
CANONICAL_DOCS_TO_UPDATE: List[Dict] = [
    {
        "filename": "docs/CLAIM_MASTER_BOARD.md",
        "purpose": "Master ledger of all UM observational claims and verdicts",
        "priority": 1,
        "update_actions": {
            "CONSISTENT": "Mark wₐ claim CONSISTENT; record DR3 tension σ",
            "TENSION": "Mark wₐ claim TENSION; record DR3 tension σ and headline numbers",
            "HIGH_TENSION": "Escalate wₐ claim to HIGH_TENSION; add DR3 numbers and resolution paths",
            "FALSIFIED": "Mark wₐ claim FALSIFIED; record DR3 numbers; activate modification roadmap",
        },
    },
    {
        "filename": "TRUTH_LAYER.md",
        "purpose": "Single-source-of-truth for UM status vs observations",
        "priority": 1,
        "update_actions": {
            "CONSISTENT": "Update DR3 entry to CONSISTENT; record date",
            "TENSION": "Update DR3 entry to TENSION; record date and σ",
            "HIGH_TENSION": "Update DR3 entry to HIGH_TENSION; record date, σ, and action items",
            "FALSIFIED": "Update DR3 entry to FALSIFIED; record date, σ; cross-reference modification roadmap",
        },
    },
    {
        "filename": "OBSERVATION_TRACKER.md",
        "purpose": "Live tracking of all observations relevant to UM predictions",
        "priority": 2,
        "update_actions": {
            "CONSISTENT": "Append DR3 row with tension σ < 2; flag as CONSISTENT",
            "TENSION": "Append DR3 row with tension σ; flag as TENSION",
            "HIGH_TENSION": "Append DR3 row; flag HIGH_TENSION; link to decision matrix",
            "FALSIFIED": "Append DR3 row; flag FALSIFIED; immediate escalation note",
        },
    },
    {
        "filename": "GATEKEEPER_SUMMARY.md",
        "purpose": "Executive summary for stewards and co-authors",
        "priority": 2,
        "update_actions": {
            "CONSISTENT": "Update executive summary: wₐ = 0 remains consistent with DR3",
            "TENSION": "Update executive summary: tension persists at σ; action plan",
            "HIGH_TENSION": "Update executive summary: high tension at σ; escalation triggered",
            "FALSIFIED": "Update executive summary: FALSIFIED; modification roadmap activated",
        },
    },
    {
        "filename": "WAVE_CHANGELOG.md",
        "purpose": "Versioned changelog of all major UM updates",
        "priority": 3,
        "update_actions": {
            "CONSISTENT": "Add changelog entry: DESI DR3 verdict CONSISTENT",
            "TENSION": "Add changelog entry: DESI DR3 verdict TENSION; document σ",
            "HIGH_TENSION": "Add changelog entry: DESI DR3 verdict HIGH_TENSION; document σ",
            "FALSIFIED": "Add changelog entry: DESI DR3 verdict FALSIFIED; initiate modification roadmap",
        },
    },
    {
        "filename": "STATUS.md",
        "purpose": "Public-facing repository status file",
        "priority": 2,
        "update_actions": {
            "CONSISTENT": "Update wₐ status badge to CONSISTENT; record DR3 tension σ",
            "TENSION": "Update wₐ status badge to TENSION; record DR3 σ",
            "HIGH_TENSION": "Update wₐ status badge to HIGH_TENSION; record DR3 σ",
            "FALSIFIED": "Update wₐ status badge to FALSIFIED; record DR3 σ",
        },
    },
    {
        "filename": "FALLIBILITY.md",
        "purpose": "Honest-gap register documenting known tensions and limitations",
        "priority": 2,
        "update_actions": {
            "CONSISTENT": "Downgrade wₐ open problem: tension resolved by DR3; document σ",
            "TENSION": "Update wₐ open problem: DR3 maintains tension at σ",
            "HIGH_TENSION": "Escalate wₐ open problem to HIGH_TENSION; record DR3 σ and date",
            "FALSIFIED": "Close wₐ open problem as FALSIFIED; record DR3 σ; reference retraction/modification",
        },
    },
]

# ---------------------------------------------------------------------------
# Verdict helpers
# ---------------------------------------------------------------------------

_MANDATORY_FILENAMES: List[str] = [d["filename"] for d in CANONICAL_DOCS_TO_UPDATE]


def _compute_tension_sigma(wa_observed: float, sigma_wa: float) -> float:
    """Return the number of σ between wa_observed and the UM prediction (0).

    Parameters
    ----------
    wa_observed : float
        Observed wₐ central value.
    sigma_wa : float
        1σ uncertainty on wₐ.

    Returns
    -------
    float
        |wa_observed - 0| / sigma_wa.
    """
    return abs(wa_observed - UM_WA_PREDICTION) / sigma_wa


def _tension_to_verdict(tension_sigma: float) -> str:
    """Map a tension σ to one of the four verdict strings.

    Parameters
    ----------
    tension_sigma : float
        Number of standard deviations between measurement and UM prediction.

    Returns
    -------
    str
        One of "CONSISTENT", "TENSION", "HIGH_TENSION", "FALSIFIED".
    """
    if tension_sigma >= THRESHOLD_FALSIFIED:
        return "FALSIFIED"
    if tension_sigma >= THRESHOLD_HIGH_TENSION:
        return "HIGH_TENSION"
    if tension_sigma >= THRESHOLD_TENSION:
        return "TENSION"
    return "CONSISTENT"


def _deadline_hours(verdict: str) -> int:
    """Return the required update deadline in hours for a given verdict."""
    return {
        "FALSIFIED": _HOURS_FALSIFIED,
        "HIGH_TENSION": _HOURS_HIGH_TENSION,
        "TENSION": _HOURS_TENSION,
        "CONSISTENT": _HOURS_CONSISTENT,
    }[verdict]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def publication_day_checklist(wa_observed: float, sigma_wa: float) -> Dict:
    """Compute the full publication-day action checklist for a DR3 measurement.

    Parameters
    ----------
    wa_observed : float
        DESI DR3 central wₐ value.
    sigma_wa : float
        DESI DR3 1σ uncertainty on wₐ.

    Returns
    -------
    dict with keys:
        verdict                : str  — "CONSISTENT"/"TENSION"/"HIGH_TENSION"/"FALSIFIED"
        tension_sigma          : float — |wₐ_obs - 0| / σ
        files_to_update        : list[dict] — {filename, update_action, priority}
        required_within_hours  : int  — deadline in hours
        same_day_sync_required : bool — True if verdict is FALSIFIED or HIGH_TENSION
        retraction_required    : bool — True only if verdict is FALSIFIED
    """
    tension_sigma = _compute_tension_sigma(wa_observed, sigma_wa)
    verdict = _tension_to_verdict(tension_sigma)

    files_to_update = [
        {
            "filename": doc["filename"],
            "update_action": doc["update_actions"][verdict],
            "priority": doc["priority"],
        }
        for doc in CANONICAL_DOCS_TO_UPDATE
    ]

    return {
        "verdict": verdict,
        "tension_sigma": tension_sigma,
        "files_to_update": files_to_update,
        "required_within_hours": _deadline_hours(verdict),
        "same_day_sync_required": verdict in ("FALSIFIED", "HIGH_TENSION"),
        "retraction_required": verdict == "FALSIFIED",
    }


def verify_update_coverage(updated_files: List[str]) -> Dict:
    """Verify that all mandatory files were included in an update batch.

    Parameters
    ----------
    updated_files : list[str]
        Filenames that have been updated (as reported by the operator).

    Returns
    -------
    dict with keys:
        covered   : list[str] — mandatory files present in updated_files
        missing   : list[str] — mandatory files absent from updated_files
        audit_pass: bool      — True iff missing is empty
    """
    updated_set = set(updated_files)
    covered = [f for f in _MANDATORY_FILENAMES if f in updated_set]
    missing = [f for f in _MANDATORY_FILENAMES if f not in updated_set]
    return {
        "covered": covered,
        "missing": missing,
        "audit_pass": len(missing) == 0,
    }


def mock_drill_scenario(scenario: str) -> Dict:
    """Run a mock publication-day drill for a named scenario.

    Parameters
    ----------
    scenario : str
        One of "dr3_consistent", "dr3_tension", "dr3_high_tension",
        "dr3_falsified".

    Returns
    -------
    dict
        Full packet including scenario metadata and checklist output.

    Raises
    ------
    ValueError
        If scenario is not one of the four recognised strings.
    """
    scenarios: Dict[str, Dict] = {
        "dr3_consistent": {
            "wa_observed": -0.10,
            "sigma_wa": 0.25,
            "description": "DR3 consistent — wₐ drifts toward 0; σ < 2",
        },
        "dr3_tension": {
            "wa_observed": -0.50,
            "sigma_wa": 0.23,
            "description": "DR3 tension — wₐ persists, 2.0 ≤ σ < 2.5",
        },
        "dr3_high_tension": {
            "wa_observed": -0.55,
            "sigma_wa": 0.20,
            "description": "DR3 high tension — improved precision, 2.5 ≤ σ < 3.0",
        },
        "dr3_falsified": {
            "wa_observed": -0.62,
            "sigma_wa": 0.18,
            "description": "DR3 falsified — DR2 central value, tighter error bar → σ ≥ 3",
        },
    }
    if scenario not in scenarios:
        valid = list(scenarios.keys())
        raise ValueError(
            f"Unknown scenario {scenario!r}. Must be one of {valid}."
        )

    meta = scenarios[scenario]
    checklist = publication_day_checklist(meta["wa_observed"], meta["sigma_wa"])
    return {
        "scenario": scenario,
        "description": meta["description"],
        "wa_observed": meta["wa_observed"],
        "sigma_wa": meta["sigma_wa"],
        "checklist": checklist,
    }


def publication_day_runbook_report() -> Dict:
    """Produce a summary of all four mock drill scenarios.

    Returns
    -------
    dict
        Keys "version", "title", "drills" (list of 4 packets),
        and "mandatory_files" (list of filenames).
    """
    drills = [
        mock_drill_scenario("dr3_consistent"),
        mock_drill_scenario("dr3_tension"),
        mock_drill_scenario("dr3_high_tension"),
        mock_drill_scenario("dr3_falsified"),
    ]
    return {
        "version": "v1.0",
        "title": "DESI DR3 Same-Day Publication Runbook — Drill Summary",
        "um_wa_prediction": UM_WA_PREDICTION,
        "desi_dr2_baseline": {
            "wa_central": DESI_DR2_WA_CENTRAL,
            "wa_sigma": DESI_DR2_WA_SIGMA,
            "tension_sigma": _compute_tension_sigma(
                DESI_DR2_WA_CENTRAL, DESI_DR2_WA_SIGMA
            ),
        },
        "verdict_thresholds": {
            "CONSISTENT": f"σ < {THRESHOLD_CONSISTENT}",
            "TENSION": f"{THRESHOLD_TENSION} ≤ σ < {THRESHOLD_HIGH_TENSION}",
            "HIGH_TENSION": f"{THRESHOLD_HIGH_TENSION} ≤ σ < {THRESHOLD_FALSIFIED}",
            "FALSIFIED": f"σ ≥ {THRESHOLD_FALSIFIED}",
        },
        "mandatory_files": _MANDATORY_FILENAMES,
        "drills": drills,
    }
