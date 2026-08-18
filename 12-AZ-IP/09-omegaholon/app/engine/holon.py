# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""
app/engine/holon.py
===================
The Holon Engine — Life-Domain Epistemic Audit.

A holon (Arthur Koestler, 1967) is something that is simultaneously a
whole in itself and a part of a larger whole. Your life is a holon:
a complete system, and a part of family / community / universe.

This engine applies the Unitary Manifold's SM-parameter completeness
framework (holon_zero.py) to a human life. Each life domain is audited
for epistemic status:

    SOLID       — foundations clear; well-established; actively maintained
    CONSTRAINED — working within real limits; acknowledged tradeoffs
    ESTIMATED   — roughly on track; needs more data or attention
    OPEN        — unresolved; broken; requires urgent attention

The 5 Life Domains (Pentad mapping):
    BODY        — Ψ_brain  : physical health, sleep, nutrition, movement
    MIND        — Ψ_human  : mental/emotional state, learning, clarity
    WORK        — Ψ_AI     : purpose, career, output, creative contribution
    RELATIONS   — Ψ_trust  : relationships, community, integrity, trust
    RESOURCES   — Ψ_univ   : finances, environment, material stability

Theory: ThomasCory Walker-Pearson. Implementation: GitHub Copilot (AI).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DomainStatus(Enum):
    """Epistemic status of a life domain — mirrors holon_zero.py parameter status."""
    SOLID       = "SOLID"       # Well-founded; actively maintained
    CONSTRAINED = "CONSTRAINED" # Working within real limits
    ESTIMATED   = "ESTIMATED"   # Roughly right; needs attention
    OPEN        = "OPEN"        # Unresolved; broken; urgent

    @property
    def weight(self) -> float:
        return {
            DomainStatus.SOLID:       1.00,
            DomainStatus.CONSTRAINED: 0.70,
            DomainStatus.ESTIMATED:   0.40,
            DomainStatus.OPEN:        0.10,
        }[self]

    @property
    def emoji(self) -> str:
        return {
            DomainStatus.SOLID:       "✅",
            DomainStatus.CONSTRAINED: "⚙️",
            DomainStatus.ESTIMATED:   "〰️",
            DomainStatus.OPEN:        "🔓",
        }[self]


class LifeDomain(Enum):
    """The five life domains — mirrors the Unitary Pentad's five bodies."""
    BODY      = "Body & Health"
    MIND      = "Mind & Emotion"
    WORK      = "Work & Purpose"
    RELATIONS = "Relationships & Trust"
    RESOURCES = "Resources & Environment"

    @property
    def pentad_body(self) -> str:
        return {
            LifeDomain.BODY:      "Ψ_brain (neural/physical substrate)",
            LifeDomain.MIND:      "Ψ_human (conscious agency)",
            LifeDomain.WORK:      "Ψ_AI (purposive output)",
            LifeDomain.RELATIONS: "Ψ_trust (coupling field)",
            LifeDomain.RESOURCES: "Ψ_univ (universal context)",
        }[self]

    @property
    def daily_questions(self) -> list[str]:
        return {
            LifeDomain.BODY: [
                "How is your energy level today? (1–10)",
                "Did you sleep well last night?",
                "Did you move your body today?",
            ],
            LifeDomain.MIND: [
                "How is your emotional clarity? (1–10)",
                "What's your dominant mood or mental state right now?",
                "Are you learning anything this week?",
            ],
            LifeDomain.WORK: [
                "How aligned is your work with your purpose today? (1–10)",
                "What did you produce or create this week?",
                "What is the one thing you must complete?",
            ],
            LifeDomain.RELATIONS: [
                "How is your trust level with the people closest to you? (1–10)",
                "Did you communicate authentically today?",
                "Who do you need to reach out to?",
            ],
            LifeDomain.RESOURCES: [
                "Is your financial situation stable? (1–10)",
                "Is your environment supporting or draining you?",
                "What resource constraint needs attention?",
            ],
        }[self]


@dataclass
class DomainAudit:
    """Audit record for one life domain."""
    domain: LifeDomain
    status: DomainStatus = DomainStatus.ESTIMATED
    phi_trust: float = 0.7          # Authenticity/integrity level for this domain (0–1)
    description: str = ""           # What is the current state?
    foundations: str = ""           # What this domain is built on
    constraints: str = ""           # Real limits being worked within
    open_gaps: list[str] = field(default_factory=list)    # Unresolved issues
    falsifiers: list[str] = field(default_factory=list)   # What would prove strategy wrong
    notes: str = ""

    @property
    def resonance_score(self) -> float:
        """Domain resonance: status_weight × phi_trust"""
        return self.status.weight * min(1.0, max(0.0, self.phi_trust))

    def to_dict(self) -> dict:
        return {
            "domain": self.domain.value,
            "status": self.status.value,
            "phi_trust": self.phi_trust,
            "description": self.description,
            "foundations": self.foundations,
            "constraints": self.constraints,
            "open_gaps": self.open_gaps,
            "falsifiers": self.falsifiers,
            "notes": self.notes,
            "resonance_score": round(self.resonance_score, 4),
        }


@dataclass
class HolonAudit:
    """
    Complete life holon audit — all five domains.

    Like the SM parameter completeness certificate in holon_zero.py,
    this provides an honest epistemic accounting of your entire life system.
    """
    name: str = ""
    domains: dict[str, DomainAudit] = field(default_factory=dict)

    def set_domain(self, domain: LifeDomain, status: DomainStatus,
                   phi_trust: float = 0.7, description: str = "",
                   foundations: str = "", constraints: str = "",
                   open_gaps: list[str] | None = None,
                   falsifiers: list[str] | None = None) -> DomainAudit:
        audit = DomainAudit(
            domain=domain,
            status=status,
            phi_trust=min(1.0, max(0.0, phi_trust)),
            description=description,
            foundations=foundations,
            constraints=constraints,
            open_gaps=open_gaps or [],
            falsifiers=falsifiers or [],
        )
        self.domains[domain.value] = audit
        return audit

    def get_domain(self, domain: LifeDomain) -> Optional[DomainAudit]:
        return self.domains.get(domain.value)

    @property
    def n_solid(self) -> int:
        return sum(1 for d in self.domains.values() if d.status == DomainStatus.SOLID)

    @property
    def n_constrained(self) -> int:
        return sum(1 for d in self.domains.values() if d.status == DomainStatus.CONSTRAINED)

    @property
    def n_estimated(self) -> int:
        return sum(1 for d in self.domains.values() if d.status == DomainStatus.ESTIMATED)

    @property
    def n_open(self) -> int:
        return sum(1 for d in self.domains.values() if d.status == DomainStatus.OPEN)

    @property
    def average_phi_trust(self) -> float:
        if not self.domains:
            return 0.0
        return sum(d.phi_trust for d in self.domains.values()) / len(self.domains)

    @property
    def average_resonance(self) -> float:
        if not self.domains:
            return 0.0
        return sum(d.resonance_score for d in self.domains.values()) / len(self.domains)

    def completeness_certificate(self) -> dict:
        """Return the holon completeness certificate — mirrors holon_zero_certificate()."""
        return {
            "name": self.name,
            "total_domains": len(LifeDomain),
            "audited": len(self.domains),
            "n_solid": self.n_solid,
            "n_constrained": self.n_constrained,
            "n_estimated": self.n_estimated,
            "n_open": self.n_open,
            "average_phi_trust": round(self.average_phi_trust, 4),
            "average_resonance": round(self.average_resonance, 4),
            "domains": {k: v.to_dict() for k, v in self.domains.items()},
        }

    def render_certificate(self) -> str:
        """Human-readable completeness certificate."""
        c = self.completeness_certificate()
        lines = [
            "=" * 64,
            f"  LIFE HOLON COMPLETENESS CERTIFICATE — {self.name or 'Anonymous'}",
            "=" * 64,
            "",
            f"  Domains audited: {c['audited']} / {c['total_domains']}",
            f"  ✅ SOLID:       {c['n_solid']}   (well-founded, maintained)",
            f"  ⚙️  CONSTRAINED: {c['n_constrained']}   (working within limits)",
            f"  〰️  ESTIMATED:   {c['n_estimated']}   (roughly right, needs attention)",
            f"  🔓 OPEN:        {c['n_open']}   (unresolved, urgent)",
            "",
            f"  Avg φ_trust:    {c['average_phi_trust']:.3f}",
            f"  Avg resonance:  {c['average_resonance']:.3f}",
            "",
        ]
        for domain_name, d in c["domains"].items():
            status = d["status"]
            emoji = DomainStatus(status).emoji
            lines.append(f"  {emoji} [{status:11}] {domain_name}")
            if d["description"]:
                lines.append(f"      State: {d['description']}")
            if d["open_gaps"]:
                for gap in d["open_gaps"]:
                    lines.append(f"      🔓 Gap: {gap}")
            if d["falsifiers"]:
                for f_ in d["falsifiers"]:
                    lines.append(f"      🔬 Falsifier: {f_}")
        lines += ["", "=" * 64]
        return "\n".join(lines)
