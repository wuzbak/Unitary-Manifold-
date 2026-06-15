# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Pillar 391 — Signal-vs-Noise Filter
🔵 ADJACENT TRACK (non-hardgate; governance engineering)

Implements a repository-wide triage system that classifies every tracked item
(predictions, gaps, tensions, modules, outreach artefacts) into one of three
categories:

  ACTIONABLE_SIGNAL — directly tied to an active falsifier lane, an open
                       observational tension at ≥2σ, or a preregistered
                       decision window (DESI DR3, SO DR1, JUNO, LiteBIRD).
                       Sprint focus must be allocated here.

  MONITOR_ONLY      — consistent with current data, no action required now,
                       but must be re-evaluated when the relevant experiment
                       publishes. Do not invest sprint capacity beyond a brief
                       status check.

  ARCHIVAL_NOISE    — speculative extensions with no open falsifier, no active
                       tension, and no decision window within five years. Archive
                       or demote to reduce sprint cognitive load.

The filter is intentionally conservative: when classification is ambiguous,
items are promoted to ACTIONABLE_SIGNAL rather than demoted.

Epistemic status: GOVERNANCE_ENGINEERING — classification rules are based on
the repository's explicit falsification infrastructure; does not make physics
claims beyond what is already recorded in OBSERVATION_TRACKER.md.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ──────────────────────────────────────────────────────────────────────────────
# Triage taxonomy
# ──────────────────────────────────────────────────────────────────────────────

class TriageClass(str, Enum):
    ACTIONABLE_SIGNAL = "ACTIONABLE_SIGNAL"
    MONITOR_ONLY      = "MONITOR_ONLY"
    ARCHIVAL_NOISE    = "ARCHIVAL_NOISE"


class ItemType(str, Enum):
    PREDICTION      = "PREDICTION"        # A numerical observable prediction.
    GAP             = "GAP"               # A documented open gap in the framework.
    TENSION         = "TENSION"           # An active data tension (≥2σ).
    MODULE          = "MODULE"            # A Python source module.
    OUTREACH        = "OUTREACH"          # A Substack / outreach artefact.
    GOVERNANCE      = "GOVERNANCE"        # A governance / HILS document.
    ADJACENT_TRACK  = "ADJACENT_TRACK"   # A non-hardgate pillar or module.


# ──────────────────────────────────────────────────────────────────────────────
# Active decision windows (canonical list; update each sprint)
# ──────────────────────────────────────────────────────────────────────────────

ACTIVE_DECISION_WINDOWS = [
    "DESI_DR3",         # ~2027  wₐ = 0 vs wₐ ≠ 0 at ≥3σ
    "SO_DR1",           # ~2027  r = 0.0315 confirmation / falsification
    "JUNO",             # ~2027  Δm²₃₁ = 2.452×10⁻³ eV² at JUNO 0.5%
    "HYPER_K_2028",     # ~2028  Δm²₃₁ cross-check
    "SPHEREX",          # ~2026-2030  f_NL ∈ [−3, 0]
    "CMB_S4",           # ~2030  r, β joint
    "LITEBIRD",         # ~2032  β ∈ {0.273°, 0.331°} primary falsifier
    "LISA",             # ~2035  Ω_GW ~ 10⁻¹⁵
    "HYPER_K_2034",     # ~2034  proton decay τ ≈ 5×10³⁴ yr
]

# Active HIGH_TENSION signals (≥2σ from UM prediction)
ACTIVE_HIGH_TENSION_SIGNALS = [
    "DESI_WA",          # wₐ ≠ 0, 2.75σ combined
    "ACT_DR6_R",        # r < 0.016 (95%CL) vs UM r = 0.0315
]


# ──────────────────────────────────────────────────────────────────────────────
# Item data model
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class RepositoryItem:
    """A tracked item in the repository requiring triage classification."""

    name: str
    item_type: ItemType
    description: str = ""

    # Falsifier / decision-window linkage
    linked_falsifier: Optional[str] = None     # e.g. "LITEBIRD", "DESI_DR3"
    linked_tension: Optional[str] = None       # e.g. "DESI_WA", "ACT_DR6_R"
    decision_window_years: Optional[int] = None  # Expected data year (None = no window)

    # Current status indicators
    is_consistent_with_data: bool = True
    has_preregistered_routing: bool = False
    last_updated_sprint: str = ""

    # Noise indicators
    is_speculative_extension: bool = False     # No derivation from core geometry
    has_no_near_term_test: bool = False        # Nothing testable within 10 years
    is_superseded: bool = False                # A newer module replaces this one


# ──────────────────────────────────────────────────────────────────────────────
# Triage classifier
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class TriageResult:
    item: RepositoryItem
    classification: TriageClass
    reasons: List[str] = field(default_factory=list)
    recommended_action: str = ""


def classify_item(item: RepositoryItem) -> TriageResult:
    """Classify a single repository item.

    The filter is conservative: ambiguous cases resolve to ACTIONABLE_SIGNAL.
    """
    reasons: List[str] = []
    action: str = ""

    # ── ARCHIVAL_NOISE conditions ───────────────────────────────────────────
    if item.is_superseded:
        reasons.append("Item is superseded by a newer module")
        action = "Archive or remove; link to superseding module in docstring"
        return TriageResult(item, TriageClass.ARCHIVAL_NOISE, reasons, action)

    if (
        item.is_speculative_extension
        and item.has_no_near_term_test
        and item.linked_falsifier is None
        and item.linked_tension is None
    ):
        reasons.append("Speculative extension with no near-term test and no falsifier link")
        action = (
            "Demote to archival; label clearly as SPECULATIVE_EXTENSION; "
            "do not invest sprint capacity until a testable prediction is identified"
        )
        return TriageResult(item, TriageClass.ARCHIVAL_NOISE, reasons, action)

    # ── ACTIONABLE_SIGNAL conditions ────────────────────────────────────────
    if item.linked_tension and item.linked_tension in ACTIVE_HIGH_TENSION_SIGNALS:
        reasons.append(f"Linked to active HIGH_TENSION signal: {item.linked_tension}")
        action = (
            "Ensure routing protocol is preregistered; run rehearsal drill; "
            "update routing module within 30 days of new data"
        )
        return TriageResult(item, TriageClass.ACTIONABLE_SIGNAL, reasons, action)

    if item.linked_falsifier and item.linked_falsifier in ACTIVE_DECISION_WINDOWS:
        reasons.append(f"Linked to active decision window: {item.linked_falsifier}")
        if item.decision_window_years and item.decision_window_years <= 2028:
            reasons.append(f"Decision window expected by ~{item.decision_window_years}")
            action = (
                "Verify routing protocol is preregistered; "
                "ensure same-day update script exists and is tested"
            )
        else:
            action = (
                "Verify routing protocol is preregistered; "
                "schedule rehearsal drill within 12 months of expected publication"
            )
        return TriageResult(item, TriageClass.ACTIONABLE_SIGNAL, reasons, action)

    if not item.has_preregistered_routing and item.linked_falsifier:
        reasons.append("Has falsifier link but routing is not yet preregistered")
        action = "Preregister routing protocol; add to decision readiness package"
        return TriageResult(item, TriageClass.ACTIONABLE_SIGNAL, reasons, action)

    # ── MONITOR_ONLY — consistent, no immediate action ──────────────────────
    if item.is_consistent_with_data:
        reasons.append("Consistent with current data; no action required in this sprint")
        action = "Re-evaluate on next PDG update or when relevant experiment publishes"
        return TriageResult(item, TriageClass.MONITOR_ONLY, reasons, action)

    # Default: conservative escalation to ACTIONABLE_SIGNAL
    reasons.append("Classification ambiguous; escalating conservatively to ACTIONABLE_SIGNAL")
    action = "Review item status against current experimental landscape"
    return TriageResult(item, TriageClass.ACTIONABLE_SIGNAL, reasons, action)


# ──────────────────────────────────────────────────────────────────────────────
# Batch triage
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class TriageReport:
    """Full repository triage report."""

    results: List[TriageResult]

    @property
    def actionable(self) -> List[TriageResult]:
        return [r for r in self.results if r.classification == TriageClass.ACTIONABLE_SIGNAL]

    @property
    def monitor_only(self) -> List[TriageResult]:
        return [r for r in self.results if r.classification == TriageClass.MONITOR_ONLY]

    @property
    def archival_noise(self) -> List[TriageResult]:
        return [r for r in self.results if r.classification == TriageClass.ARCHIVAL_NOISE]

    def summary(self) -> dict:
        return {
            "total_items": len(self.results),
            "actionable_signal": len(self.actionable),
            "monitor_only": len(self.monitor_only),
            "archival_noise": len(self.archival_noise),
            "signal_fraction": (
                len(self.actionable) / len(self.results) if self.results else 0.0
            ),
        }

    def noise_reduction_recommendations(self) -> List[str]:
        """Return a list of recommended actions to reduce archival noise."""
        recs: List[str] = []
        for result in self.archival_noise:
            recs.append(f"[{result.item.name}] {result.recommended_action}")
        return recs


def triage_items(items: List[RepositoryItem]) -> TriageReport:
    """Run the signal-vs-noise filter on a list of items."""
    results = [classify_item(item) for item in items]
    return TriageReport(results=results)


# ──────────────────────────────────────────────────────────────────────────────
# Canonical item registry (current v12.8 state)
# ──────────────────────────────────────────────────────────────────────────────

def get_canonical_item_registry() -> List[RepositoryItem]:
    """Return the canonical list of tracked items for v12.8 triage.

    This registry is the official signal-vs-noise map for the v12.8 sprint.
    Items in this list are explicitly classified; any new item added to the
    repository must be added here before it can be considered in scope.
    """
    return [
        # ── ACTIVE TENSIONS (highest priority) ──────────────────────────────
        RepositoryItem(
            name="DESI_WA_TENSION",
            item_type=ItemType.TENSION,
            description="wₐ = 0 (frozen radion) vs DESI DR2 combined 2.75σ",
            linked_falsifier="DESI_DR3",
            linked_tension="DESI_WA",
            decision_window_years=2027,
            is_consistent_with_data=False,
            has_preregistered_routing=True,
            last_updated_sprint="v12.5",
        ),
        RepositoryItem(
            name="ACT_DR6_R_TENSION",
            item_type=ItemType.TENSION,
            description="r = 0.0315 vs ACT DR6 r < 0.016 (95%CL); IRREDUCIBLE_IN_BRAIDED_5D_EFT",
            linked_falsifier="SO_DR1",
            linked_tension="ACT_DR6_R",
            decision_window_years=2027,
            is_consistent_with_data=False,
            has_preregistered_routing=True,
            last_updated_sprint="v11.13",
        ),
        # ── NEAR-TERM DECISION WINDOWS (≤ 2028) ─────────────────────────────
        RepositoryItem(
            name="JUNO_DM31_PREDICTION",
            item_type=ItemType.PREDICTION,
            description="Δm²₃₁ = 2.452×10⁻³ eV² at 0.004% residual (NLO, P274)",
            linked_falsifier="JUNO",
            decision_window_years=2027,
            is_consistent_with_data=True,
            has_preregistered_routing=True,
            last_updated_sprint="v12.5",
        ),
        RepositoryItem(
            name="SO_DR1_R_PREDICTION",
            item_type=ItemType.PREDICTION,
            description="r = 0.0315; confirmation at ~5.25σ expected at SO DR1",
            linked_falsifier="SO_DR1",
            decision_window_years=2027,
            is_consistent_with_data=True,
            has_preregistered_routing=True,
            last_updated_sprint="v12.5",
        ),
        RepositoryItem(
            name="SPHEREX_FNL_PREDICTION",
            item_type=ItemType.PREDICTION,
            description="f_NL^equil ∈ [−3, 0]; NEW PREDICTION Pillar 375",
            linked_falsifier="SPHEREX",
            decision_window_years=2028,
            is_consistent_with_data=True,
            has_preregistered_routing=True,
            last_updated_sprint="v12.5",
        ),
        RepositoryItem(
            name="DESI_DR3_ROUTING",
            item_type=ItemType.PREDICTION,
            description="7-scenario DR3 routing matrix; canonical w₀=−1",
            linked_falsifier="DESI_DR3",
            decision_window_years=2027,
            is_consistent_with_data=True,
            has_preregistered_routing=True,
            last_updated_sprint="v12.5",
        ),
        # ── PRIMARY FALSIFIER (long-range but highest stakes) ────────────────
        RepositoryItem(
            name="LITEBIRD_BIREFRINGENCE",
            item_type=ItemType.PREDICTION,
            description="β ∈ {0.273°, 0.331°} ± 0.007°; primary falsifier",
            linked_falsifier="LITEBIRD",
            decision_window_years=2032,
            is_consistent_with_data=True,
            has_preregistered_routing=True,
            last_updated_sprint="v12.7",
        ),
        # ── SECONDARY PREDICTIONS (monitor-only) ────────────────────────────
        RepositoryItem(
            name="CMB_NS_PREDICTION",
            item_type=ItemType.PREDICTION,
            description="nₛ = 0.9635; 0.33σ from Planck; CONSISTENT",
            linked_falsifier="CMB_S4",
            decision_window_years=2030,
            is_consistent_with_data=True,
            has_preregistered_routing=True,
            last_updated_sprint="v12.7",
        ),
        RepositoryItem(
            name="PROTON_DECAY_PREDICTION",
            item_type=ItemType.PREDICTION,
            description="τ(p→e⁺π⁰) ≈ 5×10³⁴ yr; Hyper-K year-by-year routing",
            linked_falsifier="HYPER_K_2034",
            decision_window_years=2034,
            is_consistent_with_data=True,
            has_preregistered_routing=True,
            last_updated_sprint="v11.10",
        ),
        RepositoryItem(
            name="LISA_GW_BACKGROUND",
            item_type=ItemType.PREDICTION,
            description="Ω_GW ~ 10⁻¹⁵ at LISA band",
            linked_falsifier="LISA",
            decision_window_years=2035,
            is_consistent_with_data=True,
            has_preregistered_routing=True,
            last_updated_sprint="v11.5",
        ),
        # ── OPEN GAPS (actionable if linked to routing) ──────────────────────
        RepositoryItem(
            name="KACMOODY_C1_NP_COMPUTATION",
            item_type=ItemType.GAP,
            description="Full non-perturbative Kac-Moody c₁ computation; currently c₁^KM ≈ 3.02 (one-loop)",
            linked_falsifier=None,
            linked_tension=None,
            is_consistent_with_data=True,
            has_preregistered_routing=False,
            last_updated_sprint="v12.7",
            is_speculative_extension=False,
            has_no_near_term_test=True,
        ),
        RepositoryItem(
            name="M3_TOPOLOGY_SELECTION",
            item_type=ItemType.GAP,
            description="Compact 3-manifold topology not selected by UM geometry; requires extension",
            linked_falsifier=None,
            linked_tension=None,
            is_consistent_with_data=True,
            has_preregistered_routing=False,
            last_updated_sprint="v12.6",
            is_speculative_extension=True,
            has_no_near_term_test=True,
        ),
        # ── GOVERNANCE ITEMS (always MONITOR_ONLY unless broken) ────────────
        RepositoryItem(
            name="HILS_GOVERNANCE_FRAMEWORK",
            item_type=ItemType.GOVERNANCE,
            description="Unitary Pentad + co-emergence HILS documentation",
            linked_falsifier=None,
            is_consistent_with_data=True,
            has_preregistered_routing=True,
            last_updated_sprint="v12.8",
        ),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Pillar 391 status
# ──────────────────────────────────────────────────────────────────────────────

PILLAR_391_STATUS = "GOVERNANCE_ENGINEERING"
PILLAR_391_LABEL  = "ADJACENT_TRACK"


def pillar_391_status() -> dict:
    """Machine-readable status for Pillar 391."""
    registry = get_canonical_item_registry()
    report = triage_items(registry)
    return {
        "pillar": 391,
        "name": "Signal-vs-Noise Filter",
        "status": PILLAR_391_STATUS,
        "label": PILLAR_391_LABEL,
        "triage_classes": [t.value for t in TriageClass],
        "active_decision_windows": ACTIVE_DECISION_WINDOWS,
        "active_high_tension_signals": ACTIVE_HIGH_TENSION_SIGNALS,
        "canonical_registry_size": len(registry),
        "triage_summary": report.summary(),
        "hils_status": "ACTIVE",
    }
