# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Unitary operator lab: non-smooth optimisation that stays on U(n).

ADJACENT TRACK.  This is the measured version of the claim that "a unitary
baseline survives non-smooth geometry".  We fit a unitary U to data pairs
(A, B) under the non-smooth robust loss ``sum |(UA - B)_ij|`` using Clarke
subgradients projected to the tangent space of U(n) and the Cayley
retraction, which maps skew-Hermitian steps to exactly unitary updates.

What the lab measures, and what it does not claim:
- The unitarity residual ``||U^H U - I||`` stays at floating-point level for
  every iterate, however sharp the loss surface is.  That is a property of the
  retraction, not of the data.
- With sparse gross outliers in B, the L1 fit is compared with the smooth
  Frobenius (orthogonal Procrustes, SVD closed-form) fit on recovery error
  against the planted operator.
- Unitarity bounds magnitudes; it does not make outputs correct.  A badly fit
  unitary is still unitary.
"""

from __future__ import annotations

from typing import Any

import numpy as np

STATUS_LABEL = "ADJACENT_TRACK"
MAX_DIMENSION = 16
MAX_ITERATIONS = 2000


def random_unitary(n: int, rng: np.random.Generator) -> np.ndarray:
    z = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / np.sqrt(2.0)
    q, r = np.linalg.qr(z)
    d = np.diag(r)
    return q * (d / np.abs(d))


def unitarity_residual(u: np.ndarray) -> float:
    return float(np.linalg.norm(u.conj().T @ u - np.eye(u.shape[0]), ord="fro"))


def l1_loss(u: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(u @ a - b).sum())


def l1_clarke_subgradient(u: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Euclidean subgradient of the L1 loss; at zero residual entries 0 lies in the unit-disk subdifferential."""
    r = u @ a - b
    mag = np.abs(r)
    s = np.zeros_like(r)
    nz = mag > 0.0
    s[nz] = r[nz] / mag[nz]
    return s @ a.conj().T


def cayley_step(u: np.ndarray, g: np.ndarray, step: float) -> np.ndarray:
    """Cayley retraction along the skew-Hermitian direction W = G U^H - U G^H."""
    n = u.shape[0]
    w = g @ u.conj().T - u @ g.conj().T
    eye = np.eye(n)
    return np.linalg.solve(eye + 0.5 * step * w, (eye - 0.5 * step * w) @ u)


def procrustes_fit(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Smooth baseline: argmin_U ||UA - B||_F over U(n) via SVD of B A^H."""
    left, _, right_h = np.linalg.svd(b @ a.conj().T)
    return left @ right_h


def l1_unitary_fit(
    a: np.ndarray,
    b: np.ndarray,
    *,
    initial: np.ndarray | None = None,
    iterations: int = 400,
    step0: float = 0.05,
) -> dict[str, Any]:
    """Riemannian subgradient descent with diminishing steps; returns the best iterate."""
    n = a.shape[0]
    u = np.eye(n, dtype=complex) if initial is None else np.array(initial, dtype=complex)
    scale = max(float(np.abs(a).sum()), 1e-12) / n
    best_u, best_loss = u, l1_loss(u, a, b)
    max_residual = unitarity_residual(u)
    for k in range(int(iterations)):
        g = l1_clarke_subgradient(u, a, b) / scale
        u = cayley_step(u, g, step0 / np.sqrt(k + 1.0))
        max_residual = max(max_residual, unitarity_residual(u))
        loss = l1_loss(u, a, b)
        if loss < best_loss:
            best_u, best_loss = u, loss
    return {"u": best_u, "loss": best_loss, "max_unitarity_residual": max_residual, "iterations": int(iterations)}


def run_unitary_lab(
    *,
    n: int = 4,
    samples: int = 24,
    outlier_fraction: float = 0.1,
    outlier_scale: float = 10.0,
    noise: float = 0.01,
    iterations: int = 1500,
    seed: int = 74,
) -> dict[str, Any]:
    n = int(n)
    samples = int(samples)
    iterations = int(iterations)
    if not 2 <= n <= MAX_DIMENSION:
        return {"ok": False, "error": f"n must be in [2, {MAX_DIMENSION}]"}
    if not n <= samples <= 512:
        return {"ok": False, "error": "samples must be in [n, 512]"}
    if not 1 <= iterations <= MAX_ITERATIONS:
        return {"ok": False, "error": f"iterations must be in [1, {MAX_ITERATIONS}]"}
    outlier_fraction = min(max(float(outlier_fraction), 0.0), 0.5)
    rng = np.random.default_rng(int(seed))
    planted = random_unitary(n, rng)
    a = (rng.standard_normal((n, samples)) + 1j * rng.standard_normal((n, samples))) / np.sqrt(2.0)
    b = planted @ a + noise * (rng.standard_normal((n, samples)) + 1j * rng.standard_normal((n, samples)))
    mask = rng.random((n, samples)) < outlier_fraction
    b = b + mask * outlier_scale * (rng.standard_normal((n, samples)) + 1j * rng.standard_normal((n, samples)))

    smooth = procrustes_fit(a, b)
    robust = l1_unitary_fit(a, b, initial=smooth, iterations=iterations)

    def recovery(u: np.ndarray) -> float:
        return float(np.linalg.norm(u - planted, ord="fro") / np.sqrt(n))

    return {
        "ok": True,
        "status": STATUS_LABEL,
        "config": {
            "n": n, "samples": samples, "outlier_fraction": outlier_fraction,
            "outlier_scale": float(outlier_scale), "noise": float(noise),
            "iterations": iterations, "seed": int(seed),
        },
        "outlier_entries": int(mask.sum()),
        "frobenius_procrustes": {
            "recovery_error": round(recovery(smooth), 6),
            "l1_loss": round(l1_loss(smooth, a, b), 6),
            "unitarity_residual": unitarity_residual(smooth),
        },
        "l1_riemannian_subgradient": {
            "recovery_error": round(recovery(robust["u"]), 6),
            "l1_loss": round(robust["loss"], 6),
            "unitarity_residual": unitarity_residual(robust["u"]),
            "max_unitarity_residual_over_iterates": robust["max_unitarity_residual"],
        },
        "eigenvalue_moduli_max_deviation": float(np.max(np.abs(np.abs(np.linalg.eigvals(robust["u"])) - 1.0))),
        "interpretation": (
            "Every iterate is unitary to floating-point precision (Cayley retraction). "
            "Recovery error compares each fit with the planted operator; unitarity alone does not guarantee a good fit."
        ),
    }


RECOVERY_TOLERANCE = 0.05
MAX_SWEEP_SEEDS = 40


def run_unitary_lab_sweep(*, seeds: int = 20, outlier_fractions: tuple[float, ...] = (0.0, 0.1, 0.2), **kwargs: Any) -> dict[str, Any]:
    """Recovery rates over seeds: how often each fit lands within tolerance of the planted unitary."""
    seeds = max(1, min(int(seeds), MAX_SWEEP_SEEDS))
    rows = []
    worst_residual = 0.0
    for fraction in outlier_fractions:
        smooth_hits = robust_hits = 0
        for seed in range(seeds):
            report = run_unitary_lab(seed=seed, outlier_fraction=fraction, **kwargs)
            if not report.get("ok"):
                return report
            smooth_hits += report["frobenius_procrustes"]["recovery_error"] < RECOVERY_TOLERANCE
            robust_hits += report["l1_riemannian_subgradient"]["recovery_error"] < RECOVERY_TOLERANCE
            worst_residual = max(worst_residual, report["l1_riemannian_subgradient"]["max_unitarity_residual_over_iterates"])
        rows.append({
            "outlier_fraction": float(fraction),
            "frobenius_recovered": smooth_hits,
            "l1_recovered": robust_hits,
            "seeds": seeds,
        })
    return {
        "ok": True,
        "status": STATUS_LABEL,
        "recovery_tolerance": RECOVERY_TOLERANCE,
        "rows": rows,
        "worst_unitarity_residual": worst_residual,
        "note": "Subgradient descent is a local method; failures are reported, not hidden.",
    }


__all__ = [
    "cayley_step",
    "l1_clarke_subgradient",
    "l1_loss",
    "l1_unitary_fit",
    "procrustes_fit",
    "random_unitary",
    "run_unitary_lab",
    "run_unitary_lab_sweep",
    "unitarity_residual",
]
