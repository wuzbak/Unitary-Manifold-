# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest
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


def test_coverage_retains_failure_evidence_without_weakening_the_gate() -> None:
    jobs = _load("tests.yml")["jobs"]
    coverage_job = jobs["coverage-gate"]
    steps = {step.get("name"): step for step in coverage_job["steps"]}
    run = steps["Run coverage regression gate"]["run"]
    assert 'tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/"' in run
    assert "--ignore" not in run
    assert "--signal=TERM --kill-after=60s 160m" in run
    assert "-n 2 --dist loadfile" in run
    assert "pytest-xdist" in steps["Install dependencies"]["run"]
    integration = steps["Run serial non-slow coverage integration"]["run"]
    assert "--signal=TERM --kill-after=60s 10m" in integration
    assert "--cov-append" in integration
    assert "--cov-fail-under=85" in integration
    assert "-m 'not slow'" in integration
    assert "-n " not in integration
    assert "--dist" not in integration
    assert "set -o pipefail" in integration
    slow_runs = [
        step["run"]
        for step in jobs["test-slow"]["steps"]
        if "run" in step
    ]
    assert any("tests/ -m slow" in run for run in slow_runs)
    from src.core.regression_supervision_plan import INTEGRATION_PREFLIGHT_FILES

    for path in INTEGRATION_PREFLIGHT_FILES:
        assert path in integration
    assert coverage_job["timeout-minutes"] > 172
    assert "set -o pipefail" in run
    assert "tee coverage.log" in run
    partial = steps["Retain partial coverage evidence after failure"]
    assert partial["if"] == "always()"
    assert "coverage combine --keep" in partial["run"]
    assert "--fail-under=85" in partial["run"]
    upload = steps["Upload coverage report"]
    assert upload["if"] == "always()"
    assert upload["with"]["include-hidden-files"] is True
    for path in (
        "coverage.xml", ".coverage*", "coverage-tests.xml", "coverage.log",
        "coverage-integration.xml", "coverage-integration.log",
    ):
        assert path in upload["with"]["path"].splitlines()
    assert jobs["full-regression-gate"]["if"] == "always()"
    assert "continue-on-error" not in coverage_job
    assert all("continue-on-error" not in step for step in coverage_job["steps"])


def test_fast_supervisor_remains_fail_closed_after_failed_or_missing_receipts() -> None:
    jobs = _load("tests.yml")["jobs"]
    supervisor = jobs["test-fast-supervisor"]
    assert supervisor["if"] == "always()"
    assert supervisor["needs"] == "test-fast-batched"
    steps = {step.get("name"): step for step in supervisor["steps"]}
    for name in (
        "Download fast-suite execution evidence",
        "Require complete matching fast-suite execution receipts",
        "Require successful fast-suite jobs",
    ):
        assert steps[name]["if"] == "always()"
    assert "--aggregate" in steps["Require complete matching fast-suite execution receipts"]["run"]
    assert 'test "${BATCH_RESULT}" = "success"' in steps["Require successful fast-suite jobs"]["run"]
    assert "test-fast-supervisor" in jobs["full-regression-gate"]["needs"]


def test_main_regression_uses_frozen_cost_plan_and_serial_integration_slice() -> None:
    jobs = _load("ci.yml")["jobs"]
    batch = jobs["push-full-regression-batched"]
    assert batch["strategy"]["matrix"]["batch-index"] == list(range(13))
    assert batch["strategy"]["fail-fast"] is False
    steps = {step.get("name"): step for step in batch["steps"]}
    freeze = steps["Freeze dependency-cost regression plan"]["run"]
    run = steps["Run full regression slice"]["run"]
    assert "--batch-count 12 --workers 2 --write-plan" in freeze
    assert "--plan-file" in freeze and "--plan-file" in run
    assert "plan-${{ matrix.batch-index }}.json" in freeze
    assert "plan-${{ matrix.batch-index }}.json" in run
    assert "--timeout 5100" in run
    assert batch["timeout-minutes"] * 60 > 5100 + 600
    fast_batch = _load("tests.yml")["jobs"]["test-fast-batched"]
    assert fast_batch["timeout-minutes"] * 60 > 5100 + 600
    installation = steps["Install dependencies"]["run"]
    supervisor = jobs["push-full-regression-supervisor"]
    assert supervisor["if"].startswith("always()")
    steps = {step.get("name"): step for step in supervisor["steps"]}
    assert steps["Install matching regression dependencies"]["run"] == installation
    aggregate = steps["Require complete matching execution receipts"]
    assert aggregate["if"] == "always()"
    assert "--plan-file" in aggregate["run"] and "plan-0.json" in aggregate["run"]
    assert "--batch-count 12 --aggregate" in aggregate["run"]


@pytest.mark.parametrize(
    ("required", "result", "expected"),
    [("true", "success", 0), ("true", "skipped", 1), ("true", "failure", 1),
     ("true", "cancelled", 1), ("false", "skipped", 0), ("false", "failure", 1)],
)
def test_ci_gate_requires_main_execution_but_allows_pr_only_skips(
    tmp_path: Path, required: str, result: str, expected: int
) -> None:
    gate = _load("ci.yml")["jobs"]["ci-gate"]
    assert gate["if"] == "always()"
    step = gate["steps"][0]
    assert "github.event_name == 'push'" in step["env"]["REQUIRE_FULL_REGRESSION"]
    env = {
        **os.environ,
        "PLATFORM_SMOKE_RESULT": "success",
        "SUITE_COLLECTION_SMOKE_RESULT": "success",
        "PUSH_FULL_REGRESSION_BATCHED_RESULT": result,
        "PUSH_FULL_REGRESSION_RESULT": result,
        "REQUIRE_FULL_REGRESSION": required,
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
    }
    completed = subprocess.run(["bash", "-c", step["run"]], env=env, capture_output=True)
    assert completed.returncode == expected
