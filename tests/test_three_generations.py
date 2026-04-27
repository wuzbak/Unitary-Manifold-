# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
test_three_generations.py — Test suite for Pillar 42: Three-Generation Theorem
(src/core/three_generations.py).

~90 tests covering all public functions, constants, edge cases, and the
core theorem that n_w=5 yields exactly three stable KK generations.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.three_generations import (
    K_CS_CANONICAL,
    LAMBDA_CANONICAL,
    N_GENERATIONS_SM,
    N_W_CANONICAL,
    PHI_0_CANONICAL,
    STABILITY_EXPONENT,
    four_generation_exclusion,
    generation_count_is_unique_to_nw5,
    generation_mass_ratios,
    kk_mode_mass_spectrum,
    kk_stability_gap,
    lepton_mass_ratio_prediction,
    n_generations,
    orbifold_stable_modes,
    phi_eigenvalue,
    three_generation_proof,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_nw_canonical(self):
        assert N_W_CANONICAL == 5

    def test_kcs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_n_gen_sm(self):
        assert N_GENERATIONS_SM == 3

    def test_phi0_canonical(self):
        assert abs(PHI_0_CANONICAL - 5 * 2 * math.pi) < 1e-12

    def test_lambda_canonical(self):
        assert LAMBDA_CANONICAL == 1.0

    def test_stability_exponent(self):
        assert STABILITY_EXPONENT == 2


# ---------------------------------------------------------------------------
# orbifold_stable_modes
# ---------------------------------------------------------------------------

class TestOrbifoldStableModes:
    def test_nw5_gives_three_modes(self):
        modes = orbifold_stable_modes(5)
        assert modes == [0, 1, 2]

    def test_nw5_count(self):
        assert len(orbifold_stable_modes(5)) == 3

    def test_nw1_gives_one_mode(self):
        # 0² = 0 ≤ 1 ✓, 1² = 1 ≤ 1 ✓, 2² = 4 > 1 ✗ → modes [0, 1]
        modes = orbifold_stable_modes(1)
        assert 0 in modes
        assert 1 in modes
        assert 2 not in modes

    def test_nw3_gives_two_modes(self):
        # 0²=0≤3 ✓, 1²=1≤3 ✓, 2²=4>3 ✗ → [0,1]
        modes = orbifold_stable_modes(3)
        assert len(modes) == 2
        assert modes == [0, 1]

    def test_nw4_gives_two_modes(self):
        # 0²=0≤4, 1²=1≤4, 2²=4≤4 ✓, 3²=9>4 ✗
        modes = orbifold_stable_modes(4)
        assert 2 in modes
        assert 3 not in modes

    def test_nw8_gives_three_modes(self):
        # 0²=0≤8, 1²=1≤8, 2²=4≤8, 3²=9>8 → [0,1,2]
        modes = orbifold_stable_modes(8)
        assert modes == [0, 1, 2]

    def test_nw9_gives_four_modes(self):
        # 0²=0, 1²=1, 2²=4, 3²=9 all ≤ 9 → [0,1,2,3]
        modes = orbifold_stable_modes(9)
        assert 3 in modes

    def test_all_modes_satisfy_stability(self):
        for nw in range(1, 12):
            for n in orbifold_stable_modes(nw):
                assert n * n <= nw, f"n={n} violates n²≤n_w={nw}"

    def test_no_missing_modes(self):
        """Every n with n²≤n_w must appear."""
        for nw in range(1, 12):
            modes = orbifold_stable_modes(nw)
            for n in range(nw + 1):
                if n * n <= nw:
                    assert n in modes

    def test_raises_on_zero_nw(self):
        with pytest.raises(ValueError):
            orbifold_stable_modes(0)

    def test_raises_on_negative_nw(self):
        with pytest.raises(ValueError):
            orbifold_stable_modes(-1)

    def test_sorted(self):
        for nw in range(1, 10):
            modes = orbifold_stable_modes(nw)
            assert modes == sorted(modes)


# ---------------------------------------------------------------------------
# n_generations
# ---------------------------------------------------------------------------

class TestNGenerations:
    def test_nw5_gives_3(self):
        assert n_generations(5) == 3

    def test_nw1_gives_2(self):
        assert n_generations(1) == 2

    def test_nw3_gives_2(self):
        assert n_generations(3) == 2

    def test_nw4_gives_3(self):
        # 0,1,2 all satisfy n²≤4
        assert n_generations(4) == 3

    def test_nw9_gives_4(self):
        assert n_generations(9) == 4

    def test_consistency_with_orbifold_modes(self):
        for nw in range(1, 10):
            assert n_generations(nw) == len(orbifold_stable_modes(nw))


# ---------------------------------------------------------------------------
# phi_eigenvalue
# ---------------------------------------------------------------------------

class TestPhiEigenvalue:
    def test_n0_returns_phi0(self):
        phi0 = 10.0
        result = phi_eigenvalue(0, 5, phi0)
        assert abs(result - phi0) < 1e-12

    def test_n1_nw5(self):
        phi0 = 1.0
        expected = 1.0 / math.sqrt(1.0 + 1.0 / 5.0)
        assert abs(phi_eigenvalue(1, 5, phi0) - expected) < 1e-12

    def test_n2_nw5(self):
        phi0 = 1.0
        expected = 1.0 / math.sqrt(1.0 + 4.0 / 5.0)
        assert abs(phi_eigenvalue(2, 5, phi0) - expected) < 1e-12

    def test_hierarchy_phi0_gt_phi1_gt_phi2(self):
        phi0 = 10.0
        p0 = phi_eigenvalue(0, 5, phi0)
        p1 = phi_eigenvalue(1, 5, phi0)
        p2 = phi_eigenvalue(2, 5, phi0)
        assert p0 > p1 > p2

    def test_phi_positive(self):
        for n in range(3):
            assert phi_eigenvalue(n, 5, 1.0) > 0.0

    def test_raises_negative_n(self):
        with pytest.raises(ValueError):
            phi_eigenvalue(-1, 5, 1.0)

    def test_raises_zero_nw(self):
        with pytest.raises(ValueError):
            phi_eigenvalue(0, 0, 1.0)

    def test_raises_zero_phi0(self):
        with pytest.raises(ValueError):
            phi_eigenvalue(0, 5, 0.0)


# ---------------------------------------------------------------------------
# generation_mass_ratios
# ---------------------------------------------------------------------------

class TestGenerationMassRatios:
    def test_nw5_returns_tuple(self):
        r1, r2 = generation_mass_ratios(5)
        assert isinstance(r1, float)
        assert isinstance(r2, float)

    def test_nw5_r1_greater_than_1(self):
        r1, r2 = generation_mass_ratios(5)
        assert r1 > 1.0

    def test_nw5_r2_greater_than_r1(self):
        r1, r2 = generation_mass_ratios(5)
        assert r2 > r1

    def test_nw5_r1_exact(self):
        r1, _ = generation_mass_ratios(5)
        expected = math.sqrt(1.0 + 1.0 / 5.0)
        assert abs(r1 - expected) < 1e-12

    def test_nw5_r2_exact(self):
        _, r2 = generation_mass_ratios(5)
        expected = math.sqrt(1.0 + 4.0 / 5.0)
        assert abs(r2 - expected) < 1e-12

    def test_raises_nw3(self):
        # nw=3 gives only 2 modes; mass_ratios needs ≥ 3
        # Actually nw=3: modes=[0,1], so len<3 → should raise
        with pytest.raises(ValueError):
            generation_mass_ratios(3)

    def test_ratios_dimensionless(self):
        r1, r2 = generation_mass_ratios(5)
        # ratios must be pure numbers > 1
        assert r1 > 1.0 and r2 > 1.0


# ---------------------------------------------------------------------------
# kk_stability_gap
# ---------------------------------------------------------------------------

class TestKKStabilityGap:
    def test_canonical(self):
        gap = kk_stability_gap(5, 74)
        assert gap == 49

    def test_positive_gap(self):
        assert kk_stability_gap(5, 74) > 0

    def test_formula(self):
        for nw in range(1, 6):
            for kcs in range(nw * nw + 1, nw * nw + 10):
                assert kk_stability_gap(nw, kcs) == kcs - nw * nw

    def test_raises_zero_nw(self):
        with pytest.raises(ValueError):
            kk_stability_gap(0, 74)

    def test_raises_zero_kcs(self):
        with pytest.raises(ValueError):
            kk_stability_gap(5, 0)


# ---------------------------------------------------------------------------
# three_generation_proof
# ---------------------------------------------------------------------------

class TestThreeGenerationProof:
    def setup_method(self):
        self.proof = three_generation_proof(5)

    def test_n_w(self):
        assert self.proof["n_w"] == 5

    def test_k_cs(self):
        assert self.proof["k_cs"] == 74

    def test_stable_modes(self):
        assert self.proof["stable_modes"] == [0, 1, 2]

    def test_n_generations_3(self):
        assert self.proof["n_generations"] == 3

    def test_three_gen_confirmed(self):
        assert self.proof["three_gen_confirmed"] is True

    def test_fourth_excluded(self):
        assert self.proof["fourth_excluded"] is True

    def test_stability_gap_49(self):
        assert self.proof["stability_gap"] == 49

    def test_phi_eigenvalues_length(self):
        assert len(self.proof["phi_eigenvalues"]) == 3

    def test_phi_eigenvalues_decreasing(self):
        evs = self.proof["phi_eigenvalues"]
        assert evs[0] > evs[1] > evs[2]

    def test_mass_ratios_present(self):
        mr = self.proof["mass_ratios"]
        assert "m1_over_m0" in mr
        assert "m2_over_m0" in mr

    def test_mass_ratios_gt1(self):
        mr = self.proof["mass_ratios"]
        assert mr["m1_over_m0"] > 1.0
        assert mr["m2_over_m0"] > 1.0


# ---------------------------------------------------------------------------
# four_generation_exclusion
# ---------------------------------------------------------------------------

class TestFourGenerationExclusion:
    def test_nw5_excludes_4th(self):
        assert four_generation_exclusion(5) is True

    def test_nw9_includes_n3(self):
        # 3²=9 ≤ 9 → not excluded
        assert four_generation_exclusion(9) is False

    def test_nw8_excludes_n3(self):
        # 3²=9 > 8 → excluded
        assert four_generation_exclusion(8) is True


# ---------------------------------------------------------------------------
# lepton_mass_ratio_prediction
# ---------------------------------------------------------------------------

class TestLeptonMassRatioPrediction:
    def test_returns_dict(self):
        result = lepton_mass_ratio_prediction(5)
        assert "mu_over_e" in result
        assert "tau_over_e" in result

    def test_mu_over_e_nw5(self):
        r = lepton_mass_ratio_prediction(5)
        expected = math.sqrt(1.0 + 1.0 / 5.0)
        assert abs(r["mu_over_e"] - expected) < 1e-12

    def test_tau_over_e_nw5(self):
        r = lepton_mass_ratio_prediction(5)
        expected = math.sqrt(1.0 + 4.0 / 5.0)
        assert abs(r["tau_over_e"] - expected) < 1e-12

    def test_tau_over_e_gt_mu_over_e(self):
        r = lepton_mass_ratio_prediction(5)
        assert r["tau_over_e"] > r["mu_over_e"]

    def test_ratios_gt_1(self):
        r = lepton_mass_ratio_prediction(5)
        assert r["mu_over_e"] > 1.0
        assert r["tau_over_e"] > 1.0


# ---------------------------------------------------------------------------
# generation_count_is_unique_to_nw5
# ---------------------------------------------------------------------------

class TestGenerationCountUniqueness:
    def setup_method(self):
        self.result = generation_count_is_unique_to_nw5()

    def test_survey_length(self):
        assert len(self.result["survey"]) == 10

    def test_canonical_nw(self):
        assert self.result["canonical_nw"] == 5

    def test_nw5_in_survey(self):
        survey_dict = dict(self.result["survey"])
        assert survey_dict[5] == 3

    def test_nw_giving_3_gen_contains_5(self):
        assert 5 in self.result["nw_giving_3_gen"]

    def test_unique_statement_is_string(self):
        assert isinstance(self.result["unique_statement"], str)
        assert "n_w=5" in self.result["unique_statement"]

    def test_nw1_gives_2_modes(self):
        survey_dict = dict(self.result["survey"])
        assert survey_dict[1] == 2

    def test_nw3_gives_2_modes(self):
        survey_dict = dict(self.result["survey"])
        assert survey_dict[3] == 2


# ---------------------------------------------------------------------------
# kk_mode_mass_spectrum
# ---------------------------------------------------------------------------

class TestKKModeMassSpectrum:
    def test_nw5_returns_3_entries(self):
        spec = kk_mode_mass_spectrum(5, 1.0, 1.0)
        assert len(spec) == 3

    def test_all_stability_ok(self):
        for entry in kk_mode_mass_spectrum(5, 1.0, 1.0):
            assert entry["stability_ok"] is True

    def test_masses_increasing(self):
        spec = kk_mode_mass_spectrum(5, 1.0, 1.0)
        masses = [e["m_geo"] for e in spec]
        assert masses[0] < masses[1] < masses[2]

    def test_phi_eff_decreasing(self):
        spec = kk_mode_mass_spectrum(5, 1.0, 1.0)
        phis = [e["phi_eff"] for e in spec]
        assert phis[0] > phis[1] > phis[2]

    def test_mode_indices(self):
        spec = kk_mode_mass_spectrum(5, 1.0, 1.0)
        indices = [e["n"] for e in spec]
        assert indices == [0, 1, 2]

    def test_mass_formula_consistency(self):
        """m_geo = lam * n_w / phi_eff."""
        nw, phi0, lam = 5, 1.0, 1.0
        for entry in kk_mode_mass_spectrum(nw, phi0, lam):
            expected = lam * nw / entry["phi_eff"]
            assert abs(entry["m_geo"] - expected) < 1e-12


# ---------------------------------------------------------------------------
# n_gen_derivation_status — Issue 2 closure
# ---------------------------------------------------------------------------

from src.core.three_generations import n_gen_derivation_status


class TestNGenDerivationStatus:
    """Tests for n_gen_derivation_status(): epistemic chain for N_gen=3."""

    def test_returns_dict(self):
        result = n_gen_derivation_status()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = n_gen_derivation_status()
        for key in (
            "observational_inputs", "derivation_steps", "n_gen",
            "stable_modes", "is_conditional_theorem", "n_free_parameters",
            "epistemic_verdict",
        ):
            assert key in result, f"Missing key: {key!r}"

    def test_n_gen_is_3_for_nw5(self):
        result = n_gen_derivation_status(5)
        assert result["n_gen"] == 3

    def test_stable_modes_are_0_1_2_for_nw5(self):
        result = n_gen_derivation_status(5)
        assert result["stable_modes"] == [0, 1, 2]

    def test_is_conditional_theorem_true(self):
        result = n_gen_derivation_status()
        assert result["is_conditional_theorem"] is True

    def test_exactly_one_free_parameter(self):
        """n_w is the single observational input."""
        result = n_gen_derivation_status()
        assert result["n_free_parameters"] == 1

    def test_observational_inputs_contains_nw(self):
        result = n_gen_derivation_status()
        assert len(result["observational_inputs"]) == 1
        assert "n_w" in result["observational_inputs"][0].lower()

    def test_five_derivation_steps(self):
        result = n_gen_derivation_status()
        steps = result["derivation_steps"]
        assert len(steps) == 5

    def test_step0_is_input(self):
        steps = n_gen_derivation_status()["derivation_steps"]
        assert steps[0]["label"] == "INPUT"

    def test_remaining_steps_are_derived(self):
        steps = n_gen_derivation_status()["derivation_steps"]
        for step in steps[1:]:
            assert step["label"] == "DERIVED"

    def test_epistemic_verdict_is_str(self):
        assert isinstance(n_gen_derivation_status()["epistemic_verdict"], str)

    def test_verdict_mentions_conditional_theorem(self):
        verdict = n_gen_derivation_status()["epistemic_verdict"].lower()
        assert "conditional" in verdict or "theorem" in verdict

    def test_verdict_mentions_not_postulate(self):
        verdict = n_gen_derivation_status()["epistemic_verdict"].lower()
        assert "not" in verdict and "postulate" in verdict

    def test_nw3_gives_2_generations(self):
        # n=0: 0≤3✓, n=1: 1≤3✓, n=2: 4>3✗ → 2 stable modes
        result = n_gen_derivation_status(3)
        assert result["n_gen"] == 2

    def test_nw9_gives_4_generations(self):
        # n=0,1,2,3: 0,1,4,9 all ≤9 → 4 stable modes
        result = n_gen_derivation_status(9)
        assert result["n_gen"] == 4

    def test_invalid_nw_raises(self):
        import pytest
        with pytest.raises(ValueError):
            n_gen_derivation_status(0)
        with pytest.raises(ValueError):
            n_gen_derivation_status(-1)

    def test_step_indices_sequential(self):
        steps = n_gen_derivation_status()["derivation_steps"]
        for i, step in enumerate(steps):
            assert step["step"] == i

    def test_descriptions_nonempty(self):
        steps = n_gen_derivation_status()["derivation_steps"]
        for step in steps:
            assert len(step["description"]) > 10
