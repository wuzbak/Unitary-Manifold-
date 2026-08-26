# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Python-side TTS preprocessing and chunking helpers."""

from __future__ import annotations

import math
import re

from .constants import DEFAULT_WPM, TTS_MAX_CHARS

GREEK_REPLACEMENTS = {
    r"\phi": "phi",
    r"\Phi": "Phi",
    r"\psi": "psi",
    r"\Psi": "Psi",
    r"\Omega": "Omega",
    r"\omega": "omega",
    r"\mu": "mu",
    r"\nu": "nu",
    r"\alpha": "alpha",
    r"\beta": "beta",
    r"\gamma": "gamma",
    r"\Delta": "Delta",
    r"\delta": "delta",
    r"\Xi": "Xi",
    r"\xi": "xi",
}


def preprocess_math(text: str) -> str:
    """Strip common LaTeX wrappers and replace symbols with readable speech text."""
    if not text:
        return ""

    processed = str(text)
    processed = re.sub(r"\\\[(.*?)\\\]", r" \1 ", processed, flags=re.DOTALL)
    processed = re.sub(r"\\\((.*?)\\\)", r" \1 ", processed, flags=re.DOTALL)
    processed = re.sub(r"\$\$(.*?)\$\$", r" \1 ", processed, flags=re.DOTALL)
    processed = re.sub(r"\$(.*?)\$", r" \1 ", processed, flags=re.DOTALL)
    processed = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r" \1 over \2 ", processed)
    processed = re.sub(r"\\sqrt\{([^{}]+)\}", r" square root of \1 ", processed)
    processed = re.sub(r"[_^]\{([^{}]+)\}", r" \1 ", processed)
    processed = re.sub(r"[_^]([A-Za-z0-9+-]+)", r" \1 ", processed)

    for latex, readable in GREEK_REPLACEMENTS.items():
        processed = processed.replace(latex, readable)

    processed = processed.replace("{", " ").replace("}", " ")
    processed = processed.replace(r"\cdot", " times ")
    processed = processed.replace(r"\times", " times ")
    processed = processed.replace(r"\to", " goes to ")
    processed = processed.replace("\\", " ")
    return " ".join(processed.split())


def chunk_text(text: str, max_chars: int = TTS_MAX_CHARS) -> list[str]:
    """Split text into chunks that respect a maximum length when possible."""
    if max_chars <= 0:
        raise ValueError("max_chars must be positive.")

    cleaned = " ".join(str(text or "").split())
    if not cleaned:
        return []

    words = cleaned.split(" ")
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for word in words:
        projected = current_len + (1 if current else 0) + len(word)
        if current and projected > max_chars:
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
            continue

        if len(word) > max_chars:
            if current:
                chunks.append(" ".join(current))
                current = []
                current_len = 0
            for start in range(0, len(word), max_chars):
                piece = word[start : start + max_chars]
                if len(piece) == max_chars or start + max_chars < len(word):
                    chunks.append(piece)
                else:
                    current = [piece]
                    current_len = len(piece)
            continue

        current.append(word)
        current_len = projected

    if current:
        chunks.append(" ".join(current))

    return chunks


def estimate_reading_time(text: str, wpm: int = DEFAULT_WPM) -> float:
    """Estimate speech duration in seconds for the supplied text."""
    if wpm <= 0:
        raise ValueError("wpm must be positive.")

    words = preprocess_math(text).split()
    if not words:
        return 0.0
    return math.ceil((len(words) / wpm) * 60 * 100) / 100
