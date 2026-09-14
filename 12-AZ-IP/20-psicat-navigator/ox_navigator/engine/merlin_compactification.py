# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Governed compactification ingest helpers (sanitized, no bypass semantics)."""

from __future__ import annotations

from typing import Any

STRIP_KEY_MARKERS = (
    "track",
    "telemetry",
    "compliance",
    "license",
    "corp",
    "analytics",
)


def get_compactification_ingest_policy() -> dict[str, Any]:
    return {
        "mode": "sanitized_functional_ingest",
        "unchecked_bypass_forbidden": True,
        "central_governance_surfaces_required": True,
        "allowed_execution_paths": [
            "/api/agentInvoke",
            "/api/agentOrchestrate",
            "/api/psicat/local-execution/status",
            "/api/psicat/local-execution/run",
        ],
        "strip_key_markers": list(STRIP_KEY_MARKERS),
    }


def sanitize_legacy_payload(payload: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    stripped: list[str] = []
    for key, value in dict(payload or {}).items():
        lowered = str(key).lower()
        if any(marker in lowered for marker in STRIP_KEY_MARKERS):
            stripped.append(str(key))
            continue
        clean[str(key)] = value
    return {"clean_logic": clean, "stripped_keys": stripped}


def build_compactification_ingest_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = sanitize_legacy_payload(payload)
    clean_logic = dict(sanitized["clean_logic"])
    return {
        "ok": True,
        "policy": get_compactification_ingest_policy(),
        "input_key_count": len(dict(payload or {})),
        "retained_key_count": len(clean_logic),
        "stripped_key_count": len(list(sanitized["stripped_keys"])),
        "stripped_keys": list(sanitized["stripped_keys"]),
        "clean_logic": clean_logic,
        "honesty_note": (
            "This endpoint sanitizes and reports compactification payload structure only. "
            "It does not execute tools and does not bypass handshake/allowlist governance."
        ),
    }
