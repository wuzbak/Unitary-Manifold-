# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Independent five-dimensional Ricci oracle for a planar circle uplift.

Coordinates are ``(t, x, y, z, chi)`` and the Einstein-frame uplift is
``diag(-exp(2*sigma-psi), exp(2*sigma-psi), r**2*exp(-psi),
r**2*exp(-psi), exp(2*psi))``. No evolution equations enter this module.
"""

from dataclasses import dataclass

import numpy as np


def _real_array(value, name):
    if np.iscomplexobj(value):
        raise ValueError(f"{name} must be real")
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a real numeric array") from exc
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array


def _symmetric(array, axis1, axis2, name):
    if not np.allclose(array, array.swapaxes(axis1, axis2), rtol=1e-10, atol=1e-12):
        raise ValueError(f"{name} must be symmetric")


def _metric_array(metric):
    metric = _real_array(metric, "metric")
    if metric.ndim < 2 or metric.shape[-2:] != (5, 5):
        raise ValueError("metric must have shape (..., 5, 5)")
    _symmetric(metric, -1, -2, "metric")
    eigenvalues = np.linalg.eigvalsh(metric)
    if not np.all(
        (np.sum(eigenvalues < 0, axis=-1) == 1)
        & (np.sum(eigenvalues > 0, axis=-1) == 4)
    ):
        raise ValueError("metric must have nondegenerate Lorentz signature (-++++)")
    return metric


def ricci_from_metric_jet(metric, first, second):
    """Compute covariant Ricci directly from a five-dimensional metric jet.

    Shapes are ``(..., 5, 5)``, ``(..., 5, 5, 5)``, and
    ``(..., 5, 5, 5, 5)`` with identical optional batch dimensions.
    Derivative coordinates come first: ``first[..., c, a, b] = d_c G_ab``
    and ``second[..., c, d, a, b] = d_c d_d G_ab``.
    The convention is ``R_bc = d_a Gamma^a_bc - d_c Gamma^a_ba
    + Gamma^a_ad Gamma^d_bc - Gamma^a_cd Gamma^d_ba``.
    """
    metric = _metric_array(metric)
    first = _real_array(first, "first derivatives")
    second = _real_array(second, "second derivatives")
    batch = metric.shape[:-2]
    if first.shape != batch + (5, 5, 5):
        raise ValueError("first derivatives must have shape metric.shape[:-2] + (5, 5, 5)")
    if second.shape != batch + (5, 5, 5, 5):
        raise ValueError("second derivatives must have shape metric.shape[:-2] + (5, 5, 5, 5)")
    _symmetric(first, -1, -2, "first derivative metric indices")
    _symmetric(second, -1, -2, "second derivative metric indices")
    _symmetric(second, -4, -3, "second derivative coordinate indices")
    try:
        with np.errstate(over="raise", divide="raise", invalid="raise"):
            inverse = np.linalg.inv(metric)
            inverse_first = -np.einsum(
                "...ai,...eij,...jb->...eab", inverse, first, inverse, optimize=True
            )
            kernel = first + first.swapaxes(-3, -2) - np.moveaxis(first, -3, -1)
            kernel_first = (
                second + second.swapaxes(-3, -2) - np.moveaxis(second, -3, -1)
            )
            gamma = 0.5 * np.einsum("...ad,...bcd->...abc", inverse, kernel)
            gamma_first = 0.5 * (
                np.einsum("...ead,...bcd->...eabc", inverse_first, kernel)
                + np.einsum("...ad,...ebcd->...eabc", inverse, kernel_first)
            )
            ricci = (
                np.einsum("...aabc->...bc", gamma_first)
                - np.einsum("...caba->...bc", gamma_first)
                + np.einsum("...aad,...dbc->...bc", gamma, gamma)
                - np.einsum("...acd,...dba->...bc", gamma, gamma)
            )
    except (np.linalg.LinAlgError, FloatingPointError) as exc:
        raise ValueError("metric jet is numerically singular or overflows curvature") from exc
    if not np.all(np.isfinite(ricci)):
        raise ValueError("metric jet produced nonfinite Ricci components")
    return ricci


def ricci_frame_norm(metric, ricci):
    """Positive Frobenius norm of Ricci in the diagonal orthonormal frame.

    This is not the indefinite contraction ``R_ab R^ab``, nor the Ricci
    scalar: neither is a reliable vacuum residual.
    """
    metric = _metric_array(metric)
    ricci = _real_array(ricci, "Ricci tensor")
    if ricci.shape != metric.shape:
        raise ValueError("Ricci tensor must have the same shape as metric")
    diagonal = np.diagonal(metric, axis1=-2, axis2=-1)
    reconstructed = diagonal[..., :, None] * np.eye(5)
    if not np.array_equal(metric, reconstructed):
        raise ValueError("orthonormal frame norm requires a diagonal metric")
    if not np.all((diagonal[..., 0] < 0) & np.all(diagonal[..., 1:] > 0, axis=-1)):
        raise ValueError("orthonormal frame requires timelike t and spacelike x,y,z,chi")
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        scales = 1.0 / np.sqrt(np.abs(diagonal))
        frame = ricci * scales[..., :, None] * scales[..., None, :]
        # hypot reduction avoids overflow from squaring large finite components.
        norm = np.hypot.reduce(frame.reshape(frame.shape[:-2] + (25,)), axis=-1)
    if not np.all(np.isfinite(norm)):
        raise ValueError("orthonormal Ricci norm is nonfinite")
    return norm


def _uniform_coordinates(values, name):
    values = _real_array(values, name)
    if values.ndim != 1 or len(values) < 5:
        raise ValueError(f"{name} must be one-dimensional with at least 5 positions")
    spacing = np.diff(values)
    if spacing[0] <= 0 or not np.allclose(
        spacing, spacing[0], rtol=1e-10, atol=1e-12 * abs(spacing[0])
    ):
        raise ValueError(f"{name} positions must be increasing and uniformly spaced")
    return values, spacing[0]


def _periodic_first(values, spacing):
    return (
        np.roll(values, 2, axis=1) - 8 * np.roll(values, 1, axis=1)
        + 8 * np.roll(values, -1, axis=1) - np.roll(values, -2, axis=1)
    ) / (12 * spacing)


@dataclass(frozen=True)
class PlanarRicciResidual:
    """Slab diagnostics; tensor shape is ``(nt-4, nx, 5, 5)``.

    ``times`` contains the retained interior temporal positions. ``frame_norm``
    and ``scalar`` have shape ``(nt-4, nx)``. The scalar is diagnostic only.
    """

    times: np.ndarray
    ricci: np.ndarray
    frame_norm: np.ndarray
    scalar: np.ndarray


def evaluate_planar_ricci(t, x, r, sigma, psi):
    """Evaluate the direct 5D vacuum residual from stored spacetime slabs.

    Inputs ``r, sigma, psi`` have shape ``(len(t), len(x))``. Both coordinate
    grids are uniform and increasing with at least five points. ``x`` covers
    one periodic cell *without* a duplicated endpoint. Fourth-order centered
    first, second, and mixed derivatives act on the uplifted metric itself;
    two temporal boundary rows are discarded on each side. Jets are processed
    one time slice at a time to bound scratch memory independently of ``nt``.
    """
    t, dt = _uniform_coordinates(t, "t")
    x, dx = _uniform_coordinates(x, "x")
    fields = [_real_array(value, name) for value, name in
              ((r, "r"), (sigma, "sigma"), (psi, "psi"))]
    if any(field.shape != (len(t), len(x)) for field in fields):
        raise ValueError("r, sigma, psi must have shape (len(t), len(x))")
    r, sigma, psi = fields
    if np.any(r <= 0):
        raise ValueError("r must be strictly positive")
    try:
        with np.errstate(over="raise", under="raise", invalid="raise"):
            conformal = np.exp(2 * sigma - psi)
            transverse = r**2 * np.exp(-psi)
            circle = np.exp(2 * psi)
            diagonal = np.stack(
                (-conformal, conformal, transverse, transverse, circle), axis=-1
            )
    except FloatingPointError as exc:
        raise ValueError("uplift metric overflows or degenerates") from exc
    if not np.all(np.isfinite(diagonal)) or np.any(diagonal == 0):
        raise ValueError("uplift metric must be finite and nondegenerate")
    dx_metric = _periodic_first(diagonal, dx)
    ricci = np.empty((len(t) - 4, len(x), 5, 5))
    norms = np.empty(ricci.shape[:2])
    scalars = np.empty_like(norms)
    index = np.arange(5)
    for row, i in enumerate(range(2, len(t) - 2)):
        metric = diagonal[i, :, :, None] * np.eye(5)
        first = np.zeros((len(x), 5, 5, 5))
        second = np.zeros((len(x), 5, 5, 5, 5))
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            first[:, 0, index, index] = (
                diagonal[i - 2] - 8 * diagonal[i - 1]
                + 8 * diagonal[i + 1] - diagonal[i + 2]
            ) / (12 * dt)
            first[:, 1, index, index] = dx_metric[i]
            second[:, 0, 0, index, index] = (
                -diagonal[i + 2] + 16 * diagonal[i + 1] - 30 * diagonal[i]
                + 16 * diagonal[i - 1] - diagonal[i - 2]
            ) / (12 * dt**2)
            second[:, 1, 1, index, index] = (
                -np.roll(diagonal[i], -2, axis=0)
                + 16 * np.roll(diagonal[i], -1, axis=0) - 30 * diagonal[i]
                + 16 * np.roll(diagonal[i], 1, axis=0)
                - np.roll(diagonal[i], 2, axis=0)
            ) / (12 * dx**2)
            mixed = (
                dx_metric[i - 2] - 8 * dx_metric[i - 1]
                + 8 * dx_metric[i + 1] - dx_metric[i + 2]
            ) / (12 * dt)
            second[:, 0, 1, index, index] = mixed
            second[:, 1, 0, index, index] = mixed
        ricci[row] = ricci_from_metric_jet(metric, first, second)
        norms[row] = ricci_frame_norm(metric, ricci[row])
        scalars[row] = np.sum(
            np.diagonal(ricci[row], axis1=-2, axis2=-1) / diagonal[i], axis=-1
        )
    if not np.all(np.isfinite(scalars)):
        raise ValueError("uplift metric produced nonfinite Ricci scalars")
    return PlanarRicciResidual(t[2:-2].copy(), ricci, norms, scalars)
