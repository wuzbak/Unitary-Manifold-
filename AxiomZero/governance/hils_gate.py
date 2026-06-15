# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
AxiomZero governance/hils_gate.py — HILS Invariant Enforcement

Hard-wired human control layer.  These are NOT soft suggestions.

HILS Invariants (Constitutional layer — cannot be overridden by any agent):
  1. ThomasCory Walker-Pearson retains exclusive control over
     pillar numbering and canonicalization
  2. ThomasCory Walker-Pearson retains exclusive control over
     authorship claims in documents
  3. ThomasCory Walker-Pearson retains exclusive control over
     any action touching FALLIBILITY.md or the falsification conditions
  4. No git commit to main without explicit human approval
  5. Epistemic separation: ADJACENT-TRACK claims cannot be certified
     as HARDGATE physics by any agent

The governance MCP layer routes any action touching pillar definitions,
test counts, or theoretical claims through the Pentad classification
endpoint (/api/v1/governance/classify).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hard-coded invariants — do not make these configurable
# ---------------------------------------------------------------------------

PROTECTED_HUMAN = "ThomasCory Walker-Pearson"

PROTECTED_FILES: Set[str] = {
    "FALLIBILITY.md",
    "SEPARATION.md",
    "CLAIM_MASTER_BOARD.md",
    "PROVENANCE.md",
    "AUTHORS",
    "CITATION.cff",
}

PROTECTED_ACTIONS: Set[str] = {
    "pillar_renumber",
    "pillar_canonicalize",
    "authorship_change",
    "falsification_edit",
    "git_commit_main",
    "fallibility_md_edit",
    "separation_md_edit",
    "test_count_override",
    "epistemic_label_change",
}

# Epistemic labels that cannot be promoted by agents
CANNOT_PROMOTE_TO_HARDGATE: Set[str] = {
    "ADJACENT-TRACK",
    "GOVERNANCE",
    "UNVERIFIED",
}

# Pattern: pillar number in a filename
_PILLAR_FILE_RE = re.compile(r"pillar\d+", re.IGNORECASE)


class HILSGate:
    """
    Constitutional HILS enforcement gate.

    Every proposed agent action passes through this gate.
    Blocked actions are logged and escalated to M7 (human interface).
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).parent.parent.parent
        self._violations: List[Dict] = []

    def check_action(
        self,
        action_type: str,
        agent: str,
        payload: Optional[Dict] = None,
    ) -> Dict:
        """
        Check an agent action against HILS invariants.

        Returns:
            {"allowed": bool, "reason": str, "requires_human_approval": bool}
        """
        payload = payload or {}

        # Rule 1: Protected actions require human approval
        if action_type in PROTECTED_ACTIONS:
            self._record_violation(action_type, agent, "Protected action")
            return {
                "allowed": False,
                "requires_human_approval": True,
                "reason": (
                    f"Action '{action_type}' requires explicit approval from "
                    f"{PROTECTED_HUMAN}. This is a hard HILS invariant."
                ),
            }

        # Rule 2: Protected file edits
        changed_files = payload.get("changed_files", []) + payload.get("files", [])
        protected_edits = [
            f for f in changed_files
            if any(pf in Path(f).name for pf in PROTECTED_FILES)
        ]
        if protected_edits:
            self._record_violation(action_type, agent, f"Protected files: {protected_edits}")
            return {
                "allowed": False,
                "requires_human_approval": True,
                "reason": (
                    f"Editing protected files {protected_edits} requires approval from "
                    f"{PROTECTED_HUMAN}."
                ),
            }

        # Rule 3: Pillar number changes require human approval
        pillar_ops = payload.get("pillar_operations", [])
        if pillar_ops:
            self._record_violation(action_type, agent, f"Pillar operations: {pillar_ops}")
            return {
                "allowed": False,
                "requires_human_approval": True,
                "reason": (
                    f"Pillar operations {pillar_ops} require approval from {PROTECTED_HUMAN}."
                ),
            }

        # Rule 4: Epistemic label promotion blocked
        from_label = payload.get("from_epistemic_label", "")
        to_label = payload.get("to_epistemic_label", "")
        if from_label in CANNOT_PROMOTE_TO_HARDGATE and to_label == "HARDGATE":
            self._record_violation(action_type, agent, f"Invalid epistemic promotion {from_label}→HARDGATE")
            return {
                "allowed": False,
                "requires_human_approval": True,
                "reason": (
                    f"Cannot promote '{from_label}' to 'HARDGATE' — "
                    f"epistemic separation is a hard HILS invariant."
                ),
            }

        # Rule 5: git commit to main requires human approval
        git_ops = payload.get("git_operations", [])
        if any("commit" in op or "push" in op for op in git_ops):
            self._record_violation(action_type, agent, f"git commit/push: {git_ops}")
            return {
                "allowed": False,
                "requires_human_approval": True,
                "reason": (
                    f"Git commit/push operations require explicit approval from {PROTECTED_HUMAN}."
                ),
            }

        return {"allowed": True, "requires_human_approval": False, "reason": ""}

    def check_file_edit(self, file_path: str, agent: str) -> Dict:
        """Quick check: is editing this file allowed without human approval?"""
        path = Path(file_path)
        if path.name in PROTECTED_FILES:
            return {
                "allowed": False,
                "requires_human_approval": True,
                "reason": f"'{path.name}' is a HILS-protected file.",
            }
        # Check if it's a pillar definition file
        if _PILLAR_FILE_RE.search(path.stem):
            # Pillar source files are OK to edit (agents work on code)
            # but pillar *numbering* changes are not
            pass
        return {"allowed": True, "requires_human_approval": False, "reason": ""}

    def check_epistemic_claim(
        self,
        claim: str,
        epistemic_label: str,
    ) -> Dict:
        """
        Verify an agent's epistemic claim is consistent with the separation policy.
        """
        # ADJACENT-TRACK claims cannot be made with HARDGATE language
        hardgate_language = [
            "formally proves", "definitively establishes", "rigorously derives",
            "is a theorem of", "constitutes proof",
        ]
        if epistemic_label in ("ADJACENT-TRACK", "GOVERNANCE"):
            for phrase in hardgate_language:
                if phrase.lower() in claim.lower():
                    return {
                        "consistent": False,
                        "reason": (
                            f"ADJACENT-TRACK / GOVERNANCE claim uses HARDGATE language ('{phrase}'). "
                            "Per SEPARATION.md, this label cannot use hardgate framing."
                        ),
                    }
        return {"consistent": True}

    def classify_for_pentad(self, action_type: str, payload: Dict) -> Dict:
        """
        Route an action through the Pentad classification endpoint.
        Maps to: /api/v1/governance/classify (10-UM-SOS backend)
        """
        # Determine Pentad classification
        pillar_touched = bool(payload.get("pillar_operations"))
        if pillar_touched:
            classification = "STRUCTURAL"
        elif action_type in PROTECTED_ACTIONS or payload.get("changed_files", []):
            classification = "OPERATIONAL"
        else:
            classification = "ROUTINE"

        return {
            "pentad_classification": classification,
            "requires_pentad_review": classification == "STRUCTURAL",
            "action_type": action_type,
        }

    def get_violations(self) -> List[Dict]:
        return list(self._violations)

    def clear_violations(self) -> None:
        self._violations.clear()

    def _record_violation(self, action: str, agent: str, reason: str) -> None:
        import time
        entry = {"ts": time.time(), "action": action, "agent": agent, "reason": reason}
        self._violations.append(entry)
        logger.warning("HILS violation: agent=%s action=%s reason=%s", agent, action, reason)


# ---------------------------------------------------------------------------
# Module-level convenience gate (singleton)
# ---------------------------------------------------------------------------
_default_gate: Optional[HILSGate] = None


def get_gate(repo_root: Optional[Path] = None) -> HILSGate:
    global _default_gate
    if _default_gate is None:
        _default_gate = HILSGate(repo_root=repo_root)
    return _default_gate


def check(action_type: str, agent: str, payload: Optional[Dict] = None) -> Dict:
    """Module-level shortcut for gate checks."""
    return get_gate().check_action(action_type, agent, payload)
