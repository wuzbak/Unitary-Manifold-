# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Calorimetry Console — Product 28.

Phase-0 instrumentation software for the cold-fusion falsification protocol
described in `src/cold_fusion/` and `src/physics/lattice_dynamics.py`.

Epistemic status: this product does not claim cold fusion occurs. It builds
the run-sheet and live-tracking software that would let an external lab
actually test the module's own pre-registered COP > 1.01 prediction at a
Pd-D loading ratio near x = 0.875. See `src/cold_fusion/falsification_protocol.py`
and `FALLIBILITY.md` for the underlying physics caveats (25-order-of-magnitude
vertex gap, not yet bridged).
"""

from .run_sheet import RunSheet, generate_run_sheet
from .cop_tracker import COPTracker, COPReading

__all__ = [
    "RunSheet",
    "generate_run_sheet",
    "COPTracker",
    "COPReading",
]

__version__ = "1.0.0"
