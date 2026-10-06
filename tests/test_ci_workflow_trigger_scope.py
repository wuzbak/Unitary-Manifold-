# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    content = (WORKFLOWS / name).read_text(encoding="utf-8")
    return yaml.safe_load(content)


def _extract_branches(workflow_name: str, event_name: str) -> list[str]:
    workflow = _load(workflow_name)
    on_block = workflow.get("on") or workflow.get(True) or {}
    return list((on_block.get(event_name, {}) or {}).get("branches", []))


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


def test_tests_workflow_restores_required_coverage_gate() -> None:
    workflow = _load("tests.yml")
    jobs = workflow["jobs"]

    coverage_job = jobs["coverage-gate"]
    coverage_step = next(
        step for step in coverage_job["steps"] if step.get("name") == "Run coverage regression gate"
    )

    assert "--cov=src" in coverage_step["run"]
    assert "--cov-fail-under=85" in coverage_step["run"]
    assert "coverage-gate" in jobs["full-regression-gate"]["needs"]


def test_full_core_evidence_runs_outside_the_agent_session() -> None:
    workflow = _load("um-arts-full-core.yml")
    job = workflow["jobs"]["full-core"]
    assert _extract_branches("um-arts-full-core.yml", "push") == ["main", "copilot/um-arts-*"]
    assert _extract_branches("um-arts-full-core.yml", "pull_request") == ["**"]
    assert workflow["concurrency"]["cancel-in-progress"] is False
    assert job["steps"][0]["with"]["fetch-depth"] == 0
    assert job["timeout-minutes"] == 330
    execution = next(step for step in job["steps"] if "Collect, execute" in step.get("name", ""))
    assert execution["timeout-minutes"] < job["timeout-minutes"]
    assert 'verified["status"] != "passed"' in execution["run"]
    assert 'verified["selected"] != verified["reconciled"]' in execution["run"]
    upload = job["steps"][-1]
    assert upload["if"] == "always()"
    assert upload["with"]["include-hidden-files"] is True
    assert upload["with"]["retention-days"] == 90


def test_full_core_config_covers_slow_tests_and_independent_suites() -> None:
    from TOOLS.um_arts.adapters import load_config

    config = load_config(
        REPO_ROOT, REPO_ROOT / "12-AZ-IP/26-um-arts/um_arts/examples/full-core-ci.json")
    assert config["pytest_args"] == ["-m", ""]
    assert config["files_per_job"] == 32
    assert config["collection_timeout_seconds"] == 900
    assert {path for suite in config["suites"] for path in suite["paths"]} == {
        "tests", "recycling", "5-GOVERNANCE/Unitary Pentad"}
    assert all(not suite["requires"] for suite in config["suites"])
    assert config["plugins"] == ["pytest_asyncio.plugin", "pytest_benchmark.plugin"]


def test_full_python_codeql_is_not_changed_surface_only() -> None:
    job = _load("codeql-language-matrix.yml")["jobs"]["python-full"]
    assert "needs" not in job and "if" not in job
    assert job["permissions"]["security-events"] == "write"
    init = next(step for step in job["steps"] if "Initialize" in step.get("name", ""))
    assert init["with"]["languages"] == "python"
    config = yaml.safe_load(init["with"]["config"])
    assert "paths" not in config
    assert config["paths-ignore"] == [".github/agents"]
    analyze = next(step for step in job["steps"] if "Analyze full" in step.get("name", ""))
    assert analyze["with"]["category"] == "/language:python/repository-wide"
    assert job["steps"][-1]["if"] == "always()"


def test_lean_cache_failures_are_captured_after_independent_checks() -> None:
    steps = _load("lean4-check.yml")["jobs"]["lean4-build"]["steps"]
    names = [step.get("name") for step in steps]
    cache = steps[names.index("Download Mathlib cache")]
    assert "|| true" not in cache["run"]
    assert "TOOLS.um_arts capture" in cache["run"]
    assert "--timeout 600" in cache["run"]
    assert names.index("Verify exporter with the pinned Lean toolchain") < names.index("Download Mathlib cache")
    assert names.index("Verify NumericalChecks compile") < names.index("Download Mathlib cache")
    assert names.index("Download Mathlib cache") < names.index("Lake build")
