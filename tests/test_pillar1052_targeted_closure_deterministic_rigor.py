# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1052_targeted_closure_deterministic_rigor import (
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    targeted_closure_deterministic_rigor,
    pillar1052_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1052
    assert PILLAR_GATE == "TARGETED_CLOSURE_DETERMINISTIC_RIGOR"
    assert PILLAR_STATUS == "TARGETED_CLOSURE_DETERMINISTIC_RIGOR_COMPLETE"
    assert PILLAR_VALID is True


def test_lean4_delta() -> None:
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA == 12


def test_report_valid() -> None:
    report = targeted_closure_deterministic_rigor()
    assert report["valid"] is True
    assert report["deterministic_gate_coverage"] is True
    assert report["formal_open_substeps"]["after"] == report["formal_open_substeps"]["before"]
    assert report["scientific_progress"] is False
    assert report["physical_theorem_proved"] is False
    assert report["lean4"]["compilation_verified"] is False
    assert report["lean4"]["physical_theorem_count_verified"] == 0
    assert "CARRY_FORWARD_OPEN" in set(report["closure_attempts"].values())


def test_summary() -> None:
    summary = pillar1052_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
