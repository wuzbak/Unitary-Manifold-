# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Shared lexical retrieval scoring for Merlin (tokens, Jaccard, BM25)."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable, Sequence

TOKEN_RE = re.compile(r"[a-z0-9_ΔβΩ²³⁴⁵]+", re.IGNORECASE)
BM25_K1 = 1.5
BM25_B = 0.75


def token_list(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


def token_set(text: str) -> set[str]:
    return set(token_list(text))


def jaccard_overlap(query_tokens: set[str], sample_tokens: set[str]) -> float:
    if not query_tokens or not sample_tokens:
        return 0.0
    return len(query_tokens & sample_tokens) / max(len(query_tokens | sample_tokens), 1)


class BM25Index:
    """Small in-memory Okapi BM25 index over pre-tokenised documents."""

    def __init__(self, documents: Sequence[Iterable[str]], *, k1: float = BM25_K1, b: float = BM25_B) -> None:
        self.k1 = float(k1)
        self.b = float(b)
        self.term_counts = [Counter(doc) for doc in documents]
        self.lengths = [sum(counts.values()) for counts in self.term_counts]
        self.average_length = (sum(self.lengths) / len(self.lengths)) if self.lengths else 0.0
        document_frequency: Counter[str] = Counter()
        for counts in self.term_counts:
            document_frequency.update(counts.keys())
        n_docs = len(self.term_counts)
        self.idf = {
            term: math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
            for term, df in document_frequency.items()
        }

    def __len__(self) -> int:
        return len(self.term_counts)

    def score(self, query_tokens: Iterable[str], index: int) -> float:
        counts = self.term_counts[index]
        length = self.lengths[index]
        norm = self.k1 * (1.0 - self.b + self.b * (length / self.average_length if self.average_length else 0.0))
        total = 0.0
        for term in set(query_tokens):
            tf = counts.get(term, 0)
            if tf:
                total += self.idf.get(term, 0.0) * (tf * (self.k1 + 1.0)) / (tf + norm)
        return total

    def rank(self, query_tokens: Iterable[str], *, top_k: int = 5) -> list[tuple[int, float]]:
        terms = list(query_tokens)
        scored = [(i, self.score(terms, i)) for i in range(len(self))]
        scored = [item for item in scored if item[1] > 0.0]
        scored.sort(key=lambda item: (-item[1], item[0]))
        return scored[: max(0, int(top_k))]


__all__ = ["BM25Index", "TOKEN_RE", "jaccard_overlap", "token_list", "token_set"]
