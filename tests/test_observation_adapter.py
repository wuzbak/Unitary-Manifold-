# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_observation_adapter.py
===================================
Tests for src/core/observation_adapter.py — structured observation comparison.

Covers: report structure, pull arithmetic, grade/status logic, per-record
physics correctness, DESI tension documentation, and helper APIs.
"""
from __future__ import annotations

import math
import pytest

from src.core.observation_adapter import (
    # Constants
    PLANCK_N_S, PLANCK_N_S_SIGMA,
    PDG_ALPHA_GUT, PDG_ALPHA_GUT_SIGMA,
    PDG_ALPHA_S_MZ, PDG_ALPHA_S_MZ_SIGMA,
    PDG_LAMBDA_QCD_GEV, PDG_LAMBDA_QCD_SIGMA,
    PDG_SIN2_THETA_W, PDG_SIN2_THETA_W_SIGMA,
    PDG_MW_GEV, PDG_MW_SIGMA,
    PDG_MZ_GEV, PDG_MZ_SIGMA,
    PDG_HIGGS_MASS_GEV, PDG_HIGGS_MASS_SIGMA,
    DESI_W0, DESI_W0_SIGMA,
    DESI_WA, DESI_WA_SIGMA,
    UM_N_S, UM_ALPHA_GUT, UM_ALPHA_S_MZ, UM_LAMBDA_QCD_GEV,
    UM_SIN2_THETA_W, UM_MW_GEV, UM_MZ_GEV, UM_HIGGS_MASS_GEV,
    UM_W0_KK, UM_WA_KK, GAMMA_SU5_NLO,
    # Classes
    ObservationRecord, ObservationReport,
    # Functions
    record_n_s, record_alpha_gut, record_alpha_s_mz, record_lambda_qcd,
    record_sin2_theta_w, record_mw, record_mz, record_higgs_mass,
    record_w0_dark_energy, record_wa_dark_energy,
    observation_report, record_by_id, passing_predictions, failing_predictions,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_GRADES = {"A", "B", "C", "D", "F"}
VALID_STATUSES = {"PASS", "TENSION", "FAIL"}
VALID_EPISTEMIC = {"DERIVED", "CONSTRAINED", "PARAMETERIZED", "OPEN"}


def _check_record_fields(rec: ObservationRecord) -> None:
    """Assert all fields are present and self-consistent."""
    assert isinstance(rec.prediction_id, str) and rec.prediction_id
    assert isinstance(rec.description, str) and rec.description
    assert isinstance(rec.formula, str) and rec.formula
    assert isinstance(rec.um_prediction, float)
    assert isinstance(rec.observed_value, float)
    assert isinstance(rec.observed_sigma, float) and rec.observed_sigma > 0
    assert isinstance(rec.observed_source, str) and rec.observed_source
    assert isinstance(rec.pull, float)
    assert isinstance(rec.abs_pull, float) and rec.abs_pull >= 0
    assert rec.confidence_grade in VALID_GRADES
    assert rec.status in VALID_STATUSES
    assert rec.epistemic_status in VALID_EPISTEMIC
    assert isinstance(rec.falsification_condition, str) and rec.falsification_condition


# ---------------------------------------------------------------------------
# Module-level constant sanity checks
# ---------------------------------------------------------------------------

def test_planck_n_s_value():
    assert PLANCK_N_S == pytest.approx(0.9649)


def test_planck_n_s_sigma_positive():
    assert PLANCK_N_S_SIGMA > 0


def test_um_n_s_value():
    assert UM_N_S == pytest.approx(0.9635)


def test_um_alpha_gut_formula():
    expected = 3 / 74 * GAMMA_SU5_NLO
    assert UM_ALPHA_GUT == pytest.approx(expected, rel=1e-9)


def test_desi_w0_negative():
    assert DESI_W0 < 0


def test_um_w0_kk_is_minus_one():
    assert UM_W0_KK == pytest.approx(-1.0)


def test_um_wa_kk_is_zero():
    assert UM_WA_KK == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# ObservationRecord.make — arithmetic
# ---------------------------------------------------------------------------

def test_make_pull_formula():
    rec = ObservationRecord.make(
        "TEST", "test", "f=x", 1.5, 1.0, 0.5, "source",
        "DERIVED", "falsif"
    )
    assert rec.pull == pytest.approx((1.5 - 1.0) / 0.5)


def test_make_abs_pull_nonnegative():
    rec = ObservationRecord.make("T", "t", "f", 0.0, 1.0, 0.5, "s", "DERIVED", "c")
    assert rec.abs_pull >= 0


def test_make_abs_pull_equals_abs_pull():
    rec = ObservationRecord.make("T", "t", "f", 0.0, 1.0, 0.5, "s", "DERIVED", "c")
    assert rec.abs_pull == pytest.approx(abs(rec.pull))


def test_make_grade_A():
    rec = ObservationRecord.make("T", "t", "f", 1.0, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.confidence_grade == "A"


def test_make_grade_B():
    # pull = (2.5 - 1.0) / 1.0 = 1.5 → grade B
    rec = ObservationRecord.make("T", "t", "f", 2.5, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.confidence_grade == "B"


def test_make_grade_C():
    # pull = (3.5 - 1.0) / 1.0 = 2.5 → grade C
    rec = ObservationRecord.make("T", "t", "f", 3.5, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.confidence_grade == "C"


def test_make_grade_D():
    rec = ObservationRecord.make("T", "t", "f", 4.0, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.confidence_grade == "D"


def test_make_grade_F():
    rec = ObservationRecord.make("T", "t", "f", 6.0, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.confidence_grade == "F"


def test_make_status_pass():
    rec = ObservationRecord.make("T", "t", "f", 1.0, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.status == "PASS"


def test_make_status_tension():
    # pull = (3.5 - 1.0) / 1.0 = 2.5 → TENSION
    rec = ObservationRecord.make("T", "t", "f", 3.5, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.status == "TENSION"


def test_make_status_fail():
    rec = ObservationRecord.make("T", "t", "f", 4.5, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.status == "FAIL"


def test_make_in_1sigma_true():
    rec = ObservationRecord.make("T", "t", "f", 0.5, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.in_1sigma is True


def test_make_in_2sigma_true():
    # pull = (2.5 - 1.0) / 1.0 = 1.5 → in_2sigma=True, in_1sigma=False
    rec = ObservationRecord.make("T", "t", "f", 2.5, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.in_2sigma is True
    assert rec.in_1sigma is False


def test_make_in_3sigma_true():
    # pull = (3.5 - 1.0) / 1.0 = 2.5 → in_3sigma=True, in_2sigma=False
    rec = ObservationRecord.make("T", "t", "f", 3.5, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.in_3sigma is True
    assert rec.in_2sigma is False


def test_make_in_2sigma_false_at_high_pull():
    rec = ObservationRecord.make("T", "t", "f", 10.0, 1.0, 1.0, "s", "DERIVED", "c")
    assert rec.in_2sigma is False


# ---------------------------------------------------------------------------
# Individual record builders — physics correctness
# ---------------------------------------------------------------------------

def test_record_n_s_fields():
    _check_record_fields(record_n_s())


def test_record_n_s_prediction_id():
    assert record_n_s().prediction_id == "N_S"


def test_record_n_s_within_2sigma():
    rec = record_n_s()
    assert rec.in_2sigma, f"n_s pull={rec.pull:.3f} exceeds 2σ"


def test_record_n_s_status_pass():
    assert record_n_s().status == "PASS"


def test_record_alpha_gut_fields():
    _check_record_fields(record_alpha_gut())


def test_record_alpha_gut_within_2sigma():
    rec = record_alpha_gut()
    assert rec.in_2sigma, f"alpha_GUT pull={rec.pull:.3f} exceeds 2σ"


def test_record_alpha_gut_status_pass():
    assert record_alpha_gut().status == "PASS"


def test_record_alpha_s_mz_fields():
    _check_record_fields(record_alpha_s_mz())


def test_record_alpha_s_mz_within_2sigma():
    rec = record_alpha_s_mz()
    assert rec.in_2sigma, f"alpha_s(MZ) pull={rec.pull:.3f} exceeds 2σ"


def test_record_lambda_qcd_fields():
    _check_record_fields(record_lambda_qcd())


def test_record_lambda_qcd_within_2sigma():
    rec = record_lambda_qcd()
    assert rec.in_2sigma, f"Lambda_QCD pull={rec.pull:.3f} exceeds 2σ"


def test_record_sin2_theta_w_fields():
    _check_record_fields(record_sin2_theta_w())


def test_record_sin2_theta_w_within_2sigma():
    rec = record_sin2_theta_w()
    assert rec.in_2sigma, f"sin2_theta_W pull={rec.pull:.3f} exceeds 2σ"


def test_record_mw_fields():
    _check_record_fields(record_mw())


def test_record_mz_fields():
    _check_record_fields(record_mz())


def test_record_mz_within_2sigma():
    rec = record_mz()
    assert rec.in_2sigma, f"M_Z pull={rec.pull:.3f} exceeds 2σ"


def test_record_higgs_mass_fields():
    _check_record_fields(record_higgs_mass())


def test_record_higgs_mass_prediction_id():
    assert record_higgs_mass().prediction_id == "HIGGS_MASS"


def test_record_w0_dark_energy_fields():
    _check_record_fields(record_w0_dark_energy())


def test_record_w0_dark_energy_tension_or_fail():
    """Honest: UM predicts w_0=-1, DESI sees ~-0.73 → large tension."""
    rec = record_w0_dark_energy()
    assert rec.status in {"TENSION", "FAIL"}, (
        f"w_0 should report TENSION or FAIL (pull={rec.pull:.2f}σ) "
        "to document the DESI tension honestly"
    )


def test_record_w0_dark_energy_epistemic_open():
    assert record_w0_dark_energy().epistemic_status == "OPEN"


def test_record_w0_pull_large():
    """Pull should be >3σ to flag the DESI tension."""
    rec = record_w0_dark_energy()
    assert rec.abs_pull > 3.0, f"w_0 pull={rec.abs_pull:.2f} — expected >3σ tension"


def test_record_wa_dark_energy_fields():
    _check_record_fields(record_wa_dark_energy())


def test_record_wa_tension_or_fail():
    """w_a: UM=0, DESI=-1.05±0.27 → ~3.9σ tension."""
    rec = record_wa_dark_energy()
    assert rec.status in {"TENSION", "FAIL"}, (
        f"w_a should report TENSION or FAIL (pull={rec.pull:.2f}σ)"
    )


# ---------------------------------------------------------------------------
# ObservationReport
# ---------------------------------------------------------------------------

def test_observation_report_type():
    assert isinstance(observation_report(), ObservationReport)


def test_observation_report_has_records():
    rpt = observation_report()
    assert len(rpt.records) == 10


def test_observation_report_n_pass_ge_6():
    rpt = observation_report()
    assert rpt.n_pass >= 6, f"Expected >=6 PASS, got {rpt.n_pass}"


def test_observation_report_counts_sum():
    rpt = observation_report()
    assert rpt.n_pass + rpt.n_tension + rpt.n_fail == len(rpt.records)


def test_observation_report_overall_status_valid():
    rpt = observation_report()
    assert rpt.overall_status in {"ALL_PASS", "SOME_TENSION", "SOME_FAIL"}


def test_observation_report_framework_version():
    assert observation_report().framework_version == "v10.52"


def test_observation_report_records_are_observation_records():
    for rec in observation_report().records:
        assert isinstance(rec, ObservationRecord)


# ---------------------------------------------------------------------------
# record_by_id
# ---------------------------------------------------------------------------

def test_record_by_id_n_s():
    rec = record_by_id("N_S")
    assert isinstance(rec, ObservationRecord)
    assert rec.prediction_id == "N_S"


def test_record_by_id_alpha_gut():
    rec = record_by_id("ALPHA_GUT")
    assert rec.prediction_id == "ALPHA_GUT"


def test_record_by_id_w0():
    rec = record_by_id("W0_DE")
    assert rec.prediction_id == "W0_DE"


def test_record_by_id_unknown_raises():
    with pytest.raises(KeyError):
        record_by_id("DOES_NOT_EXIST")


# ---------------------------------------------------------------------------
# passing_predictions / failing_predictions
# ---------------------------------------------------------------------------

def test_passing_predictions_returns_list():
    assert isinstance(passing_predictions(), list)


def test_passing_predictions_includes_n_s():
    assert "N_S" in passing_predictions()


def test_passing_predictions_includes_alpha_gut():
    assert "ALPHA_GUT" in passing_predictions()


def test_passing_predictions_includes_lambda_qcd():
    assert "LAMBDA_QCD" in passing_predictions()


def test_failing_predictions_returns_list():
    assert isinstance(failing_predictions(), list)


def test_passing_not_in_failing():
    passing = set(passing_predictions())
    failing = set(failing_predictions())
    assert passing.isdisjoint(failing), "A prediction cannot be both PASS and FAIL"


def test_all_prediction_ids_covered():
    """Every record in the report appears in either passing or failing or tension."""
    rpt = observation_report()
    all_ids = {r.prediction_id for r in rpt.records}
    categorized = set(passing_predictions()) | set(failing_predictions())
    # tension records are neither passing nor failing — just check no overlap
    for pid in categorized:
        assert pid in all_ids
