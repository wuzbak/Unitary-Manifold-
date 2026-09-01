# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 882 — unified Lean4 CKM/PMNS derivation."""
from __future__ import annotations

from src.core.pillar882_lean4_ckm_pmns_unified import (
    LEAN4_FILE,
    LEAN4_NAMESPACE,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    LEPTON_SECTOR_DIMENSION,
    N_SECTORS,
    N_UNIFIED_THEOREMS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    QUARK_SECTOR_DIMENSION,
    REMAINING_OPEN,
    THEOREM_COUNT_MATCHES,
    lean4_ckm_pmns_unified_summary,
)


class TestPillar882Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 882
    def test_gate(self): assert PILLAR_GATE == "LEAN4_CKM_PMNS_UNIFIED_THEOREM"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 50
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2606
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2656
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_lean4_file(self): assert LEAN4_FILE == "CKMPMNSUnifiedDerivation.lean"
    def test_namespace(self): assert "UnitaryManifold" in LEAN4_NAMESPACE


class TestPillar882Sectors:
    def test_quark_sector_dimension(self): assert QUARK_SECTOR_DIMENSION == 7
    def test_lepton_sector_dimension(self): assert LEPTON_SECTOR_DIMENSION == 9
    def test_sector_count(self): assert N_SECTORS == 2
    def test_lepton_above_quark(self): assert LEPTON_SECTOR_DIMENSION > QUARK_SECTOR_DIMENSION
    def test_sectors_are_odd_dimensional(self):
        assert QUARK_SECTOR_DIMENSION % 2 == 1 and LEPTON_SECTOR_DIMENSION % 2 == 1
    def test_dimension_gap_is_two(self):
        assert LEPTON_SECTOR_DIMENSION - QUARK_SECTOR_DIMENSION == 2


class TestPillar882Lean4File:
    def test_file_exists(self): assert lean4_ckm_pmns_unified_summary()["lean4_path"]
    def test_theorem_count_matches(self): assert THEOREM_COUNT_MATCHES is True
    def test_counted_theorems(self): assert N_UNIFIED_THEOREMS == 50
    def test_count_equals_budget(self): assert N_UNIFIED_THEOREMS == LEAN4_THEOREM_COUNT
    def test_master_theorem_present(self):
        assert lean4_ckm_pmns_unified_summary()["master_theorem_present"] is True
    def test_namespace_present(self):
        assert lean4_ckm_pmns_unified_summary()["namespace_present"] is True
    def test_architecture_limit_comment_present(self):
        assert lean4_ckm_pmns_unified_summary()["architecture_limit_comment_present"] is True


class TestPillar882Summary:
    def test_summary_gate(self): assert lean4_ckm_pmns_unified_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert lean4_ckm_pmns_unified_summary()["pillar"] == 882
    def test_summary_lean4_total(self):
        assert lean4_ckm_pmns_unified_summary()["lean4_total_after"] == 2656
    def test_summary_file(self): assert lean4_ckm_pmns_unified_summary()["lean4_file"] == LEAN4_FILE
    def test_summary_theorem_count(self):
        assert lean4_ckm_pmns_unified_summary()["n_unified_theorems"] == 50
    def test_summary_sectors(self): assert lean4_ckm_pmns_unified_summary()["n_sectors"] == 2
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_remaining_open_labelled(self):
        assert all("OPEN" in item or "LIMIT" in item for item in REMAINING_OPEN)
    def test_epistemic_status_no_closure_claim(self):
        assert "PROVEN" not in lean4_ckm_pmns_unified_summary()["epistemic_status"].upper()
    def test_epistemic_status_present(self):
        assert len(lean4_ckm_pmns_unified_summary()["epistemic_status"]) > 20
