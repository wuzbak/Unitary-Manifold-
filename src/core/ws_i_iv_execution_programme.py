# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
ws_i_iv_execution_programme.py — Machine-readable execution record for the
post-MAS WS-I..WS-IV independent programme.

This programme executes all four dimensional-extension workstreams in the
recommended order:
    WS-II → WS-III → WS-I → WS-IV

Governance:
  - Independent of MAS (MAS remains closed)
  - Binary exits per workstream: PASS_FREEZE or TARGETED_FOLLOW_UP_FREEZE
  - No recycling of findings into MAS
"""
from __future__ import annotations

from typing import Dict, List

__all__ = [
    "EXECUTION_DATE",
    "EXECUTION_ORDER",
    "UMBRELLA_TRACKER_ARTIFACT",
    "WS_EXECUTION_PROGRAMME",
    "FULL_REGRESSION_GATE_COMMAND",
    "list_programme_workstreams",
    "get_programme_workstream",
    "execution_programme_summary",
]

EXECUTION_DATE: str = "2026-05-08"
EXECUTION_ORDER: List[str] = ["WS-II", "WS-III", "WS-I", "WS-IV"]
UMBRELLA_TRACKER_ARTIFACT: str = "docs/WS_I_IV_EXECUTION_PROGRAMME_ISSUE.md"
FULL_REGRESSION_GATE_COMMAND: str = (
    "python3 -m pytest tests/ recycling/ "
    "\"5-GOVERNANCE/Unitary Pentad/\" -q "
    "--ignore=tests/test_symbolic_metric.py "
    "--ignore=tests/test_formal_proof_hardening.py "
    "--ignore=tests/test_neural_symbolic_drift_check.py"
)

WS_EXECUTION_PROGRAMME: Dict[str, Dict] = {
    "WS-II": {
        "order": 1,
        "parameter_target": "P14, P15",
        "execution_artifact": "src/nined/cp_phase_9d_refinement.py",
        "test_artifact": "tests/test_nined_cp_phase_9d_refinement.py",
        "status": "PASS_FREEZE",
        "outcome": "9D refinement remains robust (<5% propagated uncertainty).",
        "post_freeze_action": "frozen",
        "recycle_into_mas": False,
    },
    "WS-III": {
        "order": 2,
        "parameter_target": "P19, P20, P21",
        "execution_artifact": "src/sixd/neutrino_overlap_integrals_nlo.py",
        "test_artifact": "tests/test_sixd_neutrino_overlap_integrals_nlo.py",
        "status": "TARGETED_FOLLOW_UP_FREEZE",
        "outcome": "NLO improvement retained; simultaneous Δm²₂₁/Δm²₃₁ closure remains 6D+ follow-up.",
        "post_freeze_action": "open_targeted_workstream_ticket",
        "recycle_into_mas": False,
    },
    "WS-I": {
        "order": 3,
        "parameter_target": "P5",
        "execution_artifact": "src/sixd/higgs_radion_mixing_6d.py",
        "test_artifact": "tests/test_sixd_higgs_radion_mixing_6d.py",
        "status": "TARGETED_FOLLOW_UP_FREEZE",
        "outcome": "θ_HR mechanism remains active; exact geometric closure still 6D+ follow-up.",
        "post_freeze_action": "open_targeted_workstream_ticket",
        "recycle_into_mas": False,
    },
    "WS-IV": {
        "order": 4,
        "parameter_target": "P3",
        "execution_artifact": "src/tend/cy3_kk_thresholds_alpha_s.py",
        "test_artifact": "tests/test_tend_cy3_kk_thresholds_alpha_s.py",
        "status": "TARGETED_FOLLOW_UP_FREEZE",
        "outcome": "10D CY₃ correction retained; full α_s closure remains full-moduli/flux follow-up.",
        "post_freeze_action": "open_targeted_workstream_ticket",
        "recycle_into_mas": False,
    },
}


def list_programme_workstreams() -> List[str]:
    """Return WS IDs in the official execution order."""
    return list(EXECUTION_ORDER)


def get_programme_workstream(ws_id: str) -> Dict:
    """Return execution record for WS *ws_id*."""
    if ws_id not in WS_EXECUTION_PROGRAMME:
        raise KeyError(
            f"Unknown workstream: {ws_id!r}. "
            f"Available: {sorted(WS_EXECUTION_PROGRAMME)}"
        )
    return dict(WS_EXECUTION_PROGRAMME[ws_id])


def execution_programme_summary() -> Dict:
    """Return summary for the WS-I..WS-IV execution programme."""
    statuses = [entry["status"] for entry in WS_EXECUTION_PROGRAMME.values()]
    pass_count = sum(status == "PASS_FREEZE" for status in statuses)
    targeted_count = sum(status == "TARGETED_FOLLOW_UP_FREEZE" for status in statuses)
    return {
        "execution_date": EXECUTION_DATE,
        "umbrella_tracker_artifact": UMBRELLA_TRACKER_ARTIFACT,
        "execution_order": list_programme_workstreams(),
        "workstream_count": len(WS_EXECUTION_PROGRAMME),
        "pass_freeze_count": pass_count,
        "targeted_follow_up_freeze_count": targeted_count,
        "mas_reopen_allowed": False,
        "recycle_into_mas_allowed": False,
        "regression_gate_command": FULL_REGRESSION_GATE_COMMAND,
        "all_records_no_mas_recycle": all(
            not entry["recycle_into_mas"] for entry in WS_EXECUTION_PROGRAMME.values()
        ),
    }

