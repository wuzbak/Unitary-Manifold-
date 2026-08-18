# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/holon_zero_cert.py"""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.holon_zero_cert import (
    generate_holon_zero_cert,
    validate_holon_zero_cert,
    cert_to_json,
)
from EIGE.src.constants import K_CS, PHI_0, PHI_TOLERANCE


SAMPLE_STATE_HASH = "a" * 128  # 512-bit hex placeholder


class TestGenerateHolonZeroCert:
    def _valid_cert(self, **kwargs):
        defaults = dict(
            jurisdiction_id="WA-KING-COUNTY",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=42,
            state_hash=SAMPLE_STATE_HASH,
        )
        defaults.update(kwargs)
        return generate_holon_zero_cert(**defaults)

    def test_returns_dict(self):
        cert = self._valid_cert()
        assert isinstance(cert, dict)

    def test_has_zero_knowledge_proof(self):
        cert = self._valid_cert()
        assert "zero_knowledge_proof" in cert

    def test_has_component_definition(self):
        cert = self._valid_cert()
        assert "component-definition" in cert

    def test_schema_present(self):
        cert = self._valid_cert()
        assert "$schema" in cert

    def test_proof_phi_verified_true(self):
        cert = self._valid_cert(phi_eff=PHI_0)
        assert cert["zero_knowledge_proof"]["phi_delta_bound"] is True

    def test_proof_k_cs_verified_true(self):
        cert = self._valid_cert(k_cs=K_CS)
        assert cert["zero_knowledge_proof"]["k_cs_match"] is True

    def test_proof_status_verified(self):
        cert = self._valid_cert()
        assert cert["zero_knowledge_proof"]["proof_status"] == "INVARIANTS_VERIFIED"

    def test_phi_drift_yields_violated_status(self):
        cert = self._valid_cert(phi_eff=PHI_0 + 1e-10)
        assert cert["zero_knowledge_proof"]["phi_delta_bound"] is False
        assert cert["zero_knowledge_proof"]["proof_status"] == "INVARIANTS_VIOLATED"

    def test_wrong_k_cs_yields_violated_status(self):
        cert = self._valid_cert(k_cs=73)
        assert cert["zero_knowledge_proof"]["k_cs_match"] is False

    def test_jurisdiction_id_stored(self):
        cert = self._valid_cert(jurisdiction_id="WA-PIERCE-COUNTY")
        comp_def = cert["component-definition"]
        assert comp_def["jurisdiction_id"] == "WA-PIERCE-COUNTY"

    def test_block_height_stored(self):
        cert = self._valid_cert(block_height=99)
        assert cert["component-definition"]["block_height"] == 99

    def test_state_hash_stored(self):
        cert = self._valid_cert(state_hash="deadbeef" * 16)
        assert cert["component-definition"]["state_hash"] == "deadbeef" * 16

    def test_no_raw_ballot_data_in_cert(self):
        cert = self._valid_cert()
        cert_json = json.dumps(cert)
        for forbidden in ("ballot_id", "selection_vector", "voter_id", "voter_name"):
            assert forbidden not in cert_json

    def test_oscal_version_in_metadata(self):
        cert = self._valid_cert()
        metadata = cert["component-definition"]["metadata"]
        assert "1.5.0" in metadata.get("oscal-version", "")

    def test_nist_controls_present(self):
        cert = self._valid_cert()
        cert_json = json.dumps(cert)
        for ctrl in ("AC-1", "AU-12", "SI-7"):
            assert ctrl in cert_json

    def test_components_not_empty(self):
        cert = self._valid_cert()
        assert len(cert["component-definition"]["components"]) > 0


class TestValidateHolonZeroCert:
    def _valid_cert(self):
        return generate_holon_zero_cert(
            jurisdiction_id="WA-KING-COUNTY",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=10,
            state_hash=SAMPLE_STATE_HASH,
        )

    def test_valid_cert_passes(self):
        cert = self._valid_cert()
        assert validate_holon_zero_cert(cert) is True

    def test_empty_dict_fails(self):
        assert validate_holon_zero_cert({}) is False

    def test_missing_proof_fails(self):
        cert = self._valid_cert()
        del cert["zero_knowledge_proof"]
        assert validate_holon_zero_cert(cert) is False

    def test_violated_proof_fails(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-TEST",
            phi_eff=PHI_0 + 1e-10,
            k_cs=K_CS,
            block_height=1,
            state_hash="x" * 128,
        )
        assert validate_holon_zero_cert(cert) is False

    def test_wrong_k_cs_fails(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-TEST",
            phi_eff=PHI_0,
            k_cs=73,
            block_height=1,
            state_hash="x" * 128,
        )
        assert validate_holon_zero_cert(cert) is False

    def test_missing_component_definition_fails(self):
        cert = self._valid_cert()
        del cert["component-definition"]
        assert validate_holon_zero_cert(cert) is False

    def test_non_dict_fails(self):
        assert validate_holon_zero_cert("not a dict") is False  # type: ignore


class TestCertToJson:
    def test_returns_valid_json_string(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-STATE",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=5,
            state_hash=SAMPLE_STATE_HASH,
        )
        s = cert_to_json(cert)
        parsed = json.loads(s)
        assert isinstance(parsed, dict)
