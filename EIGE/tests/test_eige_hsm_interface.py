# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/tests/test_eige_hsm_interface.py — HSM Interface & TEE Attestation Tests
==============================================================================

Tests SoftwareKeyProvider determinism, MockHSMKeyProvider contract, and
AttestationReport structure/determinism for the SOFTWARE_MOCK platform.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import hmac as _hmac

import pytest

from src.hsm_interface import (
    KeyProvider,
    SoftwareKeyProvider,
    MockHSMKeyProvider,
)
from src.tee_attestation import (
    AttestationReport,
    get_attestation_report,
    _get_software_mock_report,
    _MOCK_HMAC_KEY,
)
from src.county_node import CountyNode


# ---------------------------------------------------------------------------
# SoftwareKeyProvider
# ---------------------------------------------------------------------------

class TestSoftwareKeyProvider:
    def test_is_key_provider_subclass(self):
        p = SoftwareKeyProvider("WA-047")
        assert isinstance(p, KeyProvider)

    def test_sign_returns_64_bytes(self):
        p = SoftwareKeyProvider("WA-047")
        sig = p.sign(b"hello")
        assert len(sig) == 64

    def test_sign_is_deterministic(self):
        p1 = SoftwareKeyProvider("WA-047")
        p2 = SoftwareKeyProvider("WA-047")
        assert p1.sign(b"test-message") == p2.sign(b"test-message")

    def test_different_county_ids_produce_different_keys(self):
        p1 = SoftwareKeyProvider("WA-001")
        p2 = SoftwareKeyProvider("WA-033")
        msg = b"same message"
        assert p1.sign(msg) != p2.sign(msg)

    def test_sign_dict_returns_hex_string(self):
        p = SoftwareKeyProvider("WA-047")
        payload = {"county_id": "WA-047", "ballot_count": 10}
        sig = p.sign_dict(payload)
        assert isinstance(sig, str)
        assert len(sig) == 128  # 64 bytes = 128 hex chars

    def test_sign_dict_excludes_hmac_signature_field(self):
        p = SoftwareKeyProvider("WA-047")
        payload_with = {"county_id": "WA-047", "hmac_signature": "old-sig"}
        payload_without = {"county_id": "WA-047"}
        assert p.sign_dict(payload_with) == p.sign_dict(payload_without)

    def test_key_derivation_matches_legacy_derive_key(self):
        """SoftwareKeyProvider must produce the same key as CountyNode._derive_key()."""
        county_id = "WA-047"
        expected_key = hashlib.sha512(
            f"EIGE-v21-{county_id}-hmac-key-placeholder".encode("utf-8")
        ).digest()
        p = SoftwareKeyProvider(county_id)
        assert p._key == expected_key

    def test_sign_matches_legacy_hmac_computation(self):
        """Sign output must match the old CountyNode._sign_payload logic."""
        county_id = "WA-033"
        legacy_key = hashlib.sha512(
            f"EIGE-v21-{county_id}-hmac-key-placeholder".encode("utf-8")
        ).digest()
        p = SoftwareKeyProvider(county_id)
        msg = b"test-payload-bytes"
        legacy_sig = _hmac.new(legacy_key, msg, hashlib.sha512).digest()
        assert p.sign(msg) == legacy_sig

    def test_repr_contains_county_id(self):
        p = SoftwareKeyProvider("WA-099")
        assert "WA-099" in repr(p)

    def test_different_messages_produce_different_sigs(self):
        p = SoftwareKeyProvider("WA-047")
        assert p.sign(b"msg1") != p.sign(b"msg2")


# ---------------------------------------------------------------------------
# MockHSMKeyProvider
# ---------------------------------------------------------------------------

class TestMockHSMKeyProvider:
    def test_is_key_provider_subclass(self):
        key_bytes = b"\x01" * 64
        p = MockHSMKeyProvider(keys={"test_key": key_bytes}, active_label="test_key")
        assert isinstance(p, KeyProvider)

    def test_sign_returns_64_bytes(self):
        key_bytes = b"\xAB" * 64
        p = MockHSMKeyProvider(keys={"k": key_bytes}, active_label="k")
        sig = p.sign(b"message")
        assert len(sig) == 64

    def test_sign_is_deterministic(self):
        key_bytes = b"\x42" * 64
        p1 = MockHSMKeyProvider(keys={"k": key_bytes}, active_label="k")
        p2 = MockHSMKeyProvider(keys={"k": key_bytes}, active_label="k")
        assert p1.sign(b"hello") == p2.sign(b"hello")

    def test_sign_matches_hmac_sha512(self):
        key_bytes = b"\xCC" * 64
        p = MockHSMKeyProvider(keys={"k": key_bytes}, active_label="k")
        msg = b"test-ballot-payload"
        expected = _hmac.new(key_bytes, msg, hashlib.sha512).digest()
        assert p.sign(msg) == expected

    def test_load_key_dynamically(self):
        p = MockHSMKeyProvider()
        key_bytes = b"\xFF" * 64
        p.load_key("new_key", key_bytes)
        sig = p.sign(b"data")
        assert len(sig) == 64

    def test_sign_without_key_raises_key_error(self):
        p = MockHSMKeyProvider()
        with pytest.raises(KeyError):
            p.sign(b"data")

    def test_different_keys_produce_different_sigs(self):
        key_a = b"\xAA" * 64
        key_b = b"\xBB" * 64
        pa = MockHSMKeyProvider(keys={"k": key_a}, active_label="k")
        pb = MockHSMKeyProvider(keys={"k": key_b}, active_label="k")
        assert pa.sign(b"msg") != pb.sign(b"msg")

    def test_repr_contains_labels(self):
        p = MockHSMKeyProvider(keys={"audit_key": b"\x01"}, active_label="audit_key")
        assert "audit_key" in repr(p)

    def test_sign_dict_returns_hex_string(self):
        key_bytes = b"\x12" * 64
        p = MockHSMKeyProvider(keys={"k": key_bytes}, active_label="k")
        sig = p.sign_dict({"field": "value"})
        assert isinstance(sig, str)
        assert len(sig) == 128

    def test_sign_dict_excludes_hmac_signature(self):
        key_bytes = b"\x34" * 64
        p = MockHSMKeyProvider(keys={"k": key_bytes}, active_label="k")
        with_sig = {"data": 1, "hmac_signature": "old"}
        without_sig = {"data": 1}
        assert p.sign_dict(with_sig) == p.sign_dict(without_sig)


# ---------------------------------------------------------------------------
# CountyNode key provider wiring
# ---------------------------------------------------------------------------

class TestCountyNodeKeyProviderWiring:
    def test_default_uses_software_provider(self):
        node = CountyNode("WA-047", "King County")
        assert isinstance(node._key_provider, SoftwareKeyProvider)

    def test_default_signature_matches_legacy(self):
        """CountyNode with default provider must sign identically to old code."""
        node = CountyNode("WA-047", "King County")
        payload = {"county_id": "WA-047", "ballot_count": 5}
        new_sig = node._sign_payload(payload)

        # Legacy path: _derive_key + hmac.new
        import hmac as _h
        key = node._hmac_key
        signable = {k: v for k, v in payload.items() if k != "hmac_signature"}
        import json
        msg = json.dumps(signable, sort_keys=True).encode("utf-8")
        legacy_sig = _h.new(key, msg, hashlib.sha512).hexdigest()
        assert new_sig == legacy_sig

    def test_explicit_mock_hsm_provider_used(self):
        key_bytes = b"\xDE" * 64
        provider = MockHSMKeyProvider(keys={"k": key_bytes}, active_label="k")
        node = CountyNode("WA-047", "King County", key_provider=provider)
        assert node._key_provider is provider

    def test_legacy_hmac_key_param_still_works(self):
        key = b"\x99" * 64
        node = CountyNode("WA-001", "Adams County", hmac_key=key)
        # Signing should work — node should use the provided bytes
        payload = {"county_id": "WA-001"}
        sig = node._sign_payload(payload)
        assert isinstance(sig, str)
        assert len(sig) == 128  # 64 bytes hex = 128 chars

    def test_telemetry_signature_present_and_non_empty(self):
        node = CountyNode("WA-009", "Clallam County")
        node.ingest_ballot([1, 0, 1])
        telemetry = node.get_shard_telemetry()
        assert "hmac_signature" in telemetry
        assert len(telemetry["hmac_signature"]) == 128

    def test_key_provider_arg_takes_precedence_over_hmac_key(self):
        """If both key_provider and hmac_key are given, key_provider wins."""
        raw_key = b"\x11" * 64
        provider = MockHSMKeyProvider(keys={"k": b"\x22" * 64}, active_label="k")
        node = CountyNode("WA-047", "King County",
                          hmac_key=raw_key, key_provider=provider)
        assert node._key_provider is provider


# ---------------------------------------------------------------------------
# AttestationReport structure
# ---------------------------------------------------------------------------

class TestAttestationReport:
    def test_software_mock_report_fields(self):
        nonce = b"test-nonce-12345"
        report = _get_software_mock_report(nonce)
        assert report.platform == "SOFTWARE_MOCK"
        assert report.nonce == nonce
        assert len(report.measurement) == 64  # SHA-512 = 64 bytes
        assert len(report.signature) == 64

    def test_software_mock_is_deterministic(self):
        nonce = b"deterministic-nonce"
        r1 = _get_software_mock_report(nonce)
        r2 = _get_software_mock_report(nonce)
        assert r1.measurement == r2.measurement
        assert r1.signature == r2.signature

    def test_different_nonces_produce_different_reports(self):
        r1 = _get_software_mock_report(b"nonce-A")
        r2 = _get_software_mock_report(b"nonce-B")
        assert r1.measurement != r2.measurement
        assert r1.signature != r2.signature

    def test_is_mock_returns_true_for_software_mock(self):
        report = _get_software_mock_report(b"nonce")
        assert report.is_mock() is True

    def test_verify_nonce_correct(self):
        nonce = b"fresh-nonce"
        report = _get_software_mock_report(nonce)
        assert report.verify_nonce(nonce) is True

    def test_verify_nonce_fails_on_wrong_nonce(self):
        report = _get_software_mock_report(b"original-nonce")
        assert report.verify_nonce(b"different-nonce") is False

    def test_as_dict_contains_required_keys(self):
        report = _get_software_mock_report(b"test")
        d = report.as_dict()
        assert "platform" in d
        assert "measurement" in d
        assert "nonce" in d
        assert "signature" in d
        assert "is_mock" in d

    def test_as_dict_bytes_are_hex_encoded(self):
        report = _get_software_mock_report(b"test")
        d = report.as_dict()
        # All byte fields should be hex strings, not bytes
        assert isinstance(d["measurement"], str)
        assert isinstance(d["nonce"], str)
        assert isinstance(d["signature"], str)

    def test_get_attestation_report_defaults_to_mock(self):
        nonce = b"election-cycle-nonce"
        report = get_attestation_report(nonce)
        # In CI (no TDX/SEV hardware), should be SOFTWARE_MOCK
        assert report.platform in ("TDX", "SEV-SNP", "SOFTWARE_MOCK")
        assert report.verify_nonce(nonce)

    def test_get_attestation_report_explicit_mock(self):
        nonce = b"explicit-mock"
        report = get_attestation_report(nonce, prefer="SOFTWARE_MOCK")
        assert report.platform == "SOFTWARE_MOCK"

    def test_report_data_empty_for_mock(self):
        report = _get_software_mock_report(b"n")
        assert report.report_data == b""

    def test_measurement_is_sha512_of_nonce_and_platform(self):
        nonce = b"known-nonce"
        report = _get_software_mock_report(nonce)
        expected = hashlib.sha512(nonce + b"SOFTWARE_MOCK").digest()
        assert report.measurement == expected
