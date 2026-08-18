# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 701 — CMB amplitude layer synthesis."""
from __future__ import annotations

from src.core.pillar701_cmb_amplitude_layer_synthesis import (
    A_S_LCDM,
    PILLAR_NUMBER,
    amplitude_layer_synthesis,
    cmb_amplitude_final_status,
)

SYNTHESIS = amplitude_layer_synthesis()
FINAL = cmb_amplitude_final_status()
LAYERS = SYNTHESIS["layers"]


def test_pillar_number():
    assert PILLAR_NUMBER == 701


def test_layer_count():
    assert len(LAYERS) == 4


def test_layer_names_ordered():
    assert [layer["layer"] for layer in LAYERS] == [0, 1, 2, 3]


def test_baseline_layer_reference():
    assert LAYERS[0]["name"] == "LCDM_BASELINE"
    assert LAYERS[0]["a_s"] == A_S_LCDM


def test_phase1_partial():
    assert LAYERS[1]["status"] == "PARTIAL"


def test_phase2_closed():
    assert LAYERS[2]["status"] == "PHASE2_CLOSED"


def test_final_layer_honest_name():
    assert "SIMPLIFIED" in LAYERS[3]["name"]


def test_coverage_monotonic():
    coverages = [layer["coverage_fraction"] for layer in LAYERS]
    assert coverages[0] <= coverages[1] <= coverages[2] <= coverages[3]


def test_boltzmann_gain_gt_one():
    assert SYNTHESIS["boltzmann_gain"] > 1.0


def test_final_coverage_bounded():
    assert 0.0 < SYNTHESIS["final_coverage_fraction"] <= 1.0


def test_final_status_valid():
    assert FINAL["status"] in {"CLOSED", "ARCHITECTURE_LIMIT"}


def test_final_status_matches_coverage():
    assert FINAL["status"] == "CLOSED"
