"""
tests/test_evolution.py
=======================
Tests for src/core/evolution.py — Walker–Pearson field evolution.

Covers:
  - Determinism: identical seeds → identical outputs
  - Flat-space stability: near-Minkowski initial → R stays small, metric stays near-flat
  - constraint_monitor structure: output has expected keys
  - Stress-energy conservation (new T_div_max key)
  - Semi-implicit scalar: phi remains bounded after many steps
"""

import numpy as np
import pytest

from src.core.evolution import (
    FieldState,
    run_evolution,
    step,
    constraint_monitor,
    information_current,
    _stress_energy,
)
from src.core.metric import compute_curvature, field_strength


# ---------------------------------------------------------------------------
# 1. Determinism
# ---------------------------------------------------------------------------

def test_determinism_same_seed():
    """Two runs from the same RNG seed produce identical final states."""
    rng_a = np.random.default_rng(42)
    rng_b = np.random.default_rng(42)
    state_a = FieldState.flat(N=32, dx=0.1, rng=rng_a)
    state_b = FieldState.flat(N=32, dx=0.1, rng=rng_b)
    for _ in range(5):
        state_a = step(state_a, dt=1e-4)
        state_b = step(state_b, dt=1e-4)
    np.testing.assert_array_equal(state_a.g, state_b.g)
    np.testing.assert_array_equal(state_a.B, state_b.B)
    np.testing.assert_array_equal(state_a.phi, state_b.phi)


def test_determinism_different_seeds_differ():
    """Different seeds should produce different initial states."""
    state_a = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(1))
    state_b = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(2))
    assert not np.allclose(state_a.g, state_b.g), (
        "Different seeds should produce different initial conditions"
    )


# ---------------------------------------------------------------------------
# 2. Flat-space stability
# ---------------------------------------------------------------------------

def test_flat_space_ricci_stays_small():
    """Starting from near-flat initial conditions, |R| stays near zero."""
    state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(0))
    # Run a short evolution
    history = run_evolution(state, dt=1e-4, steps=10)
    final = history[-1]
    _, _, Ricci, R = compute_curvature(final.g, final.B, final.phi, final.dx)
    # R should remain small for near-flat, short-time evolution
    assert np.max(np.abs(R)) < 1.0, (
        f"Scalar curvature blew up: R_max = {np.max(np.abs(R)):.3e}"
    )


def test_flat_space_metric_stays_near_minkowski():
    """Metric stays close to Minkowski after short evolution from flat IC."""
    state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(0))
    history = run_evolution(state, dt=1e-4, steps=10)
    final = history[-1]
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    deviation = np.max(np.abs(final.g - eta))
    assert deviation < 0.1, (
        f"Metric deviated too far from Minkowski: max deviation = {deviation:.3e}"
    )


def test_phi_stays_bounded():
    """Scalar field φ remains bounded after many steps (semi-implicit stability)."""
    state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(0))
    history = run_evolution(state, dt=1e-3, steps=50)
    phi_max = max(np.max(np.abs(s.phi)) for s in history)
    assert phi_max < 100.0, (
        f"Scalar field blew up: phi_max = {phi_max:.3e}"
    )


# ---------------------------------------------------------------------------
# 3. constraint_monitor structure
# ---------------------------------------------------------------------------

def test_constraint_monitor_basic_keys():
    """constraint_monitor returns the expected keys."""
    state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(0))
    _, _, Ricci, R = compute_curvature(state.g, state.B, state.phi, state.dx)
    result = constraint_monitor(Ricci, R, state.B, state.phi)
    for key in ("ricci_frob_mean", "R_max", "B_norm_mean", "phi_max"):
        assert key in result, f"Missing key: {key}"
    # All values should be finite non-negative floats
    for key, val in result.items():
        assert np.isfinite(val), f"Non-finite value for key {key}: {val}"
        assert val >= 0.0, f"Negative value for key {key}: {val}"


def test_constraint_monitor_t_div_max_key():
    """constraint_monitor includes T_div_max when g, H, dx are supplied."""
    state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(0))
    _, _, Ricci, R = compute_curvature(state.g, state.B, state.phi, state.dx)
    H = field_strength(state.B, state.dx)
    result = constraint_monitor(Ricci, R, state.B, state.phi,
                                g=state.g, H=H, dx=state.dx)
    assert "T_div_max" in result, "T_div_max key should be present when g, H, dx supplied"
    assert np.isfinite(result["T_div_max"]), "T_div_max should be finite"
    assert result["T_div_max"] >= 0.0, "T_div_max should be non-negative"


def test_constraint_monitor_flat_t_div_near_zero():
    """For flat Minkowski background (B=0), T_div_max should be near zero."""
    N = 32
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1))
    B = np.zeros((N, 4))
    phi = np.ones(N)
    dx = 0.1
    _, _, Ricci, R = compute_curvature(g, B, phi, dx)
    H = field_strength(B, dx)
    result = constraint_monitor(Ricci, R, B, phi, g=g, H=H, dx=dx)
    assert result["T_div_max"] < 1e-12, (
        f"T_div_max should be ~0 for flat background; got {result['T_div_max']:.3e}"
    )


# ---------------------------------------------------------------------------
# 4. Information current
# ---------------------------------------------------------------------------

def test_information_current_shape():
    """information_current returns correct shape (N, 4)."""
    state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(0))
    J = information_current(state.g, state.phi, state.dx)
    assert J.shape == (32, 4)


def test_information_current_nonnegative_density():
    """Time component J^0 (information density proxy) is non-negative."""
    state = FieldState.flat(N=64, dx=0.1, rng=np.random.default_rng(0))
    J = information_current(state.g, state.phi, state.dx)
    assert np.all(J[:, 0] >= 0.0), "Information density J^0 should be non-negative"


# ---------------------------------------------------------------------------
# 5. FieldState factory
# ---------------------------------------------------------------------------

def test_flat_factory_shape():
    """FieldState.flat produces arrays of the correct shapes."""
    state = FieldState.flat(N=64, dx=0.1)
    assert state.g.shape == (64, 4, 4)
    assert state.B.shape == (64, 4)
    assert state.phi.shape == (64,)


def test_flat_factory_metric_nearly_minkowski():
    """FieldState.flat background is near-diagonal Minkowski."""
    N = 64
    state = FieldState.flat(N=N, dx=0.1, rng=np.random.default_rng(0))
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    deviation = np.max(np.abs(state.g - eta))
    assert deviation < 0.01, (
        f"Initial metric too far from Minkowski: {deviation:.3e}"
    )
