# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Internal structural consistency packet, not a physical closure certificate.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT
"""
from __future__ import annotations

import numpy as np

from src.core.anomaly_closure import prove_sos_identity_universally
from src.core.metric_ansatz_derivation import metric_ansatz_derivation_certificate
from src.core.nw5_pure_theorem import nw5_pure_theorem
from src.holography.boundary import boundary_area, entropy_area

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "formal_proof_closure_certificate",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"


def formal_proof_closure_certificate() -> dict[str, object]:
    """Report conditional algebra, parameterization and boundary checks.

    Legacy PASS/overall_pass concern these software checks only, not physical
    uniqueness, an action-level reduction or an orbifold photon.
    """
    nw = nw5_pure_theorem()
    kcs = prove_sos_identity_universally(max_n=31)
    metric = metric_ansatz_derivation_certificate()

    # Minimal boundary consistency audit (positive area/entropy on regular metric).
    h = np.tile(np.eye(2), (4, 1, 1))
    area = boundary_area(h)
    entropy = entropy_area(h)
    boundary_consistent = area > 0.0 and entropy > 0.0

    passed = bool(
        nw["status"] == "PROVED"
        and kcs["all_verified"]
        and metric["passed"]
        and boundary_consistent
    )

    return {
        "cert_id": "PROOF_CLOSURE_FORMAL_CERT",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "scope": "conditional internal consistency only",
        "closure_earned": False,
        "physical_derivation_established": False,
        "n_w_uniqueness": {
            "status": nw["status"],
            "selected": nw.get("selected_n_w"),
        },
        "k_cs_algebra": {
            "all_verified": kcs["all_verified"],
            "pairs_checked": kcs["n_pairs_checked"],
        },
        "metric_boundary_consistency": {
            "metric_passed": metric["passed"],
            "metric_scope": metric["status"],
            "physical_derivation_established": False,
            "max_abs_error": metric["max_abs_error_vs_metric_module"],
            "boundary_area": area,
            "boundary_entropy": entropy,
            "boundary_consistent": boundary_consistent,
        },
        "overall_pass": passed,
        "status": "PASS" if passed else "TENSION",
    }
