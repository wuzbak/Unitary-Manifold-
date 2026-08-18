# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Merged Axiom OS entry point exposing both the canonical orchestrator and legacy AgentCore."""
from __future__ import annotations

from core.agent_core import AxiomZeroOrchestrator, AgentTask, AgentState, EpistemicLabel

try:
    from legacy_agent_core import AgentCore  # type: ignore
except Exception:  # pragma: no cover
    AgentCore = None  # type: ignore

__all__ = [
    "AgentCore",
    "AxiomZeroOrchestrator",
    "AgentTask",
    "AgentState",
    "EpistemicLabel",
]
