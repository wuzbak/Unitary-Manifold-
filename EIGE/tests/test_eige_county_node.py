# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/county_node.py"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.county_node import CountyNode, BallotRecord
from EIGE.src.metric_closure import ClosureStatus
from EIGE.src.constants import K_CS, PHI_0, SHARD_COUNT


class TestBallotRecord:
    def test_as_int_deterministic(self):
        r = BallotRecord(ballot_id=1, selection_vector=[1, 0, 1], sequence_index=1)
        assert r.as_int() == r.as_int()

    def test_different_selection_vectors_different_ints(self):
        r1 = BallotRecord(ballot_id=1, selection_vector=[1, 0, 1], sequence_index=1)
        r2 = BallotRecord(ballot_id=1, selection_vector=[0, 1, 0], sequence_index=1)
        assert r1.as_int() != r2.as_int()

    def test_different_ballot_ids_different_ints(self):
        r1 = BallotRecord(ballot_id=1, selection_vector=[1, 0], sequence_index=1)
        r2 = BallotRecord(ballot_id=2, selection_vector=[1, 0], sequence_index=2)
        assert r1.as_int() != r2.as_int()

    def test_as_int_is_nonnegative(self):
        r = BallotRecord(ballot_id=99, selection_vector=[5, 3, 2], sequence_index=99)
        assert r.as_int() >= 0


class TestCountyNodeIngestion:
    def setup_method(self):
        self.node = CountyNode("WA-047", "King County")

    def test_initial_ballot_count_is_zero(self):
        assert self.node.ballot_count() == 0

    def test_ingest_single_ballot(self):
        rec = self.node.ingest_ballot([1, 0, 1])
        assert isinstance(rec, BallotRecord)
        assert self.node.ballot_count() == 1

    def test_ingest_increments_count(self):
        for i in range(5):
            self.node.ingest_ballot([i, 1])
        assert self.node.ballot_count() == 5

    def test_ingest_batch(self):
        records = self.node.ingest_batch([[1, 0], [0, 1], [1, 1]])
        assert len(records) == 3
        assert self.node.ballot_count() == 3

    def test_sequence_indices_are_sequential(self):
        recs = [self.node.ingest_ballot([i]) for i in range(4)]
        for i, rec in enumerate(recs, start=1):
            assert rec.sequence_index == i

    def test_ballot_records_are_immutable_copies(self):
        vec = [1, 2, 3]
        rec = self.node.ingest_ballot(vec)
        vec.append(99)
        assert rec.selection_vector == [1, 2, 3]

    def test_large_ingestion(self):
        for i in range(200):
            self.node.ingest_ballot([i % 5, (i + 1) % 3])
        assert self.node.ballot_count() == 200


class TestCountyNodeNetworkPartition:
    def setup_method(self):
        self.node = CountyNode("WA-033", "Snohomish County")

    def test_initially_online(self):
        assert self.node.is_online()

    def test_disconnect_marks_offline(self):
        self.node.disconnect()
        assert not self.node.is_online()

    def test_reconnect_marks_online(self):
        self.node.disconnect()
        self.node.reconnect()
        assert self.node.is_online()

    def test_ingestion_continues_while_offline(self):
        self.node.disconnect()
        for i in range(5):
            self.node.ingest_ballot([i])
        assert self.node.ballot_count() == 5

    def test_offline_ingestion_queues_telemetry(self):
        self.node.disconnect()
        self.node.ingest_ballot([1])
        self.node.ingest_ballot([2])
        assert len(self.node.get_queued_payloads()) == 2

    def test_reconnect_flushes_queue(self):
        self.node.disconnect()
        self.node.ingest_ballot([1])
        self.node.ingest_ballot([2])
        flushed = self.node.reconnect()
        assert len(flushed) == 2
        assert len(self.node.get_queued_payloads()) == 0

    def test_online_ingestion_does_not_queue(self):
        self.node.ingest_ballot([1])
        assert len(self.node.get_queued_payloads()) == 0

    def test_total_count_correct_after_partition_cycle(self):
        self.node.ingest_ballot([1])
        self.node.disconnect()
        self.node.ingest_ballot([2])
        self.node.ingest_ballot([3])
        self.node.reconnect()
        self.node.ingest_ballot([4])
        assert self.node.ballot_count() == 4


class TestCountyNodeTelemetry:
    def setup_method(self):
        self.node = CountyNode("WA-061", "Pierce County")
        for i in range(10):
            self.node.ingest_ballot([i % 3, 1])

    def test_get_shard_telemetry_returns_dict(self):
        t = self.node.get_shard_telemetry()
        assert isinstance(t, dict)

    def test_telemetry_has_shard_digests(self):
        t = self.node.get_shard_telemetry()
        assert "shard_digests" in t
        assert len(t["shard_digests"]) == SHARD_COUNT

    def test_telemetry_has_hmac_signature(self):
        t = self.node.get_shard_telemetry()
        assert "hmac_signature" in t
        assert len(t["hmac_signature"]) == 128  # SHA-512 hex

    def test_telemetry_ballot_count(self):
        t = self.node.get_shard_telemetry()
        assert t["ballot_count"] == 10

    def test_telemetry_no_raw_ballots(self):
        import json
        t = self.node.get_shard_telemetry()
        s = json.dumps(t)
        assert "selection_vector" not in s

    def test_get_metric_state_has_phi_eff(self):
        state = self.node.get_metric_state()
        assert "phi_eff" in state
        assert abs(state["phi_eff"] - PHI_0) < 1e-12

    def test_get_metric_state_has_k_cs(self):
        state = self.node.get_metric_state()
        assert state["k_cs"] == K_CS

    def test_validate_closure_returns_stable(self):
        result = self.node.validate_closure()
        assert result.status == ClosureStatus.STABLE

    def test_last_closure_result_stored(self):
        self.node.validate_closure()
        assert self.node.last_closure_result() is not None

    def test_repr_format(self):
        r = repr(self.node)
        assert "WA-061" in r
        assert "Pierce County" in r
