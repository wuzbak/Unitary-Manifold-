# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/pillar720_sprint_dd_regression_cert.py
==================================================
Pillar 720 — Sprint DD Regression Certificate

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Dict, List

from src.quantum.pillar716_xdiag_production_stub import (
    U_OVER_T_KK as P716_U_OVER_T_KK,
    double_occupancy_mott,
    mock_xdiag_solve,
    mott_energy_analytic,
    xdiag_stub_health_check,
)
from src.quantum.pillar717_fh_braid_geometry_hardening import (
    braid_bandwidth,
    fh_braid_hamiltonian_params,
    mott_gap_estimate,
    mott_insulator_verdict,
)
from src.quantum.pillar718_kk_vqe_hardening import (
    kk_vqe_params,
    vqe_fidelity_estimate,
    vqe_hardening_checks,
)
from src.quantum.pillar719_quantum_lane_phase3_synthesis import (
    quantum_lane_full_status,
    quantum_lane_phase3_synthesis,
)

PILLAR_NUMBER = 720

__all__ = ["PILLAR_NUMBER", "sprint_dd_regression_cert"]


def sprint_dd_regression_cert() -> Dict[str, object]:
    """Call the Sprint DD APIs and certify that all return valid payloads."""
    payloads = {
        "p716_mott_energy_analytic": mott_energy_analytic(),
        "p716_double_occupancy_mott": double_occupancy_mott(),
        "p716_mock_xdiag_solve": mock_xdiag_solve(10, P716_U_OVER_T_KK, "periodic"),
        "p716_xdiag_stub_health_check": xdiag_stub_health_check(),
        "p717_fh_braid_hamiltonian_params": fh_braid_hamiltonian_params(),
        "p717_braid_bandwidth": braid_bandwidth(),
        "p717_mott_gap_estimate": mott_gap_estimate(),
        "p717_mott_insulator_verdict": mott_insulator_verdict(),
        "p718_kk_vqe_params": kk_vqe_params(),
        "p718_vqe_fidelity_estimate": vqe_fidelity_estimate(),
        "p718_vqe_hardening_checks": vqe_hardening_checks(),
        "p719_quantum_lane_phase3_synthesis": quantum_lane_phase3_synthesis(),
        "p719_quantum_lane_full_status": quantum_lane_full_status(),
    }
    all_payloads_are_dicts = all(isinstance(payload, dict) for payload in payloads.values())
    has_epistemic_labels = all("epistemic_status" in payload for payload in payloads.values())
    return {
        "pillar": PILLAR_NUMBER,
        "checked_functions": list(payloads),
        "n_checked_functions": len(payloads),
        "all_payloads_are_dicts": all_payloads_are_dicts,
        "all_payloads_have_epistemic_status": has_epistemic_labels,
        "phase3_synthesized": payloads["p719_quantum_lane_phase3_synthesis"][
            "quantum_lane_phase3_synthesized"
        ],
        "stub_validated": payloads["p716_xdiag_stub_health_check"]["validated"],
        "mott_verdict": payloads["p717_mott_insulator_verdict"]["is_mott_insulator"],
        "vqe_hardening_pass": payloads["p718_vqe_hardening_checks"]["all_checks_pass"],
        "all_regressions_pass": (
            all_payloads_are_dicts
            and has_epistemic_labels
            and payloads["p716_xdiag_stub_health_check"]["validated"]
            and payloads["p717_mott_insulator_verdict"]["is_mott_insulator"]
            and payloads["p718_vqe_hardening_checks"]["all_checks_pass"]
            and payloads["p719_quantum_lane_phase3_synthesis"]["quantum_lane_phase3_synthesized"]
        ),
        "epistemic_status": "SCAFFOLD",
    }
