# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for bot/session_bootstrap.py and bot/rag_index.py intent extensions."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from bot.session_bootstrap import (
    load_boot_block,
    summarise_intent_history,
    current_intent_snapshot,
    append_session_entry,
    CURRENT_DOC,
    LOG_DOC,
)
from bot.rag_index import (
    RAGIndex,
    build_intent_index,
    retrieve_intent,
)


# ---------------------------------------------------------------------------
# load_boot_block
# ---------------------------------------------------------------------------

class TestLoadBootBlock:
    def test_loads_canonical_current_doc(self):
        """load_boot_block() should parse HILS_SESSION_CURRENT.md successfully."""
        boot = load_boot_block()
        assert isinstance(boot, dict)
        assert "active_wave" in boot
        assert "non_negotiables" in boot
        assert "strategic_intent" in boot
        assert "open_loops" in boot
        assert "key_coordinates" in boot

    def test_active_wave_non_empty(self):
        boot = load_boot_block()
        assert boot["active_wave"] not in ("", "UNKNOWN"), (
            "Active wave must be set in HILS_SESSION_CURRENT.md"
        )

    def test_non_negotiables_present(self):
        boot = load_boot_block()
        assert len(boot["non_negotiables"]) >= 5, (
            "Expected at least 5 non-negotiables in HILS_SESSION_CURRENT.md"
        )

    def test_fallback_when_file_missing(self):
        """load_boot_block() must return safe defaults when file is absent."""
        boot = load_boot_block(current_doc=Path("/nonexistent/HILS_SESSION_CURRENT.md"))
        assert boot["active_wave"] == "UNKNOWN"
        assert "warning" in boot
        assert len(boot["non_negotiables"]) > 0

    def test_custom_doc_parsed(self):
        """load_boot_block() reads a custom file correctly."""
        content = """\
# HILS Session — Current State

## Boot Block — Identity & Role Map

| Field | Value |
|-------|-------|
| **Active wave** | Wave Test |
| **Session opened** | 2026-01-01T00:00:00Z |

## Non-Negotiables (read before every action)

1. Rule one
2. Rule two

## Current Strategic Intent

| Priority | Intent | Status |
|----------|--------|--------|
| 1 | Do thing A | ✅ done |

## Open Loops / Next-Entry Trigger Conditions

- Loop one still open

## Key Repository Coordinates

| Resource | Path |
|----------|------|
| Bot | bot/rag_index.py |
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            tmp = Path(f.name)
        try:
            boot = load_boot_block(current_doc=tmp)
            assert boot["active_wave"] == "Wave Test"
            assert len(boot["non_negotiables"]) == 2
            assert boot["strategic_intent"][0]["intent"] == "Do thing A"
            assert "Loop one still open" in boot["open_loops"]
            assert "Bot" in boot["key_coordinates"]
        finally:
            tmp.unlink()


# ---------------------------------------------------------------------------
# summarise_intent_history
# ---------------------------------------------------------------------------

class TestSummariseIntentHistory:
    def test_returns_list(self):
        history = summarise_intent_history()
        assert isinstance(history, list)

    def test_entry_structure(self):
        history = summarise_intent_history()
        for entry in history:
            assert "entry_number" in entry
            assert "timestamp" in entry
            assert "wave" in entry
            assert "intents" in entry
            assert "decisions" in entry
            assert "resolved_loops" in entry
            assert "open_loops" in entry
            assert "next_triggers" in entry
            assert "session_trigger" in entry

    def test_empty_when_file_missing(self):
        result = summarise_intent_history(log_doc=Path("/nonexistent/log.md"))
        assert result == []

    def test_most_recent_first(self):
        history = summarise_intent_history()
        if len(history) >= 2:
            ts = [e["timestamp"] for e in history]
            assert ts == sorted(ts, reverse=True)


# ---------------------------------------------------------------------------
# append_session_entry
# ---------------------------------------------------------------------------

class TestAppendSessionEntry:
    def _make_log(self) -> Path:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                "# HILS Session Log\n\n"
                "<!-- Add new entries above this line -->\n"
            )
            return Path(f.name)

    def test_append_creates_entry(self):
        tmp = self._make_log()
        try:
            text = append_session_entry(
                wave="Wave X",
                session_trigger="unit test",
                intents=["Do X"],
                decisions=["Decision one"],
                loops_resolved=["Loop A resolved"],
                loops_forward=["Loop B open"],
                regression_result="100 passed",
                next_triggers=["When Y happens"],
                log_doc=tmp,
            )
            assert "## Entry 0001" in text
            assert "Wave X" in text
            assert "Do X" in text
            assert "Decision one" in text
            assert "Loop A resolved" in text
            assert "Loop B open" in text
            assert "100 passed" in text
        finally:
            tmp.unlink()

    def test_append_increments_entry_number(self):
        tmp = self._make_log()
        try:
            append_session_entry(
                wave="Wave 1", session_trigger="first",
                intents=[], decisions=[], loops_resolved=[],
                loops_forward=[], regression_result="ok",
                next_triggers=[], log_doc=tmp,
            )
            append_session_entry(
                wave="Wave 2", session_trigger="second",
                intents=[], decisions=[], loops_resolved=[],
                loops_forward=[], regression_result="ok",
                next_triggers=[], log_doc=tmp,
            )
            raw = tmp.read_text()
            assert "## Entry 0001" in raw
            assert "## Entry 0002" in raw
        finally:
            tmp.unlink()

    def test_append_preserves_existing_content(self):
        tmp = self._make_log()
        try:
            raw_before = tmp.read_text()
            append_session_entry(
                wave="Wave Z", session_trigger="test",
                intents=["Keep history"],
                decisions=[], loops_resolved=[],
                loops_forward=[], regression_result="ok",
                next_triggers=[], log_doc=tmp,
            )
            raw_after = tmp.read_text()
            assert "# HILS Session Log" in raw_after  # original header preserved
            assert "Keep history" in raw_after
        finally:
            tmp.unlink()


# ---------------------------------------------------------------------------
# current_intent_snapshot
# ---------------------------------------------------------------------------

class TestCurrentIntentSnapshot:
    def test_returns_expected_top_level_keys(self):
        snapshot = current_intent_snapshot()
        assert "active_wave" in snapshot
        assert "strategic_intent" in snapshot
        assert "unresolved_loops" in snapshot
        assert "recent_decisions" in snapshot
        assert "next_triggers" in snapshot
        assert "sources" in snapshot

    def test_uses_defaults_when_files_missing(self):
        snapshot = current_intent_snapshot(
            current_doc=Path("/nonexistent/current.md"),
            log_doc=Path("/nonexistent/log.md"),
        )
        assert snapshot["active_wave"] == "UNKNOWN"
        assert snapshot["recent_history_count"] == 0
        assert snapshot["unresolved_loops"] == []

    def test_resolved_loops_removed_from_unresolved(self):
        current_text = """\
# HILS Session — Current State

## Boot Block — Identity & Role Map

| Field | Value |
|-------|-------|
| **Active wave** | Wave Test |
| **Session opened** | 2026-01-01T00:00:00Z |

## Non-Negotiables (read before every action)

1. Keep tests green

## Current Strategic Intent

| Priority | Intent | Status |
|----------|--------|--------|
| 1 | Close loop A | active |

## Open Loops / Next-Entry Trigger Conditions

- Loop A
- Loop B
"""
        log_text = """\
# HILS Session Log

## Entry 0001 — 2026-01-02T00:00:00Z | Wave Test

### Identity
- Session trigger: unit test

### Strategic intent this session
- Resolve Loop A

### Decisions made
1. Decision one

### Open loops resolved
- Loop A

### Open loops carried forward
- Loop C

### Regression gate at session close
- Result: green

### Next-entry trigger conditions
- Trigger one
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            current_tmp = tmp_path / "current.md"
            log_tmp = tmp_path / "log.md"
            current_tmp.write_text(current_text, encoding="utf-8")
            log_tmp.write_text(log_text, encoding="utf-8")
            snapshot = current_intent_snapshot(current_doc=current_tmp, log_doc=log_tmp)
            assert "Loop A" not in snapshot["unresolved_loops"]
            assert "Loop B" in snapshot["unresolved_loops"]
            assert "Loop C" in snapshot["unresolved_loops"]
            assert "Decision one" in snapshot["recent_decisions"]
            assert "Trigger one" in snapshot["next_triggers"]


# ---------------------------------------------------------------------------
# build_intent_index / retrieve_intent
# ---------------------------------------------------------------------------

class TestIntentIndex:
    def test_build_intent_index_returns_ragindex(self):
        idx = build_intent_index()
        assert isinstance(idx, RAGIndex)

    def test_intent_index_has_chunks(self):
        idx = build_intent_index()
        assert len(idx.chunks) > 0

    def test_intent_index_includes_session_sources(self):
        idx = build_intent_index()
        sources = {chunk.source for chunk in idx.chunks}
        # At least one of the session docs should be indexed
        session_sources = {"HILS_SESSION_CURRENT.md", "HILS_SESSION_LOG.md"}
        assert session_sources & sources, (
            "Intent index must include HILS_SESSION_CURRENT.md or HILS_SESSION_LOG.md"
        )

    def test_retrieve_intent_latest(self):
        idx = build_intent_index()
        result = retrieve_intent(idx, mode="latest_intent")
        assert "mode" in result
        assert result["mode"] == "latest_intent"
        assert "answer" in result
        assert "sources" in result

    def test_retrieve_intent_long_arc(self):
        idx = build_intent_index()
        result = retrieve_intent(idx, mode="long_arc_intent")
        assert result["mode"] == "long_arc_intent"

    def test_retrieve_intent_unresolved(self):
        idx = build_intent_index()
        result = retrieve_intent(idx, mode="unresolved_intent")
        assert result["mode"] == "unresolved_intent"

    def test_retrieve_intent_unknown_mode(self):
        idx = build_intent_index()
        result = retrieve_intent(idx, mode="bad_mode")
        assert "Unknown mode" in result["answer"]

    def test_retrieve_intent_sources_have_score(self):
        idx = build_intent_index()
        result = retrieve_intent(idx, mode="latest_intent")
        for s in result["sources"]:
            assert "score" in s
            assert 0.0 <= s["score"] <= 1.0
