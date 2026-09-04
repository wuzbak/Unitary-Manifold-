# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1042_uv_joint_bottleneck_continuation import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1042_summary,
    uv_joint_bottleneck_continuation,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1042
    assert PILLAR_GATE == "UV_JOINT_BOTTLENECK_CONTINUATION"
    assert PILLAR_STATUS == "UV_JOINT_BOTTLENECK_CONTINUATION_COMPLETE"


def test_joint_narrowing() -> None:
    report = uv_joint_bottleneck_continuation()
    assert report["fractional_reductions"]["alpha_s_fractional_reduction"] > 0.0
    assert report["fractional_reductions"]["higgs_fractional_reduction"] > 0.0
    assert report["valid"] is True


def test_shared_packet_retained() -> None:
    report = uv_joint_bottleneck_continuation()
    assert report["shared_object_still_required"] is True
    assert report["joint_bottleneck_pressure"] > 1.0


def test_summary() -> None:
    summary = pillar1042_summary()
    assert PILLAR_VALID is True
    assert summary["status"] == PILLAR_STATUS
