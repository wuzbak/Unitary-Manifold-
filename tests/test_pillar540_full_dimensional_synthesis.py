# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 540 — Full Dimensional Synthesis: 6D→11D Gap Resolution &
Architecture Understanding Certificate.

Coverage: all seven deliverables, the dimensional hierarchy matrix, the
terminal synthesis certificate, parametric variations, boundary conditions,
and regression guards.
"""

from __future__ import annotations

import math

import pytest

from src.core.pillar540_full_dimensional_synthesis import (
    # Metadata
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TRACK,
    EPSILON_T2Z3,
    R_T2_OVER_S1,
    ALLOWED_FINAL_STATUSES,
    # Deliverables
    case_g_dm231_t2z3_extension,
    cmb_amplitude_6d_correction,
    tensor_ratio_6d_7d_modification,
    higgs_naturalness_6d,
    baryogenesis_6d_architecture_understanding,
    build_dimensional_hierarchy_matrix,
    full_dimensional_synthesis_certificate,
)
from src.core.pillar539_dm31_wsv_architecture_limit import (
    CASE_F_DM31,
    CASE_F_TENSION,
    JUNO_DM31_CENTRAL,
)


# ── Module metadata ────────────────────────────────────────────────────────────


class TestPillar540Metadata:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 540

    def test_pillar_status(self):
        assert PILLAR_STATUS == "FULL_DIMENSIONAL_SYNTHESIS_CERTIFIED"

    def test_pillar_track_adjacent(self):
        assert "ADJACENT" in PILLAR_TRACK

    def test_epsilon_t2z3_magnitude(self):
        # ε = (1/74)^2 ≈ 1.83×10⁻⁴
        assert 1.5e-4 < EPSILON_T2Z3 < 2.5e-4

    def test_r_t2_over_s1_value(self):
        # R_6/R_S1 = 1/74
        assert abs(R_T2_OVER_S1 - 1.0 / 74.0) < 1e-12

    def test_epsilon_equals_ratio_squared(self):
        assert abs(EPSILON_T2Z3 - R_T2_OVER_S1 ** 2) < 1e-15

    def test_allowed_final_statuses_not_empty(self):
        assert len(ALLOWED_FINAL_STATUSES) > 0

    def test_awaits_observation_in_allowed(self):
        assert "AWAITS_OBSERVATION" in ALLOWED_FINAL_STATUSES

    def test_architecture_understood_in_allowed(self):
        assert "ARCHITECTURE_UNDERSTOOD" in ALLOWED_FINAL_STATUSES


# ── Deliverable 1: Case G ─────────────────────────────────────────────────────


class TestCaseGDm231:
    """Tests for Deliverable 1 — Case G T²/Z₃ modular extension."""

    @pytest.fixture(scope="class")
    def result(self):
        return case_g_dm231_t2z3_extension()

    def test_case_g_dm231_computes(self, result):
        """Case G runs and returns a dict with tension value."""
        assert isinstance(result, dict)
        assert "case_g_tension_sigma" in result

    def test_case_g_tension_finite_and_positive(self, result):
        """Tension is a real number > 0."""
        t = result["case_g_tension_sigma"]
        assert math.isfinite(t)
        assert t > 0.0

    def test_case_g_not_worse_than_case_f(self, result):
        """Case G tension ≤ Case F tension (stack monotonicity)."""
        assert result["case_g_tension_sigma"] <= CASE_F_TENSION + 1e-6

    def test_case_g_dm31_positive(self, result):
        assert result["case_g_dm31_ev2"] > 0.0

    def test_case_g_dm31_above_case_f(self, result):
        """6D shift moves Δm²₃₁ upward toward JUNO."""
        assert result["case_g_dm31_ev2"] >= CASE_F_DM31 - 1e-12

    def test_case_g_dm31_below_juno_central(self, result):
        """Gap not fully closed: still below JUNO central."""
        assert result["case_g_dm31_ev2"] < JUNO_DM31_CENTRAL

    def test_delta_dm31_positive(self, result):
        assert result["delta_dm31_ev2"] >= 0.0

    def test_delta_dm31_much_smaller_than_gap(self, result):
        """T²/Z₃ correction is tiny relative to the total gap."""
        gap = JUNO_DM31_CENTRAL - CASE_F_DM31
        assert result["delta_dm31_ev2"] < 0.01 * gap

    def test_label_in_allowed_set(self, result):
        assert result["label"] in ALLOWED_FINAL_STATUSES

    def test_final_status_matches_label(self, result):
        assert result["final_status"] == result["label"]

    def test_has_requires_for_closure(self, result):
        assert "requires_for_closure" in result
        assert len(result["requires_for_closure"]) > 10

    def test_has_honest_note(self, result):
        assert "honest_note" in result
        assert len(result["honest_note"]) > 20

    def test_juno_constants_preserved(self, result):
        assert result["juno_central_ev2"] == pytest.approx(2.411e-3, rel=1e-6)

    def test_case_f_tension_preserved(self, result):
        assert result["case_f_tension_sigma"] == pytest.approx(CASE_F_TENSION, rel=1e-6)

    def test_epsilon_t2z3_in_result(self, result):
        assert abs(result["epsilon_t2z3"] - EPSILON_T2Z3) < 1e-15

    def test_modular_weights_positive(self, result):
        assert result["modular_weight_gen1"] > 0.0
        assert result["modular_weight_gen3"] > 0.0

    def test_m_kk_t2_much_larger_than_rs1(self, result):
        """T²/Z₃ KK scale >> RS1 KK scale (by 1/r_ratio)."""
        assert result["m_kk_t2_gev"] > 1000.0  # >> 1042 GeV

    def test_tension_improvement_positive_for_6d_improved(self, result):
        """If 6D_DIMENSION_IMPROVED, tension improvement is positive."""
        if result["label"] == "6D_DIMENSION_IMPROVED":
            assert result["tension_improvement_sigma"] > 0.0

    @pytest.mark.parametrize("c_l1,c_l3", [
        (0.46, 0.56),
        (0.50, 0.52),
        (0.48, 0.54),  # canonical
    ])
    def test_parametric_case_g(self, c_l1, c_l3):
        r = case_g_dm231_t2z3_extension(c_l_gen1=c_l1, c_l_gen3=c_l3)
        assert math.isfinite(r["case_g_tension_sigma"])
        assert r["case_g_tension_sigma"] > 0.0
        assert r["case_g_dm31_ev2"] > 0.0

    def test_case_g_tension_below_3sigma(self, result):
        """Case G is not falsified (tension < 3σ)."""
        assert result["case_g_tension_sigma"] < 3.0

    def test_case_f_and_g_pillar_reference(self, result):
        assert result["prior_pillar"] == 539
        assert result["pillar"] == PILLAR_NUMBER


# ── Deliverable 2: CMB amplitude ──────────────────────────────────────────────


class TestCmbAmplitude6D:
    """Tests for Deliverable 2 — CMB amplitude 6D correction."""

    @pytest.fixture(scope="class")
    def result(self):
        return cmb_amplitude_6d_correction()

    def test_cmb_6d_correction_positive(self, result):
        """δA_s/A_s > 0 (correction in the right direction)."""
        assert result["delta_as_over_as"] > 0.0

    def test_cmb_6d_fraction_bounded(self, result):
        """Fractional improvement ∈ [0, 1)."""
        f = result["fraction_of_gap_improved"]
        assert 0.0 <= f < 1.0

    def test_cmb_label(self, result):
        assert result["label"] == "CMB_AMPLITUDE_6D_PARTIAL_IMPROVEMENT"

    def test_cmb_final_status(self, result):
        assert result["final_status"] in ALLOWED_FINAL_STATUSES

    def test_cmb_irreducible_floor_survives(self, result):
        assert result["irreducible_floor_survives"] is True

    def test_vol_t2_over_s1_positive(self, result):
        assert result["vol_t2_over_s1"] > 0.0

    def test_delta_mpl_frac_positive(self, result):
        assert result["delta_mpl_frac"] > 0.0

    def test_pct_improvement_tiny(self, result):
        """Improvement is tiny: < 0.1% of gap."""
        assert result["pct_of_gap_improved"] < 0.1

    def test_r_t2_over_s1_consistent(self, result):
        assert abs(result["r_t2_over_s1"] - R_T2_OVER_S1) < 1e-14

    def test_suppression_gap_fraction_positive(self, result):
        assert result["suppression_gap_fraction"] > 0.0

    def test_delta_as_much_smaller_than_unity(self, result):
        """The 6D correction to A_s is << 1 (not an overestimate)."""
        assert result["delta_as_over_as"] < 1.0

    def test_has_prior_label(self, result):
        assert result["prior_label"] == "CMB_AMPLITUDE_ARCHITECTURE_LIMIT_CERTIFIED"

    @pytest.mark.parametrize("sup", [4.0, 5.0, 7.0])
    def test_parametric_cmb(self, sup):
        r = cmb_amplitude_6d_correction(suppression_factor_mid=sup)
        assert r["delta_as_over_as"] > 0.0
        assert 0.0 <= r["fraction_of_gap_improved"] < 1.0


# ── Deliverable 3: Tensor ratio ───────────────────────────────────────────────


class TestTensorRatio6D7D:
    """Tests for Deliverable 3 — Tensor ratio 6D+7D modification."""

    @pytest.fixture(scope="class")
    def result(self):
        return tensor_ratio_6d_7d_modification()

    def test_tensor_ratio_6d_correction_finite(self, result):
        """δr^{6D} is finite and computable."""
        assert math.isfinite(result["delta_r_6d"])

    def test_tensor_ratio_not_worsened(self, result):
        """6D correction does not increase r."""
        assert result["r_corrected"] <= result["r_nlo_prior"] + 1e-15

    def test_delta_r_6d_zero_flat_torus(self, result):
        """T² is flat: no Ricci correction → δr_{6D} = 0 exactly."""
        assert result["delta_r_6d"] == 0.0

    def test_delta_r_7d_positive(self, result):
        """7D discrete torsion correction is positive (non-negative)."""
        assert result["7d_discrete_torsion"]["delta_r_7d"] >= 0.0

    def test_delta_r_7d_tiny(self, result):
        """7D correction is essentially zero (~10⁻³¹)."""
        assert result["7d_discrete_torsion"]["delta_r_7d"] < 1e-20

    def test_r_corrected_matches_prior(self, result):
        """r_corrected ≈ r_NLO within machine epsilon (no effective change)."""
        assert abs(result["r_corrected"] - result["r_nlo_prior"]) < 1e-25

    def test_label_is_irreducible(self, result):
        assert result["label"] == "TENSOR_RATIO_6D_CONFIRMED_IRREDUCIBLE"

    def test_final_status_in_allowed(self, result):
        assert result["final_status"] in ALLOWED_FINAL_STATUSES

    def test_act_dr6_bound_recorded(self, result):
        assert result["act_dr6_bound"] == pytest.approx(0.016, rel=1e-6)

    def test_has_requires_for_closure(self, result):
        assert "requires_for_closure" in result
        assert len(result["requires_for_closure"]) > 0

    def test_has_honest_note(self, result):
        assert "honest_note" in result

    @pytest.mark.parametrize("r_nlo", [0.030, 0.0312, 0.0315])
    def test_parametric_tensor(self, r_nlo):
        r = tensor_ratio_6d_7d_modification(r_nlo=r_nlo)
        assert math.isfinite(r["r_corrected"])
        assert r["r_corrected"] <= r_nlo + 1e-15

    def test_cs_suppression_magnitude(self, result):
        cs = result["7d_discrete_torsion"]["cs_suppression"]
        assert 1e-35 < cs < 1e-25  # ~(1 TeV / M_Pl)^2 ≈ 2e-31


# ── Deliverable 4: Higgs naturalness ─────────────────────────────────────────


class TestHiggsNaturalness6D:
    """Tests for Deliverable 4 — Higgs naturalness 6D fixed-point geometry."""

    @pytest.fixture(scope="class")
    def result(self):
        return higgs_naturalness_6d()

    def test_higgs_naturalness_6d_tuning_positive(self, result):
        """Δ^{6D} > 0."""
        assert result["tuning_delta_6d"] > 0.0

    def test_higgs_naturalness_6d_status_string(self, result):
        """Status is DERIVED_PARTIAL_6D or ARCHITECTURE_UNDERSTOOD."""
        assert result["label"] in ("DERIVED_PARTIAL_6D", "ARCHITECTURE_UNDERSTOOD")

    def test_higgs_naturalness_6d_final_status_in_allowed(self, result):
        assert result["final_status"] in ALLOWED_FINAL_STATUSES

    def test_xi_6d_positive(self, result):
        assert result["xi_6d"] > 0.0

    def test_xi_6d_order_1_sixth(self, result):
        """ξ_{6D} ≈ 0.18 (near 1/6 but modified by brane factors)."""
        assert 0.05 < result["xi_6d"] < 0.5

    def test_theta_hr_finite(self, result):
        assert math.isfinite(result["theta_hr_rad"])

    def test_m_h_6d_positive(self, result):
        assert result["m_h_6d_gev"] > 0.0

    def test_m_h_6d_in_physical_range(self, result):
        """Physical Higgs mass in 6D is in a reasonable range."""
        assert 50.0 < result["m_h_6d_gev"] < 400.0

    def test_delta_mh2_top_positive(self, result):
        assert result["delta_mh2_top_gev2"] > 0.0

    def test_delta_mh2_rad_non_negative(self, result):
        assert result["delta_mh2_rad_gev2"] >= 0.0

    def test_total_delta_mh2_positive(self, result):
        assert result["total_delta_mh2_gev2"] > 0.0

    def test_derived_partial_flag_consistent(self, result):
        """derived_partial flag is consistent with Δ < 100."""
        if result["tuning_delta_6d"] < 100.0:
            assert result["derived_partial"] is True
            assert result["label"] == "DERIVED_PARTIAL_6D"
        else:
            assert result["derived_partial"] is False
            assert result["label"] == "ARCHITECTURE_UNDERSTOOD"

    def test_a3_prior_label(self, result):
        assert result["a3_prior_label"] == "ARCHITECTURE_LIMIT_CERTIFIED"

    def test_a3_new_label_recorded(self, result):
        assert result["a3_new_label"] in ALLOWED_FINAL_STATUSES

    def test_has_requires_for_closure(self, result):
        assert "requires_for_closure" in result

    def test_m_kk_gev_reasonable(self, result):
        """M_KK ≈ 1042 GeV."""
        assert 500.0 < result["m_kk_gev"] < 5000.0


# ── Deliverable 5: Baryogenesis ───────────────────────────────────────────────


class TestBaryogenesis6D:
    """Tests for Deliverable 5 — Baryogenesis 6D architecture understanding."""

    @pytest.fixture(scope="class")
    def result(self):
        return baryogenesis_6d_architecture_understanding()

    def test_baryogenesis_6d_classified(self, result):
        """Returns TESTABLE_6D_MECHANISM label."""
        assert result["label"] == "TESTABLE_6D_MECHANISM"

    def test_final_status_in_allowed(self, result):
        assert result["final_status"] in ALLOWED_FINAL_STATUSES

    def test_testable_flag_true(self, result):
        assert result["testable"] is True

    def test_nedm_sns_2028_flag(self, result):
        assert result["nedm_prediction"]["testable_sns_2028"] is True

    def test_d_n_positive(self, result):
        assert result["nedm_prediction"]["d_n_central_ecm"] > 0.0

    def test_d_n_above_sns_sensitivity(self, result):
        assert result["nedm_prediction"]["above_sns_sensitivity"] is True

    def test_d_n_below_current_bound(self, result):
        assert result["nedm_prediction"]["below_current_bound"] is True

    def test_field_content_recorded(self, result):
        fc = result["field_content"]
        assert "particle" in fc
        assert "mass_gev" in fc
        assert fc["mass_gev"] > 0.0

    def test_geometric_basis_recorded(self, result):
        gb = result["geometric_basis"]
        assert "mechanism" in gb
        assert "T²/Z₃" in gb["mechanism"]

    def test_baryon_asymmetry_eta_b_positive(self, result):
        ba = result["baryon_asymmetry"]
        assert ba["eta_b_observed"] > 0.0
        assert ba["eta_b_6d_estimate"] > 0.0

    def test_prior_label_is_architecture_limit(self, result):
        assert result["prior_label"] == "ARCHITECTURE_LIMIT_CERTIFIED"

    def test_falsification_condition_defined(self, result):
        assert "falsification_condition" in result
        assert len(result["falsification_condition"]) > 0

    @pytest.mark.parametrize("m_sig", [500.0, 650.0, 800.0])
    def test_parametric_baryogenesis(self, m_sig):
        r = baryogenesis_6d_architecture_understanding(m_sigma_gev=m_sig)
        assert r["label"] == "TESTABLE_6D_MECHANISM"
        assert r["nedm_prediction"]["d_n_central_ecm"] > 0.0


# ── Deliverable 6: Dimensional hierarchy matrix ───────────────────────────────


class TestDimensionalHierarchyMatrix:
    """Tests for Deliverable 6 — Dimensional hierarchy matrix."""

    @pytest.fixture(scope="class")
    def result(self):
        return build_dimensional_hierarchy_matrix()

    REQUIRED_GAPS = [
        "CMB_AMPLITUDE", "DM231", "TENSOR_RATIO",
        "HIGGS_NATURALNESS", "BARYOGENESIS", "DESI_WA", "NW_UNIQUENESS",
    ]
    REQUIRED_DIMS = ["5D", "6D", "7D", "8D", "9D", "10D", "11D"]

    def test_dimensional_hierarchy_matrix_keys(self, result):
        """All 7 gaps present."""
        for gap in self.REQUIRED_GAPS:
            assert gap in result["matrix"], f"Gap {gap} missing from matrix"

    def test_dimensional_hierarchy_matrix_all_dims(self, result):
        """Each entry has 5D through 11D keys."""
        for gap in self.REQUIRED_GAPS:
            entry = result["matrix"][gap]
            for dim in self.REQUIRED_DIMS:
                assert dim in entry, f"Dimension {dim} missing from gap {gap}"

    def test_n_gaps_correct(self, result):
        assert result["n_gaps"] == 7

    def test_dimensions_list_correct(self, result):
        assert result["dimensions"] == self.REQUIRED_DIMS

    def test_all_final_statuses_populated(self, result):
        for gap in self.REQUIRED_GAPS:
            fs = result["matrix"][gap].get("final_status")
            assert fs is not None, f"final_status missing for {gap}"
            assert len(str(fs)) > 0

    def test_desi_wa_marked_awaits_observation(self, result):
        """DESI gap flagged as AWAITS_OBSERVATION."""
        assert result["matrix"]["DESI_WA"]["final_status"] == "AWAITS_OBSERVATION"

    def test_nw_uniqueness_marked_awaits_observation(self, result):
        """n_w uniqueness gap flagged as AWAITS_OBSERVATION."""
        assert result["matrix"]["NW_UNIQUENESS"]["final_status"] == "AWAITS_OBSERVATION"

    def test_desi_wa_awaits_field(self, result):
        assert "awaits" in result["matrix"]["DESI_WA"]
        assert "2027" in result["matrix"]["DESI_WA"]["awaits"]

    def test_nw_uniqueness_awaits_litebird(self, result):
        assert "awaits" in result["matrix"]["NW_UNIQUENESS"]
        assert "LiteBIRD" in result["matrix"]["NW_UNIQUENESS"]["awaits"] or \
               "2032" in result["matrix"]["NW_UNIQUENESS"]["awaits"]

    def test_summary_structure(self, result):
        assert "summary" in result
        summary = result["summary"]
        for key in ("6d_dimension_improved", "architecture_understood",
                    "testable_6d_mechanism", "derived_partial_6d",
                    "awaits_observation", "irreducible_floor_confirmed"):
            assert key in summary

    def test_cmb_irreducible_floor_recorded(self, result):
        entry = result["matrix"]["CMB_AMPLITUDE"]
        assert entry.get("irreducible_floor_survives") is True

    def test_all_5d_entries_non_empty(self, result):
        for gap in self.REQUIRED_GAPS:
            assert len(str(result["matrix"][gap]["5D"])) > 5

    def test_all_6d_entries_non_empty(self, result):
        for gap in self.REQUIRED_GAPS:
            assert len(str(result["matrix"][gap]["6D"])) > 5


# ── Deliverable 7: Terminal synthesis certificate ─────────────────────────────


class TestTerminalCertificate:
    """Tests for Deliverable 7 — Terminal synthesis certificate."""

    @pytest.fixture(scope="class")
    def cert(self):
        return full_dimensional_synthesis_certificate()

    REQUIRED_DELIVERABLE_KEYS = [
        "1_case_g_dm231",
        "2_cmb_amplitude_6d",
        "3_tensor_ratio_6d_7d",
        "4_higgs_naturalness_6d",
        "5_baryogenesis_6d",
        "6_dimensional_hierarchy_matrix",
        "7_gap_classifications",
    ]

    def test_terminal_certificate_structure(self, cert):
        """All 7 deliverables present."""
        for key in self.REQUIRED_DELIVERABLE_KEYS:
            assert key in cert["deliverables"], f"Deliverable {key} missing"

    def test_terminal_certificate_no_hardgate_change(self, cert):
        """`no_hardgate_score_change` is True."""
        assert cert["no_hardgate_score_change"] is True

    def test_terminal_certificate_toe_score_unchanged(self, cert):
        """ToE score = '28/28'."""
        assert cert["toe_score"] == "28/28"

    def test_all_gaps_classified(self, cert):
        """Every gap has a final_status in the allowed set."""
        assert cert["all_gaps_classified"] is True

    def test_all_understood_have_closure_requirement(self, cert):
        assert cert["all_understood_have_closure_requirement"] is True

    def test_certificate_status(self, cert):
        assert cert["status"] == "FULL_DIMENSIONAL_SYNTHESIS_CERTIFIED"

    def test_certificate_pillar_number(self, cert):
        assert cert["pillar"] == 540

    def test_what_6d_11d_achieves_nonempty(self, cert):
        assert len(cert["what_6d_11d_achieves"]) >= 4

    def test_what_6d_11d_cannot_achieve_nonempty(self, cert):
        assert len(cert["what_6d_11d_cannot_achieve"]) >= 4

    def test_epistemic_summary_nonempty(self, cert):
        assert len(cert["epistemic_summary"]) > 100

    def test_next_sprint_pillar_slot(self, cert):
        assert cert["next_sprint_pillar_slot"] == 541

    def test_gap_classifications_all_in_allowed(self, cert):
        """All gap final_statuses are in the allowed set."""
        for entry in cert["deliverables"]["7_gap_classifications"]["classifications"]:
            assert entry["in_allowed_set"] is True, (
                f"Gap {entry['gap']} has final_status "
                f"{entry['final_status']} not in allowed set"
            )

    def test_desi_wa_in_classifications(self, cert):
        gaps = [
            e["gap"]
            for e in cert["deliverables"]["7_gap_classifications"]["classifications"]
        ]
        assert "DESI_WA" in gaps

    def test_nw_uniqueness_in_classifications(self, cert):
        gaps = [
            e["gap"]
            for e in cert["deliverables"]["7_gap_classifications"]["classifications"]
        ]
        assert "NW_UNIQUENESS" in gaps

    def test_architecture_understood_has_closure_requirement(self, cert):
        """Every ARCHITECTURE_UNDERSTOOD gap has a `requires_for_closure` key."""
        for entry in cert["deliverables"]["7_gap_classifications"]["classifications"]:
            if entry["final_status"] == "ARCHITECTURE_UNDERSTOOD":
                assert "requires_for_closure" in entry, (
                    f"Gap {entry['gap']} is ARCHITECTURE_UNDERSTOOD but "
                    "lacks requires_for_closure"
                )

    def test_desi_wa_marked_awaits_observation(self, cert):
        for entry in cert["deliverables"]["7_gap_classifications"]["classifications"]:
            if entry["gap"] == "DESI_WA":
                assert entry["final_status"] == "AWAITS_OBSERVATION"

    def test_nw_uniqueness_marked_awaits_observation(self, cert):
        for entry in cert["deliverables"]["7_gap_classifications"]["classifications"]:
            if entry["gap"] == "NW_UNIQUENESS":
                assert entry["final_status"] == "AWAITS_OBSERVATION"

    def test_case_g_tension_in_deliverable(self, cert):
        assert "tension_sigma" in cert["deliverables"]["1_case_g_dm231"]

    def test_higgs_tuning_in_deliverable(self, cert):
        assert "tuning_delta_6d" in cert["deliverables"]["4_higgs_naturalness_6d"]

    def test_baryogenesis_testable_in_deliverable(self, cert):
        d5 = cert["deliverables"]["5_baryogenesis_6d"]
        assert d5["testable"] is True

    def test_dimensional_matrix_has_7_gaps(self, cert):
        assert cert["deliverables"]["6_dimensional_hierarchy_matrix"]["n_gaps"] == 7

    def test_upstream_pillars_listed(self, cert):
        assert len(cert["upstream_pillars"]) > 0
        assert 539 in cert["upstream_pillars"]

    def test_sprint_label(self, cert):
        assert cert["sprint"] == "v18.4"


# ── Cross-deliverable consistency ─────────────────────────────────────────────


class TestCrossDeliverableConsistency:
    """Cross-deliverable regression and consistency checks."""

    @pytest.fixture(scope="class")
    def cert(self):
        return full_dimensional_synthesis_certificate()

    def test_case_g_tension_below_case_f(self, cert):
        """Case G tension < Case F tension (stack monotonicity preserved)."""
        d1 = cert["deliverables"]["1_case_g_dm231"]
        assert d1["tension_sigma"] <= CASE_F_TENSION + 1e-6

    def test_cmb_6d_fraction_small(self, cert):
        """CMB 6D improvement is infinitesimal (< 0.1% of gap)."""
        d2 = cert["deliverables"]["2_cmb_amplitude_6d"]
        assert d2["pct_of_gap_improved"] < 0.1

    def test_tensor_r_unchanged(self, cert):
        """Tensor ratio r_corrected ≈ r_NLO = 0.0315."""
        d3 = cert["deliverables"]["3_tensor_ratio_6d_7d"]
        assert abs(d3["r_corrected"] - 0.0315) < 1e-10

    def test_higgs_label_in_allowed(self, cert):
        d4 = cert["deliverables"]["4_higgs_naturalness_6d"]
        assert d4["status"] in ALLOWED_FINAL_STATUSES

    def test_baryogenesis_label_correct(self, cert):
        d5 = cert["deliverables"]["5_baryogenesis_6d"]
        assert d5["status"] == "TESTABLE_6D_MECHANISM"

    def test_n_gap_classifications_equals_n_gaps(self, cert):
        n_class = cert["deliverables"]["7_gap_classifications"]["n_gaps"]
        n_matrix = cert["deliverables"]["6_dimensional_hierarchy_matrix"]["n_gaps"]
        assert n_class == n_matrix == 7

    def test_no_hardgate_score_change_preserved(self, cert):
        assert cert["no_hardgate_score_change"] is True

    def test_toe_score_preserved(self, cert):
        assert cert["toe_score"] == "28/28"

    def test_full_cert_idempotent(self):
        """Calling the certificate twice gives the same gap count."""
        cert1 = full_dimensional_synthesis_certificate()
        cert2 = full_dimensional_synthesis_certificate()
        assert cert1["all_gaps_classified"] == cert2["all_gaps_classified"]
        assert cert1["toe_score"] == cert2["toe_score"]

    def test_dimensional_matrix_consistent_with_deliverables(self, cert):
        """The CMB entry in the matrix matches the CMB deliverable label."""
        matrix = cert["dimensional_hierarchy_matrix"]
        assert matrix["CMB_AMPLITUDE"]["final_status"] == (
            cert["deliverables"]["2_cmb_amplitude_6d"]["status"]
        )

    def test_pillar_number_consistent(self, cert):
        assert cert["pillar"] == PILLAR_NUMBER

    def test_substack_post_field(self, cert):
        assert "#265" in cert["substack_post"]
