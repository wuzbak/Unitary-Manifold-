# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
Tests for EIGE/src/rust_bridge.py — RustBallotBridge transparent proxy.
"""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from EIGE.src.rust_bridge import RustBallotBridge


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def fresh_bridge(use_rust: bool = False) -> RustBallotBridge:
    return RustBallotBridge(county_id=1, num_shards=8, use_rust=use_rust)


# ---------------------------------------------------------------------------
# 1. Instantiation
# ---------------------------------------------------------------------------

class TestRustBridgeInstantiation:
    def test_creates_with_defaults(self):
        b = RustBallotBridge(county_id=1)
        assert b is not None

    def test_creates_with_all_args(self):
        b = RustBallotBridge(county_id=7, num_shards=4, use_rust=False)
        assert b is not None

    def test_use_rust_false_falls_back_to_python(self):
        b = fresh_bridge(use_rust=False)
        assert b._use_rust is False

    def test_try_import_rust_returns_bool(self):
        result = RustBallotBridge.try_import_rust()
        assert isinstance(result, bool)

    def test_rust_not_available_in_test_environment(self):
        # The compiled eige_rust_core module is never available in CI
        assert RustBallotBridge.try_import_rust() is False

    def test_rust_availability_cached(self):
        r1 = RustBallotBridge.try_import_rust()
        r2 = RustBallotBridge.try_import_rust()
        assert r1 == r2


# ---------------------------------------------------------------------------
# 2. update() — normal operation
# ---------------------------------------------------------------------------

class TestRustBridgeUpdate:
    def test_update_returns_state_int(self):
        b = fresh_bridge()
        state = b.update(42)
        assert isinstance(state, int)

    def test_update_changes_state(self):
        b = fresh_bridge()
        s1 = b.update(1)
        s2 = b.update(2)
        assert s1 != s2

    def test_update_non_commutative(self):
        b1 = fresh_bridge()
        b2 = fresh_bridge()
        b1.update(1)
        b1.update(2)
        b2.update(2)
        b2.update(1)
        assert b1.state != b2.state

    def test_state_property_after_update(self):
        b = fresh_bridge()
        returned = b.update(99)
        assert returned == b.state

    def test_multiple_updates_deterministic(self):
        b1 = fresh_bridge()
        b2 = fresh_bridge()
        for v in [10, 20, 30, 40]:
            b1.update(v)
            b2.update(v)
        assert b1.state == b2.state


# ---------------------------------------------------------------------------
# 3. reset()
# ---------------------------------------------------------------------------

class TestRustBridgeReset:
    def test_reset_returns_initial_state(self):
        b = fresh_bridge()
        b.update(5)
        initial = b.reset()
        assert isinstance(initial, int)

    def test_state_after_reset_matches_fresh_bridge(self):
        b = fresh_bridge()
        b.update(10)
        b.update(20)
        b.reset()
        b2 = fresh_bridge()
        assert b.state == b2.state

    def test_reset_then_update_gives_same_result(self):
        b = fresh_bridge()
        b.update(7)
        b.reset()
        s_after_reset = b.update(7)

        b2 = fresh_bridge()
        s_fresh = b2.update(7)
        assert s_after_reset == s_fresh


# ---------------------------------------------------------------------------
# 4. checkpoint_all() / checkpoint_manifests()
# ---------------------------------------------------------------------------

class TestRustBridgeCheckpoints:
    def test_checkpoint_all_returns_list(self):
        b = fresh_bridge()
        b.update(1)
        result = b.checkpoint_all()
        assert isinstance(result, list)

    def test_checkpoint_manifests_returns_list(self):
        b = fresh_bridge()
        b.update(1)
        manifests = b.checkpoint_manifests()
        assert isinstance(manifests, list)

    def test_checkpoint_manifests_length_equals_num_shards(self):
        b = fresh_bridge()
        b.update(1)
        manifests = b.checkpoint_manifests()
        assert len(manifests) == 8


# ---------------------------------------------------------------------------
# 5. reconstruct_check()
# ---------------------------------------------------------------------------

class TestRustBridgeReconstruct:
    def test_reconstruct_check_returns_tuple(self):
        b = fresh_bridge()
        for v in range(5):
            b.update(v)
        result = b.reconstruct_check()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_reconstruct_check_success_bool(self):
        b = fresh_bridge()
        for v in range(5):
            b.update(v)
        success, _, _ = b.reconstruct_check()
        assert isinstance(success, bool)

    def test_reconstruct_check_hash_when_successful(self):
        b = fresh_bridge()
        for v in range(10):
            b.update(v)
        success, h, _ = b.reconstruct_check()
        if success:
            assert isinstance(h, int)


# ---------------------------------------------------------------------------
# 6. sha512_hexdigest proxy
# ---------------------------------------------------------------------------

class TestRustBridgeDigest:
    def test_sha512_hexdigest_returns_128_char_hex(self):
        b = fresh_bridge()
        b.update(1)
        digest = b.sha512_hexdigest()
        assert isinstance(digest, str)
        assert len(digest) == 128
        assert all(c in "0123456789abcdef" for c in digest)

    def test_digest_changes_after_update(self):
        b = fresh_bridge()
        d1 = b.sha512_hexdigest()
        b.update(1)
        d2 = b.sha512_hexdigest()
        assert d1 != d2
