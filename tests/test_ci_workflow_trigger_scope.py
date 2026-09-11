# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _read(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def _extract_branches(content: str, event_name: str) -> list[str]:
    lines = content.splitlines()
    event_indent = None
    branches_indent = None
    collecting = False
    branches: list[str] = []

    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))

        if event_indent is None:
            if line.startswith(f"  {event_name}:"):
                event_indent = indent
            continue

        if indent <= event_indent and stripped:
            break

        if branches_indent is None:
            if stripped.startswith("branches:"):
                branches_indent = indent
                remainder = stripped.removeprefix("branches:").strip()
                if remainder.startswith("[") and remainder.endswith("]"):
                    items = remainder[1:-1].split(",")
                    return [item.strip().strip("'\"") for item in items if item.strip()]
            continue

        if indent <= branches_indent and stripped:
            break

        if stripped.startswith("- "):
            collecting = True
            branches.append(stripped[2:].strip().strip("'\""))
        elif collecting and stripped:
            break

    return branches


def test_hosted_ci_workflows_run_pushes_only_on_main() -> None:
    for workflow_name in [
        "ci.yml",
        "tests.yml",
        "status-drift-gate.yml",
        "lean4-check.yml",
        "codeql-language-matrix.yml",
    ]:
        content = _read(workflow_name)
        assert _extract_branches(content, "push") == ["main"]
        assert _extract_branches(content, "pull_request") == ["**"]


def test_psicat_performance_gate_limits_pushes_to_main() -> None:
    content = _read("psicat-performance-gate.yml")
    assert _extract_branches(content, "push") == ["main"]
    assert _extract_branches(content, "pull_request") == ["**"]
