# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Local, offline hashed n-gram dense projector for Merlin/PsiCat retrieval.

ADJACENT TRACK.  This is the "token-to-coordinate" translation layer that was
missing between raw query text and Merlin's existing retrieval and toroidal
routing surfaces: a deterministic function from text to a fixed-dimensional
dense vector, computed entirely locally with no network call, no third-party
model weights, and no training step.

What this honestly is:

* a feature-hashed bag of character n-grams (3-, 4-, 5-grams) plus whole
  tokens, each hashed with BLAKE2b into a signed bucket of a fixed-size
  vector, then L2-normalised;
* a classic, well-understood sketching technique (the "hashing trick"), not
  a trained neural embedding model and not a claim about semantic
  understanding;
* fully deterministic: the same text always produces the same vector, on
  any machine, with no dependency on ``PYTHONHASHSEED`` or external services.

What this is not:

* it is not a projection onto the 5D Kaluza-Klein manifold and makes no
  hardgate physics claim;
* it is not a replacement for BM25, which the toroidal-navigation lane
  (``merlin_toroidal_router``) already treats as the retrieval authority;
* it is not promoted into any default-on ranking path.  Like every other
  opt-in upgrade in this lane, it ships behind a default-OFF flag
  (``MERLIN_SEMANTIC_EMBEDDER_RANKING`` in ``merlin_rag``) and must clear the
  same flag A/B harness (``merlin_flag_ab.run_flag_ab``) before promotion.

Why add it at all: character n-grams give partial credit for morphological
overlap ("neutrino" / "neutrinos") that whole-token hashing (the existing
``merlin_toroidal_geometry.phase_sketch``) and exact-token Jaccard/BM25 both
miss.  ``merlin_retrieval_eval.evaluate_rankers(include_embedder=True)``
measures, rather than asserts, whether that partial credit actually improves
recall/MRR on the labelled pillar corpus.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np

from .merlin_retrieval_scoring import token_list

STATUS_LABEL = "ADJACENT_TRACK"
METHOD = "hashed_char_ngram_feature_vector_cosine"
DEFAULT_EMBED_DIMS = 256
NGRAM_SIZES = (3, 4, 5)
WHOLE_TOKEN_WEIGHT = 2.0


def _ngrams(token: str, sizes: Sequence[int] = NGRAM_SIZES) -> Iterable[str]:
    padded = f"#{token}#"
    for size in sizes:
        if len(padded) < size:
            continue
        for i in range(len(padded) - size + 1):
            yield padded[i : i + size]


def _feature_hash(feature: str, dims: int) -> tuple[int, int]:
    """Deterministic (index, sign) bucket for a feature string."""
    digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
    index = int.from_bytes(digest[:4], "big") % dims
    sign = 1.0 if (digest[4] & 1) else -1.0
    return index, sign


def embed_tokens(tokens: Iterable[str], *, dims: int = DEFAULT_EMBED_DIMS) -> np.ndarray:
    """Deterministic hashed bag-of-character-n-gram embedding (feature hashing).

    Signed feature hashing (Weinberger et al.) keeps the expected inner
    product between two hashed vectors close to the inner product of the
    underlying sparse feature counts, which is why cosine similarity on the
    hashed vector is a reasonable (if lossy) stand-in for n-gram overlap.
    """
    if dims < 16 or dims > 4096:
        raise ValueError("dims must be in [16, 4096]")
    vector = np.zeros(int(dims), dtype=np.float64)
    for raw in tokens:
        token = str(raw)
        if not token:
            continue
        for gram in _ngrams(token):
            index, sign = _feature_hash(gram, dims)
            vector[index] += sign
        index, sign = _feature_hash(f"@{token}", dims)
        vector[index] += sign * WHOLE_TOKEN_WEIGHT
    norm = float(np.linalg.norm(vector))
    if norm > 0.0:
        vector = vector / norm
    return vector


def embed_text(text: str, *, dims: int = DEFAULT_EMBED_DIMS) -> np.ndarray:
    return embed_tokens(token_list(text), dims=dims)


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    denom = float(np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
    if denom <= 0.0:
        return 0.0
    return float(np.dot(vector_a, vector_b) / denom)


class EmbedderIndex:
    """Small in-memory dense index over pre-embedded documents."""

    def __init__(self, documents: Sequence[Sequence[str]], *, dims: int = DEFAULT_EMBED_DIMS) -> None:
        self.dims = int(dims)
        self.vectors = [embed_tokens(doc, dims=self.dims) for doc in documents]

    def __len__(self) -> int:
        return len(self.vectors)

    def rank(self, query_tokens: Iterable[str], *, top_k: int = 5) -> list[tuple[int, float]]:
        query_vector = embed_tokens(query_tokens, dims=self.dims)
        scored = [(i, cosine_similarity(query_vector, vector)) for i, vector in enumerate(self.vectors)]
        scored = [item for item in scored if item[1] > 0.0]
        scored.sort(key=lambda item: (-item[1], item[0]))
        return scored[: max(0, int(top_k))]


def embedder_similarity_report(
    query: str, documents: Sequence[str], *, top_k: int = 5, dims: int = DEFAULT_EMBED_DIMS
) -> dict[str, Any]:
    """Rank arbitrary documents by hashed n-gram cosine similarity to a query."""
    doc_tokens = [token_list(doc) for doc in documents]
    index = EmbedderIndex(doc_tokens, dims=dims)
    ranked = index.rank(token_list(query), top_k=top_k)
    return {
        "status": STATUS_LABEL,
        "method": METHOD,
        "dims": int(dims),
        "document_count": len(documents),
        "results": [{"index": i, "similarity": round(score, 4)} for i, score in ranked],
    }


def pillar_embedder_report(query: str, *, top_k: int = 5, dims: int = DEFAULT_EMBED_DIMS) -> dict[str, Any]:
    """Rank Merlin's pillar knowledge base by hashed n-gram cosine similarity.

    BM25 remains the authority (see ``merlin_toroidal_router.toroidal_rank``);
    this reports the embedder ranking alongside BM25 and their agreement, the
    same honesty pattern used for the integer toroidal sketch.
    """
    from .merlin_rag import PILLAR_KNOWLEDGE
    from .merlin_retrieval_scoring import BM25Index, jaccard_overlap

    corpus = [
        token_list(" ".join(str(p.get(field, "")) for field in ("id", "name", "text", "gate")))
        for p in PILLAR_KNOWLEDGE
    ]
    ids = [p.get("id") for p in PILLAR_KNOWLEDGE]
    query_tokens = token_list(query)
    query_set = set(query_tokens)

    embedder_index = EmbedderIndex(corpus, dims=dims)
    embedder_ranked = embedder_index.rank(query_tokens, top_k=top_k)

    bm25_index = BM25Index(corpus)
    bm25_ranked = bm25_index.rank(query_tokens, top_k=top_k)

    embedder_ids = {i for i, _ in embedder_ranked}
    bm25_ids = {i for i, _ in bm25_ranked}
    agreement = round(len(embedder_ids & bm25_ids) / max(len(bm25_ids), 1), 4) if bm25_ids else 0.0

    return {
        "status": STATUS_LABEL,
        "method": METHOD,
        "authority": "bm25",
        "embedder": [
            {
                "id": PILLAR_KNOWLEDGE[i].get("id"),
                "name": PILLAR_KNOWLEDGE[i].get("name"),
                "similarity": round(score, 4),
                "jaccard": round(jaccard_overlap(query_set, set(corpus[i])), 4),
            }
            for i, score in embedder_ranked
        ],
        "bm25_top_k_agreement": agreement,
        "pillar_count": len(ids),
    }


__all__ = [
    "DEFAULT_EMBED_DIMS",
    "METHOD",
    "STATUS_LABEL",
    "EmbedderIndex",
    "cosine_similarity",
    "embed_text",
    "embed_tokens",
    "embedder_similarity_report",
    "pillar_embedder_report",
]
