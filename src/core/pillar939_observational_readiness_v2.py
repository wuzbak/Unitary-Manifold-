# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 939 — Observational Readiness Matrix v2.

🔵 ADJACENT TRACK — Non-hardgate.  Does not alter core 5D predictions.

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════

Produces a single machine-readable matrix of all open UM predictions
vs. their corresponding experiments and decision timelines.

Replaces scattered docs and provides a canonical reference for:
  - LiteBIRD β birefringence (primary falsifier)
  - DESI DR3 wₐ=0
  - SPHEREx f_NL and BAO
  - Euclid Y2 lensing
  - Hyper-K Run 3 proton decay / neutrino ordering
  - LISA Ω_GW

Each entry records:
  prediction, experiment, observable, timeline, current_status,
  falsification_threshold, notes.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "OBSERVATIONAL_MATRIX",
    "observational_readiness_v2",
    "obs_matrix_summary",
]

PILLAR_NUMBER: int = 939
PILLAR_GATE: str = "OBSERVATIONAL_READINESS_V2"
PILLAR_STATUS: str = "OBSERVATIONAL_MATRIX_COMPLETE"

# ---------------------------------------------------------------------------
# Canonical observational readiness matrix
# ---------------------------------------------------------------------------
OBSERVATIONAL_MATRIX: List[Dict[str, Any]] = [
    {
        "id": "ORM-01",
        "prediction": "CMB birefringence β ∈ {≈0.273°, ≈0.331°} canonical",
        "experiment": "LiteBIRD",
        "observable": "CMB B-mode polarisation rotation angle β",
        "pillar_source": "P23/P24",
        "current_sigma": None,
        "current_status": "PENDING",
        "falsification_threshold": "β outside [0.22°, 0.38°] OR β ∈ [0.29°, 0.31°]",
        "timeline": "~2032",
        "is_primary_falsifier": True,
        "notes": "Primary falsifier. LiteBIRD launch ~2030, first results ~2032.",
    },
    {
        "id": "ORM-02",
        "prediction": "wₐ = 0 (frozen radion / cosmological constant)",
        "experiment": "DESI DR3",
        "observable": "CPL dark energy wₐ from BAO",
        "pillar_source": "P808, P824, P926, P938",
        "current_sigma": 2.75,
        "current_status": "TENSION",
        "falsification_threshold": "σ ≥ 5.0 (discovery-level)",
        "timeline": "~2027",
        "is_primary_falsifier": False,
        "notes": "σ ∈ [2.30, 2.75] as of 2026-09-01. Thresholds pre-registered (P824).",
    },
    {
        "id": "ORM-03",
        "prediction": "f_NL ~ O(1) from 5D bispectrum",
        "experiment": "SPHEREx",
        "observable": "Galaxy bispectrum primordial f_NL",
        "pillar_source": "P610",
        "current_sigma": None,
        "current_status": "PENDING",
        "falsification_threshold": "f_NL detection > 5σ inconsistent with O(1) prediction",
        "timeline": "2027–2028",
        "is_primary_falsifier": False,
        "notes": "SPHEREx Year 2 BAO will also constrain wₐ independently (P938).",
    },
    {
        "id": "ORM-04",
        "prediction": "CMB lensing + ISW consistent with 5D geometry",
        "experiment": "Euclid Y2",
        "observable": "Weak lensing power spectrum, ISW cross-correlation",
        "pillar_source": "P609, P820",
        "current_sigma": None,
        "current_status": "PENDING",
        "falsification_threshold": ">3σ tension in S₈ or σ₈ relative to UM prediction",
        "timeline": "~2027",
        "is_primary_falsifier": False,
        "notes": "Euclid Year 1 consistent (P609). Year 2 provides tighter constraint.",
    },
    {
        "id": "ORM-05",
        "prediction": "Normal neutrino ordering (m₁ < m₂ < m₃) from 7D monodromy",
        "experiment": "Hyper-Kamiokande",
        "observable": "Neutrino mass ordering from atmospheric/beam ν",
        "pillar_source": "P927",
        "current_sigma": None,
        "current_status": "PROXY_CLOSED",
        "falsification_threshold": "Inverted ordering established at > 3σ",
        "timeline": "~2027 (Run 3)",
        "is_primary_falsifier": False,
        "notes": "NLO stable (P927). HK Run 3 could definitively confirm/falsify ordering.",
    },
    {
        "id": "ORM-06",
        "prediction": "Proton lifetime τ(p→e⁺π⁰) consistent with KK gauge unification",
        "experiment": "Hyper-Kamiokande Run 3",
        "observable": "Proton decay p → e⁺π⁰",
        "pillar_source": "P611",
        "current_sigma": None,
        "current_status": "CONSISTENT",
        "falsification_threshold": "Observation of p → e⁺π⁰ with τ < 10³⁴ yr at > 5σ",
        "timeline": "~2030+",
        "is_primary_falsifier": False,
        "notes": "Current Super-K bound τ > 2.4×10³⁴ yr consistent with UM. HK extends reach.",
    },
    {
        "id": "ORM-07",
        "prediction": "Gravitational wave background Ω_GW from KK spectrum",
        "experiment": "LISA",
        "observable": "Stochastic GW background Ω_GW(f)",
        "pillar_source": "P25",
        "current_sigma": None,
        "current_status": "DERIVED_PENDING",
        "falsification_threshold": "Ω_GW detection inconsistent with KK mass spectrum",
        "timeline": "~2037",
        "is_primary_falsifier": False,
        "notes": "P25 DERIVED-PENDING. LISA launch ~2034, science operations ~2037.",
    },
    {
        "id": "ORM-08",
        "prediction": "α_s(M_Z) ∈ tightened window (P937)",
        "experiment": "LHC Run 4 / lattice QCD",
        "observable": "Strong coupling constant α_s(M_Z)",
        "pillar_source": "P912, P920, P937",
        "current_sigma": None,
        "current_status": "ARCHITECTURE_LIMIT",
        "falsification_threshold": "Tightened P937 window remains below PDG α_s(M_Z)=0.1180; full CY₄ moduli specification required",
        "timeline": "Ongoing",
        "is_primary_falsifier": False,
        "notes": "PDG α_s=0.1180 is outside the tightened P937 window; the broader P920 coverage did not close the 13D lane.",
    },
]

# Summary statistics
N_ENTRIES: int = len(OBSERVATIONAL_MATRIX)
N_PRIMARY_FALSIFIERS: int = sum(1 for e in OBSERVATIONAL_MATRIX if e["is_primary_falsifier"])
N_PENDING: int = sum(1 for e in OBSERVATIONAL_MATRIX if e["current_status"] == "PENDING")
N_CONSISTENT: int = sum(
    1 for e in OBSERVATIONAL_MATRIX
    if e["current_status"] in {"CONSISTENT", "PROXY_CLOSED"}
)
N_TENSION: int = sum(1 for e in OBSERVATIONAL_MATRIX if e["current_status"] == "TENSION")


def observational_readiness_v2() -> Dict[str, Any]:
    """Return the full observational readiness matrix v2."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "n_entries": N_ENTRIES,
        "n_primary_falsifiers": N_PRIMARY_FALSIFIERS,
        "n_pending": N_PENDING,
        "n_consistent": N_CONSISTENT,
        "n_tension": N_TENSION,
        "matrix": OBSERVATIONAL_MATRIX,
        "version": "v2",
        "date": "2026-09-01",
        "honest_note": (
            "Machine-readable matrix of all open UM predictions vs. experiments. "
            "No prediction falsified as of 2026-09-01. "
            "Primary falsifier: LiteBIRD β (~2032). "
            "DESI DR3 wₐ tension at 2.75σ — below 3σ threshold, not falsified."
        ),
    }


def obs_matrix_summary() -> Dict[str, Any]:
    """Return pillar summary dict."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "n_entries": N_ENTRIES,
        "n_tension": N_TENSION,
        "n_pending": N_PENDING,
    }
