# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge — AxiomZero Logic Lodge & Public Gymnasium

A publicly accessible, multi-agent physics gymnasium grounded in the
Unitary Manifold's 208+ pillars.  Every challenge is a real derivation;
every score is a mathematical truth value.

Structure
---------
lodge/
  pillar_registry.py   — 208-pillar challenge catalogue (backed by src/core/)
  scoring.py           — precision comparator + epistemic honesty rubric
  session_logger.py    — append-only honest JSON session ledger
  arcade.py            — CLI Pillar Arcade runner (Zone 1)
  leaderboard.py       — SQLite leaderboard + aggregate stats (Zone 1-3)
  watch.py             — real-time terminal observability monitor (Zone 4)
  rl_env.py            — gymnasium-compatible RL environment (Zone 3)
  lodge_zone.py        — Logic Lodge Socratic Q&A + human review queue (Zone 2)
  rag_bridge.py        — Knowledge Exchange RAG wrapper (Zone 5)
  server.py            — FastAPI HTTP + WebSocket server (public API)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

from lodge.pillar_registry import PillarRegistry, PillarEntry, REGISTRY
from lodge.scoring import score_answer, PrecisionResult
from lodge.session_logger import SessionLogger

__all__ = [
    "PillarRegistry",
    "PillarEntry",
    "REGISTRY",
    "score_answer",
    "PrecisionResult",
    "SessionLogger",
]
