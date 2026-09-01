# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Open-data helpers for Axiom Journalist."""
from __future__ import annotations

import json
import re
from collections import Counter
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

OPEN_DATA_SOURCES = {
    'usaspending': 'https://api.usaspending.gov/api/v2/',
    'opensecrets_base': 'https://www.opensecrets.org/api/',
    'court_listener': 'https://www.courtlistener.com/api/rest/v3/',
}

_STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'in', 'into',
    'is', 'it', 'of', 'on', 'or', 'that', 'the', 'their', 'this', 'to', 'was', 'with',
}
_PILLAR_RULES = [
    {
        'pillar': 'P001',
        'keywords': ('5d', '5-dimensional', 'five compact dimensions', 'kaluza-klein', 'compact dimensions'),
        'contradictions': ('11 compact dimensions', '10 compact dimensions', 'four dimensions only', 'no compact dimensions'),
    },
    {
        'pillar': 'P004',
        'keywords': ('holography', 'entropy-area', 'boundary entropy', 'holographic boundary'),
        'contradictions': ('entropy is purely volumetric', 'no boundary entropy'),
    },
    {
        'pillar': 'P005',
        'keywords': ('fixed point', 'ftum', 'multiverse iteration'),
        'contradictions': ('no fixed point', 'fixed point is impossible'),
    },
    {
        'pillar': 'P009',
        'keywords': ('consciousness coupling', 'brain-universe', 'xi_c', 'coupled attractor'),
        'contradictions': ('consciousness coupling is zero', 'no brain-universe coupling'),
    },
    {
        'pillar': 'P021',
        'keywords': ('ecosystem', 'ecology', 'biodiversity', 'food web'),
        'contradictions': ('ecosystems cannot self-organize', 'no ecological homeostasis'),
    },
]


def fetch_usaspending_awards(keyword: str, limit: int = 10) -> list[dict]:
    """Fetch award summaries from USAspending and degrade safely on failures."""
    term = keyword.strip()
    capped_limit = max(0, min(int(limit), 50))
    if not term or capped_limit == 0:
        return []

    endpoint = OPEN_DATA_SOURCES['usaspending'].rstrip('/') + '/search/spending_by_award/'
    payload = {
        'filters': {'keywords': [term]},
        'limit': capped_limit,
        'page': 1,
        'sort': 'Award Amount',
        'order': 'desc',
    }
    request = Request(
        endpoint,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'AxiomJournalist/1.0',
        },
        method='POST',
    )
    try:
        with urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, OSError, TimeoutError, ValueError, json.JSONDecodeError):
        return []

    raw_awards = data.get('results') or data.get('awards') or []
    awards: list[dict] = []
    for item in raw_awards[:capped_limit]:
        if not isinstance(item, dict):
            continue
        awards.append({
            'award_id': item.get('generated_internal_id') or item.get('award_id') or item.get('id') or '',
            'recipient': item.get('recipient_name') or item.get('recipient') or '',
            'description': item.get('award_description') or item.get('description') or '',
            'amount': item.get('total_obligation') or item.get('amount') or 0,
            'source': 'usaspending',
        })
    return awards


def build_investigative_brief(corpus: list[str], topic: str) -> dict:
    """Build a compact investigative brief with simple lexical heuristics."""
    joined = ' '.join(corpus)
    tokens = [
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", joined)
        if token.lower() not in _STOPWORDS
    ]
    key_terms = [term for term, _ in Counter(tokens).most_common(8)]
    timeline = sorted({
        match
        for text in corpus
        for match in re.findall(r"\b(?:19|20)\d{2}(?:-\d{2}-\d{2})?\b", text)
    })
    urls = re.findall(r"https?://[^\s)]+", joined)
    sources = sorted({urlparse(url).netloc for url in urls if urlparse(url).netloc})
    return {
        'topic': topic,
        'document_count': len(corpus),
        'key_terms': key_terms,
        'timeline': timeline,
        'sources': sources,
    }


def check_physics_integrity(claim: str) -> dict:
    """Check whether a claim obviously conflicts with a small hardgate keyword map."""
    claim_lower = claim.lower()
    related_pillars: list[str] = []
    contradictions: list[str] = []
    for rule in _PILLAR_RULES:
        if any(keyword in claim_lower for keyword in rule['keywords']):
            related_pillars.append(rule['pillar'])
            if any(marker in claim_lower for marker in rule['contradictions']):
                contradictions.append(rule['pillar'])

    consistent = not contradictions
    if not related_pillars:
        caveat = 'No direct hardgate pillar match; heuristic keyword screen only.'
    elif consistent:
        caveat = 'No contradiction detected in the keyword-matched hardgate subset.'
    else:
        caveat = 'Potential contradiction detected; human review should compare the claim against the cited pillars.'
    return {
        'claim': claim,
        'consistent': consistent,
        'related_pillars': sorted(set(related_pillars or contradictions)),
        'caveat': caveat,
    }
