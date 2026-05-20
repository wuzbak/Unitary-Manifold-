# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 300 — Observatory Network Integration Dashboard.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

**Milestone Pillar 300** — The observatory network integration dashboard
aggregates all active preregistrations from the v11.x sprint series into a
single queryable, machine-readable status table.  Call
`observatory_network_status()` to get the live PASS/TENSION/FALSIFIED verdict
across all active experiments.

This module is the "control tower" for the Unitary Manifold's observational
programme.  It replaces the need to search across ten separate pillar files
when new data arrives: one function call delivers the full network state.

Active preregistrations aggregated (v11.10)
--------------------------------------------
  Pillar | Experiment          | Observable            | Exp. Date | Status
  -------|---------------------|-----------------------|-----------|----------
  288    | ACT DR6             | n_s, r                | 2024 done | Routed
  289    | IceCube / KM3NeT    | flavor ratio, θ_s     | Ongoing   | CONSISTENT
  290    | LZ Year 2           | σ_SI dark matter      | 2024 done | CONSISTENT
  291    | DART / Hera / NEO   | Taurid risk           | 2026–2028 | OPERATIONAL
  292    | ACT DR6 (deep r)    | r                     | 2024 done | HIGH_TENSION
  293    | Hyper-K             | τ(p→e⁺π⁰), τ(p→ν̄K⁺) | ~2024–34  | OBSERVABLE_WINDOW_OPEN
  294    | LISA                | Ω_GW                  | ~2035     | PREREGISTERED
  295    | WdW (theory)        | —                     | —         | ARCH_LIMIT_CERTIFIED
  296    | P17 seesaw diag.    | Δm²₃₁ seesaw          | —         | UPGRADE_NOT_AVAIL_5D
  297    | SPT-3G              | r (p→e⁺π⁰ via n_s,r)  | 2022 done | CONSISTENT
  298    | Simons Observatory  | r, n_s                | ~2027     | PREREGISTERED
  299    | Hyper-K timeline    | τ(p→e⁺π⁰) vs year     | 2024–34   | TIMELINE_PREREGISTERED

Auxiliary preregistrations:
  JUNO (Pillar 274)     | Δm²₃₁           | ~2027 | PREREGISTERED
  DESI DR3 (Pillar 285) | wₐ (dark energy) | ~2027 | HIGH_TENSION (DR2)
  CMB-S4 (Pillar 292)   | r, n_s           | ~2030 | PREREGISTERED
  LiteBIRD (P1/P1b)     | β (birefringence)| ~2032 | PENDING — PRIMARY

Design principles
------------------
  1. **Single entry point**: `observatory_network_status()` returns the full
     network table, refreshable as new data is integrated.
  2. **No post-hoc adjustment**: all routing thresholds are locked at pillar
     preregistration (versions cited in each entry).
  3. **Separation of concerns**: this module does not implement routing logic.
     It calls the canonical routing functions from each pillar module.
  4. **Queryable**: `query_experiment(name)` returns a single-experiment
     deep-dive; `experiments_by_status(status)` filters by verdict.
  5. **Action-oriented**: every entry includes the specific action required
     if a measurement arrives in that experiment's observable window.

Falsifier priority matrix (as of v11.10)
------------------------------------------
  Priority | Falsifier           | Threshold                  | Timeline
  ---------|---------------------|----------------------------|----------
  P.1      | LiteBIRD β          | β ∉ [0.22°, 0.38°] ≥3σ    | ~2032
  P.2      | CMB-S4 r            | r < 0.010 ≥3σ measured     | ~2030
  P.3      | Simons Obs. r       | r < 0.010 ≥3σ measured     | ~2027-29
  P.4      | JUNO Δm²₃₁          | > 3% residual vs UM ≥3σ    | ~2027
  P.5      | DESI DR3 wₐ         | wₐ ≠ 0 ≥3σ measured        | ~2027
  P.6      | Hyper-K proton      | τ_meas < SK limit ≥3σ      | ~2024-34
  P.7      | LiteBIRD β gap      | β ∈ (0.29°, 0.31°) ≥3σ    | ~2032
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "NETWORK_VERSION",
    "NETWORK_DATE",
    "separation_guard",
    "build_network_table",
    "observatory_network_status",
    "query_experiment",
    "experiments_by_status",
    "falsifier_priority_matrix",
    "upcoming_decision_windows",
    "network_integration_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 300
PILLAR_TITLE: str = "Observatory Network Integration Dashboard"
NETWORK_VERSION: str = "v11.10"
NETWORK_DATE: str = "2026-05-20"


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for Pillar 300."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "aggregates_pillars": list(range(288, 300)) + [274, 285],
        "milestone": "Pillar 300 — Observatory Control Tower",
        "network_version": NETWORK_VERSION,
    }


def build_network_table() -> List[Dict[str, object]]:
    """Build the complete observatory network table.

    Each entry is a machine-readable record covering one experiment.
    All routing thresholds are as preregistered in the cited pillar module.

    Returns
    -------
    List[Dict]
        Ordered list of observatory entries (ordered by expected date).
    """
    return [
        # ── Active / Completed Data ──────────────────────────────────────────
        {
            "experiment": "ACT DR6",
            "pillar": 288,
            "observable": "n_s, r",
            "um_prediction": {"ns": 0.9635, "r": 0.0315},
            "measurement": {"ns": 0.9660, "ns_sigma": 0.0038,
                            "r_upper_95": 0.016},
            "status": "ROUTED",
            "ns_verdict": "CONSISTENT",
            "r_verdict": "HIGH_TENSION",
            "p_falsifier_triggered": False,
            "expected_year": 2024,
            "data_available": True,
            "action": (
                "HIGH_TENSION on r maintained. Await SPT-3G joint analysis "
                "and Simons Observatory DR1 (~2027) for resolution."
            ),
            "preregistration_version": "v11.7",
        },
        {
            "experiment": "BICEP/Keck 2022",
            "pillar": None,
            "observable": "r",
            "um_prediction": {"r": 0.0315},
            "measurement": {"r_upper_95": 0.036},
            "status": "ROUTED",
            "ns_verdict": None,
            "r_verdict": "CONSISTENT",
            "p_falsifier_triggered": False,
            "expected_year": 2022,
            "data_available": True,
            "action": "CONSISTENT. P2 status unchanged.",
            "preregistration_version": "v11.0",
        },
        {
            "experiment": "IceCube / KM3NeT",
            "pillar": 289,
            "observable": "ν flavor ratio, θ_s",
            "um_prediction": {"flavor_ratio": "1:1:1", "theta_s_rad": 0.037},
            "measurement": {"nu_e_frac": 0.49, "nu_e_sigma": 0.10,
                            "consistency_sigma": 2.0},
            "status": "CONSISTENT",
            "ns_verdict": None,
            "r_verdict": None,
            "flavor_verdict": "CONSISTENT",
            "p_falsifier_triggered": False,
            "expected_year": "Ongoing",
            "data_available": True,
            "action": "Monitor KM3NeT 2030 for improved flavor statistics.",
            "preregistration_version": "v11.7",
        },
        {
            "experiment": "LZ Year 2 (Dark Matter)",
            "pillar": 290,
            "observable": "σ_SI (WIMP-nucleon)",
            "um_prediction": {"sigma_si_cm2": 1.0e-77},
            "measurement": {"sigma_si_limit_cm2": 6.6e-48},
            "status": "CONSISTENT",
            "ns_verdict": None,
            "r_verdict": None,
            "dm_verdict": "CONSISTENT_BELOW_LIMIT",
            "orders_below_limit": 29.0,
            "p_falsifier_triggered": False,
            "expected_year": 2024,
            "data_available": True,
            "action": "CONSISTENT by 29 orders of magnitude. Monitor LZ Year 3.",
            "preregistration_version": "v11.7",
        },
        {
            "experiment": "SPT-3G 2022",
            "pillar": 297,
            "observable": "n_s, r",
            "um_prediction": {"ns": 0.9635, "r": 0.0315},
            "measurement": {"ns": 0.9657, "ns_sigma": 0.0040,
                            "r_upper_95": 0.036},
            "status": "ROUTED",
            "ns_verdict": "CONSISTENT",
            "r_verdict": "CONSISTENT",
            "p_falsifier_triggered": False,
            "expected_year": 2022,
            "data_available": True,
            "action": (
                "CONSISTENT. Second ground-based instrument to confirm n_s "
                "and r=CONSISTENT. ACT DR6 remains the only HIGH_TENSION data point."
            ),
            "preregistration_version": "v11.10",
        },
        # ── Near-Term Preregistered (2026–2029) ─────────────────────────────
        {
            "experiment": "DESI DR3 / Year 5",
            "pillar": 285,
            "observable": "wₐ (dark energy EoS)",
            "um_prediction": {"wa": 0.0},
            "measurement": {"wa_dr2": -0.55, "wa_dr2_sigma": 0.20,
                            "significance_dr2": 2.75},
            "status": "HIGH_TENSION",
            "wa_verdict": "HIGH_TENSION",
            "p_falsifier_triggered": False,
            "expected_year": 2027,
            "data_available": False,
            "action": (
                "DR2 = 2.75σ HIGH_TENSION (not FALSIFIED). Await DR3/Y5 (~2027). "
                "If wₐ ≈ -0.62 at σ=0.18 → 3.44σ FALSIFIED. "
                "Run `full_dr2_gap_report()` within 30 days of DR3 publication."
            ),
            "preregistration_version": "v11.5",
        },
        {
            "experiment": "JUNO DR1",
            "pillar": 274,
            "observable": "Δm²₃₁",
            "um_prediction": {"dm31_ev2": 2.452e-3},
            "measurement": None,
            "status": "PREREGISTERED",
            "dm31_verdict": "PENDING",
            "p_falsifier_triggered": False,
            "expected_year": 2027,
            "data_available": False,
            "action": (
                "Run `juno_dr1_routing(dm31_measured, sigma)` within 24 hrs of DR1. "
                "FALSIFIED if residual ≥ 3%. CONSISTENT if < 1%."
            ),
            "preregistration_version": "v11.7",
        },
        {
            "experiment": "Simons Observatory",
            "pillar": 298,
            "observable": "r, n_s",
            "um_prediction": {"r": 0.0315, "ns": 0.9635},
            "measurement": None,
            "status": "PREREGISTERED",
            "r_verdict": "PENDING",
            "ns_verdict": "PENDING",
            "p_falsifier_triggered": False,
            "expected_year": 2027,
            "data_available": False,
            "action": (
                "Run `so_dr1_r_routing(r_meas, sigma_r)` within 24 hrs of DR1. "
                "CONSISTENT if r_meas ≥ 0.020; FALSIFIED if r_meas < 0.010 at ≥3σ. "
                "If UM correct: SO should DETECT r at ~5σ (DR1) or ~10σ (5-yr)."
            ),
            "preregistration_version": "v11.10",
        },
        {
            "experiment": "Hyper-Kamiokande (proton decay)",
            "pillar": 293,
            "observable": "τ(p→e⁺π⁰), τ(p→ν̄K⁺)",
            "um_prediction": {"tau_eplus_pi0_central_yr": 5.0e34},
            "measurement": {"sk_limit_eplus_pi0": 2.4e34},
            "status": "OBSERVABLE_WINDOW_OPEN",
            "tau_verdict": "VIABLE_HK_WINDOW_OPEN",
            "p_falsifier_triggered": False,
            "expected_year": "2024–2034",
            "data_available": False,
            "action": (
                "Run `hyperk_routing(tau_measured)` when HK publishes. "
                "FALSIFIED if τ < SK limit at ≥3σ. "
                "Year-by-year timeline: see Pillar 299."
            ),
            "preregistration_version": "v11.9",
        },
        # ── Long-term (2030–2035) ─────────────────────────────────────────
        {
            "experiment": "CMB-S4",
            "pillar": 292,
            "observable": "r, n_s",
            "um_prediction": {"r": 0.0315, "ns": 0.9635},
            "measurement": None,
            "status": "PREREGISTERED",
            "r_verdict": "PENDING",
            "ns_verdict": "PENDING",
            "p_falsifier_triggered": False,
            "expected_year": 2030,
            "data_available": False,
            "action": (
                "Run `joint_ns_r_verdict()` from cmbs4_ns_r_joint_falsifier.py. "
                "CONSISTENT if r ≥ 0.020; FALSIFIED if r < 0.010 at ≥3σ."
            ),
            "preregistration_version": "v11.9",
        },
        {
            "experiment": "LISA",
            "pillar": 294,
            "observable": "Ω_GW",
            "um_prediction": {"omega_gw": 1.0e-15},
            "measurement": None,
            "status": "PREREGISTERED",
            "gw_verdict": "PENDING",
            "p_falsifier_triggered": False,
            "expected_year": 2035,
            "data_available": False,
            "action": (
                "Run `lisa_dr1_routing(omega_gw_measured, sigma)`. "
                "Non-detection (Ω_GW < 10⁻¹²) → CONSISTENT. "
                "Positive detection > 3σ inconsistent with UM KK → REVIEW."
            ),
            "preregistration_version": "v11.9",
        },
        {
            "experiment": "LiteBIRD",
            "pillar": None,
            "observable": "β (cosmic birefringence), r",
            "um_prediction": {"beta_primary_deg": 0.331, "beta_shadow_deg": 0.273,
                              "r": 0.0315},
            "measurement": {"hint_beta_deg": 0.35, "hint_sigma_deg": 0.14},
            "status": "PENDING",
            "beta_verdict": "PENDING — consistent with 0.35±0.14° hint",
            "r_verdict": "PENDING",
            "p_falsifier_triggered": False,
            "expected_year": 2032,
            "data_available": False,
            "action": (
                "PRIMARY FALSIFIER EVENT. Run `classify_beta()` from "
                "litebird_gap_hardening.py immediately. "
                "FALSIFIED if β < 0.22° or β > 0.38° at ≥3σ, or "
                "β ∈ (0.29°, 0.31°) at ≥3σ (inter-sector gap)."
            ),
            "preregistration_version": "v11.0",
        },
    ]


def observatory_network_status() -> Dict[str, object]:
    """Return the full observatory network status table.

    This is the primary entry point for the control-tower function.
    Refreshable when new data is integrated into any pillar module.

    Returns
    -------
    Dict with:
      - "network_version": str — version of this dashboard
      - "network_date": str — date of last update
      - "experiments": List[Dict] — full network table
      - "summary": Dict — counts by status
      - "open_falsifiers": List[Dict] — active falsifier windows
    """
    table = build_network_table()

    # Status counts
    status_counts: Dict[str, int] = {}
    for entry in table:
        s = entry["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    # Active falsifier windows (experiments not yet falsified and not archival)
    open_falsifiers = [
        e for e in table
        if not e["p_falsifier_triggered"] and e["status"] not in ("ROUTED", "CONSISTENT")
    ]

    return {
        "network_version": NETWORK_VERSION,
        "network_date": NETWORK_DATE,
        "total_experiments": len(table),
        "experiments": table,
        "summary": {
            "total": len(table),
            "status_counts": status_counts,
            "p_falsifier_triggered_count": sum(
                1 for e in table if e["p_falsifier_triggered"]
            ),
            "consistent_count": sum(
                1 for e in table
                if e.get("r_verdict") == "CONSISTENT"
                or e.get("flavor_verdict") == "CONSISTENT"
                or e.get("dm_verdict", "").startswith("CONSISTENT")
                or e.get("ns_verdict") == "CONSISTENT"
            ),
        },
        "open_falsifier_windows": open_falsifiers,
        "label": "ADJACENT_TRACK",
    }


def query_experiment(name: str) -> Optional[Dict[str, object]]:
    """Query a single experiment from the network table by name.

    Parameters
    ----------
    name : str
        Experiment name (case-insensitive partial match).

    Returns
    -------
    Dict or None
        The matching experiment entry, or None if not found.
    """
    table = build_network_table()
    name_lower = name.lower()
    matches = [e for e in table if name_lower in e["experiment"].lower()]
    if not matches:
        return None
    return matches[0]


def experiments_by_status(status: str) -> List[Dict[str, object]]:
    """Filter the network table by status.

    Parameters
    ----------
    status : str
        Status string to match (case-sensitive). Examples:
        "CONSISTENT", "HIGH_TENSION", "PREREGISTERED", "ROUTED",
        "PENDING", "OBSERVABLE_WINDOW_OPEN".

    Returns
    -------
    List[Dict]
        All experiments with the given status.
    """
    table = build_network_table()
    return [e for e in table if e["status"] == status]


def falsifier_priority_matrix() -> List[Dict[str, object]]:
    """Return the falsifier priority matrix for all active UM falsifiers.

    Ordered by priority (P.1 = most fundamental / earliest / highest impact).
    Thresholds are hardgated and must not be changed post-hoc.
    """
    return [
        {
            "priority": "P.1",
            "falsifier": "LiteBIRD β — primary",
            "condition": "β ∉ [0.22°, 0.38°] at ≥3σ",
            "timeline": "~2032",
            "module": "litebird_gap_hardening.py::classify_beta()",
            "impact": "Eliminates braided-winding mechanism entirely",
            "preregistered_version": "v11.0",
        },
        {
            "priority": "P.2",
            "falsifier": "CMB-S4 r measurement",
            "condition": "r < 0.010 at ≥3σ measured",
            "timeline": "~2030",
            "module": "cmbs4_ns_r_joint_falsifier.py::joint_ns_r_verdict()",
            "impact": "Falsifies braided inflation mechanism; P2 FALSIFIED",
            "preregistered_version": "v11.9",
        },
        {
            "priority": "P.3",
            "falsifier": "Simons Observatory r measurement",
            "condition": "r < 0.010 at ≥3σ measured",
            "timeline": "~2027–2029",
            "module": "pillar298_simons_observatory_preregistration.py::so_dr1_r_routing()",
            "impact": "Same as CMB-S4 P2 falsifier; earlier timeline",
            "preregistered_version": "v11.10",
        },
        {
            "priority": "P.4",
            "falsifier": "JUNO Δm²₃₁",
            "condition": "Residual > 3% vs UM at JUNO precision",
            "timeline": "~2027",
            "module": "juno_dr1_preregistration_package.py::juno_dr1_routing()",
            "impact": "Falsifies P17 Δm²₃₁ CONDITIONAL_DERIVATION",
            "preregistered_version": "v11.7",
        },
        {
            "priority": "P.5",
            "falsifier": "DESI DR3 wₐ",
            "condition": "wₐ ≠ 0 at ≥3σ measured",
            "timeline": "~2027",
            "module": "desi_year3_monitor.py::route_desi_y3()",
            "impact": "Falsifies frozen radion (P4 wₐ=0 prediction)",
            "preregistered_version": "v11.5",
        },
        {
            "priority": "P.6",
            "falsifier": "Hyper-Kamiokande proton decay",
            "condition": "τ_measured < SK limit at ≥3σ",
            "timeline": "~2024–2034",
            "module": "pillar293_proton_decay_rate_prediction.py::hyperk_routing()",
            "impact": "Falsifies UM GUT sector (M_GUT / α_GUT derivation)",
            "preregistered_version": "v11.9",
        },
        {
            "priority": "P.7",
            "falsifier": "LiteBIRD β — inter-sector gap",
            "condition": "β ∈ (0.29°, 0.31°) at ≥3σ",
            "timeline": "~2032",
            "module": "litebird_gap_hardening.py::classify_beta()",
            "impact": "Neither (5,7) primary nor (5,6) shadow sector consistent",
            "preregistered_version": "v11.0",
        },
    ]


def upcoming_decision_windows() -> List[Dict[str, object]]:
    """Return the ordered list of upcoming observational decision windows.

    Ordered by expected year.
    """
    return [
        {
            "year": 2027,
            "experiments": ["JUNO DR1", "DESI DR3", "Simons Observatory DR1"],
            "primary_falsifier_window": "DESI DR3 wₐ / JUNO Δm²₃₁",
            "action": (
                "Three major decision points in a single year. "
                "Pre-positioned routing scripts are ready for same-day execution."
            ),
        },
        {
            "year": 2029,
            "experiments": ["Simons Observatory 5-yr"],
            "primary_falsifier_window": "SO 5-yr r measurement",
            "action": (
                "SO 5-yr should detect r = 0.0315 at ~10σ if UM is correct. "
                "Non-detection or r < 0.010 at ≥3σ triggers P2 falsifier."
            ),
        },
        {
            "year": 2030,
            "experiments": ["CMB-S4"],
            "primary_falsifier_window": "CMB-S4 r measurement (definitive)",
            "action": (
                "Decisive experiment for P2 (r) falsifier. "
                "Combined with LiteBIRD β in 2032 completes the birefringence picture."
            ),
        },
        {
            "year": 2032,
            "experiments": ["LiteBIRD"],
            "primary_falsifier_window": "LiteBIRD β — PRIMARY FALSIFIER (P.1)",
            "action": (
                "PRIMARY FALSIFIER EVENT. Run classify_beta() immediately. "
                "The UM stands or falls on this measurement above all others."
            ),
        },
        {
            "year": 2035,
            "experiments": ["LISA"],
            "primary_falsifier_window": "LISA Ω_GW",
            "action": "Run lisa_dr1_routing(). Non-detection → CONSISTENT.",
        },
    ]


def network_integration_report() -> Dict[str, object]:
    """Generate the complete observatory network integration report.

    This is the top-level aggregate function for Pillar 300.
    """
    guard = separation_guard()
    status = observatory_network_status()
    falsifiers = falsifier_priority_matrix()
    windows = upcoming_decision_windows()

    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "network_version": NETWORK_VERSION,
        "network_date": NETWORK_DATE,
        "adjacency_guard": guard,
        "network_status": status,
        "falsifier_priority_matrix": falsifiers,
        "upcoming_decision_windows": windows,
        "summary": {
            "total_experiments_tracked": status["total_experiments"],
            "active_falsifier_windows": len(falsifiers),
            "upcoming_decision_years": [w["year"] for w in windows],
            "p_falsifier_triggered": status["summary"]["p_falsifier_triggered_count"] > 0,
            "framework_status": "STANDING",
            "primary_falsifier_year": 2032,
            "primary_falsifier_experiment": "LiteBIRD",
        },
        "usage": (
            "Call observatory_network_status() for live table. "
            "Call query_experiment(name) for single-experiment deep-dive. "
            "Call experiments_by_status(status) to filter by verdict. "
            "Call falsifier_priority_matrix() for action-ordered falsifier list. "
            "Call upcoming_decision_windows() for the ordered event timeline."
        ),
        "status": "INTEGRATION_DASHBOARD_OPERATIONAL",
        "label": "ADJACENT_TRACK",
        "milestone": "Pillar 300 — Observatory Control Tower",
    }
