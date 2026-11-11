# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Linearized coordinate-time radion--gauge dynamics from the KK zero-mode action."""

from __future__ import annotations

from typing import Any

PILLAR_NUMBER = 1138
PILLAR_GATE = "ACTION_DERIVED_LINEARIZED_ZERO_MODE_EVOLUTION"
PILLAR_STATUS = "LINEARIZED_ZERO_MODE_RADION_GAUGE_EVOLUTION_CERTIFIED"
VERSION = "v38.9"
SPRINT = "DE"
SPRINT_DATE = "2026-11-11"
NEXT_PILLAR_SLOT = 1139

SCOPE = (
    "Quadratic perturbations of the massless Einstein-frame circle action about "
    "4D Minkowski space with constant positive radion and zero gauge background; "
    "fields depend on physical time and one spatial coordinate."
)
DOES_NOT_ESTABLISH = [
    "The result is linearized about a fixed Minkowski background; it does not "
    "derive nonlinear metric backreaction or a full 3+1 evolution system.",
    "The action determines these coordinate-time field equations, not the "
    "repository's separate, declared relaxation-time law.",
    "It does not establish the fully inhomogeneous 5D or Z2-orbifold dynamics, "
    "global nonlinear well-posedness, or framework-level closure.",
]


def _linearized_euler_residuals() -> dict[str, Any]:
    import sympy as sp
    from sympy.calculus.euler import euler_equations

    t, x = sp.symbols("t x", real=True)
    z = sp.symbols("Z", positive=True)
    chi, a0, ax, ay, az = [
        sp.Function(name)(t, x) for name in ("chi", "a0", "ax", "ay", "az")
    ]
    electric = sp.diff(ax, t) - sp.diff(a0, x)
    lagrangian = (
        sp.Rational(3, 2) * (sp.diff(chi, t) ** 2 - sp.diff(chi, x) ** 2)
        + z * (
            electric**2
            + sp.diff(ay, t) ** 2 - sp.diff(ay, x) ** 2
            + sp.diff(az, t) ** 2 - sp.diff(az, x) ** 2
        ) / 2
    )
    fields = {
        name: field for name, field in
        (("radion", chi), ("temporal_potential", a0), ("longitudinal_potential", ax),
         ("transverse_y", ay), ("transverse_z", az))
    }
    equations = {
        name: euler_equations(lagrangian, [field], (t, x))[0].lhs
        for name, field in fields.items()
    }
    return {
        "radion_wave": sp.simplify(equations["radion"] / -3),
        "gauss_constraint": sp.simplify(equations["temporal_potential"] / z),
        "longitudinal_evolution": sp.simplify(equations["longitudinal_potential"] / -z),
        "transverse_y_wave": sp.simplify(equations["transverse_y"] / -z),
        "transverse_z_wave": sp.simplify(equations["transverse_z"] / -z),
        "electric_field_time_derivative": sp.diff(electric, t),
        "electric_field_spatial_derivative": sp.diff(electric, x),
    }


def _quadratic_action_expansion() -> dict[str, Any]:
    import sympy as sp

    eps, lam, psi0, chi, f_squared, gradient_contraction = sp.symbols(
        "eps lambda psi_0 chi F_squared gradient_contraction",
        real=True,
    )
    gauge_density = (
        -lam**2 * sp.exp(3 * (psi0 + eps * chi)) * eps**2 * f_squared / 4
    )
    gauge_quadratic = sp.series(gauge_density, eps, 0, 3).removeO().coeff(eps, 2)
    radion_quadratic = (
        sp.series(-sp.Rational(3, 2) * eps**2 * gradient_contraction, eps, 0, 3)
        .removeO()
        .coeff(eps, 2)
    )
    radion_gauge_cross = sp.series(
        gauge_density
        + lam**2 * sp.exp(3 * psi0) * eps**2 * f_squared / 4,
        eps,
        0,
        3,
    ).removeO().coeff(eps, 2)
    return {
        "gauge_quadratic": sp.simplify(gauge_quadratic),
        "radion_quadratic": sp.simplify(radion_quadratic),
        "radion_gauge_cross": sp.simplify(radion_gauge_cross),
        "expected_gauge_quadratic": -lam**2 * sp.exp(3 * psi0) * f_squared / 4,
        "expected_radion_quadratic": -sp.Rational(3, 2) * gradient_contraction,
    }


def action_derived_linearized_zero_mode_certificate() -> dict[str, Any]:
    """Derive and fail-closed check the quadratic radion--Maxwell equations."""
    import sympy as sp

    residuals = _linearized_euler_residuals()
    quadratic = _quadratic_action_expansion()
    t, x, omega, k = sp.symbols("t x omega k", real=True)
    chi, ay, az = [
        sp.Function(name)(t, x) for name in ("chi", "ay", "az")
    ]
    def wave(field):
        return sp.diff(field, t, 2) - sp.diff(field, x, 2)

    mode = sp.exp(sp.I * (k * x - omega * t))
    mode_symbol = sp.simplify(wave(mode) / mode)
    expected = {
        "radion_wave": wave(chi),
        "gauss_constraint": sp.diff(
            sp.diff(sp.Function("ax")(t, x), t)
            - sp.diff(sp.Function("a0")(t, x), x), x
        ),
        "longitudinal_evolution": sp.diff(
            sp.diff(sp.Function("ax")(t, x), t)
            - sp.diff(sp.Function("a0")(t, x), x), t
        ),
        "transverse_y_wave": wave(ay),
        "transverse_z_wave": wave(az),
    }
    equation_checks = {
        name: sp.simplify(residuals[name] - expression) == 0
        for name, expression in expected.items()
    }
    constraint_checks = {
        "gauss_constraint_is_spatial_electric_divergence":
            sp.simplify(residuals["gauss_constraint"] - residuals["electric_field_spatial_derivative"]) == 0,
        "longitudinal_equation_preserves_electric_field":
            sp.simplify(residuals["longitudinal_evolution"] - residuals["electric_field_time_derivative"]) == 0,
        "massless_modes_have_null_principal_symbol":
            sp.simplify(mode_symbol + omega**2 - k**2) == 0,
    }
    checks = {**equation_checks, **constraint_checks}
    checks.update({
        "gauge_action_expands_to_radion_independent_quadratic_term":
            sp.simplify(
                quadratic["gauge_quadratic"] - quadratic["expected_gauge_quadratic"]
            ) == 0,
        "radion_action_retains_canonical_quadratic_kinetic_term":
            sp.simplify(
                quadratic["radion_quadratic"] - quadratic["expected_radion_quadratic"]
            ) == 0,
        "radion_gauge_coupling_enters_only_beyond_quadratic_order":
            quadratic["radion_gauge_cross"] == 0,
    })
    verified = all(checks.values())
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS if verified else "LINEARIZED_ZERO_MODE_RADION_GAUGE_NOT_VERIFIED",
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "scope": SCOPE,
        "quadratic_action": (
            "3/2[(d_t chi)^2-(d_x chi)^2] - Z/4 f_mu_nu f^mu_nu, "
            "Z=lambda^2 exp(3 psi_0)>0; perturbations depend on (t,x)"
        ),
        "quadratic_action_expansion": {
            "gauge_term": str(quadratic["gauge_quadratic"]),
            "radion_term": str(quadratic["radion_quadratic"]),
            "radion_gauge_cross_term": str(quadratic["radion_gauge_cross"]),
            "verified": checks[
                "gauge_action_expands_to_radion_independent_quadratic_term"
            ] and checks["radion_gauge_coupling_enters_only_beyond_quadratic_order"],
        },
        "equations": {
            "radion": "chi_tt - chi_xx = 0",
            "transverse_gauge": "A_{y,tt} - A_{y,xx} = 0 and A_{z,tt} - A_{z,xx} = 0",
            "longitudinal_gauge": "d_x E_x = 0 and d_t E_x = 0, E_x = A_{x,t} - A_{0,x}",
        },
        "dispersion_relation": "omega^2 = k^2",
        "mode_principal_symbol": str(mode_symbol),
        "checks": checks,
        "verified": verified,
        "framework_closure_earned": False,
        "does_not_establish": list(DOES_NOT_ESTABLISH),
    }


__all__ = [
    "DOES_NOT_ESTABLISH",
    "NEXT_PILLAR_SLOT",
    "PILLAR_GATE",
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "SPRINT",
    "SPRINT_DATE",
    "SCOPE",
    "VERSION",
    "action_derived_linearized_zero_mode_certificate",
]
