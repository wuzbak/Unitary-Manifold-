# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 504 lattice braid Phase-4 condensate bounds."""

import pytest

from src.core import pillar504_lattice_braid_phase4_np_condensate as p504


def test_constants():
    assert p504.PILLAR_NUMBER == 504
    assert p504.PILLAR_STATUS == "LATTICE_BRAID_PHASE4_NP_CONDENSATE_BOUNDED"
    assert "ADJACENT" in p504.ADJACENCY_TRACK_LABEL
    assert len(p504.FINITE_VOLUME_SIZES) >= 6


@pytest.mark.parametrize("size", [16, 24, 32, 48, 64, 96, 128])
def test_finite_volume_condensate_positive(size):
    result = p504.finite_volume_condensate(size)
    assert result["size"] == float(size)
    assert result["condensate"] > 0
    assert 0 < result["finite_volume_loss"] < 1


@pytest.mark.parametrize("bad_size", [0, -1, -16])
def test_finite_volume_rejects_bad_size(bad_size):
    with pytest.raises(ValueError):
        p504.finite_volume_condensate(bad_size)


def test_sequence_uses_default_sizes():
    seq = p504.np_condensate_sequence()
    assert len(seq) == len(p504.FINITE_VOLUME_SIZES)
    assert [int(item["size"]) for item in seq] == p504.FINITE_VOLUME_SIZES


def test_custom_sequence():
    seq = p504.np_condensate_sequence([8, 16, 32])
    assert len(seq) == 3
    assert seq[0]["size"] == 8.0


def test_residual_band_ordering():
    band = p504.phase4_residual_band()
    assert band["delta_gamma_lower"] < band["delta_gamma_central"] < band["delta_gamma_upper"]
    assert band["target"] > 0


def test_residual_band_coverable():
    assert p504.phase4_residual_band()["sub_1pct_coverable"] is True


def test_best_case_remaining_nonnegative():
    assert p504.phase4_residual_band()["best_case_remaining"] >= 0


def test_central_remaining_less_than_target():
    band = p504.phase4_residual_band()
    assert band["central_remaining"] < band["target"]


def test_certificate_shape():
    cert = p504.l2_closure_certificate()
    assert cert["pillar"] == 504
    assert cert["adjacent_track"] is True
    assert cert["external_hmc_receipt"] is False
    assert cert["hardgate_score_delta"] == 0.0


def test_certificate_retains_honesty():
    cert = p504.l2_closure_certificate()
    assert "BOUNDED" in cert["epistemic_delta"]


def test_report_shape():
    report = p504.pillar_report()
    assert report["pillar"] == 504
    assert "certificate" in report
