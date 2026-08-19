# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar692_sprint_y_regression_cert.py
==========================
Pillar 692 — Sprint Y Regression Certificate

Runtime certificate for Sprint Y (Pillars 688–692).  This module verifies that
all Sprint Y public entry points return dict payloads with the expected keys.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import importlib
from typing import Any, Dict, List

__all__ = [
    "SPRINT_Y_PILLARS",
    "EXPECTED_TEST_COUNT",
    "sprint_y_regression_cert",
]

SPRINT_Y_PILLARS = [688, 689, 690, 691, 692]
EXPECTED_TEST_COUNT = 105


def sprint_y_regression_cert() -> Dict[str, Any]:
    """Return the Sprint Y regression certificate and enforce key contracts."""
    checks_spec = [
        (
            688,
            "src.core.pillar688_jarlskog_layer2_fn_mixing",
            [
                ("fn_phase_correction", {"delta_fn_deg", "epsilon_fn", "fn_charges_u", "fn_charges_d"}),
                ("rho_bar_fn_corrected", {"rho_bar_fn", "delta_eff_deg", "residual_percent"}),
                ("layer2_closure_status", {"status", "gap_percent", "passes_10_percent", "passes_5_percent"}),
                ("jarlskog_layer2_result", {"pillar", "status", "fn_phase_correction", "rho_bar_fn_corrected"}),
            ],
        ),
        (
            689,
            "src.core.pillar689_ckm_triangle_fn_geometry",
            [
                ("eta_bar_fn", {"eta_bar_fn", "rho_bar_fn", "residual_percent"}),
                ("wolfenstein_fn_corrected", {"lambda_fn", "A_fn", "rho_bar_fn", "eta_bar_fn"}),
                ("jarlskog_invariant_fn", {"J_CP_geo", "J_CP_fn", "J_CP_pdg"}),
                ("ckm_triangle_fn_geometry", {"pillar", "status", "triangle_coordinates", "jarlskog"}),
            ],
        ),
        (
            690,
            "src.core.pillar690_rho_bar_multi_layer_synthesis",
            [
                ("layer_improvement_table", None),
                ("final_rho_bar_status", {"status", "final_gap_percent", "best_layer"}),
                ("multi_layer_synthesis", {"pillar", "status", "layers", "final_status"}),
            ],
        ),
        (
            691,
            "src.core.pillar691_ckm_jarlskog_hardgate_assessment",
            [
                ("ckm_hardgate_assessment", {"pillar", "rho_bar", "eta_bar", "J_CP", "overall_pass"}),
                ("jarlskog_hardgate_verdict", {"overall_verdict", "failing_observables", "passing_observables"}),
                ("sprint_y_summary", {"pillar", "sprint", "status", "assessment", "verdict"}),
            ],
        ),
    ]

    checks: List[Dict[str, Any]] = []
    all_passed = True

    for pillar, module_path, entries in checks_spec:
        module = importlib.import_module(module_path)
        for func_name, expected_keys in entries:
            payload = getattr(module, func_name)()
            if func_name == "layer_improvement_table":
                assert isinstance(payload, list)
                assert len(payload) == 3
                assert all({"layer", "label", "rho_bar", "gap_percent"}.issubset(item.keys()) for item in payload)
                passed = True
                key_list = ["layer", "label", "rho_bar", "gap_percent"]
            else:
                assert isinstance(payload, dict)
                assert expected_keys is not None
                assert expected_keys.issubset(payload.keys())
                passed = True
                key_list = sorted(expected_keys)
            checks.append({
                "pillar": pillar,
                "module": module_path,
                "function": func_name,
                "passed": passed,
                "verified_keys": key_list,
            })

    assert all(item["passed"] for item in checks)

    return {
        "pillar": 692,
        "status": "SPRINT_Y_REGRESSION_PASSED" if all_passed else "SPRINT_Y_REGRESSION_FAILED",
        "sprint": "Sprint Y",
        "pillar_count": len(SPRINT_Y_PILLARS),
        "pillars": SPRINT_Y_PILLARS,
        "expected_test_count": EXPECTED_TEST_COUNT,
        "checks": checks,
        "all_passed": all_passed,
        "next_pillar_slot": 693,
    }
