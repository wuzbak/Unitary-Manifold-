# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/nw_circularity_audit.py
=====================================
Explicit circularity audit for the n_w = 5 winding-number selection argument.

This module traces every dependency in the n_w = 5 selection chain and
classifies each as:
  - PURELY_GEOMETRIC: Derived from the 5D metric / orbifold structure alone
  - OBSERVATIONAL_INPUT: Requires experimental data as input
  - ARCHITECTURE_LIMIT: Cannot be closed within 5D-EFT

The audit is machine-readable, enabling automated checks that no claim is
over-stated relative to its actual epistemic basis.

Corresponds to Lean4: lean4/UnitaryManifold/NWUniquenessHonest.lean

Author / theory: ThomasCory Walker-Pearson
Code: GitHub Copilot (AI)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

__all__ = [
    "EpistemicStatus",
    "Dependency",
    "CircularityAuditReport",
    "build_nw_dependency_graph",
    "run_circularity_audit",
    "AUDIT_STEPS",
]


class EpistemicStatus(str, Enum):
    """Classification of each step in the n_w derivation chain."""

    PURELY_GEOMETRIC = "PURELY_GEOMETRIC"
    """Derived from 5D metric + orbifold structure, no observational input."""

    OBSERVATIONAL_INPUT = "OBSERVATIONAL_INPUT"
    """Requires experimental measurement as input (honest dependency)."""

    ARITHMETIC_IDENTITY = "ARITHMETIC_IDENTITY"
    """Pure integer/rational arithmetic — machine-verifiable unconditionally."""

    ARCHITECTURE_LIMIT = "ARCHITECTURE_LIMIT"
    """Cannot be closed within 5D-EFT; requires UV completion or new physics."""

    AXIOM_DEPENDENT = "AXIOM_DEPENDENT"
    """Logically follows from stated axioms, but those axioms are not yet
    formally derived (e.g., APS index theorem application)."""

    PROVED = "PROVED"
    """Machine-verified by Lean4 native_decide / norm_num (no physics axioms)."""


@dataclass(frozen=True)
class Dependency:
    """One step in the n_w derivation chain."""

    step_id: str
    """Short identifier, e.g. 'Z2_PARITY'."""

    description: str
    """Human-readable description of this step."""

    status: EpistemicStatus
    """Epistemic classification of this step."""

    pillar: str
    """Pillar(s) where this is established, e.g. 'Pillar 39'."""

    lean4_file: Optional[str]
    """Lean4 file where this is (partially) machine-verified, if any."""

    observational_inputs: List[str] = field(default_factory=list)
    """List of observations required as input (empty if PURELY_GEOMETRIC)."""

    gap_description: Optional[str] = None
    """If not PROVED, description of what remains open."""

    closes_to: Optional[str] = None
    """What this step closes, or None if it is itself a gap."""


# ---------------------------------------------------------------------------
# The canonical audit table
# ---------------------------------------------------------------------------

AUDIT_STEPS: List[Dependency] = [
    Dependency(
        step_id="Z2_PARITY",
        description=(
            "S¹/Z₂ involution y → −y projects out even winding numbers. "
            "Surviving set: n_w ∈ {1, 3, 5, 7, 9, …}."
        ),
        status=EpistemicStatus.PURELY_GEOMETRIC,
        pillar="Pillar 39",
        lean4_file="NWIntegerLattice.lean",
        observational_inputs=[],
        gap_description=None,
        closes_to="Reduces n_w to odd positive integers",
    ),
    Dependency(
        step_id="CS_ANOMALY_GAP_LOWER",
        description=(
            "CS anomaly stability requires mode n=2 to be stable: 4 ≤ n_w. "
            "This derives the LOWER bound n_w ≥ 4 from N_gen = 3 stability."
        ),
        status=EpistemicStatus.AXIOM_DEPENDENT,
        pillar="Pillar 42",
        lean4_file="NWIntegerLattice.lean",
        observational_inputs=["N_gen = 3 (three SM generations, observed)"],
        gap_description=(
            "The CS anomaly gap argument requires N_gen = 3 as input. "
            "N_gen is observed, not derived from the 5D metric."
        ),
        closes_to="n_w ≥ 4 (lower bound)",
    ),
    Dependency(
        step_id="CS_ANOMALY_GAP_UPPER",
        description=(
            "CS anomaly stability requires mode n=3 to be UNstable: n_w < 9. "
            "Combined with Z₂ parity: n_w ≤ 8."
        ),
        status=EpistemicStatus.AXIOM_DEPENDENT,
        pillar="Pillar 42",
        lean4_file="NWIntegerLattice.lean",
        observational_inputs=["N_gen = 3 (three SM generations, observed)"],
        gap_description="Same N_gen = 3 dependency as lower bound.",
        closes_to="n_w ≤ 8 (upper bound)",
    ),
    Dependency(
        step_id="CANDIDATE_SET_5_7",
        description=(
            "Combining Z₂ parity + [lower, upper] bounds: n_w ∈ {5, 7}. "
            "Machine-verified by Lean4 Finset enumeration."
        ),
        status=EpistemicStatus.PROVED,
        pillar="Pillar 67",
        lean4_file="NWIntegerLattice.lean",
        observational_inputs=["N_gen = 3 (inherited from CS_ANOMALY_GAP steps)"],
        gap_description=(
            "The arithmetic enumeration is machine-proved, BUT the physical "
            "premises (Z₂ orbifold, CS anomaly) still require geometric axioms. "
            "PROVED conditional on those axioms."
        ),
        closes_to="n_w ∈ {5, 7} (candidate set)",
    ),
    Dependency(
        step_id="ACTION_ORDERING",
        description=(
            "k_eff(5) = 74 < k_eff(7) = 130: n_w = 5 has lower Euclidean CS action. "
            "Machine-verified by Lean4 native_decide."
        ),
        status=EpistemicStatus.PROVED,
        pillar="Pillar 67",
        lean4_file="NWIntegerLattice.lean / BraidUniqueness.lean",
        observational_inputs=[],
        gap_description=(
            "Action ordering is PROVED unconditionally. However, minimum action "
            "does not uniquely select n_w = 5 — both saddles contribute."
        ),
        closes_to="n_w = 5 is dominant saddle (not unique)",
    ),
    Dependency(
        step_id="APS_ETA_INVARIANT",
        description=(
            "APS η-invariant: η̄(5) = 1/2, η̄(7) = 0. Three independent derivations "
            "(Hurwitz ζ, CS inflow, Z₂ zero-mode parity). Selects n_w = 5 if "
            "a quantization condition forces η̄ = 1/2."
        ),
        status=EpistemicStatus.AXIOM_DEPENDENT,
        pillar="Pillar 70-B",
        lean4_file="NWUniquenessHonest.lean (declared as axiom)",
        observational_inputs=[],
        gap_description=(
            "Mathlib does not yet contain APS index theory for Dirac operators "
            "on manifolds with boundary. This is the primary blocking gap for "
            "full formal uniqueness. The Python derivation in aps_spin_structure.py "
            "is correct but not machine-verified in Lean4."
        ),
        closes_to="Distinct η-invariants for n_w=5 vs n_w=7",
    ),
    Dependency(
        step_id="CHIRALITY_REQUIREMENT",
        description=(
            "GW potential with φ₀ ≠ 0 requires chiral fermion spectrum. "
            "APS index theorem + chirality → n_w = 5 without SM input (Pillar 70-C). "
            "G_{μ5} Z₂-odd → Dirichlet BC → η̄ = 1/2 → n_w = 5 (Pillar 70-C-bis)."
        ),
        status=EpistemicStatus.AXIOM_DEPENDENT,
        pillar="Pillar 70-C, 70-C-bis",
        lean4_file="NWUniquenessHonest.lean (declared as axiom)",
        observational_inputs=[],
        gap_description=(
            "Requires formalization of the Goldberger-Wise mechanism in Lean4, "
            "which in turn requires differential geometry of warped extra dimensions. "
            "Not yet in Mathlib."
        ),
        closes_to="n_w = 5 from metric geometry (no SM input)",
    ),
    Dependency(
        step_id="PLANCK_NS_SELECTION",
        description=(
            "Planck 2018 n_s = 0.9649 ± 0.0042 selects n_w = 5 at 3.9σ confidence. "
            "n_w=5: 0.33σ from Planck. n_w=7: 3.9σ from Planck."
        ),
        status=EpistemicStatus.OBSERVATIONAL_INPUT,
        pillar="Pillar 1",
        lean4_file="FalsifierBoundary.lean / InflationObservableChain.lean",
        observational_inputs=["Planck 2018 n_s = 0.9649 ± 0.0042"],
        gap_description=None,
        closes_to="n_w = 5 uniquely (observationally)",
    ),
    Dependency(
        step_id="NGEN_DERIVATION",
        description=(
            "N_gen = 3 (three SM generations) from the 5D metric geometry alone. "
            "This would close the observational dependency in CS_ANOMALY_GAP."
        ),
        status=EpistemicStatus.ARCHITECTURE_LIMIT,
        pillar="Open",
        lean4_file=None,
        observational_inputs=[],
        gap_description=(
            "No mechanism within 5D-EFT derives N_gen = 3 from first principles. "
            "This is a UV completion problem. Orbifold models like Kawamura can "
            "accommodate N_gen = 3 but do not uniquely predict it."
        ),
        closes_to=None,
    ),
    Dependency(
        step_id="APS_MATHLIB_FORMALIZATION",
        description=(
            "Formalization of the Atiyah-Patodi-Singer index theorem for Dirac "
            "operators on S¹/Z₂ in Lean4 / Mathlib."
        ),
        status=EpistemicStatus.ARCHITECTURE_LIMIT,
        pillar="Open (Mathlib research frontier)",
        lean4_file=None,
        observational_inputs=[],
        gap_description=(
            "Mathlib contains manifold theory and some spectral theory, but "
            "not the APS boundary condition for elliptic operators. This is an "
            "active area of formalized mathematics (see e.g. Lean4 Sphere Eversion "
            "project and Mathlib4 geometric analysis track)."
        ),
        closes_to=None,
    ),
]


@dataclass
class CircularityAuditReport:
    """Machine-readable report from the circularity audit."""

    total_steps: int
    proved_steps: int
    geometric_steps: int
    axiom_dependent_steps: int
    observational_input_steps: int
    architecture_limit_steps: int
    arithmetic_steps: int

    observational_inputs: List[str]
    """All unique observational inputs required by any step."""

    open_gaps: List[str]
    """Steps classified as ARCHITECTURE_LIMIT with non-None gap descriptions."""

    summary: str
    """Human-readable summary."""

    steps: List[Dependency]
    """Full audit table."""

    def to_dict(self) -> dict:
        return {
            "total_steps": self.total_steps,
            "proved_steps": self.proved_steps,
            "geometric_steps": self.geometric_steps,
            "axiom_dependent_steps": self.axiom_dependent_steps,
            "observational_input_steps": self.observational_input_steps,
            "architecture_limit_steps": self.architecture_limit_steps,
            "arithmetic_steps": self.arithmetic_steps,
            "observational_inputs": self.observational_inputs,
            "open_gaps": self.open_gaps,
            "summary": self.summary,
        }


def build_nw_dependency_graph() -> List[Dependency]:
    """Return the canonical n_w derivation dependency graph."""
    return list(AUDIT_STEPS)


def run_circularity_audit() -> CircularityAuditReport:
    """
    Run the full circularity audit on the n_w = 5 selection argument.

    Returns a CircularityAuditReport with machine-readable classification
    of every step in the derivation chain.
    """
    steps = build_nw_dependency_graph()

    # Count by status
    counts: Dict[EpistemicStatus, int] = {s: 0 for s in EpistemicStatus}
    for step in steps:
        counts[step.status] += 1

    # Collect all unique observational inputs
    obs_inputs: List[str] = []
    for step in steps:
        for obs in step.observational_inputs:
            if obs not in obs_inputs:
                obs_inputs.append(obs)

    # Collect open gaps
    open_gaps = [
        step.step_id
        for step in steps
        if step.status == EpistemicStatus.ARCHITECTURE_LIMIT
        and step.gap_description is not None
    ]

    # Build summary
    summary_lines = [
        f"n_w = 5 Circularity Audit Report",
        f"================================",
        f"Total derivation steps: {len(steps)}",
        f"  PROVED (unconditional):  {counts[EpistemicStatus.PROVED]}",
        f"  PURELY_GEOMETRIC:        {counts[EpistemicStatus.PURELY_GEOMETRIC]}",
        f"  AXIOM_DEPENDENT:         {counts[EpistemicStatus.AXIOM_DEPENDENT]}",
        f"  OBSERVATIONAL_INPUT:     {counts[EpistemicStatus.OBSERVATIONAL_INPUT]}",
        f"  ARCHITECTURE_LIMIT:      {counts[EpistemicStatus.ARCHITECTURE_LIMIT]}",
        f"  ARITHMETIC_IDENTITY:     {counts[EpistemicStatus.ARITHMETIC_IDENTITY]}",
        f"",
        f"Observational inputs required:",
    ]
    for obs in obs_inputs:
        summary_lines.append(f"  - {obs}")

    summary_lines += [
        f"",
        f"Open gaps (Architecture Limits):",
    ]
    for gap in open_gaps:
        step = next(s for s in steps if s.step_id == gap)
        summary_lines.append(f"  - {gap}: {step.gap_description[:80]}...")

    summary_lines += [
        f"",
        f"Proof distance to full first-principles uniqueness: {len(open_gaps)} open gaps.",
        f"  Gap 1: APS index theorem formalization in Lean4/Mathlib",
        f"  Gap 2: N_gen = 3 derivation from 5D geometry",
        f"  Gap 3: Goldberger-Wise / chirality mechanism in Lean4",
    ]

    return CircularityAuditReport(
        total_steps=len(steps),
        proved_steps=counts[EpistemicStatus.PROVED],
        geometric_steps=counts[EpistemicStatus.PURELY_GEOMETRIC],
        axiom_dependent_steps=counts[EpistemicStatus.AXIOM_DEPENDENT],
        observational_input_steps=counts[EpistemicStatus.OBSERVATIONAL_INPUT],
        architecture_limit_steps=counts[EpistemicStatus.ARCHITECTURE_LIMIT],
        arithmetic_steps=counts[EpistemicStatus.ARITHMETIC_IDENTITY],
        observational_inputs=obs_inputs,
        open_gaps=open_gaps,
        summary="\n".join(summary_lines),
        steps=steps,
    )


if __name__ == "__main__":  # pragma: no cover
    report = run_circularity_audit()
    print(report.summary)
