# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 535 — Full Architecture Closure Certificate v3."""

from __future__ import annotations
import pytest
from src.core.full_architecture_closure_v3 import (
    ARCHITECTURE_LIMITS, CERT_V3_SUMMARY, CLOSED_GAPS, PILLAR_NUMBER,
    PILLAR_STATUS, PILLAR_TITLE, TENSIONS_BELOW_THRESHOLD,
    architecture_closure_v3_report, pillar535_report,
)


class TestPillarMetadata:
    def test_pillar_number(self): assert PILLAR_NUMBER == 535
    def test_status(self): assert PILLAR_STATUS == "ARCHITECTURE_CLOSURE_CERT_V3"
    def test_title_mentions_v3(self): assert "v3" in PILLAR_TITLE or "V3" in PILLAR_TITLE


class TestArchitectureLimits:
    def test_two_limits(self): assert len(ARCHITECTURE_LIMITS) == 2
    def test_cmb_limit_present(self):
        names = [al["name"] for al in ARCHITECTURE_LIMITS]
        assert any("CMB" in n or "AMPLITUDE" in n for n in names)
    def test_tensor_limit_present(self):
        names = [al["name"] for al in ARCHITECTURE_LIMITS]
        assert any("TENSOR" in n or "ACT" in n for n in names)
    def test_all_have_status_irreducible(self):
        for al in ARCHITECTURE_LIMITS:
            assert "IRREDUCIBLE" in al["status"]


class TestClosedGaps:
    def test_at_least_5_closed(self): assert len(CLOSED_GAPS) >= 5
    def test_vol_cy3_closed(self):
        names = [g["name"] for g in CLOSED_GAPS]
        assert any("VOL" in n or "CY3" in n for n in names)
    def test_p_r_gap_closed(self):
        names = [g["name"] for g in CLOSED_GAPS]
        assert any("P_R" in n or "SEESAW" in n for n in names)
    def test_pillar_526_closes_vol(self):
        vol_gaps = [g for g in CLOSED_GAPS if "VOL" in g["name"] or "CY3" in g["name"]]
        assert any(g["pillar_closed"] == 526 for g in vol_gaps)
    def test_pillar_527_closes_pr(self):
        pr_gaps = [g for g in CLOSED_GAPS if "P_R" in g["name"] or "SEESAW" in g["name"]]
        assert any(g["pillar_closed"] == 527 for g in pr_gaps)


class TestTensionsBelowThreshold:
    def test_desi_tracked(self):
        names = [t["name"] for t in TENSIONS_BELOW_THRESHOLD]
        assert any("DESI" in n for n in names)
    def test_all_below_3sigma(self):
        for t in TENSIONS_BELOW_THRESHOLD:
            assert t["sigma"] < t["threshold"]


class TestCertV3Summary:
    def test_toe_score(self): assert CERT_V3_SUMMARY["toe_score"] == "28/28"
    def test_sprint_v18(self): assert "18" in CERT_V3_SUMMARY["sprint"]
    def test_hardgate_unchanged(self): assert CERT_V3_SUMMARY["hardgate_lanes"] == "UNCHANGED"
    def test_n_closed_gaps_positive(self): assert CERT_V3_SUMMARY["n_closed_gaps"] > 0


class TestPillar535Report:
    def setup_method(self): self.r = pillar535_report()
    def test_returns_dict(self): assert isinstance(self.r, dict)
    def test_pillar_number(self): assert self.r["pillar"] == 535
    def test_status(self): assert self.r["status"] == "ARCHITECTURE_CLOSURE_CERT_V3"
    def test_closed_gaps_present(self): assert "closed_gaps" in self.r
    def test_architecture_limits_present(self): assert "architecture_limits" in self.r
    def test_summary_present(self): assert "summary" in self.r
    def test_toe_score_in_summary(self): assert self.r["summary"]["toe_score"] == "28/28"
