# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
test_hils_core.py — Tests for the consolidated hils_core module.
Theory: ThomasCory Walker-Pearson.  Code: GitHub Copilot (AI).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pytest
from hils_core import (
    HILS_CORE_VERSION,
    HIL_PHASE_SHIFT_THRESHOLD,
    SENTINEL_CAPACITY,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
    SUM_OF_SQUARES_RESONANCE,
    XI_C,
    HILOperator,
    HILSCertificationPipeline,
    HILSGateDecision,
    EpistemicClass,
    CANONICAL_PRIMARY_OPERATOR,
    build_certified_pipeline,
    CertificationStatus,
)


# ── Constants ────────────────────────────────────────────────────────────────

def test_threshold_is_15():
    assert HIL_PHASE_SHIFT_THRESHOLD == 15

def test_sentinel_capacity_equals_braided_sound_speed():
    assert SENTINEL_CAPACITY == BRAIDED_SOUND_SPEED

def test_braided_sound_speed_value():
    assert abs(BRAIDED_SOUND_SPEED - 12/37) < 1e-12

def test_trust_phi_min_positive():
    assert TRUST_PHI_MIN > 0

def test_sum_of_squares_resonance():
    assert SUM_OF_SQUARES_RESONANCE == 5**2 + 7**2

def test_xi_c_value():
    assert abs(XI_C - 35/74) < 1e-12

def test_version_string():
    parts = HILS_CORE_VERSION.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


# ── HILOperator ───────────────────────────────────────────────────────────────

def test_hil_operator_aligned_above_threshold():
    op = HILOperator("op1", "physics", 0.9)
    assert op.is_aligned()

def test_hil_operator_not_aligned_below_threshold():
    op = HILOperator("op2", "physics", 0.5)
    assert not op.is_aligned()

def test_hil_operator_frozen():
    op = HILOperator("op3", "physics", 1.0)
    with pytest.raises((AttributeError, TypeError)):
        op.alignment_score = 0.0  # type: ignore


# ── HILSCertificationPipeline ─────────────────────────────────────────────────

def test_empty_pipeline_insufficient():
    pipeline = HILSCertificationPipeline()
    assert pipeline.certify() == "INSUFFICIENT"

def test_pipeline_pending_with_8_operators():
    pipeline = HILSCertificationPipeline()
    for i in range(8):
        pipeline.submit_operator(HILOperator(f"op{i}", "domain", 1.0))
    assert pipeline.certify() == "PENDING"

def test_pipeline_certified_with_15_operators():
    pipeline = HILSCertificationPipeline()
    for i in range(15):
        pipeline.submit_operator(HILOperator(f"op{i}", "domain", 1.0))
    assert pipeline.certify() == "CERTIFIED"

def test_pipeline_low_score_operators_not_counted():
    pipeline = HILSCertificationPipeline()
    for i in range(15):
        pipeline.submit_operator(HILOperator(f"op{i}", "domain", 0.3))
    assert pipeline.certify() == "INSUFFICIENT"

def test_entropy_saturation_max_one():
    pipeline = HILSCertificationPipeline()
    for i in range(100):
        pipeline.submit_operator(HILOperator(f"op{i}", "domain", 1.0))
    assert pipeline.get_entropy_saturation() == 1.0

def test_entropy_saturation_below_threshold():
    pipeline = HILSCertificationPipeline()
    for i in range(5):
        pipeline.submit_operator(HILOperator(f"op{i}", "domain", 1.0))
    assert abs(pipeline.get_entropy_saturation() - 5/15) < 1e-9

def test_get_certificate_fields():
    pipeline = build_certified_pipeline()
    cert = pipeline.get_certificate()
    assert cert.threshold == HIL_PHASE_SHIFT_THRESHOLD
    assert cert.sentinel_capacity == SENTINEL_CAPACITY
    assert cert.version == HILS_CORE_VERSION

def test_remove_operator():
    pipeline = HILSCertificationPipeline()
    pipeline.submit_operator(HILOperator("op1", "domain", 1.0))
    assert pipeline.get_alignment_count() == 1
    pipeline.remove_operator("op1")
    assert pipeline.get_alignment_count() == 0


# ── Gate evaluation ───────────────────────────────────────────────────────────

def test_gate_unknown_operator_rejected():
    pipeline = HILSCertificationPipeline()
    result = pipeline.evaluate_gate("unknown")
    assert result.decision == HILSGateDecision.REJECTED

def test_gate_quorum_bypass():
    pipeline = build_certified_pipeline()
    result = pipeline.evaluate_gate("wuzbak")
    assert result.decision == HILSGateDecision.BYPASS_QUORUM
    assert result.quorum_satisfied

def test_gate_deferred_insufficient_quorum():
    pipeline = HILSCertificationPipeline()
    pipeline.submit_operator(HILOperator("op1", "domain", 1.0))
    result = pipeline.evaluate_gate("op1")
    assert result.decision == HILSGateDecision.DEFERRED

def test_gate_approved_with_full_quorum():
    pipeline = HILSCertificationPipeline()
    for i in range(HIL_PHASE_SHIFT_THRESHOLD):
        pipeline.submit_operator(HILOperator(f"op{i}", "domain", 1.0))
    result = pipeline.evaluate_gate("op0")
    assert result.decision == HILSGateDecision.APPROVED


# ── Canonical operator ────────────────────────────────────────────────────────

def test_canonical_operator_identity():
    assert CANONICAL_PRIMARY_OPERATOR.operator_id == "wuzbak"
    assert CANONICAL_PRIMARY_OPERATOR.quorum_bypass is True
    assert CANONICAL_PRIMARY_OPERATOR.revocable is False
    assert CANONICAL_PRIMARY_OPERATOR.alignment_score == 1.0

def test_build_certified_pipeline_pre_seeded():
    pipeline = build_certified_pipeline()
    assert "wuzbak" in [
        op for op in pipeline._operators
    ]


# ── Epistemic classes ─────────────────────────────────────────────────────────

def test_epistemic_class_values():
    assert EpistemicClass.HARDGATE == "HARDGATE"
    assert EpistemicClass.ADJACENT_TRACK == "ADJACENT-TRACK"
    assert EpistemicClass.GOVERNANCE == "GOVERNANCE"
    assert EpistemicClass.UNCLASSIFIED == "UNCLASSIFIED"
