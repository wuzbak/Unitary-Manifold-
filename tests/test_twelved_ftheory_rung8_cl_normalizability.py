from __future__ import annotations

import pytest

from src.twelved.ftheory_rung8_cl_normalizability import (
    C_L_MIN,
    EPISTEMIC_STATUS,
    M_KK_GEV,
    PI_KR,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SUM_MNU_BOUND_EV,
    VERSION,
    VOL_S_REF_PROXY,
    axiomzero_seed_purity_check,
    compute_cl_min,
    gap_b_proved_certificate,
    kill_switch_check,
    pillar_report,
    remaining_blocking_residuals,
)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("PILLAR_NUMBER", PILLAR_NUMBER),
        ("PILLAR_STATUS", PILLAR_STATUS),
        ("EPISTEMIC_STATUS", EPISTEMIC_STATUS),
        ("VERSION", VERSION),
        ("PI_KR", PI_KR),
        ("M_KK_GEV", M_KK_GEV),
        ("SUM_MNU_BOUND_EV", SUM_MNU_BOUND_EV),
        ("VOL_S_REF_PROXY", VOL_S_REF_PROXY),
    ],
)
def test_constants_are_present(label, value):
    assert value is not None, label


def test_constant_values_are_exact():
    assert PILLAR_NUMBER == 577
    assert PILLAR_STATUS == "FTHEORY_RUNG8_CL_NORMALIZABILITY_PROVED_ADJACENT"
    assert EPISTEMIC_STATUS == "ADJACENT_TRACK"
    assert VERSION == "v20.1"
    assert PI_KR == 37.0
    assert M_KK_GEV == 1000.0
    assert SUM_MNU_BOUND_EV == pytest.approx(0.12)
    assert VOL_S_REF_PROXY == pytest.approx(275.5)
    assert C_L_MIN == pytest.approx(0.917)


@pytest.mark.parametrize(
    "key",
    [
        "check",
        "vol_s_ref_exact",
        "vol_s_ref_proxy",
        "m_kk_gev",
        "m_nu1_max_gev",
        "pi_kr",
        "log_ratio",
        "c_l_min_exact",
        "c_l_min_rounded",
        "manual_cutoff_reference",
        "stronger_than_manual",
        "pass",
    ],
)
def test_compute_cl_min_keys(key):
    result = compute_cl_min()
    assert key in result


def test_compute_cl_min_numeric_values():
    result = compute_cl_min()
    assert result["vol_s_ref_exact"] == pytest.approx(275.3906316489361)
    assert result["vol_s_ref_proxy"] == pytest.approx(275.5)
    assert result["c_l_min_exact"] == pytest.approx(0.916890499199956)
    assert result["c_l_min_rounded"] == pytest.approx(0.917)
    assert result["manual_cutoff_reference"] == pytest.approx(0.88)
    assert result["stronger_than_manual"] is True
    assert result["pass"] is True


@pytest.mark.parametrize(
    ("m_kk_gev", "m_nu1_max_gev", "pi_kr"),
    [
        (0.0, 1.0e-10, 37.0),
        (-1.0, 1.0e-10, 37.0),
        (1000.0, 0.0, 37.0),
        (1000.0, -1.0, 37.0),
        (1000.0, 1.0e-10, 0.0),
    ],
)
def test_compute_cl_min_invalid_positive_requirements(m_kk_gev, m_nu1_max_gev, pi_kr):
    with pytest.raises(ValueError):
        compute_cl_min(m_kk_gev=m_kk_gev, m_nu1_max_gev=m_nu1_max_gev, pi_kr=pi_kr)


def test_compute_cl_min_rejects_ratio_not_above_one():
    with pytest.raises(ValueError):
        compute_cl_min(m_kk_gev=1.0e-12, m_nu1_max_gev=1.0e-10)


def test_remaining_blocking_residuals_are_two_named_items():
    residuals = remaining_blocking_residuals()
    assert len(residuals) == 2
    assert "Residual 2" in residuals[0]
    assert "Residual 3" in residuals[1]


@pytest.mark.parametrize("fragment", ["Weierstrass", "genus", "curvature", "Higgs bundle"])
def test_remaining_blocking_residuals_include_expected_fragments(fragment):
    residuals = " ".join(remaining_blocking_residuals())
    assert fragment in residuals


@pytest.mark.parametrize(
    "key",
    [
        "gap",
        "before_status",
        "after_status",
        "c_l_min",
        "c_l_min_exact",
        "vol_s_ref_proxy",
        "free_parameter_count",
        "proved_deterministically",
        "remaining_residual_count",
        "remaining_residuals",
        "honest_status",
    ],
)
def test_gap_b_certificate_keys(key):
    certificate = gap_b_proved_certificate()
    assert key in certificate


def test_gap_b_certificate_values():
    certificate = gap_b_proved_certificate()
    assert certificate["gap"] == "B"
    assert certificate["before_status"] == "MECHANISM_IDENTIFIED"
    assert certificate["after_status"] == "PROVED_AT_REFERENCE_CY4"
    assert certificate["c_l_min"] == pytest.approx(0.917)
    assert certificate["free_parameter_count"] == 0
    assert certificate["proved_deterministically"] is True
    assert certificate["remaining_residual_count"] == 2


@pytest.mark.parametrize(
    "key",
    ["check", "geometric_inputs", "observational_inputs", "pdg_fit_inputs", "pass", "evidence"],
)
def test_axiomzero_seed_purity_keys(key):
    purity = axiomzero_seed_purity_check()
    assert key in purity


def test_axiomzero_seed_purity_values():
    purity = axiomzero_seed_purity_check()
    assert len(purity["geometric_inputs"]) == 4
    assert purity["observational_inputs"] == ["Σm_ν < 0.12 eV"]
    assert purity["pdg_fit_inputs"] == []
    assert purity["pass"] is True


def test_kill_switch_passes():
    assert kill_switch_check() is True


@pytest.mark.parametrize(
    "key",
    [
        "pillar",
        "title",
        "status",
        "version",
        "epistemic_status",
        "constants",
        "compute_cl_min",
        "gap_b_certificate",
        "axiomzero_seed_purity",
        "kill_switch_pass",
    ],
)
def test_pillar_report_keys(key):
    report = pillar_report()
    assert key in report


def test_pillar_report_values():
    report = pillar_report()
    assert report["constants"]["c_l_min"] == pytest.approx(0.917)
    assert report["compute_cl_min"]["stronger_than_manual"] is True
    assert report["gap_b_certificate"]["after_status"] == "PROVED_AT_REFERENCE_CY4"
    assert report["kill_switch_pass"] is True
