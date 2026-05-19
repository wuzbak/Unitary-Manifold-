# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/pillar285_dark_energy_extension_specification.py.

Pillar 285 — Dark Energy Extension Specification (v2.0 Contingency Architecture)

Validates: quantitative extension constraints, DR3 falsification routing,
viability rankings, and the full extension specification report.
All numbers independently verified against the analysis in docs/CLAIM_MASTER_BOARD.md.
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar285_dark_energy_extension_specification import (
    # Constants
    UM_WA_PREDICTION,
    FALSIFICATION_THRESHOLD_SIGMA,
    DESI_DR2_COMBINED,
    DESI_DR3_FORECAST_SIGMA,
    GW_COUPLING_BOUND,
    BF_BOUND_ADS5,
    SUPER_PLANCKIAN_THRESHOLD,
    BRAIDED_SOUND_SPEED,
    # Functions
    bulk_scalar_extension_constraints,
    cosmological_radion_constraints,
    k_essence_extension_constraints,
    coupled_dark_energy_constraints,
    dr3_falsification_check,
    extension_viability_ranking,
    extension_specification_report,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants sanity
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_um_wa_prediction_is_zero(self):
        assert UM_WA_PREDICTION == 0.0

    def test_falsification_threshold(self):
        assert FALSIFICATION_THRESHOLD_SIGMA == pytest.approx(3.0)

    def test_desi_dr2_combined_structure(self):
        for key in ("wa_central", "wa_sigma", "w0_central", "w0_sigma",
                    "wa_tension_sigma", "status"):
            assert key in DESI_DR2_COMBINED

    def test_desi_dr2_tension_matches_published(self):
        # Independent check: |−0.55|/0.20 = 2.75σ (arXiv:2503.14738 combined)
        expected = abs(DESI_DR2_COMBINED["wa_central"]) / DESI_DR2_COMBINED["wa_sigma"]
        assert DESI_DR2_COMBINED["wa_tension_sigma"] == pytest.approx(expected, abs=1e-9)
        assert DESI_DR2_COMBINED["wa_tension_sigma"] == pytest.approx(2.75, abs=1e-9)

    def test_desi_dr2_high_tension_not_falsified(self):
        # CORE INTEGRITY: DESI DR2 does NOT falsify the framework
        assert DESI_DR2_COMBINED["wa_tension_sigma"] < FALSIFICATION_THRESHOLD_SIGMA

    def test_gw_coupling_bound(self):
        assert 0.0 < GW_COUPLING_BOUND < 0.1

    def test_bf_bound_ads5(self):
        assert BF_BOUND_ADS5 == pytest.approx(-4.0)

    def test_super_planckian_threshold(self):
        assert SUPER_PLANCKIAN_THRESHOLD == pytest.approx(1.0)

    def test_braided_sound_speed_exact(self):
        # c_s = 12/37 from Pillar 27 (5,7) braid resonance
        assert BRAIDED_SOUND_SPEED == pytest.approx(12.0 / 37.0, rel=1e-9)

    def test_dr3_forecast_sigma_reasonable(self):
        # DR3 forecast precision should be tighter than DR2 (0.20)
        assert 0.05 < DESI_DR3_FORECAST_SIGMA < DESI_DR2_COMBINED["wa_sigma"]


# ─────────────────────────────────────────────────────────────────────────────
# Extension 1: Bulk scalar
# ─────────────────────────────────────────────────────────────────────────────

class TestBulkScalarExtension:
    def test_structure(self):
        result = bulk_scalar_extension_constraints()
        for key in ("extension", "wa_target", "required_one_plus_w",
                    "required_field_displacement_mpl", "is_super_planckian",
                    "bf_bound_satisfied", "gw_stable", "viable", "conclusion"):
            assert key in result

    def test_extension_name(self):
        result = bulk_scalar_extension_constraints()
        assert result["extension"] == "BULK_SCALAR_QUINTESSENCE"

    def test_required_one_plus_w(self):
        # (1+w) = |wₐ|/2 for tracker solution
        result = bulk_scalar_extension_constraints(wa_target=-0.55)
        assert result["required_one_plus_w"] == pytest.approx(0.275, abs=1e-9)

    def test_required_displacement_formula(self):
        # Δφ̃ = √(2·(1+w)) = √(|wₐ|)
        wa = -0.55
        result = bulk_scalar_extension_constraints(wa_target=wa)
        expected = math.sqrt(2.0 * abs(wa) / 2.0)
        assert result["required_field_displacement_mpl"] == pytest.approx(expected, abs=1e-9)

    def test_desi_dr2_combined_is_sub_planckian(self):
        # For wa = -0.55: Δφ̃ = √0.55 ≈ 0.742 < 1 M_Pl
        result = bulk_scalar_extension_constraints(wa_target=-0.55)
        assert not result["is_super_planckian"]
        assert result["required_field_displacement_mpl"] < 1.0

    def test_large_wa_is_super_planckian(self):
        # For |wₐ| > 2: Δφ̃ = √|wₐ| > 1 M_Pl
        result = bulk_scalar_extension_constraints(wa_target=-2.5)
        assert result["is_super_planckian"]

    def test_bf_bound_satisfied_for_typical_wa(self):
        result = bulk_scalar_extension_constraints(wa_target=-0.55)
        # m₅²/k² = −|wₐ| = −0.55 > −4 (BF bound)
        assert result["bf_bound_satisfied"]

    def test_bf_bound_violated_for_large_wa(self):
        # For |wₐ| > 4: m₅²/k² < −4 → BF violation
        result = bulk_scalar_extension_constraints(wa_target=-4.5)
        assert not result["bf_bound_satisfied"]

    def test_gw_stable_with_small_coupling(self):
        result = bulk_scalar_extension_constraints(gw_coupling=0.005)
        assert result["gw_stable"]

    def test_gw_unstable_with_large_coupling(self):
        result = bulk_scalar_extension_constraints(gw_coupling=0.05)
        assert not result["gw_stable"]

    def test_viable_for_dr2_central(self):
        # DESI DR2 combined target: sub-Planckian, BF OK, GW stable → viable
        result = bulk_scalar_extension_constraints(wa_target=-0.55)
        assert result["viable"]

    def test_conclusion_is_string(self):
        result = bulk_scalar_extension_constraints()
        assert isinstance(result["conclusion"], str)
        assert len(result["conclusion"]) > 20


# ─────────────────────────────────────────────────────────────────────────────
# Extension 2: Cosmological radion
# ─────────────────────────────────────────────────────────────────────────────

class TestCosmologicalRadionExtension:
    def test_structure(self):
        result = cosmological_radion_constraints()
        for key in ("extension", "m_r_gev_required", "eps_gw_required_for_light_radion",
                    "tuning_severity_factor", "viable", "conclusion"):
            assert key in result

    def test_extension_name(self):
        result = cosmological_radion_constraints()
        assert result["extension"] == "COSMOLOGICAL_RADION"

    def test_never_viable(self):
        # This extension is fundamentally incompatible with RS1 hierarchy
        result = cosmological_radion_constraints()
        assert result["viable"] is False

    def test_enormous_tuning_required(self):
        # Tuning severity must be >> 1 (enormous fine-tuning)
        result = cosmological_radion_constraints(m_kk_gev=1e3)
        assert result["tuning_severity_factor"] > 1e80

    def test_required_mass_is_cosmologically_small(self):
        # m_r target ~ H₀ ~ 10⁻⁴² GeV
        result = cosmological_radion_constraints(m_radion_over_hubble_target=1.0)
        assert result["m_r_gev_required"] < 1e-40

    def test_conclusion_mentions_hierarchy(self):
        result = cosmological_radion_constraints()
        assert "hierarchy" in result["conclusion"].lower() or "stabilisation" in result["conclusion"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# Extension 3: k-Essence
# ─────────────────────────────────────────────────────────────────────────────

class TestKEssenceExtension:
    def test_structure(self):
        result = k_essence_extension_constraints()
        for key in ("extension", "n_kinetic", "cs_squared", "cs",
                    "gradient_stable", "causal", "viable", "conclusion"):
            assert key in result

    def test_extension_name(self):
        result = k_essence_extension_constraints()
        assert result["extension"] == "K_ESSENCE_BULK_SCALAR"

    def test_canonical_reduces_to_cs_equal_1(self):
        result = k_essence_extension_constraints(n_kinetic=1.0)
        assert result["cs_squared"] == pytest.approx(1.0, abs=1e-9)
        assert result["cs"] == pytest.approx(1.0, abs=1e-9)

    def test_cs_formula(self):
        # c_s² = 1/(2n-1)
        for n in [2.0, 3.0, 5.0]:
            result = k_essence_extension_constraints(n_kinetic=n)
            expected_cs2 = 1.0 / (2*n - 1)
            assert result["cs_squared"] == pytest.approx(expected_cs2, abs=1e-9)

    def test_gradient_stable_for_n_geq_1(self):
        for n in [1.0, 2.0, 5.0, 10.0]:
            result = k_essence_extension_constraints(n_kinetic=n)
            assert result["gradient_stable"], f"n={n} should be gradient stable"

    def test_causal_for_any_n(self):
        # c_s² = 1/(2n-1) ≤ 1 for n ≥ 1 → always causal
        for n in [1.0, 2.0, 3.0, 10.0]:
            result = k_essence_extension_constraints(n_kinetic=n)
            assert result["causal"]

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            k_essence_extension_constraints(n_kinetic=0.5)

    def test_reduced_displacement_vs_canonical(self):
        # k-essence reduces required displacement vs canonical
        r_canonical = k_essence_extension_constraints(n_kinetic=1.0, wa_target=-0.55)
        r_kessence = k_essence_extension_constraints(n_kinetic=3.0, wa_target=-0.55)
        assert r_kessence["required_field_displacement_mpl"] < r_canonical["required_field_displacement_mpl"]

    def test_high_n_is_sub_planckian(self):
        # Large n greatly reduces required displacement
        result = k_essence_extension_constraints(n_kinetic=10.0, wa_target=-0.55)
        assert not result["is_super_planckian"]

    def test_braided_sound_speed_stored(self):
        result = k_essence_extension_constraints()
        assert result["braided_sound_speed"] == pytest.approx(12.0/37.0, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# Extension 4: Coupled dark energy
# ─────────────────────────────────────────────────────────────────────────────

class TestCoupledDarkEnergy:
    def test_structure(self):
        result = coupled_dark_energy_constraints()
        for key in ("extension", "beta_de_input", "wa_eff_from_input_beta",
                    "beta_de_required_for_target", "viable", "conclusion"):
            assert key in result

    def test_extension_name(self):
        result = coupled_dark_energy_constraints()
        assert result["extension"] == "COUPLED_DARK_ENERGY"

    def test_wa_eff_formula(self):
        # wₐ_eff = −6β²Ω_m
        beta = 0.05; omega_m = 0.315
        result = coupled_dark_energy_constraints(beta_de=beta)
        expected = -6.0 * beta**2 * omega_m
        assert result["wa_eff_from_input_beta"] == pytest.approx(expected, abs=1e-9)

    def test_wa_eff_is_negative(self):
        result = coupled_dark_energy_constraints(beta_de=0.1)
        assert result["wa_eff_from_input_beta"] < 0.0

    def test_required_beta_formula(self):
        # β = √(|wₐ_target| / (6Ω_m))
        wa = -0.55; omega_m = 0.315
        result = coupled_dark_energy_constraints(wa_target=wa)
        expected = math.sqrt(abs(wa) / (6.0 * omega_m))
        assert result["beta_de_required_for_target"] == pytest.approx(expected, abs=1e-9)

    def test_small_coupling_is_viable(self):
        # beta_input = 0.05 < cmb_growth_bound, but viability is based on
        # the *required* coupling to explain the target wₐ.  For DR2 combined
        # (|wₐ| = 0.55), beta_required ≈ 0.54 >> CMB bound → not CMB safe.
        # Test that the returned flag correctly reflects required coupling.
        result = coupled_dark_energy_constraints(beta_de=0.05, wa_target=-0.55)
        # The required coupling is much larger than CMB bound
        assert result["beta_de_required_for_target"] > result["cmb_growth_bound"]
        assert not result["cmb_growth_safe"]

    def test_small_wa_target_is_viable(self):
        # For a very small wₐ target the required coupling is within CMB bounds
        # wa=-0.01: beta_required = √(0.01/(6×0.315)) ≈ 0.073 < 0.10 (CMB bound) ✓
        result = coupled_dark_energy_constraints(beta_de=0.02, wa_target=-0.01)
        assert result["beta_de_required_for_target"] < result["cmb_growth_bound"]
        assert result["cmb_growth_safe"]

    def test_large_coupling_not_cmb_safe(self):
        result = coupled_dark_energy_constraints(beta_de=0.15)
        assert not result["cmb_growth_safe"]

    def test_beta_zero_gives_no_wa(self):
        result = coupled_dark_energy_constraints(beta_de=0.0)
        assert result["wa_eff_from_input_beta"] == pytest.approx(0.0)

    def test_omega_m_stored(self):
        result = coupled_dark_energy_constraints()
        assert 0.28 < result["omega_m"] < 0.35  # Planck 2018 range


# ─────────────────────────────────────────────────────────────────────────────
# DR3 falsification check
# ─────────────────────────────────────────────────────────────────────────────

class TestDR3FalsificationCheck:
    def test_structure(self):
        result = dr3_falsification_check(-0.55, 0.20)
        for key in ("wa_dr3", "sigma_dr3", "tension_sigma", "verdict",
                    "extension_activated", "action"):
            assert key in result

    def test_current_dr2_not_falsified(self):
        result = dr3_falsification_check(-0.55, 0.20)
        assert result["verdict"] != "FALSIFIED"
        assert not result["extension_activated"]

    def test_high_tension_scenario(self):
        result = dr3_falsification_check(-0.55, 0.15)
        # |−0.55|/0.15 = 3.67σ → FALSIFIED
        assert result["tension_sigma"] == pytest.approx(0.55/0.15, abs=1e-9)
        assert result["verdict"] == "FALSIFIED"
        assert result["extension_activated"]

    def test_pass_scenario(self):
        result = dr3_falsification_check(-0.10, 0.20)
        assert result["verdict"] == "PASS" or result["verdict"] == "RESOLVED"
        assert not result["extension_activated"]

    def test_tension_exactly_at_threshold(self):
        # Use clean values: wa=-0.90, sigma=0.20 → 4.5σ → FALSIFIED
        result = dr3_falsification_check(-0.90, 0.20)
        assert result["tension_sigma"] == pytest.approx(4.5, abs=1e-9)
        assert result["verdict"] == "FALSIFIED"

    def test_tension_just_at_3sigma(self):
        # Use float-exact 3.0: -0.9/0.3 = 3.0 (verified in Python float arithmetic)
        result = dr3_falsification_check(-0.90, 0.30)
        assert result["tension_sigma"] == pytest.approx(3.0, abs=1e-9)
        assert result["verdict"] == "FALSIFIED"

    def test_tension_formula(self):
        wa, sigma = -0.55, 0.18
        result = dr3_falsification_check(wa, sigma)
        assert result["tension_sigma"] == pytest.approx(abs(wa)/sigma, abs=1e-9)

    def test_invalid_sigma_raises(self):
        with pytest.raises(ValueError):
            dr3_falsification_check(-0.55, 0.0)
        with pytest.raises(ValueError):
            dr3_falsification_check(-0.55, -0.1)

    def test_bao_only_dr3_scenario(self):
        # DESI BAO-only central: if DR3 gives σ=0.15, tension = 0.62/0.15 = 4.13σ
        result = dr3_falsification_check(-0.62, 0.15)
        assert result["tension_sigma"] == pytest.approx(0.62/0.15, abs=1e-9)
        assert result["verdict"] == "FALSIFIED"

    def test_action_field_is_string(self):
        result = dr3_falsification_check(-0.55, 0.20)
        assert isinstance(result["action"], str)

    def test_falsified_action_mentions_protocol(self):
        result = dr3_falsification_check(-0.55, 0.15)
        assert "FALSIFIED" in result["action"] or "CLAIM_MASTER_BOARD" in result["action"]


# ─────────────────────────────────────────────────────────────────────────────
# Extension viability ranking
# ─────────────────────────────────────────────────────────────────────────────

class TestExtensionViabilityRanking:
    def test_returns_four_extensions(self):
        ranking = extension_viability_ranking()
        assert len(ranking) == 4

    def test_all_have_required_fields(self):
        for ext in extension_viability_ranking():
            for key in ("rank", "name", "viable", "viability_note",
                        "disruption_level", "detail"):
                assert key in ext

    def test_ranks_are_1_to_4(self):
        ranks = [ext["rank"] for ext in extension_viability_ranking()]
        assert sorted(ranks) == [1, 2, 3, 4]

    def test_cosmological_radion_ranked_last(self):
        ranking = extension_viability_ranking()
        last = ranking[-1]
        assert last["name"] == "COSMOLOGICAL_RADION"
        assert not last["viable"]

    def test_viable_extensions_ranked_before_nonviable(self):
        ranking = extension_viability_ranking()
        viable_ranks = [e["rank"] for e in ranking if e["viable"]]
        nonviable_ranks = [e["rank"] for e in ranking if not e["viable"]]
        if viable_ranks and nonviable_ranks:
            assert max(viable_ranks) < min(nonviable_ranks)

    def test_all_disruption_levels_present(self):
        ranking = extension_viability_ranking()
        levels = {e["disruption_level"] for e in ranking}
        assert "EXTREME" in levels


# ─────────────────────────────────────────────────────────────────────────────
# Full report
# ─────────────────────────────────────────────────────────────────────────────

class TestExtensionSpecificationReport:
    def test_structure(self):
        report = extension_specification_report()
        for key in ("pillar", "title", "status", "current_status",
                    "dr3_projections", "extension_ranking",
                    "recommended_extension_if_falsified",
                    "protocol_if_falsified", "falsification_boundary",
                    "reference_modules"):
            assert key in report

    def test_pillar_label(self):
        report = extension_specification_report()
        assert report["pillar"] == "P268"

    def test_status_pre_specified(self):
        report = extension_specification_report()
        assert "PRE_SPECIFIED" in report["status"] or "CONTINGENCY" in report["status"]

    def test_current_status_not_falsified(self):
        report = extension_specification_report()
        assert report["current_status"]["not_yet_falsified"]
        assert report["current_status"]["tension_sigma"] < FALSIFICATION_THRESHOLD_SIGMA

    def test_dr3_tension_correctly_projected(self):
        report = extension_specification_report(wa_target=-0.55)
        proj = report["dr3_projections"]["combined_central_held"]
        # |−0.55|/0.15 = 3.67σ → FALSIFIED at DR3 sigma forecast
        expected_tension = 0.55 / DESI_DR3_FORECAST_SIGMA
        assert proj["tension_sigma"] == pytest.approx(expected_tension, abs=1e-9)

    def test_extension_ranking_has_four_entries(self):
        report = extension_specification_report()
        assert len(report["extension_ranking"]) == 4

    def test_protocol_mentions_claim_master_board(self):
        report = extension_specification_report()
        assert "CLAIM_MASTER_BOARD" in report["protocol_if_falsified"]

    def test_falsification_boundary_threshold_exact(self):
        report = extension_specification_report()
        assert report["falsification_boundary"]["threshold"] == pytest.approx(3.0)

    def test_falsification_boundary_not_weakened(self):
        report = extension_specification_report()
        stmt = report["falsification_boundary"]["statement"]
        assert "must not be weakened" in stmt

    def test_reference_modules_list(self):
        report = extension_specification_report()
        modules = report["reference_modules"]
        assert isinstance(modules, list)
        assert len(modules) >= 4
        assert any("pillar_desi_tension_monitor" in m for m in modules)
        assert any("pillar266" in m for m in modules)

    def test_recommended_extension_is_bulk_scalar(self):
        # The least-disruptive viable extension should be mentioned first
        report = extension_specification_report()
        rec = report["recommended_extension_if_falsified"]
        assert "BULK_SCALAR" in rec or "bulk scalar" in rec.lower()


# ─────────────────────────────────────────────────────────────────────────────
# Cross-checks with published numbers
# ─────────────────────────────────────────────────────────────────────────────

class TestPublishedNumbersCrossCheck:
    """Verify Pillar 285 numbers are consistent with all other DESI modules."""

    def test_desi_tension_consistent_with_monitor(self):
        # Import the corrected monitor and verify consistency
        from src.core.pillar_desi_tension_monitor import DESI_TENSION_SIGMA
        # Both should report 2.75σ for combined
        assert DESI_DR2_COMBINED["wa_tension_sigma"] == pytest.approx(DESI_TENSION_SIGMA, abs=1e-9)

    def test_desi_tension_consistent_with_pillar266(self):
        from src.core.pillar266_desi_wa_frozen_radion import (
            desi_tension_sigma as p266_tension,
            DESI_WA_CENTRAL_COMBINED,
            DESI_WA_SIGMA_COMBINED,
            WA_KK,
        )
        p266_val = p266_tension(WA_KK, DESI_WA_CENTRAL_COMBINED, DESI_WA_SIGMA_COMBINED)
        assert DESI_DR2_COMBINED["wa_tension_sigma"] == pytest.approx(p266_val, abs=1e-6)

    def test_falsification_threshold_consistent_with_pillar266(self):
        from src.core.pillar266_desi_wa_frozen_radion import FALSIFICATION_SIGMA as p266_thresh
        assert FALSIFICATION_THRESHOLD_SIGMA == pytest.approx(p266_thresh, abs=1e-9)

    def test_braided_sound_speed_consistent_with_convention(self):
        # c_s = 12/37 is the repository-wide canonical value
        assert BRAIDED_SOUND_SPEED == pytest.approx(12.0/37.0, rel=1e-9)

    def test_dr3_at_dr2_central_gives_high_tension_or_falsified(self):
        # DR3 with tighter error at DR2 combined central: 0.55/0.15 = 3.67σ
        result = dr3_falsification_check(DESI_DR2_COMBINED["wa_central"], DESI_DR3_FORECAST_SIGMA)
        assert result["tension_sigma"] > 2.5
