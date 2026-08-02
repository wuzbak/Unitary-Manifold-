# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/precision_audit_worker.py"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.precision_audit_worker import PrecisionAuditWorker, BackgroundAuditThread
from EIGE.src.constants import PHI_0


class TestPrecisionAuditWorker:
    def setup_method(self):
        self.worker = PrecisionAuditWorker()

    def test_empty_block_passes(self):
        assert self.worker.execute_deep_geometric_validation([]) is True

    def test_single_zero_vector_passes(self):
        records = [{"selection_vector": [0, 0, 0]}]
        assert self.worker.execute_deep_geometric_validation(records) is True

    def test_typical_ballot_records_pass(self):
        records = [
            {"selection_vector": [1, 0, 1]},
            {"selection_vector": [0, 1, 0]},
            {"selection_vector": [1, 1, 0]},
        ]
        assert self.worker.execute_deep_geometric_validation(records) is True

    def test_empty_selection_vector_passes(self):
        records = [{"selection_vector": []}]
        assert self.worker.execute_deep_geometric_validation(records) is True

    def test_records_without_selection_vector_passes(self):
        records = [{"ballot_id": 1, "sequence_index": 1}]
        assert self.worker.execute_deep_geometric_validation(records) is True

    def test_audits_passed_increments(self):
        self.worker.execute_deep_geometric_validation([])
        assert self.worker.audits_passed() == 1

    def test_audits_failed_starts_at_zero(self):
        assert self.worker.audits_failed() == 0

    def test_reset_counters(self):
        self.worker.execute_deep_geometric_validation([])
        self.worker.reset_counters()
        assert self.worker.audits_passed() == 0
        assert self.worker.audits_failed() == 0

    def test_get_phi_0_is_string(self):
        phi_str = self.worker.get_phi_0()
        assert isinstance(phi_str, str)

    def test_get_phi_0_starts_with_0_785(self):
        phi_str = self.worker.get_phi_0()
        assert phi_str.startswith("0.785")

    def test_validate_block_json_empty(self):
        block = {"block_id": 1, "records": []}
        assert self.worker.validate_block_json(block) is True

    def test_validate_block_json_with_records(self):
        block = {
            "block_id": 1,
            "records": [
                {"selection_vector": [1, 0]},
                {"selection_vector": [0, 1]},
            ],
        }
        assert self.worker.validate_block_json(block) is True

    def test_validate_block_json_missing_records(self):
        block = {"block_id": 1}
        assert self.worker.validate_block_json(block) is True  # empty = pass

    def test_repr_format(self):
        r = repr(self.worker)
        assert "PrecisionAuditWorker" in r
        assert "dps" in r

    def test_batch_validation(self):
        records = [{"selection_vector": [i % 3, (i + 1) % 2]} for i in range(50)]
        assert self.worker.execute_deep_geometric_validation(records) is True
        assert self.worker.audits_passed() == 1


class TestBackgroundAuditThread:
    def test_start_and_stop(self):
        thread = BackgroundAuditThread()
        thread.start()
        thread.stop(timeout=2.0)

    def test_submit_and_process(self):
        import time
        thread = BackgroundAuditThread()
        thread.start()

        block = {"block_id": 1, "records": [{"selection_vector": [1, 0]}]}
        thread.submit(block)

        time.sleep(0.3)  # Allow processing
        thread.stop(timeout=2.0)
        results = thread.results()
        assert len(results) >= 1
        assert results[0] is True

    def test_on_failure_callback(self):
        """Test that the on_failure callback is not called for clean blocks."""
        failures = []

        def on_fail(block):
            failures.append(block)

        thread = BackgroundAuditThread(on_failure=on_fail)
        thread.start()
        block = {"block_id": 1, "records": []}
        thread.submit(block)
        import time
        time.sleep(0.3)
        thread.stop(timeout=2.0)
        assert len(failures) == 0
