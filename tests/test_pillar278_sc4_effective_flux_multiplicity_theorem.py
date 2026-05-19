# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 278 — SC4 Effective-Flux Multiplicity Theorem."""
from __future__ import annotations

import pytest

from src.core.p28_lambda_10d_closure import DUAL_FLUX_MULTIPLICITY as P28_DUAL_FLUX_MULTIPLICITY
from src.core.pillar278_sc4_effective_flux_multiplicity_theorem import (
    ADJACENCY_TRACK_LABEL,
    CANONICAL_N_FLUX,
    DUAL_FLUX_MULTIPLICITY,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    effective_flux_count,
    effective_multiplicity,
    multiplicity_theorem_certificate,
    multiplicity_theorem_report,
    orientifold_antiinvariant_count,
    orientifold_invariant_count,
    separation_guard,
)


def test_identity_and_separation():
    assert PILLAR_NUMBER == 278
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert separation_guard()["promotes_scan_to_theorem"] is True


def test_dual_flux_multiplicity_matches_p28():
    assert DUAL_FLUX_MULTIPLICITY == P28_DUAL_FLUX_MULTIPLICITY


def test_canonical_n_flux_is_37():
    assert CANONICAL_N_FLUX == 37


def test_orientifold_counts_input_validation():
    with pytest.raises(ValueError):
        orientifold_invariant_count(-1)
    with pytest.raises(ValueError):
        orientifold_antiinvariant_count(-1)
    with pytest.raises(ValueError):
        effective_flux_count(-1)


def test_effective_multiplicity_is_exactly_two():
    assert effective_multiplicity() == 2


def test_effective_flux_count_canonical():
    # 2 · 37 = 74 = K_CS, the canonical UM braid resonance
    assert effective_flux_count() == 74


def test_effective_flux_count_arbitrary():
    for n in (0, 1, 10, 51, 100):
        assert effective_flux_count(n) == 2 * n


def test_invariant_and_antiinvariant_counts_match():
    # σ canonical action: equal-dimensional ±1 eigenspaces by symmetry
    for n in (0, 5, 37, 100):
        assert orientifold_invariant_count(n) == orientifold_antiinvariant_count(n) == n


def test_certificate_consistency_canonical():
    c = multiplicity_theorem_certificate()
    assert c["n_flux"] == 37
    assert c["orientifold_invariant_count"] == 37
    assert c["orientifold_antiinvariant_count"] == 37
    assert c["RR_NSNS_independence_degree"] == 2
    assert c["derived_effective_count"] == 74
    assert c["n_eff_canonical_formula"] == 74
    assert c["theorem_consistency_passed"] is True
    assert c["matches_existing_DUAL_FLUX_MULTIPLICITY"] is True


def test_certificate_consistency_across_grid():
    for n in (0, 10, 20, 37, 51, 74, 100, 200):
        c = multiplicity_theorem_certificate(n_flux=n)
        assert c["theorem_consistency_passed"] is True
        assert c["derived_effective_count"] == 2 * n


def test_multiplicity_theorem_report_structure():
    r = multiplicity_theorem_report()
    assert r["acceptance_gate_passed"] is True
    assert r["grid_all_consistent"] is True
    assert "THEOREM_278_1" in r["theorem_label"]
    assert "RR (F₃)" in r["theorem_statement"]
    nm = r["named_modules"]
    assert "flux_landscape_extended_scan" in nm["scan_being_promoted"]
    assert "DUAL_FLUX_MULTIPLICITY" in nm["constant_being_certified"]


def test_no_hardgate_drift():
    r = multiplicity_theorem_report()
    g = r["separation_guard"]
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
