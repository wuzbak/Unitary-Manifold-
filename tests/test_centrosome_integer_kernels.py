# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for centrosome integer-kernel decomposition."""

from __future__ import annotations

import pytest

from src.biology.centrosome_integer_kernels import (
    bc_protofilament_count,
    centriole_triplet_count,
    centrosome_integer_kernel_report,
    curvature_tensor_component_count,
)


def test_triplet_count_specializes_to_nine():
    assert centriole_triplet_count() == 9


def test_bc_protofilaments_specialize_to_ten():
    assert bc_protofilament_count() == 10


def test_curvature_component_count_is_nine():
    assert curvature_tensor_component_count() == 9


def test_report_promotes_only_count_identities():
    report = centrosome_integer_kernel_report()
    assert report["triplet_kernel_status"] == "DERIVED_STRUCTURAL"
    assert report["protofilament_kernel_status"] == "DERIVED_STRUCTURAL"
    assert report["mechanism_status"] == "FALSIFIABLE_PREDICTION"


@pytest.mark.parametrize("bad_dims", [-1, -3])
def test_triplet_count_rejects_negative_spatial_dims(bad_dims: int):
    with pytest.raises(ValueError):
        centriole_triplet_count(spatial_dims=bad_dims)


def test_curvature_count_rejects_zero_dimensional_block():
    with pytest.raises(ValueError):
        curvature_tensor_component_count(0)
