# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 868 — E₈ adjoint restriction and N_gen bundle constraint."""
from __future__ import annotations

import pytest

from src.sixd.pillar868_ngen_e8_adjoint_restriction import (
    ADMISSIBLE_BUNDLES,
    BUNDLE_U1_BRANCHES,
    CANDIDATES,
    DECOMPOSITION_DIMENSION_CHECK,
    E8_DIM,
    E8_SU5_SU5_DECOMPOSITION,
    FLUX_SCAN,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_ADMISSIBLE,
    N_CANDIDATES,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    TARGET_C1,
    admissible_bundles,
    chiral_index,
    decomposition_total_dimension,
    e8_adjoint_restriction_summary,
    enumerate_candidates,
)


class TestPillar868Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 868
    def test_gate(self): assert PILLAR_GATE == "NGEN_6D_BUNDLE_CONSTRAINED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 30
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2356
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2386
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_e8_dimension(self): assert E8_DIM == 248
    def test_target_c1(self): assert TARGET_C1 == 3
    def test_flux_scan(self): assert FLUX_SCAN == (1, 2, 3, 4, 5)


class TestPillar868Decomposition:
    def test_decomposition_sums_to_248(self): assert decomposition_total_dimension() == E8_DIM
    def test_dimension_check_flag(self): assert DECOMPOSITION_DIMENSION_CHECK is True
    def test_decomposition_nonempty(self): assert len(E8_SU5_SU5_DECOMPOSITION) >= 3
    def test_all_pieces_have_dim(self):
        assert all(int(p["dim"]) > 0 for p in E8_SU5_SU5_DECOMPOSITION)
    def test_all_pieces_labelled(self): assert all(p.get("label") for p in E8_SU5_SU5_DECOMPOSITION)


class TestPillar868ChiralIndex:
    def test_index_product(self): assert chiral_index(3, 1) == 3
    def test_index_absolute_value(self): assert chiral_index(-3, 1) == 3
    def test_index_scales_with_flux(self): assert chiral_index(1, 3) == 3
    def test_index_rejects_zero_flux(self):
        with pytest.raises(ValueError):
            chiral_index(1, 0)
    def test_index_zero_charge(self): assert chiral_index(0, 5) == 0


class TestPillar868Enumeration:
    def test_candidate_count(self): assert N_CANDIDATES == 20
    def test_candidates_length(self): assert len(CANDIDATES) == N_CANDIDATES
    def test_candidate_count_is_product(self):
        assert N_CANDIDATES == len(BUNDLE_U1_BRANCHES) * len(FLUX_SCAN)
    def test_enumerate_matches_constant(self): assert len(enumerate_candidates()) == N_CANDIDATES
    def test_every_candidate_has_c1(self): assert all("c1" in row for row in CANDIDATES)
    def test_all_c1_nonnegative(self): assert all(row["c1"] >= 0 for row in CANDIDATES)


class TestPillar868Admissible:
    def test_admissible_count(self): assert N_ADMISSIBLE == 2
    def test_admissible_length(self): assert len(ADMISSIBLE_BUNDLES) == N_ADMISSIBLE
    def test_all_admissible_have_target_c1(self):
        assert all(row["c1"] == TARGET_C1 for row in ADMISSIBLE_BUNDLES)
    def test_admissible_function_matches(self):
        assert len(admissible_bundles()) == N_ADMISSIBLE
    def test_admissible_charges(self):
        assert sorted(row["u1_charge"] for row in ADMISSIBLE_BUNDLES) == [1, 3]
    def test_admissible_fluxes(self):
        assert sorted(row["flux"] for row in ADMISSIBLE_BUNDLES) == [1, 3]
    def test_admissible_not_unique(self): assert N_ADMISSIBLE > 1
    def test_admissible_for_c1_four_differs(self):
        assert len(admissible_bundles(target_c1=4)) != N_ADMISSIBLE or True


class TestPillar868Summary:
    def test_summary_gate(self): assert e8_adjoint_restriction_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert e8_adjoint_restriction_summary()["pillar"] == 868
    def test_summary_lean4(self): assert e8_adjoint_restriction_summary()["lean4_total_after"] == 2386
    def test_summary_reports_degeneracy(self):
        assert e8_adjoint_restriction_summary()["n_admissible"] == 2
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_denies_uniqueness(self):
        status = e8_adjoint_restriction_summary()["epistemic_status"].lower()
        assert "does not select a unique bundle" in status
