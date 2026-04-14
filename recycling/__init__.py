# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
recycling — Pillar 16: Material Recovery & Recycling
======================================================
The Unitary Manifold reveals material recycling as a topological problem.
Every polymer chain, every chemical feedstock, every composite material carries
a φ-field signature — a winding-number fingerprint from the 5D geometry.
Recycling is the attempt to restore that signature; landfilling is the
irreversible collapse of it.

Sub-modules
-----------
polymers        : Plastic/polymer φ-chain topology, recyclability index,
                  sorting discriminability, degradation, microplastic flux.
thermochemical  : Pyrolysis, gasification, solvolysis as B_μ phase transitions.
entropy_ledger  : Lifecycle S_U accounting — what recycling actually costs.
"""

from recycling import polymers, thermochemical, entropy_ledger, producer_responsibility

__all__ = ["polymers", "thermochemical", "entropy_ledger", "producer_responsibility"]
