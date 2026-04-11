# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
scripts/run_inflation.py
========================
Falsifiability test: scalar spectral index nₛ from the Unitary Manifold.

The Unitary Manifold predicts that the KK radion φ₀ (pinned by the FTUM
fixed point) doubles as the inflaton.  Its self-interaction is described by
the Goldberger–Wise potential V(φ) = λ(φ² − φ₀²)².

This script:
  1. Derives φ₀ from a converged FieldState (using extract_alpha_from_curvature
     which gives α = φ₀⁻², hence φ₀ = α⁻¹/²).
  2. Computes the slow-roll parameters ε, η at the inflection-point horizon exit.
  3. Predicts nₛ, r, and nₜ.
  4. Compares against Planck 2018: nₛ = 0.9649 ± 0.0042.
  5. Exits 0 (PASS) or 1 (FAIL).

Run:
    python scripts/run_inflation.py
"""

import sys
import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.evolution import FieldState, run_evolution
from src.core.metric import extract_alpha_from_curvature
from src.core.inflation import (
    gw_potential_derivs,
    slow_roll_params,
    spectral_index,
    tensor_to_scalar_ratio,
    gw_spectral_index,
    ns_from_phi0,
    planck2018_check,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
)

# ── Parameters ───────────────────────────────────────────────────────────────
N        = 24      # grid points (small: fast, representative)
DX       = 0.1    # grid spacing
DT       = 0.001  # timestep (CFL-safe for N=24, dx=0.1)
STEPS    = 50     # evolution steps to reach near-equilibrium φ₀
LAM      = 1.0    # Goldberger–Wise self-coupling (nₛ independent of λ)
SEED     = 42

print("=" * 62)
print("Unitary Manifold — Spectral Index Falsifiability Test")
print("=" * 62)

# ── Step 1: evolve bulk field to extract stabilised φ₀ ───────────────────────
print("\n[1] Evolving bulk FieldState to extract radion φ₀ …")
rng   = np.random.default_rng(SEED)
state = FieldState.flat(N=N, dx=DX, rng=rng, phi0=1.0, m_phi=0.1)

history = run_evolution(state, dt=DT, steps=STEPS)
final   = history[-1]

alpha_geom, _ = extract_alpha_from_curvature(
    final.g, final.B, final.phi, final.dx
)
phi0_geom = 1.0 / np.sqrt(alpha_geom)   # α = φ₀⁻²  →  φ₀ = α⁻¹/²
phi0_mean  = float(np.mean(np.abs(final.phi)))   # direct spatial mean

print(f"   α (geometric, from KK cross-block)  = {alpha_geom:.6f}")
print(f"   φ₀ (from α = φ₀⁻²)                 = {phi0_geom:.6f}")
print(f"   ⟨|φ|⟩ (spatial mean of evolved φ)   = {phi0_mean:.6f}")

# Use the geometrically derived φ₀ as the canonical value
phi0 = phi0_geom

# ── Step 2: horizon-exit field value ─────────────────────────────────────────
# Inflection-point approximation: φ* = φ₀ / √3  (where V'' = 0, η = 0)
phi_star = phi0 / np.sqrt(3.0)
V, dV, d2V = gw_potential_derivs(phi_star, phi0, lam=LAM)
epsilon, eta = slow_roll_params(phi_star, V, dV, d2V)

print(f"\n[2] Slow-roll parameters at horizon exit φ* = φ₀/√3 = {phi_star:.6f}")
print(f"    V(φ*)   = {V:.6e}")
print(f"    V'(φ*)  = {dV:.6e}")
print(f"    V''(φ*) = {d2V:.6e}")
print(f"    ε       = {epsilon:.6f}")
print(f"    η       = {eta:.6f}")

# ── Step 3: CMB observables ───────────────────────────────────────────────────
ns = spectral_index(epsilon, eta)
r  = tensor_to_scalar_ratio(epsilon)
nt = gw_spectral_index(epsilon)

print(f"\n[3] CMB observables (leading-order slow roll)")
print(f"    nₛ  (scalar tilt)             = {ns:.6f}")
print(f"    r   (tensor-to-scalar ratio)  = {r:.6f}")
print(f"    nₜ  (tensor tilt)             = {nt:.6f}")

# ── Step 4: Planck 2018 comparison ────────────────────────────────────────────
passed_1s = planck2018_check(ns, n_sigma=1.0)
passed_2s = planck2018_check(ns, n_sigma=2.0)
deviation  = (ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA   # in σ

print(f"\n[4] Planck 2018 comparison")
print(f"    Target:     nₛ = {PLANCK_NS_CENTRAL} ± {PLANCK_NS_SIGMA}  (1-σ)")
print(f"    Predicted:  nₛ = {ns:.6f}")
print(f"    Deviation:  {deviation:+.2f} σ")
print(f"    1-σ window [{PLANCK_NS_CENTRAL - PLANCK_NS_SIGMA:.4f}, "
      f"{PLANCK_NS_CENTRAL + PLANCK_NS_SIGMA:.4f}]  →  "
      f"{'PASS ✓' if passed_1s else 'FAIL ✗'}")
print(f"    2-σ window [{PLANCK_NS_CENTRAL - 2*PLANCK_NS_SIGMA:.4f}, "
      f"{PLANCK_NS_CENTRAL + 2*PLANCK_NS_SIGMA:.4f}]  →  "
      f"{'PASS ✓' if passed_2s else 'FAIL ✗'}")

# ── Step 5: exit code ─────────────────────────────────────────────────────────
if passed_2s:
    print("\n✓  VERDICT: nₛ prediction is consistent with Planck 2018 (≤ 2 σ).")
    sys.exit(0)
else:
    print(f"\n✗  VERDICT: nₛ = {ns:.4f} lies {abs(deviation):.1f} σ outside "
          f"Planck 2018 — theory requires revision.")
    sys.exit(1)
