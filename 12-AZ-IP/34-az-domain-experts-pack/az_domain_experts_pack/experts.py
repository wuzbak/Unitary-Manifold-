# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pre-configured domain experts — the fourth and fifth siblings in the
Terra OS / Lithos OS / PsiCat retrieval pattern, per article-354 direction
#7: a materials-science expert over `src/materials/`, and an
atomic-spectroscopy expert over `src/atomic_structure/`.
"""

from __future__ import annotations

from ._repo import ensure_repo_on_path
from .retrieval import DomainExpert

_REPO_ROOT = ensure_repo_on_path()

MATERIALS_EXPERT = DomainExpert("materials-science", _REPO_ROOT / "src" / "materials")
SPECTROSCOPY_EXPERT = DomainExpert("atomic-spectroscopy", _REPO_ROOT / "src" / "atomic_structure")
