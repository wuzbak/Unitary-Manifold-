# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 506 LHC gluon-channel formal audit."""

import pytest

from src.core import pillar506_lhc_gluon_channel_formal_audit as p506


def test_constants():
    assert p506.PILLAR_NUMBER == 506
    assert p506.PILLAR_STATUS == "LHC_GLUON_CHANNEL_FORMAL_AUDIT_COMPLETE"


@pytest.mark.parametrize("mass", [4.0, 5.0, 6.0, 8.0])
def test_k_factor_reasonable(mass):
    k = p506.drell_yan_loop_k_factor(mass)
    assert 1.0 < k["k_factor"] < 1.4
    assert k["vertex"] > 0
    assert k["box"] > 0
    assert k["interference"] < 0


@pytest.mark.parametrize("mass", [5.0, 6.0, 8.0])
def test_pdf_uncertainty_below_threshold(mass):
    pdf = p506.pdf_uncertainty_band(mass)
    assert pdf["combined_fractional"] < 0.10
    assert pdf["below_10pct"] is True


@pytest.mark.parametrize("mass", [5.0, 6.0, 8.0])
def test_formal_sigma_ratio_band_ordered(mass):
    ratio = p506.formal_sigma_ratio(mass)
    assert ratio["sigma_ratio_low"] < ratio["sigma_ratio_central"] < ratio["sigma_ratio_high"]
    assert ratio["pdf_fractional"] < 0.10


def test_sigma_ratio_decreases_with_mass():
    assert p506.formal_sigma_ratio(6.0)["sigma_ratio_central"] < p506.formal_sigma_ratio(5.0)["sigma_ratio_central"]


def test_mass_bound_certificate_shape():
    cert = p506.mass_bound_certificate()
    assert cert["status"] == p506.PILLAR_STATUS
    assert cert["m_gkk_lower_bound_tev"] >= 5.0
    assert cert["pdf_below_10pct"] is True
    assert cert["verdict"] == "FORMAL_BOUND_CERTIFIED"


def test_ratio_at_6tev_safer_than_5tev():
    cert = p506.mass_bound_certificate()
    assert cert["ratio_at_6tev"] < cert["ratio_at_5tev"]


def test_hllhc_tripwire():
    tripwire = p506.hllhc_tripwire()
    assert tripwire["experiment"] == "HL-LHC Run 4"
    assert tripwire["m_gkk_lower_bound_tev"] >= 5.0


def test_report_shape():
    report = p506.pillar_report()
    assert report["pillar"] == 506
    assert report["hardgate_score_delta"] == 0.0
    assert "certificate" in report
