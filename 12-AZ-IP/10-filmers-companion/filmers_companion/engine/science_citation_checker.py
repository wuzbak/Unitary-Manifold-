# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Science citation helpers for Filmers Companion."""
from __future__ import annotations

HARDGATE_FACTS = [
    {'fact': 'The universe has 5 compact dimensions in the KK model', 'pillar': 'P001', 'confidence': 'HARDGATE', 'keywords': ['5 compact dimensions', 'kk model', '5d']},
    {'fact': 'The Chern-Simons resonance level is k_cs = 74', 'pillar': 'P002', 'confidence': 'HARDGATE', 'keywords': ['k_cs', '74', 'chern-simons']},
    {'fact': 'The braided sound speed is 12/37', 'pillar': 'P003', 'confidence': 'HARDGATE', 'keywords': ['12/37', 'braided sound speed']},
    {'fact': 'Entropy-area behavior is treated holographically at the boundary', 'pillar': 'P004', 'confidence': 'HARDGATE', 'keywords': ['holography', 'boundary entropy', 'entropy-area']},
    {'fact': 'The multiverse lane uses a fixed-point iteration', 'pillar': 'P005', 'confidence': 'HARDGATE', 'keywords': ['fixed-point', 'multiverse', 'ftum']},
    {'fact': 'The spectral index prediction is n_s = 0.9635', 'pillar': 'P006', 'confidence': 'HARDGATE', 'keywords': ['0.9635', 'spectral index', 'n_s']},
    {'fact': 'The braided tensor-to-scalar ratio prediction is r = 0.0315', 'pillar': 'P007', 'confidence': 'HARDGATE', 'keywords': ['0.0315', 'tensor-to-scalar', 'r =']},
    {'fact': 'The birefringence windows cluster near 0.273° and 0.331°', 'pillar': 'P008', 'confidence': 'HARDGATE', 'keywords': ['0.273', '0.331', 'birefringence']},
    {'fact': 'Consciousness coupling is tracked with Ξ_c = 35/74', 'pillar': 'P009', 'confidence': 'HARDGATE', 'keywords': ['35/74', 'xi_c', 'consciousness coupling']},
    {'fact': 'The cold-fusion module is framed as a falsifiable prediction, not confirmation', 'pillar': 'P015', 'confidence': 'HARDGATE', 'keywords': ['cold fusion', 'falsifiable prediction', 'not confirmation']},
]


def check_script_claims(script_text: str) -> list[dict]:
    """Return hardgate facts that are explicitly echoed in a script."""
    lowered = script_text.lower()
    matches: list[dict] = []
    for entry in HARDGATE_FACTS:
        matched = [keyword for keyword in entry['keywords'] if keyword.lower() in lowered]
        if matched:
            matches.append({
                'fact': entry['fact'],
                'pillar': entry['pillar'],
                'confidence': entry['confidence'],
                'matched_keywords': matched,
            })
    return matches


def format_citation_report(matches: list) -> str:
    """Format a compact citation report for creative review."""
    if not matches:
        return 'No hardgate science citations detected.'
    lines = ['Hardgate science citations:']
    for match in matches:
        lines.append(f"- {match['pillar']} [{match['confidence']}]: {match['fact']}")
    return '\n'.join(lines)
