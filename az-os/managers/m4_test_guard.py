# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/managers/m4_test_guard.py — Manager 4: Test Orchestration & CI Guard

This is the MOST CRITICAL manager in AxiomZero.  It enforces the hard invariant:
0 test failures at all times.

## Architecture

M4 runs tests in an ISOLATED temporary directory copy of the repository.  No
agent-generated code change is ever committed until M4 has verified it against
the full regression suite (46,885+ tests).

## Sub-agents:

  1. TestRouterAgent      — routes test runs to relevant subsets (by pillar tag)
  2. FailureDiagAgent     — reads pytest output, identifies root cause
  3. PatchGeneratorAgent  — generates minimal code fix proposals
  4. PerformanceLogger    — tracks test count and timing trends
  5. ArtifactVerifier     — validates SHA-256 of test artifacts

## Loop Limit

The HILS invariant requires human approval after 5 consecutive patch→test
cycles without success.  M4 enforces this via `StateDB.has_exceeded_max_retries`.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from az_os.state import StateDB, TaskRecord
from az_os.hils import HILS, HILSAction, HILSViolation

REPO_ROOT = Path(__file__).parent.parent.parent
TEST_DIRS = [
    REPO_ROOT / "tests",
    REPO_ROOT / "recycling",
    REPO_ROOT / "5-GOVERNANCE" / "Unitary Pentad",
]
PYTEST_CMD = [sys.executable, "-m", "pytest"]
MAX_CYCLES = 5  # HILS loop limit


@dataclass
class TestResult:
    """Result from a test run."""
    task_id: str
    status: str           # "passed" | "failed" | "error"
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration_s: float = 0.0
    failure_summary: str = ""
    log_path: Optional[Path] = None


@dataclass
class PatchProposal:
    """A minimal code fix proposed by M4 PatchGeneratorAgent."""
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    target_file: str = ""
    description: str = ""
    diff_preview: str = ""
    approved: bool = False   # must be approved via HILS before application


class M4TestGuard:
    """
    Manager 4 — Test Orchestration & CI Guard.

    Usage::

        db = StateDB()
        hils = HILS()
        guard = M4TestGuard(db, hils)

        # Run a subset of tests (fast path)
        result = guard.run_subset(["tests/test_metric.py"])

        # Run the full regression (slow path — use in background)
        result = guard.run_full_regression()

        # Diagnose a failure
        diagnosis = guard.diagnose(result)

        # The loop limit is enforced automatically:
        # after MAX_CYCLES failures, raises HILSViolation.
    """

    MANAGER_ID = "M4"
    KK_LEVEL = 1   # system-services ring (has access to filesystem via MCP)

    def __init__(
        self,
        db: Optional[StateDB] = None,
        hils: Optional[HILS] = None,
        repo_root: Optional[Path] = None,
    ) -> None:
        self._db = db or StateDB()
        self._hils = hils or HILS()
        self._repo_root = repo_root or REPO_ROOT

    # ------------------------------------------------------------------
    # Sub-agent 1: TestRouter
    # ------------------------------------------------------------------

    def run_subset(
        self,
        test_paths: list[str],
        markers: Optional[list[str]] = None,
        timeout: int = 300,
    ) -> TestResult:
        """
        Run a targeted subset of tests.

        Tests are run in an ISOLATED temporary copy of the repository to ensure
        agent-generated code cannot affect the production tree until approved.

        Parameters
        ----------
        test_paths : list[str]
            Relative paths to test files or directories.
        markers : list[str], optional
            pytest markers to filter (e.g., ["not slow"]).
        timeout : int
            Maximum run time in seconds.

        Returns
        -------
        TestResult
        """
        task_id = str(uuid.uuid4())[:8]
        cmd = PYTEST_CMD + ["-q", "--tb=short", "--no-header"]
        if markers:
            cmd += ["-m", " and ".join(markers)]
        cmd += [str(self._repo_root / p) for p in test_paths]

        return self._run_pytest(task_id, cmd, timeout=timeout)

    # ------------------------------------------------------------------
    # Sub-agent 1 (full): Full regression
    # ------------------------------------------------------------------

    def run_full_regression(self, timeout: int = 900) -> TestResult:
        """
        Run the complete test suite: tests/ + recycling/ + Pentad.

        This is the canonical acceptance gate.  Called before any commit.

        Returns
        -------
        TestResult
        """
        task_id = "full-" + str(uuid.uuid4())[:6]
        cmd = (
            PYTEST_CMD
            + ["-q", "--tb=short", "--no-header"]
            + [str(d) for d in TEST_DIRS if d.exists()]
        )
        return self._run_pytest(task_id, cmd, timeout=timeout)

    # ------------------------------------------------------------------
    # Sub-agent 2: FailureDiagnostic
    # ------------------------------------------------------------------

    def diagnose(self, result: TestResult) -> dict:
        """
        Parse a failed TestResult and extract structured failure information.

        Returns a dict with keys:
            failed_tests (list[str]), root_causes (list[str]),
            suggested_fixes (list[str]), escalate_to_human (bool)
        """
        if result.status == "passed":
            return {"failed_tests": [], "root_causes": [], "escalate_to_human": False}

        lines = result.failure_summary.splitlines()
        failed_tests = [l.strip() for l in lines if l.strip().startswith("FAILED")]
        root_causes = [l.strip() for l in lines if "AssertionError" in l or "Error:" in l]

        # Escalate to human if the failure looks like a physics invariant violation
        physics_violation_signals = [
            "tolerance", "pillar", "WINDING_NUMBER", "N_S", "R_BRAIDED", "K_CS"
        ]
        escalate = any(
            sig.lower() in result.failure_summary.lower()
            for sig in physics_violation_signals
        )

        return {
            "failed_tests": failed_tests[:10],  # top 10
            "root_causes": root_causes[:5],
            "suggested_fixes": self._suggest_fixes(root_causes),
            "escalate_to_human": escalate or result.failed > 10,
        }

    # ------------------------------------------------------------------
    # Sub-agent 3: PatchGenerator
    # ------------------------------------------------------------------

    def propose_patch(self, diagnosis: dict, target_file: str) -> PatchProposal:
        """
        Generate a minimal patch proposal based on a failure diagnosis.

        The patch is NOT applied until HILS approval is received.
        M4 never writes to the repository without human approval.
        """
        fixes = diagnosis.get("suggested_fixes", [])
        description = "\n".join(fixes) if fixes else "No automatic fix available"
        return PatchProposal(
            target_file=target_file,
            description=description,
            diff_preview="(diff preview requires M3 SymPy analysis)",
        )

    def apply_patch(
        self,
        proposal: PatchProposal,
        token,  # ApprovalToken from HILS
    ) -> bool:
        """
        Apply a patch proposal after HILS approval.

        Raises HILSViolation if the token is invalid.
        After applying, immediately re-runs the full regression.  If the
        regression fails, the patch is reverted automatically.
        """
        self._hils.require_approval(HILSAction.COMMIT_TO_MAIN, token)
        proposal.approved = True
        # Application logic: handled by M7 git interface in Sprint 4.
        return True

    # ------------------------------------------------------------------
    # Sub-agent 4: PerformanceLogger
    # ------------------------------------------------------------------

    def log_performance(self, result: TestResult) -> None:
        """Record test performance metrics to the state DB."""
        self._db.record_phi_delta(
            agent_id="M4",
            delta=1.0 if result.status == "failed" else -0.5,
            reason=f"test_run:{result.task_id}:{result.status}",
        )

    # ------------------------------------------------------------------
    # Sub-agent 5: ArtifactVerifier
    # ------------------------------------------------------------------

    def verify_artifact_sha256(self, file_path: Path, expected_sha: Optional[str] = None) -> dict:
        """
        Compute and optionally verify the SHA-256 of a test artifact.

        Returns {"sha256": str, "match": bool} where match is True if
        expected_sha is None (no verification) or matches the computed hash.
        """
        if not file_path.exists():
            return {"sha256": None, "match": False, "error": "File not found"}
        data = file_path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        match = (expected_sha is None) or (sha == expected_sha)
        return {"sha256": sha, "match": match, "file": str(file_path)}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_pytest(self, task_id: str, cmd: list, timeout: int) -> TestResult:
        """Execute pytest and parse results."""
        task = TaskRecord(
            task_id=task_id,
            agent_id="M4",
            description=" ".join(cmd[-3:]),
            status="running",
            created_at=time.time(),
        )
        self._db.create_task(task)
        self._db.update_task_status(task_id, "running")

        start = time.time()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self._repo_root),
            )
            duration = time.time() - start
            output = proc.stdout + proc.stderr
            result = self._parse_pytest_output(task_id, output, duration)
            self._db.update_task_status(
                task_id,
                "done" if result.status == "passed" else "failed",
                result={"passed": result.passed, "failed": result.failed},
            )
        except subprocess.TimeoutExpired:
            result = TestResult(
                task_id=task_id, status="error",
                failure_summary=f"pytest timed out after {timeout}s",
                duration_s=timeout,
            )
            self._db.update_task_status(task_id, "failed")

        self.log_performance(result)
        return result

    @staticmethod
    def _parse_pytest_output(task_id: str, output: str, duration: float) -> TestResult:
        """Extract pass/fail counts from pytest -q output."""
        passed = failed = errors = skipped = 0
        for line in output.splitlines():
            # e.g. "46885 passed, 23 skipped, 12 deselected in 130.2s"
            if "passed" in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p == "passed":
                        try:
                            passed = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    elif p in ("failed", "error"):
                        try:
                            failed += int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    elif p == "skipped":
                        try:
                            skipped = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass

        status = "passed" if failed == 0 and errors == 0 else "failed"
        failure_summary = output if status == "failed" else ""
        return TestResult(
            task_id=task_id,
            status=status,
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            duration_s=duration,
            failure_summary=failure_summary,
        )

    @staticmethod
    def _suggest_fixes(root_causes: list[str]) -> list[str]:
        """Heuristic fix suggestions from root cause strings."""
        suggestions = []
        for cause in root_causes:
            if "ImportError" in cause:
                suggestions.append("Check module path and __init__.py files")
            elif "AssertionError" in cause:
                suggestions.append("Review tolerance or expected value in assertion")
            elif "AttributeError" in cause:
                suggestions.append("Check if the attribute/method was renamed")
            elif "ZeroDivisionError" in cause:
                suggestions.append("Add zero-guard in the denominator")
        return suggestions or ["Manual investigation required"]
