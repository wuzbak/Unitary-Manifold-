# Core Theory — Unitary Manifold

## What is the Unitary Manifold?

The Unitary Manifold is a 5-dimensional Kaluza-Klein gauge-geometric framework
developed by ThomasCory Walker-Pearson (2026). Its central claim is:

> **The Second Law of Thermodynamics is a geometric identity, not a statistical postulate.**

This means that the tendency of entropy to increase — the arrow of time — is
not an emergent approximation or a probabilistic assumption. It is a direct
consequence of the geometry of spacetime when a 5th compact dimension is
included.

## The 5D Geometry

The manifold is a 5-dimensional spacetime M⁵ = M⁴ × S¹, where:

- **M⁴** is ordinary 4-dimensional spacetime (space + time)
- **S¹** is a compact circular 5th dimension with radius R (extremely small,
  near the Planck scale)

The 5D metric takes the Kaluza-Klein ansatz:

```
ds² = g_μν dx^μ dx^ν + φ²(dy + A_μ dx^μ)²
```

where y is the coordinate on the compact 5th dimension, φ is a scalar (dilaton)
field, and A_μ is a gauge vector field.

## The Irreversibility Field

The key new ingredient is the **irreversibility field** B_μ — a vector field
that lives in the 5th dimension. Its field strength tensor is:

```
H_μν = ∂_μ B_ν − ∂_ν B_μ
```

This field is not present in ordinary Kaluza-Klein theory. It is the geometric
object that encodes the arrow of time.

## Kaluza-Klein Reduction

When the 5D theory is dimensionally reduced to 4D (integrating out the compact
5th dimension), the irreversibility field B_μ appears directly in the 4D
Einstein equations via the H_μν term. This is the Walker-Pearson mechanism:
the Second Law does not need to be *imposed* — it falls out automatically from
the 5D geometry.

## What This Means for 4D Existence

1. **The arrow of time is real and geometric** — it is not a low-entropy
   initial condition or a coarse-graining artifact.

2. **Information is conserved** — the information current J^μ_inf = φ²u^μ
   satisfies ∇_μ J^μ_inf = 0 (covariant conservation). Black hole evaporation
   does not destroy information (Theorem XII).

3. **The coupling constant α is derived** — the fine-structure-constant-like
   coupling α = φ₀⁻² where φ₀ is the vacuum value of the scalar field. It is
   not a free parameter.

4. **The Standard Model, QM, and EM are projections** — the full 5D geometry
   contains General Relativity, Quantum Mechanics, Electromagnetism, and the
   Standard Model as exact 4D projections (see UNIFICATION_PROOF.md).

## Key Files

- `WHAT_THIS_MEANS.md` — plain-language explanation for non-specialists
- `MCP_INGEST.md` — compact structured summary for AI agents
- `README.md` — full project overview with equations
- `UNIFICATION_PROOF.md` — formal proof of QM/EM/SM as projections
- `src/core/metric.py` — Python implementation of the 5D metric
- `src/core/evolution.py` — Walker-Pearson field evolution
