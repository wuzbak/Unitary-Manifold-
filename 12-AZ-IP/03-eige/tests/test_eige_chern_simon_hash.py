# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/chern_simon_hash.py"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.chern_simon_hash import (
    chern_simon_hash,
    chern_simon_hash_hex,
    ChernSimonChain,
    ShardedChernSimonChain,
)
from EIGE.src.constants import K_CS, SHARD_COUNT, SHARD_RECONSTRUCTION_THRESHOLD


class TestChernSimonHashFunction:
    def test_empty_sequence_returns_k_cs(self):
        assert chern_simon_hash([]) == K_CS

    def test_single_ballot(self):
        h = chern_simon_hash([42])
        assert isinstance(h, int)
        assert h >= 0

    def test_order_sensitivity_basic(self):
        assert chern_simon_hash([1, 2, 3]) != chern_simon_hash([3, 2, 1])

    def test_order_sensitivity_swap(self):
        assert chern_simon_hash([10, 20]) != chern_simon_hash([20, 10])

    def test_same_sequence_is_deterministic(self):
        seq = [1, 2, 3, 4, 5]
        assert chern_simon_hash(seq) == chern_simon_hash(seq)

    def test_different_content_different_hash(self):
        assert chern_simon_hash([1, 2, 3]) != chern_simon_hash([1, 2, 4])

    def test_hash_is_nonnegative(self):
        for seq in [[], [0], [1], [1, 2, 3], [99, 100, 101]]:
            assert chern_simon_hash(seq) >= 0

    def test_hash_within_modulus(self):
        from EIGE.src.constants import HASH_MODULUS
        for seq in [[1], [1, 2], [100, 200, 300]]:
            assert chern_simon_hash(seq) < HASH_MODULUS

    def test_hex_output_format(self):
        h = chern_simon_hash_hex([1, 2, 3])
        assert len(h) == 16
        assert all(c in "0123456789abcdef" for c in h)

    def test_insertion_order_matters(self):
        # [a, b, c] vs [a, c, b] must differ
        assert chern_simon_hash([1, 2, 3]) != chern_simon_hash([1, 3, 2])

    def test_prepend_changes_hash(self):
        # Retroactive insertion at position 0
        original = chern_simon_hash([10, 20, 30])
        stuffed = chern_simon_hash([99, 10, 20, 30])
        assert original != stuffed

    def test_append_changes_hash(self):
        original = chern_simon_hash([10, 20, 30])
        appended = chern_simon_hash([10, 20, 30, 99])
        assert original != appended

    def test_large_sequence(self):
        seq = list(range(1000))
        h = chern_simon_hash(seq)
        assert isinstance(h, int)
        assert h >= 0


class TestChernSimonChain:
    def test_initial_state_is_k_cs(self):
        chain = ChernSimonChain()
        assert chain.digest() == K_CS

    def test_update_changes_state(self):
        chain = ChernSimonChain()
        chain.update(42)
        assert chain.digest() != K_CS

    def test_ballot_count_increments(self):
        chain = ChernSimonChain()
        assert chain.ballot_count() == 0
        chain.update(1)
        chain.update(2)
        assert chain.ballot_count() == 2

    def test_hexdigest_format(self):
        chain = ChernSimonChain()
        chain.update(1)
        h = chain.hexdigest()
        assert len(h) == 16
        assert all(c in "0123456789abcdef" for c in h)

    def test_sha512_hexdigest_format(self):
        chain = ChernSimonChain()
        chain.update(1)
        h = chain.sha512_hexdigest()
        assert len(h) == 128  # SHA-512 = 64 bytes = 128 hex chars
        assert all(c in "0123456789abcdef" for c in h)

    def test_checkpoint_returns_count_and_state(self):
        chain = ChernSimonChain()
        chain.update(10)
        chain.update(20)
        snap = chain.checkpoint()
        assert snap == (2, chain.digest())

    def test_checkpoints_list_grows(self):
        chain = ChernSimonChain()
        chain.checkpoint()
        chain.update(1)
        chain.checkpoint()
        assert len(chain.checkpoints()) == 2

    def test_shard_slot_in_range(self):
        chain = ChernSimonChain()
        for ballot in [1, 2, 3, 100, 999]:
            chain.update(ballot)
            slot = chain.shard_slot()
            assert 0 <= slot < SHARD_COUNT

    def test_reset_restores_initial_state(self):
        chain = ChernSimonChain()
        chain.update(42)
        chain.update(43)
        chain.checkpoint()
        chain.reset()
        assert chain.digest() == K_CS
        assert chain.ballot_count() == 0
        assert chain.checkpoints() == []

    def test_order_sensitivity_via_chain(self):
        chain_a = ChernSimonChain()
        chain_b = ChernSimonChain()
        chain_a.update(1)
        chain_a.update(2)
        chain_b.update(2)
        chain_b.update(1)
        assert chain_a.digest() != chain_b.digest()

    def test_repr_format(self):
        chain = ChernSimonChain()
        r = repr(chain)
        assert "ChernSimonChain" in r
        assert "count=0" in r


class TestShardedChernSimonChain:
    def test_initial_primary_digest_is_k_cs(self):
        sc = ShardedChernSimonChain()
        assert sc.primary_digest() == K_CS

    def test_update_returns_valid_shard_slot(self):
        sc = ShardedChernSimonChain()
        slot = sc.update(42)
        assert 0 <= slot < SHARD_COUNT

    def test_shard_counts_sum_equals_ballot_count(self):
        sc = ShardedChernSimonChain()
        for i in range(10):
            sc.update(i)
        assert sum(sc.shard_counts()) == 10

    def test_all_shard_digests_length(self):
        sc = ShardedChernSimonChain()
        digests = sc.all_shard_digests()
        assert len(digests) == SHARD_COUNT

    def test_shard_hexdigest_format(self):
        sc = ShardedChernSimonChain()
        sc.update(1)
        h = sc.shard_hexdigest(0)
        assert len(h) == 16

    def test_shard_index_out_of_range(self):
        sc = ShardedChernSimonChain()
        with pytest.raises(IndexError):
            sc.shard_digest(SHARD_COUNT)

    def test_synchronized_shards_grows(self):
        sc = ShardedChernSimonChain()
        assert sc.synchronized_shards() == 0
        for i in range(100):
            sc.update(i)
        # After 100 ballots spread across 8 shards, all shards should have data
        assert sc.synchronized_shards() > 0

    def test_reconstruct_check_passes_with_threshold(self):
        sc = ShardedChernSimonChain()
        available = list(range(SHARD_RECONSTRUCTION_THRESHOLD))
        success, _, _ = sc.reconstruct_check(available)
        assert success is True

    def test_reconstruct_check_fails_below_threshold(self):
        sc = ShardedChernSimonChain()
        available = list(range(SHARD_RECONSTRUCTION_THRESHOLD - 1))
        success, _, _ = sc.reconstruct_check(available)
        assert success is False

    def test_telemetry_dict_structure(self):
        sc = ShardedChernSimonChain()
        sc.update(1)
        telemetry = sc.get_telemetry()
        assert "primary_hash" in telemetry
        assert "ballot_count" in telemetry
        assert "shard_digests" in telemetry
        assert len(telemetry["shard_digests"]) == SHARD_COUNT
        assert "parity_check" in telemetry

    def test_primary_ballot_count(self):
        sc = ShardedChernSimonChain()
        for i in range(7):
            sc.update(i)
        assert sc.primary_ballot_count() == 7
