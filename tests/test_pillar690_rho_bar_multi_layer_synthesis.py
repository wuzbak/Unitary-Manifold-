# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 690 — rho-bar multi-layer synthesis."""
from __future__ import annotations

import pytest

from src.core.pillar690_rho_bar_multi_layer_synthesis import (
    LAYER0_RHO_BAR,
    LAYER1_RHO_BAR,
    W_RHOBAR_PDG,
    final_rho_bar_status,
    layer_improvement_table,
    multi_layer_synthesis,
)


@pytest.fixture(scope="module")
def table():
    return layer_improvement_table()


@pytest.fixture(scope="module")
def status():
    return final_rho_bar_status()


@pytest.fixture(scope="module")
def synthesis():
    return multi_layer_synthesis()


def test_table_is_list(table):
    assert isinstance(table, list)


def test_table_has_three_layers(table):
    assert len(table) == 3


def test_layer0_value(table):
    assert table[0]["rho_bar"] == pytest.approx(LAYER0_RHO_BAR)


def test_layer1_value(table):
    assert table[1]["rho_bar"] == pytest.approx(LAYER1_RHO_BAR)


def test_layer2_value(table):
    assert table[2]["rho_bar"] == pytest.approx(0.0961145280, abs=1e-10)


def test_layer0_gap(table):
    assert table[0]["gap_percent"] == pytest.approx(28.9308176101, abs=1e-8)


def test_layer1_gap(table):
    assert table[1]["gap_percent"] == pytest.approx(25.1572327044, abs=1e-8)


def test_layer2_gap(table):
    assert table[2]["gap_percent"] == pytest.approx(39.5506113051, abs=1e-8)


def test_layer1_best_improvement_over_layer0(table):
    assert table[1]["improvement_vs_layer0_percent_points"] > 0.0


def test_layer2_negative_improvement_over_layer0(table):
    assert table[2]["improvement_vs_layer0_percent_points"] < 0.0


def test_status_is_dict(status):
    assert isinstance(status, dict)


def test_status_architecture_limit(status):
    assert status["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_status_best_layer_is_subleading(status):
    assert status["best_layer"]["layer"] == 1


def test_status_final_layer_is_fn(status):
    assert status["final_layer"]["layer"] == 2


def test_status_final_gap_large(status):
    assert status["final_gap_percent"] > 10.0


def test_status_fails_10_percent(status):
    assert status["passes_10_percent"] is False


def test_status_fails_5_percent(status):
    assert status["passes_5_percent"] is False


def test_status_honest_note_mentions_over_rotates(status):
    assert "over-rotates" in status["honest_note"] or "does not monotonically improve" in status["honest_note"]


def test_synthesis_is_dict(synthesis):
    assert isinstance(synthesis, dict)


def test_synthesis_pdg_constant(synthesis):
    assert synthesis["rho_bar_pdg"] == pytest.approx(W_RHOBAR_PDG)


def test_synthesis_embeds_layers(synthesis, table):
    assert synthesis["layers"] == table


def test_synthesis_embeds_status(synthesis, status):
    assert synthesis["final_status"]["best_layer"]["layer"] == status["best_layer"]["layer"]
