# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Controlled CMB comparisons, not a derived UM Boltzmann solver.

CAMB computes independent reference and candidate *unlensed* TT spectra with
identical late-time cosmology. Only explicitly supplied primordial inputs
change. A_s is an empirical calibration, not a prediction of this module.
The reference is a theoretical Lambda-CDM control, NOT Planck bandpowers.

Reported spectra are D_ell = ell(ell+1)C_ell/(2*pi), in microkelvin squared.
Two CAMB accuracy settings and lmax margins give a numerical sensitivity
estimate, not a certified error bound or an observational uncertainty.
No Z_phi, warp-floor, or breathing-mode correction is applied: their
normalization and dimensionally consistent transfer derivations are absent.
The optional toy fallback is explicitly dimensionless and cannot earn closure.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib.util
import json
import math

import numpy as np

PILLAR_NUMBER = 814
PILLAR_GATE = "ZPH_CAMB_BRIDGE_UM_TRANSFER_UNSUPPORTED"
LEAN4_THEOREM_COUNT = 15  # Historical inventory, not solver validation.
LEAN4_TOTAL_AFTER = 1351
N_W, K_CS = 5, 74
PHI0 = math.pi / 4
PHI0_EFF = N_W * 2 * math.pi
N_S = 1 - 36 / PHI0_EFF**2
R_BRAIDED = (96 / PHI0_EFF**2) * (12 / 37)
A_S_PLANCK = 2.1e-9
A_S_UM = None  # No independently derived primordial normalization.
Z_PHI = None
ELL_LOW, ELL_HIGH = 200, 2000
PLANCK_2018_ELL = tuple(range(200, 2001, 50))  # Sampling grid, NOT measured bins.
CAMB_AVAILABLE = importlib.util.find_spec("camb") is not None


@dataclass(frozen=True)
class Cosmology:
    """Shared, externally calibrated background; densities are Omega_i h^2."""

    H0: float = 67.4  # km/s/Mpc
    ombh2: float = 0.0224
    omch2: float = 0.120
    tau: float = 0.054
    mnu: float = 0.06  # eV, one massive neutrino
    omk: float = 0.0
    TCMB: float = 2.7255  # K
    nnu: float = 3.044
    YHe: float = 0.2454

    def __post_init__(self):
        if not all(math.isfinite(v) for v in asdict(self).values()):
            raise ValueError("Cosmology must be finite")
        if (self.H0 <= 0 or self.ombh2 <= 0 or self.omch2 < 0
                or self.tau < 0 or self.mnu < 0 or self.TCMB <= 0
                or self.nnu <= 0 or not 0 < self.YHe < 1):
            raise ValueError("Invalid cosmology")


@dataclass(frozen=True)
class PrimordialSpectrum:
    """Input calibration at k_pivot (Mpc^-1), never an inferred UM amplitude."""

    As: float = A_S_PLANCK
    ns: float = 0.9649
    r: float = 0.0
    pivot_scalar: float = 0.05
    pivot_tensor: float = 0.05
    nt: float = 0.0  # Explicit tensor tilt, no hidden consistency relation.

    def __post_init__(self):
        if not all(math.isfinite(v) for v in asdict(self).values()):
            raise ValueError("Primordial inputs must be finite")
        if self.As <= 0 or self.r < 0 or self.pivot_scalar <= 0 or self.pivot_tensor <= 0:
            raise ValueError("Invalid primordial normalization, pivot or tensor ratio")


@dataclass
class SpectrumComparison:
    ell: np.ndarray
    reference_dl: np.ndarray
    candidate_dl: np.ndarray
    residual_dl: np.ndarray
    relative_residual: np.ndarray
    reference_numerical_error: np.ndarray | None
    candidate_numerical_error: np.ndarray | None
    residual_numerical_error: np.ndarray | None
    observed_residual_dl: np.ndarray | None
    covariance: np.ndarray | None
    chi_square: float | None
    metadata: dict
    gate: str = PILLAR_GATE
    closure_earned: bool = False

    @property
    def camb_used(self):
        return self.metadata["backend"] == "camb"

    def to_dict(self):
        return {
            key: value.tolist() if isinstance(value, np.ndarray) else value
            for key, value in asdict(self).items()
        }


def _multipoles(ell_values):
    ell = np.asarray(ell_values)
    if (ell.ndim != 1 or not ell.size or not np.issubdtype(ell.dtype, np.number)
            or not np.all(np.isfinite(ell)) or np.any(ell < 2)
            or np.any(ell != np.floor(ell)) or np.any(np.diff(ell) <= 0)):
        raise ValueError("Multipoles must be nonempty, increasing integers >= 2")
    return ell.astype(int)


def _run_camb_cl_tt(ell, cosmology, primordial, accuracy, margin):
    """One independent CAMB run; no peak normalization or post-hoc rescaling."""
    import camb

    pars = camb.CAMBparams()
    pars.set_cosmology(**asdict(cosmology), num_massive_neutrinos=1)
    pars.InitPower.set_params(**asdict(primordial))
    pars.WantTensors = primordial.r > 0
    pars.DoLensing = False
    pars.NonLinear = camb.model.NonLinear_none
    pars.set_accuracy(AccuracyBoost=accuracy, lAccuracyBoost=accuracy,
                      lSampleBoost=accuracy)
    pars.set_for_lmax(max(600, int(ell[-1]) + margin), lens_potential_accuracy=0)
    results = camb.get_results(pars)
    powers = results.get_cmb_power_spectra(CMB_unit="muK", raw_cl=False)
    return powers["unlensed_total"][ell, 0].copy()


def _toy_spectrum(ell, primordial):
    """Positive arbitrary-unit envelope for software tests; NOT sky data."""
    if primordial.r != 0:
        raise NotImplementedError("Toy fallback has no tensor transfer function")
    return (primordial.As / A_S_PLANCK * (ell / 700.0)**(primordial.ns - 1)
            * (1 + 0.5 * np.cos(2 * np.pi * (ell - 220) / 300))**2
            * np.exp(-(ell / 1800.0)**2))


def compare_cmb_spectra(
    ell_values=PLANCK_2018_ELL,
    *,
    reference: PrimordialSpectrum = PrimordialSpectrum(),
    candidate: PrimordialSpectrum = PrimordialSpectrum(ns=N_S),
    cosmology: Cosmology = Cosmology(),
    backend: str = "auto",
    observed_dl=None,
    covariance=None,
    observation_source: str | None = None,
    accuracy_settings: tuple[float, float] = (1.0, 2.0),
    lmax_margins: tuple[int, int] = (150, 300),
) -> SpectrumComparison:
    """Compare primordial choices with fixed, unmodified GR transfer physics.

    ``backend='camb'`` requires CAMB and never silently falls back. ``auto``
    falls back only when CAMB is absent, not when a solver run fails.
    Optional observations and covariance must already be in this ell ordering,
    in D_ell [microK^2] and its covariance [microK^4]. No binning, window
    functions, nuisance fitting or likelihood calibration is implied.
    """
    ell = _multipoles(ell_values)
    if backend not in {"auto", "camb", "toy"}:
        raise ValueError("backend must be auto, camb or toy")
    if backend == "camb" and not CAMB_AVAILABLE:
        raise ImportError("CAMB is required for backend='camb'")
    selected = "camb" if backend == "camb" or (backend == "auto" and CAMB_AVAILABLE) else "toy"
    if (len(accuracy_settings) != 2 or not all(math.isfinite(x) for x in accuracy_settings)
            or not 0 < accuracy_settings[0] < accuracy_settings[1]):
        raise ValueError("Two positive increasing CAMB accuracy settings required")
    if (len(lmax_margins) != 2 or any(not isinstance(x, int) for x in lmax_margins)
            or not 0 <= lmax_margins[0] < lmax_margins[1]):
        raise ValueError("Two increasing nonnegative integer lmax margins required")
    observed = cov = cholesky = None
    if observed_dl is not None:
        if selected != "camb":
            raise ValueError("Arbitrary-unit toy spectra cannot be compared to observations")
        observed = np.asarray(observed_dl, dtype=float)
        if observed.shape != ell.shape or not np.all(np.isfinite(observed)):
            raise ValueError("Observed D_ell must be finite and match ell ordering")
        if not observation_source or not observation_source.strip():
            raise ValueError("An observation source is required")
    if covariance is not None:
        if observed is None:
            raise ValueError("Empirical covariance requires observed D_ell")
        cov = np.asarray(covariance, dtype=float)
        if (cov.shape != (ell.size, ell.size) or not np.all(np.isfinite(cov))
                or not np.allclose(cov, cov.T, rtol=1e-12, atol=0)):
            raise ValueError("Covariance must be finite, symmetric and match ell ordering")
        try:
            cholesky = np.linalg.cholesky(cov)
        except np.linalg.LinAlgError as exc:
            raise ValueError("Covariance must be positive definite") from exc
    ref_error = cand_error = residual_error = None
    if selected == "camb":
        import camb
        spectra = []
        for primordial in (reference, candidate):
            coarse, fine = [
                _run_camb_cl_tt(ell, cosmology, primordial, accuracy, margin)
                for accuracy, margin in zip(accuracy_settings, lmax_margins)
            ]
            spectra.append((fine, np.abs(fine - coarse)))
        (ref, ref_error), (cand, cand_error) = spectra
        residual_error = ref_error + cand_error
        version = camb.__version__
    else:
        ref, cand = (_toy_spectrum(ell, p) for p in (reference, candidate))
        version = None
    if (ref.shape != ell.shape or cand.shape != ell.shape
            or not np.all(np.isfinite(ref)) or not np.all(np.isfinite(cand))
            or np.any(ref <= 0) or np.any(cand < 0)):
        raise RuntimeError("Solver produced invalid TT spectra")
    residual = cand - ref
    observed_residual = None if observed is None else cand - observed
    chi_square = None
    if cholesky is not None:
        whitened = np.linalg.solve(cholesky, observed_residual)
        chi_square = float(whitened @ whitened)
    metadata = {
        "backend": selected,
        "backend_requested": backend,
        "fallback_reason": "CAMB unavailable" if backend == "auto" and selected == "toy" else None,
        "camb_version": version,
        "numpy_version": np.__version__,
        "spectrum": "unlensed_total_TT",
        "convention": "D_ell = ell(ell+1) C_ell / (2 pi)",
        "units": "microK^2" if selected == "camb" else "arbitrary",
        "reference_kind": "theoretical control, not empirical Planck bandpowers",
        "cosmology": asdict(cosmology),
        "reference_primordial": asdict(reference),
        "candidate_primordial": asdict(candidate),
        "primordial_normalization": "externally supplied calibration, not a UM prediction",
        "transfer_physics": "identical GR transfer; no UM correction",
        "corrections_applied": [],
        "corrections_disabled": {
            "Z_phi": "no normalized action-to-transfer derivation",
            "warp_suppression_4_to_7": "not a derived primordial amplitude interval",
            "breathing_mode": "Planck and Mpc units were mixed",
            "six_d_factor_1.084": "assigned coefficient, not derived",
        },
        "accuracy_settings": list(accuracy_settings) if selected == "camb" else None,
        "lmax_margins": list(lmax_margins) if selected == "camb" else None,
        "numerical_error_kind": (
            "absolute fine-minus-coarse sensitivity; residual uses sum of magnitudes, not a bound"
            if selected == "camb" else "not estimated; toy model has no physical error budget"
        ),
        "model_error": "UM transfer and amplitude derivations absent; not quantified",
        "observation_source": observation_source,
        "covariance_status": "supplied" if cov is not None else "missing; no empirical chi-square",
        "covariance_units": "microK^4" if cov is not None else None,
        "chi_square_kind": "raw supplied-covariance quadratic form, not fitted/reduced"
            if chi_square is not None else None,
    }
    return SpectrumComparison(
        ell, ref, cand, residual, residual / ref, ref_error, cand_error,
        residual_error, observed_residual, cov, chi_square, metadata,
    )


def run_zph_camb_bridge(ell_values=PLANCK_2018_ELL, use_camb=True, **kwargs):
    """Compatibility entry point; inspect metadata to distinguish CAMB and toy."""
    return compare_cmb_spectra(ell_values, backend="auto" if use_camb else "toy", **kwargs)


def evaluate_closure_gate(*args, **kwargs):
    """A small comparison residual cannot establish a missing UM derivation."""
    return PILLAR_GATE


def _unsupported_correction(*args, **kwargs):
    raise NotImplementedError("UM correction lacks a normalized, unit-consistent derivation")


compute_z_phi = _unsupported_correction
breathing_mode_damping = _unsupported_correction
compute_damping_filter = _unsupported_correction
um_transfer_correction = _unsupported_correction
toy_cl_tt_um = _unsupported_correction
planck_reference_cl = _unsupported_correction


if __name__ == "__main__":
    # Reproducible calculation with all arrays/provenance, never an implicit toy.
    print(json.dumps(compare_cmb_spectra(backend="camb").to_dict(), allow_nan=False))
