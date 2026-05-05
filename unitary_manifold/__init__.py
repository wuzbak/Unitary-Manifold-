# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
unitary_manifold — namespace shim
==================================
Maps ``from unitary_manifold.X import Y`` to ``src/X.py`` (or ``src/X/__init__.py``).

After ``pip install -e .`` (or ``pip install .``) you can write::

    from unitary_manifold.core import metric, evolution
    from unitary_manifold.holography import boundary
    from unitary_manifold.multiverse import fixed_point

All sub-packages resolve directly to the ``src/`` directory in this
repository, so no source files need to be moved or duplicated.

DOI: https://doi.org/10.5281/zenodo.19584531
"""

from __future__ import annotations

import os as _os

__version__ = "9.33.0"
__author__ = "ThomasCory Walker-Pearson"
__license__ = "AGPL-3.0-or-later"

# ---------------------------------------------------------------------------
# Namespace redirect: point this package's search path at src/ so that
# sub-package imports like `unitary_manifold.core` resolve to `src/core/`.
# This works for both editable (`pip install -e .`) and regular installs
# provided src/ is on the filesystem at the expected relative location.
# ---------------------------------------------------------------------------
_src_dir = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), "..", "src"))
__path__ = [_src_dir]
