# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
scripts/run_inflation.py
========================
Falsifiability test: scalar spectral index and CMB power spectrum from the
Unitary Manifold.

The Unitary Manifold predicts that the KK radion φ₀ (pinned by the FTUM
fixed point) doubles as the inflaton.  Its self-interaction is described by
the Goldberger–Wise potential V(φ) = λ(φ² − φ₀²)².

This script:
  1. Derives φ₀ from a converged FieldState (using extract_alpha_from_curvature
     which gives α = φ₀⁻², hence φ₀ = α⁻¹/²).
  2. Computes the slow-roll parameters ε, η at the inflection-point horizon exit.
  3. Predicts nₛ, r, and nₜ.
  4. Compares nₛ against Planck 2018: nₛ = 0.9649 ± 0.0042.
  5. Runs the CMB transfer function to compute Cₗ → Dₗ at representative
     multipoles and evaluates χ² against the Planck 2018 reference Dₗ table.
  6. Exits 0 (both PASS) or 1 (either FAIL).

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
    planck2018_check,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
)
from src.core.transfer import (
    angular_power_spectrum,
    dl_from_cl,
    chi2_planck,
    PLANCK_2018_DL_REF,
    PLANCK_2018_COSMO,
)

# ── Parameters ───────────────────────────────────────────────────────────────
N        = 24      # grid points (small: fast, representative)
DX       = 0.1    # grid spacing
DT       = 0.001  # timestep (CFL-safe for N=24, dx=0.1)
STEPS    = 50     # evolution steps to reach near-equilibrium φ₀
LAM      = 1.0    # Goldberger–Wise self-coupling (nₛ independent of λ)
SEED     = 42

# Multipoles at which to evaluate Dₗ (must overlap with PLANCK_2018_DL_REF)
ELLS_COMPARE = np.array([10, 30, 100, 220, 540, 810, 1000])

print("=" * 66)
print("Unitary Manifold — Spectral Index & CMB Transfer Falsifiability Test")
print("=" * 66)

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
phi0_mean  = float(np.mean(np.abs(final.phi)))

print(f"   α (geometric, from KK cross-block)  = {alpha_geom:.6f}")
print(f"   φ₀ (from α = φ₀⁻²)                 = {phi0_geom:.6f}")
print(f"   ⟨|φ|⟩ (spatial mean of evolved φ)   = {phi0_mean:.6f}")

phi0 = phi0_geom   # canonical geometric value

# ── Step 2: slow-roll parameters ─────────────────────────────────────────────
phi_star = phi0 / np.sqrt(3.0)   # inflection-point approximation (η = 0)
V, dV, d2V = gw_potential_derivs(phi_star, phi0, lam=LAM)
epsilon, eta = slow_roll_params(phi_star, V, dV, d2V)

print(f"\n[2] Slow-roll parameters at horizon exit φ★ = φ₀/√3 = {phi_star:.6f}")
print(f"    V(φ★)    = {V:.6e}")
print(f"    V'(φ★)   = {dV:.6e}")
print(f"    V''(φ★)  = {d2V:.6e}")
print(f"    ε        = {epsilon:.6f}")
print(f"    η        = {eta:.6f}")

# ── Step 3: spectral index test ───────────────────────────────────────────────
ns = spectral_index(epsilon, eta)
r  = tensor_to_scalar_ratio(epsilon)
nt = gw_spectral_index(epsilon)

passed_1s = planck2018_check(ns, n_sigma=1.0)
passed_2s = planck2018_check(ns, n_sigma=2.0)
deviation  = (ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA

print(f"\n[3] CMB observables (leading-order slow roll)")
print(f"    nₛ  (scalar tilt)             = {ns:.6f}")
print(f"    r   (tensor-to-scalar ratio)  = {r:.6f}")
print(f"    nₜ  (tensor tilt)             = {nt:.6f}")
print(f"\n    Planck 2018 target: nₛ = {PLANCK_NS_CENTRAL} ± {PLANCK_NS_SIGMA}  (1-σ)")
print(f"    Deviation:  {deviation:+.2f} σ")
print(f"    1-σ window  →  {'PASS ✓' if passed_1s else 'FAIL ✗'}")
print(f"    2-σ window  →  {'PASS ✓' if passed_2s else 'FAIL ✗'}")

# ── Step 4: CMB transfer function → Dₗ comparison ────────────────────────────
print(f"\n[4] CMB transfer function  (φ₀ → nₛ → Δ²_ℛ(k) → S(k) → Cₗ → Dₗ)")
print(f"    Computing Cₗ at ℓ = {ELLS_COMPARE.tolist()} …")

Cl_pred = angular_power_spectrum(ELLS_COMPARE, ns,
                                  As=PLANCK_2018_COSMO["As"])
Dl_pred = dl_from_cl(ELLS_COMPARE, Cl_pred)

print(f"\n    {'ℓ':>6}  {'Dₗ_pred [μK²]':>16}  "
      f"{'Dₗ_ref [μK²]':>14}  {'σ [μK²]':>9}  {'(pred−ref)/σ':>13}")
print("    " + "-" * 70)

for ell, dl in zip(ELLS_COMPARE, Dl_pred):
    ell = int(ell)
    if ell in PLANCK_2018_DL_REF:
        dl_ref, sigma = PLANCK_2018_DL_REF[ell]
        pull = (dl - dl_ref) / sigma
        flag = "✓" if abs(pull) <= 2.0 else "✗"
        print(f"    {ell:>6}  {dl:>16.1f}  {dl_ref:>14.1f}  "
              f"{sigma:>9.1f}  {pull:>+12.2f}  {flag}")
    else:
        print(f"    {ell:>6}  {dl:>16.1f}  {'—':>14}  {'—':>9}  {'—':>13}")

chi2, chi2_dof, n_dof = chi2_planck(ELLS_COMPARE, Dl_pred)
print(f"\n    χ² = {chi2:.2f}  over  {n_dof} multipoles  "
      f"(χ²/dof = {chi2_dof:.2f})")

transfer_pass = chi2_dof <= 9.0   # generous threshold: <3σ per dof on average

print(f"    χ²/dof ≤ 9 threshold  →  {'PASS ✓' if transfer_pass else 'FAIL ✗'}")

# ── Step 5: overall verdict ───────────────────────────────────────────────────
print("\n" + "=" * 66)
if passed_2s and transfer_pass:
    print("✓  OVERALL VERDICT: theory is consistent with Planck 2018 CMB data.")
    sys.exit(0)
else:
    reasons = []
    if not passed_2s:
        reasons.append(
            f"nₛ = {ns:.4f} is {abs(deviation):.1f} σ from Planck 2018"
        )
    if not transfer_pass:
        reasons.append(
            f"CMB spectrum χ²/dof = {chi2_dof:.2f} exceeds threshold of 9"
        )
    print("✗  OVERALL VERDICT: theory requires revision.")
    for reason in reasons:
        print(f"   • {reason}")
    sys.exit(1)
