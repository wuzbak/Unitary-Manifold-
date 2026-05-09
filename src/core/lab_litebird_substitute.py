# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Machine-readable immediate lab substitute for LiteBIRD falsification lane.

This module operationalizes F14/P8:
table-top, topology-certified (5,7) CP-asymmetry campaigns that can run now,
in parallel with cosmological timelines.
"""
from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "SIGMA_TARGET",
    "TOPOLOGY_TARGET",
    "LabCPCampaignInput",
    "evaluate_lab_cp_campaign",
    "lab_protocol_checklist",
    "lab_substitute_status_snapshot",
]

SIGMA_TARGET: float = 1.0e-5
TOPOLOGY_TARGET: str = "(5,7)"
_ZERO_CONSISTENT_SIGMA_95CL: float = 1.96


@dataclass(frozen=True)
class LabCPCampaignInput:
    """Decision-grade input bundle for one lab campaign summary."""

    a_cp_lab: float
    sigma_a: float
    topology_certified: bool
    independent_replications: int
    systematics_controls_passed: bool
    topology_independent_asymmetry: bool
    sign_reversal_inverts_cp_odd: bool
    cp_even_baseline_stable: bool
    signal_explained_by_systematics: bool


def evaluate_lab_cp_campaign(inputs: LabCPCampaignInput) -> dict[str, object]:
    """Apply bright-line F-LAB-CP-1..4 logic to a campaign.

    Returns a dict with verdict in {"FALSIFIED", "SUPPORTED", "INCONCLUSIVE"}.
    """
    if inputs.sigma_a <= 0:
        raise ValueError(f"sigma_a must be positive, got {inputs.sigma_a}")

    if not inputs.topology_certified:
        return {
            "verdict": "INCONCLUSIVE",
            "falsified": False,
            "reason": "Topology has not been independently certified as stable (5,7).",
            "triggered_conditions": [],
            "decision_grade": False,
        }

    if inputs.sigma_a > SIGMA_TARGET:
        return {
            "verdict": "INCONCLUSIVE",
            "falsified": False,
            "reason": (
                f"Sensitivity not yet decision-grade: sigma_a={inputs.sigma_a:.3e} "
                f"> {SIGMA_TARGET:.1e}."
            ),
            "triggered_conditions": [],
            "decision_grade": False,
        }

    zero_consistent_at_95_cl = abs(inputs.a_cp_lab) <= _ZERO_CONSISTENT_SIGMA_95CL * inputs.sigma_a
    has_replication = inputs.independent_replications >= 2

    triggered: list[str] = []
    if (
        zero_consistent_at_95_cl
        and has_replication
        and inputs.systematics_controls_passed
    ):
        triggered.append("F-LAB-CP-1")
    if inputs.topology_independent_asymmetry:
        triggered.append("F-LAB-CP-2")
    if (not inputs.sign_reversal_inverts_cp_odd) and inputs.cp_even_baseline_stable:
        triggered.append("F-LAB-CP-3")
    if inputs.signal_explained_by_systematics:
        triggered.append("F-LAB-CP-4")

    if triggered:
        return {
            "verdict": "FALSIFIED",
            "falsified": True,
            "reason": "One or more bright-line lab falsification conditions were met.",
            "triggered_conditions": triggered,
            "decision_grade": True,
        }

    supports_transfer = (
        abs(inputs.a_cp_lab) >= 3.0 * inputs.sigma_a
        and has_replication
        and inputs.systematics_controls_passed
        and inputs.sign_reversal_inverts_cp_odd
        and not inputs.topology_independent_asymmetry
        and not inputs.signal_explained_by_systematics
    )
    if supports_transfer:
        return {
            "verdict": "SUPPORTED",
            "falsified": False,
            "reason": "Topology-locked nonzero A_CP^lab survives controls at decision-grade sensitivity.",
            "triggered_conditions": [],
            "decision_grade": True,
        }

    return {
        "verdict": "INCONCLUSIVE",
        "falsified": False,
        "reason": "Decision-grade sensitivity reached, but support/falsification criteria were not fully met.",
        "triggered_conditions": [],
        "decision_grade": True,
    }


def lab_protocol_checklist() -> list[str]:
    """Return the required checklist for reproducible decision-grade reporting."""
    return [
        "Independent (5,7) topology certification report attached",
        "Paired conjugate protocols with raw Γ+ and Γ− published",
        f"Total uncertainty target met: sigma_a <= {SIGMA_TARGET:.1e}",
        "Topology-swap controls included under matched conditions",
        "Sign-reversal controls included with CP-even baseline stability",
        "Systematics decomposition and correction model published",
        "At least two independent replications logged",
    ]


def lab_substitute_status_snapshot() -> dict[str, object]:
    """Return current status for canonical evidence feeds and governance trackers."""
    return {
        "lane_id": "F14/P8",
        "name": "Immediate Table-Top CP Falsifier",
        "topology_target": TOPOLOGY_TARGET,
        "sigma_target": SIGMA_TARGET,
        "status": "PENDING_CAMPAIGN",
        "next_milestone_year": 2026,
        "decision_rule": (
            "FALSIFIED iff topology_certified and sigma_a<=1e-5 and "
            "zero-consistent-at-95CL with replication and controls, "
            "or F-LAB-CP-2/F-LAB-CP-3/F-LAB-CP-4 triggered"
        ),
        "checklist": lab_protocol_checklist(),
    }
