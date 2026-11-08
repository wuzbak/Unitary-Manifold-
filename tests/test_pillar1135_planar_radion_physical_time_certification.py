# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from pathlib import Path

import pytest

pytest.importorskip("sympy")

import src.core.pillar1135_planar_radion_physical_time_certification as p1135

from src.core.pillar1135_planar_radion_physical_time_certification import (
    DOES_NOT_ESTABLISH,
    NEW_CERTIFIED_SUBCASE,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REMAINING_RESIDUAL_OBLIGATIONS,
    VERSION,
    pillar1135_planar_radion_physical_time_certification,
    pillar1135_summary,
    planar_radion_physical_time_certificate,
)


@pytest.fixture(scope="module")
def certificate():
    return planar_radion_physical_time_certificate()


@pytest.fixture(scope="module")
def packet():
    return pillar1135_planar_radion_physical_time_certification()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1135
    assert PILLAR_GATE == 'PLANAR_RADION_INHOMOGENEOUS_PHYSICAL_TIME_CERTIFICATION'
    assert PILLAR_STATUS == 'PLANAR_RADION_RESTRICTED_PHYSICAL_TIME_EVOLUTION_CERTIFIED'
    assert VERSION == 'v38.6'
    assert NEXT_PILLAR_SLOT == 1136
    assert NEW_CERTIFIED_SUBCASE == (
        'PLANAR_MASSLESS_ZERO_VECTOR_CONSTRAINT_COMPATIBLE_PHYSICAL_TIME_EVOLUTION_CERTIFIED'
    )


def test_module_is_sharded_at_1129_1168() -> None:
    assert Path(p1135.__file__).parent.name == "pillar_1129_1168"
    assert p1135.__name__ == "src.core.pillar1135_planar_radion_physical_time_certification"
    assert not (p1135._ROOT / "src/core/pillar1135_planar_radion_physical_time_certification.py").exists()
    assert p1135._ROOT == Path(__file__).resolve().parents[1]


def test_remaining_obligations_are_untouched() -> None:
    assert 'T_RELAXATION_LAW_DECLARED_NOT_DERIVED' in REMAINING_RESIDUAL_OBLIGATIONS
    assert 'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED' in REMAINING_RESIDUAL_OBLIGATIONS
    # This pillar introduces a new sub-case rather than closing either obligation.
    assert NEW_CERTIFIED_SUBCASE not in REMAINING_RESIDUAL_OBLIGATIONS


def test_non_claims_are_stated() -> None:
    joined = ' '.join(DOES_NOT_ESTABLISH)
    assert 'massless (m_phi = 0), zero-vector' in joined
    assert 'NOT reinterpreted as coordinate time' in joined
    assert 'NOT closed by this pillar' in joined
    assert 'DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN' in joined
    assert 'not a Lean proof' in joined


@pytest.mark.slow
def test_certificate_matches_existing_acceptance_evidence(certificate) -> None:
    from TOOLS.checks.run_planar_radion_acceptance import run_acceptance

    direct_report = run_acceptance()
    assert certificate['verified'] is True
    assert certificate['status'] == NEW_CERTIFIED_SUBCASE
    assert certificate['gates'] == direct_report['gates']
    assert all(certificate['gates'].values())
    assert certificate['symbolic_checks_all_zero'] is True
    assert certificate['negative_controls_all_rejected'] is True
    assert 3.5 <= certificate['temporal_refinement_observed_order'] <= 4.5
    assert len(certificate['source_sha256']) == 4
    assert certificate['t_dynamics_derived_from_action'] is True
    assert certificate['off_shell_time_derivative_terms_derived'] is False
    assert certificate['constraint_compatible_nonconstant_scalar_evolution'] is True
    assert certificate['well_posedness_established'] is False
    assert certificate['closure_earned'] is False


def test_certificate_fails_closed_when_acceptance_evidence_fails(monkeypatch) -> None:
    def failing_evidence():
        return {
            'passed': False,
            'gates': {'symbolic_identities_verified': False},
            'scope': 'test',
            'not_claimed': [],
            'symbolic_checks': {'all_zero': False},
            'negative_controls': {'a': False},
            'temporal_refinement': {'observed_order': 0.0},
            'source_sha256': {},
        }

    monkeypatch.setattr(p1135, '_planar_radion_acceptance_evidence', failing_evidence)
    result = p1135.planar_radion_physical_time_certificate()
    assert result['verified'] is False
    assert result['status'] == 'PLANAR_RADION_PHYSICAL_TIME_EVOLUTION_NOT_VERIFIED'


def test_certificate_fails_closed_when_gates_missing(monkeypatch) -> None:
    def empty_gates_evidence():
        return {'passed': True, 'gates': {}}

    monkeypatch.setattr(p1135, '_planar_radion_acceptance_evidence', empty_gates_evidence)
    result = p1135.planar_radion_physical_time_certificate()
    assert result['verified'] is False


@pytest.mark.parametrize("removed_gate", sorted(p1135._REQUIRED_ACCEPTANCE_GATES))
def test_certificate_rejects_each_missing_gate(monkeypatch, removed_gate) -> None:
    gates = {name: True for name in p1135._REQUIRED_ACCEPTANCE_GATES}
    del gates[removed_gate]
    monkeypatch.setattr(p1135, '_planar_radion_acceptance_evidence',
                        lambda: {'passed': True, 'gates': gates})
    assert planar_radion_physical_time_certificate()['verified'] is False


@pytest.mark.parametrize("gate_change", ["unexpected", "false", "truthy_non_boolean"])
def test_certificate_rejects_invalid_gate_set(monkeypatch, gate_change) -> None:
    gates = {name: True for name in p1135._REQUIRED_ACCEPTANCE_GATES}
    if gate_change == "unexpected":
        gates["unexpected_gate"] = True
    elif gate_change == "false":
        gates["symbolic_identities_verified"] = False
    else:
        gates["symbolic_identities_verified"] = 1
    monkeypatch.setattr(p1135, '_planar_radion_acceptance_evidence',
                        lambda: {'passed': True, 'gates': gates})
    assert planar_radion_physical_time_certificate()['verified'] is False


def test_certificate_does_not_expose_cached_report(monkeypatch) -> None:
    evidence = {
        'passed': True,
        'gates': {name: True for name in p1135._REQUIRED_ACCEPTANCE_GATES},
        'symbolic_checks': {'all_zero': True},
    }
    monkeypatch.setattr(p1135, '_planar_radion_acceptance_evidence', lambda: evidence)
    first = planar_radion_physical_time_certificate()
    first['acceptance_report']['symbolic_checks']['all_zero'] = False
    first['acceptance_report']['gates']['symbolic_identities_verified'] = False
    second = planar_radion_physical_time_certificate()
    assert second['verified'] is True
    assert second['symbolic_checks_all_zero'] is True


@pytest.mark.slow
def test_truth_surfaces_synchronized(packet) -> None:
    assert packet['truth_surface_sync']['all_pass'] is True


@pytest.mark.slow
def test_truth_surfaces_reject_missing_evidence(monkeypatch) -> None:
    original = Path.read_text

    def altered_text(path, *args, **kwargs):
        text = original(path, *args, **kwargs)
        if path.name == "STATUS.md":
            return text.replace("Pillar 1135", "Removed")
        return text

    monkeypatch.setattr(Path, "read_text", altered_text)
    assert p1135._truth_surface_sync_status()["all_pass"] is False


@pytest.mark.slow
def test_truth_surfaces_reject_misplaced_wave_changelog_evidence(monkeypatch) -> None:
    original = Path.read_text

    def altered_text(path, *args, **kwargs):
        text = original(path, *args, **kwargs)
        if path.name == "WAVE_CHANGELOG.md":
            heading = f'## {VERSION} ({p1135.SPRINT_DATE} — Sprint {p1135.SPRINT}: Pillar {PILLAR_NUMBER})'
            before, marker, after = text.partition(heading)
            if not marker:
                return text
            section, next_heading, rest = after.partition("\n## ")
            target = "**Next pillar slot:** 1136"
            return before + target + "\n" + marker + section.replace(target, "") + next_heading + rest
        return text

    monkeypatch.setattr(Path, "read_text", altered_text)
    assert p1135._truth_surface_sync_status()["all_pass"] is False


@pytest.mark.slow
def test_packet_valid(packet) -> None:
    assert packet['valid'] is True
    assert packet['status'] == PILLAR_STATUS
    assert packet['framework_closure_earned'] is False
    assert packet['remaining_residual_obligations'] == REMAINING_RESIDUAL_OBLIGATIONS


@pytest.mark.slow
def test_summary() -> None:
    summary = pillar1135_summary()
    assert summary['valid'] is True
    assert summary['verified'] is True
    assert summary['framework_closure_earned'] is False
    assert summary['status'] == PILLAR_STATUS
