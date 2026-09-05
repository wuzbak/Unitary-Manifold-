#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Compatibility entry point for the canonical conditional model checks."""

from proof.VERIFY import run_verify


if __name__ == "__main__":
    raise SystemExit(run_verify())
