# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Proof-closure hardening certificate for structural claims.

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
    """Return machine-checkable proof-closure packet for core structural claims."""
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
            "max_abs_error": metric["max_abs_error_vs_metric_module"],
            "boundary_area": area,
            "boundary_entropy": entropy,
            "boundary_consistent": boundary_consistent,
        },
        "overall_pass": passed,
        "status": "PASS" if passed else "TENSION",
    }
