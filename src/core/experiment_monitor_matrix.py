# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
experiment_monitor_matrix.py — unified machine-readable monitor matrix.

Aggregates the experiment-facing monitor harnesses for:
  - CMB-S4 (n_s, r)
  - DUNE (δ_CP)
  - Hyper-K / JUNO (Δm²₃₁)
  - DESI Year 3 (w₀, wₐ)
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List

from src.core.cmbs4_monitor import monitoring_report as cmbs4_monitoring_report
from src.core.desi_year3_monitor import monitoring_report as desi_monitoring_report
from src.core.dune_dcp_monitor import monitoring_report as dune_monitoring_report
from src.core.hyperk_juno_monitor import monitoring_report as hyperk_juno_monitoring_report

__all__ = [
    "collect_monitor_reports",
    "monitoring_status_table",
    "hard_gate_snapshot",
    "machine_readable_monitor_bundle",
]


def collect_monitor_reports() -> Dict:
    """Collect all monitor reports in one dictionary."""
    return {
        "version": "v10.18",
        "cmbs4": cmbs4_monitoring_report(),
        "dune": dune_monitoring_report(),
        "hyperk_juno": hyperk_juno_monitoring_report(),
        "desi_year3": desi_monitoring_report(),
    }


def monitoring_status_table() -> List[Dict]:
    """Return a compact status table across all monitor harnesses."""
    reports = collect_monitor_reports()
    return [
        {
            "experiment": "CMB-S4",
            "status": reports["cmbs4"]["current_ns_verdict"]["level"],
            "next_milestone": reports["cmbs4"]["next_milestone"]["expected_year"],
        },
        {
            "experiment": "DUNE",
            "status": reports["dune"]["current_verdict"]["level"],
            "next_milestone": reports["dune"]["next_milestone"]["first_physics"],
        },
        {
            "experiment": "Hyper-K/JUNO",
            "status": reports["hyperk_juno"]["current_verdict"]["level"],
            "next_milestone": min(
                reports["hyperk_juno"]["next_milestone"]["juno_first_data"],
                reports["hyperk_juno"]["next_milestone"]["hyperk_first_data"],
            ),
        },
        {
            "experiment": "DESI Year 3",
            "status": reports["desi_year3"]["falsification_verdict"]["level"],
            "next_milestone": reports["desi_year3"]["next_milestone"]["expected_year"],
        },
    ]


def hard_gate_snapshot() -> Dict:
    """Binary pass/fail snapshot for governance routing."""
    table = monitoring_status_table()
    failures = [row for row in table if row["status"] in ("TENSION", "EXCLUDED")]
    return {
        "pass": len(failures) == 0,
        "fail_count": len(failures),
        "failures": failures,
        "policy": "pass→freeze, fail→targeted ticket",
    }


def machine_readable_monitor_bundle() -> Dict:
    """Machine-readable bundle for external audit/reporting."""
    return {
        "schema_version": "1.0",
        "generated_on": date.today().isoformat(),
        "monitor_suite_version": "v10.18",
        "reports": collect_monitor_reports(),
        "status_table": monitoring_status_table(),
        "hard_gate": hard_gate_snapshot(),
    }
