# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for PsiCat's editorial literature corpus retrieval (ADJACENT TRACK).

Covers: the ``evaluate_literature_rankers`` benchmark in
``merlin_retrieval_eval``, the default-OFF ``psicat_literature`` key in
``retrieve_context``, and the ``psicat_literature_corpus`` flag wiring in the
A/B harness. These guard Part A of the PsiCat literature-ingestion gap
(governance label ``PSICAT_EDITORIAL_CORPUS``) so it cannot silently regress
or reopen.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine import merlin_flag_ab, merlin_rag
from ox_navigator.engine.merlin_program import build_psicat_literature_training_split
from ox_navigator.engine.merlin_retrieval_eval import (
    LITERATURE_LABELLED_QUERIES,
    evaluate_literature_rankers,
)


# --- evaluate_literature_rankers ---------------------------------------------------------


def test_evaluate_literature_rankers_shape() -> None:
    report = evaluate_literature_rankers()
    assert report["ok"] is True
    assert report["status"] == "ADJACENT_TRACK"
    assert report["governance_label"] == "PSICAT_EDITORIAL_CORPUS"
    assert report["query_count"] == len(LITERATURE_LABELLED_QUERIES)
    assert report["skipped_queries"] == []
    assert set(report["rankers"]) == {"jaccard", "bm25", "rrf"}
    assert "caveat" in report and report["caveat"]


def test_evaluate_literature_rankers_corpus_counts_are_honest() -> None:
    report = evaluate_literature_rankers()
    # Every labelled relevant source must actually exist in the built corpus,
    # otherwise the benchmark would be measuring nothing.
    assert report["corpus_document_count"] >= 400
    assert report["corpus_chunk_count"] >= report["corpus_document_count"]


def test_evaluate_literature_rankers_mrr_is_plausible() -> None:
    report = evaluate_literature_rankers()
    for name, metrics in report["summary"].items():
        assert 0.0 <= metrics["mrr"] <= 1.0, name
        assert 0.0 <= metrics["recall@5"] <= 1.0, name
    # BM25 (lexical, exact-token) should not be worse than chance on a
    # hand-labelled set built from paraphrases of real document titles.
    assert report["summary"]["bm25"]["mrr"] > 0.0


def test_evaluate_literature_rankers_accepts_custom_queries() -> None:
    chunks_report = evaluate_literature_rankers()
    known_source = chunks_report["per_query"][0]["relevant"][0]
    custom = [("a query with no plausible match", (known_source,))]
    report = evaluate_literature_rankers(queries=custom)
    assert report["query_count"] == 1
    assert report["per_query"][0]["relevant"] == [known_source]


def test_evaluate_literature_rankers_skips_unknown_relevant_sources() -> None:
    report = evaluate_literature_rankers(queries=[("nonsense query", ("no/such/file.md",))])
    assert report["query_count"] == 0
    assert report["skipped_queries"] == ["nonsense query"]


# --- retrieve_context / flag wiring ------------------------------------------------------


def test_psicat_literature_corpus_flag_default_off() -> None:
    assert merlin_rag.psicat_literature_corpus_enabled() is False


def test_retrieve_context_literature_key_present_and_empty_by_default() -> None:
    context = merlin_rag.retrieve_context("What is the braided winding number?")
    assert "psicat_literature" in context
    assert context["psicat_literature"] == []


def test_flag_ab_registers_psicat_literature_corpus_variant() -> None:
    assert merlin_rag.PSICAT_LITERATURE_CORPUS_FLAG in merlin_flag_ab.OPT_IN_FLAGS
    report = merlin_flag_ab.run_flag_ab(
        stages=["stage_a_parity_capture"],
        limit_per_stage=1,
        variants={
            "baseline": (),
            "psicat_literature_corpus": (merlin_rag.PSICAT_LITERATURE_CORPUS_FLAG,),
        },
    )
    assert report.get("ok") is not False
    assert "psicat_literature_corpus" in report["summary"]
    assert report["summary"]["psicat_literature_corpus"]["promotable"] is True


def test_enabling_flag_populates_literature_context(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(merlin_rag.PSICAT_LITERATURE_CORPUS_FLAG, "1")
    assert merlin_rag.psicat_literature_corpus_enabled() is True
    context = merlin_rag.retrieve_context("the honest machine")
    assert isinstance(context["psicat_literature"], list)
    assert len(context["psicat_literature"]) > 0


# --- build_psicat_literature_training_split ----------------------------------------------


def test_build_psicat_literature_training_split_shape() -> None:
    report = build_psicat_literature_training_split()
    assert report["ok"] is True
    assert report["status"] == "ADJACENT_TRACK"
    assert report["governance_label"] == "PSICAT_EDITORIAL_CORPUS"
    assert report["validation"]["status"] == "passed"
    assert report["source_document_count"] >= 400
    total = sum(report["split_counts"].values())
    assert total == report["source_document_count"] - report["quality_filters"]["rejection_count"]
    assert report["split_counts"]["train"] > report["split_counts"]["dev"]
    assert report["split_counts"]["train"] > report["split_counts"]["test"]


def test_build_psicat_literature_training_split_records_validate() -> None:
    report = build_psicat_literature_training_split(limit=20)
    for rows in report["splits"].values():
        for record in rows:
            assert record["format_version"] == "merlin_training_jsonl_v1"
            assert record["split"] in {"train", "dev", "test"}
            assert record["kernel_id"] in {"kernel_s", "kernel_p", "kernel_r", "kernel_a", "kernel_g"}
            assert record["response_target"]["answer"]
            assert record["provenance_sources"]
            assert set(record["required_gates"]) <= {"ADJACENT_TRACK", "GOVERNANCE"}


def test_build_psicat_literature_training_split_is_separate_from_bundle() -> None:
    # This split must not be silently folded into the physics/governance
    # bundle builder's own record ids.
    from ox_navigator.engine.merlin_program import build_training_dataset_bundle

    bundle = build_training_dataset_bundle(limit=5)
    literature = build_psicat_literature_training_split(limit=5)
    bundle_ids = {
        row.get("record_id")
        for rows in bundle.get("splits", {}).values()
        for row in rows
    }
    literature_ids = {
        row["record_id"]
        for rows in literature["splits"].values()
        for row in rows
    }
    assert not (bundle_ids & literature_ids)
