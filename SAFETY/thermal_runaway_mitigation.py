# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
SAFETY/thermal_runaway_mitigation.py
=====================================
Thermal Runaway Mitigation for Pillar 15: φ-Enhanced Cold Fusion.

Background
----------
Pillar 15 (src/core/cold_fusion.py) describes how the 5D Kaluza–Klein
geometry of the Unitary Manifold provides a φ-enhanced Gamow tunneling
mechanism that can, in principle, increase the D+D fusion rate inside a
coherent Palladium lattice by many orders of magnitude relative to the
standard 4D prediction.

The mechanism requires three conditions:

  1.  A high D/Pd loading ratio (x ≳ 0.7) to sustain the φ enhancement.
  2.  The (5,7) braided winding state to remain resonant (k_cs = 74 stable).
  3.  The lattice temperature to remain below the 5D coupling stability limit.

Condition 3 defines the **Thermal Runaway Risk**:

  If the φ-enhanced reaction rate deposits heat faster than the lattice can
  dissipate it, the temperature T rises.  As T rises, the Gamow peak energy
  E_G ∝ T^{2/3} shifts upward, accessing more kinetic energy and further
  increasing the rate — a positive feedback loop.  In extreme cases this can
  destabilise the Pd crystal (palladium melts at 1828 K) and terminate the
  φ-coherence that makes the enhancement possible in the first place.

  Separately, the 5D coupling λ (the KK coupling of the gauge field B_μ to
  the scalar φ) has a stability limit T_5D above which the thermal fluctuations
  in the lattice phonon bath are energetically comparable to the compactification
  scale energy ~1/r_φ.  When this happens the φ-enhancement loses its geometric
  coherence and the (5,7) braid is disrupted.

**The Three-Layer Shutdown Protocol:**

  Layer 1 — Temperature limit:  T > T_max
    The lattice temperature exceeds the operator-configured maximum.  The
    most conservative shutdown: cut loading ratio to zero to quench the rate.

  Layer 2 — 5D coupling destabilisation:  T > T_5D
    Lattice thermal energy kT approaches the compactification energy ℏ/(r_φ).
    The φ-enhancement factor f_KK is no longer geometric — it is thermal.
    Shutdown the φ-enhancement (set phi_lattice → phi_vacuum) while allowing
    the lattice to cool passively.

  Layer 3 — Loading ratio runaway:  x > x_max or COP drift
    If the loading ratio drifts above x_max = 0.95, the lattice stress exceeds
    the safe operating range and the φ-coherence volume shrinks (deuterium
    occupation blocks KK propagation at very high filling).  Reduce loading
    ratio.

  Layer 4 — Neutron flux (radiological):  Φ_n > neutron_flux_limit
    If the estimated fast-neutron flux at the detector distance exceeds the
    regulatory uncontrolled-area threshold (~1 n/cm²/s), a radiological
    shutdown is triggered.  D+D → ³He + n (50% branch, 2.45 MeV neutrons)
    represents the primary biological hazard in a functional device.  This
    layer fires in simulation to warn that the modelled rate would require
    professional radiation monitoring and containment before any physical
    experiment is attempted.

This module implements these four layers as a configurable guard that wraps
the run_cold_fusion() pipeline from src/core/cold_fusion.py.

Physical constants and defaults
--------------------------------
T_5D is estimated from the condition kT_5D ≈ ℏ c / (2π r_φ) where r_φ = ⟨φ⟩
is the compactification radius in natural units.  With ⟨φ⟩_vacuum = 1 (UM
convention), r_φ is set by the fundamental scale; the numerical estimate
places T_5D at approximately 1200 K for bulk Pd geometry.  The operator can
override this.

Layer 4 neutron flux limit (neutron_flux_limit) defaults to 1.0 n/cm²/s,
which is the approximate regulatory threshold for fast neutrons in uncontrolled
areas (corresponding to ~0.1 mrem/h dose rate).  The estimated flux is:

    Φ_n ≈ 0.5 × R × V / (4π d²)   [neutrons / (cm² · s)]

where R is the rate (fusions/cm³/s), V is the active volume (cm³), d is the
detector distance (cm), and 0.5 is the D+D → ³He+n branching ratio.

Public API
----------
ThermalRunawayError
    Exception raised when a thermal runaway condition is detected.

ThermalRunawayReport
    Dataclass: T_K, loading_ratio, phi_lattice, cop, neutron_flux, layer, status, message.

ThermalRunawayGuard(T_max_K, T_5D_K, x_max, cop_min, cop_max,
                    neutron_flux_limit, detector_distance_cm, active_volume_cc)
    Configurable guard.  Call .check(T_K, loading_ratio, cop) or
    .run_safe(config) for a full pipeline run.

ThermalRunawayGuard.check(T_K, loading_ratio, phi_lattice, cop, reaction_rate)
    -> ThermalRunawayReport
    Inspect current state.  Raises ThermalRunawayError if any layer fires.

ThermalRunawayGuard.run_safe(config) -> ColdFusionResult or None
    Run the full cold fusion pipeline with thermal and radiological safety
    monitoring.  Returns None (and logs) if any layer fires before completion.
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# Allow imports from the repository root when run directly
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.core.cold_fusion import (
    ColdFusionConfig,
    run_cold_fusion,
    phi_lattice_enhancement,
    K_B_EV_PER_K,
    PHI_VACUUM,
    C_S_BRAID,
    N1_BRAID,
    N2_BRAID,
    K_CS_BRAID,
)


# ---------------------------------------------------------------------------
# Default safety parameters
# ---------------------------------------------------------------------------

#: Default maximum lattice temperature (K) — Pd melts at 1828 K; conservative limit
T_MAX_K_DEFAULT: float = 400.0

#: Default 5D coupling stability temperature (K)
#: Estimated from kT ≈ ℏ c / (2π r_φ) with r_φ = ⟨φ⟩_vacuum in UM units
T_5D_K_DEFAULT: float = 1200.0

#: Default maximum safe D/Pd loading ratio
X_MAX_DEFAULT: float = 0.95

#: Default minimum COP for anomalous heat significance
COP_MIN_DEFAULT: float = 1.0

#: Default maximum COP (above this the model is extrapolating dangerously)
COP_MAX_DEFAULT: float = 1e6

#: Default neutron flux limit (n/cm²/s) — regulatory uncontrolled-area threshold
NEUTRON_FLUX_LIMIT_DEFAULT: float = 1.0   # ~0.1 mrem/h for 2.45 MeV fast neutrons

#: Default detector distance (cm) for flux estimation
DETECTOR_DISTANCE_CM_DEFAULT: float = 100.0  # 1 metre

#: Default active volume for flux estimation (cm³)
ACTIVE_VOLUME_CC_DEFAULT: float = 1.0

#: D+D → ³He+n branching fraction (~50% at low energy)
DD_NEUTRON_BRANCH: float = 0.5

#: Warning fraction — issue WARNING when within this fraction of a limit
WARN_FRACTION_DEFAULT: float = 0.8


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ThermalRunawayError(RuntimeError):
    """Raised when a thermal runaway condition is detected in the Pd lattice.

    Attributes
    ----------
    layer : int
        The shutdown layer that fired (1, 2, or 3).
    T_K : float
        Lattice temperature at shutdown (K).
    loading_ratio : float
        D/Pd loading ratio at shutdown.
    message : str
        Human-readable description.
    """

    def __init__(
        self,
        layer: int,
        T_K: float,
        loading_ratio: float,
        message: str,
    ) -> None:
        self.layer = layer
        self.T_K = T_K
        self.loading_ratio = loading_ratio
        self.message = message
        super().__init__(message)


# ---------------------------------------------------------------------------
# Report dataclass
# ---------------------------------------------------------------------------

@dataclass
class ThermalRunawayReport:
    """Diagnostic summary of a single thermal safety check.

    Attributes
    ----------
    T_K : float
        Lattice temperature at the time of the check (K).
    loading_ratio : float
        D/Pd loading ratio.
    phi_lattice : float
        Current φ_lattice value.
    cop : float or None
        Coefficient of performance (None if not yet computed).
    layer : int or None
        Shutdown layer triggered (1, 2, or 3), or None if safe.
    status : str
        'OK', 'WARNING', or 'SHUTDOWN'.
    message : str
        Human-readable summary.
    """

    T_K: float
    loading_ratio: float
    phi_lattice: float
    cop: Optional[float]
    neutron_flux: Optional[float]
    layer: Optional[int]
    status: str
    message: str

    @property
    def is_safe(self) -> bool:
        return self.status != "SHUTDOWN"


# ---------------------------------------------------------------------------
# Guard class
# ---------------------------------------------------------------------------

class ThermalRunawayGuard:
    """Three-layer thermal runaway guard for φ-enhanced cold fusion simulations.

    Parameters
    ----------
    T_max_K : float
        Layer 1 shutdown: absolute temperature limit (K).  Default 400 K.
    T_5D_K : float
        Layer 2 shutdown: 5D coupling destabilisation temperature (K).
        Default 1200 K.
    x_max : float
        Layer 3 shutdown: maximum D/Pd loading ratio.  Default 0.95.
    cop_min : float
        Minimum expected COP for anomalous heat significance.  Default 1.0.
    cop_max : float
        Maximum COP before the model is considered to be extrapolating
        dangerously beyond its calibration range.  Default 1e6.
    neutron_flux_limit : float
        Layer 4 shutdown: maximum fast-neutron flux in n/cm²/s.
        Default 1.0 n/cm²/s (regulatory uncontrolled-area threshold).
    detector_distance_cm : float
        Distance from the active volume to the nearest unshielded person
        or detector (cm).  Used for flux estimation.  Default 100 cm.
    active_volume_cc : float
        Active volume of the Pd–D lattice (cm³).  Default 1.0 cm³.
    warn_fraction : float
        Fraction of each limit at which to issue WARNING.  Default 0.8.
    """

    def __init__(
        self,
        T_max_K: float = T_MAX_K_DEFAULT,
        T_5D_K: float = T_5D_K_DEFAULT,
        x_max: float = X_MAX_DEFAULT,
        cop_min: float = COP_MIN_DEFAULT,
        cop_max: float = COP_MAX_DEFAULT,
        neutron_flux_limit: float = NEUTRON_FLUX_LIMIT_DEFAULT,
        detector_distance_cm: float = DETECTOR_DISTANCE_CM_DEFAULT,
        active_volume_cc: float = ACTIVE_VOLUME_CC_DEFAULT,
        warn_fraction: float = WARN_FRACTION_DEFAULT,
    ) -> None:
        self.T_max_K = float(T_max_K)
        self.T_5D_K = float(T_5D_K)
        self.x_max = float(x_max)
        self.cop_min = float(cop_min)
        self.cop_max = float(cop_max)
        self.neutron_flux_limit = float(neutron_flux_limit)
        self.detector_distance_cm = float(detector_distance_cm)
        self.active_volume_cc = float(active_volume_cc)
        self._warn_fraction = float(warn_fraction)

    def check(
        self,
        T_K: float,
        loading_ratio: float,
        phi_lattice: Optional[float] = None,
        cop: Optional[float] = None,
        reaction_rate: Optional[float] = None,
    ) -> ThermalRunawayReport:
        """Inspect current operating conditions.

        Parameters
        ----------
        T_K : float
            Current lattice temperature (K).
        loading_ratio : float
            Current D/Pd loading ratio (0 < x ≤ 1).
        phi_lattice : float, optional
            Current φ_lattice value.  If None, computed from loading_ratio.
        cop : float, optional
            Current coefficient of performance.  If None, Layer 3 COP check
            is skipped.
        reaction_rate : float, optional
            Estimated reaction rate R in fusions/(cm³·s).  If provided, a
            Layer 4 neutron flux check is performed.

        Returns
        -------
        ThermalRunawayReport

        Raises
        ------
        ThermalRunawayError
        """
        if phi_lattice is None:
            phi_lattice = phi_lattice_enhancement(
                loading_ratio=max(loading_ratio, 1e-9)
            )

        # Estimate neutron flux if reaction_rate is provided
        neutron_flux: Optional[float] = None
        if reaction_rate is not None and reaction_rate > 0.0:
            d = self.detector_distance_cm
            V = self.active_volume_cc
            neutron_flux = (
                DD_NEUTRON_BRANCH * reaction_rate * V / (4.0 * np.pi * d**2)
            )

        # ── Layer 1: absolute temperature limit ────────────────────────
        if T_K > self.T_max_K:
            msg = (
                f"THERMAL RUNAWAY LAYER 1: T = {T_K:.1f} K exceeds T_max = "
                f"{self.T_max_K:.1f} K.  "
                f"Cut loading ratio to zero to quench the reaction.  "
                f"Pd lattice stability requires T < {self.T_max_K:.0f} K."
            )
            raise ThermalRunawayError(1, T_K, loading_ratio, msg)

        # ── Layer 2: 5D coupling destabilisation ────────────────────────
        if T_K > self.T_5D_K:
            msg = (
                f"THERMAL RUNAWAY LAYER 2: T = {T_K:.1f} K exceeds T_5D = "
                f"{self.T_5D_K:.1f} K.  "
                f"Lattice thermal energy kT = {K_B_EV_PER_K * T_K:.4f} eV approaches "
                f"the compactification scale.  "
                f"φ-enhancement is no longer geometric — set phi_lattice → phi_vacuum.  "
                f"Allow lattice to cool passively before resuming."
            )
            raise ThermalRunawayError(2, T_K, loading_ratio, msg)

        # ── Layer 3: loading ratio runaway ─────────────────────────────
        if loading_ratio > self.x_max:
            msg = (
                f"THERMAL RUNAWAY LAYER 3: loading_ratio x = {loading_ratio:.4f} "
                f"exceeds x_max = {self.x_max:.4f}.  "
                f"Lattice stress at near-saturation loading blocks KK propagation.  "
                f"Reduce D loading before continuing."
            )
            raise ThermalRunawayError(3, T_K, loading_ratio, msg)

        # ── Layer 3 (COP): model extrapolation warning ─────────────────
        if cop is not None and cop > self.cop_max:
            msg = (
                f"THERMAL RUNAWAY LAYER 3 (COP): COP = {cop:.2e} exceeds "
                f"cop_max = {self.cop_max:.2e}.  "
                f"The φ-enhancement model is extrapolating outside its calibration "
                f"range.  The physical rate is unconstrained; halt and re-evaluate."
            )
            raise ThermalRunawayError(3, T_K, loading_ratio, msg)

        # ── Layer 4: radiological — neutron flux ───────────────────────
        if neutron_flux is not None and neutron_flux > self.neutron_flux_limit:
            msg = (
                f"RADIOLOGICAL SHUTDOWN LAYER 4: estimated fast-neutron flux "
                f"Φ_n = {neutron_flux:.3e} n/cm²/s at {self.detector_distance_cm:.0f} cm "
                f"exceeds regulatory limit {self.neutron_flux_limit:.1f} n/cm²/s.  "
                f"D+D → ³He + n (2.45 MeV, 50% branch).  "
                f"Professional radiation monitoring, boron-doped shielding, and a "
                f"radioactive materials licence are required before any physical "
                f"experiment at this modelled rate.  "
                f"See SAFETY/RADIOLOGICAL_SAFETY.md for shielding requirements."
            )
            raise ThermalRunawayError(4, T_K, loading_ratio, msg)

        # ── Warnings ───────────────────────────────────────────────────
        warnings = []
        if T_K > self._warn_fraction * self.T_max_K:
            warnings.append(
                f"T = {T_K:.1f} K is within {100*(1-self._warn_fraction):.0f}% "
                f"of T_max = {self.T_max_K:.1f} K"
            )
        if loading_ratio > self._warn_fraction * self.x_max:
            warnings.append(
                f"loading_ratio = {loading_ratio:.3f} is within "
                f"{100*(1-self._warn_fraction):.0f}% of x_max = {self.x_max:.3f}"
            )
        if neutron_flux is not None and neutron_flux > self._warn_fraction * self.neutron_flux_limit:
            warnings.append(
                f"neutron flux = {neutron_flux:.3e} n/cm²/s approaching limit "
                f"{self.neutron_flux_limit:.1f} n/cm²/s (Layer 4)"
            )

        if warnings:
            msg = "WARNING: " + "; ".join(warnings) + ".  Monitor closely."
            status = "WARNING"
        else:
            msg = (
                f"OK: T = {T_K:.1f} K, x = {loading_ratio:.3f}, "
                f"phi_lattice = {phi_lattice:.4f}.  All four safety layers clear."
            )
            status = "OK"

        return ThermalRunawayReport(
            T_K=T_K,
            loading_ratio=loading_ratio,
            phi_lattice=phi_lattice,
            cop=cop,
            neutron_flux=neutron_flux,
            layer=None,
            status=status,
            message=msg,
        )

    # ------------------------------------------------------------------

    def run_safe(
        self, config: ColdFusionConfig
    ) -> Optional["ColdFusionResult"]:  # noqa: F821
        """Run the cold fusion pipeline with thermal and radiological safety monitoring.

        Performs a pre-flight check on the config, runs run_cold_fusion(),
        then performs a post-flight check on the result COP and neutron flux.

        Parameters
        ----------
        config : ColdFusionConfig
            Configuration for the cold fusion calculation.

        Returns
        -------
        ColdFusionResult or None
            The result if all safety checks pass; None if a thermal runaway
            or radiological condition was detected (error is printed to stderr).
        """
        # Pre-flight
        try:
            phi_lattice = phi_lattice_enhancement(
                loading_ratio=config.loading_ratio
            )
            self.check(
                T_K=config.T_K,
                loading_ratio=config.loading_ratio,
                phi_lattice=phi_lattice,
            )
        except ThermalRunawayError as exc:
            print(
                f"\n[ThermalRunawayGuard] Pre-flight SHUTDOWN (Layer {exc.layer}): "
                f"{exc.message}",
                file=sys.stderr,
            )
            return None

        # Run pipeline
        result = run_cold_fusion(config)

        # Post-flight check: COP + neutron flux
        try:
            self.check(
                T_K=config.T_K,
                loading_ratio=config.loading_ratio,
                phi_lattice=phi_lattice,
                cop=result.cop,
                reaction_rate=result.rate_per_cc_s,
            )
        except ThermalRunawayError as exc:
            print(
                f"\n[ThermalRunawayGuard] Post-flight SHUTDOWN (Layer {exc.layer}): "
                f"{exc.message}",
                file=sys.stderr,
            )
            return None

        return result

    # ------------------------------------------------------------------

    @staticmethod
    def geometric_shutdown_temperature(phi_vacuum: float = PHI_VACUUM) -> float:
        """Estimate the 5D coupling stability temperature T_5D (K).

        From the condition kT_5D ≈ ℏ c / (2π r_φ) ≈ ℏ c / (2π ⟨φ⟩).
        In UM natural units with ⟨φ⟩_vacuum = 1, and converting to Kelvin
        using the Boltzmann constant:

            T_5D ≈ (ℏ c) / (2π ⟨φ⟩ × k_B)

        Using ℏ c ≈ 197.3 MeV·fm and assuming ⟨φ⟩ scales the compactification
        radius to the nuclear scale (~1 fm) for maximal φ enhancement:

            T_5D ≈ 197.3 MeV / (2π × k_B [MeV/K])

        This returns an order-of-magnitude estimate; the exact value depends
        on the physical compactification radius which is not yet measured.

        Parameters
        ----------
        phi_vacuum : float
            Vacuum radion mean value (default 1.0).

        Returns
        -------
        float
            T_5D in Kelvin (order-of-magnitude estimate).
        """
        hbar_c_MeV_fm = 197.3269804  # MeV·fm
        k_B_MeV_per_K = 8.617333262e-11  # MeV/K
        # Assume compactification radius r_phi ~ phi_vacuum fm
        r_phi_fm = phi_vacuum
        T_5D = hbar_c_MeV_fm / (2.0 * np.pi * r_phi_fm * k_B_MeV_per_K)
        return float(T_5D)
