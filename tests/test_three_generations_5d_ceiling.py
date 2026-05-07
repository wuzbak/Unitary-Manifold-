# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Three Generations 5D Ceiling (Pillar 220, Track A Session 3)."""

import math
import pytest

from src.core.three_generations_5d_ceiling import (
    N_W, K_CS, N_C, PI_KR,
    GENERATION_QUANTUM_NUMBERS,
    N_GEN_UPPER_BOUND,
    ARCHITECTURE_LIMIT,
    REQUIRES_DIMENSION,
    anomaly_gap_condition,
    generation_quantum_numbers,
    cl_quantized_by_generation,
    generation_mass_ratios,
    five_d_generation_derivation,
    six_d_requirement_proof,
    three_generations_ceiling_audit,
    pillar220_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_n_gen_is_3(self):
        assert N_GEN_UPPER_BOUND == 3

    def test_generation_quantum_numbers_tuple(self):
        assert isinstance(GENERATION_QUANTUM_NUMBERS, tuple)

    def test_generation_quantum_numbers_values(self):
        # n ∈ {0, 1, 2} satisfy n² ≤ 5
        assert set(GENERATION_QUANTUM_NUMBERS) == {0, 1, 2}

    def test_3_excluded_from_n(self):
        # 3² = 9 > 5 → n=3 should NOT be in the set
        assert 3 not in GENERATION_QUANTUM_NUMBERS

    def test_architecture_limit(self):
        assert ARCHITECTURE_LIMIT is True

    def test_requires_6d(self):
        assert REQUIRES_DIMENSION == 6


class TestAnomalyGapCondition:
    def test_returns_dict(self):
        result = anomaly_gap_condition()
        assert isinstance(result, dict)

    def test_n_w_in_result(self):
        result = anomaly_gap_condition()
        assert result["n_w"] == N_W

    def test_valid_n_values(self):
        result = anomaly_gap_condition()
        assert result["valid_n_values"] == [0, 1, 2]

    def test_n_generations_is_3(self):
        result = anomaly_gap_condition()
        assert result["n_generations"] == 3

    def test_derivation_steps_present(self):
        result = anomaly_gap_condition()
        assert len(result["derivation_steps"]) >= 4

    def test_key_exclusion_mentions_3(self):
        result = anomaly_gap_condition()
        assert "3" in result["key_exclusion"]

    def test_different_n_w_gives_different_n_gen(self):
        # n_w = 1: only n=0,1 satisfy n²≤1
        result = anomaly_gap_condition(n_w=1)
        assert result["n_generations"] == 2

        # n_w = 9: n=0,1,2,3 satisfy n²≤9
        result = anomaly_gap_condition(n_w=9)
        assert result["n_generations"] == 4


class TestGenerationQuantumNumbers:
    def test_for_n_w_5(self):
        result = generation_quantum_numbers(5)
        assert result == [0, 1, 2]

    def test_for_n_w_1(self):
        result = generation_quantum_numbers(1)
        assert result == [0, 1]

    def test_for_n_w_4(self):
        # n² ≤ 4: n ∈ {0, 1, 2}
        result = generation_quantum_numbers(4)
        assert result == [0, 1, 2]

    def test_for_n_w_8(self):
        # n² ≤ 8: n ∈ {0, 1, 2}
        result = generation_quantum_numbers(8)
        assert result == [0, 1, 2]

    def test_for_n_w_9(self):
        # n² ≤ 9: n ∈ {0, 1, 2, 3}
        result = generation_quantum_numbers(9)
        assert result == [0, 1, 2, 3]


class TestCLQuantizedByGeneration:
    def test_returns_list(self):
        result = cl_quantized_by_generation()
        assert isinstance(result, list)

    def test_length_is_3(self):
        result = cl_quantized_by_generation()
        assert len(result) == 3

    def test_gen0_cl_is_0(self):
        result = cl_quantized_by_generation()
        assert result[0]["c_l"] == pytest.approx(0.0)

    def test_gen1_cl_is_04(self):
        result = cl_quantized_by_generation()
        assert result[1]["c_l"] == pytest.approx(0.4)

    def test_gen2_cl_is_08(self):
        result = cl_quantized_by_generation()
        assert result[2]["c_l"] == pytest.approx(0.8)

    def test_yukawa_decreases_with_generation(self):
        result = cl_quantized_by_generation()
        yukawas = [r["yukawa_effective"] for r in result]
        assert yukawas[0] >= yukawas[1] >= yukawas[2]

    def test_gen2_yukawa_very_small(self):
        result = cl_quantized_by_generation()
        assert result[2]["yukawa_effective"] < 1e-3


class TestGenerationMassRatios:
    def test_returns_dict(self):
        result = generation_mass_ratios()
        assert isinstance(result, dict)

    def test_has_mass_ratios_key(self):
        result = generation_mass_ratios()
        assert "mass_ratios" in result

    def test_m01_ratio_at_least_1(self):
        # gen0 and gen1 can both be IR-localized (Yukawa=1) depending on c_L values
        result = generation_mass_ratios()
        assert result["mass_ratios"]["m_gen0_over_m_gen1"] >= 1.0

    def test_m12_ratio_greater_than_1(self):
        result = generation_mass_ratios()
        assert result["mass_ratios"]["m_gen1_over_m_gen2"] > 1.0

    def test_gen_table_present(self):
        result = generation_mass_ratios()
        assert "generation_table" in result


class TestFiveDGenerationDerivation:
    def test_returns_dict(self):
        result = five_d_generation_derivation()
        assert isinstance(result, dict)

    def test_status_says_derived(self):
        result = five_d_generation_derivation()
        assert "DERIVED" in result["status"]

    def test_axiom_zero_compliant(self):
        result = five_d_generation_derivation()
        assert result["axiom_zero_compliant"] is True

    def test_five_d_achievements_nonempty(self):
        result = five_d_generation_derivation()
        assert len(result["five_d_achievements"]) >= 3

    def test_five_d_limitations_nonempty(self):
        result = five_d_generation_derivation()
        assert len(result["five_d_limitations"]) >= 2


class TestSixDRequirementProof:
    def test_returns_dict(self):
        result = six_d_requirement_proof()
        assert isinstance(result, dict)

    def test_has_proof_steps(self):
        result = six_d_requirement_proof()
        assert len(result["proof_steps"]) >= 4

    def test_conclusion_mentions_architecture_limit(self):
        result = six_d_requirement_proof()
        assert "ARCHITECTURE_LIMIT" in result["conclusion"]

    def test_requires_dimension_6(self):
        result = six_d_requirement_proof()
        assert result["requires_dimension"] == 6


class TestThreeGenerationsCeilingAudit:
    def test_returns_dict(self):
        result = three_generations_ceiling_audit()
        assert isinstance(result, dict)

    def test_has_architecture_limit(self):
        result = three_generations_ceiling_audit()
        assert result["architecture_limit"]["flag"] is True

    def test_verdict_mentions_derived(self):
        result = three_generations_ceiling_audit()
        assert "DERIVES" in result["verdict"]

    def test_verdict_mentions_n_gen_3(self):
        result = three_generations_ceiling_audit()
        assert "3" in result["verdict"]


class TestPillar220Summary:
    def test_returns_dict(self):
        s = pillar220_summary()
        assert isinstance(s, dict)

    def test_pillar_number(self):
        s = pillar220_summary()
        assert s["pillar"] == 220

    def test_n_gen_derived_is_3(self):
        s = pillar220_summary()
        assert s["n_gen_derived"] == 3

    def test_generation_quantum_numbers_in_summary(self):
        s = pillar220_summary()
        assert set(s["generation_quantum_numbers"]) == {0, 1, 2}
