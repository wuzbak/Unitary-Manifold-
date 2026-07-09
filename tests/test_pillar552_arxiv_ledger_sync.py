# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 552 — arXiv Ledger Sync to v19.1."""
from __future__ import annotations

import pytest
from src.core.pillar552_arxiv_ledger_sync import (
    ARXIV_ABSTRACT_DRAFT,
    LAST_ARXIV_SYNC_VERSION,
    NEW_RESULTS_SINCE_SYNC,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    arxiv_abstract_draft,
    mcp_ingest_update,
    new_results_since_v158,
    pillar_report,
    sync_certificate,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 552


def test_pillar_status():
    assert "ARXIV" in PILLAR_STATUS
    assert "SYNC" in PILLAR_STATUS


def test_version():
    assert VERSION == "v19.1"


def test_last_sync_version():
    assert LAST_ARXIV_SYNC_VERSION == "v15.8"


# ─── New results ─────────────────────────────────────────────────────────────

def test_new_results_count():
    results = new_results_since_v158()
    assert len(results) >= 4   # at least v16–v19.1


def test_new_results_have_required_keys():
    for r in new_results_since_v158():
        assert "version" in r
        assert "key_results" in r
        assert "test_count_delta" in r


def test_new_results_juno_v18():
    results = new_results_since_v158()
    # v18.0 should contain JUNO result
    v18 = next(r for r in results if "v18.0" in r["version"])
    juno_mentioned = any("JUNO" in k for k in v18["key_results"])
    assert juno_mentioned


def test_new_results_lean4_mentioned():
    results = new_results_since_v158()
    all_results_text = " ".join(
        " ".join(r["key_results"]) for r in results
    )
    assert "Lean4" in all_results_text or "lean4" in all_results_text.lower()


def test_new_results_v191_present():
    results = new_results_since_v158()
    versions = [r["version"] for r in results]
    assert any("19.1" in v for v in versions)


def test_new_results_test_deltas_positive():
    for r in new_results_since_v158():
        delta = int(r["test_count_delta"].replace("+", ""))
        assert delta > 0


# ─── arXiv abstract ──────────────────────────────────────────────────────────

def test_abstract_is_string():
    abstract = arxiv_abstract_draft()
    assert isinstance(abstract, str)


def test_abstract_nonempty():
    abstract = arxiv_abstract_draft()
    assert len(abstract) > 500


def test_abstract_contains_juno():
    abstract = arxiv_abstract_draft()
    assert "JUNO" in abstract


def test_abstract_contains_toe_score():
    abstract = arxiv_abstract_draft()
    assert "28/28" in abstract


def test_abstract_contains_litebird():
    abstract = arxiv_abstract_draft()
    assert "LiteBIRD" in abstract


def test_abstract_contains_desi():
    abstract = arxiv_abstract_draft()
    assert "DESI" in abstract


def test_abstract_contains_falsification():
    abstract = arxiv_abstract_draft()
    assert "falsif" in abstract.lower()


# ─── Sync certificate ────────────────────────────────────────────────────────

def test_sync_certificate_keys():
    cert = sync_certificate()
    for key in ["pillar", "status", "last_arxiv_sync", "current_version",
                "new_test_count_since_sync", "what_was_done", "what_was_NOT_done",
                "toe_score_delta"]:
        assert key in cert


def test_sync_cert_last_sync():
    cert = sync_certificate()
    assert cert["last_arxiv_sync"] == "v15.8"


def test_sync_cert_current_version():
    cert = sync_certificate()
    assert cert["current_version"] == "v19.1"


def test_sync_cert_new_test_count_positive():
    cert = sync_certificate()
    assert cert["new_test_count_since_sync"] > 0


def test_sync_cert_toe_unchanged():
    cert = sync_certificate()
    assert cert["toe_score_delta"] == pytest.approx(0.0)


def test_sync_cert_what_not_done():
    cert = sync_certificate()
    not_done_text = " ".join(cert["what_was_NOT_done"])
    assert "main.tex" in not_done_text or "LaTeX" in not_done_text


def test_sync_cert_lean4_theorems():
    cert = sync_certificate()
    assert cert["new_lean4_theorems_since_sync"] > 0


def test_sync_cert_versions_listed():
    cert = sync_certificate()
    assert "v19.1" in cert["versions_since_sync"]
    assert "v16.x" in cert["versions_since_sync"]


# ─── MCP INGEST update ───────────────────────────────────────────────────────

def test_mcp_ingest_update_keys():
    update = mcp_ingest_update()
    for key in ["Version", "Tests_passing", "Lean4_theorems", "ToE_score"]:
        assert key in update


def test_mcp_ingest_version_v191():
    update = mcp_ingest_update()
    assert "19.1" in update["Version"]


def test_mcp_ingest_toe_score():
    update = mcp_ingest_update()
    assert "28/28" in update["ToE_score"]


def test_mcp_ingest_lean4():
    update = mcp_ingest_update()
    assert "109" in update["Lean4_theorems"]


def test_mcp_ingest_desi_status():
    update = mcp_ingest_update()
    assert "DESI" in update["DESI_status"] or "tension" in update["DESI_status"].lower()


# ─── Full report ─────────────────────────────────────────────────────────────

def test_pillar_report_structure():
    report = pillar_report()
    assert report["pillar"] == 552
    assert report["toe_score_delta"] == pytest.approx(0.0)
    assert report["last_arxiv_sync"] == "v15.8"
