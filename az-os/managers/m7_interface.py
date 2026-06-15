# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/managers/m7_interface.py — Manager 7: Executive Synthesis & Human Interface

The only manager that talks directly to the human operator (ThomasCory Walker-Pearson).
Aggregates outputs from M1–M6, synthesises a digest, and presents it clearly.
Also responsible for issuing HILS approval tokens after human confirmation.

Sub-agents:
  1. DiscrepancyAuditor   — cross-checks M1–M6 outputs for contradictions
  2. BranchMergePlanner   — plans git branch strategy for approved changes
  3. ContextCompressor    — compresses context to fit model windows
  4. StateSnapshotManager — saves and restores agent network state
  5. ReportWriter         — generates human-readable engineering reports
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from az_os.hils import HILS, HILSAction, ApprovalToken
from az_os.state import StateDB, AgentRecord

REPO_ROOT = Path(__file__).parent.parent.parent


@dataclass
class SynthesisReport:
    """The output of M7 — what the human sees."""
    timestamp: float = field(default_factory=time.time)
    overall_status: str = "ok"    # "ok" | "warning" | "critical"
    geometry_status: str = "unknown"
    field_status: str = "unknown"
    symbolic_status: str = "unknown"
    test_status: str = "unknown"
    corpus_status: str = "unknown"
    research_findings: list[str] = field(default_factory=list)
    discrepancies: list[str] = field(default_factory=list)
    pending_hils: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    raw_outputs: dict = field(default_factory=dict)


class M7InterfaceManager:
    """
    Manager 7 — Executive Synthesis & Human Interface.

    This is the "face" of AxiomZero.  It receives digests from all other
    managers, checks for internal contradictions, and presents a clean
    engineering report to the human.

    It is also the ONLY manager that can issue HILS approval tokens.
    Token issuance requires an explicit human confirmation (in Sprint 4:
    a UI dialog; in Sprint 2: a CLI prompt).
    """

    MANAGER_ID = "M7"
    KK_LEVEL = 3   # user space — intentionally NOT kernel or system

    def __init__(
        self,
        db: Optional[StateDB] = None,
        hils: Optional[HILS] = None,
    ) -> None:
        self._db = db or StateDB()
        self._hils = hils or HILS()

    # ------------------------------------------------------------------
    # Sub-agent 1: Discrepancy Auditor
    # ------------------------------------------------------------------

    def audit_discrepancies(self, manager_outputs: dict[str, list]) -> list[str]:
        """
        Cross-check outputs from all managers for internal contradictions.

        A discrepancy is flagged when:
          - M1 (geometry) says "ok" but M2 (fields) says "error"
          - M3 (symbolic) says "falsified" but M2 (fields) says "ok"
          - M4 (tests) says "failed" but M3 (symbolic) says "verified"

        Returns a list of discrepancy descriptions.
        """
        discrepancies = []
        m1 = manager_outputs.get("M1", [])
        m2 = manager_outputs.get("M2", [])
        m3 = manager_outputs.get("M3", [])
        m4_status = manager_outputs.get("M4", {}).get("status", "unknown")

        m1_ok = all(getattr(r, "status", "ok") == "ok" for r in m1)
        m2_ok = all(getattr(r, "status", "ok") == "ok" for r in m2)
        m3_verified = all(getattr(r, "status", "ok") in ("ok", "verified") for r in m3)

        if m1_ok and not m2_ok:
            discrepancies.append(
                "DISCREPANCY: M1 geometry is consistent but M2 field equations show errors. "
                "Possible sign error in stress-energy projection."
            )
        if not m3_verified and m2_ok:
            discrepancies.append(
                "DISCREPANCY: M3 symbolic verification failed but M2 field check passed. "
                "Numerical and symbolic results diverge — investigate tolerance settings."
            )
        if m4_status == "failed" and m3_verified:
            discrepancies.append(
                "DISCREPANCY: M4 test suite failed but M3 symbolic verification passed. "
                "Likely a code implementation error rather than a physics error."
            )
        return discrepancies

    # ------------------------------------------------------------------
    # Sub-agent 2: Branch Merge Planner
    # ------------------------------------------------------------------

    def plan_merge(self, approved_patches: list[str]) -> dict:
        """
        Plan the git branch strategy for merging approved patches.

        Returns a merge plan dict with branch names, commit messages, and
        the HILS token required to execute each step.

        This is informational — actual git operations are performed by
        the MCP Filesystem Server (Sprint 3).
        """
        if not approved_patches:
            return {"steps": [], "requires_hils": False}

        steps = []
        for i, patch in enumerate(approved_patches):
            steps.append({
                "step": i + 1,
                "action": f"Apply patch: {patch}",
                "branch": f"az-patch-{int(time.time())}-{i}",
                "commit_message": f"fix: {patch[:60]}",
                "requires_hils_action": HILSAction.COMMIT_TO_MAIN.value,
            })
        return {
            "steps": steps,
            "requires_hils": True,
            "note": "All steps require HILS approval token from M7 before execution.",
        }

    # ------------------------------------------------------------------
    # Sub-agent 3: Context Compressor
    # ------------------------------------------------------------------

    def compress_context(self, full_output: dict, max_chars: int = 8000) -> str:
        """
        Compress the full manager output into a context-window-friendly summary.

        Ensures that sub-agents never receive the full corpus — only the
        targeted excerpt relevant to their task.
        """
        lines = []
        for manager, output in full_output.items():
            if isinstance(output, list):
                summary = f"[{manager}] {len(output)} results"
                errors = [getattr(r, "error", None) for r in output if getattr(r, "error", None)]
                if errors:
                    summary += f" — ERRORS: {errors[:2]}"
            elif isinstance(output, dict):
                summary = f"[{manager}] status={output.get('status', 'unknown')}"
            else:
                summary = f"[{manager}] {str(output)[:200]}"
            lines.append(summary)

        compressed = "\n".join(lines)
        if len(compressed) > max_chars:
            compressed = compressed[:max_chars] + "\n... [truncated by M7 context compressor]"
        return compressed

    # ------------------------------------------------------------------
    # Sub-agent 4: State Snapshot Manager
    # ------------------------------------------------------------------

    def save_snapshot(self, label: str = "auto") -> str:
        """
        Save a snapshot of all agent states to the StateDB.

        Returns the snapshot ID.
        """
        agents = self._db.all_agents()
        snapshot_id = f"snap-{label}-{int(time.time())}"
        blob = json.dumps(
            [{"agent_id": a.agent_id, "status": a.status, "phi_debt": a.phi_debt}
             for a in agents]
        ).encode()
        self._db.save_checkpoint(snapshot_id, "M7", blob)
        return snapshot_id

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore agent states from a saved snapshot."""
        blob = self._db.load_checkpoint(snapshot_id)
        if blob is None:
            return False
        states = json.loads(blob.decode())
        for s in states:
            agent = self._db.get_agent(s["agent_id"])
            if agent:
                agent.status = s["status"]
                agent.phi_debt = s["phi_debt"]
                self._db.upsert_agent(agent)
        return True

    # ------------------------------------------------------------------
    # Sub-agent 5: Report Writer
    # ------------------------------------------------------------------

    def write_report(self, synthesis: SynthesisReport) -> str:
        """Generate a human-readable engineering report in Markdown."""
        status_emoji = {"ok": "✅", "warning": "⚠️", "critical": "🔴"}.get(
            synthesis.overall_status, "❓"
        )
        lines = [
            f"# AxiomZero Status Report {status_emoji}",
            f"*Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(synthesis.timestamp))}*",
            "",
            "## Subsystem Status",
            f"| Manager | Status |",
            f"|---------|--------|",
            f"| M1 Geometry  | {synthesis.geometry_status}  |",
            f"| M2 Fields    | {synthesis.field_status}     |",
            f"| M3 Symbolic  | {synthesis.symbolic_status}  |",
            f"| M4 Tests     | {synthesis.test_status}      |",
            f"| M5 Corpus    | {synthesis.corpus_status}    |",
            "",
        ]
        if synthesis.discrepancies:
            lines.append("## ⚠️ Discrepancies")
            for d in synthesis.discrepancies:
                lines.append(f"- {d}")
            lines.append("")
        if synthesis.research_findings:
            lines.append("## 📡 Research Findings")
            for f_ in synthesis.research_findings[:5]:
                lines.append(f"- {f_}")
            lines.append("")
        if synthesis.pending_hils:
            lines.append("## 🔐 Pending HILS Approvals")
            for h in synthesis.pending_hils:
                lines.append(f"- {h}")
            lines.append("")
        if synthesis.recommendations:
            lines.append("## 💡 Recommendations")
            for r in synthesis.recommendations:
                lines.append(f"- {r}")
            lines.append("")
        lines.append("---")
        lines.append("*Theory: ThomasCory Walker-Pearson  |  Kernel: GitHub Copilot (AI)*")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HILS token issuance (M7 exclusive)
    # ------------------------------------------------------------------

    def request_human_approval(
        self,
        action: HILSAction,
        description: str,
        ttl: float = 300.0,
    ) -> ApprovalToken:
        """
        Present an approval request to the human operator.

        In Sprint 2: prints to stdout and waits for input.
        In Sprint 4: presents a UI dialog.
        In bare-metal mode: renders to the framebuffer and waits for keyboard input.

        Returns an ApprovalToken if approved, raises HILSViolation if denied.
        """
        print(f"\n{'='*60}")
        print(f"🔐 HILS APPROVAL REQUEST")
        print(f"{'='*60}")
        print(f"Action:      {action.value}")
        print(f"Description: {description}")
        print(f"TTL:         {ttl}s")
        print(f"{'='*60}")

        try:
            response = input("Approve? [y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            response = "n"

        if response in ("y", "yes"):
            token = self._hils.issue_approval(action, ttl=ttl,
                                               metadata={"description": description})
            print(f"✅ Approved.  Token: {token.token_hash}")
            return token
        else:
            from az_os.hils import HILSViolation
            raise HILSViolation(f"Human operator denied action '{action.value}'")

    # ------------------------------------------------------------------
    # Master synthesis (orchestrates all managers)
    # ------------------------------------------------------------------

    def synthesise(self, manager_outputs: dict) -> SynthesisReport:
        """Build a SynthesisReport from all manager outputs."""
        def _status(outputs, ok_val="ok"):
            if not outputs:
                return "unknown"
            return "ok" if all(
                getattr(r, "status", ok_val) in (ok_val, "verified", "ok")
                for r in (outputs if isinstance(outputs, list) else [outputs])
            ) else "error"

        discrepancies = self.audit_discrepancies(manager_outputs)
        overall = "critical" if discrepancies else "ok"

        report = SynthesisReport(
            overall_status=overall,
            geometry_status=_status(manager_outputs.get("M1", [])),
            field_status=_status(manager_outputs.get("M2", [])),
            symbolic_status=_status(manager_outputs.get("M3", [])),
            test_status=manager_outputs.get("M4", {}).get("status", "unknown"),
            corpus_status=_status(manager_outputs.get("M5", [])),
            discrepancies=discrepancies,
            raw_outputs={k: str(v)[:500] for k, v in manager_outputs.items()},
        )
        return report
