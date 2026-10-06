# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Ed25519 signing, public key registry, rotation and revocation.

Public-key signatures replace the v21 shared-secret HMAC scheme: anyone holding
a public key can *verify* an EIGE artifact, but only the holder of the private
key (ideally inside an HSM) can *produce* one.

Every signed message is domain-separated: ``b"EIGE-v22/" + context + b"\\x00"
+ canonical_json(payload)``, so a signature over one artifact type can never
be replayed as another.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from ..canonical import canonical_bytes
from ..config import require_non_production

SIGNATURE_ALG = "Ed25519"
DOMAIN_PREFIX = b"EIGE-v22/"


class KeyRegistryError(ValueError):
    """Raised for invalid registry operations (duplicate key, unknown key...)."""


def key_id_for(public_key_raw: bytes) -> str:
    """Stable key identifier: ``ed25519:`` + first 16 bytes of SHA-256(pubkey) in hex."""
    if len(public_key_raw) != 32:
        raise KeyRegistryError("Ed25519 public keys are 32 bytes")
    return "ed25519:" + hashlib.sha256(public_key_raw).hexdigest()[:32]


def signing_message(context: str, payload: object) -> bytes:
    """Domain-separated message bytes for ``payload`` under ``context``."""
    if not context or "\x00" in context:
        raise ValueError("context must be a non-empty string without NUL")
    return DOMAIN_PREFIX + context.encode("utf-8") + b"\x00" + canonical_bytes(payload)


def _raw_public(pub: Ed25519PublicKey) -> bytes:
    return pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


class Signer(ABC):
    """Abstract Ed25519 signer.  Private key material never leaves the signer."""

    development_only: bool = False

    @property
    @abstractmethod
    def public_key_raw(self) -> bytes:
        """32-byte raw Ed25519 public key."""

    @abstractmethod
    def _sign_bytes(self, message: bytes) -> bytes:
        """Return a 64-byte Ed25519 signature over ``message``."""

    @property
    def key_id(self) -> str:
        return key_id_for(self.public_key_raw)

    def sign(self, context: str, payload: object) -> str:
        """Sign ``payload`` under ``context``; returns the signature as hex."""
        return self._sign_bytes(signing_message(context, payload)).hex()


class DevelopmentSigner(Signer):
    """**DEVELOPMENT ONLY** in-process Ed25519 key.

    Refuses to be constructed when ``EIGE_MODE=production``.  By default a
    fresh random key is generated; a 32-byte ``seed`` may be supplied only to
    produce reproducible test vectors.
    """

    development_only = True

    def __init__(self, seed: Optional[bytes] = None) -> None:
        require_non_production("DevelopmentSigner")
        if seed is None:
            self._priv = Ed25519PrivateKey.generate()
        else:
            if len(seed) != 32:
                raise ValueError("Ed25519 seed must be 32 bytes")
            self._priv = Ed25519PrivateKey.from_private_bytes(seed)
        self._pub = _raw_public(self._priv.public_key())

    @property
    def public_key_raw(self) -> bytes:
        return self._pub

    def _sign_bytes(self, message: bytes) -> bytes:
        return self._priv.sign(message)

    def __repr__(self) -> str:
        return f"DevelopmentSigner(key_id={self.key_id!r}, DEVELOPMENT ONLY)"


class PKCS11Ed25519Signer(Signer):
    """Ed25519 signer backed by a PKCS#11 HSM (mechanism ``CKM_EDDSA``).

    Requires the optional ``python-pkcs11`` package and an HSM that supports
    Ed25519.  The private key never leaves the hardware boundary.
    """

    def __init__(self, lib_path: str, token_label: str, key_label: str, pin: str) -> None:
        try:
            import pkcs11  # type: ignore[import]
            from pkcs11 import Attribute, Mechanism, ObjectClass  # type: ignore[import]
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("PKCS11Ed25519Signer requires python-pkcs11") from exc
        lib = pkcs11.lib(lib_path)  # pragma: no cover - requires hardware
        token = lib.get_token(token_label=token_label)  # pragma: no cover
        self._session = token.open(user_pin=pin)  # pragma: no cover
        self._priv = self._session.get_key(  # pragma: no cover
            object_class=ObjectClass.PRIVATE_KEY, label=key_label
        )
        pub = self._session.get_key(object_class=ObjectClass.PUBLIC_KEY, label=key_label)  # pragma: no cover
        point = bytes(pub[Attribute.EC_POINT])  # pragma: no cover
        self._pub = point[-32:]  # pragma: no cover - DER OCTET STRING wrapper
        self._mechanism = Mechanism.EDDSA  # pragma: no cover

    @property
    def public_key_raw(self) -> bytes:  # pragma: no cover - requires hardware
        return self._pub

    def _sign_bytes(self, message: bytes) -> bytes:  # pragma: no cover - requires hardware
        return bytes(self._priv.sign(message, mechanism=self._mechanism))


def verify_signature(public_key_raw: bytes, context: str, payload: object, signature_hex: str) -> bool:
    """Verify an Ed25519 signature without consulting a registry."""
    try:
        sig = bytes.fromhex(signature_hex)
        Ed25519PublicKey.from_public_bytes(public_key_raw).verify(sig, signing_message(context, payload))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


@dataclass
class KeyRecord:
    """Public registry entry for one Ed25519 key.

    Times are integer Unix seconds.  ``valid_until`` is set on rotation;
    ``revoked_at`` is set on revocation.  A *compromised* revocation
    invalidates every signature made with the key, regardless of timestamp.
    """

    key_id: str
    public_key_hex: str
    owner: str
    role: str
    valid_from: int
    valid_until: Optional[int] = None
    revoked_at: Optional[int] = None
    revocation_reason: Optional[str] = None
    compromised: bool = False
    development_only: bool = False

    def status_at(self, when: int) -> str:
        if self.compromised:
            return "compromised"
        if self.revoked_at is not None and when >= self.revoked_at:
            return "revoked"
        if when < self.valid_from:
            return "not-yet-valid"
        if self.valid_until is not None and when >= self.valid_until:
            return "expired"
        return "valid"

    def as_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "public_key": self.public_key_hex,
            "owner": self.owner,
            "role": self.role,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "revoked_at": self.revoked_at,
            "revocation_reason": self.revocation_reason,
            "compromised": self.compromised,
            "development_only": self.development_only,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "KeyRecord":
        pub_hex = str(d["public_key"])
        record = cls(
            key_id=str(d["key_id"]),
            public_key_hex=pub_hex,
            owner=str(d["owner"]),
            role=str(d["role"]),
            valid_from=int(d["valid_from"]),
            valid_until=None if d.get("valid_until") is None else int(d["valid_until"]),
            revoked_at=None if d.get("revoked_at") is None else int(d["revoked_at"]),
            revocation_reason=d.get("revocation_reason"),
            compromised=bool(d.get("compromised", False)),
            development_only=bool(d.get("development_only", False)),
        )
        if key_id_for(bytes.fromhex(pub_hex)) != record.key_id:
            raise KeyRegistryError(f"key_id does not match public key for {record.key_id}")
        return record


@dataclass
class VerificationResult:
    valid: bool
    reason: str
    key_id: Optional[str] = None
    development_only: bool = False

    def __bool__(self) -> bool:  # pragma: no cover - convenience
        return self.valid


@dataclass
class KeyRegistry:
    """Public registry of signing keys (publishable; contains no secrets)."""

    records: Dict[str, KeyRecord] = field(default_factory=dict)

    def register(
        self,
        public_key_raw: bytes,
        owner: str,
        role: str,
        valid_from: int,
        development_only: bool = False,
    ) -> KeyRecord:
        kid = key_id_for(public_key_raw)
        if kid in self.records:
            raise KeyRegistryError(f"key {kid} already registered")
        record = KeyRecord(
            key_id=kid,
            public_key_hex=public_key_raw.hex(),
            owner=owner,
            role=role,
            valid_from=int(valid_from),
            development_only=development_only,
        )
        self.records[kid] = record
        return record

    def register_signer(self, signer: Signer, owner: str, role: str, valid_from: int) -> KeyRecord:
        return self.register(signer.public_key_raw, owner, role, valid_from, signer.development_only)

    def get(self, key_id: str) -> KeyRecord:
        try:
            return self.records[key_id]
        except KeyError:
            raise KeyRegistryError(f"unknown key {key_id}") from None

    def rotate(self, old_key_id: str, new_public_key_raw: bytes, at: int, development_only: bool = False) -> KeyRecord:
        """Retire ``old_key_id`` at time ``at`` and register its successor."""
        old = self.get(old_key_id)
        if old.revoked_at is not None or old.compromised:
            raise KeyRegistryError("cannot rotate a revoked key; register a new key instead")
        old.valid_until = int(at)
        return self.register(new_public_key_raw, old.owner, old.role, at, development_only)

    def revoke(self, key_id: str, at: int, reason: str, compromised: bool = False) -> KeyRecord:
        record = self.get(key_id)
        record.revoked_at = int(at)
        record.revocation_reason = reason
        record.compromised = record.compromised or compromised
        return record

    def keys_for_owner(self, owner: str) -> List[KeyRecord]:
        return [r for r in self.records.values() if r.owner == owner]

    def verify(
        self,
        key_id: str,
        context: str,
        payload: object,
        signature_hex: str,
        signed_at: int,
        expected_owner: Optional[str] = None,
        expected_role: Optional[str] = None,
        allow_development: bool = True,
    ) -> VerificationResult:
        record = self.records.get(key_id)
        if record is None:
            return VerificationResult(False, "unknown key", key_id)
        if expected_owner is not None and record.owner != expected_owner:
            return VerificationResult(False, f"key owned by {record.owner}, expected {expected_owner}", key_id)
        if expected_role is not None and record.role != expected_role:
            return VerificationResult(False, f"key role {record.role}, expected {expected_role}", key_id)
        if record.development_only and not allow_development:
            return VerificationResult(False, "development-only key not accepted", key_id, True)
        status = record.status_at(int(signed_at))
        if status != "valid":
            return VerificationResult(False, f"key {status} at signing time", key_id, record.development_only)
        if not verify_signature(bytes.fromhex(record.public_key_hex), context, payload, signature_hex):
            return VerificationResult(False, "bad signature", key_id, record.development_only)
        return VerificationResult(True, "ok", key_id, record.development_only)

    def as_dict(self) -> dict:
        return {"format": "eige.key_registry.v1", "keys": [r.as_dict() for r in sorted(self.records.values(), key=lambda r: r.key_id)]}

    @classmethod
    def from_dict(cls, d: dict) -> "KeyRegistry":
        if d.get("format") != "eige.key_registry.v1":
            raise KeyRegistryError("unsupported key registry format")
        reg = cls()
        for item in d.get("keys", []):
            rec = KeyRecord.from_dict(item)
            if rec.key_id in reg.records:
                raise KeyRegistryError(f"duplicate key {rec.key_id}")
            reg.records[rec.key_id] = rec
        return reg

    @classmethod
    def from_records(cls, records: Iterable[KeyRecord]) -> "KeyRegistry":
        return cls({r.key_id: r for r in records})
