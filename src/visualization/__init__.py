# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/visualization
=================
Deterministic, mathematically accurate physics graphics for the Unitary Manifold.

All plots are produced with matplotlib from analytic formulae derived in the
framework — no AI image generator or external rendering service is used.
Every figure function:
  - accepts an optional ``output_path`` (str | Path | None);
  - saves an SVG when ``output_path`` is given;
  - returns the ``matplotlib.figure.Figure`` object for programmatic use.

Sub-modules
-----------
pillar_plots      CMB TT spectrum, birefringence β window, KK mass tower, r–nₛ plane
geometry_viz      5D metric slice, compactification-radius plot, winding-number diagram
feynman_diagrams  Kaluza-Klein and SM Feynman-style vertex diagrams
cmb_skymap        CMB angular power spectrum Cℓ with UM prediction vs Planck overlay
"""

__all__ = ["pillar_plots", "geometry_viz", "feynman_diagrams", "cmb_skymap"]
