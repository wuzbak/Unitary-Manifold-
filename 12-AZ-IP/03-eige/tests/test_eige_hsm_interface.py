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
    get_attestation_report,
    _get_software_mock_report,
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

    def test_sign_is_deterministic_for_explicit_key(self):
        key = b"\x42" * 64
        p1 = SoftwareKeyProvider("WA-047", key=key)
        p2 = SoftwareKeyProvider("WA-047", key=key)
        assert p1.sign(b"test-message") == p2.sign(b"test-message")

    def test_default_keys_are_random_per_instance(self):
        p1 = SoftwareKeyProvider("WA-047")
        p2 = SoftwareKeyProvider("WA-047")
        assert p1.sign(b"test-message") != p2.sign(b"test-message")

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

    def test_key_is_not_the_v21_placeholder_derivation(self):
        """F4: the key must never be derivable from the public county id."""
        county_id = "WA-047"
        placeholder = hashlib.sha512(
            f"EIGE-v21-{county_id}-hmac-key-placeholder".encode("utf-8")
        ).digest()
        p = SoftwareKeyProvider(county_id)
        assert p._key != placeholder

    def test_short_explicit_key_rejected(self):
        with pytest.raises(ValueError):
            SoftwareKeyProvider("WA-033", key=b"short")

    def test_refuses_production_mode(self, monkeypatch):
        from eige.config import ProductionModeViolation
        monkeypatch.setenv("EIGE_MODE", "production")
        with pytest.raises(ProductionModeViolation):
            SoftwareKeyProvider("WA-033")
        with pytest.raises(ProductionModeViolation):
            MockHSMKeyProvider(keys={"k": b"\x01" * 64}, active_label="k")

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
    def test_default_has_no_legacy_hmac_provider(self):
        node = CountyNode("WA-047", "King County")
        assert node._key_provider is None
        with pytest.raises(RuntimeError):
            node._sign_payload({"county_id": "WA-047"})

    def test_default_telemetry_verifies_with_registry(self):
        from eige.crypto.signing import KeyRegistry
        from src.county_node import verify_telemetry
        node = CountyNode("WA-047", "King County")
        node.ingest_ballot([1, 0, 1])
        reg = KeyRegistry()
        reg.register_signer(node.signer, owner="WA-047", role="county", valid_from=0)
        t = node.get_shard_telemetry()
        assert verify_telemetry(t, reg, expected_owner="WA-047").valid
        t["ballot_count"] += 1
        assert not verify_telemetry(t, reg, expected_owner="WA-047").valid

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

    def test_telemetry_hmac_only_with_explicit_provider(self):
        node = CountyNode("WA-009", "Clallam County", hmac_key=b"\x07" * 64)
        node.ingest_ballot([1, 0, 1])
        telemetry = node.get_shard_telemetry()
        assert len(telemetry["hmac_signature"]) == 128
        assert len(telemetry["signature"]) == 128

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
        # v22 (F4): the mock carries no (fake) signature and is labelled.
        assert report.signature == b""
        assert report.verification_status == "MOCK_NOT_EVIDENCE"
        assert report.verified is False

    def test_software_mock_is_deterministic(self):
        nonce = b"deterministic-nonce"
        r1 = _get_software_mock_report(nonce)
        r2 = _get_software_mock_report(nonce)
        assert r1.measurement == r2.measurement

    def test_different_nonces_produce_different_reports(self):
        r1 = _get_software_mock_report(b"nonce-A")
        r2 = _get_software_mock_report(b"nonce-B")
        assert r1.measurement != r2.measurement

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

    def test_get_attestation_report_never_defaults_to_mock(self, monkeypatch):
        from src.tee_attestation import TEEUnavailable
        monkeypatch.delenv("EIGE_ALLOW_TEE_MOCK", raising=False)
        monkeypatch.setattr("os.path.exists", lambda p: False)
        with pytest.raises(TEEUnavailable):
            get_attestation_report(b"election-cycle-nonce")

    def test_get_attestation_report_mock_requires_opt_in(self, monkeypatch):
        from src.tee_attestation import TEEUnavailable
        monkeypatch.delenv("EIGE_ALLOW_TEE_MOCK", raising=False)
        with pytest.raises(TEEUnavailable):
            get_attestation_report(b"explicit-mock", prefer="SOFTWARE_MOCK")
        report = get_attestation_report(b"explicit-mock", prefer="SOFTWARE_MOCK", allow_mock=True)
        assert report.platform == "SOFTWARE_MOCK"
        monkeypatch.setenv("EIGE_ALLOW_TEE_MOCK", "1")
        assert get_attestation_report(b"x", prefer="SOFTWARE_MOCK").is_mock()

    def test_mock_refused_in_production(self, monkeypatch):
        from eige.config import ProductionModeViolation
        monkeypatch.setenv("EIGE_MODE", "production")
        with pytest.raises(ProductionModeViolation):
            get_attestation_report(b"n", prefer="SOFTWARE_MOCK", allow_mock=True)

    def test_verify_attestation_report_is_honest(self):
        from src.tee_attestation import AttestationReport, verify_attestation_report
        mock = _get_software_mock_report(b"n")
        assert verify_attestation_report(mock, b"n").status == "MOCK_NOT_EVIDENCE"
        assert verify_attestation_report(mock, b"other").status == "NONCE_MISMATCH"
        hw = AttestationReport("TDX", b"m" * 48, b"n", b"", b"quote")
        v = verify_attestation_report(hw, b"n")
        assert v.verified is False and v.status == "RAW_QUOTE_UNVERIFIED"

    def test_report_data_empty_for_mock(self):
        report = _get_software_mock_report(b"n")
        assert report.report_data == b""

    def test_measurement_is_sha512_of_nonce_and_platform(self):
        nonce = b"known-nonce"
        report = _get_software_mock_report(nonce)
        expected = hashlib.sha512(nonce + b"SOFTWARE_MOCK").digest()
        assert report.measurement == expected
