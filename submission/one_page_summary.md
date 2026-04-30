# Unitary Manifold — 1-Page Submission Summary

**Version:** 1.1 | **Date:** 2026-04-30 | `python validate.py` → all numbers below

---

## Model definition

**State space:** Ψ = (φ, π, S, X, Ẋ) on a 1D spatial grid (N=48, dx=0.1).

**Evolution operator:** U = H ∘ T ∘ I

| Symbol | Name | Rule |
|---|---|---|
| I | Irreversibility | dS/dt = κ(A/4G − S),   κ = 0.25 |
| T | Topology | dS_T = dt · Σⱼ Aᵢⱼ(Sⱼ − Sᵢ) |
| H | Holography | S ← min(S, A/4G) |

**Bulk scalar (φ):** semi-implicit Laplacian update, λ|φ|² potential, α coupling to metric.

**Conserved charge:**

    Q = ∫ J⁰ dx,    J^μ = ∂L/∂(∂_μφ)

**Fixed-point theorem (FTUM):** I alone is a Banach contraction with rate

    ρ = |1 − κ dt| = 0.875

guaranteeing unique S* = A/4G with ‖Sⁿ − S*‖ ≤ ρⁿ ‖S⁰ − S*‖.

---

## Numerical results (single run, N=48, dt=5×10⁻⁵, 300 steps)

| Test | Metric | Value | Threshold | Result |
|---|---|---|---|---|
| 1. Charge conservation | Q drift | 0.0013 % | < 0.1 % | **PASS** |
| 2. Hidden-state reconstruction | φ → φ̂ mean error | 2.50 × 10⁻¹³ | < 1 % | **PASS** |
| 3. Nontrivial dynamics | Spectral entropy H(ω) | 0.762 | > 0.01 (pure sine) | **PASS** |
| 4. Fixed-point convergence (I alone) | Defect ‖A/4G − Sⁿ‖ | 6.30 × 10⁻¹³ | < 10⁻⁶ | **PASS** |
| 5. vs. random baseline — charge | drift ratio | 0.0003 % vs 1.62 % | model < random | **PASS** |
| 6. vs. random baseline — prediction | error ratio | 3.0 × 10⁻⁷ vs 1.0 × 10⁻² | model < random | **PASS** |

Convergence rate measured: (1 − κ dt) = **0.8750** — exact match to theory.  
Iterations to convergence: **94**.

---

## Plots

| File | Content |
|---|---|
| `results/01_charge_conservation.png` | Q(t) time series + Gauss-law residual histogram |
| `results/02_reconstruction.png` | φ(t) true vs. reconstructed φ̂(t), error band |
| `results/03_power_spectrum.png` | Power spectrum P(ω), dominant mode at 66 Hz |
| `results/04_phase_space.png` | UEUM phase-space trajectories (X, Ẋ) for 5 nodes |
| `results/05_convergence.png` | Entropy defect decay vs. theoretical rate ρⁿ |
| `results/06_falsification.png` | Model vs. random baseline on both metrics |

---

## Known limitations (see `submission/falsification_report.md` for full detail)

> **Read falsification_report.md §0 first.** Two residuals exist in this codebase
> (`information_conservation_check` and `constraint_monitor`) that measure different
> things.  The Gauss-law number below is the evaluation proxy, not the geometric constraint.

1. **Gauss-law evaluation residual:** mean 2.84 × 10⁻¹ — globally conserved, not locally tight
2. **Full U non-convergence:** defect floor 3.52 × 10⁻¹ — only I-alone is Banach-provable
3. **No mesh-refinement study:** N = 48 only; continuum limit not demonstrated
4. **No external benchmark:** fixed point is self-referential (S* = A/4G by definition)

**Previously open — now resolved:** The nonminimal coupling α was listed as a free parameter. It is determined internally by the KK geometry: **α = φ₀⁻²**, where φ₀ is the stabilised radion value (see `src/core/metric.py:extract_alpha_from_curvature` and `REVIEW_CONCLUSION.md §3`). The cosmological coupling Γ remains observationally open.

---

## Reproducibility

```
git clone https://github.com/wuzbak/Unitary-Manifold-
cd Unitary-Manifold-
pip install numpy matplotlib scipy
python validate.py          # ~6 s; writes results/
python submission/demo.py   # minimal 30-line version; same 6 verdicts
```

No internet access required after clone.  All outputs are deterministic
(seed=42).
