#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# termux_boot_s24ultra.sh — Termux:Boot auto-start for Samsung Galaxy S24 Ultra
# =============================================================================
# Place at: ~/.termux/boot/start-gibberlink.sh
# Termux:Boot executes this on every device boot after the user unlocks.
#
# Differences from the BV9900 Pro boot script:
#  - --device-id S24ULTRA (not BV9900)
#  - No Sentinel Watchdog (that is BV9900-only per Android/docs/EXISTING_TECH.md)
#  - Ollama target model is llama3.2:8b (S24 Ultra has 12 GB RAM vs 8 GB)
#  - No IR / HR sensor on-device — nurse_suite.py uses Samsung Health bridge
# =============================================================================

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

log "=== Termux:Boot starting (S24 Ultra) ==="
log "PWD: $(pwd)"

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

# ── Load Gibberlink secret (required by UPB Hub) ──────────────────────────────
ENV_FILE="$DIARY_DIR/Gibberlink/.env"
if [[ -f "$ENV_FILE" ]]; then
    source "$ENV_FILE"
    export GIBBERLINK_SECRET
    log "GIBBERLINK_SECRET loaded from .env"
else
    log "WARNING: $ENV_FILE not found — run setup_android.sh first"
fi

# ── Start Gibberlink UPB Hub ──────────────────────────────────────────────────
UPB_SCRIPT="$DIARY_DIR/Gibberlink/scripts/upb_hub.py"
if [[ -f "$UPB_SCRIPT" ]]; then
    log "Starting UPB Hub (S24ULTRA)…"
    nohup "$PYTHON" "$UPB_SCRIPT" \
        --log-dir "$HOME_DIR/sessions" \
        --device-id S24ULTRA \
        >> "$HOME_DIR/upb_hub.log" 2>&1 &
    UPB_PID=$!
    log "UPB Hub PID: $UPB_PID"
else
    log "WARNING: UPB Hub script not found at $UPB_SCRIPT"
fi

# ── Ollama serve (optional) ───────────────────────────────────────────────────
# S24 Ultra has 12 GB RAM — can run llama3.2:8b comfortably (vs 3b on BV9900).
if command -v ollama &>/dev/null; then
    log "Starting Ollama serve…"
    nohup ollama serve >> "$HOME_DIR/ollama.log" 2>&1 &
    OLLAMA_PID=$!
    log "Ollama PID: $OLLAMA_PID"
    sleep 10
    # Pull 8B model if not already present (one-time download, ~5 GB)
    ollama list 2>/dev/null | grep -q "llama3.2:8b" || \
        (log "Pulling llama3.2:8b (one-time, ~5 GB)…"; ollama pull llama3.2:8b >> "$HOME_DIR/ollama.log" 2>&1) &
else
    log "Ollama not installed — skipping (install: pkg install ollama)"
fi

log "=== Termux:Boot startup complete (S24 Ultra) ==="
