# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/visualization/pillar_plots.py
==================================
Automated reference plots for the Unitary Manifold's key observable predictions.

Every function is deterministic (no random state) and derives its curves
directly from the framework constants — the same values that appear in the
test suite.  Figures are saved as vector SVGs for publication quality.

Public API
----------
plot_birefringence_window(output_path=None)
    β admissible window [0.22°, 0.38°] with canonical (0.273°/0.331°) and
    derived (0.290°/0.351°) branches marked.  LiteBIRD gap [0.29°, 0.31°] shaded.

plot_r_ns_plane(output_path=None)
    Tensor-to-scalar ratio r vs spectral index nₛ.  UM prediction point
    (nₛ = 0.9635, r = 0.0315) overlaid on Planck 2018 + BICEP/Keck contours
    represented analytically (no external data files required).

plot_kk_mass_tower(n_max=10, output_path=None)
    Kaluza-Klein mass tower mₙ = n / R_c for n = 0 … n_max using the
    UM-derived compactification radius R_c = N_W / (K_CS × M_Pl).

plot_cmb_tt_spectrum(output_path=None)
    Toy CMB TT power spectrum Dℓ = ℓ(ℓ+1)Cℓ / 2π showing the braided-winding
    KK suppression η(k) < 1 documented in Pillar 698.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# Framework constants (all values match the test suite and STATUS.md)
# ---------------------------------------------------------------------------

# Winding / braid triad
N_W: int = 5          # winding number (selected by Planck nₛ)
K_CS: int = 74        # Chern-Simons level = 5² + 7²
C_S: float = 12 / 37  # braided sound speed

# Inflation observables (UM predictions)
N_S_UM: float = 0.9635     # scalar spectral index (UM prediction)
R_TENSOR_UM: float = 0.0315  # tensor-to-scalar ratio (UM prediction)

# Planck 2018 best-fit
N_S_PLANCK: float = 0.9649
N_S_PLANCK_ERR: float = 0.0042

# Birefringence (degrees)
BETA_ADMISSIBLE_LOW: float = 0.22
BETA_ADMISSIBLE_HIGH: float = 0.38
BETA_CANONICAL_LOW: float = 0.273   # n=5 low branch
BETA_CANONICAL_HIGH: float = 0.331  # n=5 high branch
BETA_DERIVED_LOW: float = 0.290     # n=7 low branch (from framework)
BETA_DERIVED_HIGH: float = 0.351    # n=7 high branch
BETA_GAP_LOW: float = 0.290         # LiteBIRD gap region
BETA_GAP_HIGH: float = 0.310

# KK compactification (natural units, M_Pl = 1)
# R_c = N_W / (K_CS × M_Pl)  [Planck units]
R_C_PLANCK: float = N_W / K_CS      # ≈ 0.0676 M_Pl⁻¹

# KK suppression amplitude from Pillar 698
ETA_KK: float = 1.0 - 1.0 / K_CS   # η ≈ 0.9865


def _save_fig(fig: plt.Figure, output_path: Optional[str | Path]) -> plt.Figure:
    """Save *fig* to *output_path* as SVG if a path is provided."""
    if output_path is not None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, format="svg", bbox_inches="tight", dpi=150)
    return fig


# ---------------------------------------------------------------------------
# 1. Birefringence β window
# ---------------------------------------------------------------------------

def plot_birefringence_window(output_path: Optional[str | Path] = None) -> plt.Figure:
    """Plot the UM birefringence β admissible window with predicted branches.

    The admissible window [0.22°, 0.38°] is shaded in light blue.
    The forbidden gap [0.29°, 0.31°] is shaded in pink — a β measurement
    landing inside the gap would falsify the braided-winding mechanism.

    Parameters
    ----------
    output_path : str | Path | None
        If given, the figure is saved as an SVG at this path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    # Admissible window
    ax.axhspan(BETA_ADMISSIBLE_LOW, BETA_ADMISSIBLE_HIGH,
               color="steelblue", alpha=0.15, label="Admissible window [0.22°, 0.38°]")

    # Forbidden gap (falsification region)
    ax.axhspan(BETA_GAP_LOW, BETA_GAP_HIGH,
               color="salmon", alpha=0.35, label="Forbidden gap [0.29°, 0.31°]")

    # n = 5 canonical branches
    for beta, label in [
        (BETA_CANONICAL_LOW, r"$\beta_{\rm can,\,low}$ = 0.273° (n=5)"),
        (BETA_CANONICAL_HIGH, r"$\beta_{\rm can,\,high}$ = 0.331° (n=5)"),
    ]:
        ax.axhline(beta, color="navy", linewidth=2, linestyle="-")
        ax.text(1.02, beta, label, va="center", ha="left",
                transform=ax.get_yaxis_transform(), fontsize=9, color="navy")

    # n = 7 derived branches
    for beta, label in [
        (BETA_DERIVED_LOW, r"$\beta_{\rm der,\,low}$ = 0.290° (n=7)"),
        (BETA_DERIVED_HIGH, r"$\beta_{\rm der,\,high}$ = 0.351° (n=7)"),
    ]:
        ax.axhline(beta, color="darkorange", linewidth=2, linestyle="--")
        ax.text(1.02, beta, label, va="center", ha="left",
                transform=ax.get_yaxis_transform(), fontsize=9, color="darkorange")

    ax.set_ylim(0.18, 0.42)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_ylabel(r"Birefringence angle $\beta$ [degrees]", fontsize=11)
    ax.set_title(
        "Unitary Manifold — CMB Birefringence β Prediction\n"
        r"Primary falsifier: LiteBIRD ~2032; window $\beta \in [0.22°,\,0.38°]$",
        fontsize=11,
    )
    ax.legend(loc="upper right", fontsize=9)

    fig.tight_layout()
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 2. r – nₛ plane
# ---------------------------------------------------------------------------

def plot_r_ns_plane(output_path: Optional[str | Path] = None) -> plt.Figure:
    """Plot the tensor-to-scalar ratio r vs spectral index nₛ.

    Shows 68 % and 95 % analytic Gaussian approximations of Planck 2018 +
    BICEP/Keck posteriors centred on the Planck best-fit nₛ.  The UM
    prediction point (nₛ = 0.9635, r = 0.0315) is overlaid.

    Parameters
    ----------
    output_path : str | Path | None
        If given, the figure is saved as an SVG at this path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(7, 6))

    # --- analytic Planck 2018 posterior approximation (Gaussian in nₛ, r) ---
    ns_center = N_S_PLANCK        # 0.9649
    ns_sigma = N_S_PLANCK_ERR     # 0.0042
    r_upper_95 = 0.036            # BICEP/Keck 2021 95 % upper limit

    ns_vals = np.linspace(0.94, 0.985, 400)
    r_vals = np.linspace(0.0, 0.065, 400)
    NS, R = np.meshgrid(ns_vals, r_vals)

    # Approximate 2D posterior: Gaussian in nₛ, exponential decay in r
    # r posterior ~ exp(-r / r_scale) normalised so 95 % < r_upper_95
    r_scale = r_upper_95 / (-np.log(0.05))
    log_posterior = (
        -0.5 * ((NS - ns_center) / ns_sigma) ** 2
        - R / r_scale
    )
    posterior = np.exp(log_posterior - log_posterior.max())

    # Contour levels for 68 % and 95 % credible regions
    flat = np.sort(posterior.ravel())[::-1]
    cumsum = np.cumsum(flat) / flat.sum()
    level_68 = flat[np.searchsorted(cumsum, 0.68)]
    level_95 = flat[np.searchsorted(cumsum, 0.95)]

    cf = ax.contourf(NS, R, posterior, levels=[level_95, level_68, posterior.max()],
                     colors=["#aec6e8", "#4a90d9", "#1a5fa8"], alpha=0.55)
    ax.contour(NS, R, posterior, levels=[level_95, level_68],
               colors=["#1a5fa8", "#4a90d9"], linewidths=1.2)

    # Legend patches for contours
    p68 = mpatches.Patch(color="#4a90d9", alpha=0.75, label="Planck 2018 68%")
    p95 = mpatches.Patch(color="#aec6e8", alpha=0.75, label="Planck 2018 95%")

    # UM prediction
    ax.plot(N_S_UM, R_TENSOR_UM, "r*", markersize=14,
            label=fr"UM prediction ($n_s$={N_S_UM}, r={R_TENSOR_UM})",
            zorder=5)
    ax.annotate(
        fr"UM: $n_s$={N_S_UM}, r={R_TENSOR_UM}",
        xy=(N_S_UM, R_TENSOR_UM),
        xytext=(N_S_UM + 0.003, R_TENSOR_UM + 0.006),
        arrowprops=dict(arrowstyle="->", color="red"),
        fontsize=9, color="red",
    )

    # BICEP/Keck r < 0.036 upper limit (dashed)
    ax.axhline(0.036, color="gray", linestyle=":", linewidth=1.2,
               label="BICEP/Keck r < 0.036 (95%)")

    ax.set_xlabel(r"Scalar spectral index $n_s$", fontsize=12)
    ax.set_ylabel(r"Tensor-to-scalar ratio $r$", fontsize=12)
    ax.set_title(
        r"Unitary Manifold — $r\,{-}\,n_s$ Inflation Plane" "\n"
        r"Planck 2018 + BICEP/Keck contours (analytic approximation)",
        fontsize=11,
    )
    ax.set_xlim(0.945, 0.982)
    ax.set_ylim(0.0, 0.060)
    ax.legend(handles=[p68, p95,
                        ax.lines[-1],
                        ax.get_lines()[0] if ax.get_lines() else mpatches.Patch()],
              fontsize=9, loc="upper left")
    ax.legend(fontsize=9, loc="upper left")

    fig.tight_layout()
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 3. Kaluza-Klein mass tower
# ---------------------------------------------------------------------------

def plot_kk_mass_tower(
    n_max: int = 10,
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Plot the Kaluza-Klein mass tower mₙ = n / R_c (Planck units).

    The UM-derived compactification radius R_c = N_W / K_CS M_Pl sets the
    mass gap.  Modes are shown as horizontal levels with the zero-mode (n=0)
    at the bottom.

    Parameters
    ----------
    n_max : int
        Highest KK level to display (default 10).
    output_path : str | Path | None
        If given, the figure is saved as an SVG at this path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    ns = np.arange(0, n_max + 1)
    masses = ns / R_C_PLANCK  # mₙ = n / R_c  [M_Pl]

    fig, ax = plt.subplots(figsize=(6, 7))

    for n, m in zip(ns, masses):
        color = "royalblue" if n > 0 else "black"
        lw = 2 if n > 0 else 2.5
        ax.axhline(m, color=color, linewidth=lw, xmin=0.1, xmax=0.9)
        ax.text(0.92, m, f"n={n}", va="center", ha="left",
                transform=ax.get_yaxis_transform(), fontsize=9, color=color)

    # Mark the KK mass gap
    ax.annotate(
        "",
        xy=(0.5, masses[1]), xytext=(0.5, 0),
        arrowprops=dict(arrowstyle="<->", color="red", lw=1.5),
        xycoords=("axes fraction", "data"),
        textcoords=("axes fraction", "data"),
    )
    ax.text(0.53, masses[1] / 2,
            fr"$\Delta m = 1/R_c = {1/R_C_PLANCK:.1f}\,M_{{Pl}}$",
            va="center", fontsize=9, color="red",
            transform=ax.get_yaxis_transform())

    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_ylabel(r"KK mode mass $m_n$ [$M_{\rm Pl}$]", fontsize=12)
    ax.set_title(
        "Unitary Manifold — Kaluza-Klein Mass Tower\n"
        fr"$R_c = N_W / K_{{CS}} = {N_W}/{K_CS} \approx {R_C_PLANCK:.4f}\,M_{{Pl}}^{{-1}}$",
        fontsize=11,
    )

    fig.tight_layout()
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 4. Toy CMB TT power spectrum with KK suppression
# ---------------------------------------------------------------------------

def plot_cmb_tt_spectrum(output_path: Optional[str | Path] = None) -> plt.Figure:
    """Plot the CMB TT power spectrum Dℓ = ℓ(ℓ+1)Cℓ / 2π.

    Shows the ΛCDM baseline and the UM braided-winding KK-suppressed variant
    (η < 1 from Pillar 698).  Acoustic peaks are modelled analytically via
    a damped sinusoidal approximation.

    Parameters
    ----------
    output_path : str | Path | None
        If given, the figure is saved as an SVG at this path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    ell = np.linspace(2, 2500, 3000)

    # --------------- ΛCDM analytic approximation -------------------------
    # D_ell ~ A_s * (ell/ell_pivot)^(n_s - 1) * (1 + acoustic + damping)
    A_s = 2.101e-9
    ell_pivot = 200.0

    # Sachs-Wolfe plateau + acoustic peaks (simplified analytic model)
    plateau = A_s * (ell / ell_pivot) ** (N_S_PLANCK - 1)
    acoustic = 5000.0 * np.exp(-((ell - 220) ** 2) / (2 * 80 ** 2))  # 1st peak
    acoustic += 2400.0 * np.exp(-((ell - 540) ** 2) / (2 * 70 ** 2))  # 2nd peak
    acoustic += 1500.0 * np.exp(-((ell - 815) ** 2) / (2 * 60 ** 2))  # 3rd peak
    acoustic += 900.0 * np.exp(-((ell - 1100) ** 2) / (2 * 55 ** 2))   # 4th peak
    # Silk damping envelope
    damping = np.exp(-(ell / 1500.0) ** 1.4)
    D_lcdm_raw = (plateau + acoustic * 1e-9) * ell * (ell + 1) / (2 * np.pi)
    # Rescale to physical μK² units (rough normalisation)
    D_lcdm = D_lcdm_raw / D_lcdm_raw.max() * 5800.0 * damping + 5800.0 * plateau / plateau[0] * (1 - damping) * 0.01

    # Proper Sachs-Wolfe plateau ~ 1000 μK² normalised
    # Use a cleaner analytic model:
    D_lcdm = (
        1000.0 * (ell / 10) ** (N_S_PLANCK - 1) * np.exp(-(ell / 1500) ** 1.4)
        + 5800.0 * np.exp(-((ell - 220) ** 2) / (2 * 90 ** 2))
        + 2600.0 * np.exp(-((ell - 540) ** 2) / (2 * 75 ** 2))
        + 1400.0 * np.exp(-((ell - 815) ** 2) / (2 * 60 ** 2))
        + 800.0 * np.exp(-((ell - 1100) ** 2) / (2 * 55 ** 2))
    ) * damping

    # UM variant: KK suppression η = 1 - 1/K_CS < 1 at all scales
    # η(ℓ) = ETA_KK at high ℓ, approaches 1 for ℓ → 0
    eta_ell = 1.0 - (1.0 / K_CS) * (ell / (ell + 200.0))
    D_um = D_lcdm * eta_ell

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ell, D_lcdm, color="steelblue", linewidth=1.8,
            label=r"$\Lambda$CDM baseline ($n_s^{\rm Planck}$ = 0.9649)")
    ax.plot(ell, D_um, color="darkorange", linewidth=1.8, linestyle="--",
            label=fr"UM KK-suppressed ($\eta < 1$, $K_{{CS}}={K_CS}$, $n_s^{{UM}}={N_S_UM}$)")
    ax.fill_between(ell, D_um, D_lcdm, alpha=0.15, color="darkorange",
                    label=r"KK suppression $\Delta D_\ell$")

    ax.set_xlabel(r"Multipole $\ell$", fontsize=12)
    ax.set_ylabel(r"$D_\ell \equiv \ell(\ell+1)C_\ell / 2\pi$ [$\mu\mathrm{K}^2$]",
                  fontsize=12)
    ax.set_title(
        "Unitary Manifold — CMB TT Power Spectrum\n"
        r"Analytic model: Pillar 698 KK suppression $\eta(k) < 1$ (ARCHITECTURE_LIMIT documented)",
        fontsize=11,
    )
    ax.set_xlim(2, 2500)
    ax.set_ylim(0, 7000)
    ax.legend(fontsize=9)
    ax.text(0.98, 0.04,
            "Note: acoustic peak amplitudes are analytically approximated;\n"
            "sub-percent accuracy requires CAMB/CLASS.",
            ha="right", va="bottom", transform=ax.transAxes,
            fontsize=7.5, color="gray", style="italic")

    fig.tight_layout()
    return _save_fig(fig, output_path)
