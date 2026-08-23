# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_base44_live_status.py — Base44 live-status integration tests

Covers:
  - 9-INFRASTRUCTURE/generate_live_status.py parsing and validation
  - 9-INFRASTRUCTURE/um_live_status.json generated artifact
  - bot/assistant_api.py /api/status canonical + compatibility response

0 test failures required.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi", reason="fastapi not installed")
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).parent.parent
STATUS_PATH = REPO_ROOT / "STATUS.md"
LIVE_STATUS_PATH = REPO_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def live_status_module():
    return _load_module(
        "generate_live_status_test",
        REPO_ROOT / "9-INFRASTRUCTURE" / "generate_live_status.py",
    )


@pytest.fixture(scope="module")
def assistant_api_module():
    return _load_module(
        "assistant_api_base44_test",
        REPO_ROOT / "bot" / "assistant_api.py",
    )


def _first_sprint_entry() -> str:
    text = STATUS_PATH.read_text(encoding="utf-8")
    sprint_start = text.find("*v")
    assert sprint_start >= 0
    return text[sprint_start:].split("\n\n", 1)[0].strip()


def test_build_live_status_matches_headline_entry(live_status_module):
    entry = _first_sprint_entry()
    version_match = re.search(r"\*v([\d.]+) Sprint (\w+)", entry)
    expected_lean4 = int(re.findall(r"Lean4[^)]*?(?:total\s+|→)(\d{3,5})", entry)[-1])
    expected_tests = re.search(
        r"~?([\d,]+)\s+passed\s*[·•]\s*(\d+)\s+skipped\s*[·•]\s*(\d+)\s+deselected\s*[·•]\s*(\d+)\s+failed",
        entry,
    )
    expected_next_slot = int(re.search(r"next slot (\d+)", entry).group(1))

    data = live_status_module.build_live_status()

    assert data["meta"]["version"] == version_match.group(1)
    assert data["meta"]["sprint"] == version_match.group(2)
    assert data["tests"]["passed"] == int(expected_tests.group(1).replace(",", ""))
    assert data["tests"]["skipped"] == int(expected_tests.group(2))
    assert data["tests"]["deselected"] == int(expected_tests.group(3))
    assert data["tests"]["failed"] == int(expected_tests.group(4))
    assert data["lean4"]["theorem_count"] == expected_lean4
    assert data["pillars"]["next_slot"] == expected_next_slot


def test_live_status_validation_passes(live_status_module):
    data = live_status_module.build_live_status()
    assert live_status_module.validate(data) == []


def test_generated_live_status_file_is_current(live_status_module):
    assert LIVE_STATUS_PATH.exists(), "um_live_status.json not found — run 9-INFRASTRUCTURE/generate_live_status.py"
    repo_json = json.loads(LIVE_STATUS_PATH.read_text(encoding="utf-8"))
    assert repo_json == live_status_module.build_live_status()


def test_generated_live_status_has_no_keys():
    text = LIVE_STATUS_PATH.read_text(encoding="utf-8")
    assert re.search(r"\bsk-[A-Za-z0-9]{20,}", text) is None
    assert "OPENROUTER_API_KEY" not in text
    assert "HF_API_TOKEN" not in text


def test_assistant_api_status_uses_live_status(assistant_api_module, live_status_module):
    client = TestClient(assistant_api_module.app)
    response = client.get("/api/status")
    assert response.status_code == 200

    payload = response.json()
    live_status = live_status_module.build_live_status()

    assert payload["meta"]["version"] == live_status["meta"]["version"]
    assert payload["tests"]["passed"] == live_status["tests"]["passed"]
    assert payload["lean4"]["theorem_count"] == live_status["lean4"]["theorem_count"]
    assert payload["pillars"]["next_slot"] == live_status["pillars"]["next_slot"]
    assert payload["tests_passed"] == live_status["tests"]["passed"]
    assert payload["tests_skipped"] == live_status["tests"]["skipped"]
    assert payload["tests_deselected"] == live_status["tests"]["deselected"]
    assert payload["tests_failed"] == live_status["tests"]["failed"]
    assert payload["lean4_theorems"] == live_status["lean4"]["theorem_count"]
    assert payload["pillars_hardgate"] == live_status["pillars"]["hardgate_count"]
    assert payload["pillars_total"] == live_status["pillars"]["total_slots"]
    assert payload["next_pillar_slot"] == live_status["pillars"]["next_slot"]
    assert payload["status_source"]
