# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Verdict schema for Product 19."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VerdictResult:
    exp_id: str
    name: str
    verdict: str
    prediction: str
    measured: Any
    sigma_deviation: float | None
    kill_condition: str
    pillar_refs: tuple[int, ...]
    note: str
