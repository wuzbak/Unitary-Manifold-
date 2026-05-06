# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_bulk_eigenvalues.py
================================
Tests for src/core/bulk_eigenvalues.py — Pillar 189-B: Laplacian Eigenvalue Quantization.
"""

from __future__ import annotations

import math
import pytest

from src.core.bulk_eigenvalues import (
    N_W,
    K_CS,
    C_L_CRITICAL,
    C_L_STEP,
    C_L_MAX_EIGENVALUE,
    J_PDG,
    braid_cl_eigenvalue,
    braid_cl_spectrum,
    assign_eigenvalues_to_fermions,
    jarlskog_shift_from_braid_cl,
    eigenvalue_quantization_audit,
    pillar189b_summary,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_c_l_critical_is_half(self):
        assert C_L_CRITICAL == pytest.approx(0.5, rel=1e-9)

    def test_c_l_step_is_5_over_74(self):
        assert C_L_STEP == pytest.approx(5.0 / 74.0, rel=1e-9)

    def test_c_l_step_is_n_w_over_k_cs(self):
        assert C_L_STEP == pytest.approx(N_W / K_CS, rel=1e-9)

    def test_c_l_max_eigenvalue(self):
        # int(K_CS / N_W) = int(74/5) = 14
        assert C_L_MAX_EIGENVALUE == 14

    def test_j_pdg_is_3e5(self):
        assert abs(J_PDG - 3.08e-5) < 1e-7


# ===========================================================================
# braid_cl_eigenvalue
# ===========================================================================

class TestBraidClEigenvalue:
    def test_ell_1(self):
        assert braid_cl_eigenvalue(1) == pytest.approx(5.0 / 74.0, rel=1e-9)

    def test_ell_2(self):
        assert braid_cl_eigenvalue(2) == pytest.approx(10.0 / 74.0, rel=1e-9)

    def test_ell_7(self):
        assert braid_cl_eigenvalue(7) == pytest.approx(35.0 / 74.0, rel=1e-9)

    def test_ell_14(self):
        assert braid_cl_eigenvalue(14) == pytest.approx(70.0 / 74.0, rel=1e-9)

    def test_step_property(self):
        # c_L(ℓ+1) - c_L(ℓ) = C_L_STEP
        for ell in range(1, 10):
            diff = braid_cl_eigenvalue(ell + 1) - braid_cl_eigenvalue(ell)
            assert diff == pytest.approx(C_L_STEP, rel=1e-9)

    def test_all_positive(self):
        for ell in range(1, 15):
            assert braid_cl_eigenvalue(ell) > 0.0

    def test_invalid_ell_zero_raises(self):
        with pytest.raises(ValueError):
            braid_cl_eigenvalue(0)

    def test_invalid_ell_negative_raises(self):
        with pytest.raises(ValueError):
            braid_cl_eigenvalue(-1)

    def test_ir_class_ell_7(self):
        # ℓ=7: c_L = 35/74 ≈ 0.473 < 0.5 → IR-class
        assert braid_cl_eigenvalue(7) < C_L_CRITICAL

    def test_uv_class_ell_8(self):
        # ℓ=8: c_L = 40/74 ≈ 0.541 > 0.5 → UV-class
        assert braid_cl_eigenvalue(8) > C_L_CRITICAL


# ===========================================================================
# braid_cl_spectrum
# ===========================================================================

class TestBraidClSpectrum:
    def setup_method(self):
        self.spectrum = braid_cl_spectrum()

    def test_returns_list(self):
        assert isinstance(self.spectrum, list)

    def test_length_is_c_l_max(self):
        assert len(self.spectrum) == C_L_MAX_EIGENVALUE

    def test_each_entry_has_ell(self):
        for entry in self.spectrum:
            assert "ell" in entry

    def test_each_entry_has_c_l(self):
        for entry in self.spectrum:
            assert "c_l" in entry

    def test_each_entry_has_zone(self):
        for entry in self.spectrum:
            assert "zone" in entry

    def test_ell_values_monotone(self):
        ells = [e["ell"] for e in self.spectrum]
        assert ells == sorted(ells)
        assert ells[0] == 1

    def test_c_l_values_monotone(self):
        cls = [e["c_l"] for e in self.spectrum]
        assert cls == sorted(cls)

    def test_zone_ir_for_small_ell(self):
        # ℓ=1..7: c_L < 0.5 → IR-class
        assert self.spectrum[0]["zone"] == "IR-class"

    def test_zone_uv_for_large_ell(self):
        # ℓ=8+: c_L > 0.5 → UV-class
        assert self.spectrum[-1]["zone"] == "UV-class"

    def test_custom_n_max(self):
        spec5 = braid_cl_spectrum(n_max=5)
        assert len(spec5) == 5

    def test_invalid_n_max_raises(self):
        with pytest.raises(ValueError):
            braid_cl_spectrum(n_max=0)

    def test_fraction_string_present(self):
        for entry in self.spectrum:
            assert "c_l_fraction" in entry


# ===========================================================================
# assign_eigenvalues_to_fermions
# ===========================================================================

class TestAssignEigenvaluesToFermions:
    def setup_method(self):
        self.assignments = assign_eigenvalues_to_fermions()

    def test_returns_list(self):
        assert isinstance(self.assignments, list)

    def test_9_fermions_assigned(self):
        assert len(self.assignments) == 9

    def test_each_entry_has_name(self):
        for a in self.assignments:
            assert "name" in a

    def test_each_entry_has_mass_mev(self):
        for a in self.assignments:
            assert "mass_mev" in a

    def test_each_entry_has_c_l_braid(self):
        for a in self.assignments:
            assert "c_l_braid" in a

    def test_each_entry_has_c_l_fitted(self):
        for a in self.assignments:
            assert "c_l_fitted_scaffold" in a

    def test_c_l_braid_all_positive(self):
        for a in self.assignments:
            assert a["c_l_braid"] > 0.0

    def test_c_l_braid_all_lt_1(self):
        for a in self.assignments:
            assert a["c_l_braid"] < 1.0

    def test_top_quark_present(self):
        names = [a["name"] for a in self.assignments]
        assert "top" in names

    def test_electron_present(self):
        names = [a["name"] for a in self.assignments]
        assert "electron" in names

    def test_heaviest_fermion_has_smallest_ell(self):
        # Top quark (heaviest) should have the smallest ℓ
        sorted_by_mass = sorted(self.assignments, key=lambda x: -x["mass_mev"])
        assert sorted_by_mass[0]["ell_assigned"] < sorted_by_mass[-1]["ell_assigned"]

    def test_deviation_from_fitted_is_finite(self):
        for a in self.assignments:
            assert math.isfinite(a["deviation_from_fitted"])

    def test_zone_consistent_flag_present(self):
        for a in self.assignments:
            assert "zone_consistent" in a
            assert isinstance(a["zone_consistent"], bool)


# ===========================================================================
# jarlskog_shift_from_braid_cl
# ===========================================================================

class TestJarlskogShiftFromBraidCl:
    def setup_method(self):
        self.result = jarlskog_shift_from_braid_cl()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_j_pdg_stored(self):
        assert abs(self.result["j_pdg"] - J_PDG) < 1e-8

    def test_j_scaffold_positive(self):
        assert self.result["j_scaffold"] > 0.0

    def test_j_braid_positive(self):
        assert self.result["j_braid"] > 0.0

    def test_gap_scaffold_pct_positive(self):
        assert self.result["gap_scaffold_pct"] >= 0.0

    def test_gap_braid_pct_positive(self):
        assert self.result["gap_braid_pct"] >= 0.0

    def test_improvement_is_bool(self):
        assert isinstance(self.result["improvement"], bool)

    def test_sin_angles_scaffold_present(self):
        s = self.result["sin_angles_scaffold"]
        assert "sin12" in s and "sin13" in s and "sin23" in s

    def test_sin_angles_braid_present(self):
        s = self.result["sin_angles_braid"]
        assert "sin12" in s and "sin13" in s and "sin23" in s

    def test_all_sin_angles_in_0_1(self):
        for key in ["sin_angles_scaffold", "sin_angles_braid"]:
            for angle_key, val in self.result[key].items():
                assert 0.0 <= val <= 1.0, f"{key}[{angle_key}] = {val} out of [0,1]"

    def test_honest_note_present(self):
        assert "honest_note" in self.result
        assert len(self.result["honest_note"]) > 20


# ===========================================================================
# eigenvalue_quantization_audit
# ===========================================================================

class TestEigenvalueQuantizationAudit:
    def setup_method(self):
        self.result = eigenvalue_quantization_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_189b(self):
        assert self.result["pillar"] == "189-B"

    def test_n_w_correct(self):
        assert self.result["n_w"] == N_W

    def test_k_cs_correct(self):
        assert self.result["k_cs"] == K_CS

    def test_c_l_step_correct(self):
        assert self.result["c_l_step"] == pytest.approx(C_L_STEP, rel=1e-9)

    def test_n_eigenvalues_computed(self):
        assert self.result["n_eigenvalues_computed"] == C_L_MAX_EIGENVALUE

    def test_n_fermions_assigned_9(self):
        assert self.result["n_fermions_assigned"] == 9

    def test_zone_consistency_fraction_in_0_1(self):
        f = self.result["zone_consistency_fraction"]
        assert 0.0 <= f <= 1.0

    def test_status_is_constrained_improvement(self):
        assert "CONSTRAINED" in self.result["status"]

    def test_pillar174_still_correct(self):
        assert self.result["pillar174_still_correct"] is True

    def test_pillar183_retained(self):
        assert self.result["pillar183_retained"] is True

    def test_verdict_nonempty(self):
        assert len(self.result["verdict"]) > 30

    def test_open_items_list(self):
        assert isinstance(self.result["open_items"], list)
        assert len(self.result["open_items"]) >= 2

    def test_jarlskog_analysis_present(self):
        assert "jarlskog_analysis" in self.result

    def test_mean_deviation_is_finite_positive(self):
        assert self.result["mean_cl_deviation_from_fitted"] >= 0.0
        assert math.isfinite(self.result["mean_cl_deviation_from_fitted"])


# ===========================================================================
# pillar189b_summary
# ===========================================================================

class TestPillar189bSummary:
    def setup_method(self):
        self.result = pillar189b_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_189b(self):
        assert self.result["pillar"] == "189-B"

    def test_status_is_constrained_improvement(self):
        assert "CONSTRAINED" in self.result["status"]

    def test_c_l_step_is_5_over_74(self):
        assert self.result["c_l_step"] == pytest.approx(5.0 / 74.0, rel=1e-9)

    def test_c_l_step_fraction_is_5_74(self):
        assert "5/74" in self.result["c_l_step_fraction"]

    def test_n_discrete_levels_is_14(self):
        assert self.result["n_discrete_levels"] == 14

    def test_zone_consistency_pct_in_0_100(self):
        assert 0.0 <= self.result["zone_consistency_pct"] <= 100.0

    def test_pillar174_preserved(self):
        assert self.result["pillar174_continuous_spectrum_preserved"] is True

    def test_pillar183_retained(self):
        assert self.result["pillar183_scaffold_retained"] is True

    def test_improvement_over_scaffold_present(self):
        assert "improvement_over_scaffold" in self.result
        assert len(self.result["improvement_over_scaffold"]) > 20
