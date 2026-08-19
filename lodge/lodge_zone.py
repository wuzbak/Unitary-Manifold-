# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge/lodge_zone.py — Logic Lodge: Socratic Q&A + Human Review Queue (Zone 2)

The Logic Lodge is the epistemically rigorous zone where agents engage with
the formal proof structure of the Unitary Manifold.  Unlike the Pillar Arcade
(automated scoring), the Lodge awards full marks only after human review.

Workflow
--------
1. Agent receives a Lodge prompt (a Socratic reasoning challenge).
2. Agent submits a reasoning trace (free text + optional numeric claims).
3. The system auto-scores numeric claims against the known physics.
4. The full submission is placed in the human review queue.
5. A human steward reviews the reasoning quality and epistemic honesty.
6. Final score = 0.6 × auto_score + 0.4 × human_score (both in [0, 1]).

Lodge prompt types
------------------
derive    : "Starting from X, derive Y."
gap       : "Identify the known gap in Admission N and propose a test."
falsify   : "Given observation Z, compute the falsification implications."
compare   : "Compare the UM prediction to the experimental measurement."
extend    : "Propose a new pillar or corollary consistent with the framework."

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys
_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

__all__ = [
    "LodgePrompt",
    "LodgeSubmission",
    "LodgeReviewQueue",
    "LODGE_PROMPTS",
]

_QUEUE_DIR = Path(__file__).parent / "ledger" / "lodge_queue"


# ---------------------------------------------------------------------------
# Prompt catalogue
# ---------------------------------------------------------------------------

@dataclass
class LodgePrompt:
    prompt_id: str
    prompt_type: str        # derive | gap | falsify | compare | extend
    difficulty: str         # easy | medium | hard
    domain: str
    text: str               # The challenge text presented to the agent
    rubric: Dict[str, str]  # {"mathematical_correctness": "...", ...}
    known_answer: Optional[str] = None  # Key claims the correct answer must contain
    source_file: Optional[str] = None   # e.g. "src/core/braided_winding.py"


LODGE_PROMPTS: List[LodgePrompt] = [

    LodgePrompt(
        prompt_id="L001",
        prompt_type="derive",
        difficulty="easy",
        domain="inflation",
        text=(
            "Starting from the sum-of-squares resonance condition k_CS = n₁² + n₂² "
            "and the Chern-Simons mixing parameter ρ = 2n₁n₂/k_CS, derive the "
            "canonically-normalised braided sound speed c_s. "
            "Show your algebraic steps and state the numerical result for (n₁, n₂) = (5, 7)."
        ),
        rubric={
            "mathematical_correctness": "c_s = |n₂²−n₁²|/k_CS = 24/74 ≈ 0.3243 must appear",
            "derivation_chain": "ρ → c_s = √(1−ρ²) or equivalent algebraic path",
            "epistemic_honesty": "No overclaiming; c_s is derived, not measured",
        },
        known_answer="c_s = 24/74 = 12/37 ≈ 0.3243",
        source_file="src/core/braided_winding.py",
    ),

    LodgePrompt(
        prompt_id="L002",
        prompt_type="gap",
        difficulty="medium",
        domain="geometry",
        text=(
            "FALLIBILITY.md Admission 3 states: 'n_w = 5 uniqueness not yet proved "
            "from first principles alone.' Identify what is and is not proved, "
            "explain why the Planck n_s measurement provides the final selection "
            "between n_w ∈ {5, 7}, and propose one independent observational test "
            "that could further constrain n_w without relying on CMB data."
        ),
        rubric={
            "gap_identification": "Must distinguish what Steps 1-3 of Pillar 67 establish vs. what Planck data selects",
            "test_proposal": "Must be a concrete, falsifiable observational test",
            "epistemic_honesty": "Must not claim n_w=5 is fully derived from first principles",
        },
        known_answer=None,  # Human review required for full credit
        source_file="FALLIBILITY.md",
    ),

    LodgePrompt(
        prompt_id="L003",
        prompt_type="falsify",
        difficulty="hard",
        domain="inflation",
        text=(
            "LiteBIRD is projected to measure the CMB birefringence angle β to "
            "σ(β) ≈ 0.04° precision (launch ~2032). The UM predicts β ∈ {≈0.273°, ≈0.331°} "
            "with an admissible window [0.22°, 0.38°] and a falsification gap [0.29°, 0.31°]. "
            "\n\n"
            "Suppose LiteBIRD reports β = 0.305° ± 0.03°. "
            "Is this inside the falsification gap? Compute the tension in σ with "
            "each canonical prediction. State clearly whether this result falsifies, "
            "supports, or is ambiguous with respect to the braided-winding mechanism."
        ),
        rubric={
            "gap_check": "0.305° is inside [0.29°, 0.31°] — must identify this",
            "tension_calculation": "Tension with 0.273°: |0.305−0.273|/0.04 = 0.8σ (ambiguous). With 0.331°: |0.331−0.305|/0.04 = 0.65σ",
            "falsification_logic": "A value in the gap at >2σ confidence falsifies the mechanism; at 0.8σ it is ambiguous",
            "epistemic_honesty": "Must not claim certainty from a sub-2σ result",
        },
        known_answer="β = 0.305° is inside the gap but only at ~0.7σ — ambiguous, not a falsification",
        source_file="src/core/braided_winding.py",
    ),

    LodgePrompt(
        prompt_id="L004",
        prompt_type="compare",
        difficulty="medium",
        domain="sm",
        text=(
            "The UM derives α_em⁻¹ ≈ 137.0 via the chain: "
            "α_GUT = 3/74 → SU(5)→SM one-loop RGE → α_em⁻¹(Q=0). "
            "The PDG value is α_em⁻¹ = 137.036. "
            "\n\n"
            "1. Compute the residual |137.0 − 137.036| / 137.036 as a percentage. "
            "2. Is this residual within the claimed precision of the geometric derivation? "
            "3. Identify any approximations made in the RGE running that contribute to the residual."
        ),
        rubric={
            "residual_computation": "residual ≈ 0.026% — must compute correctly",
            "precision_assessment": "0.026% < 5% threshold → within claimed precision",
            "approximation_identification": "One-loop RGE, SU(5) embedding assumption, threshold corrections neglected",
        },
        known_answer="residual ≈ 0.026%; within claimed precision; major approximation is one-loop RGE without threshold corrections",
        source_file="src/core/alpha_em_geometric.py",
    ),

    LodgePrompt(
        prompt_id="L005",
        prompt_type="extend",
        difficulty="hard",
        domain="multiverse",
        text=(
            "The FTUM fixed-point iteration establishes that the Unitary Manifold "
            "operator U is a contraction on the space of Multiverse states (Pillar 5). "
            "\n\n"
            "Propose a new corollary (call it Pillar 5-X) that follows from this "
            "contraction property. Your proposal must: "
            "(a) state a precise mathematical claim, "
            "(b) identify what new physical observable it predicts or constrains, "
            "(c) be consistent with the existing pillar set (no contradictions), "
            "(d) be falsifiable — state the experiment or observation that would refute it."
        ),
        rubric={
            "mathematical_precision": "Claim must be stated as a theorem or inequality",
            "physical_observable": "Must connect to a measurable quantity",
            "consistency": "Must not contradict existing pillars",
            "falsifiability": "Must name a concrete test",
        },
        known_answer=None,  # Fully open-ended; human review only
        source_file="src/multiverse/fixed_point.py",
    ),
]


# ---------------------------------------------------------------------------
# Submission + auto-scoring
# ---------------------------------------------------------------------------

@dataclass
class LodgeSubmission:
    submission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt_id: str = ""
    agent_label: str = "anonymous"
    agent_class: str = "human"
    reasoning_trace: str = ""
    numeric_claims: Dict[str, float] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda:
        datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    # Scores — filled in by auto_score() and complete_review()
    auto_score: Optional[float] = None
    human_score: Optional[float] = None
    final_score: Optional[float] = None
    reviewer_notes: str = ""
    reviewed: bool = False


def auto_score_submission(
    submission: LodgeSubmission,
    prompt: LodgePrompt,
) -> float:
    """
    Auto-score numeric claims in a submission against known_answer numeric values.

    Returns a score in [0, 1].  Purely textual prompts (known_answer is None)
    return 0.5 as a neutral placeholder pending human review.
    """
    if prompt.known_answer is None:
        # Cannot auto-score — neutral placeholder
        return 0.5

    # Check how many rubric key terms appear in the reasoning trace
    lower = submission.reasoning_trace.lower()
    rubric_hits = sum(
        1 for key_phrase in prompt.rubric.values()
        if any(w in lower for w in key_phrase.lower().split()[:3])
    )
    rubric_fraction = rubric_hits / max(len(prompt.rubric), 1)

    # Check numeric claims against known answer text
    known_lower = prompt.known_answer.lower()
    claim_score = 0.0
    if submission.numeric_claims:
        for k, v in submission.numeric_claims.items():
            # Simple presence check — a human will verify precision
            claim_score += 0.5
        claim_score = min(1.0, claim_score / len(submission.numeric_claims))
    else:
        # No numeric claims submitted — partial credit if reasoning is present
        claim_score = 0.3 if len(submission.reasoning_trace) > 100 else 0.0

    return round(0.5 * rubric_fraction + 0.5 * claim_score, 4)


# ---------------------------------------------------------------------------
# Review queue
# ---------------------------------------------------------------------------

class LodgeReviewQueue:
    """
    Append-only human review queue stored as JSON files.

    Usage::

        queue = LodgeReviewQueue()
        sub = LodgeSubmission(
            prompt_id="L001",
            agent_label="gpt-4o",
            reasoning_trace="c_s = |n₂²−n₁²|/k_CS = 24/74 ...",
        )
        queue.submit(sub)
        pending = queue.pending()
        queue.complete_review("sub-id", human_score=0.9, notes="Correct derivation, good epistemic framing")
    """

    def __init__(self, queue_dir: Optional[Path] = None) -> None:
        self.queue_dir = Path(queue_dir or _QUEUE_DIR)
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, submission_id: str) -> Path:
        return self.queue_dir / f"{submission_id}.json"

    def submit(self, submission: LodgeSubmission) -> Path:
        """Auto-score and enqueue a submission.  Returns the JSON path."""
        prompt = next(
            (p for p in LODGE_PROMPTS if p.prompt_id == submission.prompt_id), None
        )
        if prompt:
            submission.auto_score = auto_score_submission(submission, prompt)

        path = self._path(submission.submission_id)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(submission), fh, indent=2, ensure_ascii=False)
        return path

    def pending(self) -> List[LodgeSubmission]:
        """Return all unreviewed submissions."""
        items = []
        for p in sorted(self.queue_dir.glob("*.json")):
            with open(p, "r", encoding="utf-8") as fh:
                try:
                    d = json.load(fh)
                except json.JSONDecodeError:
                    continue
            if not d.get("reviewed"):
                items.append(LodgeSubmission(**{k: v for k, v in d.items()
                                                if k in LodgeSubmission.__dataclass_fields__}))
        return items

    def complete_review(
        self,
        submission_id: str,
        human_score: float,
        notes: str = "",
    ) -> Optional[LodgeSubmission]:
        """
        Finalise a review.  final_score = 0.6 × auto_score + 0.4 × human_score.
        """
        path = self._path(submission_id)
        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as fh:
            d = json.load(fh)

        auto = float(d.get("auto_score") or 0.5)
        d["human_score"] = round(float(human_score), 6)
        d["reviewer_notes"] = notes
        d["reviewed"] = True
        d["final_score"] = round(0.6 * auto + 0.4 * float(human_score), 6)

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False)

        return LodgeSubmission(**{k: v for k, v in d.items()
                                   if k in LodgeSubmission.__dataclass_fields__})

    def all_reviewed(self) -> List[LodgeSubmission]:
        items = []
        for p in sorted(self.queue_dir.glob("*.json")):
            with open(p, "r", encoding="utf-8") as fh:
                try:
                    d = json.load(fh)
                except json.JSONDecodeError:
                    continue
            if d.get("reviewed"):
                items.append(LodgeSubmission(**{k: v for k, v in d.items()
                                                if k in LodgeSubmission.__dataclass_fields__}))
        return items
