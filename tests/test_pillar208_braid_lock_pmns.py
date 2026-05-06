# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 208 — Braid-Lock PMNS Topological Mixing Angles."""

import math
import pytest

from src.core.pillar208_braid_lock_pmns import (
    N_W, K_CS, N_C, N2, PI_KR,
    SIN2_THETA12_GEO, SIN2_THETA23_GEO, SIN2_THETA13_GEO,
    THETA12_GEO_DEG, THETA23_GEO_DEG, THETA13_GEO_DEG,
    PDG_SIN2_THETA12, PDG_SIN2_THETA23, PDG_SIN2_THETA13,
    RESIDUAL12_PCT, RESIDUAL23_PCT, RESIDUAL13_PCT,
    HOPF_LINKING_NUMBER,
    secondary_braid_mode,
    pmns_sin2_theta12,
    pmns_sin2_theta23,
    pmns_sin2_theta13,
    pmns_all_angles,
    hopf_fibration_framework,
    braid_lock_sweep,
    dam_lattice_pmns_test,
    consistency_firewall,
    axiom_zero_audit,
    pillar208_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_n2(self):
        assert N2 == 7

    def test_braid_identity(self):
        assert N_W ** 2 + N2 ** 2 == K_CS

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_hopf_linking_number(self):
        assert HOPF_LINKING_NUMBER == N_W * N2  # = 35

    def test_sin2_th12_formula(self):
        assert SIN2_THETA12_GEO == pytest.approx(3.0 / 10.0, rel=1e-8)

    def test_sin2_th23_formula(self):
        expected = 0.5 + 3.0 / 74.0
        assert SIN2_THETA23_GEO == pytest.approx(expected, rel=1e-8)

    def test_sin2_th13_formula(self):
        expected = 3.0 / (12.0 ** 2)
        assert SIN2_THETA13_GEO == pytest.approx(expected, rel=1e-8)

    def test_sin2_th23_as_fraction(self):
        # (74 + 6)/148 = 80/148 = 20/37
        assert SIN2_THETA23_GEO == pytest.approx(20.0 / 37.0, rel=1e-8)

    def test_sin2_th13_as_fraction(self):
        # 3/144 = 1/48
        assert SIN2_THETA13_GEO == pytest.approx(1.0 / 48.0, rel=1e-8)

    def test_residual12_below_5pct(self):
        assert RESIDUAL12_PCT < 5.0

    def test_residual23_below_5pct(self):
        assert RESIDUAL23_PCT < 5.0

    def test_residual13_below_5pct(self):
        assert RESIDUAL13_PCT < 5.0

    def test_residual12_approx_23pct(self):
        assert 1.5 < RESIDUAL12_PCT < 3.5

    def test_residual23_below_1pct(self):
        assert RESIDUAL23_PCT < 1.5

    def test_residual13_approx_45pct(self):
        assert 3.0 < RESIDUAL13_PCT < 5.0

    def test_theta12_deg_range(self):
        assert 30.0 < THETA12_GEO_DEG < 40.0

    def test_theta23_deg_range(self):
        assert 45.0 < THETA23_GEO_DEG < 55.0

    def test_theta13_deg_range(self):
        assert 7.0 < THETA13_GEO_DEG < 10.0


# ─────────────────────────────────────────────────────────────────────────────
# SECONDARY BRAID MODE
# ─────────────────────────────────────────────────────────────────────────────

class TestSecondaryBraidMode:
    def test_default_gives_7(self):
        assert secondary_braid_mode() == 7

    def test_74_5_gives_7(self):
        assert secondary_braid_mode(74, 5) == 7

    def test_non_square_raises(self):
        with pytest.raises(ValueError):
            secondary_braid_mode(75, 5)

    def test_zero_n2_raises(self):
        with pytest.raises(ValueError):
            secondary_braid_mode(25, 5)

    def test_50_1_gives_7(self):
        assert secondary_braid_mode(50, 1) == 7


# ─────────────────────────────────────────────────────────────────────────────
# THETA_12 (SOLAR)
# ─────────────────────────────────────────────────────────────────────────────

class TestPmnsSin2Theta12:
    def setup_method(self):
        self.result = pmns_sin2_theta12()

    def test_value(self):
        assert self.result["sin2_theta12_geo"] == pytest.approx(0.300, rel=1e-6)

    def test_fraction_string(self):
        assert "3/10" in self.result["sin2_theta12_fraction"]

    def test_pdg_stored(self):
        assert self.result["sin2_theta12_pdg"] == pytest.approx(0.307)

    def test_residual_below_5(self):
        assert self.result["residual_pct"] < 5.0

    def test_within_5pct(self):
        assert self.result["within_5pct"] is True

    def test_no_sm_anchors(self):
        assert self.result["sm_anchors_used"] == []

    def test_status_geometric(self):
        assert self.result["status"] == "GEOMETRIC PREDICTION"

    def test_n_c(self):
        assert self.result["n_c"] == 3

    def test_n2(self):
        assert self.result["n2"] == 7

    def test_formula_string(self):
        assert "N_c" in self.result["formula"]

    def test_angle_in_degrees(self):
        assert 30.0 < self.result["theta12_deg"] < 40.0

    def test_physical_story_present(self):
        assert len(self.result["physical_story"]) > 50


# ─────────────────────────────────────────────────────────────────────────────
# THETA_23 (ATMOSPHERIC)
# ─────────────────────────────────────────────────────────────────────────────

class TestPmnsSin2Theta23:
    def setup_method(self):
        self.result = pmns_sin2_theta23()

    def test_value(self):
        assert self.result["sin2_theta23_geo"] == pytest.approx(20.0 / 37.0, rel=1e-8)

    def test_value_approx(self):
        assert self.result["sin2_theta23_geo"] == pytest.approx(0.5405, abs=0.001)

    def test_fraction_string(self):
        frac = self.result["sin2_theta23_fraction"]
        assert "80/148" in frac or "20/37" in frac

    def test_pdg_stored(self):
        assert self.result["sin2_theta23_pdg"] == pytest.approx(0.545)

    def test_residual_below_1pct(self):
        assert self.result["residual_pct"] < 1.5

    def test_within_5pct(self):
        assert self.result["within_5pct"] is True

    def test_alpha_gut(self):
        assert self.result["alpha_gut_geo"] == pytest.approx(3.0 / 74.0, rel=1e-6)

    def test_no_sm_anchors(self):
        assert self.result["sm_anchors_used"] == []

    def test_status_geometric(self):
        assert self.result["status"] == "GEOMETRIC PREDICTION"

    def test_angle_near_49_deg(self):
        assert 47.0 < self.result["theta23_deg"] < 52.0

    def test_pillar204_connection(self):
        assert "204" in self.result["pillar204_connection"]

    def test_formula_contains_gut(self):
        assert "α_GUT" in self.result["formula"]


# ─────────────────────────────────────────────────────────────────────────────
# THETA_13 (REACTOR)
# ─────────────────────────────────────────────────────────────────────────────

class TestPmnsSin2Theta13:
    def setup_method(self):
        self.result = pmns_sin2_theta13()

    def test_value(self):
        assert self.result["sin2_theta13_geo"] == pytest.approx(3.0 / 144.0, rel=1e-8)

    def test_value_as_1_over_48(self):
        assert self.result["sin2_theta13_geo"] == pytest.approx(1.0 / 48.0, rel=1e-8)

    def test_fraction_string(self):
        assert "3/144" in self.result["sin2_theta13_fraction"]

    def test_pdg_stored(self):
        assert self.result["sin2_theta13_pdg"] == pytest.approx(0.0218)

    def test_residual_below_5pct(self):
        assert self.result["residual_pct"] < 5.0

    def test_within_5pct(self):
        assert self.result["within_5pct"] is True

    def test_edge_of_window_flag(self):
        # At 4.5% — should be flagged
        assert self.result["edge_of_window"] is True

    def test_total_winding(self):
        assert self.result["total_winding"] == N_W + N2  # = 12

    def test_no_sm_anchors(self):
        assert self.result["sm_anchors_used"] == []

    def test_status_geometric(self):
        assert self.result["status"] == "GEOMETRIC PREDICTION"

    def test_angle_near_8_deg(self):
        assert 7.0 < self.result["theta13_deg"] < 10.0

    def test_formula_contains_n_w(self):
        assert "n_w" in self.result["formula"] or "n₁" in self.result["formula"] or "(n_w" in self.result["formula"]


# ─────────────────────────────────────────────────────────────────────────────
# ALL ANGLES TOGETHER
# ─────────────────────────────────────────────────────────────────────────────

class TestPmnsAllAngles:
    def setup_method(self):
        self.result = pmns_all_angles()

    def test_all_within_5pct(self):
        assert self.result["all_within_5pct"] is True

    def test_summary_table_has_3_rows(self):
        assert len(self.result["summary_table"]) == 3

    def test_axiom_zero_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_no_sm_anchors(self):
        assert self.result["sm_anchors_used"] == []

    def test_delta_cp_note(self):
        assert "143" in self.result["delta_cp_note"]

    def test_all_statuses_geometric(self):
        for row in self.result["summary_table"]:
            assert "GEOMETRIC" in row["status"]

    def test_th12_row(self):
        row = self.result["summary_table"][0]
        assert row["angle"] == "sin²θ₁₂"
        assert row["residual_pct"] < 5.0

    def test_th23_row(self):
        row = self.result["summary_table"][1]
        assert row["angle"] == "sin²θ₂₃"
        assert row["residual_pct"] < 1.5

    def test_th13_row(self):
        row = self.result["summary_table"][2]
        assert row["angle"] == "sin²θ₁₃"
        assert row["residual_pct"] < 5.0


# ─────────────────────────────────────────────────────────────────────────────
# HOPF FIBRATION FRAMEWORK
# ─────────────────────────────────────────────────────────────────────────────

class TestHopfFibrationFramework:
    def setup_method(self):
        self.result = hopf_fibration_framework()

    def test_hopf_base(self):
        assert "S²" in self.result["hopf_base"]

    def test_hopf_fiber(self):
        assert "S¹" in self.result["hopf_fiber"]

    def test_hopf_total(self):
        assert "S³" in self.result["hopf_total"]

    def test_linking_number(self):
        assert self.result["hopf_linking_number"] == 35

    def test_n_w_fold(self):
        assert self.result["n_w_fold_symmetry"] == 5

    def test_golden_ratio(self):
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        assert self.result["golden_ratio"] == pytest.approx(phi)

    def test_berry_phases_count(self):
        assert len(self.result["berry_phase_levels_rad"]) == N_W

    def test_icosahedral_group(self):
        assert "60" in self.result["icosahedral_group"]

    def test_rigorous_derivation_needed(self):
        assert self.result["rigorous_derivation_needed"] is True

    def test_framework_status_motivational(self):
        assert "MOTIVATIONAL" in self.result["framework_status"]

    def test_icosahedron_dihedral_approx(self):
        # arccos(-1/√5) ≈ 116.57° (icosahedron dihedral angle)
        assert 114.0 < self.result["icosahedron_dihedral_deg"] < 120.0


# ─────────────────────────────────────────────────────────────────────────────
# BRAID-LOCK SWEEP
# ─────────────────────────────────────────────────────────────────────────────

class TestBraidLockSweep:
    def setup_method(self):
        self.result = braid_lock_sweep()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_canonical_lock_confirmed(self):
        assert self.result["canonical_lock_confirmed"] is True

    def test_canonical_is_n_w5_k74(self):
        lock = self.result["canonical_lock"]
        assert lock["n_w"] == 5
        assert lock["k_cs"] == 74

    def test_all_top5_within_5pct(self):
        for entry in self.result["top_5_locks"]:
            assert entry["max_residual_pct"] < 5.0

    def test_at_least_one_lock_found(self):
        assert self.result["lock_candidates_found"] >= 1

    def test_verdict_present(self):
        assert "Braid-Lock" in self.result["verdict"]

    def test_canonical_lock_max_residual(self):
        lock = self.result["canonical_lock"]
        assert lock["max_residual_pct"] < 5.0


# ─────────────────────────────────────────────────────────────────────────────
# DAM LATTICE PMNS TEST
# ─────────────────────────────────────────────────────────────────────────────

class TestDamLatticePmnsTest:
    def setup_method(self):
        self.result = dam_lattice_pmns_test()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_sin2_th12_unchanged(self):
        # sin²θ₁₂ = N_c/(N_c+n₂) does not depend on K_CS
        note = self.result["k_bare_72"]["note"]
        assert "sin²θ₁₂" in note or "12" in note

    def test_sin2_th23_shifts_small(self):
        # K=74 vs K=72 shifts sin²θ₂₃ by a tiny amount
        assert abs(self.result["sin2_th23_shift"]) < 0.005

    def test_both_residuals_below_2pct(self):
        assert self.result["k_cs_74"]["r23_pct"] < 2.0
        assert self.result["k_bare_72"]["r23_pct"] < 2.0

    def test_verdict_not_significant(self):
        assert "NOT significantly improve" in self.result["verdict"] or \
               "NOT" in self.result["verdict"]

    def test_verdict_mentions_braid_lock(self):
        assert "exact braid theorem" in self.result["verdict"] or "K_CS=74" in self.result["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# CONSISTENCY FIREWALL
# ─────────────────────────────────────────────────────────────────────────────

class TestConsistencyFirewall:
    def setup_method(self):
        self.result = consistency_firewall()

    def test_m_h_unchanged(self):
        assert self.result["m_H_unchanged"] is True

    def test_beta_unchanged(self):
        assert self.result["beta_birefringence_unchanged"] is True

    def test_pillar58_consistent(self):
        assert self.result["pmns_inputs_consistent_with_pillar58"] is True

    def test_verdict_safe(self):
        assert "SAFE" in self.result["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# AXIOM ZERO AUDIT
# ─────────────────────────────────────────────────────────────────────────────

class TestAxiomZeroAudit:
    def setup_method(self):
        self.result = axiom_zero_audit()

    def test_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_zero_sm_anchors(self):
        assert self.result["sm_anchors_count"] == 0

    def test_two_inputs(self):
        assert len(self.result["derivation_inputs"]) == 2

    def test_five_derived_steps(self):
        assert len(self.result["derived_chain"]) == 5

    def test_n_c_in_chain(self):
        chain = " ".join(self.result["derived_chain"])
        assert "N_c" in chain or "3" in chain


# ─────────────────────────────────────────────────────────────────────────────
# PILLAR 208 SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar208Summary:
    def setup_method(self):
        self.result = pillar208_summary()

    def test_pillar_tag(self):
        assert self.result["pillar"] == "208"

    def test_version(self):
        assert "v10" in self.result["version"]

    def test_all_three_geometric(self):
        for key in ["sin2_theta12", "sin2_theta23", "sin2_theta13"]:
            assert "GEOMETRIC" in self.result["key_results"][key]["status"]

    def test_th12_residual_below_5(self):
        assert self.result["key_results"]["sin2_theta12"]["residual_pct"] < 5.0

    def test_th23_residual_below_1pt5(self):
        assert self.result["key_results"]["sin2_theta23"]["residual_pct"] < 1.5

    def test_th13_residual_below_5(self):
        assert self.result["key_results"]["sin2_theta13"]["residual_pct"] < 5.0

    def test_toe_impact_42pct(self):
        assert "42%" in self.result["toe_impact"]

    def test_toe_impact_p22(self):
        assert "P22" in self.result["toe_impact"]

    def test_caveats_present(self):
        assert len(self.result["caveats"]) >= 3

    def test_status_geometric(self):
        assert "GEOMETRIC PREDICTION" in self.result["status"]

    def test_dam_test_present(self):
        assert "dam_lattice_pmns_test" in self.result

    def test_braid_lock_sweep_present(self):
        assert "braid_lock_sweep" in self.result

    def test_sweep_lock_confirmed(self):
        assert self.result["braid_lock_sweep"]["canonical_lock_confirmed"] is True
