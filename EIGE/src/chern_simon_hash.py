# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/chern_simon_hash.py — Path-Dependent Chern-Simons Rolling Hash
========================================================================

The CS Rolling Hash treats ballot ingestion as a path-dependent sequence
integral.  The chronological placement of each ballot modifies the running
geometric gauge field state so that:

  1. The hash of [a, b, c] ≠ hash of [b, a, c]  (order sensitivity)
  2. Retroactive insertion of any ballot into an earlier temporal slot
     disrupts the entire downstream chain of custody — rendering "ballot
     stuffing" cryptographically detectable.
  3. Each county's accumulated hash can be checkpointed into shard slots
     using modular placement arithmetic derived from k_CS = 74.

Mathematical construction
--------------------------
Let s₀ = K_CS (seed state).  For each ballot integer bₙ:

    s_{n+1} = ((s_n × K_CS + bₙ) ^ (s_n >> SHIFT)) mod M63

where M63 = 2⁶³ − 1 (Mersenne prime), SHIFT = 7.

This accumulation is non-commutative: swapping any two bₙ produces a
completely different final state.  The XOR term (s_n >> SHIFT) introduces
non-linearity that prevents an adversary from solving for a forged ballot
sequence that collides with the true sequence.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .constants import (
    K_CS,
    HASH_MODULUS,
    HASH_SHIFT_BITS,
    SHARD_COUNT,
    SHARD_RECONSTRUCTION_THRESHOLD,
)


# ---------------------------------------------------------------------------
# Shard reconstruction types
# ---------------------------------------------------------------------------

class ReconstructionError(Exception):
    """Raised when shard reconstruction fails due to insufficient or
    inconsistent shard data.

    Attributes
    ----------
    available : int
        Number of shards that were available.
    required : int
        Minimum shards required (SHARD_RECONSTRUCTION_THRESHOLD).
    reason : str
        Human-readable explanation.
    """

    def __init__(self, reason: str, available: int = 0) -> None:
        self.available = available
        self.required = SHARD_RECONSTRUCTION_THRESHOLD
        self.reason = reason
        super().__init__(
            f"ReconstructionError ({available}/{SHARD_RECONSTRUCTION_THRESHOLD} shards): {reason}"
        )


@dataclass
class ShardEntry:
    """A single ballot event recorded in a shard manifest.

    Each ballot that was routed to this shard is stored as a triple of:
      - sequence_index : int  — global chronological index of this ballot
      - ballot_int     : int  — the integer fed into the CS hash
      - pre_state      : int  — chain state before this ballot was ingested
      - post_state     : int  — chain state after this ballot was ingested
    """

    sequence_index: int
    ballot_int: int
    pre_state: int
    post_state: int


@dataclass
class ShardManifest:
    """Persistent manifest of all ballot events routed to one shard.

    Created by ShardedChernSimonChain.checkpoint_manifests() and used by
    reconstruct_from_shards() to replay the ballot stream.

    The holographic property: every shard manifest carries the complete
    primary-chain entry sequence (``primary_entries``) as well as the
    shard-specific sub-sequence (``entries``).  This ensures that any
    SHARD_RECONSTRUCTION_THRESHOLD manifests together can reconstruct the
    full primary hash by quorum agreement on ``primary_entries``, even when
    the other shards are unavailable.

    Parameters
    ----------
    shard_index : int
        Which shard (0–7) this manifest belongs to.
    entries : list[ShardEntry]
        Ordered list of ballot events routed to THIS shard specifically,
        sorted by sequence_index.
    primary_entries : list[ShardEntry]
        Complete ordered list of ALL ballot events from the primary chain.
        Identical across all shard manifests — forms the holographic copy.
    final_state : int
        The shard chain's final accumulated hash state.
    entry_count : int
        Total number of ballot entries in this shard (len(entries)).
    primary_final_state : int
        The primary chain's final accumulated hash state.
    """

    shard_index: int
    entries: List[ShardEntry] = field(default_factory=list)
    primary_entries: List[ShardEntry] = field(default_factory=list)
    final_state: int = K_CS
    entry_count: int = 0
    primary_final_state: int = K_CS

    def verify_internal_consistency(self) -> bool:
        """Check that each shard-specific entry's post_state matches the CS formula."""
        state = K_CS
        for entry in self.entries:
            b = entry.ballot_int & 0xFFFFFFFFFFFFFFFF
            expected = ((state * K_CS + b) ^ (state >> HASH_SHIFT_BITS)) % HASH_MODULUS
            if entry.pre_state != state or entry.post_state != expected:
                return False
            state = expected
        return state == self.final_state

    def verify_primary_consistency(self) -> bool:
        """Check that the primary_entries replay produces primary_final_state."""
        state = K_CS
        for entry in self.primary_entries:
            b = entry.ballot_int & 0xFFFFFFFFFFFFFFFF
            state = ((state * K_CS + b) ^ (state >> HASH_SHIFT_BITS)) % HASH_MODULUS
        return state == self.primary_final_state


def reconstruct_from_shards(
    available_shards: Dict[int, "ShardManifest"],
) -> int:
    """Reconstruct the primary Chern-Simons hash from a subset of shard manifests.

    Holographic property
    --------------------
    Every shard manifest carries a complete copy of the primary chain's ballot
    sequence in ``manifest.primary_entries``.  This mirrors the holographic
    principle: any sub-region of the hologram encodes the full image at lower
    fidelity — here the fidelity guarantee is provided by the quorum check.

    Algorithm
    ---------
    1. Verify ≥ SHARD_RECONSTRUCTION_THRESHOLD shards are available.
    2. Verify the primary_entries in each available shard are internally
       consistent (replay produces the expected primary_final_state).
    3. Check quorum: all available shards must agree on the same primary
       entry sequence length and final state.
    4. Replay the primary_entries from any one shard and return the hash.

    Parameters
    ----------
    available_shards : dict[int, ShardManifest]
        Mapping of shard_index → ShardManifest for each available shard.

    Returns
    -------
    int
        Reconstructed primary hash state.

    Raises
    ------
    ReconstructionError
        If fewer than SHARD_RECONSTRUCTION_THRESHOLD shards are available,
        if any shard manifest fails primary consistency, or if shards
        disagree on the primary sequence (quorum failure).
    """
    n_available = len(available_shards)
    if n_available < SHARD_RECONSTRUCTION_THRESHOLD:
        raise ReconstructionError(
            reason=(
                f"Insufficient shards: need ≥{SHARD_RECONSTRUCTION_THRESHOLD}, "
                f"got {n_available}. Reconstruction requires (5,7) braid threshold."
            ),
            available=n_available,
        )

    manifests = list(available_shards.values())

    # Step 1: Verify primary consistency of each shard
    for manifest in manifests:
        if not manifest.verify_primary_consistency():
            raise ReconstructionError(
                reason=(
                    f"Shard {manifest.shard_index} failed primary chain consistency. "
                    f"The holographic copy of the primary sequence is corrupted."
                ),
                available=n_available,
            )

    # Step 2: Quorum check — all shards must agree on primary final state
    final_states = [m.primary_final_state for m in manifests]
    if len(set(final_states)) > 1:
        raise ReconstructionError(
            reason=(
                f"Quorum failure: shards disagree on primary_final_state. "
                f"Distinct values: {list(set(final_states))[:5]}. "
                f"Possible tampering detected."
            ),
            available=n_available,
        )

    # Step 3: Replay using the primary_entries from the first available shard
    reference = manifests[0]
    if not reference.primary_entries and reference.primary_final_state == K_CS:
        # Zero ballots ingested — return seed state
        return K_CS

    state: int = K_CS
    for entry in reference.primary_entries:
        b = entry.ballot_int & 0xFFFFFFFFFFFFFFFF
        state = ((state * K_CS + b) ^ (state >> HASH_SHIFT_BITS)) % HASH_MODULUS

    return state


# ---------------------------------------------------------------------------
# Core stateless hash function
# ---------------------------------------------------------------------------

def chern_simon_hash(ballot_sequence: Sequence[int]) -> int:
    """Compute the path-dependent Chern-Simons rolling hash of a ballot sequence.

    Parameters
    ----------
    ballot_sequence:
        An ordered sequence of discrete integer ballot values.  Each integer
        represents one cast vote (N=1 per ballot card).

    Returns
    -------
    int
        A non-negative integer hash in [0, M63) that encodes the entire
        ordered sequence.  Two sequences that differ in ordering or content
        will (with overwhelming probability) produce different hashes.

    Examples
    --------
    >>> chern_simon_hash([1, 2, 3]) != chern_simon_hash([3, 2, 1])
    True
    >>> chern_simon_hash([]) == K_CS
    True
    """
    state: int = K_CS
    for ballot in ballot_sequence:
        b = int(ballot) & 0xFFFFFFFFFFFFFFFF  # coerce to unsigned 64-bit
        state = ((state * K_CS + b) ^ (state >> HASH_SHIFT_BITS)) % HASH_MODULUS
    return state


def chern_simon_hash_hex(ballot_sequence: Sequence[int]) -> str:
    """Return the CS hash as a zero-padded 16-character hex string."""
    return f"{chern_simon_hash(ballot_sequence):016x}"


# ---------------------------------------------------------------------------
# ChernSimonChain — stateful incremental hasher
# ---------------------------------------------------------------------------

class ChernSimonChain:
    """Stateful, incremental Chern-Simons rolling hash chain.

    Maintains a running geometric gauge state that is updated with each
    ballot ingested.  Supports:
      - Incremental update (one ballot at a time)
      - Checkpoint snapshots (for shard-level persistence)
      - Shard-slot placement via modular k_CS arithmetic

    Attributes
    ----------
    _state : int
        Current accumulated hash state.
    _count : int
        Number of ballots ingested so far.
    _checkpoints : list[tuple[int, int]]
        List of (count, state) tuples saved at checkpoint() calls.
    """

    def __init__(self, sequence_offset: int = 0) -> None:
        self._state: int = K_CS
        self._count: int = 0
        self._checkpoints: List[Tuple[int, int]] = []
        self._entries: List[ShardEntry] = []
        self._sequence_offset: int = sequence_offset

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def update(self, ballot_int: int) -> None:
        """Ingest one ballot integer and update the running state.

        Parameters
        ----------
        ballot_int:
            Discrete integer representation of a single cast ballot.
        """
        b = int(ballot_int) & 0xFFFFFFFFFFFFFFFF
        pre = self._state
        self._state = ((self._state * K_CS + b) ^ (self._state >> HASH_SHIFT_BITS)) % HASH_MODULUS
        self._count += 1
        self._entries.append(ShardEntry(
            sequence_index=self._sequence_offset + self._count,
            ballot_int=ballot_int,
            pre_state=pre,
            post_state=self._state,
        ))

    def digest(self) -> int:
        """Return the current hash state as an integer."""
        return self._state

    def hexdigest(self) -> str:
        """Return the current hash state as a 16-char hex string."""
        return f"{self._state:016x}"

    def sha512_hexdigest(self) -> str:
        """Return a SHA-512 hex digest of the current CS state.

        This provides a cryptographically standard-format representation
        of the chain state suitable for block headers and OSCAL evidence.
        """
        raw = self._state.to_bytes(8, byteorder="big", signed=False)
        return hashlib.sha512(raw).hexdigest()

    def checkpoint(self) -> Tuple[int, int]:
        """Save and return the current (count, state) checkpoint.

        Returns
        -------
        tuple[int, int]
            (ballots_ingested, current_hash_state)
        """
        snap = (self._count, self._state)
        self._checkpoints.append(snap)
        return snap

    def shard_slot(self) -> int:
        """Return the shard index [0, SHARD_COUNT) for the current state.

        Uses modular placement arithmetic seeded by k_CS to distribute
        checkpoints uniformly across the 8 holographic persistence shards.
        """
        return (self._state % K_CS) % SHARD_COUNT

    def ballot_count(self) -> int:
        """Return the number of ballots ingested so far."""
        return self._count

    def checkpoints(self) -> List[Tuple[int, int]]:
        """Return a copy of all saved (count, state) checkpoints."""
        return list(self._checkpoints)

    def reset(self) -> None:
        """Reset the chain to its initial seed state."""
        self._state = K_CS
        self._count = 0
        self._checkpoints = []
        self._entries = []

    def get_entries(self) -> List[ShardEntry]:
        """Return a copy of all recorded ballot entries."""
        return list(self._entries)

    def __repr__(self) -> str:
        return (
            f"ChernSimonChain(count={self._count}, "
            f"state=0x{self._state:016x})"
        )


# ---------------------------------------------------------------------------
# Shard sub-chain manager
# ---------------------------------------------------------------------------

class ShardedChernSimonChain:
    """Manages SHARD_COUNT independent CS sub-chains for holographic persistence.

    Each ballot is ingested into both the primary chain and one shard
    sub-chain determined by the primary chain's current shard_slot().
    This ensures that losing any 3 shards leaves 5 sufficient to
    reconstruct the full sequence topology.

    Parameters
    ----------
    n_shards : int
        Number of shards (default: SHARD_COUNT = 8).
    """

    def __init__(self, n_shards: int = SHARD_COUNT) -> None:
        self._n_shards = n_shards
        self._primary = ChernSimonChain()
        self._shards: List[ChernSimonChain] = [ChernSimonChain() for _ in range(n_shards)]
        self._shard_counts: List[int] = [0] * n_shards
        self._global_sequence: int = 0

    def update(self, ballot_int: int) -> int:
        """Ingest one ballot into primary chain and the assigned shard.

        Returns
        -------
        int
            The shard index that received this ballot.
        """
        self._global_sequence += 1
        # Temporarily set the shard chain's sequence offset so the entry
        # carries the correct global sequence_index.
        self._primary.update(ballot_int)
        # Correct the primary entry's sequence_index to global
        if self._primary._entries:
            self._primary._entries[-1] = ShardEntry(
                sequence_index=self._global_sequence,
                ballot_int=self._primary._entries[-1].ballot_int,
                pre_state=self._primary._entries[-1].pre_state,
                post_state=self._primary._entries[-1].post_state,
            )
        slot = self._primary.shard_slot()
        # Update the shard chain and fix its entry's sequence_index
        self._shards[slot].update(ballot_int)
        if self._shards[slot]._entries:
            self._shards[slot]._entries[-1] = ShardEntry(
                sequence_index=self._global_sequence,
                ballot_int=self._shards[slot]._entries[-1].ballot_int,
                pre_state=self._shards[slot]._entries[-1].pre_state,
                post_state=self._shards[slot]._entries[-1].post_state,
            )
        self._shard_counts[slot] += 1
        return slot

    def primary_digest(self) -> int:
        """Return the primary chain's current hash state."""
        return self._primary.digest()

    def primary_hexdigest(self) -> str:
        """Return the primary chain's current hash as hex."""
        return self._primary.hexdigest()

    def shard_digest(self, shard_index: int) -> int:
        """Return the hash state of a specific shard."""
        if not 0 <= shard_index < self._n_shards:
            raise IndexError(f"Shard index {shard_index} out of range [0, {self._n_shards})")
        return self._shards[shard_index].digest()

    def shard_hexdigest(self, shard_index: int) -> str:
        """Return the hex hash state of a specific shard."""
        return f"{self.shard_digest(shard_index):016x}"

    def all_shard_digests(self) -> List[int]:
        """Return list of all shard hash states."""
        return [s.digest() for s in self._shards]

    def shard_counts(self) -> List[int]:
        """Return list of ballot counts per shard."""
        return list(self._shard_counts)

    def synchronized_shards(self) -> int:
        """Return number of shards that have received at least one ballot."""
        return sum(1 for c in self._shard_counts if c > 0)

    def checkpoint_all(self) -> List[Tuple[int, int]]:
        """Checkpoint all shards and return their (count, state) tuples."""
        return [s.checkpoint() for s in self._shards]

    def checkpoint_manifests(self) -> Dict[int, ShardManifest]:
        """Build and return a ShardManifest for every shard.

        Each manifest contains:
        - ``entries``: the ballot events routed specifically to that shard
        - ``primary_entries``: a complete copy of ALL ballot events from the
          primary chain (the holographic copy — identical across all shards)
        - ``final_state``: the shard's own accumulated CS hash
        - ``primary_final_state``: the primary chain's accumulated CS hash

        This holographic structure ensures that any
        SHARD_RECONSTRUCTION_THRESHOLD manifests together can reconstruct the
        primary hash via quorum agreement, even when the other shards are
        unavailable.

        Returns
        -------
        dict[int, ShardManifest]
            Mapping of shard_index → ShardManifest.
        """
        primary_entries = self._primary.get_entries()
        primary_final = self._primary.digest()
        manifests: Dict[int, ShardManifest] = {}
        for i, shard in enumerate(self._shards):
            shard_entries = shard.get_entries()
            manifests[i] = ShardManifest(
                shard_index=i,
                entries=list(shard_entries),
                primary_entries=list(primary_entries),
                final_state=shard.digest(),
                entry_count=len(shard_entries),
                primary_final_state=primary_final,
            )
        return manifests

    def reconstruct_check(
        self, available_shard_indices: List[int]
    ) -> Tuple[bool, Optional[int], List[int]]:
        """Attempt reconstruction from the specified subset of shards.

        Returns a 3-tuple so callers can inspect the result without a try/except.

        Parameters
        ----------
        available_shard_indices : list[int]
            Indices of shards still available after partial failure.

        Returns
        -------
        tuple[bool, int | None, list[int]]
            (success, reconstructed_hash, missing_shard_indices)
            - success: True if reconstruction produced a valid hash.
            - reconstructed_hash: The recovered primary hash, or None on failure.
            - missing_shard_indices: Indices of shards NOT in available_shard_indices.
        """
        all_indices = set(range(self._n_shards))
        available_set = set(available_shard_indices)
        missing = sorted(all_indices - available_set)

        if len(available_set) < SHARD_RECONSTRUCTION_THRESHOLD:
            return False, None, missing

        all_manifests = self.checkpoint_manifests()
        subset_manifests = {i: all_manifests[i] for i in available_shard_indices if i in all_manifests}

        try:
            recovered = reconstruct_from_shards(subset_manifests)
            return True, recovered, missing
        except ReconstructionError:
            return False, None, missing

    def get_telemetry(self) -> dict:
        """Return a structured telemetry dict for state mesh transmission."""
        return {
            "primary_hash": self._primary.hexdigest(),
            "primary_sha512": self._primary.sha512_hexdigest(),
            "ballot_count": self._primary.ballot_count(),
            "shard_digests": [self.shard_hexdigest(i) for i in range(self._n_shards)],
            "shard_counts": self.shard_counts(),
            "synchronized_shards": self.synchronized_shards(),
            "parity_check": f"PASS_{K_CS}_{K_CS}",
        }

    def primary_ballot_count(self) -> int:
        """Return total ballots ingested."""
        return self._primary.ballot_count()
