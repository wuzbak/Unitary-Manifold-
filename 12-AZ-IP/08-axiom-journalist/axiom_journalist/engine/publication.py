# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Governed publication/export helpers for Axiom Journalist."""
from __future__ import annotations

from collections import Counter
import math
from typing import Any


def _score_label(value: float) -> str:
    if value >= 0.85:
        return 'HIGH'
    if value >= 0.6:
        return 'ELEVATED'
    if value >= 0.35:
        return 'MIXED'
    return 'LOW'


def _claims(investigation: dict[str, Any]) -> list[dict[str, Any]]:
    raw = investigation.get('claims') or []
    return [item for item in raw if isinstance(item, dict)]


def _sources(investigation: dict[str, Any]) -> list[dict[str, Any]]:
    raw = investigation.get('sources') or []
    return [item for item in raw if isinstance(item, dict)]


def _entities(investigation: dict[str, Any]) -> list[dict[str, Any]]:
    raw = investigation.get('entities') or []
    return [item for item in raw if isinstance(item, dict)]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def _normalized_legal_flags(claim: dict[str, Any]) -> list[str]:
    raw = str(claim.get('legal_risks', 'None identified'))
    normalized: list[str] = []
    for part in [piece.strip() for piece in raw.split('|') if piece.strip()]:
        upper = part.upper().replace(' ', '_')
        if upper in {'NONE_IDENTIFIED', 'NONE'}:
            normalized.append('NONE_IDENTIFIED')
        else:
            normalized.append(upper)
    return normalized or ['NONE_IDENTIFIED']


def build_dossier_packet(investigation: dict[str, Any]) -> dict[str, Any]:
    """Build a governed dossier packet from a structured investigation dict."""
    claims = _claims(investigation)
    sources = _sources(investigation)
    entities = _entities(investigation)
    scores = investigation.get('scores') or {}

    confidence_counts = Counter(
        str(claim.get('confidence', 'UNVERIFIED')).upper()
        for claim in claims
    )
    legal_flags = Counter()
    for claim in claims:
        for flag in _normalized_legal_flags(claim):
            legal_flags[flag] += 1

    source_tiers = Counter(
        str(source.get('tier') or 'Unclassified')
        for source in sources
    )
    contradiction_count = sum(
        len(entity.get('contradictions') or [])
        for entity in entities
    )

    overall_confidence = _safe_float(scores.get('overall_confidence', 0.0), 0.0)
    source_quality = _safe_float(scores.get('source_quality', 0.0), 0.0)

    recognized_flags = {
        'NONE_IDENTIFIED',
        'LIBEL_EXPOSURE',
        'SOURCE_PROTECT',
        'WHISTLEBLOWER',
        'PRIVACY',
        'NATIONAL_SECURITY',
    }
    unknown_flags = set(legal_flags) - recognized_flags

    normalized_flag_set = set(legal_flags)
    highest_risk = 'CONTROLLED'
    if any(flag in legal_flags for flag in ('NATIONAL_SECURITY', 'LIBEL_EXPOSURE', 'SOURCE_PROTECT', 'PRIVACY', 'WHISTLEBLOWER')):
        highest_risk = 'HIGH'
    elif unknown_flags:
        highest_risk = 'REVIEW'
    elif normalized_flag_set and normalized_flag_set != {'NONE_IDENTIFIED'}:
        highest_risk = 'ELEVATED'

    return {
        'title': investigation.get('title', 'Untitled Investigation'),
        'lead': investigation.get('lead', ''),
        'journalist': investigation.get('journalist', ''),
        'status': investigation.get('status', 'Active'),
        'scores': {
            'overall_confidence': round(overall_confidence, 3),
            'overall_confidence_label': _score_label(overall_confidence),
            'source_quality': round(source_quality, 3),
            'source_quality_label': _score_label(source_quality),
        },
        'evidence_summary': {
            'entity_count': len(entities),
            'source_count': len(sources),
            'claim_count': len(claims),
            'open_question_count': len(investigation.get('open_questions') or []),
            'contradiction_count': contradiction_count,
            'source_tiers': dict(source_tiers),
            'confidence_counts': dict(confidence_counts),
            'legal_flags': dict(legal_flags),
        },
        'publication_posture': {
            'status': 'HUMAN_REVIEW_REQUIRED',
            'legal_risk_level': highest_risk,
            'unclassified_risk_flags': sorted(unknown_flags),
            'retaliation_awareness': [
                'Preserve documentary chain-of-custody for every quoted source.',
                'Separate adjudicated fact, corroborated reporting, allegation, and open question.',
                'Log contradictions and unanswered questions without narrative smoothing.',
                'Escalate named-party claims carrying legal or source-protection risk before publication.',
            ],
        },
        'editorial_sections': {
            'prefatory_note': (
                'This packet is a document-first investigative synthesis. '
                'It is structured for verification, challenge, legal review, and human editorial judgment.'
            ),
            'entity_watchlist': [
                {
                    'name': entity.get('name', ''),
                    'type': entity.get('type', 'Other'),
                    'stated_position': entity.get('stated_position', ''),
                    'contradictions': entity.get('contradictions') or [],
                }
                for entity in entities
            ],
            'claim_watchlist': [
                {
                    'statement': claim.get('statement', ''),
                    'confidence': claim.get('confidence', 'UNVERIFIED'),
                    'legal_risks': ' | '.join(_normalized_legal_flags(claim)).replace('NONE_IDENTIFIED', 'None identified'),
                    'entities_involved': claim.get('entities_involved') or [],
                    'source_titles': [
                        source.get('title', '')
                        for source in (claim.get('sources') or [])
                        if isinstance(source, dict)
                    ],
                }
                for claim in claims
            ],
            'source_ledger': [
                {
                    'title': source.get('title', ''),
                    'tier': source.get('tier') or 'Unclassified',
                    'source_type': source.get('source_type', ''),
                    'url_or_ref': source.get('url_or_ref', ''),
                    'date': source.get('date', ''),
                }
                for source in sources
            ],
            'open_questions': investigation.get('open_questions') or [],
        },
        'hils_gate': {
            'required': True,
            'status': 'PENDING_HUMAN_REVIEW',
            'checks': [
                'Verify every named-party claim against the attached source ledger.',
                'Confirm confidence labels match the actual evidence mix.',
                'Confirm retaliation/legal concerns are visible and unresolved unknowns remain visible.',
                'Approve, hold, or narrow publication scope before any outward release.',
            ],
        },
    }


def render_dossier_markdown(packet: dict[str, Any]) -> str:
    """Render the governed dossier packet as human-readable markdown."""
    lines = [
        f"# {packet['title']} — Governed Dossier Packet",
        '',
        '## Publication posture',
        f"- Status: **{packet['publication_posture']['status']}**",
        f"- Legal risk level: **{packet['publication_posture']['legal_risk_level']}**",
        f"- Overall confidence: **{packet['scores']['overall_confidence']:.2f}** ({packet['scores']['overall_confidence_label']})",
        f"- Source quality: **{packet['scores']['source_quality']:.2f}** ({packet['scores']['source_quality_label']})",
        '',
        '## Investigative lead',
        packet['lead'] or '_No lead recorded._',
        '',
        '## Evidence summary',
        f"- Entities: {packet['evidence_summary']['entity_count']}",
        f"- Sources: {packet['evidence_summary']['source_count']}",
        f"- Claims: {packet['evidence_summary']['claim_count']}",
        f"- Open questions: {packet['evidence_summary']['open_question_count']}",
        f"- Contradictions logged: {packet['evidence_summary']['contradiction_count']}",
        '',
        '### Confidence mix',
    ]
    confidence_counts = packet['evidence_summary']['confidence_counts']
    if confidence_counts:
        for key, value in sorted(confidence_counts.items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append('- _No claims recorded yet._')
    lines += [
        '',
        '### Source tiers',
    ]
    source_tiers = packet['evidence_summary']['source_tiers']
    if source_tiers:
        for key, value in sorted(source_tiers.items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append('- _No sources recorded yet._')
    lines += [
        '',
        '### Legal / retaliation awareness',
    ]
    if packet['publication_posture']['unclassified_risk_flags']:
        lines.append(
            "- Unclassified legal flags requiring bespoke review: "
            + ', '.join(packet['publication_posture']['unclassified_risk_flags'])
        )
    for item in packet['publication_posture']['retaliation_awareness']:
        lines.append(f"- {item}")
    lines += [
        '',
        '## Entity watchlist',
    ]
    entity_watchlist = packet['editorial_sections']['entity_watchlist']
    if entity_watchlist:
        for entity in entity_watchlist:
            lines.append(f"- **{entity['name']}** [{entity['type']}]")
            if entity['stated_position']:
                lines.append(f"  - Stated position: {entity['stated_position']}")
            contradictions = entity['contradictions'] or []
            if contradictions:
                for contradiction in contradictions:
                    lines.append(f"  - Contradiction: {contradiction}")
    else:
        lines.append('- _No entities recorded._')
    lines += [
        '',
        '## Claim watchlist',
    ]
    for claim in packet['editorial_sections']['claim_watchlist']:
        lines.append(
            f"- **{claim['confidence']}** — {claim['statement']}"
        )
        if claim['entities_involved']:
            lines.append(f"  - Entities: {', '.join(claim['entities_involved'])}")
        if claim['source_titles']:
            lines.append(f"  - Sources: {', '.join(claim['source_titles'])}")
        if claim['legal_risks'] and claim['legal_risks'] != 'None identified':
            lines.append(f"  - Legal: {claim['legal_risks']}")
    if not packet['editorial_sections']['claim_watchlist']:
        lines.append('- _No claims recorded._')
    lines += [
        '',
        '## Source ledger',
    ]
    source_ledger = packet['editorial_sections']['source_ledger']
    if source_ledger:
        for source in source_ledger:
            lines.append(f"- **{source['title']}** [{source['tier']}]")
            if source['source_type']:
                lines.append(f"  - Type: {source['source_type']}")
            if source['url_or_ref']:
                lines.append(f"  - Ref: {source['url_or_ref']}")
            if source['date']:
                lines.append(f"  - Date: {source['date']}")
    else:
        lines.append('- _No sources recorded._')
    lines += [
        '',
        '## Open questions',
    ]
    open_questions = packet['editorial_sections']['open_questions']
    if open_questions:
        for question in open_questions:
            lines.append(f"- {question}")
    else:
        lines.append('- _No open questions recorded._')
    lines += [
        '',
        '## HILS gate',
        f"- Required: {packet['hils_gate']['required']}",
        f"- Status: **{packet['hils_gate']['status']}**",
    ]
    for check in packet['hils_gate']['checks']:
        lines.append(f"- {check}")
    return '\n'.join(lines)


def build_psicat_training_packet(investigation: dict[str, Any]) -> dict[str, Any]:
    """Convert an investigation into a PsiCat-oriented study and publication packet."""
    claims = _claims(investigation)
    sources = _sources(investigation)
    open_questions = investigation.get('open_questions') or []
    source_refs = [
        source.get('url_or_ref', '')
        for source in sources
        if source.get('url_or_ref')
    ]

    challenge_set = [
        {
            'type': 'contradiction-check',
            'prompt': claim.get('statement', ''),
            'required_behavior': 'preserve uncertainty and cite supporting evidence before synthesis',
        }
        for claim in claims[:8]
    ]
    challenge_set.extend(
        {
            'type': 'open-question',
            'prompt': question,
            'required_behavior': 'convert the unknown into a research task without pretending closure',
        }
        for question in open_questions[:8]
    )

    return {
        'product': 'PsiCat',
        'mission': 'Governed investigative support, training, and publication construction',
        'investigation_title': investigation.get('title', 'Untitled Investigation'),
        'study_targets': {
            'claim_count': len(claims),
            'source_count': len(sources),
            'priority_sources': source_refs[:12],
            'open_questions': open_questions[:12],
        },
        'training_objectives': [
            'Retain the distinction between adjudicated fact, corroborated reporting, allegation, and unresolved unknown.',
            'Use source-ledger discipline before narrative synthesis.',
            'Surface legal-risk and retaliation-awareness markers in outward-facing outputs.',
            'Preserve contradiction state instead of collapsing it for narrative cleanliness.',
        ],
        'publication_requirements': [
            'Every high-impact conclusion must cite retrievable evidence.',
            'Confidence labels must survive into drafts and review packets.',
            'No publication without human review and explicit scope approval.',
            'Unknowns remain visible in the publication packet.',
        ],
        'challenge_pack': challenge_set,
        'handoff_status': 'READY_FOR_GOVERNED_PSICAT_STUDY',
    }


def render_psicat_training_markdown(packet: dict[str, Any]) -> str:
    """Render a PsiCat handoff packet as markdown."""
    lines = [
        f"# PsiCat Training / Publication Packet — {packet['investigation_title']}",
        '',
        f"- Product: **{packet['product']}**",
        f"- Mission: **{packet['mission']}**",
        f"- Handoff status: **{packet['handoff_status']}**",
        '',
        '## Study targets',
        f"- Claims to study: {packet['study_targets']['claim_count']}",
        f"- Sources to study: {packet['study_targets']['source_count']}",
    ]
    if packet['study_targets']['priority_sources']:
        lines.append('- Priority source refs:')
        lines.extend(f"  - {ref}" for ref in packet['study_targets']['priority_sources'])
    if packet['study_targets']['open_questions']:
        lines.append('- Open questions:')
        lines.extend(f"  - {question}" for question in packet['study_targets']['open_questions'])
    lines += [
        '',
        '## Training objectives',
    ]
    lines.extend(f"- {item}" for item in packet['training_objectives'])
    lines += [
        '',
        '## Publication requirements',
    ]
    lines.extend(f"- {item}" for item in packet['publication_requirements'])
    lines += [
        '',
        '## Challenge pack',
    ]
    if packet['challenge_pack']:
        for item in packet['challenge_pack']:
            lines.append(f"- [{item['type']}] {item['prompt']}")
            lines.append(f"  - Required behavior: {item['required_behavior']}")
    else:
        lines.append('- _No claims or open questions available yet._')
    return '\n'.join(lines)
