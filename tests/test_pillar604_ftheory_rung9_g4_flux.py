# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 604 — F-theory rung 9 G4 flux."""
from __future__ import annotations

import pytest

from src.core.pillar604_ftheory_rung9_g4_flux_quantization import (
    G4_CONSISTENT,
    G4_FLUX_QUANTIZATION_HALF_INTEGER,
    K_CS_HALF,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    VERSION,
    d3_tadpole_consistency,
    g4_flux_quantization,
    pillar_report,
)

PRIMARY = g4_flux_quantization()
REPORT = pillar_report()

PRIMARY_KEYS = ["half_integer_shift", "k_cs_half", "g4_consistent", "chi_over_two", "integrality_condition"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "g4_flux_quantization", "d3_tadpole_consistency", "toe_score_delta"]
NUMERIC_CHECKS = [
    G4_FLUX_QUANTIZATION_HALF_INTEGER is True,
    K_CS_HALF == 37,
    G4_CONSISTENT is True,
    PRIMARY["chi_over_two"] == 37,
    d3_tadpole_consistency()["tadpole_safe"] is True,
    REPORT["adjacent_track"] is True,
]
STRING_CHECKS = [
    PILLAR_STATUS == "FTHEORY_RUNG9_G4_FLUX_QUANTIZATION_CONSISTENT_ADJACENT",
    VERSION == "v20.4",
    "G4 Flux" in PILLAR_TITLE,
    PRIMARY["integrality_condition"] == "Z + chi(S)/2",
    d3_tadpole_consistency()["g4_consistent"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 604
    assert PILLAR_STATUS == "FTHEORY_RUNG9_G4_FLUX_QUANTIZATION_CONSISTENT_ADJACENT"



def test_constants() -> None:
    assert REPORT["hardgate_score_delta"] == 0.0
    assert PRIMARY["half_integer_shift"] is True


@pytest.mark.parametrize("key", PRIMARY_KEYS)
def test_primary_keys(key: str) -> None:
    assert key in PRIMARY


@pytest.mark.parametrize("key", REPORT_KEYS)
def test_report_keys(key: str) -> None:
    assert key in REPORT


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
