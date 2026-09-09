# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1111_lane1_action_to_evolution_closure_attempt import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    lane1_action_to_evolution_closure_attempt,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1111
    assert PILLAR_GATE == 'LANE1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT'
    assert PILLAR_STATUS == 'LANE1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1112


def test_contract() -> None:
    report = lane1_action_to_evolution_closure_attempt()
    assert report['outcome'] in {'LANE1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT_READY', 'LANE1_ACTION_TO_EVOLUTION_CLOSURE_ATTEMPT_BLOCKED'}
    assert report['unit_outcome'] in {'CLOSED_NOW', 'TIGHTENED_WITH_EXPLICIT_BLOCKER'}


def test_blocking_analysis_is_specific_and_non_trivial() -> None:
    report = lane1_action_to_evolution_closure_attempt()
    analysis = report['blocking_analysis']
    assert analysis['non_triviality_guard']['all_blockers_non_trivial'] is True
    assert analysis['non_triviality_guard']['blocker_count'] == 3
    assert len(analysis['specific_blockers']) == 3
    for item in analysis['specific_blockers']:
        assert item['is_trivial_block'] is False
        assert item['required_evidence']
        assert item['current_gap']


def test_process_progress_surfaces_wins_and_no_go_paths() -> None:
    report = lane1_action_to_evolution_closure_attempt()
    progress = report['process_progress']
    assert len(progress['victories']) >= 2
    assert len(progress['no_go_or_dead_end_learnings']) >= 2
    assert len(progress['next_smart_steps']) >= 2
