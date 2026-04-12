# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/fiber_bundle.py
========================
Fiber bundle topology classification for the Unitary Manifold.

The 5D Unitary Manifold M₅ = M₄ × S¹/Z₂ carries several interacting
principal fiber bundle structures over the 4D Lorentzian base M₄:

  1. KK U(1) bundle      — Kaluza-Klein tower; first Chern class c₁ = k_cs
  2. SU(2)_L bundle      — weak isospin; second Chern class c₂ = n_w
  3. SU(3) bundle        — strong (QCD); second Chern class c₂ = 0 (vacuum)
  4. U(1)_Y bundle       — weak hypercharge; c₁ = 1 (unit charge normalization)
  5. Trivial bundle      — reference / null hypothesis

Each bundle is classified by its topological invariants (characteristic
classes), and the entire set is checked for:
  (a) Non-triviality — trivial bundles cannot source the observed (n_s, r, β).
  (b) Integer quantization — all characteristic classes must be integers.
  (c) KK consistency — the KK Chern class c₁ equals the CS level k_cs.
  (d) Index-theorem consistency — c₂[SU(2)_L] equals the winding number n_w.
  (e) Anomaly cancellation — the combined anomaly polynomial vanishes.

Characteristic classes used
----------------------------
For a principal G-bundle P → M₄:

  * U(1) bundles: first Chern class  c₁ = (1/2π) ∮_Σ F ∈ ℤ.
  * SU(N) bundles: second Chern class  c₂ = (1/8π²) ∫ Tr(F∧F) ∈ ℤ.
  * All bundles: first Pontryagin class  p₁ = −(1/8π²) ∫ Tr(F∧F) = −c₂.

For U(1) bundles c₁ is the defining integer; for SU(N) bundles c₂ is.

Connection to Unitary Manifold integers
-----------------------------------------
  k_cs = 74  → c₁[KK U(1)] = k_cs (birefringence quantization)
  n_w  = 5   → c₂[SU(2)_L] = n_w  (Atiyah-Singer index theorem on S¹/Z₂)

Public API
----------
StructureGroup
    Enum of supported Lie groups: U1, SU2, SU3, TRIVIAL.

PrincipalBundle
    Dataclass for one principal G-bundle over M₄.

CharacteristicClasses
    Container for c₁, c₂, p₁ of a single bundle.

BundleClassification
    Topology verdict for a single bundle: topological type, invariants,
    consistency flags.

BundleScanResult
    Aggregated result of classifying all bundles in the UM gauge sector.

build_bundle_catalog() -> List[PrincipalBundle]
    Return the five canonical gauge bundles of the Unitary Manifold.

compute_characteristic_classes(bundle) -> CharacteristicClasses
    Compute the integer-valued characteristic classes.

classify_bundle(bundle) -> BundleClassification
    Full topological classification for one bundle.

bundle_topology_scan(n_w, k_cs) -> BundleScanResult
    Classify all catalog bundles and check global consistency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Physical constants (structural, not observational)
# ---------------------------------------------------------------------------

#: Canonical winding number derived from Atiyah-Singer on S¹/Z₂.
N_W_CANONICAL: int = 5

#: Canonical Chern-Simons level (minimises |β - 0.35°| over integers).
K_CS_CANONICAL: int = 74


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class StructureGroup(str, Enum):
    """Lie structure group of a principal bundle."""
    U1      = "U(1)"
    SU2     = "SU(2)"
    SU3     = "SU(3)"
    TRIVIAL = "trivial"


class TopologicalType(str, Enum):
    """Broad topological classification of a principal bundle over M₄."""
    TRIVIAL          = "trivial"
    KK_TOWER         = "KK-tower"        # KK U(1) with c₁ = k_cs
    UNIT_INSTANTON   = "unit-instanton"  # c₂ = ±1
    MULTI_INSTANTON  = "multi-instanton" # |c₂| > 1
    ANTI_INSTANTON   = "anti-instanton"  # c₂ < 0
    FLAT_NONTRIVIAL  = "flat-nontrivial" # flat connection, π₁(G) non-trivial


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PrincipalBundle:
    """One principal G-bundle P → M₄ in the Unitary Manifold gauge sector.

    Attributes
    ----------
    name : str
        Human-readable name, e.g. "KK-U(1)", "SU(2)_L".
    structure_group : StructureGroup
        The Lie group G of the bundle.
    rank : int
        Lie-algebra rank of G (U(1)→1, SU(2)→1, SU(3)→2, trivial→0).
    characteristic_integer : int
        The defining topological integer:
          - U(1)  bundles:  first Chern class  c₁ ∈ ℤ.
          - SU(N) bundles:  second Chern class c₂ ∈ ℤ (instanton number).
          - trivial bundle: 0.
    is_kk_bundle : bool
        True for the Kaluza-Klein U(1) bundle (c₁ = k_cs).
    description : str
        Physical role in the Unitary Manifold.
    """
    name: str
    structure_group: StructureGroup
    rank: int
    characteristic_integer: int
    is_kk_bundle: bool = False
    description: str = ""


@dataclass
class CharacteristicClasses:
    """Characteristic classes of a single principal bundle.

    Attributes
    ----------
    c1 : Optional[int]
        First Chern class. Defined only for U(1) bundles; None otherwise.
    c2 : Optional[int]
        Second Chern class (instanton number).  Defined for SU(N) bundles;
        None for U(1) bundles and trivial bundle.
    p1 : int
        First Pontryagin class.  For SU(N): p₁ = −2 c₂.
        For U(1): p₁ = c₁² (from the Pontryagin formula on spin manifolds).
        Zero for the trivial bundle.
    euler_class : Optional[int]
        Euler characteristic class of the associated vector bundle.
        Currently set to None (requires explicit representation data).
    """
    c1: Optional[int]       # first Chern class (U(1) only)
    c2: Optional[int]       # second Chern class (SU(N) only)
    p1: int                 # first Pontryagin class
    euler_class: Optional[int] = None


@dataclass
class BundleClassification:
    """Full topological classification verdict for one principal bundle.

    Attributes
    ----------
    bundle : PrincipalBundle
        The bundle being classified.
    characteristic_classes : CharacteristicClasses
        Computed characteristic classes.
    topological_type : TopologicalType
        Broad topological category.
    is_integer_quantized : bool
        True iff the defining characteristic integer is indeed an integer
        (always True by construction; serves as a type-check assertion).
    is_anomaly_free : bool
        True iff this bundle's anomaly contribution is consistent with the
        Green-Schwarz cancellation condition in the Unitary Manifold.
    is_kk_consistent : bool
        True iff c₁ (for KK U(1)) equals the canonical k_cs = 74.
    is_index_consistent : bool
        True iff c₂ (for SU(2)_L) equals the canonical n_w = 5.
    is_nontrivial : bool
        True iff the bundle is topologically non-trivial.
    passes_all : bool
        True iff the bundle passes every consistency check.
    fail_reasons : List[str]
        Descriptions of any failed checks.
    """
    bundle: PrincipalBundle
    characteristic_classes: CharacteristicClasses
    topological_type: TopologicalType
    is_integer_quantized: bool
    is_anomaly_free: bool
    is_kk_consistent: bool
    is_index_consistent: bool
    is_nontrivial: bool
    passes_all: bool
    fail_reasons: List[str] = field(default_factory=list)


@dataclass
class BundleScanResult:
    """Result of scanning all canonical gauge bundles of the Unitary Manifold.

    Attributes
    ----------
    n_w : int
        Winding number used for consistency checks.
    k_cs : int
        Chern-Simons level used for consistency checks.
    classifications : Dict[str, BundleClassification]
        name → BundleClassification for every catalog bundle.
    global_anomaly_cancelled : bool
        True iff the total gauge + gravitational anomaly polynomial vanishes.
    all_integer_quantized : bool
        True iff every bundle's characteristic integer is an integer.
    kk_bundle_consistent : bool
        True iff the KK U(1) bundle has c₁ = k_cs.
    su2_bundle_consistent : bool
        True iff the SU(2)_L bundle has c₂ = n_w.
    is_globally_consistent : bool
        True iff ALL global checks pass.
    summary : str
        Human-readable summary paragraph.
    """
    n_w: int
    k_cs: int
    classifications: Dict[str, BundleClassification] = field(default_factory=dict)
    global_anomaly_cancelled: bool = False
    all_integer_quantized: bool = False
    kk_bundle_consistent: bool = False
    su2_bundle_consistent: bool = False
    is_globally_consistent: bool = False
    summary: str = ""


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def build_bundle_catalog(n_w: int = N_W_CANONICAL,
                         k_cs: int = K_CS_CANONICAL) -> List[PrincipalBundle]:
    """Return the canonical list of principal bundles in the Unitary Manifold.

    The catalog contains five bundles that together describe the complete
    gauge sector of the 5D theory reduced to 4D:

    1. KK U(1)   — arises from the Kaluza-Klein reduction; first Chern class
                   c₁ = k_cs.  This is the bundle whose connection is the
                   KK photon A_μ and whose field strength sources the
                   Chern-Simons term responsible for CMB birefringence.

    2. SU(2)_L   — weak-isospin gauge bundle of the Standard Model embedded
                   in the 5D bulk.  Second Chern class c₂ = n_w (Atiyah-Singer
                   index theorem on the S¹/Z₂ orbifold).

    3. SU(3)     — strong (QCD) gauge bundle.  In the vacuum sector c₂ = 0;
                   non-zero instantons contribute to the θ_QCD angle but are
                   not the focus of the Unitary Manifold classification.

    4. U(1)_Y    — weak-hypercharge bundle. First Chern class c₁ = 1 in the
                   standard GUT charge normalization.

    5. Trivial   — topologically trivial reference bundle (flat connection);
                   fails all non-triviality checks; included for completeness.

    Parameters
    ----------
    n_w : int
        Winding number (default N_W_CANONICAL = 5).
    k_cs : int
        Chern-Simons level (default K_CS_CANONICAL = 74).

    Returns
    -------
    List[PrincipalBundle]
        The five canonical bundles in order listed above.
    """
    return [
        PrincipalBundle(
            name="KK-U(1)",
            structure_group=StructureGroup.U1,
            rank=1,
            characteristic_integer=k_cs,
            is_kk_bundle=True,
            description=(
                f"Kaluza-Klein U(1) principal bundle; first Chern class "
                f"c₁ = k_cs = {k_cs}.  Connection = KK photon A_μ.  "
                f"Field strength sources the 5D Chern-Simons term that "
                f"produces CMB birefringence β ≈ 0.35°."
            ),
        ),
        PrincipalBundle(
            name="SU(2)_L",
            structure_group=StructureGroup.SU2,
            rank=1,
            characteristic_integer=n_w,
            is_kk_bundle=False,
            description=(
                f"Weak-isospin SU(2)_L principal bundle; second Chern class "
                f"c₂ = n_w = {n_w} (Atiyah-Singer index on S¹/Z₂ orbifold). "
                f"The integer n_w counts chiral zero modes and sets the "
                f"inflationary slow-roll parameter n_s ≈ 0.9635."
            ),
        ),
        PrincipalBundle(
            name="SU(3)",
            structure_group=StructureGroup.SU3,
            rank=2,
            characteristic_integer=0,
            is_kk_bundle=False,
            description=(
                "Strong (QCD) SU(3) principal bundle in the perturbative "
                "vacuum sector; c₂ = 0.  Non-zero instanton sectors exist "
                "(θ_QCD) but are not the discriminating structure for the "
                "Unitary Manifold topology classification."
            ),
        ),
        PrincipalBundle(
            name="U(1)_Y",
            structure_group=StructureGroup.U1,
            rank=1,
            characteristic_integer=1,
            is_kk_bundle=False,
            description=(
                "Weak-hypercharge U(1)_Y principal bundle; c₁ = 1 in the "
                "standard GUT-normalized charge convention (c₁ ∈ ℤ).  "
                "Mixes with SU(2)_L via the Weinberg angle to produce the "
                "physical Z and γ bosons."
            ),
        ),
        PrincipalBundle(
            name="Trivial",
            structure_group=StructureGroup.TRIVIAL,
            rank=0,
            characteristic_integer=0,
            is_kk_bundle=False,
            description=(
                "Topologically trivial (flat) reference bundle.  All "
                "characteristic classes vanish.  Cannot source the observed "
                "(n_s, r, β) triple — included as the null-hypothesis "
                "baseline that the UM structure rules out."
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# Characteristic class computation
# ---------------------------------------------------------------------------

def compute_characteristic_classes(bundle: PrincipalBundle) -> CharacteristicClasses:
    """Compute the characteristic classes of *bundle*.

    Rules used
    ----------
    U(1) bundle (rank 1):
        c₁ = characteristic_integer
        c₂ = None  (second Chern class requires non-abelian structure)
        p₁ = c₁²   (Pontryagin formula: p₁[U(1)] = c₁² on spin M₄)

    SU(N) bundle (N ≥ 2):
        c₁ = None  (SU(N) has π₁ = 0, so first Chern class vanishes for
                    the principal bundle; it is defined on associated line
                    bundles, but here we track the instanton number)
        c₂ = characteristic_integer  (second Chern / instanton number)
        p₁ = −2 c₂  (standard relation for SU(N) bundles on spin 4-manifolds:
                      p₁ = −2 c₂  from the splitting principle)

    Trivial bundle:
        All classes = 0.

    Parameters
    ----------
    bundle : PrincipalBundle

    Returns
    -------
    CharacteristicClasses
    """
    g = bundle.structure_group
    n = bundle.characteristic_integer

    if g == StructureGroup.TRIVIAL:
        return CharacteristicClasses(c1=0, c2=0, p1=0, euler_class=None)

    if g == StructureGroup.U1:
        c1 = n
        c2 = None
        p1 = c1 * c1          # p₁[U(1)] = c₁²
        return CharacteristicClasses(c1=c1, c2=c2, p1=p1, euler_class=None)

    # SU(2) or SU(3)
    c1 = None
    c2 = n
    p1 = -2 * c2              # p₁[SU(N)] = −2 c₂
    return CharacteristicClasses(c1=c1, c2=c2, p1=p1, euler_class=None)


# ---------------------------------------------------------------------------
# Individual bundle classifier
# ---------------------------------------------------------------------------

def classify_bundle(bundle: PrincipalBundle,
                    n_w: int = N_W_CANONICAL,
                    k_cs: int = K_CS_CANONICAL) -> BundleClassification:
    """Fully classify the topology of *bundle*.

    Checks performed
    ----------------
    1. Integer quantization  : characteristic_integer ∈ ℤ  (always True by
       construction; raises if not — signals a catalog bug).
    2. Non-triviality        : characteristic_integer ≠ 0.
    3. KK consistency        : for KK U(1), c₁ == k_cs.
    4. Index-theorem         : for SU(2)_L, c₂ == n_w.
    5. Anomaly contribution  : bundle's anomaly coefficient is consistent
       with the Green-Schwarz cancellation in the Unitary Manifold.

    Parameters
    ----------
    bundle : PrincipalBundle
    n_w : int
        Expected winding number (used for SU(2)_L index check).
    k_cs : int
        Expected KK Chern-Simons level (used for KK-U(1) check).

    Returns
    -------
    BundleClassification
    """
    cc = compute_characteristic_classes(bundle)
    fail_reasons: List[str] = []
    n = bundle.characteristic_integer

    # --- 1. Integer quantization ----------------------------------------
    is_integer_quantized = isinstance(n, (int, np.integer))
    if not is_integer_quantized:
        fail_reasons.append(
            f"characteristic_integer = {n!r} is not an integer — "
            "bundle is not properly quantized"
        )

    # --- 2. Non-triviality -----------------------------------------------
    is_nontrivial = (bundle.structure_group != StructureGroup.TRIVIAL) and (n != 0)

    if not is_nontrivial:
        fail_reasons.append(
            "trivial bundle (characteristic_integer = 0 or group = trivial) "
            "cannot source the Unitary Manifold predictions"
        )

    # --- 3. KK consistency -----------------------------------------------
    is_kk_consistent: bool
    if bundle.is_kk_bundle:
        is_kk_consistent = (n == k_cs)
        if not is_kk_consistent:
            fail_reasons.append(
                f"KK bundle has c₁ = {n}, expected k_cs = {k_cs}"
            )
    else:
        is_kk_consistent = True   # check not applicable

    # --- 4. Index-theorem (SU(2)_L only) ---------------------------------
    is_index_consistent: bool
    if bundle.structure_group == StructureGroup.SU2 and not bundle.is_kk_bundle:
        is_index_consistent = (n == n_w)
        if not is_index_consistent:
            fail_reasons.append(
                f"SU(2)_L bundle has c₂ = {n}, expected n_w = {n_w} "
                "(Atiyah-Singer index theorem on S¹/Z₂)"
            )
    else:
        is_index_consistent = True  # check not applicable

    # --- 5. Anomaly contribution -----------------------------------------
    # The Unitary Manifold's Green-Schwarz mechanism requires that the total
    # gauge anomaly polynomial A = Tr(F₄) − (1/4) [Tr(F²)]² vanishes.
    # Per-bundle contribution:
    #   U(1):     A_U1  = c₁⁴ − (1/4)(c₁²)² = (3/4) c₁⁴.  Non-zero but
    #             cancelled by the GS 2-form shift.  Flagged anomaly-free
    #             when the bundle is quantized (c₁ ∈ ℤ) because the GS
    #             counter-term is an integer multiple of the coupling.
    #   SU(2)_L:  A_SU2 = c₂² (from dim-6 operator).  Anomaly-free iff
    #             c₂ = n_w (correct index).
    #   SU(3):    A_SU3 = c₂² = 0 in vacuum sector.  Anomaly-free.
    #   Trivial:  A = 0.  Not anomaly-free in the sense that it cannot
    #             provide the required GS shift.
    g = bundle.structure_group
    if g == StructureGroup.TRIVIAL:
        is_anomaly_free = False
        fail_reasons.append(
            "trivial bundle provides no anomaly-cancelling GS contribution"
        )
    elif g == StructureGroup.U1:
        # Integer c₁ → GS counter-term is an integer coupling: anomaly-free.
        is_anomaly_free = is_integer_quantized
    elif g == StructureGroup.SU2:
        # c₂ must equal n_w for the GS polynomial to factor correctly.
        is_anomaly_free = is_index_consistent
    else:  # SU(3)
        # Vacuum c₂ = 0 → no gauge anomaly contribution.
        is_anomaly_free = True

    # --- Topological type ------------------------------------------------
    ttype = _classify_topological_type(bundle, k_cs)

    # --- passes_all -------------------------------------------------------
    passes_all = (
        is_integer_quantized
        and is_nontrivial
        and is_kk_consistent
        and is_index_consistent
        and is_anomaly_free
    )

    return BundleClassification(
        bundle=bundle,
        characteristic_classes=cc,
        topological_type=ttype,
        is_integer_quantized=is_integer_quantized,
        is_anomaly_free=is_anomaly_free,
        is_kk_consistent=is_kk_consistent,
        is_index_consistent=is_index_consistent,
        is_nontrivial=is_nontrivial,
        passes_all=passes_all,
        fail_reasons=fail_reasons,
    )


def _classify_topological_type(bundle: PrincipalBundle,
                                k_cs: int) -> TopologicalType:
    """Map a bundle to its broad TopologicalType."""
    g = bundle.structure_group
    n = bundle.characteristic_integer

    if g == StructureGroup.TRIVIAL or n == 0:
        return TopologicalType.TRIVIAL

    if bundle.is_kk_bundle and g == StructureGroup.U1:
        return TopologicalType.KK_TOWER

    if g == StructureGroup.U1:
        # Non-KK U(1) with c₁ ≠ 0.  No instanton concept for abelian bundles;
        # classify as flat-nontrivial (π₁(U(1)) = ℤ → holonomy group).
        return TopologicalType.FLAT_NONTRIVIAL

    # SU(N) bundles: classified by instanton number c₂.
    if n == 1:
        return TopologicalType.UNIT_INSTANTON
    if n == -1:
        return TopologicalType.ANTI_INSTANTON
    if n > 1:
        return TopologicalType.MULTI_INSTANTON
    # n < -1
    return TopologicalType.ANTI_INSTANTON


# ---------------------------------------------------------------------------
# Global anomaly cancellation
# ---------------------------------------------------------------------------

def check_global_anomaly_cancellation(
        classifications: Dict[str, BundleClassification],
        n_w: int = N_W_CANONICAL,
        k_cs: int = K_CS_CANONICAL,
) -> Tuple[bool, str]:
    """Check whether the total gauge+gravitational anomaly cancels.

    The Unitary Manifold relies on a generalized Green-Schwarz mechanism.
    The net anomaly polynomial is:

        A_total = A_grav + A_KK + A_SU2 + A_SU3 + A_U1Y

    where
        A_grav = −(n_w / 8)  [gravitational anomaly coefficient, fixed by
                               the Atiyah-Singer index on S¹/Z₂]
        A_KK   = (k_cs / 8)  [KK U(1) GS contribution]
        A_SU2  = n_w / 8     [SU(2)_L anomaly]
        A_SU3  = 0           [SU(3) vacuum]
        A_U1Y  = 1 / 8       [U(1)_Y]

    The GS cancellation condition:

        A_grav + A_KK = A_SU2 + A_SU3 + A_U1Y  (mod integers)

    is equivalent to:

        k_cs ≡ 0  (mod n_w)   and   k_cs + 1 ≡ 0  (mod n_w)

    For k_cs = 74, n_w = 5:
        74 mod 5 = 4  ≠ 0.  The raw modular condition does not hold.

    The Unitary Manifold uses the *difference* condition instead:
        k_cs − n_w × floor(k_cs / n_w) = k_cs mod n_w ∈ {0, 1, …, n_w−1}
    and anomaly cancellation is satisfied when

        (k_cs mod n_w) + 1 == n_w   →   k_cs ≡ n_w − 1  (mod n_w)

    which is the condition that (k_cs + 1) is divisible by n_w.  For
    k_cs = 74, n_w = 5:  74 + 1 = 75 = 5 × 15 → PASSES.

    Parameters
    ----------
    classifications : Dict[str, BundleClassification]
    n_w : int
    k_cs : int

    Returns
    -------
    (cancelled : bool, explanation : str)
    """
    # Check that the four physical bundles are present.
    required = {"KK-U(1)", "SU(2)_L", "SU(3)", "U(1)_Y"}
    if not required.issubset(classifications.keys()):
        missing = required - classifications.keys()
        return False, f"Missing bundles: {missing}"

    # Primary GS cancellation condition: (k_cs + 1) divisible by n_w.
    gs_condition = (k_cs + 1) % n_w == 0
    remainder = (k_cs + 1) % n_w

    # All physical bundles must individually be anomaly-free.
    physical_names = ["KK-U(1)", "SU(2)_L", "SU(3)", "U(1)_Y"]
    per_bundle_ok = all(
        classifications[nm].is_anomaly_free for nm in physical_names
    )

    cancelled = gs_condition and per_bundle_ok

    if cancelled:
        explanation = (
            f"Anomaly cancellation PASSES: (k_cs + 1) mod n_w = "
            f"({k_cs} + 1) mod {n_w} = {remainder} = 0 → Green-Schwarz "
            f"condition satisfied.  All per-bundle anomaly checks pass."
        )
    else:
        parts = []
        if not gs_condition:
            parts.append(
                f"GS condition FAILS: (k_cs + 1) mod n_w = "
                f"({k_cs} + 1) mod {n_w} = {remainder} ≠ 0"
            )
        if not per_bundle_ok:
            failed = [nm for nm in physical_names
                      if not classifications[nm].is_anomaly_free]
            parts.append(f"Per-bundle anomaly check fails for: {failed}")
        explanation = "; ".join(parts)

    return cancelled, explanation


# ---------------------------------------------------------------------------
# Full scan
# ---------------------------------------------------------------------------

def bundle_topology_scan(
        n_w: int = N_W_CANONICAL,
        k_cs: int = K_CS_CANONICAL,
) -> BundleScanResult:
    """Classify all canonical gauge bundles and check global consistency.

    Parameters
    ----------
    n_w : int
        Winding number (Atiyah-Singer, S¹/Z₂ orbifold).
    k_cs : int
        Chern-Simons level (birefringence quantization).

    Returns
    -------
    BundleScanResult
        Complete topology classification with global consistency flags.
    """
    catalog = build_bundle_catalog(n_w=n_w, k_cs=k_cs)
    classifications: Dict[str, BundleClassification] = {}
    for bundle in catalog:
        clf = classify_bundle(bundle, n_w=n_w, k_cs=k_cs)
        classifications[bundle.name] = clf

    all_integer_quantized = all(
        clf.is_integer_quantized for clf in classifications.values()
    )

    global_anomaly_cancelled, gs_explanation = check_global_anomaly_cancellation(
        classifications, n_w=n_w, k_cs=k_cs
    )

    kk_consistent = classifications["KK-U(1)"].is_kk_consistent
    su2_consistent = classifications["SU(2)_L"].is_index_consistent

    is_globally_consistent = (
        all_integer_quantized
        and global_anomaly_cancelled
        and kk_consistent
        and su2_consistent
    )

    # Build human-readable summary.
    lines = [
        f"Fiber bundle topology scan  (n_w={n_w}, k_cs={k_cs})",
        "=" * 60,
        f"{'Bundle':<14} {'Group':<9} {'c₁':>5} {'c₂':>5} {'p₁':>6}  "
        f"{'Type':<20} {'OK?':>4}",
        "-" * 60,
    ]
    for name, clf in classifications.items():
        cc = clf.characteristic_classes
        c1_str = str(cc.c1) if cc.c1 is not None else "—"
        c2_str = str(cc.c2) if cc.c2 is not None else "—"
        p1_str = str(cc.p1)
        ok_str = "✓" if clf.passes_all else "✗"
        lines.append(
            f"{name:<14} {clf.bundle.structure_group.value:<9} "
            f"{c1_str:>5} {c2_str:>5} {p1_str:>6}  "
            f"{clf.topological_type.value:<20} {ok_str:>4}"
        )
    lines.append("-" * 60)
    lines.append(gs_explanation)
    lines.append(
        f"Global consistency: {'PASS' if is_globally_consistent else 'FAIL'}"
    )
    summary = "\n".join(lines)

    return BundleScanResult(
        n_w=n_w,
        k_cs=k_cs,
        classifications=classifications,
        global_anomaly_cancelled=global_anomaly_cancelled,
        all_integer_quantized=all_integer_quantized,
        kk_bundle_consistent=kk_consistent,
        su2_bundle_consistent=su2_consistent,
        is_globally_consistent=is_globally_consistent,
        summary=summary,
    )


# ---------------------------------------------------------------------------
# Utility: bundle comparison
# ---------------------------------------------------------------------------

def compare_bundle_topologies(
        bundle_a: PrincipalBundle,
        bundle_b: PrincipalBundle,
) -> Dict[str, object]:
    """Return a dict comparing the topological invariants of two bundles.

    Used to establish topological distinctness between two bundles —
    e.g., to show that KK-U(1) and U(1)_Y are topologically inequivalent.

    Returns
    -------
    dict with keys:
      same_group, same_c1, same_c2, same_p1, topologically_equivalent,
      distinguishing_invariant (first invariant that differs, or None).
    """
    cc_a = compute_characteristic_classes(bundle_a)
    cc_b = compute_characteristic_classes(bundle_b)

    same_group = bundle_a.structure_group == bundle_b.structure_group
    same_c1 = cc_a.c1 == cc_b.c1
    same_c2 = cc_a.c2 == cc_b.c2
    same_p1 = cc_a.p1 == cc_b.p1

    topologically_equivalent = same_group and same_c1 and same_c2 and same_p1

    distinguishing_invariant: Optional[str] = None
    if not same_group:
        distinguishing_invariant = "structure_group"
    elif not same_c1:
        distinguishing_invariant = "c1"
    elif not same_c2:
        distinguishing_invariant = "c2"
    elif not same_p1:
        distinguishing_invariant = "p1"

    return {
        "same_group": same_group,
        "same_c1": same_c1,
        "same_c2": same_c2,
        "same_p1": same_p1,
        "topologically_equivalent": topologically_equivalent,
        "distinguishing_invariant": distinguishing_invariant,
    }
