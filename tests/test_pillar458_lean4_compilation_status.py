# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 458 — Lean4 compilation status."""
import re

from src.core.pillar458_lean4_compilation_status import (
    PILLAR_STATUS,
    VERSION,
    check_lean4_availability,
    document_compilation_obstruction,
    lean4_proof_text_hash,
    lean4_compilation_certificate,
    what_would_close_this,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'LEAN4_BLOCKED_NAMED_OBSTRUCTION'

    def test_version(self):
        assert VERSION == 'v14.0'


class TestAvailability:
    def test_returns_dict(self):
        assert isinstance(check_lean4_availability(), dict)

    def test_has_available_flag(self):
        assert 'available' in check_lean4_availability()

    def test_has_reason(self):
        assert check_lean4_availability()['reason']

    def test_reason_is_string(self):
        assert isinstance(check_lean4_availability()['reason'], str)


class TestProofHash:
    def test_hash_length(self):
        assert len(lean4_proof_text_hash()) == 64

    def test_hash_hex(self):
        assert re.fullmatch(r'[0-9a-f]{64}', lean4_proof_text_hash())

    def test_hash_deterministic(self):
        assert lean4_proof_text_hash() == lean4_proof_text_hash()


class TestObstruction:
    def test_returns_dict(self):
        assert isinstance(document_compilation_obstruction(), dict)

    def test_hash_mentioned_when_blocked(self):
        obstruction = document_compilation_obstruction()
        if obstruction['status'] == PILLAR_STATUS:
            assert lean4_proof_text_hash() in obstruction['statement']

    def test_engineering_not_mathematics_phrase(self):
        obstruction = document_compilation_obstruction()
        if obstruction['status'] == PILLAR_STATUS:
            assert 'engineering, not mathematics' in obstruction['statement']

    def test_named_obstruction_present_when_blocked(self):
        obstruction = document_compilation_obstruction()
        if obstruction['status'] == PILLAR_STATUS:
            assert obstruction['named_obstruction'] == 'LEAN4_TOOLCHAIN_NOT_INSTALLED_IN_CI_RUNNER'


class TestCertificate:
    def test_pillar_number(self):
        assert lean4_compilation_certificate()['pillar'] == 458

    def test_hash_matches(self):
        assert lean4_compilation_certificate()['proof_text_hash'] == lean4_proof_text_hash()

    def test_numeric_steps_verified(self):
        assert lean4_compilation_certificate()['numeric_steps_verified_by_python'] is True

    def test_obstruction_present(self):
        assert 'obstruction' in lean4_compilation_certificate()

    def test_status_blocked_or_compiled(self):
        assert lean4_compilation_certificate()['status'] in {PILLAR_STATUS, 'LEAN4_COMPILED'}


class TestClosurePath:
    def test_closure_path_mentions_install(self):
        assert 'Install Lean4 + mathlib4' in what_would_close_this()['closure_path']

    def test_steps_length(self):
        assert len(what_would_close_this()['steps']) == 4

    def test_run_lake_build_step_present(self):
        assert any('lake build' in step for step in what_would_close_this()['steps'])


class TestAvailabilityKeys:
    def test_availability_has_paths(self):
        availability = check_lean4_availability()
        assert 'lean_path' in availability and 'lake_path' in availability

    def test_reason_mentions_missing_or_available(self):
        reason = check_lean4_availability()['reason']
        assert ('Missing toolchain components' in reason) or ('Lean4 available' in reason)


class TestCertificateDetails:
    def test_availability_embedded(self):
        assert 'availability' in lean4_compilation_certificate()

    def test_engineering_flag_boolean(self):
        assert isinstance(lean4_compilation_certificate()['ci_obstruction_is_engineering'], bool)

    def test_closure_steps_nonempty(self):
        assert all(step for step in what_would_close_this()['steps'])


class TestPillarReport:
    def test_pillar_number(self):
        assert pillar_report()['pillar'] == 458

    def test_status(self):
        assert pillar_report()['status'] == PILLAR_STATUS

    def test_certificate_present(self):
        assert 'certificate' in pillar_report()

    def test_closure_present(self):
        assert 'closure' in pillar_report()
