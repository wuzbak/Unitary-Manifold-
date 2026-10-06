# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Authoritative v22 control mapping and honest OSCAL component definition.

Every control marked ``implemented`` or ``partial`` names the tests that
exercise the behaviour; ``tests/test_eige_compliance.py`` fails if any named
test does not exist, and ``COMPLIANCE.md`` must state the same status.
``planned`` controls make no claim and name no tests.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Tuple

STATUSES = ("implemented", "partial", "planned")
OSCAL_VERSION = "1.1.2"
_NS = uuid.UUID("6f1c1d2e-8f3a-5b7c-9d0e-1a2b3c4d5e6f")


@dataclass(frozen=True)
class ControlMapping:
    framework: str
    control_id: str
    title: str
    status: str
    modules: Tuple[str, ...]
    statement: str
    tests: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"{self.control_id}: unknown status {self.status!r}")
        if self.status != "planned" and not self.tests:
            raise ValueError(f"{self.control_id}: {self.status} control must name tests")
        if self.status == "planned" and self.tests:
            raise ValueError(f"{self.control_id}: planned control must not claim tests")


_R = "tests/test_eige_redteam_findings.py"
_ADV = "tests/test_eige_v22_adversarial.py"

CONTROL_MAPPINGS: Tuple[ControlMapping, ...] = (
    ControlMapping(
        "NIST SP 800-53r5", "AU-2", "Event Logging", "implemented",
        ("eige.ledger.log", "eige.ledger.custody"),
        "CVRs, manifest commitments and paper custody events are appended to a typed Merkle log.",
        ("tests/test_eige_v22_ledger.py::test_merkle_log_append_root_proofs_and_signed_head",
         "tests/test_eige_v22_ledger.py::test_custody_two_person_rule_and_role_enforcement"),
    ),
    ControlMapping(
        "NIST SP 800-53r5", "AU-3", "Content of Audit Records", "partial",
        ("eige.ledger.log", "eige.ledger.custody"),
        "Records are canonical typed JSON with custody fields and signer key ids; operator identity "
        "proofing is a deployment responsibility.",
        ("tests/test_eige_v22_ledger.py::test_verify_container_reports_broken_seals_and_transfer_gaps",
         "tests/test_eige_v22_properties.py::test_canonical_bytes_are_deterministic_for_json_values"),
    ),
    ControlMapping(
        "NIST SP 800-53r5", "AU-9", "Protection of Audit Information", "partial",
        ("eige.crypto.merkle", "eige.ledger.log", "eige.ledger.bulletin"),
        "Signed tree heads, consistency proofs and witness cosignatures make post-publication alteration "
        "and split views detectable. They do not prevent deletion of unpublished data.",
        (f"{_ADV}::test_ballot_stuffing_extra_cvr_in_log_fails",
         f"{_ADV}::test_deletion_of_logged_cvr_fails",
         f"{_ADV}::test_reordering_logged_cvrs_fails",
         f"{_ADV}::test_equivocation_same_size_different_root_fails",
         "tests/test_eige_v22_ledger.py::test_bulletin_board_consistency_witness_threshold_and_gossip"),
    ),
    ControlMapping(
        "NIST SP 800-53r5", "AU-10", "Non-repudiation", "partial",
        ("eige.crypto.signing",),
        "Ed25519 signatures identify which registered key signed a record; they do not prove the keyholder acted honestly.",
        (f"{_R}::TestF5SymmetricSignatures",
         f"{_ADV}::test_forged_county_key_head_fails"),
    ),
    ControlMapping(
        "NIST SP 800-53r5", "AU-12", "Audit Record Generation", "implemented",
        ("eige.ledger.log", "eige.pipeline"),
        "Canonical audit records are generated for CVRs, custody events, heads and publication bundles.",
        ("tests/test_eige_v22_verifier.py::test_build_synthetic_bundle_verifies_with_zero_failed_checks",),
    ),
    ControlMapping(
        "NIST SP 800-53r5", "SC-12", "Cryptographic Key Establishment and Management", "partial",
        ("eige.crypto.signing", "eige.config"),
        "Key registry with roles, validity windows, rotation and revocation; development keys refused in "
        "production. Hardware key ceremonies are not exercised in this repository.",
        ("tests/test_eige_v22_signing.py::test_registry_register_verify_rotate_revoke_and_round_trip",
         "tests/test_eige_v22_signing.py::test_development_signer_refuses_in_production",
         f"{_R}::TestF4PlaceholderKeys"),
    ),
    ControlMapping(
        "NIST SP 800-53r5", "SC-13", "Cryptographic Protection", "partial",
        ("eige.crypto.signing", "eige.crypto.merkle", "eige.crypto.commitments"),
        "Ed25519 (RFC 8032), SHA-256 Merkle trees (RFC 6962) and Pedersen tally commitments. HSM signing "
        "is available via PKCS#11 but untested on hardware.",
        ("tests/test_eige_v22_signing.py::test_rfc8032_ed25519_vector_one_with_cryptography",
         "tests/test_eige_v22_merkle.py::test_certificate_transparency_reference_roots",
         "tests/test_eige_v22_commitments.py::test_county_commitments_aggregate_to_state_total"),
    ),
    ControlMapping(
        "NIST SP 800-53r5", "SI-7", "Software, Firmware, and Information Integrity", "partial",
        ("eige.ledger.log", "eige.ledger.bulletin", "eige.verify"),
        "Integrity of published election records is independently checkable. Tabulator software and "
        "firmware integrity is out of scope.",
        (f"{_ADV}::test_altered_results_totals_fail",
         f"{_ADV}::test_altered_commitment_opening_fails",
         f"{_R}::TestF1RollingHashForgeable"),
    ),
    ControlMapping(
        "NIST SP 800-53r5", "SI-7(6)", "Cryptographic Protection (software/firmware)", "planned",
        (), "No claim for cryptographic protection of voting-system software or firmware.",
    ),
    ControlMapping(
        "NIST SP 800-53r5", "SI-10", "Information Input Validation", "implemented",
        ("eige.canonical", "eige.model.election", "eige.bundle", "eige.data.open_data"),
        "Strict parsers reject malformed election definitions, CVRs, manifests, CSVs and bundles.",
        ("tests/test_eige_v22_model.py::test_parse_cvrs_strict_rejections_and_outcomes",
         "tests/test_eige_v22_properties.py::test_parse_cvrs_random_input_only_succeeds_or_raises_model_error",
         "tests/test_eige_v22_properties.py::test_parse_openelections_csv_random_bytes_only_succeeds_or_raises_open_data_error"),
    ),
    ControlMapping(
        "NIST SP 800-53r5", "CM-6", "Configuration Settings", "partial",
        ("eige.config",),
        "EIGE_MODE separates development and production; development-only components refuse production.",
        (f"{_R}::TestF4PlaceholderKeys",),
    ),
    ControlMapping("NIST SP 800-53r5", "AC-2", "Account Management", "planned", (), "No production account management."),
    ControlMapping("NIST SP 800-53r5", "AC-3", "Access Enforcement", "planned", (), "Supplied by the deployment environment."),
    ControlMapping("NIST SP 800-53r5", "IA-2", "Identification and Authentication", "planned", (), "No user authentication system is claimed."),
    ControlMapping("NIST SP 800-53r5", "RA-5", "Vulnerability Monitoring and Scanning", "planned", (), "Independent review invited; not an automated control."),
    ControlMapping("NIST SP 800-53r5", "CP-9", "System Backup", "planned", (), "Backup and retention are deployment responsibilities."),
    ControlMapping(
        "VVSG 2.0", "AUDIT", "Auditability of records", "partial",
        ("eige.ledger.log", "eige.verify"),
        "Published records can be recomputed independently. EIGE does not create the certified CVR.",
        ("tests/test_eige_v22_verifier.py::test_cli_bundle_exit_codes_zero_one_and_two",),
    ),
    ControlMapping(
        "VVSG 2.0", "RLA", "Risk-limiting audit support", "partial",
        ("eige.audit.rla", "eige.audit.sampling"),
        "Seeded sampling, BRAVO and Kaplan–Markov comparison audits; cross-check with SHANGRLA or Arlo.",
        ("tests/test_eige_v22_audit.py::test_rla_sample_size_reference_values_and_tie_rejection",
         "tests/test_eige_v22_audit.py::test_comparison_audit_confirms_clean_mvrs_and_escalates_with_overstatements",
         f"{_ADV}::test_sample_seed_before_committed_root_timestamp_fails"),
    ),
    ControlMapping(
        "VVSG 2.0", "ACCOUNTING", "Ballot accounting support", "partial",
        ("eige.audit.reconciliation", "eige.model.election"),
        "Reconciliation flags manifest/cast/counted/reported/provisional mismatches for explanation.",
        ("tests/test_eige_v22_audit.py::test_reconciliation_discrepancy_codes",),
    ),
    ControlMapping("VVSG 2.0", "TABULATION", "Tabulator security and certification", "planned", (), "Out of scope."),
)


def mappings(framework: str | None = None) -> List[ControlMapping]:
    return [m for m in CONTROL_MAPPINGS if framework is None or m.framework == framework]


def oscal_component_definition(last_modified: str = "2026-10-06T00:00:00+00:00") -> dict:
    """Return an OSCAL component definition whose statuses match ``CONTROL_MAPPINGS``.

    Deterministic: UUIDs are name-based so the output is reproducible.
    """
    def uid(*parts: str) -> str:
        return str(uuid.uuid5(_NS, "/".join(parts)))

    reqs = []
    for m in mappings("NIST SP 800-53r5"):
        reqs.append({
            "uuid": uid("req", m.control_id),
            "control-id": m.control_id.lower().replace("(", ".").replace(")", ""),
            "description": m.statement,
            "props": [
                {"name": "implementation-status", "ns": "https://fedramp.gov/ns/oscal", "value": m.status},
            ] + [{"name": "eige-test", "ns": "https://axiomzero.org/ns/eige", "value": t} for t in m.tests],
        })
    return {
        "component-definition": {
            "uuid": uid("component-definition", "eige", "22.0.0"),
            "metadata": {
                "title": "EIGE v22 audit-support and transparency tool",
                "last-modified": last_modified,
                "version": "22.0.0",
                "oscal-version": OSCAL_VERSION,
                "remarks": "Statuses reflect tested behaviour only. EIGE is not a certified voting system.",
            },
            "components": [{
                "uuid": uid("component", "eige"),
                "type": "software",
                "title": "EIGE",
                "description": "Tamper-evident election record log, verifier and audit-support library.",
                "control-implementations": [{
                    "uuid": uid("impl", "sp800-53r5"),
                    "source": "https://doi.org/10.6028/NIST.SP.800-53r5",
                    "description": "NIST SP 800-53 Rev. 5 controls with honest implementation status.",
                    "implemented-requirements": reqs,
                }],
            }],
        }
    }
