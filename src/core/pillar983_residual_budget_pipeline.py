# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 983 — Residual Budget Pipeline (Sprint BL).

Decomposes each open lane into explicit budget components:
- EFT-exhausted contribution,
- UV-missing contribution,
- external-data pending contribution.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar982_architecture_limit_registry_runtime import (
    RUNTIME_ARCHITECTURE_LIMIT_REGISTRY,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "RESIDUAL_BUDGET_TABLE",
    "residual_budget_pipeline",
]

PILLAR_NUMBER: int = 983
PILLAR_GATE: str = "RESIDUAL_BUDGET_PIPELINE"

# Fractions sum to 1.0 per lane.
RESIDUAL_BUDGET_TABLE: List[Dict[str, Any]] = [
    {"lane": "B3_G4_FLUX", "eft_exhausted": 0.25, "uv_missing": 0.75, "external_pending": 0.00},
    {"lane": "CKM_THETA13", "eft_exhausted": 0.90, "uv_missing": 0.10, "external_pending": 0.00},
    {"lane": "FERMION_MASS_MAGNITUDES", "eft_exhausted": 0.30, "uv_missing": 0.70, "external_pending": 0.00},
    {"lane": "JARLSKOG_LAYER2", "eft_exhausted": 0.80, "uv_missing": 0.20, "external_pending": 0.00},
    {"lane": "CMB_AMP", "eft_exhausted": 0.85, "uv_missing": 0.15, "external_pending": 0.00},
    {"lane": "ALPHA_S_TYPE_B_FLOOR", "eft_exhausted": 0.35, "uv_missing": 0.65, "external_pending": 0.00},
    {"lane": "DESI_DR3", "eft_exhausted": 0.00, "uv_missing": 0.00, "external_pending": 1.00},
    {"lane": "LITEBIRD_BIREFRINGENCE", "eft_exhausted": 0.00, "uv_missing": 0.00, "external_pending": 1.00},
]


def _dominant_component(row: Dict[str, Any]) -> str:
    values = {
        "EFT_EXHAUSTED": float(row["eft_exhausted"]),
        "UV_MISSING": float(row["uv_missing"]),
        "EXTERNAL_PENDING": float(row["external_pending"]),
    }
    return max(values, key=values.get)


def residual_budget_pipeline() -> Dict[str, Any]:
    """Return residual budget table with routing labels and aggregate metrics."""
    registry_lanes = {row["lane"] for row in RUNTIME_ARCHITECTURE_LIMIT_REGISTRY}
    enriched: List[Dict[str, Any]] = []

    for row in RESIDUAL_BUDGET_TABLE:
        lane = str(row["lane"])
        total = float(row["eft_exhausted"] + row["uv_missing"] + row["external_pending"])
        enriched.append(
            {
                **row,
                "normalized": abs(total - 1.0) < 1e-9,
                "dominant": _dominant_component(row),
                "has_registry_row": lane in registry_lanes,
            }
        )

    n_uv_dominant = sum(1 for row in enriched if row["dominant"] == "UV_MISSING")
    n_external = sum(1 for row in enriched if row["dominant"] == "EXTERNAL_PENDING")
    n_eft = sum(1 for row in enriched if row["dominant"] == "EFT_EXHAUSTED")
    all_rows_normalized = all(row["normalized"] for row in enriched)
    all_architecture_rows_linked = all(
        row["has_registry_row"]
        for row in enriched
        if row["lane"] not in {"DESI_DR3", "LITEBIRD_BIREFRINGENCE"}
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": all_rows_normalized and all_architecture_rows_linked,
        "rows": enriched,
        "n_rows": len(enriched),
        "n_uv_dominant": n_uv_dominant,
        "n_eft_dominant": n_eft,
        "n_external_pending_dominant": n_external,
        "all_rows_normalized": all_rows_normalized,
        "all_architecture_rows_linked": all_architecture_rows_linked,
    }


PILLAR_STATUS: str = "RESIDUAL_BUDGET_PIPELINE_COMPLETE"
PILLAR_VALID: bool = residual_budget_pipeline()["all_rows_normalized"]
