# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Bounded, immutable exact-vector reference index and retrieval evaluator.

This is an offline oracle, not an embedding service, ANN backend, or RAG
controller. A hit identifies source evidence; it does not establish entailment.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, Mapping, Sequence

VECTOR_INDEX_SCHEMA_VERSION = "az_exact_vector_index_v1"
_HASH = re.compile(r"^[0-9a-f]{64}$")
_METRICS = frozenset({"cosine", "l2"})


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _vector(name: str, value: Sequence[float], dimension: int) -> tuple[float, ...]:
    if isinstance(value, (str, bytes)):
        raise ValueError(f"{name} must be a numeric sequence.")
    try:
        result = tuple(value)
    except TypeError as exc:
        raise ValueError(f"{name} must be a numeric sequence.") from exc
    if len(result) != dimension:
        raise ValueError(f"{name} dimension does not match the manifest.")
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in result):
        raise ValueError(f"{name} must contain finite numbers, not booleans.")
    result = tuple(float(item) for item in result)
    if any(not math.isfinite(item) for item in result):
        raise ValueError(f"{name} must contain only finite numbers.")
    return result


def _norm(vector: Sequence[float]) -> float:
    return math.hypot(*vector)


def _freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("citation_metadata keys must be strings.")
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise ValueError("citation_metadata must contain only finite JSON values.")


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True)
class EmbeddingManifest:
    """Pinned encoder, vector, corpus, and owner identity for one index generation."""

    model_revision: str
    dimension: int
    normalized: bool
    metric: str
    corpus_snapshot_id: str
    preprocessing_version: str
    owner_scope: str

    def __post_init__(self) -> None:
        _text("model_revision", self.model_revision)
        _text("preprocessing_version", self.preprocessing_version)
        _text("owner_scope", self.owner_scope)
        if type(self.dimension) is not int or self.dimension <= 0:
            raise ValueError("dimension must be a positive integer.")
        if type(self.normalized) is not bool:
            raise ValueError("normalized must be a boolean.")
        if self.metric not in _METRICS:
            raise ValueError(f"metric must be one of {sorted(_METRICS)}.")
        if not isinstance(self.corpus_snapshot_id, str) or not _HASH.fullmatch(self.corpus_snapshot_id):
            raise ValueError("corpus_snapshot_id must be a lowercase SHA-256 digest.")


@dataclass(frozen=True)
class VectorDocument:
    """One exact-search candidate with explicit, immutable source evidence."""

    document_id: str
    owner_scope: str
    vector: tuple[float, ...]
    evidence_path: str
    source_hash: str
    citation_metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        _text("document_id", self.document_id)
        _text("owner_scope", self.owner_scope)
        _text("evidence_path", self.evidence_path)
        try:
            vector = tuple(self.vector)
        except TypeError as exc:
            raise ValueError("document vector must be a numeric sequence.") from exc
        if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in vector):
            raise ValueError("document vector must contain finite numbers, not booleans.")
        vector = tuple(float(item) for item in vector)
        if any(not math.isfinite(item) for item in vector):
            raise ValueError("document vector must contain only finite numbers.")
        object.__setattr__(self, "vector", vector)
        if not isinstance(self.source_hash, str) or not _HASH.fullmatch(self.source_hash):
            raise ValueError("source_hash must be a lowercase SHA-256 digest.")
        try:
            metadata = json.loads(_canonical_json(self.citation_metadata))
        except (TypeError, ValueError) as exc:
            raise ValueError("citation_metadata must be a finite JSON object.") from exc
        if not isinstance(metadata, dict):
            raise ValueError("citation_metadata must be a JSON object.")
        object.__setattr__(self, "citation_metadata", _freeze_json(metadata))


def _document_payload(document: VectorDocument) -> dict[str, Any]:
    return {
        "document_id": document.document_id,
        "owner_scope": document.owner_scope,
        "vector": list(document.vector),
        "evidence_path": document.evidence_path,
        "source_hash": document.source_hash,
        "citation_metadata": _thaw_json(document.citation_metadata),
    }


def corpus_content_identity(documents: Sequence[VectorDocument]) -> str:
    """Return the canonical identity to pin in an EmbeddingManifest."""
    records = tuple(documents)
    if any(not isinstance(item, VectorDocument) for item in records):
        raise ValueError("documents must contain VectorDocument values.")
    ids = [item.document_id for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError("document IDs must be unique.")
    payload = [_document_payload(item) for item in sorted(records, key=lambda doc: doc.document_id)]
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _manifest_payload(manifest: EmbeddingManifest) -> dict[str, Any]:
    return {
        "model_revision": manifest.model_revision,
        "dimension": manifest.dimension,
        "normalized": manifest.normalized,
        "metric": manifest.metric,
        "corpus_snapshot_id": manifest.corpus_snapshot_id,
        "preprocessing_version": manifest.preprocessing_version,
        "owner_scope": manifest.owner_scope,
    }


def _generation_payload(manifest: EmbeddingManifest, documents: Sequence[VectorDocument]) -> dict[str, Any]:
    return {
        "schema_version": VECTOR_INDEX_SCHEMA_VERSION,
        "manifest": _manifest_payload(manifest),
        "documents": [_document_payload(doc) for doc in documents],
    }


@dataclass(frozen=True)
class SearchHit:
    document: VectorDocument
    score: float


@dataclass(frozen=True)
class ExactVectorIndex:
    """Immutable exact reference index for a single owner and corpus generation."""

    manifest: EmbeddingManifest
    documents: tuple[VectorDocument, ...]
    schema_version: str = VECTOR_INDEX_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.manifest, EmbeddingManifest):
            raise ValueError("manifest must be an EmbeddingManifest.")
        if self.schema_version != VECTOR_INDEX_SCHEMA_VERSION:
            raise ValueError(f"Unsupported vector index schema: {self.schema_version!r}.")
        try:
            documents = tuple(self.documents)
        except TypeError as exc:
            raise ValueError("documents must be an iterable of VectorDocument values.") from exc
        if any(not isinstance(doc, VectorDocument) for doc in documents):
            raise ValueError("documents must contain only VectorDocument values.")
        documents = tuple(sorted(documents, key=lambda doc: doc.document_id))
        ids = [doc.document_id for doc in documents]
        if len(ids) != len(set(ids)):
            raise ValueError("document IDs must be unique.")
        for doc in documents:
            if doc.owner_scope != self.manifest.owner_scope:
                raise ValueError("Every document must match the manifest owner_scope.")
            vector = _vector("document vector", doc.vector, self.manifest.dimension)
            magnitude = _norm(vector)
            if not math.isfinite(magnitude):
                raise ValueError("document vector magnitude must be finite.")
            if self.manifest.metric == "cosine" and magnitude == 0:
                raise ValueError("cosine vectors cannot be zero.")
            if self.manifest.normalized and not math.isclose(magnitude, 1.0, rel_tol=1e-6, abs_tol=1e-6):
                raise ValueError("normalized manifest requires unit-length document vectors.")
        if corpus_content_identity(documents) != self.manifest.corpus_snapshot_id:
            raise ValueError("corpus_snapshot_id does not match document content.")
        object.__setattr__(self, "documents", documents)

    @property
    def generation_ref(self) -> str:
        payload = _generation_payload(self.manifest, self.documents)
        return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()

    def search(
        self,
        query_vector: Sequence[float],
        *,
        query_manifest: EmbeddingManifest,
        owner_scope: str,
        top_k: int,
    ) -> tuple[SearchHit, ...]:
        """Return exact top-k hits; owner filtering precedes all candidate scoring."""
        if not isinstance(query_manifest, EmbeddingManifest):
            raise ValueError("query_manifest must be an EmbeddingManifest.")
        if owner_scope != self.manifest.owner_scope or query_manifest.owner_scope != owner_scope:
            raise ValueError("Requested owner_scope does not match the index and query.")
        if query_manifest != self.manifest:
            raise ValueError("query manifest is incompatible with the indexed corpus or encoder.")
        if type(top_k) is not int or top_k < 0:
            raise ValueError("top_k must be a non-negative integer.")
        query = _vector("query_vector", query_vector, self.manifest.dimension)
        query_norm = _norm(query)
        if not math.isfinite(query_norm):
            raise ValueError("query vector magnitude must be finite.")
        if self.manifest.metric == "cosine" and query_norm == 0:
            raise ValueError("cosine query vectors cannot be zero.")
        if self.manifest.normalized and not math.isclose(query_norm, 1.0, rel_tol=1e-6, abs_tol=1e-6):
            raise ValueError("normalized manifest requires a unit-length query vector.")
        candidates = tuple(doc for doc in self.documents if doc.owner_scope == owner_scope)
        scored: list[SearchHit] = []
        for document in candidates:
            if self.manifest.metric == "cosine":
                document_norm = _norm(document.vector)
                score = math.fsum(
                    (a / query_norm) * (b / document_norm)
                    for a, b in zip(query, document.vector)
                )
            else:
                score = math.hypot(*(a - b for a, b in zip(query, document.vector)))
            if not math.isfinite(score):
                raise ValueError("vector score is not finite for the supplied numeric range.")
            scored.append(SearchHit(document, score))
        if self.manifest.metric == "cosine":
            scored.sort(key=lambda hit: (-hit.score, hit.document.document_id))
        else:
            scored.sort(key=lambda hit: (hit.score, hit.document.document_id))
        return tuple(scored[:top_k])

    def delete(self, document_id: str) -> "ExactVectorIndex":
        """Return a new generation; old saved generations remain loadable until separately purged."""
        _text("document_id", document_id)
        remaining = tuple(doc for doc in self.documents if doc.document_id != document_id)
        if len(remaining) == len(self.documents):
            raise ValueError(f"Unknown document_id: {document_id!r}.")
        manifest = replace(self.manifest, corpus_snapshot_id=corpus_content_identity(remaining))
        return ExactVectorIndex(manifest, remaining)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}.")
        result[key] = value
    return result


def save_index(index: ExactVectorIndex, directory: str | Path) -> Path:
    """Durably publish canonical JSON without overwriting an existing generation.

    The caller must provide an existing, durably established directory.
    """
    from .artifact_io import publish_immutable

    if not isinstance(index, ExactVectorIndex):
        raise ValueError("index must be an ExactVectorIndex.")
    payload = _generation_payload(index.manifest, index.documents)
    payload["generation_ref"] = index.generation_ref
    content = (_canonical_json(payload) + "\n").encode("utf-8")
    return publish_immutable(directory, index.generation_ref, content)


def load_index(directory: str | Path, generation_ref: str) -> ExactVectorIndex:
    """Load a persisted generation and verify both corpus and full-generation hashes."""
    if not isinstance(generation_ref, str) or not _HASH.fullmatch(generation_ref):
        raise ValueError("generation_ref must be a lowercase SHA-256 digest.")
    path = Path(directory) / f"{generation_ref}.json"
    if path.is_symlink():
        raise ValueError("Index snapshot cannot be a symbolic link.")
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Invalid JSON number: {value}")),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Unable to read a valid vector index snapshot.") from exc
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "manifest", "documents", "generation_ref"}:
        raise ValueError("Malformed vector index snapshot schema.")
    if payload["schema_version"] != VECTOR_INDEX_SCHEMA_VERSION or payload["generation_ref"] != generation_ref:
        raise ValueError("Vector index snapshot version or generation reference mismatch.")
    raw_manifest = payload["manifest"]
    expected_manifest_fields = {
        "model_revision", "dimension", "normalized", "metric", "corpus_snapshot_id",
        "preprocessing_version", "owner_scope",
    }
    if not isinstance(raw_manifest, dict) or set(raw_manifest) != expected_manifest_fields:
        raise ValueError("Malformed embedding manifest schema.")
    manifest = EmbeddingManifest(**raw_manifest)
    if not isinstance(payload["documents"], list):
        raise ValueError("documents must be a JSON array.")
    documents = []
    for item in payload["documents"]:
        if not isinstance(item, dict) or set(item) != {
            "document_id", "owner_scope", "vector", "evidence_path", "source_hash", "citation_metadata",
        }:
            raise ValueError("Malformed vector document schema.")
        vector = _vector("document vector", item["vector"], manifest.dimension)
        documents.append(VectorDocument(
            item["document_id"], item["owner_scope"], vector,
            item["evidence_path"], item["source_hash"], item["citation_metadata"],
        ))
    index = ExactVectorIndex(manifest, tuple(documents))
    if index.generation_ref != generation_ref:
        raise ValueError("Vector index generation hash verification failed.")
    return index


@dataclass(frozen=True)
class RetrievalQuery:
    query_id: str
    vector: tuple[float, ...]
    manifest: EmbeddingManifest
    judgments: Mapping[str, float]


@dataclass(frozen=True)
class RetrievalEvaluation:
    recall_at_k: float | None
    ndcg_at_k: float | None
    k: int
    query_count: int
    evaluated_query_count: int
    skipped_no_relevant: int
    skipped_no_queries: bool
    denominator: str


def evaluate_retrieval(
    index: ExactVectorIndex,
    queries: Sequence[RetrievalQuery],
    *,
    owner_scope: str,
    k: int,
) -> RetrievalEvaluation:
    """Macro-average over queries with positive judgments; require k > 0.

    Recall divides by every positively judged document, including absent corpus
    documents. nDCG uses exponential gain and logarithmic rank discount, with
    unjudged hits graded zero. This does not estimate statistical uncertainty.
    """
    if not isinstance(index, ExactVectorIndex):
        raise ValueError("index must be an ExactVectorIndex.")
    if owner_scope != index.manifest.owner_scope:
        raise ValueError("Requested owner_scope does not match the index.")
    if type(k) is not int or k <= 0:
        raise ValueError("k must be a positive integer; nDCG@0 is undefined.")
    if isinstance(queries, (str, bytes)):
        raise ValueError("queries must be a sequence of RetrievalQuery values.")
    queries = tuple(queries)
    if any(not isinstance(query, RetrievalQuery) for query in queries):
        raise ValueError("queries must contain only RetrievalQuery values.")
    query_ids = [_text("query_id", query.query_id) for query in queries]
    if len(set(query_ids)) != len(query_ids):
        raise ValueError("query IDs must be unique; implicit duplicate weighting is not allowed.")
    if not queries:
        return RetrievalEvaluation(None, None, k, 0, 0, 0, True, "no queries")
    recall_values: list[float] = []
    ndcg_values: list[float] = []
    skipped = 0
    for query in queries:
        hits = index.search(
            query.vector, query_manifest=query.manifest, owner_scope=owner_scope, top_k=k,
        )
        judgments = dict(query.judgments)
        if any(not isinstance(doc_id, str) or not doc_id.strip() for doc_id in judgments):
            raise ValueError("judgment document IDs must be non-empty strings.")
        gains: dict[str, float] = {}
        for doc_id, relevance in judgments.items():
            if isinstance(relevance, bool) or not isinstance(relevance, (int, float)):
                raise ValueError("judgment relevance must be finite and non-negative.")
            try:
                numeric = float(relevance)
                if not math.isfinite(numeric) or numeric < 0:
                    raise ValueError("judgment relevance must be finite and non-negative.")
                if numeric >= 1024:
                    raise ValueError("judgment gain exceeds the supported finite numeric range.")
                gain = math.expm1(numeric * math.log(2.0))
            except OverflowError as exc:
                raise ValueError("judgment gain exceeds the supported finite numeric range.") from exc
            if not math.isfinite(gain) or (numeric > 0 and gain <= 0):
                raise ValueError("judgment gain is not representable as a finite positive number.")
            gains[doc_id] = gain
        relevant = {doc_id for doc_id, relevance in judgments.items() if relevance > 0}
        if not relevant:
            skipped += 1
            continue
        retrieved = [hit.document.document_id for hit in hits]
        recall_values.append(len(relevant.intersection(retrieved)) / len(relevant))

        def dcg(values: Sequence[float]) -> float:
            try:
                score = math.fsum(value / math.log2(rank + 2) for rank, value in enumerate(values))
            except OverflowError as exc:
                raise ValueError("DCG exceeds the supported finite numeric range.") from exc
            if not math.isfinite(score):
                raise ValueError("DCG must be finite.")
            return score

        actual = [gains.get(doc_id, 0.0) for doc_id in retrieved]
        ideal = sorted(gains.values(), reverse=True)[:k]
        ideal_dcg = dcg(ideal)
        if ideal_dcg <= 0:
            raise ValueError("nDCG denominator is not representable as a positive number.")
        ndcg_values.append(dcg(actual) / ideal_dcg)
    denominator = f"{len(recall_values)} queries with at least one positively judged relevant document"
    return RetrievalEvaluation(
        math.fsum(recall_values) / len(recall_values) if recall_values else None,
        math.fsum(ndcg_values) / len(ndcg_values) if ndcg_values else None,
        k, len(queries), len(recall_values), skipped, False,
        denominator if recall_values else "no queries with relevant judgments",
    )
