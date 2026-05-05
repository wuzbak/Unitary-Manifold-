# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 176 — E8 Root System Embedding."""
import math
import pytest
from src.core.e8_root_embedding import (
    E8_RANK, E8_DIMENSION, E8_ROOTS, SM_GENERATORS, SU5_GENERATORS, N_W, K_CS,
    e8_subgroup_chain, um_gauge_generator_count, e8_root_coverage_fraction,
    nw_selects_su5_maximal_subgroup, kk_tower_e8_map, e8_compatibility_check,
    e8_root_embedding_audit, pillar174_summary,
)

class TestConstants:
    def test_e8_rank(self): assert E8_RANK == 8
    def test_e8_dimension(self): assert E8_DIMENSION == 248
    def test_e8_roots(self): assert E8_ROOTS == 240
    def test_sm_generators(self): assert SM_GENERATORS == 12
    def test_su5_generators(self): assert SU5_GENERATORS == 24
    def test_n_w(self): assert N_W == 5
    def test_k_cs(self): assert K_CS == 74
    def test_sm_generators_decomposition(self): assert SM_GENERATORS == 8+3+1
    def test_e8_roots_equals_dimension_minus_rank(self): assert E8_ROOTS == E8_DIMENSION - E8_RANK

class TestSubgroupChain:
    def setup_method(self): self.r = e8_subgroup_chain()
    def test_returns_dict(self): assert isinstance(self.r, dict)
    def test_has_chain_key(self): assert "chain" in self.r
    def test_has_steps_key(self): assert "steps" in self.r
    def test_chain_is_list(self): assert isinstance(self.r["chain"], list)
    def test_chain_length(self): assert len(self.r["chain"]) == 4
    def test_chain_starts_with_e8(self): assert self.r["chain"][0] == "E8"
    def test_chain_ends_with_sm(self):
        last = self.r["chain"][-1]
        assert "SU(3)" in last and "SU(2)" in last and "U(1)" in last
    def test_steps_length(self): assert len(self.r["steps"]) == 3
    def test_kawamura_mentioned(self):
        mechs = " ".join(s["mechanism"] for s in self.r["steps"])
        assert "Kawamura" in mechs or "orbifold" in mechs.lower()

class TestGaugeGeneratorCount:
    def test_returns_12(self): assert um_gauge_generator_count() == 12
    def test_returns_int(self): assert isinstance(um_gauge_generator_count(), int)

class TestRootCoverageFraction:
    def test_returns_float(self): assert isinstance(e8_root_coverage_fraction(), float)
    def test_value(self): assert e8_root_coverage_fraction() == pytest.approx(0.05, rel=1e-9)
    def test_positive(self): assert e8_root_coverage_fraction() > 0
    def test_less_than_1(self): assert e8_root_coverage_fraction() < 1.0

class TestNwSelectsSU5:
    def test_returns_true(self): assert nw_selects_su5_maximal_subgroup() is True

class TestKKTowerMap:
    def setup_method(self): self.r = kk_tower_e8_map()
    def test_has_5_levels(self): assert len(self.r) == N_W
    def test_level_1_subgroup(self):
        assert "SU(3)" in self.r[1]["subgroup"] and "SU(2)" in self.r[1]["subgroup"]
    def test_level_1_generators(self): assert self.r[1]["generators"] == SM_GENERATORS
    def test_higher_levels_have_generators(self):
        for n in range(2, N_W+1): assert self.r[n]["generators"] == SM_GENERATORS

class TestCompatibilityCheck:
    def setup_method(self): self.r = e8_compatibility_check()
    def test_compatible_true(self): assert self.r["compatible"] is True
    def test_status_compatible(self): assert self.r["status"] == "COMPATIBLE"
    def test_leptoquarks_in_extra_particles(self): assert "leptoquarks" in self.r["extra_particles_predicted_by_e8_not_um"]
    def test_mirror_fermions(self): assert "mirror fermions" in self.r["extra_particles_predicted_by_e8_not_um"]

class TestEmbeddingAudit:
    def setup_method(self): self.r = e8_root_embedding_audit()
    def test_e8_rank(self): assert self.r["e8_rank"] == E8_RANK
    def test_root_coverage_fraction(self): assert self.r["root_coverage_fraction"] == pytest.approx(0.05, rel=1e-9)
    def test_nw_selects_su5(self): assert self.r["nw_selects_su5"] is True
    def test_status(self): assert self.r["status"] == "COMPATIBLE"

class TestPillar174Summary:
    def test_returns_string(self): assert isinstance(pillar174_summary(), str)
    def test_contains_174(self): assert "174" in pillar174_summary()
    def test_contains_e8(self): assert "E8" in pillar174_summary()
    def test_contains_status(self): assert "COMPATIBLE" in pillar174_summary()
