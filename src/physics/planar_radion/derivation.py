# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Exact symbolic checks for the planar Einstein--radion reduction.

The functions here build and simplify the identities from their defining
expressions.  They intentionally return symbolic residuals rather than
certificate/status flags.
"""

from __future__ import annotations

from functools import lru_cache

import sympy as sp


def _fields():
    u, v, x, y = sp.symbols("u v x y", real=True)
    r = sp.Function("r")(u, v)
    sigma = sp.Function("sigma")(u, v)
    psi = sp.Function("psi")(u, v)
    return (u, v, x, y), r, sigma, psi


def null_evolution_residuals():
    """Return the three equations from the reduced action in null gauge."""
    (u, v, _, _), r, sigma, psi = _fields()
    ru, rv = sp.diff(r, u), sp.diff(r, v)
    pu, pv = sp.diff(psi, u), sp.diff(psi, v)
    return {
        "r": sp.diff(r, u, v) + ru * rv / r,
        "psi": sp.diff(psi, u, v) + (ru * pv + rv * pu) / r,
        "sigma": sp.diff(sigma, u, v) - ru * rv / r**2
        + sp.Rational(3, 4) * pu * pv,
    }


def null_constraints():
    """Return the null constraints obtained by varying the metric pre-gauge."""
    (u, v, _, _), r, sigma, psi = _fields()
    ru, rv = sp.diff(r, u), sp.diff(r, v)
    pu, pv = sp.diff(psi, u), sp.diff(psi, v)
    return {
        "u": sp.diff(r, u, 2) - 2 * sp.diff(sigma, u) * ru
        + sp.Rational(3, 4) * r * pu**2,
        "v": sp.diff(r, v, 2) - 2 * sp.diff(sigma, v) * rv
        + sp.Rational(3, 4) * r * pv**2,
    }


def metric_variation_residuals():
    """Check that the pre-gauge metric Euler tensor gives both constraints.

    The tensor is the result of varying the covariant reduced action with
    respect to q^{ab}, integrating the curvature variation by parts, and only
    then inserting q=-exp(2 sigma) du dv. The r and psi Euler derivatives are
    also computed from the resulting gauge-fixed action density.
    """
    (u, v, _, _), r, sigma, psi = _fields()
    coordinates = (u, v)
    metric = sp.Matrix([
        [0, -sp.exp(2 * sigma) / 2],
        [-sp.exp(2 * sigma) / 2, 0],
    ])
    inverse = metric.inv()
    christoffel = {}
    for a in range(2):
        for b in range(2):
            for c in range(2):
                christoffel[a, b, c] = sp.simplify(sum(
                    inverse[a, d] * (
                        sp.diff(metric[d, c], coordinates[b])
                        + sp.diff(metric[d, b], coordinates[c])
                        - sp.diff(metric[b, c], coordinates[d])
                    ) for d in range(2)
                ) / 2)

    fields = {"r2": r**2, "psi": psi}
    gradients = {
        name: [sp.diff(field, coordinate) for coordinate in coordinates]
        for name, field in fields.items()
    }
    hessians = {}
    for name, field in fields.items():
        hessians[name] = sp.Matrix(2, 2, lambda a, b: (
            sp.diff(field, coordinates[a], coordinates[b])
            - sum(christoffel[c, a, b] * gradients[name][c] for c in range(2))
        ))
    box_r2 = sum(
        inverse[a, b] * hessians["r2"][a, b]
        for a in range(2) for b in range(2)
    )
    grad_r = [sp.diff(r, coordinate) for coordinate in coordinates]
    grad_r_norm = sum(
        inverse[a, b] * grad_r[a] * grad_r[b]
        for a in range(2) for b in range(2)
    )
    grad_psi2 = sum(
        inverse[a, b] * gradients["psi"][a] * gradients["psi"][b]
        for a in range(2) for b in range(2)
    )
    euler_tensor = sp.zeros(2)
    for a in range(2):
        for b in range(2):
            euler_tensor[a, b] = (
                metric[a, b] * box_r2 - hessians["r2"][a, b]
                + 2 * sp.diff(r, coordinates[a]) * sp.diff(r, coordinates[b])
                - metric[a, b] * grad_r_norm
                - sp.Rational(3, 2) * r**2
                * gradients["psi"][a] * gradients["psi"][b]
                + sp.Rational(3, 4) * metric[a, b] * r**2 * grad_psi2
            )
    constraints = null_constraints()
    equations = null_evolution_residuals()
    gauge_fixed_density = (
        4 * r**2 * sp.diff(sigma, u, v)
        - 4 * sp.diff(r, u) * sp.diff(r, v)
        + 3 * r**2 * sp.diff(psi, u) * sp.diff(psi, v)
    )
    radion_euler = (
        sp.diff(gauge_fixed_density, r)
        - sp.diff(sp.diff(gauge_fixed_density, sp.diff(r, u)), u)
        - sp.diff(sp.diff(gauge_fixed_density, sp.diff(r, v)), v)
    )
    psi_euler = (
        -sp.diff(sp.diff(gauge_fixed_density, sp.diff(psi, u)), u)
        - sp.diff(sp.diff(gauge_fixed_density, sp.diff(psi, v)), v)
    )
    return {
        "uu": sp.simplify(euler_tensor[0, 0] + 2 * r * constraints["u"]),
        "vv": sp.simplify(euler_tensor[1, 1] + 2 * r * constraints["v"]),
        "uv": sp.simplify(euler_tensor[0, 1] - 2 * r * equations["r"]),
        "radion_euler_reduction": sp.simplify(
            radion_euler - 8 * r * (equations["sigma"] + equations["r"] / r)
        ),
        "psi_euler_reduction": sp.simplify(
            psi_euler + 6 * r**2 * equations["psi"]
        ),
    }


def constraint_propagation_residuals():
    """Differentiate r C_u and r C_v and use only evolution equations."""
    (u, v, _, _), r, sigma, psi = _fields()
    ru, rv = sp.diff(r, u), sp.diff(r, v)
    pu, pv = sp.diff(psi, u), sp.diff(psi, v)
    r_uv = -ru * rv / r
    psi_uv = -(ru * pv + rv * pu) / r
    sigma_uv = ru * rv / r**2 - sp.Rational(3, 4) * pu * pv
    constraints = null_constraints()
    du = sp.diff(r * constraints["u"], v).subs(
        sp.diff(r, u, u, v), sp.diff(r_uv, u)
    )
    dv = sp.diff(r * constraints["v"], u).subs(
        sp.diff(r, v, v, u), sp.diff(r_uv, v)
    )
    substitutions = {
        sp.diff(r, u, v): r_uv,
        sp.diff(psi, u, v): psi_uv,
        sp.diff(sigma, u, v): sigma_uv,
    }
    du = du.subs(substitutions)
    dv = dv.subs(substitutions)
    return {"u": sp.factor(du), "v": sp.factor(dv)}


def scalar_energy_balance_residual():
    """Derive the local radion-weighted scalar energy balance from its EOM."""
    t, x = sp.symbols("t x", real=True)
    r = sp.Function("r")(t, x)
    psi = sp.Function("psi")(t, x)
    psi_t, psi_x = sp.diff(psi, t), sp.diff(psi, x)
    energy_density = sp.Rational(1, 2) * r**2 * (psi_t**2 + psi_x**2)
    flux = r**2 * psi_t * psi_x
    radion_work = r * sp.diff(r, t) * (psi_x**2 - psi_t**2)
    wave_equation = (
        sp.diff(psi, t, 2) - sp.diff(psi, x, 2)
        + 2 * sp.diff(r, t) * psi_t / r
        - 2 * sp.diff(r, x) * psi_x / r
    )
    residual = sp.diff(energy_density, t) - sp.diff(flux, x) - radion_work
    residual = residual.subs(
        sp.diff(psi, t, 2),
        sp.diff(psi, x, 2)
        - 2 * sp.diff(r, t) * psi_t / r
        + 2 * sp.diff(r, x) * psi_x / r,
    )
    return sp.simplify(residual), wave_equation


@lru_cache(maxsize=1)
def direct_ricci_residuals():
    """Compute Ricci from the 4D metric and compare to planar warped products.

    The metric is ds^2=-exp(2 sigma) du dv+r^2(dx^2+dy^2).  Christoffels and
    Ricci are constructed directly from this matrix; no warped-product Ricci
    formula is used in the computation.
    """
    coordinates, r, sigma, _ = _fields()
    u, v, x, y = coordinates
    metric = sp.zeros(4)
    metric[0, 1] = metric[1, 0] = -sp.exp(2 * sigma) / 2
    metric[2, 2] = metric[3, 3] = r**2
    inverse = metric.inv()

    christoffel = {}
    for a in range(4):
        for b in range(4):
            for c in range(b, 4):
                component = sum(
                    inverse[a, d]
                    * (sp.diff(metric[d, c], coordinates[b])
                       + sp.diff(metric[d, b], coordinates[c])
                       - sp.diff(metric[b, c], coordinates[d]))
                    for d in range(4)
                ) / 2
                if component != 0:
                    christoffel[a, b, c] = component
                    christoffel[a, c, b] = component

    ricci = sp.zeros(4)
    for a in range(4):
        for b in range(4):
            value = 0
            for c in range(4):
                value += sp.diff(christoffel.get((c, a, b), 0), coordinates[c])
                value -= sp.diff(christoffel.get((c, a, c), 0), coordinates[b])
                for d in range(4):
                    value += (
                        christoffel.get((c, c, d), 0)
                        * christoffel.get((d, a, b), 0)
                        - christoffel.get((c, b, d), 0)
                        * christoffel.get((d, a, c), 0)
                    )
            ricci[a, b] = sp.simplify(value)

    expected = {
        (0, 0): -2 * (sp.diff(r, u, 2) - 2 * sp.diff(sigma, u) * sp.diff(r, u)) / r,
        (1, 1): -2 * (sp.diff(r, v, 2) - 2 * sp.diff(sigma, v) * sp.diff(r, v)) / r,
        (0, 1): -2 * sp.diff(sigma, u, v) - 2 * sp.diff(r, u, v) / r,
        (1, 0): -2 * sp.diff(sigma, u, v) - 2 * sp.diff(r, u, v) / r,
        (2, 2): 4 * sp.exp(-2 * sigma) * (
            r * sp.diff(r, u, v) + sp.diff(r, u) * sp.diff(r, v)
        ),
        (3, 3): 4 * sp.exp(-2 * sigma) * (
            r * sp.diff(r, u, v) + sp.diff(r, u) * sp.diff(r, v)
        ),
    }
    return {
        f"R_{i}{j}": sp.simplify(ricci[i, j] - expected.get((i, j), 0))
        for i in range(4) for j in range(4)
    }


@lru_cache(maxsize=1)
def direct_five_dimensional_uplift_residuals():
    """Compute the uplift Ricci tensor directly and impose the reduced EOM.

    The actual diagonal five-metric is built in (t,x,X,Y,z) coordinates as
    diag(-e^(2 sigma-psi), e^(2 sigma-psi), r^2 e^-psi, r^2 e^-psi,
    e^(2 psi)). No KK Ricci formula is used.
    """
    t, x = sp.symbols("t x", real=True)
    sigma = sp.Function("sigma")(t, x)
    r = sp.Function("r")(t, x)
    psi = sp.Function("psi")(t, x)
    coordinates = (t, x, sp.Symbol("X"), sp.Symbol("Y"), sp.Symbol("z"))
    metric = sp.diag(
        -sp.exp(2 * sigma - psi),
        sp.exp(2 * sigma - psi),
        r**2 * sp.exp(-psi),
        r**2 * sp.exp(-psi),
        sp.exp(2 * psi),
    )
    inverse = metric.inv()
    christoffel = {}
    for a in range(5):
        for b in range(5):
            for c in range(b, 5):
                component = sp.S.Zero
                for d in range(5):
                    if inverse[a, d] == 0:
                        continue
                    component += inverse[a, d] * (
                        sp.diff(metric[d, c], coordinates[b])
                        + sp.diff(metric[d, b], coordinates[c])
                        - sp.diff(metric[b, c], coordinates[d])
                    ) / 2
                if component != 0:
                    christoffel[a, b, c] = component
                    christoffel[a, c, b] = component

    ricci = sp.zeros(5)
    for a in range(5):
        for b in range(5):
            value = sp.S.Zero
            for c in range(5):
                value += sp.diff(christoffel.get((c, a, b), 0), coordinates[c])
                value -= sp.diff(christoffel.get((c, a, c), 0), coordinates[b])
                for d in range(5):
                    value += (
                        christoffel.get((c, c, d), 0)
                        * christoffel.get((d, a, b), 0)
                        - christoffel.get((c, b, d), 0)
                        * christoffel.get((d, a, c), 0)
                    )

            # Evolution equations in (t,x): each wave equation supplies
            # field_tt-field_xx. Residuals are substituted, never asserted.
            rtt_rhs = sp.diff(r, x, 2) - (
                sp.diff(r, t)**2 - sp.diff(r, x)**2
            ) / r
            psitt_rhs = sp.diff(psi, x, 2) - 2 * (
                sp.diff(r, t) * sp.diff(psi, t)
                - sp.diff(r, x) * sp.diff(psi, x)
            ) / r
            sigmatt_rhs = sp.diff(sigma, x, 2) + (
                (sp.diff(r, t)**2 - sp.diff(r, x)**2) / r**2
                - sp.Rational(3, 4) * (
                    sp.diff(psi, t)**2 - sp.diff(psi, x)**2
                )
            )
            value = value.subs({
                sp.diff(r, t, 2): rtt_rhs,
                sp.diff(psi, t, 2): psitt_rhs,
                sp.diff(sigma, t, 2): sigmatt_rhs,
            })

            # The two null constraints determine the remaining r_xx and r_tx
            # combinations; apply their linear consequences after the wave eq.
            ruu = (
                (sp.diff(sigma, t) - sp.diff(sigma, x))
                * (sp.diff(r, t) - sp.diff(r, x)) / 2
                - sp.Rational(3, 16) * r
                * (sp.diff(psi, t) - sp.diff(psi, x))**2
            )
            rvv = (
                (sp.diff(sigma, t) + sp.diff(sigma, x))
                * (sp.diff(r, t) + sp.diff(r, x)) / 2
                - sp.Rational(3, 16) * r
                * (sp.diff(psi, t) + sp.diff(psi, x))**2
            )
            ruv = -(sp.diff(r, t)**2 - sp.diff(r, x)**2) / (4 * r)
            rtt_rhs = ruu + rvv + 2 * ruv
            rxx_rhs = ruu + rvv - 2 * ruv
            rtx_rhs = rvv - ruu
            value = value.subs({
                sp.diff(r, t, 2): rtt_rhs,
                sp.diff(r, x, 2): rxx_rhs,
                sp.diff(r, t, x): rtx_rhs,
            })
            ricci[a, b] = sp.simplify(value)

    return {
        f"R5_{i}{j}": ricci[i, j]
        for i in range(5) for j in range(5)
    }


def frozen_spectator_residuals():
    """Return exact fixed-product Einstein and radion equation components."""
    u, v = sp.symbols("u v", real=True)
    sigma = sp.Function("sigma")(u, v)
    r0 = sp.symbols("r0", positive=True)
    coordinates = (u, v, sp.Symbol("X"), sp.Symbol("Y"))
    metric = sp.diag(0, 0, r0**2, r0**2)
    metric[0, 1] = metric[1, 0] = -sp.exp(2 * sigma) / 2
    inverse = metric.inv()
    christoffel = {}
    for a in range(4):
        for b in range(4):
            for c in range(b, 4):
                component = sum(
                    inverse[a, d] * (
                        sp.diff(metric[d, c], coordinates[b])
                        + sp.diff(metric[d, b], coordinates[c])
                        - sp.diff(metric[b, c], coordinates[d])
                    ) for d in range(4)
                ) / 2
                if component != 0:
                    christoffel[a, b, c] = component
                    christoffel[a, c, b] = component
    ricci = sp.zeros(4)
    for a in range(4):
        for b in range(4):
            value = sp.S.Zero
            for c in range(4):
                value += sp.diff(christoffel.get((c, a, b), 0), coordinates[c])
                value -= sp.diff(christoffel.get((c, a, c), 0), coordinates[b])
                for d in range(4):
                    value += (
                        christoffel.get((c, c, d), 0) * christoffel.get((d, a, b), 0)
                        - christoffel.get((c, b, d), 0) * christoffel.get((d, a, c), 0)
                    )
            ricci[a, b] = sp.simplify(value)
    scalar_curvature = sp.simplify(sum(
        inverse[a, b] * ricci[a, b] for a in range(4) for b in range(4)
    ))
    einstein = sp.Matrix(4, 4, lambda a, b: sp.simplify(
        ricci[a, b] - metric[a, b] * scalar_curvature / 2
    ))

    # A real scalar on this fixed product has these canonical base sources.
    psi_u, psi_v = sp.symbols("psi_u psi_v", real=True)
    source_uu = sp.Rational(3, 2) * psi_u**2
    source_vv = sp.Rational(3, 2) * psi_v**2
    rq = scalar_curvature
    radion_equation = 2 * r0 * rq
    return {
        "base_einstein_uu": einstein[0, 0],
        "base_einstein_uv": einstein[0, 1],
        "base_einstein_vv": einstein[1, 1],
        "source_uu": source_uu,
        "source_vv": source_vv,
        "transverse_einstein_xx": einstein[2, 2],
        "transverse_einstein_yy": einstein[3, 3],
        "radion_equation": radion_equation,
        "nonflat_example": sp.simplify(radion_equation.subs({
            sp.diff(sigma, u, v): 1,
        })),
    }


def frw_kasner_parameters(a, momentum):
    """Return the exact power-law Kasner data for r^2=a t (a != 0)."""
    a, momentum = sp.sympify(a), sp.sympify(momentum)
    if a == 0:
        raise ValueError("the rolling planar branch requires a != 0")
    k = (3 * momentum**2 - a**2) / (4 * a**2)
    return {
        "sigma_log_power": k,
        "proper_time_power": k + 1,
        "longitudinal_kasner_exponent": sp.simplify(k / (k + 1)),
        "transverse_kasner_exponent": sp.simplify(1 / (2 * (k + 1))),
        "scalar_kasner_amplitude": sp.simplify(momentum / (a * (k + 1))),
    }


def frw_branch_residuals():
    """Check the exact rolling FRW branch for either sign of nonzero a.

    On any interval where ``a*t+b > 0``, set r^2=a*t+b.  The integration
    constants in psi and sigma only set their additive origins.
    """
    t, a, b, momentum = sp.symbols("t a b p", real=True)
    psi0, sigma0, scale0 = sp.symbols("psi0 sigma0 scale0", real=True)
    area = a * t + b
    r = sp.sqrt(area)
    k = (3 * momentum**2 - a**2) / (4 * a**2)
    psi = psi0 + momentum / a * sp.log(area / scale0)
    sigma = sigma0 + k * sp.log(area / scale0)
    rt, psit, sigmat = sp.diff(r, t), sp.diff(psi, t), sp.diff(sigma, t)
    rtt, psitt, sigmatt = sp.diff(r, t, 2), sp.diff(psi, t, 2), sp.diff(sigma, t, 2)
    constraints = rtt - 2 * sigmat * rt + sp.Rational(3, 4) * r * psit**2
    equations = {
        "r": rtt + rt**2 / r,
        "psi": psitt + 2 * rt * psit / r,
        "sigma": sigmatt - rt**2 / r**2 + sp.Rational(3, 4) * psit**2,
    }
    return {
        "constraint_u": sp.simplify(constraints / 4),
        "constraint_v": sp.simplify(constraints / 4),
        **{name: sp.simplify(value) for name, value in equations.items()},
    }


def bessel_mode_residual():
    """Check an exact periodic Bessel mode and its coupled sigma quadratures."""
    t, wave_number = sp.symbols("t k", positive=True, real=True)
    x, length = sp.symbols("x L", real=True, positive=True)
    mode_number = sp.symbols("n", integer=True)
    mode = sp.besselj(0, wave_number * t) * sp.cos(wave_number * x)
    residual = sp.diff(mode, t, 2) + sp.diff(mode, t) / t - sp.diff(mode, x, 2)
    periodic_k = 2 * sp.pi * mode_number / length
    periodic_mode = sp.besselj(0, periodic_k * t) * sp.cos(periodic_k * x)
    momentum = sp.integrate(
        t * sp.diff(periodic_mode, t) * sp.diff(periodic_mode, x),
        (x, 0, length),
    )
    return {
        "mode_equation": sp.simplify(residual),
        "solution": mode,
        "periodic_wavenumber": periodic_k,
        "momentum_integral": sp.simplify(momentum),
        "sigma_integrability": areal_sigma_integrability_residuals(),
    }


def areal_sigma_integrability_residuals():
    """Check sigma quadrature compatibility for r^2=t and scalar-wave data."""
    t, x = sp.symbols("t x", real=True, positive=True)
    psi = sp.Function("psi")(t, x)
    pt, px = sp.diff(psi, t), sp.diff(psi, x)
    sigma_t = -sp.Rational(1, 4) / t + sp.Rational(3, 4) * t * (pt**2 + px**2)
    sigma_x = sp.Rational(3, 2) * t * pt * px
    wave_equation = sp.diff(psi, t, 2) - sp.diff(psi, x, 2) + pt / t
    integrability = sp.diff(sigma_t, x) - sp.diff(sigma_x, t)
    sigma_wave = (
        sp.diff(sigma_t, t) - sp.diff(sigma_x, x)
        - sp.Rational(1, 4) / t**2
        + sp.Rational(3, 4) * pt**2
        - sp.Rational(3, 4) * px**2
    )
    wave_substitutions = {
        sp.diff(psi, t, 2): sp.diff(psi, x, 2) - pt / t,
        sp.diff(psi, t, 2, x): sp.diff(psi, x, 3) - sp.diff(psi, t, x) / t,
    }
    return {
        "scalar_wave": sp.simplify(wave_equation.subs(
            sp.diff(psi, t, 2), sp.diff(psi, x, 2) - pt / t
        )),
        "quadrature_integrability": sp.simplify(integrability.subs(wave_substitutions)),
        "sigma_wave": sp.simplify(sigma_wave.subs(wave_substitutions)),
    }


def exact_symbolic_checks():
    """Collect identities used by tests and the accompanying derivation note."""
    return {
        "metric_variation": metric_variation_residuals(),
        "constraint_propagation": constraint_propagation_residuals(),
        "scalar_energy_balance": {
            "local_balance": scalar_energy_balance_residual()[0],
        },
        "direct_ricci": direct_ricci_residuals(),
        "direct_5d_uplift_ricci": direct_five_dimensional_uplift_residuals(),
        "frw_branch": frw_branch_residuals(),
        "bessel_mode": bessel_mode_residual(),
        "areal_sigma_integrability": areal_sigma_integrability_residuals(),
    }
