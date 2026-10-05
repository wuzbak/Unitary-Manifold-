# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1011 — 10D flux-vacuum measure/selection bridge audit.

Adjacent sprint lane A:
- make the 10D flux-count story and vacuum-selection story one auditable object
- keep architecture/open labels explicit (no hidden promotion)
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.p28_lambda_10d_closure import effective_flux_sufficiency, explicit_vacuum_selection
from src.core.p28_lambda_first_principles import DUAL_FLUX_MULTIPLICITY
from src.eleventd.g4_flux_vacuum_link import CANDIDATES, candidate_flux_sector
from src.tend.flux_landscape import rung5_gate_evidence

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "flux_selection_measure_table",
    "flux_selection_measure_audit",
    "pillar1011_summary",
]

PILLAR_NUMBER: int = 1011
PILLAR_GATE: str = "TEN_D_FLUX_SELECTION_MEASURE_AUDIT"
PILLAR_STATUS: str = "TEN_D_FLUX_SELECTION_MEASURE_AUDIT_COMPLETE"


def _topological_partition_weight(n_w: int) -> float:
    """Return inverse topological-partition weight used for relative branch measure."""
    # Matches the closure-chain partition structure while keeping candidate comparison explicit.
    partition = float((2 * (n_w * n_w + (n_w + 2) * (n_w + 2)) // 2) * (n_w + 2))
    return 0.0 if partition <= 0.0 else 1.0 / partition


def flux_selection_measure_table() -> List[Dict[str, Any]]:
    """Return candidate-wise selection table with hard-gate + normalized measure."""
    rows: List[Dict[str, Any]] = []
    for n_w in CANDIDATES:
        sector = candidate_flux_sector(n_w)
        survives = bool(sector["candidate_survives_flux_background"])
        hard_gate_weight = 1.0 if survives else 0.0
        topo_weight = _topological_partition_weight(n_w)
        raw_measure = hard_gate_weight * topo_weight
        rows.append(
            {
                "n_w": n_w,
                "braid_pair": sector["braid_pair"],
                "k_cs": sector["k_cs"],
                "survives_flux_background": survives,
                "hard_gate_weight": hard_gate_weight,
                "topological_weight": topo_weight,
                "raw_measure": raw_measure,
                "sector_status": sector["status"],
            }
        )

    total_raw = sum(float(row["raw_measure"]) for row in rows)
    for row in rows:
        row["normalized_measure"] = (
            float(row["raw_measure"]) / total_raw if total_raw > 0.0 else 0.0
        )
    rows.sort(key=lambda row: row["n_w"])
    return rows


def flux_selection_measure_audit() -> Dict[str, Any]:
    """Return integrated R5 + closure + explicit-selection + candidate-measure audit."""
    rung5 = rung5_gate_evidence()
    flux = effective_flux_sufficiency()
    selection = explicit_vacuum_selection()
    table = flux_selection_measure_table()

    winner = selection["selection_summary"].get("unique_flux_selected_n_w")
    winner_row = next((row for row in table if row["n_w"] == winner), None)
    winner_weight = float(winner_row["normalized_measure"]) if winner_row else 0.0

    measure_is_unique = sum(1 for row in table if row["normalized_measure"] > 0.0) == 1
    all_gates_pass = bool(
        rung5["hard_gate_pass"]
        and flux["meets_bp_threshold"]
        and flux["spacing_below_lambda_obs"]
        and selection["explicit_selection_pass"]
    )

    valid = bool(
        all_gates_pass
        and measure_is_unique
        and winner == 5
        and winner_weight > 0.0
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "r5_hard_gate_pass": bool(rung5["hard_gate_pass"]),
        "effective_flux_sufficiency": flux,
        "explicit_selection": selection,
        "candidate_measure_table": table,
        "dual_flux_multiplicity_reference": DUAL_FLUX_MULTIPLICITY,
        "measure_unique_support": measure_is_unique,
        "selected_n_w": winner,
        "selected_normalized_measure": winner_weight,
        "interpretation": (
            "10D flux counting, explicit UV selection, and candidate weighting are now one "
            "auditable bridge object. The surviving support remains unique to n_w=5."
        ),
    }


PILLAR_VALID: bool = flux_selection_measure_audit()["valid"]


def pillar1011_summary() -> Dict[str, Any]:
    """Return concise Pillar 1011 summary."""
    report = flux_selection_measure_audit()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "10D Flux Selection Measure Audit",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "selected_n_w": report["selected_n_w"],
        "measure_unique_support": report["measure_unique_support"],
        "r5_hard_gate_pass": report["r5_hard_gate_pass"],
    }
