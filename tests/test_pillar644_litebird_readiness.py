# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 644 — LiteBIRD two-branch readiness hardening."""
from __future__ import annotations

import math

from src.core.pillar644_litebird_readiness_hardening import (
    BAYES_FACTOR_57_OVER_56,
    BETA_56,
    BETA_57,
    BETA_HINT,
    BETA_HINT_SIGMA,
    GAP_DEG,
    GAP_SIGMA,
    LITEBIRD_DATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SIGMA_LITEBIRD,
    VERSION,
    WINDOW_HIGH,
    WINDOW_LOW,
    bayes_factor,
    branch_identification_rules,
    early_cross_check,
    pillar_report,
    snr_metrics,
    verdict_table,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
BRANCHES = branch_identification_rules()
BF = bayes_factor()
SNR = snr_metrics()
EARLY = early_cross_check()
VERDICT = verdict_table()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 644

    def test_status(self):
        assert "READINESS_HARDENED" in PILLAR_STATUS

    def test_gap_deg(self):
        assert abs(GAP_DEG - (BETA_57 - BETA_56)) < 1e-12

    def test_gap_sigma(self):
        assert abs(GAP_SIGMA - GAP_DEG / SIGMA_LITEBIRD) < 1e-12

    def test_gap_discriminable(self):
        assert GAP_SIGMA > 2.5

    def test_beta_57_in_window(self):
        assert WINDOW_LOW < BETA_57 < WINDOW_HIGH

    def test_beta_56_in_window(self):
        assert WINDOW_LOW < BETA_56 < WINDOW_HIGH

    def test_bayes_factor_positive(self):
        assert BAYES_FACTOR_57_OVER_56 > 0.0


class TestBranchRules:
    def test_four_branches(self):
        assert len(BRANCHES) == 4

    def test_branch_labels(self):
        labels = [b["branch"] for b in BRANCHES]
        for expected in ["OM-A", "OM-B", "OM-C", "OM-D"]:
            assert expected in labels

    def test_om_c_falsification(self):
        om_c = next(b for b in BRANCHES if b["branch"] == "OM-C")
        assert "FALSIFIED" in om_c["verdict"]

    def test_om_d_falsification(self):
        om_d = next(b for b in BRANCHES if b["branch"] == "OM-D")
        assert "FALSIFIED" in om_d["verdict"]


class TestBayesFactor:
    def test_hint_sigma(self):
        assert abs(BF["hint_sigma"] - BETA_HINT_SIGMA) < 1e-12

    def test_favored_branch(self):
        assert "(5,7)" in BF["favored_branch"] or "(5,6)" in BF["favored_branch"]


class TestSNR:
    def test_snr_57_positive(self):
        assert SNR["snr_57"] > 0.0

    def test_gap_discriminable(self):
        assert SNR["gap_discriminable"] is True


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
