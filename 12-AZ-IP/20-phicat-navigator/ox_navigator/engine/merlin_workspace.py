# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Governed internal workspace contract for Merlin orchestration."""

from __future__ import annotations

from typing import Any


def get_workspace_policy() -> dict[str, Any]:
    return {
        "name": "Merlin Back Room",
        "purpose": "Governed planning/scratchpad/execution staging surface.",
        "allowed_capabilities": [
            "scratchpad_planning",
            "bounded_tool_orchestration",
            "interface_profile_selection",
            "deterministic_replay_pack_generation",
        ],
        "disallowed_capabilities": [
            "unauthorized_backdoor_execution",
            "secret_exfiltration",
            "policy_bypass",
            "unbounded_autonomous_write_execute",
        ],
        "controls": [
            "typed_tool_schemas",
            "risk_labels",
            "audit_logs",
            "human_gate_for_high_risk_actions",
        ],
    }


def get_workspace_state() -> dict[str, Any]:
    return {
        "workspace_enabled": True,
        "profile": "balanced",
        "audit_log_mode": "required",
        "adaptive_interface_controls": {
            "allowed": True,
            "bounded_by_policy": True,
        },
        "status": "schema_and_policy_ready",
    }
