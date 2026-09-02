# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 984 — Compactification Parameter Object."""

from __future__ import annotations

from src.core.pillar984_compactification_parameter_object import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    canonical_compactification_parameters,
    compactification_parameter_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 984
    assert PILLAR_STATUS == "COMPACTIFICATION_PARAMETER_OBJECT_COMPLETE"
    assert PILLAR_VALID is True


def test_canonical_values() -> None:
    obj = canonical_compactification_parameters()
    assert obj.n_w == 5
    assert obj.k_cs == 74
    assert obj.chi_cy4 == 1820
    assert obj.is_valid() is True


def test_summary_valid() -> None:
    summary = compactification_parameter_summary()
    assert summary["valid"] is True
    assert "parameters" in summary
