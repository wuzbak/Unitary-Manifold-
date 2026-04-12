# Key Equations — Unitary Manifold

## 5D Metric Ansatz (Kaluza-Klein Decomposition)

```
ds² = g_μν dx^μ dx^ν + φ²(dy + A_μ dx^μ)²
```

| Symbol | Meaning |
|--------|---------|
| g_μν | 4D spacetime metric |
| φ | Scalar (KK dilaton) field — sets the radius of the 5th dimension |
| A_μ | KK gauge vector field |
| y | Coordinate on compact 5th dimension (S¹) |

## Walker-Pearson Field Equations

The central equations of the theory — the 4D Einstein equations modified by
the irreversibility field:

```
G_μν + λ²(H_μρ H_ν^ρ − ¼ g_μν H²) + α R φ² g_μν = 8πG₄ T_μν
```

| Symbol | Meaning |
|--------|---------|
| G_μν | Einstein tensor (4D) |
| H_μν = ∂_μ B_ν − ∂_ν B_μ | Irreversibility field strength tensor |
| H² = H_μν H^μν | Irreversibility field norm |
| λ | Irreversibility coupling constant |
| α | Derived coupling: α = φ₀⁻² |
| R | 4D Ricci scalar |
| φ | KK dilaton scalar field |
| G₄ | 4D Newton's gravitational constant |
| T_μν | Stress-energy tensor of matter |

## α Derivation

The coupling α is **derived**, not a free parameter:

```
α = φ₀⁻²
```

where φ₀ is the vacuum expectation value (VEV) of the KK dilaton φ. This VEV
is determined by a self-consistency equation:

```
V'(φ₀) = 0,   V(φ) = − ½ λ² ⟨H²⟩ φ² − α R₀ φ⁴
```

Note: the full analytic closure of this self-consistency equation is an
acknowledged open problem (see 03_predictions.md for honest gaps).

## Information Current (Conservation Law)

```
∇_μ J^μ_inf = 0,   J^μ_inf = φ² u^μ
```

The information current is the dilaton field squared times the 4-velocity u^μ.
Its covariant divergence vanishes — information is conserved. This is the
geometric statement of unitarity and underpins Theorem XII (BH information
preservation).

## UEUM — Unified Evolution Universal Manifold

The geodesic equation on the extended 5D manifold with entropy and topological
sources:

```
Ẍ^a + Γ^a_{bc} Ẋ^b Ẋ^c = G_U^{ab} ∇_b S_U + δ/δX^a (Σ A_{∂,i}/4G + Q_top)
```

| Symbol | Meaning |
|--------|---------|
| X^a | Coordinates on the unified manifold |
| Γ^a_{bc} | Christoffel symbols |
| G_U^{ab} | Universal metric |
| S_U | Universal entropy functional |
| A_{∂,i} | Boundary area contributions |
| Q_top | Topological charge |

The right-hand side drives evolution along the entropy gradient — this is
the geometric formulation of the Second Law.

## FTUM — Fixed-Point Theorem of the Unitary Manifold

The evolution operator U is:

```
U = I + H + T
```

where I = identity, H = Hamiltonian evolution, T = topological correction.

The FTUM states there exists a fixed point Ψ* such that:

```
U Ψ* = Ψ*
```

This Ψ* is the self-consistent vacuum of the 5D manifold. The iteration
`Ψ_{n+1} = U Ψ_n` converges to Ψ* for initial states Ψ₀ near the physical
vacuum (proved numerically; analytic proof in QUANTUM_THEOREMS.md Theorem XV).

## Field Symbols Reference

| Symbol | Type | Meaning |
|--------|------|---------|
| B_μ | Vector | Irreversibility field (5D origin) |
| H_μν | 2-tensor | Irreversibility field strength |
| φ | Scalar | KK dilaton (encodes 5th dimension radius) |
| A_μ | Vector | KK gauge field (reduces to EM in flat limit) |
| G_μν | 2-tensor | Einstein tensor |
| T_μν | 2-tensor | Stress-energy of matter |
| J^μ_inf | Vector | Information current |
| λ | Scalar | Irreversibility coupling |
| α | Scalar | Derived coupling = φ₀⁻² |
| φ₀ | Scalar | VEV of dilaton |
| R | Scalar | Ricci scalar |
| G₄ | Scalar | 4D Newton constant |
