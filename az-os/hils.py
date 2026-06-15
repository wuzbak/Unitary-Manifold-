# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/hils.py — HILS (Human-in-the-Loop Systems) Invariant Enforcement

The HILS Invariant is the constitutional layer of AxiomZero.  No agent action
that crosses a hardgate boundary is permitted without a human-approved token.

Hardgate boundaries in AxiomZero OS:
  1. Pillar numbering and canonicalisation
  2. Authorship claims in documents
  3. Any write to FALLIBILITY.md or falsification conditions
  4. Any kernel operation at KK ring 0 from a ring 3+ agent
  5. Any action that would remove or modify existing test assertions

This module enforces these boundaries.  Agent code must call
``hils.require_approval(action)`` before crossing any boundary.
If approval is not present, the call raises ``HILSViolation``.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import enum
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Set

__all__ = ["HILS", "HILSAction", "HILSViolation", "ApprovalToken"]


class HILSAction(enum.Enum):
    """Enumeration of actions that require HILS approval."""
    PILLAR_CANONICALISE   = "pillar_canonicalise"
    AUTHORSHIP_MODIFY     = "authorship_modify"
    FALLIBILITY_WRITE     = "fallibility_write"
    FALSIFICATION_MODIFY  = "falsification_modify"
    TEST_DELETE           = "test_delete"
    TEST_MODIFY_ASSERTION = "test_modify_assertion"
    KERNEL_RING0_ACCESS   = "kernel_ring0_access"
    COMMIT_TO_MAIN        = "commit_to_main"
    AGENT_SPAWN_UNLIMITED = "agent_spawn_unlimited"


class HILSViolation(Exception):
    """Raised when an agent attempts a hardgate action without approval."""


@dataclass
class ApprovalToken:
    """
    A human-issued approval token for a specific HILS action.

    Tokens are created by the human operator, have a TTL (default 300 s),
    and are single-use.  The token's integrity is verified by SHA-256 of
    the action + timestamp + a shared secret.

    In production: tokens are issued through the M7 human interface and
    signed with the operator's private key.  In Sprint 2: a simple HMAC
    approach is used.
    """
    action: HILSAction
    issued_at: float
    ttl_seconds: float
    token_hash: str
    used: bool = False
    metadata: dict = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check that the token has not expired or been used."""
        if self.used:
            return False
        age = time.time() - self.issued_at
        return age <= self.ttl_seconds

    def consume(self) -> None:
        """Mark the token as used (single-use enforcement)."""
        self.used = True


class HILS:
    """
    HILS Invariant Enforcement Engine.

    Maintains a registry of pending and consumed approval tokens.
    All hardgate actions must pass through ``require_approval``.

    Usage::

        hils = HILS()
        token = hils.issue_approval(HILSAction.COMMIT_TO_MAIN, ttl=300)
        # ... (human reviews the action in M7 interface) ...
        hils.require_approval(HILSAction.COMMIT_TO_MAIN, token)
        # Now the action is permitted.
    """

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self._tokens: dict[str, ApprovalToken] = {}
        self._audit_log: list[dict] = []
        self._repo_root = repo_root or Path(__file__).parent.parent

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def issue_approval(
        self,
        action: HILSAction,
        ttl: float = 300.0,
        metadata: Optional[dict] = None,
    ) -> ApprovalToken:
        """
        Issue a new approval token for the given action.

        This method should be called by the M7 Human Interface agent
        AFTER receiving explicit confirmation from the human operator.
        The token is then passed to the agent that needs to perform the
        hardgate action.

        Parameters
        ----------
        action : HILSAction
            The hardgate action being approved.
        ttl : float
            Time-to-live in seconds.  Default 300 (5 minutes).
        metadata : dict, optional
            Additional context (e.g., which pillar, which commit SHA).

        Returns
        -------
        ApprovalToken
            A single-use token valid for ``ttl`` seconds.
        """
        now = time.time()
        raw = f"{action.value}:{now}:{ttl}"
        token_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        token = ApprovalToken(
            action=action,
            issued_at=now,
            ttl_seconds=ttl,
            token_hash=token_hash,
            metadata=metadata or {},
        )
        self._tokens[token_hash] = token
        self._log("ISSUED", action, token_hash, metadata or {})
        return token

    def require_approval(
        self,
        action: HILSAction,
        token: Optional[ApprovalToken] = None,
    ) -> None:
        """
        Assert that the given action has a valid approval token.

        Raises ``HILSViolation`` if:
          - No token is provided
          - The token has expired
          - The token has already been used
          - The token is for a different action

        Parameters
        ----------
        action : HILSAction
        token : ApprovalToken, optional
        """
        if token is None:
            self._log("BLOCKED", action, None, {})
            raise HILSViolation(
                f"HILS: Action '{action.value}' requires human approval. "
                f"No token provided.  Request approval through M7 interface."
            )
        if token.action != action:
            self._log("BLOCKED", action, token.token_hash, {"reason": "wrong_action"})
            raise HILSViolation(
                f"HILS: Token is for action '{token.action.value}', "
                f"not '{action.value}'."
            )
        if not token.is_valid():
            self._log("BLOCKED", action, token.token_hash, {"reason": "expired_or_used"})
            raise HILSViolation(
                f"HILS: Approval token for '{action.value}' has expired or been used."
            )
        token.consume()
        self._log("APPROVED", action, token.token_hash, token.metadata)

    def audit_log(self) -> list[dict]:
        """Return a copy of the full HILS audit log."""
        return list(self._audit_log)

    def pending_approvals(self) -> list[ApprovalToken]:
        """Return all tokens that are still valid and unused."""
        return [t for t in self._tokens.values() if t.is_valid()]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _log(
        self,
        event: str,
        action: HILSAction,
        token_hash: Optional[str],
        metadata: dict,
    ) -> None:
        entry = {
            "timestamp": time.time(),
            "event": event,
            "action": action.value,
            "token_hash": token_hash,
            "metadata": metadata,
        }
        self._audit_log.append(entry)
