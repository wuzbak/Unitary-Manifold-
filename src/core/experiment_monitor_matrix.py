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

from datetime import date, datetime
from typing import Dict, List

from src.core.cmbs4_monitor import monitoring_report as cmbs4_monitoring_report
from src.core.desi_year3_monitor import monitoring_report as desi_monitoring_report
from src.core.dune_dcp_monitor import monitoring_report as dune_monitoring_report
from src.core.hyperk_juno_monitor import monitoring_report as hyperk_juno_monitoring_report
from src.core.litebird_readiness_hardening import litebird_prepublication_packet

OVERDUE_THRESHOLD_DAYS: int = 30

__all__ = [
    "collect_monitor_reports",
    "monitoring_status_table",
    "high_priority_action_queue",
    "overdue_priority_actions",
    "uninitialized_priority_actions",
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


def _parse_iso_date(value: str) -> date | None:
    """Parse ISO datetime/date string and return date, else None."""
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


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
        {
            "experiment": "LiteBIRD",
            "status": "PENDING",
            "next_milestone": 2032,
        },
    ]


def high_priority_action_queue() -> List[Dict]:
    """Return high-priority action queue for current monitoring operations."""
    desi = desi_monitoring_report()
    litebird_policy = "same_day_recording_required"
    litebird_status = "READY_PACKET_AVAILABLE"
    litebird_note = ""
    try:
        litebird = litebird_prepublication_packet()
        litebird_policy = litebird.get("policy", litebird_policy)
    except Exception as exc:
        litebird_status = "READINESS_PACKET_ERROR"
        litebird_note = f"packet_generation_failed:{exc.__class__.__name__}:{exc}"
    return [
        {
            "id": "DESI_Y3_30_DAY_ROUTING",
            "priority": "CRITICAL",
            "trigger": "DESI Year 3 publication",
            "status": desi["routing"]["route"],
            "deadline_policy": "within_30_days_of_publication",
            "action": (
                "Run PASS/TENSION/FALSIFIED routing and sync kk_de_wa_cpl.py, "
                "OBSERVATION_TRACKER.md, and canonical falsifier feed."
            ),
            "note": "",
        },
        {
            "id": "LITEBIRD_PRIMARY_FALSIFIER_READY",
            "priority": "CRITICAL",
            "trigger": "LiteBIRD β publication",
            "status": litebird_status,
            "deadline_policy": litebird_policy,
            "action": "Execute falsification_check.py immediately and record same-day verdict.",
            "note": litebird_note,
        },
        {
            "id": "CMBS4_MONITOR_SYNC",
            "priority": "HIGH",
            "trigger": "new CMB-S4 release",
            "status": "ACTIVE_MONITORING",
            "deadline_policy": "update_on_release",
            "action": "Update monitor registry and canonical feed for n_s, r, and A_s state.",
            "note": "",
        },
        {
            "id": "ACT_DR6_MONITOR_SYNC",
            "priority": "HIGH",
            "trigger": "ACT DR6 full-release update",
            "status": "ACTIVE_MONITORING",
            "deadline_policy": "update_on_release",
            "action": "Re-evaluate n_s consistency status and sync tracker/falsifier feed.",
            "note": "",
        },
        {
            "id": "SIMONS_OBSERVATORY_BETA_MONITOR",
            "priority": "HIGH",
            "trigger": "Simons Observatory β update",
            "status": "ACTIVE_MONITORING",
            "deadline_policy": "update_on_release",
            "action": "Update birefringence pre-discrimination status and sync tracker/falsifier feed.",
            "note": "",
        },
    ]


def overdue_priority_actions(
    last_updated: Dict[str, str] | None = None,
    today: str | None = None,
) -> List[Dict]:
    """Return overdue actions from timestamp history.

    Parameters
    ----------
    last_updated : dict[str, str]
        Mapping from action IDs to last-update timestamps in ISO format (YYYY-MM-DD).
    today : str | None
        Optional ISO date string (YYYY-MM-DD). If not provided, uses current UTC date.
    """
    freshness_source = {} if last_updated is None else last_updated
    reference_day = date.today() if today is None else (_parse_iso_date(today) or date.today())
    overdue: List[Dict] = []
    for action in high_priority_action_queue():
        action_id = action["id"]
        stamp = freshness_source.get(action_id)
        if not stamp:
            continue
        updated_day = _parse_iso_date(stamp)
        if updated_day is None:
            overdue.append(
                {
                    "id": action_id,
                    "age_days": None,
                    "priority": action["priority"],
                    "reason": "invalid_timestamp_format",
                }
            )
            continue
        age_days = (reference_day - updated_day).days
        if age_days > OVERDUE_THRESHOLD_DAYS:
            overdue.append(
                {
                    "id": action_id,
                    "age_days": age_days,
                    "priority": action["priority"],
                    "reason": "stale_update_window_exceeded",
                }
            )
    return overdue


def uninitialized_priority_actions(last_updated: Dict[str, str] | None = None) -> List[str]:
    """Return action IDs that have no timestamp entry in `last_updated`."""
    known_ids = set((last_updated or {}).keys())
    return [action["id"] for action in high_priority_action_queue() if action["id"] not in known_ids]


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


def machine_readable_monitor_bundle(
    last_updated: Dict[str, str] | None = None,
    today: str | None = None,
) -> Dict:
    """Machine-readable bundle for external audit/reporting."""
    freshness_source = {} if last_updated is None else last_updated
    return {
        "schema_version": "1.0",
        "generated_on": date.today().isoformat(),
        "monitor_suite_version": "v10.18",
        "reports": collect_monitor_reports(),
        "status_table": monitoring_status_table(),
        "high_priority_queue": high_priority_action_queue(),
        "overdue_actions": overdue_priority_actions(last_updated=freshness_source, today=today),
        "uninitialized_actions": uninitialized_priority_actions(last_updated=freshness_source),
        "hard_gate": hard_gate_snapshot(),
    }
