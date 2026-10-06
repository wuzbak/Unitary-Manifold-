# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Hypothesis properties for EIGE v22 primitives and parsers."""

import json

import pytest
from hypothesis import given, settings, strategies as st

from eige.bundle import BundleError, read_bundle
from eige.canonical import CanonicalEncodingError, canonical_bytes
from eige.crypto import commitments as cm
from eige.crypto import merkle
from eige.data.open_data import OpenDataError, parse_openelections_csv
from eige.model.election import ModelError, parse_cvrs, parse_election, parse_manifest

ELECTION = parse_election({"id": "e", "name": "E", "date": "d", "jurisdiction": "J", "contests": [
    {"id": "c", "name": "Contest", "vote_for": 1, "candidates": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}]}
]})
json_scalars = st.one_of(st.none(), st.booleans(), st.integers(min_value=-10**6, max_value=10**6), st.text(max_size=20))
json_values = st.recursive(json_scalars, lambda children: st.lists(children, max_size=5) | st.dictionaries(st.text(max_size=10), children, max_size=5), max_leaves=20)


@settings(max_examples=80, deadline=None)
@given(st.lists(st.binary(max_size=32), min_size=1, max_size=25))
def test_inclusion_proofs_verify_for_random_trees_and_mutations_fail(leaves):
    hashes = [merkle.leaf_hash(x) for x in leaves]
    root = merkle.root_from_leaf_hashes(hashes)
    for index, digest in enumerate(hashes):
        proof = merkle.inclusion_proof(hashes, index)
        assert merkle.verify_inclusion(digest, index, len(hashes), proof, root)
        assert not merkle.verify_inclusion(merkle.leaf_hash(digest), index, len(hashes), proof, root)
        if proof:
            mutated = list(proof)
            mutated[0] = bytes([mutated[0][0] ^ 1]) + mutated[0][1:]
            assert not merkle.verify_inclusion(digest, index, len(hashes), mutated, root)


@settings(max_examples=80, deadline=None)
@given(st.lists(st.binary(max_size=24), min_size=2, max_size=25), st.data())
def test_consistency_proofs_verify_for_random_trees_and_mutations_fail(leaves, data):
    old_size = data.draw(st.integers(min_value=1, max_value=len(leaves) - 1))
    hashes = [merkle.leaf_hash(x) for x in leaves]
    old_root = merkle.root_from_leaf_hashes(hashes[:old_size])
    new_root = merkle.root_from_leaf_hashes(hashes)
    proof = merkle.consistency_proof(hashes, old_size)
    assert merkle.verify_consistency(old_size, len(hashes), old_root, new_root, proof)
    assert not merkle.verify_consistency(old_size, len(hashes), old_root, b"x" * 32, proof)
    if proof:
        mutated = list(proof)
        mutated[-1] = mutated[-1][:-1] + bytes([mutated[-1][-1] ^ 1])
        assert not merkle.verify_consistency(old_size, len(hashes), old_root, new_root, mutated)


@settings(max_examples=80, deadline=None)
@given(json_values)
def test_canonical_bytes_are_deterministic_for_json_values(value):
    assert canonical_bytes(value) == canonical_bytes(json.loads(canonical_bytes(value).decode("utf-8")))


@settings(max_examples=40, deadline=None)
@given(st.floats(allow_nan=False, allow_infinity=False))
def test_canonical_bytes_rejects_floats(value):
    with pytest.raises(CanonicalEncodingError):
        canonical_bytes({"float": value})


@settings(max_examples=100, deadline=None)
@given(st.lists(st.dictionaries(st.text(max_size=5), json_values, max_size=5), max_size=5))
def test_parse_cvrs_random_input_only_succeeds_or_raises_model_error(items):
    try:
        parse_cvrs(items, ELECTION)
    except ModelError:
        pass


@settings(max_examples=100, deadline=None)
@given(json_values)
def test_parse_manifest_random_input_only_succeeds_or_raises_model_error(value):
    try:
        parse_manifest(value)
    except ModelError:
        pass


@settings(max_examples=100, deadline=None)
@given(st.binary(max_size=200))
def test_parse_openelections_csv_random_bytes_only_succeeds_or_raises_open_data_error(data):
    try:
        parse_openelections_csv(data)
    except OpenDataError:
        pass


@settings(max_examples=30, deadline=None)
@given(st.text(max_size=20))
def test_bundle_reader_errors_are_documented_for_random_non_directories(name):
    if not name or "/" in name or "\x00" in name:
        return
    try:
        read_bundle("tests/.definitely-not-a-bundle-" + name)
    except (BundleError, OSError):
        pass


@settings(max_examples=80, deadline=None)
@given(st.integers(min_value=0, max_value=10_000), st.integers(min_value=0, max_value=10_000), st.integers(min_value=0, max_value=10_000), st.integers(min_value=0, max_value=10_000))
def test_commitment_homomorphism(value1, value2, rand1, rand2):
    c1, o1 = cm.commit_value(value1, rand1)
    c2, o2 = cm.commit_value(value2, rand2)
    assert cm.verify_opening(cm.combine([c1, c2]), o1 + o2)
