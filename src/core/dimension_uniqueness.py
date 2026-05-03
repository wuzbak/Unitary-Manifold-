# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/dimension_uniqueness.py
================================
Pillar 112 — Why 5D?  Dimension Uniqueness.

Assembles the argument that D=5 is the *minimum* bulk dimension consistent
with three independent constraints:

1. FTUM fixed-point isolation  (odd dimension + holographic floor)
2. Holographic irreversibility  (bulk encodes entropy on boundary)
3. Observer self-reference  (ΔI = 0 requires observer ↔ universe boundary)

All three constraints independently select D=5.

Epistemic status: ARGUED — the constraints are physically motivated but no
single rigorous proof closes all three simultaneously.  See FALLIBILITY.md.
"""


def ftum_fixed_point_isolated(n_dim: int) -> bool:
    """Return True if the FTUM fixed point is isolated in *n_dim* dimensions.

    Isolation requires:
      • n_dim is odd  (Z₂ orbifold symmetry forces an odd number of fixed
        points, producing a discrete rather than a continuous family)
      • n_dim >= 5  (holographic bound: bulk must have at least one compact
        dimension beyond the 4D boundary)
    """
    return (n_dim % 2 == 1) and (n_dim >= 5)


def holographic_pair_dimension(bulk_dim: int) -> int:
    """Return the boundary dimension for a given bulk dimension.

    The holographic boundary is always one dimension lower than the bulk.
    """
    return bulk_dim - 1


def minimum_holographic_dim() -> int:
    """Return the minimum bulk dimension that supports holographic irreversibility.

    Irreversibility requires a non-trivial B_μ (1-form gauge field), which
    appears only when there is at least one compact dimension beyond 4D
    spacetime.  Minimum: 4 (spacetime) + 1 (compact) = 5.
    """
    return 5


def observer_dimensionality_constraint() -> int:
    """Return the bulk dimension required by the observer self-reference constraint.

    The observer-universe information balance ΔI = |φ²_brain − φ²_univ| = 0
    requires the observer and the universe boundary to share the same geometry.
    The boundary is 4D, so the bulk must be 5D.
    """
    return 5


def cs_resonance_requires_nw(n_dim: int) -> int:
    """Return the winding number required for CS resonance in *n_dim* dimensions.

    In 5D the unique integer pair satisfying n² + (n+2)² = k_cs = 74 is
    (5, 7), so the required winding number is 5.  For other dimensions the
    resonance pair is not generically (5,7); we return n_dim as a placeholder
    signalling that no canonical choice is known.
    """
    if n_dim == 5:
        return 5
    return n_dim


def dimension_uniqueness_theorem() -> dict:
    """Return the dimension-uniqueness theorem summary.

    theorem_status is "ARGUED": the three constraints all select D=5 but no
    single formal proof simultaneously closes all three.
    """
    return {
        "min_dim_for_holography": minimum_holographic_dim(),
        "min_dim_for_ftum_isolation": 5,
        "observer_constraint": observer_dimensionality_constraint(),
        "cs_resonance_dim": cs_resonance_requires_nw(5),
        "unique_dimension": 5,
        "theorem_status": "ARGUED",
    }
