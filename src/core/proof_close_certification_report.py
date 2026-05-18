# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Final proof-close certification packet for sprint completion.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

from src.core.architecture_limit_closure_path import architecture_limit_closure_path_report
from src.core.as_transfer_normalization_audit import as_transfer_chain_audit
from src.core.pillar262_full_residual_sprint_execution import execute_all_residual_sprints
from src.core.proof_closure_formal_cert import formal_proof_closure_certificate
from src.core.pillar255_open_gap_residual_dashboard import full_dashboard

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "proof_close_certification_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"


def proof_close_certification_report() -> dict[str, object]:
    """Return a single audit-ready closure packet for the active sprint."""
    dashboard = full_dashboard()
    sc2 = as_transfer_chain_audit()
    proofs = formal_proof_closure_certificate()
    arch = architecture_limit_closure_path_report()
    sprint_execution = execute_all_residual_sprints()
    statuses = sprint_execution["statuses"]

    closed = []
    hardened = []
    measurement_gated = []

    for rid in ("T3", "A3", "SC2", "SC4"):
        if statuses[rid] in {
            "CLOSED_REDUCED_SECTOR",
            "CLOSED_FULL_POINT_DERIVATION",
            "CLOSED_WITH_EFFECTIVE_FLUX_CHANNELS",
            "DERIVED_COMPLETE",
        }:
            closed.append(rid)
        else:
            hardened.append(rid)

    hardened.extend(["RG1", "FD1", "FB1"])

    measurement_gated.extend(["G3_DESI", "LITEBIRD_BETA", "JUNO_DM31"])

    overall_status = "PASS" if proofs["overall_pass"] else "TENSION"

    return {
        "report_id": "FINAL_PROOF_CLOSE_CERTIFICATION",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "overall_status": overall_status,
        "proof_closure": proofs,
        "residual_dashboard": dashboard,
        "sprint_execution": sprint_execution,
        "sc2_chain": sc2,
        "architecture_paths": arch,
        "closed_items": closed,
        "hardened_items": hardened,
        "measurement_gated_items": measurement_gated,
    }
