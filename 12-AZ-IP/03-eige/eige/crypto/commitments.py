# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pedersen commitments to per-contest vote totals.

What this provides
------------------
* ``C = g^v · h^r mod p`` in the prime-order subgroup of quadratic residues of
  the RFC 3526 2048-bit MODP group (p is a safe prime, q = (p−1)/2).
* **Hiding** (perfect): C reveals nothing about v without the opening r.
* **Binding** (computational): opening C to two different values requires the
  discrete log of h to base g, which nobody knows because h is derived from a
  public seed by hashing (nothing-up-my-sleeve).
* **Additive homomorphism**: ``C(v1, r1) · C(v2, r2) = C(v1+v2, r1+r2)``, so
  county commitments multiply into a commitment to the state total, which can
  be checked against the state's opening without opening any county.
* **Selective opening**: each candidate total is committed separately, so an
  auditor can be given the opening for one candidate or contest only.

What this does NOT provide
--------------------------
No zero-knowledge proofs (e.g. range proofs or proofs that totals match
cast-vote records) are implemented.  Nothing in this module should be
described as "zero-knowledge".
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional

_P_HEX = (
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF"
)
P: int = int(_P_HEX, 16)
Q: int = (P - 1) // 2
G: int = 4  # 2^2: a quadratic residue, hence a generator of the order-q subgroup
H_SEED = b"EIGE-v22 Pedersen generator h / RFC3526 group 14 / quadratic-residue subgroup"


def _hash_to_subgroup(seed: bytes) -> int:
    counter = 0
    while True:
        x = int.from_bytes(hashlib.shake_256(seed + counter.to_bytes(4, "big")).digest(256), "big") % P
        h = pow(x, 2, P)  # squaring maps into the quadratic-residue subgroup
        if h not in (0, 1) and h != G:
            return h
        counter += 1  # pragma: no cover - astronomically unlikely


H: int = _hash_to_subgroup(H_SEED)
COMMITMENT_SCHEME = "pedersen-rfc3526-group14-qr-v1"


class CommitmentError(ValueError):
    """Raised for invalid commitment operations."""


@dataclass(frozen=True)
class Opening:
    """Private opening (value, randomness) for a commitment."""

    value: int
    randomness: int

    def __add__(self, other: "Opening") -> "Opening":
        return Opening(self.value + other.value, (self.randomness + other.randomness) % Q)


def _check_value(value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < Q:
        raise CommitmentError("committed value must be an integer in [0, q)")


def commit_value(value: int, randomness: Optional[int] = None) -> tuple[int, Opening]:
    """Commit to ``value``; returns ``(commitment, opening)``."""
    _check_value(value)
    r = secrets.randbelow(Q) if randomness is None else int(randomness) % Q
    return (pow(G, value, P) * pow(H, r, P)) % P, Opening(value, r)


def verify_opening(commitment: int, opening: Opening) -> bool:
    if not 1 <= commitment < P or not 0 <= opening.value < Q:
        return False
    return commitment == (pow(G, opening.value, P) * pow(H, opening.randomness % Q, P)) % P


def is_valid_commitment(commitment: int) -> bool:
    """Check that ``commitment`` is an element of the order-q subgroup."""
    return 1 <= commitment < P and pow(commitment, Q, P) == 1


def combine(commitments: Iterable[int]) -> int:
    acc = 1
    for c in commitments:
        acc = (acc * c) % P
    return acc


@dataclass
class ContestTallyCommitment:
    """Public per-candidate commitments for one contest in one jurisdiction."""

    jurisdiction: str
    contest_id: str
    commitments: Dict[str, int]

    def as_dict(self) -> dict:
        return {
            "format": "eige.tally_commitment.v1",
            "scheme": COMMITMENT_SCHEME,
            "jurisdiction": self.jurisdiction,
            "contest_id": self.contest_id,
            "commitments": {k: format(v, "x") for k, v in sorted(self.commitments.items())},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ContestTallyCommitment":
        if d.get("format") != "eige.tally_commitment.v1" or d.get("scheme") != COMMITMENT_SCHEME:
            raise CommitmentError("unsupported tally commitment format")
        commitments = {str(k): int(v, 16) for k, v in d["commitments"].items()}
        for k, c in commitments.items():
            if not is_valid_commitment(c):
                raise CommitmentError(f"commitment for {k} is not a subgroup element")
        return cls(str(d["jurisdiction"]), str(d["contest_id"]), commitments)


def commit_tallies(
    jurisdiction: str, contest_id: str, tallies: Mapping[str, int]
) -> tuple[ContestTallyCommitment, Dict[str, Opening]]:
    """Commit separately to every candidate total of one contest."""
    commitments: Dict[str, int] = {}
    openings: Dict[str, Opening] = {}
    for candidate, total in sorted(tallies.items()):
        c, o = commit_value(int(total))
        commitments[candidate] = c
        openings[candidate] = o
    return ContestTallyCommitment(jurisdiction, contest_id, commitments), openings


def open_selected(openings: Mapping[str, Opening], candidates: Iterable[str]) -> Dict[str, Opening]:
    """Selective disclosure: return openings only for the requested candidates."""
    return {c: openings[c] for c in candidates}


def verify_selected(public: ContestTallyCommitment, disclosed: Mapping[str, Opening]) -> Dict[str, bool]:
    return {c: c in public.commitments and verify_opening(public.commitments[c], o) for c, o in disclosed.items()}


def aggregate(parts: Iterable[ContestTallyCommitment], jurisdiction: str) -> ContestTallyCommitment:
    """Homomorphically combine county commitments into a state-level commitment."""
    parts = list(parts)
    if not parts:
        raise CommitmentError("nothing to aggregate")
    contest = parts[0].contest_id
    candidates = set(parts[0].commitments)
    for part in parts:
        if part.contest_id != contest or set(part.commitments) != candidates:
            raise CommitmentError("all parts must cover the same contest and candidate set")
    return ContestTallyCommitment(
        jurisdiction,
        contest,
        {c: combine(part.commitments[c] for part in parts) for c in sorted(candidates)},
    )


def aggregate_openings(openings: Iterable[Mapping[str, Opening]]) -> Dict[str, Opening]:
    total: Dict[str, Opening] = {}
    for item in openings:
        for c, o in item.items():
            total[c] = total[c] + o if c in total else o
    return total
