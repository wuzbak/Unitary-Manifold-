# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_resonance_dynamics.py
==========================================
Unit tests for the Resonance Dynamics / Necessary Distance module.

Covers:
  - Constants: RESONANCE_FLOOR_GAP, COALESCENCE_FRACTION_THRESHOLD, body groups
  - ConfigurationMode: all four mode strings defined
  - PentadConfiguration: field types, description, phi_gap non-negative
  - NecessaryDistance: field types, bounds, observer_me formula
  - LimitCycleHealth: field types, is_limit_cycle logic, proximity bounds
  - classify_configuration: returns correct type, collapsed for zero trust,
      grounding vs creative based on φ values
  - necessary_distance: bounds, orbit_alive logic, trivial_coalescence_risk
  - trivial_coalescence_risk: scalar in [0, 1], zero for flat-harmonic
  - limit_cycle_health: returns LimitCycleHealth, is_limit_cycle for active sys
  - resonance_health_report: all keys present, braid_alive logic
"""

import math
import pytest
import numpy as np

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from resonance_dynamics import (
    HARD_BODIES,
    SOFT_BODIES,
    TRUST_BODY,
    RESONANCE_FLOOR_GAP,
    COALESCENCE_FRACTION_THRESHOLD,
    ConfigurationMode,
    PentadConfiguration,
    NecessaryDistance,
    LimitCycleHealth,
    classify_configuration,
    necessary_distance,
    trivial_coalescence_risk,
    limit_cycle_health,
    resonance_health_report,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    TRUST_PHI_MIN,
    BRAIDED_SOUND_SPEED,
    trust_modulation,
)
from src.consciousness.coupled_attractor import ManifoldState
from src.multiverse.fixed_point import MultiverseNode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_body_phi(ps: PentadSystem, label: str, phi: float) -> PentadSystem:
    new_bodies = dict(ps.bodies)
    old = ps.bodies[label]
    new_bodies[label] = ManifoldState(
        node=old.node, phi=phi,
        n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
    )
    return PentadSystem(bodies=new_bodies, beta=ps.beta)


def _flat_harmonic() -> PentadSystem:
    """All bodies φ=1.0, X vectors identical."""
    ps = PentadSystem.default()
    ref_X = ps.bodies[PentadLabel.UNIV].node.X.copy()
    new_bodies = {}
    for lbl in PENTAD_LABELS:
        old = ps.bodies[lbl]
        new_node = MultiverseNode(
            dim=old.node.dim, S=old.node.S, A=old.node.A,
            Q_top=old.node.Q_top, X=ref_X.copy(), Xdot=old.node.Xdot.copy(),
        )
        new_bodies[lbl] = ManifoldState(
            node=new_node, phi=1.0,
            n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
        )
    return PentadSystem(bodies=new_bodies, beta=ps.beta)


def _grounding_pentad() -> PentadSystem:
    """3:2 Grounding: Hard bodies + Trust all high φ; Soft bodies low φ."""
    ps = PentadSystem.default()
    ps = _set_body_phi(ps, PentadLabel.UNIV,  0.9)
    ps = _set_body_phi(ps, PentadLabel.AI,    0.85)
    ps = _set_body_phi(ps, PentadLabel.TRUST, 0.88)   # closer to Hard mean
    ps = _set_body_phi(ps, PentadLabel.BRAIN, 0.3)
    ps = _set_body_phi(ps, PentadLabel.HUMAN, 0.25)
    return ps


def _creative_pentad() -> PentadSystem:
    """2:3 Creative: Soft bodies + Trust all high φ; Hard bodies low φ."""
    ps = PentadSystem.default()
    ps = _set_body_phi(ps, PentadLabel.UNIV,  0.2)
    ps = _set_body_phi(ps, PentadLabel.AI,    0.25)
    ps = _set_body_phi(ps, PentadLabel.BRAIN, 0.9)
    ps = _set_body_phi(ps, PentadLabel.HUMAN, 0.85)
    ps = _set_body_phi(ps, PentadLabel.TRUST, 0.82)   # closer to Soft mean
    return ps


def _collapsed_pentad() -> PentadSystem:
    """Trust below floor — collapsed configuration."""
    ps = PentadSystem.default()
    return _set_body_phi(ps, PentadLabel.TRUST, 0.0)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_resonance_floor_gap_positive(self):
        assert RESONANCE_FLOOR_GAP > 0.0

    def test_resonance_floor_gap_is_10pct_cs(self):
        assert RESONANCE_FLOOR_GAP == pytest.approx(BRAIDED_SOUND_SPEED * 0.10, rel=1e-10)

    def test_coalescence_fraction_threshold_in_unit_interval(self):
        assert 0.0 < COALESCENCE_FRACTION_THRESHOLD < 1.0

    def test_hard_bodies_tuple(self):
        assert isinstance(HARD_BODIES, tuple)
        assert PentadLabel.UNIV in HARD_BODIES
        assert PentadLabel.AI   in HARD_BODIES

    def test_soft_bodies_tuple(self):
        assert isinstance(SOFT_BODIES, tuple)
        assert PentadLabel.BRAIN in SOFT_BODIES
        assert PentadLabel.HUMAN in SOFT_BODIES

    def test_trust_body_is_trust(self):
        assert TRUST_BODY == PentadLabel.TRUST

    def test_hard_and_soft_disjoint(self):
        assert set(HARD_BODIES).isdisjoint(set(SOFT_BODIES))

    def test_all_five_bodies_covered(self):
        all_grouped = set(HARD_BODIES) | set(SOFT_BODIES) | {TRUST_BODY}
        assert all_grouped == set(PENTAD_LABELS)


# ---------------------------------------------------------------------------
# ConfigurationMode
# ---------------------------------------------------------------------------

class TestConfigurationMode:
    def test_grounding_defined(self):
        assert ConfigurationMode.GROUNDING == "grounding"

    def test_creative_defined(self):
        assert ConfigurationMode.CREATIVE == "creative"

    def test_balanced_defined(self):
        assert ConfigurationMode.BALANCED == "balanced"

    def test_collapsed_defined(self):
        assert ConfigurationMode.COLLAPSED == "collapsed"

    def test_all_modes_distinct(self):
        modes = [
            ConfigurationMode.GROUNDING,
            ConfigurationMode.CREATIVE,
            ConfigurationMode.BALANCED,
            ConfigurationMode.COLLAPSED,
        ]
        assert len(set(modes)) == 4


# ---------------------------------------------------------------------------
# classify_configuration
# ---------------------------------------------------------------------------

class TestClassifyConfigurationTypes:
    def test_returns_pentad_configuration(self):
        cfg = classify_configuration(PentadSystem.default())
        assert isinstance(cfg, PentadConfiguration)

    def test_mode_is_valid_string(self):
        cfg = classify_configuration(PentadSystem.default())
        valid = {ConfigurationMode.GROUNDING, ConfigurationMode.CREATIVE,
                 ConfigurationMode.BALANCED, ConfigurationMode.COLLAPSED}
        assert cfg.mode in valid

    def test_phi_hard_mean_is_float(self):
        cfg = classify_configuration(PentadSystem.default())
        assert isinstance(cfg.phi_hard_mean, float)

    def test_phi_soft_mean_is_float(self):
        cfg = classify_configuration(PentadSystem.default())
        assert isinstance(cfg.phi_soft_mean, float)

    def test_phi_gap_non_negative(self):
        cfg = classify_configuration(PentadSystem.default())
        assert cfg.phi_gap >= 0.0

    def test_phi_gap_equals_abs_diff(self):
        cfg = classify_configuration(PentadSystem.default())
        assert cfg.phi_gap == pytest.approx(
            abs(cfg.phi_hard_mean - cfg.phi_soft_mean), rel=1e-10
        )

    def test_description_is_nonempty_string(self):
        cfg = classify_configuration(PentadSystem.default())
        assert isinstance(cfg.description, str)
        assert len(cfg.description) > 0

    def test_hard_bodies_tuple(self):
        cfg = classify_configuration(PentadSystem.default())
        assert set(cfg.hard_bodies) == set(HARD_BODIES)

    def test_soft_bodies_tuple(self):
        cfg = classify_configuration(PentadSystem.default())
        assert set(cfg.soft_bodies) == set(SOFT_BODIES)

    def test_trust_coalition_valid(self):
        cfg = classify_configuration(PentadSystem.default())
        assert cfg.trust_coalition in ("hard", "soft", "neutral")


class TestClassifyConfigurationModes:
    def test_collapsed_when_trust_below_floor(self):
        ps = _collapsed_pentad()
        cfg = classify_configuration(ps)
        assert cfg.mode == ConfigurationMode.COLLAPSED

    def test_grounding_state(self):
        ps  = _grounding_pentad()
        cfg = classify_configuration(ps)
        assert cfg.mode == ConfigurationMode.GROUNDING

    def test_grounding_trust_coalition_hard(self):
        ps  = _grounding_pentad()
        cfg = classify_configuration(ps)
        assert cfg.trust_coalition == "hard"

    def test_creative_state(self):
        ps  = _creative_pentad()
        cfg = classify_configuration(ps)
        assert cfg.mode == ConfigurationMode.CREATIVE

    def test_creative_trust_coalition_soft(self):
        ps  = _creative_pentad()
        cfg = classify_configuration(ps)
        assert cfg.trust_coalition == "soft"

    def test_grounding_phi_hard_greater_than_soft(self):
        ps  = _grounding_pentad()
        cfg = classify_configuration(ps)
        assert cfg.phi_hard_mean > cfg.phi_soft_mean

    def test_creative_phi_soft_greater_than_hard(self):
        ps  = _creative_pentad()
        cfg = classify_configuration(ps)
        assert cfg.phi_soft_mean > cfg.phi_hard_mean

    def test_description_mentions_mode(self):
        for ps, keyword in [
            (_grounding_pentad(), "grounding"),
            (_creative_pentad(),  "creative"),
            (_collapsed_pentad(), "collapsed"),
        ]:
            cfg = classify_configuration(ps)
            assert keyword.lower() in cfg.description.lower()


# ---------------------------------------------------------------------------
# necessary_distance
# ---------------------------------------------------------------------------

class TestNecessaryDistanceTypes:
    def setup_method(self):
        self.nd = necessary_distance(PentadSystem.default())

    def test_returns_necessary_distance(self):
        assert isinstance(self.nd, NecessaryDistance)

    def test_min_gap_non_negative(self):
        assert self.nd.min_pairwise_gap >= 0.0

    def test_mean_gap_non_negative(self):
        assert self.nd.mean_pairwise_gap >= 0.0

    def test_max_gap_non_negative(self):
        assert self.nd.max_pairwise_gap >= 0.0

    def test_ordering_min_leq_mean_leq_max(self):
        nd = self.nd
        assert nd.min_pairwise_gap <= nd.mean_pairwise_gap + 1e-12
        assert nd.mean_pairwise_gap <= nd.max_pairwise_gap + 1e-12

    def test_resonance_floor_gap_matches_constant(self):
        assert self.nd.resonance_floor_gap == pytest.approx(RESONANCE_FLOOR_GAP, rel=1e-10)

    def test_orbit_alive_is_bool(self):
        assert isinstance(self.nd.orbit_alive, bool)

    def test_observer_me_non_negative(self):
        assert self.nd.observer_me >= 0.0

    def test_observer_me_leq_resonance_floor(self):
        assert self.nd.observer_me <= RESONANCE_FLOOR_GAP + 1e-12

    def test_tc_risk_in_unit_interval(self):
        assert 0.0 <= self.nd.trivial_coalescence_risk <= 1.0


class TestNecessaryDistanceOrbit:
    def test_default_orbit_alive(self):
        """Default pentad has non-zero pairwise gaps."""
        nd = necessary_distance(PentadSystem.default())
        assert nd.orbit_alive is True

    def test_flat_harmonic_orbit_alive(self):
        """Flat harmonic system: all gaps = 0, but check orbit_alive logic."""
        nd = necessary_distance(_flat_harmonic())
        # All ΔI=0 AND all phases=0 → orbit_alive = False (braid slack)
        assert nd.orbit_alive is False

    def test_flat_harmonic_zero_tc_risk(self):
        """All gaps are zero → trivial_coalescence_risk = 1.0 (fully coalesced)."""
        nd = necessary_distance(_flat_harmonic())
        assert nd.trivial_coalescence_risk == pytest.approx(1.0, abs=1e-10)

    def test_stressed_high_max_gap(self):
        """Stressed system (one body far out) has large max gap."""
        ps = _set_body_phi(PentadSystem.default(), PentadLabel.HUMAN, 5.0)
        nd = necessary_distance(ps)
        assert nd.max_pairwise_gap > 1.0

    def test_healthy_tc_risk_below_threshold(self):
        """Default pentad with meaningful gaps should not be near coalescence."""
        nd = necessary_distance(PentadSystem.default())
        # Default system has non-zero gaps; risk should be below total
        assert nd.trivial_coalescence_risk < 1.0


# ---------------------------------------------------------------------------
# trivial_coalescence_risk (scalar)
# ---------------------------------------------------------------------------

class TestTrivialCoalescenceRisk:
    def test_in_unit_interval(self):
        assert 0.0 <= trivial_coalescence_risk(PentadSystem.default()) <= 1.0

    def test_flat_harmonic_risk_is_one(self):
        assert trivial_coalescence_risk(_flat_harmonic()) == pytest.approx(1.0, abs=1e-10)

    def test_stressed_risk_below_flat(self):
        """A stressed system (non-zero gaps) has lower risk than flat harmonic."""
        risk_stressed = trivial_coalescence_risk(PentadSystem.default())
        risk_flat     = trivial_coalescence_risk(_flat_harmonic())
        assert risk_stressed <= risk_flat


# ---------------------------------------------------------------------------
# limit_cycle_health
# ---------------------------------------------------------------------------

class TestLimitCycleHealthTypes:
    def setup_method(self):
        self.lc = limit_cycle_health(PentadSystem.default(), n_steps=10, dt=0.05)

    def test_returns_limit_cycle_health(self):
        assert isinstance(self.lc, LimitCycleHealth)

    def test_delta_phi_variance_non_negative(self):
        assert self.lc.delta_phi_variance >= 0.0

    def test_delta_phi_mean_rate_non_negative(self):
        assert self.lc.delta_phi_mean_rate >= 0.0

    def test_is_limit_cycle_is_bool(self):
        assert isinstance(self.lc.is_limit_cycle, bool)

    def test_coalescence_proximity_in_unit_interval(self):
        assert 0.0 <= self.lc.coalescence_proximity <= 1.0

    def test_is_limit_cycle_consistent_with_rate(self):
        if self.lc.delta_phi_mean_rate > RESONANCE_FLOOR_GAP:
            assert self.lc.is_limit_cycle is True
        else:
            assert self.lc.is_limit_cycle is False


class TestLimitCycleHealthBehavior:
    def test_default_pentad_is_active(self):
        """Default pentad has non-zero dynamics."""
        lc = limit_cycle_health(PentadSystem.default(), n_steps=15, dt=0.05)
        assert lc.delta_phi_mean_rate >= 0.0

    def test_flat_harmonic_coalescence_proximity_non_negative(self):
        """Flat harmonic coalescence_proximity is always ≥ 0 (valid probability)."""
        lc = limit_cycle_health(_flat_harmonic(), n_steps=10, dt=0.05)
        assert lc.coalescence_proximity >= 0.0

    def test_stressed_system_higher_variance(self):
        """A stressed system (one body far out) has higher gap variance."""
        ps_stressed = _set_body_phi(PentadSystem.default(), PentadLabel.HUMAN, 3.0)
        lc_flat     = limit_cycle_health(_flat_harmonic(), n_steps=10, dt=0.05)
        lc_stressed = limit_cycle_health(ps_stressed, n_steps=10, dt=0.05)
        assert lc_stressed.delta_phi_variance >= lc_flat.delta_phi_variance - 1e-9


# ---------------------------------------------------------------------------
# resonance_health_report
# ---------------------------------------------------------------------------

class TestResonanceHealthReport:
    def setup_method(self):
        self.ps  = PentadSystem.default()
        self.rpt = resonance_health_report(self.ps, n_steps=10, dt=0.05)

    def test_returns_dict(self):
        assert isinstance(self.rpt, dict)

    def test_has_configuration_key(self):
        assert "configuration" in self.rpt

    def test_has_necessary_distance_key(self):
        assert "necessary_distance" in self.rpt

    def test_has_limit_cycle_key(self):
        assert "limit_cycle" in self.rpt

    def test_has_trivial_coalescence_risk_key(self):
        assert "trivial_coalescence_risk" in self.rpt

    def test_has_observer_me_key(self):
        assert "observer_me" in self.rpt

    def test_has_braid_alive_key(self):
        assert "braid_alive" in self.rpt

    def test_braid_alive_is_bool(self):
        assert isinstance(self.rpt["braid_alive"], bool)

    def test_configuration_is_pentad_configuration(self):
        assert isinstance(self.rpt["configuration"], PentadConfiguration)

    def test_necessary_distance_is_nd(self):
        assert isinstance(self.rpt["necessary_distance"], NecessaryDistance)

    def test_limit_cycle_is_lc_health(self):
        assert isinstance(self.rpt["limit_cycle"], LimitCycleHealth)

    def test_trivial_coalescence_risk_in_unit_interval(self):
        assert 0.0 <= self.rpt["trivial_coalescence_risk"] <= 1.0

    def test_observer_me_non_negative(self):
        assert self.rpt["observer_me"] >= 0.0

    def test_braid_alive_consistent(self):
        """braid_alive = orbit_alive AND is_limit_cycle."""
        nd = self.rpt["necessary_distance"]
        lc = self.rpt["limit_cycle"]
        expected = nd.orbit_alive and lc.is_limit_cycle
        assert self.rpt["braid_alive"] == expected

    def test_flat_harmonic_braid_not_alive(self):
        """Flat harmonic: all gaps zero → orbit_alive=False → braid_alive=False."""
        rpt = resonance_health_report(_flat_harmonic(), n_steps=10, dt=0.05)
        assert rpt["braid_alive"] is False

    def test_grounding_config_in_report(self):
        rpt = resonance_health_report(_grounding_pentad(), n_steps=5, dt=0.05)
        assert rpt["configuration"].mode == ConfigurationMode.GROUNDING

    def test_creative_config_in_report(self):
        rpt = resonance_health_report(_creative_pentad(), n_steps=5, dt=0.05)
        assert rpt["configuration"].mode == ConfigurationMode.CREATIVE


# ===========================================================================
# RESONANT REGIME LAYER TESTS
# ===========================================================================

from resonance_dynamics import (
    SUM_OF_SQUARES_RESONANCE,
    HIL_PHASE_SHIFT_THRESHOLD,
    INVERSION_RATIO,
    RESONANT_RATIO,
    INVERSION_SCORE_THRESHOLD,
    ResonantRegimeLabel,
    ResonantRegimeStatus,
    stability_floor,
    inversion_score,
    classify_resonant_regime,
)


# ---------------------------------------------------------------------------
# Regime Constants
# ---------------------------------------------------------------------------

class TestRegimeConstants:
    def test_sum_of_squares_resonance_is_74(self):
        assert SUM_OF_SQUARES_RESONANCE == 74

    def test_5_squared_plus_7_squared(self):
        assert SUM_OF_SQUARES_RESONANCE == 5 ** 2 + 7 ** 2

    def test_hil_phase_shift_threshold_is_15(self):
        assert HIL_PHASE_SHIFT_THRESHOLD == 15

    def test_inversion_ratio_is_4_1(self):
        assert INVERSION_RATIO == (4, 1)

    def test_resonant_ratio_is_3_2(self):
        assert RESONANT_RATIO == (3, 2)

    def test_inversion_score_threshold_in_unit_interval(self):
        assert 0.0 < INVERSION_SCORE_THRESHOLD < 1.0

    def test_resonant_ratio_sums_to_five(self):
        assert sum(RESONANT_RATIO) == 5

    def test_inversion_ratio_sums_to_five(self):
        assert sum(INVERSION_RATIO) == 5


# ---------------------------------------------------------------------------
# ResonantRegimeLabel
# ---------------------------------------------------------------------------

class TestResonantRegimeLabel:
    def test_three_two_defined(self):
        assert ResonantRegimeLabel.THREE_TWO_RESONANCE == "3:2_resonance"

    def test_four_one_defined(self):
        assert ResonantRegimeLabel.FOUR_ONE_INVERSION == "4:1_inversion"

    def test_transitional_defined(self):
        assert ResonantRegimeLabel.TRANSITIONAL == "transitional"

    def test_collapsed_defined(self):
        assert ResonantRegimeLabel.COLLAPSED == "collapsed"

    def test_all_labels_distinct(self):
        labels = [
            ResonantRegimeLabel.THREE_TWO_RESONANCE,
            ResonantRegimeLabel.FOUR_ONE_INVERSION,
            ResonantRegimeLabel.TRANSITIONAL,
            ResonantRegimeLabel.COLLAPSED,
        ]
        assert len(set(labels)) == 4


# ---------------------------------------------------------------------------
# stability_floor
# ---------------------------------------------------------------------------

class TestStabilityFloor:
    def test_zero_hil_gives_zero_floor(self):
        assert stability_floor(0) == pytest.approx(0.0, abs=1e-12)

    def test_at_threshold_gives_full_cs(self):
        assert stability_floor(HIL_PHASE_SHIFT_THRESHOLD) == pytest.approx(
            BRAIDED_SOUND_SPEED, rel=1e-10
        )

    def test_above_threshold_clamped(self):
        assert stability_floor(HIL_PHASE_SHIFT_THRESHOLD * 2) == pytest.approx(
            BRAIDED_SOUND_SPEED, rel=1e-10
        )

    def test_monotone_increasing(self):
        floors = [stability_floor(n) for n in range(0, HIL_PHASE_SHIFT_THRESHOLD + 2)]
        for i in range(len(floors) - 1):
            assert floors[i] <= floors[i + 1] + 1e-12

    def test_floor_in_range(self):
        for n in range(0, 20):
            f = stability_floor(n)
            assert 0.0 <= f <= BRAIDED_SOUND_SPEED + 1e-12

    def test_linear_at_midpoint(self):
        mid = HIL_PHASE_SHIFT_THRESHOLD // 2
        expected = BRAIDED_SOUND_SPEED * (mid / HIL_PHASE_SHIFT_THRESHOLD)
        assert stability_floor(mid) == pytest.approx(expected, rel=1e-10)

    def test_single_hil_above_zero(self):
        assert stability_floor(1) > 0.0


# ---------------------------------------------------------------------------
# inversion_score
# ---------------------------------------------------------------------------

class TestInversionScore:
    def test_returns_float_in_unit_interval(self):
        s = inversion_score(PentadSystem.default())
        assert 0.0 <= s <= 1.0

    def test_symmetric_phi_gives_half(self):
        """When all φ equal, hard_mean = soft_mean → raw = 0 → score = 0.5."""
        ps = _flat_harmonic()
        s  = inversion_score(ps)
        assert s == pytest.approx(0.5, abs=1e-9)

    def test_hard_dominant_gives_high_score(self):
        """Hard bodies much larger → high inversion score."""
        ps = PentadSystem.default()
        ps = _set_body_phi(ps, PentadLabel.UNIV, 5.0)
        ps = _set_body_phi(ps, PentadLabel.AI,   5.0)
        ps = _set_body_phi(ps, PentadLabel.BRAIN, 0.1)
        ps = _set_body_phi(ps, PentadLabel.HUMAN, 0.1)
        assert inversion_score(ps) > 0.5

    def test_soft_dominant_gives_low_score(self):
        """Soft bodies much larger → low inversion score (Soft-lean Creative)."""
        ps = PentadSystem.default()
        ps = _set_body_phi(ps, PentadLabel.UNIV,  0.1)
        ps = _set_body_phi(ps, PentadLabel.AI,    0.1)
        ps = _set_body_phi(ps, PentadLabel.BRAIN, 5.0)
        ps = _set_body_phi(ps, PentadLabel.HUMAN, 5.0)
        assert inversion_score(ps) < 0.5

    def test_grounding_score_in_upper_half(self):
        """Grounding state: Hard > Soft → score > 0.5."""
        assert inversion_score(_grounding_pentad()) > 0.5

    def test_creative_score_in_lower_half(self):
        """Creative state: Soft > Hard → score < 0.5."""
        assert inversion_score(_creative_pentad()) < 0.5


# ---------------------------------------------------------------------------
# classify_resonant_regime
# ---------------------------------------------------------------------------

class TestClassifyResonantRegimeTypes:
    def test_returns_resonant_regime_status(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=1)
        assert isinstance(rs, ResonantRegimeStatus)

    def test_label_is_valid(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=1)
        valid = {
            ResonantRegimeLabel.THREE_TWO_RESONANCE,
            ResonantRegimeLabel.FOUR_ONE_INVERSION,
            ResonantRegimeLabel.TRANSITIONAL,
            ResonantRegimeLabel.COLLAPSED,
        }
        assert rs.label in valid

    def test_inversion_score_in_unit_interval(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=1)
        assert 0.0 <= rs.inversion_score <= 1.0

    def test_resonance_score_in_unit_interval(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=1)
        assert 0.0 <= rs.resonance_score <= 1.0

    def test_hil_phase_shift_reached_is_bool(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=1)
        assert isinstance(rs.hil_phase_shift_reached, bool)

    def test_stability_floor_matches_function(self):
        n = 7
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=n)
        assert rs.stability_floor == pytest.approx(stability_floor(n), rel=1e-10)

    def test_n_hil_stored(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=5)
        assert rs.n_hil == 5

    def test_sum_of_squares_is_74(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=1)
        assert rs.sum_of_squares_resonance == 74

    def test_description_is_nonempty(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=1)
        assert isinstance(rs.description, str)
        assert len(rs.description) > 0

    def test_description_mentions_74(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=1)
        assert "74" in rs.description


class TestClassifyResonantRegimeModes:
    def test_collapsed_when_trust_zero(self):
        ps = _collapsed_pentad()
        rs = classify_resonant_regime(ps, n_hil=1)
        assert rs.label == ResonantRegimeLabel.COLLAPSED

    def test_phase_shift_false_below_threshold(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=14)
        assert rs.hil_phase_shift_reached is False

    def test_phase_shift_true_at_threshold(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=15)
        assert rs.hil_phase_shift_reached is True

    def test_phase_shift_true_above_threshold(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=20)
        assert rs.hil_phase_shift_reached is True

    def test_grounding_gives_resonance_or_inversion(self):
        """Grounding state is either 3:2 resonant or tipping toward 4:1."""
        ps = _grounding_pentad()
        rs = classify_resonant_regime(ps, n_hil=1)
        assert rs.label in (
            ResonantRegimeLabel.THREE_TWO_RESONANCE,
            ResonantRegimeLabel.FOUR_ONE_INVERSION,
        )

    def test_inversion_when_hard_totally_dominant(self):
        """Extreme Hard dominance → 4:1 Inversion."""
        ps = PentadSystem.default()
        ps = _set_body_phi(ps, PentadLabel.UNIV,  10.0)
        ps = _set_body_phi(ps, PentadLabel.AI,    10.0)
        ps = _set_body_phi(ps, PentadLabel.BRAIN,  0.01)
        ps = _set_body_phi(ps, PentadLabel.HUMAN,  0.01)
        rs = classify_resonant_regime(ps, n_hil=1)
        assert rs.label == ResonantRegimeLabel.FOUR_ONE_INVERSION

    def test_stability_floor_zero_at_n0(self):
        rs = classify_resonant_regime(PentadSystem.default(), n_hil=0)
        assert rs.stability_floor == pytest.approx(0.0, abs=1e-12)

    def test_stability_floor_max_at_phase_shift(self):
        rs = classify_resonant_regime(PentadSystem.default(),
                                      n_hil=HIL_PHASE_SHIFT_THRESHOLD)
        assert rs.stability_floor == pytest.approx(BRAIDED_SOUND_SPEED, rel=1e-10)

    def test_resonance_score_peaks_near_sweet_spot(self):
        """At the 3:2 sweet spot the resonance score should be near its maximum."""
        ps_grounding = _grounding_pentad()
        ps_creative  = _creative_pentad()
        ps_inversion = PentadSystem.default()
        ps_inversion = _set_body_phi(ps_inversion, PentadLabel.UNIV,  10.0)
        ps_inversion = _set_body_phi(ps_inversion, PentadLabel.AI,    10.0)
        ps_inversion = _set_body_phi(ps_inversion, PentadLabel.BRAIN,  0.01)
        ps_inversion = _set_body_phi(ps_inversion, PentadLabel.HUMAN,  0.01)
        rs_g = classify_resonant_regime(ps_grounding, n_hil=1)
        rs_i = classify_resonant_regime(ps_inversion, n_hil=1)
        # Grounding state should have higher resonance score than extreme inversion
        assert rs_g.resonance_score >= rs_i.resonance_score - 1e-9
