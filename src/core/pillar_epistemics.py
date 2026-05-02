# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar_epistemics.py
==============================
Pillar 101 — Honest Epistemics Table for Pillars 1–26 + Extensions (§XIV.4).

This module provides the canonical classification of every UM pillar by its
epistemological status.  The four categories are:

  PHYSICS_DERIVATION  — Derived directly and necessarily from the 5D metric
                         G_{AB} or the FTUM fixed-point equation.  No external
                         mechanism or observational anchor required.

  CONDITIONAL_THEOREM — Derived assuming UM geometry with one UM-internal
                         observational anchor (e.g., one Yukawa scale, one
                         compactification parameter).

  FALSIFIABLE_PREDICTION — Makes a specific, testable experimental prediction
                         tied to UM-native constants.  Not yet confirmed.

  FORMAL_ANALOGY      — Mathematical structure borrowed from the UM; not
                         derived from G_{AB}.  Speculative structural
                         correspondence.  Should not be cited as a physical
                         prediction.

Public API
----------
pillar_epistemics_table() → list[dict]
    Return a list of dicts (one per pillar) with fields:
        pillar, domain, module_path, epistemology, analogy_coupling,
        path_to_upgrade, exception_note.

epistemics_summary() → dict
    Return counts by category and a plain-English summary.
"""

from __future__ import annotations

from typing import Any, Dict, List

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "pillar": 101,
    "fingerprint": "(5, 7, 74)",
}

# ---------------------------------------------------------------------------
# Epistemology categories
# ---------------------------------------------------------------------------

PHYSICS_DERIVATION = "PHYSICS_DERIVATION"
CONDITIONAL_THEOREM = "CONDITIONAL_THEOREM"
FALSIFIABLE_PREDICTION = "FALSIFIABLE_PREDICTION"
FORMAL_ANALOGY = "FORMAL_ANALOGY"

VALID_EPISTEMOLOGIES = {
    PHYSICS_DERIVATION,
    CONDITIONAL_THEOREM,
    FALSIFIABLE_PREDICTION,
    FORMAL_ANALOGY,
}


def pillar_epistemics_table() -> List[Dict[str, Any]]:
    """Return the §XIV.4 epistemics table for all UM pillars 1–26 + extensions.

    Returns
    -------
    list[dict]
        Each entry has:
            pillar         : str or int
            domain         : str
            module_path    : str  — relative path to primary source module
            epistemology   : str  — one of VALID_EPISTEMOLOGIES
            analogy_coupling : str — which UM constant links module to 5D geometry
            path_to_upgrade : str — what derivation step would elevate status
            exception_note  : str — special note (e.g., falsification exception)
    """
    return [
        # ── Core KK geometry and FTUM (Pillars 1–5) ──────────────────
        {
            "pillar": "1",
            "domain": "5D Kaluza-Klein metric",
            "module_path": "src/core/metric.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "φ₀, K_CS, M_KK",
            "path_to_upgrade": "N/A — already a physics derivation.",
            "exception_note": "",
        },
        {
            "pillar": "2",
            "domain": "KK field evolution",
            "module_path": "src/core/evolution.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "φ₀, B_μ",
            "path_to_upgrade": "N/A — already a physics derivation.",
            "exception_note": "",
        },
        {
            "pillar": "3",
            "domain": "Holographic boundary",
            "module_path": "src/holography/boundary.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "φ₀, K_CS",
            "path_to_upgrade": "N/A — already a physics derivation.",
            "exception_note": "",
        },
        {
            "pillar": "4",
            "domain": "Holographic entropy-area",
            "module_path": "src/holography/boundary.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": "N/A — already a physics derivation.",
            "exception_note": "",
        },
        {
            "pillar": "5",
            "domain": "FTUM multiverse fixed-point",
            "module_path": "src/multiverse/fixed_point.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": "N/A — already a physics derivation.",
            "exception_note": "",
        },
        # ── Applied pillars (Pillars 6–9) ────────────────────────────
        {
            "pillar": "6",
            "domain": "Braided winding / inflation",
            "module_path": "src/core/braided_winding.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "K_CS, c_s = 12/37",
            "path_to_upgrade": "N/A — CMB predictions derived from 5D geometry.",
            "exception_note": "",
        },
        {
            "pillar": "7",
            "domain": "Non-Gaussianity f_NL",
            "module_path": "src/core/non_gaussianity.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "c_s, K_CS",
            "path_to_upgrade": "N/A — f_NL derived from braid dispersion.",
            "exception_note": "",
        },
        {
            "pillar": "8",
            "domain": "Dark energy / radion",
            "module_path": "src/core/metric.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "M_KK, φ₀",
            "path_to_upgrade": "N/A — ρ_eff = f_braid × M_KK⁴/(16π²) derived.",
            "exception_note": "",
        },
        {
            "pillar": "9",
            "domain": "Consciousness attractor (core)",
            "module_path": "src/consciousness/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "Derive a physical coupling between the FTUM fixed-point φ₀ and "
                "a neural field equation from G_{AB} boundary conditions. "
                "Currently no derivation from 5D metric exists."
            ),
            "exception_note": (
                "The Ξ_c consciousness coupling constant is a formal analogy. "
                "No physical derivation from G_{AB} has been established."
            ),
        },
        # ── Applied pillars 10–26 ─────────────────────────────────────
        {
            "pillar": "10",
            "domain": "Consciousness / brain attractor",
            "module_path": "src/consciousness/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀, Ξ_c",
            "path_to_upgrade": (
                "Derive a physical coupling between φ₀ and a neural field equation "
                "from G_{AB} boundary conditions. No derivation from 5D metric exists."
            ),
            "exception_note": (
                "Ξ_c = 35/74 is a formally defined constant with no derivation "
                "from the 5D metric. The 'brain attractor' model is a mathematical "
                "analogy, not a physics claim."
            ),
        },
        {
            "pillar": "11",
            "domain": "Earth / geology",
            "module_path": "src/earth/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "Derive a physical coupling between the KK radion and geological "
                "cycles from the UM metric. No such derivation exists."
            ),
            "exception_note": (
                "KK radion mapped to geological cycles via dimensionless ratio "
                "comparisons only — formal analogy."
            ),
        },
        {
            "pillar": "12",
            "domain": "Biology / organisms",
            "module_path": "src/biology/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "Establish a physical coupling from the 5D metric to biological "
                "homeostasis. Currently a formal analogy."
            ),
            "exception_note": "φ-homeostasis as organismal metaphor — not a physics claim.",
        },
        {
            "pillar": "13",
            "domain": "Medicine (systemic)",
            "module_path": "src/medicine/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "Derive a physical link from radion dynamics to physiological "
                "parameters. Currently a formal analogy."
            ),
            "exception_note": "φ-homeostasis as health metaphor — not a physics claim.",
        },
        {
            "pillar": "14",
            "domain": "Atomic structure",
            "module_path": "src/atomic_structure/",
            "epistemology": CONDITIONAL_THEOREM,
            "analogy_coupling": "α_em",
            "path_to_upgrade": (
                "α_em is derived from UM (φ₀⁻²). Atomic level spacings reproduced "
                "to < 1% using this α. Upgrade to full PHYSICS_DERIVATION by "
                "deriving the QED coupling from the 5D gauge field without "
                "referencing PDG α_em directly."
            ),
            "exception_note": (
                "Fine structure constant α is UM-derived. Hydrogen spectrum is "
                "reproduced to < 1%. This is the tightest connection to physics "
                "among Pillars 10–26 (excluding Pillar 15)."
            ),
        },
        {
            "pillar": "15",
            "domain": "Cold fusion (Gamow enhancement)",
            "module_path": "src/cold_fusion/",
            "epistemology": FALSIFIABLE_PREDICTION,
            "analogy_coupling": "φ₀, B_μ, M_KK",
            "path_to_upgrade": (
                "Already a falsifiable prediction. Upgrade to CONDITIONAL_THEOREM "
                "by deriving the coherence volume N_coh from first-principles "
                "lattice dynamics."
            ),
            "exception_note": (
                "Exception: Pillar 15 provides a genuine COP > 1 falsification "
                "criterion (calorimetry test F1). B_μ mass from KK spectrum → "
                "phonon routing > 99% → COP > 1. See cold_fusion_physics_link()."
            ),
        },
        {
            "pillar": "15-B",
            "domain": "Cold fusion lattice dynamics / phonon-radion bridge",
            "module_path": "src/physics/lattice_dynamics.py",
            "epistemology": FALSIFIABLE_PREDICTION,
            "analogy_coupling": "B_μ, c_s, M_KK",
            "path_to_upgrade": (
                "Derive the phonon-radion coupling from the 5D metric G_{AB} "
                "without reference to lattice models. Difficulty: LONG."
            ),
            "exception_note": (
                "Exception: Pillar 15-B provides the phonon-radion bridge used "
                "in the COP prediction. The B_μ-phonon coupling is tied to the "
                "KK spectrum (Pillar 1). See cold_fusion_physics_link()."
            ),
        },
        {
            "pillar": "15-F",
            "domain": "Cold fusion falsification protocol",
            "module_path": "src/cold_fusion/falsification_protocol.py",
            "epistemology": FALSIFIABLE_PREDICTION,
            "analogy_coupling": "φ₀, M_KK",
            "path_to_upgrade": "N/A — falsification protocol is the correct status.",
            "exception_note": (
                "Explicit experimental criteria F1 (calorimetry), F2 (particle "
                "emission), F3 (DFT screening). These are the hardest constraints "
                "on the cold fusion prediction."
            ),
        },
        {
            "pillar": "16",
            "domain": "Recycling / φ-debt entropy",
            "module_path": "recycling/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "Derive entropy accounting from the UM 5D metric rather than "
                "using φ as a formal entropy variable."
            ),
            "exception_note": (
                "φ-debt recycling is a formal analogy for circular economy "
                "accounting. Not a physics claim."
            ),
        },
        {
            "pillar": "17",
            "domain": "Medicine / diagnosis",
            "module_path": "src/medicine/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "No derivation from G_{AB} exists. Upgrade requires establishing "
                "a physical link from radion dynamics to physiological parameters."
            ),
            "exception_note": "Formal analogy — not a physics claim.",
        },
        {
            "pillar": "18",
            "domain": "Justice / law",
            "module_path": "src/justice/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "Ξ_c",
            "path_to_upgrade": (
                "No derivation from G_{AB} exists. The φ-equity metaphor is "
                "a formal analogy for fairness modelling."
            ),
            "exception_note": "Formal analogy — not a physics claim.",
        },
        {
            "pillar": "19",
            "domain": "Governance / democracy",
            "module_path": "src/governance/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "Ξ_c",
            "path_to_upgrade": (
                "No derivation from G_{AB} exists. CS stability gap as governance "
                "metaphor is a formal analogy."
            ),
            "exception_note": "Formal analogy — not a physics claim.",
        },
        {
            "pillar": "20",
            "domain": "Neuroscience",
            "module_path": "src/neuroscience/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "No derivation from G_{AB} exists. Neurons as φ-networks is "
                "a formal analogy."
            ),
            "exception_note": "Formal analogy — not a physics claim.",
        },
        {
            "pillar": "21",
            "domain": "Ecology",
            "module_path": "src/ecology/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "No derivation from G_{AB} exists. Ecosystems as φ-homeostasis "
                "is a formal analogy."
            ),
            "exception_note": "Formal analogy — not a physics claim.",
        },
        {
            "pillar": "22",
            "domain": "Climate science",
            "module_path": "src/climate/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "No derivation from G_{AB} exists. Carbon cycle as radion feedback "
                "is a formal analogy."
            ),
            "exception_note": "Formal analogy — not a physics claim.",
        },
        {
            "pillar": "23",
            "domain": "Marine biology",
            "module_path": "src/marine/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "No derivation from G_{AB} exists. Ocean dynamics as φ-attractor "
                "is a formal analogy."
            ),
            "exception_note": "Formal analogy — not a physics claim.",
        },
        {
            "pillar": "24",
            "domain": "Psychology",
            "module_path": "src/psychology/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "Ξ_c",
            "path_to_upgrade": (
                "No derivation from G_{AB} exists. Cognition as φ-network "
                "is a formal analogy."
            ),
            "exception_note": "Formal analogy — not a physics claim.",
        },
        {
            "pillar": "25",
            "domain": "Genetics / genomics",
            "module_path": "src/genetics/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "No derivation from G_{AB} exists. Gene expression as winding-mode "
                "hierarchy is a formal analogy."
            ),
            "exception_note": "Formal analogy — not a physics claim.",
        },
        {
            "pillar": "26",
            "domain": "Materials science",
            "module_path": "src/materials/",
            "epistemology": FORMAL_ANALOGY,
            "analogy_coupling": "K_CS",
            "path_to_upgrade": (
                "Condensed matter KK analogy is the closest to physics among Pillars 10–26. "
                "Upgrade by deriving effective mass tensor from KK compactification "
                "rather than using K_CS as a numerical coincidence."
            ),
            "exception_note": (
                "Closest to physics among Pillars 10–26 (excluding 14/15). "
                "K_CS = 74 = 5² + 7² appears in condensed matter band structure "
                "comparisons, but no first-principles derivation from G_{AB} exists."
            ),
        },
        # ── Extension pillars ─────────────────────────────────────────
        {
            "pillar": "70-D",
            "domain": "n_w=5 pure uniqueness theorem",
            "module_path": "src/core/nw5_pure_theorem.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "K_CS = 74, η̄",
            "path_to_upgrade": "N/A — pure theorem from 5D geometry.",
            "exception_note": (
                "SU(5) derivation from 5D geometry is genuine. "
                "SU(5) → G_SM breaking uses Kawamura (2001) — see §XIV.2."
            ),
        },
        {
            "pillar": "97",
            "domain": "GW Yukawa / 5D Yukawa universality",
            "module_path": "src/core/sm_free_parameters.py",
            "epistemology": CONDITIONAL_THEOREM,
            "analogy_coupling": "φ₀",
            "path_to_upgrade": (
                "Ŷ₅=1 is a GW vacuum conjecture, not yet derived from boundary "
                "conditions. Derive Ŷ₅ from the 5D action to make this a "
                "PHYSICS_DERIVATION."
            ),
            "exception_note": "",
        },
        {
            "pillar": "100",
            "domain": "ADM Foundation / arrow of time",
            "module_path": "src/core/adm_decomposition.py",
            "epistemology": PHYSICS_DERIVATION,
            "analogy_coupling": "φ₀, K_ij",
            "path_to_upgrade": "N/A — standard GR + NEC applied to UM matter sector.",
            "exception_note": "ADM lapse deviation < 1% (see §XIV.3, adm_lapse_deviation()).",
        },
    ]


def epistemics_summary() -> Dict[str, Any]:
    """Return counts by epistemology category and a plain-English summary.

    Returns
    -------
    dict with keys:
        counts_by_category : dict[str, int]
        pillar_lists       : dict[str, list[str]]
        summary            : str
        section            : str
    """
    table = pillar_epistemics_table()
    from collections import Counter
    counts = Counter(entry["epistemology"] for entry in table)
    pillar_lists: Dict[str, list] = {ep: [] for ep in VALID_EPISTEMOLOGIES}
    for entry in table:
        pillar_lists[entry["epistemology"]].append(str(entry["pillar"]))

    total = len(table)
    n_phys = counts[PHYSICS_DERIVATION]
    n_cond = counts[CONDITIONAL_THEOREM]
    n_fals = counts[FALSIFIABLE_PREDICTION]
    n_anal = counts[FORMAL_ANALOGY]

    return {
        "total_pillars": total,
        "counts_by_category": dict(counts),
        "pillar_lists": pillar_lists,
        "summary": (
            f"Of {total} pillars catalogued: "
            f"{n_phys} PHYSICS_DERIVATION (derived from 5D metric G_{{AB}}), "
            f"{n_cond} CONDITIONAL_THEOREM (one UM-internal anchor needed), "
            f"{n_fals} FALSIFIABLE_PREDICTION (testable but unconfirmed), "
            f"{n_anal} FORMAL_ANALOGY (speculative structural correspondence). "
            "Formal analogies are not errors — they are an honest label for "
            "speculative applications that may guide future research. "
            "Only Pillars 14, 15, and 15-B have genuine derivation or "
            "falsifiability status in the range 10–26."
        ),
        "section": "§XIV.4",
    }
