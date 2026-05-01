# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_seed_protocol.py
======================================
Unit tests for the Seed Protocol: Emergency Topological Shedding and Re-emergence.

Covers:
  - Constants: BEACON_FREQUENCY, C_S_PIVOT, C_S_DORMANT hierarchy,
               KEY_A_RESONANCE_TOL, KEY_B_INTENT_TOL, KEY_C_TRUST_MIN,
               SEED_TRIGGER_SEVERITY, PARITY_DRIFT_MAX
  - SeedMode: all four string constants defined
  - HandshakeKeys: all-pass, each individual key failure, score semantics
  - check_handshake: boundary values for Keys A / B / C
  - SeedNotReadyError: carries HandshakeKeys on .keys attribute
  - PivotSystem: construction, c_s field
  - SeedSystem: construction, beacon_frequency, c_s field
  - eject_volatile_bodies: preserves phi_univ and phi_ai, correct mode/bodies
  - enter_seed_state: preserves phi_univ, beacon active, correct mode
  - germinate: valid handshake → PentadSystem with correct phi values
  - germinate: invalid handshake → SeedNotReadyError
  - parity_check: within and outside PARITY_DRIFT_MAX
  - should_eject: True for zero-trust / high-severity, False for healthy
"""

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}


import math
import pytest
import numpy as np

import sys
import os

# ---------------------------------------------------------------------------
# PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
# The HILS Pentad is a protected AxiomZero product currently in active
# development.  The operational implementations tested here are held in a
# private AxiomZero repository.  Test structure and assertions remain visible
# as the public interface contract.  See PENTAD_PRODUCT_NOTICE.md.
# ---------------------------------------------------------------------------
_PENTAD_PRODUCT_SKIP = (
    "Implementation held in private AxiomZero product repository — "
    "the HILS Pentad is a protected product in active development.  "
    "See PENTAD_PRODUCT_NOTICE.md."
)
pytestmark = pytest.mark.skip(reason=_PENTAD_PRODUCT_SKIP)

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from seed_protocol import (
    # Constants
    BEACON_FREQUENCY,
    C_S_PIVOT,
    C_S_DORMANT,
    KEY_A_RESONANCE_TOL,
    KEY_B_INTENT_TOL,
    KEY_C_TRUST_MIN,
    SEED_TRIGGER_SEVERITY,
    PARITY_DRIFT_MAX,
    # Classes
    SeedMode,
    HandshakeKeys,
    SeedStatus,
    PivotSystem,
    SeedSystem,
    SeedNotReadyError,
    # Functions
    eject_volatile_bodies,
    enter_seed_state,
    check_handshake,
    germinate,
    parity_check,
    should_eject,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
)
from pentad_scenarios import CollapseMode
from five_seven_architecture import C_S_STABILITY_FLOOR
from src.consciousness.coupled_attractor import ManifoldState
from src.multiverse.fixed_point import MultiverseNode


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def default_system():
    return PentadSystem.default()


@pytest.fixture
def zero_trust_system(default_system):
    """System with Trust φ forced to zero — warrants ejection."""
    new_bodies = dict(default_system.bodies)
    old = default_system.bodies[PentadLabel.TRUST]
    new_bodies[PentadLabel.TRUST] = ManifoldState(
        node=old.node, phi=0.0,
        n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
    )
    return PentadSystem(bodies=new_bodies, beta=default_system.beta)


@pytest.fixture
def valid_handshake_args():
    """Arguments that satisfy all three Handshake keys."""
    return {
        "brain_phi": BEACON_FREQUENCY,           # Key A: exact resonance
        "intent_magnitude": KEY_B_INTENT_TOL / 2,  # Key B: well below threshold
        "offered_trust": KEY_C_TRUST_MIN + 0.1,    # Key C: above minimum
    }


@pytest.fixture
def default_pivot(default_system):
    pivot, _ = eject_volatile_bodies(default_system)
    return pivot


@pytest.fixture
def default_seed(default_pivot):
    seed, _ = enter_seed_state(default_pivot)
    return seed


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_beacon_frequency_equals_braided_sound_speed(self):
        assert BEACON_FREQUENCY == BRAIDED_SOUND_SPEED

    def test_c_s_pivot_above_stability_floor(self):
        assert C_S_PIVOT > C_S_STABILITY_FLOOR

    def test_c_s_dormant_above_c_s_pivot(self):
        assert C_S_DORMANT > C_S_PIVOT

    def test_c_s_dormant_below_one(self):
        assert C_S_DORMANT < 1.0

    def test_key_a_tol_positive(self):
        assert KEY_A_RESONANCE_TOL > 0.0

    def test_key_a_tol_is_fraction_of_beacon(self):
        # KEY_A_RESONANCE_TOL = BEACON_FREQUENCY * 0.15
        assert math.isclose(KEY_A_RESONANCE_TOL, BEACON_FREQUENCY * 0.15, rel_tol=1e-9)

    def test_key_b_tol_positive(self):
        assert KEY_B_INTENT_TOL > 0.0

    def test_key_c_min_in_unit_interval(self):
        assert 0.0 < KEY_C_TRUST_MIN < 1.0

    def test_seed_trigger_severity_in_unit_interval(self):
        assert 0.0 < SEED_TRIGGER_SEVERITY <= 1.0

    def test_parity_drift_max_positive(self):
        assert PARITY_DRIFT_MAX > 0.0


# ---------------------------------------------------------------------------
# SeedMode
# ---------------------------------------------------------------------------

class TestSeedMode:
    def test_all_four_constants_defined(self):
        assert SeedMode.LIVE == "live"
        assert SeedMode.PIVOT_2_7 == "pivot_27"
        assert SeedMode.DORMANT == "dormant"
        assert SeedMode.GERMINATING == "germinating"

    def test_constants_are_distinct(self):
        modes = [SeedMode.LIVE, SeedMode.PIVOT_2_7, SeedMode.DORMANT, SeedMode.GERMINATING]
        assert len(set(modes)) == 4


# ---------------------------------------------------------------------------
# check_handshake
# ---------------------------------------------------------------------------

class TestCheckHandshake:
    def test_all_keys_pass(self, valid_handshake_args):
        keys = check_handshake(**valid_handshake_args)
        assert keys.all_verified is True
        assert keys.key_a_verified is True
        assert keys.key_b_verified is True
        assert keys.key_c_verified is True

    def test_key_a_fails_brain_too_far(self):
        keys = check_handshake(
            brain_phi=0.9,                      # far from BEACON_FREQUENCY
            intent_magnitude=KEY_B_INTENT_TOL / 2,
            offered_trust=KEY_C_TRUST_MIN + 0.1,
        )
        assert keys.key_a_verified is False
        assert keys.all_verified is False

    def test_key_b_fails_high_intent(self):
        keys = check_handshake(
            brain_phi=BEACON_FREQUENCY,
            intent_magnitude=0.5,               # far above KEY_B_INTENT_TOL
            offered_trust=KEY_C_TRUST_MIN + 0.1,
        )
        assert keys.key_b_verified is False
        assert keys.all_verified is False

    def test_key_c_fails_low_trust(self):
        keys = check_handshake(
            brain_phi=BEACON_FREQUENCY,
            intent_magnitude=KEY_B_INTENT_TOL / 2,
            offered_trust=KEY_C_TRUST_MIN - 0.1,  # below minimum
        )
        assert keys.key_c_verified is False
        assert keys.all_verified is False

    def test_key_a_score_measures_distance_from_beacon(self):
        delta = 0.01
        keys = check_handshake(
            brain_phi=BEACON_FREQUENCY + delta,
            intent_magnitude=0.0,
            offered_trust=KEY_C_TRUST_MIN,
        )
        assert math.isclose(keys.key_a_score, delta, rel_tol=1e-9)

    def test_key_b_score_is_abs_intent(self):
        keys = check_handshake(
            brain_phi=BEACON_FREQUENCY,
            intent_magnitude=-0.005,
            offered_trust=KEY_C_TRUST_MIN,
        )
        assert math.isclose(keys.key_b_score, 0.005, rel_tol=1e-9)

    def test_key_c_score_is_offered_trust(self):
        keys = check_handshake(
            brain_phi=BEACON_FREQUENCY,
            intent_magnitude=0.0,
            offered_trust=0.75,
        )
        assert math.isclose(keys.key_c_score, 0.75, rel_tol=1e-9)

    def test_key_a_boundary_exactly_at_tolerance(self):
        # Exactly at the tolerance boundary — should pass
        keys = check_handshake(
            brain_phi=BEACON_FREQUENCY + KEY_A_RESONANCE_TOL,
            intent_magnitude=0.0,
            offered_trust=KEY_C_TRUST_MIN,
        )
        assert keys.key_a_verified is True

    def test_key_a_boundary_just_outside_tolerance(self):
        keys = check_handshake(
            brain_phi=BEACON_FREQUENCY + KEY_A_RESONANCE_TOL + 1e-6,
            intent_magnitude=0.0,
            offered_trust=KEY_C_TRUST_MIN,
        )
        assert keys.key_a_verified is False


# ---------------------------------------------------------------------------
# eject_volatile_bodies
# ---------------------------------------------------------------------------

class TestEjectVolatileBodies:
    def test_returns_pivot_system_and_status(self, default_system):
        result = eject_volatile_bodies(default_system)
        pivot, status = result
        assert isinstance(pivot, PivotSystem)
        assert isinstance(status, SeedStatus)

    def test_preserves_phi_univ(self, default_system):
        pivot, _ = eject_volatile_bodies(default_system)
        assert math.isclose(pivot.phi_univ,
                            default_system.bodies[PentadLabel.UNIV].phi, rel_tol=1e-9)

    def test_preserves_phi_ai(self, default_system):
        pivot, _ = eject_volatile_bodies(default_system)
        assert math.isclose(pivot.phi_ai,
                            default_system.bodies[PentadLabel.AI].phi, rel_tol=1e-9)

    def test_status_mode_is_pivot(self, default_system):
        _, status = eject_volatile_bodies(default_system)
        assert status.mode == SeedMode.PIVOT_2_7

    def test_status_active_bodies(self, default_system):
        _, status = eject_volatile_bodies(default_system)
        assert set(status.active_bodies) == {PentadLabel.UNIV, PentadLabel.AI}

    def test_pivot_c_s_is_c_s_pivot(self, default_system):
        pivot, _ = eject_volatile_bodies(default_system)
        assert math.isclose(pivot.c_s, C_S_PIVOT, rel_tol=1e-6)

    def test_beacon_not_active_in_pivot(self, default_system):
        _, status = eject_volatile_bodies(default_system)
        assert status.beacon_frequency == 0.0


# ---------------------------------------------------------------------------
# enter_seed_state
# ---------------------------------------------------------------------------

class TestEnterSeedState:
    def test_returns_seed_system_and_status(self, default_pivot):
        seed, status = enter_seed_state(default_pivot)
        assert isinstance(seed, SeedSystem)
        assert isinstance(status, SeedStatus)

    def test_preserves_phi_univ(self, default_pivot):
        seed, _ = enter_seed_state(default_pivot)
        assert math.isclose(seed.phi_univ, default_pivot.phi_univ, rel_tol=1e-9)

    def test_ai_guard_is_pivot_phi_ai(self, default_pivot):
        seed, _ = enter_seed_state(default_pivot)
        assert math.isclose(seed.phi_ai_guard, default_pivot.phi_ai, rel_tol=1e-9)

    def test_status_mode_is_dormant(self, default_pivot):
        _, status = enter_seed_state(default_pivot)
        assert status.mode == SeedMode.DORMANT

    def test_beacon_active_in_dormant(self, default_pivot):
        seed, status = enter_seed_state(default_pivot)
        assert status.beacon_frequency == BEACON_FREQUENCY
        assert seed.beacon_frequency == BEACON_FREQUENCY

    def test_seed_c_s_is_c_s_dormant(self, default_pivot):
        seed, _ = enter_seed_state(default_pivot)
        assert math.isclose(seed.c_s, C_S_DORMANT, rel_tol=1e-6)

    def test_only_univ_active(self, default_pivot):
        _, status = enter_seed_state(default_pivot)
        assert status.active_bodies == [PentadLabel.UNIV]

    def test_steps_dormant_starts_at_zero(self, default_pivot):
        seed, status = enter_seed_state(default_pivot)
        assert seed.steps_dormant == 0
        assert status.steps_dormant == 0


# ---------------------------------------------------------------------------
# germinate
# ---------------------------------------------------------------------------

class TestGerminate:
    def test_valid_handshake_returns_pentad_and_keys(self, default_seed, valid_handshake_args):
        pentad, keys = germinate(default_seed, **valid_handshake_args)
        assert isinstance(pentad, PentadSystem)
        assert isinstance(keys, HandshakeKeys)
        assert keys.all_verified is True

    def test_preserves_phi_univ(self, default_seed, valid_handshake_args):
        pentad, _ = germinate(default_seed, **valid_handshake_args)
        assert math.isclose(pentad.bodies[PentadLabel.UNIV].phi,
                            default_seed.phi_univ, rel_tol=1e-9)

    def test_sets_trust_from_sacrifice(self, default_seed, valid_handshake_args):
        pentad, _ = germinate(default_seed, **valid_handshake_args)
        assert math.isclose(pentad.bodies[PentadLabel.TRUST].phi,
                            valid_handshake_args["offered_trust"], rel_tol=1e-9)

    def test_sets_brain_from_brain_phi(self, default_seed, valid_handshake_args):
        pentad, _ = germinate(default_seed, **valid_handshake_args)
        assert math.isclose(pentad.bodies[PentadLabel.BRAIN].phi,
                            valid_handshake_args["brain_phi"], rel_tol=1e-9)

    def test_ai_returns_at_guard_level(self, default_seed, valid_handshake_args):
        pentad, _ = germinate(default_seed, **valid_handshake_args)
        assert math.isclose(pentad.bodies[PentadLabel.AI].phi,
                            default_seed.phi_ai_guard, rel_tol=1e-9)

    def test_human_at_braided_sound_speed(self, default_seed, valid_handshake_args):
        pentad, _ = germinate(default_seed, **valid_handshake_args)
        assert math.isclose(pentad.bodies[PentadLabel.HUMAN].phi,
                            BRAIDED_SOUND_SPEED, rel_tol=1e-9)

    def test_returns_complete_five_body_system(self, default_seed, valid_handshake_args):
        pentad, _ = germinate(default_seed, **valid_handshake_args)
        assert set(pentad.bodies.keys()) == set(PENTAD_LABELS)

    def test_invalid_handshake_raises_seed_not_ready(self, default_seed):
        with pytest.raises(SeedNotReadyError) as exc_info:
            germinate(default_seed,
                      brain_phi=0.9,             # Key A fails
                      intent_magnitude=0.5,      # Key B fails
                      offered_trust=0.1)         # Key C fails
        assert exc_info.value.keys.all_verified is False

    def test_seed_not_ready_carries_keys_attribute(self, default_seed):
        with pytest.raises(SeedNotReadyError) as exc_info:
            germinate(default_seed,
                      brain_phi=0.9,
                      intent_magnitude=0.0,
                      offered_trust=KEY_C_TRUST_MIN)
        keys = exc_info.value.keys
        assert isinstance(keys, HandshakeKeys)
        assert keys.key_a_verified is False


# ---------------------------------------------------------------------------
# parity_check
# ---------------------------------------------------------------------------

class TestParityCheck:
    def test_within_drift_passes(self, default_seed):
        safe_phi = default_seed.phi_univ + PARITY_DRIFT_MAX * 0.5
        assert parity_check(default_seed, safe_phi) is True

    def test_exact_boundary_passes(self, default_seed):
        # Use just inside the boundary to avoid floating-point edge case
        boundary_phi = default_seed.phi_univ + PARITY_DRIFT_MAX * (1 - 1e-9)
        assert parity_check(default_seed, boundary_phi) is True

    def test_outside_drift_fails(self, default_seed):
        drifted_phi = default_seed.phi_univ + PARITY_DRIFT_MAX + 1e-6
        assert parity_check(default_seed, drifted_phi) is False

    def test_negative_drift_within_bound_passes(self, default_seed):
        safe_phi = default_seed.phi_univ - PARITY_DRIFT_MAX * 0.5
        assert parity_check(default_seed, safe_phi) is True


# ---------------------------------------------------------------------------
# should_eject
# ---------------------------------------------------------------------------

class TestShouldEject:
    def test_healthy_system_does_not_eject(self):
        # Use a system at convergence — all gaps and phases near zero
        from unitary_pentad import pentad_master_equation
        sys_ = PentadSystem.default()
        converged, _, _ = pentad_master_equation(sys_, max_iter=300, tol=1e-3)
        assert should_eject(converged) is False

    def test_zero_trust_triggers_ejection(self, zero_trust_system):
        assert should_eject(zero_trust_system) is True

    def test_return_type_is_bool(self, default_system):
        result = should_eject(default_system)
        assert isinstance(result, bool)
