# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/proof_closure_formal_cert.py."""
from __future__ import annotations

from src.core.proof_closure_formal_cert import (
    ADJACENCY_TRACK_LABEL,
    formal_proof_closure_certificate,
)


def test_formal_proof_closure_certificate_shape():
    cert = formal_proof_closure_certificate()
    assert cert["cert_id"] == "PROOF_CLOSURE_FORMAL_CERT"
    assert cert["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert "n_w_uniqueness" in cert
    assert "k_cs_algebra" in cert
    assert "metric_boundary_consistency" in cert


def test_formal_proof_closure_certificate_status():
    cert = formal_proof_closure_certificate()
    assert cert["status"] in {"PASS", "TENSION"}
    assert cert["overall_pass"] == (cert["status"] == "PASS")


def test_metric_assembly_agreement_does_not_establish_physical_closure():
    cert = formal_proof_closure_certificate()
    assert cert["metric_boundary_consistency"]["metric_passed"]
    assert cert["metric_boundary_consistency"]["metric_scope"] == "CONDITIONAL_KK_PARAMETERIZATION"
    assert cert["metric_boundary_consistency"]["physical_derivation_established"] is False
    assert cert["closure_earned"] is False
    assert cert["physical_derivation_established"] is False
