# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_hosted_ci_workflows_run_pushes_only_on_main() -> None:
    for workflow_name in [
        "ci.yml",
        "tests.yml",
        "status-drift-gate.yml",
        "lean4-check.yml",
        "codeql-language-matrix.yml",
    ]:
        content = _read(workflow_name)
        assert 'branches: ["main"]' in content or "- main" in content
        assert '"**"' in content or "- '**'" in content


def test_psicat_performance_gate_limits_pushes_to_main() -> None:
    content = _read("psicat-performance-gate.yml")
    assert 'branches: ["main"]' in content
    assert 'pull_request:' in content
