# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Regression tests for the bounded exact-vector reference index."""

from __future__ import annotations

import hashlib
import json
import math
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import stat
import uuid

import pytest

from src.infrastructure.vector_index import (
    EmbeddingManifest,
    ExactVectorIndex,
    RetrievalQuery,
    VectorDocument,
    corpus_content_identity,
    evaluate_retrieval,
    load_index,
    save_index,
)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def doc(identifier: str, vector, *, owner: str = "tenant-a") -> VectorDocument:
    return VectorDocument(
        identifier, owner, tuple(vector), f"corpus/{identifier}.txt", digest(identifier),
        {"citation": {"title": identifier, "locator": "section 1"}},
    )


def index_for(documents, *, metric="cosine", normalized=False) -> ExactVectorIndex:
    documents = tuple(documents)
    manifest = EmbeddingManifest(
        "encoder@revision-3", 2, normalized, metric,
        corpus_content_identity(documents), "preprocess-v2", "tenant-a",
    )
    return ExactVectorIndex(manifest, documents)


def test_exact_cosine_and_l2_match_independent_brute_force_and_ties() -> None:
    documents = (doc("z", (1, 0)), doc("a", (0, 1)), doc("b", (1, 1)))
    query = (1, 0)
    cosine_index = index_for(documents)
    cosine = cosine_index.search(
        query, query_manifest=cosine_index.manifest, owner_scope="tenant-a", top_k=3,
    )
    expected_cosine = sorted(
        ((sum(a * b for a, b in zip(query, item.vector)) /
          ((sum(x * x for x in query) ** 0.5) * (sum(x * x for x in item.vector) ** 0.5)),
          item.document_id) for item in documents),
        key=lambda pair: (-pair[0], pair[1]),
    )
    assert [hit.document.document_id for hit in cosine] == [identifier for _, identifier in expected_cosine]
    assert [hit.score for hit in cosine] == pytest.approx([score for score, _ in expected_cosine])

    l2_index = index_for(documents, metric="l2")
    l2 = l2_index.search(
        query, query_manifest=l2_index.manifest, owner_scope="tenant-a", top_k=3,
    )
    expected_l2 = sorted(
        ((sum((a - b) ** 2 for a, b in zip(query, item.vector)) ** 0.5, item.document_id)
         for item in documents),
        key=lambda pair: (pair[0], pair[1]),
    )
    assert [hit.document.document_id for hit in l2] == [identifier for _, identifier in expected_l2]
    assert [hit.score for hit in l2] == pytest.approx([score for score, _ in expected_l2])
    assert [hit.document.document_id for hit in cosine_index.search(
        (1, 1), query_manifest=cosine_index.manifest, owner_scope="tenant-a", top_k=2,
    )] == ["b", "a"]


def test_scope_and_manifest_compatibility_fail_closed() -> None:
    index = index_for((doc("a", (1, 0)),))
    with pytest.raises(ValueError, match="owner_scope"):
        index.search((1, 0), query_manifest=index.manifest, owner_scope="tenant-b", top_k=1)
    for changed in (
        EmbeddingManifest("encoder@revision-4", 2, False, "cosine", index.manifest.corpus_snapshot_id, "preprocess-v2", "tenant-a"),
        EmbeddingManifest("encoder@revision-3", 2, False, "cosine", index.manifest.corpus_snapshot_id, "preprocess-v3", "tenant-a"),
        EmbeddingManifest("encoder@revision-3", 3, False, "cosine", index.manifest.corpus_snapshot_id, "preprocess-v2", "tenant-a"),
        EmbeddingManifest("encoder@revision-3", 2, True, "cosine", index.manifest.corpus_snapshot_id, "preprocess-v2", "tenant-a"),
    ):
        with pytest.raises(ValueError, match="incompatible"):
            index.search((1, 0), query_manifest=changed, owner_scope="tenant-a", top_k=1)
    with pytest.raises(ValueError, match="owner_scope"):
        index.search(
            (1, 0), query_manifest=EmbeddingManifest(
                "encoder@revision-3", 2, False, "cosine", index.manifest.corpus_snapshot_id,
                "preprocess-v2", "tenant-b",
            ), owner_scope="tenant-b", top_k=1,
        )


@pytest.mark.parametrize("vector", [(True, 1), (float("nan"), 1), (float("inf"), 1), (0, 0)])
def test_invalid_cosine_query_rejected(vector) -> None:
    index = index_for((doc("a", (1, 0)),))
    with pytest.raises(ValueError):
        index.search(vector, query_manifest=index.manifest, owner_scope="tenant-a", top_k=1)


@pytest.mark.parametrize("top_k", [-1, True, 1.5, "1"])
def test_invalid_top_k_rejected(top_k) -> None:
    index = index_for((doc("a", (1, 0)),))
    with pytest.raises(ValueError, match="top_k"):
        index.search((1, 0), query_manifest=index.manifest, owner_scope="tenant-a", top_k=top_k)


def test_index_rejects_bad_documents_duplicates_mixed_scope_and_stale_identity() -> None:
    first = doc("a", (1, 0))
    with pytest.raises(ValueError, match="unique"):
        index_for((first, first))
    with pytest.raises(ValueError, match="owner_scope"):
        index_for((first, doc("b", (0, 1), owner="tenant-b")))
    with pytest.raises(ValueError, match="corpus_snapshot_id"):
        ExactVectorIndex(
            EmbeddingManifest("e", 2, False, "l2", digest("stale"), "p1", "tenant-a"),
            (first,),
        )
    with pytest.raises(ValueError, match="dimension"):
        index_for((doc("short", (1,)),))
    with pytest.raises(ValueError, match="normalized"):
        index_for((doc("not-unit", (2, 0)),), normalized=True)


def test_evidence_metadata_is_preserved_and_immutable() -> None:
    document = doc("source", (1, 0))
    index = index_for((document,))
    hit = index.search((1, 0), query_manifest=index.manifest, owner_scope="tenant-a", top_k=1)[0]
    assert hit.document.evidence_path == "corpus/source.txt"
    assert hit.document.source_hash == digest("source")
    assert hit.document.citation_metadata["citation"]["title"] == "source"
    with pytest.raises(TypeError):
        hit.document.citation_metadata["new"] = "value"
    with pytest.raises(TypeError):
        hit.document.citation_metadata["citation"]["title"] = "changed"


def test_delete_returns_new_generation_with_new_identity_and_old_snapshot_unchanged() -> None:
    index = index_for((doc("a", (1, 0)), doc("b", (0, 1))))
    deleted = index.delete("a")
    assert index.generation_ref != deleted.generation_ref
    assert index.manifest.corpus_snapshot_id != deleted.manifest.corpus_snapshot_id
    assert [hit.document.document_id for hit in deleted.search(
        (1, 0), query_manifest=deleted.manifest, owner_scope="tenant-a", top_k=5,
    )] == ["b"]
    assert [item.document_id for item in index.documents] == ["a", "b"]
    with pytest.raises(ValueError, match="Unknown"):
        deleted.delete("a")


def test_persistence_round_trip_and_tamper_detection() -> None:
    directory = Path(__file__).parent / f".vector-index-test-{uuid.uuid4().hex}"
    directory.mkdir()
    try:
        index = index_for((doc("a", (1, 0)), doc("b", (0, 1))))
        path = save_index(index, directory)
        assert path.name == f"{index.generation_ref}.json"
        assert load_index(directory, index.generation_ref) == index
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["documents"][0]["evidence_path"] = "changed"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ValueError, match="corpus_snapshot_id"):
            load_index(directory, index.generation_ref)
    finally:
        shutil.rmtree(directory)


def test_retrieval_metrics_use_judged_relevant_denominator_and_report_undefined() -> None:
    index = index_for((doc("a", (1, 0)), doc("b", (0.8, 0.2)), doc("c", (0, 1))))
    query = RetrievalQuery("q1", (1, 0), index.manifest, {"a": 2, "c": 1})
    result = evaluate_retrieval(index, (query,), owner_scope="tenant-a", k=1)
    assert result.recall_at_k == 0.5
    assert result.ndcg_at_k == 1.0
    assert result.evaluated_query_count == 1
    assert result.denominator == "1 queries with at least one positively judged relevant document"

    empty = evaluate_retrieval(index, (), owner_scope="tenant-a", k=1)
    assert empty.recall_at_k is None and empty.ndcg_at_k is None
    assert empty.skipped_no_queries
    no_relevance = evaluate_retrieval(
        index, (RetrievalQuery("q2", (1, 0), index.manifest, {"a": 0}),),
        owner_scope="tenant-a", k=1,
    )
    assert no_relevance.recall_at_k is None and no_relevance.ndcg_at_k is None
    assert no_relevance.skipped_no_relevant == 1
    assert no_relevance.denominator == "no queries with relevant judgments"


def test_retrieval_evaluator_rejects_boolean_and_negative_judgments() -> None:
    index = index_for((doc("a", (1, 0)),))
    for relevance in (True, -1, float("nan")):
        with pytest.raises(ValueError, match="relevance"):
            evaluate_retrieval(
                index, (RetrievalQuery("q", (1, 0), index.manifest, {"a": relevance}),),
                owner_scope="tenant-a", k=1,
            )


@pytest.mark.parametrize("k", [0, -1, True, 1.5])
def test_evaluation_requires_positive_k_even_without_queries(k) -> None:
    index = index_for((doc("a", (1, 0)),))
    with pytest.raises(ValueError, match="positive integer"):
        evaluate_retrieval(index, (), owner_scope="tenant-a", k=k)


def test_empty_and_skipped_evaluations_do_not_bypass_identity_validation() -> None:
    from dataclasses import replace

    index = index_for((doc("a", (1, 0)),))
    with pytest.raises(ValueError, match="owner_scope"):
        evaluate_retrieval(index, (), owner_scope="tenant-b", k=1)
    wrong_manifest = replace(index.manifest, model_revision="other-encoder")
    with pytest.raises(ValueError, match="incompatible"):
        evaluate_retrieval(
            index, (RetrievalQuery("q", (1, 0), wrong_manifest, {}),),
            owner_scope="tenant-a", k=1,
        )
    with pytest.raises(ValueError, match="zero"):
        evaluate_retrieval(
            index, (RetrievalQuery("q", (0, 0), index.manifest, {}),),
            owner_scope="tenant-a", k=1,
        )
    assert index.search(
        (1, 0), query_manifest=index.manifest, owner_scope="tenant-a", top_k=0,
    ) == ()


def test_duplicate_query_ids_rejected_instead_of_silent_weighting() -> None:
    index = index_for((doc("a", (1, 0)),))
    query = RetrievalQuery("same", (1, 0), index.manifest, {"a": 1})
    with pytest.raises(ValueError, match="query IDs must be unique"):
        evaluate_retrieval(index, (query, query), owner_scope="tenant-a", k=1)


@pytest.mark.parametrize("grade", [1024.0, 1e308, 10 ** 400])
def test_unrepresentable_judgment_gains_fail_with_value_error(grade) -> None:
    index = index_for((doc("a", (1, 0)),))
    with pytest.raises(ValueError, match="gain"):
        evaluate_retrieval(
            index, (RetrievalQuery("q", (1, 0), index.manifest, {"a": grade}),),
            owner_scope="tenant-a", k=1,
        )


def test_ndcg_uses_independently_computed_rank_discount_and_absent_relevance() -> None:
    index = index_for((doc("a", (1, 0)), doc("b", (0, 1))))
    query = RetrievalQuery("q", (1, 0), index.manifest, {"a": 1, "b": 3, "missing": 2})
    result = evaluate_retrieval(index, (query,), owner_scope="tenant-a", k=2)
    assert result.recall_at_k == pytest.approx(2 / 3)
    assert result.ndcg_at_k == pytest.approx(
        (1 + 7 / math.log2(3)) / (7 + 3 / math.log2(3)),
    )


def test_immutable_publication_survives_retry_and_rejects_existing_corruption() -> None:
    directory = Path(__file__).parent / f".vector-index-test-{uuid.uuid4().hex}"
    directory.mkdir()
    try:
        index = index_for((doc("a", (1, 0)),))
        target = save_index(index, directory)
        original = target.read_bytes()
        assert save_index(index, directory) == target
        assert target.read_bytes() == original
        target.write_bytes(b"corrupt")
        with pytest.raises(ValueError):
            save_index(index, directory)
        assert target.read_bytes() == b"corrupt"
        target.unlink()
        evidence = directory / "not-the-index"
        evidence.write_bytes(b"must-not-overwrite")
        target.symlink_to(evidence.name)
        with pytest.raises((ValueError, OSError)):
            save_index(index, directory)
        assert evidence.read_bytes() == b"must-not-overwrite"
    finally:
        shutil.rmtree(directory)


def test_interrupted_publication_never_exposes_partial_generation(monkeypatch) -> None:
    directory = Path(__file__).parent / f".vector-index-test-{uuid.uuid4().hex}"
    directory.mkdir()
    try:
        index = index_for((doc("a", (1, 0)),))
        target = directory / f"{index.generation_ref}.json"

        def interrupted_link(*args, **kwargs):
            assert not target.exists()
            raise OSError("publication interrupted")

        monkeypatch.setattr(os, "link", interrupted_link)
        with pytest.raises(OSError, match="publication interrupted"):
            save_index(index, directory)
        assert not tuple(directory.iterdir())
    finally:
        shutil.rmtree(directory)


def test_snapshot_directory_sync_failure_is_propagated(monkeypatch) -> None:
    directory = Path(__file__).parent / f".vector-index-test-{uuid.uuid4().hex}"
    directory.mkdir()
    real_fsync = os.fsync
    try:
        def failing_fsync(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                raise OSError("directory sync failed")
            return real_fsync(fd)

        monkeypatch.setattr(os, "fsync", failing_fsync)
        with pytest.raises(OSError, match="directory sync failed"):
            save_index(index_for((doc("a", (1, 0)),)), directory)
        assert not list(directory.glob(".*.tmp"))
    finally:
        shutil.rmtree(directory)


def test_concurrent_publication_exposes_one_complete_generation() -> None:
    directory = Path(__file__).parent / f".vector-index-test-{uuid.uuid4().hex}"
    directory.mkdir()
    try:
        index = index_for((doc("a", (1, 0)), doc("b", (0, 1))))
        with ThreadPoolExecutor(max_workers=4) as executor:
            paths = tuple(executor.map(lambda _: save_index(index, directory), range(8)))
        assert len(set(paths)) == 1
        assert load_index(directory, index.generation_ref) == index
        assert list(directory.iterdir()) == [paths[0]]
    finally:
        shutil.rmtree(directory)


def test_saved_old_generation_remains_explicitly_loadable_after_deletion() -> None:
    directory = Path(__file__).parent / f".vector-index-test-{uuid.uuid4().hex}"
    directory.mkdir()
    try:
        original = index_for((doc("a", (1, 0)), doc("b", (0, 1))))
        deleted = original.delete("a")
        save_index(original, directory)
        save_index(deleted, directory)
        assert [doc.document_id for doc in load_index(directory, original.generation_ref).documents] == ["a", "b"]
        loaded_new = load_index(directory, deleted.generation_ref)
        assert [doc.document_id for doc in loaded_new.documents] == ["b"]
        with pytest.raises(ValueError, match="incompatible"):
            loaded_new.search(
                (1, 0), query_manifest=original.manifest, owner_scope="tenant-a", top_k=1,
            )
    finally:
        shutil.rmtree(directory)
