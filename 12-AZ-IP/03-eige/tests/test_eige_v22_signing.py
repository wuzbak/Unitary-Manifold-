# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Ed25519 signing and key registry semantics."""

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from eige.config import ProductionModeViolation
from eige.crypto.signing import DevelopmentSigner, KeyRegistry, KeyRegistryError, key_id_for, verify_signature

RFC8032_SECRET = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
RFC8032_PUBLIC = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
RFC8032_SIG_EMPTY = bytes.fromhex(
    "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
    "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
)


def test_rfc8032_ed25519_vector_one_with_cryptography():
    priv = Ed25519PrivateKey.from_private_bytes(RFC8032_SECRET)
    pub = priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    assert pub == RFC8032_PUBLIC
    assert priv.sign(b"") == RFC8032_SIG_EMPTY


def test_development_signer_key_id_and_context_separation():
    signer = DevelopmentSigner(b"a" * 32)
    payload = {"root": "abc", "size": 3}
    sig = signer.sign("sth", payload)
    assert signer.key_id == key_id_for(signer.public_key_raw)
    assert signer.key_id.startswith("ed25519:") and len(signer.key_id) == 40
    assert verify_signature(signer.public_key_raw, "sth", payload, sig)
    assert not verify_signature(signer.public_key_raw, "telemetry", payload, sig)
    with pytest.raises(KeyRegistryError):
        key_id_for(b"too short")


def test_development_signer_refuses_in_production(monkeypatch):
    monkeypatch.setenv("EIGE_MODE", "production")
    with pytest.raises(ProductionModeViolation):
        DevelopmentSigner(b"b" * 32)


def test_registry_register_verify_rotate_revoke_and_round_trip():
    signer1 = DevelopmentSigner(b"1" * 32)
    signer2 = DevelopmentSigner(b"2" * 32)
    registry = KeyRegistry()
    rec1 = registry.register_signer(signer1, owner="county", role="county-log", valid_from=10)
    with pytest.raises(KeyRegistryError):
        registry.register_signer(signer1, owner="county", role="county-log", valid_from=10)

    payload = {"message": "ok"}
    sig1 = signer1.sign("sth", payload)
    assert registry.verify(rec1.key_id, "sth", payload, sig1, 20, expected_owner="county", expected_role="county-log").valid
    assert not registry.verify(rec1.key_id, "sth", payload, sig1, 20, expected_owner="other").valid
    assert not registry.verify(rec1.key_id, "sth", payload, sig1, 20, expected_role="witness").valid
    assert not registry.verify(rec1.key_id, "sth", payload, sig1, 5).valid
    assert not registry.verify(rec1.key_id, "sth", payload, sig1, 20, allow_development=False).valid

    rec2 = registry.rotate(rec1.key_id, signer2.public_key_raw, at=30, development_only=True)
    assert not registry.verify(rec1.key_id, "sth", payload, sig1, 30).valid
    sig2 = signer2.sign("sth", payload)
    assert registry.verify(rec2.key_id, "sth", payload, sig2, 30).valid

    data = registry.as_dict()
    restored = KeyRegistry.from_dict(data)
    assert restored.as_dict() == data
    assert restored.keys_for_owner("county")

    restored.revoke(rec2.key_id, at=50, reason="lost", compromised=False)
    assert restored.verify(rec2.key_id, "sth", payload, sig2, 49).valid
    assert not restored.verify(rec2.key_id, "sth", payload, sig2, 50).valid
    restored.revoke(rec2.key_id, at=60, reason="compromised", compromised=True)
    assert not restored.verify(rec2.key_id, "sth", payload, sig2, 40).valid


def test_registry_rejects_bad_serialized_key_id():
    signer = DevelopmentSigner(b"3" * 32)
    reg = KeyRegistry(); reg.register_signer(signer, "owner", "role", 0)
    data = reg.as_dict(); data["keys"][0]["key_id"] = "ed25519:" + "0" * 32
    with pytest.raises(KeyRegistryError):
        KeyRegistry.from_dict(data)
