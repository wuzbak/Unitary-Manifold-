# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
Tests for EIGE/src/oscal_validator.py — OSCAL 1.5.0 dossier schema validator
and for the SI-7/AU-12 enhancement controls added to oscal_schema.py.
"""

from __future__ import annotations

import json
import sys
import os
import uuid
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from EIGE.src.oscal_validator import OSCALValidator, ValidationResult, validate_oscal_schema
from EIGE.src.oscal_schema import (
    NIST_SP800_53_MAPPINGS,
    build_si7_evidence_block,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_valid_dossier(**overrides) -> dict:
    """Return a minimal OSCAL 1.5.0 component-definition dossier."""
    dossier = {
        "component-definition": {
            "uuid": str(uuid.uuid4()),
            "metadata": {
                "title": "Test Dossier",
                "last-modified": datetime.now(timezone.utc).isoformat(),
                "version": "1.0",
                "oscal-version": "1.5.0",
            },
            "components": [
                {
                    "uuid": str(uuid.uuid4()),
                    "type": "software",
                    "title": "ChernSimonHash",
                    "description": "Test component",
                    "control-implementations": [
                        {
                            "uuid": str(uuid.uuid4()),
                            "source": "https://csrc.nist.gov/",
                            "description": "NIST SP-800-53 R5",
                            "implemented-requirements": [
                                {
                                    "uuid": str(uuid.uuid4()),
                                    "control-id": "SI-7",
                                    "description": "Integrity",
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    }
    dossier["component-definition"].update(overrides)
    return dossier


# ---------------------------------------------------------------------------
# OSCALValidator instantiation
# ---------------------------------------------------------------------------

class TestOSCALValidatorInit:
    def test_creates_with_defaults(self):
        v = OSCALValidator()
        assert v is not None

    def test_schema_loaded(self):
        v = OSCALValidator()
        assert isinstance(v._schema, dict)

    def test_schema_has_component_definition_key(self):
        v = OSCALValidator()
        assert "component-definition" in str(v._schema)


# ---------------------------------------------------------------------------
# validate_oscal_schema — valid dossiers
# ---------------------------------------------------------------------------

class TestValidOSCALDossiers:
    def test_minimal_valid_passes(self):
        result = validate_oscal_schema(_minimal_valid_dossier())
        assert result.valid is True

    def test_valid_result_has_no_errors(self):
        result = validate_oscal_schema(_minimal_valid_dossier())
        assert result.errors == []

    def test_valid_result_bool_true(self):
        result = validate_oscal_schema(_minimal_valid_dossier())
        assert bool(result) is True

    def test_valid_result_has_dossier_uuid(self):
        d = _minimal_valid_dossier()
        expected_uuid = d["component-definition"]["uuid"]
        result = validate_oscal_schema(d)
        assert result.dossier_uuid == expected_uuid

    def test_valid_result_schema_version(self):
        result = validate_oscal_schema(_minimal_valid_dossier())
        assert result.schema_version == "oscal-1.5.0"

    def test_multiple_components_valid(self):
        d = _minimal_valid_dossier()
        d["component-definition"]["components"].append(
            {
                "uuid": str(uuid.uuid4()),
                "type": "hardware",
                "title": "HSM",
                "description": "Hardware Security Module",
                "control-implementations": [
                    {
                        "uuid": str(uuid.uuid4()),
                        "source": "https://csrc.nist.gov/",
                        "description": "Controls",
                        "implemented-requirements": [
                            {"uuid": str(uuid.uuid4()), "control-id": "SI-7(6)"}
                        ],
                    }
                ],
            }
        )
        result = validate_oscal_schema(d)
        assert result.valid is True


# ---------------------------------------------------------------------------
# validate_oscal_schema — invalid dossiers
# ---------------------------------------------------------------------------

class TestInvalidOSCALDossiers:
    def test_not_a_dict_fails(self):
        result = validate_oscal_schema("not a dict")  # type: ignore[arg-type]
        assert result.valid is False
        assert len(result.errors) > 0

    def test_missing_component_definition_fails(self):
        result = validate_oscal_schema({"other_key": {}})
        assert result.valid is False

    def test_missing_uuid_fails(self):
        d = _minimal_valid_dossier()
        del d["component-definition"]["uuid"]
        result = validate_oscal_schema(d)
        assert result.valid is False

    def test_missing_metadata_fails(self):
        d = _minimal_valid_dossier()
        del d["component-definition"]["metadata"]
        result = validate_oscal_schema(d)
        assert result.valid is False

    def test_missing_components_fails(self):
        d = _minimal_valid_dossier()
        del d["component-definition"]["components"]
        result = validate_oscal_schema(d)
        assert result.valid is False

    def test_empty_components_array_fails(self):
        d = _minimal_valid_dossier()
        d["component-definition"]["components"] = []
        result = validate_oscal_schema(d)
        assert result.valid is False

    def test_wrong_oscal_version_fails(self):
        d = _minimal_valid_dossier()
        d["component-definition"]["metadata"]["oscal-version"] = "1.4.0"
        result = validate_oscal_schema(d)
        assert result.valid is False

    def test_missing_metadata_title_fails(self):
        d = _minimal_valid_dossier()
        del d["component-definition"]["metadata"]["title"]
        result = validate_oscal_schema(d)
        assert result.valid is False

    def test_invalid_result_bool_false(self):
        result = validate_oscal_schema({"no_cd_key": True})
        assert bool(result) is False

    def test_invalid_result_to_dict(self):
        result = validate_oscal_schema({})
        d = result.to_dict()
        assert d["valid"] is False
        assert isinstance(d["errors"], list)


# ---------------------------------------------------------------------------
# ValidationResult dataclass
# ---------------------------------------------------------------------------

class TestValidationResult:
    def test_valid_result_construct(self):
        r = ValidationResult(valid=True)
        assert bool(r) is True

    def test_invalid_result_construct(self):
        r = ValidationResult(valid=False, errors=["error1"])
        assert bool(r) is False

    def test_to_dict_keys(self):
        r = ValidationResult(valid=True, dossier_uuid="test-uuid")
        d = r.to_dict()
        assert set(d.keys()) >= {"valid", "errors", "schema_version", "dossier_uuid"}

    def test_errors_default_empty(self):
        r = ValidationResult(valid=True)
        assert r.errors == []


# ---------------------------------------------------------------------------
# NIST SP-800-53 R5 control mapping — SI-7 and AU-12 enhancements
# ---------------------------------------------------------------------------

class TestNISTMappingsEnhancements:
    def test_si7_base_control_present(self):
        assert "chern_simon_hash" in NIST_SP800_53_MAPPINGS
        assert NIST_SP800_53_MAPPINGS["chern_simon_hash"]["control_id"] == "SI-7"

    def test_si7_1_integrity_checks_present(self):
        assert "si7_integrity_checks" in NIST_SP800_53_MAPPINGS
        assert NIST_SP800_53_MAPPINGS["si7_integrity_checks"]["control_id"] == "SI-7(1)"

    def test_si7_6_crypto_protection_present(self):
        assert "si7_cryptographic_protection" in NIST_SP800_53_MAPPINGS
        assert NIST_SP800_53_MAPPINGS["si7_cryptographic_protection"]["control_id"] == "SI-7(6)"

    def test_au12_base_control_present(self):
        assert "scaffold_invariant" in NIST_SP800_53_MAPPINGS
        assert NIST_SP800_53_MAPPINGS["scaffold_invariant"]["control_id"] == "AU-12"

    def test_au12_1_system_wide_audit_trail_present(self):
        assert "au12_system_wide_audit_trail" in NIST_SP800_53_MAPPINGS
        assert NIST_SP800_53_MAPPINGS["au12_system_wide_audit_trail"]["control_id"] == "AU-12(1)"

    def test_all_mappings_have_description(self):
        for key, mapping in NIST_SP800_53_MAPPINGS.items():
            assert "description" in mapping, f"Missing description for {key}"
            assert len(mapping["description"]) > 10

    def test_all_mappings_have_control_id(self):
        for key, mapping in NIST_SP800_53_MAPPINGS.items():
            assert "control_id" in mapping, f"Missing control_id for {key}"


# ---------------------------------------------------------------------------
# build_si7_evidence_block
# ---------------------------------------------------------------------------

class TestBuildSI7EvidenceBlock:
    @pytest.fixture
    def chain(self):
        from EIGE.src.chern_simon_hash import ChernSimonChain
        c = ChernSimonChain()
        for i in range(5):
            c.update(i)
        return c

    def test_returns_dict(self, chain):
        block = build_si7_evidence_block(chain)
        assert isinstance(block, dict)

    def test_has_control_id(self, chain):
        block = build_si7_evidence_block(chain)
        assert block["control_id"] == "SI-7"

    def test_has_enhancement_controls(self, chain):
        block = build_si7_evidence_block(chain)
        assert "SI-7(1)" in block["enhancement_controls"]
        assert "SI-7(6)" in block["enhancement_controls"]

    def test_has_cs_hash_state_hex(self, chain):
        block = build_si7_evidence_block(chain)
        assert "cs_hash_state_hex" in block
        assert isinstance(block["cs_hash_state_hex"], str)
        assert len(block["cs_hash_state_hex"]) > 0

    def test_has_sha512_hexdigest(self, chain):
        block = build_si7_evidence_block(chain)
        assert "sha512_hexdigest" in block
        assert len(block["sha512_hexdigest"]) == 128

    def test_has_ballot_count(self, chain):
        block = build_si7_evidence_block(chain)
        assert "ballot_count" in block
        assert block["ballot_count"] == 5

    def test_has_timestamp(self, chain):
        block = build_si7_evidence_block(chain)
        assert "timestamp" in block

    def test_has_oscal_version(self, chain):
        block = build_si7_evidence_block(chain)
        assert "oscal_version" in block

    def test_cs_hash_state_hex_matches_chain_state(self, chain):
        block = build_si7_evidence_block(chain)
        assert int(block["cs_hash_state_hex"], 16) == chain.state

    def test_evidence_changes_after_update(self, chain):
        block1 = build_si7_evidence_block(chain)
        chain.update(999)
        block2 = build_si7_evidence_block(chain)
        assert block1["cs_hash_state_hex"] != block2["cs_hash_state_hex"]


# ---------------------------------------------------------------------------
# FederalAuditor OSCAL pre-flight integration
# ---------------------------------------------------------------------------

class TestFederalAuditorOSCALPreflight:
    @pytest.fixture
    def auditor_with_preflight(self):
        from EIGE.src.federal_auditor import FederalAuditor
        return FederalAuditor(oscal_preflight=True)

    @pytest.fixture
    def auditor_no_preflight(self):
        from EIGE.src.federal_auditor import FederalAuditor
        return FederalAuditor(oscal_preflight=False)

    @pytest.fixture
    def valid_cert(self):
        from EIGE.src.holon_zero_cert import generate_holon_zero_cert
        from EIGE.src.chern_simon_hash import ChernSimonChain
        chain = ChernSimonChain()
        chain.update(1)
        return generate_holon_zero_cert(chain, jurisdiction_id="TEST-01")

    def test_valid_cert_passes_preflight(self, auditor_with_preflight, valid_cert):
        from EIGE.src.federal_auditor import AuditVerdict
        result = auditor_with_preflight.validate_certificate(valid_cert)
        assert result.verdict == AuditVerdict.VERIFIED

    def test_invalid_oscal_struct_rejected_by_preflight(self, auditor_with_preflight):
        from EIGE.src.federal_auditor import AuditVerdict
        bad_cert = {"not-component-definition": True}
        result = auditor_with_preflight.validate_certificate(bad_cert)
        assert result.verdict == AuditVerdict.SCHEMA_INVALID

    def test_preflight_false_skips_oscal_check(self, auditor_no_preflight, valid_cert):
        from EIGE.src.federal_auditor import AuditVerdict
        result = auditor_no_preflight.validate_certificate(valid_cert)
        assert result.verdict == AuditVerdict.VERIFIED
