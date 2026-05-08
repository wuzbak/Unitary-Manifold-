# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for WS-D++: src/core/alpha_s_direct_chain_reconciliation.py"""

from __future__ import annotations

import pytest

from src.core.alpha_s_direct_chain_reconciliation import (
    ALPHA_S_DIRECT_CHAIN,
    ALPHA_S_DIRECT_CHAIN_PCT_ERR,
    DIRECT_CHAIN_GAP_FACTOR,
    GATE_PASSED,
    P3_STATUS,
    canonical_forward_chain,
    hidden_anchor_guard,
    reconciliation_hard_gates,
    wsdpp_summary,
)


def test_hidden_anchor_guard_passes():
    g = hidden_anchor_guard()
    assert g["pass"] is True
    assert "empirical_fit_factor" in g["forbidden_inputs"]


def test_canonical_chain_payload():
    c = canonical_forward_chain()
    assert c["alpha_s_direct_chain"] > 0.0
    assert c["alpha_s_pdg_comparison"] > 0.0
    assert c["gap_factor"] > 1.0
    assert c["pct_err"] > 0.0


def test_constants_match_chain():
    c = canonical_forward_chain()
    assert ALPHA_S_DIRECT_CHAIN == pytest.approx(c["alpha_s_direct_chain"])
    assert ALPHA_S_DIRECT_CHAIN_PCT_ERR == pytest.approx(c["pct_err"])
    assert DIRECT_CHAIN_GAP_FACTOR == pytest.approx(c["gap_factor"])


def test_hard_gates_shape():
    g = reconciliation_hard_gates()
    assert {"direct_chain_closure_gate", "threshold_consistency_gate", "hidden_anchor_guard_gate"} <= set(g["gates"])
    assert isinstance(g["hard_gate_pass"], bool)


def test_status_is_consistency_check():
    assert P3_STATUS == "CONSISTENCY CHECK"
    assert GATE_PASSED is False


def test_summary_shape():
    s = wsdpp_summary()
    assert s["workstream"] == "WS-D++"
    assert s["parameter"].startswith("P3")
    assert "chain" in s
    assert "hard_gates" in s
    assert "verdict" in s
