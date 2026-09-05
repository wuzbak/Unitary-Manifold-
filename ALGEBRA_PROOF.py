# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Compatibility entry point; canonical selected algebra lives under proof/."""

from proof.ALGEBRA_PROOF import _exit_code


if __name__ == "__main__":
    raise SystemExit(_exit_code)
