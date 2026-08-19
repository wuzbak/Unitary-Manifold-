# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
oracle/engine/resonance.py
==========================
Decision Resonance Engine.

Evaluates how well each option in a decision resonates with the current
state of a system (Pentad or free-form).  Mathematics mirrors the
OmegaHolon Decision Oracle (Product 09) extended with the full five-body
coupling tensor.

Theory: ThomasCory Walker-Pearson.
Code:   GitHub Copilot (AI).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from oracle.engine.constants import (
    N_W, XI_C_F, C_S_F, IMPACT_MULTIPLIERS, STATUS_WEIGHTS,
)
from oracle.engine.pentad import PentadModel, PentadBody


# ── Impact specification ──────────────────────────────────────────────────────

@dataclass
class BodyImpact:
    """How one decision option affects one Pentad body."""
    body_label: str
    direction: str       # "improve" | "harm" | "neutral"
    magnitude: float     # 0.0 – 2.0

    def __post_init__(self) -> None:
        self.direction = self.direction.lower()
        if self.direction not in ("improve", "harm", "neutral"):
            raise ValueError(f"direction must be improve|harm|neutral; got '{self.direction}'")
        if not (0.0 <= self.magnitude <= 2.0):
            raise ValueError(f"magnitude must be in [0, 2]; got {self.magnitude}")


@dataclass
class DecisionOption:
    """One option in a multi-option decision."""
    name: str
    description: str = ""
    body_impacts: list[BodyImpact] = field(default_factory=list)
    phi_trust_impact: float = 0.0   # expected change in authenticity  (-1 to +1)

    def __post_init__(self) -> None:
        if not (-1.0 <= self.phi_trust_impact <= 1.0):
            raise ValueError(
                f"phi_trust_impact must be in [-1, 1]; got {self.phi_trust_impact}"
            )


# ── Resonance computation ─────────────────────────────────────────────────────

def compute_option_resonance(
    option: DecisionOption,
    pentad: PentadModel,
) -> float:
    """
    Compute the resonance score for one decision option against a Pentad state.

    resonance(option) =
        weighted_sum(body_impacts × status_weight) + Ξ_c × phi_trust_impact

    Status weights for impacts:
        Improving an OPEN body:        +2.0 × magnitude  (highest priority)
        Improving an ESTIMATED body:   +1.5 × magnitude
        Improving a CONSTRAINED body:  +1.0 × magnitude
        Improving a SOLID body:        +0.5 × magnitude
        Harming a SOLID body:          −2.0 × magnitude  (highest penalty)
        Harming a CONSTRAINED body:    −1.5 × magnitude
        Harming an ESTIMATED body:     −0.5 × magnitude
        Harming an OPEN body:          −0.2 × magnitude

    Returns a float (can be negative; higher is better).
    """
    body_map = {b.label: b for b in pentad.bodies}
    total = 0.0
    for impact in option.body_impacts:
        body = body_map.get(impact.body_label)
        if body is None:
            continue
        if impact.direction == "neutral":
            continue
        key = (body.epistemic_status, impact.direction)
        multiplier = IMPACT_MULTIPLIERS.get(key, 0.0)
        total += multiplier * impact.magnitude

    total += XI_C_F * option.phi_trust_impact
    return total


@dataclass
class DecisionAnalysis:
    """Complete multi-option decision analysis against a Pentad state."""
    question: str
    pentad: PentadModel
    options: list[DecisionOption]

    def __post_init__(self) -> None:
        if len(self.options) < 2:
            raise ValueError("A decision analysis requires at least 2 options.")

    @property
    def ranked_options(self) -> list[tuple[float, DecisionOption]]:
        scored = [(compute_option_resonance(o, self.pentad), o) for o in self.options]
        return sorted(scored, reverse=True)

    def best_option(self) -> DecisionOption:
        return self.ranked_options[0][1]

    def summary(self) -> str:
        ranked = self.ranked_options
        max_score = max(abs(s) for s, _ in ranked) or 1.0

        lines = [
            f"╔══════════════════════════════════════════════════════════════╗",
            f"║  DECISION ORACLE                                             ║",
            f"╚══════════════════════════════════════════════════════════════╝",
            f"",
            f"  Question : {self.question}",
            f"  System   : {self.pentad.system_name}",
            f"",
            f"  OPTION RESONANCE RANKING:",
        ]
        for rank, (score, opt) in enumerate(ranked, 1):
            bar_len = int(((score + max_score) / (2 * max_score)) * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(
                f"    #{rank}  {opt.name:<28}  [{bar}]  {score:+.3f}"
            )
            if opt.description:
                lines.append(f"         {opt.description}")

        winner = ranked[0][1]
        lines.extend([
            f"",
            f"  ✅ HIGHEST RESONANCE: {winner.name}",
            f"     This option best fits the current system state:",
            f"     it prioritizes repairing OPEN bodies and avoids harming SOLID ones.",
            f"",
            f"  Mathematics: resonance = Σ(impact_multiplier × magnitude) + Ξ_c × Δφ_trust",
            f"  where Ξ_c = {XI_C_F:.5f}  (consciousness coupling constant).",
        ])
        return "\n".join(lines)
