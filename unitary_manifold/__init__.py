# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
unitary_manifold — namespace shim
==================================
Maps ``from unitary_manifold.X import Y`` to ``src/X.py`` (or ``src/X/__init__.py``).

After ``pip install -e .`` (or ``pip install .``) you can write::

    from unitary_manifold.core import metric, evolution
    from unitary_manifold.holography import boundary
    from unitary_manifold.multiverse import fixed_point

All sub-packages resolve directly to the sibling ``src/`` package, shipped
in wheels as well as available in the checkout. No source files need to be
moved or duplicated.

DOI: https://doi.org/10.5281/zenodo.19584531
"""

from __future__ import annotations

import os as _os

__version__ = "11.12.0"
__author__ = "ThomasCory Walker-Pearson"
__license__ = "AGPL-3.0-or-later"

# ---------------------------------------------------------------------------
# Namespace redirect: point this package's search path at src/ so that
# sub-package imports like `unitary_manifold.core` resolve to `src/core/`.
# Package discovery ships src/ at this same relative location in wheels.
# ---------------------------------------------------------------------------
_src_dir = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), "..", "src"))
__path__.append(_src_dir)
