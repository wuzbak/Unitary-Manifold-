# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 534 — JUNO Phase 2 Pre-Registration + v18.0 Sprint Gate."""

from __future__ import annotations

import math
import pytest

from src.core.juno_phase2_preregistration import (
    JUNO_PHASE2_DM21_PRECISION_PCT,
    JUNO_PHASE2_DM31_PRECISION_PCT,
    JUNO_PHASE2_NMO_SIGMA_TARGET,
    JUNO_PHASE2_SIN2THETA12_PRECISION_PCT,
    PDG_DM21,
    PDG_DM31,
    PDG_SIN2THETA12,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SPRINT_V18_GATE,
    UM_DM21_PRED,
    UM_DM31_NLO,
    UM_MASS_ORDERING,
    UM_SIN2THETA12_VACUUM,
    phase2_dm21_verdict,
    phase2_dm31_verdict,
    phase2_nmo_verdict,
    phase2_sin2theta12_verdict,
    pillar534_report,
    preregistration_hash,
    sprint_v18_gate,
)


# ── Metadata ───────────────────────────────────────────────────────────────────

class TestPillarMetadata:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 534

    def test_status(self):
        assert PILLAR_STATUS == "JUNO_PHASE2_PREREGISTERED"

    def test_title_contains_juno(self):
        assert "JUNO" in PILLAR_TITLE

    def test_title_contains_phase2(self):
        assert "Phase 2" in PILLAR_TITLE or "Sprint" in PILLAR_TITLE


# ── Constants ──────────────────────────────────────────────────────────────────

class TestConstants:
    def test_dm31_nlo_eV2(self):
        # UM NLO prediction consistent with PDG within 1%
        assert abs(UM_DM31_NLO - PDG_DM31) / PDG_DM31 < 0.01

    def test_dm21_pred_eV2(self):
        # Within 1% of PDG
        assert abs(UM_DM21_PRED - PDG_DM21) / PDG_DM21 < 0.01

    def test_sin2theta12_vacuum_range(self):
        # Physical range (0, 1)
        assert 0 < UM_SIN2THETA12_VACUUM < 1

    def test_sin2theta12_roughly_pdg(self):
        # Within 5% of PDG solar+reactor global fit
        assert abs(UM_SIN2THETA12_VACUUM - PDG_SIN2THETA12) / PDG_SIN2THETA12 < 0.05

    def test_mass_ordering_normal(self):
        assert UM_MASS_ORDERING == "NORMAL"

    def test_phase2_dm31_precision_pct(self):
        assert JUNO_PHASE2_DM31_PRECISION_PCT == pytest.approx(0.5)

    def test_phase2_dm21_precision_pct(self):
        assert JUNO_PHASE2_DM21_PRECISION_PCT == pytest.approx(0.5)

    def test_phase2_sin2theta12_precision_pct(self):
        assert JUNO_PHASE2_SIN2THETA12_PRECISION_PCT == pytest.approx(1.0)

    def test_nmo_sigma_target(self):
        assert JUNO_PHASE2_NMO_SIGMA_TARGET == pytest.approx(3.0)

    def test_pdg_dm31_eV2(self):
        # PDG 2024 value within 5% of rough order-of-magnitude (2.4e-3)
        assert 2.0e-3 < PDG_DM31 < 3.0e-3

    def test_pdg_dm21_eV2(self):
        assert 7.0e-5 < PDG_DM21 < 8.0e-5

    def test_pdg_sin2theta12(self):
        assert 0.25 < PDG_SIN2THETA12 < 0.40


# ── Phase 2 Δm²₃₁ verdict ─────────────────────────────────────────────────────

class TestPhase2DM31Verdict:
    def setup_method(self):
        self.v = phase2_dm31_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_observable(self):
        assert self.v["observable"] == "delta_m31_sq"

    def test_um_prediction(self):
        assert self.v["um_prediction_eV2"] == pytest.approx(UM_DM31_NLO)

    def test_pdg_reference(self):
        assert self.v["pdg_reference_eV2"] == pytest.approx(PDG_DM31)

    def test_sigma_is_float(self):
        assert isinstance(self.v["sigma_expected"], float)

    def test_sigma_positive(self):
        assert self.v["sigma_expected"] >= 0

    def test_safe(self):
        # NLO prediction should be very close to PDG → safe at Phase 2 precision
        assert self.v["safe"] is True

    def test_verdict_safe(self):
        assert self.v["verdict"] == "SAFE"

    def test_sigma_below_1(self):
        # |2.452 - 2.453| / (0.005 × 2.453) ≈ 0.08σ
        assert self.v["sigma_expected"] < 1.0

    def test_note_is_string(self):
        assert isinstance(self.v["note"], str)


# ── Phase 2 Δm²₂₁ verdict ─────────────────────────────────────────────────────

class TestPhase2DM21Verdict:
    def setup_method(self):
        self.v = phase2_dm21_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_observable(self):
        assert self.v["observable"] == "delta_m21_sq"

    def test_sigma_positive(self):
        assert self.v["sigma_expected"] >= 0

    def test_verdict_is_safe_or_tension(self):
        assert self.v["verdict"] in ("SAFE", "HIGH_TENSION")

    def test_sigma_below_2(self):
        # Prediction is within ~0.4% of PDG → expect < 2σ at 0.5% precision
        assert self.v["sigma_expected"] < 2.0

    def test_safe(self):
        assert self.v["safe"] is True

    def test_note_string(self):
        assert isinstance(self.v["note"], str)


# ── Phase 2 sin²θ₁₂ verdict ───────────────────────────────────────────────────

class TestPhase2Sin2Theta12Verdict:
    def setup_method(self):
        self.v = phase2_sin2theta12_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_observable(self):
        assert self.v["observable"] == "sin2_theta12_reactor"

    def test_um_prediction(self):
        assert self.v["um_prediction_vacuum"] == pytest.approx(UM_SIN2THETA12_VACUUM)

    def test_sigma_positive(self):
        assert self.v["sigma_expected"] >= 0

    def test_verdict_is_string(self):
        assert isinstance(self.v["verdict"], str)

    def test_sigma_below_3(self):
        # Vacuum vs global fit; reactor measurement agrees better with vacuum → safe
        assert self.v["sigma_expected"] < 3.0

    def test_note_mentions_msw(self):
        assert "MSW" in self.v["note"] or "solar" in self.v["note"].lower()


# ── NMO verdict ────────────────────────────────────────────────────────────────

class TestPhase2NMOVerdict:
    def setup_method(self):
        self.v = phase2_nmo_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_observable(self):
        assert self.v["observable"] == "neutrino_mass_ordering"

    def test_um_predicts_normal(self):
        assert self.v["um_prediction"] == "NORMAL"

    def test_basis_mentions_pillar60(self):
        assert "60" in self.v["um_basis"] or "9D" in self.v["um_basis"]

    def test_phase1_signal_positive(self):
        assert self.v["juno_phase1_signal_sigma"] > 0

    def test_phase1_consistent_with_nmo(self):
        assert "CONSISTENT" in self.v["current_status"]

    def test_falsification_condition_present(self):
        assert isinstance(self.v["falsification_condition"], str)
        assert len(self.v["falsification_condition"]) > 20

    def test_falsification_mentions_inverted(self):
        assert "nverted" in self.v["falsification_condition"]  # "Inverted"

    def test_verdict(self):
        assert self.v["verdict"] == "NORMAL_ORDERING_PREDICTED"


# ── Sprint gate ────────────────────────────────────────────────────────────────

class TestSprintGate:
    def test_sprint_v18_gate_list(self):
        assert isinstance(SPRINT_V18_GATE, list)
        assert len(SPRINT_V18_GATE) >= 8

    def test_all_gate_items_have_status(self):
        for check in SPRINT_V18_GATE:
            assert "status" in check

    def test_all_consistent(self):
        for check in SPRINT_V18_GATE:
            assert check["status"] == "CONSISTENT", f"Gate check failed: {check['check']}"

    def test_gate_checks_cover_sprint_range(self):
        pillars_referenced = set()
        for c in SPRINT_V18_GATE:
            pillars_referenced.add(c["from_pillar"])
            pillars_referenced.add(c["to_pillar"])
        # All referenced pillars should be within v18.0 sprint
        for p in pillars_referenced:
            assert 525 <= p <= 535

    def test_sprint_v18_gate_function(self):
        g = sprint_v18_gate()
        assert isinstance(g, dict)
        assert g["sprint"] == "v18.0"
        assert g["all_consistent"] is True
        assert g["gate_status"] == "GATE_PASSED"
        assert g["toe_score"] == "28/28"
        assert g["hardgate_lanes"] == "UNCHANGED"

    def test_sprint_pillars_range(self):
        g = sprint_v18_gate()
        assert 525 in g["pillars"]
        assert 535 in g["pillars"]
        assert 534 in g["pillars"]

    def test_n_checks(self):
        g = sprint_v18_gate()
        assert g["n_checks"] == g["n_passed"]

    def test_gate_descriptions_nonempty(self):
        for c in SPRINT_V18_GATE:
            assert len(c["description"]) > 5


# ── Pre-registration hash ──────────────────────────────────────────────────────

class TestPreregistrationHash:
    def test_returns_string(self):
        h = preregistration_hash()
        assert isinstance(h, str)

    def test_length_64(self):
        # SHA-256 hex digest = 64 characters
        assert len(preregistration_hash()) == 64

    def test_deterministic(self):
        assert preregistration_hash() == preregistration_hash()

    def test_hex_only(self):
        import re
        assert re.match(r"^[0-9a-f]{64}$", preregistration_hash())


# ── Full report ────────────────────────────────────────────────────────────────

class TestPillar534Report:
    def setup_method(self):
        self.r = pillar534_report()

    def test_returns_dict(self):
        assert isinstance(self.r, dict)

    def test_pillar_number(self):
        assert self.r["pillar"] == 534

    def test_status(self):
        assert self.r["status"] == "JUNO_PHASE2_PREREGISTERED"

    def test_phase2_verdicts_present(self):
        assert "phase2_verdicts" in self.r
        verdicts = self.r["phase2_verdicts"]
        assert "dm31" in verdicts
        assert "dm21" in verdicts
        assert "sin2theta12" in verdicts
        assert "nmo" in verdicts

    def test_all_phase2_safe(self):
        assert self.r["all_phase2_safe"] is True

    def test_sprint_gate_present(self):
        assert "sprint_gate" in self.r
        assert self.r["gate_status"] == "GATE_PASSED"

    def test_preregistration_hash_present(self):
        assert "preregistration_sha256" in self.r
        assert len(self.r["preregistration_sha256"]) == 64

    def test_dm31_safe(self):
        assert self.r["phase2_verdicts"]["dm31"]["safe"] is True

    def test_dm21_safe(self):
        assert self.r["phase2_verdicts"]["dm21"]["safe"] is True

    def test_nmo_normal(self):
        assert self.r["phase2_verdicts"]["nmo"]["um_prediction"] == "NORMAL"
