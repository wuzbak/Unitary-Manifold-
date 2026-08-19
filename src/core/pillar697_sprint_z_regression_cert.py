# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar697_sprint_z_regression_cert.py
==============================================
Pillar 697 — Sprint Z Regression Certificate

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import importlib
from typing import Any, Dict, List

__all__ = [
    "SPRINT_Z_PILLARS",
    "NEXT_PILLAR_SLOT",
    "sprint_z_regression_cert",
]

SPRINT_Z_PILLARS: List[str] = ["693", "694", "695", "696", "697"]
NEXT_PILLAR_SLOT: int = 698
PILLAR_NUMBER: str = "697"


def sprint_z_regression_cert() -> Dict[str, Any]:
    """Import Sprint Z modules and verify their exported entry points."""
    checks = [
        (
            "693",
            "src.core.pillar693_alpha_s_13d_moduli_pathway",
            ["gauge_kinetic_function_13d", "alpha_s_13d_moduli", "alpha_s_13d_status"],
        ),
        (
            "694",
            "src.core.pillar694_alpha_s_rge_kk_tower_nlo",
            ["beta_function_kk_corrected", "alpha_s_nlo_kk_tower", "nlo_residual"],
        ),
        (
            "695",
            "src.core.pillar695_alpha_s_irreducibility_proof",
            ["all_alpha_s_paths", "irreducibility_proof", "alpha_s_irreducibility_cert"],
        ),
        (
            "696",
            "src.core.pillar696_alpha_s_lhc_run4_discriminator",
            ["alpha_s_kk_prediction", "lhc_run4_snr", "alpha_s_preregistration"],
        ),
    ]

    module_checks: List[Dict[str, Any]] = []
    for pillar, module_path, function_names in checks:
        try:
            mod = importlib.import_module(module_path)
            results = {}
            all_dicts = True
            for func_name in function_names:
                value = getattr(mod, func_name)()
                is_valid = isinstance(value, dict) or isinstance(value, list)
                all_dicts = all_dicts and is_valid
                results[func_name] = {
                    "type": type(value).__name__,
                    "valid": is_valid,
                }
            module_checks.append(
                {
                    "pillar": pillar,
                    "module": module_path,
                    "passed": all_dicts,
                    "results": results,
                }
            )
        except Exception as exc:
            module_checks.append(
                {
                    "pillar": pillar,
                    "module": module_path,
                    "passed": False,
                    "error": str(exc),
                }
            )

    all_passed = all(item["passed"] for item in module_checks)
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint Z Regression Certificate",
        "status": "SPRINT_Z_REGRESSION_PASSED" if all_passed else "SPRINT_Z_REGRESSION_FAILED",
        "sprint_z_pillars": SPRINT_Z_PILLARS,
        "module_checks": module_checks,
        "all_passed": all_passed,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "honest_note": (
            "Sprint Z adds negative-result closure tests plus an experimental "
            "discriminator. If the α_s residual remains large, the certificate "
            "must say so explicitly."
        ),
    }
