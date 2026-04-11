# Test Suite — Unitary Manifold

**256 / 256 tests passing (100%)** — verified 2026-04-11, Python 3.12, pytest 9.0.3

---

## How to Run

```bash
pip install numpy scipy pytest
python -m pytest tests/ -v
```

Expected result:

```
256 passed in ~16s
```

---

## Test File Summary

| File | Tests | What It Covers |
|------|------:|----------------|
| `tests/test_metric.py` | 30 | KK metric assembly, Christoffel symbols, Riemann/Ricci tensors, field strength, α derivation from curvature |
| `tests/test_evolution.py` | 49 | RK4 integrator, FieldState dataclass, CFL timestep, information current, constraint monitor, radion stabilisation, metric volume preservation |
| `tests/test_boundary.py` | 21 | Entropy-area law, Bekenstein–Hawking formula, holographic boundary construction and evolution, information conservation |
| `tests/test_fixed_point.py` | 35 | Multiverse network (chain + fully-connected), operators I / H / T, FTUM fixed-point iteration, α derivation from fixed point |
| `tests/test_convergence.py` | 10 | Full-pipeline integration (bulk → boundary → multiverse), FTUM defect decrease, evolution diagnostics |
| `tests/test_inflation.py` | 111 | GW potential, slow-roll parameters, CMB observables (nₛ, r), Planck 2018 check, KK Jacobian, Casimir potential, birefringence angle, Chern–Simons coupling, triple constraint |
| **Total** | **256** | |

---

## Test Classes at a Glance

### `test_metric.py` (30 tests)

| Class | Tests | What it verifies |
|-------|------:|-----------------|
| `TestFieldStrength` | 4 | H_μν shape, antisymmetry, zero on constant B |
| `TestAssemble5dMetric` | 6 | G_AB shape, G₅₅ = φ², off-diagonal block, symmetry, λ coupling |
| `TestChristoffel` | 4 | Γ shape (4D & 5D), vanishes on flat metric, lower-index symmetry |
| `TestComputeCurvature` | 5 | Output shapes, Ricci symmetry, R≈0 on flat, 5D pipeline ≠ naive 4D |
| `TestExtractAlphaFromCurvature` | 11 | α = φ₀⁻² formula, scaling with φ, spatial mean, cross-block shape and finiteness |

### `test_evolution.py` (49 tests)

| Class | Tests | What it verifies |
|-------|------:|-----------------|
| `TestFieldStateFlat` | 5 | Shapes, t=0, near-Minkowski metric, φ≈1, reproducibility |
| `TestStep` | 6 | Time advances, shapes unchanged, metric symmetry, fields change, g and φ finite |
| `TestRunEvolution` | 4 | History length, first state = initial, times monotone, callback called |
| `TestInformationCurrent` | 4 | J shape, J⁰ > 0, finite, zero when φ = 0 |
| `TestConstraintMonitor` | 3 | Returns expected keys, values finite, φ_max ≈ 1 on flat state |
| `TestRK4VsEuler` | 6 | RK4 and Euler agree at first order, metric symmetric, all fields finite, time advances |
| `TestCFLTimestep` | 4 | dt > 0, finite, scales with dx², default dt within CFL bound |
| `TestEvolutionPhysics` | 3 | R bounded, φ norm bounded, metric invertible over 20 steps |
| `TestRadionStabilization` | 4 | m_phi=0 recovers original behaviour, φ restored toward φ₀, fields carried through steps |
| `TestMetricVolumePreservation` | 6 | det projection enforces target, symmetry preserved, det pinned after RK4 and Euler, 20-step pinning |
| `TestConstraintMonitorDetG` | 4 | det key absent without g kwarg, present with g kwarg, ≈0 for projected metric, finite |

### `test_boundary.py` (21 tests)

| Class | Tests | What it verifies |
|-------|------:|-----------------|
| `TestBoundaryArea` | 4 | Flat metric → identity area, non-negative, scales with metric |
| `TestEntropyArea` | 3 | Bekenstein–Hawking formula, default G₄=1, non-negative |
| `TestBoundaryStateFromBulk` | 7 | h/J_bdry/κ shapes, h symmetric, κ ≥ 0, all finite, h matches spatial block of g |
| `TestEvolveBoundary` | 4 | h finite after step, time advances, h stays symmetric, h changes from initial |
| `TestInformationConservationCheck` | 3 | Returns float, non-negative, finite |

### `test_fixed_point.py` (35 tests)

| Class | Tests | What it verifies |
|-------|------:|-----------------|
| `TestMultiverseNode` | 3 | State vector shape and values, norm positive |
| `TestMultiverseNetwork` | 3 | Chain adjacency, fully-connected adjacency, global state shape |
| `TestApplyIrreversibility` | 5 | dS = κ(A/4G − S)dt formula, no drift at fixed point, S increases/decreases correctly, other fields unchanged |
| `TestApplyHolography` | 4 | Clamps S above bound, does not raise S below bound, exact bound, G₄ scaling |
| `TestApplyTopology` | 2 | Gradient-flow formula, isolated node unchanged |
| `TestUeumAcceleration` | 3 | Shape, finite, no divergence at X=0 |
| `TestFixedPointIteration` | 5 | Return types, convergence on chain, defect < tol, residuals ≥ 0, per-node entropy at bound |
| `TestDeriveAlphaFromFixedPoint` | 10 | α=1 for φ₀=1, α=¼ for φ₀=2, α=4 for φ₀=½, spatial mean, α positive, α decreases with larger φ, runs fixed-point, converges, None network, return types |

### `test_convergence.py` (10 tests)

| Class | Tests | What it verifies |
|-------|------:|-----------------|
| `TestFullPipeline` | 2 | Bulk → boundary → multiverse end-to-end, boundary evolution after bulk step |
| `TestFTUMConvergence` | 3 | Defect decreases overall, residual history non-empty, fully-connected network also converges |
| `TestEvolutionDiagnostics` | 3 | φ energy bounded, Ricci symmetry preserved through step, information conservation stays finite |
| `TestBoundaryDiagnostics` | 2 | Boundary entropy ≥ 0 after evolution, κ ≥ 0 after bulk step |

### `test_inflation.py` (111 tests)

| Class | Tests | What it verifies |
|-------|------:|-----------------|
| `TestGWPotential` | 4 | Zero at minimum, non-negative, λ scaling, array input |
| `TestGWPotentialDerivs` | 4 | V=0 at minimum, d²V=0 at inflection, finite at φ=0, consistent with potential |
| `TestSlowRollParams` | 4 | η=0 at inflection, ε ≥ 0, raises on non-positive V, scale-invariant limit |
| `TestCMBObservables` | 4 | nₛ formula, tensor ratio r, tensor tilt nₜ, consistency relation |
| `TestNsFromPhi0` | 4 | Finite tuple, λ-independent, φ₀ dependence, custom φ★ |
| `TestPlanck2018Check` | 5 | Central value passes 1σ, boundary passes 1σ, outside 1σ fails, passes 2σ, far value fails both |
| `TestPrimordialPowerSpectrum` | 4 | Scale-invariant, red/blue tilt direction, at pivot scale |
| `TestCMBSourceFunction` | 4 | Small-k limit, Silk damping at large k, acoustic oscillations, output shape |
| `TestAngularPowerSpectrum` | 4 | Positive, finite, correct shape, red tilt suppresses high-ℓ |
| `TestDlFromCl` | 4 | Zero at ℓ=0, positive for Cℓ>0, T_CMB scaling, order of magnitude |
| `TestChi2Planck` | 5 | Perfect match → χ²=0, 1σ deviation → +1, no overlap raises, partial overlap, n_dof counts |
| `TestJacobian5d4d` | 6 | n=1 formula, n=5/φ=1, √φ₀ scaling, n_winding linear, raises on non-positive φ₀/n_w |
| `TestEffectivePhi0KK` | 5 | n=5 recovers Planck nₛ, φ_eff ≈ 31, bare φ₀ fails Planck, larger n increases φ_eff, φ_eff scales with bare φ₀ |
| `TestCasimirPotential` | 4 | Positive for A_c>0, φ⁴ scaling, A_c scaling, array input |
| `TestCasimirEffectivePotentialDerivs` | 4 | Reduces to GW at A_c=0, Casimir increases V, more-negative dV, positive d²V correction |
| `TestCasimirAcFromPhiMin` | 4 | Round-trip minimum, positive A_c, raises when φ_min ≤ φ₀, φ_min⁸ scaling |
| `TestNsWithCasimir` | 5 | KK minimum ≈ scale-invariant, Jacobian minimum gives Planck nₛ, four finite values, larger φ_min increases nₛ, Casimir dramatically improves over bare FTUM |
| `TestJacobianRSOrbifold` | 7 | RS formula, saturates at large k·r_c, saturation independent of k·r_c > 10, smaller/larger k effects, raises on non-positive k or r_c |
| `TestEffectivePhi0RS` | 3 | n=7/k=1 recovers Planck nₛ, φ_eff ≈ 31, bare φ₀ fails Planck |
| `TestNsStabilityRS` | 3 | nₛ stable across k·r_c, r stable across k·r_c, nₛ passes Planck across k·r_c |
| `TestCsAxionPhotonCoupling` | 6 | Formula, linear in k_CS, positive, raises on bad k_CS/α/r_c |
| `TestFieldDisplacementGW` | 4 | Formula, positive, raises on non-positive input, reference value |
| `TestBirefringenceAngle` | 3 | Formula, absolute value, zero for Δφ=0 |
| `TestCsLevelForBirefringence` | 3 | Matches Planck constant k=74, round-trip, linear scaling with β |
| `TestCosmicBirefringenceK74` | 4 | k=74 gives target β, β within 1σ (0.35°±0.14°), stable across k·r_c, topological consistency |
| `TestTripleConstraint` | 4 | Returns all keys, nₛ passes Planck, β matches target, r positive and finite |

---

## Key Physical Results Verified by Tests

| Observable | Value | Planck 2018 bound | Test class |
|-----------|-------|-------------------|------------|
| Spectral index nₛ | 0.9635 | 0.965 ± 0.004 (1σ) | `TestEffectivePhi0KK`, `TestNsWithCasimir`, `TestTripleConstraint` |
| Tensor-to-scalar r | < 0.056 | < 0.056 (95% CL) | `TestTripleConstraint` |
| Cosmic birefringence β | 0.3513° | 0.35° ± 0.14° (1σ) | `TestCosmicBirefringenceK74` |
| α (derived) | φ₀⁻² | — | `TestExtractAlphaFromCurvature`, `TestDeriveAlphaFromFixedPoint` |
| Holographic bound | S = A/4G | Bekenstein–Hawking | `TestFixedPointIteration`, `TestApplyHolography` |

---

See [RESULTS.md](RESULTS.md) for the complete per-test pass/fail listing.
