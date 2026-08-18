#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# termux_boot.sh — GibberNode Termux:Boot auto-start script
# =============================================================================
# Place this file at:  ~/.termux/boot/start-gibberlink.sh
# Termux:Boot will execute it on every device boot (after the user unlocks).
#
# This script:
#  1. Acquires a wakelock (prevents CPU sleep while running)
#  2. Waits for the network to be available
#  3. Activates the diary virtualenv (if present) or uses system Python
#  4. Starts the UPB Hub background service
#  5. Starts the Sentinel Watchdog
#  6. Optionally starts the Ollama serve daemon (if ollama is installed)
#
# Logs are written to ~/termux_boot.log (rotated daily).
# =============================================================================

# Termux prefix
PREFIX="/data/data/com.termux/files/usr"
HOME_DIR="/data/data/com.termux/files/home"
DIARY_DIR="$HOME_DIR/diary"
LOG_FILE="$HOME_DIR/termux_boot.log"
DATE=$(date "+%Y-%m-%d %H:%M:%S")

log() {
    echo "[$DATE] $*" | tee -a "$LOG_FILE"
}

# ── Rotate log ────────────────────────────────────────────────────────────────
if [[ -f "$LOG_FILE" ]]; then
    LOG_SIZE=$(wc -c < "$LOG_FILE")
    if [[ "$LOG_SIZE" -gt 524288 ]]; then  # 512 KB
        mv "$LOG_FILE" "${LOG_FILE}.old"
    fi
fi

log "=== Termux:Boot starting ==="
log "PWD: $(pwd)"
log "PATH: $PATH"

# ── Wakelock ──────────────────────────────────────────────────────────────────
termux-wake-lock 2>/dev/null &
log "Wakelock acquired"

# ── Wait for network ─────────────────────────────────────────────────────────
MAX_WAIT=60
WAITED=0
while [[ $WAITED -lt $MAX_WAIT ]]; do
    if ping -c1 -W2 8.8.8.8 &>/dev/null 2>&1; then
        log "Network available"
        break
    fi
    sleep 5
    WAITED=$((WAITED + 5))
done
if [[ $WAITED -ge $MAX_WAIT ]]; then
    log "WARNING: Network not available after ${MAX_WAIT}s — continuing offline"
fi

# ── Ensure diary is up to date ────────────────────────────────────────────────
if [[ -d "$DIARY_DIR/.git" ]]; then
    log "Pulling latest diary repo…"
    (cd "$DIARY_DIR" && git pull --ff-only 2>&1 | head -5) >> "$LOG_FILE" 2>&1 || \
        log "git pull failed (offline or conflict) — using existing version"
else
    log "diary not cloned yet — skipping git pull"
fi

# ── Python / venv ─────────────────────────────────────────────────────────────
PYTHON="$PREFIX/bin/python3"
VENV_DIR="$HOME_DIR/diary_venv"

if [[ -f "$VENV_DIR/bin/python" ]]; then
    PYTHON="$VENV_DIR/bin/python"
    log "Using venv: $VENV_DIR"
else
    log "Using system Python: $PYTHON"
fi

export PYTHONPATH="$DIARY_DIR:$PYTHONPATH"

# ── Start Gibberlink UPB Hub ──────────────────────────────────────────────────
UPB_SCRIPT="$DIARY_DIR/Gibberlink/scripts/upb_hub.py"
if [[ -f "$UPB_SCRIPT" ]]; then
    log "Starting UPB Hub…"
    nohup "$PYTHON" "$UPB_SCRIPT" \
        --log-dir "$HOME_DIR/sessions" \
        --device-id BV9900 \
        >> "$HOME_DIR/upb_hub.log" 2>&1 &
    UPB_PID=$!
    log "UPB Hub PID: $UPB_PID"
else
    log "WARNING: UPB Hub script not found at $UPB_SCRIPT"
fi

# ── Start Sentinel Watchdog ───────────────────────────────────────────────────
SENTINEL_SCRIPT="$DIARY_DIR/Gibberlink/scripts/sentinel_watchdog.py"
if [[ -f "$SENTINEL_SCRIPT" ]]; then
    log "Starting Sentinel Watchdog…"
    nohup "$PYTHON" "$SENTINEL_SCRIPT" \
        --device BV9900 \
        --interval 300 \
        --log-dir "$HOME_DIR/sessions" \
        >> "$HOME_DIR/sentinel.log" 2>&1 &
    SENTINEL_PID=$!
    log "Sentinel PID: $SENTINEL_PID"
else
    log "WARNING: Sentinel script not found at $SENTINEL_SCRIPT"
fi

# ── Ollama serve (optional) ───────────────────────────────────────────────────
if command -v ollama &>/dev/null; then
    log "Starting Ollama serve (llama3.2:3b)…"
    nohup ollama serve >> "$HOME_DIR/ollama.log" 2>&1 &
    OLLAMA_PID=$!
    log "Ollama PID: $OLLAMA_PID"
    # Give Ollama 10 s to start, then pull model if not already present
    sleep 10
    ollama list 2>/dev/null | grep -q "llama3.2" || \
        (log "Pulling llama3.2:3b…"; ollama pull llama3.2:3b >> "$HOME_DIR/ollama.log" 2>&1) &
else
    log "Ollama not installed — skipping (run 'pkg install ollama' to enable)"
fi

log "=== Termux:Boot startup complete ==="
