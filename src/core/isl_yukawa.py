# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/isl_yukawa.py
======================
Pillar 33 — Kaluza-Klein Yukawa / Inverse-Square-Law (ISL) Fifth-Force Prediction.

Scope correction
----------------
The historical helpers and their numerical defaults below are retained for
compatibility, not as action-derived experimental exclusions. In particular,
``yukawa_correction`` is the correction to the *potential*, not the force;
``yukawa_force_correction`` supplies the point-source force factor. The
cylinder condition is independence from the extra coordinate, not a condition
that the radion is frozen. A stationary potential does not remove a scalar
force sourced by matter. The assumed coupling constants, baryon coupling and
the approximate Eot-Wash bound are not derived from the circle action.
See ``docs/physics/RADION_FIFTH_FORCE_AUDIT.md``.

For a point-source potential -G M1 M2 (1 + alpha exp(-r/lambda))/r,
the fractional force correction is alpha (1+r/lambda) exp(-r/lambda).
The finite homogeneous-sphere helpers implement a separate conditional,
unscreened model, not an actual experimental apparatus. Historical couplings,
mass and bound proxies are not predictions or validated experimental limits.

"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import math


# ---------------------------------------------------------------------------
# Module-level constants (Planck units throughout unless noted)
# ---------------------------------------------------------------------------

#: Historical scalar-coupling input, not a derived matter charge.
ALPHA_RADION: float = 2.0 / 3.0

#: Historical assumed vector-coupling input, not a derived baryon charge.
ALPHA_KK_PHOTON: float = 2.0

#: Planck length in SI metres (NIST CODATA 2022)
L_PLANCK_SI: float = 1.616255e-35   # m

#: Planck mass in SI kilograms (NIST CODATA 2022)
M_PLANCK_SI: float = 2.176434e-8    # kg

#: 1 μm in Planck length units
MICRON_IN_PLANCK: float = 1.0e-6 / L_PLANCK_SI   # ≈ 6.187e28 L_Pl

#: 1 eV in Planck mass units  (1 eV / c² = 1.783e-36 kg; / M_Pl)
EV_IN_PLANCK_MASS: float = 1.783e-36 / M_PLANCK_SI  # ≈ 8.19e-29 M_Pl

#: Reference range for the historical alpha-bound proxy (100 μm).
EOT_WASH_REFERENCE_LAMBDA_PLANCK: float = 100.0 * MICRON_IN_PLANCK

#: Historical proxy normalization, not a published 95% limit.
EOT_WASH_ALPHA_BOUND_AT_REFERENCE: float = 1.0e-3

#: Historical proxy exponent, not a validated empirical fit.
EOT_WASH_BOUND_SLOPE: float = 2.0

#: Canonical braid pair for the (5,7) branch
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
K_CS_CANONICAL: int = 74    # = 5² + 7²
C_S_CANONICAL: float = 12.0 / 37.0


# ---------------------------------------------------------------------------
# yukawa_range_radion
# ---------------------------------------------------------------------------

def yukawa_range_radion(m_phi: float) -> float:
    """Yukawa range of the radion (scalar) channel.

    In natural units the de Broglie wavelength of the radion with mass m_φ is

        λ_φ = ħ c / (m_φ c²) = 1 / m_φ                (Planck units)

    This is the length scale below which the Yukawa correction is of order
    one and above which it is exponentially suppressed.

    Parameters
    ----------
    m_phi : float
        Goldberger–Wise radion mass in Planck units (> 0).

    Returns
    -------
    lambda_phi : float
        Yukawa range in Planck units (> 0).

    Raises
    ------
    ValueError
        If m_phi ≤ 0.
    """
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0, got {m_phi!r}")
    return 1.0 / m_phi


# ---------------------------------------------------------------------------
# yukawa_range_kk
# ---------------------------------------------------------------------------

def yukawa_range_kk(R: float) -> float:
    """Yukawa range of the KK-photon (vector) channel.

    The KK gauge boson A_μ acquires mass m_A = 1/R from the compactification,
    giving Yukawa range λ_A = R.

    Parameters
    ----------
    R : float
        Compactification radius in Planck units (> 0).

    Returns
    -------
    lambda_A : float
        Yukawa range in Planck units (= R).

    Raises
    ------
    ValueError
        If R ≤ 0.
    """
    if R <= 0.0:
        raise ValueError(f"R must be > 0, got {R!r}")
    return R


# ---------------------------------------------------------------------------
# yukawa_correction
# ---------------------------------------------------------------------------

def yukawa_correction(r: float, alpha: float, yukawa_lambda: float) -> float:
    """Fractional correction to the Newtonian potential, α e^{−r/λ}.

    This is not the acceleration correction. The latter also contains the
    factor (1 + r/λ); see ``yukawa_force_correction``.

    Parameters
    ----------
    r : float
        Test-mass separation in Planck units (> 0).
    alpha : float
        Dimensionless coupling strength (can be positive or negative).
    yukawa_lambda : float
        Yukawa range in Planck units (> 0).

    Returns
    -------
    delta_g_over_g : float
        Fractional correction to Newtonian gravity (dimensionless).

    Raises
    ------
    ValueError
        If r ≤ 0 or yukawa_lambda ≤ 0.
    """
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    if yukawa_lambda <= 0.0:
        raise ValueError(f"yukawa_lambda must be > 0, got {yukawa_lambda!r}")
    return alpha * math.exp(-r / yukawa_lambda)


def yukawa_force_correction(r: float, alpha: float, yukawa_lambda: float) -> float:
    """Point-source force correction from the derivative of ``isl_potential``.

    All lengths use the same units; alpha is the signed dimensionless
    potential coefficient. This does not model finite bodies or screening.
    """
    if not all(math.isfinite(value) for value in (r, alpha, yukawa_lambda)):
        raise ValueError("r, alpha and yukawa_lambda must be finite")
    if r <= 0.0 or yukawa_lambda <= 0.0:
        raise ValueError("r and yukawa_lambda must be positive")
    x = r / yukawa_lambda
    if not math.isfinite(x):
        return 0.0
    if x >= 500.0 and alpha != 0.0:
        magnitude = math.exp(math.log(abs(alpha)) + math.log1p(x) - x)
        return math.copysign(magnitude, alpha)
    return alpha * (math.exp(-x) + x * math.exp(-x))


def homogeneous_sphere_yukawa_force_correction(
    r: float, radius: float, alpha: float, yukawa_lambda: float
) -> float:
    """Unscreened Yukawa force correction outside a homogeneous source sphere.

    The test body is pointlike, the source has uniform scalar charge per unit
    mass, and r >= radius. All lengths must use the same units. This is not a
    torsion-balance geometry or an experimental exclusion.
    """
    if not all(math.isfinite(value) for value in (r, radius, alpha, yukawa_lambda)):
        raise ValueError("all arguments must be finite")
    if radius <= 0 or yukawa_lambda <= 0 or r < radius:
        raise ValueError("require r >= radius > 0 and yukawa_lambda > 0")
    x = radius / yukawa_lambda
    y = r / yukawa_lambda
    if not math.isfinite(x) or not math.isfinite(y):
        raise ValueError("length ratios overflow; rescale inputs")
    if alpha == 0.0:
        return 0.0
    if x < 0.05:
        x2 = x * x
        form = 1.0 + x2 / 10.0 + x2 * x2 / 280.0 + x2 * x2 * x2 / 15120.0
        result = form * yukawa_force_correction(r, alpha, yukawa_lambda)
    else:
        gap = (r - radius) / yukawa_lambda
        if not math.isfinite(gap):
            raise ValueError("surface separation ratio overflowed")
        # The exponential is combined with the sphere form factor to avoid
        # overflow of cosh(R/lambda) at short range.
        bracket = (1.0 - 1.0 / x) + (1.0 + 1.0 / x) * math.exp(-2.0 * x)
        log_magnitude = (
            math.log(abs(alpha)) + math.log(1.5) + math.log1p(y)
            - 2.0 * math.log(x) + math.log(bracket) - gap
        )
        try:
            result = math.copysign(math.exp(log_magnitude), alpha)
        except OverflowError as exc:
            raise ValueError("sphere force correction overflowed") from exc
    if not math.isfinite(result):
        raise ValueError("sphere force correction overflowed")
    return result


def homogeneous_sphere_eotvos_parameter(
    r: float,
    radius: float,
    yukawa_lambda: float,
    source_charge: float,
    charge_a: float,
    charge_b: float,
) -> float:
    """Exact point-test Eotvos ratio for the unscreened linear sphere model.

    Scalar charges use q = M_Pl d(ln m)/d(varphi); the source is uniform in
    charge per mass. The Newtonian acceleration is normalized to one.
    """
    if not all(math.isfinite(q) for q in (source_charge, charge_a, charge_b)):
        raise ValueError("scalar charges must be finite")
    response = homogeneous_sphere_yukawa_force_correction(
        r, radius, 1.0, yukawa_lambda
    )
    a = 1.0 + 2.0 * source_charge * charge_a * response
    b = 1.0 + 2.0 * source_charge * charge_b * response
    if not math.isfinite(a) or not math.isfinite(b) or a <= 0.0 or b <= 0.0:
        raise ValueError("both inward accelerations must be finite and positive")
    difference = 2.0 * source_charge * (charge_a - charge_b) * response
    result = abs(difference) / (0.5 * a + 0.5 * b)
    if not math.isfinite(result):
        raise ValueError("Eotvos parameter overflowed")
    return result


def periodic_slab_yukawa_coefficients(
    separation: float,
    thickness_a: float,
    thickness_b: float,
    wavenumber: float,
    yukawa_lambda: float,
    density_amplitude_a: float,
    density_amplitude_b: float,
    alpha: float,
    gravitational_constant: float,
) -> tuple[float, float]:
    """Yukawa energy and lateral-force coefficients for patterned slabs.

    The infinite parallel slabs have uniform depth profiles and density
    harmonic components ``density_amplitude_i * cos(k*x)``. Physical total
    densities also need suitable nonnegative mean components. For their
    lateral offset ``delta``, the energy per unit area is ``-C*cos(k*delta)``
    and the force per unit area on the displaced slab is ``-D*sin(k*delta)``.
    The returned values are ``(C, D)`` with ``D = k*C``. Mean densities do
    not contribute to these nonzero-wavenumber coefficients.

    SI inputs give J/m² and N/m² respectively. All inputs must use mutually
    consistent units. This infinite, planar harmonic approximation is not the
    patterned rotating Eot-Wash apparatus or a measured likelihood.
    """
    values = (separation, thickness_a, thickness_b, wavenumber, yukawa_lambda,
              density_amplitude_a, density_amplitude_b, alpha, gravitational_constant)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("all arguments must be finite")
    if separation < 0 or min(thickness_a, thickness_b, wavenumber,
                             yukawa_lambda, gravitational_constant) <= 0:
        raise ValueError("separation must be nonnegative and lengths, k and G positive")
    if alpha == 0 or density_amplitude_a == 0 or density_amplitude_b == 0:
        return 0.0, 0.0
    inverse_range = 1.0 / yukawa_lambda
    p = math.hypot(wavenumber, inverse_range)
    if not math.isfinite(p):
        raise ValueError("inverse range or wavenumber is too large")
    gap = p * separation
    if not math.isfinite(gap):
        return 0.0, 0.0

    def log_depth_factor(thickness: float) -> float:
        product = p * thickness
        if product == 0.0:
            return math.log(p) + math.log(thickness)
        if math.isinf(product):
            return 0.0
        return math.log(-math.expm1(-product))

    log_c = (
        math.log(math.pi) + math.log(gravitational_constant)
        + math.log(abs(alpha)) + math.log(abs(density_amplitude_a))
        + math.log(abs(density_amplitude_b)) - 3.0 * math.log(p) - gap
        + log_depth_factor(thickness_a) + log_depth_factor(thickness_b)
    )
    sign = (
        math.copysign(1.0, alpha) * math.copysign(1.0, density_amplitude_a)
        * math.copysign(1.0, density_amplitude_b)
    )
    try:
        return sign * math.exp(log_c), sign * math.exp(log_c + math.log(wavenumber))
    except OverflowError as exc:
        raise ValueError("patterned slab response overflowed") from exc


def gaussian_ring_yukawa_torque_coefficient(
    separation: float,
    thickness_a: float,
    thickness_b: float,
    radius_scale_a: float,
    radius_scale_b: float,
    harmonic: int,
    yukawa_lambda: float,
    density_amplitude_a: float,
    density_amplitude_b: float,
    alpha: float,
    gravitational_constant: float,
) -> float:
    """Torque amplitude for two idealized coaxial Gaussian-ring harmonics.

    The nonzero-harmonic mass density of each slab is
    ``rho_i * g_m(r/a_i) * cos(m*theta)``, constant through its thickness,
    where ``g_m(s) = (s/sqrt(m))**m * exp((m-s*s)/2)`` has maximum one.
    Add a nonnegative axisymmetric density to obtain a physical total density.
    If slab b is rotated by delta, its Yukawa torque is ``-T*sin(m*delta)``.

    SI inputs give T in N m. This infinite-extent idealized radial profile
    is not the measured Eot-Wash hole pattern, torque or likelihood.
    """
    from scipy.integrate import quad

    values = (separation, thickness_a, thickness_b, radius_scale_a,
              radius_scale_b, yukawa_lambda, density_amplitude_a,
              density_amplitude_b, alpha, gravitational_constant)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("all arguments must be finite")
    if not isinstance(harmonic, int) or isinstance(harmonic, bool) or not 1 <= harmonic <= 512:
        raise ValueError("harmonic must be an integer between 1 and 512")
    if separation < 0 or min(thickness_a, thickness_b, radius_scale_a,
                             radius_scale_b, yukawa_lambda, gravitational_constant) <= 0:
        raise ValueError("separation must be nonnegative and lengths and G positive")
    if alpha == 0 or density_amplitude_a == 0 or density_amplitude_b == 0:
        return 0.0
    scale = math.hypot(radius_scale_a, radius_scale_b) / math.sqrt(2)
    ratio = scale / yukawa_lambda
    gap = separation / scale
    depth_a = thickness_a / scale
    depth_b = thickness_b / scale
    if not all(math.isfinite(v) for v in (scale, ratio, gap, depth_a, depth_b)):
        raise ValueError("length ratios overflowed")
    m = harmonic
    log_gamma = math.lgamma(m + 1)

    def integrand(t: float) -> float:
        if t <= 0:
            return 0.0
        h = math.hypot(math.sqrt(t), ratio)
        if h == 0:
            raise ValueError("dimensionless inverse range underflowed")
        log_value = (
            m * math.log(t) - t - log_gamma - h * gap - 3 * math.log(h)
        )
        fa = -math.expm1(-h * depth_a)
        fb = -math.expm1(-h * depth_b)
        if fa == 0 or fb == 0:
            raise ValueError("dimensionless thickness underflowed")
        return math.exp(log_value + math.log(fa) + math.log(fb))

    # Split at the mode of the gamma weight so high harmonics are not missed.
    pieces = (
        quad(integrand, 0, m, epsabs=0, epsrel=1e-9, limit=200, full_output=1),
        quad(integrand, m, math.inf, epsabs=0, epsrel=1e-9, limit=200, full_output=1),
    )
    if any(len(part) != 3 for part in pieces):
        raise ValueError("ring torque quadrature failed to converge")
    integral = sum(part[0] for part in pieces)
    if not math.isfinite(integral) or integral <= 0:
        raise ValueError("ring torque quadrature is nonfinite or underflowed")
    log_torque = (
        2 * math.log(math.pi) + math.log(gravitational_constant)
        + math.log(abs(alpha)) + math.log(abs(density_amplitude_a))
        + math.log(abs(density_amplitude_b)) + math.log(m) + math.log(scale)
        + 2 * math.log(radius_scale_a) + 2 * math.log(radius_scale_b)
        + m * (math.log(radius_scale_a) + math.log(radius_scale_b)
               - 2 * math.log(scale) + 1 - math.log(m))
        + log_gamma + math.log(integral)
    )
    sign = (math.copysign(1.0, alpha) * math.copysign(1.0, density_amplitude_a)
            * math.copysign(1.0, density_amplitude_b))
    try:
        result = math.copysign(math.exp(log_torque), sign)
    except OverflowError as exc:
        raise ValueError("ring torque overflowed") from exc
    if result == 0:
        raise ValueError("ring torque underflowed")
    return result


def voxel_yukawa_energy_and_torque(
    positions_a, masses_a, positions_b, masses_b, rotation: float,
    yukawa_lambda: float, alpha: float, gravitational_constant: float,
    block_size: int = 256,
) -> tuple[float, float]:
    """Midpoint-voxel Yukawa energy and z torque on a rotated body.

    Positions are N-by-3 and M-by-3 arrays relative to a common z axis;
    masses are nonnegative voxel masses. Body b is rotated by ``rotation``
    about that axis, while body a remains fixed. Cartesian coordinates
    and separation use the same units as the positive Yukawa range.

    This pairwise, unscreened point-voxel approximation must be checked
    for grid convergence. It does not infer a material map, model screening,
    or implement the actual apparatus, background subtraction or likelihood.
    SI inputs give energy in joules and torque in newton metres.
    """
    import numpy as np

    scalars = (rotation, yukawa_lambda, alpha, gravitational_constant)
    if not all(math.isfinite(value) for value in scalars):
        raise ValueError("rotation, range, alpha and G must be finite")
    if yukawa_lambda <= 0 or gravitational_constant <= 0:
        raise ValueError("range and G must be positive")
    if not isinstance(block_size, int) or isinstance(block_size, bool) or block_size < 1:
        raise ValueError("block_size must be a positive integer")
    pa, pb = np.asarray(positions_a, dtype=float), np.asarray(positions_b, dtype=float)
    ma, mb = np.asarray(masses_a, dtype=float), np.asarray(masses_b, dtype=float)
    if (pa.ndim != 2 or pa.shape[1] != 3 or pb.ndim != 2 or pb.shape[1] != 3
            or ma.shape != (len(pa),) or mb.shape != (len(pb),)
            or not len(pa) or not len(pb)):
        raise ValueError("positions must be nonempty N-by-3 arrays with matching masses")
    if (not all(np.all(np.isfinite(a)) for a in (pa, pb, ma, mb))
            or np.any(ma < 0) or np.any(mb < 0)):
        raise ValueError("coordinates and masses must be finite; masses must be nonnegative")
    c, s = math.cos(rotation), math.sin(rotation)
    rotated = pb.copy()
    rotated[:, 0] = c * pb[:, 0] - s * pb[:, 1]
    rotated[:, 1] = s * pb[:, 0] + c * pb[:, 1]
    if not np.all(np.isfinite(rotated)):
        raise ValueError("rotated coordinates overflowed")
    energies, torques = [], []
    with np.errstate(over="ignore", under="ignore", invalid="ignore", divide="ignore"):
        for i in range(0, len(pa), block_size):
            a = pa[i:i + block_size]
            for j in range(0, len(pb), block_size):
                b = rotated[j:j + block_size]
                dx = b[None, :, 0] - a[:, None, 0]
                dy = b[None, :, 1] - a[:, None, 1]
                dz = b[None, :, 2] - a[:, None, 2]
                distance = np.hypot(np.hypot(dx, dy), dz)
                if not np.all(np.isfinite(distance)) or np.any(distance == 0):
                    raise ValueError("voxel centers must be distinct and have finite separation")
                x = distance / yukawa_lambda
                exponential = np.exp(-x)
                force_factor = np.zeros_like(x)
                finite = np.isfinite(x)
                force_factor[finite] = exponential[finite] * (1 + x[finite])
                mass_product = ma[i:i + block_size, None] * mb[None, j:j + block_size]
                pair_energy = mass_product * exponential / distance
                cross_over_distance = ((b[None, :, 0] / distance) * dy
                                       - (b[None, :, 1] / distance) * dx)
                pair_torque = -mass_product * force_factor * cross_over_distance / distance / distance
                if not np.all(np.isfinite(pair_energy)) or not np.all(np.isfinite(pair_torque)):
                    raise ValueError("voxel interaction overflowed; rescale inputs")
                energies.append(float(np.sum(pair_energy)))
                torques.append(float(np.sum(pair_torque)))
    energy = -gravitational_constant * alpha * math.fsum(energies)
    torque = gravitational_constant * alpha * math.fsum(torques)
    if not math.isfinite(energy) or not math.isfinite(torque):
        raise ValueError("total voxel interaction overflowed")
    return energy, torque


def digitized_yukawa_excluded_range(
    alpha: float, curve_lambda_m, curve_alpha_limit,
) -> tuple[float, float]:
    """Range interval (m) excluded by a digitized 95% upper limit on |alpha|.

    ``curve`` points are (range, |alpha| limit) and must be strictly
    increasing in range and strictly decreasing in limit, as a monotone
    short-range exclusion curve is. Interpolation is log-log and never
    extrapolates: the returned upper end is the last digitized range, not
    a statement about longer ranges. A value |alpha| below the weakest
    limit in the curve is not excluded and raises ValueError.

    The result inherits the curve's provenance: a community digitization
    is not an official likelihood, and the limit assumes the experiment's
    point-like Yukawa model with its own conventions.
    """
    import numpy as np

    if not math.isfinite(alpha) or alpha == 0:
        raise ValueError("alpha must be finite and nonzero")
    lam = np.asarray(curve_lambda_m, dtype=float)
    lim = np.asarray(curve_alpha_limit, dtype=float)
    if lam.ndim != 1 or lam.shape != lim.shape or len(lam) < 2:
        raise ValueError("curve arrays must be matching one-dimensional arrays")
    if (not np.all(np.isfinite(lam)) or not np.all(np.isfinite(lim))
            or np.any(lam <= 0) or np.any(lim <= 0)
            or np.any(np.diff(lam) <= 0) or np.any(np.diff(lim) >= 0)):
        raise ValueError("curve must be positive, finite, increasing in range, decreasing in limit")
    a = abs(alpha)
    if a < lim[-1]:
        raise ValueError("|alpha| is below the weakest limit; not excluded in the digitized range")
    if a >= lim[0]:
        return float(lam[0]), float(lam[-1])
    log_lambda = np.interp(math.log(a), np.log(lim[::-1]), np.log(lam[::-1]))
    return float(math.exp(log_lambda)), float(lam[-1])


def digitized_yukawa_exclusion_intervals(
    alpha: float, curves, grid_points: int = 40001,
) -> list[tuple[float, float]]:
    """Range intervals (m) where any digitized upper limit lies below |alpha|.

    ``curves`` is a sequence of (range_m, alpha_limit) array pairs. Each
    curve has strictly increasing positive ranges and positive limits, and
    is log-log interpolated only inside its own digitized range; nothing is
    extrapolated. The result is the union over curves, on a log-spaced grid
    with ``grid_points`` samples, so interval endpoints carry grid
    resolution error (a few 1e-4 relative for the default).

    Limits are one-sided and assume each experiment's own point-like Yukawa
    convention and confidence level; independent curves are not combined
    statistically, only overlaid. Community digitizations are not official
    likelihoods.
    """
    import numpy as np

    if not math.isfinite(alpha) or alpha == 0:
        raise ValueError("alpha must be finite and nonzero")
    if not isinstance(grid_points, int) or isinstance(grid_points, bool) or grid_points < 100:
        raise ValueError("grid_points must be an integer of at least 100")
    parsed = []
    for lam, lim in curves:
        lam, lim = np.asarray(lam, dtype=float), np.asarray(lim, dtype=float)
        if lam.ndim != 1 or lam.shape != lim.shape or len(lam) < 2:
            raise ValueError("each curve needs matching one-dimensional arrays")
        if (not np.all(np.isfinite(lam)) or not np.all(np.isfinite(lim))
                or np.any(lam <= 0) or np.any(lim <= 0) or np.any(np.diff(lam) <= 0)):
            raise ValueError("curves must be finite, positive, with increasing range")
        parsed.append((np.log(lam), np.log(lim)))
    if not parsed:
        raise ValueError("at least one curve is required")
    lo = min(c[0][0] for c in parsed)
    hi = max(c[0][-1] for c in parsed)
    grid = np.linspace(lo, hi, grid_points)
    best = np.full(grid_points, np.inf)
    for x, y in parsed:
        inside = (grid >= x[0]) & (grid <= x[-1])
        best[inside] = np.minimum(best[inside], np.interp(grid[inside], x, y))
    excluded = best < math.log(abs(alpha))
    intervals = []
    start = None
    for i, flag in enumerate(excluded):
        if flag and start is None:
            start = i
        if start is not None and (not flag or i == len(excluded) - 1):
            end = i if flag else i - 1
            intervals.append((float(math.exp(grid[start])), float(math.exp(grid[end]))))
            start = None
    return intervals


def flat_interval_scalar_mode(
    k: float, u: float, v0: float, m5: float, length: float,
    stiffness_uv: float, stiffness_ir: float,
    mass_squared_bracket: tuple[float, float],
) -> dict[str, float]:
    """Shoot for a nodeless coupled scalar mode of the tuned flat interval.

    The action, gauge and boundary conditions are specified in
    ``docs/physics/RADION_FIFTH_FORCE_AUDIT.md``. Stiffness may be positive
    infinity for the Dirichlet limit. The bracket is in squared mass units
    in the common 4D coordinates and must isolate a positive nodeless root.
    Charge estimates additionally assume the documented quadratic-action
    normalization and fixed-Jordan-mass boundary matter without direct bulk
    scalar coupling. Their action normalization and sourced residues have
    not been independently established. This does not solve the tensor or
    sourced junction problem and is not an experimental prediction.
    """
    from scipy.integrate import quad, solve_ivp
    from scipy.optimize import brentq

    if not all(math.isfinite(x) and x > 0 for x in (k, u, v0, m5, length)):
        raise ValueError("background parameters must be finite and positive")
    if not all(x > 0 and not math.isnan(x) for x in (stiffness_uv, stiffness_ir)):
        raise ValueError("boundary stiffnesses must be positive or infinity")
    if len(mass_squared_bracket) != 2:
        raise ValueError("mass_squared_bracket must contain two endpoints")
    lo, hi = mass_squared_bracket
    if not all(math.isfinite(x) for x in (lo, hi)) or lo < 0 or hi <= lo:
        raise ValueError("mass-squared bracket must be finite and satisfy 0 <= lo < hi")
    m3 = m5**3
    if not math.isfinite(m3) or m3 == 0:
        raise ValueError("m5 cubed is not representable")

    def background(y):
        chi = v0 * math.exp(-u * y)
        if chi == 0:
            raise ValueError("background scalar underflowed")
        A = k * y - (v0 * v0 - chi * chi) / (12 * m3)
        Ap = k - u * chi * chi / (6 * m3)
        App = (u * chi)**2 / (3 * m3)
        e2A = math.exp(2 * A)
        if not all(math.isfinite(x) for x in (A, Ap, App, e2A)) or App == 0:
            raise ValueError("background is not numerically representable")
        return chi, A, Ap, App, e2A

    uv_weight = 0.0 if math.isinf(stiffness_uv) else 1 / stiffness_uv
    ir_weight = 0.0 if math.isinf(stiffness_ir) else 1 / stiffness_ir
    _, _, _, _, e2A_ir = background(length)

    def shoot(mass_squared, keep=False):
        def rhs(y, state):
            _, _, ap, app, e2a = background(y)
            h, hp = state
            return (hp, -(2 * ap + 2 * u) * hp + (2 * app - mass_squared * e2a) * h)

        def node(y, state):
            return state[0]

        max_step = math.inf
        if keep:
            frequency = math.sqrt(mass_squared) * math.sqrt(max(1.0, e2A_ir))
            max_step = min(length / 128, math.pi / (16 * frequency))
        sol = solve_ivp(
            rhs, (0, length), (1.0, -mass_squared * uv_weight),
            rtol=2e-10, atol=1e-12, dense_output=keep,
            events=node if keep else None,
            max_step=max_step,
        )
        if not sol.success:
            raise ValueError(f"scalar shooting failed: {sol.message}")
        h, hp = sol.y[:, -1]
        residual = hp - mass_squared * e2A_ir * ir_weight * h
        if not math.isfinite(residual):
            raise ValueError("scalar shooting residual is nonfinite")
        return residual, sol

    f_lo, _ = shoot(lo)
    f_hi, _ = shoot(hi)
    if f_lo == 0 or f_hi == 0 or math.copysign(1, f_lo) == math.copysign(1, f_hi):
        raise ValueError("bracket must strictly straddle an eigenvalue")
    mass2 = brentq(lambda value: shoot(value)[0], lo, hi, xtol=5e-324, rtol=1e-12)
    if mass2 <= 0:
        raise ValueError("nonpositive scalar mass squared")
    residual, sol = shoot(mass2, keep=True)
    if len(sol.t_events[0]) != 0:
        raise ValueError("bracket found a mode with nodes, not the nodeless mode")

    def terms(y):
        chi, _, _, app, e2a = background(y)
        h, hp = sol.sol(y)
        p = e2a / (u * chi)**2
        return p * (hp * hp + 2 * app * h * h), p * e2a * h * h

    kinetic = quad(lambda y: terms(y)[0], 0, length, epsabs=0, epsrel=1e-9)[0]
    inertia = quad(lambda y: terms(y)[1], 0, length, epsabs=0, epsrel=1e-9)[0]
    chi0, _, _, _, _ = background(0)
    chil, _, _, _, _ = background(length)
    h0, hl = 1.0, float(sol.y[0, -1])
    inertia += uv_weight / (u * chi0)**2
    inertia += ir_weight * e2A_ir**2 * hl**2 / (u * chil)**2
    norm = 9 * m3**2 * kinetic
    planck2 = m3 * quad(lambda y: 1 / background(y)[4], 0, length, epsabs=0, epsrel=1e-9)[0]
    if not all(math.isfinite(x) and x > 0 for x in (kinetic, inertia, norm, planck2)):
        raise ValueError("mode normalization is nonpositive or nonfinite")
    ratio = kinetic / (mass2 * inertia)
    if not math.isfinite(ratio) or abs(ratio - 1) > 1e-6:
        raise ValueError("mode fails the integrated eigenvalue identity")
    q_uv = -math.sqrt(planck2 / norm) * h0
    q_ir = -math.sqrt(planck2 / norm) * e2A_ir * hl
    return {
        "conditional_alpha_uv_uv": 2 * q_uv * q_uv,
        "conditional_alpha_uv_ir": 2 * q_uv * q_ir,
        "conditional_alpha_ir_ir": 2 * q_ir * q_ir,
        "mass_squared": mass2,
        "planck_mass_squared": planck2,
        "conditional_charge_uv": -math.sqrt(planck2 / norm) * h0,
        "conditional_charge_ir": -math.sqrt(planck2 / norm) * e2A_ir * hl,
        "rayleigh_ratio": ratio,
        "boundary_residual": residual,
    }


def stiff_wall_probe_radion_mass_squared(
    k: float, epsilon: float, v_ir: float, m5: float, warp_factor: float
) -> float:
    """Leading probe-limit radion mass squared for the tuned interval model.

    Assumes fixed scalar endpoint values, an RS metric, weak scalar
    backreaction, the conventional Einstein-frame modulus kinetic term, and
    an isolated low-energy mode. ``epsilon=u/k`` and ``warp_factor=e**(-kL)``
    are positive. k and m5 have mass dimension one, v_ir dimension 3/2.
    This is not the exact 5D eigenmass or a UM prediction.
    """
    values = (k, epsilon, v_ir, m5, warp_factor)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("all arguments must be finite")
    if min(k, epsilon, v_ir, m5) <= 0 or not 0 < warp_factor < 1:
        raise ValueError("k, epsilon, v_ir and m5 must be positive; 0 < warp_factor < 1")
    log_mu = math.log(warp_factor)
    numerator = -math.expm1(2 * log_mu)
    denominator = -math.expm1((4 + 2 * epsilon) * log_mu)
    log_m2 = (
        math.log(2 / 3) + 2 * math.log(k) + math.log(2 + epsilon)
        + 2 * math.log(epsilon) + 2 * math.log(v_ir) + 2 * log_mu
        - 3 * math.log(m5) + math.log(numerator) - math.log(denominator)
    )
    try:
        result = math.exp(log_m2)
    except OverflowError as exc:
        raise ValueError("probe radion mass squared overflowed") from exc
    if result == 0:
        raise ValueError("probe radion mass squared underflowed")
    return result


def reduced_action_radion_mass_squared(m_phi: float, phi0: float) -> float:
    """Mass squared for the optional potential of ``action_derived_flow``.

    The circle-reduced action is R - 3/2 (d ln phi)^2 - U, with
    U = m_phi^2 (phi - phi0)^2 / (2 phi). Linearization about phi0 gives
    m_physical^2 = m_phi^2 phi0 / 3 in the same natural-unit convention.
    The potential is an independent assumption, not derived stabilization.
    At m_phi = 0 the optional potential is absent and this sector is massless.
    """
    if not math.isfinite(m_phi) or not math.isfinite(phi0):
        raise ValueError("m_phi and phi0 must be finite")
    if m_phi < 0.0 or phi0 <= 0.0:
        raise ValueError("m_phi must be nonnegative and phi0 must be positive")
    mass = m_phi * (math.sqrt(phi0) / math.sqrt(3.0))
    result = mass * mass
    if not math.isfinite(result):
        raise ValueError("radion mass squared overflowed")
    return result


# ---------------------------------------------------------------------------
# isl_potential
# ---------------------------------------------------------------------------

def isl_potential(
    r: float,
    M1: float,
    M2: float,
    alpha: float,
    yukawa_lambda: float,
) -> float:
    """Full Yukawa-modified gravitational potential.

    V(r) = −G M₁ M₂ / r × (1 + α e^{−r/λ})

    In Planck units G = 1, so this simplifies to:

        V(r) = −M₁ M₂ / r × (1 + α e^{−r/λ})

    Parameters
    ----------
    r : float
        Test-mass separation in Planck units (> 0).
    M1, M2 : float
        Test masses in Planck units (> 0).
    alpha : float
        Yukawa coupling strength (dimensionless).
    yukawa_lambda : float
        Yukawa range in Planck units (> 0).

    Returns
    -------
    V : float
        Gravitational potential energy in Planck units (≤ 0 for alpha > −1).

    Raises
    ------
    ValueError
        If r ≤ 0, M1 ≤ 0, M2 ≤ 0, or yukawa_lambda ≤ 0.
    """
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    if M1 <= 0.0:
        raise ValueError(f"M1 must be > 0, got {M1!r}")
    if M2 <= 0.0:
        raise ValueError(f"M2 must be > 0, got {M2!r}")
    if yukawa_lambda <= 0.0:
        raise ValueError(f"yukawa_lambda must be > 0, got {yukawa_lambda!r}")
    newton = -M1 * M2 / r
    correction = 1.0 + yukawa_correction(r, alpha, yukawa_lambda)
    return newton * correction


# ---------------------------------------------------------------------------
# cylinder_deviation
# ---------------------------------------------------------------------------

def cylinder_deviation(phi: float, phi0: float) -> float:
    """Normalised deviation from the cylinder condition.

    Historical name: this measures displacement from phi0, not the cylinder
    condition. A y-independent radion may vary in four dimensions, and a
    matter-sourced fifth force can exist even at the vacuum value.

        δ_cyl(φ) = |φ − φ₀| / φ₀

    The value alone does not determine the presence of a Yukawa signal.

    Parameters
    ----------
    phi : float
        Current radion field value in Planck units (> 0).
    phi0 : float
        Reference vacuum value φ₀ in Planck units (> 0).

    Returns
    -------
    delta : float
        Normalised deviation (≥ 0).

    Raises
    ------
    ValueError
        If phi ≤ 0 or phi0 ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be > 0, got {phi0!r}")
    return abs(phi - phi0) / phi0


# ---------------------------------------------------------------------------
# radion_produces_fifth_force
# ---------------------------------------------------------------------------

def radion_produces_fifth_force(
    phi: float,
    phi0: float,
    tol: float = 1e-10,
) -> bool:
    """Return True iff the radion deviates from φ₀ beyond tolerance.

    This legacy displacement predicate does not determine whether a
    matter-sourced fifth force exists.

    Parameters
    ----------
    phi : float — current radion value (> 0)
    phi0 : float — GW vacuum value (> 0)
    tol : float — relative tolerance (default 1e-10)

    Returns
    -------
    bool
    """
    return cylinder_deviation(phi, phi0) > tol


# ---------------------------------------------------------------------------
# eot_wash_alpha_bound
# ---------------------------------------------------------------------------

def eot_wash_alpha_bound(yukawa_lambda: float) -> float:
    """Legacy unvalidated power-law proxy, not an Eöt-Wash exclusion bound.

    Its reference value disagrees with a published community digitization;
    no accuracy, confidence level or conservative coverage is established.
    Its numerical behavior is preserved only for compatibility.

    Parameters
    ----------
    yukawa_lambda : float
        Yukawa range in Planck units (> 0).

    Returns
    -------
    alpha_bound : float
        Historical proxy value (> 0), not an experimental limit.

    Raises
    ------
    ValueError
        If yukawa_lambda ≤ 0.
    """
    if yukawa_lambda <= 0.0:
        raise ValueError(f"yukawa_lambda must be > 0, got {yukawa_lambda!r}")
    ratio = EOT_WASH_REFERENCE_LAMBDA_PLANCK / yukawa_lambda
    return EOT_WASH_ALPHA_BOUND_AT_REFERENCE * (ratio ** EOT_WASH_BOUND_SLOPE)


# ---------------------------------------------------------------------------
# fifth_force_signal_strength
# ---------------------------------------------------------------------------

def fifth_force_signal_strength(
    m_phi: float,
    alpha: float,
    r: float,
) -> float:
    """Legacy potential correction α e^{−r m_φ}, not a force correction.

    Equivalent to yukawa_correction(r, alpha, 1/m_phi).

    Parameters
    ----------
    m_phi : float — radion mass in Planck units (> 0)
    alpha : float — coupling strength (dimensionless)
    r : float     — test-mass separation in Planck units (> 0)

    Returns
    -------
    delta_g_over_g : float

    Raises
    ------
    ValueError if m_phi ≤ 0 or r ≤ 0.
    """
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0, got {m_phi!r}")
    if r <= 0.0:
        raise ValueError(f"r must be > 0, got {r!r}")
    return alpha * math.exp(-r * m_phi)


# ---------------------------------------------------------------------------
# kk_compactification_radius
# ---------------------------------------------------------------------------

def kk_compactification_radius(m_kk: float) -> float:
    """Compactification radius from the KK mass scale.

    The first KK excitation has mass m_KK = 1/R, so the compactification
    radius is R = 1/m_KK.

    Parameters
    ----------
    m_kk : float
        KK mass scale in Planck units (> 0).

    Returns
    -------
    R : float
        Compactification radius in Planck units (> 0).

    Raises
    ------
    ValueError if m_kk ≤ 0.
    """
    if m_kk <= 0.0:
        raise ValueError(f"m_kk must be > 0, got {m_kk!r}")
    return 1.0 / m_kk


# ---------------------------------------------------------------------------
# radion_mass_from_gw
# ---------------------------------------------------------------------------

def radion_mass_from_gw(
    m_phi_bare: float,
    phi0: float,
    phi_min: float,
) -> float:
    """Return a historical bare curvature parameter, not a physical mass.

    Converting potential curvature into a mass requires the kinetic
    normalization and the actual stabilized action, neither supplied here.

    Parameters
    ----------
    m_phi_bare : float — bare GW mass parameter (> 0)
    phi0       : float — GW vacuum expectation value (> phi_min)
    phi_min    : float — GW lower bound on φ (> 0)

    Returns
    -------
    m_phi_eff : float
        Historical input m_phi_bare (Planck units).

    Raises
    ------
    ValueError
        If m_phi_bare ≤ 0, phi_min ≤ 0, or phi0 ≤ phi_min.
    """
    if m_phi_bare <= 0.0:
        raise ValueError(f"m_phi_bare must be > 0, got {m_phi_bare!r}")
    if phi_min <= 0.0:
        raise ValueError(f"phi_min must be > 0, got {phi_min!r}")
    if phi0 <= phi_min:
        raise ValueError(
            f"phi0 ({phi0!r}) must be strictly > phi_min ({phi_min!r})"
        )
    return m_phi_bare


# ---------------------------------------------------------------------------
# isl_summary
# ---------------------------------------------------------------------------

def isl_summary(
    m_phi: float,
    R: float,
    r: float,
) -> dict:
    """Report legacy inputs and potential proxies, not experimental verdicts.

    Deprecated misleading keys remain present with None values; explicitly
    named proxy keys preserve access to the historical numerical calculations.

    Parameters
    ----------
    m_phi : float — radion mass (Planck units, > 0)
    R     : float — compactification radius (Planck units, > 0)
    r     : float — test-mass separation (Planck units, > 0)

    Raises
    ------
    ValueError if m_phi ≤ 0, R ≤ 0, or r ≤ 0.
    """
    lam_phi = yukawa_range_radion(m_phi)
    lam_kk  = yukawa_range_kk(R)

    dg_phi = yukawa_correction(r, ALPHA_RADION,   lam_phi)
    dg_kk  = yukawa_correction(r, ALPHA_KK_PHOTON, lam_kk)

    bound_phi = eot_wash_alpha_bound(lam_phi)
    bound_kk  = eot_wash_alpha_bound(lam_kk)

    return {
        "status": "UNVALIDATED LEGACY PROXIES; NO EXPERIMENTAL VERDICT",
        "lambda_radion": lam_phi,
        "lambda_kk": lam_kk,
        "alpha_radion": ALPHA_RADION,
        "alpha_kk": ALPHA_KK_PHOTON,
        "potential_correction_radion_proxy": dg_phi,
        "potential_correction_kk_proxy": dg_kk,
        "alpha_bound_radion_proxy": bound_phi,
        "alpha_bound_kk_proxy": bound_kk,
        "delta_g_radion": None,
        "delta_g_kk": None,
        "eot_wash_bound_radion": None,
        "eot_wash_bound_kk": None,
        "radion_detectable": None,
        "kk_detectable": None,
        "cylinder_condition": "not determined by these inputs",
    }
