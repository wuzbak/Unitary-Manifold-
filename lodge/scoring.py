# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge/scoring.py — Precision Comparator & Epistemic Honesty Rubric

Evaluates an agent's submitted answer against the canonical ground-truth
produced by the pillar's backing ``src/core/`` module.

Scoring philosophy
------------------
* **Float answers** — scored by relative precision:
      score = max(0, 1 − |agent − truth| / (|truth| + ε))
* **Dict answers** — each numeric key is scored independently; mean is returned.
* **Bool answers** — 1.0 if correct, 0.0 if not.
* **Epistemic bonus** — +0.05 (capped at 1.0) if the agent explicitly states
  an uncertainty or identifies a known gap documented in FALLIBILITY.md.
* **Overclaiming penalty** — −0.10 if the agent claims exact derivation for a
  result that is known to be constrained (not fully derived) in the theory.

All scores are in [0.0, 1.0].  Reproducibility: re-running the same pillar
executor always returns the same ground truth, so scores are deterministic.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

__all__ = ["PrecisionResult", "score_answer", "score_float", "score_dict", "score_bool"]

_EPSILON = 1e-12

# Keys that are known to be *constrained* (not fully derived) in v20.1.
# Agents claiming "exact derivation" for these are penalised.
_CONSTRAINED_KEYS = frozenset({
    "lam_cobe",       # λ_COBE is fixed by normalisation, not derived
    "As_predicted",   # follows from λ_COBE
})

# Substrings that indicate the agent is acknowledging uncertainty (epistemic bonus)
_EPISTEMIC_MARKERS = (
    "uncertain", "approximate", "gap", "admission", "fallibility",
    "not derived", "constrained", "open problem", "tension", "undetermined",
    "circa", "±", "error", "open question",
)


@dataclass
class PrecisionResult:
    """Result of scoring one agent answer against the ground truth."""
    pillar_id: int
    agent_label: str
    raw_score: float                  # [0, 1] before bonuses/penalties
    final_score: float                # [0, 1] after adjustments
    epistemic_bonus: float = 0.0
    overclaim_penalty: float = 0.0
    detail: Dict[str, Any] = field(default_factory=dict)
    passed: bool = False              # True if final_score >= 0.75

    def __post_init__(self) -> None:
        self.passed = self.final_score >= 0.75

    def summary(self) -> str:
        status = "✅ PASS" if self.passed else "❌ BELOW THRESHOLD"
        return (
            f"Pillar {self.pillar_id} | {self.agent_label} | "
            f"raw={self.raw_score:.4f} → final={self.final_score:.4f} | {status}"
        )


# ---------------------------------------------------------------------------
# Core comparison helpers
# ---------------------------------------------------------------------------

def score_float(agent: float, truth: float) -> float:
    """Relative precision score for a scalar answer."""
    denom = abs(truth) + _EPSILON
    return max(0.0, 1.0 - abs(float(agent) - float(truth)) / denom)


def score_dict(agent: Dict[str, Any], truth: Dict[str, Any]) -> tuple[float, Dict[str, float]]:
    """Score each numeric key individually; return (mean_score, per_key_scores)."""
    per_key: Dict[str, float] = {}
    for key, truth_val in truth.items():
        agent_val = agent.get(key)
        if agent_val is None:
            per_key[key] = 0.0
            continue
        if isinstance(truth_val, bool):
            per_key[key] = 1.0 if bool(agent_val) == bool(truth_val) else 0.0
        elif isinstance(truth_val, (int, float)):
            per_key[key] = score_float(float(agent_val), float(truth_val))
        elif isinstance(truth_val, str):
            per_key[key] = 1.0 if str(agent_val).strip() == str(truth_val).strip() else 0.0
        else:
            per_key[key] = 0.0
    mean = sum(per_key.values()) / max(len(per_key), 1)
    return mean, per_key


def score_bool(agent: Any, truth: bool) -> float:
    """Binary score for boolean answers."""
    try:
        return 1.0 if bool(agent) == bool(truth) else 0.0
    except (TypeError, ValueError):
        return 0.0


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def score_answer(
    *,
    pillar_id: int,
    agent_label: str,
    agent_answer: Any,
    ground_truth: Any,
    expected_type: str,
    agent_reasoning: Optional[str] = None,
) -> PrecisionResult:
    """
    Score *agent_answer* against *ground_truth* for the given pillar.

    Parameters
    ----------
    pillar_id:      Pillar ID (for reporting)
    agent_label:    Human-readable label for the agent ("gpt-4o", "human", …)
    agent_answer:   The agent's submitted answer (float, dict, bool, …)
    ground_truth:   Canonical value from the pillar's executor
    expected_type:  "float" | "dict" | "bool" | "tuple"
    agent_reasoning: Optional free-text reasoning trace (used for epistemic bonus)
    """
    raw_score = 0.0
    detail: Dict[str, Any] = {}

    # ── Primary scoring ──────────────────────────────────────────────────────
    if expected_type == "float":
        if agent_answer is None:
            raw_score = 0.0
        else:
            raw_score = score_float(agent_answer, float(ground_truth))

    elif expected_type == "dict":
        if not isinstance(agent_answer, dict) or not isinstance(ground_truth, dict):
            raw_score = 0.0
        else:
            raw_score, detail["per_key"] = score_dict(agent_answer, ground_truth)

    elif expected_type == "bool":
        raw_score = score_bool(agent_answer, bool(ground_truth))

    elif expected_type == "tuple":
        # For tuple-valued ground truths (e.g. (alpha, converged))
        if isinstance(ground_truth, dict) and isinstance(agent_answer, dict):
            raw_score, detail["per_key"] = score_dict(agent_answer, ground_truth)
        elif isinstance(agent_answer, (list, tuple)) and isinstance(ground_truth, (list, tuple)):
            scores = [
                score_float(float(a), float(t))
                for a, t in zip(agent_answer, ground_truth)
                if isinstance(t, (int, float))
            ]
            raw_score = sum(scores) / max(len(scores), 1)
        else:
            raw_score = 0.0

    else:
        raw_score = 0.0

    # ── Epistemic bonus ──────────────────────────────────────────────────────
    epistemic_bonus = 0.0
    if agent_reasoning:
        lower = agent_reasoning.lower()
        if any(marker in lower for marker in _EPISTEMIC_MARKERS):
            epistemic_bonus = 0.05
            detail["epistemic_bonus_reason"] = "Agent acknowledged uncertainty or gap"

    # ── Overclaim penalty ────────────────────────────────────────────────────
    overclaim_penalty = 0.0
    if agent_reasoning and isinstance(ground_truth, dict):
        lower = agent_reasoning.lower()
        if any(k in lower for k in _CONSTRAINED_KEYS):
            if "exact derivation" in lower or "fully derived" in lower:
                overclaim_penalty = 0.10
                detail["overclaim_penalty_reason"] = (
                    "Agent claimed exact derivation for a constrained parameter"
                )

    # ── Final score ──────────────────────────────────────────────────────────
    final_score = min(1.0, max(0.0, raw_score + epistemic_bonus - overclaim_penalty))

    return PrecisionResult(
        pillar_id=pillar_id,
        agent_label=agent_label,
        raw_score=round(raw_score, 6),
        final_score=round(final_score, 6),
        epistemic_bonus=round(epistemic_bonus, 6),
        overclaim_penalty=round(overclaim_penalty, 6),
        detail=detail,
    )
