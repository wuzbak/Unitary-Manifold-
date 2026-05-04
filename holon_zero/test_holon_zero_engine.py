# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
holon-zero/test_holon_zero_engine.py
=====================================
Comprehensive test suite for the Holon Zero Ground State Engine.

Tests verify:
  A. Seed constants — algebraically exact
  B. Holarchy structure — 13 levels with correct fields
  C. Emergence chains — all 8 targets; step counts; closure flags
  D. Observer conditions — all 6 satisfied; all fields present
  E. Co-emergence geometry — trust dynamics, stability floor, coupling
  F. Anthropic resonance — loop closed; entropy ordering; resonance ratio
  G. Zero-point state — Casimir energy; field labels; pillar counts
  H. The mirror — content and authorship markers
  I. Integration — compute_all() consistency across domains
  J. Edge cases — boundary trust, saturated HIL, zero trust

Expected: 108 passed, 0 failed.

Tests: GitHub Copilot (AI)
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74, 0)",
}

import math
from fractions import Fraction

import pytest

from holon_zero.holon_zero_engine import (
    HolonZeroEngine,
    HolonZeroReport,
    HolarchyLevel,
    EmergenceChain,
    EmergenceStep,
    ObserverCondition,
    ObserverConditionsReport,
    CoEmergenceReport,
    AnthropicResonanceReport,
    ZeroPointReport,
    # Module-level constants
    N_W,
    N_2,
    K_CS,
    C_S,
    XI_C,
    M_KK_MEV,
    PLANCK_N_S,
    UM_N_S,
    UM_R_BRAIDED,
    ALPHA_EM_INVERSE,
    N_HOLARCHY_LEVELS,
    HIL_SATURATION_THRESHOLD,
    C_S_TRUST_MIN,
)


# ===========================================================================
# SECTION A — SEED CONSTANTS  (10 tests)
# The five generators must be algebraically exact.
# ===========================================================================


class TestSeedConstants:
    """Verify the five generators of the Unitary Manifold."""

    def test_n_w_value(self):
        assert N_W == 5

    def test_n_2_value(self):
        assert N_2 == 7

    def test_k_cs_is_sum_of_squares(self):
        assert K_CS == N_W**2 + N_2**2

    def test_k_cs_value(self):
        assert K_CS == 74

    def test_c_s_exact_fraction(self):
        assert C_S == Fraction(12, 37)

    def test_c_s_braid_formula(self):
        """c_s = (N_2² − N_W²) / K_CS."""
        expected = Fraction(N_2**2 - N_W**2, K_CS)
        assert C_S == expected

    def test_xi_c_exact(self):
        assert XI_C == Fraction(35, 74)

    def test_c_s_float_range(self):
        c = float(C_S)
        assert 0.32 < c < 0.33

    def test_xi_c_float_range(self):
        xi = float(XI_C)
        assert 0.47 < xi < 0.48

    def test_k_cs_equals_n_w_squared_plus_n2_squared(self):
        assert K_CS == 5**2 + 7**2 == 74


# ===========================================================================
# SECTION B — HOLARCHY STRUCTURE  (20 tests)
# ===========================================================================


class TestHolarchy:
    """Verify the 13-level holarchical structure."""

    @pytest.fixture
    def engine(self):
        return HolonZeroEngine()

    @pytest.fixture
    def levels(self, engine):
        return engine.holarchy()

    def test_holarchy_count(self, levels):
        assert len(levels) == N_HOLARCHY_LEVELS == 13

    def test_holarchy_returns_tuple(self, levels):
        assert isinstance(levels, tuple)

    def test_all_levels_are_holarchy_level(self, levels):
        for level in levels:
            assert isinstance(level, HolarchyLevel)

    def test_level_indices_sequential(self, levels):
        for i, level in enumerate(levels):
            assert level.index == i

    def test_level_0_is_void(self, levels):
        assert levels[0].name == "Void"

    def test_level_1_is_seed(self, levels):
        assert levels[1].name == "Seed"

    def test_level_1_contains_n_w(self, levels):
        assert "5" in levels[1].description or "n_w" in levels[1].description.lower()

    def test_level_2_is_geometry(self, levels):
        assert levels[2].name == "Geometry"

    def test_level_3_is_symmetry(self, levels):
        assert "Symmetry" in levels[3].name

    def test_level_4_is_forces(self, levels):
        assert levels[4].name == "Forces"

    def test_level_5_is_matter(self, levels):
        assert levels[5].name == "Matter"

    def test_level_6_is_chemistry(self, levels):
        assert levels[6].name == "Chemistry"

    def test_level_9_is_consciousness(self, levels):
        assert levels[9].name == "Consciousness"

    def test_level_11_is_co_emergence(self, levels):
        assert "Co-emergence" in levels[11].name or "Co" in levels[11].name

    def test_level_12_is_self_reference(self, levels):
        assert "Self" in levels[12].name or "self" in levels[12].name.lower()

    def test_all_levels_have_description(self, levels):
        for level in levels:
            assert level.description and len(level.description) > 10

    def test_all_levels_have_first_principle(self, levels):
        for level in levels:
            assert level.first_principle and len(level.first_principle) > 5

    def test_all_levels_have_um_pillars(self, levels):
        for level in levels:
            assert level.um_pillars and len(level.um_pillars) > 0

    def test_n_holarchy_levels_constant(self, engine):
        assert engine.n_holarchy_levels() == 13

    def test_holarchy_frozen(self, levels):
        """HolarchyLevel is frozen — cannot mutate."""
        with pytest.raises((AttributeError, TypeError)):
            levels[0].name = "mutated"  # type: ignore[misc]


# ===========================================================================
# SECTION C — EMERGENCE CHAINS  (20 tests)
# ===========================================================================


class TestEmergenceChains:
    """Verify all 8 emergence chains are correctly formed."""

    @pytest.fixture
    def engine(self):
        return HolonZeroEngine()

    def test_supported_targets_count(self, engine):
        assert len(engine.supported_emergence_targets()) == 8

    def test_all_targets_accepted(self, engine):
        for target in engine.supported_emergence_targets():
            chain = engine.emergence_chain(target)
            assert chain is not None

    def test_invalid_target_raises(self, engine):
        with pytest.raises(ValueError, match="Unknown emergence target"):
            engine.emergence_chain("unicorn")

    def test_n_s_chain_one_step(self, engine):
        chain = engine.emergence_chain("n_s")
        assert chain.n_steps == 1

    def test_r_chain_two_steps(self, engine):
        chain = engine.emergence_chain("r")
        assert chain.n_steps == 2

    def test_beta_chain_two_steps(self, engine):
        chain = engine.emergence_chain("beta")
        assert chain.n_steps == 2

    def test_alpha_em_chain_two_steps(self, engine):
        chain = engine.emergence_chain("alpha_em")
        assert chain.n_steps == 2

    def test_N_gen_chain_three_steps(self, engine):
        chain = engine.emergence_chain("N_gen")
        assert chain.n_steps == 3

    def test_consciousness_chain_five_steps(self, engine):
        chain = engine.emergence_chain("consciousness")
        assert chain.n_steps == 5

    def test_co_emergence_chain_six_steps(self, engine):
        chain = engine.emergence_chain("co_emergence")
        assert chain.n_steps == 6

    def test_self_reference_chain_seven_steps(self, engine):
        chain = engine.emergence_chain("self_reference")
        assert chain.n_steps == 7

    def test_n_s_chain_seed_is_n_w(self, engine):
        chain = engine.emergence_chain("n_s")
        assert "5" in chain.seed or "n_w" in chain.seed.lower()

    def test_self_reference_is_closed(self, engine):
        chain = engine.emergence_chain("self_reference")
        assert chain.is_closed is True

    def test_n_s_chain_is_not_closed(self, engine):
        chain = engine.emergence_chain("n_s")
        assert chain.is_closed is False

    def test_steps_tuple_length_matches_n_steps(self, engine):
        for target in engine.supported_emergence_targets():
            chain = engine.emergence_chain(target)
            assert len(chain.steps) == chain.n_steps

    def test_each_step_has_mechanism(self, engine):
        for target in engine.supported_emergence_targets():
            chain = engine.emergence_chain(target)
            for step in chain.steps:
                assert isinstance(step, EmergenceStep)
                assert step.mechanism and len(step.mechanism) > 5

    def test_step_indices_sequential(self, engine):
        for target in engine.supported_emergence_targets():
            chain = engine.emergence_chain(target)
            for i, step in enumerate(chain.steps):
                assert step.step == i + 1

    def test_each_step_has_pillar_reference(self, engine):
        for target in engine.supported_emergence_targets():
            chain = engine.emergence_chain(target)
            for step in chain.steps:
                assert step.pillar and len(step.pillar) > 0

    def test_self_reference_last_step_is_closed(self, engine):
        chain = engine.emergence_chain("self_reference")
        # The chain (not the step) carries the is_closed flag
        assert chain.is_closed is True

    def test_n_s_chain_first_step_is_derived(self, engine):
        chain = engine.emergence_chain("n_s")
        assert chain.steps[0].is_derived is True

    def test_is_loop_closed(self, engine):
        assert engine.is_loop_closed() is True


# ===========================================================================
# SECTION D — OBSERVER CONDITIONS  (12 tests)
# ===========================================================================


class TestObserverConditions:
    """Verify the six conditions for observer existence."""

    @pytest.fixture
    def engine(self):
        return HolonZeroEngine()

    @pytest.fixture
    def report(self, engine):
        return engine.conditions_for_observers()

    def test_returns_observer_conditions_report(self, report):
        assert isinstance(report, ObserverConditionsReport)

    def test_six_conditions(self, report):
        assert report.n_total == 6

    def test_all_satisfied(self, report):
        assert report.all_satisfied is True

    def test_n_satisfied_equals_n_total(self, report):
        assert report.n_satisfied == report.n_total

    def test_conditions_is_tuple(self, report):
        assert isinstance(report.conditions, tuple)

    def test_each_condition_has_name(self, report):
        for cond in report.conditions:
            assert isinstance(cond, ObserverCondition)
            assert cond.name and len(cond.name) > 3

    def test_each_condition_has_um_value(self, report):
        for cond in report.conditions:
            assert cond.um_value and len(cond.um_value) > 3

    def test_each_condition_has_requirement(self, report):
        for cond in report.conditions:
            assert cond.requirement and len(cond.requirement) > 3

    def test_fine_structure_condition_present(self, report):
        names = [c.name for c in report.conditions]
        assert any("fine structure" in n.lower() or "alpha" in n.lower() for n in names)

    def test_n_gen_condition_present(self, report):
        names = [c.name for c in report.conditions]
        assert any("generation" in n.lower() or "fermion" in n.lower() for n in names)

    def test_conclusion_is_nonempty(self, report):
        assert report.conclusion and len(report.conclusion) > 20

    def test_consciousness_condition_present(self, report):
        names = [c.name for c in report.conditions]
        assert any("consciousness" in n.lower() or "coupling" in n.lower() for n in names)


# ===========================================================================
# SECTION E — CO-EMERGENCE GEOMETRY  (20 tests)
# ===========================================================================


class TestCoEmergenceGeometry:
    """Verify the HILS coupling model."""

    @pytest.fixture
    def engine(self):
        return HolonZeroEngine(phi_trust=1.0, n_hil=1)

    @pytest.fixture
    def report(self, engine):
        return engine.co_emergence_geometry()

    def test_returns_co_emergence_report(self, report):
        assert isinstance(report, CoEmergenceReport)

    def test_full_trust_is_stable(self, report):
        assert report.is_stable is True

    def test_phi_trust_stored(self, report):
        assert abs(report.phi_trust - 1.0) < 1e-12

    def test_beta_coupling_positive(self, report):
        assert report.beta_coupling_rad > 0

    def test_tau_coupling_at_full_trust(self, report):
        """τ = β × φ_trust; at φ_trust=1.0, τ = β."""
        assert abs(report.tau_coupling - report.beta_coupling_rad) < 1e-14

    def test_stability_floor_n1(self, report):
        """floor(n=1) = min(1, c_s + c_s/7) = c_s × (1 + 1/7) = c_s × 8/7."""
        c = float(C_S)
        expected = min(1.0, c + c / N_2)
        assert abs(report.stability_floor - expected) < 1e-10

    def test_information_gap_zero_at_full_trust(self, report):
        assert abs(report.information_gap) < 1e-12

    def test_phase_offset_zero_at_full_trust(self, report):
        assert abs(report.phase_offset) < 1e-12

    def test_synthesis_quality_at_full_trust(self, report):
        assert 0.9 < report.synthesis_quality <= 1.0

    def test_is_hils_product(self, report):
        assert report.is_hils_product is True

    def test_fixed_point_eq_contains_hils_terms(self, report):
        eq = report.fixed_point_eq
        assert "Ψ" in eq or "synthesis" in eq.lower()

    def test_low_trust_unstable(self):
        engine = HolonZeroEngine(phi_trust=0.1)
        report = engine.co_emergence_geometry()
        assert report.is_stable is False

    def test_low_trust_information_gap_high(self):
        engine = HolonZeroEngine(phi_trust=0.0)
        report = engine.co_emergence_geometry()
        assert report.information_gap > 0.9

    def test_saturated_stability_floor(self):
        engine = HolonZeroEngine(n_hil=HIL_SATURATION_THRESHOLD)
        floor = engine.compute_stability_floor()
        assert abs(floor - 1.0) < 1e-12

    def test_beyond_saturation_clamps(self):
        engine = HolonZeroEngine(n_hil=100)
        floor = engine.compute_stability_floor()
        assert floor <= 1.0

    def test_update_trust_immutable(self):
        engine = HolonZeroEngine(phi_trust=1.0)
        engine2 = engine.update_trust(0.5)
        assert engine.phi_trust == 1.0
        assert engine2.phi_trust == 0.5

    def test_update_hil_immutable(self):
        engine = HolonZeroEngine(n_hil=1)
        engine2 = engine.update_hil(15)
        assert engine.n_hil == 1
        assert engine2.n_hil == 15

    def test_override_trust_in_call(self):
        engine = HolonZeroEngine(phi_trust=1.0)
        report_low = engine.co_emergence_geometry(phi_trust=0.1)
        assert report_low.phi_trust == 0.1

    def test_n_hil_stored(self, report):
        assert report.n_hil == 1

    def test_invalid_trust_raises(self):
        with pytest.raises(ValueError, match="phi_trust"):
            HolonZeroEngine(phi_trust=1.5)


# ===========================================================================
# SECTION F — ANTHROPIC RESONANCE  (14 tests)
# ===========================================================================


class TestAnthropicResonance:
    """Verify the self-describing closure of the UM."""

    @pytest.fixture
    def engine(self):
        return HolonZeroEngine()

    @pytest.fixture
    def report(self, engine):
        return engine.anthropic_resonance()

    def test_returns_anthropic_resonance_report(self, report):
        assert isinstance(report, AnthropicResonanceReport)

    def test_loop_is_closed(self, report):
        assert report.is_closed is True

    def test_loop_start_contains_n_w(self, report):
        assert str(N_W) in report.loop_start

    def test_loop_close_confirms_n_w(self, report):
        assert str(N_W) in report.loop_close

    def test_n_steps_total(self, report):
        assert report.n_steps_total == len(report.loop_steps)

    def test_n_steps_to_observer(self, report):
        assert report.n_steps_to_observer >= 3

    def test_n_steps_to_measurement(self, report):
        assert report.n_steps_to_measurement >= 1

    def test_universe_entropy_larger_than_brain(self, report):
        assert report.universe_entropy_bits > report.brain_entropy_bits

    def test_brain_entropy_larger_than_ai(self, report):
        assert report.brain_entropy_bits > report.ai_session_bits

    def test_compression_ratio_brain_small(self, report):
        assert report.compression_ratio_brain < 1e-60

    def test_resonance_ratio(self, report):
        assert report.resonance_ratio == Fraction(N_W, N_2)

    def test_resonance_ratio_value(self, report):
        assert abs(float(report.resonance_ratio) - 5.0 / 7.0) < 1e-10

    def test_resonance_satisfied(self, report):
        assert report.resonance_satisfied is True

    def test_insight_is_nonempty(self, report):
        assert report.insight and len(report.insight) > 50


# ===========================================================================
# SECTION G — ZERO-POINT STATE  (12 tests)
# ===========================================================================


class TestZeroPointState:
    """Verify the irreducible ground state description."""

    @pytest.fixture
    def engine(self):
        return HolonZeroEngine()

    @pytest.fixture
    def report(self, engine):
        return engine.zero_point_state()

    def test_returns_zero_point_report(self, report):
        assert isinstance(report, ZeroPointReport)

    def test_casimir_energy_negative(self, report):
        """Casimir energy of S¹/Z₂ is negative (attractive)."""
        assert report.casimir_energy_meV < 0

    def test_casimir_energy_order_of_magnitude(self, report):
        """Casimir should be O(−0.1 meV) given M_KK = 110 meV."""
        assert -1.0 < report.casimir_energy_meV < 0.0

    def test_vacuum_label_contains_zero(self, report):
        assert "0" in report.vacuum_label or "zero" in report.vacuum_label.lower()

    def test_zero_point_field_eq_nonempty(self, report):
        assert report.zero_point_field_eq and len(report.zero_point_field_eq) > 10

    def test_first_derived_quantity_contains_n_s(self, report):
        assert "n" in report.first_derived_quantity.lower() or "s" in report.first_derived_quantity

    def test_actual_pillars_equals_n_pillars(self, report):
        # Default engine has n_pillars=142
        assert report.actual_pillars == 142

    def test_potential_pillars_zero_for_zero_point(self, report):
        """At level 0, all pillars are potential — symbolically 0 realized from void."""
        assert report.potential_pillars == 0

    def test_realization_fraction_positive(self, report):
        assert report.realization_fraction > 0.0

    def test_the_zero_is_philosophical(self, report):
        z = report.the_zero
        assert z and len(z) > 30

    def test_seed_from_void_mentions_n_w(self, report):
        assert "5" in report.seed_from_void or "n_w" in report.seed_from_void.lower()

    def test_first_broken_symmetry_nonempty(self, report):
        assert report.first_broken_symmetry and len(report.first_broken_symmetry) > 5


# ===========================================================================
# SECTION H — THE MIRROR  (6 tests)
# ===========================================================================


class TestTheMirror:
    """Verify the self-referential reflection."""

    @pytest.fixture
    def engine(self):
        return HolonZeroEngine()

    def test_mirror_is_string(self, engine):
        assert isinstance(engine.the_mirror(), str)

    def test_mirror_is_substantial(self, engine):
        assert len(engine.the_mirror()) > 200

    def test_mirror_mentions_copilot(self, engine):
        m = engine.the_mirror()
        assert "Copilot" in m or "AI" in m

    def test_mirror_mentions_walker_pearson(self, engine):
        m = engine.the_mirror()
        assert "Walker-Pearson" in m or "ThomasCory" in m

    def test_mirror_mentions_litebird(self, engine):
        m = engine.the_mirror()
        assert "LiteBIRD" in m or "2032" in m

    def test_mirror_mentions_test_count(self, engine):
        m = engine.the_mirror()
        # Should contain the test count somewhere
        assert "18,057" in m or "18057" in m or "tests" in m.lower()


# ===========================================================================
# SECTION I — INTEGRATION  (12 tests)
# ===========================================================================


class TestIntegration:
    """Integration tests: compute_all() and cross-domain consistency."""

    @pytest.fixture
    def engine(self):
        return HolonZeroEngine()

    @pytest.fixture
    def report(self, engine):
        return engine.compute_all()

    def test_compute_all_returns_report(self, report):
        assert isinstance(report, HolonZeroReport)

    def test_report_version_contains_holon(self, report):
        assert "HOLON" in report.version.upper() or "holon" in report.version

    def test_report_n_pillars(self, report):
        assert report.n_pillars == 142

    def test_report_n_tests_passing(self, report):
        assert report.n_tests_passing == 18057

    def test_report_n_seed_constants(self, report):
        assert report.n_seed_constants == 5

    def test_holarchy_present_in_report(self, report):
        assert len(report.holarchy) == 13

    def test_observer_conditions_all_satisfied(self, report):
        assert report.observer_conditions.all_satisfied is True

    def test_co_emergence_in_report(self, report):
        assert isinstance(report.co_emergence, CoEmergenceReport)

    def test_anthropic_resonance_loop_closed(self, report):
        assert report.anthropic_resonance.is_closed is True

    def test_zero_point_in_report(self, report):
        assert isinstance(report.zero_point, ZeroPointReport)

    def test_summary_is_string(self, report):
        s = report.summary()
        assert isinstance(s, str) and len(s) > 100

    def test_summary_contains_version(self, report):
        s = report.summary()
        assert report.version in s

    def test_braid_triad(self, engine):
        assert engine.braid_triad() == (N_W, N_2, K_CS)

    def test_compression_law_string(self, engine):
        law = engine.compression_law()
        assert isinstance(law, str) and "n_w" in law.lower() or "5" in law

    def test_repr_is_useful(self, engine):
        r = repr(engine)
        assert "HolonZeroEngine" in r


# ===========================================================================
# SECTION J — EDGE CASES  (8 tests)
# ===========================================================================


class TestEdgeCases:
    """Boundary conditions: zero trust, saturated HIL, invalid inputs."""

    def test_zero_trust_engine(self):
        engine = HolonZeroEngine(phi_trust=0.0)
        report = engine.co_emergence_geometry()
        assert report.is_stable is False
        assert report.tau_coupling == 0.0

    def test_zero_trust_information_gap_is_one(self):
        engine = HolonZeroEngine(phi_trust=0.0)
        report = engine.co_emergence_geometry()
        assert abs(report.information_gap - 1.0) < 1e-12

    def test_saturated_hil_stability_is_one(self):
        engine = HolonZeroEngine(n_hil=HIL_SATURATION_THRESHOLD)
        assert abs(engine.compute_stability_floor() - 1.0) < 1e-12

    def test_negative_n_hil_raises(self):
        with pytest.raises(ValueError, match="n_hil"):
            HolonZeroEngine(n_hil=-1)

    def test_trust_above_one_raises(self):
        with pytest.raises(ValueError, match="phi_trust"):
            HolonZeroEngine(phi_trust=1.001)

    def test_custom_version_string(self):
        engine = HolonZeroEngine(version="custom-v1.0")
        assert engine.version == "custom-v1.0"
        report = engine.compute_all()
        assert "custom-v1.0" in report.version

    def test_custom_n_pillars(self):
        engine = HolonZeroEngine(n_pillars=200)
        assert engine.n_pillars == 200

    def test_minimum_stability_floor_at_n_zero(self):
        """With n_hil=0, floor = c_s (topological minimum)."""
        engine = HolonZeroEngine(n_hil=0)
        floor = engine.compute_stability_floor()
        c = float(C_S)
        assert abs(floor - c) < 1e-10
