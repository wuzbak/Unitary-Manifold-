# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 984 — Shared Compactification Parameter Object (Sprint BL)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

from src.core.pillar949_cy4_intersection_ring_g4_explicit import N_D3_FULL
from src.core.pillar951_fermion_ri_constraint_scaffold import CONSISTENCY_RATIO_MAX
from src.core.pillar937_alpha_s_13d_window_tighten import ALPHA_S_PDG, WINDOW_TIGHTENED
from src.core.pillar980_jarlskog_layer2_architecture_limit import (
    GAP_BASELINE,
    GAP_LOWER_BOUND,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "CompactificationParameterObject",
    "canonical_compactification_parameters",
    "compactification_parameter_summary",
]

PILLAR_NUMBER: int = 984
PILLAR_GATE: str = "COMPACTIFICATION_PARAMETER_OBJECT"


@dataclass(frozen=True)
class CompactificationParameterObject:
    """Single shared parameter object passed into cross-domain lanes."""

    n_w: int
    k_cs: int
    chi_cy4: int
    alpha_s_window: Tuple[float, float]
    alpha_s_pdg: float
    ri_window_max_abs: float
    n_d3_reference: float
    jarlskog_gap_window: Tuple[float, float]

    def is_valid(self) -> bool:
        low, high = self.alpha_s_window
        j_low, j_high = self.jarlskog_gap_window
        return (
            self.n_w == 5
            and self.k_cs == 74
            and self.chi_cy4 > 0
            and low < high
            and 0.0 < self.alpha_s_pdg < 1.0
            and 0.0 <= self.ri_window_max_abs < 1.0
            and self.n_d3_reference >= 0.0
            and 0.0 < j_low < j_high
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def canonical_compactification_parameters() -> CompactificationParameterObject:
    """Return canonical compactification parameter object for runtime scaffolding."""
    return CompactificationParameterObject(
        n_w=5,
        k_cs=74,
        chi_cy4=1820,
        alpha_s_window=WINDOW_TIGHTENED,
        alpha_s_pdg=ALPHA_S_PDG,
        ri_window_max_abs=abs(CONSISTENCY_RATIO_MAX),
        n_d3_reference=max(0.0, N_D3_FULL),
        jarlskog_gap_window=(GAP_LOWER_BOUND, GAP_BASELINE),
    )


def compactification_parameter_summary() -> Dict[str, Any]:
    """Return machine-readable summary."""
    obj = canonical_compactification_parameters()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": obj.is_valid() and PILLAR_VALID,
        "parameters": obj.to_dict(),
    }


PILLAR_STATUS: str = "COMPACTIFICATION_PARAMETER_OBJECT_COMPLETE"
PILLAR_VALID: bool = canonical_compactification_parameters().is_valid()
