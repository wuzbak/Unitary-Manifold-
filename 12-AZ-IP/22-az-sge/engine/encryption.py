# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/encryption.py — AES-256-GCM + X25519 ECDH Encryption Layer
===================================================================

Provides:
  • SymmetricCipher   — AES-256-GCM encrypt/decrypt with random IV
  • KeyExchange       — X25519 ECDH via the cryptography library
  • SessionKey        — HKDF-SHA-512 key derivation from shared secret
  • SecureEnvelope    — self-describing JSON envelope: encrypt any bytes,
                        decrypt back, carry metadata

All ciphertexts are BASE64 (URL-safe, no padding stripped) to allow safe
JSON transport.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import base64
import json
import os
import hashlib
import hmac
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Import the required cryptography provider.
# ---------------------------------------------------------------------------
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.asymmetric.x25519 import (
        X25519PrivateKey, X25519PublicKey,
    )
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes
    _CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover — only missing in stripped envs
    _CRYPTO_AVAILABLE = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
AES_KEY_BYTES = 32       # AES-256
GCM_IV_BYTES  = 12       # 96-bit nonce (GCM standard)
HKDF_INFO     = b"AXIOMZERO-SGE-SESSION-v1"


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode()


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "==")


def _require_crypto() -> None:
    if not _CRYPTO_AVAILABLE:
        raise RuntimeError(
            "AZ-SGE encryption requires the 'cryptography' package; "
            "refusing to substitute non-standard cryptography."
        )


# ---------------------------------------------------------------------------
# SymmetricCipher — public API
# ---------------------------------------------------------------------------

class SymmetricCipher:
    """AES-256-GCM encrypt/decrypt.

    The operation is unavailable when the ``cryptography`` library is missing.
    """

    def __init__(self, key: bytes) -> None:
        if len(key) != AES_KEY_BYTES:
            raise ValueError(f"Key must be {AES_KEY_BYTES} bytes; got {len(key)}")
        _require_crypto()
        self._key = key
        self._gcm = AESGCM(key)

    @property
    def provider(self) -> str:
        return "cryptography"

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> Tuple[str, str]:
        """Encrypt and return (iv_b64, ciphertext_with_tag_b64)."""
        iv = os.urandom(GCM_IV_BYTES)
        ct = self._gcm.encrypt(iv, plaintext, aad or None)
        return _b64e(iv), _b64e(ct)

    def decrypt(self, iv_b64: str, ciphertext_b64: str, aad: bytes = b"") -> bytes:
        """Decrypt and return plaintext bytes."""
        iv = _b64d(iv_b64)
        ct = _b64d(ciphertext_b64)
        return self._gcm.decrypt(iv, ct, aad or None)


# ---------------------------------------------------------------------------
# HKDF-SHA-512 session key derivation
# ---------------------------------------------------------------------------

def derive_session_key(
    shared_secret: bytes,
    salt: Optional[bytes] = None,
    info: bytes = HKDF_INFO,
    length: int = AES_KEY_BYTES,
) -> bytes:
    """Derive a session key from a shared secret via HKDF-SHA-512."""
    if _CRYPTO_AVAILABLE:
        hkdf = HKDF(
            algorithm=hashes.SHA512(),
            length=length,
            salt=salt,
            info=info,
        )
        return hkdf.derive(shared_secret)
    # Software fallback: HMAC-SHA-512 extract-and-expand
    if salt is None:
        salt = b"\x00" * 64
    prk = hmac.new(salt, shared_secret, hashlib.sha512).digest()
    okm = b""
    prev = b""
    counter = 1
    while len(okm) < length:
        prev = hmac.new(prk, prev + info + bytes([counter]), hashlib.sha512).digest()
        okm += prev
        counter += 1
    return okm[:length]


# ---------------------------------------------------------------------------
# X25519 Key Exchange
# ---------------------------------------------------------------------------

@dataclass
class KeyPair:
    private_bytes: bytes   # 32 raw bytes
    public_bytes: bytes    # 32 raw bytes


def generate_keypair() -> KeyPair:
    """Generate an X25519 key pair."""
    _require_crypto()
    priv = X25519PrivateKey.generate()
    pub = priv.public_key()
    return KeyPair(priv.private_bytes_raw(), pub.public_bytes_raw())


def compute_shared_secret(our_private: bytes, their_public: bytes) -> bytes:
    """Perform X25519 ECDH to produce a shared secret."""
    _require_crypto()
    priv_obj = X25519PrivateKey.from_private_bytes(our_private)
    pub_obj = X25519PublicKey.from_public_bytes(their_public)
    return priv_obj.exchange(pub_obj)


# ---------------------------------------------------------------------------
# SecureEnvelope — self-describing encrypted JSON container
# ---------------------------------------------------------------------------

class SecureEnvelope:
    """Encrypt any bytes into a self-describing JSON envelope.

    The envelope carries: algorithm, IV, ciphertext+tag, AAD hash (for
    verification), sender public key (optional), timestamp.
    """

    ALGORITHM = "AES-256-GCM+HKDF-SHA-512+X25519"

    def __init__(self, cipher: SymmetricCipher) -> None:
        self._cipher = cipher

    def seal(
        self,
        plaintext: bytes,
        sender_pub: Optional[bytes] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> str:
        """Encrypt plaintext and return JSON envelope string."""
        import time as _time
        ts = _time.time()
        aad = json.dumps({"ts": ts, "meta": metadata or {}}, sort_keys=True).encode()
        iv_b64, ct_b64 = self._cipher.encrypt(plaintext, aad)
        envelope = {
            "algorithm": self.ALGORITHM,
            "provider": self._cipher.provider,
            "iv": iv_b64,
            "ciphertext": ct_b64,
            "aad_sha512": _b64e(hashlib.sha512(aad).digest()),
            "timestamp": ts,
            "metadata": metadata or {},
            "sender_public_key": _b64e(sender_pub) if sender_pub else None,
        }
        return json.dumps(envelope, indent=2)

    def open(self, envelope_json: str) -> bytes:
        """Decrypt an envelope and return the plaintext bytes."""
        env = json.loads(envelope_json)
        ts = env["timestamp"]
        metadata = env.get("metadata", {})
        aad = json.dumps({"ts": ts, "meta": metadata}, sort_keys=True).encode()
        return self._cipher.decrypt(env["iv"], env["ciphertext"], aad)
