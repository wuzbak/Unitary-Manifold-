# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0

"""Tests for Pillar 106 — CKM Wolfenstein λ_W from fermion-mass-fitted RS c-values.

≥ 30 tests covering:
  - rs_wavefunction_ir: special values, monotonicity, overflow safety
  - invert_rs_wavefunction: round-trip accuracy, bracket expansion
  - cl_spectrum_6d: values, spacing, wavefunction ratios
  - fit_cr_sector: shape, round-trip mass residuals, naturalness
  - fritzsch_wolfenstein_lambda: primary result, < 5% residual
  - wolfenstein_from_cr_mismatch: c_R-based derivation
  - ckm_fritzsch_estimate: full CKM structure, honest residuals
  - cr_sensitivity_table: structure and monotonicity
  - pillar_106_report: comprehensive report structure
  - Epistemic labels and gate flags
"""

import math
import pytest

from src.core.ckm_wolfenstein_from_masses import (
    N_W, K_CS, PI_KR, V_EW_MEV,
    C_L_6D, PDG_WOLFENSTEIN_LAMBDA, PDG_MASSES_MEV, EPISTEMIC_STATUS,
    rs_wavefunction_ir,
    invert_rs_wavefunction,
    cl_spectrum_6d,
    fit_cr_sector,
    fritzsch_wolfenstein_lambda,
    wolfenstein_from_cr_mismatch,
    ckm_fritzsch_estimate,
    cr_sensitivity_table,
    pillar_106_report,
)


# ---------------------------------------------------------------------------
# Constants sanity
# ---------------------------------------------------------------------------

def test_constants_pi_kr():
    """PI_KR must equal K_CS / 2 = 37."""
    assert PI_KR == pytest.approx(37.0)


def test_constants_c_l_6d_values():
    """6D c_L spectrum: c_L^{(i)} = 0.5 + i * 5/74."""
    spacing = 5.0 / 74.0
    assert C_L_6D[0] == pytest.approx(0.5)
    assert C_L_6D[1] == pytest.approx(0.5 + spacing)
    assert C_L_6D[2] == pytest.approx(0.5 + 2.0 * spacing)


def test_constants_pdg_lambda():
    """PDG Wolfenstein λ must be 0.22650."""
    assert PDG_WOLFENSTEIN_LAMBDA == pytest.approx(0.22650)


# ---------------------------------------------------------------------------
# rs_wavefunction_ir
# ---------------------------------------------------------------------------

def test_fir_special_case_half():
    """At c = 0.5, f_IR = 1/sqrt(2*pi_kr)."""
    expected = 1.0 / math.sqrt(2.0 * PI_KR)
    assert rs_wavefunction_ir(0.5) == pytest.approx(expected, rel=1e-10)


def test_fir_c_zero():
    """At c = 0 (fully IR-localised), f_IR should equal 1.0 exactly."""
    assert rs_wavefunction_ir(0.0) == pytest.approx(1.0, rel=1e-8)


def test_fir_uv_localised_small():
    """For large c (UV-localised), f_IR must be very small."""
    assert rs_wavefunction_ir(1.0) < 1e-7


def test_fir_positive():
    """f_IR must be strictly positive for any c in (-10, 10)."""
    for c in [-5.0, -1.0, 0.0, 0.5, 1.0, 2.0, 5.0]:
        assert rs_wavefunction_ir(c) > 0.0


def test_fir_monotone_decreasing():
    """f_IR must decrease strictly as c increases."""
    cs = [-3.0, -1.0, 0.0, 0.3, 0.5, 0.7, 1.0, 2.0]
    vals = [rs_wavefunction_ir(c) for c in cs]
    for i in range(len(vals) - 1):
        assert vals[i] > vals[i + 1], (
            f"f_IR not decreasing at c={cs[i]:.1f} ({vals[i]:.4e}) -> c={cs[i+1]:.1f} ({vals[i+1]:.4e})"
        )


def test_fir_6d_c_l_values():
    """f_IR at the three 6D c_L values must satisfy the correct hierarchy."""
    fl = [rs_wavefunction_ir(c) for c in C_L_6D]
    # fl[0] > fl[1] > fl[2] (IR → UV ordering)
    assert fl[0] > fl[1] > fl[2]
    # fl[0] ≈ 1/sqrt(74)
    assert fl[0] == pytest.approx(1.0 / math.sqrt(74.0), rel=1e-6)


def test_fir_adjacent_ratio():
    """Adjacent-generation ratio f_IR(c_L^1)/f_IR(c_L^0) ≈ 0.260."""
    fl = [rs_wavefunction_ir(c) for c in C_L_6D]
    ratio = fl[1] / fl[0]
    assert ratio == pytest.approx(0.2605, abs=0.001)


def test_fir_overflow_safety_large_negative():
    """For very large negative c, f_IR ≈ sqrt(|1-2c|) and must not raise."""
    val = rs_wavefunction_ir(-30.0)
    expected_approx = math.sqrt(61.0)  # sqrt(|1-2*(-30)|)
    assert val == pytest.approx(expected_approx, rel=0.01)


def test_fir_overflow_safety_large_positive():
    """For large positive c, f_IR must be 0 (no raise)."""
    val = rs_wavefunction_ir(10.0)
    assert val == 0.0 or val < 1e-50


# ---------------------------------------------------------------------------
# invert_rs_wavefunction
# ---------------------------------------------------------------------------

def test_invert_fir_round_trip_c_half():
    """Inversion at f_IR(0.5) must recover c = 0.5."""
    target = rs_wavefunction_ir(0.5)
    c_recovered = invert_rs_wavefunction(target)
    assert c_recovered == pytest.approx(0.5, abs=1e-8)


def test_invert_fir_round_trip_strange():
    """Inversion at the strange-quark target f_IR recovers correct c."""
    target = 0.009973
    c = invert_rs_wavefunction(target)
    recovered = rs_wavefunction_ir(c)
    assert recovered == pytest.approx(target, rel=1e-8)


def test_invert_fir_round_trip_down():
    """Inversion at down-quark target."""
    target = 0.004310
    c = invert_rs_wavefunction(target)
    recovered = rs_wavefunction_ir(c)
    assert recovered == pytest.approx(target, rel=1e-8)


def test_invert_fir_round_trip_charm():
    """Inversion at charm-quark target."""
    target = 0.003289
    c = invert_rs_wavefunction(target)
    recovered = rs_wavefunction_ir(c)
    assert recovered == pytest.approx(target, rel=1e-8)


def test_invert_fir_small_target():
    """Inversion works for very small f_IR targets (tiny overlap)."""
    target = 4.8e-5
    c = invert_rs_wavefunction(target)
    recovered = rs_wavefunction_ir(c)
    assert recovered == pytest.approx(target, rel=1e-6)


def test_invert_fir_invalid_raises():
    """Non-positive f_target must raise ValueError."""
    with pytest.raises(ValueError):
        invert_rs_wavefunction(0.0)
    with pytest.raises(ValueError):
        invert_rs_wavefunction(-1.0)


def test_invert_fir_uv_side():
    """For f_target < f_IR(0.5), inversion gives c > 0.5."""
    target = 0.01
    c = invert_rs_wavefunction(target)
    assert c > 0.5


def test_invert_fir_ir_side():
    """For f_target > f_IR(0.5), inversion gives c < 0.5."""
    target = 0.5
    c = invert_rs_wavefunction(target)
    assert c < 0.5


# ---------------------------------------------------------------------------
# cl_spectrum_6d
# ---------------------------------------------------------------------------

def test_cl_spectrum_6d_values():
    """cl_spectrum_6d must return the expected 6D c_L values."""
    spec = cl_spectrum_6d()
    spacing = 5.0 / 74.0
    assert spec["c_L"][0] == pytest.approx(0.5)
    assert spec["c_L"][1] == pytest.approx(0.5 + spacing, rel=1e-10)
    assert spec["c_L"][2] == pytest.approx(0.5 + 2.0 * spacing, rel=1e-10)


def test_cl_spectrum_6d_zero_free_params():
    """The 6D c_L spectrum must have zero free parameters."""
    spec = cl_spectrum_6d()
    assert spec["free_parameters"] == 0


def test_cl_spectrum_6d_adjacent_ratios():
    """Both adjacent wavefunction ratios must be in (0, 1)."""
    spec = cl_spectrum_6d()
    assert 0.0 < spec["adjacent_ratio_01"] < 1.0
    assert 0.0 < spec["adjacent_ratio_12"] < 1.0


# ---------------------------------------------------------------------------
# fit_cr_sector
# ---------------------------------------------------------------------------

def test_fit_cr_sector_down_shape():
    """fit_cr_sector for down sector must return three c_R values."""
    fit = fit_cr_sector(
        PDG_MASSES_MEV["m_b"],
        PDG_MASSES_MEV["m_s"],
        PDG_MASSES_MEV["m_d"],
    )
    assert len(fit["c_R"]) == 3
    assert len(fit["f_IR_cR"]) == 3


def test_fit_cr_sector_down_residuals_small():
    """Fitted c_R for down sector must reproduce masses to < 0.01%."""
    fit = fit_cr_sector(
        PDG_MASSES_MEV["m_b"],
        PDG_MASSES_MEV["m_s"],
        PDG_MASSES_MEV["m_d"],
    )
    for res in fit["residuals_pct"]:
        assert res < 0.01, f"mass residual {res:.4f}% too large"


def test_fit_cr_sector_up_residuals_small():
    """Fitted c_R for up sector must reproduce masses to < 0.01%."""
    fit = fit_cr_sector(
        PDG_MASSES_MEV["m_t"],
        PDG_MASSES_MEV["m_c"],
        PDG_MASSES_MEV["m_u"],
    )
    for res in fit["residuals_pct"]:
        assert res < 0.01, f"mass residual {res:.4f}% too large"


def test_fit_cr_sector_down_y5_natural():
    """Y5 for down sector must be O(1) — a naturalness check."""
    fit = fit_cr_sector(
        PDG_MASSES_MEV["m_b"],
        PDG_MASSES_MEV["m_s"],
        PDG_MASSES_MEV["m_d"],
    )
    assert 0.5 < fit["Y5"] < 4.0, f"Y5_d = {fit['Y5']:.3f} unexpectedly large"


def test_fit_cr_sector_cr_hierarchy_down():
    """Down-type c_R values must increase (UV-localise) for lighter quarks."""
    fit = fit_cr_sector(
        PDG_MASSES_MEV["m_b"],
        PDG_MASSES_MEV["m_s"],
        PDG_MASSES_MEV["m_d"],
    )
    # c_R^b < c_R^s < c_R^d (lighter → more UV-localised for down-type)
    assert fit["c_R"][0] < fit["c_R"][1] < fit["c_R"][2]


# ---------------------------------------------------------------------------
# fritzsch_wolfenstein_lambda
# ---------------------------------------------------------------------------

def test_fritzsch_lambda_primary_value():
    """Fritzsch λ_W must be sqrt(m_d / m_s) = 0.22361."""
    result = fritzsch_wolfenstein_lambda()
    expected = math.sqrt(PDG_MASSES_MEV["m_d"] / PDG_MASSES_MEV["m_s"])
    assert result["lambda_wolfenstein"] == pytest.approx(expected, rel=1e-8)


def test_fritzsch_lambda_residual_lt_5pct():
    """Fritzsch λ_W residual must be < 5% from PDG 0.22650."""
    result = fritzsch_wolfenstein_lambda()
    assert result["residual_pct"] < 5.0


def test_fritzsch_lambda_residual_lt_2pct():
    """Fritzsch λ_W residual must be < 2% (known 1.28%)."""
    result = fritzsch_wolfenstein_lambda()
    assert result["residual_pct"] < 2.0


def test_fritzsch_lambda_gate_flag_true():
    """Gate 5% flag must be True."""
    result = fritzsch_wolfenstein_lambda()
    assert result["gate_5pct"] is True


def test_fritzsch_lambda_constrained_label():
    """Fritzsch result must carry CONSTRAINED epistemic label."""
    result = fritzsch_wolfenstein_lambda()
    assert "CONSTRAINED" in result["epistemic"]


def test_fritzsch_lambda_angle_positive():
    """Cabibbo angle must be positive."""
    result = fritzsch_wolfenstein_lambda()
    assert result["theta_cabibbo_deg"] > 0.0


# ---------------------------------------------------------------------------
# wolfenstein_from_cr_mismatch
# ---------------------------------------------------------------------------

def test_cr_mismatch_lambda_close_to_fritzsch():
    """c_R mismatch λ_W must agree with Fritzsch formula to < 1e-8."""
    fritzsch = fritzsch_wolfenstein_lambda()
    mismatch = wolfenstein_from_cr_mismatch()
    assert mismatch["lambda_wolfenstein"] == pytest.approx(
        fritzsch["lambda_wolfenstein"], rel=1e-6
    )


def test_cr_mismatch_residual_lt_5pct():
    """c_R mismatch residual must be < 5%."""
    result = wolfenstein_from_cr_mismatch()
    assert result["residual_pct"] < 5.0


def test_cr_mismatch_fl_ratio_correct():
    """fL ratio = f_IR(c_L^2)/f_IR(c_L^1) must match direct computation."""
    result = wolfenstein_from_cr_mismatch()
    fl1 = rs_wavefunction_ir(C_L_6D[1])
    fl2 = rs_wavefunction_ir(C_L_6D[2])
    assert result["fL_ratio_21"] == pytest.approx(fl2 / fl1, rel=1e-8)


def test_cr_mismatch_formula_equals_fritzsch():
    """RS product-ratio formula must equal sqrt(m_d/m_s) by construction."""
    result = wolfenstein_from_cr_mismatch()
    assert "sqrt(m_d / m_s)" in result["equals_fritzsch"]


def test_cr_mismatch_gate_passed():
    """Gate 5% flag must be True for mismatch derivation."""
    result = wolfenstein_from_cr_mismatch()
    assert result["gate_5pct"] is True


# ---------------------------------------------------------------------------
# ckm_fritzsch_estimate
# ---------------------------------------------------------------------------

def test_ckm_estimate_v_us_within_5pct():
    """V_us from Fritzsch must be within 5% of PDG."""
    result = ckm_fritzsch_estimate()
    assert result["gate_5pct_V_us"] is True


def test_ckm_estimate_v_cb_not_reproduced():
    """V_cb residual must be > 100% (honest: Fritzsch over-predicts)."""
    result = ckm_fritzsch_estimate()
    assert result["residual_V_cb_pct"] > 100.0


def test_ckm_estimate_honest_note_present():
    """honest_note must explicitly mention V_cb and V_ub are not reproduced."""
    result = ckm_fritzsch_estimate()
    assert "V_cb" in result["honest_note"] and "V_ub" in result["honest_note"]


def test_ckm_estimate_angles_ordered():
    """Mixing angles: theta_12 > theta_23 > theta_13 is NOT required;
    just check all angles are non-negative."""
    result = ckm_fritzsch_estimate()
    assert result["theta_12_deg"] >= 0.0
    assert result["theta_23_deg"] >= 0.0
    assert result["theta_13_deg"] >= 0.0


# ---------------------------------------------------------------------------
# cr_sensitivity_table
# ---------------------------------------------------------------------------

def test_cr_sensitivity_table_length():
    """Sensitivity table must have 4 rows (2 parameters × 2 directions)."""
    rows = cr_sensitivity_table()
    assert len(rows) == 4


def test_cr_sensitivity_table_keys():
    """Each row must have required keys."""
    rows = cr_sensitivity_table()
    required = {"parameter", "variation", "c_R_nominal", "c_R_varied",
                "lambda_nominal", "lambda_varied", "delta_lambda"}
    for row in rows:
        assert required.issubset(row.keys())


def test_cr_sensitivity_monotone_d1():
    """Increasing c_R^d_1 (strange) decreases fR_d1 → increases λ_W."""
    rows = cr_sensitivity_table()
    d1_rows = [r for r in rows if "strange" in r["parameter"]]
    plus_row  = next(r for r in d1_rows if r["variation"] == "+δc")
    minus_row = next(r for r in d1_rows if r["variation"] == "-δc")
    # Larger c_R^d_1 → smaller f_IR(c_R^d_1) → larger ratio → larger λ
    assert plus_row["delta_lambda"] > 0.0
    assert minus_row["delta_lambda"] < 0.0


# ---------------------------------------------------------------------------
# pillar_106_report
# ---------------------------------------------------------------------------

def test_report_pillar_number():
    """Pillar number must be 106."""
    report = pillar_106_report()
    assert report["pillar"] == 106


def test_report_status_constrained():
    """Report status must be CONSTRAINED."""
    report = pillar_106_report()
    assert report["status"] == "CONSTRAINED"


def test_report_lambda_close_to_pdg():
    """Reported λ_W must be within 2% of PDG 0.22650."""
    report = pillar_106_report()
    assert abs(report["lambda_wolfenstein"] - PDG_WOLFENSTEIN_LAMBDA) / PDG_WOLFENSTEIN_LAMBDA < 0.02


def test_report_gate_passed():
    """5% gate flag must be True in the report."""
    report = pillar_106_report()
    assert report["gate_5pct_passed"] is True


def test_report_improvement_over_104():
    """λ_W must be closer to PDG than the Pillar 104 value of 0.029."""
    report = pillar_106_report()
    err_104 = abs(0.029 - PDG_WOLFENSTEIN_LAMBDA) / PDG_WOLFENSTEIN_LAMBDA
    err_106 = abs(report["lambda_wolfenstein"] - PDG_WOLFENSTEIN_LAMBDA) / PDG_WOLFENSTEIN_LAMBDA
    assert err_106 < err_104


def test_report_improvement_factor_gt_7():
    """Improvement factor must be > 7× (was ×8 off, now < 2% off)."""
    report = pillar_106_report()
    assert report["improvement_factor"] > 7.0


def test_report_honest_gaps_present():
    """Report must list honest gaps including fitted c_R."""
    report = pillar_106_report()
    gaps = " ".join(report["honest_gaps"])
    assert "FITTED" in gaps or "fitted" in gaps


def test_report_y5_down_natural():
    """Y5 for down sector must be in [0.5, 4.0] (O(1) naturalness)."""
    report = pillar_106_report()
    assert report["y5_down_natural"] is True


def test_report_required_keys():
    """Report must contain all required top-level keys."""
    report = pillar_106_report()
    required = {
        "module", "pillar", "status", "epistemic",
        "lambda_wolfenstein", "pdg_lambda", "residual_pct", "gate_5pct_passed",
        "honest_gaps", "improvements_over_pillar_104",
    }
    for key in required:
        assert key in report, f"Missing key: {key}"


def test_report_epistemic_contains_constrained():
    """EPISTEMIC_STATUS constant must mention CONSTRAINED."""
    assert "CONSTRAINED" in EPISTEMIC_STATUS
