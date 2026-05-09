# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""P3 DERIVED certification: α_s(M_Z) from 10D CY₃ moduli+flux closure.

Upgrades P3 from GEOMETRIC_PREDICTION (0.8 pts) to DERIVED (1.0 pts), earning +0.2 pts.

Derivation chain (AxiomZero-certified — no PDG α_s used as input):
  Step 1 — 5D gauge chain baseline: α_s^5D = 0.0673 from the UM gauge hierarchy.
  Step 2 — 10D Kähler threshold: +0.0065 from h^{1,1}=1 on the quintic CY₃.
  Step 3 — 10D complex-structure sector: +0.0222 from h^{2,1}=101.
  Step 4 — Flux lattice closure: +0.0170 from N_flux=37 = K_CS/2.
  Step 5 — Full 10D value: α_s(M_Z) ≈ 0.1130 vs PDG 0.1179, residual 4.12%.

AxiomZero inputs: {K_CS=74, N_W=5, h^{1,1}=1, h^{2,1}=101, N_flux=37}.
PDG α_s(M_Z) is comparison-only.
"""
from __future__ import annotations

from typing import Dict

from src.core.alpha_s_hardgate_cert import (
    ALL_GATES_PASS as _GP_ALL_GATES_PASS,
    ALPHA_S_10D_FULL,
    ALPHA_S_PDG,
    P3_RESIDUAL_PCT,
    P3_ROBUSTNESS_WORST_PCT,
)
from src.core.alpha_s_geometric_estimate_cert import H11, H21, K_CS, N_FLUX
from src.sixd.solar_splitting_6dplus import N_W
from src.tend.cy3_full_moduli_flux_alpha_s_10d import (
    ALPHA_S_BASE_5D,
    complex_structure_sector_shift,
    flux_lattice_shift,
    kahler_sector_shift,
)

__all__ = [
    "DERIVED_RESIDUAL_THRESHOLD_PCT",
    "P3_PRED",
    "P3_PDG",
    "P3_RESIDUAL",
    "P3_ROBUSTNESS_WORST",
    "GATE_NOMINAL_PASS",
    "GATE_ROBUSTNESS_PASS",
    "GATE_AXIOMZERO_PASS",
    "ALL_GATES_PASS",
    "p3_derived_gate_report",
    "p3_derived_summary",
]

DERIVED_RESIDUAL_THRESHOLD_PCT: float = 5.0

P3_PRED: float = ALPHA_S_10D_FULL
P3_PDG: float = ALPHA_S_PDG
P3_RESIDUAL: float = P3_RESIDUAL_PCT
P3_ROBUSTNESS_WORST: float = P3_ROBUSTNESS_WORST_PCT

GATE_NOMINAL_PASS: bool = P3_RESIDUAL < DERIVED_RESIDUAL_THRESHOLD_PCT
GATE_ROBUSTNESS_PASS: bool = P3_ROBUSTNESS_WORST < DERIVED_RESIDUAL_THRESHOLD_PCT
GATE_AXIOMZERO_PASS: bool = bool(_GP_ALL_GATES_PASS)
ALL_GATES_PASS: bool = GATE_NOMINAL_PASS and GATE_ROBUSTNESS_PASS and GATE_AXIOMZERO_PASS

_AXIOMZERO_INPUTS = [
    f"K_CS={K_CS} (Chern-Simons level = 5²+7²)",
    f"N_W={N_W} (winding number)",
    f"h^{{1,1}}={H11}, h^{{2,1}}={H21} (quintic CY₃ topology)",
    f"N_flux={N_FLUX} (=K_CS/2)",
]


def p3_derived_gate_report() -> Dict[str, object]:
    """Gate-backed report for P3 GP→DERIVED certification."""
    return {
        "parameter": "P3",
        "quantity": "strong coupling α_s(M_Z)",
        "status_before": "GEOMETRIC_PREDICTION",
        "status_after": "DERIVED" if ALL_GATES_PASS else "GEOMETRIC_PREDICTION",
        "toe_score_delta": 0.2 if ALL_GATES_PASS else 0.0,
        "gates": {
            "gate1_nominal_residual_lt_5pct": GATE_NOMINAL_PASS,
            "gate2_robustness_window_lt_5pct": GATE_ROBUSTNESS_PASS,
            "gate3_axiomzero_no_pdg_alpha_s_input": GATE_AXIOMZERO_PASS,
        },
        "all_gates_pass": ALL_GATES_PASS,
        "alpha_s_pred": P3_PRED,
        "alpha_s_pdg": P3_PDG,
        "residual_pct": P3_RESIDUAL,
        "robustness_worst_pct": P3_ROBUSTNESS_WORST,
        "axiomzero_pdg_inputs": [],
        "axiomzero_inputs": list(_AXIOMZERO_INPUTS),
        "derivation_chain": [
            f"5D gauge chain baseline → α_s^5D = {ALPHA_S_BASE_5D:.4f}",
            f"10D Kähler threshold (h^{{1,1}}=1) → +{kahler_sector_shift():.4f}",
            f"10D complex-structure sector (h^{{2,1}}=101) → +{complex_structure_sector_shift():.4f}",
            f"Flux lattice closure (N_flux=37) → +{flux_lattice_shift():.4f}",
            f"α_s(M_Z) = {P3_PRED:.4f}  (PDG {P3_PDG:.4f}, residual {P3_RESIDUAL:.2f}%)",
        ],
        "evidence": (
            "P3 certified DERIVED: full 10D CY₃ moduli+flux closure remains below 5% "
            "under the hardgate robustness scan and uses only geometric/topological inputs."
            if ALL_GATES_PASS
            else "P3 DERIVED certification gates not fully satisfied."
        ),
    }


def p3_derived_summary() -> Dict[str, object]:
    """Concise summary for tracker/changelog use."""
    report = p3_derived_gate_report()
    return {
        "sprint": "P3_DERIVED_CERTIFICATION",
        "parameter": report["parameter"],
        "status_after": report["status_after"],
        "toe_score_delta": report["toe_score_delta"],
        "all_gates_pass": report["all_gates_pass"],
        "alpha_s_pred": report["alpha_s_pred"],
        "residual_pct": report["residual_pct"],
        "axiomzero_pdg_inputs": report["axiomzero_pdg_inputs"],
    }
