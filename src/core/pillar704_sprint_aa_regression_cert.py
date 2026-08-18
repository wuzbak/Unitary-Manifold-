# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar704_sprint_aa_regression_cert.py
===============================================
Pillar 704 — Sprint AA Regression Certificate

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Dict

from src.core.pillar698_cmb_phase2_boltzmann_solver import (
    cl_from_hierarchy,
    phase2_amplitude_audit,
    solve_boltzmann_kk,
)
from src.core.pillar699_cmb_zphi_phase2_closure import (
    suppression_coverage,
    zphi_closure_status,
    zphi_phase2_total,
)
from src.core.pillar700_cmb_s4_kk_residual_forecast import (
    cmb_residual_after_phase2,
    kk_cmb_s4_snr,
    kk_litebird_snr,
)
from src.core.pillar701_cmb_amplitude_layer_synthesis import (
    amplitude_layer_synthesis,
    cmb_amplitude_final_status,
)
from src.core.pillar702_cmb_peak_ratio_kk_prediction import (
    peak_height_ratios_um,
    peak_ratio_kk_correction,
    peak_ratio_planck_comparison,
)
from src.core.pillar703_cmb_fullchain_audit import (
    cmb_fullchain_audit,
    cmb_sprint_aa_summary,
)

PILLAR_NUMBER = 704

__all__ = ["PILLAR_NUMBER", "sprint_aa_regression_cert"]


def sprint_aa_regression_cert() -> Dict[str, object]:
    """Call all Sprint AA public APIs and certify basic regression integrity."""
    checks = {
        "p698_solver": solve_boltzmann_kk(0.02, n_tau_steps=60),
        "p698_cl": cl_from_hierarchy(200, n_k=6),
        "p698_audit": phase2_amplitude_audit(),
        "p699_total": zphi_phase2_total(),
        "p699_coverage": suppression_coverage(),
        "p699_status": zphi_closure_status(),
        "p700_s4": kk_cmb_s4_snr(),
        "p700_litebird": kk_litebird_snr(),
        "p700_residual": cmb_residual_after_phase2(),
        "p701_layers": amplitude_layer_synthesis(),
        "p701_status": cmb_amplitude_final_status(),
        "p702_ratios": peak_height_ratios_um(),
        "p702_delta": peak_ratio_kk_correction(),
        "p702_planck": peak_ratio_planck_comparison(),
        "p703_audit": cmb_fullchain_audit(),
        "p703_summary": cmb_sprint_aa_summary(),
    }
    dict_checks = {name: isinstance(value, dict) for name, value in checks.items()}
    return {
        "pillar": PILLAR_NUMBER,
        "status": "REGRESSION_CERTIFIED" if all(dict_checks.values()) else "REGRESSION_FAILED",
        "all_dicts": all(dict_checks.values()),
        "checks": dict_checks,
        "artifacts": checks,
    }
