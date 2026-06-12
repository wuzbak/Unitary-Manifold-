# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 524 — Full precision closure certificate v2.

Status: FULL_PRECISION_CLOSURE_CERTIFIED (🔵 ADJACENT TRACK)
"""

from __future__ import annotations

import pytest

from src.eleventd.full_precision_closure_v2 import (
    bridge_burn_status,
    full_precision_closure_v2_report,
    irreducible_gap_inventory,
)


# ── bridge_burn_status ────────────────────────────────────────────────────────


class TestBridgeBurnStatus:
    @pytest.fixture(scope="class")
    def status(self):
        return bridge_burn_status()

    def test_returns_dict(self, status):
        assert isinstance(status, dict)

    def test_pillar_is_245(self, status):
        assert status["pillar"] == 245

    def test_policy_present(self, status):
        assert len(status["policy"]) > 20

    def test_bridge_burn_key_present(self, status):
        assert "bridge_burn_confirmed" in status


# ── irreducible_gap_inventory ─────────────────────────────────────────────────


class TestIrreducibleGapInventory:
    @pytest.fixture(scope="class")
    def inventory(self):
        return irreducible_gap_inventory()

    def test_returns_dict(self, inventory):
        assert isinstance(inventory, dict)

    def test_label(self, inventory):
        assert inventory["label"] == "5D_IRREDUCIBLE_FLOOR"

    def test_gaps_count(self, inventory):
        assert inventory["count"] == 3
        assert len(inventory["gaps"]) == 3

    def test_cmb_amplitude_gap_present(self, inventory):
        ids = [g["id"] for g in inventory["gaps"]]
        assert "CMB_AMPLITUDE_IRREDUCIBLE" in ids

    def test_n_w_uniqueness_gap_present(self, inventory):
        ids = [g["id"] for g in inventory["gaps"]]
        assert "N_W_UNIQUENESS_IRREDUCIBLE" in ids

    def test_desi_wa_gap_present(self, inventory):
        ids = [g["id"] for g in inventory["gaps"]]
        assert "DESI_WA_TENSION" in ids

    def test_all_gaps_have_floor_label(self, inventory):
        for gap in inventory["gaps"]:
            assert gap["floor_label"] == "5D_IRREDUCIBLE_FLOOR"

    def test_note_present(self, inventory):
        assert "FALLIBILITY.md" in inventory["note"]


# ── full_precision_closure_v2_report (main) ───────────────────────────────────


class TestFullPrecisionClosureV2Report:
    @pytest.fixture(scope="class")
    def report(self):
        return full_precision_closure_v2_report()

    def test_pillar_number(self, report):
        assert report["pillar"] == 524

    def test_status(self, report):
        assert report["status"] == "FULL_PRECISION_CLOSURE_CERTIFIED"

    def test_track_label(self, report):
        assert "ADJACENT TRACK" in report["track"]

    def test_sprint_label(self, report):
        assert "v17.0" in report["sprint"]

    # Deliverable 1: Bridge burn
    def test_deliverable_1_bridge_burn(self, report):
        d1 = report["deliverables"]["1_bridge_burn"]
        assert d1["label"] == "Bridge burn confirmed"
        assert d1["pillar"] == 245

    # Deliverable 2: G4 Z_φ correction
    def test_deliverable_2_zphi_correction(self, report):
        d2 = report["deliverables"]["2_g4_zphi_correction"]
        assert d2["pillar"] == 519
        assert d2["zphi_nlo"] > d2["zphi_0"]
        assert d2["delta_zphi_g4"] > 0
        assert d2["pct_residual_resolved"] > 0

    # Deliverable 3: Moduli NLO seed
    def test_deliverable_3_moduli_seed(self, report):
        d3 = report["deliverables"]["3_moduli_nlo_seed"]
        assert d3["pillar"] == 521
        assert d3["pi_kr_nlo"] > 0
        assert d3["vol_cy3_nlo"] > 0
        assert d3["status"] == "CERTIFIED"

    # Deliverable 4: p_R conditional
    def test_deliverable_4_p_r(self, report):
        d4 = report["deliverables"]["4_p_r_conditional"]
        assert d4["pillar"] == 520
        assert d4["p_r_value"] > 0
        assert "CONDITIONAL_DERIVATION" in d4["status"]
        assert "521" in d4["open_condition"]

    # Deliverable 5: CMB amplitude partial closure
    def test_deliverable_5_cmb(self, report):
        d5 = report["deliverables"]["5_cmb_amplitude_partial_closure"]
        assert d5["pillar"] == 519
        assert d5["pct_resolved"] > 0
        assert d5["irreducible_floor"] == "5D_IRREDUCIBLE_FLOOR"
        assert d5["sigma_residual_nlo_pct"] < d5["sigma_residual_baseline_pct"]

    # Deliverable 6: Architecture limit upgrades
    def test_deliverable_6_upgrades(self, report):
        d6 = report["deliverables"]["6_architecture_limit_upgrades"]
        assert d6["pillar"] == 523
        assert d6["both_valid"] is True
        assert "ARCHITECTURE_LIMIT" in d6["p517_upgrade"]
        assert "CONDITIONAL_DERIVATION" in d6["p517_upgrade"]
        assert "ARCHITECTURE_LIMIT" in d6["p518_upgrade"]
        assert "PARTIAL_CLOSURE" in d6["p518_upgrade"]

    # Irreducible floors
    def test_irreducible_floor_inventory(self, report):
        floors = report["irreducible_floor_inventory"]
        assert floors["label"] == "5D_IRREDUCIBLE_FLOOR"
        assert floors["count"] == 3

    # Pipeline consistency
    def test_pipeline_consistency(self, report):
        assert report["pipeline_consistency"]["all_checks_pass"] is True

    # All steps certified
    def test_all_steps_certified(self, report):
        assert report["all_steps_certified"] is True

    # What 11D fixes / cannot fix
    def test_what_11d_fixes(self, report):
        assert len(report["what_11d_fixes"]) >= 4

    def test_what_11d_cannot_fix(self, report):
        assert len(report["what_11d_cannot_fix"]) >= 3

    def test_no_hardgate_score_change(self, report):
        assert report["no_hardgate_score_change"] is True

    def test_upstream_pillars(self, report):
        for p in [245, 355, 517, 518, 519, 520, 521, 522, 523]:
            assert p in report["upstream_pillars"]

    def test_next_sprint_slot(self, report):
        assert report["next_sprint_pillar_slot"] == 525

    def test_substack_post(self, report):
        assert "257" in report["substack_post"]

    def test_deterministic(self):
        r1 = full_precision_closure_v2_report()
        r2 = full_precision_closure_v2_report()
        assert (
            r1["deliverables"]["2_g4_zphi_correction"]["zphi_nlo"]
            == pytest.approx(r2["deliverables"]["2_g4_zphi_correction"]["zphi_nlo"])
        )
        assert (
            r1["deliverables"]["4_p_r_conditional"]["p_r_value"]
            == pytest.approx(r2["deliverables"]["4_p_r_conditional"]["p_r_value"])
        )
