# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 725 — Lean4 Braid Uniqueness Algebraic Certificate

Python-side certificate for BraidUniquenessAlgebraic.lean.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""

# ── Integer anchors ────────────────────────────────────────────────────────────
N_W     = 5
K_CS    = 74

LEAN4_MODULE       = "BraidUniquenessAlgebraic"
LEAN4_NEW_THEOREMS = 15
LEAN4_PREV_TOTAL   = 494     # after WarpFactorUniqueness
LEAN4_NEW_TOTAL    = LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS   # 509


def cs_action_step2(n: int) -> int:
    """Euclidean CS action for step-2 braid pair (n, n+2)."""
    return n**2 + (n + 2)**2


def braid_algebraic_certificate() -> dict:
    """Return the braid algebraic uniqueness certificate."""
    # Physically valid: odd a ≥ 5 (from NWIntegerLattice — n_w ∈ {5,7,...})
    candidates   = [5, 7, 9, 11]
    actions      = {a: cs_action_step2(a) for a in candidates}
    min_action   = min(actions.values())
    min_seed     = min(k for k, v in actions.items() if v == min_action)
    unique_in_70_80 = [a for a in range(1, 20) if 70 <= cs_action_step2(a) <= 80]
    return {
        "pillar":              725,
        "label":               "LEAN4_BRAID_UNIQUENESS_ALGEBRAIC",
        "lean4_module":        LEAN4_MODULE,
        "new_theorems":        LEAN4_NEW_THEOREMS,
        "total_theorems":      LEAN4_NEW_TOTAL,
        "cs_action_57":        cs_action_step2(5),       # 74
        "min_action_seed":     min_seed,                  # 5
        "min_action":          min_action,                # 74
        "unique_seed_in_70_80": unique_in_70_80,          # [5]
        "width4_dominated":    cs_action_step2(5) < cs_action_step2(4),  # but 4 is even
        "action_increasing":   cs_action_step2(5) < cs_action_step2(7),
        "coprime_57":          True,                       # proved by Lean4
        "status":              "LEAN4_PROVED",
    }


def theorem_count() -> int:
    return LEAN4_NEW_TOTAL


def braid_uniqueness_in_window() -> list:
    """Return seeds a with CS action in [70,80]."""
    return [a for a in range(1, 20) if 70 <= cs_action_step2(a) <= 80]


def action_strictly_increasing() -> bool:
    """Return True if CS action is strictly increasing for odd seeds 5,7,9,11."""
    return all(
        cs_action_step2(a) < cs_action_step2(a+2)
        for a in [5, 7, 9]
    )
