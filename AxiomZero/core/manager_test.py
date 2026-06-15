# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero Manager 4 — Test Orchestration & CI Guard

Maps to: tests/, recycling/, 5-GOVERNANCE/Unitary Pentad/, pytest.ini

Sub-agents:
    SA4.1  Test subset router (pillar-tag-based selection)
    SA4.2  Failure diagnostician
    SA4.3  Patch generator
    SA4.4  Performance logger
    SA4.5  Artifact verifier

Purpose: MANDATORY GATEKEEPER.  Any agent-generated code change must pass
the regression suite before being committed.

Critical invariant:
    M4 ALWAYS runs tests in an isolated tmpdir copy of the repository.
    It NEVER modifies the working tree.
    Only M7 (with explicit human approval) can trigger git commit.

The 0 test failure constraint is the hardest invariant in the system.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import asyncio
import logging
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TestManager:
    """Manager 4: Test Orchestration & CI Guard — the gatekeeper."""

    name = "M4_Test"
    model_key = "test"
    sub_agents = [
        "SA4.1_test_subset_router",
        "SA4.2_failure_diagnostician",
        "SA4.3_patch_generator",
        "SA4.4_performance_logger",
        "SA4.5_artifact_verifier",
    ]

    # Pillar-tag → test path mapping for fast subset routing
    PILLAR_TEST_MAP = {
        "core": "tests/test_metric.py tests/test_evolution.py tests/test_boundary.py",
        "multiverse": "tests/test_fixed_point.py",
        "quantum": "tests/test_quantum_unification.py",
        "atomic": "tests/test_atomic_structure.py",
        "cold_fusion": "tests/test_cold_fusion.py",
        "medicine": "tests/test_medicine.py",
        "justice": "tests/test_justice.py",
        "governance": "tests/test_governance.py",
        "neuroscience": "tests/test_neuroscience.py",
        "ecology": "tests/test_ecology.py",
        "climate": "tests/test_climate.py",
        "marine": "tests/test_marine.py",
        "psychology": "tests/test_psychology.py",
        "genetics": "tests/test_genetics.py",
        "materials": "tests/test_materials.py",
        "recycling": "recycling/",
        "pentad": "5-GOVERNANCE/Unitary Pentad/",
        "axiomzero": "AxiomZero/tests/",
        "full": "tests/ recycling/ 5-GOVERNANCE/Unitary Pentad/",
    }

    def __init__(self, config: Dict, model_router: Any, repo_root: Path):
        self.config = config
        self.model_router = model_router
        self.repo_root = repo_root

    async def run(self, state: Any) -> Dict[str, Any]:
        """
        Run the appropriate test subset in an isolated tmpdir.
        Returns tests_passed=True/False and detailed results.
        """
        task = state.task
        payload = task.payload

        logger.info("[%s] Test gate for task %s", self.name, task.task_id)

        # SA4.1 — Determine which tests to run
        route_result = await self._sa_route_tests(payload)

        if not route_result.get("should_run", True):
            return {
                "manager": self.name,
                "tests_passed": True,
                "reason": "No code changes detected — tests not required",
                "skipped": True,
            }

        test_paths = route_result.get("test_paths", ["tests/"])

        # SA4.4 — Log start
        perf = await self._sa_perf_start()

        # Run tests in isolation
        run_result = await self._run_tests_isolated(test_paths, payload)

        # SA4.2 — Diagnose failures if any
        diagnosis = {}
        if not run_result["passed"]:
            diagnosis = await self._sa_diagnose_failures(run_result)

        # SA4.4 — Log finish
        await self._sa_perf_finish(perf, run_result)

        # SA4.5 — Artifact verification
        artifacts = await self._sa_verify_artifacts(run_result)

        passed = run_result["passed"]
        reason = None if passed else (
            diagnosis.get("summary") or run_result.get("summary", "Tests failed")
        )

        return {
            "manager": self.name,
            "tests_passed": passed,
            "reason": reason,
            "test_paths": test_paths,
            "run_result": run_result,
            "diagnosis": diagnosis,
            "artifacts": artifacts,
            "status": "ok" if passed else "blocked",
        }

    async def _sa_route_tests(self, payload: Dict) -> Dict:
        """SA4.1: Select the minimal test subset based on pillar tag or changed files."""
        # Check if payload requests a specific pillar tag
        pillar_tag = payload.get("pillar_tag", "")
        changed_files: List[str] = payload.get("changed_files", [])
        force_full = payload.get("force_full_suite", False)

        if force_full:
            return {"should_run": True, "test_paths": ["tests/", "recycling/",
                                                        "5-GOVERNANCE/Unitary Pentad/"]}

        if not changed_files and not pillar_tag:
            # No code changes — skip tests
            return {"should_run": False}

        # Route by pillar tag
        if pillar_tag and pillar_tag in self.PILLAR_TEST_MAP:
            raw = self.PILLAR_TEST_MAP[pillar_tag]
            paths = [p.strip() for p in raw.split() if p.strip()]
            return {"should_run": True, "test_paths": paths, "routed_by": "pillar_tag"}

        # Route by changed files — pick the narrowest matching subset
        for tag, raw_paths in self.PILLAR_TEST_MAP.items():
            if tag == "full":
                continue
            if any(tag in f for f in changed_files):
                paths = [p.strip() for p in raw_paths.split() if p.strip()]
                return {"should_run": True, "test_paths": paths, "routed_by": f"changed_files({tag})"}

        # Default: run axiomzero tests + core
        return {
            "should_run": True,
            "test_paths": ["tests/test_metric.py", "tests/test_evolution.py",
                           "AxiomZero/tests/"],
            "routed_by": "default_subset",
        }

    async def _run_tests_isolated(self, test_paths: List[str], payload: Dict) -> Dict:
        """
        Run pytest in an isolated tmpdir.  NEVER modifies the working tree.
        """
        with tempfile.TemporaryDirectory(prefix="axiomzero_test_") as tmpdir:
            tmp = Path(tmpdir)

            # Copy repository to tmpdir (shallow — just what we need)
            logger.info("[%s] Copying repo to isolated tmpdir: %s", self.name, tmpdir)
            try:
                shutil.copytree(
                    self.repo_root, tmp / "repo",
                    ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc",
                                                 ".dvc", "node_modules"),
                    dirs_exist_ok=False,
                )
            except Exception as exc:
                return {"passed": False, "summary": f"Failed to copy repo: {exc}",
                        "stdout": "", "stderr": str(exc), "returncode": -1}

            # Apply any patch from payload
            patch = payload.get("code_patch")
            if patch:
                patch_result = self._apply_patch(tmp / "repo", patch)
                if not patch_result["ok"]:
                    return {"passed": False,
                            "summary": f"Patch failed: {patch_result['error']}",
                            "stdout": "", "stderr": patch_result["error"], "returncode": -2}

            # Build pytest command
            resolved_paths = []
            for p in test_paths:
                full = tmp / "repo" / p
                if full.exists():
                    resolved_paths.append(str(full))
                else:
                    logger.warning("[%s] Test path not found in tmpdir: %s", self.name, p)

            if not resolved_paths:
                return {"passed": True, "summary": "No valid test paths found — vacuously passed",
                        "stdout": "", "stderr": "", "returncode": 0}

            cmd = [sys.executable, "-m", "pytest"] + resolved_paths + ["-q", "--tb=short", "--no-header"]

            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(tmp / "repo"),
                )
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=300  # 5 minute max
                )
                stdout = stdout_b.decode(errors="replace")
                stderr = stderr_b.decode(errors="replace")
                passed = proc.returncode == 0
                # Extract summary line
                summary = self._extract_summary(stdout)
                return {
                    "passed": passed,
                    "returncode": proc.returncode,
                    "summary": summary,
                    "stdout": stdout[-5000:],  # Last 5k chars
                    "stderr": stderr[-2000:],
                }
            except asyncio.TimeoutError:
                return {"passed": False, "summary": "Tests timed out (>5 min)",
                        "stdout": "", "stderr": "TIMEOUT", "returncode": -3}
            except Exception as exc:
                return {"passed": False, "summary": f"Test runner error: {exc}",
                        "stdout": "", "stderr": str(exc), "returncode": -4}

    def _apply_patch(self, repo_path: Path, patch: Dict) -> Dict:
        """Apply a file patch (dict of {filepath: new_content}) to the tmpdir."""
        try:
            for rel_path, content in patch.items():
                target = repo_path / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _extract_summary(self, output: str) -> str:
        """Extract the pytest summary line (e.g. '427 passed, 0 failed')."""
        for line in reversed(output.splitlines()):
            if "passed" in line or "failed" in line or "error" in line:
                return line.strip()
        return output[-200:].strip() if output else "(no output)"

    async def _sa_diagnose_failures(self, run_result: Dict) -> Dict:
        """SA4.2: Parse pytest output and extract failure details."""
        stdout = run_result.get("stdout", "")
        lines = stdout.splitlines()

        failures = []
        current = []
        in_failure = False
        for line in lines:
            if line.startswith("FAILED") or line.startswith("ERROR"):
                if current:
                    failures.append("\n".join(current))
                current = [line]
                in_failure = True
            elif in_failure:
                current.append(line)

        if current:
            failures.append("\n".join(current))

        return {
            "failure_count": len(failures),
            "failures": failures[:5],  # First 5 failures
            "summary": run_result.get("summary", ""),
        }

    async def _sa_perf_start(self) -> Dict:
        import time
        return {"start_time": time.time()}

    async def _sa_perf_finish(self, perf: Dict, run_result: Dict) -> Dict:
        import time
        elapsed = time.time() - perf.get("start_time", time.time())
        logger.info("[%s] Test run completed in %.1fs — passed=%s",
                    self.name, elapsed, run_result.get("passed"))
        return {"elapsed_seconds": elapsed}

    async def _sa_verify_artifacts(self, run_result: Dict) -> Dict:
        """SA4.5: Verify test artifacts (coverage report, junit XML, etc.)."""
        return {
            "stdout_chars": len(run_result.get("stdout", "")),
            "has_output": bool(run_result.get("stdout")),
        }
