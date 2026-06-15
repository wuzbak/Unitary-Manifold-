# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""az-os/managers/__init__.py — Manager package."""
from .m1_geometry import M1GeometryManager
from .m2_fields import M2FieldManager
from .m3_symbolic import M3SymbolicManager
from .m4_test_guard import M4TestGuard
from .m5_corpus import M5CorpusManager
from .m6_research import M6ResearchManager
from .m7_interface import M7InterfaceManager

__all__ = [
    "M1GeometryManager",
    "M2FieldManager",
    "M3SymbolicManager",
    "M4TestGuard",
    "M5CorpusManager",
    "M6ResearchManager",
    "M7InterfaceManager",
]
