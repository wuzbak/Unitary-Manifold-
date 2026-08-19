# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/public_trust_index.py — Phase 3: Public Trust Index"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.public_trust_index import PublicTrustIndexBuilder, PublicTrustReport
from EIGE.src.metric_closure import MetricClosure, ClosureStatus
from EIGE.src.constants import PHI_0, K_CS, PHI_TOLERANCE, PHI_DRIFT_WARNING


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def builder():
    return PublicTrustIndexBuilder(
        jurisdiction="Test County",
        county_count=10,
    )


@pytest.fixture
def state_builder():
    return PublicTrustIndexBuilder(
        jurisdiction="Washington State",
        county_count=39,
    )


@pytest.fixture
def stable_result():
    mc = MetricClosure()
    return mc.validate(PHI_0, K_CS)


@pytest.fixture
def drifted_result():
    mc = MetricClosure()
    return mc.validate(PHI_0 + PHI_TOLERANCE * 2, K_CS)


@pytest.fixture
def violated_result():
    mc = MetricClosure()
    return mc.validate(PHI_0 + PHI_DRIFT_WARNING * 2, K_CS)


# ---------------------------------------------------------------------------
# PublicTrustReport dataclass
# ---------------------------------------------------------------------------

class TestPublicTrustReport:
    def test_is_verified_true_for_verified_status(self):
        r = PublicTrustReport(
            status="VERIFIED",
            plain_english_summary="All good.",
            statistical_equivalent="99.7% CI",
            timestamp="2026-01-01T00:00:00+00:00",
            jurisdiction="Test",
            ballot_count=1000,
            county_count=5,
            counties_verified=5,
            counties_watch=0,
            counties_alert=0,
        )
        assert r.is_verified() is True

    def test_is_verified_false_for_watch_status(self):
        r = PublicTrustReport(
            status="WATCH",
            plain_english_summary="Minor variance.",
            statistical_equivalent="",
            timestamp="2026-01-01T00:00:00+00:00",
            jurisdiction="Test",
            ballot_count=1000,
            county_count=5,
            counties_verified=4,
            counties_watch=1,
            counties_alert=0,
        )
        assert r.is_verified() is False

    def test_is_verified_false_for_alert_status(self):
        r = PublicTrustReport(
            status="ALERT",
            plain_english_summary="Critical.",
            statistical_equivalent="",
            timestamp="2026-01-01T00:00:00+00:00",
            jurisdiction="Test",
            ballot_count=1000,
            county_count=5,
            counties_verified=3,
            counties_watch=1,
            counties_alert=1,
        )
        assert r.is_verified() is False

    def test_as_public_dict_excludes_detail(self):
        r = PublicTrustReport(
            status="VERIFIED",
            plain_english_summary="All good.",
            statistical_equivalent="",
            timestamp="2026-01-01T00:00:00+00:00",
            jurisdiction="Test",
            ballot_count=100,
            county_count=1,
            counties_verified=1,
            counties_watch=0,
            counties_alert=0,
            detail={"secret_internal": "value"},
        )
        public = r.as_public_dict()
        assert "detail" not in public
        assert "status" in public

    def test_as_dict_includes_detail(self):
        r = PublicTrustReport(
            status="VERIFIED",
            plain_english_summary="All good.",
            statistical_equivalent="",
            timestamp="2026-01-01T00:00:00+00:00",
            jurisdiction="Test",
            ballot_count=100,
            county_count=1,
            counties_verified=1,
            counties_watch=0,
            counties_alert=0,
            detail={"internal": "value"},
        )
        full = r.as_dict()
        assert "detail" in full

    def test_str_representation_contains_status(self):
        r = PublicTrustReport(
            status="VERIFIED",
            plain_english_summary="OK.",
            statistical_equivalent="99%",
            timestamp="2026-01-01T00:00:00+00:00",
            jurisdiction="Test",
            ballot_count=100,
            county_count=1,
            counties_verified=1,
            counties_watch=0,
            counties_alert=0,
        )
        s = str(r)
        assert "VERIFIED" in s
        assert "Test" in s


# ---------------------------------------------------------------------------
# from_closure_result
# ---------------------------------------------------------------------------

class TestFromClosureResult:
    def test_stable_result_gives_verified_status(self, builder, stable_result):
        report = builder.from_closure_result(stable_result, ballot_count=500)
        assert report.status == "VERIFIED"

    def test_drifted_result_gives_watch_status(self, builder, drifted_result):
        report = builder.from_closure_result(drifted_result, ballot_count=500)
        assert report.status == "WATCH"

    def test_violated_result_gives_alert_status(self, builder, violated_result):
        report = builder.from_closure_result(violated_result, ballot_count=500)
        assert report.status == "ALERT"

    def test_summary_contains_no_kk_vocabulary(self, builder, stable_result):
        report = builder.from_closure_result(stable_result, ballot_count=500)
        forbidden = ["φ", "Kaluza", "k_CS", "Chern", "radion", "braid"]
        for term in forbidden:
            assert term not in report.plain_english_summary, (
                f"Physics term {term!r} found in plain_english_summary"
            )

    def test_summary_contains_no_kk_vocabulary_in_stat_equiv(self, builder, stable_result):
        report = builder.from_closure_result(stable_result, ballot_count=500)
        forbidden = ["φ", "Kaluza", "k_CS", "Chern", "radion", "braid"]
        for term in forbidden:
            assert term not in report.statistical_equivalent, (
                f"Physics term {term!r} found in statistical_equivalent"
            )

    def test_ballot_count_set(self, builder, stable_result):
        report = builder.from_closure_result(stable_result, ballot_count=12345)
        assert report.ballot_count == 12345

    def test_county_count_is_one_for_single_county(self, builder, stable_result):
        report = builder.from_closure_result(stable_result)
        assert report.county_count == 1

    def test_counties_verified_1_for_stable(self, builder, stable_result):
        report = builder.from_closure_result(stable_result)
        assert report.counties_verified == 1

    def test_counties_alert_1_for_violated(self, builder, violated_result):
        report = builder.from_closure_result(violated_result)
        assert report.counties_alert == 1

    def test_timestamp_present(self, builder, stable_result):
        report = builder.from_closure_result(stable_result)
        assert report.timestamp

    def test_detail_contains_closure_data(self, builder, stable_result):
        report = builder.from_closure_result(stable_result)
        assert "status" in report.detail
        assert "phi_eff" in report.detail


# ---------------------------------------------------------------------------
# from_raw_metrics
# ---------------------------------------------------------------------------

class TestFromRawMetrics:
    def test_clean_metrics_verified(self, builder):
        report = builder.from_raw_metrics(
            phi_eff=PHI_0, k_cs=K_CS, ballot_count=1000
        )
        assert report.status == "VERIFIED"

    def test_k_cs_mismatch_alert(self, builder):
        report = builder.from_raw_metrics(
            phi_eff=PHI_0, k_cs=99, ballot_count=1000
        )
        assert report.status == "ALERT"

    def test_phi_drifted_watch(self, builder):
        report = builder.from_raw_metrics(
            phi_eff=PHI_0 + PHI_TOLERANCE * 5,
            k_cs=K_CS,
            ballot_count=1000,
        )
        assert report.status == "WATCH"

    def test_phi_violated_alert(self, builder):
        report = builder.from_raw_metrics(
            phi_eff=PHI_0 + PHI_DRIFT_WARNING * 5,
            k_cs=K_CS,
            ballot_count=1000,
        )
        assert report.status == "ALERT"

    def test_county_count_propagated(self, builder):
        report = builder.from_raw_metrics(
            phi_eff=PHI_0, k_cs=K_CS, ballot_count=1000,
            county_count=39,
        )
        assert report.county_count == 39

    def test_jurisdiction_override(self, builder):
        report = builder.from_raw_metrics(
            phi_eff=PHI_0, k_cs=K_CS, ballot_count=1000,
            jurisdiction="Pierce County",
        )
        assert report.jurisdiction == "Pierce County"


# ---------------------------------------------------------------------------
# from_state_ledger
# ---------------------------------------------------------------------------

class TestFromStateLedger:
    def _make_ledger_entry(
        self,
        counties_stable=5,
        counties_drifted=0,
        counties_violated=0,
        status="STABLE",
        ballot_count_per_county=100,
    ):
        """Build a minimal duck-typed StateLedgerEntry substitute."""
        class FakeLedger:
            def __init__(self):
                self.state_closure_status = status
                self.counties_stable = counties_stable
                self.counties_drifted = counties_drifted
                self.counties_violated = counties_violated
                self.county_count = counties_stable + counties_drifted + counties_violated
                self.timestamp = "2026-01-01T00:00:00+00:00"
                self.county_details = [
                    {"ballot_count": ballot_count_per_county}
                ] * self.county_count

            def as_dict(self):
                return {
                    "state_closure_status": self.state_closure_status,
                    "county_count": self.county_count,
                    "counties_stable": self.counties_stable,
                }

        return FakeLedger()

    def test_stable_ledger_gives_verified(self, state_builder):
        ledger = self._make_ledger_entry(5, 0, 0, "STABLE")
        report = state_builder.from_state_ledger(ledger)
        assert report.status == "VERIFIED"

    def test_drifted_ledger_gives_watch(self, state_builder):
        ledger = self._make_ledger_entry(4, 1, 0, "DRIFTED")
        report = state_builder.from_state_ledger(ledger)
        assert report.status == "WATCH"

    def test_violated_ledger_gives_alert(self, state_builder):
        ledger = self._make_ledger_entry(3, 0, 2, "VIOLATED")
        report = state_builder.from_state_ledger(ledger)
        assert report.status == "ALERT"

    def test_total_ballot_count_computed(self, state_builder):
        ledger = self._make_ledger_entry(3, 0, 0, "STABLE", ballot_count_per_county=200)
        report = state_builder.from_state_ledger(ledger)
        assert report.ballot_count == 600

    def test_summary_mentions_jurisdiction(self, state_builder):
        ledger = self._make_ledger_entry(5, 0, 0, "STABLE")
        report = state_builder.from_state_ledger(ledger)
        assert "Washington State" in report.plain_english_summary

    def test_summary_no_physics_vocabulary(self, state_builder):
        ledger = self._make_ledger_entry(5, 0, 0, "STABLE")
        report = state_builder.from_state_ledger(ledger)
        forbidden = ["φ", "Kaluza", "k_CS", "Chern", "radion", "braid"]
        for term in forbidden:
            assert term not in report.plain_english_summary
            assert term not in report.statistical_equivalent


# ---------------------------------------------------------------------------
# Statistical equivalent quality
# ---------------------------------------------------------------------------

class TestStatisticalEquivalent:
    def test_stable_stat_equiv_mentions_confidence(self, builder, stable_result):
        report = builder.from_closure_result(stable_result, ballot_count=10000)
        assert "confidence" in report.statistical_equivalent.lower() or \
               "margin" in report.statistical_equivalent.lower() or \
               "parts-per-billion" in report.statistical_equivalent.lower()

    def test_violated_stat_equiv_mentions_anomaly(self, builder, violated_result):
        report = builder.from_closure_result(violated_result, ballot_count=10000)
        assert (
            "statistically" in report.statistical_equivalent.lower()
            or "anomaly" in report.statistical_equivalent.lower()
            or "threshold" in report.statistical_equivalent.lower()
        )

    def test_stat_equiv_not_empty(self, builder, stable_result):
        report = builder.from_closure_result(stable_result)
        assert len(report.statistical_equivalent) > 20
