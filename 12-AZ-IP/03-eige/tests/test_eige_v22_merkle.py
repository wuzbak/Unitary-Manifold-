# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for RFC 6962 Merkle hashing and proofs."""

import hashlib

import pytest

from eige.crypto import merkle

LEAVES = [
    b"",
    b"\x00",
    b"\x10",
    b"\x20\x21",
    b"\x30\x31",
    b"\x40\x41\x42\x43",
    b"\x50\x51\x52\x53\x54\x55\x56\x57",
    b"\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f",
]
ROOTS = [
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d",
    "fac54203e7cc696cf0dfcb42c92a1d9dbaf70ad9e621f4bd8d98662f00e3c125",
    "aeb6bcfe274b70a14fb067a5e5578264db0fa9b51af5e0ba159158f329e06e77",
    "d37ee418976dd95753c1c73862b9398fa2a2cf9b4ff0fdfe8b30cd95209614b7",
    "4e3bbb1f7b478dcfe71fb631631519a3bca12c9aefca1612bfce4c13a86264d4",
    "76e67dadbcdf1e10e1b74ddc608abd2f98dfb16fbce75277b5232a127f2087ef",
    "ddb89be403809e325750d3d263cd78929c2942b7942a34b77e122c9594a74c8c",
    "5dc9da79a70659a9ad559cb701ded9a2ab9d823aad2f4960cfe370eff4604328",
]


def test_leaf_node_and_empty_hashing_match_rfc6962_prefixes():
    assert merkle.leaf_hash(b"abc") == hashlib.sha256(b"\x00abc").digest()
    assert merkle.node_hash(b"a" * 32, b"b" * 32) == hashlib.sha256(b"\x01" + b"a" * 32 + b"b" * 32).digest()
    assert merkle.empty_root().hex() == ROOTS[0]


@pytest.mark.parametrize("size,root_hex", list(enumerate(ROOTS)))
def test_certificate_transparency_reference_roots(size, root_hex):
    assert merkle.merkle_root(LEAVES[:size]).hex() == root_hex


def test_inclusion_proofs_verify_for_all_indices_up_to_twenty():
    leaves = [f"leaf-{i}".encode() for i in range(20)]
    hashes = [merkle.leaf_hash(x) for x in leaves]
    for size in range(1, len(leaves) + 1):
        root = merkle.root_from_leaf_hashes(hashes[:size])
        for index in range(size):
            proof = merkle.inclusion_proof(hashes[:size], index)
            assert merkle.verify_inclusion(hashes[index], index, size, proof, root)
            assert not merkle.verify_inclusion(merkle.leaf_hash(b"evil"), index, size, proof, root)
            if proof:
                tampered = list(proof)
                tampered[0] = bytes([tampered[0][0] ^ 1]) + tampered[0][1:]
                assert not merkle.verify_inclusion(hashes[index], index, size, tampered, root)


def test_consistency_proofs_verify_for_all_sizes_up_to_twenty():
    leaves = [f"leaf-{i}".encode() for i in range(20)]
    hashes = [merkle.leaf_hash(x) for x in leaves]
    for new_size in range(1, len(leaves) + 1):
        new_root = merkle.root_from_leaf_hashes(hashes[:new_size])
        for old_size in range(0, new_size + 1):
            old_root = merkle.root_from_leaf_hashes(hashes[:old_size])
            proof = merkle.consistency_proof(hashes[:new_size], old_size)
            assert merkle.verify_consistency(old_size, new_size, old_root, new_root, proof)
            if proof:
                tampered = list(proof)
                tampered[-1] = tampered[-1][:-1] + bytes([tampered[-1][-1] ^ 1])
                assert not merkle.verify_consistency(old_size, new_size, old_root, new_root, tampered)


def test_bad_proof_requests_and_malformed_proofs_are_rejected():
    hashes = [merkle.leaf_hash(b"x")]
    with pytest.raises(merkle.ProofError):
        merkle.inclusion_proof(hashes, 1)
    with pytest.raises(merkle.ProofError):
        merkle.consistency_proof(hashes, 2)
    assert not merkle.verify_inclusion(hashes[0], 1, 1, [], hashes[0])
    assert not merkle.verify_inclusion(hashes[0], 0, 1, [b"short"], hashes[0])
    assert not merkle.verify_consistency(2, 1, hashes[0], hashes[0], [])
    assert not merkle.verify_consistency(0, 1, b"wrong", hashes[0], [])
