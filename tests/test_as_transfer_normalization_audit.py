# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/as_transfer_normalization_audit.py."""
from __future__ import annotations

from src.core.as_transfer_normalization_audit import (
    ADJACENCY_TRACK_LABEL,
    M_KK_WARP_RELATIVE_UNCERTAINTY,
    SC2_PASS_THRESHOLD,
    SC2_TENSION_THRESHOLD,
    as_transfer_chain_audit,
    classify_sc2_step,
    sc2_chain_verdict,
)


def test_classify_sc2_step_pass():
    assert classify_sc2_step(0.05, 0.10, 0.20) == "PASS"


def test_classify_sc2_step_tension():
    assert classify_sc2_step(0.15, 0.10, 0.20) == "TENSION"


def test_classify_sc2_step_falsified():
    assert classify_sc2_step(0.30, 0.10, 0.20) == "FALSIFIED"


def test_constants_are_ordered():
    assert 0.0 < M_KK_WARP_RELATIVE_UNCERTAINTY < 1.0
    assert SC2_PASS_THRESHOLD < SC2_TENSION_THRESHOLD


def test_as_transfer_chain_audit_packet_shape():
    report = as_transfer_chain_audit()
    assert report["audit_id"] == "SC2_AS_TRANSFER_NORMALIZATION_AUDIT"
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert "step1_mkk_transfer_uncertainty" in report
    assert "step2_alpha_gw_bridge" in report
    assert "step3_as_consistency" in report


def test_sc2_chain_verdict_is_explicit_three_state():
    verdict = sc2_chain_verdict()
    assert verdict in {"PASS", "TENSION", "FALSIFIED"}


def test_sc2_chain_closed_on_pass():
    report = as_transfer_chain_audit()
    assert report["chain_is_closed"] == (report["chain_verdict"] == "PASS")
