# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
holon-zero — The Ground State Engine of the Unitary Manifold

The zero-point before the first pillar.  The silence that contains every sound.
The single integer n_w = 5 before it knew what it would become.

Quick start::

    from holon_zero.holon_zero_engine import HolonZeroEngine

    engine = HolonZeroEngine()
    report = engine.compute_all()

    # Explore the holarchy: 13 levels from void to self-reference
    for level in engine.holarchy():
        print(f"Level {level.index}: {level.name}")

    # Trace any observable back to the seed
    chain = engine.emergence_chain("consciousness")
    for step in chain.steps:
        print(f"  {step.from_quantity}  →  {step.to_quantity}")

    # The self-describing loop
    res = engine.anthropic_resonance()
    print(f"Loop closed: {res.is_closed}")   # True
    print(res.insight)

    # The full reflection
    print(report.summary())

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74, 0)",  # braid triad + the zero-point
}

from .holon_zero_engine import (
    HolonZeroEngine,
    HolonZeroReport,
    HolarchyLevel,
    EmergenceChain,
    EmergenceStep,
    ObserverCondition,
    ObserverConditionsReport,
    CoEmergenceReport,
    AnthropicResonanceReport,
    ZeroPointReport,
    # Seed constants
    N_W,
    N_2,
    K_CS,
    C_S,
    XI_C,
)

__all__ = [
    "HolonZeroEngine",
    "HolonZeroReport",
    "HolarchyLevel",
    "EmergenceChain",
    "EmergenceStep",
    "ObserverCondition",
    "ObserverConditionsReport",
    "CoEmergenceReport",
    "AnthropicResonanceReport",
    "ZeroPointReport",
    "N_W",
    "N_2",
    "K_CS",
    "C_S",
    "XI_C",
]
