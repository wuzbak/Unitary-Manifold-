# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 476 — Lean4 CI Engineering Fix."""
from __future__ import annotations

from src.core.pillar476_lean4_ci_fix import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    CANONICAL_PROOF_HASH,
    N_W,
    K_CS,
    compute_proof_hash,
    validate_proof_hash,
    check_lean4_binary,
    compile_lean4_proof,
    tier1_hash_verification,
    tier2_lean4_compilation,
    ci_installation_metadata,
    full_verification_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'LEAN4_CI_HASH_VALIDATED'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 476

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_canonical_hash_is_hex(self):
        assert len(CANONICAL_PROOF_HASH) == 64  # SHA-256 is 64 hex chars
        assert all(c in '0123456789abcdef' for c in CANONICAL_PROOF_HASH)


class TestProofHash:
    def test_compute_returns_string(self):
        h = compute_proof_hash()
        assert isinstance(h, str)
        assert len(h) == 64

    def test_compute_matches_canonical(self):
        h = compute_proof_hash()
        assert h == CANONICAL_PROOF_HASH

    def test_different_text_different_hash(self):
        h1 = compute_proof_hash("proof text A")
        h2 = compute_proof_hash("proof text B")
        assert h1 != h2

    def test_same_text_same_hash(self):
        h1 = compute_proof_hash("test")
        h2 = compute_proof_hash("test")
        assert h1 == h2


class TestValidateProofHash:
    def test_canonical_matches(self):
        result = validate_proof_hash()
        assert result['match'] is True

    def test_status_valid(self):
        result = validate_proof_hash()
        assert result['status'] == 'HASH_VALID'

    def test_mismatch_detected(self):
        result = validate_proof_hash("tampered proof text")
        assert result['match'] is False
        assert result['status'] == 'HASH_MISMATCH'

    def test_returns_dict(self):
        result = validate_proof_hash()
        assert isinstance(result, dict)

    def test_has_both_hashes(self):
        result = validate_proof_hash()
        assert 'canonical_hash' in result
        assert 'computed_hash' in result


class TestLean4BinaryCheck:
    def test_returns_dict(self):
        result = check_lean4_binary()
        assert isinstance(result, dict)

    def test_has_status(self):
        result = check_lean4_binary()
        assert 'status' in result

    def test_status_is_valid_value(self):
        result = check_lean4_binary()
        assert result['status'] in (
            'LEAN4_TOOLCHAIN_AVAILABLE',
            'LEAN4_TOOLCHAIN_MISSING',
        )

    def test_has_availability_fields(self):
        result = check_lean4_binary()
        assert 'lean_available' in result
        assert 'lake_available' in result


class TestCompileLean4Proof:
    def test_returns_dict(self):
        result = compile_lean4_proof()
        assert isinstance(result, dict)

    def test_has_status(self):
        result = compile_lean4_proof()
        assert 'status' in result

    def test_status_is_valid(self):
        result = compile_lean4_proof()
        valid = {
            'LEAN4_COMPILED',
            'LEAN4_COMPILE_ERROR',
            'LEAN4_TIMEOUT',
            'TOOLCHAIN_MISSING',
        }
        assert result['status'] in valid

    def test_fallback_instruction_when_missing(self):
        result = compile_lean4_proof()
        if result['status'] == 'TOOLCHAIN_MISSING':
            assert 'fallback' in result
            assert 'installation_cmd' in result


class TestTier1HashVerification:
    def setup_method(self):
        self.result = tier1_hash_verification()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_ci_compatible(self):
        assert self.result['ci_compatible'] is True

    def test_no_lean4_required(self):
        assert self.result['lean4_required'] is False

    def test_match_is_true(self):
        assert self.result['match'] is True

    def test_status_valid(self):
        assert self.result['status'] == 'HASH_VALID'

    def test_has_pillar(self):
        assert self.result['pillar'] == PILLAR_NUMBER


class TestTier2Compilation:
    def setup_method(self):
        self.result = tier2_lean4_compilation()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_lean4_required_true(self):
        assert self.result['lean4_required'] is True

    def test_has_verification_tier(self):
        assert self.result['verification_tier'] == 'TIER2_LEAN4_COMPILATION'

    def test_has_pillar(self):
        assert self.result['pillar'] == PILLAR_NUMBER


class TestCIInstallationMetadata:
    def setup_method(self):
        self.meta = ci_installation_metadata()

    def test_returns_dict(self):
        assert isinstance(self.meta, dict)

    def test_has_install_command(self):
        assert 'install_command' in self.meta
        assert 'elan' in self.meta['install_command']

    def test_has_verify_command(self):
        assert self.meta['verify_command'] == 'lean --version'

    def test_has_added_minutes(self):
        assert self.meta['ci_added_minutes'] > 0


class TestFullVerificationReport:
    def setup_method(self):
        self.report = full_verification_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == PILLAR_NUMBER

    def test_proof_integrity_true(self):
        assert self.report['proof_integrity'] is True

    def test_canonical_hash_matches(self):
        assert self.report['canonical_hash'] == CANONICAL_PROOF_HASH

    def test_has_tier1(self):
        assert 'tier1_hash' in self.report

    def test_has_tier2(self):
        assert 'tier2_lean4' in self.report

    def test_overall_status_set(self):
        assert self.report['overall_status'] in (
            'FULLY_VERIFIED_LEAN4_COMPILED',
            'TIER1_VERIFIED_HASH_ONLY',
            'VERIFICATION_FAILED',
        )

    def test_not_verification_failed(self):
        # Hash must match, so this should never be VERIFICATION_FAILED
        assert self.report['overall_status'] != 'VERIFICATION_FAILED'
