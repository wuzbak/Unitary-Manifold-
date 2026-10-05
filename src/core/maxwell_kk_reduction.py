# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 773 — Maxwell equations from 5D KK reduction.

We record the standard Kaluza-Klein metric split

    G_{μν} = g_{μν} + φ² A_μ A_ν,
    G_{μ5} = φ² A_μ,
    G_{55} = φ²,

On a circle this split admits a graviphoton with Maxwell-form dynamics.
On the standard S¹/Z₂ metric orbifold, however, G_{μ5} and A_μ are both
odd because φ² is even. Their constant vector zero mode is projected out.
An independent bulk U(1) field can instead be assigned even vector parity;
its constant Neumann mode is a different, explicitly conditional model.
For that independent field the covering-space volume reduction gives

    1/g₄,tree² = (2πR)/g₅²,

using the covering-space interval [-πR, πR]. The retained numerical coupling
illustration additionally assumes the overlap prescription

    I_CS = (1 - exp(-3πkR)) / (3πkR),

so that g₄,eff² = g₄,tree² sqrt(I_CS). This prescription is not derived here
from a normalized action and does not identify the observed photon or α_em.

The separate ``MaxwellTestFieldState`` API integrates physical-time source-free
Maxwell fields on a prescribed Einstein-frame Minkowski background with a
positive constant radion and a retained circle vector zero mode. It is a
test-field initial-value solver, not coupled Einstein/radion evolution, and
does not change the existing reduction report or action/evolution contract.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict

import numpy as np

PILLAR: int = 773
PILLAR_STATUS: str = "CIRCLE_MAXWELL_CONDITIONAL_ORBIFOLD_PHOTON_UNSUPPORTED"
N_W: int = 5
K_CS: int = 74
PI_K_R: float = 37.0
M_PL_GEV: float = 1.22e19
M_KK_GEV: float = M_PL_GEV * math.exp(-PI_K_R)

__all__ = [
    "PILLAR",
    "PILLAR_STATUS",
    "N_W",
    "K_CS",
    "PI_K_R",
    "M_PL_GEV",
    "M_KK_GEV",
    "metric_kk_decomposition",
    "photon_zero_mode_bc",
    "photon_z2_parity",
    "kk_reduction_gauge_coupling",
    "maxwell_equations_4d",
    "maxwell_kk_reduction_report",
    "MaxwellTestFieldState",
    "maxwell_test_field_surface",
    "maxwell_test_field_rhs",
    "maxwell_test_field_cfl_timestep",
    "step_maxwell_test_field",
    "maxwell_test_field_diagnostics",
]


def _validate_positive(name: str, value: float) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


def _cs_overlap(pi_kr: float) -> float:
    return (1.0 - math.exp(-3.0 * pi_kr)) / (3.0 * pi_kr)


def metric_kk_decomposition() -> Dict:
    """Return the local KK split, without assuming the vector survives a quotient."""
    return {
        "status": "DERIVED",
        "value": {
            "G_munu": "g_munu + phi^2 A_mu A_nu",
            "G_mu5": "phi^2 A_mu",
            "G_55": "phi^2",
        },
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "fields": {
            "g_munu": "4D graviton",
            "A_mu": "KK U(1) graviphoton on a circle; odd vector on the metric orbifold",
            "phi": "radion scalar",
        },
        "inverse_metric_note": "G^mu5 = -A^mu, G^55 = phi^-2 + A^2",
    }


def photon_zero_mode_bc(
    pi_kr: float = PI_K_R, *, field_origin: str = "metric",
) -> Dict:
    """Distinguish the projected metric vector from an independent bulk U(1).

    Only for an independent even bulk Maxwell field is the zero-mode equation

        f₀'' - 2k f₀' = 0,

    with general solution f₀(y) = c₁ + c₂ exp(2ky).  Neumann BC at y=0, πR force
    c₂ = 0, leaving a constant profile and exact zero mass. This cannot be
    applied to the odd metric vector or used to identify the observed photon.
    """
    _validate_positive("pi_kr", pi_kr)
    if field_origin not in {"metric", "independent_bulk_u1"}:
        raise ValueError("field_origin must be metric or independent_bulk_u1")
    if field_origin == "metric":
        return {
            "status": "PROJECTED_OUT",
            "value": None,
            "epistemic_status": "STANDARD_METRIC_ORBIFOLD",
            "pillar": PILLAR,
            "pi_kr": pi_kr,
            "field_origin": field_origin,
            "boundary_conditions": ["f0(0)=0", "f0(pi R)=0"],
            "zero_mode_profile": "no nonzero constant vector mode",
            "zero_mode_survives": False,
            "photon_mass_zero_gev": None,
            "observed_photon_identified": False,
            "reason": "A_mu = G_mu5 / phi^2 is odd; a constant odd profile must vanish",
        }
    return {
        "status": "CONDITIONAL",
        "value": 0.0,
        "epistemic_status": "INDEPENDENT_BULK_U1_ASSUMED",
        "pillar": PILLAR,
        "pi_kr": pi_kr,
        "field_origin": field_origin,
        "bulk_equation": "f0'' - 2 k f0' = 0",
        "general_solution": "f0(y) = c1 + c2 exp(2 k y)",
        "boundary_conditions": ["f0'(0)=0", "f0'(pi R)=0"],
        "c2_forced": 0.0,
        "zero_mode_profile": "constant",
        "photon_mass_zero_gev": 0.0,
        "zero_mode_survives": True,
        "observed_photon_identified": False,
    }


def photon_z2_parity() -> Dict:
    """Return standard metric-orbifold parity, not an independent gauge assignment.

    Under y -> -y the one-form dy changes sign.  Therefore the metric component
    G_{μ5} must be odd so that G_{μ5} dx^μ dy remains invariant, while the 4D
    coefficient A_μ = G_{μ5}/φ² is also odd. Its constant mode cannot survive.
    """
    return {
        "status": "DERIVED",
        "value": -1,
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "a_mu_parity": -1,
        "g_mu5_parity": -1,
        "g_55_parity": +1,
        "survives_orbifold": False,
        "interpretation": "A_mu is Z2-odd, so the constant metric-vector mode is projected out.",
    }


def kk_reduction_gauge_coupling(
    g5_sq: float | None = None,
    pi_kr: float = PI_K_R,
    k_cs: int = K_CS,
    m_pl_gev: float = M_PL_GEV,
) -> Dict:
    """Evaluate a conditional independent-bulk-U(1) coupling illustration.

    Using the covering-space interval length 2πR = 2 (πkR) / k and the CS
    assigned 5D coupling g₅² = K_CS / M_Pl, the tree-level reduction gives

        g₄,tree² = g₅² / (2πR) = g₅² k / (2πkR).

    With k ≈ M_Pl and πkR = 37 this yields g₄,tree² ≈ 1.  We then apply the
    warped overlap renormalization sqrt(I_CS), so the effective coupling is

        g₄,eff² = g₄,tree² sqrt(I_CS),

    and the historically named α_em = g₄,eff² / (4π). Neither the CS assignment
    nor its overlap normalization is derived here; this is not an orbifold
    metric-photon prediction.
    """
    _validate_positive("pi_kr", pi_kr)
    _validate_positive("m_pl_gev", m_pl_gev)
    if g5_sq is None:
        g5_sq = k_cs / m_pl_gev
    _validate_positive("g5_sq", g5_sq)

    k_gev = m_pl_gev
    radius_gev_inv = pi_kr / (math.pi * k_gev)
    interval_length_gev_inv = 2.0 * math.pi * radius_gev_inv
    g4_tree_sq = g5_sq / interval_length_gev_inv
    overlap = _cs_overlap(pi_kr)
    warp_factor = math.sqrt(overlap)
    g4_effective_sq = g4_tree_sq * warp_factor
    alpha_em = g4_effective_sq / (4.0 * math.pi)
    inverse_alpha = math.inf if alpha_em == 0 else 1.0 / alpha_em

    return {
        "status": "CONSTRAINED",
        "value": g4_effective_sq,
        "epistemic_status": "CONSTRAINED",
        "pillar": PILLAR,
        "model_scope": "conditional independent bulk U(1), not the odd metric vector",
        "observed_photon_identified": False,
        "coupling_derivation_complete": False,
        "g5_sq": g5_sq,
        "radius_gev_inv": radius_gev_inv,
        "interval_length_gev_inv": interval_length_gev_inv,
        "g4_tree_sq": g4_tree_sq,
        "warp_overlap": overlap,
        "warp_factor": warp_factor,
        "g4_effective_sq": g4_effective_sq,
        "alpha_em_geometric": alpha_em,
        "inverse_alpha_em": inverse_alpha,
        "formula": "g4_eff^2 = (g5^2 / 2piR) * sqrt((1-exp(-3 pi k R))/(3 pi k R))",
    }


def maxwell_equations_4d() -> Dict:
    """Maxwell-form effective action conditional on a retained U(1) and fixed radion."""
    return {
        "status": "CONDITIONAL",
        "value": "partial_nu F^{mu nu} = j^mu",
        "epistemic_status": "CIRCLE_OR_INDEPENDENT_BULK_U1_WITH_FIXED_RADION",
        "pillar": PILLAR,
        "reduced_action": "S_4 = -(1/4 g4^2) int d^4x sqrt(-g) F_{mu nu} F^{mu nu}",
        "field_strength": "F_{mu nu} = partial_mu A_nu - partial_nu A_mu",
        "equation_of_motion": "partial_nu F^{mu nu} = j^mu",
        "bianchi_identity": "partial_[lambda F_{mu nu]} = 0",
        "mass_term": 0.0,
        "metric_orbifold_zero_mode": False,
    }


def maxwell_kk_reduction_report() -> Dict:
    """Return the complete Pillar 773 summary."""
    decomposition = metric_kk_decomposition()
    bc = photon_zero_mode_bc()
    parity = photon_z2_parity()
    coupling = kk_reduction_gauge_coupling()
    equations = maxwell_equations_4d()
    return {
        "status": PILLAR_STATUS,
        "value": {
            "photon_mass_zero_gev": bc["photon_mass_zero_gev"],
            "alpha_em_geometric": None,
        },
        "epistemic_status": "ORBIFOLD_PHOTON_UNSUPPORTED",
        "observed_photon_identified": False,
        "closure_earned": False,
        "pillar": PILLAR,
        "n_w": N_W,
        "k_cs": K_CS,
        "pi_kr": PI_K_R,
        "decomposition": decomposition,
        "boundary_value_problem": bc,
        "parity": parity,
        "gauge_coupling": coupling,
        "maxwell_equations": equations,
        "summary": (
            "The standard orbifold projects out the odd metric-vector zero mode. "
            "Circle Maxwell dynamics and a conditional independent bulk U(1) "
            "coupling illustration do not establish the observed photon or alpha_em."
        ),
    }


def maxwell_test_field_surface() -> Dict:
    """Declare the physical-time solver's perimeter, without promoting any contract."""
    return {
        "status": "PRESCRIBED_BACKGROUND_TEST_FIELD",
        "epistemic_scope": "conditional source-free Maxwell initial-value problem",
        "compactification": "circle, y-independent vector zero mode; not the metric orbifold",
        "background": "prescribed Einstein-frame Minkowski metric diag(-1,1,1,1)",
        "radion": "prescribed positive constant phi0; potential absent",
        "gauge_weight": "w = lam^2 phi0^3, finite and strictly positive",
        "action_density": "-w F_mu,nu F^mu,nu / 4 on the prescribed background",
        "domain": "periodic x in [0,N*dx); translation invariance in the other two spatial directions",
        "time": "physical Einstein-frame coordinate time; lapse 1, shift 0, c=1",
        "equations": [
            "partial_t E = curl B_mag",
            "partial_t B_mag = -curl E",
            "div E = 0 and div B_mag = 0 for admissible source-free initial data",
        ],
        "field_convention": "E_i = F_i0; F_ij = epsilon_ijk B_mag,k; B_mag is not the KK potential",
        "discretization": "periodic second-order centered spatial differences; separate RK4 in physical time",
        "timestep": "0 < dt <= dx (conservative hyperbolic CFL, not a diffusion timestep)",
        "constraint_policy": (
            "measure discrete centered Dx electric and magnetic divergences; "
            "not a continuum certificate; no cleaning or projection"
        ),
        "backreaction": "not evolved; metric and radion equations are not claimed to hold",
        "limitations": [
            "Nonzero Maxwell stress sources gravity even when F^2=0.",
            "Generic fields also source the radion through F^2; fixing it is a test-field assumption.",
            "Centered differences do not resolve Nyquist-grid modes; continuum accuracy and constraints require refinement.",
            "No curved background, matter sources, higher KK modes, observed-photon identification, or universe validation.",
        ],
        "self_consistent_backreaction": False,
        "observed_photon_identified": False,
        "action_evolution_contract_promoted": False,
        "closure_earned": False,
    }


@dataclass(frozen=True)
class MaxwellTestFieldState:
    """Electric and magnetic initial data on a prescribed periodic Minkowski background.

    Arrays have shape (N, 3), with components ordered (x, y, z). The separate
    electric data supplies the physical-time momentum missing from a spatial
    potential alone. Constraint-violating data is retained for diagnostics, not
    silently repaired. ``time`` is Einstein-frame coordinate/proper time for
    stationary observers, not the relaxation parameter in ``evolution.py``.

    Constant ``phi0`` and ``lam`` specify only the positive Maxwell action weight;
    they do not change the vacuum propagation speed. Neither field backreacts
    on the prescribed metric or radion in this approximation.
    """

    electric: np.ndarray
    magnetic: np.ndarray
    dx: float
    phi0: float = 1.0
    lam: float = 1.0
    time: float = 0.0

    def __post_init__(self) -> None:
        for name in ("dx", "phi0", "lam", "time"):
            raw = getattr(self, name)
            if np.iscomplexobj(raw):
                raise ValueError(f"{name} must be real and finite")
            value = float(raw)
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        _validate_positive("dx", self.dx)
        _validate_positive("phi0", self.phi0)
        _validate_positive("gauge weight lam^2 phi0^3", self.gauge_weight)
        for name in ("electric", "magnetic"):
            raw = getattr(self, name)
            if np.iscomplexobj(raw):
                raise ValueError(f"{name} must be real")
            value = np.array(raw, dtype=float, copy=True)
            if value.ndim != 2 or value.shape[1] != 3 or value.shape[0] < 3:
                raise ValueError(f"{name} must have shape (N, 3) with N >= 3")
            if not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must be finite")
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        if self.electric.shape != self.magnetic.shape:
            raise ValueError("electric and magnetic must have identical shapes")

    @property
    def gauge_weight(self) -> float:
        """Constant coefficient w of -F^2/4 in the prescribed-background action."""
        return (self.lam * self.lam) * (self.phi0 * self.phi0 * self.phi0)


def _maxwell_periodic_derivative(field: np.ndarray, dx: float) -> np.ndarray:
    return (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0)) / (2.0 * dx)


def _maxwell_test_field_rhs_arrays(
    electric: np.ndarray, magnetic: np.ndarray, dx: float,
) -> tuple[np.ndarray, np.ndarray]:
    d_electric = _maxwell_periodic_derivative(electric, dx)
    d_magnetic = _maxwell_periodic_derivative(magnetic, dx)
    electric_rhs = np.zeros_like(electric)
    magnetic_rhs = np.zeros_like(magnetic)
    electric_rhs[:, 1] = -d_magnetic[:, 2]
    electric_rhs[:, 2] = d_magnetic[:, 1]
    magnetic_rhs[:, 1] = d_electric[:, 2]
    magnetic_rhs[:, 2] = -d_electric[:, 1]
    return electric_rhs, magnetic_rhs


def maxwell_test_field_rhs(
    state: MaxwellTestFieldState,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (partial_t E, partial_t B_mag), with derivatives only along x.

    With constant w, variation of -w F^2/4 gives partial_mu F^mu,nu=0;
    the Bianchi identity supplies Faraday's law. These are hyperbolic
    physical-time equations, not static residual relaxation.
    """
    return _maxwell_test_field_rhs_arrays(state.electric, state.magnetic, state.dx)


def maxwell_test_field_cfl_timestep(
    state: MaxwellTestFieldState, cfl: float = 0.5,
) -> float:
    """Return cfl*dx for 0<cfl<=1 and unit characteristic speed.

    Centered differences have imaginary eigenvalues with magnitude <=1/dx.
    RK4 is stable on the imaginary axis through |dt*omega|=sqrt(8), so
    dt<=dx is a conservative sufficient bound, not the sharp stability limit.
    """
    _validate_positive("cfl", cfl)
    if cfl > 1.0:
        raise ValueError("cfl must not exceed 1")
    return cfl * state.dx


def step_maxwell_test_field(
    state: MaxwellTestFieldState, dt: float,
) -> MaxwellTestFieldState:
    """Advance the source-free prescribed-background fields by a separate RK4 step."""
    _validate_positive("dt", dt)
    if dt > state.dx:
        raise ValueError("dt must not exceed dx for the conservative hyperbolic CFL")
    electric, magnetic = state.electric, state.magnetic
    rhs = _maxwell_test_field_rhs_arrays
    e1, b1 = rhs(electric, magnetic, state.dx)
    e2, b2 = rhs(electric + 0.5 * dt * e1, magnetic + 0.5 * dt * b1, state.dx)
    e3, b3 = rhs(electric + 0.5 * dt * e2, magnetic + 0.5 * dt * b2, state.dx)
    e4, b4 = rhs(electric + dt * e3, magnetic + dt * b3, state.dx)
    return MaxwellTestFieldState(
        electric=electric + (dt / 6.0) * (e1 + 2.0 * e2 + 2.0 * e3 + e4),
        magnetic=magnetic + (dt / 6.0) * (b1 + 2.0 * b2 + 2.0 * b3 + b4),
        dx=state.dx,
        phi0=state.phi0,
        lam=state.lam,
        time=state.time + dt,
    )


def maxwell_test_field_diagnostics(state: MaxwellTestFieldState) -> Dict:
    """Discrete Gauss constraints, energy and flux per unit transverse area.

    Energy is w*dx*sum(E^2+B_mag^2)/2; flux is w*(E cross B_mag).
    The centered spatial operator conserves this discrete energy exactly in
    continuous time (periodic summation by parts); RK4 has finite timestep error.
    Discrete Dx divergences are reported rather than cleaned, not certified as
    continuum constraints. In particular, even-N checkerboard/Nyquist modes
    lie in the centered derivative's nullspace. In this 1D reduction both
    longitudinal components are constant in time, so resolved violations persist.

    Raises ValueError if any diagnostic product or reduction is nonfinite;
    finite input fields alone do not ensure representable squares or totals.
    """
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        electric_squared = np.sum(state.electric * state.electric, axis=1)
        magnetic_squared = np.sum(state.magnetic * state.magnetic, axis=1)
        energy_density = 0.5 * state.gauge_weight * (electric_squared + magnetic_squared)
        electric_divergence = _maxwell_periodic_derivative(state.electric[:, 0], state.dx)
        magnetic_divergence = _maxwell_periodic_derivative(state.magnetic[:, 0], state.dx)
        diagnostics = {
            "electric_divergence": electric_divergence,
            "magnetic_divergence": magnetic_divergence,
            "electric_gauss_rms": float(np.sqrt(np.mean(electric_divergence**2))),
            "magnetic_gauss_rms": float(np.sqrt(np.mean(magnetic_divergence**2))),
            "energy_density": energy_density,
            "energy": float(state.dx * np.sum(energy_density)),
            "poynting_flux": state.gauge_weight * np.cross(state.electric, state.magnetic),
            "F2_lorentzian": 2.0 * (magnetic_squared - electric_squared),
        }
    if not all(np.all(np.isfinite(value)) for value in diagnostics.values()):
        raise ValueError("Maxwell diagnostics require finite representable products and reductions")
    return diagnostics
