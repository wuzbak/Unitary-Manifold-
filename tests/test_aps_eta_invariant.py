# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_aps_eta_invariant.py
================================
Test suite for src/core/aps_eta_invariant.py — Pillar 70.

Covers:
  - Module constants
  - orbifold_fixed_point_spectrum: modes, symmetry, errors
  - aps_eta_spectral_sum: positive/negative, symmetric, empty
  - aps_eta_invariant: specific values, formula, errors
  - eta_quantization_condition: dict keys, conditions for n_w=5 and n_w=7
  - nw_selection_from_aps: selected n_w, honest status, structure
  - aps_uniqueness_audit: proof steps, honest status labels
  - aps_comparison_table: list structure, n_w=5 and n_w=7 present

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.aps_eta_invariant import (
    N_W_CANONICAL,
    N_W2_CANONICAL,
    K_CS_CANONICAL,
    ETA_HALF,
    ETA_ZERO,
    APS_ADMISSIBLE_SET,
    orbifold_fixed_point_spectrum,
    aps_eta_spectral_sum,
    aps_eta_invariant,
    eta_quantization_condition,
    nw_selection_from_aps,
    aps_uniqueness_audit,
    aps_comparison_table,
)


class TestConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_n_w2_canonical(self):
        assert N_W2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_k_cs_sum_of_squares(self):
        assert K_CS_CANONICAL == N_W_CANONICAL ** 2 + N_W2_CANONICAL ** 2

    def test_eta_half_value(self):
        assert ETA_HALF == pytest.approx(0.5, rel=1e-10)

    def test_eta_zero_value(self):
        assert ETA_ZERO == pytest.approx(0.0, abs=1e-14)

    def test_aps_admissible_contains_zero(self):
        assert 0.0 in APS_ADMISSIBLE_SET

    def test_aps_admissible_contains_half(self):
        assert 0.5 in APS_ADMISSIBLE_SET

    def test_aps_admissible_length(self):
        assert len(APS_ADMISSIBLE_SET) == 2

    def test_eta_half_positive(self):
        assert ETA_HALF > 0

    def test_eta_zero_nonneg(self):
        assert ETA_ZERO >= 0

    def test_n_w_canonical_odd(self):
        assert N_W_CANONICAL % 2 == 1

    def test_n_w2_canonical_odd(self):
        assert N_W2_CANONICAL % 2 == 1

    def test_n_w_canonical_mod4(self):
        # For η̄(5) = 0.5 we need 5 % 4 == 1
        assert N_W_CANONICAL % 4 == 1

    def test_n_w2_canonical_mod4(self):
        # For η̄(7) = 0 we need 7 % 4 == 3
        assert N_W2_CANONICAL % 4 == 3


class TestOrbifoldSpectrum:
    def test_n_w_5_includes_zero(self):
        spec = orbifold_fixed_point_spectrum(5)
        assert 0.0 in spec

    def test_n_w_5_includes_pm1(self):
        spec = orbifold_fixed_point_spectrum(5)
        assert 1.0 in spec
        assert -1.0 in spec

    def test_n_w_5_includes_pm2(self):
        spec = orbifold_fixed_point_spectrum(5)
        assert 2.0 in spec
        assert -2.0 in spec

    def test_n_w_5_excludes_pm3(self):
        # 3^2 = 9 > 5, so ±3 not in spectrum
        spec = orbifold_fixed_point_spectrum(5)
        assert 3.0 not in spec
        assert -3.0 not in spec

    def test_n_w_1_has_modes_0_pm1(self):
        # n_w=1: stable modes n² ≤ 1 → n ∈ {-1, 0, 1}
        spec = orbifold_fixed_point_spectrum(1)
        assert sorted(spec) == [-1.0, 0.0, 1.0]

    def test_n_w_7_same_modes_as_5(self):
        # floor(sqrt(7)) = 2, same as floor(sqrt(5)) = 2
        spec5 = orbifold_fixed_point_spectrum(5)
        spec7 = orbifold_fixed_point_spectrum(7)
        assert len(spec5) == len(spec7)

    def test_spectrum_sorted(self):
        spec = orbifold_fixed_point_spectrum(5)
        assert spec == sorted(spec)

    def test_spectrum_symmetric(self):
        spec = orbifold_fixed_point_spectrum(5)
        for val in spec:
            assert -val in spec

    def test_n_w_3_spectrum(self):
        # floor(sqrt(3)) = 1: modes {-1, 0, 1}
        spec = orbifold_fixed_point_spectrum(3)
        assert sorted(spec) == sorted([-1.0, 0.0, 1.0])

    def test_n_w_9_spectrum(self):
        # floor(sqrt(9)) = 3: modes {-3,-2,-1,0,1,2,3}
        spec = orbifold_fixed_point_spectrum(9)
        assert 3.0 in spec
        assert -3.0 in spec

    def test_even_n_w_raises(self):
        with pytest.raises(ValueError):
            orbifold_fixed_point_spectrum(4)

    def test_zero_n_w_raises(self):
        with pytest.raises(ValueError):
            orbifold_fixed_point_spectrum(0)

    def test_negative_n_w_raises(self):
        with pytest.raises(ValueError):
            orbifold_fixed_point_spectrum(-1)

    def test_spectrum_length_n_w_5(self):
        # floor(sqrt(5)) = 2: {-2,-1,0,1,2} → length 5
        spec = orbifold_fixed_point_spectrum(5)
        assert len(spec) == 5

    def test_spectrum_output_type(self):
        assert isinstance(orbifold_fixed_point_spectrum(5), list)

    def test_spectrum_elements_float(self):
        spec = orbifold_fixed_point_spectrum(5)
        for s in spec:
            assert isinstance(s, float)

    def test_n_w_25_spectrum(self):
        # floor(sqrt(25)) = 5: modes {-5,...,5}
        spec = orbifold_fixed_point_spectrum(25)
        assert 5.0 in spec
        assert -5.0 in spec

    def test_spectrum_n_modes_arg_unused(self):
        # n_modes argument accepted without error
        spec = orbifold_fixed_point_spectrum(5, n_modes=50)
        assert len(spec) == 5

    def test_n_w_11_spectrum(self):
        # floor(sqrt(11)) = 3
        spec = orbifold_fixed_point_spectrum(11)
        assert 3.0 in spec
        assert -3.0 in spec
        assert 4.0 not in spec

    def test_spectrum_n_w_15(self):
        # floor(sqrt(15)) = 3
        spec = orbifold_fixed_point_spectrum(15)
        assert len(spec) == 7  # {-3,-2,-1,0,1,2,3}


class TestApsEtaSpectralSum:
    def test_empty_spectrum_zero(self):
        assert aps_eta_spectral_sum([]) == pytest.approx(0.0, abs=1e-14)

    def test_symmetric_spectrum_zero(self):
        assert aps_eta_spectral_sum([-1.0, 0.0, 1.0]) == pytest.approx(0.0, abs=1e-14)

    def test_all_positive(self):
        result = aps_eta_spectral_sum([1.0, 2.0, 3.0])
        # n_pos=3, n_neg=0, eta = 1.5, eta_bar = 0.5
        assert result == pytest.approx(0.5, rel=1e-10)

    def test_all_negative(self):
        result = aps_eta_spectral_sum([-1.0, -2.0, -3.0])
        # n_pos=0, n_neg=3, eta = -1.5, eta_bar = -1.5 % 1 = 0.5
        assert result == pytest.approx(0.5, rel=1e-10)

    def test_more_positive(self):
        result = aps_eta_spectral_sum([1.0, 2.0, -1.0])
        # n_pos=2, n_neg=1, eta = 0.5, eta_bar = 0.5
        assert result == pytest.approx(0.5, rel=1e-10)

    def test_only_zeros(self):
        result = aps_eta_spectral_sum([0.0, 0.0, 0.0])
        assert result == pytest.approx(0.0, abs=1e-14)

    def test_n_w_5_spectrum_sum(self):
        spec = orbifold_fixed_point_spectrum(5)
        result = aps_eta_spectral_sum(spec)
        # Symmetric: n_pos=2, n_neg=2, eta=0, eta_bar=0
        assert result == pytest.approx(0.0, abs=1e-14)

    def test_output_in_unit_interval(self):
        for spec in [[], [1.0], [-1.0, 1.0], [1.0, 2.0, 3.0]]:
            result = aps_eta_spectral_sum(spec)
            assert 0.0 <= result < 1.0

    def test_two_positives_one_negative(self):
        result = aps_eta_spectral_sum([1.0, 2.0, -1.0])
        # n_pos=2, n_neg=1, eta=0.5 → eta_bar=0.5
        assert result == pytest.approx(0.5, rel=1e-10)

    def test_output_type(self):
        assert isinstance(aps_eta_spectral_sum([1.0, -1.0]), float)

    def test_single_positive(self):
        result = aps_eta_spectral_sum([1.0])
        # n_pos=1, eta=0.5, eta_bar=0.5
        assert result == pytest.approx(0.5, rel=1e-10)

    def test_single_negative(self):
        result = aps_eta_spectral_sum([-1.0])
        # n_pos=0, n_neg=1, eta=-0.5, eta_bar=0.5
        assert result == pytest.approx(0.5, rel=1e-10)

    def test_four_positives(self):
        result = aps_eta_spectral_sum([1.0, 2.0, 3.0, 4.0])
        # n_pos=4, eta=2.0 → eta_bar=0.0
        assert result == pytest.approx(0.0, abs=1e-14)

    def test_mod_reduction(self):
        # 4 positives: eta=2.0, eta_bar=0
        result = aps_eta_spectral_sum([1.0, 2.0, 3.0, 4.0])
        assert result == pytest.approx(0.0, abs=1e-14)

    def test_large_symmetric(self):
        vals = list(range(-10, 11))
        result = aps_eta_spectral_sum([float(v) for v in vals])
        assert result == pytest.approx(0.0, abs=1e-14)


class TestApsEtaInvariant:
    def test_eta_n_w_5(self):
        assert aps_eta_invariant(5) == pytest.approx(ETA_HALF, rel=1e-10)

    def test_eta_n_w_7(self):
        assert aps_eta_invariant(7) == pytest.approx(ETA_ZERO, abs=1e-14)

    def test_eta_n_w_1(self):
        # 1 % 4 = 1 → η̄ = 0.5
        assert aps_eta_invariant(1) == pytest.approx(ETA_HALF, rel=1e-10)

    def test_eta_n_w_3(self):
        # 3 % 4 = 3 → η̄ = 0.0
        assert aps_eta_invariant(3) == pytest.approx(ETA_ZERO, abs=1e-14)

    def test_eta_n_w_9(self):
        # 9 % 4 = 1 → η̄ = 0.5
        assert aps_eta_invariant(9) == pytest.approx(ETA_HALF, rel=1e-10)

    def test_eta_n_w_11(self):
        # 11 % 4 = 3 → η̄ = 0.0
        assert aps_eta_invariant(11) == pytest.approx(ETA_ZERO, abs=1e-14)

    def test_eta_n_w_13(self):
        # 13 % 4 = 1 → η̄ = 0.5
        assert aps_eta_invariant(13) == pytest.approx(ETA_HALF, rel=1e-10)

    def test_eta_n_w_15(self):
        # 15 % 4 = 3 → η̄ = 0.0
        assert aps_eta_invariant(15) == pytest.approx(ETA_ZERO, abs=1e-14)

    def test_eta_n_w_17(self):
        # 17 % 4 = 1 → η̄ = 0.5
        assert aps_eta_invariant(17) == pytest.approx(ETA_HALF, rel=1e-10)

    def test_eta_n_w_19(self):
        # 19 % 4 = 3 → η̄ = 0.0
        assert aps_eta_invariant(19) == pytest.approx(ETA_ZERO, abs=1e-14)

    def test_eta_n_w_21(self):
        # 21 % 4 = 1 → η̄ = 0.5
        assert aps_eta_invariant(21) == pytest.approx(ETA_HALF, rel=1e-10)

    def test_eta_n_w_23(self):
        # 23 % 4 = 3 → η̄ = 0.0
        assert aps_eta_invariant(23) == pytest.approx(ETA_ZERO, abs=1e-14)

    def test_n_w_zero_raises(self):
        with pytest.raises(ValueError):
            aps_eta_invariant(0)

    def test_n_w_negative_raises(self):
        with pytest.raises(ValueError):
            aps_eta_invariant(-1)

    def test_even_n_w_raises(self):
        with pytest.raises(ValueError):
            aps_eta_invariant(2)

    def test_even_n_w_raises_4(self):
        with pytest.raises(ValueError):
            aps_eta_invariant(4)

    def test_even_n_w_raises_6(self):
        with pytest.raises(ValueError):
            aps_eta_invariant(6)

    def test_output_in_admissible_set(self):
        for n_w in [1, 3, 5, 7, 9, 11, 13, 15]:
            eta = aps_eta_invariant(n_w)
            assert any(abs(eta - v) < 1e-10 for v in APS_ADMISSIBLE_SET)

    def test_output_type(self):
        assert isinstance(aps_eta_invariant(5), float)

    def test_alternating_pattern(self):
        # 1→0.5, 3→0.0, 5→0.5, 7→0.0, 9→0.5, ...
        expected = [0.5, 0.0, 0.5, 0.0, 0.5]
        for i, n in enumerate([1, 3, 5, 7, 9]):
            assert aps_eta_invariant(n) == pytest.approx(expected[i], abs=1e-10)

    def test_n_w_5_not_zero(self):
        assert aps_eta_invariant(5) != pytest.approx(0.0, abs=1e-10)

    def test_n_w_7_is_zero(self):
        assert aps_eta_invariant(7) == pytest.approx(0.0, abs=1e-14)

    def test_n_w_5_is_half(self):
        assert aps_eta_invariant(5) == pytest.approx(0.5, rel=1e-10)

    def test_canonical_5_half(self):
        assert aps_eta_invariant(N_W_CANONICAL) == pytest.approx(ETA_HALF, rel=1e-10)

    def test_canonical_7_zero(self):
        assert aps_eta_invariant(N_W2_CANONICAL) == pytest.approx(ETA_ZERO, abs=1e-14)

    def test_n_w_25(self):
        # 25 % 4 = 1 → η̄ = 0.5
        assert aps_eta_invariant(25) == pytest.approx(ETA_HALF, rel=1e-10)

    def test_n_w_27(self):
        # 27 % 4 = 3 → η̄ = 0.0
        assert aps_eta_invariant(27) == pytest.approx(ETA_ZERO, abs=1e-14)


class TestEtaQuantizationCondition:
    def test_returns_dict(self):
        result = eta_quantization_condition(5)
        assert isinstance(result, dict)

    def test_key_eta_bar(self):
        assert "eta_bar" in eta_quantization_condition(5)

    def test_key_satisfies_aps_condition(self):
        assert "satisfies_aps_condition" in eta_quantization_condition(5)

    def test_key_satisfies_spin_structure(self):
        assert "satisfies_spin_structure_conjecture" in eta_quantization_condition(5)

    def test_key_n_w(self):
        assert "n_w" in eta_quantization_condition(5)

    def test_key_interpretation(self):
        assert "interpretation" in eta_quantization_condition(5)

    def test_n_w_5_satisfies_aps(self):
        result = eta_quantization_condition(5)
        assert result["satisfies_aps_condition"] is True

    def test_n_w_5_satisfies_spin_structure(self):
        result = eta_quantization_condition(5)
        assert result["satisfies_spin_structure_conjecture"] is True

    def test_n_w_7_satisfies_aps(self):
        result = eta_quantization_condition(7)
        assert result["satisfies_aps_condition"] is True

    def test_n_w_7_does_not_satisfy_spin_structure(self):
        result = eta_quantization_condition(7)
        assert result["satisfies_spin_structure_conjecture"] is False

    def test_n_w_5_eta_value(self):
        result = eta_quantization_condition(5)
        assert result["eta_bar"] == pytest.approx(0.5, rel=1e-10)

    def test_n_w_7_eta_value(self):
        result = eta_quantization_condition(7)
        assert result["eta_bar"] == pytest.approx(0.0, abs=1e-14)

    def test_interpretation_is_str(self):
        result = eta_quantization_condition(5)
        assert isinstance(result["interpretation"], str)

    def test_n_w_stored_correctly(self):
        result = eta_quantization_condition(5)
        assert result["n_w"] == 5

    def test_n_w_7_stored(self):
        result = eta_quantization_condition(7)
        assert result["n_w"] == 7

    def test_satisfies_aps_is_bool(self):
        result = eta_quantization_condition(5)
        assert isinstance(result["satisfies_aps_condition"], bool)

    def test_satisfies_spin_is_bool(self):
        result = eta_quantization_condition(5)
        assert isinstance(result["satisfies_spin_structure_conjecture"], bool)

    def test_n_w_3_satisfies_aps(self):
        # η̄(3) = 0.0 → satisfies APS (0 is admissible)
        result = eta_quantization_condition(3)
        assert result["satisfies_aps_condition"] is True

    def test_n_w_3_does_not_satisfy_spin_structure(self):
        result = eta_quantization_condition(3)
        assert result["satisfies_spin_structure_conjecture"] is False

    def test_n_w_1_satisfies_spin(self):
        result = eta_quantization_condition(1)
        assert result["satisfies_spin_structure_conjecture"] is True

    def test_n_w_9_satisfies_spin(self):
        result = eta_quantization_condition(9)
        assert result["satisfies_spin_structure_conjecture"] is True

    def test_even_raises(self):
        with pytest.raises(ValueError):
            eta_quantization_condition(4)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            eta_quantization_condition(0)

    def test_interpretation_mentions_admissible_for_5(self):
        result = eta_quantization_condition(5)
        assert "ADMISSIBLE" in result["interpretation"]

    def test_interpretation_mentions_excluded_for_7(self):
        result = eta_quantization_condition(7)
        assert "EXCLUDED" in result["interpretation"]

    def test_output_consistent_with_invariant(self):
        for n_w in [5, 7, 9, 11]:
            eta = aps_eta_invariant(n_w)
            cond = eta_quantization_condition(n_w)
            assert cond["eta_bar"] == pytest.approx(eta, abs=1e-14)


class TestNwSelectionFromAps:
    def setup_method(self):
        self.result = nw_selection_from_aps()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_key_eta_5(self):
        assert "eta_5" in self.result

    def test_key_eta_7(self):
        assert "eta_7" in self.result

    def test_key_selected_nw(self):
        assert "selected_nw" in self.result

    def test_key_selection_basis(self):
        assert "selection_basis" in self.result

    def test_key_honest_status(self):
        assert "honest_status" in self.result

    def test_key_caveat(self):
        assert "caveat" in self.result

    def test_eta_5_value(self):
        assert self.result["eta_5"] == pytest.approx(0.5, rel=1e-10)

    def test_eta_7_value(self):
        assert self.result["eta_7"] == pytest.approx(0.0, abs=1e-14)

    def test_selected_nw_is_5(self):
        assert self.result["selected_nw"] == 5

    def test_honest_status_physically_motivated(self):
        assert self.result["honest_status"] == "PHYSICALLY-MOTIVATED"

    def test_selection_basis_is_str(self):
        assert isinstance(self.result["selection_basis"], str)

    def test_caveat_is_str(self):
        assert isinstance(self.result["caveat"], str)

    def test_caveat_mentions_geometric_proof(self):
        assert "geometric proof" in self.result["caveat"].lower()

    def test_selection_basis_mentions_aps(self):
        assert "APS" in self.result["selection_basis"]

    def test_eta_5_not_zero(self):
        assert self.result["eta_5"] != pytest.approx(0.0, abs=1e-10)

    def test_condition_5_key(self):
        assert "condition_5" in self.result

    def test_condition_7_key(self):
        assert "condition_7" in self.result

    def test_condition_5_dict(self):
        assert isinstance(self.result["condition_5"], dict)

    def test_condition_7_dict(self):
        assert isinstance(self.result["condition_7"], dict)

    def test_selected_nw_canonical(self):
        assert self.result["selected_nw"] == N_W_CANONICAL

    def test_honest_status_not_proved(self):
        assert self.result["honest_status"] != "PROVED"


class TestApsUniquenessAudit:
    def setup_method(self):
        self.audit = aps_uniqueness_audit()

    def test_returns_dict(self):
        assert isinstance(self.audit, dict)

    def test_pillar_key(self):
        assert "pillar" in self.audit

    def test_pillar_value(self):
        assert self.audit["pillar"] == 70

    def test_name_key(self):
        assert "name" in self.audit

    def test_proof_steps_key(self):
        assert "proof_steps" in self.audit

    def test_proof_steps_dict(self):
        assert isinstance(self.audit["proof_steps"], dict)

    def test_step_1_proved(self):
        assert self.audit["proof_steps"]["step_1"]["status"] == "PROVED"

    def test_step_2_derived(self):
        assert self.audit["proof_steps"]["step_2"]["status"] == "DERIVED"

    def test_step_3_physically_motivated(self):
        assert self.audit["proof_steps"]["step_3"]["status"] == "PHYSICALLY-MOTIVATED"

    def test_honest_status_key(self):
        assert "honest_status" in self.audit

    def test_honest_status_dict(self):
        assert isinstance(self.audit["honest_status"], dict)

    def test_honest_status_proved(self):
        assert "PROVED" in self.audit["honest_status"]

    def test_honest_status_physically_motivated(self):
        assert "PHYSICALLY-MOTIVATED" in self.audit["honest_status"]

    def test_honest_status_open(self):
        assert "OPEN" in self.audit["honest_status"]

    def test_selected_nw_key(self):
        assert "selected_nw" in self.audit

    def test_selected_nw_value(self):
        assert self.audit["selected_nw"] == 5

    def test_gap_addressed_key(self):
        assert "gap_addressed" in self.audit

    def test_k_cs_key(self):
        assert "k_cs" in self.audit

    def test_eta_values_key(self):
        assert "eta_values" in self.audit

    def test_eta_values_has_5_and_7(self):
        ev = self.audit["eta_values"]
        assert "n_w_5" in ev and "n_w_7" in ev

    def test_eta_values_5_half(self):
        assert self.audit["eta_values"]["n_w_5"] == pytest.approx(0.5, rel=1e-10)

    def test_eta_values_7_zero(self):
        assert self.audit["eta_values"]["n_w_7"] == pytest.approx(0.0, abs=1e-14)

    def test_step_3_has_to_prove(self):
        assert "to_prove" in self.audit["proof_steps"]["step_3"]


class TestApsComparisonTable:
    def setup_method(self):
        self.table = aps_comparison_table()

    def test_returns_list(self):
        assert isinstance(self.table, list)

    def test_length_two(self):
        assert len(self.table) == 2

    def test_both_entries_dicts(self):
        for row in self.table:
            assert isinstance(row, dict)

    def test_n_w_5_present(self):
        nws = [row["n_w"] for row in self.table]
        assert 5 in nws

    def test_n_w_7_present(self):
        nws = [row["n_w"] for row in self.table]
        assert 7 in nws

    def test_n_w_5_selected_true(self):
        row5 = next(r for r in self.table if r["n_w"] == 5)
        assert row5["selected"] is True

    def test_n_w_7_selected_false(self):
        row7 = next(r for r in self.table if r["n_w"] == 7)
        assert row7["selected"] is False

    def test_eta_bar_key_present(self):
        for row in self.table:
            assert "eta_bar" in row

    def test_n_w_5_eta_half(self):
        row5 = next(r for r in self.table if r["n_w"] == 5)
        assert row5["eta_bar"] == pytest.approx(0.5, rel=1e-10)

    def test_n_w_7_eta_zero(self):
        row7 = next(r for r in self.table if r["n_w"] == 7)
        assert row7["eta_bar"] == pytest.approx(0.0, abs=1e-14)
