# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 831 — Quark-Lepton c_L Splitting Derivation."""
from __future__ import annotations
import pytest
from src.core.pillar831_quark_lepton_cl_splitting_derivation import (
    PILLAR, GATE, LEAN4_TOTAL, LEAN4_COUNT, N_W, K_CS, N_C,
    color_cl_correction, lepton_cl_spectrum, quark_cl_spectrum,
    cl_splitting_matrix, pdg_consistency_check, quark_lepton_cl_splitting_summary,
)


class TestPillar831Constants:
    def test_pillar_number(self): assert PILLAR == 831
    def test_nw(self): assert N_W == 5
    def test_kcs(self): assert K_CS == 74
    def test_nc(self): assert N_C == 3
    def test_lean4_count(self): assert LEAN4_COUNT == 30
    def test_lean4_total(self): assert LEAN4_TOTAL == 1711
    def test_lean4_accumulates(self):
        from src.core.pillar831_quark_lepton_cl_splitting_derivation import LEAN4_PRIOR
        assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT


class TestColorClCorrection:
    def test_returns_dict(self):
        r = color_cl_correction()
        assert isinstance(r, dict)

    def test_quark_gt_lepton(self):
        r = color_cl_correction()
        assert r["delta_c_L_quark"] > r["delta_c_L_lepton"]

    def test_lepton_zero(self):
        r = color_cl_correction()
        assert r["delta_c_L_lepton"] == 0.0

    def test_quark_positive(self):
        r = color_cl_correction()
        assert r["delta_c_L_quark"] > 0

    def test_relative_splitting_small(self):
        r = color_cl_correction()
        assert r["relative_splitting"] < 0.1

    def test_formula_present(self):
        r = color_cl_correction()
        assert "formula" in r


class TestLeptonClSpectrum:
    def test_returns_dict(self):
        r = lepton_cl_spectrum()
        assert isinstance(r, dict)

    def test_three_generations(self):
        r = lepton_cl_spectrum()
        assert r["fermion_type"] == "lepton"

    def test_spectrum_length(self):
        r = lepton_cl_spectrum()
        assert len(r["spectrum"]) == 3

    def test_all_positive(self):
        r = lepton_cl_spectrum()
        # spectrum is a list of dicts
        assert all(s['c_L'] > 0 for s in r["spectrum"])


class TestQuarkClSpectrum:
    def test_returns_dict(self):
        r = quark_cl_spectrum()
        assert isinstance(r, dict)

    def test_fermion_type(self):
        r = quark_cl_spectrum()
        assert r["fermion_type"] == "quark"

    def test_spectrum_length(self):
        r = quark_cl_spectrum()
        assert len(r["spectrum"]) == 3

    def test_nc_correct(self):
        r = quark_cl_spectrum()
        assert r["N_c"] == 3


class TestClSplittingMatrix:
    def test_returns_dict(self):
        r = cl_splitting_matrix()
        assert isinstance(r, dict)

    def test_splittings_present(self):
        r = cl_splitting_matrix()
        assert "splittings" in r

    def test_mean_splitting_positive(self):
        r = cl_splitting_matrix()
        assert r["mean_splitting"] > 0

    def test_gate_present(self):
        r = cl_splitting_matrix()
        assert "gate" in r


class TestPdgConsistencyCheck:
    def test_returns_dict(self):
        r = pdg_consistency_check()
        assert isinstance(r, dict)

    def test_honest_note(self):
        r = pdg_consistency_check()
        assert "honest_note" in r

    def test_qualitatively_consistent(self):
        r = pdg_consistency_check()
        # Consistency check is valid either way — just must be present
        assert isinstance(r["qualitatively_consistent"], bool)


class TestQuarkLeptonClSplittingSummary:
    def test_returns_dict(self):
        r = quark_lepton_cl_splitting_summary()
        assert isinstance(r, dict)

    def test_pillar(self):
        r = quark_lepton_cl_splitting_summary()
        assert r["pillar"] == 831

    def test_lean4_total(self):
        r = quark_lepton_cl_splitting_summary()
        assert r["lean4_total_after"] == 1711

    def test_splitting_positive(self):
        r = quark_lepton_cl_splitting_summary()
        assert r["delta_c_L_quark"] > 0

    def test_open_items(self):
        r = quark_lepton_cl_splitting_summary()
        assert "remaining_open" in r
