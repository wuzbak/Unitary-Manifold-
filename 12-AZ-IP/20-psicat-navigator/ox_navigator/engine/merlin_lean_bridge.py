# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Native Python↔Lean bridge receipts for Merlin/Product 20."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .lean4_index import get_theorem_count, search_theorems

REPO_ROOT = Path(__file__).resolve().parents[4]
LEAN4_ROOT = REPO_ROOT / "lean4"
LIVE_STATUS_PATH = REPO_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"

_EXTERNAL_BACKEND_SPECS: list[dict[str, Any]] = [
    {
        "backend_id": "leanclient_lsp",
        "module_candidates": ["leanclient"],
        "primary_mechanism": "lean_lsp_wrapper",
        "core_use_case": "fast batch processing and diagnostics",
    },
    {
        "backend_id": "leaninteract_repl",
        "module_candidates": ["LeanInteract", "lean_interact"],
        "primary_mechanism": "lean_repl_abstraction",
        "core_use_case": "direct Lean execution and temporary projects",
    },
    {
        "backend_id": "leandojo_dataset",
        "module_candidates": ["lean_dojo", "LeanDojo"],
        "primary_mechanism": "proof extraction and ML data collection",
        "core_use_case": "training and theorem-state dataset capture",
    },
    {
        "backend_id": "leancall_ffi",
        "module_candidates": ["leancall"],
        "primary_mechanism": "direct function binding",
        "core_use_case": "stable kernel invocation with narrow interfaces",
    },
]


def _safe_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def get_live_theorem_count_receipt() -> dict[str, Any]:
    payload = _safe_json(LIVE_STATUS_PATH)
    lean4 = dict(payload.get("lean4") or {})
    count = lean4.get("theorem_count")
    if isinstance(count, int) and count >= 0:
        return {
            "theorem_count": count,
            "source": "9-INFRASTRUCTURE/um_live_status.json",
            "count_scope": str(lean4.get("count_scope") or ""),
        }
    return {
        "theorem_count": get_theorem_count(),
        "source": "lean4_index_fallback",
        "count_scope": "local_fallback",
    }


def detect_lean_bridge_backends() -> dict[str, Any]:
    candidates = []
    for spec in _EXTERNAL_BACKEND_SPECS:
        module_name = next(
            (name for name in spec["module_candidates"] if importlib.util.find_spec(name) is not None),
            "",
        )
        candidates.append(
            {
                "backend_id": spec["backend_id"],
                "available": bool(module_name),
                "module_name": module_name,
                "primary_mechanism": spec["primary_mechanism"],
                "core_use_case": spec["core_use_case"],
            }
        )
    lean_binary = shutil.which("lean")
    lake_binary = shutil.which("lake")
    elan_binary = shutil.which("elan")
    return {
        "recommended_stack": "LSP_PLUS_REPL_HYBRID",
        "external_backends": candidates,
        "local_runtime": {
            "lean_binary": lean_binary or "",
            "lake_binary": lake_binary or "",
            "elan_binary": elan_binary or "",
            "lean_available": bool(lean_binary),
            "lake_available": bool(lake_binary),
            "elan_available": bool(elan_binary),
            "lean4_root_exists": LEAN4_ROOT.is_dir(),
        },
    }


def _formal_bridge_snapshot() -> tuple[dict[str, Any], dict[str, Any]]:
    from src.core.formal_traceability_spine import formal_traceability_spine
    from src.core.lean_python_bridge_ir import build_python_lean_bridge_contract

    snapshot = formal_traceability_spine()
    bridge_contract = build_python_lean_bridge_contract(
        rows=list(snapshot.get("traceability_rows") or []),
        primary_lanes=list(snapshot.get("primary_lanes") or []),
        runtime_alignment=dict(snapshot.get("runtime_alignment") or {}),
    )
    return snapshot, bridge_contract


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_]+", str(text or "").lower()) if token}


def _resolve_formal_unit(*, unit_id: str = "", text: str = "") -> dict[str, Any]:
    _, bridge_contract = _formal_bridge_snapshot()
    units = list(bridge_contract.get("formal_units") or [])
    if unit_id:
        for unit in units:
            if str(unit.get("unit_id") or "") == unit_id:
                return unit
        return {}
    tokens = _tokenize(text)
    best_unit: dict[str, Any] = {}
    best_score = 0
    for unit in units:
        score = 0
        haystacks = [
            str(unit.get("unit_id") or ""),
            str(unit.get("summary") or ""),
            str(unit.get("lane_title") or ""),
            str((unit.get("lean") or {}).get("module_name") or ""),
            " ".join(list((unit.get("lean") or {}).get("symbols") or [])),
        ]
        haystack_tokens = _tokenize(" ".join(haystacks))
        score += len(tokens & haystack_tokens)
        joined = " ".join(haystacks).lower()
        if "n_w" in text.lower() or "first principles" in text.lower():
            if "n_w" in joined or "nw" in haystack_tokens or "uniqueness" in joined:
                score += 3
        if "action" in text.lower() and "evolution" in text.lower() and "action_to_evolution" in str(unit.get("unit_id", "")).lower():
            score += 4
        if score > best_score:
            best_score = score
            best_unit = unit
    return dict(best_unit) if best_score > 0 else {}


def _run_scoped_build(*, check_target: str, timeout_seconds: int = 45) -> dict[str, Any]:
    if not check_target:
        return {
            "status": "SKIPPED",
            "ok": False,
            "reason": "missing_check_target",
            "invocation": [],
        }
    lean_file = (LEAN4_ROOT / check_target).resolve()
    try:
        command_target = str(lean_file.relative_to(LEAN4_ROOT))
    except ValueError:
        return {
            "status": "SKIPPED",
            "ok": False,
            "reason": "check_target_outside_lean4_root",
            "invocation": [],
        }
    if not lean_file.is_file():
        return {
            "status": "SKIPPED",
            "ok": False,
            "reason": "missing_lean_file",
            "invocation": [],
        }
    runtime = detect_lean_bridge_backends()["local_runtime"]
    lake_binary = str(runtime.get("lake_binary") or "")
    if not lake_binary:
        return {
            "status": "ENVIRONMENT_BLOCKED",
            "ok": False,
            "reason": "lake_not_available",
            "invocation": [],
        }
    command = [lake_binary, "env", "lean", command_target]
    try:
        completed = subprocess.run(
            command,
            cwd=LEAN4_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "TIMEOUT",
            "ok": False,
            "reason": "scoped_build_timeout",
            "invocation": command,
            "stdout_tail": (exc.stdout or "")[-400:],
            "stderr_tail": (exc.stderr or "")[-400:],
        }
    return {
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "ok": completed.returncode == 0,
        "reason": "scoped_build_completed",
        "returncode": completed.returncode,
        "invocation": command,
        "stdout_tail": (completed.stdout or "")[-400:],
        "stderr_tail": (completed.stderr or "")[-400:],
    }


def get_merlin_lean_bridge_artifact(limit: int | None = None) -> dict[str, Any]:
    snapshot, bridge_contract = _formal_bridge_snapshot()
    backend_state = detect_lean_bridge_backends()
    units = list(bridge_contract.get("formal_units") or [])
    resolved_limit = None if limit is None or int(limit) <= 0 else int(limit)
    if resolved_limit is not None:
        units = units[:resolved_limit]
    return {
        "artifact_id": "merlin_lean_bridge_artifact_v1",
        "strategy": str(bridge_contract.get("strategy") or "LSP_PLUS_REPL_HYBRID"),
        "theorem_count_receipt": get_live_theorem_count_receipt(),
        "backend_state": backend_state,
        "runtime_alignment": dict(snapshot.get("runtime_alignment") or {}),
        "formal_units": units,
        "bridge_contract": {
            "contract_id": str(bridge_contract.get("contract_id") or ""),
            "tiers": list(bridge_contract.get("tiers") or []),
            "governance": dict(bridge_contract.get("governance") or {}),
            "backend_comparison": list(bridge_contract.get("backend_comparison") or []),
        },
        "counts": {
            "formal_unit_count": len(units),
            "available_external_backend_count": sum(
                1 for item in list((backend_state.get("external_backends") or [])) if item.get("available")
            ),
        },
    }


def run_python_to_lean_bridge_receipt(
    *,
    conjecture: str,
    context: str = "",
    unit_id: str = "",
    run_build: bool = False,
) -> dict[str, Any]:
    merged_text = f"{conjecture}\n{context}".strip()
    unit = _resolve_formal_unit(unit_id=unit_id, text=merged_text)
    theorem_receipt = get_live_theorem_count_receipt()
    backend_state = detect_lean_bridge_backends()
    theorem_hits = search_theorems(merged_text)
    build_receipt = {
        "status": "SKIPPED",
        "ok": False,
        "reason": "build_not_requested",
        "invocation": [],
    }
    if run_build and unit:
        build_receipt = _run_scoped_build(
            check_target=str(((unit.get("lean") or {}).get("check_target") or ""))
        )
    return {
        "receipt_id": "python_lean_bridge_receipt_v1",
        "conjecture": str(conjecture or "").strip(),
        "context_excerpt": str(context or "").strip()[:240],
        "selected_unit_id": str(unit.get("unit_id") or ""),
        "selected_lane_id": str(unit.get("lane_id") or ""),
        "selected_unit_summary": str(unit.get("summary") or ""),
        "strategy": "LSP_PLUS_REPL_HYBRID",
        "theorem_hits": theorem_hits[:5],
        "theorem_count_receipt": theorem_receipt,
        "backend_state": backend_state,
        "formal_unit": unit,
        "scoped_build_receipt": build_receipt,
        "machine_to_machine_contract": {
            "python_emits": "formal_unit_ir",
            "lean_returns": "checked_receipt_or_blocker",
            "python_reingests": "structured_epistemic_result_only",
        },
        "promotion_allowed": False,
    }


__all__ = [
    "detect_lean_bridge_backends",
    "get_live_theorem_count_receipt",
    "get_merlin_lean_bridge_artifact",
    "run_python_to_lean_bridge_receipt",
]
