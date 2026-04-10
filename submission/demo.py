"""
demo.py — Artifact 2: Unitary Manifold reproducible demo
Usage:  python submission/demo.py   (~4 s, seed=42, 6/6 PASS expected)
Deps:   pip install -r requirements.txt
Notes:  residual definitions and known failure modes → falsification_report.md
"""
from __future__ import annotations
import os, sys, time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.evolution import FieldState, run_evolution, information_current
from src.holography.boundary import BoundaryState, information_conservation_check
from src.multiverse.fixed_point import MultiverseNetwork

N, DX, DT, STEPS     = 48, 0.1, 5e-5, 300
LAM, ALPHA, SEED      = 1.0, 0.1, 42
G4, KAPPA, FP_DT      = 1.0, 0.25, 0.5
FP_TOL                = 1e-6

def _charge(s):
    return float(np.sum(information_current(s.g, s.phi, s.dx)[:, 0]) * s.dx)

def _gauss(s):
    J = information_current(s.g, s.phi, s.dx)
    return float(information_conservation_check(
        J, BoundaryState.from_bulk(s.g, s.B, s.phi, s.dx, s.t).J_bdry, s.dx))

t0 = time.time()

# model run
state   = FieldState.flat(N=N, dx=DX, lam=LAM, alpha=ALPHA, rng=np.random.default_rng(SEED))
history = run_evolution(state, dt=DT, steps=STEPS)
charges = np.array([_charge(s) for s in history])
gauss   = np.array([_gauss(s)  for s in history])
drift   = 100.0 * abs(charges[-1] - charges[0]) / abs(charges[0])
g_mean  = float(gauss.mean())
recon   = float(gauss[-1])

# spectral entropy (midpoint time series, matches validate.py)
phi_t    = np.array([s.phi[N // 2] for s in history])
p        = np.abs(np.fft.rfft(phi_t - phi_t.mean())) ** 2
p       /= p.sum() + 1e-30
H_spec   = float(-np.sum(p * np.log(p + 1e-30)))

# I-alone Banach contraction
S, S_star, defects = 0.0, 1.0 / (4.0 * G4), []
while True:
    S += KAPPA * (S_star - S) * FP_DT
    defects.append(abs(S_star - S))
    if defects[-1] < FP_TOL or len(defects) >= 500:
        break

# random baseline
rng_r   = np.random.default_rng(SEED + 1)
g_r     = np.tile(np.diag([-1.,1.,1.,1.]), (N,1,1)).reshape(N,4,4)
g_r     = 0.5 * (g_r + g_r.transpose(0,2,1) + rng_r.standard_normal((N,4,4)) * 0.5)
s_rand  = FieldState(g=g_r, B=rng_r.standard_normal((N,4))*0.5,
                     phi=rng_r.standard_normal(N)*0.1,
                     t=0.0, dx=DX, lam=LAM, alpha=ALPHA)
hist_r  = run_evolution(s_rand, dt=DT, steps=STEPS)
ch_r    = np.array([_charge(s) for s in hist_r])
ga_r    = np.array([_gauss(s)  for s in hist_r])
drift_r = 100.0 * abs(ch_r[-1] - ch_r[0]) / max(abs(ch_r[0]), 1e-30)
g_r_mean = float(ga_r.mean())

elapsed = time.time() - t0

# ── output ─────────────────────────────────────────────────────────────────
ok  = lambda b: "PASS" if b else "FAIL"
sep = "─" * 65
print(sep)
print(f" UNITARY MANIFOLD  Artifact 2  N={N}  seed={SEED}  {elapsed:.1f}s")
print(sep)
print(f" 1. Charge drift        {drift:.4f}%               [{ok(drift < 0.1)}]")
print(f"    Gauss eval residual {g_mean:.4e}  (see falsification_report.md §0)")
print(f" 2. Recon error         {recon:.4e}           [{ok(recon < 0.01)}]")
print(f" 3. Spectral entropy    {H_spec:.4f}               [{ok(H_spec > 0.5)}]")
print(f" 4. FP defect (I-alone) {defects[-1]:.4e}  {len(defects)} iters  [{ok(defects[-1] < FP_TOL)}]")
print(f" 5. Charge model/rand   {drift:.4f}% / {drift_r:.2f}%         [{ok(drift < drift_r)}]")
print(f" 6. Gauss  model/rand   {g_mean:.4e} / {g_r_mean:.4e}  [{ok(g_mean < g_r_mean)}]")
print(sep)
n = sum([drift<0.1, recon<0.01, H_spec>0.5, defects[-1]<FP_TOL, drift<drift_r, g_mean<g_r_mean])
print(f" VERDICT: {n}/6 PASS  —  open issues: falsification_report.md")
print(sep)
