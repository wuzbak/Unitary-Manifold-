# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Materials Screening Engine — Product 30.

Phase-0/1 consolidated screening tool for article-354 direction #3: pulls
the polaron, metamaterial, and critical-angle formulas out of
`src/materials/froehlich_polaron.py`, `metamaterials.py`, and
`polariton_vortex.py` into one shared, material-parameter-agnostic function
signature, then descriptively ranks supplied Froehlich couplings by their
absolute divergence from the canonical UM value. This ordering does not
establish experimental significance or candidate feasibility.

Epistemic status: this is a screening/ranking tool over already-published
formulas; it validates nothing on its own and makes no claim that any
specific candidate material will show UM-distinctive behavior.
"""

from .screening import MaterialCandidate, screen_candidate, rank_candidates
from .api import API_ENDPOINTS, dispatch_api_request
from .ingestion import screen_file

__all__ = [
    "MaterialCandidate",
    "screen_candidate",
    "rank_candidates",
    "API_ENDPOINTS",
    "dispatch_api_request",
    "screen_file",
]

__version__ = "1.2.0"
