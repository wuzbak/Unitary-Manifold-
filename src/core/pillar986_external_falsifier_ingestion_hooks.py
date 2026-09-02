# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 986 — External Falsifier Ingestion Hooks (Sprint BL).

Deterministic ingestion hooks for new observational releases.
No network IO is performed here; payloads are passed in by upstream tooling.
"""

from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "ingest_release",
    "ingest_release_batch",
]

PILLAR_NUMBER: int = 986
PILLAR_GATE: str = "EXTERNAL_FALSIFIER_INGESTION_HOOKS"

DESI_PASS_SIGMA: float = 2.0
DESI_FALSIFIED_SIGMA: float = 5.0

LITEBIRD_BETA_MIN: float = 0.22
LITEBIRD_BETA_MAX: float = 0.38
LITEBIRD_GAP_MIN: float = 0.29
LITEBIRD_GAP_MAX: float = 0.31


def _desi_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    sigma = float(payload["sigma_wa_from_zero"])
    if sigma < DESI_PASS_SIGMA:
        verdict = "PASS"
    elif sigma < DESI_FALSIFIED_SIGMA:
        verdict = "TENSION"
    else:
        verdict = "FALSIFIED"
    return {
        "experiment": "DESI_DR3",
        "verdict": verdict,
        "sigma_wa_from_zero": sigma,
        "thresholds": {"pass_lt": DESI_PASS_SIGMA, "falsified_ge": DESI_FALSIFIED_SIGMA},
    }


def _litebird_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    beta = float(payload["beta_deg"])
    sigma = float(payload.get("sigma_deg", 0.02))

    in_window = LITEBIRD_BETA_MIN <= beta <= LITEBIRD_BETA_MAX
    in_gap = LITEBIRD_GAP_MIN <= beta <= LITEBIRD_GAP_MAX

    if not in_window:
        verdict = "FALSIFIED_WINDOW"
    elif in_gap:
        verdict = "FALSIFIED_GAP"
    else:
        min_dist = min(abs(beta - 0.273), abs(beta - 0.331))
        verdict = "PASS" if min_dist <= 3.0 * sigma else "TENSION"

    return {
        "experiment": "LITEBIRD",
        "verdict": verdict,
        "beta_deg": beta,
        "sigma_deg": sigma,
        "window": [LITEBIRD_BETA_MIN, LITEBIRD_BETA_MAX],
        "forbidden_gap": [LITEBIRD_GAP_MIN, LITEBIRD_GAP_MAX],
    }


def ingest_release(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Route a single external release payload to deterministic verdict logic."""
    experiment = str(payload.get("experiment", "")).upper()
    if experiment == "DESI_DR3":
        result = _desi_route(payload)
    elif experiment == "LITEBIRD":
        result = _litebird_route(payload)
    else:
        result = {
            "experiment": experiment,
            "verdict": "UNSUPPORTED_EXPERIMENT",
            "supported": ["DESI_DR3", "LITEBIRD"],
        }

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "result": result,
    }


def ingest_release_batch(payloads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Route a batch of external releases."""
    results = [ingest_release(payload)["result"] for payload in payloads]
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "n_payloads": len(payloads),
        "results": results,
    }


PILLAR_STATUS: str = "EXTERNAL_FALSIFIER_INGESTION_HOOKS_READY"
PILLAR_VALID: bool = True
