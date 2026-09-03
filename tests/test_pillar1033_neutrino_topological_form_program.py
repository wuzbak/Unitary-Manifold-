# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1033 — neutrino topological-form program."""

from src.core.pillar1033_neutrino_topological_form_program import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    PILLAR964_UV_FRACTION,
    neutrino_topological_form_program,
    pillar1033_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1033
    assert PILLAR_GATE == "NEUTRINO_TOPOLOGICAL_FORM_PROGRAM"
    assert PILLAR_STATUS == "NEUTRINO_TOPOLOGICAL_FORM_PROGRAM_COMPLETE"
    assert PILLAR_VALID is True


def test_uv_ir_separation_is_reported_honestly() -> None:
    report = neutrino_topological_form_program()
    assert report["uv_fraction"] == PILLAR964_UV_FRACTION
    assert report["uv_ir_gap"] > 0.01
    assert report["closure_earned"] is False
    assert report["named_residual"] == "CL_PHYS_IR_SHIFT_FROM_RGE"
    assert report["outcome"] == "NEUTRINO_UV_IR_SEPARATION_CERTIFIED"


def test_summary() -> None:
    summary = pillar1033_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True

