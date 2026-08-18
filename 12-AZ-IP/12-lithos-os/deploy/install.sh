#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && cd .. && pwd)"
echo "[LithosOS] Installer"
PYTHON=""
for cmd in python3 python; do
    if command -v $cmd &>/dev/null; then
        PYTHON=$cmd
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "Python not found. Please install Python 3.9+"
    exit 1
fi
echo "Using: $($PYTHON --version)"
cd "$REPO_ROOT"
exec "$PYTHON" "$SCRIPT_DIR/install.py" "$@"
