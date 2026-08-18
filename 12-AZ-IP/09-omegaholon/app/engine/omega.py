# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""
app/engine/omega.py
===================
The Omega Engine — Personal Resonance Calculator.

Applies the mathematical structure of the Unitary Manifold's Omega Synthesis
(omega/omega_synthesis.py) to human life coherence.

KEY MAPPINGS
------------
  Seed constant    Physics               Personal Life
  ─────────────────────────────────────────────────────
  N_W = 5          Primary winding       5 life domains (Pentad)
  N_2 = 7          Braid partner         7-day weekly cycle
  K_CS = 74        Chern-Simons level    Complexity budget (N_W² + N_2²)
  C_S = 12/37      Braided sound speed   Authenticity threshold (≈0.324)
  Ξ_c = 35/74      Consciousness coupling  Life-coherence coupling (≈0.473)

STABILITY FLOOR (from HILSReport in omega_synthesis.py):
  floor(n) = min(1.0, C_S + n × C_S / N_2)
  where n = number of SOLID or CONSTRAINED domains (aligned life pillars)
  Saturates to 1.0 at n ≥ 15 life pillars aligned.

PHI_TRUST THRESHOLD:
  The Pentad decouples if phi_trust < C_S ≈ 0.324.
  Below this threshold, the system loses coherence — authenticity crisis.

OMEGA_SCORE:
  omega_score = stability_floor × average_resonance
  This is the single number summary of your life's current coherence.

DECISION RESONANCE (the creative heart of the Omega Engine):
  Given a decision option with its domain impacts, compute how well it
  resonates with your current life holon. A decision that improves OPEN
  domains and preserves SOLID ones has high resonance.

Theory: ThomasCory Walker-Pearson. Implementation: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional

from .holon import DomainStatus, HolonAudit, LifeDomain

# ---------------------------------------------------------------------------
# Seed constants — directly from omega_synthesis.py
# ---------------------------------------------------------------------------
N_W: int = 5           # 5 life domains
N_2: int = 7           # 7-day weekly cycle / braid partner
K_CS: int = N_W**2 + N_2**2   # = 74 (complexity budget)
C_S: float = float(Fraction(N_2**2 - N_W**2, K_CS))   # = 12/37 ≈ 0.3243
XI_C: float = float(Fraction(N_W * N_2, K_CS))          # = 35/74 ≈ 0.4730

# Phase-shift threshold: n_aligned ≥ 15 → stability saturates at 1.0
HIL_THRESHOLD: int = 15

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def stability_floor(n_aligned: int) -> float:
    """
    Compute the stability floor from n aligned life pillars.

    Directly mirrors HILSReport.stability_floor from omega_synthesis.py:
        floor(n) = min(1.0, C_S + n × C_S / N_2)

    At n=0:  floor = C_S ≈ 0.324  (minimum baseline)
    At n=7:  floor ≈ 0.648
    At n=15: floor = 1.0           (phase-shift threshold; fully stable)
    """
    return min(1.0, C_S + n_aligned * C_S / N_2)


def trust_is_sufficient(phi_trust: float) -> bool:
    """True if phi_trust ≥ C_S (authenticity threshold ≈ 0.324)."""
    return phi_trust >= C_S


def omega_score(n_aligned: int, average_resonance: float) -> float:
    """
    Single-number life coherence score.
    omega_score = stability_floor(n) × average_resonance
    Range: 0.0 (incoherent) → 1.0 (fully coherent).
    """
    return stability_floor(n_aligned) * min(1.0, max(0.0, average_resonance))


def coherence_grade(score: float) -> str:
    """Human-readable grade from omega_score."""
    if score >= 0.90:
        return "Ω — Unified   (all domains resonant)"
    if score >= 0.75:
        return "A — Strong    (most domains solid; minor gaps)"
    if score >= 0.60:
        return "B — Functional (working well; some open work)"
    if score >= 0.40:
        return "C — Fragmented (several domains need attention)"
    if score >= 0.24:
        return "D — Unstable  (significant open domains; rebuild needed)"
    return "F — Crisis    (low coherence; multiple domains need urgent attention)"


# ---------------------------------------------------------------------------
# Decision analysis
# ---------------------------------------------------------------------------

@dataclass
class DecisionOption:
    """One option in a decision being analyzed."""
    name: str
    description: str = ""
    # domain_impact: keys are LifeDomain values, values are -2..+2
    # -2 = significantly harmful  -1 = slightly harmful
    #  0 = neutral   +1 = slightly beneficial  +2 = significantly beneficial
    domain_impacts: dict[str, int] = field(default_factory=dict)
    phi_trust_impact: float = 0.0   # expected change in phi_trust (-0.5..+0.5)
    time_horizon: str = "medium"    # "immediate" / "medium" / "long"
    notes: str = ""

    def resonance_with(self, audit: HolonAudit) -> float:
        """
        Compute decision resonance with the current life holon.

        Logic:
        - Improvements to OPEN domains count most (weight 2.0)
        - Improvements to ESTIMATED domains count (weight 1.5)
        - Harm to SOLID domains is penalized heavily (weight -2.0)
        - Harm to CONSTRAINED domains penalized (weight -1.5)
        - phi_trust_impact scaled by XI_C
        """
        score = 0.0
        max_possible = 0.0

        for domain in LifeDomain:
            impact = self.domain_impacts.get(domain.value, 0)
            d_audit = audit.get_domain(domain)
            if d_audit is None:
                continue

            if impact > 0:
                weight = {
                    DomainStatus.OPEN:        2.0,
                    DomainStatus.ESTIMATED:   1.5,
                    DomainStatus.CONSTRAINED: 1.2,
                    DomainStatus.SOLID:       1.0,
                }[d_audit.status]
            elif impact < 0:
                weight = {
                    DomainStatus.SOLID:       -2.0,
                    DomainStatus.CONSTRAINED: -1.5,
                    DomainStatus.ESTIMATED:   -1.0,
                    DomainStatus.OPEN:        -0.5,
                }[d_audit.status]
            else:
                weight = 0.0

            score += impact * weight
            max_possible += 2.0 * max(abs(weight), 1.0)

        # phi_trust component (scaled by consciousness coupling)
        score += self.phi_trust_impact * XI_C * 4.0
        max_possible += 4.0

        if max_possible == 0:
            return 0.5

        # Normalize to [0, 1]
        normalized = (score / max_possible + 1.0) / 2.0
        return max(0.0, min(1.0, normalized))

    def to_dict(self, audit: Optional[HolonAudit] = None) -> dict:
        d = {
            "name": self.name,
            "description": self.description,
            "domain_impacts": self.domain_impacts,
            "phi_trust_impact": self.phi_trust_impact,
            "time_horizon": self.time_horizon,
            "notes": self.notes,
        }
        if audit is not None:
            d["resonance"] = round(self.resonance_with(audit), 4)
        return d


# ---------------------------------------------------------------------------
# Daily Pulse
# ---------------------------------------------------------------------------

@dataclass
class DailyPulse:
    """A daily check-in across the 5 domains."""
    date: str = ""
    scores: dict[str, float] = field(default_factory=dict)   # domain → 0–10
    notes: dict[str, str] = field(default_factory=dict)      # domain → text

    def set(self, domain: LifeDomain, score: float, note: str = "") -> None:
        self.scores[domain.value] = min(10.0, max(0.0, float(score)))
        self.notes[domain.value] = note

    @property
    def overall(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)

    @property
    def phi_trust_estimate(self) -> float:
        """Estimate phi_trust from daily scores (normalized to 0–1)."""
        return self.overall / 10.0

    @property
    def n_aligned(self) -> int:
        """Count domains with score ≥ 7 (i.e., functioning well)."""
        return sum(1 for v in self.scores.values() if v >= 7.0)

    @property
    def daily_omega(self) -> float:
        """Quick daily omega score from pulse alone."""
        return omega_score(self.n_aligned, self.phi_trust_estimate)

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "scores": self.scores,
            "notes": self.notes,
            "overall": round(self.overall, 2),
            "phi_trust_estimate": round(self.phi_trust_estimate, 4),
            "n_aligned": self.n_aligned,
            "daily_omega": round(self.daily_omega, 4),
        }


# ---------------------------------------------------------------------------
# Full Omega Report
# ---------------------------------------------------------------------------

@dataclass
class OmegaPersonalReport:
    """
    The complete personal Omega Report — mirrors OmegaReport from omega_synthesis.py.

    Fields
    ------
    audit           Life holon audit (5 domains)
    pulse           Today's daily pulse
    decision_options  Decisions being analyzed
    """
    audit: Optional[HolonAudit] = None
    pulse: Optional[DailyPulse] = None
    decision_options: list[DecisionOption] = field(default_factory=list)

    @property
    def n_aligned(self) -> int:
        """n_aligned = n_solid + n_constrained from holon audit."""
        if self.audit is None:
            return self.pulse.n_aligned if self.pulse else 0
        return self.audit.n_solid + self.audit.n_constrained

    @property
    def phi_trust(self) -> float:
        if self.audit is not None:
            return self.audit.average_phi_trust
        if self.pulse is not None:
            return self.pulse.phi_trust_estimate
        return 0.5

    @property
    def resonance(self) -> float:
        if self.audit is not None:
            return self.audit.average_resonance
        if self.pulse is not None:
            return self.pulse.phi_trust_estimate
        return 0.5

    @property
    def stability(self) -> float:
        return stability_floor(self.n_aligned)

    @property
    def score(self) -> float:
        return omega_score(self.n_aligned, self.resonance)

    @property
    def grade(self) -> str:
        return coherence_grade(self.score)

    @property
    def trust_ok(self) -> bool:
        return trust_is_sufficient(self.phi_trust)

    def falsifiable_commitments(self) -> list[dict]:
        """Extract falsifiable commitments from the audit's falsifiers."""
        result = []
        if self.audit is None:
            return result
        for domain_audit in self.audit.domains.values():
            for f in domain_audit.falsifiers:
                result.append({
                    "domain": domain_audit.domain.value,
                    "commitment": f,
                })
        return result

    def render_report(self) -> str:
        """Full Omega Personal Report — mirrors engine.compute_all().summary()."""
        divider = "═" * 64
        lines = [
            divider,
            "  OMEGA PERSONAL REPORT",
            divider,
            "",
            f"  Ω Score:         {self.score:.4f}  ({self.grade})",
            f"  Stability floor: {self.stability:.4f}  (n_aligned={self.n_aligned})",
            f"  φ_trust:         {self.phi_trust:.4f}  ({'✅ sufficient' if self.trust_ok else '⚠ BELOW THRESHOLD — authenticity gap'})",
            f"  Resonance:       {self.resonance:.4f}",
            "",
            f"  Seed constants (physics → life):",
            f"    N_W  = {N_W}   → 5 life domains",
            f"    N_2  = {N_2}   → 7-day cycle",
            f"    K_CS = {K_CS}  → complexity budget",
            f"    C_S  = {C_S:.5f} → authenticity threshold",
            f"    Ξ_c  = {XI_C:.5f} → coherence coupling",
            "",
        ]
        if self.audit is not None:
            lines.append("  LIFE HOLON STATUS")
            lines.append("  " + "─" * 40)
            for d in self.audit.domains.values():
                lines.append(
                    f"    {d.status.emoji} [{d.status.value:11}] "
                    f"{d.domain.value:<24} φ={d.phi_trust:.2f}  R={d.resonance_score:.3f}"
                )
            lines += [
                "",
                f"    SOLID: {self.audit.n_solid} | CONSTRAINED: {self.audit.n_constrained} | "
                f"ESTIMATED: {self.audit.n_estimated} | OPEN: {self.audit.n_open}",
                "",
            ]
        if self.pulse is not None:
            lines.append("  TODAY'S PULSE")
            lines.append("  " + "─" * 40)
            for domain, score in self.pulse.scores.items():
                bar = "█" * int(score) + "░" * (10 - int(score))
                lines.append(f"    {domain:<26} {bar} {score:.1f}/10")
            lines += [
                f"    Overall: {self.pulse.overall:.1f}/10  Daily Ω: {self.pulse.daily_omega:.4f}",
                "",
            ]
        if self.decision_options and self.audit is not None:
            lines.append("  DECISION RESONANCE RANKING")
            lines.append("  " + "─" * 40)
            ranked = sorted(
                self.decision_options,
                key=lambda o: o.resonance_with(self.audit),
                reverse=True,
            )
            for i, opt in enumerate(ranked, 1):
                r = opt.resonance_with(self.audit)
                bar = "█" * int(r * 10) + "░" * (10 - int(r * 10))
                lines.append(f"    [{i}] {bar} {r:.3f}  {opt.name}")
                if opt.description:
                    lines.append(f"         {opt.description}")
            lines.append("")
        falsifiers = self.falsifiable_commitments()
        if falsifiers:
            lines.append("  FALSIFIABLE COMMITMENTS")
            lines.append("  " + "─" * 40)
            for i, f in enumerate(falsifiers, 1):
                lines.append(f"    [{i}] [{f['domain']}] {f['commitment']}")
            lines.append("")
        lines += [
            divider,
            "  Your life is a holon — a complete system and a part of something larger.",
            "  The Omega Score is an honest mirror, not a judgment.",
            divider,
        ]
        return "\n".join(lines)
