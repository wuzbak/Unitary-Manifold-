#!/usr/bin/env bash
# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
#
# axiomzero.sh — Shell wrapper for the AxiomZero bootstrap.
# Usage: bash axiomzero.sh [--mode=full|thin-client|cpu-only] [options]
#
# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture: GitHub Copilot (AI).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          AxiomZero — The Uncompactification Event        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  Repository root: $REPO_ROOT"
echo "  AxiomZero dir:   $SCRIPT_DIR"
echo ""

# Detect Python
PYTHON=""
for candidate in python3 python python3.12 python3.11 python3.10; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" -c "import sys; print(sys.version_info[:2])" 2>/dev/null || true)
        # crude check: must be (3, 10) or higher
        major=$("$candidate" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo "0")
        minor=$("$candidate" -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo "0")
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON="$candidate"
            echo "  ✔  Found $PYTHON ($major.$minor)"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "  ✗  Python 3.10+ not found."
    echo "     Install via: sudo apt install python3.11  OR  brew install python@3.11"
    exit 1
fi

# Forward all arguments to the Python bootstrap
exec "$PYTHON" "$SCRIPT_DIR/axiomzero_bootstrap.py" \
    --repo-root="$REPO_ROOT" \
    "$@"
