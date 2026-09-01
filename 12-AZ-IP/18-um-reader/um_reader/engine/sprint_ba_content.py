# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Sprint BA chapter content for UM Reader."""
from __future__ import annotations

SPRINT_BA_CHAPTERS = [
    {'chapter': 1, 'title': 'Threshold Geometry', 'pillar_range': [837, 841], 'status': 'research draft', 'summary': 'Introduces the late-stage dimensional handoff from readable 4D intuition into compact 5D geometry.'},
    {'chapter': 2, 'title': 'Recursive Field Ladders', 'pillar_range': [842, 846], 'status': 'working synthesis', 'summary': 'Tracks how compactification motifs repeat as the reader climbs from 5D to 7D constraints.'},
    {'chapter': 3, 'title': 'Gauge Memory and Phase', 'pillar_range': [847, 851], 'status': 'cross-checked notes', 'summary': 'Connects phase memory, braid bookkeeping, and mid-chain gauge narration for Sprint BA.'},
    {'chapter': 4, 'title': 'Higher-Dimensional Closure', 'pillar_range': [852, 856], 'status': 'research draft', 'summary': 'Summarizes how 8D through 10D sectors tighten anomaly, flux, and landscape language.'},
    {'chapter': 5, 'title': 'Reader Synthesis Window', 'pillar_range': [857, 860], 'status': 'editorial preview', 'summary': 'Frames the 11D capstone as a reading guide with explicit epistemic caveats and review prompts.'},
]

SPRINT_BA_DIMENSIONAL_CHAIN = [
    {'step': 1, 'from_dim': 4, 'to_dim': 5, 'mechanism': 'KK compactification anchor', 'pillar': 'P837'},
    {'step': 2, 'from_dim': 5, 'to_dim': 6, 'mechanism': 'scalar closure lift', 'pillar': 'P840'},
    {'step': 3, 'from_dim': 6, 'to_dim': 7, 'mechanism': 'torsion-informed flavor extension', 'pillar': 'P844'},
    {'step': 4, 'from_dim': 7, 'to_dim': 8, 'mechanism': 'Wilson-line gauge routing', 'pillar': 'P848'},
    {'step': 5, 'from_dim': 8, 'to_dim': 9, 'mechanism': 'anomaly-cancellation refinement', 'pillar': 'P851'},
    {'step': 6, 'from_dim': 9, 'to_dim': 10, 'mechanism': 'flux landscape bookkeeping', 'pillar': 'P855'},
    {'step': 7, 'from_dim': 10, 'to_dim': 11, 'mechanism': 'Horava-Witten capstone reduction', 'pillar': 'P860'},
]


def get_chapter(chapter_id: int) -> dict:
    """Return one Sprint BA chapter by id."""
    for chapter in SPRINT_BA_CHAPTERS:
        if chapter['chapter'] == chapter_id:
            return chapter
    raise KeyError(f'Unknown chapter: {chapter_id}')


def export_chapter_latex(chapter: dict) -> str:
    """Export a minimal LaTeX fragment with a CC-BY header comment."""
    start, end = chapter['pillar_range']
    return (
        '% CC-BY 4.0\n'
        '\\documentclass{article}\n'
        '\\begin{document}\n'
        f"\\section*{{Chapter {chapter['chapter']}: {chapter['title']}}}\n"
        f"Pillars: P{start}--P{end}\\\\\n"
        f"Status: {chapter['status']}\\\\\n"
        f"{chapter['summary']}\n"
        '\\end{document}\n'
    )
