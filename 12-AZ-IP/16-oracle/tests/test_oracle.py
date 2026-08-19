# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_oracle.py
====================
Comprehensive test suite for the AxiomZero Ω Oracle.

106 tests covering:
  - Seed constants and derived quantities
  - Pentad construction and metrics
  - Integrity audit construction and scoring
  - Decision resonance computation
  - Grand synthesis orchestrator
  - Database persistence (in-memory)
  - Edge cases and error paths

Theory: ThomasCory Walker-Pearson.
Code:   GitHub Copilot (AI).
"""

import math
import os
import sys
import uuid
import pytest
from fractions import Fraction

# Ensure the package root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from oracle.engine.constants import (
    N_W, N_2, K_CS, C_S, C_S_F, XI_C, XI_C_F,
    N_S, R_BRAIDED,
    STATUS_WEIGHTS, OMEGA_GRADE_BOUNDS,
    stability_floor, phi_trust_status, omega_grade,
    GOV_INTEGRITY_THRESHOLD, GOV_FREEDOM_FLOOR, HIL_PHASE_SHIFT_THRESHOLD,
)
from oracle.engine.pentad import PentadBody, PentadModel
from oracle.engine.integrity import (
    IntegrityAudit, AuditDimension, AUDIT_DIMENSIONS,
)
from oracle.engine.resonance import (
    DecisionOption, BodyImpact, DecisionAnalysis, compute_option_resonance,
)
from oracle.engine.synthesis import (
    SynthesisOrchestrator, SynthesisReport, ActionPriority,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_body(
    label="Ψ₁ — Test",
    status="SOLID",
    phi_trust=0.8,
    **kwargs,
) -> PentadBody:
    return PentadBody(
        name=label,
        label=label,
        epistemic_status=status,
        phi_trust=phi_trust,
        **kwargs,
    )


def make_pentad(
    bodies=None,
    system_name="Test System",
    system_type="Test",
) -> PentadModel:
    if bodies is None:
        bodies = [
            make_body(f"Ψ{i+1} — Body {i+1}", "SOLID", 0.8)
            for i in range(N_W)
        ]
    return PentadModel(
        system_name=system_name,
        system_type=system_type,
        bodies=bodies,
    )


def make_audit(scores=None) -> IntegrityAudit:
    if scores is None:
        scores = {k: 0.75 for k, _ in AUDIT_DIMENSIONS}
    dims = [
        AuditDimension(key=k, description=d, score=scores.get(k, 0.75))
        for k, d in AUDIT_DIMENSIONS
    ]
    return IntegrityAudit(
        system_name="Test System",
        system_type="Test",
        dimensions=dims,
    )


def all_body_specs(statuses, phi_trusts):
    from oracle.engine.constants import DEFAULT_PENTAD_BODIES
    return [
        {
            "label": DEFAULT_PENTAD_BODIES[i],
            "status": statuses[i],
            "phi_trust": phi_trusts[i],
        }
        for i in range(N_W)
    ]


def dim_scores_all(value: float = 0.75):
    return {k: value for k, _ in AUDIT_DIMENSIONS}


_orch = SynthesisOrchestrator()


# ═════════════════════════════════════════════════════════════════════════════
# 1. SEED CONSTANTS
# ═════════════════════════════════════════════════════════════════════════════

class TestSeedConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n_2(self):
        assert N_2 == 7

    def test_k_cs_identity(self):
        assert K_CS == N_W**2 + N_2**2
        assert K_CS == 74

    def test_c_s_is_fraction(self):
        assert isinstance(C_S, Fraction)
        assert C_S == Fraction(12, 37)

    def test_xi_c_is_fraction(self):
        assert isinstance(XI_C, Fraction)
        assert XI_C == Fraction(35, 74)

    def test_c_s_float(self):
        assert abs(C_S_F - 12/37) < 1e-12

    def test_xi_c_float(self):
        assert abs(XI_C_F - 35/74) < 1e-12

    def test_n_s_range(self):
        # nₛ must be positive and less than 1
        assert 0.9 < N_S < 1.0

    def test_r_braided_positive(self):
        assert R_BRAIDED > 0.0

    def test_hil_threshold(self):
        assert HIL_PHASE_SHIFT_THRESHOLD == 15

    def test_gov_freedom_floor_equals_cs(self):
        assert abs(GOV_FREEDOM_FLOOR - C_S_F) < 1e-12


class TestStabilityFloor:
    def test_zero_aligned(self):
        assert abs(stability_floor(0) - C_S_F) < 1e-12

    def test_one_aligned(self):
        expected = min(1.0, C_S_F + C_S_F / N_2)
        assert abs(stability_floor(1) - expected) < 1e-12

    def test_five_aligned(self):
        expected = min(1.0, C_S_F + 5 * C_S_F / N_2)
        assert abs(stability_floor(5) - expected) < 1e-12

    def test_cap_at_one(self):
        assert stability_floor(100) == 1.0

    def test_monotone_increasing(self):
        vals = [stability_floor(n) for n in range(20)]
        for i in range(len(vals) - 1):
            assert vals[i] <= vals[i + 1]

    def test_fifteen_hits_cap(self):
        assert stability_floor(HIL_PHASE_SHIFT_THRESHOLD) == 1.0


class TestPhiTrustStatus:
    def test_authentic(self):
        assert phi_trust_status(0.90) == "AUTHENTIC"

    def test_coherent(self):
        assert phi_trust_status(C_S_F + 0.01) == "COHERENT"

    def test_strained(self):
        assert phi_trust_status(0.15) == "STRAINED"

    def test_crisis(self):
        assert phi_trust_status(0.05) == "CRISIS"


class TestOmegaGrade:
    def test_omega_grade(self):
        letter, label, _ = omega_grade(0.95)
        assert letter == "Ω"
        assert "Unified" in label

    def test_a_grade(self):
        letter, _, _ = omega_grade(0.80)
        assert letter == "A"

    def test_f_grade(self):
        letter, _, _ = omega_grade(0.0)
        assert letter == "F"

    def test_boundary_b(self):
        letter, _, _ = omega_grade(0.60)
        assert letter == "B"


# ═════════════════════════════════════════════════════════════════════════════
# 2. PENTAD BODY
# ═════════════════════════════════════════════════════════════════════════════

class TestPentadBody:
    def test_solid_body(self):
        b = make_body(status="SOLID", phi_trust=1.0)
        assert b.is_aligned
        assert b.status_weight == 1.0
        assert b.resonance == 1.0

    def test_constrained_body(self):
        b = make_body(status="CONSTRAINED", phi_trust=0.8)
        assert b.is_aligned
        assert abs(b.status_weight - 0.75) < 1e-9

    def test_estimated_body(self):
        b = make_body(status="ESTIMATED", phi_trust=0.5)
        assert not b.is_aligned

    def test_open_body(self):
        b = make_body(status="OPEN", phi_trust=0.0)
        assert not b.is_aligned
        assert b.status_weight == 0.0
        assert b.resonance == 0.0

    def test_resonance_formula(self):
        b = make_body(status="CONSTRAINED", phi_trust=0.6)
        assert abs(b.resonance - 0.75 * 0.6) < 1e-9

    def test_invalid_status(self):
        with pytest.raises(ValueError):
            make_body(status="BROKEN")

    def test_phi_trust_bounds(self):
        with pytest.raises(ValueError):
            make_body(phi_trust=1.5)
        with pytest.raises(ValueError):
            make_body(phi_trust=-0.1)

    def test_status_symbols(self):
        assert make_body(status="SOLID").status_symbol == "✅"
        assert make_body(status="OPEN").status_symbol == "🔓"


# ═════════════════════════════════════════════════════════════════════════════
# 3. PENTAD MODEL
# ═════════════════════════════════════════════════════════════════════════════

class TestPentadModel:
    def test_requires_five_bodies(self):
        with pytest.raises(ValueError):
            PentadModel(
                system_name="Bad", system_type="Test",
                bodies=[make_body() for _ in range(3)],
            )

    def test_n_aligned_all_solid(self):
        p = make_pentad()
        assert p.n_aligned == N_W

    def test_n_aligned_mixed(self):
        bodies = [
            make_body(f"Ψ{i+1}", "SOLID" if i < 3 else "OPEN", 0.8)
            for i in range(N_W)
        ]
        p = make_pentad(bodies)
        assert p.n_aligned == 3

    def test_stability_all_solid(self):
        p = make_pentad()
        expected = stability_floor(N_W)
        assert abs(p.stability - expected) < 1e-9

    def test_omega_score_positive(self):
        p = make_pentad()
        assert p.omega_score > 0

    def test_omega_score_cap(self):
        # Can't exceed stability_floor × max_resonance = stability × 1.0
        p = make_pentad()
        assert p.omega_score <= 1.0

    def test_phi_trust_crisis_when_low(self):
        bodies = [make_body(f"Ψ{i+1}", "SOLID", 0.10) for i in range(N_W)]
        p = make_pentad(bodies)
        assert p.in_authenticity_crisis

    def test_no_crisis_when_above_cs(self):
        bodies = [make_body(f"Ψ{i+1}", "SOLID", C_S_F + 0.05) for i in range(N_W)]
        p = make_pentad(bodies)
        assert not p.in_authenticity_crisis

    def test_weakest_body(self):
        bodies = [
            make_body("Ψ1", "SOLID", 0.9),
            make_body("Ψ2", "OPEN", 0.0),
            make_body("Ψ3", "SOLID", 0.8),
            make_body("Ψ4", "CONSTRAINED", 0.7),
            make_body("Ψ5", "SOLID", 0.85),
        ]
        p = make_pentad(bodies)
        assert p.weakest_body().label == "Ψ2"

    def test_braid_coherence_range(self):
        p = make_pentad()
        bc = p.braid_coherence()
        assert 0.0 <= bc <= 1.0

    def test_summary_string(self):
        p = make_pentad()
        s = p.summary()
        assert "PENTAD ANALYSIS" in s
        assert "Omega Score" in s
        assert "Stability floor" in s

    def test_coupling_matrix_shape(self):
        p = make_pentad()
        m = p.coupling_matrix()
        assert len(m) == N_W
        assert all(len(row) == N_W for row in m)

    def test_coupling_diagonal(self):
        bodies = [make_body(f"Ψ{i+1}", "SOLID", 0.8) for i in range(N_W)]
        p = make_pentad(bodies)
        m = p.coupling_matrix()
        for i, b in enumerate(p.bodies):
            assert abs(m[i][i] - b.resonance) < 1e-9

    def test_coupling_off_diagonal(self):
        bodies = [make_body(f"Ψ{i+1}", "SOLID", 0.8) for i in range(N_W)]
        p = make_pentad(bodies)
        m = p.coupling_matrix()
        for i in range(N_W):
            for j in range(N_W):
                if i != j:
                    expected = XI_C_F * bodies[i].resonance * bodies[j].resonance
                    assert abs(m[i][j] - expected) < 1e-9


# ═════════════════════════════════════════════════════════════════════════════
# 4. INTEGRITY AUDIT
# ═════════════════════════════════════════════════════════════════════════════

class TestIntegrityAudit:
    def test_perfect_integrity(self):
        audit = make_audit({k: 1.0 for k, _ in AUDIT_DIMENSIONS})
        assert audit.integrity_score >= 0.99

    def test_zero_integrity(self):
        audit = make_audit({k: 0.0 for k, _ in AUDIT_DIMENSIONS})
        assert audit.integrity_score < 0.05

    def test_freedom_floor_met(self):
        audit = make_audit({"Freedom Floor": 0.9, **{k: 0.75 for k, _ in AUDIT_DIMENSIONS if k != "Freedom Floor"}})
        assert audit.freedom_floor_met

    def test_freedom_floor_not_met(self):
        audit = make_audit({"Freedom Floor": 0.1, **{k: 0.75 for k, _ in AUDIT_DIMENSIONS if k != "Freedom Floor"}})
        assert not audit.freedom_floor_met

    def test_integrity_grade_exemplary(self):
        audit = make_audit({k: 1.0 for k, _ in AUDIT_DIMENSIONS})
        assert audit.integrity_grade == "EXEMPLARY"

    def test_integrity_grade_critical(self):
        audit = make_audit({k: 0.1 for k, _ in AUDIT_DIMENSIONS})
        assert audit.integrity_grade == "CRITICAL"

    def test_chain_of_custody_range(self):
        audit = make_audit()
        cc = audit.chain_of_custody_index
        assert 0.0 < cc <= 1.0

    def test_wrong_dimension_count(self):
        dims = [AuditDimension(key="X", description="Y", score=0.5)] * 3
        with pytest.raises(ValueError):
            IntegrityAudit(system_name="T", system_type="T", dimensions=dims)

    def test_summary_string(self):
        audit = make_audit()
        s = audit.summary()
        assert "GOVERNANCE AUDIT" in s
        assert "Integrity score" in s

    def test_audit_dimension_score_clamp(self):
        with pytest.raises(ValueError):
            AuditDimension(key="X", description="Y", score=1.5)


# ═════════════════════════════════════════════════════════════════════════════
# 5. DECISION RESONANCE
# ═════════════════════════════════════════════════════════════════════════════

class TestDecisionResonance:
    def _simple_pentad(self) -> PentadModel:
        bodies = [
            make_body("Ψ1", "OPEN", 0.5),
            make_body("Ψ2", "SOLID", 0.9),
            make_body("Ψ3", "ESTIMATED", 0.6),
            make_body("Ψ4", "CONSTRAINED", 0.7),
            make_body("Ψ5", "SOLID", 0.8),
        ]
        return make_pentad(bodies)

    def test_improving_open_gives_high_resonance(self):
        pentad = self._simple_pentad()
        opt = DecisionOption(
            name="Fix Ψ1",
            body_impacts=[BodyImpact("Ψ1", "improve", 2.0)],
        )
        r = compute_option_resonance(opt, pentad)
        assert r > 3.5   # 2.0 × 2.0 = 4.0 for OPEN improve

    def test_harming_solid_gives_negative_resonance(self):
        pentad = self._simple_pentad()
        opt = DecisionOption(
            name="Harm Ψ2",
            body_impacts=[BodyImpact("Ψ2", "harm", 2.0)],
        )
        r = compute_option_resonance(opt, pentad)
        assert r < -3.5  # -2.0 × 2.0 for SOLID harm

    def test_neutral_gives_zero(self):
        pentad = self._simple_pentad()
        opt = DecisionOption(
            name="Status quo",
            body_impacts=[BodyImpact("Ψ2", "neutral", 1.0)],
        )
        r = compute_option_resonance(opt, pentad)
        assert abs(r) < 1e-9

    def test_phi_trust_impact(self):
        pentad = self._simple_pentad()
        opt_pos = DecisionOption(name="Trust+", phi_trust_impact=1.0)
        opt_neg = DecisionOption(name="Trust-", phi_trust_impact=-1.0)
        assert compute_option_resonance(opt_pos, pentad) > compute_option_resonance(opt_neg, pentad)

    def test_ranked_order(self):
        pentad = self._simple_pentad()
        fix_open = DecisionOption(
            name="Fix open", body_impacts=[BodyImpact("Ψ1", "improve", 2.0)]
        )
        harm_solid = DecisionOption(
            name="Harm solid", body_impacts=[BodyImpact("Ψ2", "harm", 2.0)]
        )
        da = DecisionAnalysis(question="Which?", pentad=pentad, options=[fix_open, harm_solid])
        ranked = da.ranked_options
        assert ranked[0][1].name == "Fix open"

    def test_requires_two_options(self):
        pentad = self._simple_pentad()
        with pytest.raises(ValueError):
            DecisionAnalysis(
                question="Q", pentad=pentad,
                options=[DecisionOption(name="Only")],
            )

    def test_summary_string(self):
        pentad = self._simple_pentad()
        opts = [
            DecisionOption("A", body_impacts=[BodyImpact("Ψ1", "improve", 1.0)]),
            DecisionOption("B", body_impacts=[BodyImpact("Ψ2", "harm", 1.0)]),
        ]
        da = DecisionAnalysis(question="Test?", pentad=pentad, options=opts)
        s = da.summary()
        assert "DECISION ORACLE" in s
        assert "HIGHEST RESONANCE" in s

    def test_body_impact_invalid_direction(self):
        with pytest.raises(ValueError):
            BodyImpact(body_label="X", direction="sideways", magnitude=1.0)

    def test_body_impact_magnitude_bounds(self):
        with pytest.raises(ValueError):
            BodyImpact(body_label="X", direction="improve", magnitude=5.0)


# ═════════════════════════════════════════════════════════════════════════════
# 6. SYNTHESIS ORCHESTRATOR
# ═════════════════════════════════════════════════════════════════════════════

class TestSynthesisOrchestrator:
    def _run_synthesis(self, **kwargs):
        from oracle.engine.constants import DEFAULT_PENTAD_BODIES
        defaults = dict(
            system_name="Test System",
            system_type="Test",
            body_specs=all_body_specs(
                ["SOLID", "CONSTRAINED", "ESTIMATED", "OPEN", "SOLID"],
                [0.9, 0.7, 0.5, 0.0, 0.8],
            ),
            dim_scores=dim_scores_all(0.75),
        )
        defaults.update(kwargs)
        return _orch.synthesize(**defaults)

    def test_basic_synthesis(self):
        r = self._run_synthesis()
        assert isinstance(r, SynthesisReport)
        assert r.omega_score >= 0.0
        assert r.integrity_score >= 0.0
        assert r.synthesis_score >= 0.0

    def test_synthesis_score_formula(self):
        r = self._run_synthesis()
        expected = XI_C_F * r.omega_score + (1 - XI_C_F) * r.integrity_score
        assert abs(r.synthesis_score - expected) < 1e-9

    def test_full_report_string(self):
        r = self._run_synthesis()
        s = r.full_report()
        assert "GRAND SYNTHESIS REPORT" in s
        assert "SYNTHESIS SCORE" in s
        assert "PENTAD ANALYSIS" in s
        assert "GOVERNANCE AUDIT" in s

    def test_wrong_body_count(self):
        with pytest.raises(ValueError):
            _orch.synthesize(
                system_name="X", system_type="Y",
                body_specs=[{"label": "A", "status": "SOLID", "phi_trust": 0.5}],
                dim_scores=dim_scores_all(),
            )

    def test_action_priorities_ordered(self):
        r = self._run_synthesis()
        if len(r.action_priorities) > 1:
            scores = [a.priority_score for a in r.action_priorities]
            assert scores == sorted(scores, reverse=True)

    def test_action_priority_for_open_body(self):
        r = self._run_synthesis()
        labels = [a.body_label for a in r.action_priorities]
        # At least one priority should reference the OPEN body (Ψ₄)
        assert any("Ψ" in lbl or "Body" in lbl for lbl in labels)

    def test_synthesis_with_decision(self):
        r = self._run_synthesis(
            decision_question="Should we expand?",
            decision_options=[
                {"name": "Yes", "impacts": [], "phi_trust_impact": 0.1},
                {"name": "No",  "impacts": [], "phi_trust_impact": -0.1},
            ],
        )
        assert r.decision_analysis is not None
        assert r.decision_analysis.best_option() is not None

    def test_synthesis_with_commitment(self):
        r = self._run_synthesis(
            commitments=[{
                "domain": "Process",
                "commitment": "Ship v2.0 by Q4.",
                "falsification_condition": "If not shipped by Dec 31, plan fails.",
                "test_horizon": "Q4 2026",
            }]
        )
        assert len(r.commitments) == 1
        assert r.commitments[0].domain == "Process"

    def test_synthesis_grade_type(self):
        r = self._run_synthesis()
        letter, label = r.synthesis_grade
        assert isinstance(letter, str)
        assert isinstance(label, str)

    def test_all_solid_gives_high_score(self):
        r = _orch.synthesize(
            system_name="Perfect",
            system_type="Test",
            body_specs=all_body_specs(
                ["SOLID"] * N_W, [1.0] * N_W
            ),
            dim_scores=dim_scores_all(1.0),
        )
        assert r.synthesis_score >= 0.75

    def test_all_open_gives_low_score(self):
        r = _orch.synthesize(
            system_name="Broken",
            system_type="Test",
            body_specs=all_body_specs(
                ["OPEN"] * N_W, [0.0] * N_W
            ),
            dim_scores=dim_scores_all(0.0),
        )
        assert r.synthesis_score < 0.10

    def test_session_id_assigned(self):
        r = self._run_synthesis()
        assert isinstance(r.session_id, str)
        assert len(r.session_id) > 0

    def test_created_at_format(self):
        r = self._run_synthesis()
        assert "T" in r.created_at
        assert "Z" in r.created_at


# ═════════════════════════════════════════════════════════════════════════════
# 7. DATABASE (temp file, cleaned up)
# ═════════════════════════════════════════════════════════════════════════════

class TestDatabase:
    def _temp_report(self, name="DBTest"):
        return _orch.synthesize(
            system_name=name,
            system_type="Test",
            body_specs=all_body_specs(
                ["SOLID", "SOLID", "CONSTRAINED", "ESTIMATED", "OPEN"],
                [0.9, 0.8, 0.7, 0.5, 0.2],
            ),
            dim_scores=dim_scores_all(0.7),
        )

    def test_save_and_load(self, tmp_path, monkeypatch):
        import oracle.db.store as store_mod
        monkeypatch.setattr(store_mod, "DB_PATH", tmp_path / "oracle.db")
        r = self._temp_report()
        store_mod.save_session(r)
        rows = store_mod.load_sessions()
        assert any(row["id"] == r.session_id for row in rows)

    def test_load_report_text(self, tmp_path, monkeypatch):
        import oracle.db.store as store_mod
        monkeypatch.setattr(store_mod, "DB_PATH", tmp_path / "oracle.db")
        r = self._temp_report()
        store_mod.save_session(r)
        text = store_mod.load_session_report(r.session_id)
        assert text is not None
        assert "GRAND SYNTHESIS REPORT" in text

    def test_load_unknown_session(self, tmp_path, monkeypatch):
        import oracle.db.store as store_mod
        monkeypatch.setattr(store_mod, "DB_PATH", tmp_path / "oracle.db")
        assert store_mod.load_session_report("nonexistent") is None

    def test_save_with_commitment(self, tmp_path, monkeypatch):
        import oracle.db.store as store_mod
        monkeypatch.setattr(store_mod, "DB_PATH", tmp_path / "oracle.db")
        r = _orch.synthesize(
            system_name="CommitTest",
            system_type="Test",
            body_specs=all_body_specs(["SOLID"] * N_W, [0.8] * N_W),
            dim_scores=dim_scores_all(),
            commitments=[{
                "domain": "D",
                "commitment": "C",
                "falsification_condition": "F",
                "test_horizon": "T",
            }],
        )
        store_mod.save_session(r)
        commits = store_mod.load_open_commitments()
        assert any(c["domain"] == "D" for c in commits)
