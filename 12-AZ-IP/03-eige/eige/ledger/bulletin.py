# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Public bulletin board of signed tree heads, with independent witnesses.

A county could try to show one history to the public and another to an
auditor ("split view").  This board defends against that by:

1. accepting a new head only with a valid signature and a valid consistency
   proof from the previously accepted head (append-only);
2. having independent *witnesses* (e.g. a university, a party observer, a
   newspaper) cosign heads they have checked against their own last view;
3. treating two validly signed heads for the same log and size with
   different roots as cryptographic **evidence of equivocation**.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from ..crypto import merkle
from ..crypto.signing import KeyRegistry, Signer
from .log import SignedTreeHead

COSIGN_CONTEXT = "cosign"


class BulletinError(ValueError):
    """Raised when a head is rejected."""


@dataclass(frozen=True)
class EquivocationEvidence:
    """Two validly signed, mutually inconsistent heads from the same log."""

    log_id: str
    head_a: SignedTreeHead
    head_b: SignedTreeHead
    reason: str

    def as_dict(self) -> dict:
        return {
            "format": "eige.equivocation_evidence.v1",
            "log_id": self.log_id,
            "head_a": self.head_a.as_dict(),
            "head_b": self.head_b.as_dict(),
            "reason": self.reason,
        }


class EquivocationDetected(BulletinError):
    def __init__(self, evidence: EquivocationEvidence) -> None:
        self.evidence = evidence
        super().__init__(f"equivocation by {evidence.log_id}: {evidence.reason}")


def _check_extension(prev: SignedTreeHead, new: SignedTreeHead, proof: Sequence[bytes]) -> Optional[str]:
    if new.tree_size < prev.tree_size:
        return f"tree shrank from {prev.tree_size} to {new.tree_size}"
    if new.timestamp < prev.timestamp:
        return "timestamp went backwards"
    if new.tree_size == prev.tree_size:
        return None if new.root_hash == prev.root_hash else "same tree size, different root"
    ok = merkle.verify_consistency(
        prev.tree_size, new.tree_size, bytes.fromhex(prev.root_hash), bytes.fromhex(new.root_hash), proof
    )
    return None if ok else "consistency proof failed (history rewritten or proof invalid)"


@dataclass(frozen=True)
class Cosignature:
    witness_id: str
    key_id: str
    log_id: str
    tree_size: int
    root_hash: str
    timestamp: int
    signature: str

    def payload(self) -> dict:
        return {
            "format": "eige.cosignature.v1",
            "witness_id": self.witness_id,
            "log_id": self.log_id,
            "tree_size": self.tree_size,
            "root_hash": self.root_hash,
            "timestamp": self.timestamp,
        }

    def as_dict(self) -> dict:
        return {**self.payload(), "key_id": self.key_id, "signature": self.signature}


class Witness:
    """An independent party that cosigns heads only if they extend its own view."""

    def __init__(self, witness_id: str, signer: Signer, registry: KeyRegistry) -> None:
        self.witness_id = witness_id
        self.signer = signer
        self.registry = registry
        self._latest: Dict[str, SignedTreeHead] = {}

    def latest(self, log_id: str) -> Optional[SignedTreeHead]:
        return self._latest.get(log_id)

    def cosign(self, head: SignedTreeHead, proof_from_latest: Sequence[bytes] = ()) -> Cosignature:
        res = head.verify(self.registry, expected_owner=head.log_id)
        if not res.valid:
            raise BulletinError(f"witness {self.witness_id}: bad head signature ({res.reason})")
        prev = self._latest.get(head.log_id)
        if prev is not None:
            problem = _check_extension(prev, head, proof_from_latest)
            if problem:
                raise EquivocationDetected(EquivocationEvidence(head.log_id, prev, head, problem))
        self._latest[head.log_id] = head
        unsigned = Cosignature(self.witness_id, self.signer.key_id, head.log_id, head.tree_size, head.root_hash, head.timestamp, "")
        return Cosignature(**{**unsigned.__dict__, "signature": self.signer.sign(COSIGN_CONTEXT, unsigned.payload())})


def verify_cosignature(cosig: Cosignature, head: SignedTreeHead, registry: KeyRegistry) -> bool:
    if (cosig.log_id, cosig.tree_size, cosig.root_hash, cosig.timestamp) != (
        head.log_id, head.tree_size, head.root_hash, head.timestamp
    ):
        return False
    return registry.verify(
        cosig.key_id, COSIGN_CONTEXT, cosig.payload(), cosig.signature, cosig.timestamp,
        expected_owner=cosig.witness_id, expected_role="witness",
    ).valid


@dataclass
class BulletinBoard:
    """Append-only public record of accepted heads for every log."""

    registry: KeyRegistry
    witness_threshold: int = 0
    _heads: Dict[str, List[SignedTreeHead]] = field(default_factory=dict)
    _cosigs: Dict[tuple, List[Cosignature]] = field(default_factory=dict)
    evidence: List[EquivocationEvidence] = field(default_factory=list)

    def latest(self, log_id: str) -> Optional[SignedTreeHead]:
        heads = self._heads.get(log_id)
        return heads[-1] if heads else None

    def history(self, log_id: str) -> List[SignedTreeHead]:
        return list(self._heads.get(log_id, []))

    def publish(
        self,
        head: SignedTreeHead,
        consistency_proof: Sequence[bytes] = (),
        cosignatures: Sequence[Cosignature] = (),
    ) -> None:
        res = head.verify(self.registry, expected_owner=head.log_id)
        if not res.valid:
            raise BulletinError(f"rejected head for {head.log_id}: {res.reason}")
        good = {c.witness_id for c in cosignatures if verify_cosignature(c, head, self.registry)}
        if len(good) < self.witness_threshold:
            raise BulletinError(f"need {self.witness_threshold} witness cosignatures, got {len(good)}")
        prev = self.latest(head.log_id)
        if prev is not None:
            problem = _check_extension(prev, head, consistency_proof)
            if problem:
                ev = EquivocationEvidence(head.log_id, prev, head, problem)
                self.evidence.append(ev)
                raise EquivocationDetected(ev)
        self._heads.setdefault(head.log_id, []).append(head)
        self._cosigs[(head.log_id, head.tree_size, head.root_hash)] = [c for c in cosignatures if c.witness_id in good]

    def cosignatures(self, head: SignedTreeHead) -> List[Cosignature]:
        return list(self._cosigs.get((head.log_id, head.tree_size, head.root_hash), []))

    def check_gossip(self, other_view: Sequence[SignedTreeHead]) -> List[EquivocationEvidence]:
        """Compare heads seen elsewhere (e.g. by an auditor) with this board's record."""
        found: List[EquivocationEvidence] = []
        for other in other_view:
            if not other.verify(self.registry, expected_owner=other.log_id).valid:
                continue
            for mine in self._heads.get(other.log_id, []):
                if mine.tree_size == other.tree_size and mine.root_hash != other.root_hash:
                    ev = EquivocationEvidence(other.log_id, mine, other, "split view: same size, different root")
                    found.append(ev)
        self.evidence.extend(found)
        return found
