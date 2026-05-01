# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
scripts/run_metric.py
=====================
Reproducible demo: KK metric assembly, field strength, and curvature computation.

What is tested:
  - assemble_5d_metric on Minkowski + small perturbation
  - field_strength antisymmetry and norm
  - compute_curvature Ricci and scalar curvature R
  - Confirmation that flat-space Ricci ≈ 0

Parameter regime:
  N = 64 grid points, dx = 0.1, lam = 1.0
  Perturbation amplitude eps = 1e-3

Expected outputs (with tolerances):
  - Ricci Frobenius mean < 1.0  (near-flat)
  - R max < 5.0                 (near-flat)
  - H antisymmetry residual < 1e-10
  - 5D metric symmetry residual < 1e-14

Run:
    python scripts/run_metric.py
"""

import json
import sys
import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.metric import (
    field_strength,
    assemble_5d_metric,
    christoffel,
    compute_curvature,
)

# ── Parameters ──────────────────────────────────────────────────────────────
SEED = 0
N = 64
DX = 0.1
LAM = 1.0
EPS = 1e-3

print("=" * 60)
print("Unitary Manifold — Metric Demo")
print("=" * 60)
print(f"  N={N}, dx={DX}, lam={LAM}, eps={EPS}, seed={SEED}")
print()

rng = np.random.default_rng(SEED)

# ── Build fields ─────────────────────────────────────────────────────────────
eta = np.diag([-1.0, 1.0, 1.0, 1.0])
g = np.tile(eta, (N, 1, 1)) + EPS * rng.standard_normal((N, 4, 4))
g = 0.5 * (g + g.transpose(0, 2, 1))
B = EPS * rng.standard_normal((N, 4))
phi = 1.0 + EPS * rng.standard_normal(N)

# ── 5D metric symmetry ───────────────────────────────────────────────────────
G5 = assemble_5d_metric(g, B, phi, lam=LAM)
sym_residual = float(np.max(np.abs(G5 - G5.transpose(0, 2, 1))))
print(f"5D metric symmetry residual (max |G_AB - G_BA|): {sym_residual:.3e}")
assert sym_residual < 1e-14, f"FAIL: symmetry residual too large: {sym_residual}"
print("  ✓ G_AB == G_BA")

# ── Field strength ────────────────────────────────────────────────────────────
H = field_strength(B, DX)
antisym_residual = float(np.max(np.abs(H + H.transpose(0, 2, 1))))
H_frob = float(np.mean(np.linalg.norm(H.reshape(N, -1), axis=1)))
print(f"\nField strength:")
print(f"  H antisymmetry residual:   {antisym_residual:.3e}  (expect < 1e-10)")
print(f"  H Frobenius norm (mean):   {H_frob:.4e}")
assert antisym_residual < 1e-10, f"FAIL: antisymmetry residual too large"
print("  ✓ H_μν + H_νμ == 0")

# ── Curvature ─────────────────────────────────────────────────────────────────
Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, DX, lam=LAM)
ricci_frob_mean = float(np.mean(np.linalg.norm(Ricci.reshape(N, -1), axis=1)))
R_max = float(np.max(np.abs(R)))
R_mean = float(np.mean(R))

print(f"\nCurvature (near-flat initial conditions):")
print(f"  Ricci Frobenius norm mean: {ricci_frob_mean:.4e}  (expect < 1.0)")
print(f"  Scalar curvature R_max:    {R_max:.4e}  (expect < 5.0)")
print(f"  Scalar curvature R_mean:   {R_mean:.4e}")
assert ricci_frob_mean < 1.0, f"FAIL: Ricci too large: {ricci_frob_mean}"
assert R_max < 5.0, f"FAIL: R_max too large: {R_max}"
print("  ✓ Near-flat curvature within expected bounds")

# ── Exact flat-space check ────────────────────────────────────────────────────
g_flat = np.tile(eta, (N, 1, 1))
B_zero = np.zeros((N, 4))
phi_one = np.ones(N)
_, _, Ricci_flat, R_flat = compute_curvature(g_flat, B_zero, phi_one, DX)
print(f"\nExact Minkowski background:")
print(f"  Ricci max abs:  {np.max(np.abs(Ricci_flat)):.3e}  (expect < 1e-10)")
print(f"  R     max abs:  {np.max(np.abs(R_flat)):.3e}      (expect < 1e-10)")
assert np.max(np.abs(Ricci_flat)) < 1e-10
assert np.max(np.abs(R_flat)) < 1e-10
print("  ✓ Ricci = 0, R = 0 for exact flat background")

# ── Structured output ─────────────────────────────────────────────────────────
results = {
    "parameters": {"N": N, "dx": DX, "lam": LAM, "eps": EPS, "seed": SEED},
    "metrics": {
        "5d_symmetry_residual": sym_residual,
        "H_antisymmetry_residual": antisym_residual,
        "H_frob_mean": H_frob,
        "ricci_frob_mean": ricci_frob_mean,
        "R_max": R_max,
        "R_mean": R_mean,
    },
    "tolerances": {
        "5d_symmetry_residual_bound": 1e-14,
        "H_antisymmetry_residual_bound": 1e-10,
        "ricci_frob_mean_bound": 1.0,
        "R_max_bound": 5.0,
    },
    "status": "PASS",
}
print("\n" + json.dumps(results, indent=2))
print("\nAll metric checks PASSED.")
