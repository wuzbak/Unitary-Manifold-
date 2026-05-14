# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import numpy as np

from src.core.metric import assemble_5d_metric
from src.core.metric_ansatz_derivation import (
    assemble_derived_5d_metric,
    derive_metric_ansatz_from_deeper_principle,
    metric_ansatz_derivation_certificate,
)


def test_derivation_checks_pass():
    result = derive_metric_ansatz_from_deeper_principle()
    assert result["all_checks_pass"] is True


def test_derivation_fixes_expected_block_form():
    result = derive_metric_ansatz_from_deeper_principle()
    form = result["derived_form"]
    assert "lambda^2 phi^2" in form["G_munu"]
    assert "lambda phi B_mu" in form["G_mu5"]
    assert form["G_55"] == "phi^2"


def test_derived_coefficients_satisfy_completion_identity():
    result = derive_metric_ansatz_from_deeper_principle(lam=1.7)
    coeffs = result["coefficients"]
    assert abs(coeffs.bmu_quadratic_prefactor - coeffs.bmu_linear_prefactor**2) < 1e-14


def test_derived_assembly_matches_metric_module():
    rng = np.random.default_rng(123)
    n = 7
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (n, 1, 1)) + 1e-4 * rng.standard_normal((n, 4, 4))
    g = 0.5 * (g + np.transpose(g, (0, 2, 1)))
    B = 1e-3 * rng.standard_normal((n, 4))
    phi = 1.0 + 1e-3 * rng.standard_normal(n)

    derived = assemble_derived_5d_metric(g, B, phi, lam=1.0)
    canonical = assemble_5d_metric(g, B, phi, lam=1.0)
    np.testing.assert_allclose(derived, canonical, atol=1e-12, rtol=0.0)


def test_derivation_certificate_passes():
    cert = metric_ansatz_derivation_certificate()
    assert cert["status"] == "DERIVED_FROM_DEEPER_PRINCIPLE"
    assert cert["passed"] is True
    assert cert["max_abs_error_vs_metric_module"] < 1e-12
