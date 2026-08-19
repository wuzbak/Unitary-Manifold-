# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""
app/core/investigator.py
========================
AXIOM Investigative Journalism Engine — core logic.

The engine enforces the AxiomZero investigative methodology:
  - Document is primary reality.
  - Every claim is attached to a source with a tier classification.
  - Confidence scoring: CONFIRMED / CORROBORATED / ALLEGED / UNVERIFIED.
  - Legal risk flags: libel exposure, whistleblower considerations.
  - Human review gate: no output is presented as ready to publish.

Theory, methodology, scientific direction: ThomasCory Walker-Pearson / AxiomZero.
Implementation: GitHub Copilot (AI).
"""
from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SourceTier(Enum):
    """Source reliability classification.

    Tier 1 — Primary government / legal / official records (highest weight).
    Tier 2 — Established journalism, academic, on-record institutional.
    Tier 3 — Statements, press releases, social media, anonymous tips.
    Unclassified — Not yet evaluated.
    """
    TIER_1 = 1  # Primary records: court filings, regulatory docs, FOIA, legislation
    TIER_2 = 2  # Established journalism, academic papers, on-record officials
    TIER_3 = 3  # Press releases, social media, anonymous tips, secondary reports
    UNCLASSIFIED = 0


TIER_LABELS = {
    SourceTier.TIER_1:       "Tier 1 — Primary Record (court/regulatory/FOIA)",
    SourceTier.TIER_2:       "Tier 2 — Established/On-Record",
    SourceTier.TIER_3:       "Tier 3 — Secondary/Unverified",
    SourceTier.UNCLASSIFIED: "Unclassified",
}

TIER_WEIGHT = {
    SourceTier.TIER_1:       1.00,
    SourceTier.TIER_2:       0.65,
    SourceTier.TIER_3:       0.25,
    SourceTier.UNCLASSIFIED: 0.10,
}


class ConfidenceLevel(Enum):
    """Factual confidence classification for a claim."""
    CONFIRMED    = "CONFIRMED"     # Multiple Tier-1 sources; independently verifiable
    CORROBORATED = "CORROBORATED"  # Consistent across Tier 1 + Tier 2
    ALLEGED      = "ALLEGED"       # One or more sources, not fully corroborated
    UNVERIFIED   = "UNVERIFIED"    # Single source, low-tier, or contradicted


CONFIDENCE_WEIGHT = {
    ConfidenceLevel.CONFIRMED:    1.0,
    ConfidenceLevel.CORROBORATED: 0.75,
    ConfidenceLevel.ALLEGED:      0.40,
    ConfidenceLevel.UNVERIFIED:   0.15,
}


class LegalRisk(Enum):
    """Legal risk categories for a claim."""
    NONE            = "NONE"
    LIBEL_EXPOSURE  = "LIBEL_EXPOSURE"
    SOURCE_PROTECT  = "SOURCE_PROTECT"
    WHISTLEBLOWER   = "WHISTLEBLOWER"
    PRIVACY         = "PRIVACY"
    NATIONAL_SEC    = "NATIONAL_SECURITY"


class EntityType(Enum):
    PERSON       = "Person"
    ORGANIZATION = "Organization"
    GOVERNMENT   = "Government Agency"
    CORPORATE    = "Corporate Structure"
    LOCATION     = "Location"
    FINANCIAL    = "Financial Instrument"
    OTHER        = "Other"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Entity:
    name: str
    entity_type: EntityType = EntityType.OTHER
    description: str = ""
    stated_position: str = ""
    contradictions: list[str] = field(default_factory=list)
    notes: str = ""

    def add_contradiction(self, contradiction: str) -> None:
        self.contradictions.append(contradiction)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.entity_type.value,
            "description": self.description,
            "stated_position": self.stated_position,
            "contradictions": self.contradictions,
            "notes": self.notes,
        }


@dataclass
class Source:
    title: str
    tier: SourceTier = SourceTier.UNCLASSIFIED
    source_type: str = ""        # e.g. "Court filing", "FOIA document", "News article"
    url_or_ref: str = ""
    date: str = ""
    excerpt: str = ""
    notes: str = ""

    @property
    def weight(self) -> float:
        return TIER_WEIGHT[self.tier]

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "tier": TIER_LABELS[self.tier],
            "source_type": self.source_type,
            "url_or_ref": self.url_or_ref,
            "date": self.date,
            "excerpt": self.excerpt,
            "notes": self.notes,
        }


@dataclass
class Claim:
    statement: str
    sources: list[Source] = field(default_factory=list)
    entities_involved: list[str] = field(default_factory=list)
    legal_risks: list[LegalRisk] = field(default_factory=list)
    notes: str = ""

    @property
    def confidence(self) -> ConfidenceLevel:
        """Auto-score confidence from attached sources."""
        if not self.sources:
            return ConfidenceLevel.UNVERIFIED
        tier1_count = sum(1 for s in self.sources if s.tier == SourceTier.TIER_1)
        tier2_count = sum(1 for s in self.sources if s.tier == SourceTier.TIER_2)
        if tier1_count >= 2:
            return ConfidenceLevel.CONFIRMED
        if tier1_count >= 1 and tier2_count >= 1:
            return ConfidenceLevel.CORROBORATED
        if tier1_count >= 1 or tier2_count >= 2:
            return ConfidenceLevel.ALLEGED
        return ConfidenceLevel.UNVERIFIED

    @property
    def legal_risk_label(self) -> str:
        if not self.legal_risks or LegalRisk.NONE in self.legal_risks:
            return "None identified"
        return " | ".join(r.value for r in self.legal_risks if r != LegalRisk.NONE)

    def to_dict(self) -> dict:
        return {
            "statement": self.statement,
            "confidence": self.confidence.value,
            "sources": [s.to_dict() for s in self.sources],
            "entities_involved": self.entities_involved,
            "legal_risks": self.legal_risk_label,
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# Investigation
# ---------------------------------------------------------------------------

@dataclass
class Investigation:
    title: str
    lead: str
    journalist: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    status: str = "Active"
    entities: list[Entity] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    notes: str = ""

    # --- entity helpers ---

    def add_entity(self, name: str, entity_type: EntityType = EntityType.OTHER,
                   description: str = "", stated_position: str = "") -> Entity:
        e = Entity(name, entity_type, description, stated_position)
        self.entities.append(e)
        return e

    def get_entity(self, name: str) -> Optional[Entity]:
        return next((e for e in self.entities if e.name.lower() == name.lower()), None)

    # --- source helpers ---

    def add_source(self, title: str, tier: SourceTier = SourceTier.UNCLASSIFIED,
                   source_type: str = "", url_or_ref: str = "", date: str = "",
                   excerpt: str = "") -> Source:
        s = Source(title, tier, source_type, url_or_ref, date, excerpt)
        self.sources.append(s)
        return s

    # --- claim helpers ---

    def add_claim(self, statement: str, source_titles: list[str] | None = None,
                  entities: list[str] | None = None,
                  legal_risks: list[LegalRisk] | None = None) -> Claim:
        # Resolve sources by title
        resolved: list[Source] = []
        if source_titles:
            for t in source_titles:
                match = next((s for s in self.sources if t.lower() in s.title.lower()), None)
                if match:
                    resolved.append(match)
        c = Claim(
            statement=statement,
            sources=resolved,
            entities_involved=entities or [],
            legal_risks=legal_risks or [LegalRisk.NONE],
        )
        self.claims.append(c)
        return c

    # --- scoring ---

    @property
    def overall_confidence_score(self) -> float:
        """Weighted average confidence across all claims (0.0–1.0)."""
        if not self.claims:
            return 0.0
        return sum(CONFIDENCE_WEIGHT[c.confidence] for c in self.claims) / len(self.claims)

    @property
    def source_quality_score(self) -> float:
        """Average source weight across all sources (0.0–1.0)."""
        if not self.sources:
            return 0.0
        return sum(s.weight for s in self.sources) / len(self.sources)

    @property
    def has_legal_flags(self) -> bool:
        return any(
            LegalRisk.NONE not in c.legal_risks
            for c in self.claims
            if c.legal_risks
        )

    # --- brief generation ---

    def generate_brief(self) -> str:
        """Generate a structured investigative brief for human review."""
        divider = "=" * 72
        lines: list[str] = [
            divider,
            f"  AXIOM INVESTIGATIVE BRIEF — {self.title.upper()}",
            f"  Prepared: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Status: {self.status}",
            f"  Journalist: {self.journalist or 'Not specified'}",
            divider,
            "",
            "INVESTIGATIVE LEAD",
            "-" * 40,
            textwrap.fill(self.lead, 70),
            "",
            "ENTITIES IDENTIFIED",
            "-" * 40,
        ]
        if self.entities:
            for e in self.entities:
                lines.append(f"  [{e.entity_type.value}] {e.name}")
                if e.description:
                    lines.append(f"    Description: {e.description}")
                if e.stated_position:
                    lines.append(f"    Stated position: {e.stated_position}")
                if e.contradictions:
                    for c in e.contradictions:
                        lines.append(f"    ⚠ Contradiction: {c}")
        else:
            lines.append("  None recorded.")
        lines += [
            "",
            f"SOURCES ({len(self.sources)} total | quality score: {self.source_quality_score:.2f})",
            "-" * 40,
        ]
        if self.sources:
            for i, s in enumerate(self.sources, 1):
                lines.append(f"  [{i}] {TIER_LABELS[s.tier]}")
                lines.append(f"      {s.title}")
                if s.url_or_ref:
                    lines.append(f"      Ref: {s.url_or_ref}")
                if s.date:
                    lines.append(f"      Date: {s.date}")
                if s.excerpt:
                    lines.append(f"      Excerpt: \"{s.excerpt[:120]}\"")
        else:
            lines.append("  None recorded.")
        lines += [
            "",
            f"CLAIMS & CONFIDENCE ({len(self.claims)} claims | avg confidence: {self.overall_confidence_score:.2f})",
            "-" * 40,
        ]
        if self.claims:
            for i, c in enumerate(self.claims, 1):
                label = c.confidence.value
                marker = "✓" if c.confidence in (ConfidenceLevel.CONFIRMED, ConfidenceLevel.CORROBORATED) else "⚠"
                lines.append(f"  [{i}] [{marker} {label}] {c.statement}")
                if c.entities_involved:
                    lines.append(f"      Entities: {', '.join(c.entities_involved)}")
                if c.sources:
                    lines.append(f"      Sources: {', '.join(s.title for s in c.sources)}")
                if c.legal_risk_label and c.legal_risk_label != "None identified":
                    lines.append(f"      ⚖ Legal flag: {c.legal_risk_label}")
                if c.notes:
                    lines.append(f"      Notes: {c.notes}")
        else:
            lines.append("  None recorded.")
        lines += [
            "",
            "OPEN QUESTIONS",
            "-" * 40,
        ]
        if self.open_questions:
            for i, q in enumerate(self.open_questions, 1):
                lines.append(f"  [{i}] {q}")
        else:
            lines.append("  None recorded.")
        if self.has_legal_flags:
            lines += [
                "",
                "⚖ LEGAL RISK SUMMARY",
                "-" * 40,
                "  This investigation contains claims with legal risk flags.",
                "  Review with legal counsel before publication.",
            ]
        lines += [
            "",
            divider,
            "  ⚠ AXIOM OUTPUT — FOR HUMAN REVIEW ONLY. NOT READY TO PUBLISH.",
            "  This brief is a research instrument. Editorial judgment is required.",
            divider,
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "lead": self.lead,
            "journalist": self.journalist,
            "created_at": self.created_at,
            "status": self.status,
            "entities": [e.to_dict() for e in self.entities],
            "sources": [s.to_dict() for s in self.sources],
            "claims": [c.to_dict() for c in self.claims],
            "open_questions": self.open_questions,
            "notes": self.notes,
            "scores": {
                "overall_confidence": round(self.overall_confidence_score, 3),
                "source_quality": round(self.source_quality_score, 3),
                "has_legal_flags": self.has_legal_flags,
            },
        }
