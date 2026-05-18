# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 261 — Foundational Boundary Hardening (adjacent research track).

Executable blocker/no-go registry for the remaining foundational hardgate
boundaries. This module sharpens the boundary conditions honestly; it does not
promote any incomplete hardgate to CLOSED.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from src.core.canonical_ledger_consistency import ROOT, canonical_status_token_report
from src.core.closure_hardgate_registry import REGISTRY_PATH, load_hardgate_registry, workstream_partition

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "foundational_boundary_rows",
    "boundary_no_go_statement",
    "pillar261_foundational_boundary_report",
]

ADJACENCY_TRACK_LABEL = "NON_HARDGATE_ADJACENT"


def foundational_boundary_rows() -> List[Dict[str, object]]:
    registry = load_hardgate_registry()
    rows: List[Dict[str, object]] = []
    for gate in registry.get("gates", []):
        artifacts = [str(p) for p in gate.get("required_artifacts", [])]
        tests = [str(p) for p in gate.get("required_tests", [])]
        artifact_presence = {p: (ROOT / p).exists() for p in artifacts}
        test_presence = {p: (ROOT / p).exists() for p in tests}
        rows.append(
            {
                "gate": str(gate["key"]),
                "declared_status": str(gate.get("status", "")),
                "workstream": str(gate.get("workstream", "")),
                "artifact_presence": artifact_presence,
                "test_presence": test_presence,
                "artifacts_present": all(artifact_presence.values()),
                "tests_present": all(test_presence.values()),
                "promotion_rule": str(gate.get("promotion_rule", "")),
                "falsifier": str(gate.get("falsifier", "")),
                "forbidden_labels": list(gate.get("forbid_if_incomplete", [])),
            }
        )
    return rows


def boundary_no_go_statement(gate_key: str) -> str:
    rows = {row["gate"]: row for row in foundational_boundary_rows()}
    if gate_key not in rows:
        raise ValueError(f"Unknown gate_key: {gate_key}")
    row = rows[gate_key]
    missing_artifacts = [p for p, present in row["artifact_presence"].items() if not present]
    missing_tests = [p for p, present in row["test_presence"].items() if not present]
    blockers = []
    if missing_artifacts:
        blockers.append(f"missing artifacts: {', '.join(missing_artifacts)}")
    if missing_tests:
        blockers.append(f"missing tests: {', '.join(missing_tests)}")
    if not blockers:
        blockers.append("promotion evidence absent: registry still declares the gate open")
    return (
        f"NO_GO::{gate_key} — {row['promotion_rule']} "
        f"Current blockers: {'; '.join(blockers)}."
    )


def pillar261_foundational_boundary_report() -> Dict[str, object]:
    rows = foundational_boundary_rows()
    token_sync = canonical_status_token_report()
    partition = workstream_partition()
    no_go = {row["gate"]: boundary_no_go_statement(str(row["gate"])) for row in rows}
    open_gates = [row["gate"] for row in rows if row["declared_status"] != "COMPLETE"]

    return {
        "pillar": 261,
        "title": "Foundational Boundary Hardening",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "registry_path": str(REGISTRY_PATH),
        "workstream_partition": partition,
        "token_sync": token_sync,
        "rows": rows,
        "open_gates": open_gates,
        "no_go_statements": no_go,
        "status": "OPEN_BOUNDARIES_HARDENED" if token_sync["all_pass"] else "TOKEN_SYNC_TENSION",
        "separation_guard": True,
    }
