# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Merkle logs, custody attestations, and bulletin boards."""

import pytest

from eige.crypto import merkle
from eige.crypto.signing import DevelopmentSigner, KeyRegistry
from eige.ledger.bulletin import BulletinBoard, BulletinError, EquivocationDetected, Witness
from eige.ledger.custody import CustodyError, CustodyLedger, custody_event, sign_off
from eige.ledger.log import MerkleLog, sign_tree_head


def registry_with(*items):
    reg = KeyRegistry()
    for signer, owner, role in items:
        reg.register_signer(signer, owner, role, 0)
    return reg


def test_merkle_log_append_root_proofs_and_signed_head():
    signer = DevelopmentSigner(b"l" * 32)
    reg = registry_with((signer, "county", "county-log"))
    log = MerkleLog("county")
    for i in range(5):
        assert log.append({"type": "cvr", "i": i}) == i
    root = log.root()
    head = log.sign_head(signer, 100)
    assert head.tree_size == 5 and head.root_hash == root.hex()
    assert head.verify(reg, expected_owner="county").valid
    hashes = log.leaf_hashes()
    for i, digest in enumerate(hashes):
        assert merkle.verify_inclusion(digest, i, log.size, log.inclusion_proof(i), root)
    assert merkle.verify_consistency(2, 5, log.root(2), root, log.consistency_proof(2))


def test_custody_two_person_rule_and_role_enforcement():
    a, b, observer = DevelopmentSigner(b"a" * 32), DevelopmentSigner(b"b" * 32), DevelopmentSigner(b"o" * 32)
    reg = registry_with((a, "alice", "official"), (b, "bob", "official"), (observer, "obs", "witness"))
    ledger = CustodyLedger(MerkleLog("custody"), reg)
    body = custody_event("seal_applied", "box1", "warehouse", 10, seal_id="S1")
    with pytest.raises(CustodyError):
        ledger.record(body, [sign_off(body, "alice", a), sign_off(body, "alice", a)])
    with pytest.raises(CustodyError):
        ledger.record(body, [sign_off(body, "alice", a), sign_off(body, "obs", observer)])
    assert ledger.record(body, [sign_off(body, "alice", a), sign_off(body, "bob", b)]) == 0
    with pytest.raises(CustodyError):
        custody_event("transfer", "box1", "warehouse", 11, from_party="A")


def test_verify_container_reports_broken_seals_and_transfer_gaps():
    a, b = DevelopmentSigner(b"a" * 32), DevelopmentSigner(b"b" * 32)
    reg = registry_with((a, "alice", "official"), (b, "bob", "official"))
    ledger = CustodyLedger(MerkleLog("custody"), reg)
    def record(body):
        ledger.record(body, [sign_off(body, "alice", a), sign_off(body, "bob", b)])
    record(custody_event("seal_applied", "box1", "warehouse", 10, seal_id="S1"))
    record(custody_event("seal_verified", "box1", "warehouse", 11, seal_id="WRONG"))
    record(custody_event("container_opened", "box1", "warehouse", 12, reason="audit"))
    record(custody_event("seal_broken", "box1", "warehouse", 13, seal_id="S1", reason="reseal"))
    record(custody_event("transfer", "box1", "warehouse", 14, from_party="someone_else", to_party="tabulation"))
    issues = ledger.verify_container("box1", initial_custodian="warehouse")
    assert any("does not match" in issue for issue in issues)
    assert any("opened without recording seal" in issue for issue in issues)
    assert any("transfer from someone_else" in issue for issue in issues)
    assert any("without an intact seal" in issue for issue in issues)


def test_bulletin_board_consistency_witness_threshold_and_gossip():
    county = DevelopmentSigner(b"c" * 32)
    w1, w2 = DevelopmentSigner(b"1" * 32), DevelopmentSigner(b"2" * 32)
    reg = registry_with((county, "county", "county-log"), (w1, "w1", "witness"), (w2, "w2", "witness"))
    log = MerkleLog("county")
    for i in range(3):
        log.append({"type": "record", "i": i})
    head1 = sign_tree_head(county, "county", 2, log.root(2), 10)
    head2 = sign_tree_head(county, "county", 3, log.root(3), 20)
    wit1, wit2 = Witness("w1", w1, reg), Witness("w2", w2, reg)
    cosig1 = wit1.cosign(head1)
    cosig2 = wit2.cosign(head1)
    board = BulletinBoard(reg, witness_threshold=2)
    with pytest.raises(BulletinError):
        board.publish(head1, cosignatures=[cosig1])
    board.publish(head1, cosignatures=[cosig1, cosig2])
    cosig1b = wit1.cosign(head2, log.consistency_proof(2))
    cosig2b = wit2.cosign(head2, log.consistency_proof(2))
    board.publish(head2, consistency_proof=log.consistency_proof(2), cosignatures=[cosig1b, cosig2b])
    assert board.latest("county") == head2
    assert len(board.cosignatures(head2)) == 2

    split = sign_tree_head(county, "county", 3, b"x" * 32, 30)
    gossip = board.check_gossip([split])
    assert gossip and gossip[0].reason.startswith("split view")
    board.witness_threshold = 0
    with pytest.raises(EquivocationDetected) as exc:
        board.publish(split, consistency_proof=[])
    assert exc.value.evidence.as_dict()["format"] == "eige.equivocation_evidence.v1"
