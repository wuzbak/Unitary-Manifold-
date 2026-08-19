# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
oracle/engine/integrity.py
==========================
Governance and accountability audit engine — EIGE-aligned.

Applies the mathematical integrity framework of the Election Integrity
Governance Engine (EIGE, Product 03) to any institution, policy, or
governance system.

Seven audit dimensions map to the seven EIGE attack-detection categories.
Each dimension is scored 0.0–1.0.  The overall integrity score and a
chain-of-custody index are computed from the five seed constants.

Theory: ThomasCory Walker-Pearson.
Code:   GitHub Copilot (AI).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import math

from oracle.engine.constants import (
    K_CS, C_S_F, XI_C_F,
    GOV_INTEGRITY_THRESHOLD, GOV_TRANSPARENCY_IDEAL, GOV_FREEDOM_FLOOR,
)


# ── Audit dimensions ──────────────────────────────────────────────────────────

AUDIT_DIMENSIONS = [
    ("Transparency",      "Are processes, decisions, and data publicly visible?"),
    ("Sequence Integrity","Is the chain of events tamper-evident and ordered?"),
    ("Participation",     "Do all stakeholders have meaningful access and voice?"),
    ("Accountability",    "Are failures detected and attributed without ambiguity?"),
    ("Resilience",        "Can the system survive targeted disruption or failure?"),
    ("Epistemic Honesty", "Are uncertainty and error acknowledged openly?"),
    ("Freedom Floor",     "Is the minimum participation threshold guaranteed?"),
]

DIMENSION_KEYS = [d[0] for d in AUDIT_DIMENSIONS]


@dataclass
class AuditDimension:
    """One governance audit dimension."""
    key: str
    description: str
    score: float                  # 0.0–1.0
    evidence: str = ""            # what supports this score
    concern: str = ""             # specific issue or gap

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"score must be in [0, 1]; got {self.score}")

    @property
    def status(self) -> str:
        if self.score >= 0.85:  return "STRONG"
        if self.score >= 0.70:  return "ADEQUATE"
        if self.score >= 0.50:  return "WEAK"
        return "FAILING"

    @property
    def symbol(self) -> str:
        return {"STRONG": "✅", "ADEQUATE": "⚙️", "WEAK": "⚠️", "FAILING": "🚨"}[self.status]


@dataclass
class IntegrityAudit:
    """
    Full governance integrity audit for any institution or policy.

    Mathematics:
        integrity_score = Σ(dimension_score × weight_i) / Σ(weight_i)

    Weights reflect the CS-level ordering from EIGE:
        Transparency and Participation weighted by K_CS/74 = 1.0 (base)
        Sequence Integrity weighted by C_S_F (tamper-detection emphasis)
        Freedom Floor weighted by 2.0 (kill-switch — non-negotiable)
    """
    system_name: str
    system_type: str
    dimensions: list[AuditDimension]
    context: str = ""

    _WEIGHTS: dict[str, float] = field(default_factory=lambda: {
        "Transparency":       1.0,
        "Sequence Integrity": C_S_F,
        "Participation":      1.0,
        "Accountability":     1.0,
        "Resilience":         C_S_F,
        "Epistemic Honesty":  1.0,
        "Freedom Floor":      2.0,    # non-negotiable — doubled weight
    })

    def __post_init__(self) -> None:
        if len(self.dimensions) != len(AUDIT_DIMENSIONS):
            raise ValueError(
                f"IntegrityAudit requires {len(AUDIT_DIMENSIONS)} dimensions; "
                f"got {len(self.dimensions)}"
            )

    @property
    def integrity_score(self) -> float:
        weights = self._WEIGHTS
        total_w = sum(weights.get(d.key, 1.0) for d in self.dimensions)
        weighted = sum(d.score * weights.get(d.key, 1.0) for d in self.dimensions)
        return weighted / total_w if total_w > 0 else 0.0

    @property
    def chain_of_custody_index(self) -> float:
        """
        Rolling-hash analogue: product of sequence-dependent dimension scores,
        normalized by k_CS.  Measures the overall tamper-resistance of the
        governance chain.
        """
        product = 1.0
        for d in self.dimensions:
            product *= max(d.score, 1e-6)
        return product ** (1.0 / len(self.dimensions))   # geometric mean

    @property
    def freedom_floor_met(self) -> bool:
        ff_dim = next((d for d in self.dimensions if d.key == "Freedom Floor"), None)
        return ff_dim is not None and ff_dim.score >= GOV_FREEDOM_FLOOR

    @property
    def transparency_score(self) -> float:
        tr = next((d for d in self.dimensions if d.key == "Transparency"), None)
        return tr.score if tr else 0.0

    @property
    def integrity_grade(self) -> str:
        s = self.integrity_score
        if s >= 0.90: return "EXEMPLARY"
        if s >= 0.80: return "STRONG"
        if s >= 0.70: return "ADEQUATE"
        if s >= 0.55: return "WEAK"
        if s >= 0.40: return "FAILING"
        return "CRITICAL"

    @property
    def failing_dimensions(self) -> list[AuditDimension]:
        return [d for d in self.dimensions if d.status in ("WEAK", "FAILING")]

    def summary(self) -> str:
        lines = [
            f"╔══════════════════════════════════════════════════════════════╗",
            f"║  GOVERNANCE AUDIT — {self.system_name[:42]:<42}  ║",
            f"╚══════════════════════════════════════════════════════════════╝",
            f"",
            f"  System type          : {self.system_type}",
            f"  Integrity score      : {self.integrity_score:.4f}  [{self.integrity_grade}]",
            f"  Chain-of-custody idx : {self.chain_of_custody_index:.4f}",
            f"  Transparency         : {self.transparency_score:.4f}",
            f"  Freedom Floor met    : {'YES ✅' if self.freedom_floor_met else 'NO 🚨'}",
            f"",
            f"  DIMENSION BREAKDOWN:",
        ]
        for d in self.dimensions:
            bar_len = int(d.score * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(
                f"    {d.symbol} {d.key:<22}  [{bar}]  {d.score:.3f}  [{d.status}]"
            )
            if d.concern:
                lines.append(f"       ↳ Concern: {d.concern}")

        failing = self.failing_dimensions
        if failing:
            lines.append("")
            lines.append("  🚨 DIMENSIONS REQUIRING INTERVENTION:")
            for d in failing:
                lines.append(f"    • {d.key}: {d.concern or d.description}")

        lines.append("")
        lines.append(
            f"  Target: integrity ≥ {GOV_INTEGRITY_THRESHOLD:.2f} (adequate); "
            f"≥ {GOV_TRANSPARENCY_IDEAL:.2f} (exemplary)."
        )
        lines.append(
            f"  Freedom Floor threshold: {GOV_FREEDOM_FLOOR:.4f} = C_S (braided sound speed)."
        )
        return "\n".join(lines)
