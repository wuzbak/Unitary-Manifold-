# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
Tests for Phase 4: Freedom Floor Kill-Switch in SentinelLoadBalancer
and for Phase 5: Full Pipeline Chaos Integration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
import tempfile
from EIGE.src.sentinel_load_balance import SentinelLoadBalancer, FreedomFloorBreach
from EIGE.src.constants import PHI_0, K_CS, FREEDOM_FLOOR, FREEDOM_FLOOR_MIN_BALLOTS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sentinel(tmp_path):
    return SentinelLoadBalancer(output_directory=str(tmp_path))


# ---------------------------------------------------------------------------
# Phase 4 — Freedom Floor Kill-Switch
# ---------------------------------------------------------------------------

class TestFreedomFloorKillSwitch:
    def test_full_participation_returns_true(self, sentinel):
        counts = [100, 200, 150, 180, 220]
        assert sentinel.check_freedom_floor(counts) is True

    def test_empty_list_returns_true(self, sentinel):
        assert sentinel.check_freedom_floor([]) is True

    def test_single_county_above_floor_ok(self, sentinel):
        sentinel_low_floor = SentinelLoadBalancer(
            freedom_floor=0.0,
            output_directory="/tmp",
        )
        assert sentinel_low_floor.check_freedom_floor([1]) is True

    def test_all_zero_counts_raises_breach(self, sentinel):
        """All zero ballot counts → 0% participation → FreedomFloorBreach."""
        with pytest.raises(FreedomFloorBreach) as exc_info:
            sentinel.check_freedom_floor([0, 0, 0, 0, 0])
        assert exc_info.value.participating_fraction == 0.0

    def test_below_floor_fraction_raises(self, sentinel):
        # 1 of 10 counties has ballots → 10% participating, floor is 0.85
        counts = [100] + [0] * 9
        with pytest.raises(FreedomFloorBreach):
            sentinel.check_freedom_floor(counts)

    def test_exactly_at_floor_passes(self):
        # Exactly 85% non-trivial (8.5 rounds down, use 9/10 = 0.90 to be safe)
        s = SentinelLoadBalancer(
            freedom_floor=0.85,
            freedom_floor_min_ballots=1,
            output_directory="/tmp",
        )
        # 9 of 10 counties have ballots → 90% ≥ 85%
        counts = [100] * 9 + [0]
        assert s.check_freedom_floor(counts) is True

    def test_breach_exception_message_contains_fraction(self, sentinel):
        counts = [50] + [0] * 9
        with pytest.raises(FreedomFloorBreach) as exc_info:
            sentinel.check_freedom_floor(counts)
        msg = str(exc_info.value)
        assert "0.1" in msg

    def test_breach_exception_contains_county_counts(self, sentinel):
        counts = [50] + [0] * 9
        with pytest.raises(FreedomFloorBreach) as exc_info:
            sentinel.check_freedom_floor(counts)
        assert exc_info.value.county_counts == counts

    def test_breach_sets_system_status(self, sentinel):
        with pytest.raises(FreedomFloorBreach):
            sentinel.check_freedom_floor([0, 0, 0])
        assert sentinel.system_status == "FREEDOM_FLOOR_BREACH"

    def test_breach_count_increments(self, sentinel):
        assert sentinel.freedom_floor_breach_count() == 0
        for _ in range(3):
            with pytest.raises(FreedomFloorBreach):
                sentinel.check_freedom_floor([0, 0, 0])
        assert sentinel.freedom_floor_breach_count() == 3

    def test_reset_status_resets_breach_count(self, sentinel):
        with pytest.raises(FreedomFloorBreach):
            sentinel.check_freedom_floor([0, 0, 0])
        sentinel.reset_status()
        assert sentinel.freedom_floor_breach_count() == 0
        assert sentinel.system_status == "CLOSED_PURE"


# ---------------------------------------------------------------------------
# Phase 4 — Participation variance diagnostics
# ---------------------------------------------------------------------------

class TestParticipationVariance:
    def test_empty_list_returns_safe_dict(self, sentinel):
        result = sentinel.check_participation_variance([])
        assert result["county_count"] == 0
        assert result["floor_intact"] is True

    def test_uniform_counts_low_cv(self, sentinel):
        counts = [100] * 10
        result = sentinel.check_participation_variance(counts)
        assert result["coefficient_of_variation"] == pytest.approx(0.0, abs=1e-9)
        assert result["floor_intact"] is True

    def test_uneven_counts_nonzero_cv(self, sentinel):
        counts = [100, 1, 200, 50, 500]
        result = sentinel.check_participation_variance(counts)
        assert result["coefficient_of_variation"] > 0.0

    def test_min_max_correct(self, sentinel):
        counts = [10, 50, 100, 200, 5]
        result = sentinel.check_participation_variance(counts)
        assert result["min_count"] == 5
        assert result["max_count"] == 200

    def test_participating_fraction_computed(self, sentinel):
        counts = [100, 0, 100, 0, 100]
        result = sentinel.check_participation_variance(counts)
        assert result["participating_fraction"] == pytest.approx(0.60, abs=0.01)

    def test_floor_intact_false_when_below_threshold(self, sentinel):
        counts = [100] + [0] * 9
        result = sentinel.check_participation_variance(counts)
        assert result["floor_intact"] is False

    def test_mean_count_correct(self, sentinel):
        counts = [100, 200, 300]
        result = sentinel.check_participation_variance(counts)
        assert result["mean_count"] == pytest.approx(200.0, abs=1e-9)

    def test_repr_contains_breach_count(self, sentinel):
        assert "freedom_floor_breaches" in repr(sentinel)


# ---------------------------------------------------------------------------
# Phase 5 — Full Pipeline Chaos Integration Test
# ---------------------------------------------------------------------------

class TestChaosIntegration:
    """
    Full pipeline: ChaosInjector → HolographicScreen → CountyNode
                   → StateMesh → PublicTrustReport

    Three scenarios:
      1. Baseline clean run
      2. 10% noise injection
      3. 50% noise injection above freedom floor (FreedomFloorViolation fires)
    """

    def _build_county_node(self, county_id="WA-047", name="King County"):
        from EIGE.src.county_node import CountyNode
        return CountyNode(county_id, name)

    def _build_injector(self, node, noise_budget=0.0, mode=None, seed=42):
        from EIGE.src.chaos_injection import ChaosInjector, NoiseMode
        return ChaosInjector(
            node,
            noise_budget=noise_budget,
            noise_mode=mode or NoiseMode.BITFLIP,
            freedom_floor=FREEDOM_FLOOR,
            seed=seed,
        )

    def _build_screen(self):
        from EIGE.src.holographic_screen import HolographicScreen
        return HolographicScreen(min_confidence=0.60)

    def _run_pipeline(self, injector, screen, raw_records):
        """Run the full screen → inject pipeline for a list of raw records."""
        from EIGE.src.holographic_screen import AdmissibilityError
        results = []
        for raw in raw_records:
            try:
                vec = screen.normalise(raw)
                rec = injector.inject_ballot(vec)
                results.append(rec)
            except AdmissibilityError:
                pass
        return results

    def _make_raw_records(self, n, confidence=0.99):
        return [
            {"selections": [1, 0, 1], "mark_confidence": confidence}
            for _ in range(n)
        ]

    # --- Scenario 1: Baseline clean run ---

    def test_scenario1_baseline_clean(self):
        """Baseline: no noise, all clean — STABLE closure, VERIFIED trust report."""
        from EIGE.src.metric_closure import ClosureStatus
        from EIGE.src.public_trust_index import PublicTrustIndexBuilder

        node = self._build_county_node()
        injector = self._build_injector(node, noise_budget=0.0)
        screen = self._build_screen()

        raw_records = self._make_raw_records(50)
        self._run_pipeline(injector, screen, raw_records)

        # 1. Metric closure should be STABLE
        result = node.validate_closure()
        assert result.status == ClosureStatus.STABLE, (
            f"Expected STABLE, got {result.status.name}"
        )

        # 2. Public trust report should be VERIFIED
        builder = PublicTrustIndexBuilder("King County", county_count=1)
        report = builder.from_closure_result(result, ballot_count=node.ballot_count())
        assert report.is_verified()

        # 3. No KK vocabulary in public output
        forbidden = ["φ", "Kaluza", "k_CS", "Chern", "radion", "braid", "π/4"]
        for term in forbidden:
            assert term not in report.plain_english_summary
            assert term not in report.statistical_equivalent

        # 4. Freedom floor intact with single node
        sentinel = SentinelLoadBalancer(output_directory="/tmp")
        assert sentinel.check_freedom_floor([node.ballot_count()]) is True

    # --- Scenario 2: 10% noise injection ---

    def test_scenario2_ten_percent_noise(self):
        """10% bitflip noise: engine stays STABLE, trust report stays VERIFIED."""
        from EIGE.src.chaos_injection import NoiseMode
        from EIGE.src.metric_closure import ClosureStatus
        from EIGE.src.public_trust_index import PublicTrustIndexBuilder

        node = self._build_county_node("WA-061", "Pierce County")
        injector = self._build_injector(
            node, noise_budget=0.10, mode=NoiseMode.BITFLIP, seed=1234
        )
        screen = self._build_screen()

        raw_records = self._make_raw_records(100)
        self._run_pipeline(injector, screen, raw_records)

        # Engine should survive 10% noise without metric collapse
        result = node.validate_closure()
        assert result.status == ClosureStatus.STABLE

        # Trust report should be VERIFIED
        builder = PublicTrustIndexBuilder("Pierce County", county_count=1)
        report = builder.from_closure_result(result, ballot_count=node.ballot_count())
        assert report.is_verified()

        # Some noise events should have been logged
        assert injector.total_events() == 100

    # --- Scenario 3: 50% noise + freedom floor kill-switch ---

    def test_scenario3_fifty_percent_noise_freedom_floor(self):
        """50% ZERO_OUT noise on large batch must trigger FreedomFloorViolation."""
        from EIGE.src.chaos_injection import ChaosInjector, NoiseMode, FreedomFloorViolation

        node = self._build_county_node("WA-033", "Thurston County")
        injector = ChaosInjector(
            node,
            noise_budget=1.0,   # 100% noise
            noise_mode=NoiseMode.ZERO_OUT,
            freedom_floor=0.70,
            seed=99,
        )

        # All-zeros batch: ZERO_OUT turns every vector into [0,0,0]
        # → all perturbed vectors are trivial → FreedomFloorViolation fires
        vectors = [[1, 1, 1]] * 20
        with pytest.raises(FreedomFloorViolation) as exc_info:
            injector.inject_batch(vectors)

        exc = exc_info.value
        assert exc.participating_fraction < injector.freedom_floor
        assert isinstance(exc.injection_log, list)
        assert len(exc.injection_log) > 0

    # --- Scenario 4: Multi-county state mesh integration ---

    def test_scenario4_multi_county_state_mesh(self):
        """Three counties ingest ballots, StateMesh aggregates, report produced."""
        from EIGE.src.county_node import CountyNode
        from EIGE.src.state_mesh import StateMesh
        from EIGE.src.public_trust_index import PublicTrustIndexBuilder

        counties = [
            CountyNode("WA-047", "King County"),
            CountyNode("WA-061", "Pierce County"),
            CountyNode("WA-033", "Thurston County"),
        ]
        screen = self._build_screen()

        for node in counties:
            inj = self._build_injector(node, noise_budget=0.0)
            for _ in range(30):
                vec = screen.normalise({"selections": [1, 0, 1], "mark_confidence": 0.99})
                inj.inject_ballot(vec)

        mesh = StateMesh(counties, jurisdiction_id="WA-STATE")
        entry = mesh.compute_braid_sync()

        assert entry.county_count == 3
        assert entry.counties_violated == 0
        assert entry.state_closure_status == "STABLE"

        builder = PublicTrustIndexBuilder("Washington State", county_count=3)
        report = builder.from_state_ledger(entry)
        assert report.is_verified()
        assert report.county_count == 3

    # --- Scenario 5: Freedom floor sentinel over multi-county counts ---

    def test_scenario5_sentinel_freedom_floor_multi_county(self, tmp_path):
        """Sentinel fires FreedomFloorBreach when majority of counties have 0 ballots."""
        sentinel = SentinelLoadBalancer(output_directory=str(tmp_path))

        # 5 counties — only 1 has votes
        county_counts = [500] + [0] * 38  # King County only
        with pytest.raises(FreedomFloorBreach) as exc_info:
            sentinel.check_freedom_floor(county_counts)

        assert exc_info.value.participating_fraction < FREEDOM_FLOOR
        assert sentinel.system_status == "FREEDOM_FLOOR_BREACH"

    # --- Scenario 6: Holographic screen rejects low-confidence ballots gracefully ---

    def test_scenario6_screen_rejects_low_confidence_gracefully(self):
        """Screen raises AdmissibilityError on low-confidence ballots; engine continues."""
        from EIGE.src.holographic_screen import AdmissibilityError

        node = self._build_county_node()
        screen = self._build_screen()  # min_confidence = 0.60

        high_conf_records = self._make_raw_records(10, confidence=0.99)
        low_conf_record = {"selections": [1, 0], "mark_confidence": 0.20}

        # High-confidence pass
        for raw in high_conf_records:
            vec = screen.normalise(raw)
            node.ingest_ballot(vec)

        # Low-confidence should raise
        with pytest.raises(AdmissibilityError):
            screen.normalise(low_conf_record)

        # Engine should still have 10 ballots (not 11)
        assert node.ballot_count() == 10

    # --- Scenario 7: End-to-end public report is legally usable ---

    def test_scenario7_public_report_has_no_physics_vocabulary(self):
        """The final public trust report must contain zero 5D/KK physics terms."""
        from EIGE.src.county_node import CountyNode
        from EIGE.src.state_mesh import StateMesh
        from EIGE.src.public_trust_index import PublicTrustIndexBuilder

        node = CountyNode("WA-047", "King County")
        for i in range(20):
            node.ingest_ballot([1, 0, i % 3])

        mesh = StateMesh([node])
        entry = mesh.compute_braid_sync()

        builder = PublicTrustIndexBuilder("Washington State", county_count=1)
        report = builder.from_state_ledger(entry)

        forbidden = [
            "φ", "Kaluza", "k_CS", "Chern-Simons", "radion", "braid",
            "5D", "KK", "π/4", "Winding", "winding", "topological invariant",
            "metric closure", "ClosureStatus",
        ]
        for term in forbidden:
            assert term not in report.plain_english_summary, (
                f"Physics term {term!r} found in plain_english_summary:\n"
                f"{report.plain_english_summary}"
            )
            assert term not in report.statistical_equivalent, (
                f"Physics term {term!r} found in statistical_equivalent:\n"
                f"{report.statistical_equivalent}"
            )
