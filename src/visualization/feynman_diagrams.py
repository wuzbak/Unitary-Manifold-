# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/visualization/feynman_diagrams.py
======================================
Programmatic Feynman-style vertex diagrams for the Unitary Manifold, drawn
entirely with matplotlib — no external ``feynman`` package required.

Each diagram function returns a ``matplotlib.figure.Figure`` and accepts an
optional ``output_path`` for SVG export.

Functions
---------
draw_kk_graviton_vertex(output_path=None)
    KK graviton (Gμν⁽ⁿ⁾) coupled to two Standard Model fermions at the
    brane, showing the tower index n.

draw_kk_photon_vertex(output_path=None)
    KK photon (Aμ⁽ⁿ⁾) — emergence of U(1)_EM from the 5D gauge field Bμ.
    Vertex labels encode λφ coupling from the KK metric ansatz.

draw_radion_coupling(output_path=None)
    Radion (φ) – matter coupling vertex: φ × T^μμ (trace of stress tensor).
    Goldberger-Wise stabilisation mass mφ = √(2λ_GW) shown on the line.

draw_braided_winding_vertex(output_path=None)
    Two-axion → graviton scattering with the (5, 7, 74) braid triad
    Chern-Simons insertion, illustrating the birefringence mechanism.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np

# ---------------------------------------------------------------------------
# Framework constants (kept local to avoid import-chain coupling)
# ---------------------------------------------------------------------------

N_W: int = 5
K_CS: int = 74
R_C: float = N_W / K_CS
LAMBDA_GW: float = 1.0

# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------

def _arrow_line(ax, x0, y0, x1, y1, color="black", lw=1.8,
                label: str = "", label_pos: float = 0.5,
                label_offset=(0.02, 0.04)):
    """Draw a directed line with a mid-arrow and optional label."""
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=lw, mutation_scale=14))
    if label:
        mx = x0 + label_pos * (x1 - x0) + label_offset[0]
        my = y0 + label_pos * (y1 - y0) + label_offset[1]
        ax.text(mx, my, label, fontsize=10, color=color, ha="center", va="center")


def _wavy_line(ax, x0, y0, x1, y1, n_waves=6, amplitude=0.04,
               color="royalblue", lw=1.8, label="", label_offset=(0, 0.08)):
    """Draw a wavy (boson) propagator line."""
    t = np.linspace(0, 1, 400)
    dx = x1 - x0
    dy = y1 - y0
    length = np.hypot(dx, dy)
    perp_x = -dy / length
    perp_y = dx / length
    wave = amplitude * np.sin(2 * np.pi * n_waves * t)
    xs = x0 + t * dx + wave * perp_x
    ys = y0 + t * dy + wave * perp_y
    ax.plot(xs, ys, color=color, linewidth=lw)
    if label:
        mx = (x0 + x1) / 2 + label_offset[0]
        my = (y0 + y1) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=10, color=color, ha="center")


def _gluon_line(ax, x0, y0, x1, y1, n_loops=5, amplitude=0.04,
                color="green", lw=1.6, label="", label_offset=(0, 0.08)):
    """Draw a spring/gluon propagator line (helical)."""
    t = np.linspace(0, 1, 600)
    dx = x1 - x0
    dy = y1 - y0
    length = np.hypot(dx, dy)
    perp_x = -dy / (length + 1e-12)
    perp_y = dx / (length + 1e-12)
    wave = amplitude * np.sin(2 * np.pi * n_loops * t)
    bulge = amplitude * 0.6 * np.cos(2 * np.pi * n_loops * t)
    xs = x0 + t * dx + wave * perp_x + bulge * (perp_x * 0.0)
    ys = y0 + t * dy + wave * perp_y
    ax.plot(xs, ys, color=color, linewidth=lw)
    if label:
        mx = (x0 + x1) / 2 + label_offset[0]
        my = (y0 + y1) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=10, color=color, ha="center")


def _dashed_line(ax, x0, y0, x1, y1, color="gray", lw=1.6,
                 label="", label_offset=(0.02, 0.04)):
    """Draw a dashed scalar propagator line."""
    ax.plot([x0, x1], [y0, y1], color=color, linewidth=lw, linestyle="--")
    if label:
        mx = (x0 + x1) / 2 + label_offset[0]
        my = (y0 + y1) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=10, color=color, ha="center")


def _vertex_dot(ax, x, y, size=80, color="black"):
    ax.scatter([x], [y], s=size, color=color, zorder=5)


def _save_fig(fig: plt.Figure, output_path: Optional[str | Path]) -> plt.Figure:
    if output_path is not None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, format="svg", bbox_inches="tight", dpi=150)
    return fig


def _clean_axes(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")


# ---------------------------------------------------------------------------
# 1. KK graviton – fermion vertex
# ---------------------------------------------------------------------------

def draw_kk_graviton_vertex(
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Draw KK graviton G^(n)_μν coupled to two Standard Model fermions.

    Topology: two fermion lines enter/exit the vertex, one wavy graviton
    line carries tower index n.  The coupling ~ (1/M_Pl) × (n/R_c) is
    annotated.

    Parameters
    ----------
    output_path : str | Path | None
    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(6, 5))
    _clean_axes(ax)

    # Vertex at centre
    vx, vy = 0.5, 0.5
    _vertex_dot(ax, vx, vy)

    # Incoming fermion f (lower left → vertex)
    _arrow_line(ax, 0.15, 0.2, vx, vy, color="black", label=r"$f$",
                label_offset=(-0.05, 0.04))
    # Outgoing fermion f' (vertex → upper left)
    _arrow_line(ax, vx, vy, 0.15, 0.8, color="black", label=r"$f$",
                label_offset=(-0.05, -0.04))
    # KK graviton (wavy, right)
    _wavy_line(ax, vx, vy, 0.92, 0.5,
               label=r"$G^{(n)}_{\mu\nu}$", label_offset=(0.0, 0.07))

    # Coupling annotation
    ax.text(0.62, 0.32,
            fr"$\kappa_n = \frac{{1}}{{M_{{Pl}}}}\,\frac{{n}}{{R_c}}$"
            fr"$= \frac{{n\,K_{{CS}}}}{{N_W\,M_{{Pl}}}}$",
            fontsize=10, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray", alpha=0.8))
    ax.text(0.87, 0.43, fr"$n = 1,2,\ldots$", fontsize=9, color="royalblue")

    ax.set_title(
        "KK Graviton – Fermion Vertex\n"
        fr"$G^{{(n)}}_{{\mu\nu}}\,\bar{{f}}\,f$  coupling  ($K_{{CS}}={K_CS}$, $N_W={N_W}$)",
        fontsize=11,
    )
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 2. KK photon vertex: U(1)_EM from 5D gauge field
# ---------------------------------------------------------------------------

def draw_kk_photon_vertex(
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Draw the KK photon A^(n)_μ – charged fermion vertex.

    The 5D origin A_μ = λφB_μ from the KK metric ansatz is annotated,
    showing how U(1)_EM emerges geometrically.

    Parameters
    ----------
    output_path : str | Path | None
    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(6, 5))
    _clean_axes(ax)

    vx, vy = 0.5, 0.5
    _vertex_dot(ax, vx, vy)

    _arrow_line(ax, 0.15, 0.2, vx, vy, label=r"$e^-$",
                label_offset=(-0.06, 0.04))
    _arrow_line(ax, vx, vy, 0.15, 0.8, label=r"$e^-$",
                label_offset=(-0.06, -0.04))
    _wavy_line(ax, vx, vy, 0.92, 0.5,
               color="darkorange",
               label=r"$A^{(n)}_\mu = \lambda\phi B_\mu$",
               label_offset=(0.02, 0.08))

    ax.text(0.60, 0.28,
            r"$g_n = e\,\frac{n}{R_c\,M_{\rm Pl}}$",
            fontsize=10, ha="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray", alpha=0.8))
    ax.text(0.50, 0.13,
            r"U(1)$_{\rm EM}$ emerges from $G_{A5} = \lambda\phi B_A$  (KK metric ansatz)",
            fontsize=8.5, ha="center", color="gray", style="italic")

    ax.set_title(
        r"KK Photon – Fermion Vertex" "\n"
        r"$A^{(n)}_\mu\,\bar{e}\,e$  coupling  (5D origin: $G_{A5} = \lambda\phi B_A$)",
        fontsize=11,
    )
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 3. Radion – matter coupling
# ---------------------------------------------------------------------------

def draw_radion_coupling(
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Draw the radion φ – matter coupling vertex φ × T^μ_μ.

    The radion mass m_φ = √(2λ_GW) from Goldberger-Wise stabilisation is
    annotated on the propagator line.

    Parameters
    ----------
    output_path : str | Path | None
    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(6, 5))
    _clean_axes(ax)

    vx, vy = 0.5, 0.5
    _vertex_dot(ax, vx, vy)

    # Two matter lines
    _arrow_line(ax, 0.15, 0.2, vx, vy, label=r"$q$",
                label_offset=(-0.05, 0.04))
    _arrow_line(ax, vx, vy, 0.15, 0.8, label=r"$q$",
                label_offset=(-0.05, -0.04))

    # Radion (dashed scalar)
    _dashed_line(ax, vx, vy, 0.92, 0.5, color="purple",
                 label=r"$\phi$  (radion)", label_offset=(0.02, 0.08))

    # Mass annotation on propagator
    ax.text(0.82, 0.42,
            r"$m_\phi = \sqrt{2\lambda_{\rm GW}}$",
            fontsize=9, color="purple", ha="center")
    ax.text(0.60, 0.28,
            r"$g_\phi = \frac{1}{M_{\rm Pl}}\,T^\mu_\mu$",
            fontsize=10, ha="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="purple", alpha=0.15))
    ax.text(0.50, 0.10,
            fr"GW stabilisation: $R_c^* = {N_W}/{K_CS} \approx {R_C:.4f}\,M_{{Pl}}^{{-1}}$",
            fontsize=8.5, ha="center", color="gray", style="italic")

    ax.set_title(
        r"Radion $\phi$ – Matter Coupling" "\n"
        r"$\phi\,T^\mu_\mu / M_{\rm Pl}$  vertex  (Goldberger-Wise radion)",
        fontsize=11,
    )
    return _save_fig(fig, output_path)


# ---------------------------------------------------------------------------
# 4. Braided winding / CS birefringence vertex
# ---------------------------------------------------------------------------

def draw_braided_winding_vertex(
    output_path: Optional[str | Path] = None,
) -> plt.Figure:
    """Draw the axion–axion → graviton Chern-Simons scattering vertex.

    Illustrates the (5, 7, 74) braid triad that produces the CMB
    birefringence β ∈ {0.273°, 0.331°} prediction.

    Parameters
    ----------
    output_path : str | Path | None
    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    _clean_axes(ax)

    vx, vy = 0.5, 0.5
    _vertex_dot(ax, vx, vy, size=100, color="darkred")

    # Incoming axion a₁ (lower left)
    _dashed_line(ax, 0.12, 0.18, vx, vy, color="darkorange",
                 label=r"$a_1$  ($n_w=5$)", label_offset=(-0.08, 0.04))
    # Incoming axion a₂ (upper left)
    _dashed_line(ax, 0.12, 0.82, vx, vy, color="forestgreen",
                 label=r"$a_2$  ($n_w=7$)", label_offset=(-0.08, -0.04))
    # Outgoing graviton h (right)
    _wavy_line(ax, vx, vy, 0.92, 0.5, color="royalblue", n_waves=4,
               label=r"$h_{\mu\nu}$", label_offset=(0.02, 0.08))

    # CS insertion label
    ax.text(0.50, 0.62,
            fr"$\mathcal{{L}}_{{CS}} = \frac{{K_{{CS}}}}{{8\pi}}\,a\,R\,\tilde{{R}}$"
            fr"  ($K_{{CS}} = {N_W}^2 + 7^2 = {K_CS}$)",
            fontsize=10, ha="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="darkred", alpha=0.3))

    # Birefringence outcome
    ax.text(0.50, 0.10,
            r"$\Rightarrow$ CMB birefringence $\beta \in \{0.273°,\,0.331°\}$"
            "  (LiteBIRD ~2032)",
            fontsize=9, ha="center", color="darkred",
            bbox=dict(boxstyle="round,pad=0.2", fc="mistyrose", ec="darkred", alpha=0.4))

    ax.set_title(
        fr"Braided-Winding CS Vertex — $(n_w, n_7, K_{{CS}}) = ({N_W}, 7, {K_CS})$" "\n"
        r"Axion–Axion → Graviton  via  $K_{CS}\,a\,R\tilde{R}$",
        fontsize=11,
    )
    return _save_fig(fig, output_path)
