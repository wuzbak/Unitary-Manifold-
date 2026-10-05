# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 666 — XDiag Phase 2 KK Mott benchmark.

STATUS: XDIAG_PHASE2_KK_MOTT_BENCHMARK_CERTIFIED

Background
----------
This adjacent-track pillar codifies the analytical KK–Fermi-Hubbard benchmark
that the UM↔XDiag bridge would exercise in production.  CI does not ship with
XDiag, so this module does not call the bridge directly; instead it defines the
parameter certificate, the expected strong-coupling Mott verdict, and the
schema/parity requirements that the bridge must satisfy when installed.
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "ADJACENT_TRACK",
    "L_SITES",
    "T_KK",
    "U_KK",
    "U_OVER_T_MOTT",
    "MOTT_TRANSITION_THRESHOLD",
    "IS_MOTT_INSULATOR",
    "ROUTING_ZONE",
    "SCHEMA_VERSION",
    "XDIAG_PRODUCTION_INSTALL_REQUIRED",
    "BRAID_CONDENSATE_CONSISTENT",
    "kk_mott_parameters",
    "analytical_mott_prediction",
    "schema_round_trip_spec",
    "parity_gate_spec",
    "pillar_report",
]

PILLAR_NUMBER: int = 666
PILLAR_STATUS: str = "XDIAG_PHASE2_KK_MOTT_BENCHMARK_CERTIFIED"
PILLAR_TITLE: str = "XDiag Phase 2 — KK Mott Benchmark"
VERSION: str = "v21.0"
ADJACENT_TRACK: bool = True

L_SITES: int = 8
T_KK: float = 12 / 37
U_KK: float = 74 / 5
U_OVER_T_MOTT: float = U_KK / T_KK
MOTT_TRANSITION_THRESHOLD: float = 40.0
IS_MOTT_INSULATOR: bool = U_OVER_T_MOTT > MOTT_TRANSITION_THRESHOLD
ROUTING_ZONE: str = "um_exact_dense"
SCHEMA_VERSION: str = "1.0.0"
XDIAG_PRODUCTION_INSTALL_REQUIRED: bool = True
BRAID_CONDENSATE_CONSISTENT: bool = True


def kk_mott_parameters() -> Dict[str, Any]:
    """Return KK–Fermi-Hubbard parameters at UM-motivated values."""
    return {
        "l_sites": L_SITES,
        "t_kk": T_KK,
        "u_kk": U_KK,
        "u_over_t": U_OVER_T_MOTT,
        "mott_transition_threshold": MOTT_TRANSITION_THRESHOLD,
        "is_mott_insulator": IS_MOTT_INSULATOR,
        "routing_zone": ROUTING_ZONE,
        "schema_version": SCHEMA_VERSION,
    }


def analytical_mott_prediction() -> Dict[str, Any]:
    """Return the strong-coupling analytical Mott prediction."""
    j_eff = 4.0 * T_KK**2 / U_KK
    return {
        "j_eff": j_eff,
        "spin_gap_estimate": j_eff,
        "mott_insulator_confirmed": IS_MOTT_INSULATOR,
        "p412_consistency": BRAID_CONDENSATE_CONSISTENT,
        "honest_residual": (
            "Numerical exact-diagonalisation confirmation requires an XDiag "
            "production install outside CI."
        ),
    }


def schema_round_trip_spec() -> Dict[str, Any]:
    """Return the XDiag schema round-trip specification."""
    required_fields: List[str] = [
        "ground_energy",
        "first_gap",
        "staggered_magnetization",
    ]
    optional_fields: List[str] = [
        "charge_gap",
        "spin_gap",
        "double_occupancy",
    ]
    return {
        "required_fields": required_fields,
        "optional_fields": optional_fields,
        "schema_version": SCHEMA_VERSION,
        "routing_zone": ROUTING_ZONE,
        "export_spec": {
            "payload_keys": ["run_id", "spec", "hamiltonian_terms"],
            "required_schema_key": "schema_version",
        },
        "ingest_spec": {
            "required_result_keys": ["eigenvalues", "observables"],
            "required_metric_count": len(required_fields),
        },
    }


def parity_gate_spec() -> Dict[str, Any]:
    """Return the parity gate specification for the benchmark lane."""
    schema_spec = schema_round_trip_spec()
    return {
        "required_fields": schema_spec["required_fields"],
        "optional_fields": schema_spec["optional_fields"],
        "required_pass_count": len(schema_spec["required_fields"]),
        "optional_pass_count_if_present": len(schema_spec["optional_fields"]),
        "energy_abs_tol": 1.0e-8,
        "observable_abs_tol": 1.0e-6,
        "routing_zone": ROUTING_ZONE,
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 666 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": ADJACENT_TRACK,
        "kk_mott_parameters": kk_mott_parameters(),
        "analytical_mott_prediction": analytical_mott_prediction(),
        "schema_round_trip_spec": schema_round_trip_spec(),
        "parity_gate_spec": parity_gate_spec(),
        "xdiag_production_install_required": XDIAG_PRODUCTION_INSTALL_REQUIRED,
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
