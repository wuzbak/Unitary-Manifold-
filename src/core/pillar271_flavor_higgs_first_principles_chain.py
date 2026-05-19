# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 271 — Unified flavor + Higgs first-principles chain.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

This module consolidates the clean executable chain for:
- P7–P10 Yukawas,
- P14 CKM ρ̄,
- P18–P20 PMNS angles,
- P5 Higgs mass, now evaluated from the *derived* top Yukawa rather than an
  external top-mass seed.
"""
from __future__ import annotations

import math
from typing import Dict

from src.core.higgs_mass_closure import HIGGS_MASS_PDG_GEV, HIGGS_VEV_GEV, ftum_tree_quartic, kk_scale_gev, rge_quartic_correction
from src.core.p14_ckm_rhobar_derived_cert import p14_derived_gate_report
from src.core.p18_theta12_derived_cert import p18_derived_gate_report
from src.core.p19_theta23_derived_cert import p19_derived_gate_report
from src.core.p20_theta13_derived_cert import p20_derived_gate_report
from src.core.p7_p10_yukawa_derived_cert import yukawa_derived_gate_report
from src.core.yukawa_tier4_hardgate_cert import tier4_nlo_yukawa_table

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "derived_top_yukawa_prediction",
    "higgs_mass_from_derived_top_yukawa",
    "flavor_higgs_first_principles_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"


def derived_top_yukawa_prediction() -> Dict[str, float]:
    """Return the P7 top Yukawa prediction from the derived Tier-4 braid chain."""
    row = next(row for row in tier4_nlo_yukawa_table() if row["fermion"] == "top")
    return {
        "y_t_pred": float(row["y_pred_nlo"]),
        "y_t_pdg": float(row["y_pdg"]),
        "residual_pct": float(row["residual_nlo_pct"]),
        "nlo_suppression": float(row["nlo_suppression"]),
    }


def higgs_mass_from_derived_top_yukawa() -> Dict[str, float | str]:
    """Recompute P5 using the derived top Yukawa instead of an external m_top."""
    y_t = derived_top_yukawa_prediction()["y_t_pred"]
    lam_tree = float(ftum_tree_quartic()["lambda_H_tree"])
    m_kk = kk_scale_gev()
    delta_lam = rge_quartic_correction(y_t=y_t, m_kk_gev=m_kk, higgs_vev_gev=HIGGS_VEV_GEV)
    lam_eff = lam_tree + delta_lam
    m_h = HIGGS_VEV_GEV * math.sqrt(max(2.0 * lam_eff, 0.0))
    residual_pct = abs(m_h - HIGGS_MASS_PDG_GEV) / HIGGS_MASS_PDG_GEV * 100.0
    return {
        "y_t_derived": y_t,
        "lambda_tree": lam_tree,
        "delta_lambda": delta_lam,
        "lambda_eff": lam_eff,
        "m_kk_gev": m_kk,
        "m_h_pred_gev": m_h,
        "m_h_pdg_gev": HIGGS_MASS_PDG_GEV,
        "residual_pct": residual_pct,
        "status": "PASS" if residual_pct < 5.0 else "TENSION",
    }


def flavor_higgs_first_principles_report() -> Dict[str, object]:
    """Return the consolidated flavor / Higgs executable chain."""
    yukawa = yukawa_derived_gate_report()
    ckm = p14_derived_gate_report()
    pmns = {
        "P18": p18_derived_gate_report(),
        "P19": p19_derived_gate_report(),
        "P20": p20_derived_gate_report(),
    }
    higgs = higgs_mass_from_derived_top_yukawa()

    all_pmns_pass = all(bool(packet["all_gates_pass"]) for packet in pmns.values())
    all_pass = bool(yukawa["all_gates_pass"] and ckm["all_gates_pass"] and all_pmns_pass and higgs["status"] == "PASS")

    return {
        "pillar": 271,
        "title": "Unified flavor + Higgs first-principles chain",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "derived_inputs": ["K_CS=74", "N_W=5", "πkR=37", "N₂=7", "N_c=3"],
        "yukawa_quartet": yukawa,
        "ckm_chain": ckm,
        "pmns_chain": pmns,
        "higgs_from_derived_top_yukawa": higgs,
        "all_pass": all_pass,
        "status": (
            "UNIFIED_FLAVOR_HIGGS_CHAIN_EXECUTABLE"
            if all_pass
            else "UNIFIED_FLAVOR_HIGGS_CHAIN_TENSION"
        ),
        "remaining_open": (
            "This packet unifies the executable chain, but the absolute light-fermion "
            "hierarchy still depends on the open Yukawa-scale / c_L completion lane."
        ),
    }
