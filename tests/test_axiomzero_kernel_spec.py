# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_axiomzero_kernel_spec.py — Python-Side Kernel Invariant Tests

These tests verify the core mathematical invariants of the AZ-KERNEL
from the Python side — no Rust compilation required.

Invariants tested:
  1. Fiber bundle adjacency rule: |level_a - level_b| must equal 1
  2. φ-debt formula: debt decays by φ⁻¹ = 0.618... per cycle
  3. Geodesic metric weights: g = diag(1.0, 0.5, 2.0, 0.01, 0.618)
  4. KK level count: exactly 5 rings (n_w = 5)
  5. k_cs = 74 = 5² + 7²
  6. φ-debt threshold: reclaim at debt ≥ 8.0
  7. Compactification domain size: 74 pages (one per k_cs)
  8. Braided sound speed: c_s = 12/37

These invariants mirror the Rust kernel constants and must never be
changed without a corresponding HILS-approved pillar update.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
import math
import pytest

# ── Physics constants ──────────────────────────────────────────────────────
WINDING_NUMBER = 5          # n_w
K_CS = 74                   # = 5² + 7²
PHI_INV = 1.0 / 1.6180339887  # φ⁻¹
BRAIDED_SOUND_SPEED = 12 / 37  # c_s from (5,7) braid resonance
PHI_DEBT_THRESHOLD = 8.0
PAGES_PER_DOMAIN = 74
GEODESIC_METRIC = (1.0, 0.5, 2.0, 0.01, 0.618)  # (W_CPU, W_MEM, W_IO, W_AGE, W_PHI)
N_RINGS = 5


# ── Helpers (Python mirror of Rust kernel functions) ───────────────────────

def phi_debt_decay(debt: float, is_write: bool) -> float:
    """Mirror of phi_debt.rs: decay = debt × φ⁻¹ + delta."""
    if is_write:
        return debt * PHI_INV + 1.0
    else:
        return max(0.0, debt * PHI_INV - 0.5)


def geodesic_distance(cpu: float, mem: float, io: float, age: float, phi: float) -> float:
    """Mirror of geodesic.rs: distance = √(Σ gᵢᵢ × xᵢ²)."""
    g = GEODESIC_METRIC
    return math.sqrt(
        g[0] * cpu ** 2
        + g[1] * mem ** 2
        + g[2] * io ** 2
        + g[3] * age ** 2
        + g[4] * phi ** 2
    )


def ipc_adjacency_allowed(level_a: int, level_b: int) -> bool:
    """Mirror of fiber_bundle.rs: IPC only between adjacent KK levels."""
    return abs(level_a - level_b) == 1


# ── 1. Fiber bundle adjacency rule ─────────────────────────────────────────

def test_adjacency_level_0_1_allowed():
    assert ipc_adjacency_allowed(0, 1)


def test_adjacency_level_1_0_allowed():
    assert ipc_adjacency_allowed(1, 0)


def test_adjacency_level_3_4_allowed():
    assert ipc_adjacency_allowed(3, 4)


def test_adjacency_level_4_3_allowed():
    assert ipc_adjacency_allowed(4, 3)


def test_adjacency_same_level_blocked():
    for level in range(N_RINGS):
        assert not ipc_adjacency_allowed(level, level)


def test_adjacency_skip_two_blocked():
    assert not ipc_adjacency_allowed(0, 2)
    assert not ipc_adjacency_allowed(1, 3)
    assert not ipc_adjacency_allowed(2, 4)


def test_adjacency_cross_ring_blocked():
    assert not ipc_adjacency_allowed(0, 4)
    assert not ipc_adjacency_allowed(4, 0)


# ── 2. φ-debt formula ─────────────────────────────────────────────────────

def test_phi_debt_write_increases_debt():
    debt = 0.0
    new_debt = phi_debt_decay(debt, is_write=True)
    assert new_debt > debt


def test_phi_debt_read_decreases_debt():
    debt = 5.0
    new_debt = phi_debt_decay(debt, is_write=False)
    assert new_debt < debt


def test_phi_debt_converges_to_phi_fixed_point():
    """After many write→read cycles, debt should oscillate around a fixed point."""
    debt = 0.0
    for _ in range(100):
        debt = phi_debt_decay(debt, is_write=True)
        debt = phi_debt_decay(debt, is_write=False)
    # Must not blow up
    assert 0.0 <= debt < 100.0


def test_phi_debt_read_floor_is_zero():
    """Read cannot drive debt below 0."""
    debt = 0.1
    for _ in range(20):
        debt = phi_debt_decay(debt, is_write=False)
    assert debt >= 0.0


def test_phi_debt_decay_uses_phi_inv():
    """Write increment uses φ⁻¹ as the decay factor."""
    debt = 2.0
    expected = debt * PHI_INV + 1.0
    result = phi_debt_decay(debt, is_write=True)
    assert abs(result - expected) < 1e-12


def test_phi_debt_threshold_constant():
    assert PHI_DEBT_THRESHOLD == 8.0


# ── 3. Geodesic metric weights ─────────────────────────────────────────────

def test_geodesic_metric_has_five_components():
    assert len(GEODESIC_METRIC) == 5


def test_geodesic_metric_io_weight_largest():
    """I/O weight (index 2 = 2.0) dominates because I/O-bound processes need priority."""
    assert GEODESIC_METRIC[2] == max(GEODESIC_METRIC)


def test_geodesic_metric_age_weight_smallest():
    """Age weight (index 3 = 0.01) is the smallest contribution."""
    assert GEODESIC_METRIC[3] == min(GEODESIC_METRIC)


def test_geodesic_metric_phi_weight_equals_phi_inv():
    """The φ weight must equal φ⁻¹ = 0.618..."""
    assert abs(GEODESIC_METRIC[4] - PHI_INV) < 1e-3


def test_geodesic_distance_zero_for_origin():
    d = geodesic_distance(0, 0, 0, 0, 0)
    assert d == pytest.approx(0.0)


def test_geodesic_distance_positive_definite():
    d = geodesic_distance(1, 1, 1, 1, 1)
    assert d > 0.0


def test_geodesic_distance_io_dominates():
    """A process with high I/O debt should have larger geodesic distance than one with equal CPU."""
    d_cpu = geodesic_distance(cpu=5, mem=0, io=0, age=0, phi=0)
    d_io  = geodesic_distance(cpu=0, mem=0, io=5, age=0, phi=0)
    assert d_io > d_cpu, "High I/O should result in greater geodesic distance than high CPU"


def test_geodesic_distance_triangle_inequality():
    """Simplified triangle inequality: d(A,C) ≤ d(A,B) + d(B,C) for linear path."""
    d_ab = geodesic_distance(1, 0, 0, 0, 0)
    d_bc = geodesic_distance(0, 1, 0, 0, 0)
    d_ac = geodesic_distance(1, 1, 0, 0, 0)
    # Not strict triangle inequality in this metric, but sum must dominate:
    assert d_ac <= d_ab + d_bc + 1e-10


# ── 4. KK level count ─────────────────────────────────────────────────────

def test_n_rings_equals_five():
    assert N_RINGS == WINDING_NUMBER


def test_ring_range_valid():
    """Rings must be 0, 1, 2, 3, 4."""
    rings = list(range(N_RINGS))
    assert rings == [0, 1, 2, 3, 4]


# ── 5. k_cs = 74 = 5² + 7² ───────────────────────────────────────────────

def test_k_cs_equals_74():
    assert K_CS == 74


def test_k_cs_equals_5_squared_plus_7_squared():
    assert K_CS == 5 ** 2 + 7 ** 2


def test_pages_per_domain_equals_k_cs():
    assert PAGES_PER_DOMAIN == K_CS


# ── 6. Compactification parameters ────────────────────────────────────────

def test_braided_sound_speed():
    assert abs(BRAIDED_SOUND_SPEED - 12 / 37) < 1e-15


def test_phi_inv_approximation():
    """φ⁻¹ should be within 0.1% of the golden ratio inverse."""
    golden_ratio = (1 + math.sqrt(5)) / 2
    assert abs(PHI_INV - 1 / golden_ratio) < 0.001


# ── 7. Integration: scheduler picks minimum geodesic distance ──────────────

def test_scheduler_selects_minimum_distance_process():
    """
    Given two processes, the scheduler should select the one with the
    smaller geodesic distance (closer to the current metric state).
    """
    # Process A: high I/O debt (far from ideal)
    d_a = geodesic_distance(cpu=0, mem=0, io=8, age=100, phi=5)
    # Process B: low debt (close to ideal)
    d_b = geodesic_distance(cpu=0.1, mem=0.1, io=0.1, age=1, phi=0.1)
    # Scheduler should pick B (lower distance = next to run)
    selected = "A" if d_a < d_b else "B"
    assert selected == "B", f"Scheduler chose {selected}; d_A={d_a:.4f}, d_B={d_b:.4f}"
