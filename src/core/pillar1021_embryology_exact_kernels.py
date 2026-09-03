# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1021 — Embryology exact-kernel promotion bundle.

This pillar promotes only the exact, decomposition-safe kernels identified in
the embryology lane:

- HOX cluster count: 2^(n₂−n₁)=4
- HOX co-linearity order kernel: mirror pairing + S¹/Z₂ unrolling
- centrosome integer kernels: 9 triplets and 10 B/C protofilaments
- critical hydration exact kernel: ε_r,crit = 1/c_s²

What it does not promote:

- vertebrate ``HOX_groups = 10`` as a biology-wide claim,
- full HOX transcription-boundary closure,
- centrosome curvature-reader mechanism,
- medium-dependent hydration conversions as exact theorems.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.biology.centrosome_integer_kernels import centrosome_integer_kernel_report
from src.biology.critical_hydration_kernels import critical_hydration_kernel_report
from src.biology.hox_exact_kernels import hox_exact_kernel_report
from src.biology.hox_kk_alignment import hox_report

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "embryology_exact_kernel_bundle",
    "pillar1021_summary",
]

PILLAR_NUMBER: int = 1021
PILLAR_GATE: str = "EMBRYOLOGY_EXACT_KERNEL_PROMOTION_BUNDLE"
PILLAR_STATUS: str = "EMBRYOLOGY_EXACT_KERNELS_CERTIFIED"


def embryology_exact_kernel_bundle() -> Dict[str, Any]:
    """Return the exact-kernel promotion bundle for the embryology lane."""
    hox = hox_exact_kernel_report()
    alignment = hox_report()
    centrosome = centrosome_integer_kernel_report()
    hydration = critical_hydration_kernel_report()
    exact_statuses = [
        hox["cluster_kernel_status"],
        hox["colinearity_kernel"]["status"],
        centrosome["triplet_kernel_status"],
        centrosome["protofilament_kernel_status"],
        hydration["exact_kernel_status"],
    ]
    valid = (
        all(status == "DERIVED_STRUCTURAL" for status in exact_statuses)
        and hox["cluster_count"] == 4
        and hox["vertebrate_group_count"]["status"] == "FORMAL_ANALOGY_ONLY"
        and alignment["pillar_classification"].startswith("🔵 ADJACENT TRACK")
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "exact_promotions": {
            "hox_clusters": hox["cluster_kernel_status"],
            "hox_colinearity_order": hox["colinearity_kernel"]["status"],
            "centrosome_triplets": centrosome["triplet_kernel_status"],
            "centrosome_protofilaments": centrosome["protofilament_kernel_status"],
            "hydration_dielectric_threshold": hydration["exact_kernel_status"],
        },
        "contained_non_promotions": {
            "vertebrate_hox_groups_eq_10": hox["vertebrate_group_count"]["status"],
            "hox_boundary_spacing_lane": "EMPIRICAL_AUDIT_RETAINED",
            "centrosome_curvature_reader": centrosome["mechanism_status"],
            "hydration_mass_ratio_exactness": hydration["model_dependent_prediction_status"],
        },
        "dependencies": {
            "hox_exact_kernels": hox,
            "hox_empirical_alignment": {
                "tier1_overall": alignment["tier1_overall"],
                "pillar_classification": alignment["pillar_classification"],
                "promotion_condition": alignment["promotion_condition"],
            },
            "centrosome_integer_kernels": centrosome,
            "critical_hydration_kernels": hydration,
        },
        "what_is_claimed": [
            "HOX cluster count = 2^(n₂−n₁)=4 is promotion-safe and structurally exact",
            "HOX co-linearity is promoted only as an order-preserving orbifold-unrolling kernel",
            "Centrosome triplet and B/C protofilament counts are promoted only as integer identities",
            "The dielectric threshold ε_r,crit = 1/c_s² is promoted as the exact hydration kernel",
        ],
        "what_is_NOT_claimed": [
            "Vertebrate HOX group count is not promoted as 10; it remains analogy-only",
            "The empirical HOX boundary-fit lane is not upgraded by this pillar",
            "The centrosome curvature-reader mechanism is not closed here",
            "Water-fraction and mass-ratio hydration conversions remain model-dependent",
        ],
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }


PILLAR_VALID: bool = bool(embryology_exact_kernel_bundle()["valid"])


def pillar1021_summary() -> Dict[str, Any]:
    """Return concise Pillar 1021 summary."""
    report = embryology_exact_kernel_bundle()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Embryology Exact-Kernel Promotion Bundle",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "hox_cluster_count": report["dependencies"]["hox_exact_kernels"]["cluster_count"],
        "exact_promotion_count": len(report["exact_promotions"]),
    }
