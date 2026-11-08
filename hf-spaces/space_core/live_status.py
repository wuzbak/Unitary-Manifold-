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

    for source, read in (
        ("generator", lambda: _build_from_generator(repo_root)),
        ("local artifact", lambda: _read_json(repo_root / "9-INFRASTRUCTURE" / "um_live_status.json")),
        (DEFAULT_STATUS_URL, lambda: _read_url(DEFAULT_STATUS_URL)),
    ):
        payload = read()
        if payload is not None:
            return {**payload, "_status_source": source}

    return {"meta": {}, "tests": {}, "lean4": {}, "pillars": {},
            "_status_source": "unavailable"}


def status_snapshot() -> dict[str, int | str | None]:
    """Normalize counts without treating missing data as zero."""
    payload = load_live_status()
    meta = payload.get("meta", {})
    version = meta.get("version") or "unknown"
    version = str(version)
    if version != "unknown" and not version.startswith("v"):
        version = f"v{version}"

    def count(section: str, key: str) -> int | None:
        value = payload.get(section, {}).get(key)
        return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None

    return {
        "version": version,
        "date": meta.get("date") or "unknown",
        "source": payload.get("_status_source", "unknown"),
        "tests_passed": count("tests", "passed"),
        "tests_skipped": count("tests", "skipped"),
        "tests_deselected": count("tests", "deselected"),
        "tests_failed": count("tests", "failed"),
        "lean4_theorems": count("lean4", "theorem_count"),
        "hardgate_pillars": count("pillars", "hardgate_count"),
        "total_pillar_slots": count("pillars", "total_slots"),
        "next_pillar_slot": count("pillars", "next_slot"),
    }
