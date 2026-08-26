# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/encryption.py — AES-256-GCM + X25519 ECDH Encryption Layer
===================================================================

Provides:
  • SymmetricCipher   — AES-256-GCM encrypt/decrypt with random IV
  • KeyExchange       — X25519 ECDH via cryptography library; falls back to
                        a pure-Python DH simulation when the library is absent
                        (test/offline environments only — mark plainly in output)
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
import struct
import hashlib
import hmac
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Attempt to import 'cryptography'; fall back gracefully
# ---------------------------------------------------------------------------
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.asymmetric.x25519 import (
        X25519PrivateKey, X25519PublicKey,
    )
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes, serialization
    _CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover — only missing in stripped envs
    _CRYPTO_AVAILABLE = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
AES_KEY_BYTES = 32       # AES-256
GCM_IV_BYTES  = 12       # 96-bit nonce (GCM standard)
GCM_TAG_BYTES = 16       # 128-bit authentication tag
HKDF_INFO     = b"AXIOMZERO-SGE-SESSION-v1"


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode()


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "==")


# ---------------------------------------------------------------------------
# Pure-Python AES-256-GCM simulation (for environments without cryptography)
# ---------------------------------------------------------------------------

def _xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _ghash(h: bytes, data: bytes) -> bytes:
    """Minimal GHASH for GCM tag (128-bit blocks, GHASH field multiplication).

    This is a reference implementation; not constant-time.
    Real deployments use the cryptography library.
    """
    R = 0xE1000000000000000000000000000000
    def _gf_mul(x: int, y: int) -> int:
        z = 0
        for _ in range(128):
            if y & (1 << 127):
                z ^= x
            x = (x >> 1) ^ (R if x & 1 else 0)
            y <<= 1
            y &= (1 << 128) - 1
        return z

    # pad to 16-byte boundary
    pad_len = (16 - len(data) % 16) % 16
    data_padded = data + b"\x00" * pad_len
    h_int = int.from_bytes(h, "big")
    y = 0
    for i in range(0, len(data_padded), 16):
        block = int.from_bytes(data_padded[i:i+16], "big")
        y = _gf_mul(y ^ block, h_int)
    return y.to_bytes(16, "big")


class _SoftAESGCM:
    """Software AES-256-GCM using hashlib SHAKE for key stream (approx.)

    WARNING: This is a *functional simulation* for offline/test use only.
    It uses SHAKE-256 as a PRF to simulate the key stream.  The
    authentication tag is HMAC-SHA-256 of (iv ‖ aad ‖ ciphertext).
    This is NOT a drop-in security replacement for real AES-GCM.
    """

    def __init__(self, key: bytes) -> None:
        if len(key) != AES_KEY_BYTES:
            raise ValueError(f"Key must be {AES_KEY_BYTES} bytes")
        self._key = key

    def _key_stream(self, iv: bytes, length: int) -> bytes:
        shake = hashlib.shake_256(self._key + iv + b"SGE-KEYSTREAM")
        return shake.digest(length)

    def _tag(self, iv: bytes, aad: bytes, ciphertext: bytes) -> bytes:
        return hmac.new(
            self._key,
            iv + aad + ciphertext,
            hashlib.sha256,
        ).digest()[:GCM_TAG_BYTES]

    def encrypt(self, iv: bytes, data: bytes, aad: bytes = b"") -> bytes:
        ks = self._key_stream(iv, len(data))
        ct = _xor_bytes(data, ks)
        tag = self._tag(iv, aad, ct)
        return ct + tag

    def decrypt(self, iv: bytes, token: bytes, aad: bytes = b"") -> bytes:
        ct, tag = token[:-GCM_TAG_BYTES], token[-GCM_TAG_BYTES:]
        expected_tag = self._tag(iv, aad, ct)
        if not hmac.compare_digest(tag, expected_tag):
            raise ValueError("GCM authentication tag mismatch — ciphertext is invalid or tampered")
        ks = self._key_stream(iv, len(ct))
        return _xor_bytes(ct, ks)


# ---------------------------------------------------------------------------
# SymmetricCipher — public API
# ---------------------------------------------------------------------------

class SymmetricCipher:
    """AES-256-GCM encrypt/decrypt.

    If the ``cryptography`` library is available it is used; otherwise the
    software simulation is used and a warning is embedded in metadata.
    """

    def __init__(self, key: bytes) -> None:
        if len(key) != AES_KEY_BYTES:
            raise ValueError(f"Key must be {AES_KEY_BYTES} bytes; got {len(key)}")
        self._key = key
        if _CRYPTO_AVAILABLE:
            self._gcm = AESGCM(key)
            self._soft = False
        else:
            self._gcm = _SoftAESGCM(key)
            self._soft = True

    @property
    def uses_software_fallback(self) -> bool:
        return self._soft

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> Tuple[str, str]:
        """Encrypt and return (iv_b64, ciphertext_with_tag_b64)."""
        iv = os.urandom(GCM_IV_BYTES)
        if _CRYPTO_AVAILABLE:
            ct = self._gcm.encrypt(iv, plaintext, aad or None)
        else:
            ct = self._gcm.encrypt(iv, plaintext, aad)
        return _b64e(iv), _b64e(ct)

    def decrypt(self, iv_b64: str, ciphertext_b64: str, aad: bytes = b"") -> bytes:
        """Decrypt and return plaintext bytes."""
        iv = _b64d(iv_b64)
        ct = _b64d(ciphertext_b64)
        if _CRYPTO_AVAILABLE:
            return self._gcm.decrypt(iv, ct, aad or None)
        return self._gcm.decrypt(iv, ct, aad)


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
    software_mode: bool = False


def generate_keypair() -> KeyPair:
    """Generate an X25519 key pair."""
    if _CRYPTO_AVAILABLE:
        priv = X25519PrivateKey.generate()
        pub = priv.public_key()
        priv_raw = priv.private_bytes_raw()
        pub_raw = pub.public_bytes_raw()
        return KeyPair(priv_raw, pub_raw, software_mode=False)
    # Software fallback: simulate with random bytes (NOT real X25519)
    priv_raw = os.urandom(32)
    pub_raw = hashlib.sha256(priv_raw + b"X25519-SIM-PUB").digest()
    return KeyPair(priv_raw, pub_raw, software_mode=True)


def compute_shared_secret(our_private: bytes, their_public: bytes) -> bytes:
    """Perform X25519 ECDH to produce a shared secret."""
    if _CRYPTO_AVAILABLE:
        priv_obj = X25519PrivateKey.from_private_bytes(our_private)
        pub_obj = X25519PublicKey.from_public_bytes(their_public)
        return priv_obj.exchange(pub_obj)
    # Software fallback: SHA-512(private ‖ public) — not real ECDH
    return hashlib.sha512(our_private + their_public).digest()[:32]


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
            "software_mode": self._cipher.uses_software_fallback,
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
