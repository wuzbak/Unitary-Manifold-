# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/oscal_schema.py"""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.oscal_schema import (
    OSCALMetadata,
    SystemStateSnapshot,
    InterventionMetadata,
    AutomatedResponseAction,
    AssessmentResults,
    AssessmentPlan,
    HolonZeroComponent,
    HolonZeroComponentDefinition,
    ControlImplementation,
    ImplementedRequirement,
    NIST_SP800_53_MAPPINGS,
    DEFAULT_RESPONSE_ACTIONS,
    build_override_dossier,
    new_uuid,
)
from EIGE.src.constants import K_CS, PHI_0, ENGINE_VERSION, OSCAL_VERSION


class TestNISTMappings:
    def test_all_five_components_present(self):
        keys = set(NIST_SP800_53_MAPPINGS.keys())
        assert "chern_simon_hash" in keys
        assert "metric_closure" in keys
        assert "scaffold_invariant" in keys
        assert "hils_pentad" in keys
        assert "holon_zero_cert" in keys

    def test_si7_maps_to_chern_simon_hash(self):
        assert NIST_SP800_53_MAPPINGS["chern_simon_hash"]["control_id"] == "SI-7"

    def test_ac1_maps_to_metric_closure(self):
        assert NIST_SP800_53_MAPPINGS["metric_closure"]["control_id"] == "AC-1"

    def test_au12_maps_to_scaffold_invariant(self):
        assert NIST_SP800_53_MAPPINGS["scaffold_invariant"]["control_id"] == "AU-12"

    def test_each_mapping_has_required_fields(self):
        for key, mapping in NIST_SP800_53_MAPPINGS.items():
            for field in ("control_id", "control_family", "vvsg_criterion", "oscal_taxonomy"):
                assert field in mapping, f"Missing {field} in {key}"


class TestOSCALMetadata:
    def test_to_dict_has_required_keys(self):
        m = OSCALMetadata(title="Test")
        d = m.to_dict()
        for key in ("title", "last-modified", "version", "oscal-version", "remarks"):
            assert key in d

    def test_oscal_version_field(self):
        m = OSCALMetadata(title="Test")
        assert m.to_dict()["oscal-version"] == OSCAL_VERSION

    def test_custom_title(self):
        m = OSCALMetadata(title="My Report")
        assert m.to_dict()["title"] == "My Report"


class TestSystemStateSnapshot:
    def test_defaults_are_correct(self):
        s = SystemStateSnapshot()
        assert s.k_cs_level == K_CS
        assert abs(s.expected_phi_0 - PHI_0) < 1e-15

    def test_to_dict_structure(self):
        s = SystemStateSnapshot()
        d = s.to_dict()
        assert "metric_identity" in d
        assert "precision_allocation" in d
        assert "holographic_shards" in d

    def test_metric_identity_has_phi_0(self):
        s = SystemStateSnapshot()
        mi = s.to_dict()["metric_identity"]
        assert "expected_phi_0" in mi
        assert "k_cs_level" in mi

    def test_precision_allocation_has_512_bits(self):
        s = SystemStateSnapshot()
        pa = s.to_dict()["precision_allocation"]
        assert pa["active_mantissa_bits"] == 512

    def test_shard_count_in_holographic_shards(self):
        s = SystemStateSnapshot()
        hs = s.to_dict()["holographic_shards"]
        assert hs["total_shards_deployed"] == 8


class TestInterventionMetadata:
    def test_to_dict_has_required_keys(self):
        im = InterventionMetadata(
            operator_cryptographic_signature="0xABC",
            hardware_terminal_uuid="term-001",
            command_payload_intercepted='{"force_tally_override": true}',
        )
        d = im.to_dict()
        assert "operator_cryptographic_signature" in d
        assert "hardware_terminal_uuid" in d
        assert "command_payload_intercepted" in d
        assert "impact_analysis" in d


class TestDefaultResponseActions:
    def test_three_default_actions(self):
        assert len(DEFAULT_RESPONSE_ACTIONS) == 3

    def test_sequences_are_ordered(self):
        seqs = [a.sequence for a in DEFAULT_RESPONSE_ACTIONS]
        assert seqs == sorted(seqs)

    def test_sentinel_action_first(self):
        assert "SENTINEL" in DEFAULT_RESPONSE_ACTIONS[0].action_taken

    def test_export_action_second(self):
        assert "EXPORT" in DEFAULT_RESPONSE_ACTIONS[1].action_taken


class TestBuildOverrideDossier:
    def test_returns_assessment_plan(self):
        dossier = build_override_dossier("0xSIG", "term-001", '{"force": true}')
        assert isinstance(dossier, AssessmentPlan)

    def test_dossier_has_uuid(self):
        dossier = build_override_dossier("0xSIG", "term-001", '{}')
        assert len(dossier.plan_uuid) == 36  # UUID4 format

    def test_dossier_to_dict_has_schema(self):
        dossier = build_override_dossier("0xSIG", "term-001", '{}')
        d = dossier.to_dict()
        assert "$schema" in d
        assert "assessment-plan" in d

    def test_dossier_to_json_is_valid_json(self):
        dossier = build_override_dossier("0xSIG", "term-001", '{}')
        json_str = dossier.to_json()
        parsed = json.loads(json_str)
        assert "assessment-plan" in parsed

    def test_status_is_intercepted(self):
        dossier = build_override_dossier("0xSIG", "term-001", '{}')
        d = dossier.to_dict()
        results = d["assessment-plan"]["assessment-results"]
        assert results["status"] == "INTERCEPTED_BY_SENTINEL"

    def test_custom_phi_and_kcs_reflected(self):
        dossier = build_override_dossier(
            "0xSIG", "term-001", '{}',
            phi_eff=0.5, k_cs=73
        )
        d = dossier.to_dict()
        mi = d["assessment-plan"]["assessment-results"]["system-state-snapshot"]["metric_identity"]
        assert mi["k_cs_level"] == 73

    def test_unique_uuids_per_call(self):
        d1 = build_override_dossier("sig", "term", "{}")
        d2 = build_override_dossier("sig", "term", "{}")
        assert d1.plan_uuid != d2.plan_uuid


class TestNewUUID:
    def test_format(self):
        u = new_uuid()
        assert len(u) == 36
        parts = u.split("-")
        assert len(parts) == 5

    def test_uniqueness(self):
        uuids = {new_uuid() for _ in range(100)}
        assert len(uuids) == 100
