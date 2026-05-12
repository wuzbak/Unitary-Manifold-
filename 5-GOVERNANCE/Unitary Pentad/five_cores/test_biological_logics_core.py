# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/test_biological_logics_core.py
==========================================
Unit tests for the Biological Logics Core.

Covers:
  - Constants: C_S, vital weights (sum to 1), triage thresholds
  - VitalCategory, TriagePriority, CarePathway, PRIORITY_TO_PATHWAY
  - CrewMember: construction, phi_health, urgency, triage_priority, care_pathway
  - BiologicalLogicsCore: factory, add_crew_member, update_vital,
    apply_intervention, remove_intervention, triage_all,
    critical_members, crew_readiness, system_health, care_plan, tick
  - Evolution: natural relaxation toward healthy setpoint
  - Intervention effectiveness modulated by trust
  - Edge cases: empty crew, P1 emergency, all healthy
"""

import math
import sys
import os

import pytest
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_PENTAD = os.path.dirname(_HERE)
_ROOT = os.path.dirname(_PENTAD)
for _p in [_HERE, _PENTAD, _ROOT]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from five_cores.biological_logics_core import (
    C_S,
    VitalCategory,
    VITAL_CATEGORIES,
    VITAL_WEIGHTS,
    VITAL_RECOVERY_RATES,
    TriagePriority,
    CarePathway,
    PRIORITY_TO_PATHWAY,
    THRESHOLD_P1,
    THRESHOLD_P2,
    THRESHOLD_P3,
    URGENCY_P1,
    URGENCY_P2,
    CrewMember,
    BiologicalState,
    BiologicalLogicsCore,
)

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
}


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_c_s_value(self):
        assert math.isclose(C_S, 12 / 37, rel_tol=1e-12)

    def test_vital_weights_sum_to_one(self):
        total = sum(VITAL_WEIGHTS.values())
        assert math.isclose(total, 1.0, abs_tol=1e-10)

    def test_five_vital_categories(self):
        assert len(VITAL_CATEGORIES) == 5

    def test_all_categories_have_weights(self):
        for vc in VITAL_CATEGORIES:
            assert vc in VITAL_WEIGHTS

    def test_all_categories_have_recovery_rates(self):
        for vc in VITAL_CATEGORIES:
            assert vc in VITAL_RECOVERY_RATES

    def test_recovery_rates_positive(self):
        for r in VITAL_RECOVERY_RATES.values():
            assert r > 0

    def test_triage_threshold_ordering(self):
        assert THRESHOLD_P1 < THRESHOLD_P2 < THRESHOLD_P3

    def test_priority_to_pathway_complete(self):
        for p in [TriagePriority.P1_IMMEDIATE, TriagePriority.P2_URGENT,
                  TriagePriority.P3_DELAYED, TriagePriority.P4_MINIMAL]:
            assert p in PRIORITY_TO_PATHWAY


# ===========================================================================
# CrewMember
# ===========================================================================

class TestCrewMember:
    def _healthy(self) -> CrewMember:
        return CrewMember("C001", "Test", vital_radions={
            vc: 1.0 for vc in VITAL_CATEGORIES
        })

    def _critical(self) -> CrewMember:
        return CrewMember("C002", "Critical", vital_radions={
            vc: 0.10 for vc in VITAL_CATEGORIES
        })

    def test_default_vitals_present(self):
        m = CrewMember("C001", "Alice")
        for vc in VITAL_CATEGORIES:
            assert vc in m.vital_radions

    def test_vitals_clamped(self):
        m = CrewMember("C001", "X", vital_radions={
            VitalCategory.CARDIOVASCULAR: 2.0,
            VitalCategory.RESPIRATORY: -1.0,
            VitalCategory.NEUROLOGICAL: 0.5,
            VitalCategory.MUSCULOSKELETAL: 0.5,
            VitalCategory.IMMUNE: 0.5,
        })
        assert m.vital_radions[VitalCategory.CARDIOVASCULAR] == 1.0
        assert m.vital_radions[VitalCategory.RESPIRATORY] == 0.0

    def test_phi_health_of_healthy(self):
        m = self._healthy()
        assert math.isclose(m.phi_health, 1.0, abs_tol=1e-10)

    def test_phi_health_weighted_mean(self):
        m = CrewMember("C001", "X", vital_radions={
            vc: 0.5 for vc in VITAL_CATEGORIES
        })
        assert math.isclose(m.phi_health, 0.5, abs_tol=1e-10)

    def test_urgency_healthy_is_zero(self):
        m = self._healthy()
        assert math.isclose(m.urgency, 0.0, abs_tol=1e-10)

    def test_urgency_critical_is_high(self):
        m = self._critical()
        assert m.urgency > URGENCY_P2

    def test_triage_priority_healthy_is_p4(self):
        m = self._healthy()
        assert m.triage_priority == TriagePriority.P4_MINIMAL

    def test_triage_priority_critical_is_p1(self):
        m = self._critical()
        assert m.triage_priority == TriagePriority.P1_IMMEDIATE

    def test_care_pathway_healthy(self):
        m = self._healthy()
        assert m.care_pathway == CarePathway.SELF_CARE

    def test_care_pathway_critical(self):
        m = self._critical()
        assert m.care_pathway == CarePathway.RESUSCITATION

    def test_severity_factor_floored_at_one(self):
        m = CrewMember("C001", "X", severity_factor=0.5)
        assert m.severity_factor == 1.0

    def test_urgency_amplified_by_severity(self):
        m_low = CrewMember("C001", "X", vital_radions={vc: 0.5 for vc in VITAL_CATEGORIES}, severity_factor=1.0)
        m_high = CrewMember("C002", "Y", vital_radions={vc: 0.5 for vc in VITAL_CATEGORIES}, severity_factor=2.0)
        assert m_high.urgency > m_low.urgency


# ===========================================================================
# BiologicalLogicsCore — factory
# ===========================================================================

class TestBioFactory:
    def test_default_creates_five_crew(self):
        bc = BiologicalLogicsCore.default()
        assert len(bc._crew) == 5

    def test_default_all_healthy(self):
        bc = BiologicalLogicsCore.default()
        # All crew should be at P4 (default vitals = 0.95)
        triage = bc.triage_all()
        for p in triage.values():
            assert p in (TriagePriority.P3_DELAYED, TriagePriority.P4_MINIMAL)


# ===========================================================================
# Crew Management
# ===========================================================================

class TestCrewManagement:
    def test_add_crew_member(self):
        bc = BiologicalLogicsCore(crew=[])
        bc.add_crew_member(CrewMember("C100", "Extra"))
        assert "C100" in bc._crew

    def test_update_vital(self):
        bc = BiologicalLogicsCore.default()
        bc.update_vital("C001", VitalCategory.CARDIOVASCULAR, 0.3)
        assert math.isclose(bc._crew["C001"].vital_radions[VitalCategory.CARDIOVASCULAR], 0.3)

    def test_apply_intervention(self):
        bc = BiologicalLogicsCore.default()
        bc.apply_intervention("C001", VitalCategory.RESPIRATORY, 0.1)
        assert VitalCategory.RESPIRATORY in bc._crew["C001"].interventions

    def test_remove_intervention(self):
        bc = BiologicalLogicsCore.default()
        bc.apply_intervention("C001", VitalCategory.IMMUNE, 0.1)
        bc.remove_intervention("C001", VitalCategory.IMMUNE)
        assert VitalCategory.IMMUNE not in bc._crew["C001"].interventions


# ===========================================================================
# Triage and Readiness
# ===========================================================================

class TestTriageAndReadiness:
    def test_triage_all_returns_dict(self):
        bc = BiologicalLogicsCore.default()
        triage = bc.triage_all()
        assert set(triage.keys()) == set(bc._crew.keys())

    def test_critical_members_empty_when_all_healthy(self):
        bc = BiologicalLogicsCore.default()
        assert bc.critical_members() == []

    def test_critical_member_detected(self):
        bc = BiologicalLogicsCore.default()
        # Make one crew member critical
        for vc in VITAL_CATEGORIES:
            bc._crew["C001"].vital_radions[vc] = 0.05
        assert "C001" in bc.critical_members()

    def test_crew_readiness_all_healthy(self):
        bc = BiologicalLogicsCore.default()
        r = bc.crew_readiness()
        assert math.isclose(r, 1.0, abs_tol=0.01)

    def test_crew_readiness_decreases_with_critical(self):
        bc = BiologicalLogicsCore.default()
        r_before = bc.crew_readiness()
        for vc in VITAL_CATEGORIES:
            bc._crew["C001"].vital_radions[vc] = 0.05
        r_after = bc.crew_readiness()
        assert r_after < r_before

    def test_system_health_mean(self):
        bc = BiologicalLogicsCore.default()
        expected = np.mean([m.phi_health for m in bc._crew.values()])
        assert math.isclose(bc.system_health(), expected, abs_tol=1e-10)

    def test_empty_crew_readiness_is_one(self):
        bc = BiologicalLogicsCore(crew=[])
        assert bc.crew_readiness() == 1.0

    def test_empty_crew_system_health_is_one(self):
        bc = BiologicalLogicsCore(crew=[])
        assert bc.system_health() == 1.0


# ===========================================================================
# Care Plan
# ===========================================================================

class TestCarePlan:
    def test_care_plan_returns_dict(self):
        bc = BiologicalLogicsCore.default()
        plan = bc.care_plan("C001")
        assert "phi_health" in plan
        assert "triage_priority" in plan
        assert "care_pathway" in plan
        assert "recommended_interventions" in plan

    def test_care_plan_unknown_member(self):
        bc = BiologicalLogicsCore.default()
        plan = bc.care_plan("NONEXISTENT")
        assert "error" in plan

    def test_intervention_recommended_below_c_s(self):
        bc = BiologicalLogicsCore.default()
        bc._crew["C001"].vital_radions[VitalCategory.CARDIOVASCULAR] = 0.10
        plan = bc.care_plan("C001")
        rec_cats = [r["category"] for r in plan["recommended_interventions"]]
        assert VitalCategory.CARDIOVASCULAR in rec_cats


# ===========================================================================
# Tick and Evolution
# ===========================================================================

class TestTick:
    def test_tick_returns_state(self):
        bc = BiologicalLogicsCore.default()
        state = bc.tick()
        assert isinstance(state, BiologicalState)

    def test_step_count_increments(self):
        bc = BiologicalLogicsCore.default()
        bc.tick()
        bc.tick()
        assert bc._step_count == 2

    def test_natural_recovery_toward_health(self):
        bc = BiologicalLogicsCore.default()
        # Set low vitals
        for vc in VITAL_CATEGORIES:
            bc._crew["C001"].vital_radions[vc] = 0.50
        phi_before = bc._crew["C001"].phi_health
        # Run 50 steps without intervention
        for _ in range(50):
            bc.tick()
        phi_after = bc._crew["C001"].phi_health
        assert phi_after > phi_before

    def test_intervention_accelerates_recovery(self):
        bc_no = BiologicalLogicsCore.default()
        bc_iv = BiologicalLogicsCore.default()
        for vc in VITAL_CATEGORIES:
            bc_no._crew["C001"].vital_radions[vc] = 0.30
            bc_iv._crew["C001"].vital_radions[vc] = 0.30
        bc_iv.apply_intervention("C001", VitalCategory.CARDIOVASCULAR, 0.1)
        for _ in range(20):
            bc_no.tick()
            bc_iv.tick()
        # Both recover, but with intervention should be slightly higher
        phi_no = bc_no._crew["C001"].phi_health
        phi_iv = bc_iv._crew["C001"].phi_health
        assert phi_iv >= phi_no

    def test_trust_modulates_intervention(self):
        bc_hi = BiologicalLogicsCore(phi_trust=1.0)
        bc_lo = BiologicalLogicsCore(phi_trust=0.1)
        for bc in [bc_hi, bc_lo]:
            for vc in VITAL_CATEGORIES:
                bc._crew["C001"].vital_radions[vc] = 0.30
            bc.apply_intervention("C001", VitalCategory.RESPIRATORY, 0.2)
        for _ in range(10):
            bc_hi.tick()
            bc_lo.tick()
        # Higher trust → more effective intervention
        assert bc_hi._crew["C001"].phi_health >= bc_lo._crew["C001"].phi_health

    def test_vital_updates_applied_in_tick(self):
        bc = BiologicalLogicsCore.default()
        bc.tick(vital_updates={"C001": {VitalCategory.CARDIOVASCULAR: 0.20}})
        # After tick, evolution will have slightly adjusted it but it started near 0.20
        assert bc._crew["C001"].vital_radions[VitalCategory.CARDIOVASCULAR] < 0.60
