# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.z2_odd_power_suppression import (
    corrected_tensor_to_scalar_ratio,
    z2_odd_scalar_suppression,
    z2_odd_tensor_suppression,
    al1_al2_delta_report,
)


def test_scalar_tensor_suppression_fractions():
    scalar = z2_odd_scalar_suppression()
    tensor = z2_odd_tensor_suppression()
    assert scalar["odd_fraction_removed"] == 25.0 / 74.0
    assert scalar["observed_fraction_remaining"] == 49.0 / 74.0
    assert tensor["odd_fraction_removed"] == 49.0 / 74.0
    assert tensor["observed_fraction_remaining"] == 25.0 / 74.0


def test_r_correction_ratio():
    out = corrected_tensor_to_scalar_ratio()
    assert out["ratio_25_over_49"] == 25.0 / 49.0
    assert abs(out["r_corrected"] - (0.0315 * 25.0 / 49.0)) < 1e-12


def test_al1_al2_falsification_checks():
    report = al1_al2_delta_report()
    assert report["al1_check"]["within_1pct"] is True
    assert report["al2_check"]["approaches_bound"] is True
    assert report["status"] == "FITTED"

