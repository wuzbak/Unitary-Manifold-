"""Canonical status loader for HF spaces."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import Any
from urllib.request import urlopen

DEFAULT_STATUS_URL = os.environ.get(
    "UM_LIVE_STATUS_URL",
    "https://raw.githubusercontent.com/wuzbak/Unitary-Manifold-/main/9-INFRASTRUCTURE/um_live_status.json",
)


def _is_valid(payload: Any) -> bool:
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("meta"), dict)
        and isinstance(payload.get("tests"), dict)
        and isinstance(payload.get("lean4"), dict)
        and isinstance(payload.get("pillars"), dict)
    )


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if _is_valid(payload):
                return payload
    except Exception:
        return None
    return None


def _build_from_generator(repo_root: Path) -> dict[str, Any] | None:
    script = repo_root / "9-INFRASTRUCTURE" / "generate_live_status.py"
    try:
        if not script.exists():
            return None
        spec = importlib.util.spec_from_file_location("generate_live_status", script)
        if not spec or not spec.loader:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        payload = module.build_live_status()
        return payload if _is_valid(payload) else None
    except Exception:
        return None


def _read_url(url: str, timeout: int = 5) -> dict[str, Any] | None:
    try:
        with urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload if _is_valid(payload) else None
    except Exception:
        return None


def load_live_status() -> dict[str, Any]:
    """Load canonical status from generator, then local artifact, then remote URL."""
    repo_root = Path(__file__).resolve().parents[2]

    payload = _build_from_generator(repo_root)
    if payload:
        return payload

    payload = _read_json(repo_root / "9-INFRASTRUCTURE" / "um_live_status.json")
    if payload:
        return payload

    payload = _read_url(DEFAULT_STATUS_URL)
    if payload:
        return payload

    return {
        "meta": {"version": "unknown", "date": "unknown"},
        "tests": {"passed": 0, "skipped": 0, "deselected": 0, "failed": 0},
        "lean4": {"theorem_count": 0},
        "pillars": {"hardgate_count": 208, "next_slot": 0, "total_slots": 0},
    }


def status_snapshot() -> dict[str, int | str]:
    """Normalized status values for UI surfaces."""
    payload = load_live_status()
    version = str(payload.get("meta", {}).get("version", "unknown"))
    if version != "unknown" and not version.startswith("v"):
        version = f"v{version}"
    return {
        "version": version,
        "date": str(payload.get("meta", {}).get("date", "unknown")),
        "tests_passed": int(payload.get("tests", {}).get("passed", 0) or 0),
        "tests_skipped": int(payload.get("tests", {}).get("skipped", 0) or 0),
        "tests_deselected": int(payload.get("tests", {}).get("deselected", 0) or 0),
        "tests_failed": int(payload.get("tests", {}).get("failed", 0) or 0),
        "lean4_theorems": int(payload.get("lean4", {}).get("theorem_count", 0) or 0),
        "hardgate_pillars": int(payload.get("pillars", {}).get("hardgate_count", 208) or 208),
        "next_pillar_slot": int(payload.get("pillars", {}).get("next_slot", 0) or 0),
    }

