# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 279 — n_w Uniqueness Parity / Handedness Obstruction (Planck-free).

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

`src/core/pillar_nw_uniqueness_hardening.py` narrows the winding number
n_w to {5, 7} from Z₂ orbifold parity + the three-generation stability
window + the sum-of-squares anchor K_CS = 74 = 5² + 7², then breaks the
{5,7} tie via the Planck nₛ χ² preference.  This module records the
explicit *Planck-free* parity / handedness obstruction that prefers
n_w = 5 over n_w = 7 *without* invoking Planck data, and quantifies
honestly what remains to make the argument fully first-principles.

──────────────────────────────────────────────────────────────────────────────
Mathematical content
──────────────────────────────────────────────────────────────────────────────

The braid resonance constraint K_CS = n_w² + m_w² = 74 has the unique
positive-integer sum-of-squares decomposition

    74 = 5² + 7² = 7² + 5²                (unordered solution {5, 7})

Two ordered pairs (n_w, m_w) ∈ {(5, 7), (7, 5)} satisfy this.  The
question is whether the two ordered pairs are physically distinguishable.

OBSERVATION 279.1 (chirality).  The torus link T(p, q) and T(q, p) are
*ambient isotopic* as unoriented links but have opposite handedness as
oriented torus links once a spacetime orientation is fixed.  Equivalently,
the braided-winding pair (n_w, m_w) and its transposition (m_w, n_w) are
related by the parity operation P on the T² compactification.

OBSERVATION 279.2 (CP-fixed orientation).  The SM exhibits observed CP
violation (PDG: δ_CKM ≈ 1.196 rad ≠ 0), which fixes a definite handedness
on the 5D KK background through the Wess–Zumino term coupling
(see `src/core/strong_cp_pq_z2_closure.py` for the Z₂-orbifold
realization).  Consequently the *ordered* braid pair is uniquely
determined by the SM-fixed chirality.

OBSERVATION 279.3 (short/long convention).  The geometric prescription
assigns the *primary* winding number n_w to the *short* cycle of the
modular T² (smaller fundamental period R_short), and the *secondary*
m_w to the *long* cycle (R_long > R_short).  This convention forces

    n_w ≤ m_w                          (Convention 279.3)

For the {5, 7} sum-of-squares decomposition, Convention 279.3 immediately
selects (n_w, m_w) = (5, 7), i.e. n_w = 5.

──────────────────────────────────────────────────────────────────────────────
Honest scope of this obstruction
──────────────────────────────────────────────────────────────────────────────

The argument above does *not* constitute a complete first-principles
exclusion of n_w = 7.  It is a *conditional* exclusion: given the
short/long cycle convention and the CP-fixed chirality, n_w = 5 is
selected.  The residual open question — "*why* is n_w assigned to the
short cycle and not the long cycle" — is recorded explicitly and is the
remaining piece of work that would close the {5,7} ambiguity from first
principles alone.

The plan §C.6 acknowledged this: "If the proof fails, that itself is a
rigorous outcome documented in FALLIBILITY".  This module records the
honest outcome: **Planck-free selection of n_w = 5 is achieved subject
to one named convention**, narrowing FALLIBILITY Admission #3 from a
two-step ambiguity {5,7}-then-χ² to a single-convention obstruction.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "K_CS",
    "FINALIST_PAIR",
    "ORDERED_BRAID_PAIR_SELECTED",
    "separation_guard",
    "sum_of_squares_decompositions",
    "is_unique_unordered_decomposition_of_K_CS",
    "ordered_pair_chirality_label",
    "selected_ordered_pair_from_convention",
    "planck_free_obstruction_certificate",
    "fallibility_admission3_summary",
    "remaining_first_principles_residual",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 279
PILLAR_TITLE: str = "n_w Uniqueness Parity / Handedness Obstruction (Planck-free)"

K_CS: int = 74
FINALIST_PAIR: Tuple[int, int] = (5, 7)
ORDERED_BRAID_PAIR_SELECTED: Tuple[int, int] = (5, 7)


def separation_guard() -> Dict[str, object]:
    """Explicit non-hardgate separation guard."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "complements_existing_chi2_selection": True,
    }


# ---------------------------------------------------------------------------
# Sum-of-squares enumeration
# ---------------------------------------------------------------------------

def sum_of_squares_decompositions(n: int) -> List[Tuple[int, int]]:
    """Return all *ordered* (a, b) with a, b ≥ 1 and a² + b² = n.

    Includes both (a, b) and (b, a) for a ≠ b.
    """
    if n < 2:
        raise ValueError("n must be >= 2")
    out: List[Tuple[int, int]] = []
    a = 1
    while a * a < n:
        b2 = n - a * a
        b = int(round(b2 ** 0.5))
        if b >= 1 and b * b == b2:
            out.append((a, b))
        a += 1
    return out


def is_unique_unordered_decomposition_of_K_CS() -> bool:
    """Verify that K_CS = 74 has a unique unordered positive sum-of-squares pair."""
    ordered = sum_of_squares_decompositions(K_CS)
    unordered = {tuple(sorted(p)) for p in ordered}
    return len(unordered) == 1


# ---------------------------------------------------------------------------
# Chirality / convention obstruction
# ---------------------------------------------------------------------------

def ordered_pair_chirality_label(pair: Tuple[int, int]) -> str:
    """Return the chirality label for an ordered braid pair (p, q)."""
    p, q = pair
    if p == q:
        return "CHIRAL_NEUTRAL"
    if p < q:
        return "LEFT_HANDED_SHORT_CYCLE_PRIMARY"
    return "RIGHT_HANDED_LONG_CYCLE_PRIMARY"


def selected_ordered_pair_from_convention(
    finalists: Tuple[int, int] = FINALIST_PAIR,
) -> Tuple[int, int]:
    """Return the selected ordered pair under Convention 279.3 (n_w ≤ m_w)."""
    a, b = finalists
    return (min(a, b), max(a, b))


# ---------------------------------------------------------------------------
# Certificate and summary
# ---------------------------------------------------------------------------

def planck_free_obstruction_certificate() -> Dict[str, object]:
    """Return the Planck-free parity/handedness obstruction certificate."""
    ordered_decomps = sum_of_squares_decompositions(K_CS)
    selected = selected_ordered_pair_from_convention()
    selected_label = ordered_pair_chirality_label(selected)
    rejected = (selected[1], selected[0])
    rejected_label = ordered_pair_chirality_label(rejected)
    obstruction_complete = bool(
        is_unique_unordered_decomposition_of_K_CS()
        and selected == ORDERED_BRAID_PAIR_SELECTED
    )
    return {
        "K_CS": K_CS,
        "ordered_sum_of_squares_decompositions": ordered_decomps,
        "unique_unordered_pair": tuple(sorted(FINALIST_PAIR)),
        "convention_279_3": "n_w assigned to short cycle ⇒ n_w ≤ m_w",
        "selected_ordered_pair": selected,
        "selected_chirality_label": selected_label,
        "rejected_ordered_pair": rejected,
        "rejected_chirality_label": rejected_label,
        "planck_data_used": False,
        "obstruction_complete_under_named_convention": obstruction_complete,
    }


def remaining_first_principles_residual() -> Dict[str, str]:
    """Name the residual first-principles step still required for full closure."""
    return {
        "id": "SHORT_LONG_CYCLE_ASSIGNMENT_DERIVATION",
        "title": (
            "Derive the short/long-cycle convention (Convention 279.3) from "
            "the radion stabilization mechanism rather than asserting it."
        ),
        "blocker": (
            "Pillars 91 / 99-B / 165 fix the radion VEV but do not yet "
            "*derive* the cycle ordering R_short < R_long that anchors "
            "Convention 279.3."
        ),
    }


def fallibility_admission3_summary() -> Dict[str, object]:
    """Return the structured Admission #3 rewrite payload."""
    cert = planck_free_obstruction_certificate()
    return {
        "headline": (
            "n_w ∈ {5, 7} from Z₂ orbifold + 3-generation window + "
            "K_CS = 74 sum-of-squares; **Planck-free obstruction** "
            "(Pillar 279) selects (n_w, m_w) = (5, 7) under "
            "Convention 279.3 (n_w on short cycle). Remaining residual: "
            "derive Convention 279.3 from the radion stabilization."
        ),
        "selected_ordered_pair": cert["selected_ordered_pair"],
        "planck_data_used": cert["planck_data_used"],
        "obstruction_complete_under_named_convention": cert[
            "obstruction_complete_under_named_convention"
        ],
        "remaining_residual": remaining_first_principles_residual(),
    }


def nw_obstruction_report() -> Dict[str, object]:
    """Top-level report packet."""
    cert = planck_free_obstruction_certificate()
    summary = fallibility_admission3_summary()
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "certificate": cert,
        "fallibility_admission3_summary": summary,
        "honest_note": (
            "This module supplies a Planck-free *conditional* selection of "
            "n_w = 5: given Convention 279.3 (short/long cycle ordering), "
            "the (5, 7) ordered pair is forced. The unconditional first-"
            "principles exclusion of n_w = 7 still requires deriving the "
            "cycle ordering itself."
        ),
        "separation_guard": separation_guard(),
    }
