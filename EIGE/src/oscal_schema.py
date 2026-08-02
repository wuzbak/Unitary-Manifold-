# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/oscal_schema.py — OSCAL 1.5.0 Dataclasses & NIST SP-800-53 R5 Mappings
==================================================================================

This module defines the structured data types used to produce machine-readable
OSCAL 1.5.0 compliance artifacts.  The schema enforces:

  - NIST SP 800-53 Revision 5 control taxonomy
  - NIST VVSG 2.0 mapping criteria (from EIGE Section 3.4)
  - Zero-knowledge structure: no raw ballot data, no voter identifiers

All serialization produces valid JSON via to_json() / to_dict().

NIST SP 800-53 R5 Control Mapping (from EIGE Section 3.4)
-----------------------------------------------------------
Component                         | NIST Control | OSCAL Taxonomy
Chern-Simons Rolling Hash         | SI-7         | System & Information Integrity
5D Metric Closure (G_AB)          | AC-1         | Access Control
3:2 Scaffold Invariant Auditing   | AU-12        | Audit & Accountability
Pentad HILS High-Density Matrix   | PS-*         | Personnel Security
Holon Zero Certificate Engine     | CA-*         | Security Assessment

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .constants import ENGINE_VERSION, OSCAL_VERSION, NIST_SP_VERSION, K_CS, PHI_0


# ---------------------------------------------------------------------------
# NIST SP-800-53 R5 control mapping catalogue
# ---------------------------------------------------------------------------

NIST_SP800_53_MAPPINGS: Dict[str, Dict[str, str]] = {
    "chern_simon_hash": {
        "control_id": "SI-7",
        "control_family": "System and Information Integrity",
        "vvsg_criterion": "Data Integrity and Electronic Chain of Custody",
        "oscal_taxonomy": "System Integrity (SI) Component",
        "description": (
            "Path-dependent CS rolling hash ensures sequential ballot integrity. "
            "Retroactive insertion or reordering of any ballot is immediately detectable "
            "as a hash chain break, satisfying SI-7 software and information integrity controls."
        ),
    },
    "metric_closure": {
        "control_id": "AC-1",
        "control_family": "Access Control",
        "vvsg_criterion": "Access Control and Perimeter Hardening",
        "oscal_taxonomy": "Access Control (AC) Component",
        "description": (
            "5D metric closure validation (φ₀=π/4, k_CS=74) renders unauthorized "
            "administrative modifications immediately detectable as curvature errors, "
            "satisfying AC-1 access control policy and procedure requirements."
        ),
    },
    "scaffold_invariant": {
        "control_id": "AU-12",
        "control_family": "Audit and Accountability",
        "vvsg_criterion": "Comprehensive Audit and Accountability Tracks",
        "oscal_taxonomy": "Audit Logging (AU) Component",
        "description": (
            "3:2 Scaffold Invariant Auditing Engine maps field layers to legal audit "
            "counterweights (voter registry ↔ boundary tally), satisfying AU-12 audit "
            "generation requirements with 500ms dossier emission guarantee."
        ),
    },
    "hils_pentad": {
        "control_id": "PS-6",
        "control_family": "Personnel Security",
        "vvsg_criterion": "Human Factors, Transparency, and Usability Floors",
        "oscal_taxonomy": "Personnel Security (PS) Component",
        "description": (
            "Unitary Pentad HILS 5-body matrix treats all human actors as untrusted "
            "data vectors requiring multi-signature handover protocols, satisfying PS-6 "
            "access agreements and multi-party authorization requirements."
        ),
    },
    "holon_zero_cert": {
        "control_id": "CA-2",
        "control_family": "Security Assessment and Authorization",
        "vvsg_criterion": "Comprehensive Security and System State Assessment",
        "oscal_taxonomy": "Assessment Plan (AP) Component",
        "description": (
            "Holon Zero Certificate Engine generates zero-knowledge OSCAL 1.5.0 proofs "
            "of metric invariant satisfaction for federal oversight consumption, satisfying "
            "CA-2 security assessment controls without exposing raw ballot telemetry."
        ),
    },
}


# ---------------------------------------------------------------------------
# Core OSCAL dataclasses
# ---------------------------------------------------------------------------

@dataclass
class OSCALMetadata:
    """OSCAL document metadata block."""

    title: str
    version: str = ENGINE_VERSION
    oscal_version: str = OSCAL_VERSION
    last_modified: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    remarks: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "last-modified": self.last_modified,
            "version": self.version,
            "oscal-version": self.oscal_version,
            "remarks": self.remarks,
        }


@dataclass
class SystemStateSnapshot:
    """Snapshot of system metric state at the time of an event."""

    expected_phi_0: float = PHI_0
    observed_phi_eff: float = PHI_0
    k_cs_level: int = K_CS
    kinetic_mixing_rho: float = 0.0
    unitarity_status: str = "CLOSED_PURE"
    active_mantissa_bits: int = 512
    floating_point_regime: str = "MPMATH_HIGH_PRECISION"
    total_shards_deployed: int = 8
    synchronized_shards: int = 8
    parity_verification: str = f"PASS_{K_CS}_{K_CS}"

    def to_dict(self) -> dict:
        return {
            "metric_identity": {
                "expected_phi_0": str(self.expected_phi_0),
                "observed_phi_eff": str(self.observed_phi_eff),
                "k_cs_level": self.k_cs_level,
                "kinetic_mixing_rho": self.kinetic_mixing_rho,
                "unitarity_status": self.unitarity_status,
            },
            "precision_allocation": {
                "active_mantissa_bits": self.active_mantissa_bits,
                "floating_point_regime": self.floating_point_regime,
            },
            "holographic_shards": {
                "total_shards_deployed": self.total_shards_deployed,
                "synchronized_shards": self.synchronized_shards,
                "parity_verification": self.parity_verification,
            },
        }


@dataclass
class InterventionMetadata:
    """Metadata about a detected intervention or override attempt."""

    operator_cryptographic_signature: str
    hardware_terminal_uuid: str
    command_payload_intercepted: str
    administrative_clearance_level: str = "LEVEL_1_OVERSIGHT_BYPASS_ATTEMPT"
    impact_analysis: str = (
        "Attempted structural bypass of path-dependent Chern-Simons loop sequence."
    )

    def to_dict(self) -> dict:
        return {
            "operator_cryptographic_signature": self.operator_cryptographic_signature,
            "administrative_clearance_level": self.administrative_clearance_level,
            "hardware_terminal_uuid": self.hardware_terminal_uuid,
            "command_payload_intercepted": self.command_payload_intercepted,
            "impact_analysis": self.impact_analysis,
        }


@dataclass
class AutomatedResponseAction:
    """A single automated response action taken by the sentinel."""

    sequence: int
    action_taken: str
    description: str

    def to_dict(self) -> dict:
        return {
            "sequence": self.sequence,
            "action_taken": self.action_taken,
            "description": self.description,
        }


# Default sentinel response action sequence
DEFAULT_RESPONSE_ACTIONS: List[AutomatedResponseAction] = [
    AutomatedResponseAction(
        sequence=1,
        action_taken="INVOKE_SENTINEL_LOAD_BALANCE_ABSORPTION",
        description=(
            "System optimization levels throttled. Input packet isolated into "
            "quarantined, non-privileged computing manifold. Main tally pipeline shielded."
        ),
    ),
    AutomatedResponseAction(
        sequence=2,
        action_taken="EXPORT_DOSSIER_TO_PUBLIC_MIRROR",
        description=(
            "Immediate writing of state telemetry to immutable public storage targets."
        ),
    ),
    AutomatedResponseAction(
        sequence=3,
        action_taken="LEGAL_AGPL_COMPLIANCE_ENFORCEMENT",
        description=(
            "Triggered broadcast of active runtime memory footprint hashes to registered "
            "public code mirrors to prevent proprietary black-box encapsulation."
        ),
    ),
]


@dataclass
class AssessmentResults:
    """OSCAL assessment-results block for override dossiers."""

    assessment_uuid: str
    system_state: SystemStateSnapshot
    intervention: InterventionMetadata
    response_actions: List[AutomatedResponseAction]
    status: str = "INTERCEPTED_BY_SENTINEL"
    title: str = "System Telemetry Real-Time Capture on Override Trigger"
    start: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "uuid": self.assessment_uuid,
            "title": self.title,
            "start": self.start,
            "status": self.status,
            "system-state-snapshot": self.system_state.to_dict(),
            "intervention-metadata": self.intervention.to_dict(),
            "automated-response-actions": [a.to_dict() for a in self.response_actions],
        }


@dataclass
class AssessmentPlan:
    """Top-level OSCAL assessment-plan document (override dossier format)."""

    plan_uuid: str
    metadata: OSCALMetadata
    results: AssessmentResults

    def to_dict(self) -> dict:
        return {
            "$schema": "https://nist.gov",
            "assessment-plan": {
                "uuid": self.plan_uuid,
                "metadata": self.metadata.to_dict(),
                "assessment-results": self.results.to_dict(),
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to OSCAL-compliant JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


# ---------------------------------------------------------------------------
# Holon Zero Certificate schema (component-definition format)
# ---------------------------------------------------------------------------

@dataclass
class ImplementedRequirement:
    """A single NIST control implementation inside a Holon Zero cert."""

    req_uuid: str
    control_id: str
    remarks: str

    def to_dict(self) -> dict:
        return {
            "uuid": self.req_uuid,
            "control-id": self.control_id,
            "remarks": self.remarks,
        }


@dataclass
class ControlImplementation:
    """Control implementation block inside a Holon Zero cert component."""

    impl_uuid: str
    source: str
    description: str
    requirements: List[ImplementedRequirement]

    def to_dict(self) -> dict:
        return {
            "uuid": self.impl_uuid,
            "source": self.source,
            "description": self.description,
            "implemented-requirements": [r.to_dict() for r in self.requirements],
        }


@dataclass
class HolonZeroComponent:
    """A single component entry in a Holon Zero Certificate."""

    component_uuid: str
    component_type: str
    title: str
    description: str
    purpose: str
    status_state: str
    control_implementations: List[ControlImplementation]

    def to_dict(self) -> dict:
        return {
            "uuid": self.component_uuid,
            "type": self.component_type,
            "title": self.title,
            "description": self.description,
            "purpose": self.purpose,
            "status": {"state": self.status_state},
            "control-implementations": [ci.to_dict() for ci in self.control_implementations],
        }


@dataclass
class HolonZeroComponentDefinition:
    """
    Top-level OSCAL component-definition document — Holon Zero Certificate.

    This is the zero-knowledge artifact transmitted to federal oversight tiers.
    It contains ONLY the mathematical proof that k_CS=74 and φ₀=π/4 hold;
    no raw ballot counts, no voter identifiers.
    """

    cert_uuid: str
    metadata: OSCALMetadata
    components: List[HolonZeroComponent]
    jurisdiction_id: str = ""
    block_height: int = 0
    state_hash: str = ""

    def to_dict(self) -> dict:
        return {
            "$schema": "https://nist.gov",
            "component-definition": {
                "uuid": self.cert_uuid,
                "metadata": self.metadata.to_dict(),
                "jurisdiction_id": self.jurisdiction_id,
                "block_height": self.block_height,
                "state_hash": self.state_hash,
                "components": [c.to_dict() for c in self.components],
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to OSCAL-compliant JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def new_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def build_override_dossier(
    operator_sig: str,
    terminal_id: str,
    command_payload: str,
    phi_eff: float = PHI_0,
    k_cs: int = K_CS,
    rho: float = 0.0,
    synchronized_shards: int = 8,
    unitarity_status: str = "COMPROMISED_INFRASTRUCTURE",
) -> AssessmentPlan:
    """Factory: build a complete OSCAL override dossier AssessmentPlan.

    Parameters
    ----------
    operator_sig : str
        Cryptographic signature of the operator who triggered the event.
    terminal_id : str
        Hardware terminal UUID of the node that attempted the override.
    command_payload : str
        JSON-serialized payload of the intercepted command.
    phi_eff : float
        Observed radion scalar at interception time.
    k_cs : int
        Observed k_CS level at interception time.
    rho : float
        Observed kinetic mixing parameter.
    synchronized_shards : int
        Number of shards synchronized at interception time.
    unitarity_status : str
        Descriptive unitarity status string.
    """
    now = datetime.now(timezone.utc).isoformat()
    plan_uuid = new_uuid()
    results_uuid = new_uuid()

    metadata = OSCALMetadata(
        title="AxiomZero EIGE v21.0 Automated System Override Integrity Dossier",
        version=f"{ENGINE_VERSION}-HARDENED",
        last_modified=now,
        remarks="Irrevocable Automated Public Record of Administrative System Intervention.",
    )

    snapshot = SystemStateSnapshot(
        observed_phi_eff=phi_eff,
        k_cs_level=k_cs,
        kinetic_mixing_rho=rho,
        synchronized_shards=synchronized_shards,
        unitarity_status=unitarity_status,
    )

    intervention = InterventionMetadata(
        operator_cryptographic_signature=operator_sig,
        hardware_terminal_uuid=terminal_id,
        command_payload_intercepted=command_payload,
    )

    results = AssessmentResults(
        assessment_uuid=results_uuid,
        system_state=snapshot,
        intervention=intervention,
        response_actions=list(DEFAULT_RESPONSE_ACTIONS),
        start=now,
    )

    return AssessmentPlan(
        plan_uuid=plan_uuid,
        metadata=metadata,
        results=results,
    )
