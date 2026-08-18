# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/state_mesh.py"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.county_node import CountyNode
from EIGE.src.state_mesh import StateMesh, StateLedgerEntry
from EIGE.src.metric_closure import ClosureStatus
from EIGE.src.constants import K_CS, PHI_0


def make_county_set(n: int = 3) -> list:
    """Create n county nodes with some pre-ingested ballots."""
    counties = []
    for i in range(n):
        node = CountyNode(f"WA-{100 + i:03d}", f"County {i}")
        for j in range(10):
            node.ingest_ballot([j % 3, (j + 1) % 2])
        counties.append(node)
    return counties


class TestStateMeshPollAllCounties:
    def setup_method(self):
        self.counties = make_county_set(3)
        self.mesh = StateMesh(self.counties, jurisdiction_id="WA-STATE")

    def test_poll_all_returns_list(self):
        states = self.mesh.poll_all_counties()
        assert isinstance(states, list)

    def test_poll_returns_one_entry_per_county(self):
        states = self.mesh.poll_all_counties()
        assert len(states) == 3

    def test_poll_state_has_phi_eff(self):
        states = self.mesh.poll_all_counties()
        for state in states:
            assert "phi_eff" in state
            assert abs(state["phi_eff"] - PHI_0) < 1e-10

    def test_poll_state_has_k_cs(self):
        states = self.mesh.poll_all_counties()
        for state in states:
            assert state["k_cs"] == K_CS

    def test_poll_state_has_ballot_count(self):
        states = self.mesh.poll_all_counties()
        for state in states:
            assert state["ballot_count"] == 10

    def test_county_count(self):
        assert self.mesh.county_count() == 3


class TestStateMeshBraidSync:
    def setup_method(self):
        self.counties = make_county_set(5)
        self.mesh = StateMesh(self.counties, jurisdiction_id="WA-STATE")

    def test_returns_state_ledger_entry(self):
        entry = self.mesh.compute_braid_sync()
        assert isinstance(entry, StateLedgerEntry)

    def test_entry_county_count_correct(self):
        entry = self.mesh.compute_braid_sync()
        assert entry.county_count == 5

    def test_all_counties_stable(self):
        entry = self.mesh.compute_braid_sync()
        assert entry.counties_stable == 5
        assert entry.counties_violated == 0

    def test_state_closure_is_stable(self):
        entry = self.mesh.compute_braid_sync()
        assert entry.state_closure_status == "STABLE"
        assert entry.is_clean()

    def test_aggregate_phi_near_phi_0(self):
        entry = self.mesh.compute_braid_sync()
        assert abs(entry.aggregate_phi - PHI_0) < 1e-10

    def test_aggregate_hash_is_sha512(self):
        entry = self.mesh.compute_braid_sync()
        assert len(entry.aggregate_state_hash) == 128  # SHA-512 hex

    def test_county_details_populated(self):
        entry = self.mesh.compute_braid_sync()
        assert len(entry.county_details) == 5
        for detail in entry.county_details:
            assert "county_id" in detail
            assert "closure_status" in detail

    def test_holon_zero_cert_generated(self):
        entry = self.mesh.compute_braid_sync()
        assert entry.holon_zero_cert is not None

    def test_holon_zero_cert_is_valid(self):
        from EIGE.src.holon_zero_cert import validate_holon_zero_cert
        entry = self.mesh.compute_braid_sync()
        assert validate_holon_zero_cert(entry.holon_zero_cert) is True

    def test_ledger_entries_accumulate(self):
        self.mesh.compute_braid_sync()
        self.mesh.compute_braid_sync()
        assert len(self.mesh.ledger_entries()) == 2

    def test_get_state_closure_returns_status(self):
        status = self.mesh.get_state_closure()
        assert isinstance(status, ClosureStatus)

    def test_get_holon_zero_cert_after_sync(self):
        self.mesh.compute_braid_sync()
        cert = self.mesh.get_holon_zero_cert()
        assert cert is not None

    def test_get_holon_zero_cert_before_sync_is_none(self):
        fresh_mesh = StateMesh(make_county_set(2))
        assert fresh_mesh.get_holon_zero_cert() is None

    def test_entry_as_dict(self):
        entry = self.mesh.compute_braid_sync()
        d = entry.as_dict()
        assert "timestamp" in d
        assert "county_count" in d
        assert "state_closure_status" in d

    def test_no_raw_ballot_data_in_entry(self):
        import json
        entry = self.mesh.compute_braid_sync()
        s = json.dumps(entry.as_dict())
        assert "selection_vector" not in s
        assert "voter_id" not in s

    def test_repr_format(self):
        r = repr(self.mesh)
        assert "StateMesh" in r
        assert "WA-STATE" in r
