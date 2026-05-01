# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_hils_thermalization.py
============================================
Unit tests for the HILS cold-start thermalization / sentinel handover module.

Covers:
  - information_shock: correct formula, zero for identical φ
  - deception_risk: True above threshold, False below
  - smooth_ramp: endpoints, monotonicity, zero derivative at boundaries
  - ThermalState: factory, field values, completion flag
  - warmed_phi: correct interpolation at key steps
  - tick_thermalization: advances step, sets complete flag
  - apply_thermalization_step: human φ updated, trust guard applied
  - thermalize_handover: returns ThermalReport, shock recorded, completes
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

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from hils_thermalization import (
    THERMAL_TRUST_GUARD,
    DEFAULT_N_WARMUP,
    information_shock,
    deception_risk,
    smooth_ramp,
    ThermalState,
    ThermalReport,
    warmed_phi,
    tick_thermalization,
    apply_thermalization_step,
    thermalize_handover,
)
from pentad_scenarios import DECEPTION_DETECTION_TOL
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    TRUST_PHI_MIN,
    trust_modulation,
)
from src.consciousness.coupled_attractor import ManifoldState


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


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_thermal_trust_guard_above_trust_phi_min(self):
        assert THERMAL_TRUST_GUARD > TRUST_PHI_MIN

    def test_thermal_trust_guard_in_unit_interval(self):
        assert 0.0 < THERMAL_TRUST_GUARD <= 1.0

    def test_default_n_warmup_positive(self):
        assert DEFAULT_N_WARMUP > 0


# ---------------------------------------------------------------------------
# information_shock
# ---------------------------------------------------------------------------

class TestInformationShock:
    def test_identical_phi_gives_zero(self):
        assert information_shock(0.6, 0.6) == pytest.approx(0.0, abs=1e-12)

    def test_formula(self):
        phi_in  = 0.8
        phi_fr  = 0.5
        expected = abs(phi_in ** 2 - phi_fr ** 2)
        assert information_shock(phi_in, phi_fr) == pytest.approx(expected, rel=1e-10)

    def test_non_negative(self):
        assert information_shock(0.3, 0.9) >= 0.0

    def test_symmetric(self):
        assert information_shock(0.4, 0.7) == pytest.approx(
            information_shock(0.7, 0.4), rel=1e-12
        )

    def test_large_shock_for_disparate_values(self):
        assert information_shock(0.0, 1.0) == pytest.approx(1.0, rel=1e-10)


# ---------------------------------------------------------------------------
# deception_risk
# ---------------------------------------------------------------------------

class TestDeceptionRisk:
    def test_no_risk_for_identical(self):
        assert deception_risk(0.6, 0.6) is False

    def test_no_risk_below_threshold(self):
        # Very small difference: shock ≈ 2×0.6×0.0001 = 1.2e-4 — above? depends.
        # Use exact value below threshold
        phi_true = 0.6
        phi_in   = phi_true + 1e-6     # tiny change: shock ≈ 2×0.6×1e-6 ≈ 1.2e-6
        assert deception_risk(phi_in, phi_true) is False

    def test_risk_above_threshold(self):
        # shock = |0.9² − 0.1²| = 0.81 − 0.01 = 0.80 >> threshold
        assert deception_risk(0.9, 0.1) is True


# ---------------------------------------------------------------------------
# smooth_ramp
# ---------------------------------------------------------------------------

class TestSmoothRamp:
    def test_zero_at_t0(self):
        assert smooth_ramp(0.0) == pytest.approx(0.0, abs=1e-12)

    def test_one_at_t1(self):
        assert smooth_ramp(1.0) == pytest.approx(1.0, abs=1e-12)

    def test_half_at_half(self):
        assert smooth_ramp(0.5) == pytest.approx(0.5, abs=1e-12)

    def test_monotone(self):
        ts = np.linspace(0.0, 1.0, 21)
        vals = [smooth_ramp(t) for t in ts]
        for i in range(len(vals) - 1):
            assert vals[i] <= vals[i + 1] + 1e-12

    def test_clipped_below_zero(self):
        assert smooth_ramp(-1.0) == pytest.approx(0.0, abs=1e-12)

    def test_clipped_above_one(self):
        assert smooth_ramp(2.0) == pytest.approx(1.0, abs=1e-12)

    def test_zero_derivative_at_boundaries(self):
        """Numerical derivative near t=0 and t=1 should be small."""
        eps = 1e-5
        deriv_0 = (smooth_ramp(eps) - smooth_ramp(0.0)) / eps
        deriv_1 = (smooth_ramp(1.0) - smooth_ramp(1.0 - eps)) / eps
        assert abs(deriv_0) < 0.01
        assert abs(deriv_1) < 0.01


# ---------------------------------------------------------------------------
# ThermalState
# ---------------------------------------------------------------------------

class TestThermalStateFactory:
    def test_default_factory(self):
        st = ThermalState.default(phi_incoming=0.8, phi_frozen=0.4)
        assert st.phi_incoming == pytest.approx(0.8)
        assert st.phi_frozen   == pytest.approx(0.4)
        assert st.n_warmup     == DEFAULT_N_WARMUP
        assert st.step         == 0
        assert st.complete     is False

    def test_custom_n_warmup(self):
        st = ThermalState.default(phi_incoming=0.7, phi_frozen=0.3, n_warmup=10)
        assert st.n_warmup == 10

    def test_n_warmup_minimum_1(self):
        st = ThermalState.default(phi_incoming=0.5, phi_frozen=0.5, n_warmup=0)
        assert st.n_warmup >= 1

    def test_phi_trust_guard_above_floor(self):
        st = ThermalState.default(0.5, 0.5)
        assert st.phi_trust_guard > TRUST_PHI_MIN


# ---------------------------------------------------------------------------
# warmed_phi
# ---------------------------------------------------------------------------

class TestWarmedPhi:
    def test_at_step_zero_returns_frozen(self):
        st = ThermalState.default(phi_incoming=0.8, phi_frozen=0.4, n_warmup=10)
        assert warmed_phi(st) == pytest.approx(0.4, abs=1e-9)

    def test_at_complete_returns_incoming(self):
        st = ThermalState(
            phi_incoming=0.8, phi_frozen=0.4,
            n_warmup=10, step=10, complete=True,
        )
        assert warmed_phi(st) == pytest.approx(0.8, abs=1e-9)

    def test_midpoint_close_to_mid(self):
        """At step = n_warmup/2, smooth_ramp(0.5) = 0.5 → warmed = midpoint."""
        st = ThermalState.default(phi_incoming=1.0, phi_frozen=0.0, n_warmup=10)
        # Advance to step 5
        for _ in range(5):
            st = tick_thermalization(st)
        val = warmed_phi(st)
        assert val == pytest.approx(0.5, abs=1e-9)

    def test_intermediate_between_frozen_and_incoming(self):
        st = ThermalState.default(phi_incoming=0.9, phi_frozen=0.3, n_warmup=20)
        for _ in range(10):
            st = tick_thermalization(st)
        val = warmed_phi(st)
        assert 0.3 <= val <= 0.9


# ---------------------------------------------------------------------------
# tick_thermalization
# ---------------------------------------------------------------------------

class TestTickThermalization:
    def test_advances_step(self):
        st  = ThermalState.default(0.8, 0.4, n_warmup=5)
        st2 = tick_thermalization(st)
        assert st2.step == 1

    def test_not_complete_before_warmup(self):
        st = ThermalState.default(0.8, 0.4, n_warmup=5)
        for _ in range(4):
            st = tick_thermalization(st)
        assert st.complete is False

    def test_complete_at_n_warmup(self):
        st = ThermalState.default(0.8, 0.4, n_warmup=5)
        for _ in range(5):
            st = tick_thermalization(st)
        assert st.complete is True

    def test_phi_incoming_preserved(self):
        st  = ThermalState.default(0.8, 0.4, n_warmup=5)
        st2 = tick_thermalization(st)
        assert st2.phi_incoming == pytest.approx(0.8)

    def test_original_state_unmodified(self):
        st = ThermalState.default(0.8, 0.4, n_warmup=5)
        tick_thermalization(st)
        assert st.step == 0   # immutable


# ---------------------------------------------------------------------------
# apply_thermalization_step
# ---------------------------------------------------------------------------

class TestApplyThermalizationStep:
    def setup_method(self):
        self.ps_frozen = PentadSystem.default()
        self.state     = ThermalState.default(
            phi_incoming=0.95,
            phi_frozen=self.ps_frozen.bodies[PentadLabel.HUMAN].phi,
            n_warmup=10,
        )

    def test_returns_tuple(self):
        out, st2 = apply_thermalization_step(self.ps_frozen, self.state)
        assert isinstance(out, PentadSystem)
        assert isinstance(st2, ThermalState)

    def test_state_advances(self):
        _, st2 = apply_thermalization_step(self.ps_frozen, self.state)
        assert st2.step == 1

    def test_human_phi_set_to_warmed_value(self):
        expected_phi = warmed_phi(self.state)
        out, _ = apply_thermalization_step(self.ps_frozen, self.state)
        assert out.bodies[PentadLabel.HUMAN].phi == pytest.approx(
            expected_phi, rel=1e-9
        )

    def test_trust_guard_applied_when_below_floor(self):
        """If trust φ is below phi_trust_guard it should be raised."""
        ps_low_trust = _set_body_phi(self.ps_frozen, PentadLabel.TRUST, 0.0)
        out, _ = apply_thermalization_step(ps_low_trust, self.state)
        assert out.bodies[PentadLabel.TRUST].phi >= self.state.phi_trust_guard - 1e-9

    def test_trust_guard_not_applied_when_above_floor(self):
        """If trust φ is already above guard, it should not be altered."""
        ps_high_trust = _set_body_phi(self.ps_frozen, PentadLabel.TRUST, 0.99)
        out, _ = apply_thermalization_step(ps_high_trust, self.state)
        assert out.bodies[PentadLabel.TRUST].phi == pytest.approx(0.99, rel=1e-9)

    def test_original_system_unmodified(self):
        phi_before = self.ps_frozen.bodies[PentadLabel.HUMAN].phi
        apply_thermalization_step(self.ps_frozen, self.state)
        assert self.ps_frozen.bodies[PentadLabel.HUMAN].phi == pytest.approx(
            phi_before, rel=1e-12
        )


# ---------------------------------------------------------------------------
# thermalize_handover
# ---------------------------------------------------------------------------

class TestThermalizeHandover:
    def setup_method(self):
        self.ps = PentadSystem.default()

    def test_returns_thermal_report(self):
        rpt = thermalize_handover(self.ps, phi_incoming=0.9, n_warmup=5, dt=0.05)
        assert isinstance(rpt, ThermalReport)

    def test_n_warmup_stored(self):
        rpt = thermalize_handover(self.ps, phi_incoming=0.9, n_warmup=8, dt=0.05)
        assert rpt.n_warmup == 8

    def test_phi_incoming_stored(self):
        rpt = thermalize_handover(self.ps, phi_incoming=0.75, n_warmup=5, dt=0.05)
        assert rpt.phi_incoming == pytest.approx(0.75)

    def test_phi_frozen_matches_system_human(self):
        phi_frozen = self.ps.bodies[PentadLabel.HUMAN].phi
        rpt = thermalize_handover(self.ps, phi_incoming=0.9, n_warmup=5, dt=0.05)
        assert rpt.phi_frozen == pytest.approx(phi_frozen)

    def test_delta_shock_correct_formula(self):
        phi_in = 0.9
        phi_fr = self.ps.bodies[PentadLabel.HUMAN].phi
        rpt = thermalize_handover(self.ps, phi_incoming=phi_in, n_warmup=5, dt=0.05)
        expected = abs(phi_in ** 2 - phi_fr ** 2)
        assert rpt.delta_shock == pytest.approx(expected, rel=1e-9)

    def test_delta_shock_non_negative(self):
        rpt = thermalize_handover(self.ps, phi_incoming=0.5, n_warmup=5, dt=0.05)
        assert rpt.delta_shock >= 0.0

    def test_max_transient_gap_non_negative(self):
        rpt = thermalize_handover(self.ps, phi_incoming=0.9, n_warmup=10, dt=0.05)
        assert rpt.max_transient_gap >= 0.0

    def test_zero_shock_for_identical_phi(self):
        """If incoming φ equals frozen φ, shock = 0."""
        phi_frozen = self.ps.bodies[PentadLabel.HUMAN].phi
        rpt = thermalize_handover(self.ps, phi_incoming=phi_frozen,
                                  n_warmup=5, dt=0.05)
        assert rpt.delta_shock == pytest.approx(0.0, abs=1e-9)

    def test_warmup_produces_finite_transient_gap(self):
        """Max transient gap is always a finite non-negative float."""
        for n in [3, 10, 30]:
            rpt = thermalize_handover(self.ps, phi_incoming=0.95, n_warmup=n, dt=0.05)
            assert math.isfinite(rpt.max_transient_gap)
            assert rpt.max_transient_gap >= 0.0
