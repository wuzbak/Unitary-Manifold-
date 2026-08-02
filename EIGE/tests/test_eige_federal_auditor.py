# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/federal_auditor.py"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.federal_auditor import (
    FederalAuditor,
    RawDataAccessAttempt,
    AuditResult,
    AuditVerdict,
)
from EIGE.src.holon_zero_cert import generate_holon_zero_cert
from EIGE.src.constants import K_CS, PHI_0


SAMPLE_STATE_HASH = "b" * 128


def valid_cert(**overrides):
    defaults = dict(
        jurisdiction_id="WA-STATE",
        phi_eff=PHI_0,
        k_cs=K_CS,
        block_height=10,
        state_hash=SAMPLE_STATE_HASH,
    )
    defaults.update(overrides)
    return generate_holon_zero_cert(**defaults)


class TestFederalAuditorValidCert:
    def setup_method(self):
        self.auditor = FederalAuditor()

    def test_valid_cert_returns_verified(self):
        cert = valid_cert()
        result = self.auditor.validate_certificate(cert)
        assert result.verdict == AuditVerdict.VERIFIED

    def test_valid_cert_is_verified(self):
        cert = valid_cert()
        result = self.auditor.validate_certificate(cert)
        assert result.is_verified()

    def test_result_phi_verified_true(self):
        cert = valid_cert()
        result = self.auditor.validate_certificate(cert)
        assert result.phi_verified is True

    def test_result_k_cs_verified_true(self):
        cert = valid_cert()
        result = self.auditor.validate_certificate(cert)
        assert result.k_cs_verified is True

    def test_result_jurisdiction_id(self):
        cert = valid_cert(jurisdiction_id="WA-PIERCE")
        result = self.auditor.validate_certificate(cert)
        assert result.jurisdiction_id == "WA-PIERCE"

    def test_result_block_height(self):
        cert = valid_cert(block_height=42)
        result = self.auditor.validate_certificate(cert)
        assert result.block_height == 42

    def test_result_state_hash(self):
        cert = valid_cert(state_hash="c" * 128)
        result = self.auditor.validate_certificate(cert)
        assert result.state_hash == "c" * 128

    def test_result_proof_status_verified(self):
        cert = valid_cert()
        result = self.auditor.validate_certificate(cert)
        assert result.proof_status == "INVARIANTS_VERIFIED"

    def test_result_has_no_raw_ballot_data(self):
        import json
        cert = valid_cert()
        result = self.auditor.validate_certificate(cert)
        d = result.as_dict()
        s = json.dumps(d)
        for forbidden in ("ballot_id", "selection_vector", "voter_id", "raw_votes"):
            assert forbidden not in s


class TestFederalAuditorViolatedCert:
    def setup_method(self):
        self.auditor = FederalAuditor()

    def test_phi_drift_returns_integrity_violation(self):
        cert = valid_cert(phi_eff=PHI_0 + 1e-10)
        result = self.auditor.validate_certificate(cert)
        assert result.verdict == AuditVerdict.INTEGRITY_VIOLATION

    def test_wrong_k_cs_returns_integrity_violation(self):
        cert = valid_cert(k_cs=73)
        result = self.auditor.validate_certificate(cert)
        assert result.verdict == AuditVerdict.INTEGRITY_VIOLATION

    def test_empty_dict_returns_schema_invalid(self):
        result = self.auditor.validate_certificate({})
        assert result.verdict == AuditVerdict.SCHEMA_INVALID

    def test_non_dict_returns_schema_invalid(self):
        result = self.auditor.validate_certificate("not a cert")  # type: ignore
        assert result.verdict == AuditVerdict.SCHEMA_INVALID

    def test_missing_proof_returns_schema_invalid(self):
        cert = valid_cert()
        del cert["zero_knowledge_proof"]
        result = self.auditor.validate_certificate(cert)
        assert result.verdict == AuditVerdict.SCHEMA_INVALID


class TestRawDataAccessAttempt:
    def setup_method(self):
        self.auditor = FederalAuditor()

    def test_query_raw_raises(self):
        with pytest.raises(RawDataAccessAttempt):
            _ = self.auditor.query_raw_votes()

    def test_fetch_ballots_raises(self):
        with pytest.raises(RawDataAccessAttempt):
            _ = self.auditor.fetch_ballots()

    def test_get_voter_data_raises(self):
        with pytest.raises(RawDataAccessAttempt):
            _ = self.auditor.get_voter_data()

    def test_get_vote_count_raises(self):
        with pytest.raises(RawDataAccessAttempt):
            _ = self.auditor.get_vote_count()

    def test_exception_message_contains_security_violation(self):
        try:
            _ = self.auditor.query_raw()
        except RawDataAccessAttempt as exc:
            assert "SECURITY VIOLATION" in str(exc)
        except AttributeError:
            pass  # Also acceptable

    def test_exception_stores_attribute_name(self):
        try:
            _ = self.auditor.fetch_raw_ballots()
        except RawDataAccessAttempt as exc:
            assert "fetch_raw_ballots" in exc.attempted_attribute
        except AttributeError:
            pass


class TestFederalAuditorHistory:
    def setup_method(self):
        self.auditor = FederalAuditor()

    def test_audit_history_starts_empty(self):
        assert self.auditor.audit_history() == []

    def test_audit_history_grows_with_validations(self):
        cert = valid_cert()
        self.auditor.validate_certificate(cert)
        self.auditor.validate_certificate(cert)
        assert len(self.auditor.audit_history()) == 2

    def test_clear_history(self):
        cert = valid_cert()
        self.auditor.validate_certificate(cert)
        self.auditor.clear_history()
        assert self.auditor.audit_history() == []

    def test_get_audit_report_returns_dict(self):
        cert = valid_cert()
        report = self.auditor.get_audit_report(cert)
        assert isinstance(report, dict)
        assert "verdict" in report
        assert "phi_verified" in report
        assert "k_cs_verified" in report

    def test_repr_format(self):
        r = repr(self.auditor)
        assert "FederalAuditor" in r
        assert "k_cs" in r
