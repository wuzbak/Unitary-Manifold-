# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Materials Screening Engine — Product 30.

Phase-0/1 consolidated screening tool for article-354 direction #3: pulls
the polaron, metamaterial, and critical-angle formulas out of
`src/materials/froehlich_polaron.py`, `metamaterials.py`, and
`polariton_vortex.py` into one shared, material-parameter-agnostic function
signature, then ranks candidate materials by how far their predicted
Froehlich coupling diverges from the canonical UM value — i.e. which
materials would make the best new falsification targets, before anyone
grows a crystal or runs an experiment.

Epistemic status: this is a screening/ranking tool over already-published
formulas; it validates nothing on its own and makes no claim that any
specific candidate material will show UM-distinctive behavior.
"""

from .screening import MaterialCandidate, screen_candidate, rank_candidates
from .api import API_ENDPOINTS, dispatch_api_request

__all__ = [
    "MaterialCandidate",
    "screen_candidate",
    "rank_candidates",
    "API_ENDPOINTS",
    "dispatch_api_request",
]

__version__ = "1.1.0"
