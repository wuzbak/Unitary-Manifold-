#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
set -euo pipefail
ROOT="/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/01-axiom-os"
cd "$ROOT"
python3 -m pip install -r "$ROOT/requirements.txt"
python3 "$ROOT/axiomzero_bootstrap.py" --help >/dev/null || true
echo "Axiom OS dependencies installed. Start with: python3 -m uvicorn AxiomZero.api.server:app --host 0.0.0.0 --port 8000"
