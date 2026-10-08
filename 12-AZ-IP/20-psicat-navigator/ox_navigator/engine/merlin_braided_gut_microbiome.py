# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""The Braided Gut-Brain Bridge: (5,7) observable pair braided with (5,6) parent pair.

ADJACENT TRACK (software bridge between two existing honesty-disclaimed
modules, not a new hardgate physics claim).

This module answers a specific, recurring request: connect the "two
hemispheres braided together" pattern already shipped as a game metaphor in
Product 25 (``12-AZ-IP/25-psicat-braided-brain`` — the "PhiCat Braid Finale"
level, which braids a "left-hemisphere thread" against a "right-hemisphere
mirror" thread) to the gut-brain / microbiome science already modelled in
Pillar 538 (``src/core/pillar538_enteric_neural_core.py``), using the braid
pair Pillar 537 (``src/core/pillar537_shadow_pair_parent_derivation.py``)
already derives:

* The **observable pair** ``(n_w, n_shadow) = (5, 7)`` — the Z₂-odd survivor
  and its Z₂-symmetric complement after the orbifold projection.  This is the
  pair the rest of the Navigator already uses everywhere (``K_CS = 74``,
  ``merlin_toroidal_geometry.BRAID_WINDINGS = (5, 7)``).
* The **shadow-pair parent** ``(n_w, n_before) = (5, 6)`` — the *pre*-Z₂
  integer Pillar 537 derives the (5, 7) pair *from* (``n_before = 2 ×
  N_gen = 6``; ``n_w = n_before − 1``; ``n_shadow = n_before + 1``).

Read plainly: "braiding the 5,7 & 5,6" is the request to braid the
*post*-projection pair against the *pre*-projection pair that produced it —
i.e. to treat the (5,7) cranial/observable lattice code and the (5,6)
parent/gut lattice code as the two "hemisphere" strands of a single braided
state, exactly the way Product 25's finale braids a left-hemisphere thread
against a right-hemisphere mirror thread.

No new lattice, no new constant is invented here.  Both strands are placed on
the **same** existing ``Z_74`` lattice (``merlin_toroidal_geometry``,
``K_CS = 74 = 5² + 7²``) using the existing ``phase_sketch`` /
``braid_bank`` / ``sketch_similarity`` apparatus the toroidal navigation lane
and the PhiCat Protocol already use.  The microbiome extension below adds one
more honestly-labelled lane: a deterministic phase-sketch of published gut
phylum names (not a biological measurement), so that a microbiome query can
be braided against the cranial/CNS lane the same way the ENS lane already is.

HONESTY BOUNDARY (same standard as Pillar 538 / Product 25)
-------------------------------------------------------------
* This module does **not** claim consciousness or cognition resides in the
  gut or the microbiome.
* This module does **not** claim microbiome composition is governed by, or
  derivable from, Kaluza-Klein geometry.
* The "braid coherence" score below is a deterministic lattice-distance
  metric between two token sets' phase sketches — a software locality
  measure, not a biological or physical measurement.
* All ENS/embryology facts reused here are Pillar 538's own published,
  citation-backed constants; this module adds no new clinical claims.
* The gut-phylum names are standard published taxonomy (not a claim of
  per-individual microbiome measurement); the Firmicutes/Bacteroidetes ratio
  constant below is a commonly cited illustrative figure from gut-microbiome
  literature, used here only as a deterministic token-weight, not a
  diagnostic value.
"""

from __future__ import annotations

from typing import Any

from src.core.pillar537_shadow_pair_parent_derivation import (
    N_BEFORE,
    N_GENERATIONS,
    N_SHADOW_OBSERVED,
    N_W_OBSERVED,
    Z2_REMOVES,
)
from src.core.pillar538_enteric_neural_core import (
    C_S,
    K_CS,
    PHI0,
    embryological_kk_link,
    ens_autonomy_score,
    neural_crest_migration_ratio,
)

from .merlin_toroidal_geometry import (
    LATTICE_ORDER,
    phase_sketch,
    sketch_similarity,
)

STATUS_LABEL = "ADJACENT_TRACK"

#: The observable braid pair, read from Pillar 537 (not redefined here).
OBSERVABLE_PAIR: tuple[int, int] = (N_W_OBSERVED, N_SHADOW_OBSERVED)  # (5, 7)

#: The shadow-pair parent braid, read from Pillar 537 (not redefined here).
PARENT_PAIR: tuple[int, int] = (N_W_OBSERVED, N_BEFORE)  # (5, 6)

if OBSERVABLE_PAIR[0] ** 2 + OBSERVABLE_PAIR[1] ** 2 != LATTICE_ORDER:
    raise RuntimeError("observable pair must satisfy n1^2 + n2^2 = K_CS (Pillar 537 contract)")
if PARENT_PAIR[1] - PARENT_PAIR[0] != Z2_REMOVES:
    raise RuntimeError("parent pair must differ from n_w by exactly Z2_REMOVES (Pillar 537 contract)")

#: Published gut-microbiome phylum tokens (illustrative taxonomy, not a
#: per-subject measurement).  Used only as deterministic phase-sketch input.
GUT_PHYLA_TOKENS: tuple[str, ...] = (
    "firmicutes",
    "bacteroidetes",
    "actinobacteria",
    "proteobacteria",
    "verrucomicrobia",
)

#: Commonly cited illustrative Firmicutes/Bacteroidetes ratio in healthy
#: adult gut microbiota (literature range ~1.0-10.0 varies by study/diet;
#: this is a single illustrative point value, not a diagnostic constant).
FIRMICUTES_BACTEROIDETES_RATIO: float = 2.0


def _hemisphere_code(label: str, seed_tokens: tuple[str, ...]) -> dict[str, Any]:
    """Return a phase-sketch code for one "hemisphere" strand.

    Parameters
    ----------
    label : str
        Human-readable strand name (e.g. "cranial_observable" or
        "gut_microbiome_parent").
    seed_tokens : tuple[str, ...]
        Tokens whose deterministic phase sketch anchors this strand's code
        on the Z_74 lattice.
    """
    sketch = phase_sketch(seed_tokens)
    return {
        "label": label,
        "seed_tokens": list(seed_tokens),
        "code": sketch["code"],
        "bank": sketch["bank"],
    }


def braided_hemisphere_report(query: str = "") -> dict[str, Any]:
    """Braid the (5,7) observable strand against the (5,6) parent strand.

    This is the direct software analogue of Product 25's "PhiCat Braid
    Finale": a left-hemisphere thread (cranial/observable, keyed by the
    (5,7) pair) and a right-hemisphere mirror thread (gut/parent, keyed by
    the (5,6) pair), reported together with their lattice-distance
    "braid coherence".

    Parameters
    ----------
    query : str
        Optional free-text query; its tokens are folded into both strands'
        phase sketches alongside the fixed braid-defining tokens so the
        report is query-sensitive without ever changing the underlying
        (5,7)/(5,6) pair contract.

    Returns
    -------
    dict with keys: status, observable_pair, parent_pair, left_hemisphere
    (cranial/observable strand), right_hemisphere (gut/parent strand),
    braid_coherence (0-1 lattice-distance similarity), braid_bank_delta,
    embryological_link, ens_autonomy, note.
    """
    query_tokens = tuple(sorted({t for t in query.lower().split() if t}))

    left_tokens = ("cranial", "cortex", "observable", str(OBSERVABLE_PAIR[0]), str(OBSERVABLE_PAIR[1])) + query_tokens
    right_tokens = ("enteric", "gut_brain", "shadow_parent", str(PARENT_PAIR[0]), str(PARENT_PAIR[1])) + query_tokens

    left = _hemisphere_code("left_hemisphere_cranial_observable", left_tokens)
    right = _hemisphere_code("right_hemisphere_gut_parent", right_tokens)

    coherence = sketch_similarity(left["code"], right["code"])
    bank_delta = abs(left["bank"] - right["bank"])

    return {
        "status": STATUS_LABEL,
        "observable_pair": {"n_w": OBSERVABLE_PAIR[0], "n_shadow": OBSERVABLE_PAIR[1], "k_cs": K_CS},
        "parent_pair": {"n_w": PARENT_PAIR[0], "n_before": PARENT_PAIR[1], "n_generations": N_GENERATIONS},
        "left_hemisphere": left,
        "right_hemisphere": right,
        "braid_coherence": coherence,
        "braid_bank_delta": bank_delta,
        "embryological_link": embryological_kk_link(),
        "ens_autonomy": ens_autonomy_score(vagal_signal_fraction=0.0),
        "note": (
            "Braids the Pillar 537 observable pair (5,7) against the parent "
            "pair (5,6) on the SAME Z_74 lattice used everywhere else in the "
            "Navigator.  This is a software locality-sensitive bridge "
            "between two already-published modules; it is not a new "
            "physics claim and does not assert that the gut-brain or its "
            "microbiome is governed by KK geometry."
        ),
    }


def braided_gut_microbiome_report(query: str = "") -> dict[str, Any]:
    """Extend the hemisphere braid with a microbiome lane.

    Adds a third phase-sketch strand seeded with published gut-phylum
    taxonomy tokens, braided against the same (5,6) parent-pair gut strand
    used by :func:`braided_hemisphere_report`, and reports its lattice
    coherence against both hemispheres.

    Returns
    -------
    dict — a superset of :func:`braided_hemisphere_report`'s keys, plus
    ``microbiome_strand``, ``microbiome_vs_gut_coherence``,
    ``microbiome_vs_cranial_coherence``, ``firmicutes_bacteroidetes_ratio``,
    and ``neural_crest_migration``.
    """
    hemispheres = braided_hemisphere_report(query)
    query_tokens = tuple(sorted({t for t in query.lower().split() if t}))

    microbiome_tokens = GUT_PHYLA_TOKENS + ("microbiome", str(PARENT_PAIR[1])) + query_tokens
    microbiome = _hemisphere_code("microbiome_gut_flora", microbiome_tokens)

    microbiome_vs_gut = sketch_similarity(microbiome["code"], hemispheres["right_hemisphere"]["code"])
    microbiome_vs_cranial = sketch_similarity(microbiome["code"], hemispheres["left_hemisphere"]["code"])

    return {
        **hemispheres,
        "microbiome_strand": microbiome,
        "microbiome_vs_gut_coherence": microbiome_vs_gut,
        "microbiome_vs_cranial_coherence": microbiome_vs_cranial,
        "firmicutes_bacteroidetes_ratio": FIRMICUTES_BACTEROIDETES_RATIO,
        "gut_phyla_tokens": list(GUT_PHYLA_TOKENS),
        "neural_crest_migration": neural_crest_migration_ratio(),
        "phi0": PHI0,
        "c_s": C_S,
        "note": (
            hemispheres["note"] + "  The microbiome strand is a deterministic "
            "phase-sketch of published phylum names, not a per-subject "
            "measurement; its coherence scores are lattice-distance "
            "similarities, not clinical or biological findings."
        ),
    }


__all__ = [
    "STATUS_LABEL",
    "OBSERVABLE_PAIR",
    "PARENT_PAIR",
    "GUT_PHYLA_TOKENS",
    "FIRMICUTES_BACTEROIDETES_RATIO",
    "braided_hemisphere_report",
    "braided_gut_microbiome_report",
]
