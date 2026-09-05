# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1044_su3_functional_bridge_alignment import (
    HIGH_LEVEL_REMAINING_BURDEN,
    LEAN4_THEOREM_COUNT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1044_summary,
    su3_functional_bridge_alignment,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1044
    assert PILLAR_GATE == "SU3_FUNCTIONAL_BRIDGE_ALIGNMENT"
    assert PILLAR_STATUS == "SU3_FUNCTIONAL_BRIDGE_ALIGNMENT_COMPLETE"


def test_lean4_counts() -> None:
    report = su3_functional_bridge_alignment()
    assert report["lean4_kernel"]["theorem_count"] == LEAN4_THEOREM_COUNT
    assert report["valid"] is True


def test_remaining_burden_preserved() -> None:
    report = su3_functional_bridge_alignment()
    assert report["high_level_remaining_burden"] == HIGH_LEVEL_REMAINING_BURDEN
    assert report["substep_map"]["after"] == report["substep_map"]["before"]
    assert set(report["dependency"]["residual_map"]["open_steps_after"]) <= set(report["substep_map"]["after"])
    assert report["scientific_progress"] is False
    assert report["physical_theorem_proved"] is False


def test_summary() -> None:
    summary = pillar1044_summary()
    assert PILLAR_VALID is True
    assert summary["status"] == PILLAR_STATUS
