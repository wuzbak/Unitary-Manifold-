# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
Shared infrastructure contracts for governed execution and integration surfaces.
"""

from .execution_spine import (
    EXECUTION_SPINE_SCHEMA_VERSION,
    ExecutionSpineHealthCheck,
    ExecutionSpineRecord,
    build_fail_closed_governance,
)

__all__ = [
    "EXECUTION_SPINE_SCHEMA_VERSION",
    "ExecutionSpineHealthCheck",
    "ExecutionSpineRecord",
    "build_fail_closed_governance",
]
