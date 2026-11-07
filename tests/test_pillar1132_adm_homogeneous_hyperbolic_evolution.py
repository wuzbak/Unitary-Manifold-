# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import importlib
from pathlib import Path
import subprocess
import sys

import pytest

sp = pytest.importorskip("sympy")

import src.core.pillar1132_adm_homogeneous_hyperbolic_evolution as p1132

from src.core.pillar1132_adm_homogeneous_hyperbolic_evolution import (
    DOES_NOT_ESTABLISH,
    NEW_CERTIFIED_SUBCASE,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REMAINING_RESIDUAL_OBLIGATIONS,
    VERSION,
    adm_homogeneous_hyperbolic_evolution_certificate,
    pillar1132_adm_homogeneous_hyperbolic_evolution,
    pillar1132_summary,
)


@pytest.fixture(scope="module")
def certificate():
    return adm_homogeneous_hyperbolic_evolution_certificate()


@pytest.fixture(scope="module")
def packet():
    return pillar1132_adm_homogeneous_hyperbolic_evolution()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1132
    assert PILLAR_GATE == 'ADM_HOMOGENEOUS_HYPERBOLIC_EVOLUTION'
    assert PILLAR_STATUS == 'ADM_RESTRICTED_ACCELERATION_IDENTITIES_VERIFIED'
    assert VERSION == 'v38.4'
    assert NEXT_PILLAR_SLOT == 1133
    assert NEW_CERTIFIED_SUBCASE == (
        'ADM_OFF_SHELL_ACCELERATION_AND_STATIC_IDENTITIES_ONLY'
    )


@pytest.mark.parametrize("module_name", [
    "pillar1132_adm_homogeneous_hyperbolic_evolution",
    "pillar1133_superfluid_effective_theory",
    "pillar1134_rare_decay_probes",
])
def test_legacy_import_uses_single_sharded_source(module_name):
    module = importlib.import_module(f"src.core.{module_name}")
    expected_shard = ("pillar_1132_1134" if module_name.startswith("pillar1132_")
                      else "pillar_1129_1168")
    assert Path(module.__file__).parent.name == expected_shard
    assert module.__name__ == f"src.core.{module_name}"
    assert not (p1132._ROOT / "src/core" / f"{module_name}.py").exists()
    assert p1132._ROOT == Path(__file__).resolve().parents[1]


def test_shard_package_does_not_eagerly_import_physics_or_optional_dependencies():
    subprocess.run([
        sys.executable, "-c",
        "import sys; import src.core; import src.core.pillar_1132_1134; "
        "assert 'sympy' not in sys.modules; "
        "assert not any(name.startswith('src.core.pillar113') for name in sys.modules)",
    ], check=True, cwd=p1132._ROOT)


def test_historical_sync_does_not_require_current_cz_metadata():
    sync = p1132._truth_surface_sync_status()
    assert sync["all_pass"] is True
    wave = next(row for row in sync["files"] if row["path"].endswith("WAVE_CHANGELOG.md"))
    assert wave["scope"] == "historical Sprint CZ section, not current metadata"
    derivation = (p1132._ROOT / "1-THEORY/DERIVATION_STATUS.md").read_text()
    assert "**The Unitary Manifold v38.6" in derivation
    assert "*Last updated: 2026-11-07 (v38.6 — Sprint DB:" in derivation


@pytest.mark.parametrize("mutation", ["registration", "historical_slot", "qualification"])
def test_historical_sync_rejects_missing_or_misplaced_evidence(monkeypatch, mutation):
    original = Path.read_text

    def altered_text(path, *args, **kwargs):
        text = original(path, *args, **kwargs)
        if mutation == "registration":
            return (text.replace("Historical Sprint CZ registration", "Removed registration")
                    if path.name == "DERIVATION_STATUS.md" else text)
        if path.name == "WAVE_CHANGELOG.md":
            heading = "## v38.4 (2026-11-02 — Sprint CZ: Pillar 1132)"
            before, marker, after = text.partition(heading)
            section, next_heading, rest = after.partition("\n## ")
            target = ("**Next pillar slot:** 1133" if mutation == "historical_slot"
                      else "not a constrained nonconstant scalar evolution certificate")
            return before + target + "\n" + marker + section.replace(target, "") + next_heading + rest
        return text

    monkeypatch.setattr(Path, "read_text", altered_text)
    assert p1132._truth_surface_sync_status()["all_pass"] is False


def test_remaining_obligations_are_untouched() -> None:
    assert 'T_RELAXATION_LAW_DECLARED_NOT_DERIVED' in REMAINING_RESIDUAL_OBLIGATIONS
    assert 'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED' in REMAINING_RESIDUAL_OBLIGATIONS
    # This pillar introduces a new sub-case rather than closing either obligation.
    assert NEW_CERTIFIED_SUBCASE not in REMAINING_RESIDUAL_OBLIGATIONS


def test_non_claims_are_stated() -> None:
    joined = ' '.join(DOES_NOT_ESTABLISH)
    assert 'gauge field B_mu is excluded' in joined
    assert 'NOT reinterpreted as coordinate time' in joined
    assert 'NOT closed by this pillar' in joined
    assert 'DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN' in joined
    assert 'not a Lean proof' in joined


@pytest.mark.slow
def test_certificate_hyperbolicity_evidence(certificate) -> None:
    hyperbolicity = certificate['hyperbolicity']
    # Constraints (lapse, shift) carry no genuine second time derivative.
    assert hyperbolicity['h_equation_is_nondynamical'] is True
    assert hyperbolicity['N_equation_is_constraint'] is True
    assert hyperbolicity['Nx_equation_is_constraint'] is True
    # An off-shell acceleration term does not establish a constrained solution.
    assert hyperbolicity['p_equation_is_dynamical'] is True
    assert hyperbolicity['coeff_d2h_dt2_in_h_equation'] == 0
    assert hyperbolicity['coeff_d2p_dt2_in_p_equation'] != 0
    assert all(
        coefficient == 0
        for equation in hyperbolicity['constraint_acceleration_coefficients'].values()
        for coefficient in equation.values()
    )
    assert certificate['t_dynamics_derived_from_action'] is False
    assert certificate['off_shell_time_derivative_terms_derived'] is True
    assert certificate['constraint_compatible_nonconstant_scalar_evolution'] is False
    assert certificate['well_posedness_established'] is False


@pytest.mark.slow
def test_certificate_static_reduction_cross_check_is_exact(certificate) -> None:
    cross_check = certificate['static_reduction_cross_check']
    assert cross_check['h_equation_matches_exactly'] is True
    assert cross_check['p_equation_matches_exactly'] is True
    assert cross_check['diff_h_equation'] == 0
    assert cross_check['diff_p_equation'] == 0
    assert cross_check['repo_helpers_used'] == [
        '_symbolic_setup', '_sym_ricci_scalar', '_sym_reduced_lagrangian',
    ]


@pytest.mark.slow
def test_certificate_verified_and_fails_closed(certificate) -> None:
    assert certificate['verified'] is True
    assert all(certificate['evidence_checks'].values())
    assert certificate['closure_earned'] is False
    assert certificate['status'] == NEW_CERTIFIED_SUBCASE


def test_certificate_fails_closed_when_hyperbolicity_evidence_fails(monkeypatch) -> None:
    def failing_hyperbolicity():
        return {
            'h_equation_is_nondynamical': False,
            'p_equation_is_dynamical': True,
            'N_equation_is_constraint': True,
            'Nx_equation_is_constraint': True,
        }

    monkeypatch.setattr(p1132, '_adm_hyperbolicity_evidence', failing_hyperbolicity)
    result = p1132.adm_homogeneous_hyperbolic_evolution_certificate()
    assert result['verified'] is False
    assert result['status'] == 'ADM_HOMOGENEOUS_HYPERBOLIC_EVOLUTION_NOT_VERIFIED'


def test_certificate_fails_closed_when_cross_check_fails(monkeypatch) -> None:
    def failing_cross_check():
        return {
            'h_equation_matches_exactly': False,
            'p_equation_matches_exactly': True,
        }

    monkeypatch.setattr(p1132, '_adm_static_reduction_cross_check', failing_cross_check)
    result = p1132.adm_homogeneous_hyperbolic_evolution_certificate()
    assert result['verified'] is False


@pytest.mark.slow
@pytest.mark.parametrize("equation", ["N", "Nx"])
@pytest.mark.parametrize("field", ["h", "p", "N", "Nx"])
def test_constraint_flags_reject_any_second_time_coefficient(monkeypatch, equation, field):
    original = p1132._coeff_of_second_time_derivative
    calls = 0
    target_call = 3 + 4 * ["N", "Nx"].index(equation) + ["h", "p", "N", "Nx"].index(field)

    def inject_acceleration(sympy, expression, derivative):
        nonlocal calls
        call = calls
        calls += 1
        return sp.Integer(1) if call == target_call else original(sympy, expression, derivative)

    monkeypatch.setattr(p1132, "_coeff_of_second_time_derivative", inject_acceleration)
    evidence = p1132._adm_hyperbolicity_evidence.__wrapped__()
    assert evidence["constraint_acceleration_coefficients"][equation][field] == 1
    assert evidence[f"{equation}_equation_is_constraint"] is False
    if equation == "N":
        assert evidence["N_equation_has_no_real_second_time_derivative"] is False
    monkeypatch.setattr(p1132, "_adm_hyperbolicity_evidence", lambda: evidence)
    assert p1132.adm_homogeneous_hyperbolic_evolution_certificate()["verified"] is False


@pytest.mark.slow
def test_truth_surfaces_synchronized(packet) -> None:
    assert packet['truth_surface_sync']['all_pass'] is True


@pytest.mark.slow
def test_packet_valid(packet) -> None:
    assert packet['valid'] is True
    assert packet['status'] == PILLAR_STATUS
    assert packet['framework_closure_earned'] is False
    assert packet['remaining_residual_obligations'] == REMAINING_RESIDUAL_OBLIGATIONS


@pytest.mark.slow
def test_summary() -> None:
    summary = pillar1132_summary()
    assert summary['valid'] is True
    assert summary['verified'] is True
    assert summary['framework_closure_earned'] is False
    assert summary['status'] == PILLAR_STATUS
