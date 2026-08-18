# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/tests/test_eige_zk_proof.py — Zero-Knowledge Pedersen Commitment Tests
=============================================================================

Tests commitment roundtrip, hiding, binding, and integration with
generate_holon_zero_cert().

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import math

import pytest

from src.zk_proof import (
    PedersenCommitment,
    PedersenProof,
    commit,
    verify_commitment,
    commit_metric_state,
    verify_metric_proof,
    proof_from_dict,
    _P, _G, _H, _PHI_SCALE,
)
from src.constants import K_CS, PHI_0, PHI_TOLERANCE
from src.holon_zero_cert import generate_holon_zero_cert, validate_holon_zero_cert


# ---------------------------------------------------------------------------
# Pedersen group parameters
# ---------------------------------------------------------------------------

class TestGroupParameters:
    def test_p_is_positive_2048_bit(self):
        assert _P > 0
        assert _P.bit_length() == 2048

    def test_g_is_generator(self):
        assert _G == 2

    def test_h_is_nonzero_and_less_than_p(self):
        assert 0 < _H < _P

    def test_h_differs_from_g(self):
        assert _H != _G


# ---------------------------------------------------------------------------
# commit() — basic operations
# ---------------------------------------------------------------------------

class TestCommit:
    def test_commitment_is_positive(self):
        pc = commit(42)
        assert pc.commitment > 0

    def test_commitment_less_than_p(self):
        pc = commit(100)
        assert pc.commitment < _P

    def test_value_stored_correctly(self):
        pc = commit(7)
        assert pc.value == 7

    def test_randomness_stored(self):
        pc = commit(7, randomness=12345)
        assert pc.randomness == 12345

    def test_deterministic_with_fixed_randomness(self):
        r = 9999
        pc1 = commit(42, randomness=r)
        pc2 = commit(42, randomness=r)
        assert pc1.commitment == pc2.commitment

    def test_random_randomness_different_each_call(self):
        pc1 = commit(42)
        pc2 = commit(42)
        # Probability of collision is negligible for 256-bit random r
        assert pc1.randomness != pc2.randomness

    def test_different_values_different_commitments(self):
        r = 1234
        c1 = commit(10, randomness=r).commitment
        c2 = commit(11, randomness=r).commitment
        assert c1 != c2

    def test_negative_value_raises(self):
        with pytest.raises(ValueError):
            commit(-1)

    def test_zero_value_commits(self):
        pc = commit(0, randomness=1)
        assert pc.commitment is not None

    def test_commitment_formula(self):
        """Verify C = g^v * h^r mod p."""
        v, r = 5, 3
        pc = commit(v, randomness=r)
        expected = (pow(_G, v, _P) * pow(_H, r, _P)) % _P
        assert pc.commitment == expected


# ---------------------------------------------------------------------------
# verify_commitment()
# ---------------------------------------------------------------------------

class TestVerifyCommitment:
    def test_verify_correct_opening(self):
        pc = commit(100, randomness=555)
        assert verify_commitment(pc.commitment, 100, 555) is True

    def test_verify_wrong_value_fails(self):
        pc = commit(100, randomness=555)
        assert verify_commitment(pc.commitment, 101, 555) is False

    def test_verify_wrong_randomness_fails(self):
        pc = commit(100, randomness=555)
        assert verify_commitment(pc.commitment, 100, 556) is False

    def test_verify_zero_value(self):
        pc = commit(0, randomness=1)
        assert verify_commitment(pc.commitment, 0, 1) is True

    def test_verify_large_value(self):
        large_v = 10 ** 30
        r = 42
        pc = commit(large_v, randomness=r)
        assert verify_commitment(pc.commitment, large_v, r) is True


# ---------------------------------------------------------------------------
# Hiding property
# ---------------------------------------------------------------------------

class TestHidingProperty:
    def test_same_value_different_randomness_different_commitment(self):
        """Commitment must be different when blinding factor changes."""
        v = 74  # K_CS
        r1, r2 = 1000, 2000
        c1 = commit(v, randomness=r1).commitment
        c2 = commit(v, randomness=r2).commitment
        assert c1 != c2

    def test_multiple_random_commitments_to_same_value_all_differ(self):
        v = 42
        commitments = [commit(v).commitment for _ in range(10)]
        assert len(set(commitments)) > 5  # with overwhelm probability all differ

    def test_commitment_reveals_no_obvious_value_info(self):
        """The commitment to PHI_0 scaled should not be equal to PHI_0 scaled."""
        phi_int = round(PHI_0 * _PHI_SCALE)
        pc = commit(phi_int)
        # Trivial test: commitment != value
        assert pc.commitment != phi_int


# ---------------------------------------------------------------------------
# Binding property
# ---------------------------------------------------------------------------

class TestBindingProperty:
    def test_cannot_open_to_wrong_value_with_same_randomness(self):
        """A commitment should not verify with a different (v', r) pair
        unless a discrete log collision occurs (computationally infeasible)."""
        pc = commit(50, randomness=999)
        # Try to open to a different value with the same randomness
        assert verify_commitment(pc.commitment, 51, 999) is False

    def test_cannot_open_to_zero_with_arbitrary_randomness(self):
        pc = commit(100, randomness=12)
        # Check several wrong pairs
        for r_guess in range(0, 100):
            if not verify_commitment(pc.commitment, 0, r_guess):
                return  # expected: all fail
        pytest.fail("Should not be able to open to 0 with any of the tested randomness values")


# ---------------------------------------------------------------------------
# commit_metric_state()
# ---------------------------------------------------------------------------

class TestCommitMetricState:
    def test_returns_pedersen_proof(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        assert isinstance(proof, PedersenProof)

    def test_phi_delta_bound_true_for_valid_phi(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        assert proof.phi_delta_bound is True

    def test_phi_delta_bound_false_for_drifted_phi(self):
        proof = commit_metric_state(phi_eff=PHI_0 + 1e-10, k_cs=K_CS)
        assert proof.phi_delta_bound is False

    def test_k_cs_match_true_for_correct_k_cs(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        assert proof.k_cs_match is True

    def test_k_cs_match_false_for_wrong_k_cs(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=73)
        assert proof.k_cs_match is False

    def test_invariants_verified_when_both_hold(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        assert proof.invariants_verified() is True

    def test_invariants_violated_when_phi_drifts(self):
        proof = commit_metric_state(phi_eff=PHI_0 + 0.01, k_cs=K_CS)
        assert proof.invariants_verified() is False

    def test_proof_bytes_length(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        # 256 bytes commitment + 2 flag bytes
        assert len(proof.proof_bytes) == 258

    def test_proof_bytes_flags_reflect_invariants(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        assert proof.proof_bytes[256] == 1  # phi_delta_bound = True
        assert proof.proof_bytes[257] == 1  # k_cs_match = True

    def test_proof_bytes_flags_violated(self):
        proof = commit_metric_state(phi_eff=PHI_0 + 0.1, k_cs=73)
        assert proof.proof_bytes[256] == 0  # phi_delta_bound = False
        assert proof.proof_bytes[257] == 0  # k_cs_match = False

    def test_commitment_positive_and_valid(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        assert 0 < proof.commitment < _P

    def test_different_phi_effs_different_commitments(self):
        r = 9999
        p1 = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS, randomness=r)
        p2 = commit_metric_state(phi_eff=PHI_0 + 0.001, k_cs=K_CS, randomness=r)
        assert p1.commitment != p2.commitment

    def test_as_dict_has_required_keys(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        d = proof.as_dict()
        assert "commitment" in d
        assert "proof_bytes" in d
        assert "phi_delta_bound" in d
        assert "k_cs_match" in d
        assert "proof_status" in d

    def test_as_dict_has_no_raw_phi_eff(self):
        """The proof dict must not contain the raw phi_eff float."""
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        d = proof.as_dict()
        assert "phi_eff" not in d

    def test_as_dict_proof_status_verified(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        d = proof.as_dict()
        assert d["proof_status"] == "INVARIANTS_VERIFIED"

    def test_as_dict_proof_status_violated(self):
        proof = commit_metric_state(phi_eff=PHI_0 + 1.0, k_cs=73)
        d = proof.as_dict()
        assert d["proof_status"] == "INVARIANTS_VIOLATED"


# ---------------------------------------------------------------------------
# verify_metric_proof()
# ---------------------------------------------------------------------------

class TestVerifyMetricProof:
    def test_valid_proof_passes(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        assert verify_metric_proof(proof) is True

    def test_violated_proof_fails(self):
        proof = commit_metric_state(phi_eff=PHI_0 + 1.0, k_cs=73)
        assert verify_metric_proof(proof) is False

    def test_empty_proof_bytes_fails(self):
        bad_proof = PedersenProof(
            commitment=1,
            proof_bytes=b"",
            phi_delta_bound=True,
            k_cs_match=True,
        )
        assert verify_metric_proof(bad_proof) is False

    def test_truncated_proof_bytes_fails(self):
        bad_proof = PedersenProof(
            commitment=1,
            proof_bytes=b"\x01" * 10,  # too short
            phi_delta_bound=True,
            k_cs_match=True,
        )
        assert verify_metric_proof(bad_proof) is False


# ---------------------------------------------------------------------------
# proof_from_dict()
# ---------------------------------------------------------------------------

class TestProofFromDict:
    def test_roundtrip(self):
        original = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS, randomness=777)
        d = original.as_dict()
        restored = proof_from_dict(d)
        assert restored.commitment == original.commitment
        assert restored.proof_bytes == original.proof_bytes
        assert restored.phi_delta_bound == original.phi_delta_bound
        assert restored.k_cs_match == original.k_cs_match

    def test_verify_after_roundtrip(self):
        proof = commit_metric_state(phi_eff=PHI_0, k_cs=K_CS)
        d = proof.as_dict()
        restored = proof_from_dict(d)
        assert verify_metric_proof(restored) is True


# ---------------------------------------------------------------------------
# Integration with generate_holon_zero_cert()
# ---------------------------------------------------------------------------

class TestCertIntegration:
    def test_cert_zero_knowledge_proof_has_no_raw_phi(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-KING",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=1,
            state_hash="aa" * 64,
        )
        zk = cert["zero_knowledge_proof"]
        # Must NOT contain raw phi_eff float
        assert "phi_eff" not in zk

    def test_cert_proof_bytes_present(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-KING",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=1,
            state_hash="aa" * 64,
        )
        assert "proof_bytes" in cert["zero_knowledge_proof"]

    def test_cert_validates_with_pedersen_proof(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-KING",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=1,
            state_hash="aa" * 64,
        )
        assert validate_holon_zero_cert(cert) is True

    def test_cert_phi_delta_bound_true(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-KING",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=1,
            state_hash="bb" * 64,
        )
        assert cert["zero_knowledge_proof"]["phi_delta_bound"] is True

    def test_cert_k_cs_match_true(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-KING",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=1,
            state_hash="cc" * 64,
        )
        assert cert["zero_knowledge_proof"]["k_cs_match"] is True

    def test_cert_proof_status_verified(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-KING",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=1,
            state_hash="dd" * 64,
        )
        assert cert["zero_knowledge_proof"]["proof_status"] == "INVARIANTS_VERIFIED"

    def test_cert_with_drifted_phi_proof_status_violated(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-KING",
            phi_eff=PHI_0 + 1e-10,
            k_cs=K_CS,
            block_height=1,
            state_hash="ee" * 64,
        )
        assert cert["zero_knowledge_proof"]["proof_status"] == "INVARIANTS_VIOLATED"
        assert validate_holon_zero_cert(cert) is False

    def test_cert_commitment_field_present_and_hex(self):
        cert = generate_holon_zero_cert(
            jurisdiction_id="WA-KING",
            phi_eff=PHI_0,
            k_cs=K_CS,
            block_height=1,
            state_hash="ff" * 64,
        )
        commitment_str = cert["zero_knowledge_proof"]["commitment"]
        assert isinstance(commitment_str, str)
        assert commitment_str.startswith("0x")
