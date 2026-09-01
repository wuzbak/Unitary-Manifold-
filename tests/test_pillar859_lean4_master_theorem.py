# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 859 — Lean4 master theorem metadata."""
from __future__ import annotations

from pathlib import Path

from src.core.pillar859_lean4_master_theorem import (
    LEAN4_FILE,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    N_MASTER_THEOREMS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    lean4_master_theorem_summary,
)


class TestPillar859Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 859
    def test_gate(self): assert PILLAR_GATE == "LEAN4_MASTER_THEOREM_11D_TO_4D"
    def test_lean4_file(self): assert LEAN4_FILE == "MasterTheoremDimensionalChain.lean"
    def test_master_theorem_count(self): assert N_MASTER_THEOREMS == 40
    def test_lean4_theorem_count(self): assert LEAN4_THEOREM_COUNT == 40
    def test_lean4_total(self): assert LEAN4_TOTAL_AFTER == 2186


class TestPillar859LeanFile:
    def test_file_exists(self):
        path = Path(lean4_master_theorem_summary()["lean4_path"])
        assert path.exists()

    def test_namespace_present(self):
        assert lean4_master_theorem_summary()["namespace_present"] is True

    def test_master_theorem_present(self):
        assert lean4_master_theorem_summary()["master_theorem_present"] is True

    def test_no_sorry(self):
        assert lean4_master_theorem_summary()["contains_sorry"] is False

    def test_architecture_limit_comment_present(self):
        assert lean4_master_theorem_summary()["architecture_limit_comment_present"] is True


class TestPillar859Summary:
    def test_returns_dict(self): assert isinstance(lean4_master_theorem_summary(), dict)
    def test_summary_gate(self): assert lean4_master_theorem_summary()["gate"] == PILLAR_GATE
    def test_summary_count(self): assert lean4_master_theorem_summary()["n_master_theorems"] == 40
