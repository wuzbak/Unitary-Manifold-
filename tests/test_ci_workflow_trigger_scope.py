# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    content = (WORKFLOWS / name).read_text(encoding="utf-8")
    return yaml.load(content, Loader=yaml.BaseLoader)


def _extract_branches(workflow_name: str, event_name: str) -> list[str]:
    workflow = _load(workflow_name)
    return list((workflow.get("on", {}).get(event_name, {}) or {}).get("branches", []))


def test_hosted_ci_workflows_run_pushes_only_on_main() -> None:
    for workflow_name in [
        "ci.yml",
        "tests.yml",
        "status-drift-gate.yml",
        "lean4-check.yml",
        "codeql-language-matrix.yml",
    ]:
        assert _extract_branches(workflow_name, "push") == ["main"]
        assert _extract_branches(workflow_name, "pull_request") == ["**"]


def test_psicat_performance_gate_limits_pushes_to_main() -> None:
    assert _extract_branches("psicat-performance-gate.yml", "push") == ["main"]
    assert _extract_branches("psicat-performance-gate.yml", "pull_request") == ["**"]
