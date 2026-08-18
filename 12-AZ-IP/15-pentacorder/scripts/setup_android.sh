#!/usr/bin/env bash
# setup_android.sh — Bootstrap the Gibberlink/UPB stack in Termux
# Run this script inside Termux on any Android device.
# Usage: bash setup_android.sh

set -euo pipefail

echo "=== Gibberlink/UPB Android Setup ==="
echo "Device: $(uname -m)"
echo ""

# 1. Update package index
echo "[1/7] Updating package index..."
pkg update -y && pkg upgrade -y

# 2. Install system dependencies
echo "[2/7] Installing system packages..."
pkg install -y python python-pip portaudio libzmq git curl wget

# 3. Install Python dependencies
echo "[3/7] Installing Python packages..."
pip install --upgrade pip
pip install ggwave numpy pyaudio requests

# 4. Clone or pull the repo
REPO_DIR="$HOME/diary"
if [ -d "$REPO_DIR/.git" ]; then
    echo "[4/7] Pulling latest repo..."
    git -C "$REPO_DIR" pull
else
    echo "[4/7] Cloning repo..."
    git clone https://github.com/wuzbak/diary.git "$REPO_DIR"
fi

# 5. Create experiments directory
echo "[5/7] Creating experiments directory..."
mkdir -p "$REPO_DIR/Gibberlink/experiments"

# 6. Generate a new Gibberlink secret if not present
ENV_FILE="$REPO_DIR/Gibberlink/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "[6/7] Generating new GIBBERLINK_SECRET..."
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "GIBBERLINK_SECRET=$SECRET" > "$ENV_FILE"
    echo "  Saved to $ENV_FILE"
    echo "  NOTE: Share this secret (out-of-band) with all peer devices."
else
    echo "[6/7] Existing .env found — skipping secret generation."
fi

# 7. Verify ggwave import
echo "[7/7] Verifying ggwave installation..."
python3 -c "import ggwave; print('ggwave OK, version:', ggwave.__version__)" || {
    echo "ERROR: ggwave import failed."
    exit 1
}

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  export GIBBERLINK_SECRET=\$(grep GIBBERLINK_SECRET $ENV_FILE | cut -d= -f2)"
echo "  cd $REPO_DIR/Gibberlink"
echo "  python scripts/noise_calibrate.py --sweep --play   # calibrate your device"
echo "  python scripts/encode_message.py 'Hello' --mode green --auth --play"
echo "  python scripts/upb_hub.py relay                    # start the full hub"
