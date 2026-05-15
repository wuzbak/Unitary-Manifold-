# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 245 — 11D / Terminal Full-Closure Engine.

Adjacent research track (non-hardgate): consolidate all existing Hořava-Witten
/ 11D artefacts into one deterministic terminal-closure certificate and
permanently anchor the n_w = 5 runtime seed produced by the 11D UV reduction.

This module is the natural successor to Pillar 244.  Pillar 244 certified that
the 10D branch was internally finished and ready for handoff.  Pillar 245
executes that handoff:

  1. ``hw_kickoff_scaffold``  — Rung-6 boundary assumptions recorded and
     internally consistent (``src/eleventd/horava_witten_reduction.py``).
  2. ``hw_hard_gate``         — Four structural hard-gate checks pass for
     RUNG_SOLID status (``src/eleventd/horava_witten_hard_gate.py``).
  3. ``g4_flux_vacuum_link``  — G₄-flux elimination leaves exactly n_w = 5
     surviving the UV flux background (``src/eleventd/g4_flux_vacuum_link.py``).
  4. ``uv_vacuum_selection``  — Consolidated gate (nw5 theorem + Majorana +
     G₄ + Euclidean saddle) uniquely selects n_w = 5
     (``src/eleventd/uv_vacuum_selection_gate.py``).
  5. ``bridge_burn_5d``       — All 11D scaffold symbols are retired; only the
     minimal 5D runtime seed {n_w, braid_pair, k_cs, η̄, πkR} survives
     (``src/eleventd/uv_to_5d_boundary_map.py``).

Full closure is declared when all five lanes pass and the terminal 5D runtime
seed is confirmed as {n_w=5, braid_pair=(5,7), k_cs=74, η̄=0.5, πkR=37.0}.

This module does not change any hardgate physics status by itself.  It records
a structural fact: the Hořava-Witten / 11D geometric machinery is complete, the
bridge to 5D is burned, and the runtime is locked.
"""
from __future__ import annotations

from typing import Any

from src.eleventd.g4_flux_vacuum_link import g4_flux_selection_summary
from src.eleventd.horava_witten_hard_gate import rung6_gate_evidence
from src.eleventd.horava_witten_reduction import rung6_kickoff_evidence
from src.eleventd.uv_to_5d_boundary_map import burn_bridge_certificate, reduced_5d_invariants
from src.eleventd.uv_vacuum_selection_gate import canonical_uv_vacuum_selection_gate

__all__ = [
    # re-exported runtime seed constants
    "N_W",
    "K_CS",
    "BRAID_PAIR",
    "ETA_BAR",
    "PI_KR",
    # track labels
    "ADJACENCY_TRACK_LABEL",
    "ELEVENTD_CLOSURE_TRACK_LABEL",
    "LANE_ORDER",
    "N_LANES",
    # provenance
    "__provenance__",
    # functions
    "separation_guard",
    "terminal_runtime_seed",
    "eleventd_lane_reports",
    "eleventd_closure_summary",
    "terminal_closure_certificate",
    "pillar245_eleventd_full_closure_report",
]

# ---------------------------------------------------------------------------
# Runtime seed (locked by bridge-burn; no free parameters)
# ---------------------------------------------------------------------------
N_W: int = 5
K_CS: int = 74
BRAID_PAIR: tuple[int, int] = (5, 7)
ETA_BAR: float = 0.5
PI_KR: float = 37.0

# ---------------------------------------------------------------------------
# Track metadata
# ---------------------------------------------------------------------------
ADJACENCY_TRACK_LABEL: str = "ADJACENT_TRACK_NON_HARDGATE"
ELEVENTD_CLOSURE_TRACK_LABEL: str = "ELEVENTD_FULL_CLOSURE_TRACK"

LANE_ORDER: tuple[str, ...] = (
    "hw_kickoff_scaffold",
    "hw_hard_gate",
    "g4_flux_vacuum_link",
    "uv_vacuum_selection",
    "bridge_burn_5d",
)
N_LANES: int = len(LANE_ORDER)

__provenance__ = {
    "pillar": 245,
    "title": "11D / Terminal Full-Closure Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — deterministic 11D terminal-closure audit; "
        "non-hardgate, no ToE score delta"
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def separation_guard() -> dict[str, Any]:
    """Return explicit non-hardgate boundary metadata for Pillar 245."""
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": ELEVENTD_CLOSURE_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "message": (
            "Pillar 245 certifies 11D / terminal full-closure only.  The runtime "
            "seed is locked at n_w = 5; no physics-status promotion is claimed."
        ),
    }


def terminal_runtime_seed() -> dict[str, Any]:
    """Return the locked 5D runtime seed produced by the 11D reduction."""
    inv = reduced_5d_invariants()
    seed = inv["runtime_seed"]
    locked = bool(
        seed["n_w"] == N_W
        and tuple(seed["braid_pair"]) == BRAID_PAIR
        and seed["k_cs"] == K_CS
        and abs(seed["eta_bar"] - ETA_BAR) < 1e-12
        and abs(seed["pi_kR"] - PI_KR) < 1e-10
    )
    return {
        "n_w": seed["n_w"],
        "braid_pair": tuple(seed["braid_pair"]),
        "k_cs": seed["k_cs"],
        "eta_bar": seed["eta_bar"],
        "pi_kR": seed["pi_kR"],
        "bridge_burned": inv["bridge_burned"],
        "runtime_policy": inv["runtime_policy"],
        "forbidden_runtime_dependencies": inv["forbidden_runtime_dependencies"],
        "seed_locked": locked,
        "status": "RUNTIME_SEED_LOCKED" if locked else "RUNTIME_SEED_MISMATCH",
    }


def eleventd_lane_reports() -> dict[str, dict[str, Any]]:
    """Return deterministic pass/fail evidence for the five 11D closure lanes."""
    kickoff = rung6_kickoff_evidence()
    hw_gate = rung6_gate_evidence()
    g4_summary = g4_flux_selection_summary()
    uv_gate = canonical_uv_vacuum_selection_gate()
    bridge = burn_bridge_certificate()

    kickoff_pass = bool(kickoff["kill_switch_pass"] and kickoff["gate_count"] == 4)
    hw_hard_pass = bool(hw_gate["hard_gate_pass"] and hw_gate["kill_switch_pass"])
    g4_pass = bool(
        g4_summary["status"] == "UNIQUE_UV_FLUX_SELECTION"
        and g4_summary["unique_flux_selected_n_w"] == N_W
    )
    uv_pass = bool(
        uv_gate["unique_selection"]
        and uv_gate["selected_n_w"] == N_W
    )
    bridge_pass = bool(
        bridge["status"] == "BRIDGE_BURNED_RUNTIME_REDUCED"
        and bridge["reduced_5d_invariants"]["bridge_burned"]
    )

    return {
        "hw_kickoff_scaffold": {
            "artifact": "src/eleventd/horava_witten_reduction.py",
            "pass": kickoff_pass,
            "status": kickoff["status"],
            "evidence": {
                "kill_switch_pass": kickoff["kill_switch_pass"],
                "gate_count": kickoff["gate_count"],
                "epistemic_status": kickoff["epistemic_status"],
                "anchor": kickoff["anchor"],
            },
        },
        "hw_hard_gate": {
            "artifact": "src/eleventd/horava_witten_hard_gate.py",
            "pass": hw_hard_pass,
            "status": hw_gate["status"],
            "evidence": {
                "hard_gate_pass": hw_gate["hard_gate_pass"],
                "kill_switch_pass": hw_gate["kill_switch_pass"],
                "n_supercharges_4d": hw_gate["n_supercharges_4d"],
                "dim_e8xe8": hw_gate["dim_e8xe8"],
                "n_boundaries_s1z2": hw_gate["n_boundaries_s1z2"],
            },
        },
        "g4_flux_vacuum_link": {
            "artifact": "src/eleventd/g4_flux_vacuum_link.py",
            "pass": g4_pass,
            "status": g4_summary["status"],
            "evidence": {
                "surviving_candidates": g4_summary["surviving_candidates"],
                "unique_flux_selected_n_w": g4_summary["unique_flux_selected_n_w"],
                "no_score_inflation": g4_summary["no_score_inflation"],
            },
        },
        "uv_vacuum_selection": {
            "artifact": "src/eleventd/uv_vacuum_selection_gate.py",
            "pass": uv_pass,
            "status": uv_gate["status"],
            "evidence": {
                "selected_n_w": uv_gate["selected_n_w"],
                "unique_selection": uv_gate["unique_selection"],
                "no_score_inflation": uv_gate["no_score_inflation"],
            },
        },
        "bridge_burn_5d": {
            "artifact": "src/eleventd/uv_to_5d_boundary_map.py",
            "pass": bridge_pass,
            "status": bridge["status"],
            "evidence": {
                "bridge_burned": bridge["reduced_5d_invariants"]["bridge_burned"],
                "runtime_policy": bridge["reduced_5d_invariants"]["runtime_policy"],
                "no_score_inflation": bridge["no_score_inflation"],
            },
        },
    }


def eleventd_closure_summary() -> dict[str, Any]:
    """Return aggregate closure state for the 11D terminal programme."""
    lanes = eleventd_lane_reports()
    passed = [name for name in LANE_ORDER if lanes[name]["pass"]]
    failed = [name for name in LANE_ORDER if not lanes[name]["pass"]]
    closure_index = len(passed) / float(N_LANES)
    fully_closed = len(failed) == 0
    return {
        "track": ELEVENTD_CLOSURE_TRACK_LABEL,
        "lane_order": LANE_ORDER,
        "passed_lanes": passed,
        "failed_lanes": failed,
        "closure_index": closure_index,
        "fully_closed": fully_closed,
        "status": (
            "ELEVENTD_FULL_CLOSURE_CERTIFIED"
            if fully_closed
            else "ELEVENTD_CLOSURE_INCOMPLETE"
        ),
    }


def terminal_closure_certificate() -> dict[str, Any]:
    """Return the final terminal-closure certificate for the 11D programme."""
    summary = eleventd_closure_summary()
    seed = terminal_runtime_seed()
    certified = bool(summary["fully_closed"] and seed["seed_locked"])
    return {
        "title": "11D / Terminal Full-Closure Certificate",
        "certified": certified,
        "closure_status": summary["status"],
        "runtime_seed": {
            "n_w": seed["n_w"],
            "braid_pair": seed["braid_pair"],
            "k_cs": seed["k_cs"],
            "eta_bar": seed["eta_bar"],
            "pi_kR": seed["pi_kR"],
        },
        "bridge_burned": seed["bridge_burned"],
        "runtime_policy": seed["runtime_policy"],
        "no_score_inflation": True,
        "message": (
            "The 11D Hořava-Witten / M-theory continuation is internally complete.  "
            "The UV G₄-flux elimination uniquely selects n_w = 5.  The 11D-to-5D "
            "bridge is burned.  The 5D runtime is locked at {n_w=5, k_cs=74, "
            "braid_pair=(5,7)}.  No further 11D scaffolding is required."
        )
        if certified
        else (
            "Terminal closure cannot be declared: one or more lanes have not passed."
        ),
        "falsification_condition": (
            "FALSIFIED as a terminal-closure claim if (a) any of the five Rung-6 / "
            "UV-selection / bridge-burn lanes is later shown non-reproducible, "
            "or (b) the locked runtime seed {n_w=5, k_cs=74, braid_pair=(5,7)} "
            "is contradicted by a future geometric derivation."
        ),
    }


def pillar245_eleventd_full_closure_report() -> dict[str, Any]:
    """Return the integrated adjacent-track report for Pillar 245."""
    lanes = eleventd_lane_reports()
    summary = eleventd_closure_summary()
    cert = terminal_closure_certificate()
    seed = terminal_runtime_seed()
    return {
        "pillar": 245,
        "title": __provenance__["title"],
        "status": __provenance__["status"],
        "adjacency_track_label": ADJACENCY_TRACK_LABEL,
        "eleventd_closure_track": ELEVENTD_CLOSURE_TRACK_LABEL,
        "adjacent_toe_score_delta": 0.0,
        "separation_guard": separation_guard(),
        "lane_reports": lanes,
        "closure_summary": summary,
        "terminal_runtime_seed": seed,
        "terminal_closure_certificate": cert,
        "predecessor_pillar": 244,
        "predecessor_handoff_consumed": True,
        "falsification_condition": cert["falsification_condition"],
    }
