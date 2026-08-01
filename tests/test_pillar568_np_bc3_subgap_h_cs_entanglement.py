# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 568 — NP-BC-3 Sub-gap H: CS Entanglement Entropy Kernel."""
from __future__ import annotations

import math
import pytest
from pathlib import Path
from src.core.pillar568_np_bc3_subgap_h_cs_entanglement import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    QUANTUM_DIMENSION_LOWER_BOUND,
    REMAINING_GAPS,
    SUBGAP_H_STATUS,
    TOPOLOGICAL_ENTROPY_LOWER,
    VERSION,
    advancement_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_h_proof_state,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 568


def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC3_SUBGAP_H_CS_ENTANGLEMENT_KERNEL_PROVED"


def test_pillar_title_contains_subgap_h():
    assert "H" in PILLAR_TITLE or "Entanglement" in PILLAR_TITLE


def test_version():
    assert VERSION == "v19.4"


def test_quantum_dimension_lower_bound():
    assert QUANTUM_DIMENSION_LOWER_BOUND == 8


def test_quantum_dimension_bound_arithmetic():
    # 8² = 64 < 74 = k_CS, so D = √74 > 8
    assert QUANTUM_DIMENSION_LOWER_BOUND ** 2 < 74


def test_topological_entropy_lower_bound():
    # Should be ln(37)
    import math
    expected = math.log(37)
    assert abs(TOPOLOGICAL_ENTROPY_LOWER - expected) < 1e-10


def test_topological_entropy_positive():
    assert TOPOLOGICAL_ENTROPY_LOWER > 0


# ─── Lean4 file ───────────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC3SubgapH.lean not found at {path}"


def test_lean4_file_path_correct():
    assert "NPBC3SubgapH" in LEAN4_NEW_FILE["path"]


def test_lean4_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 11


def test_lean4_file_status():
    assert LEAN4_NEW_FILE["status"] == "CS_ENTANGLEMENT_KERNEL_PROVED"


def test_lean4_file_content_kcs():
    content = LEAN4_NEW_FILE["content"]
    assert "k_cs" in content.lower() or "74" in content or "37" in content


def test_lean4_file_content_entanglement():
    content = LEAN4_NEW_FILE["content"]
    assert "entanglement" in content.lower() or "entropy" in content.lower()


def test_lean4_file_honest_status_partially_closed():
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 228


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 11


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 217


def test_subgap_h_entry():
    assert LEAN4_THEOREM_COUNT["NPBC3SubgapH.lean"] == 11


def test_subgap_g_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC3SubgapG.lean"] == 11


def test_theorem_count_arithmetic():
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"] == LEAN4_THEOREM_COUNT["total"]


# ─── Sub-gap H status ─────────────────────────────────────────────────────────

def test_subgap_h_kernel_proved():
    assert SUBGAP_H_STATUS["kernel_proved"] is True


def test_subgap_h_full_closure_not_achieved():
    assert SUBGAP_H_STATUS["full_closure_achieved"] is False


def test_subgap_h_source_references_pillar_557():
    assert "557" in SUBGAP_H_STATUS["source"]


def test_subgap_h_advance_over_557():
    assert len(SUBGAP_H_STATUS["advance_over_pillar_557"]) > 20


# ─── Proved components ───────────────────────────────────────────────────────

def test_proved_components_count():
    components = proved_components()
    assert len(components) >= 9


def test_proved_components_all_proved():
    for c in proved_components():
        assert c["status"] == "PROVED"


def test_proved_components_has_cs_nontrivial():
    names = [c["name"] for c in proved_components()]
    assert any("k_cs" in n.lower() or "non-trivial" in n.lower() or "CS" in n for n in names)


def test_proved_components_has_quantum_dimension():
    names = [c["name"] for c in proved_components()]
    assert any("dimension" in n.lower() or "D" in n for n in names)


def test_proved_components_has_entropy_monotone():
    names = [c["name"] for c in proved_components()]
    assert any("entropy" in n.lower() or "monotone" in n.lower() for n in names)


def test_proved_components_has_even_level():
    names = [c["name"] for c in proved_components()]
    assert any("even" in n.lower() or "parity" in n.lower() for n in names)


def test_proved_components_has_wormhole_throat():
    names = [c["name"] for c in proved_components()]
    assert any("throat" in n.lower() or "37" in n or "half" in n.lower() for n in names)


def test_proved_components_has_summary():
    names = [c["name"] for c in proved_components()]
    assert any("summary" in n.lower() or "kernel" in n.lower() for n in names)


def test_proved_components_kcs_74_content():
    contents = [c["content"] for c in proved_components()]
    assert any("74" in c for c in contents)


# ─── Remaining gaps ───────────────────────────────────────────────────────────

def test_remaining_gaps_not_empty():
    gaps = remaining_gap_assessment()
    assert len(gaps) >= 1


def test_remaining_gaps_all_open():
    for gap in remaining_gap_assessment():
        assert gap["status"] == "OPEN"


def test_remaining_gaps_has_rt_formula():
    names = [g["name"] for g in remaining_gap_assessment()]
    assert any("ryu" in n.lower() or "rt" in n.lower() or "takayanagi" in n.lower() or "partition" in n.lower() for n in names)


def test_remaining_gaps_have_reason():
    for gap in remaining_gap_assessment():
        assert "reason" in gap


# ─── subgap_h_proof_state ────────────────────────────────────────────────────

def test_subgap_h_proof_state_subgap():
    state = subgap_h_proof_state()
    assert state["subgap"] == "H"


def test_subgap_h_proof_state_bc():
    state = subgap_h_proof_state()
    assert state["bc"] == "NP-BC-3"


def test_subgap_h_proof_state_status():
    state = subgap_h_proof_state()
    assert state["status"] == "NP_BC3_SUBGAP_H_CS_ENTANGLEMENT_KERNEL_PROVED"


def test_subgap_h_proof_state_kernel_proved():
    state = subgap_h_proof_state()
    assert state["kernel_proved"] is True


def test_subgap_h_proof_state_not_closed():
    state = subgap_h_proof_state()
    assert state["full_closure"] is False


def test_subgap_h_proof_state_theorems():
    state = subgap_h_proof_state()
    assert state["lean4_theorems"] == 11


def test_subgap_h_proof_state_quantum_dim():
    state = subgap_h_proof_state()
    assert state["quantum_dim_lower"] == 8


def test_subgap_h_proof_state_topological_entropy():
    state = subgap_h_proof_state()
    topo_entropy = state["topological_entropy_lower"]
    # Should be round(ln(37), 4)
    assert abs(topo_entropy - round(math.log(37), 4)) < 1e-6


# ─── advancement_certificate ─────────────────────────────────────────────────

def test_advancement_cert_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 568


def test_advancement_cert_subgap():
    cert = advancement_certificate()
    assert cert["subgap"] == "H"


def test_advancement_cert_bc():
    cert = advancement_certificate()
    assert cert["bc"] == "NP-BC-3"


def test_advancement_cert_theorems_added():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 11


def test_advancement_cert_total_theorems():
    cert = advancement_certificate()
    assert cert["total_lean4_theorems"] == 228


def test_advancement_cert_epistemic_delta_cs_entanglement():
    cert = advancement_certificate()
    assert "CS_ENTANGLEMENT_KERNEL_PROVED" in cert["epistemic_delta"]


def test_advancement_cert_not_closed():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "NOT" in not_claimed


def test_advancement_cert_erepr_not_proved():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "ER=EPR" in not_claimed


# ─── pillar_report ────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "lean4",
                "theorem_count", "subgap_h_status", "proved", "remaining", "certificate"]:
        assert key in report


def test_pillar_report_pillar_number():
    report = pillar_report()
    assert report["pillar"] == 568


def test_pillar_report_version():
    report = pillar_report()
    assert report["version"] == "v19.4"


def test_pillar_report_lean4_theorems():
    report = pillar_report()
    assert report["lean4"]["theorems"] == 11


def test_pillar_report_theorem_count_total():
    report = pillar_report()
    assert report["theorem_count"]["total"] == 228


def test_pillar_report_proved_list():
    report = pillar_report()
    assert isinstance(report["proved"], list)
    assert len(report["proved"]) >= 9


def test_pillar_report_remaining_list():
    report = pillar_report()
    assert isinstance(report["remaining"], list)
