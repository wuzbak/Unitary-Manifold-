# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 525 — JUNO 2026 falsification response module.

Tests cover:
  - JUNO 2026 data anchor constants and structure
  - Correction chain: RGE running, seesaw, KK tower negligibility
  - Projection function correctness and bounds
  - Falsification verdict structure and values
  - Full report generation
  - Key numerical results (honest open problem documentation)
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar525_juno_2026_falsification_response import (
    # Data anchor
    JUNO_2026_RELEASE,
    # Constants
    DM2_31_PDG_EV2,
    DM2_31_2NLO_EV2,
    DM2_31_2NLO_RESIDUAL_PCT,
    M_KK_GEV,
    Y_TAU,
    V_HIGGS_GEV,
    M_R_GEV,
    THETA_23_DEG,
    THETA_13_DEG,
    P_R_PMNS_MAX,
    DELTA_RGE,
    SEESAW_BASE,
    DELTA_SEESAW_MAX,
    DM2_31_PROJECTED_EV2,
    DM2_31_PROJECTED_RESIDUAL_PCT,
    JUNO_TENSION_2NLO_SIGMA,
    JUNO_TENSION_PROJECTED_SIGMA,
    PILLAR_STATUS,
    ADMISSION_TAG,
    # Functions
    rge_running_correction,
    seesaw_correction_at_p_r,
    kk_tower_correction_negligible,
    project_dm31_from_2nlo,
    juno_2026_falsification_verdict,
    juno_2026_full_report,
)


# ─────────────────────────────────────────────────────────────────────────
# JUNO 2026 data anchor
# ─────────────────────────────────────────────────────────────────────────

class TestJuno2026DataAnchor:
    def test_juno_release_is_dict(self):
        assert isinstance(JUNO_2026_RELEASE, dict)

    def test_juno_required_keys(self):
        for key in ("release", "year", "reference", "dm2_31_central_eV2",
                    "dm2_31_sigma_frac", "dm2_31_sigma_abs_eV2",
                    "exposure_days", "status", "note", "verdicts"):
            assert key in JUNO_2026_RELEASE, f"Missing key: {key}"

    def test_juno_central_value(self):
        assert abs(JUNO_2026_RELEASE["dm2_31_central_eV2"] - 2.411e-3) < 1e-15

    def test_juno_sigma_frac(self):
        # 0.81% reported in Nature
        assert abs(JUNO_2026_RELEASE["dm2_31_sigma_frac"] - 0.008125) < 1e-10

    def test_juno_sigma_abs_consistency(self):
        central = JUNO_2026_RELEASE["dm2_31_central_eV2"]
        frac = JUNO_2026_RELEASE["dm2_31_sigma_frac"]
        expected_abs = central * frac
        assert abs(JUNO_2026_RELEASE["dm2_31_sigma_abs_eV2"] - expected_abs) < 1e-15

    def test_juno_exposure_days(self):
        assert JUNO_2026_RELEASE["exposure_days"] == 59

    def test_juno_year(self):
        assert JUNO_2026_RELEASE["year"] == 2026

    def test_juno_status_active_tracking(self):
        assert JUNO_2026_RELEASE["status"] == "ACTIVE_TRACKING"

    def test_juno_verdicts_structure(self):
        v = JUNO_2026_RELEASE["verdicts"]
        assert "um_2nlo_bare" in v
        assert "um_best_attempt_projection" in v
        assert "overall_pillar17_status" in v

    def test_juno_verdicts_excluded(self):
        v = JUNO_2026_RELEASE["verdicts"]
        assert "EXCLUDED" in v["um_2nlo_bare"]
        assert "EXCLUDED" in v["um_best_attempt_projection"]

    def test_juno_verdicts_honest_open_problem(self):
        assert JUNO_2026_RELEASE["verdicts"]["overall_pillar17_status"] == "HONEST_OPEN_PROBLEM"

    def test_juno_precision_better_than_pdg(self):
        # JUNO 0.81% beats PDG 1.3%
        assert JUNO_2026_RELEASE["dm2_31_sigma_frac"] < 0.013


# ─────────────────────────────────────────────────────────────────────────
# Physical constants
# ─────────────────────────────────────────────────────────────────────────

class TestPhysicalConstants:
    def test_pdg_value(self):
        assert abs(DM2_31_PDG_EV2 - 2.453e-3) < 1e-15

    def test_2nlo_derived_correctly(self):
        expected = 2.453e-3 * (1.0 - 0.0687)
        assert abs(DM2_31_2NLO_EV2 - expected) < 1e-14

    def test_2nlo_below_juno(self):
        assert DM2_31_2NLO_EV2 < JUNO_2026_RELEASE["dm2_31_central_eV2"]

    def test_2nlo_residual_pct_positive(self):
        # JUNO > 2NLO, so residual should be positive
        assert DM2_31_2NLO_RESIDUAL_PCT > 0.0

    def test_2nlo_residual_pct_value(self):
        juno = JUNO_2026_RELEASE["dm2_31_central_eV2"]
        expected = (juno - DM2_31_2NLO_EV2) / juno * 100.0
        assert abs(DM2_31_2NLO_RESIDUAL_PCT - expected) < 1e-10

    def test_2nlo_residual_about_5pct(self):
        # ~5.2% gap from JUNO
        assert 4.0 < DM2_31_2NLO_RESIDUAL_PCT < 7.0

    def test_m_kk_gev_value(self):
        assert abs(M_KK_GEV - 1000.0) < 1e-10

    def test_v_higgs_gev(self):
        assert abs(V_HIGGS_GEV - 246.22) < 1e-5

    def test_theta_23_physical(self):
        assert 35.0 < THETA_23_DEG < 55.0

    def test_theta_13_physical(self):
        assert 5.0 < THETA_13_DEG < 15.0

    def test_p_r_pmns_max_range(self):
        # Should be sin²(42.2°)×cos²(8.6°) ≈ 0.441
        assert 0.35 < P_R_PMNS_MAX < 0.60

    def test_p_r_pmns_max_formula(self):
        expected = (
            math.sin(math.radians(THETA_23_DEG)) ** 2
            * math.cos(math.radians(THETA_13_DEG)) ** 2
        )
        assert abs(P_R_PMNS_MAX - expected) < 1e-12


# ─────────────────────────────────────────────────────────────────────────
# Module-level pre-computed values
# ─────────────────────────────────────────────────────────────────────────

class TestPrecomputedValues:
    def test_delta_rge_positive(self):
        assert DELTA_RGE > 0.0

    def test_delta_rge_small(self):
        # Should be ~4e-5 (much smaller than gap)
        assert 1e-5 < DELTA_RGE < 1e-3

    def test_seesaw_base_value(self):
        expected = (V_HIGGS_GEV / M_R_GEV) ** 2
        assert abs(SEESAW_BASE - expected) < 1e-12

    def test_seesaw_base_about_6pct(self):
        assert 0.05 < SEESAW_BASE < 0.08

    def test_delta_seesaw_max_positive(self):
        assert DELTA_SEESAW_MAX > 0.0

    def test_delta_seesaw_max_about_2_7pct(self):
        assert 0.020 < DELTA_SEESAW_MAX < 0.035

    def test_projected_ev2_above_2nlo(self):
        assert DM2_31_PROJECTED_EV2 > DM2_31_2NLO_EV2

    def test_projected_ev2_below_juno(self):
        assert DM2_31_PROJECTED_EV2 < JUNO_2026_RELEASE["dm2_31_central_eV2"]

    def test_projected_ev2_in_falsification_window(self):
        assert 2.2e-3 <= DM2_31_PROJECTED_EV2 <= 2.7e-3

    def test_projected_residual_positive(self):
        assert DM2_31_PROJECTED_RESIDUAL_PCT > 0.0

    def test_projected_residual_about_2_7pct(self):
        assert 1.5 < DM2_31_PROJECTED_RESIDUAL_PCT < 4.5

    def test_bare_tension_above_6sigma(self):
        assert JUNO_TENSION_2NLO_SIGMA > 6.0

    def test_bare_tension_value_approx(self):
        # ≈ 6.46σ
        assert 5.5 < JUNO_TENSION_2NLO_SIGMA < 8.0

    def test_projected_tension_above_3sigma(self):
        # Still EXCLUDED after all corrections
        assert JUNO_TENSION_PROJECTED_SIGMA > 3.0

    def test_projected_tension_below_bare(self):
        # Projection improved (reduced tension)
        assert JUNO_TENSION_PROJECTED_SIGMA < JUNO_TENSION_2NLO_SIGMA

    def test_pillar_status_string(self):
        assert PILLAR_STATUS == "HONEST_OPEN_PROBLEM"

    def test_admission_tag_string(self):
        assert ADMISSION_TAG == "JUNO_2026_P17_EXCLUDED"


# ─────────────────────────────────────────────────────────────────────────
# rge_running_correction()
# ─────────────────────────────────────────────────────────────────────────

class TestRGECorrection:
    def test_rge_returns_float(self):
        assert isinstance(rge_running_correction(), float)

    def test_rge_positive(self):
        assert rge_running_correction() > 0.0

    def test_rge_matches_module_constant(self):
        assert abs(rge_running_correction() - DELTA_RGE) < 1e-12

    def test_rge_larger_tau_yukawa_gives_larger_correction(self):
        d1 = rge_running_correction(y_tau=0.01)
        d2 = rge_running_correction(y_tau=0.02)
        assert d2 > d1

    def test_rge_larger_mkk_gives_larger_log(self):
        d1 = rge_running_correction(m_kk_gev=1000.0)
        d2 = rge_running_correction(m_kk_gev=10000.0)
        assert d2 > d1

    def test_rge_formula_correctness(self):
        # Manual check: δ = y²/(8π²) × ln(M_KK eV / m_atm)
        y = Y_TAU
        m_kk_ev = M_KK_GEV * 1e9
        m_atm = math.sqrt(DM2_31_2NLO_EV2)
        expected = (y ** 2) / (8 * math.pi ** 2) * math.log(m_kk_ev / m_atm)
        assert abs(rge_running_correction() - expected) < 1e-12


# ─────────────────────────────────────────────────────────────────────────
# seesaw_correction_at_p_r()
# ─────────────────────────────────────────────────────────────────────────

class TestSeesawCorrection:
    def test_seesaw_zero_at_p_r_zero(self):
        assert seesaw_correction_at_p_r(0.0) == 0.0

    def test_seesaw_positive_for_positive_p_r(self):
        assert seesaw_correction_at_p_r(0.5) > 0.0

    def test_seesaw_linear_in_p_r(self):
        d1 = seesaw_correction_at_p_r(0.2)
        d2 = seesaw_correction_at_p_r(0.4)
        assert abs(d2 - 2 * d1) < 1e-12

    def test_seesaw_at_pmns_max(self):
        result = seesaw_correction_at_p_r(P_R_PMNS_MAX)
        assert abs(result - DELTA_SEESAW_MAX) < 1e-12

    def test_seesaw_formula(self):
        p_r = 0.35
        expected = p_r * (V_HIGGS_GEV / M_R_GEV) ** 2
        assert abs(seesaw_correction_at_p_r(p_r) - expected) < 1e-12

    def test_seesaw_max_about_2_7pct(self):
        assert 0.020 < seesaw_correction_at_p_r(P_R_PMNS_MAX) < 0.035


# ─────────────────────────────────────────────────────────────────────────
# kk_tower_correction_negligible()
# ─────────────────────────────────────────────────────────────────────────

class TestKKTowerNegligible:
    def test_returns_dict(self):
        assert isinstance(kk_tower_correction_negligible(), dict)

    def test_required_keys(self):
        r = kk_tower_correction_negligible()
        for key in ("epsilon_kk", "tower_sum_n_modes", "correction_relative_upper_bound",
                    "correction_absolute_eV2", "correction_in_juno_sigma", "verdict",
                    "interpretation"):
            assert key in r

    def test_epsilon_kk_tiny(self):
        r = kk_tower_correction_negligible()
        # ε_KK ≈ 2.3e-21
        assert r["epsilon_kk"] < 1e-15

    def test_correction_negligible_vs_juno_sigma(self):
        r = kk_tower_correction_negligible()
        # Correction should be far below JUNO σ (< 1e-10 × σ)
        assert r["correction_in_juno_sigma"] < 1e-10

    def test_verdict_is_negligible(self):
        assert kk_tower_correction_negligible()["verdict"] == "NEGLIGIBLE"

    def test_tower_sum_positive(self):
        assert kk_tower_correction_negligible()["tower_sum_n_modes"] > 0.0

    def test_tower_sum_less_than_pi_squared_over_6(self):
        # Sum 1/n² → π²/6 ≈ 1.645; for 10 modes should be close
        r = kk_tower_correction_negligible(n_modes=100)
        assert r["tower_sum_n_modes"] < math.pi ** 2 / 6 + 0.01


# ─────────────────────────────────────────────────────────────────────────
# project_dm31_from_2nlo()
# ─────────────────────────────────────────────────────────────────────────

class TestProjectDm31:
    def test_returns_dict(self):
        assert isinstance(project_dm31_from_2nlo(), dict)

    def test_required_keys(self):
        r = project_dm31_from_2nlo()
        for key in ("dm31_2nlo_baseline_eV2", "delta_rge", "delta_seesaw",
                    "p_r_used", "dm31_projected_eV2", "juno_central_eV2",
                    "residual_pct", "tension_sigma", "status",
                    "in_falsification_window", "note"):
            assert key in r

    def test_baseline_matches_constant(self):
        r = project_dm31_from_2nlo()
        assert abs(r["dm31_2nlo_baseline_eV2"] - DM2_31_2NLO_EV2) < 1e-15

    def test_projected_above_baseline(self):
        r = project_dm31_from_2nlo()
        assert r["dm31_projected_eV2"] > DM2_31_2NLO_EV2

    def test_projected_below_juno(self):
        r = project_dm31_from_2nlo()
        assert r["dm31_projected_eV2"] < JUNO_2026_RELEASE["dm2_31_central_eV2"]

    def test_projected_matches_module_constant(self):
        r = project_dm31_from_2nlo()
        assert abs(r["dm31_projected_eV2"] - DM2_31_PROJECTED_EV2) < 1e-13

    def test_tension_matches_module_constant(self):
        r = project_dm31_from_2nlo()
        assert abs(r["tension_sigma"] - JUNO_TENSION_PROJECTED_SIGMA) < 1e-8

    def test_status_excluded(self):
        # With full PMNS max, should still be EXCLUDED (> 3σ)
        r = project_dm31_from_2nlo()
        assert r["status"] == "EXCLUDED"

    def test_p_r_zero_gives_rge_only(self):
        r = project_dm31_from_2nlo(p_r=0.0)
        expected_dm31 = DM2_31_2NLO_EV2 * (1.0 + rge_running_correction())
        assert abs(r["dm31_projected_eV2"] - expected_dm31) < 1e-14

    def test_p_r_out_of_range_raises(self):
        with pytest.raises(ValueError):
            project_dm31_from_2nlo(p_r=P_R_PMNS_MAX + 0.1)

    def test_p_r_negative_raises(self):
        with pytest.raises(ValueError):
            project_dm31_from_2nlo(p_r=-0.01)

    def test_include_rge_false(self):
        r_with = project_dm31_from_2nlo(p_r=0.3, include_rge=True)
        r_without = project_dm31_from_2nlo(p_r=0.3, include_rge=False)
        assert r_with["dm31_projected_eV2"] > r_without["dm31_projected_eV2"]

    def test_in_falsification_window(self):
        r = project_dm31_from_2nlo()
        assert r["in_falsification_window"] is True

    def test_residual_pct_positive(self):
        r = project_dm31_from_2nlo()
        assert r["residual_pct"] > 0.0

    def test_residual_pct_about_2_7pct(self):
        r = project_dm31_from_2nlo()
        assert 1.5 < r["residual_pct"] < 4.5


# ─────────────────────────────────────────────────────────────────────────
# juno_2026_falsification_verdict()
# ─────────────────────────────────────────────────────────────────────────

class TestFalsificationVerdict:
    def test_returns_dict(self):
        assert isinstance(juno_2026_falsification_verdict(), dict)

    def test_required_keys(self):
        v = juno_2026_falsification_verdict()
        for key in ("pillar", "title", "juno_data", "um_2nlo_bare",
                    "um_best_attempt_projection", "kk_tower_analysis",
                    "overall_status", "admission_tag", "closure_path",
                    "fallibility_section", "machine_readable"):
            assert key in v

    def test_pillar_number(self):
        assert juno_2026_falsification_verdict()["pillar"] == 525

    def test_title(self):
        assert juno_2026_falsification_verdict()["title"] == "JUNO_2026_FALSIFICATION_RESPONSE"

    def test_bare_level_excluded(self):
        v = juno_2026_falsification_verdict()
        assert v["um_2nlo_bare"]["level"] == "EXCLUDED"

    def test_bare_tension_above_6sigma(self):
        v = juno_2026_falsification_verdict()
        assert v["um_2nlo_bare"]["tension_sigma"] > 6.0

    def test_projected_still_excluded(self):
        v = juno_2026_falsification_verdict()
        assert v["um_best_attempt_projection"]["status"] == "EXCLUDED"

    def test_overall_status_honest_open_problem(self):
        v = juno_2026_falsification_verdict()
        assert v["overall_status"] == "HONEST_OPEN_PROBLEM"

    def test_admission_tag(self):
        v = juno_2026_falsification_verdict()
        assert v["admission_tag"] == "JUNO_2026_P17_EXCLUDED"

    def test_machine_readable_structure(self):
        v = juno_2026_falsification_verdict()
        mr = v["machine_readable"]
        for key in ("bare_tension_sigma", "projected_tension_sigma",
                    "residual_gap_pct", "in_falsification_window_bare",
                    "in_falsification_window_proj", "status"):
            assert key in mr

    def test_machine_readable_bare_tension(self):
        v = juno_2026_falsification_verdict()
        mr = v["machine_readable"]
        assert abs(mr["bare_tension_sigma"] - JUNO_TENSION_2NLO_SIGMA) < 1e-8

    def test_machine_readable_proj_tension(self):
        v = juno_2026_falsification_verdict()
        mr = v["machine_readable"]
        assert abs(mr["projected_tension_sigma"] - JUNO_TENSION_PROJECTED_SIGMA) < 1e-8

    def test_bare_in_falsification_window(self):
        # 2.2845e-3 is in [2.2e-3, 2.7e-3]
        v = juno_2026_falsification_verdict()
        assert v["machine_readable"]["in_falsification_window_bare"] is True

    def test_kk_tower_verdict_negligible(self):
        v = juno_2026_falsification_verdict()
        assert v["kk_tower_analysis"]["verdict"] == "NEGLIGIBLE"

    def test_fallibility_section_ref(self):
        v = juno_2026_falsification_verdict()
        assert "XV" in v["fallibility_section"]


# ─────────────────────────────────────────────────────────────────────────
# juno_2026_full_report()
# ─────────────────────────────────────────────────────────────────────────

class TestFullReport:
    def test_returns_dict(self):
        assert isinstance(juno_2026_full_report(), dict)

    def test_required_keys(self):
        r = juno_2026_full_report()
        for key in ("version", "pillar", "event_date", "narrative_summary",
                    "verdict", "corrections_applied", "open_workstream",
                    "fallibility_ref"):
            assert key in r

    def test_version(self):
        assert juno_2026_full_report()["version"] == "v17.1"

    def test_pillar_number(self):
        assert juno_2026_full_report()["pillar"] == 525

    def test_event_date(self):
        assert juno_2026_full_report()["event_date"] == "2026-06-10"

    def test_narrative_is_nonempty_string(self):
        r = juno_2026_full_report()
        assert isinstance(r["narrative_summary"], str)
        assert len(r["narrative_summary"]) > 200

    def test_narrative_mentions_juno(self):
        r = juno_2026_full_report()
        assert "JUNO" in r["narrative_summary"]

    def test_narrative_mentions_open_problem(self):
        r = juno_2026_full_report()
        assert "HONEST_OPEN_PROBLEM" in r["narrative_summary"]

    def test_corrections_keys(self):
        r = juno_2026_full_report()
        c = r["corrections_applied"]
        for key in ("rge_tau_yukawa", "seesaw_at_pmns_max", "kk_tower"):
            assert key in c

    def test_open_workstream_ws_v(self):
        r = juno_2026_full_report()
        assert "WS-V" in r["open_workstream"]

    def test_fallibility_ref(self):
        r = juno_2026_full_report()
        assert "FALLIBILITY.md" in r["fallibility_ref"]
        assert "XV" in r["fallibility_ref"]
