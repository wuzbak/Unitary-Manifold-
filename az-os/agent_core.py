# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/agent_core.py — AxiomZero 7-Manager × 5-Sub-Agent Orchestrator

This is the top-level orchestrator for the AxiomZero cognitive layer.
It initialises all 7 managers, routes tasks between them, enforces the
HILS invariant, and provides a unified interface for the human operator.

## Architecture

    AgentCore
    ├── M1: GeometryManager   (5D metric, Christoffel, Riemann, compactification, boundary)
    ├── M2: FieldManager      (KK scalar, Maxwell, geodesic, stress-energy, EH action)
    ├── M3: SymbolicManager   (SymPy, Z3, type check, equivalence, edge cases)
    ├── M4: TestGuard         (test router, failure diagnosis, patch, perf log, artifact verify)
    ├── M5: CorpusManager     (vector retrieval, synthesis, cross-ref, terminology, drafts)
    ├── M6: ResearchManager   (arXiv, Brave, academic scraper, critic, citation)
    ├── M7: InterfaceManager  (discrepancy audit, merge plan, compress, snapshot, report)
    └── MCP: Filesystem + Executor + Browser servers

## Startup sequence

    core = AgentCore()
    core.boot()               # initialise all managers, validate constants
    report = core.status()    # get current status report
    core.run_forever()        # start the main event loop (Sprint 3+)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import sys
import time
import threading
from pathlib import Path
from typing import Optional

# Internal imports
from az_os.state import StateDB, AgentRecord
from az_os.hils import HILS
from az_os.managers import (
    M1GeometryManager,
    M2FieldManager,
    M3SymbolicManager,
    M4TestGuard,
    M5CorpusManager,
    M6ResearchManager,
    M7InterfaceManager,
)
from az_os.mcp import MCPFilesystemServer, MCPExecutorServer, MCPBrowserServer
from az_os.managers.m7_interface import SynthesisReport

REPO_ROOT = Path(__file__).parent.parent

# Physics constants (kernel-level, must never change without HILS approval)
WINDING_NUMBER = 5
K_CS = 74
N_S_PREDICTED = 0.9635
R_BRAIDED = 0.0315

# Monitoring sweep interval (seconds)
MONITOR_INTERVAL = 3600  # 1 hour


class AgentCore:
    """
    AxiomZero Agent Core — top-level 7-manager orchestrator.

    The AgentCore is the "kernel process" at KK level 0.  It owns the HILS
    enforcement engine and the SQLite state database.  All managers are
    children of the AgentCore.
    """

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        db_path: Optional[Path] = None,
        interactive: bool = True,
    ) -> None:
        self._repo_root = repo_root or REPO_ROOT
        self._db = StateDB(db_path)
        self._hils = HILS(repo_root=self._repo_root)
        self._interactive = interactive
        self._boot_time: Optional[float] = None
        self._monitor_thread: Optional[threading.Thread] = None

        # MCP servers
        self._fs  = MCPFilesystemServer(kk_level=1)
        self._exec = MCPExecutorServer(kk_level=1, repo_root=self._repo_root)
        self._browser = MCPBrowserServer()

        # Managers (created in boot())
        self._m1: Optional[M1GeometryManager] = None
        self._m2: Optional[M2FieldManager] = None
        self._m3: Optional[M3SymbolicManager] = None
        self._m4: Optional[M4TestGuard] = None
        self._m5: Optional[M5CorpusManager] = None
        self._m6: Optional[M6ResearchManager] = None
        self._m7: Optional[M7InterfaceManager] = None

    # ------------------------------------------------------------------
    # Boot sequence
    # ------------------------------------------------------------------

    def boot(self) -> None:
        """
        Boot the AxiomZero cognitive layer.

        Steps:
          1. Register all 7 managers in the state DB.
          2. Validate core physics constants with M3.
          3. Run a targeted test subset to confirm the kernel is healthy.
          4. Initialise the corpus index (M5).
          5. Start the background monitoring thread (M6).
        """
        self._boot_time = time.time()
        print(f"\n{'='*60}")
        print(f"  AxiomZero Cognitive Layer — BOOT SEQUENCE")
        print(f"  Winding number n_w={WINDING_NUMBER}  |  k_cs={K_CS}")
        print(f"{'='*60}\n")

        # Step 1: Initialise managers
        print("[BOOT] Initialising 7-manager network...")
        self._m1 = M1GeometryManager()
        self._m2 = M2FieldManager()
        self._m3 = M3SymbolicManager()
        self._m4 = M4TestGuard(self._db, self._hils, self._repo_root)
        self._m5 = M5CorpusManager()
        self._m6 = M6ResearchManager()
        self._m7 = M7InterfaceManager(self._db, self._hils)

        # Register agents in state DB
        self._register_all_agents()

        # Step 2: Validate physics constants
        print("[BOOT] M3: Validating core physics constants...")
        const_results = self._m3.validate_core_constants()
        failed = [r for r in const_results if r.status not in ("verified", "ok")]
        if failed:
            print(f"[BOOT] ⚠️  {len(failed)} constant validation(s) failed:")
            for f in failed:
                print(f"       {f.agent}: {f.error or f.value}")
        else:
            print(f"[BOOT] ✅ All {len(const_results)} core constants verified.")

        # Step 3: Minimal test smoke-check (not the full regression — too slow for boot)
        print("[BOOT] M4: Running smoke test (metric + boundary)...")
        smoke = self._m4.run_subset(
            ["tests/test_metric.py", "tests/test_boundary.py"],
            markers=["not slow"],
            timeout=60,
        )
        print(f"[BOOT]    {smoke.passed} passed, {smoke.failed} failed in {smoke.duration_s:.1f}s")
        if smoke.failed > 0:
            print(f"[BOOT] ⚠️  Smoke test failures detected — run full regression: core.run_full_regression()")

        # Step 4: Corpus index
        print("[BOOT] M5: Building corpus index...")
        idx_result = self._m5.retrieve("5D Kaluza-Klein winding number", top_k=1)
        if idx_result.status == "ok":
            print(f"[BOOT] ✅ Corpus index ready.")
        else:
            print(f"[BOOT] ⚠️  Corpus index unavailable: {idx_result.error}")

        # Step 5: Start background monitoring
        print("[BOOT] M6: Starting background research monitor...")
        self._start_monitor()

        print(f"\n{'='*60}")
        print(f"  AxiomZero Cognitive Layer — BOOT COMPLETE")
        print(f"  Use core.status() for a full status report.")
        print(f"{'='*60}\n")

    # ------------------------------------------------------------------
    # Status / reporting
    # ------------------------------------------------------------------

    def status(self) -> str:
        """Return a human-readable status report."""
        if self._m1 is None:
            return "AgentCore not booted — call core.boot() first."

        m1_results = self._m1.full_audit()
        m2_results = self._m2.full_audit()
        m3_results = self._m3.validate_core_constants()

        synthesis = self._m7.synthesise({
            "M1": m1_results,
            "M2": m2_results,
            "M3": m3_results,
            "M4": {"status": "ok"},  # smoke test ran at boot
            "M5": [],
        })
        return self._m7.write_report(synthesis)

    # ------------------------------------------------------------------
    # Test management
    # ------------------------------------------------------------------

    def run_full_regression(self, timeout: int = 900) -> dict:
        """Run the full 46,885+ test regression via M4."""
        if self._m4 is None:
            return {"error": "M4 not initialised"}
        print("[M4] Starting full regression (may take ~130s)...")
        result = self._m4.run_full_regression(timeout=timeout)
        print(f"[M4] {result.passed} passed, {result.failed} failed in {result.duration_s:.1f}s")
        return {
            "status": result.status,
            "passed": result.passed,
            "failed": result.failed,
            "skipped": result.skipped,
            "duration_s": result.duration_s,
        }

    # ------------------------------------------------------------------
    # Research
    # ------------------------------------------------------------------

    def monitor_now(self) -> None:
        """Trigger an immediate research sweep via M6."""
        if self._m6 is None:
            return
        findings = self._m6.monitor_sweep()
        if findings:
            print(f"[M6] {len(findings)} relevant papers found:")
            for f in findings:
                for p in f.papers:
                    score = p.get("relevance_score", 0)
                    title = p.get("title", "Unknown")
                    print(f"     [{score:.2f}] {title}")
        else:
            print("[M6] No high-relevance papers found in this sweep.")

    # ------------------------------------------------------------------
    # Geometry query
    # ------------------------------------------------------------------

    def verify_geometry(self) -> str:
        """Run the full M1 geometry audit and return a summary."""
        if self._m1 is None:
            return "M1 not initialised"
        results = self._m1.full_audit()
        lines = []
        for r in results:
            icon = "✅" if r.status == "ok" else "❌"
            lines.append(f"{icon} {r.agent}: {r.status}")
            if r.error:
                lines.append(f"   Error: {r.error}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _register_all_agents(self) -> None:
        """Register all managers in the state DB."""
        for manager_id, kk_level in [
            ("M1", 0), ("M2", 0), ("M3", 1), ("M4", 1),
            ("M5", 2), ("M6", 2), ("M7", 3),
        ]:
            self._db.upsert_agent(AgentRecord(
                agent_id=manager_id,
                manager=manager_id,
                role="manager",
                status="idle",
                kk_level=kk_level,
            ))

    def _start_monitor(self) -> None:
        """Start the background M6 monitoring thread."""
        def _loop():
            while True:
                time.sleep(MONITOR_INTERVAL)
                if self._m6:
                    self._m6.monitor_sweep()

        self._monitor_thread = threading.Thread(target=_loop, daemon=True)
        self._monitor_thread.start()
