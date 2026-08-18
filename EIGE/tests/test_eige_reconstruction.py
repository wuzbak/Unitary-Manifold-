# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/tests/test_eige_reconstruction.py — Holographic Reconstruction Test Suite
===============================================================================

Tests the ShardManifest persistence layer and reconstruct_from_shards()
algorithm that recovers the primary Chern-Simons hash from any 5-of-8
holographic shards.

Holographic property: every shard manifest carries a complete copy of the
primary chain's ballot sequence (primary_entries), so any
SHARD_RECONSTRUCTION_THRESHOLD shards can reconstruct by quorum agreement.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import pytest

from src.chern_simon_hash import (
    ShardedChernSimonChain,
    ShardManifest,
    ShardEntry,
    ReconstructionError,
    reconstruct_from_shards,
    chern_simon_hash,
)
from src.constants import (
    K_CS,
    SHARD_COUNT,
    SHARD_RECONSTRUCTION_THRESHOLD,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chain_with_ballots(ballot_ints: list) -> ShardedChernSimonChain:
    chain = ShardedChernSimonChain()
    for b in ballot_ints:
        chain.update(b)
    return chain


SAMPLE_BALLOTS = list(range(1, 41))  # 40 distinct ballot integers


# ---------------------------------------------------------------------------
# ShardManifest construction
# ---------------------------------------------------------------------------

class TestShardManifestConstruction:
    def test_manifests_created_for_all_shards(self):
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        assert len(manifests) == SHARD_COUNT
        for i in range(SHARD_COUNT):
            assert i in manifests

    def test_manifest_entry_count_matches_shard_counts(self):
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        shard_counts = chain.shard_counts()
        for i in range(SHARD_COUNT):
            assert manifests[i].entry_count == shard_counts[i]
            assert len(manifests[i].entries) == shard_counts[i]

    def test_total_entries_across_shards_equals_ballot_count(self):
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        total = sum(len(m.entries) for m in manifests.values())
        assert total == len(SAMPLE_BALLOTS)

    def test_every_manifest_has_full_primary_entries(self):
        """Holographic property: every manifest holds the complete primary sequence."""
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        expected_len = len(SAMPLE_BALLOTS)
        for m in manifests.values():
            assert len(m.primary_entries) == expected_len

    def test_all_manifests_agree_on_primary_final_state(self):
        """Holographic property: every shard manifest records the same primary hash."""
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        primary = chain.primary_digest()
        for m in manifests.values():
            assert m.primary_final_state == primary

    def test_manifest_sequence_indices_are_unique_and_contiguous(self):
        """Per-shard entries collectively cover all sequence indices."""
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        all_indices = sorted(
            e.sequence_index
            for m in manifests.values()
            for e in m.entries
        )
        assert all_indices == list(range(1, len(SAMPLE_BALLOTS) + 1))

    def test_primary_entries_cover_all_sequence_indices(self):
        """Each manifest's primary_entries cover every ballot in order."""
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        for m in manifests.values():
            indices = [e.sequence_index for e in m.primary_entries]
            assert indices == list(range(1, len(SAMPLE_BALLOTS) + 1))

    def test_manifest_final_state_matches_shard_digest(self):
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        for i, manifest in manifests.items():
            assert manifest.final_state == chain.shard_digest(i)

    def test_empty_chain_manifests(self):
        chain = ShardedChernSimonChain()
        manifests = chain.checkpoint_manifests()
        for m in manifests.values():
            assert m.entry_count == 0
            assert m.entries == []
            assert m.primary_entries == []
            assert m.final_state == K_CS
            assert m.primary_final_state == K_CS

    def test_single_ballot_manifest(self):
        chain = _make_chain_with_ballots([42])
        manifests = chain.checkpoint_manifests()
        active_shards = [i for i, m in manifests.items() if m.entry_count > 0]
        assert len(active_shards) == 1
        assert manifests[active_shards[0]].entries[0].ballot_int == 42
        assert manifests[active_shards[0]].entries[0].sequence_index == 1
        # Holographic: every shard has primary_entries with that 1 ballot
        for m in manifests.values():
            assert len(m.primary_entries) == 1
            assert m.primary_entries[0].ballot_int == 42


# ---------------------------------------------------------------------------
# ShardManifest internal consistency
# ---------------------------------------------------------------------------

class TestShardManifestConsistency:
    def test_all_manifests_pass_internal_consistency(self):
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        for manifest in manifests.values():
            assert manifest.verify_internal_consistency()

    def test_all_manifests_pass_primary_consistency(self):
        chain = _make_chain_with_ballots(SAMPLE_BALLOTS)
        manifests = chain.checkpoint_manifests()
        for manifest in manifests.values():
            assert manifest.verify_primary_consistency()

    def test_tampered_ballot_int_fails_consistency(self):
        chain = _make_chain_with_ballots([10, 20, 30])
        manifests = chain.checkpoint_manifests()
        # Find a shard with at least one shard-specific entry and tamper it
        for m in manifests.values():
            if m.entries:
                original = m.entries[0]
                m.entries[0] = ShardEntry(
                    sequence_index=original.sequence_index,
                    ballot_int=original.ballot_int + 1,  # tamper
                    pre_state=original.pre_state,
                    post_state=original.post_state,
                )
                assert not m.verify_internal_consistency()
                break

    def test_tampered_post_state_fails_consistency(self):
        chain = _make_chain_with_ballots([10, 20, 30])
        manifests = chain.checkpoint_manifests()
        for m in manifests.values():
            if m.entries:
                original = m.entries[0]
                m.entries[0] = ShardEntry(
                    sequence_index=original.sequence_index,
                    ballot_int=original.ballot_int,
                    pre_state=original.pre_state,
                    post_state=original.post_state ^ 0xDEAD,  # tamper
                )
                assert not m.verify_internal_consistency()
                break

    def test_tampered_primary_entry_fails_primary_consistency(self):
        chain = _make_chain_with_ballots([10, 20, 30])
        manifests = chain.checkpoint_manifests()
        for m in manifests.values():
            if m.primary_entries:
                e = m.primary_entries[0]
                m.primary_entries[0] = ShardEntry(
                    sequence_index=e.sequence_index,
                    ballot_int=e.ballot_int + 999,  # tamper
                    pre_state=e.pre_state,
                    post_state=e.post_state,
                )
                assert not m.verify_primary_consistency()
                break

    def test_empty_shard_manifest_passes_consistency(self):
        m = ShardManifest(shard_index=0, entries=[], final_state=K_CS, entry_count=0)
        assert m.verify_internal_consistency()

    def test_empty_shard_manifest_passes_primary_consistency(self):
        m = ShardManifest(shard_index=0, primary_entries=[], primary_final_state=K_CS)
        assert m.verify_primary_consistency()


# ---------------------------------------------------------------------------
# reconstruct_from_shards — success paths
# ---------------------------------------------------------------------------

class TestReconstructSuccess:
    def test_all_8_shards(self):
        chain = _make_chain_with_ballots(list(range(100, 140)))
        primary = chain.primary_digest()
        manifests = chain.checkpoint_manifests()
        result = reconstruct_from_shards(manifests)
        assert result == primary

    def test_exactly_7_shards(self):
        chain = _make_chain_with_ballots(list(range(100, 180)))
        primary = chain.primary_digest()
        all_manifests = chain.checkpoint_manifests()
        # Drop any one shard — all remaining have full primary_entries
        subset = {i: m for i, m in all_manifests.items() if i != 0}
        assert len(subset) == 7
        result = reconstruct_from_shards(subset)
        assert result == primary

    def test_exactly_6_shards(self):
        chain = _make_chain_with_ballots(list(range(200, 280)))
        primary = chain.primary_digest()
        all_manifests = chain.checkpoint_manifests()
        subset = {i: m for i, m in all_manifests.items() if i not in (0, 1)}
        assert len(subset) == 6
        result = reconstruct_from_shards(subset)
        assert result == primary

    def test_exactly_5_shards(self):
        chain = _make_chain_with_ballots(list(range(300, 380)))
        primary = chain.primary_digest()
        all_manifests = chain.checkpoint_manifests()
        # Drop any 3 shards — remaining 5 each have full primary_entries
        subset = {i: m for i, m in all_manifests.items() if i not in (0, 1, 2)}
        assert len(subset) == 5
        result = reconstruct_from_shards(subset)
        assert result == primary

    def test_any_combination_of_5_shards_works(self):
        """Try multiple different 5-shard subsets — all should reconstruct correctly."""
        chain = _make_chain_with_ballots(list(range(50, 90)))
        primary = chain.primary_digest()
        all_manifests = chain.checkpoint_manifests()
        combos = [
            (0, 1, 2, 3, 4),
            (3, 4, 5, 6, 7),
            (0, 2, 4, 6, 7),
            (1, 3, 5, 6, 7),
        ]
        for drop in [set(range(8)) - set(c) for c in combos]:
            subset = {i: m for i, m in all_manifests.items() if i not in drop}
            assert reconstruct_from_shards(subset) == primary

    def test_reconstructed_hash_equals_primary_digest(self):
        chain = _make_chain_with_ballots([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        primary = chain.primary_digest()
        all_manifests = chain.checkpoint_manifests()
        result = reconstruct_from_shards(all_manifests)
        assert result == primary

    def test_zero_ballots_returns_seed(self):
        chain = ShardedChernSimonChain()
        manifests = chain.checkpoint_manifests()
        result = reconstruct_from_shards(manifests)
        assert result == K_CS

    def test_reconstruction_is_deterministic(self):
        chain = _make_chain_with_ballots(list(range(50)))
        all_manifests = chain.checkpoint_manifests()
        r1 = reconstruct_from_shards(all_manifests)
        r2 = reconstruct_from_shards(all_manifests)
        assert r1 == r2

    def test_single_ballot_reconstruction(self):
        chain = _make_chain_with_ballots([999])
        primary = chain.primary_digest()
        manifests = chain.checkpoint_manifests()
        subset = {i: manifests[i] for i in range(5)}
        result = reconstruct_from_shards(subset)
        assert result == primary


# ---------------------------------------------------------------------------
# reconstruct_from_shards — failure paths
# ---------------------------------------------------------------------------

class TestReconstructFailure:
    def test_4_shards_raises_reconstruction_error(self):
        chain = _make_chain_with_ballots(list(range(1, 50)))
        all_manifests = chain.checkpoint_manifests()
        subset = {i: all_manifests[i] for i in range(4)}
        with pytest.raises(ReconstructionError) as exc_info:
            reconstruct_from_shards(subset)
        assert exc_info.value.available == 4
        assert exc_info.value.required == SHARD_RECONSTRUCTION_THRESHOLD

    def test_3_shards_raises_reconstruction_error(self):
        chain = _make_chain_with_ballots(list(range(1, 40)))
        all_manifests = chain.checkpoint_manifests()
        subset = {i: all_manifests[i] for i in range(3)}
        with pytest.raises(ReconstructionError):
            reconstruct_from_shards(subset)

    def test_0_shards_raises_reconstruction_error(self):
        with pytest.raises(ReconstructionError):
            reconstruct_from_shards({})

    def test_tampered_primary_entry_raises_reconstruction_error(self):
        chain = _make_chain_with_ballots([10, 20, 30, 40, 50, 60, 70, 80])
        all_manifests = chain.checkpoint_manifests()
        # Tamper one shard's primary_entries
        m = all_manifests[0]
        if m.primary_entries:
            e = m.primary_entries[0]
            m.primary_entries[0] = ShardEntry(
                sequence_index=e.sequence_index,
                ballot_int=e.ballot_int + 999,
                pre_state=e.pre_state,
                post_state=e.post_state,
            )
        with pytest.raises(ReconstructionError):
            reconstruct_from_shards(all_manifests)

    def test_quorum_disagreement_raises_reconstruction_error(self):
        """Two shards with different primary_final_state raise ReconstructionError."""
        chain = _make_chain_with_ballots(list(range(1, 20)))
        all_manifests = chain.checkpoint_manifests()
        # Force a disagreement on primary_final_state for one shard
        all_manifests[0] = ShardManifest(
            shard_index=0,
            entries=all_manifests[0].entries,
            primary_entries=all_manifests[0].primary_entries,
            final_state=all_manifests[0].final_state,
            entry_count=all_manifests[0].entry_count,
            primary_final_state=all_manifests[0].primary_final_state ^ 0xDEADC0DE,
        )
        # Either consistency or quorum error is acceptable
        with pytest.raises(ReconstructionError):
            reconstruct_from_shards(all_manifests)

    def test_error_message_contains_shard_counts(self):
        with pytest.raises(ReconstructionError) as exc_info:
            reconstruct_from_shards({0: ShardManifest(0), 1: ShardManifest(1)})
        msg = str(exc_info.value)
        assert "2/" in msg or "2" in msg


# ---------------------------------------------------------------------------
# reconstruct_check() — upgraded interface
# ---------------------------------------------------------------------------

class TestReconstructCheck:
    def test_reconstruct_check_success_with_all_shards(self):
        chain = _make_chain_with_ballots(list(range(1, 30)))
        success, reconstructed, missing = chain.reconstruct_check(list(range(8)))
        assert success is True
        assert reconstructed == chain.primary_digest()
        assert missing == []

    def test_reconstruct_check_success_with_5_shards(self):
        """Any 5-shard subset should succeed since all shards have primary_entries."""
        chain = _make_chain_with_ballots(list(range(1, 50)))
        available = [3, 4, 5, 6, 7]  # any 5
        success, reconstructed, missing = chain.reconstruct_check(available)
        assert success is True
        assert reconstructed == chain.primary_digest()
        assert sorted(missing) == [0, 1, 2]

    def test_reconstruct_check_success_with_7_shards(self):
        chain = _make_chain_with_ballots(list(range(10, 60)))
        available = list(range(7))  # drop shard 7
        success, reconstructed, missing = chain.reconstruct_check(available)
        assert success is True
        assert reconstructed == chain.primary_digest()
        assert missing == [7]

    def test_reconstruct_check_failure_with_4_shards(self):
        chain = _make_chain_with_ballots(list(range(1, 30)))
        success, reconstructed, missing = chain.reconstruct_check([0, 1, 2, 3])
        assert success is False
        assert reconstructed is None
        assert len(missing) == 4

    def test_reconstruct_check_empty_available_fails(self):
        chain = _make_chain_with_ballots([1, 2, 3])
        success, reconstructed, missing = chain.reconstruct_check([])
        assert success is False
        assert reconstructed is None
        assert len(missing) == 8

    def test_reconstruct_check_missing_list_correct(self):
        chain = _make_chain_with_ballots(list(range(40)))
        available = [0, 1, 2, 3, 4, 5]  # drop 6 and 7
        success, _, missing = chain.reconstruct_check(available)
        assert success is True
        assert 6 in missing
        assert 7 in missing

    def test_reconstruct_check_returns_3_tuple(self):
        chain = ShardedChernSimonChain()
        result = chain.reconstruct_check(list(range(5)))
        assert isinstance(result, tuple)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# Non-commutativity guarantee (preserved after reconstruction changes)
# ---------------------------------------------------------------------------

class TestNonCommutativityPreserved:
    def test_order_sensitivity_preserved(self):
        assert chern_simon_hash([1, 2, 3]) != chern_simon_hash([3, 2, 1])

    def test_insertion_sensitivity(self):
        a = chern_simon_hash([10, 20, 30, 40])
        b = chern_simon_hash([10, 20, 99, 30, 40])
        assert a != b

    def test_reconstruction_matches_primary_digest(self):
        """Reconstruction result == primary_digest on the chain."""
        ballots = list(range(5, 25))
        chain = _make_chain_with_ballots(ballots)
        manifests = chain.checkpoint_manifests()
        recovered = reconstruct_from_shards(manifests)
        assert recovered == chain.primary_digest()

    def test_different_ballot_order_different_reconstruction(self):
        """Two chains with reversed ballot order produce different reconstructed hashes."""
        ballots_a = [10, 20, 30, 40, 50]
        ballots_b = [50, 40, 30, 20, 10]
        chain_a = _make_chain_with_ballots(ballots_a)
        chain_b = _make_chain_with_ballots(ballots_b)
        manifests_a = chain_a.checkpoint_manifests()
        manifests_b = chain_b.checkpoint_manifests()
        hash_a = reconstruct_from_shards(manifests_a)
        hash_b = reconstruct_from_shards(manifests_b)
        assert hash_a != hash_b
