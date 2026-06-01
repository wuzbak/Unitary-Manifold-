from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

LABEL_MAP = {
    "GEOMETRIC_PREDICTION": "DERIVED",
    "DERIVED": "DERIVED",
    "ALGEBRAIC": "DERIVED",
    "CONSTRAINED": "CONSTRAINED",
    "OPEN_GAP": "ARCHITECTURE_LIMIT",
    "ARCHITECTURE_LIMIT": "ARCHITECTURE_LIMIT",
}
MAX_SNIPPET_LINES = 6


@dataclass
class Chunk:
    path: str
    label: str
    text: str


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


def build_chunks(paths: Iterable[Path]) -> List[Chunk]:
    chunks: List[Chunk] = []
    for path in paths:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        upper = raw.upper()
        label = "CONSTRAINED"
        for candidate in ["ARCHITECTURE_LIMIT", "OPEN_GAP", "CONSTRAINED", "DERIVED", "GEOMETRIC_PREDICTION"]:
            if candidate in upper:
                label = LABEL_MAP.get(candidate, "CONSTRAINED")
                break
        chunks.append(Chunk(path=str(path), label=label, text=raw[:4000]))
    return chunks


def answer_with_labels(question: str, chunks: List[Chunk]) -> Dict[str, str]:
    q_tokens = set(_tokenize(question))
    best: Chunk | None = None
    best_score = -1
    for chunk in chunks:
        c_tokens = set(_tokenize(chunk.text))
        score = len(q_tokens & c_tokens)
        if score > best_score:
            best = chunk
            best_score = score
    if not best:
        return {
            "answer": "No indexed context available.",
            "epistemic_label": "ARCHITECTURE_LIMIT",
            "source": "none",
        }
    snippet = best.text.strip().splitlines()[:MAX_SNIPPET_LINES]
    return {
        "answer": " ".join(line.strip() for line in snippet if line.strip())[:900],
        "epistemic_label": best.label,
        "source": best.path,
    }
