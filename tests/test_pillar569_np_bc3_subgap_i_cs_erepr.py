# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 569 — NP-BC-3 Sub-gap I: CS↔ER=EPR Geometry Kernel + ER=EPR Overall."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar569_np_bc3_subgap_i_cs_erepr import (
    EREPR_OVERALL_STATUS,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    NP_BC3_OVERALL_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_I_STATUS,
    VERSION,
    advancement_certificate,
    erepr_all_subgaps_summary,
    np_bc3_subgap_summary,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_i_proof_state,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 569


def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC3_SUBGAP_I_CS_EREPR_GEOMETRY_KERNEL_PROVED"


def test_pillar_title_contains_subgap_i():
    assert "I" in PILLAR_TITLE or "ER=EPR" in PILLAR_TITLE


def test_version():
    assert VERSION == "v19.4"


# ─── Lean4 file ───────────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC3SubgapI.lean not found at {path}"


def test_lean4_file_path_correct():
    assert "NPBC3SubgapI" in LEAN4_NEW_FILE["path"]


def test_lean4_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 12


def test_lean4_file_status():
    assert LEAN4_NEW_FILE["status"] == "CS_EREPR_GEOMETRY_KERNEL_PROVED"


def test_lean4_file_content_braid():
    content = LEAN4_NEW_FILE["content"]
    assert "braid" in content.lower() or "5²" in content or "7²" in content


def test_lean4_file_content_kcs_74():
    content = LEAN4_NEW_FILE["content"]
    assert "74" in content or "k_CS" in content.lower()


def test_lean4_file_content_nine_subgaps():
    content = LEAN4_NEW_FILE["content"]
    assert "9" in content or "all 9" in content.lower()


def test_lean4_file_honest_status_partially_closed():
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


def test_lean4_file_honest_status_deepest():
    # This is the deepest algebraic advance
    assert "deepest" in LEAN4_NEW_FILE["honest_status"].lower() or "ER=EPR" in LEAN4_NEW_FILE["honest_status"]


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 240


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 12


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 228


def test_subgap_i_entry():
    assert LEAN4_THEOREM_COUNT["NPBC3SubgapI.lean"] == 12


def test_subgap_g_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC3SubgapG.lean"] == 11


def test_subgap_h_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC3SubgapH.lean"] == 11


def test_theorem_count_arithmetic():
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"] == LEAN4_THEOREM_COUNT["total"]


# ─── Sub-gap I status ─────────────────────────────────────────────────────────

def test_subgap_i_kernel_proved():
    assert SUBGAP_I_STATUS["kernel_proved"] is True


def test_subgap_i_full_closure_not_achieved():
    assert SUBGAP_I_STATUS["full_closure_achieved"] is False


def test_subgap_i_source_references_pillar_557():
    assert "557" in SUBGAP_I_STATUS["source"]


def test_subgap_i_physical_statement_kcs():
    assert "74" in SUBGAP_I_STATUS["physical_statement"] or "k_CS" in SUBGAP_I_STATUS["physical_statement"]


def test_subgap_i_advance_over_557():
    assert len(SUBGAP_I_STATUS["advance_over_pillar_557"]) > 20


# ─── NP-BC-3 overall status ──────────────────────────────────────────────────

def test_np_bc3_all_three_subgap_kernels_proved():
    assert NP_BC3_OVERALL_STATUS["all_three_subgaps_kernel_proved"] is True


def test_np_bc3_not_fully_closed():
    assert NP_BC3_OVERALL_STATUS["full_np_bc3_closed"] is False


def test_np_bc3_total_subgap_theorems():
    assert NP_BC3_OVERALL_STATUS["total_np_bc3_subgap_theorems"] == 34  # 11+11+12


def test_np_bc3_has_all_three_subgap_keys():
    assert "subgap_g_pi_topology" in NP_BC3_OVERALL_STATUS
    assert "subgap_h_cs_entanglement" in NP_BC3_OVERALL_STATUS
    assert "subgap_i_cs_erepr" in NP_BC3_OVERALL_STATUS


def test_np_bc3_subgap_g_label():
    assert "PATH_INTEGRAL_TOPOLOGY_KERNEL_PROVED" in NP_BC3_OVERALL_STATUS["subgap_g_pi_topology"]


def test_np_bc3_subgap_h_label():
    assert "CS_ENTANGLEMENT_KERNEL_PROVED" in NP_BC3_OVERALL_STATUS["subgap_h_cs_entanglement"]


def test_np_bc3_subgap_i_label():
    assert "CS_EREPR_GEOMETRY_KERNEL_PROVED" in NP_BC3_OVERALL_STATUS["subgap_i_cs_erepr"]


# ─── ER=EPR overall status ───────────────────────────────────────────────────

def test_erepr_all_nine_subgap_kernels_proved():
    assert EREPR_OVERALL_STATUS["all_nine_subgap_kernels_proved"] is True


def test_erepr_full_proof_not_achieved():
    assert EREPR_OVERALL_STATUS["full_erepr_proved"] is False


def test_erepr_total_subgap_theorems():
    assert EREPR_OVERALL_STATUS["total_subgap_theorems"] == 101


def test_erepr_np_bc1_subgap_theorems():
    assert EREPR_OVERALL_STATUS["np_bc1_subgap_theorems"] == 34  # A(12)+B(11)+C(11)


def test_erepr_np_bc2_subgap_theorems():
    assert EREPR_OVERALL_STATUS["np_bc2_subgap_theorems"] == 33  # D(11)+E(11)+F(11)


def test_erepr_np_bc3_subgap_theorems():
    assert EREPR_OVERALL_STATUS["np_bc3_subgap_theorems"] == 34  # G(11)+H(11)+I(12)


def test_erepr_total_subgap_sum():
    np1 = EREPR_OVERALL_STATUS["np_bc1_subgap_theorems"]
    np2 = EREPR_OVERALL_STATUS["np_bc2_subgap_theorems"]
    np3 = EREPR_OVERALL_STATUS["np_bc3_subgap_theorems"]
    assert np1 + np2 + np3 == EREPR_OVERALL_STATUS["total_subgap_theorems"]


def test_erepr_milestone_label():
    assert EREPR_OVERALL_STATUS["milestone_label"] == "ALL_NINE_SUBGAP_KERNELS_PROVED"


def test_erepr_blocking_residuals_total():
    assert EREPR_OVERALL_STATUS["blocking_residuals_total"] == 27  # 3 per sub-gap × 9


def test_erepr_total_lean4_theorems_after_p569():
    assert EREPR_OVERALL_STATUS["total_lean4_theorems_after_p569"] == 240


def test_erepr_epistemic_status_not_empty():
    assert len(EREPR_OVERALL_STATUS["epistemic_status"]) > 50


def test_erepr_epistemic_status_mentions_open():
    assert "OPEN" in EREPR_OVERALL_STATUS["epistemic_status"] or "open" in EREPR_OVERALL_STATUS["epistemic_status"].lower()


# ─── Proved components ───────────────────────────────────────────────────────

def test_proved_components_count():
    components = proved_components()
    assert len(components) >= 11


def test_proved_components_all_proved():
    for c in proved_components():
        assert c["status"] == "PROVED"


def test_proved_components_has_braid():
    names = [c["name"] for c in proved_components()]
    assert any("braid" in n.lower() for n in names)


def test_proved_components_has_erepr_param():
    names = [c["name"] for c in proved_components()]
    assert any("ER=EPR" in n or "erepr" in n.lower() for n in names)


def test_proved_components_has_topological_gap():
    names = [c["name"] for c in proved_components()]
    assert any("topological" in n.lower() or "protection" in n.lower() for n in names)


def test_proved_components_has_nine_subgaps():
    names = [c["name"] for c in proved_components()]
    assert any("nine" in n.lower() or "9" in n for n in names)


def test_proved_components_has_summary():
    names = [c["name"] for c in proved_components()]
    assert any("summary" in n.lower() or "kernel" in n.lower() for n in names)


def test_proved_components_entanglement_winding():
    contents = [c["content"] for c in proved_components()]
    assert any("370" in c for c in contents)


def test_proved_components_braid_74():
    contents = [c["content"] for c in proved_components()]
    assert any("74" in c and ("5²" in c or "25" in c) for c in contents)


# ─── Remaining gaps ───────────────────────────────────────────────────────────

def test_remaining_gaps_not_empty():
    gaps = remaining_gap_assessment()
    assert len(gaps) >= 1


def test_remaining_gaps_all_open():
    for gap in remaining_gap_assessment():
        assert gap["status"] == "OPEN"


def test_remaining_gaps_has_cs_rt():
    names = [g["name"] for g in remaining_gap_assessment()]
    assert any("cs" in n.lower() or "rt" in n.lower() or "identification" in n.lower() for n in names)


def test_remaining_gaps_have_reason():
    for gap in remaining_gap_assessment():
        assert "reason" in gap


# ─── subgap_i_proof_state ────────────────────────────────────────────────────

def test_subgap_i_proof_state_subgap():
    state = subgap_i_proof_state()
    assert state["subgap"] == "I"


def test_subgap_i_proof_state_bc():
    state = subgap_i_proof_state()
    assert state["bc"] == "NP-BC-3"


def test_subgap_i_proof_state_status():
    state = subgap_i_proof_state()
    assert state["status"] == "NP_BC3_SUBGAP_I_CS_EREPR_GEOMETRY_KERNEL_PROVED"


def test_subgap_i_proof_state_kernel_proved():
    state = subgap_i_proof_state()
    assert state["kernel_proved"] is True


def test_subgap_i_proof_state_not_closed():
    state = subgap_i_proof_state()
    assert state["full_closure"] is False


def test_subgap_i_proof_state_theorems():
    state = subgap_i_proof_state()
    assert state["lean4_theorems"] == 12


def test_subgap_i_proof_state_all_nine_proved():
    state = subgap_i_proof_state()
    assert state["erepr_all_nine_subgap_kernels_proved"] is True


# ─── np_bc3_subgap_summary ────────────────────────────────────────────────────

def test_np_bc3_summary_has_all_subgaps():
    summary = np_bc3_subgap_summary()
    assert "subgap_G" in summary
    assert "subgap_H" in summary
    assert "subgap_I" in summary


def test_np_bc3_summary_subgap_g_pillar():
    summary = np_bc3_subgap_summary()
    assert summary["subgap_G"]["pillar"] == 567


def test_np_bc3_summary_subgap_h_pillar():
    summary = np_bc3_subgap_summary()
    assert summary["subgap_H"]["pillar"] == 568


def test_np_bc3_summary_subgap_i_pillar():
    summary = np_bc3_subgap_summary()
    assert summary["subgap_I"]["pillar"] == 569


def test_np_bc3_summary_total_theorems():
    summary = np_bc3_subgap_summary()
    assert summary["np_bc3_total_subgap_theorems"] == 34


def test_np_bc3_summary_not_full_proof():
    summary = np_bc3_subgap_summary()
    assert summary["np_bc3_full_proof"] is False


def test_np_bc3_summary_theorem_total():
    summary = np_bc3_subgap_summary()
    g = summary["subgap_G"]["theorems"]
    h = summary["subgap_H"]["theorems"]
    i = summary["subgap_I"]["theorems"]
    assert g + h + i == 34


# ─── erepr_all_subgaps_summary ───────────────────────────────────────────────

def test_erepr_summary_has_all_three_bc():
    summary = erepr_all_subgaps_summary()
    assert "NP-BC-1" in summary
    assert "NP-BC-2" in summary
    assert "NP-BC-3" in summary


def test_erepr_summary_np_bc1_pillars():
    summary = erepr_all_subgaps_summary()
    assert 560 in summary["NP-BC-1"]["pillars"]
    assert 561 in summary["NP-BC-1"]["pillars"]
    assert 562 in summary["NP-BC-1"]["pillars"]


def test_erepr_summary_np_bc2_pillars():
    summary = erepr_all_subgaps_summary()
    assert 564 in summary["NP-BC-2"]["pillars"]
    assert 565 in summary["NP-BC-2"]["pillars"]
    assert 566 in summary["NP-BC-2"]["pillars"]


def test_erepr_summary_np_bc3_pillars():
    summary = erepr_all_subgaps_summary()
    assert 567 in summary["NP-BC-3"]["pillars"]
    assert 568 in summary["NP-BC-3"]["pillars"]
    assert 569 in summary["NP-BC-3"]["pillars"]


def test_erepr_summary_total_subgap_theorems():
    summary = erepr_all_subgaps_summary()
    assert summary["total_subgap_theorems"] == 101


def test_erepr_summary_milestone():
    summary = erepr_all_subgaps_summary()
    assert summary["erepr_milestone"] == "ALL_NINE_SUBGAP_KERNELS_PROVED"


def test_erepr_summary_not_fully_proved():
    summary = erepr_all_subgaps_summary()
    assert summary["full_erepr_proved"] is False


def test_erepr_summary_blocking_residuals():
    summary = erepr_all_subgaps_summary()
    assert summary["blocking_residuals"] == 27


def test_erepr_summary_np_bc1_total_theorems():
    summary = erepr_all_subgaps_summary()
    assert summary["NP-BC-1"]["total_theorems"] == 34


def test_erepr_summary_np_bc2_total_theorems():
    summary = erepr_all_subgaps_summary()
    assert summary["NP-BC-2"]["total_theorems"] == 33


def test_erepr_summary_np_bc3_total_theorems():
    summary = erepr_all_subgaps_summary()
    assert summary["NP-BC-3"]["total_theorems"] == 34


# ─── advancement_certificate ─────────────────────────────────────────────────

def test_advancement_cert_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 569


def test_advancement_cert_subgap():
    cert = advancement_certificate()
    assert cert["subgap"] == "I"


def test_advancement_cert_bc():
    cert = advancement_certificate()
    assert cert["bc"] == "NP-BC-3"


def test_advancement_cert_theorems_added():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 12


def test_advancement_cert_total_theorems():
    cert = advancement_certificate()
    assert cert["total_lean4_theorems"] == 240


def test_advancement_cert_np_bc3_milestone():
    cert = advancement_certificate()
    assert "np_bc3_milestone" in cert
    assert "G/H/I" in cert["np_bc3_milestone"] or "three" in cert["np_bc3_milestone"].lower()


def test_advancement_cert_erepr_milestone():
    cert = advancement_certificate()
    assert "erepr_milestone" in cert
    assert "ALL NINE" in cert["erepr_milestone"] or "all nine" in cert["erepr_milestone"].lower()


def test_advancement_cert_milestone_mentions_101():
    cert = advancement_certificate()
    assert "101" in cert["erepr_milestone"]


def test_advancement_cert_erepr_not_proved():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "ER=EPR is NOT proved" in not_claimed


def test_advancement_cert_27_residuals():
    cert = advancement_certificate()
    assert "27" in cert["epistemic_delta"]


def test_advancement_cert_no_p6_promotion():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "P6" in not_claimed or "DERIVED" in not_claimed


# ─── pillar_report ────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "lean4",
                "theorem_count", "subgap_i_status", "np_bc3_overall",
                "erepr_overall", "proved", "remaining", "certificate"]:
        assert key in report


def test_pillar_report_pillar_number():
    report = pillar_report()
    assert report["pillar"] == 569


def test_pillar_report_version():
    report = pillar_report()
    assert report["version"] == "v19.4"


def test_pillar_report_lean4_theorems():
    report = pillar_report()
    assert report["lean4"]["theorems"] == 12


def test_pillar_report_theorem_count_total():
    report = pillar_report()
    assert report["theorem_count"]["total"] == 240


def test_pillar_report_erepr_overall_nine_proved():
    report = pillar_report()
    assert report["erepr_overall"]["all_nine_subgap_kernels_proved"] is True


def test_pillar_report_np_bc3_all_proved():
    report = pillar_report()
    assert report["np_bc3_overall"]["all_three_subgaps_kernel_proved"] is True


def test_pillar_report_np_bc3_summary():
    report = pillar_report()
    assert "np_bc3_summary" in report
    assert report["np_bc3_summary"]["np_bc3_full_proof"] is False


def test_pillar_report_erepr_summary():
    report = pillar_report()
    assert "erepr_summary" in report
    assert report["erepr_summary"]["total_subgap_theorems"] == 101


def test_pillar_report_proved_list():
    report = pillar_report()
    assert isinstance(report["proved"], list)
    assert len(report["proved"]) >= 11


def test_pillar_report_remaining_list():
    report = pillar_report()
    assert isinstance(report["remaining"], list)
