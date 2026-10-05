# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/visualization/geometry_viz.py
===================================
5D Kaluza-Klein geometry visualizations for the Unitary Manifold.

Functions
---------
plot_metric_slice(x_pts=200, output_path=None)
    1-D slice of the 5D KK metric component G_55 = φ(x)² showing the
    radion profile across the extra dimension.

plot_compactification_radius(output_path=None)
    Compactification radius R_c as a function of winding number n_w,
    fixing K_CS = 74, illustrating the unique n_w = 5 selection.

plot_winding_number_diagram(output_path=None)
    Schematic of the S¹/Z₂ extra dimension with the n_w = 5 winding
    depicted as a phase diagram on the circle.

plot_5d_potential(output_path=None)
    Goldberger-Wise radion potential V(φ, r_c) slice at φ = φ₀,
    showing stabilisation at r_c = N_W / K_CS.
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
# Framework constants
# ---------------------------------------------------------------------------

N_W: int = 5
K_CS: int = 74
C_S: float = 12 / 37
R_C: float = N_W / K_CS   # compactification radius [M_Pl⁻¹]

# Goldberger-Wise potential parameters (natural units)
LAMBDA_GW: float = 1.0    # coupling (normalised)
PHI0: float = 1.0         # radion VEV at minimum

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _save_fig(fig: plt.Figure, output_path: Optional[str | Path]) -> plt.Figure:
    if output_path is not None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, format="svg", bbox_inches="tight", dpi=150)
    return fig


# ---------------------------------------------------------------------------
# 1. 5D metric G_55 = φ(x)² radion profile
# ---------------------------------------------------------------------------

def plot_metric_slice(
    x_pts: int = 200,
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Plot a 1-D slice of the 5D KK metric component G_55 = φ(x)².

    The radion field φ(x) is modelled as a Gaussian wavepacket centred on
    the orbifold fixed point x = 0, stabilised at φ₀ by the Goldberger-Wise
    mechanism.

    Parameters
    ----------
    x_pts : int
        Number of grid points along the extra dimension.
    output_path : str | Path | None
        If given, the figure is saved as an SVG.

    Returns
    -------
    matplotlib.figure.Figure
    """
    # x ∈ [-π R_c, +π R_c]  (S¹/Z₂ orbifold)
    x = np.linspace(-np.pi * R_C, np.pi * R_C, x_pts)

    # φ(x) = φ₀ × (1 − δφ × cos(x / R_c))  where δφ ≪ 1
    # This is the leading Fourier mode of the Goldberger-Wise solution.
    delta_phi = 0.05
    phi = PHI0 * (1.0 - delta_phi * np.cos(x / R_C))
    G55 = phi ** 2

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # --- left: φ(x) ---
    ax = axes[0]
    ax.plot(x / R_C, phi, color="royalblue", linewidth=2)
    ax.axhline(PHI0, color="gray", linestyle="--", linewidth=1, label=r"$\phi_0 = 1$")
    ax.set_xlabel(r"Position $x / R_c$", fontsize=11)
    ax.set_ylabel(r"Radion field $\phi(x)$ [$M_{\rm Pl}$]", fontsize=11)
    ax.set_title(r"Radion profile $\phi(x)$ on $S^1/\mathbb{Z}_2$", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_xlim(-np.pi, np.pi)

    # --- right: G_55 = φ² ---
    ax = axes[1]
    ax.plot(x / R_C, G55, color="darkorange", linewidth=2)
    ax.axhline(PHI0 ** 2, color="gray", linestyle="--", linewidth=1,
               label=r"$\phi_0^2 = 1$")
    ax.set_xlabel(r"Position $x / R_c$", fontsize=11)
    ax.set_ylabel(r"$G_{55}(x) = \phi(x)^2$ [$M_{\rm Pl}^2$]", fontsize=11)
    ax.set_title(
        fr"5D metric component $G_{{55}}$"
        fr"  ($R_c = {N_W}/{K_CS} \approx {R_C:.4f}\,M_{{Pl}}^{{-1}}$)",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.set_xlim(-np.pi, np.pi)

    fig.suptitle(
        r"Unitary Manifold — 5D KK Metric Slice  ($N_W = 5$, $K_{CS} = 74$)",
        fontsize=12, fontweight="bold", y=1.02,
    )
    fig.tight_layout()
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 2. R_c vs winding number
# ---------------------------------------------------------------------------

def plot_compactification_radius(
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Plot R_c = n_w / K_CS as a function of winding number n_w.

    Highlights n_w = 5 (UM prediction selected by Planck nₛ) and n_w = 7
    (the secondary braid strand).

    Parameters
    ----------
    output_path : str | Path | None
        If given, the figure is saved as an SVG.

    Returns
    -------
    matplotlib.figure.Figure
    """
    nw_vals = np.arange(1, 16)
    rc_vals = nw_vals / K_CS

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(nw_vals, rc_vals, color="steelblue", alpha=0.6, width=0.6,
           label=r"$R_c = n_w / K_{CS}$")
    ax.bar([N_W], [N_W / K_CS], color="darkorange", width=0.6,
           label=fr"$n_w = {N_W}$ (UM selection, Planck $n_s$)")
    ax.bar([7], [7 / K_CS], color="forestgreen", width=0.6,
           label=r"$n_w = 7$ (secondary braid strand)")

    ax.axhline(N_W / K_CS, color="darkorange", linestyle="--", linewidth=1.2)
    ax.axhline(7 / K_CS, color="forestgreen", linestyle="--", linewidth=1.2)

    ax.set_xlabel(r"Winding number $n_w$", fontsize=12)
    ax.set_ylabel(r"Compactification radius $R_c$ [$M_{\rm Pl}^{-1}$]", fontsize=12)
    ax.set_title(
        fr"Unitary Manifold — $R_c$ vs Winding Number  ($K_{{CS}} = {K_CS}$)",
        fontsize=11,
    )
    ax.set_xticks(nw_vals)
    ax.legend(fontsize=9)
    ax.text(0.98, 0.95,
            fr"$n_w = 5$ selected by Planck $n_s = {0.9649}$ (Pillar 67)",
            ha="right", va="top", transform=ax.transAxes, fontsize=9, color="darkorange")

    fig.tight_layout()
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 3. Winding number diagram (S¹ phase circle)
# ---------------------------------------------------------------------------

def plot_winding_number_diagram(
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Draw the n_w = 5 winding on S¹ as a phase diagram.

    The extra dimension S¹/Z₂ is shown as a unit circle; the winding field
    e^{i n_w θ} is drawn as a 5-lobed rose pattern to visualise the braid
    topology (5, 7) → K_CS = 74.

    Parameters
    ----------
    output_path : str | Path | None
        If given, the figure is saved as an SVG.

    Returns
    -------
    matplotlib.figure.Figure
    """
    theta = np.linspace(0, 2 * np.pi, 1000)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), subplot_kw={"aspect": "equal"})

    for ax, nw, color, title in [
        (axes[0], 5, "darkorange",
         r"$n_w = 5$ winding  (UM selection)"),
        (axes[1], 7, "forestgreen",
         r"$n_w = 7$ secondary strand"),
    ]:
        # Rose curve: r = cos(nw × θ / 2)  for petal visualisation
        r = np.abs(np.cos(nw * theta / 2))
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # Outer S¹ circle
        ax.plot(np.cos(theta), np.sin(theta), "k-", linewidth=1.2, alpha=0.4)
        ax.fill(x, y, color=color, alpha=0.25)
        ax.plot(x, y, color=color, linewidth=1.8)

        # Fixed points at θ = 0 and θ = π (Z₂ orbifold)
        ax.plot([1, -1], [0, 0], "ko", markersize=8, zorder=5)
        ax.text(1.08, 0, r"$\theta=0$", va="center", fontsize=9)
        ax.text(-1.15, 0, r"$\theta=\pi$", va="center", ha="right", fontsize=9)

        ax.set_title(title, fontsize=11)
        ax.set_xlim(-1.25, 1.25)
        ax.set_ylim(-1.25, 1.25)
        ax.axis("off")

    fig.suptitle(
        fr"Unitary Manifold — $S^1/\mathbb{{Z}}_2$ Winding Topology"
        fr"  ($K_{{CS}} = {N_W}^2 + 7^2 = {K_CS}$)",
        fontsize=12, fontweight="bold",
    )
    fig.tight_layout()
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 4. Goldberger-Wise radion potential
# ---------------------------------------------------------------------------

def plot_5d_potential(
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Plot the Goldberger-Wise radion potential V(r_c) = λ_GW (r_c − R_c*)².

    Shows stabilisation at R_c* = N_W / K_CS with the mass gap proportional
    to the curvature at the minimum.

    Parameters
    ----------
    output_path : str | Path | None
        If given, the figure is saved as an SVG.

    Returns
    -------
    matplotlib.figure.Figure
    """
    rc_min = R_C * 0.4
    rc_max = R_C * 2.0
    rc = np.linspace(rc_min, rc_max, 400)
    V = LAMBDA_GW * (rc - R_C) ** 2  # GW potential (leading term)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(rc / R_C, V / V.max(), color="royalblue", linewidth=2.5)
    ax.axvline(1.0, color="darkorange", linestyle="--", linewidth=2,
               label=fr"Minimum at $R_c^* = {N_W}/{K_CS} \approx {R_C:.4f}\,M_{{Pl}}^{{-1}}$")
    ax.fill_between(rc / R_C, 0, V / V.max(), alpha=0.08, color="royalblue")

    # Label mass gap (curvature at minimum = 2 λ_GW)
    delta = 0.15
    ax.annotate(
        r"$m_{\rm radion}^2 = 2\lambda_{\rm GW}$",
        xy=(1.0 + delta, LAMBDA_GW * (delta * R_C) ** 2 / V.max()),
        xytext=(1.4, 0.35),
        arrowprops=dict(arrowstyle="->", color="black"),
        fontsize=10,
    )

    ax.set_xlabel(r"$r_c / R_c^*$", fontsize=12)
    ax.set_ylabel(r"$V(r_c) / V_{\rm max}$  [normalised]", fontsize=12)
    ax.set_title(
        r"Unitary Manifold — Goldberger-Wise Radion Potential" "\n"
        fr"$V(r_c) = \lambda_{{GW}}\,(r_c - R_c^*)^2$,  "
        + f"$R_c^* = {N_W}/{K_CS}" + r" \approx " + f"{R_C:.4f}" + r"\,M_{\rm Pl}^{-1}$",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.set_xlim(rc_min / R_C, rc_max / R_C)
    ax.set_ylim(-0.02, 1.08)

    fig.tight_layout()
    return _save_fig(fig, output_path)
