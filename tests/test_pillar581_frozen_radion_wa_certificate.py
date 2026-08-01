from __future__ import annotations

import pytest

from src.core.pillar581_frozen_radion_wa_certificate import (
    H0_EV,
    M_PHI_EV,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    RATIO_MPHI_H0,
    VERSION,
    W0_CANONICAL,
    WA_CANONICAL,
    conditional_certificate,
    desi_t1_upgrade,
    pillar_report,
    radion_mass_condition,
    wa_zero_proof,
)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("PILLAR_NUMBER", PILLAR_NUMBER),
        ("PILLAR_STATUS", PILLAR_STATUS),
        ("VERSION", VERSION),
        ("M_PHI_EV", M_PHI_EV),
        ("H0_EV", H0_EV),
        ("RATIO_MPHI_H0", RATIO_MPHI_H0),
        ("W0_CANONICAL", W0_CANONICAL),
        ("WA_CANONICAL", WA_CANONICAL),
    ],
)
def test_constants_are_present(label, value):
    assert value is not None, label


def test_constant_values_are_exact():
    assert PILLAR_NUMBER == 581
    assert PILLAR_STATUS == "FROZEN_RADION_WA_ANALYTIC_CERTIFICATE"
    assert VERSION == "v20.1"
    assert M_PHI_EV == pytest.approx(1.0e-3)
    assert H0_EV == pytest.approx(1.5e-33)
    assert RATIO_MPHI_H0 == pytest.approx(6.666666666666667e29)
    assert W0_CANONICAL == pytest.approx(-1.0)
    assert WA_CANONICAL == pytest.approx(0.0)


@pytest.mark.parametrize(
    "key",
    [
        "check",
        "m_phi_ev",
        "h0_ev",
        "m_phi_squared",
        "h0_squared",
        "ratio_mphi_h0",
        "ratio_squared",
        "frozen_condition",
        "goldberger_wise_formula_match",
    ],
)
def test_radion_mass_condition_keys(key):
    result = radion_mass_condition()
    assert key in result


def test_radion_mass_condition_values():
    result = radion_mass_condition()
    assert result["m_phi_ev"] == pytest.approx(1.0e-3)
    assert result["h0_ev"] == pytest.approx(1.5e-33)
    assert result["ratio_mphi_h0"] == pytest.approx(RATIO_MPHI_H0)
    assert result["ratio_squared"] == pytest.approx(RATIO_MPHI_H0**2)
    assert result["frozen_condition"] is True
    assert result["goldberger_wise_formula_match"] is True


@pytest.mark.parametrize("kwargs", [{"m_phi_ev": 0.0}, {"h0_ev": 0.0}, {"m_phi_ev": -1.0}, {"h0_ev": -1.0}])
def test_radion_mass_condition_rejects_nonpositive_inputs(kwargs):
    with pytest.raises(ValueError):
        radion_mass_condition(**kwargs)


def test_wa_zero_proof_contains_five_steps():
    proof = wa_zero_proof()
    assert len(proof["proof_steps"]) == 5


@pytest.mark.parametrize("index", [0, 1, 2, 3, 4])
def test_wa_zero_proof_step_content(index):
    proof = wa_zero_proof()
    assert proof["proof_steps"][index].startswith(f"{index + 1}.")


def test_wa_zero_proof_values():
    proof = wa_zero_proof()
    assert proof["ratio_mphi_h0"] == pytest.approx(RATIO_MPHI_H0)
    assert proof["w0_canonical"] == pytest.approx(-1.0)
    assert proof["wa_canonical"] == pytest.approx(0.0)
    assert proof["proved_conditionally"] is True
    assert "conditional" in proof["honest_caveat"].lower()


@pytest.mark.parametrize(
    "key",
    ["status", "certificate", "ratio_mphi_h0", "conditional_on_lambda_gw", "pass"],
)
def test_conditional_certificate_keys(key):
    certificate = conditional_certificate()
    assert key in certificate


def test_conditional_certificate_values():
    certificate = conditional_certificate()
    assert certificate["status"] == "CONDITIONAL_ANALYTIC"
    assert certificate["conditional_on_lambda_gw"] is True
    assert certificate["pass"] is True
    assert "w_a = 0" in certificate["certificate"]


@pytest.mark.parametrize(
    "key",
    [
        "lane",
        "before_status",
        "after_status",
        "certificate_mode",
        "w0_prediction",
        "wa_prediction",
        "honest_note",
    ],
)
def test_desi_t1_upgrade_keys(key):
    upgrade = desi_t1_upgrade()
    assert key in upgrade


def test_desi_t1_upgrade_values():
    upgrade = desi_t1_upgrade()
    assert upgrade["lane"] == "T1_DARK_ENERGY_WA"
    assert upgrade["before_status"] == "TRACKED"
    assert upgrade["after_status"] == "ANALYTIC_CERTIFIED"
    assert upgrade["certificate_mode"] == "CONDITIONAL_ANALYTIC"
    assert upgrade["w0_prediction"] == pytest.approx(-1.0)
    assert upgrade["wa_prediction"] == pytest.approx(0.0)


@pytest.mark.parametrize(
    "key",
    [
        "pillar",
        "title",
        "status",
        "version",
        "constants",
        "radion_mass_condition",
        "wa_zero_proof",
        "conditional_certificate",
        "desi_t1_upgrade",
    ],
)
def test_pillar_report_keys(key):
    report = pillar_report()
    assert key in report


def test_pillar_report_values():
    report = pillar_report()
    assert report["pillar"] == 581
    assert report["constants"]["ratio_mphi_h0"] == pytest.approx(RATIO_MPHI_H0)
    assert report["radion_mass_condition"]["frozen_condition"] is True
    assert report["conditional_certificate"]["status"] == "CONDITIONAL_ANALYTIC"
    assert report["desi_t1_upgrade"]["after_status"] == "ANALYTIC_CERTIFIED"
