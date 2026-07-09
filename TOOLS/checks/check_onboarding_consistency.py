#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pre-merge CI check: onboarding docs must contain the canonical test count.

Exits 0 if all onboarding documents contain the canonical passed count from
STATUS.md; exits 1 with GitHub Actions annotation errors otherwise.

Called from .github/workflows/staleness-honesty-gate.yml whenever STATUS.md
is in the PR's changed file set.
"""

from __future__ import annotations

import sys
import os

# Allow running from repo root without installing the package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.canonical_ledger_consistency import onboarding_docs_consistency_report

report = onboarding_docs_consistency_report()

if report["canonical"] is None:
    print("::error::Could not extract canonical passed count from STATUS.md.")
    sys.exit(1)

canonical_count = report["canonical"]["passed"]

if not report["all_pass"]:
    drifted = report["drifted_docs"]
    print(
        f"::error::Onboarding docs do not contain the canonical count "
        f"({canonical_count:,} passed). Drifted: {drifted}"
    )
    print(
        "::error::Update each drifted doc to include the canonical count and re-push."
    )
    sys.exit(1)

print(f"OK: all onboarding docs consistent: {canonical_count:,} passed")
sys.exit(0)
