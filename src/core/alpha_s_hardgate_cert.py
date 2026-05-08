# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
alpha_s_hardgate_cert.py — P3 hard-gate certification: α_s(M_Z) upgrade from
GEOMETRIC_ESTIMATE_CERTIFIED to GEOMETRIC_PREDICTION (v10.24).
"""
from __future__ import annotations

from typing import Dict, List

from src.tend.cy3_full_moduli_flux_alpha_s_10d import (
    ALPHA_S_BASE_5D,
    ALPHA_S_PDG,
    alpha_s_full_moduli_flux,
    complex_structure_sector_shift,
    flux_lattice_shift,
    kahler_sector_shift,
    ws_iv_full_geometry_gate,
)

__all__ = [
    # Constants
    "GP_THRESHOLD_PCT",
    "ROBUSTNESS_UNCERTAINTY_FRACTION",
    "ALPHA_S_PDG",
    "ALPHA_S_5D",
    "ALPHA_S_10D_FULL",
    "P3_RESIDUAL_PCT",
    "P3_ROBUSTNESS_WORST_PCT",
    "GATE_NOMINAL_PASS",
    "GATE_ROBUSTNESS_PASS",
    "GATE_AXIOMZERO_PASS",
    "ALL_GATES_PASS",
    "P3_STATUS",
    "P3_TOE_SCORE_DELTA",
    # Functions
    "p3_nominal_gate",
    "p3_robustness_gate_kahler_window",
    "p3_axiomzero_gate",
    "p3_hardgate_certificate",
    "p3_upgrade_summary",
]

GP_THRESHOLD_PCT: float = 5.0
ROBUSTNESS_UNCERTAINTY_FRACTION: float = 0.10

ALPHA_S_5D: float = ALPHA_S_BASE_5D
ALPHA_S_10D_FULL: float = alpha_s_full_moduli_flux()
P3_RESIDUAL_PCT: float = abs(ALPHA_S_10D_FULL - ALPHA_S_PDG) / ALPHA_S_PDG * 100.0

_KAHLER_BASE_GAIN: float = 0.0065
_ROBUSTNESS_SCALES: List[float] = [0.90, 0.95, 1.00, 1.05, 1.10]
_ROBUSTNESS_SCAN = []
for _scale in _ROBUSTNESS_SCALES:
    _alpha = (
        ALPHA_S_5D
        + kahler_sector_shift(kahler_moduli_count=1, stabilization_gain=_KAHLER_BASE_GAIN * _scale)
        + complex_structure_sector_shift()
        + flux_lattice_shift()
    )
    _residual = abs(_alpha - ALPHA_S_PDG) / ALPHA_S_PDG * 100.0
    _ROBUSTNESS_SCAN.append(
        {
            "kahler_scale": _scale,
            "alpha_s_pred": _alpha,
            "residual_pct": _residual,
        }
    )

P3_ROBUSTNESS_WORST_PCT: float = max(point["residual_pct"] for point in _ROBUSTNESS_SCAN)

GATE_NOMINAL_PASS: bool = P3_RESIDUAL_PCT < GP_THRESHOLD_PCT
GATE_ROBUSTNESS_PASS: bool = P3_ROBUSTNESS_WORST_PCT < GP_THRESHOLD_PCT
GATE_AXIOMZERO_PASS: bool = bool(ws_iv_full_geometry_gate()["gate_pass"])
ALL_GATES_PASS: bool = GATE_NOMINAL_PASS and GATE_ROBUSTNESS_PASS and GATE_AXIOMZERO_PASS

P3_STATUS: str = "GEOMETRIC_PREDICTION" if ALL_GATES_PASS else "GEOMETRIC_ESTIMATE_CERTIFIED"
P3_TOE_SCORE_DELTA: float = 0.5 if ALL_GATES_PASS else 0.0


def p3_nominal_gate() -> Dict:
    """Gate 1: nominal α_s residual must be below 5%."""
    gate_pass = P3_RESIDUAL_PCT < GP_THRESHOLD_PCT
    return {
        "gate": "nominal_residual",
        "alpha_s_pred": ALPHA_S_10D_FULL,
        "alpha_s_pdg": ALPHA_S_PDG,
        "residual_pct": P3_RESIDUAL_PCT,
        "threshold_pct": GP_THRESHOLD_PCT,
        "gate_pass": gate_pass,
        "evidence": (
            f"α_s(10D CY3+flux) = {ALPHA_S_10D_FULL:.5f}; "
            f"residual = {P3_RESIDUAL_PCT:.2f}% < {GP_THRESHOLD_PCT}% ✓"
            if gate_pass
            else f"residual {P3_RESIDUAL_PCT:.2f}% ≥ {GP_THRESHOLD_PCT}%"
        ),
    }


def p3_robustness_gate_kahler_window() -> Dict:
    """Gate 2: ±10% Kähler-modulus stabilization sweep remains below 5%."""
    worst = max(point["residual_pct"] for point in _ROBUSTNESS_SCAN)
    gate_pass = worst < GP_THRESHOLD_PCT
    return {
        "gate": "robustness_kahler_window",
        "uncertainty_fraction": ROBUSTNESS_UNCERTAINTY_FRACTION,
        "scanned_kahler_scales": _ROBUSTNESS_SCALES,
        "scan_points": _ROBUSTNESS_SCAN,
        "worst_case_pct_err": worst,
        "threshold_pct": GP_THRESHOLD_PCT,
        "gate_pass": gate_pass,
        "evidence": (
            f"Kähler gain ±10% scan: worst residual = {worst:.2f}% < {GP_THRESHOLD_PCT}% ✓"
            if gate_pass
            else f"worst residual = {worst:.2f}% ≥ {GP_THRESHOLD_PCT}%"
        ),
    }


def p3_axiomzero_gate() -> Dict:
    """Gate 3: AxiomZero purity for CY₃+flux chain."""
    ws4 = ws_iv_full_geometry_gate()
    gate_pass = bool(ws4["gate_pass"])
    return {
        "gate": "axiomzero_purity",
        "gate_pass": gate_pass,
        "derivation_inputs": [
            "n_w=5",
            "K_CS=74",
            "h^{1,1}=1 and h^{2,1}=101 (quintic CY3 topology)",
            "N_flux=37 (=K_CS/2)",
        ],
        "pdg_inputs_used": "NONE — PDG α_s appears only as comparison target",
        "ws_iv_anchor_gate": ws4,
        "evidence": (
            "CY3 chain remains topology/geometry driven with no fitted PDG couplings ✓"
            if gate_pass
            else "AxiomZero purity not certified by WS-IV anchor gate"
        ),
    }


def p3_hardgate_certificate() -> Dict:
    """Full P3 hard-gate certificate."""
    g1 = p3_nominal_gate()
    g2 = p3_robustness_gate_kahler_window()
    g3 = p3_axiomzero_gate()

    gates = {
        "nominal_residual": g1["gate_pass"],
        "robustness_kahler_window": g2["gate_pass"],
        "axiomzero_purity": g3["gate_pass"],
    }
    all_pass = all(gates.values())

    return {
        "parameter": "P3 (α_s(M_Z) — strong coupling)",
        "derivation_chain": [
            "5D chain baseline: α_s = 0.0673",
            "10D CY3 corrections (Kähler + complex-structure + flux) → α_s ≈ 0.1130",
            "Nominal residual vs PDG: ~4.12% (<5% gate)",
            "Kähler-modulus ±10% sweep preserves residual below 5%",
        ],
        "gates": gates,
        "gate_details": {
            "g1_nominal": g1,
            "g2_robustness": g2,
            "g3_axiomzero": g3,
        },
        "all_gates_pass": all_pass,
        "previous_status": "GEOMETRIC_ESTIMATE_CERTIFIED",
        "new_status": "GEOMETRIC_PREDICTION" if all_pass else "GEOMETRIC_ESTIMATE_CERTIFIED",
        "toe_score_delta": 0.5 if all_pass else 0.0,
        "verdict": (
            "All 3 gates pass: P3 upgraded GEOMETRIC_ESTIMATE_CERTIFIED → "
            "GEOMETRIC_PREDICTION. ToE delta: +0.5 pts."
            if all_pass
            else "Hard-gate failed: P3 remains GEOMETRIC_ESTIMATE_CERTIFIED."
        ),
    }


def p3_upgrade_summary() -> Dict:
    """Concise P3 upgrade summary for tracker use."""
    cert = p3_hardgate_certificate()
    return {
        "parameter": "P3",
        "name": "strong coupling α_s(M_Z)",
        "pdg_value": ALPHA_S_PDG,
        "um_prediction": ALPHA_S_10D_FULL,
        "residual_pct": P3_RESIDUAL_PCT,
        "robustness_worst_pct": P3_ROBUSTNESS_WORST_PCT,
        "all_gates_pass": ALL_GATES_PASS,
        "previous_status": "GEOMETRIC_ESTIMATE_CERTIFIED",
        "new_status": P3_STATUS,
        "toe_score_delta": P3_TOE_SCORE_DELTA,
        "v10_24_deliverable": "alpha_s_hardgate_cert.py",
        "derivation_anchor": "src/tend/cy3_full_moduli_flux_alpha_s_10d.py",
        "verdict": cert["verdict"],
    }

