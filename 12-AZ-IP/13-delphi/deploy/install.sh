#!/usr/bin/env bash
# DelPhi install script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Installing DelPhi dependencies…"
pip install -r "$SCRIPT_DIR/requirements.txt"

echo "Seeding database…"
cd "$REPO_ROOT"
python -c "from delphi.app.db.seed import seed_database; seed_database()"

echo "DelPhi ready. Start with:"
echo "  uvicorn delphi.app.main:app --host 0.0.0.0 --port 7863"
