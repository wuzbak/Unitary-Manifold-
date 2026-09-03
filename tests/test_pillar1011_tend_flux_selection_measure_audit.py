# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1011 — 10D flux selection measure audit."""

from src.core.pillar1011_tend_flux_selection_measure_audit import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    flux_selection_measure_audit,
    flux_selection_measure_table,
)


def test_identity_constants():
    assert PILLAR_NUMBER == 1011
    assert PILLAR_GATE == "TEN_D_FLUX_SELECTION_MEASURE_AUDIT"
    assert PILLAR_STATUS == "TEN_D_FLUX_SELECTION_MEASURE_AUDIT_COMPLETE"


def test_measure_table_shape_and_normalization():
    table = flux_selection_measure_table()
    assert len(table) == 2
    assert [row["n_w"] for row in table] == [5, 7]
    total = sum(float(row["normalized_measure"]) for row in table)
    assert abs(total - 1.0) < 1e-12


def test_unique_support_on_nw5():
    table = flux_selection_measure_table()
    row5 = next(row for row in table if row["n_w"] == 5)
    row7 = next(row for row in table if row["n_w"] == 7)
    assert row5["survives_flux_background"] is True
    assert row5["normalized_measure"] > 0.0
    assert row7["survives_flux_background"] is False
    assert row7["normalized_measure"] == 0.0


def test_full_audit_valid():
    report = flux_selection_measure_audit()
    assert report["r5_hard_gate_pass"] is True
    assert report["effective_flux_sufficiency"]["meets_bp_threshold"] is True
    assert report["explicit_selection"]["explicit_selection_pass"] is True
    assert report["selected_n_w"] == 5
    assert report["measure_unique_support"] is True
    assert report["valid"] is True
