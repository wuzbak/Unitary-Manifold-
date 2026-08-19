# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero Manager 7 — Executive Synthesis & Human Interface

Maps to: 10-UM-SOS/, bot/session_bootstrap.py, HILS_SESSION_CURRENT.md

Sub-agents:
    SA7.1  Discrepancy auditor (cross-checks M1-M6 for contradictions)
    SA7.2  Branch merge planner
    SA7.3  Context compressor
    SA7.4  State-snapshot manager
    SA7.5  Human report writer

Purpose: The ONLY manager that talks directly to the human.  Aggregates,
synthesises, presents.  This is the "face" of AxiomZero.

HILS invariants (hard-wired — not soft suggestions):
    1. Human retains exclusive control over pillar numbering
    2. Human retains exclusive control over authorship claims in documents
    3. Human retains exclusive control over FALLIBILITY.md / falsification conditions
    4. No git commit without explicit human approval

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ExecutiveManager:
    """Manager 7: Executive Synthesis & Human Interface — the face of AxiomZero."""

    name = "M7_Executive"
    model_key = "strategic"
    sub_agents = [
        "SA7.1_discrepancy_auditor",
        "SA7.2_branch_merge_planner",
        "SA7.3_context_compressor",
        "SA7.4_state_snapshot_manager",
        "SA7.5_human_report_writer",
    ]

    # HILS protected actions — hard-blocked, not soft-suggested
    HILS_PROTECTED_ACTIONS = frozenset({
        "pillar_renumber",
        "authorship_change",
        "falsification_edit",
        "git_commit_main",
        "fallibility_md_edit",
        "separation_md_edit",
    })

    def __init__(self, config: Dict, model_router: Any, repo_root: Path):
        self.config = config
        self.model_router = model_router
        self.repo_root = repo_root
        self._hils_config = config.get("hils", {})

    async def run(self, state: Any) -> Dict[str, Any]:
        """
        Aggregate outputs from all managers, check for discrepancies,
        compress context, write a human-readable report, and enforce HILS.
        """
        task = state.task
        payload = task.payload

        logger.info("[%s] Executive synthesis for task %s", self.name, task.task_id)

        # SA7.1 — Audit for discrepancies between managers
        audit = await self._sa_discrepancy_audit(state)

        # HILS check — block any protected actions
        hils_block = self._hils_check(payload)
        if hils_block:
            task.status = "human_review"
            task.requires_human_approval = True
            task.results["hils_block"] = hils_block

        # SA7.2 — Branch/merge plan (if code task)
        merge_plan = await self._sa_merge_plan(payload)

        # SA7.3 — Compress context to fit in report
        compressed = await self._sa_compress_context(state)

        # SA7.4 — State snapshot
        snapshot = await self._sa_snapshot(task)

        # SA7.5 — Write human report
        report = await self._sa_human_report(
            task=task,
            audit=audit,
            merge_plan=merge_plan,
            compressed=compressed,
            hils_block=hils_block,
        )

        return {
            "manager": self.name,
            "status": "ok",
            "hils_block": hils_block,
            "discrepancies": audit.get("discrepancies", []),
            "report": report,
            "snapshot": snapshot,
            "merge_plan": merge_plan,
        }

    def _hils_check(self, payload: Dict) -> Optional[Dict]:
        """Hard-wired HILS invariant check.  Returns block info or None."""
        requested_actions = payload.get("actions", [])
        blocked = []
        for action in requested_actions:
            if action in self.HILS_PROTECTED_ACTIONS:
                blocked.append(action)

        # Check for direct file edits to protected files
        protected_files = set(self._hils_config.get("protected_files", [
            "FALLIBILITY.md", "SEPARATION.md", "CLAIM_MASTER_BOARD.md"
        ]))
        changed_files = payload.get("changed_files", [])
        protected_edits = [f for f in changed_files if any(pf in f for pf in protected_files)]

        if blocked or protected_edits:
            return {
                "blocked_actions": blocked,
                "protected_file_edits": protected_edits,
                "human": self._hils_config.get("human", "ThomasCory Walker-Pearson"),
                "message": (
                    f"HILS invariant: actions {blocked} and/or edits to "
                    f"{protected_edits} require explicit human approval from "
                    f"{self._hils_config.get('human', 'ThomasCory Walker-Pearson')}."
                ),
            }
        return None

    async def _sa_discrepancy_audit(self, state: Any) -> Dict:
        """SA7.1: Cross-check M1–M6 outputs for contradictions."""
        discrepancies = []

        m1 = getattr(state, "m1_output", None) or {}
        m2 = getattr(state, "m2_output", None) or {}
        m3 = getattr(state, "m3_output", None) or {}
        m4 = getattr(state, "m4_output", None) or {}

        # Check for M1 geometry vs M2 field consistency
        if m1.get("geometrically_consistent") is False and m2.get("field_equations_consistent") is True:
            discrepancies.append(
                "M1 reports geometry inconsistency but M2 reports field equations OK — investigate."
            )

        # Check for M3 unverified but M4 tests pass
        if m3.get("verified") is False and m4.get("tests_passed") is True:
            discrepancies.append(
                "M3 reports symbolic verification FAILED but M4 tests PASS — "
                "possible symbolic gap in test coverage."
            )

        # Check for M3 verified but M4 tests fail
        if m3.get("verified") is True and m4.get("tests_passed") is False:
            discrepancies.append(
                "M3 verified claim symbolically but M4 tests FAIL — "
                "possible symbolic-numerical discrepancy."
            )

        return {
            "discrepancy_count": len(discrepancies),
            "discrepancies": discrepancies,
        }

    async def _sa_merge_plan(self, payload: Dict) -> Dict:
        """SA7.2: If there are code changes, plan the merge strategy."""
        changed_files = payload.get("changed_files", [])
        if not changed_files:
            return {"needed": False}

        # Check if main branch is clean
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True,
                cwd=str(self.repo_root), timeout=10
            )
            dirty = bool(result.stdout.strip())
        except Exception:
            dirty = False

        return {
            "needed": True,
            "changed_files": changed_files,
            "working_tree_dirty": dirty,
            "strategy": "feature-branch → test gate → HILS approval → merge to main",
            "note": "Only M7 + human approval can trigger git commit",
        }

    async def _sa_compress_context(self, state: Any) -> Dict:
        """SA7.3: Compress the full agent state into a compact summary."""
        route = state.route if hasattr(state, "route") else []
        outputs = {}
        for key in ("m1", "m2", "m3", "m4", "m5", "m6"):
            out = getattr(state, f"{key}_output", None)
            if out:
                outputs[key] = {
                    "status": out.get("status", "unknown"),
                    "issues": out.get("issues", [])[:2],
                }
        return {
            "route": route,
            "manager_summaries": outputs,
            "cycle": state.task.cycle_count,
        }

    async def _sa_snapshot(self, task: Any) -> Dict:
        """SA7.4: Write a machine-readable state snapshot to disk."""
        snapshot_dir = Path.home() / ".axiomzero" / "snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snap = {
            "task_id": task.task_id,
            "description": task.description,
            "status": task.status,
            "epistemic_label": task.epistemic_label.value,
            "cycle_count": task.cycle_count,
            "timestamp": time.time(),
            "results": {k: str(v)[:200] for k, v in task.results.items()},
        }
        snap_file = snapshot_dir / f"{task.task_id}.json"
        snap_file.write_text(json.dumps(snap, indent=2))
        return {"snapshot_written": str(snap_file)}

    async def _sa_human_report(
        self,
        task: Any,
        audit: Dict,
        merge_plan: Dict,
        compressed: Dict,
        hils_block: Optional[Dict],
    ) -> str:
        """SA7.5: Generate a structured human-readable report."""
        lines = [
            f"# AxiomZero Task Report — {task.task_id}",
            f"",
            f"**Task:** {task.description}",
            f"**Status:** {task.status}",
            f"**Epistemic label:** {task.epistemic_label.value}",
            f"**Cycle:** {task.cycle_count}/{task.max_cycles}",
            f"",
        ]

        if hils_block:
            lines += [
                "## ⚠ HILS Invariant — Human Approval Required",
                f"",
                f"{hils_block['message']}",
                f"",
                f"**Human:** {hils_block['human']}",
                f"",
            ]

        if audit.get("discrepancies"):
            lines += ["## Manager Discrepancies", ""]
            for d in audit["discrepancies"]:
                lines.append(f"- {d}")
            lines.append("")

        # Manager pipeline summary
        summaries = compressed.get("manager_summaries", {})
        if summaries:
            lines += ["## Manager Pipeline", ""]
            for mgr, info in summaries.items():
                status = info.get("status", "?")
                issues = info.get("issues", [])
                icon = "✔" if status == "ok" else "⚠"
                lines.append(f"- {icon} **{mgr.upper()}**: {status}" +
                              (f" — {'; '.join(str(i) for i in issues)}" if issues else ""))
            lines.append("")

        if merge_plan.get("needed"):
            lines += [
                "## Code Changes Pending",
                f"Files: {', '.join(merge_plan.get('changed_files', [])[:5])}",
                f"Strategy: {merge_plan.get('strategy', 'N/A')}",
                "",
            ]

        # Task results
        if task.results:
            lines += ["## Results", ""]
            for k, v in task.results.items():
                lines.append(f"**{k}:** {str(v)[:200]}")
            lines.append("")

        return "\n".join(lines)
