# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import math
import pytest

from src.core.phi_radion_quantization import (
    K_CS,
    OMEGA_RADION,
    PI_KR,
    ZERO_POINT_ENERGY,
    canonical_quantization_report,
    expectation_values,
    jax_ground_state_normalization,
    mpmath_ground_state_audit,
    probability_normalization,
    radion_energy_level,
    radion_energy_spectrum,
)


def test_geometric_frequency_matches_inverse_sqrt_kcs():
    assert OMEGA_RADION == (K_CS ** 0.5) / (2.0 * PI_KR)
    assert OMEGA_RADION == 1.0 / math.sqrt(74.0)


def test_zero_point_energy_formula():
    assert ZERO_POINT_ENERGY == 0.5 * OMEGA_RADION


def test_energy_spectrum_uniform_spacing():
    result = radion_energy_spectrum(4)
    assert result["uniform_spacing"] is True
    assert all(abs(s - OMEGA_RADION) < 1e-12 for s in result["spacings"])


def test_energy_level_1_above_ground():
    assert radion_energy_level(1) > radion_energy_level(0)


def test_ground_state_normalization_close_to_one():
    result = probability_normalization(level=0)
    assert result["abs_error"] < 5e-4


def test_first_excited_state_normalization_close_to_one():
    result = probability_normalization(level=1)
    assert result["abs_error"] < 5e-4


def test_ground_state_expectation_is_centered():
    result = expectation_values(level=0)
    assert abs(result["mean_phi"] - 1.0) < 1e-3


def test_jax_ground_state_normalization_passes():
    pytest.importorskip("jax")
    result = jax_ground_state_normalization()
    assert result["jax_available"] is True
    assert result["passed"] is True


def test_mpmath_256bit_audit_passes():
    result = mpmath_ground_state_audit(80)
    assert result["mpmath_available"] is True
    assert result["passed"] is True


def test_canonical_quantization_report_closed():
    pytest.importorskip("jax")
    report = canonical_quantization_report()
    assert report["status"] == "LOCAL_CANONICAL_CLOSURE"
    assert report["jax_ground_state"]["passed"] is True
    assert report["precision_256bit"]["passed"] is True
