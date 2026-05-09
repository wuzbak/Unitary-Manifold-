# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Canonical falsifier-first evidence feed for Tier Acceleration Sprint (v10.25)."""
from __future__ import annotations

from datetime import date
from typing import Dict, List

from src.core.cmbs4_monitor import monitoring_report as cmbs4_report
from src.core.desi_year3_monitor import monitoring_report as desi_report
from src.core.dune_dcp_monitor import monitoring_report as dune_report
from src.core.hyperk_juno_monitor import monitoring_report as hyperk_juno_report
from src.core.lab_litebird_substitute import lab_substitute_status_snapshot
from src.core.litebird_boundary import fail_zone_report
from src.core.litebird_readiness_hardening import litebird_prepublication_packet

__all__ = [
    "collect_canonical_evidence_feed",
    "falsifier_status_table",
    "falsifier_hard_gate",
]


def collect_canonical_evidence_feed() -> Dict:
    """Collect all critical experiment-facing falsifier reports."""
    litebird = fail_zone_report(0.331)
    litebird["readiness"] = litebird_prepublication_packet()
    return {
        "version": "v10.42",
        "generated_on": date.today().isoformat(),
        "experiments": {
            "litebird": litebird,
            "lab_cp_5_7": lab_substitute_status_snapshot(),
            "cmbs4": cmbs4_report(),
            "dune": dune_report(),
            "hyperk_juno": hyperk_juno_report(),
            "desi_year3": desi_report(),
        },
    }


def falsifier_status_table() -> List[Dict]:
    """Return compact status table for governance routing."""
    feed = collect_canonical_evidence_feed()["experiments"]
    litebird_pass = bool(feed["litebird"]["theory_passes"])
    litebird_status = "CONSISTENT" if litebird_pass else "EXCLUDED"

    return [
        {
            "experiment": "LiteBIRD",
            "status": litebird_status,
            "next_milestone": 2032,
            "primary_falsifier": True,
        },
        {
            "experiment": "Lab_CP_5_7",
            "status": feed["lab_cp_5_7"]["status"],
            "next_milestone": feed["lab_cp_5_7"]["next_milestone_year"],
            "primary_falsifier": True,
        },
        {
            "experiment": "CMB-S4",
            "status": feed["cmbs4"]["current_ns_verdict"]["level"],
            "next_milestone": feed["cmbs4"]["next_milestone"]["expected_year"],
            "primary_falsifier": False,
        },
        {
            "experiment": "DUNE",
            "status": feed["dune"]["current_verdict"]["level"],
            "next_milestone": feed["dune"]["next_milestone"]["first_physics"],
            "primary_falsifier": False,
        },
        {
            "experiment": "Hyper-K/JUNO",
            "status": feed["hyperk_juno"]["current_verdict"]["level"],
            "next_milestone": min(
                feed["hyperk_juno"]["next_milestone"]["juno_first_data"],
                feed["hyperk_juno"]["next_milestone"]["hyperk_first_data"],
            ),
            "primary_falsifier": False,
        },
        {
            "experiment": "DESI Year 3",
            "status": feed["desi_year3"]["routing"]["route"],
            "next_milestone": feed["desi_year3"]["next_milestone"]["expected_year"],
            "primary_falsifier": False,
        },
    ]


def falsifier_hard_gate() -> Dict:
    """Hard-gate snapshot over the canonical falsifier feed."""
    table = falsifier_status_table()
    failing = [row for row in table if row["status"] in {"EXCLUDED", "TENSION", "FALSIFIED"}]
    return {
        "pass": len(failing) == 0,
        "fail_count": len(failing),
        "failures": failing,
        "policy": "pass→freeze, fail→targeted_ticket",
    }
