# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os — AxiomZero Operating System: Python Cognitive Layer

Sprint 2: 7-Manager × 5-Sub-Agent cognitive network running on top of the
AZ-KERNEL bare-metal layer.  On conventional OSes this runs as a daemon;
on AxiomZero bare metal it is the primary userspace process.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering: GitHub Copilot (AI).
"""
from __future__ import annotations

__version__ = "0.1.0"
__all__ = [
    "AgentCore",
    "HILS",
    "StateDB",
    "managers",
    "mcp",
]
