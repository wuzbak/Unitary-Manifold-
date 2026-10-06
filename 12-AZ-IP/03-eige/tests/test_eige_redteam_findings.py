# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Regression tests for red-team findings F1–F7 (see RED_TEAM_FINDINGS.md).

Each test class pins one finding.  Every test here fails against the v21
code and passes against v22: either the weakness is removed, or — where a
legacy function is kept for compatibility — it is labelled as non-security
and the v22 replacement is shown to resist the same attack.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re

import pytest

from eige.crypto.merkle import inclusion_proof, leaf_hash, merkle_root, verify_inclusion
from eige.crypto.signing import DevelopmentSigner, KeyRegistry, verify_signature
from eige.ledger.log import MerkleLog

PRODUCT = pathlib.Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# F1 — the Chern-Simons rolling hash is forgeable
# ---------------------------------------------------------------------------

class TestF1RollingHashForgeable:
    def test_forgery_is_demonstrable_so_hash_is_labelled_non_security(self):
        from src import chern_simon_hash as cs
        from src.chern_simon_hash import ChernSimonChain, forge_next_ballot

        honest = ChernSimonChain()
        for b in (11, 22, 33):
            honest.update(b)
        target = honest.digest()

        forged = ChernSimonChain()
        forged.update(999)  # attacker's chosen first ballot
        forged.update(forge_next_ballot(forged.digest(), target))
        assert forged.digest() == target  # different history, same "hash"
        assert "non-security" in cs.SECURITY_ROLE
        assert "NOT" in cs.__doc__ and "tamper evidence" in cs.__doc__

    def test_merkle_log_resists_the_same_substitution(self):
        honest = [json.dumps({"b": b}).encode() for b in (11, 22, 33)]
        forged = [json.dumps({"b": b}).encode() for b in (999, 4242)]
        assert merkle_root(honest) != merkle_root(forged)
        proof = inclusion_proof([leaf_hash(x) for x in honest], 1)
        assert verify_inclusion(leaf_hash(honest[1]), 1, 3, proof, merkle_root(honest))
        assert not verify_inclusion(leaf_hash(forged[0]), 1, 3, proof, merkle_root(honest))


# ---------------------------------------------------------------------------
# F2 — metric closure can never fail
# ---------------------------------------------------------------------------

class TestF2MetricClosureCannotFail:
    def test_closure_stays_stable_under_tampering_so_it_is_retired(self):
        from src import metric_closure as mc
        from src.county_node import CountyNode

        node = CountyNode("WA-047", "King County")
        for b in range(50):
            node.ingest_ballot([b % 3, 1, 0])
        honest = node._compute_phi_eff(node._chain.primary_digest(), 50)
        tampered = node._compute_phi_eff(123456789, 51)
        # Both pass: the signal carries no information about tampering...
        assert abs(honest - mc.PHI_0) <= mc.PHI_TOLERANCE
        assert abs(tampered - mc.PHI_0) <= mc.PHI_TOLERANCE
        # ...which is why v22 retires it.
        assert mc.SECURITY_ROLE.startswith("retired")

    def test_oscal_mapping_no_longer_claims_ac1_from_closure(self):
        from src.oscal_schema import NIST_SP800_53_MAPPINGS
        entry = NIST_SP800_53_MAPPINGS["metric_closure"]
        assert entry["implementation_status"] == "not-applicable"
        assert "immediately detectable" not in entry["description"]


# ---------------------------------------------------------------------------
# F3 — the "zero-knowledge proof" verified self-asserted flags
# ---------------------------------------------------------------------------

class TestF3FakeZeroKnowledgeProof:
    def test_forged_flag_bytes_do_not_verify(self):
        from src.zk_proof import PedersenProof, verify_metric_proof

        forged = PedersenProof(
            commitment=12345,
            proof_bytes=(12345).to_bytes(256, "big") + b"\x01\x01",
            phi_delta_bound=True,
            k_cs_match=True,
        )
        assert verify_metric_proof(forged) is False

    def test_flags_are_recomputed_from_the_opening(self):
        from src.zk_proof import commit_metric_state, verify_metric_proof
        bad = commit_metric_state(phi_eff=0.5, k_cs=74)
        # Flip the stored phi flag to "pass": verification must notice.
        bad.proof_bytes = bad.proof_bytes[:256] + b"\x01\x01"
        bad.phi_delta_bound = True
        assert verify_metric_proof(bad) is False

    def test_no_zero_knowledge_label_in_certificates(self):
        from src.holon_zero_cert import generate_holon_zero_cert
        from src.constants import PHI_0, K_CS
        cert = generate_holon_zero_cert("WA-STATE", PHI_0, K_CS, 1, "00" * 32)
        assert "zero_knowledge_proof" not in cert
        assert "not zero-knowledge" in json.dumps(cert, ensure_ascii=False).lower()


# ---------------------------------------------------------------------------
# F4 — placeholder / published keys and mock attestation by default
# ---------------------------------------------------------------------------

class TestF4PlaceholderKeys:
    def test_no_placeholder_key_derivation_in_source(self):
        for path in (PRODUCT / "src").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert '-hmac-key-placeholder".encode' not in text, path.name
            assert "_MOCK_HMAC_KEY" not in text, path.name

    def test_county_keys_not_derivable_from_county_id(self):
        from src.hsm_interface import SoftwareKeyProvider
        placeholder = hashlib.sha512(b"EIGE-v21-WA-047-hmac-key-placeholder").digest()
        assert SoftwareKeyProvider("WA-047")._key != placeholder

    def test_pentad_tokens_not_derivable_from_published_seed(self):
        from src.sentinel_load_balance import PENTAD_BODY_IDS, PentadHILS, _PENTAD_TOKEN_SEED
        hils = PentadHILS()
        body = sorted(PENTAD_BODY_IDS)[0]
        published = hashlib.sha512(_PENTAD_TOKEN_SEED + body.encode()).digest()
        assert hils._keys[body] != published

    def test_development_facilities_refuse_production(self, monkeypatch):
        from eige.config import ProductionModeViolation
        from src.county_node import CountyNode
        from src.tee_attestation import get_attestation_report
        monkeypatch.setenv("EIGE_MODE", "production")
        with pytest.raises(ProductionModeViolation):
            DevelopmentSigner()
        with pytest.raises(ProductionModeViolation):
            CountyNode("WA-047", "King County")  # default dev signer
        with pytest.raises(ProductionModeViolation):
            get_attestation_report(b"n", prefer="SOFTWARE_MOCK", allow_mock=True)

    def test_attestation_never_silently_mocked(self, monkeypatch):
        from src.tee_attestation import TEEUnavailable, get_attestation_report
        monkeypatch.delenv("EIGE_ALLOW_TEE_MOCK", raising=False)
        monkeypatch.setattr("os.path.exists", lambda p: False)
        with pytest.raises(TEEUnavailable):
            get_attestation_report(b"n")


# ---------------------------------------------------------------------------
# F5 — symmetric HMAC lets every verifier forge
# ---------------------------------------------------------------------------

class TestF5SymmetricSignatures:
    def test_telemetry_signed_with_public_key_signature(self):
        from src.county_node import CountyNode, verify_telemetry
        node = CountyNode("WA-047", "King County")
        node.ingest_ballot([1, 0, 1])
        t = node.get_shard_telemetry()
        assert t["signature_alg"] == "Ed25519" and "hmac_signature" not in t
        reg = KeyRegistry()
        reg.register_signer(node.signer, owner="WA-047", role="county", valid_from=0)
        assert verify_telemetry(t, reg, expected_owner="WA-047").valid

    def test_verifier_holding_public_key_cannot_forge(self):
        from src.county_node import CountyNode, verify_telemetry
        node = CountyNode("WA-047", "King County")
        reg = KeyRegistry()
        reg.register_signer(node.signer, owner="WA-047", role="county", valid_from=0)
        t = node.get_shard_telemetry()
        t["ballot_count"] = 10_000
        # A verifier only has the public key; re-signing with another key fails.
        impostor = DevelopmentSigner()
        from src.county_node import TELEMETRY_CONTEXT, telemetry_signable
        t["signature"] = impostor.sign(TELEMETRY_CONTEXT, telemetry_signable(t))
        assert not verify_telemetry(t, reg, expected_owner="WA-047").valid

    def test_tree_heads_are_publicly_verifiable(self):
        signer = DevelopmentSigner()
        log = MerkleLog("WA-047")
        log.append({"type": "cvr", "cvr": {"id": "1"}})
        head = log.sign_head(signer, timestamp=1_700_000_000)
        assert verify_signature(signer.public_key_raw, "sth", head.signed_payload(), head.signature)


# ---------------------------------------------------------------------------
# F6 — no real election workflow; fake open-data URLs with silent fallback
# ---------------------------------------------------------------------------

class TestF6ElectionWorkflow:
    def test_core_election_workflow_modules_exist(self):
        import eige.audit.reconciliation
        import eige.audit.rla
        import eige.audit.sampling
        import eige.ledger.custody
        import eige.model.election  # noqa: F401

    def test_legacy_open_data_has_no_fabricated_fallback(self):
        from eige.engine import open_election_data as oed
        assert not hasattr(oed, "_fallback_payload")
        assert "openelections.net" not in oed.OPEN_ELECTIONS_BASE

    def test_open_data_fails_loudly(self):
        from eige.data.open_data import OpenDataError, fetch

        def opener(url, timeout):
            raise OSError("network down")

        with pytest.raises(OpenDataError):
            fetch("https://raw.githubusercontent.com/openelections/x/y.csv", "openelections", opener=opener)


# ---------------------------------------------------------------------------
# F7 — overstated documentation and compliance claims
# ---------------------------------------------------------------------------

_DOCS = ("README.md", "COMPLIANCE.md", "FAQ.md", "EXPLAINER.md", "ARCHITECTURE.md", "SECURITY.md")
_FORBIDDEN = (
    re.compile(r"prevents? (ballot )?forgery", re.I),
    re.compile(r"mathematically impossible", re.I),
    re.compile(r"\b449 (tests|passing)", re.I),
)


class TestF7DocumentationClaims:
    @pytest.mark.parametrize("doc", _DOCS)
    def test_no_retracted_claims_in_primary_docs(self, doc):
        text = (PRODUCT / doc).read_text(encoding="utf-8")
        for pattern in _FORBIDDEN:
            for m in pattern.finditer(text):
                window = text[max(0, m.start() - 200): m.end() + 200].lower()
                assert "retract" in window or "not" in window or "no longer" in window, (
                    f"{doc}: unqualified claim {m.group(0)!r}"
                )

    def test_zero_knowledge_only_in_negations(self):
        for doc in _DOCS:
            text = (PRODUCT / doc).read_text(encoding="utf-8")
            for m in re.finditer(r"zero[- ]knowledge", text, re.I):
                window = text[max(0, m.start() - 160): m.end() + 160].lower()
                assert any(w in window for w in ("not", "retract", "no ", "never", "isn't", "without")), (
                    f"{doc}: affirmative zero-knowledge claim near {text[m.start()-60:m.end()+20]!r}"
                )

    def test_findings_and_retractions_published(self):
        findings = (PRODUCT / "RED_TEAM_FINDINGS.md").read_text(encoding="utf-8")
        retracted = (PRODUCT / "RETRACTED_CLAIMS.md").read_text(encoding="utf-8")
        for f in ("F1", "F2", "F3", "F4", "F5", "F6", "F7"):
            assert f in findings and f in retracted

    def test_oscal_mappings_carry_honest_status(self):
        from src.oscal_schema import IMPLEMENTATION_STATUSES, NIST_SP800_53_MAPPINGS
        for key, entry in NIST_SP800_53_MAPPINGS.items():
            assert entry["implementation_status"] in IMPLEMENTATION_STATUSES, key
            assert "zero-knowledge cryptographic proof" not in entry["description"]
