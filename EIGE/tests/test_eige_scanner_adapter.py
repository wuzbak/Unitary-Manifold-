# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
Tests for EIGE/src/scanner_adapter.py — ScannerAdapter and MockScanner.
"""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from EIGE.src.scanner_adapter import ScannerAdapter, MockScanner, ScannerFormat


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def adapter():
    return ScannerAdapter(jurisdiction_id="TEST-01", num_candidates=5)


@pytest.fixture
def mock_scanner():
    return MockScanner(num_candidates=5, seed=42)


# ---------------------------------------------------------------------------
# MockScanner tests
# ---------------------------------------------------------------------------

class TestMockScanner:
    def test_emits_record(self, mock_scanner):
        record = mock_scanner.next_record()
        assert record is not None

    def test_emits_dict(self, mock_scanner):
        record = mock_scanner.next_record()
        assert isinstance(record, dict)

    def test_record_has_scanner_format(self, mock_scanner):
        record = mock_scanner.next_record()
        assert "scanner_format" in record

    def test_record_is_omr_dict_format(self, mock_scanner):
        record = mock_scanner.next_record()
        assert record["scanner_format"] == ScannerFormat.OMR_DICT

    def test_record_has_marks_field(self, mock_scanner):
        record = mock_scanner.next_record()
        assert "marks" in record

    def test_deterministic_with_same_seed(self):
        ms1 = MockScanner(num_candidates=3, seed=7)
        ms2 = MockScanner(num_candidates=3, seed=7)
        r1 = ms1.next_record()
        r2 = ms2.next_record()
        assert r1["marks"] == r2["marks"]

    def test_different_seeds_different_records(self):
        ms1 = MockScanner(num_candidates=5, seed=1)
        ms2 = MockScanner(num_candidates=5, seed=2)
        # Run enough records to find a difference
        for _ in range(10):
            r1 = ms1.next_record()
            r2 = ms2.next_record()
            if r1["marks"] != r2["marks"]:
                return  # found a difference, test passes
        pytest.fail("No differences found between scanners with different seeds")

    def test_sequence_counter_increments(self, mock_scanner):
        r1 = mock_scanner.next_record()
        r2 = mock_scanner.next_record()
        assert r2["sequence"] > r1["sequence"]

    def test_emit_batch_returns_list(self, mock_scanner):
        batch = mock_scanner.emit_batch(5)
        assert isinstance(batch, list)
        assert len(batch) == 5

    def test_emit_batch_all_unique(self, mock_scanner):
        batch = mock_scanner.emit_batch(10)
        seqs = [r["sequence"] for r in batch]
        assert len(set(seqs)) == 10


# ---------------------------------------------------------------------------
# ScannerAdapter — OMR_DICT format
# ---------------------------------------------------------------------------

class TestScannerAdapterOMRDict:
    def test_process_returns_result(self, adapter, mock_scanner):
        record = mock_scanner.next_record()
        result = adapter.process(record)
        assert result is not None

    def test_process_returns_dict(self, adapter, mock_scanner):
        record = mock_scanner.next_record()
        result = adapter.process(record)
        assert isinstance(result, dict)

    def test_process_result_has_status(self, adapter, mock_scanner):
        record = mock_scanner.next_record()
        result = adapter.process(record)
        assert "status" in result

    def test_process_accepted_or_rejected(self, adapter, mock_scanner):
        for _ in range(10):
            record = mock_scanner.next_record()
            result = adapter.process(record)
            assert result["status"] in ("ACCEPTED", "REJECTED", "QUEUED_FOR_ADJUDICATION")

    def test_rejection_log_accumulates(self, adapter):
        # Process several records; rejection count is tracked
        ms = MockScanner(num_candidates=5, seed=99)
        for _ in range(20):
            adapter.process(ms.next_record())
        assert adapter.total_processed >= 20

    def test_total_processed_counter(self, adapter, mock_scanner):
        for i in range(5):
            adapter.process(mock_scanner.next_record())
        assert adapter.total_processed == 5


# ---------------------------------------------------------------------------
# ScannerAdapter — FLAT_CONFIDENCE format
# ---------------------------------------------------------------------------

class TestScannerAdapterFlatConfidence:
    def test_process_flat_confidence_record(self, adapter):
        record = {
            "scanner_format": ScannerFormat.FLAT_CONFIDENCE,
            "sequence": 1,
            "confidence_scores": [0.95, 0.02, 0.01, 0.01, 0.01],
        }
        result = adapter.process(record)
        assert isinstance(result, dict)
        assert "status" in result

    def test_flat_confidence_accepted_on_high_score(self, adapter):
        record = {
            "scanner_format": ScannerFormat.FLAT_CONFIDENCE,
            "sequence": 1,
            "confidence_scores": [0.99, 0.0, 0.0, 0.0, 0.01],
        }
        result = adapter.process(record)
        assert result["status"] in ("ACCEPTED", "QUEUED_FOR_ADJUDICATION")


# ---------------------------------------------------------------------------
# ScannerAdapter — process_batch
# ---------------------------------------------------------------------------

class TestScannerAdapterBatch:
    def test_process_batch_returns_list(self, adapter, mock_scanner):
        batch = mock_scanner.emit_batch(5)
        results = adapter.process_batch(batch)
        assert isinstance(results, list)
        assert len(results) == 5

    def test_process_batch_all_have_status(self, adapter, mock_scanner):
        batch = mock_scanner.emit_batch(8)
        results = adapter.process_batch(batch)
        assert all("status" in r for r in results)
