#!/usr/bin/env bash
# =============================================================================
# uninstall_s24ultra.sh — GibberNode clean exit / full uninstall for S24 Ultra
# =============================================================================
# Runs on the LAPTOP/PC side over USB ADB.
#
# Usage:
#   chmod +x uninstall_s24ultra.sh
#   ./uninstall_s24ultra.sh [--keep-termux] [--keep-data]
#
# Options:
#   --keep-termux   Do NOT uninstall Termux / Termux:Boot / Termux:API
#   --keep-data     Do NOT wipe /sdcard/manifold or /sdcard/gibberlink
#
# What this script does:
#   1. Uninstalls GibberNode (com.axiomzero.pentacorder)
#   2. Removes the Termux:Boot auto-start script
#   3. Re-enables all Samsung packages that were disabled during install
#   4. Resets the settings changed during install
#   5. (Optional) Uninstalls Termux and its companions
#   6. (Optional) Removes pushed data from internal storage
#
# Everything is reversible by running install_s24ultra.sh again.
# =============================================================================

set -euo pipefail

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; RST='\033[0m'

info()  { echo -e "${CYN}[INFO]${RST}  $*"; }
ok()    { echo -e "${GRN}[ OK ]${RST}  $*"; }
warn()  { echo -e "${YLW}[WARN]${RST}  $*"; }
fail()  { echo -e "${RED}[FAIL]${RST}  $*"; exit 1; }
step()  { echo; echo -e "${YLW}════ $* ════${RST}"; }

# ── Args ──────────────────────────────────────────────────────────────────────
KEEP_TERMUX=false
KEEP_DATA=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --keep-termux) KEEP_TERMUX=true; shift ;;
        --keep-data)   KEEP_DATA=true;   shift ;;
        *) warn "Unknown argument: $1"; shift ;;
    esac
done

# ── Dependency check ──────────────────────────────────────────────────────────
step "Dependency check"
if ! command -v adb &>/dev/null; then
    fail "adb not found. Install Android Platform Tools and add to PATH."
fi
ok "adb found: $(adb version | head -1)"

# ── Detect device ─────────────────────────────────────────────────────────────
step "Detect S24 Ultra"

adb kill-server &>/dev/null || true
adb start-server &>/dev/null

DEVICE_LIST=$(adb devices 2>/dev/null | tail -n +2 | grep -v "^$" || true)
if [[ -z "$DEVICE_LIST" ]]; then
    warn "No device detected. Connect the S24 Ultra via USB with USB Debugging enabled."
    fail "No device connected"
fi

SERIAL=$(adb devices 2>/dev/null | tail -n +2 | grep -v "^$" | awk '{print $1}' | head -1)
ADB="adb -s $SERIAL"
info "Using device: $SERIAL"

MODEL=$($ADB shell getprop ro.product.model 2>/dev/null | tr -d '\r')
info "Device: $MODEL"

# Confirm before destructive steps
echo
echo -e "${YLW}This will remove GibberNode and undo all changes made by install_s24ultra.sh${RST}"
echo    "Device: $MODEL  Serial: $SERIAL"
echo    "Keep Termux: $KEEP_TERMUX"
echo    "Keep /sdcard data: $KEEP_DATA"
echo
read -r -p "Proceed? [y/N] " REPLY
[[ "$REPLY" =~ ^[Yy]$ ]] || fail "Aborted"

# ── Step 1 — Stop running GibberNode services ─────────────────────────────────
step "Step 1 — Stop GibberNode services"

$ADB shell "am force-stop com.axiomzero.pentacorder 2>/dev/null || true"
ok "GibberNode stopped"

# ── Step 2 — Remove Termux:Boot auto-start script ────────────────────────────
step "Step 2 — Remove Termux:Boot auto-start script"

$ADB shell "rm -f ~/.termux/boot/start-gibberlink.sh 2>/dev/null || true"
$ADB shell "rm -f /sdcard/start-gibberlink.sh 2>/dev/null || true"
ok "Termux:Boot auto-start script removed"

# ── Step 3 — Uninstall GibberNode APK ────────────────────────────────────────
step "Step 3 — Uninstall GibberNode"

if $ADB shell pm list packages 2>/dev/null | grep -q com.axiomzero.pentacorder; then
    $ADB uninstall com.axiomzero.pentacorder && ok "GibberNode uninstalled" || warn "GibberNode uninstall failed"
else
    ok "GibberNode not installed — nothing to remove"
fi

# ── Step 4 — Re-enable Samsung / Google packages ─────────────────────────────
step "Step 4 — Re-enable Samsung / Google packages"

REENABLE=(
    "com.samsung.android.bixby.agent"
    "com.samsung.android.app.spage"
    "com.samsung.android.bixbyvision.framework"
    "com.samsung.android.game.gamehome"
    "com.microsoft.skydrive"
    "com.facebook.appmanager"
    "com.facebook.services"
    "com.google.android.videos"
    "com.google.android.apps.tachyon"
)

for pkg in "${REENABLE[@]}"; do
    result=$($ADB shell "pm enable --user 0 $pkg 2>/dev/null" || true)
    if echo "$result" | grep -qi "enabled"; then
        info "  Re-enabled: $pkg"
    fi
done
ok "Samsung / Google packages restored"

# ── Step 5 — Reset settings ───────────────────────────────────────────────────
step "Step 5 — Reset install settings"

$ADB shell "settings put global install_non_market_apps 0" 2>/dev/null || true
$ADB shell "settings put secure install_non_market_apps 0" 2>/dev/null || true
$ADB shell "settings delete global background_process_limit" 2>/dev/null || true
$ADB shell "settings delete global app_standby_enabled" 2>/dev/null || true

# Remove Termux from device idle whitelist
$ADB shell "dumpsys deviceidle whitelist -com.termux 2>/dev/null || true"
ok "Settings reset"

# ── Step 6 — Uninstall Termux (optional) ─────────────────────────────────────
step "Step 6 — Uninstall Termux (optional)"

if [[ "$KEEP_TERMUX" == true ]]; then
    ok "Skipping Termux removal (--keep-termux)"
else
    for pkg in com.termux.boot com.termux.api com.termux; do
        if $ADB shell pm list packages 2>/dev/null | grep -q "$pkg"; then
            $ADB uninstall "$pkg" 2>/dev/null && info "  Uninstalled: $pkg" || warn "  Could not uninstall: $pkg"
        fi
    done
    ok "Termux removed (reinstall from F-Droid if needed)"
fi

# ── Step 7 — Remove pushed data from internal storage (optional) ─────────────
step "Step 7 — Remove pushed data from internal storage"

if [[ "$KEEP_DATA" == true ]]; then
    ok "Skipping /sdcard data removal (--keep-data)"
else
    $ADB shell "rm -rf /sdcard/manifold 2>/dev/null || true"
    $ADB shell "rm -rf /sdcard/gibberlink 2>/dev/null || true"
    ok "Removed /sdcard/manifold and /sdcard/gibberlink"
    info "(The repo itself on the phone at ~/diary is inside Termux — it was removed with Termux above)"
fi

# ── Step 8 — Final summary ────────────────────────────────────────────────────
echo
echo -e "${GRN}════════════════════════════════════════════════════════${RST}"
echo -e "${GRN}  Clean exit complete.${RST}"
echo    "  GibberNode: REMOVED"
echo    "  Termux:Boot script: REMOVED"
if [[ "$KEEP_TERMUX" == false ]]; then
    echo    "  Termux: REMOVED"
else
    echo    "  Termux: kept (--keep-termux)"
fi
if [[ "$KEEP_DATA" == false ]]; then
    echo    "  /sdcard data: REMOVED"
else
    echo    "  /sdcard data: kept (--keep-data)"
fi
echo -e "${GRN}  To reinstall, run:${RST}"
echo    "    ./install_s24ultra.sh --apk path/to/GibberNode.apk"
echo -e "${GRN}════════════════════════════════════════════════════════${RST}"
