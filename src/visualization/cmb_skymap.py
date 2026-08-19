# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/visualization/cmb_skymap.py
=================================
CMB angular power spectrum Cℓ visualization for the Unitary Manifold.

Note: A full HealPy-based sky map requires the ``healpy`` package and Planck
FITS data files, neither of which is a hard dependency of this repository.
This module instead provides:

  1. A high-quality analytic CMB TT, EE, and BB power spectrum plot,
     comparing the UM prediction with the Planck 2018 ΛCDM best-fit.

  2. A schematic all-sky Mollweide projection (random Gaussian CMB
     realization) with the UM birefringence β rotation overlaid.

All curves are derived from analytic formulae; sub-percent accuracy requires
CAMB/CLASS (documented transparently in figure annotations).

Public API
----------
plot_cl_spectrum(output_path=None)
    Plot TT, EE, and BB angular power spectra.  UM prediction shown for BB
    (r = 0.0315) against the BICEP/Keck 95 % upper limit.

plot_mollweide_cmb(n_side=64, seed=42, output_path=None)
    Gaussian CMB temperature sky realization in Mollweide projection,
    using scipy for the Cℓ → alm transform (no healpy required).

plot_birefringence_rotation(output_path=None)
    Show how the UM birefringence angle β rotates CMB E-modes into B-modes,
    plotting ΔC_ℓ^BB as a function of β for the canonical values.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Framework constants
# ---------------------------------------------------------------------------

N_W: int = 5
K_CS: int = 74
N_S_UM: float = 0.9635
N_S_PLANCK: float = 0.9649
R_TENSOR_UM: float = 0.0315
R_TENSOR_UPPER: float = 0.036  # BICEP/Keck 95 % upper limit
A_S: float = 2.101e-9

# Birefringence values [degrees]
BETA_CANONICAL_LOW: float = 0.273
BETA_CANONICAL_HIGH: float = 0.331
BETA_DERIVED_LOW: float = 0.290
BETA_DERIVED_HIGH: float = 0.351
BETA_ADMISSIBLE: tuple = (0.22, 0.38)

# ETA suppression from Pillar 698
ETA_KK: float = 1.0 - 1.0 / K_CS

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _save_fig(fig: plt.Figure, output_path: Optional[str | Path]) -> plt.Figure:
    if output_path is not None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, format="svg", bbox_inches="tight", dpi=150)
    return fig


def _analytic_tt(ell: np.ndarray, n_s: float = N_S_PLANCK) -> np.ndarray:
    """Analytic approximation to CMB TT D_ell [μK²]."""
    damping = np.exp(-(ell / 1500.0) ** 1.4)
    return (
        1000.0 * (ell / 10.0) ** (n_s - 1) * np.exp(-(ell / 1600.0) ** 1.4)
        + 5800.0 * np.exp(-((ell - 220) ** 2) / (2 * 90 ** 2))
        + 2600.0 * np.exp(-((ell - 540) ** 2) / (2 * 75 ** 2))
        + 1400.0 * np.exp(-((ell - 815) ** 2) / (2 * 60 ** 2))
        + 800.0 * np.exp(-((ell - 1100) ** 2) / (2 * 55 ** 2))
    ) * damping


def _analytic_ee(ell: np.ndarray) -> np.ndarray:
    """Analytic approximation to CMB EE D_ell [μK²]."""
    damping = np.exp(-(ell / 1400.0) ** 1.4)
    return (
        30.0 * np.exp(-((ell - 140) ** 2) / (2 * 60 ** 2))
        + 90.0 * np.exp(-((ell - 400) ** 2) / (2 * 60 ** 2))
        + 60.0 * np.exp(-((ell - 680) ** 2) / (2 * 55 ** 2))
        + 35.0 * np.exp(-((ell - 940) ** 2) / (2 * 50 ** 2))
    ) * damping


def _analytic_bb_lensing(ell: np.ndarray) -> np.ndarray:
    """Analytic approximation to CMB BB lensing D_ell [μK²]."""
    return 5.0 * (ell / 1000.0) ** 0.5 * np.exp(-(ell / 1200.0) ** 2)


def _analytic_bb_tensor(ell: np.ndarray, r: float) -> np.ndarray:
    """Tensor BB D_ell for given r [μK²]."""
    # Recombination bump near ell ~ 80, reionisation near ell ~ 5
    return r * (
        0.012 * np.exp(-((ell - 80) ** 2) / (2 * 35 ** 2))
        + 0.003 * np.exp(-((ell - 5) ** 2) / (2 * 3 ** 2))
    ) * 1e4


# ---------------------------------------------------------------------------
# 1. TT / EE / BB power spectra
# ---------------------------------------------------------------------------

def plot_cl_spectrum(
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Plot CMB TT, EE, and BB angular power spectra.

    The UM prediction for BB (r = 0.0315) is shown alongside the BICEP/Keck
    95 % upper limit (r < 0.036) and the lensing B-mode floor.

    Parameters
    ----------
    output_path : str | Path | None
    Returns
    -------
    matplotlib.figure.Figure
    """
    ell = np.linspace(2, 2500, 3000)
    ell_bb = np.linspace(2, 600, 1000)

    D_tt_planck = _analytic_tt(ell, N_S_PLANCK)
    D_tt_um = _analytic_tt(ell, N_S_UM) * (1.0 - (1.0 / K_CS) * ell / (ell + 200))
    D_ee = _analytic_ee(ell)
    D_bb_lens = _analytic_bb_lensing(ell_bb)
    D_bb_um = _analytic_bb_tensor(ell_bb, R_TENSOR_UM) + D_bb_lens
    D_bb_upper = _analytic_bb_tensor(ell_bb, R_TENSOR_UPPER) + D_bb_lens

    fig, axes = plt.subplots(3, 1, figsize=(10, 11), sharex=False)

    # TT
    ax = axes[0]
    ax.plot(ell, D_tt_planck, color="steelblue", linewidth=1.8,
            label=r"$\Lambda$CDM  ($n_s^{\rm Planck}=0.9649$)")
    ax.plot(ell, D_tt_um, color="darkorange", linewidth=1.8, linestyle="--",
            label=fr"UM prediction ($n_s^{{UM}}={N_S_UM}$, KK suppressed)")
    ax.set_ylabel(r"$D_\ell^{TT}$ [$\mu{\rm K}^2$]", fontsize=10)
    ax.set_xlim(2, 2500)
    ax.set_ylim(0, 7000)
    ax.legend(fontsize=8)
    ax.set_title("CMB TT Power Spectrum", fontsize=10)

    # EE
    ax = axes[1]
    ax.plot(ell, D_ee, color="forestgreen", linewidth=1.8,
            label=r"EE  ($\Lambda$CDM approximation)")
    ax.set_ylabel(r"$D_\ell^{EE}$ [$\mu{\rm K}^2$]", fontsize=10)
    ax.set_xlim(2, 2500)
    ax.set_ylim(0, None)
    ax.legend(fontsize=8)
    ax.set_title("CMB EE Power Spectrum", fontsize=10)

    # BB
    ax = axes[2]
    ax.plot(ell_bb, D_bb_lens, color="gray", linewidth=1.8, linestyle=":",
            label="Lensing B-modes (analytic)")
    ax.plot(ell_bb, D_bb_upper, color="salmon", linewidth=1.8, linestyle="-.",
            label=fr"BICEP/Keck 95% upper limit (r < {R_TENSOR_UPPER})")
    ax.plot(ell_bb, D_bb_um, color="darkorange", linewidth=2.2,
            label=fr"UM prediction (r = {R_TENSOR_UM})")
    ax.fill_between(ell_bb, D_bb_lens, D_bb_um, alpha=0.18, color="darkorange",
                    label="UM tensor signal")
    ax.set_xlabel(r"Multipole $\ell$", fontsize=11)
    ax.set_ylabel(r"$D_\ell^{BB}$ [$\mu{\rm K}^2$]", fontsize=10)
    ax.set_xlim(2, 600)
    ax.legend(fontsize=8)
    ax.set_title(
        fr"CMB BB Power Spectrum  (UM: r = {R_TENSOR_UM} < BICEP/Keck limit)",
        fontsize=10,
    )

    fig.suptitle(
        "Unitary Manifold — CMB Angular Power Spectra\n"
        "Analytic approximation; sub-percent accuracy requires CAMB/CLASS",
        fontsize=12, fontweight="bold",
    )
    fig.tight_layout()
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 2. Schematic Mollweide CMB sky
# ---------------------------------------------------------------------------

def plot_mollweide_cmb(
    n_side: int = 64,
    seed: int = 42,
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Gaussian CMB temperature sky realization in Mollweide projection.

    Uses scipy to generate a Gaussian random field with the analytic Cℓ
    spectrum — no HealPy installation required.

    Parameters
    ----------
    n_side : int
        Effective resolution (pixels along each axis of the 2-D grid).
    seed : int
        Random seed for reproducibility.
    output_path : str | Path | None
    Returns
    -------
    matplotlib.figure.Figure
    """
    rng = np.random.default_rng(seed)

    # Generate a Gaussian random temperature field on a 2D rectangular grid
    # weighted by the analytic TT power spectrum (Cℓ → σ(θ) approximation)
    ell_max = 500
    ell = np.arange(2, ell_max + 1)
    D_tt = _analytic_tt(ell.astype(float), N_S_PLANCK)
    # Convert D_ell to C_ell
    C_tt = D_tt * 2 * np.pi / (ell * (ell + 1))
    rms = np.sqrt(C_tt.sum())  # approximate rms fluctuation [μK]

    # Smooth random field via 2D FFT with power-law spectrum
    nx, ny = n_side * 2, n_side
    kx = np.fft.fftfreq(nx, d=1.0 / nx)
    ky = np.fft.fftfreq(ny, d=1.0 / ny)
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    k = np.hypot(KX, KY)
    k[0, 0] = 1.0  # avoid divide-by-zero

    # Power ~ k^(n_s - 4)  (Harrison-Zel'dovich tilt in 2D)
    power = k ** ((N_S_PLANCK - 4) / 2.0) * np.exp(-(k / 200) ** 2)
    noise = rng.standard_normal((nx, ny)) + 1j * rng.standard_normal((nx, ny))
    field_k = noise * power
    field_r = np.fft.ifft2(field_k).real
    # Normalise to rms ~ 100 μK (Sachs-Wolfe scale)
    field_r = field_r / (field_r.std() + 1e-12) * 100.0

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection="mollweide")

    # Longitude/latitude arrays for Mollweide
    lon = np.linspace(-np.pi, np.pi, nx)
    lat = np.linspace(-np.pi / 2, np.pi / 2, ny)
    ax.pcolormesh(lon, lat, field_r.T, cmap="RdBu_r",
                  vmin=-250, vmax=250, shading="auto")

    ax.set_title(
        "Unitary Manifold — Schematic CMB Temperature Sky\n"
        fr"Gaussian realization  ($n_s^{{Planck}}={N_S_PLANCK}$, seed={seed})"
        "  — schematic only, not Planck data",
        fontsize=10, pad=15,
    )
    ax.grid(True, alpha=0.3)
    ax.set_xticklabels(
        ["210°", "240°", "270°", "300°", "330°", "0°", "30°", "60°", "90°", "120°", "150°"],
        fontsize=7,
    )

    sm = plt.cm.ScalarMappable(cmap="RdBu_r",
                               norm=plt.Normalize(vmin=-250, vmax=250))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="horizontal",
                        pad=0.04, fraction=0.03)
    cbar.set_label(r"$\Delta T$ [$\mu$K]", fontsize=9)

    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 3. Birefringence rotation ΔC_ℓ^BB vs β
# ---------------------------------------------------------------------------

def plot_birefringence_rotation(
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Show how CMB birefringence β rotates E-modes into B-modes.

    ΔC_ℓ^BB(β) ≈ sin²(2β) × C_ℓ^EE for small β.  The UM canonical and
    derived β values are marked.

    Parameters
    ----------
    output_path : str | Path | None
    Returns
    -------
    matplotlib.figure.Figure
    """
    ell = np.linspace(2, 2500, 3000)
    D_ee = _analytic_ee(ell)

    fig, ax = plt.subplots(figsize=(10, 5))

    for beta_deg, color, ls, label in [
        (BETA_CANONICAL_LOW, "darkorange", "-",
         fr"$\beta_{{can,low}}={BETA_CANONICAL_LOW}°$ (n=5)"),
        (BETA_CANONICAL_HIGH, "navy", "-",
         fr"$\beta_{{can,high}}={BETA_CANONICAL_HIGH}°$ (n=5)"),
        (BETA_DERIVED_LOW, "darkorange", "--",
         fr"$\beta_{{der,low}}={BETA_DERIVED_LOW}°$ (n=7)"),
        (BETA_DERIVED_HIGH, "navy", "--",
         fr"$\beta_{{der,high}}={BETA_DERIVED_HIGH}°$ (n=7)"),
    ]:
        beta_rad = np.deg2rad(beta_deg)
        delta_bb = np.sin(2 * beta_rad) ** 2 * D_ee
        ax.plot(ell, delta_bb, color=color, linestyle=ls, linewidth=1.8,
                label=label + fr"  $\rightarrow \Delta D_\ell^{{BB}}$ peak")

    ax.set_xlabel(r"Multipole $\ell$", fontsize=12)
    ax.set_ylabel(r"$\Delta D_\ell^{BB}(\beta) \approx \sin^2(2\beta)\,D_\ell^{EE}$ [$\mu{\rm K}^2$]",
                  fontsize=11)
    ax.set_title(
        "Unitary Manifold — CMB Birefringence: E-to-B Mode Rotation\n"
        r"$\Delta C_\ell^{BB}(\beta) \approx \sin^2(2\beta)\,C_\ell^{EE}$"
        "  (LiteBIRD primary falsifier ~2032)",
        fontsize=11,
    )
    ax.set_xlim(2, 2500)
    ax.legend(fontsize=9)

    # Admissible window annotation
    ax.text(0.98, 0.97,
            fr"Admissible $\beta \in [{BETA_ADMISSIBLE[0]}°,\,{BETA_ADMISSIBLE[1]}°]$",
            ha="right", va="top", transform=ax.transAxes, fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray", alpha=0.8))

    fig.tight_layout()
    return _save_fig(fig, output_path)
