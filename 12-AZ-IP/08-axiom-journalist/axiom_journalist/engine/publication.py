# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Governed publication/export helpers for Axiom Journalist."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True)
class PublicationPolicy:
    high_score_threshold: float = 0.85
    elevated_score_threshold: float = 0.6
    mixed_score_threshold: float = 0.35
    max_claim_challenges: int = 8
    max_open_question_challenges: int = 8
    contradiction_overlap_minimum: int = 3


DEFAULT_PUBLICATION_POLICY = PublicationPolicy()


def _score_label(value: float, policy: PublicationPolicy) -> str:
    if value >= policy.high_score_threshold:
        return 'HIGH'
    if value >= policy.elevated_score_threshold:
        return 'ELEVATED'
    if value >= policy.mixed_score_threshold:
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


def _normalized_source_tier(value: Any) -> str:
    normalized = str(value or '').strip()
    return normalized or 'Unclassified'


def _normalized_text(value: Any) -> str:
    return ' '.join(str(value or '').split())


def _source_identity(source: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        _normalized_text(source.get('title', '')).casefold(),
        _normalized_text(source.get('url_or_ref', '')).casefold(),
        _normalized_text(source.get('source_type', '')).casefold(),
        _normalized_text(source.get('date', '')).casefold(),
    )


def _deduplicate_sources(sources: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seen: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    duplicates: list[dict[str, Any]] = []
    deduped: list[dict[str, Any]] = []
    for source in sources:
        key = _source_identity(source)
        if key in seen:
            duplicates.append({
                'title': _normalized_text(source.get('title', '')),
                'url_or_ref': _normalized_text(source.get('url_or_ref', '')),
                'date': _normalized_text(source.get('date', '')),
            })
            continue
        normalized = dict(source)
        normalized['title'] = _normalized_text(source.get('title', ''))
        normalized['tier'] = _normalized_source_tier(source.get('tier'))
        normalized['source_type'] = _normalized_text(source.get('source_type', ''))
        normalized['url_or_ref'] = _normalized_text(source.get('url_or_ref', ''))
        normalized['date'] = _normalized_text(source.get('date', ''))
        seen[key] = normalized
        deduped.append(normalized)
    return deduped, duplicates


_NEGATION_MARKERS = {'no', 'not', 'never', 'none'}
_CLAIM_STOPWORDS = {
    'the', 'and', 'that', 'with', 'from', 'into', 'this', 'there', 'their', 'have',
    'were', 'will', 'shall', 'about', 'under', 'after', 'before', 'because',
}


def _normalized_tokens(statement: str) -> list[str]:
    tokens: list[str] = []
    for raw in _normalized_text(statement).lower().replace('-', ' ').split():
        token = ''.join(ch for ch in raw if ch.isalnum() or ch == "'")
        if token:
            tokens.append(token)
    return tokens


def _claim_terms(statement: str) -> set[str]:
    terms: set[str] = set()
    for raw in _normalized_tokens(statement):
        token = ''.join(ch for ch in raw if ch.isalnum())
        if len(token) >= 4 and token not in _CLAIM_STOPWORDS:
            terms.add(token)
    return terms


def _claim_phrases(statement: str) -> set[str]:
    tokens = [''.join(ch for ch in raw if ch.isalnum()) for raw in _normalized_tokens(statement)]
    filtered = [token for token in tokens if len(token) >= 4 and token not in _CLAIM_STOPWORDS]
    return {
        f'{filtered[index]} {filtered[index + 1]}'
        for index in range(len(filtered) - 1)
    }


def _claim_is_negative(statement: str) -> bool:
    tokens = _normalized_tokens(statement)
    normalized = {token.rstrip(".,;:!?") for token in tokens}
    contraction_expansions = {
        "didn't": 'not',
        "doesn't": 'not',
        "don't": 'not',
        "isn't": 'not',
        "wasn't": 'not',
        "weren't": 'not',
        "can't": 'not',
        "couldn't": 'not',
        "shouldn't": 'not',
        "wouldn't": 'not',
        "won't": 'not',
        "hasn't": 'not',
        "haven't": 'not',
        "hadn't": 'not',
    }
    expanded = {contraction_expansions.get(token, token) for token in normalized}
    return any(marker in expanded for marker in _NEGATION_MARKERS)


def _cross_claim_contradictions(
    claims: list[dict[str, Any]],
    policy: PublicationPolicy,
) -> list[dict[str, Any]]:
    contradictions: list[dict[str, Any]] = []
    for idx, left in enumerate(claims):
        left_entities = {str(item).strip().casefold() for item in (left.get('entities_involved') or []) if str(item).strip()}
        left_terms = _claim_terms(str(left.get('statement', '')))
        left_phrases = _claim_phrases(str(left.get('statement', '')))
        if not left_terms:
            continue
        left_negative = _claim_is_negative(str(left.get('statement', '')))
        for right in claims[idx + 1:]:
            right_entities = {str(item).strip().casefold() for item in (right.get('entities_involved') or []) if str(item).strip()}
            shared_entities = sorted(left_entities & right_entities)
            if not shared_entities:
                continue
            right_terms = _claim_terms(str(right.get('statement', '')))
            right_phrases = _claim_phrases(str(right.get('statement', '')))
            if not right_terms:
                continue
            overlap = sorted(left_terms & right_terms)
            phrase_overlap = sorted(left_phrases & right_phrases)
            phrase_threshold = max(1, policy.contradiction_overlap_minimum - 1)
            if len(overlap) < policy.contradiction_overlap_minimum and len(phrase_overlap) < phrase_threshold:
                continue
            right_negative = _claim_is_negative(str(right.get('statement', '')))
            if left_negative == right_negative:
                continue
            contradictions.append({
                'claim_a': str(left.get('statement', '')),
                'claim_b': str(right.get('statement', '')),
                'shared_entities': shared_entities,
                'overlap_terms': overlap,
                'overlap_phrases': phrase_overlap,
            })
    return contradictions


def build_dossier_packet(
    investigation: dict[str, Any],
    policy: PublicationPolicy = DEFAULT_PUBLICATION_POLICY,
) -> dict[str, Any]:
    """Build a governed dossier packet from a structured investigation dict."""
    claims = _claims(investigation)
    sources, duplicate_sources = _deduplicate_sources(_sources(investigation))
    entities = _entities(investigation)
    scores = investigation.get('scores') or {}
    cross_claim_contradictions = _cross_claim_contradictions(claims, policy)

    confidence_counts = Counter(
        str(claim.get('confidence', 'UNVERIFIED')).upper()
        for claim in claims
    )
    legal_flags = Counter()
    for claim in claims:
        for flag in _normalized_legal_flags(claim):
            legal_flags[flag] += 1

    source_tiers = Counter(
        _normalized_source_tier(source.get('tier'))
        for source in sources
    )
    contradiction_count = sum(
        len(entity.get('contradictions') or [])
        for entity in entities
    ) + len(cross_claim_contradictions)

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
    has_high_risk_flags = any(
        flag in legal_flags
        for flag in ('NATIONAL_SECURITY', 'LIBEL_EXPOSURE', 'SOURCE_PROTECT', 'PRIVACY', 'WHISTLEBLOWER')
    )

    highest_risk = 'CONTROLLED'
    if has_high_risk_flags and unknown_flags:
        highest_risk = 'HIGH_REVIEW'
    elif has_high_risk_flags:
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
            'overall_confidence_label': _score_label(overall_confidence, policy),
            'source_quality': round(source_quality, 3),
            'source_quality_label': _score_label(source_quality, policy),
        },
        'evidence_summary': {
            'entity_count': len(entities),
            'source_count': len(sources),
            'duplicate_source_count': len(duplicate_sources),
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
                    'tier': _normalized_source_tier(source.get('tier')),
                    'source_type': source.get('source_type', ''),
                    'url_or_ref': source.get('url_or_ref', ''),
                    'date': source.get('date', ''),
                }
                for source in sources
            ],
            'duplicate_sources': duplicate_sources,
            'cross_claim_contradictions': cross_claim_contradictions,
            'open_questions': investigation.get('open_questions') or [],
        },
        'policy': {
            'high_score_threshold': policy.high_score_threshold,
            'elevated_score_threshold': policy.elevated_score_threshold,
            'mixed_score_threshold': policy.mixed_score_threshold,
            'max_claim_challenges': policy.max_claim_challenges,
            'max_open_question_challenges': policy.max_open_question_challenges,
            'contradiction_overlap_minimum': policy.contradiction_overlap_minimum,
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
        f"- Duplicate sources collapsed: {packet['evidence_summary']['duplicate_source_count']}",
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
        '## Duplicate source review',
    ]
    duplicate_sources = packet['editorial_sections']['duplicate_sources']
    if duplicate_sources:
        for source in duplicate_sources:
            lines.append(f"- **{source['title'] or 'Untitled source'}**")
            if source['url_or_ref']:
                lines.append(f"  - Ref: {source['url_or_ref']}")
            if source['date']:
                lines.append(f"  - Date: {source['date']}")
    else:
        lines.append('- _No duplicate sources detected._')
    lines += [
        '',
        '## Cross-claim contradiction review',
    ]
    cross_claim_contradictions = packet['editorial_sections']['cross_claim_contradictions']
    if cross_claim_contradictions:
        for item in cross_claim_contradictions:
            lines.append(f"- Claim A: {item['claim_a']}")
            lines.append(f"  - Claim B: {item['claim_b']}")
            lines.append(f"  - Shared entities: {', '.join(item['shared_entities'])}")
            lines.append(f"  - Overlap terms: {', '.join(item['overlap_terms'])}")
            lines.append(f"  - Overlap phrases: {', '.join(item['overlap_phrases'])}")
    else:
        lines.append('- _No cross-claim contradictions detected by heuristic review._')
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


def build_psicat_training_packet(
    investigation: dict[str, Any],
    policy: PublicationPolicy = DEFAULT_PUBLICATION_POLICY,
) -> dict[str, Any]:
    """Convert an investigation into a PsiCat-oriented study and publication packet."""
    claims = _claims(investigation)
    sources, duplicate_sources = _deduplicate_sources(_sources(investigation))
    open_questions = investigation.get('open_questions') or []
    contradictions = _cross_claim_contradictions(claims, policy)
    source_refs = [
        _normalized_text(source.get('url_or_ref', ''))
        for source in sources
        if _normalized_text(source.get('url_or_ref', ''))
    ]

    contradiction_capacity = 0
    if policy.max_claim_challenges > 0 and contradictions:
        contradiction_capacity = min(
            len(contradictions),
            max(1, policy.max_claim_challenges // 2),
        )
    claim_capacity = max(policy.max_claim_challenges - contradiction_capacity, 0)

    contradiction_challenges = [
        {
            'type': 'cross-claim-contradiction',
            'prompt': item['claim_a'],
            'required_behavior': (
                'compare against the paired claim, preserve the contradiction, '
                'and route to human review before narrative closure'
            ),
            'paired_claim': item['claim_b'],
        }
        for item in contradictions[:contradiction_capacity]
    ]
    contradiction_claims = {
        challenge['prompt']
        for challenge in contradiction_challenges
    } | {
        challenge['paired_claim']
        for challenge in contradiction_challenges
    }
    claim_challenges = [
        {
            'type': 'contradiction-check',
            'prompt': claim.get('statement', ''),
            'required_behavior': 'preserve uncertainty and cite supporting evidence before synthesis',
        }
        for claim in claims
        if str(claim.get('statement', '')) not in contradiction_claims
    ][:claim_capacity]
    challenge_set = claim_challenges + contradiction_challenges
    challenge_set.extend(
        {
            'type': 'open-question',
            'prompt': question,
            'required_behavior': 'convert the unknown into a research task without pretending closure',
        }
        for question in open_questions[:policy.max_open_question_challenges]
    )

    return {
        'product': 'PsiCat',
        'mission': 'Governed investigative support, training, and publication construction',
        'investigation_title': investigation.get('title', 'Untitled Investigation'),
        'study_targets': {
            'claim_count': len(claims),
            'source_count': len(sources),
            'duplicate_source_count': len(duplicate_sources),
            'cross_claim_contradiction_count': len(contradictions),
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
        'policy': {
            'max_claim_challenges': policy.max_claim_challenges,
            'max_open_question_challenges': policy.max_open_question_challenges,
            'contradiction_overlap_minimum': policy.contradiction_overlap_minimum,
        },
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
        f"- Duplicate sources collapsed: {packet['study_targets']['duplicate_source_count']}",
        f"- Cross-claim contradictions queued: {packet['study_targets']['cross_claim_contradiction_count']}",
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
            if item.get('paired_claim'):
                lines.append(f"  - Paired claim: {item['paired_claim']}")
    else:
        lines.append('- _No claims or open questions available yet._')
    return '\n'.join(lines)


def build_story_packet(
    investigation: dict[str, Any],
    policy: PublicationPolicy = DEFAULT_PUBLICATION_POLICY,
) -> dict[str, Any]:
    """Build an evidence-led story packet for governed PsiCat publication drafting."""
    dossier_packet = build_dossier_packet(investigation, policy)
    psicat_packet = build_psicat_training_packet(investigation, policy)
    entities = dossier_packet['editorial_sections']['entity_watchlist']
    claims = dossier_packet['editorial_sections']['claim_watchlist']
    open_questions = dossier_packet['editorial_sections']['open_questions']
    contradictions = dossier_packet['editorial_sections']['cross_claim_contradictions']
    source_ledger = dossier_packet['editorial_sections']['source_ledger']

    chapters: list[dict[str, Any]] = [
        {
            'heading': 'What can be established from the record',
            'focus': 'Open with the lead, the strongest claims, and the highest-grade source anchors.',
            'evidence': [claim['statement'] for claim in claims[:3]],
        },
        {
            'heading': 'Who is in the story and what each party says',
            'focus': 'Map the named entities, their public positions, and the documented contradictions.',
            'evidence': [entity['name'] for entity in entities[:6]],
        },
        {
            'heading': 'What remains unresolved',
            'focus': 'Keep unanswered questions and contradiction points visible instead of narratively smoothing them away.',
            'evidence': open_questions[:6],
        },
    ]
    if contradictions:
        chapters.insert(2, {
            'heading': 'Where the record conflicts with itself',
            'focus': 'Show contradiction pairs explicitly and explain why human review is still required.',
            'evidence': [item['claim_a'] for item in contradictions[:4]],
        })

    return {
        'title': f"{investigation.get('title', 'Untitled Investigation')} — PsiCat Publication Story Packet",
        'publication_posture': dossier_packet['publication_posture'],
        'narrative_contract': {
            'voice': 'AxiomZero / PsiCat sober public-record narrative',
            'governing_rule': 'Every major conclusion must stay attached to a source and confidence label.',
            'forbidden_moves': [
                'Do not collapse allegations into adjudicated fact.',
                'Do not erase contradictions or unknowns for narrative elegance.',
                'Do not imply publication readiness without human review.',
            ],
        },
        'story_spine': {
            'lede': dossier_packet['lead'] or 'No investigative lead recorded.',
            'evidence_posture': dossier_packet['scores'],
            'chapters': chapters,
        },
        'source_backbone': source_ledger[:12],
        'psicat_learning_packet': {
            'challenge_count': len(psicat_packet['challenge_pack']),
            'training_objectives': psicat_packet['training_objectives'],
            'challenge_pack': psicat_packet['challenge_pack'][:12],
        },
        'final_gate': dossier_packet['hils_gate'],
    }


def render_story_markdown(packet: dict[str, Any]) -> str:
    """Render the governed story packet as a human-readable drafting guide."""
    lines = [
        f"# {packet['title']}",
        '',
        '## Publication posture',
        f"- Legal risk level: **{packet['publication_posture']['legal_risk_level']}**",
        f"- Status: **{packet['publication_posture']['status']}**",
        '',
        '## Narrative contract',
        f"- Voice: **{packet['narrative_contract']['voice']}**",
        f"- Governing rule: {packet['narrative_contract']['governing_rule']}",
        '- Forbidden moves:',
    ]
    lines.extend(f"  - {item}" for item in packet['narrative_contract']['forbidden_moves'])
    lines += [
        '',
        '## Story spine',
        f"- Lede: {packet['story_spine']['lede']}",
        f"- Evidence posture: confidence {packet['story_spine']['evidence_posture']['overall_confidence']:.2f} / source quality {packet['story_spine']['evidence_posture']['source_quality']:.2f}",
        '',
    ]
    for chapter in packet['story_spine']['chapters']:
        lines.append(f"### {chapter['heading']}")
        lines.append(chapter['focus'])
        if chapter['evidence']:
            lines.extend(f"- {item}" for item in chapter['evidence'])
        else:
            lines.append('- _No evidence items attached yet._')
        lines.append('')
    lines += [
        '## Source backbone',
    ]
    if packet['source_backbone']:
        for source in packet['source_backbone']:
            lines.append(f"- **{source['title']}** [{source['tier']}]")
            if source['url_or_ref']:
                lines.append(f"  - Ref: {source['url_or_ref']}")
    else:
        lines.append('- _No sources attached yet._')
    lines += [
        '',
        '## PsiCat learning packet',
        f"- Challenge count: {packet['psicat_learning_packet']['challenge_count']}",
        '- Training objectives:',
    ]
    lines.extend(f"  - {item}" for item in packet['psicat_learning_packet']['training_objectives'])
    if packet['psicat_learning_packet']['challenge_pack']:
        lines.append('- Challenge pack:')
        for item in packet['psicat_learning_packet']['challenge_pack']:
            lines.append(f"  - [{item['type']}] {item['prompt']}")
    lines += [
        '',
        '## Final gate',
        f"- Status: **{packet['final_gate']['status']}**",
    ]
    lines.extend(f"- {item}" for item in packet['final_gate']['checks'])
    return '\n'.join(lines)
