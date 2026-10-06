# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/zk_proof.py — Pedersen Commitment Layer (legacy; NOT zero-knowledge)
=============================================================================

SECURITY NOTICE (v22, red-team finding F3)
------------------------------------------
v21 called this a "zero-knowledge proof".  It was not one: the "proof" was a
commitment followed by two self-asserted pass/fail flag bytes, and
``verify_metric_proof`` only read those flags back, so anyone could produce a
"passing" proof for any value.  As of v22:

* ``verify_metric_proof`` requires the opening (value + blinding factor) and
  recomputes both the commitment and the flags from the opened values.  A
  serialized proof without its opening never verifies.
* Nothing here is zero-knowledge.  Verifying requires revealing the value.
* The committed quantity (φ_eff, k_cs) is the retired metric-closure signal
  and carries no evidentiary weight.  For tally commitments use
  ``eige.crypto.commitments``.

Provides a Pedersen commitment scheme over the 2048-bit MODP group from
RFC 3526 (Group 14).  This group was chosen for:

  - Auditability: standardized parameters, no trusted setup required.
  - Compatibility: widely available in cryptographic literature and tools.
  - No external dependencies: pure-Python arithmetic, no third-party ZK libs.

Scheme
------
Let (p, g, h) be the public parameters from RFC 3526 Group 14.
A commitment to integer ``v`` with blinding factor ``r`` is:

    C = g^v * h^r mod p

The commitment is *hiding*: C reveals no information about v without r.
The commitment is *binding*: finding (v', r') ≠ (v, r) such that
    g^v * h^r ≡ g^v' * h^r' mod p
requires computing discrete logarithms in a 2048-bit prime-order group.

Usage
-----
Commit to phi_eff and k_cs jointly::

    proof = commit_metric_state(phi_eff=0.7853981, k_cs=74)
    valid = verify_metric_proof(proof)

The resulting PedersenProof contains:
  - commitment (int): the commitment value C
  - phi_delta_bound (float): |phi_eff - phi_0| ≤ PHI_TOLERANCE (bool flag)
  - k_cs_match (bool): k_cs == K_CS
  - proof_bytes (bytes): compact serialization of (C, phi_delta_bound, k_cs_match)

No raw phi_eff value or hash state is included in the proof.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import math
import os
import struct
from dataclasses import dataclass, field
from typing import Optional

from .constants import K_CS, PHI_0, PHI_TOLERANCE

# ---------------------------------------------------------------------------
# RFC 3526 Group 14 — 2048-bit MODP parameters
# ---------------------------------------------------------------------------
# These are the standard parameters from IETF RFC 3526 §3.
# p is a 2048-bit safe prime; g = 2 is the generator.
# h is derived as h = SHA-512(b"EIGE-Pedersen-h-seed") treated as an integer
# reduced mod p. This makes h a hash-to-group point with no hidden trapdoor.

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
_P: int = int(_P_HEX.replace(" ", ""), 16)
_G: int = 2
# Derive h as SHA-512 of a public seed, reduced mod p
_H_SEED = b"EIGE-v21-Pedersen-h-generator-seed-RFC3526-Group14"
_H: int = int.from_bytes(hashlib.sha512(_H_SEED).digest(), "big") % _P

# Scale factor to convert phi_eff (float near π/4) to an integer suitable
# for commitment.  1e15 gives ~15 decimal digits of precision.
_PHI_SCALE: int = 10 ** 15


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class PedersenCommitment:
    """A single Pedersen commitment.

    Attributes
    ----------
    value : int
        The committed secret integer (cleared after verification; treat as private).
    randomness : int
        The blinding factor r (treat as private; never share).
    commitment : int
        The public commitment C = g^value * h^randomness mod p.
    """

    value: int
    randomness: int
    commitment: int


@dataclass
class PedersenProof:
    """A commitment to the (retired) metric state plus claimed flags.

    NOT a zero-knowledge proof.  The flags are claims by the committer; they
    are only trustworthy once checked by :func:`verify_metric_proof` against
    the opening.

    Contains ONLY the commitment and boolean bounds — no raw phi_eff value,
    no hash state, no raw k_cs integer beyond the boolean match flag.

    Attributes
    ----------
    commitment : int
        The Pedersen commitment C = g^v * h^r mod p.
    proof_bytes : bytes
        Compact binary serialization: commitment (256 bytes big-endian) +
        phi_delta_bound flag (1 byte) + k_cs_match flag (1 byte).
    phi_delta_bound : bool
        True iff |phi_eff - phi_0| ≤ PHI_TOLERANCE at commitment time.
    k_cs_match : bool
        True iff k_cs == K_CS at commitment time.
    engine_version : str
        Engine version string for forward-compat cert validation.
    """

    commitment: int
    proof_bytes: bytes
    phi_delta_bound: bool
    k_cs_match: bool
    engine_version: str = "21.0.0"
    opening: Optional["MetricOpening"] = field(default=None, repr=False, compare=False)

    def invariants_verified(self) -> bool:
        """Return True if both invariants hold in this proof."""
        return self.phi_delta_bound and self.k_cs_match

    def as_dict(self) -> dict:
        """Serialize to a JSON-safe dict."""
        return {
            "commitment": hex(self.commitment),
            "proof_bytes": self.proof_bytes.hex(),
            "phi_delta_bound": self.phi_delta_bound,
            "k_cs_match": self.k_cs_match,
            "engine_version": self.engine_version,
            "proof_status": (
                "INVARIANTS_CLAIMED"
                if self.invariants_verified()
                else "INVARIANTS_VIOLATED"
            ),
            "scheme_note": "Pedersen commitment with self-asserted flags; not zero-knowledge; "
            "verification requires the opening (see RETRACTED_CLAIMS.md)",
        }


# ---------------------------------------------------------------------------
# Core commitment operations
# ---------------------------------------------------------------------------

def commit(secret_int: int, randomness: int | None = None) -> PedersenCommitment:
    """Compute a Pedersen commitment to ``secret_int``.

    Parameters
    ----------
    secret_int : int
        The secret value to commit to.  Must be a non-negative integer.
    randomness : int, optional
        The blinding factor r.  If not provided, a 256-bit random integer is
        generated via ``os.urandom``.  Callers who need deterministic commits
        (e.g. for testing) may supply a fixed value.

    Returns
    -------
    PedersenCommitment
        (value, randomness, C = g^value * h^r mod p)
    """
    if secret_int < 0:
        raise ValueError(f"secret_int must be ≥ 0, got {secret_int}")
    if randomness is None:
        randomness = int.from_bytes(os.urandom(32), "big")
    # C = g^v * h^r mod p
    c = (pow(_G, secret_int, _P) * pow(_H, randomness, _P)) % _P
    return PedersenCommitment(value=secret_int, randomness=randomness, commitment=c)


def verify_commitment(
    commitment_value: int,
    revealed_secret: int,
    revealed_randomness: int,
) -> bool:
    """Verify that a commitment opens to the revealed values.

    Parameters
    ----------
    commitment_value : int
        The commitment C to verify.
    revealed_secret : int
        The claimed secret v.
    revealed_randomness : int
        The claimed blinding factor r.

    Returns
    -------
    bool
        True if g^v * h^r mod p == commitment_value.
    """
    expected = (pow(_G, revealed_secret, _P) * pow(_H, revealed_randomness, _P)) % _P
    return expected == commitment_value


@dataclass(frozen=True)
class MetricOpening:
    """Opening of a metric-state commitment: the packed value and blinding factor."""

    phi_int: int
    k_cs: int
    randomness: int


def _pack(phi_int: int, k_cs: int) -> int:
    return phi_int * (K_CS + 1) + k_cs


def commit_metric_state(
    phi_eff: float,
    k_cs: int,
    randomness: int | None = None,
) -> PedersenProof:
    """Commit to the joint metric state (phi_eff, k_cs).

    The returned proof carries its :class:`MetricOpening` in memory (never
    serialized by :meth:`PedersenProof.as_dict`) so the committer can later
    reveal it to a verifier.
    """
    phi_int = round(phi_eff * _PHI_SCALE)
    if not 0 <= k_cs <= K_CS:
        raise ValueError(f"k_cs must be in [0, {K_CS}] to pack unambiguously")
    pc = commit(_pack(phi_int, k_cs), randomness=randomness)

    phi_ok = abs(phi_eff - PHI_0) <= PHI_TOLERANCE
    kcs_ok = (k_cs == K_CS)

    commitment_bytes = pc.commitment.to_bytes(256, "big")
    flags = struct.pack("BB", int(phi_ok), int(kcs_ok))
    return PedersenProof(
        commitment=pc.commitment,
        proof_bytes=commitment_bytes + flags,
        phi_delta_bound=phi_ok,
        k_cs_match=kcs_ok,
        opening=MetricOpening(phi_int, k_cs, pc.randomness),
    )


def verify_metric_proof(proof: PedersenProof, opening: Optional[MetricOpening] = None) -> bool:
    """Verify a metric-state commitment by opening it.

    ``opening`` defaults to the opening held by the committer's in-memory
    proof object.  Verification recomputes the commitment from the opening,
    checks that ``proof_bytes`` encodes that same commitment, and recomputes
    both invariant flags from the opened values — the flags stored in the
    proof are never trusted.  Returns False when no opening is available.
    """
    opening = opening if opening is not None else proof.opening
    if opening is None or len(proof.proof_bytes) != 258:
        return False
    if int.from_bytes(proof.proof_bytes[:256], "big") != proof.commitment:
        return False
    if not verify_commitment(proof.commitment, _pack(opening.phi_int, opening.k_cs), opening.randomness):
        return False
    phi_ok = abs(opening.phi_int / _PHI_SCALE - PHI_0) <= PHI_TOLERANCE + 1.0 / _PHI_SCALE
    kcs_ok = opening.k_cs == K_CS
    if (bool(proof.proof_bytes[256]), bool(proof.proof_bytes[257])) != (phi_ok, kcs_ok):
        return False
    return phi_ok and kcs_ok


def proof_from_dict(d: dict) -> PedersenProof:
    """Deserialize a PedersenProof from a dict (e.g. from a JSON certificate)."""
    commitment = int(d["commitment"], 16)
    proof_bytes = bytes.fromhex(d["proof_bytes"])
    phi_delta_bound = bool(d["phi_delta_bound"])
    k_cs_match = bool(d["k_cs_match"])
    engine_version = d.get("engine_version", "21.0.0")
    opening = None
    if isinstance(d.get("opening"), dict):
        o = d["opening"]
        opening = MetricOpening(int(o["phi_int"]), int(o["k_cs"]), int(o["randomness"], 16))
    return PedersenProof(
        commitment=commitment,
        proof_bytes=proof_bytes,
        phi_delta_bound=phi_delta_bound,
        k_cs_match=k_cs_match,
        engine_version=engine_version,
        opening=opening,
    )


def opening_as_dict(opening: MetricOpening) -> dict:
    """Serialize an opening for disclosure to a verifier."""
    return {"phi_int": opening.phi_int, "k_cs": opening.k_cs, "randomness": hex(opening.randomness)}
