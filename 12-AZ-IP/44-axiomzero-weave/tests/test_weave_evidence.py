# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from az_weave.evidence import SourceIndex


def test_search_returns_cited_fresh_excerpt_and_verifies(tmp_path):
    source = tmp_path / "docs" / "truth.md"
    source.parent.mkdir()
    source.write_text("# Truth layer\n\nThe RadionField equation is constrained.\n")
    index = SourceIndex(tmp_path, ["docs/truth.md"])

    hits = index.search("radion field")
    assert len(hits) == 1
    hit = hits[0]
    assert hit["source"] == "docs/truth.md"
    assert (hit["start_line"], hit["end_line"]) == (1, 3)
    assert "RadionField" in hit["excerpt"]
    assert hit["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert hit["evidence_kind"] == "source_content"
    assert hit["current"] is True and hit["score"] > 0
    assert index.verify(hits)


def test_verify_requires_authentic_complete_citation(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("first line\nsecond line\n")
    index = SourceIndex(tmp_path, ["source.md"])
    hit = index.search("second")[0]
    assert index.verify([hit])
    for fields in [
        {"excerpt": "forged text"},
        {"start_line": 0},
        {"start_line": True},
        {"start_line": 1.0},
        {"start_line": 2, "end_line": 1},
        {"end_line": 3},
        {"end_line": "2"},
        {"evidence_kind": "inventory"},
        {"current": False},
        {"current": 1},
    ]:
        assert not index.verify([{**hit, **fields}])
    for key in ("start_line", "end_line", "excerpt", "evidence_kind", "current"):
        incomplete = dict(hit)
        del incomplete[key]
        assert not index.verify([incomplete])
    assert not index.verify([{"source": hit["source"], "sha256": hit["sha256"]}])


def test_search_merges_overlapping_windows_and_freshness_changes(tmp_path):
    source = tmp_path / "notes.md"
    lines = ["ordinary filler"] * 70
    lines[10], lines[40] = "alpha marker", "beta marker"
    source.write_text("\n".join(lines))
    index = SourceIndex(tmp_path, ["notes.md"])

    hits = index.search("alpha beta")
    assert len(hits) == 2
    assert hits[0]["end_line"] < hits[1]["start_line"]
    source.write_text("changed")
    assert not index.verify(hits)
    assert index.search("alpha beta") == []


def test_default_corpus_is_tracked_and_excludes_private_files(tmp_path):
    import subprocess

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRUTH_LAYER.md").write_text(
        "## Retrieval correction (2026-11-04)\ntruth layer current\n")
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / "secret.md").write_text("truth layer secret\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "docs/TRUTH_LAYER.md", "private/secret.md"],
        check=True,
    )
    index = SourceIndex(tmp_path)
    assert [hit["source"] for hit in index.search("truth layer")] == ["docs/TRUTH_LAYER.md"]


def test_rejects_bad_queries_limits_and_symlinks(tmp_path):
    source = tmp_path / "safe.md"
    source.write_text("alpha")
    index = SourceIndex(tmp_path, ["safe.md"])
    for query, limit in [("", 1), ("alpha", 0), ("alpha", True), ("x" * 2049, 1)]:
        with pytest.raises(ValueError):
            index.search(query, limit)

    outside = tmp_path / "outside.md"
    outside.write_text("alpha")
    link = tmp_path / "link.md"
    link.symlink_to(outside)
    with pytest.raises(ValueError):
        SourceIndex(tmp_path, ["link.md"])


def test_default_grounding_ranks_product_content_over_inventory(tmp_path):
    import subprocess

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    corpus = {
        "12-AZ-IP/43-az-geometric-tori-transformer/README.md":
            "# Product43\n" + "metadata\n" * 35
            + "Toroidal rotary encoding uses exact phase lattice transformer attention.\n",
        "12-AZ-IP/16-oracle/README.md":
            "# OmegaOracle\n" + "metadata\n" * 35
            + "OmegaOracle synthesizes five bodies with epistemic status and phi_trust.\n",
        "docs/inventory.md": "Product43 Product43 Product43 OmegaOracle OmegaOracle",
        "docs/TRUTH_LAYER.md": "## Retrieval correction (2026-11-04)\nA new constrained planar radion correction.",
        "proof/TIER_1_FORMAL.md": "Formal gate",
        "FALLIBILITY.md": "Open obligations",
    }
    for path, text in corpus.items():
        file = tmp_path / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text)
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    index = SourceIndex(tmp_path)
    for query, source, passage in [
        ("What is Product43 toroidal rotary encoding phase lattice?", "43-", "Toroidal rotary"),
        ("How does OmegaOracle synthesize five bodies epistemic status?", "16-", "five bodies"),
        ("constrained planar radion", "TRUTH_LAYER", "correction"),
    ]:
        hit = index.search(query, limit=1)[0]
        assert source in hit["source"] and passage in hit["excerpt"]
        lines = (tmp_path / hit["source"]).read_text().splitlines()
        assert hit["excerpt"] == "\n".join(lines[hit["start_line"] - 1:hit["end_line"]])


def test_unsafe_ignored_missing_and_oversized_sources(tmp_path):
    (tmp_path / ".gitignore").write_text("runtime/\n*.sqlite\n")
    (tmp_path / "runtime").mkdir()
    (tmp_path / "runtime" / "note.md").write_text("secret")
    for path in ["../escape", "/absolute", "AXIOMZERO-SYNTHESIS/x.md",
                 ".axiomzero-weave/state.md", "runtime/note.md", "memory.sqlite"]:
        with pytest.raises(ValueError):
            SourceIndex(tmp_path, [path])
    with pytest.raises(RuntimeError):
        SourceIndex(tmp_path)
    source = tmp_path / "content.md"
    source.write_text("fresh")
    index = SourceIndex(tmp_path, ["content.md"])
    old = index.search("fresh")
    first = index.semantic_fingerprint(old)
    assert first == index.semantic_fingerprint([{**old[0], "timestamp": "later"}])
    source.write_text("fresh changed")
    assert not index.verify(old)
    assert first != index.semantic_fingerprint(index.search("fresh"))
    assert not index.verify([{"source": "../outside", "sha256": "abc"}])
    assert not index.verify([{"source": "content.md", "sha256": "invented"}])
    source.unlink()
    assert not index.verify(old)
    substitute = tmp_path / "substitute.md"
    substitute.write_text("fresh")
    source.symlink_to(substitute)
    assert not index.verify(old) and index.search("fresh") == []
    source.unlink()
    source.write_bytes(b"fresh" * 120_000)
    assert index.search("fresh") == []


def test_truth_search_and_verify_exclude_historical_spans_and_keep_source_offsets(tmp_path):
    source = tmp_path / "docs" / "TRUTH_LAYER.md"
    source.parent.mkdir()
    text = (
        "# Truth layer\nUnselected preamble.\n"
        "## Retrieval correction (2026-11-04)\nCurrent radion boundary.\n"
        "### Historical archive\nRadion historical-only-obligation.\n"
        "#### Correction (2026-11-05)\nRadion excluded descendant.\n"
        "### Validation boundary\nCurrent radion test scope.\n"
        "## Historical archive\n"
        "### Mathematical findings and assumptions\nRadion excluded whitelist.\n"
    )
    source.write_text(text)
    index = SourceIndex(tmp_path, ["docs/TRUTH_LAYER.md"])
    hits = index.search("radion")
    assert [(hit["start_line"], hit["end_line"]) for hit in hits] == [(3, 4), (9, 10)]
    assert index.search("historical-only-obligation") == []
    assert index.verify(hits)
    lines = text.splitlines()
    for hit in hits:
        assert hit["excerpt"] == "\n".join(lines[hit["start_line"] - 1:hit["end_line"]])
    for start, end in [(5, 6), (3, 10), (12, 13)]:
        forged = {**hits[0], "start_line": start, "end_line": end,
                  "excerpt": "\n".join(lines[start - 1:end])}
        assert not index.verify([forged])
    source.write_text("## Unreviewed section\nradion unknown freshness\n")
    assert index.search("radion") == []


def test_search_hashes_each_matching_file_once_before_candidate_ranking(tmp_path, monkeypatch):
    import az_weave.evidence as evidence

    for name in ("one.md", "two.md"):
        (tmp_path / name).write_text("radion boundary\n" * 100)
    index = SourceIndex(tmp_path, ["one.md", "two.md"])
    original = evidence._digest
    calls = []

    def counted(data):
        calls.append(data)
        return original(data)

    monkeypatch.setattr(evidence, "_digest", counted)
    hits = index.search("radion", limit=1)
    assert len(hits) == 1
    assert len(calls) == 2
