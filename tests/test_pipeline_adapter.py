# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pipeline_adapter.py
==============================
Pytest test suite for src/core/pipeline_adapter.py (73 tests).

Covers:
  - Return types and dataclass field presence
  - Physical value ranges for all predictions
  - Observational pull and status logic
  - UncertaintyBudget sign and quadrature
  - Custom-parameter variations
  - full_pipeline_report() aggregate
"""
from __future__ import annotations

import math
import pytest

from src.core.pipeline_adapter import (
    ObservationalComparator,
    PipelineManifest,
    PredictionCertificate,
    ProcessingStep,
    UncertaintyBudget,
    full_pipeline_report,
    pipeline_alpha_gut,
    pipeline_kk_tower,
    pipeline_lambda_qcd,
    pipeline_ns_r,
)


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture(scope="module")
def cert_ns_r() -> PredictionCertificate:
    return pipeline_ns_r()


@pytest.fixture(scope="module")
def cert_alpha() -> PredictionCertificate:
    return pipeline_alpha_gut()


@pytest.fixture(scope="module")
def cert_kk() -> PredictionCertificate:
    return pipeline_kk_tower()


@pytest.fixture(scope="module")
def cert_lqcd() -> PredictionCertificate:
    return pipeline_lambda_qcd()


@pytest.fixture(scope="module")
def report() -> dict:
    return full_pipeline_report()


# ===========================================================================
# PredictionCertificate return-type tests
# ===========================================================================

class TestReturnTypes:
    def test_ns_r_is_certificate(self, cert_ns_r):
        assert isinstance(cert_ns_r, PredictionCertificate)

    def test_alpha_gut_is_certificate(self, cert_alpha):
        assert isinstance(cert_alpha, PredictionCertificate)

    def test_kk_tower_is_certificate(self, cert_kk):
        assert isinstance(cert_kk, PredictionCertificate)

    def test_lambda_qcd_is_certificate(self, cert_lqcd):
        assert isinstance(cert_lqcd, PredictionCertificate)


# ===========================================================================
# PipelineManifest field tests
# ===========================================================================

class TestPipelineManifest:
    def test_ns_r_manifest_run_id(self, cert_ns_r):
        assert cert_ns_r.manifest.run_id == "um_ns_r_v1"

    def test_ns_r_manifest_framework_version(self, cert_ns_r):
        assert cert_ns_r.manifest.framework_version == "v10.52"

    def test_ns_r_manifest_has_parameters(self, cert_ns_r):
        assert isinstance(cert_ns_r.manifest.parameters, dict)
        assert "phi0_bare" in cert_ns_r.manifest.parameters
        assert "n_w" in cert_ns_r.manifest.parameters
        assert "c_s" in cert_ns_r.manifest.parameters

    def test_ns_r_manifest_assumptions_is_tuple(self, cert_ns_r):
        assert isinstance(cert_ns_r.manifest.assumptions, tuple)
        assert len(cert_ns_r.manifest.assumptions) >= 1

    def test_manifest_created_utc_is_string(self, cert_ns_r):
        utc = cert_ns_r.manifest.created_utc
        assert isinstance(utc, str)
        assert "T" in utc   # ISO8601 shape

    def test_alpha_manifest_run_id(self, cert_alpha):
        assert cert_alpha.manifest.run_id == "um_alpha_gut_v1"

    def test_kk_manifest_run_id(self, cert_kk):
        assert cert_kk.manifest.run_id == "um_kk_tower_v1"

    def test_lqcd_manifest_run_id(self, cert_lqcd):
        assert cert_lqcd.manifest.run_id == "um_lambda_qcd_v1"


# ===========================================================================
# ProcessingStep field tests
# ===========================================================================

class TestProcessingStep:
    def test_ns_r_has_two_steps(self, cert_ns_r):
        assert len(cert_ns_r.steps) == 2

    def test_ns_r_step1_output_name(self, cert_ns_r):
        assert cert_ns_r.steps[0].output_name == "n_s"

    def test_ns_r_step2_output_name(self, cert_ns_r):
        assert cert_ns_r.steps[1].output_name == "r"

    def test_processing_step_precision_bits(self, cert_ns_r):
        for step in cert_ns_r.steps:
            assert step.precision_bits in (64, 128)

    def test_step_inputs_is_dict(self, cert_ns_r):
        for step in cert_ns_r.steps:
            assert isinstance(step.inputs, dict)

    def test_step_formula_description_nonempty(self, cert_ns_r):
        for step in cert_ns_r.steps:
            assert len(step.formula_description) > 0

    def test_kk_tower_has_n_modes_steps(self, cert_kk):
        assert len(cert_kk.steps) == 5   # default n_modes=5

    def test_kk_m0_is_zero(self, cert_kk):
        m0_step = cert_kk.steps[0]
        assert m0_step.output_value == pytest.approx(0.0)

    def test_kk_m1_equals_M_KK(self, cert_kk):
        m1_step = cert_kk.steps[1]
        assert m1_step.output_value == pytest.approx(1.0)   # default M_KK_TeV=1.0

    def test_kk_m2_equals_2M_KK(self, cert_kk):
        m2_step = cert_kk.steps[2]
        assert m2_step.output_value == pytest.approx(2.0)

    def test_kk_tower_custom_modes(self):
        cert = pipeline_kk_tower(M_KK_TeV=2.0, n_modes=3)
        assert len(cert.steps) == 3
        assert cert.steps[0].output_value == pytest.approx(0.0)
        assert cert.steps[1].output_value == pytest.approx(2.0)
        assert cert.steps[2].output_value == pytest.approx(4.0)


# ===========================================================================
# UncertaintyBudget tests
# ===========================================================================

class TestUncertaintyBudget:
    def test_budget_total_nonnegative(self, cert_ns_r):
        assert cert_ns_r.uncertainty_budget.total >= 0.0

    def test_budget_statistical_nonnegative(self, cert_ns_r):
        assert cert_ns_r.uncertainty_budget.statistical >= 0.0

    def test_budget_systematic_nonnegative(self, cert_ns_r):
        assert cert_ns_r.uncertainty_budget.systematic >= 0.0

    def test_budget_truncation_nonnegative(self, cert_ns_r):
        assert cert_ns_r.uncertainty_budget.truncation >= 0.0

    def test_budget_dominant_source_valid(self, cert_ns_r):
        valid = {"statistical", "systematic", "truncation", "architecture_limit"}
        assert cert_ns_r.uncertainty_budget.dominant_source in valid

    def test_budget_total_at_least_largest_component(self, cert_ns_r):
        b = cert_ns_r.uncertainty_budget
        largest = max(b.statistical, b.systematic, b.truncation)
        assert b.total >= largest - 1e-15

    def test_alpha_budget_total_positive(self, cert_alpha):
        assert cert_alpha.uncertainty_budget.total > 0.0

    def test_lqcd_budget_prediction_id(self, cert_lqcd):
        assert cert_lqcd.uncertainty_budget.prediction_id == "lambda_qcd"


# ===========================================================================
# ObservationalComparator tests
# ===========================================================================

class TestObservationalComparator:
    def test_pull_formula_pass(self):
        obs = ObservationalComparator.make("test", 1.0, 1.0, 0.1, "TestSource")
        assert obs.pull == pytest.approx(0.0)
        assert obs.in_2sigma is True
        assert obs.status == "PASS"

    def test_pull_formula_tension(self):
        # pull = (2.5 - 0.0) / 1.0 = 2.5  → TENSION
        obs = ObservationalComparator.make("test", 2.5, 0.0, 1.0, "TestSource")
        assert obs.pull == pytest.approx(2.5)
        assert obs.in_2sigma is False
        assert obs.status == "TENSION"

    def test_pull_formula_fail(self):
        # pull = (4.0 - 0.0) / 1.0 = 4.0 → FAIL
        obs = ObservationalComparator.make("test", 4.0, 0.0, 1.0, "TestSource")
        assert obs.pull == pytest.approx(4.0)
        assert obs.status == "FAIL"

    def test_status_pass_boundary(self):
        # exactly 2.0 sigma → PASS
        obs = ObservationalComparator.make("test", 2.0, 0.0, 1.0, "TestSource")
        assert obs.status == "PASS"

    def test_status_tension_boundary(self):
        # exactly 3.0 sigma → TENSION
        obs = ObservationalComparator.make("test", 3.0, 0.0, 1.0, "TestSource")
        assert obs.status == "TENSION"

    def test_negative_pull_in_2sigma(self):
        obs = ObservationalComparator.make("test", 0.5, 1.0, 0.5, "TestSource")
        assert obs.pull == pytest.approx(-1.0)
        assert obs.in_2sigma is True

    def test_zero_sigma_gives_inf_pull(self):
        obs = ObservationalComparator.make("test", 1.0, 0.5, 0.0, "TestSource")
        assert math.isinf(obs.pull)


# ===========================================================================
# pipeline_ns_r() value tests
# ===========================================================================

class TestPipelineNsR:
    def test_ns_r_overall_status_pass_or_tension(self, cert_ns_r):
        assert cert_ns_r.overall_status in ("PASS", "TENSION")

    def test_n_s_between_096_and_097(self, cert_ns_r):
        n_s = cert_ns_r.steps[0].output_value
        assert 0.960 <= n_s <= 0.970

    def test_r_below_bicep_limit(self, cert_ns_r):
        r = cert_ns_r.steps[1].output_value
        assert r < 0.036

    def test_r_positive(self, cert_ns_r):
        r = cert_ns_r.steps[1].output_value
        assert r > 0.0

    def test_ns_planck_within_2sigma(self, cert_ns_r):
        obs = cert_ns_r.observational
        assert abs(obs.pull) <= 2.0

    def test_observational_source_planck(self, cert_ns_r):
        assert cert_ns_r.observational.observational_source == "Planck2018"

    def test_custom_phi0_changes_ns(self):
        cert_default = pipeline_ns_r()
        cert_custom = pipeline_ns_r(phi0=2.0)
        ns_default = cert_default.steps[0].output_value
        ns_custom = cert_custom.steps[0].output_value
        assert ns_default != pytest.approx(ns_custom)

    def test_custom_phi0_changes_r(self):
        cert1 = pipeline_ns_r(phi0=1.5)
        cert2 = pipeline_ns_r(phi0=2.0)
        r1 = cert1.steps[1].output_value
        r2 = cert2.steps[1].output_value
        assert r1 != pytest.approx(r2)

    def test_larger_nw_larger_ns_fixed_phi0(self):
        # With fixed bare vev phi0, larger n_w → larger phi_eff → smaller 1-n_s → larger n_s
        cert5 = pipeline_ns_r(phi0=1.0, n_w=5)
        cert7 = pipeline_ns_r(phi0=1.0, n_w=7)
        ns5 = cert5.steps[0].output_value
        ns7 = cert7.steps[0].output_value
        assert ns7 > ns5


# ===========================================================================
# pipeline_alpha_gut() value tests
# ===========================================================================

class TestPipelineAlphaGut:
    def test_alpha_gut_value_approx(self, cert_alpha):
        alpha = cert_alpha.steps[0].output_value
        assert 0.039 <= alpha <= 0.043

    def test_alpha_gut_pull_within_3sigma(self, cert_alpha):
        assert abs(cert_alpha.observational.pull) <= 3.0

    def test_alpha_gut_status_not_fail(self, cert_alpha):
        assert cert_alpha.overall_status != "FAIL"

    def test_alpha_gut_observational_source(self, cert_alpha):
        assert cert_alpha.observational.observational_source == "PDG2024"

    def test_alpha_gut_custom_params(self):
        cert = pipeline_alpha_gut(N_C=3, K_CS=74, gamma_SU5=1.0)
        alpha = cert.steps[0].output_value
        assert alpha == pytest.approx(3 / 74)


# ===========================================================================
# pipeline_kk_tower() value tests
# ===========================================================================

class TestPipelineKkTower:
    def test_kk_tower_status_pass(self, cert_kk):
        assert cert_kk.overall_status in ("PASS", "TENSION")

    def test_kk_masses_monotone(self, cert_kk):
        vals = [s.output_value for s in cert_kk.steps]
        assert vals == sorted(vals)

    def test_kk_mass_spacing_uniform(self, cert_kk):
        vals = [s.output_value for s in cert_kk.steps]
        diffs = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        for d in diffs:
            assert d == pytest.approx(diffs[0])

    def test_kk_default_n_modes_5(self, cert_kk):
        assert len(cert_kk.steps) == 5

    def test_kk_manifest_has_M_KK(self, cert_kk):
        assert "M_KK_TeV" in cert_kk.manifest.parameters


# ===========================================================================
# pipeline_lambda_qcd() value tests
# ===========================================================================

class TestPipelineLambdaQcd:
    def test_lqcd_value_in_range(self, cert_lqcd):
        lqcd = cert_lqcd.steps[1].output_value
        assert 0.1 <= lqcd <= 1.0   # physical range

    def test_lqcd_near_pdg_332_mev(self, cert_lqcd):
        lqcd = cert_lqcd.steps[1].output_value
        assert abs(lqcd - 0.332) < 0.25   # within 250 MeV of PDG

    def test_lqcd_status_pass_or_tension(self, cert_lqcd):
        assert cert_lqcd.overall_status in ("PASS", "TENSION")

    def test_lqcd_two_steps(self, cert_lqcd):
        assert len(cert_lqcd.steps) == 2

    def test_lqcd_step1_alpha_s(self, cert_lqcd):
        assert cert_lqcd.steps[0].output_name == "alpha_s_mz"

    def test_lqcd_step2_lambda(self, cert_lqcd):
        assert cert_lqcd.steps[1].output_name == "lambda_qcd_GeV"

    def test_lqcd_observational_source(self, cert_lqcd):
        assert cert_lqcd.observational.observational_source == "PDG2024"


# ===========================================================================
# full_pipeline_report() tests
# ===========================================================================

class TestFullPipelineReport:
    def test_report_returns_dict(self, report):
        assert isinstance(report, dict)

    def test_report_has_ns_r_key(self, report):
        assert "ns_r_certificate" in report

    def test_report_has_alpha_gut_key(self, report):
        assert "alpha_gut_certificate" in report

    def test_report_has_kk_tower_key(self, report):
        assert "kk_tower_certificate" in report

    def test_report_has_lambda_qcd_key(self, report):
        assert "lambda_qcd_certificate" in report

    def test_report_overall_pass_is_true(self, report):
        assert report["overall_pass"] is True

    def test_report_framework_version(self, report):
        assert report["framework_version"] == "v10.52"

    def test_report_certificates_are_prediction_certificates(self, report):
        for key in ("ns_r_certificate", "alpha_gut_certificate",
                    "kk_tower_certificate", "lambda_qcd_certificate"):
            assert isinstance(report[key], PredictionCertificate)

    def test_report_all_statuses_not_fail(self, report):
        for key in ("ns_r_certificate", "alpha_gut_certificate",
                    "kk_tower_certificate", "lambda_qcd_certificate"):
            assert report[key].overall_status != "FAIL"
