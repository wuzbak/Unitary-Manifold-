# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1009 — CMB nonperturbative/global-UV normalization candidate audit.

Secondary Sprint BQ lane: execute one candidate route that avoids external A_s
fitting and issue a binary outcome (earned upgrade or strengthened limit).
"""

from __future__ import annotations

from typing import Any, Dict

from src.core.pillar983_residual_budget_pipeline import residual_budget_pipeline
from src.core.pillar999_cmb_amplitude_calibration_boundary import (
    cmb_amplitude_evidence_ledger,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "CANDIDATE_NAME",
    "cmb_nonperturbative_normalization_candidate",
    "pillar1009_summary",
]

PILLAR_NUMBER: int = 1009
PILLAR_GATE: str = "CMB_NONPERTURBATIVE_GLOBAL_UV_NORMALIZATION_CANDIDATE"
PILLAR_STATUS: str = "CMB_NONPERTURBATIVE_NORMALIZATION_CANDIDATE_COMPLETE"
CANDIDATE_NAME: str = "GLOBAL_UV_NONPERTURBATIVE_TRANSFER_NORMALIZATION_KERNEL"


def cmb_nonperturbative_normalization_candidate() -> Dict[str, Any]:
    """Return binary verdict for one non-fitted CMB normalization candidate."""
    ledger = cmb_amplitude_evidence_ledger()
    budget = residual_budget_pipeline()
    cmb_budget = next(row for row in budget["rows"] if row["lane"] == "CMB_AMP")

    candidate = {
        "name": CANDIDATE_NAME,
        "uses_external_as_target": False,
        "free_parameters_added": 0,
        "targets_missing_objects": {
            "nonperturbative amplitude-generation mechanism": False,
            "global UV completion of transfer normalization": False,
        },
    }

    candidate_success = all(candidate["targets_missing_objects"].values())
    outcome = (
        "CMB_NONPERTURBATIVE_NORMALIZATION_EARNED"
        if candidate_success
        else "CMB_NONPERTURBATIVE_NORMALIZATION_NOT_EARNED"
    )

    strengthened_limit = (
        not candidate_success
        and ledger["terminal_eft_routes"]
        and cmb_budget["normalized"]
        and cmb_budget["has_registry_row"]
    )

    strengthened_certificate = {
        "status": "CMB_RESIDUAL_BUDGET_TIGHTENED" if strengthened_limit else "CMB_RESIDUAL_BUDGET_UNCHANGED",
        "lane": "CMB_AMP",
        "dominant_component": cmb_budget["dominant"],
        "eft_exhausted": cmb_budget["eft_exhausted"],
        "uv_missing": cmb_budget["uv_missing"],
        "external_pending": cmb_budget["external_pending"],
    }

    valid = (
        candidate["uses_external_as_target"] is False
        and candidate["free_parameters_added"] == 0
        and outcome
        in {
            "CMB_NONPERTURBATIVE_NORMALIZATION_EARNED",
            "CMB_NONPERTURBATIVE_NORMALIZATION_NOT_EARNED",
        }
        and strengthened_certificate["status"] in {
            "CMB_RESIDUAL_BUDGET_TIGHTENED",
            "CMB_RESIDUAL_BUDGET_UNCHANGED",
        }
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "candidate": candidate,
        "candidate_success": candidate_success,
        "outcome": outcome,
        "strengthened_certificate": strengthened_certificate,
        "evidence_ledger_status": ledger["status"],
        "named_missing_objects": ledger["named_missing_objects"],
        "interpretation": (
            "The tested non-fitted candidate does not supply either named missing CMB object, "
            "so no closure upgrade is earned; the residual-budget architecture-limit certificate is "
            "strengthened instead of softened."
        ),
    }


PILLAR_VALID: bool = cmb_nonperturbative_normalization_candidate()["valid"]


def pillar1009_summary() -> Dict[str, Any]:
    """Return concise Pillar 1009 summary."""
    report = cmb_nonperturbative_normalization_candidate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "CMB Nonperturbative/Global-UV Normalization Candidate",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "outcome": report["outcome"],
        "strengthened_status": report["strengthened_certificate"]["status"],
    }
