# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
test_pentad_mission_packs.py
============================
Tests for Sprint E — Multi-Agent Mission Packs.
"""

from __future__ import annotations

import pytest

from pentad_mission_packs import (
    MissionPackID,
    MISSION_PACK_IDS,
    MissionPackSpec,
    MISSION_PACK_REGISTRY,
    get_pack_spec,
    list_pack_ids,
    describe_pack,
    MissionRunner,
    research_jobs,
    triage_jobs,
    planning_jobs,
    monitoring_jobs,
    interrogation_jobs,
)
from five_cores.five_cores_system import FiveCoresSystem


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cloud_eligible(job) -> bool:  # noqa: ANN001
    """Return cloud_adjunct_eligible for either AgentJob or plain dict."""
    if isinstance(job, dict):
        return job.get("cloud_adjunct_eligible", False)
    return getattr(job, "cloud_adjunct_eligible", False)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def system() -> FiveCoresSystem:
    """A Five-Cores system with comfortable trust."""
    return FiveCoresSystem(phi_trust=1.0)


# ---------------------------------------------------------------------------
# MissionPackID constants
# ---------------------------------------------------------------------------


class TestMissionPackID:
    def test_research_constant(self) -> None:
        assert MissionPackID.RESEARCH == "research"

    def test_triage_constant(self) -> None:
        assert MissionPackID.TRIAGE == "triage"

    def test_planning_constant(self) -> None:
        assert MissionPackID.PLANNING == "planning"

    def test_monitoring_constant(self) -> None:
        assert MissionPackID.MONITORING == "monitoring"

    def test_interrogation_constant(self) -> None:
        assert MissionPackID.INTERROGATION == "interrogation"


# ---------------------------------------------------------------------------
# MISSION_PACK_IDS
# ---------------------------------------------------------------------------


class TestMissionPackIDs:
    def test_has_exactly_five(self) -> None:
        assert len(MISSION_PACK_IDS) == 5

    def test_is_tuple(self) -> None:
        assert isinstance(MISSION_PACK_IDS, tuple)

    def test_contains_all_constants(self) -> None:
        for cid in (
            MissionPackID.RESEARCH,
            MissionPackID.TRIAGE,
            MissionPackID.PLANNING,
            MissionPackID.MONITORING,
            MissionPackID.INTERROGATION,
        ):
            assert cid in MISSION_PACK_IDS


# ---------------------------------------------------------------------------
# MISSION_PACK_REGISTRY
# ---------------------------------------------------------------------------


class TestMissionPackRegistry:
    def test_registry_has_five_entries(self) -> None:
        assert len(MISSION_PACK_REGISTRY) == 5

    def test_registry_keys_match_ids(self) -> None:
        for pid in MISSION_PACK_IDS:
            assert pid in MISSION_PACK_REGISTRY

    def test_all_values_are_mission_pack_spec(self) -> None:
        for spec in MISSION_PACK_REGISTRY.values():
            assert isinstance(spec, MissionPackSpec)

    def test_pack_id_field_matches_key(self) -> None:
        for key, spec in MISSION_PACK_REGISTRY.items():
            assert spec.pack_id == key


# ---------------------------------------------------------------------------
# get_pack_spec
# ---------------------------------------------------------------------------


class TestGetPackSpec:
    @pytest.mark.parametrize("pack_id", list(MISSION_PACK_IDS))
    def test_returns_spec_with_correct_pack_id(self, pack_id: str) -> None:
        spec = get_pack_spec(pack_id)
        assert spec.pack_id == pack_id

    def test_raises_key_error_for_unknown(self) -> None:
        with pytest.raises(KeyError):
            get_pack_spec("nonexistent_pack_xyz")

    def test_returns_mission_pack_spec_instance(self) -> None:
        spec = get_pack_spec(MissionPackID.RESEARCH)
        assert isinstance(spec, MissionPackSpec)


# ---------------------------------------------------------------------------
# list_pack_ids
# ---------------------------------------------------------------------------


class TestListPackIds:
    def test_returns_tuple(self) -> None:
        assert isinstance(list_pack_ids(), tuple)

    def test_returns_five_entries(self) -> None:
        assert len(list_pack_ids()) == 5

    def test_contains_all_known_ids(self) -> None:
        ids = list_pack_ids()
        for pid in MISSION_PACK_IDS:
            assert pid in ids


# ---------------------------------------------------------------------------
# describe_pack
# ---------------------------------------------------------------------------


class TestDescribePack:
    @pytest.mark.parametrize("pack_id", list(MISSION_PACK_IDS))
    def test_returns_non_empty_string(self, pack_id: str) -> None:
        result = describe_pack(pack_id)
        assert isinstance(result, str) and len(result) > 0

    @pytest.mark.parametrize("pack_id", list(MISSION_PACK_IDS))
    def test_contains_pack_id(self, pack_id: str) -> None:
        assert pack_id in describe_pack(pack_id)

    def test_raises_for_unknown_pack(self) -> None:
        with pytest.raises(KeyError):
            describe_pack("bogus_pack")


# ---------------------------------------------------------------------------
# MissionPackSpec cloud_adjunct_eligible correctness
# ---------------------------------------------------------------------------


class TestCloudAdjunctEligibility:
    def test_research_is_eligible(self) -> None:
        assert get_pack_spec(MissionPackID.RESEARCH).cloud_adjunct_eligible is True

    def test_triage_is_not_eligible(self) -> None:
        assert get_pack_spec(MissionPackID.TRIAGE).cloud_adjunct_eligible is False

    def test_planning_is_eligible(self) -> None:
        assert get_pack_spec(MissionPackID.PLANNING).cloud_adjunct_eligible is True

    def test_monitoring_is_not_eligible(self) -> None:
        assert get_pack_spec(MissionPackID.MONITORING).cloud_adjunct_eligible is False

    def test_interrogation_is_eligible(self) -> None:
        assert get_pack_spec(MissionPackID.INTERROGATION).cloud_adjunct_eligible is True

    def test_triage_cloud_roles_empty(self) -> None:
        assert get_pack_spec(MissionPackID.TRIAGE).cloud_roles == ()

    def test_monitoring_cloud_roles_empty(self) -> None:
        assert get_pack_spec(MissionPackID.MONITORING).cloud_roles == ()

    def test_research_cloud_roles_non_empty(self) -> None:
        assert len(get_pack_spec(MissionPackID.RESEARCH).cloud_roles) > 0


# ---------------------------------------------------------------------------
# Job builder functions
# ---------------------------------------------------------------------------


class TestResearchJobs:
    def test_returns_non_empty_list(self) -> None:
        jobs = research_jobs()
        assert len(jobs) > 0

    def test_returns_three_jobs(self) -> None:
        assert len(research_jobs()) == 3

    def test_no_cloud_when_disabled(self) -> None:
        jobs = research_jobs(include_cloud=False)
        for job in jobs:
            assert _cloud_eligible(job) is False


class TestTriageJobs:
    def test_returns_two_entries(self) -> None:
        assert len(triage_jobs()) == 2

    def test_is_list(self) -> None:
        assert isinstance(triage_jobs(), list)


class TestPlanningJobs:
    def test_returns_three_entries(self) -> None:
        assert len(planning_jobs()) == 3

    def test_no_cloud_when_disabled(self) -> None:
        jobs = planning_jobs(include_cloud=False)
        for job in jobs:
            assert _cloud_eligible(job) is False


class TestMonitoringJobs:
    def test_returns_five_entries(self) -> None:
        assert len(monitoring_jobs()) == 5

    def test_is_list(self) -> None:
        assert isinstance(monitoring_jobs(), list)


class TestInterrogationJobs:
    def test_returns_three_entries(self) -> None:
        assert len(interrogation_jobs()) == 3

    def test_no_cloud_when_disabled(self) -> None:
        jobs = interrogation_jobs(include_cloud=False)
        for job in jobs:
            assert _cloud_eligible(job) is False


# ---------------------------------------------------------------------------
# MissionRunner construction
# ---------------------------------------------------------------------------


class TestMissionRunnerConstruction:
    @pytest.mark.parametrize("pack_id", list(MISSION_PACK_IDS))
    def test_can_be_created_for_each_pack(self, pack_id: str, system: FiveCoresSystem) -> None:
        runner = MissionRunner(pack_id, system)
        assert runner is not None

    def test_spec_property_returns_mission_pack_spec(self, system: FiveCoresSystem) -> None:
        runner = MissionRunner(MissionPackID.RESEARCH, system)
        assert isinstance(runner.spec, MissionPackSpec)

    def test_spec_pack_id_matches(self, system: FiveCoresSystem) -> None:
        runner = MissionRunner(MissionPackID.TRIAGE, system)
        assert runner.spec.pack_id == MissionPackID.TRIAGE

    def test_custom_jobs_accepted(self, system: FiveCoresSystem) -> None:
        custom = triage_jobs()
        runner = MissionRunner(MissionPackID.TRIAGE, system, custom_jobs=custom)
        assert runner is not None


# ---------------------------------------------------------------------------
# MissionRunner.run
# ---------------------------------------------------------------------------


class TestMissionRunnerRun:
    @pytest.mark.parametrize("pack_id", list(MISSION_PACK_IDS))
    def test_returns_dict_with_status(self, pack_id: str, system: FiveCoresSystem) -> None:
        runner = MissionRunner(pack_id, system)
        result = runner.run()
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.parametrize("pack_id", list(MISSION_PACK_IDS))
    def test_status_is_valid_string(self, pack_id: str, system: FiveCoresSystem) -> None:
        result = MissionRunner(pack_id, system).run()
        assert result["status"] in ("completed", "failed", "stopped")

    def test_result_contains_pack_id(self, system: FiveCoresSystem) -> None:
        result = MissionRunner(MissionPackID.PLANNING, system).run()
        assert result["pack_id"] == MissionPackID.PLANNING

    def test_result_contains_jobs_completed(self, system: FiveCoresSystem) -> None:
        result = MissionRunner(MissionPackID.RESEARCH, system).run()
        assert "jobs_completed" in result
        assert isinstance(result["jobs_completed"], list)

    def test_result_contains_jobs_pending(self, system: FiveCoresSystem) -> None:
        result = MissionRunner(MissionPackID.RESEARCH, system).run()
        assert "jobs_pending" in result
        assert isinstance(result["jobs_pending"], list)

    def test_result_contains_event_count(self, system: FiveCoresSystem) -> None:
        result = MissionRunner(MissionPackID.MONITORING, system).run()
        assert "event_count" in result
        assert isinstance(result["event_count"], int)

    def test_result_contains_stop_reason(self, system: FiveCoresSystem) -> None:
        result = MissionRunner(MissionPackID.TRIAGE, system).run()
        assert "stop_reason" in result


# ---------------------------------------------------------------------------
# MissionRunner.get_events
# ---------------------------------------------------------------------------


class TestMissionRunnerGetEvents:
    def test_returns_list(self, system: FiveCoresSystem) -> None:
        runner = MissionRunner(MissionPackID.RESEARCH, system)
        runner.run()
        assert isinstance(runner.get_events(), list)

    def test_events_match_event_count(self, system: FiveCoresSystem) -> None:
        runner = MissionRunner(MissionPackID.MONITORING, system)
        result = runner.run()
        assert len(runner.get_events()) == result["event_count"]


# ---------------------------------------------------------------------------
# MissionRunner.summary
# ---------------------------------------------------------------------------


class TestMissionRunnerSummary:
    @pytest.mark.parametrize("pack_id", list(MISSION_PACK_IDS))
    def test_returns_non_empty_string(self, pack_id: str, system: FiveCoresSystem) -> None:
        runner = MissionRunner(pack_id, system)
        summary = runner.summary()
        assert isinstance(summary, str) and len(summary) > 0

    def test_summary_contains_pack_name(self, system: FiveCoresSystem) -> None:
        runner = MissionRunner(MissionPackID.RESEARCH, system)
        assert "Research Mission" in runner.summary()
