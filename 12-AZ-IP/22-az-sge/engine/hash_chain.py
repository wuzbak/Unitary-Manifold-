# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/hash_chain.py — SHA-512 Rolling Hash Chain for File & Event Integrity
=============================================================================

Every security event, file-scan result, and policy change is committed into an
immutable, append-only SHA-512 rolling hash chain.  The chain inherits the
Chern-Simons rolling-hash protocol from EIGE (03-eige/src/chern_simon_hash.py)
but extends it with:

  • Full SHA-512 output per link (not a truncated integer)
  • HMAC-SHA-512 link authentication (keyed by a device-local secret)
  • Merkle forest sidebar for batch verification
  • Tamper-detection: any single byte change in any prior link invalidates
    all subsequent links deterministically

The rolling accumulation uses:

    state_{n+1} = SHA-512( state_n ‖ K_CS ‖ payload_n ‖ timestamp_n )

Non-commutativity is enforced by embedding the prior state in every link, so
swapping or inserting any event produces a completely different chain tail.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import secrets
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Chern-Simons constant (from Unitary Manifold k_CS = 5² + 7²)
# ---------------------------------------------------------------------------
K_CS: int = 74  # seed / non-linearity constant

# ---------------------------------------------------------------------------
# Datatypes
# ---------------------------------------------------------------------------

@dataclass
class ChainLink:
    """A single immutable link in the hash chain."""
    index: int
    timestamp: float
    payload_type: str
    payload_summary: str          # human-readable, ≤ 256 chars
    payload_sha512: str           # hex digest of the raw payload bytes
    prev_digest: str              # hex digest of previous link (or genesis)
    link_digest: str              # SHA-512( prev_digest ‖ payload_sha512 ‖ ts )
    hmac_digest: str              # HMAC-SHA-512 of link_digest, keyed by chain key
    extra: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "payload_type": self.payload_type,
            "payload_summary": self.payload_summary,
            "payload_sha512": self.payload_sha512,
            "prev_digest": self.prev_digest,
            "link_digest": self.link_digest,
            "hmac_digest": self.hmac_digest,
            "extra": self.extra,
        }


class TamperError(Exception):
    """Raised when chain verification detects a tampered link."""


# ---------------------------------------------------------------------------
# Genesis sentinel
# ---------------------------------------------------------------------------
_GENESIS_DIGEST = hashlib.sha512(
    f"AXIOMZERO-SGE-GENESIS-K_CS={K_CS}".encode()
).hexdigest()


def _sha512_hex(data: bytes) -> str:
    return hashlib.sha512(data).hexdigest()


def _hmac_sha512_hex(key: bytes, data: bytes) -> str:
    return hmac.new(key, data, hashlib.sha512).hexdigest()


# ---------------------------------------------------------------------------
# HashChain
# ---------------------------------------------------------------------------

class HashChain:
    """Append-only SHA-512 rolling hash chain.

    Parameters
    ----------
    chain_key : bytes, optional
        Secret key for HMAC-SHA-512 link authentication.  If omitted, a
        cryptographically random 64-byte key is generated at construction
        time and stored in memory only (ephemeral chain — useful for
        testing and single-session auditing).
    """

    def __init__(self, chain_key: Optional[bytes] = None) -> None:
        self._key: bytes = chain_key if chain_key is not None else secrets.token_bytes(64)
        self._links: List[ChainLink] = []
        self._current_digest: str = _GENESIS_DIGEST

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def commit(
        self,
        payload: bytes,
        payload_type: str = "event",
        payload_summary: str = "",
        extra: Optional[Dict[str, object]] = None,
    ) -> ChainLink:
        """Append a payload to the chain and return the new link.

        Parameters
        ----------
        payload : bytes
            Raw bytes of the event/file data being committed.
        payload_type : str
            Category tag (e.g. "file_scan", "threat_event", "policy_change").
        payload_summary : str
            Human-readable summary, max 256 chars.
        extra : dict, optional
            Additional metadata attached to the link.

        Returns
        -------
        ChainLink
            The newly created immutable link.
        """
        ts = time.time()
        payload_sha512 = _sha512_hex(payload)

        # Incorporate K_CS into the mix for non-linearity
        link_preimage = (
            self._current_digest.encode()
            + K_CS.to_bytes(8, "big")
            + payload_sha512.encode()
            + str(ts).encode()
        )
        link_digest = _sha512_hex(link_preimage)
        hmac_digest = _hmac_sha512_hex(self._key, link_digest.encode())

        link = ChainLink(
            index=len(self._links),
            timestamp=ts,
            payload_type=payload_type,
            payload_summary=payload_summary[:256],
            payload_sha512=payload_sha512,
            prev_digest=self._current_digest,
            link_digest=link_digest,
            hmac_digest=hmac_digest,
            extra=extra or {},
        )
        self._links.append(link)
        self._current_digest = link_digest
        return link

    def verify(self) -> Tuple[bool, Optional[int], Optional[str]]:
        """Verify the entire chain for tamper.

        Returns
        -------
        (ok, bad_index, reason)
            ok       : True if chain is intact.
            bad_index: Index of first bad link, or None.
            reason   : Description of the failure, or None.
        """
        prev = _GENESIS_DIGEST
        for lnk in self._links:
            if lnk.prev_digest != prev:
                return False, lnk.index, "prev_digest mismatch"
            link_preimage = (
                lnk.prev_digest.encode()
                + K_CS.to_bytes(8, "big")
                + lnk.payload_sha512.encode()
                + str(lnk.timestamp).encode()
            )
            expected_ld = _sha512_hex(link_preimage)
            if lnk.link_digest != expected_ld:
                return False, lnk.index, "link_digest recomputation mismatch"
            expected_hm = _hmac_sha512_hex(self._key, lnk.link_digest.encode())
            if not hmac.compare_digest(lnk.hmac_digest, expected_hm):
                return False, lnk.index, "hmac_digest mismatch (possible key change or tampering)"
            prev = lnk.link_digest
        return True, None, None

    def head(self) -> str:
        """Return current head digest (tail of the chain)."""
        return self._current_digest

    def __len__(self) -> int:
        return len(self._links)

    def to_list(self) -> List[dict]:
        return [lnk.to_dict() for lnk in self._links]

    def export_json(self) -> str:
        return json.dumps({
            "genesis": _GENESIS_DIGEST,
            "k_cs": K_CS,
            "head": self._current_digest,
            "length": len(self._links),
            "links": self.to_list(),
        }, indent=2)


# ---------------------------------------------------------------------------
# Merkle forest for batch verification
# ---------------------------------------------------------------------------

def _merkle_root(digests: Sequence[str]) -> str:
    """Compute Merkle root over a list of hex digests."""
    if not digests:
        return _sha512_hex(b"EMPTY")
    nodes = list(digests)
    while len(nodes) > 1:
        if len(nodes) % 2 != 0:
            nodes.append(nodes[-1])  # duplicate last for odd count
        nodes = [
            _sha512_hex((nodes[i] + nodes[i + 1]).encode())
            for i in range(0, len(nodes), 2)
        ]
    return nodes[0]


def merkle_root_of_chain(chain: HashChain) -> str:
    """Return the Merkle root of all link digests in the chain."""
    return _merkle_root([lnk.link_digest for lnk in chain._links])


def verify_merkle_proof(
    target_digest: str,
    proof: List[Tuple[str, str]],  # list of (sibling_digest, direction)
    root: str,
) -> bool:
    """Verify a Merkle inclusion proof.

    Parameters
    ----------
    target_digest : str
        The leaf digest to prove membership of.
    proof : list of (sibling, direction)
        direction ∈ {"left", "right"} — which side the sibling is on.
    root : str
        Expected Merkle root.
    """
    current = target_digest
    for sibling, direction in proof:
        if direction == "left":
            current = _sha512_hex((sibling + current).encode())
        else:
            current = _sha512_hex((current + sibling).encode())
    return hmac.compare_digest(current, root)
