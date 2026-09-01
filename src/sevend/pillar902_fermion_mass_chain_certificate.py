# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 902 — FERMION_MASS_CHAIN_CERTIFICATE.

This registry summarises Sprint BC pillars 887–901 as a single fermion-sector
ledger.  It counts what is resolved, what is only partial, what remains in
tension, and what is now honestly classed as an architecture limit.
"""
from __future__ import annotations

from typing import Any

from src.core.pillar891_sprint_bc_phase1_certificate import STATUS_LABEL as STATUS_891
from src.core.pillar897_sprint_bc_phase2_certificate import STATUS_LABEL as STATUS_897
from src.nined.pillar894_alpha_s_vol_pinning import STATUS_LABEL as STATUS_894
from src.sevend.pillar887_fn_charge_assignment import PILLAR_GATE as GATE_887, STATUS_LABEL as STATUS_887
from src.sevend.pillar888_ckm_7d_fn_correction import PILLAR_GATE as GATE_888, STATUS_LABEL as STATUS_888
from src.sevend.pillar889_jarlskog_fn import PILLAR_GATE as GATE_889, STATUS_LABEL as STATUS_889
from src.sevend.pillar890_pmns_fn_bridge import PILLAR_GATE as GATE_890, STATUS_LABEL as STATUS_890
from src.sevend.pillar898_quark_mass_ratios_fn import PILLAR_GATE as GATE_898, STATUS_LABEL as STATUS_898
from src.sevend.pillar899_lepton_mass_ratios_fn import PILLAR_GATE as GATE_899, STATUS_LABEL as STATUS_899
from src.sevend.pillar900_neutrino_mass_ordering import PILLAR_GATE as GATE_900, STATUS_LABEL as STATUS_900
from src.sevend.pillar901_yukawa_svd_fn_unified import PILLAR_GATE as GATE_901, STATUS_LABEL as STATUS_901
from src.sixd.pillar892_ngen_bundle_third_filter import STATUS_LABEL as STATUS_892
from src.sixd.pillar893_e8_breaking_third_filter import STATUS_LABEL as STATUS_893
from src.core.pillar895_tcc_efold_nlo import STATUS_LABEL as STATUS_895
from src.core.pillar896_cmb_amplitude_beyond_eft import STATUS_LABEL as STATUS_896

PILLAR_NUMBER: int = 902
PILLAR_GATE: str = "FERMION_MASS_CHAIN_CERTIFICATE"
FERMION_CHAIN_GATE: str = "FERMION_CHAIN_PARTIAL"
STATUS_LABEL: str = "PARTIAL"

FERMION_PILLARS: list[tuple[int, str, str]] = [
    (887, GATE_887, STATUS_887),
    (888, GATE_888, STATUS_888),
    (889, GATE_889, STATUS_889),
    (890, GATE_890, STATUS_890),
    (891, "SPRINT_BC_PHASE1_CERTIFICATE", STATUS_891),
    (892, "NGEN_6D_BUNDLE_THIRD_FILTER", STATUS_892),
    (893, "E8_BREAKING_THIRD_FILTER", STATUS_893),
    (894, "ALPHA_S_M7_VOL_PINNING", STATUS_894),
    (895, "TCC_EFOLD_NLO_AUDIT", STATUS_895),
    (896, "CMB_AMPLITUDE_BEYOND_EFT_SURVEY", STATUS_896),
    (897, "SPRINT_BC_PHASE2_CERTIFICATE", STATUS_897),
    (898, GATE_898, STATUS_898),
    (899, GATE_899, STATUS_899),
    (900, GATE_900, STATUS_900),
    (901, GATE_901, STATUS_901),
]
FRACTION_CLOSED: float = sum(status in {"RESOLVED", "PARTIAL"} for _, _, status in FERMION_PILLARS) / len(FERMION_PILLARS)
FRACTION_TENSION: float = sum(status == "TENSION_PERSISTS" for _, _, status in FERMION_PILLARS) / len(FERMION_PILLARS)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "FERMION_PILLARS",
    "FRACTION_CLOSED",
    "FRACTION_TENSION",
    "FERMION_CHAIN_GATE",
    "STATUS_LABEL",
    "fermion_chain_summary",
]


def fermion_chain_summary() -> dict[str, Any]:
    """Return the machine-readable fermion-sector chain summary."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": FERMION_CHAIN_GATE,
        "fermion_pillars": FERMION_PILLARS,
        "fraction_closed": FRACTION_CLOSED,
        "fraction_tension": FRACTION_TENSION,
        "epistemic_status": (
            "The fermion-sector chain is mixed: bookkeeping and ordering audits improved, but CKM/Jarlskog and charged-mass ratios retain open tension."
        ),
    }
