# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/recovery_kernel.py"""

import json
import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.recovery_kernel import RecoveryKernel
from EIGE.src.constants import K_CS


def make_kernel(tmp_dir):
    path = os.path.join(tmp_dir, "ledger.dat")
    return RecoveryKernel(ledger_file=path), path


class TestBootWithIntegrityAssertion:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp(prefix="eige_test_recovery_")

    def test_missing_ledger_returns_false(self):
        kernel = RecoveryKernel(ledger_file="/nonexistent/ledger.dat")
        assert kernel.boot_with_integrity_assertion() is False

    def test_empty_ledger_returns_true(self):
        kernel, path = make_kernel(self.tmp)
        open(path, "w").close()
        assert kernel.boot_with_integrity_assertion() is True

    def test_single_valid_block_passes(self):
        kernel, path = make_kernel(self.tmp)
        block = kernel.build_block(1, [
            {"ballot_id": 1, "selection_vector": [1, 0], "sequence_index": 1}
        ])
        kernel.write_block(block)
        assert kernel.boot_with_integrity_assertion() is True

    def test_multiple_valid_blocks_pass(self):
        kernel, path = make_kernel(self.tmp)
        prev_hash = None
        for i in range(5):
            block = kernel.build_block(
                block_id=i + 1,
                records=[{"ballot_id": i + 1, "selection_vector": [1], "sequence_index": i + 1}],
                previous_block_hash=prev_hash,
            )
            kernel.write_block(block)
            prev_hash = block["block_state_hash"]
        assert kernel.boot_with_integrity_assertion() is True

    def test_tampered_block_hash_fails(self):
        kernel, path = make_kernel(self.tmp)
        block = kernel.build_block(
            1,
            [{"ballot_id": 1, "selection_vector": [1, 0], "sequence_index": 1}]
        )
        # Tamper the block state hash
        block["block_state_hash"] = "tampered" + "0" * 120
        kernel.write_block(block)
        assert kernel.boot_with_integrity_assertion() is False

    def test_tampered_record_fails(self):
        kernel, path = make_kernel(self.tmp)
        block = kernel.build_block(
            1,
            [{"ballot_id": 1, "selection_vector": [1, 0], "sequence_index": 1}]
        )
        kernel.write_block(block)

        # Manually tamper the ledger file content
        with open(path, "r") as f:
            content = f.read()
        tampered = content.replace('"selection_vector": [1, 0]', '"selection_vector": [9, 9]')
        with open(path, "w") as f:
            f.write(tampered)

        assert kernel.boot_with_integrity_assertion() is False

    def test_invalid_json_line_fails(self):
        kernel, path = make_kernel(self.tmp)
        with open(path, "w") as f:
            f.write("NOT VALID JSON\n")
        assert kernel.boot_with_integrity_assertion() is False

    def test_wrong_k_cs_fails(self):
        kernel, path = make_kernel(self.tmp)
        block = kernel.build_block(
            1,
            [{"ballot_id": 1, "selection_vector": [1], "sequence_index": 1}]
        )
        block["k_cs_level"] = 73  # Wrong
        kernel.write_block(block)
        assert kernel.boot_with_integrity_assertion() is False

    def test_missing_k_cs_is_accepted(self):
        kernel, path = make_kernel(self.tmp)
        block = kernel.build_block(
            1,
            [{"ballot_id": 1, "selection_vector": [1], "sequence_index": 1}]
        )
        # Remove k_cs_level — should still pass (optional field)
        del block["k_cs_level"]
        kernel.write_block(block)
        assert kernel.boot_with_integrity_assertion() is True


class TestReconstructFromShards:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.kernel = RecoveryKernel(
            ledger_file=os.path.join(self.tmp, "ledger.dat")
        )

    def test_five_shards_meet_threshold(self):
        assert self.kernel.reconstruct_from_shards([0, 1, 2, 3, 4]) is True

    def test_all_eight_shards_passes(self):
        assert self.kernel.reconstruct_from_shards(list(range(8))) is True

    def test_four_shards_fails(self):
        assert self.kernel.reconstruct_from_shards([0, 1, 2, 3]) is False

    def test_zero_shards_fails(self):
        assert self.kernel.reconstruct_from_shards([]) is False

    def test_duplicate_indices_deduplicated(self):
        # Duplicates should not count as extra shards
        assert self.kernel.reconstruct_from_shards([0, 0, 0, 0, 0, 1, 2, 3]) is False

    def test_with_shard_digests(self):
        digests = {i: f"{i:016x}" for i in range(8)}
        result = self.kernel.reconstruct_from_shards(list(range(5)), shard_digests=digests)
        assert result is True


class TestGetLastBlockHash:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()

    def test_empty_ledger_returns_genesis_hash(self):
        kernel, path = make_kernel(self.tmp)
        open(path, "w").close()
        assert kernel.get_last_block_hash() == RecoveryKernel.GENESIS_HASH

    def test_missing_ledger_returns_genesis_hash(self):
        kernel = RecoveryKernel(ledger_file="/nonexistent/path.dat")
        assert kernel.get_last_block_hash() == RecoveryKernel.GENESIS_HASH

    def test_after_one_block(self):
        kernel, path = make_kernel(self.tmp)
        block = kernel.build_block(
            1,
            [{"ballot_id": 1, "selection_vector": [1], "sequence_index": 1}]
        )
        kernel.write_block(block)
        h = kernel.get_last_block_hash()
        assert h == block["block_state_hash"]
        assert len(h) == 128  # SHA-512 hex
