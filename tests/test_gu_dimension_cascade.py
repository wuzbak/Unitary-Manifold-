# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 178 — GU Dimension Cascade."""
import pytest
from src.core.gu_dimension_cascade import (
    GU_OBSERVERSE_DIM, UM_MANIFOLD_DIM, N_W, K_CS, CHIMERIC_BUNDLE_RANK,
    gu_observerse_dimension, gu_chimeric_bundle_rank, frozen_gu_dof_by_s1_compactification,
    nw5_compactification_constraint, gu_to_um_metric_reduction, gu_fermion_content_check,
    gu_um_cascade_audit, pillar176_summary,
)

class TestConstants:
    def test_gu_dim(self): assert GU_OBSERVERSE_DIM == 14
    def test_um_dim(self): assert UM_MANIFOLD_DIM == 5
    def test_n_w(self): assert N_W == 5
    def test_chimeric_rank(self): assert CHIMERIC_BUNDLE_RANK == 7
    def test_frozen_count(self): assert GU_OBSERVERSE_DIM - UM_MANIFOLD_DIM == 9

class TestDimFunctions:
    def test_gu_returns_14(self): assert gu_observerse_dimension() == 14
    def test_chimeric_returns_7(self): assert gu_chimeric_bundle_rank() == 7
    def test_frozen_returns_9(self): assert frozen_gu_dof_by_s1_compactification() == 9
    def test_frozen_plus_remaining(self): assert frozen_gu_dof_by_s1_compactification() + UM_MANIFOLD_DIM == GU_OBSERVERSE_DIM

class TestCompactification:
    def setup_method(self): self.r = nw5_compactification_constraint()
    def test_frozen_9(self): assert self.r["frozen_dimensions"] == 9
    def test_remaining_5(self): assert self.r["remaining_dimensions"] == UM_MANIFOLD_DIM
    def test_status_verified(self): assert self.r["status"] == "VERIFIED"
    def test_mechanism_orbifold(self): assert "orbifold" in self.r["mechanism"].lower() or "S1/Z2" in self.r["mechanism"]

class TestMetricReduction:
    def setup_method(self): self.r = gu_to_um_metric_reduction()
    def test_gu_metric_dim(self): assert self.r["gu_metric_dim"] == GU_OBSERVERSE_DIM
    def test_um_metric_dim(self): assert self.r["um_metric_dim"] == UM_MANIFOLD_DIM
    def test_status_metric_reduced(self): assert self.r["status"] == "METRIC_REDUCED"

class TestFermionContent:
    def setup_method(self): self.r = gu_fermion_content_check()
    def test_gu_gen_3(self): assert self.r["gu_generations"] == 3
    def test_um_gen_3(self): assert self.r["um_generations"] == 3
    def test_agreement(self): assert self.r["agreement"] is True
    def test_status(self): assert self.r["status"] == "CONSISTENT"

class TestCascadeAudit:
    def setup_method(self): self.r = gu_um_cascade_audit()
    def test_um_as_gu_vacuum(self): assert self.r["um_as_gu_vacuum"] is True
    def test_status(self): assert self.r["status"] == "UM_AS_GU_VACUUM_SELECTION"
    def test_selection_mechanism(self): assert "n_w" in self.r["selection_mechanism"] or "winding" in self.r["selection_mechanism"]

class TestPillar176Summary:
    def test_returns_string(self): assert isinstance(pillar176_summary(), str)
    def test_contains_176(self): assert "176" in pillar176_summary()
    def test_contains_status(self): assert "UM_AS_GU_VACUUM_SELECTION" in pillar176_summary()
