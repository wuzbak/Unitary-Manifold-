# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Phi-Debt Early Warning Library — Product 32.

Phase-0 extraction for article-354 direction #5: the φ-debt entropy
accounting in `recycling/entropy_ledger.py` and the resonance-audit tooling
in `src/governance/resonance_audit.py` are, underneath their framework
vocabulary, a general-purpose dynamical-systems monitor: a formalism for
detecting when a bounded-capacity network is accumulating unaddressed
structural debt faster than it discharges it, with an explicit saturation
threshold built in as a warning rail.

This library strips the framework nouns out and exposes a clean,
domain-agnostic API: capacity in, discharge rate in, accumulated debt and
time-to-saturation out.

Epistemic status: this is a general dynamical-systems accounting tool, not
a physics claim. It is validated against one worked example drawn from
`recycling/entropy_ledger.material_entropy_debt` as a sanity check (Phase 0
+ a single internal cross-check); full Phase 1 internal dogfooding across
all five products the article names (EIGE, the Falsification Observatory,
the Geophysical Monitor, the staleness-honesty CI gate, and the Pentad) and
Phase 2 external release are not part of this version.
"""

from .debt_monitor import DebtMonitor, DebtReading, DebtStatus
from .recycling_dogfood import run_recycling_dogfood

__all__ = ["DebtMonitor", "DebtReading", "DebtStatus", "run_recycling_dogfood"]

__version__ = "1.0.0"
