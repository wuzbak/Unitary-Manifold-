# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
12-AZ-IP/lib/az_ip_common/__init__.py
=======================================
Shared library for all AZ-IP apps, engines, and calculators.

Provides:
  - AuthenticatedHTTPClient   — httpx client with JWT bearer + retry
  - StructuredLogger          — structlog JSON-line logger factory
  - AZIPConfig                — pydantic-settings config loader
  - pentad_classify()         — classify a task with the Pentad governance lane
  - Engine                    — base class for all AZ-IP engines

Theory: ThomasCory Walker-Pearson.  Code: GitHub Copilot (AI).
"""
from az_ip_common.client import AuthenticatedHTTPClient
from az_ip_common.config import AZIPConfig
from az_ip_common.engine import Engine, EngineResult
from az_ip_common.logger import get_logger
from az_ip_common.pentad import pentad_classify

__all__ = [
    "AuthenticatedHTTPClient",
    "AZIPConfig",
    "Engine",
    "EngineResult",
    "get_logger",
    "pentad_classify",
]
