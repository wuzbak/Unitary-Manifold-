#!/usr/bin/env bash
# =============================================================================
# install_s24ultra.sh — Unitary Pentacorder installer for Samsung Galaxy S24 Ultra
# =============================================================================
# Runs on the LAPTOP/PC side over USB ADB.
# The phone must have USB Debugging enabled.
#
# Usage:
#   chmod +x install_s24ultra.sh
#   ./install_s24ultra.sh                   # auto-downloads latest APK from GitHub
#   ./install_s24ultra.sh --apk /path/to/GibberNode.apk  # use a local APK
#
# Auto-download URL (requires curl and internet access):
#   https://github.com/wuzbak/diary/releases/download/android-latest/gibbernode-s24ultra.apk
#
# To UNINSTALL everything cleanly, run:
#   ./uninstall_s24ultra.sh
#
# All ADB commands are non-destructive and fully reversible.
# Nothing is written to /system. Bootloader is untouched. Knox is intact.
# =============================================================================

set -euo pipefail

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; RST='\033[0m'

info()  { echo -e "${CYN}[INFO]${RST}  $*"; }
ok()    { echo -e "${GRN}[ OK ]${RST}  $*"; }
warn()  { echo -e "${YLW}[WARN]${RST}  $*"; }
fail()  { echo -e "${RED}[FAIL]${RST}  $*"; exit 1; }
step()  { echo; echo -e "${YLW}════ $* ════${RST}"; }

# ── Constants ─────────────────────────────────────────────────────────────────
RELEASE_APK_URL="https://github.com/wuzbak/Private/releases/download/android-latest/pentacorder-s24ultra.apk"
RELEASE_APK_NAME="pentacorder-s24ultra.apk"

# ── Args ──────────────────────────────────────────────────────────────────────
APK_PATH=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --apk) APK_PATH="$2"; shift 2 ;;
        *) warn "Unknown argument: $1"; shift ;;
    esac
done

# ── Dependency check ──────────────────────────────────────────────────────────
step "Dependency check"
if ! command -v adb &>/dev/null; then
    fail "adb not found. Install Android Platform Tools:\n  macOS: brew install android-platform-tools\n  Linux: sudo apt install adb\n  Win:   https://developer.android.com/studio/releases/platform-tools"
fi
ok "adb found: $(adb version | head -1)"

# ── Step 0 — Pre-flight ───────────────────────────────────────────────────────
step "Step 0 — Pre-flight: detect S24 Ultra"

adb kill-server &>/dev/null || true
adb start-server &>/dev/null

DEVICE_LIST=$(adb devices 2>/dev/null | tail -n +2 | grep -v "^$" || true)
if [[ -z "$DEVICE_LIST" ]]; then
    echo
    warn "No device detected. To enable USB Debugging on the S24 Ultra:"
    echo "  1. Settings → About Phone → Software Information"
    echo "  2. Tap 'Build Number' exactly 7 times  (you are now a developer)"
    echo "  3. Settings → Developer Options → USB Debugging: ON"
    echo "  4. Connect the phone via USB-C cable"
    echo "  5. Unlock the phone and tap 'Allow' on the ADB authorisation dialog"
    echo "  6. Re-run this script"
    fail "No device connected"
fi

SERIAL=$(adb devices 2>/dev/null | tail -n +2 | grep -v "^$" | awk '{print $1}' | head -1)
ADB="adb -s $SERIAL"
info "Using device: $SERIAL"

ANDROID_VER=$($ADB shell getprop ro.build.version.release 2>/dev/null | tr -d '\r')
MODEL=$($ADB shell getprop ro.product.model 2>/dev/null | tr -d '\r')
info "Device: $MODEL  Android: $ANDROID_VER"

# Battery check
BAT_PCT=$($ADB shell dumpsys battery 2>/dev/null | grep "level:" | awk '{print $2}' | tr -d '\r' || echo "0")
if [[ "$BAT_PCT" =~ ^[0-9]+$ ]] && [[ "$BAT_PCT" -lt 20 ]]; then
    warn "Battery is at ${BAT_PCT}%. Charge to at least 20% before installing."
    read -r -p "Continue anyway? [y/N] " REPLY
    [[ "$REPLY" =~ ^[Yy]$ ]] || fail "Aborted: low battery"
fi
ok "Battery: ${BAT_PCT}%"

# Storage check (require 3 GB free — S24 Ultra stores everything in internal)
FREE_KB=$($ADB shell df /data 2>/dev/null | tail -1 | awk '{print $4}' | tr -d '\r' || echo "0")
FREE_MB=$(( ${FREE_KB:-0} / 1024 ))
if [[ "$FREE_MB" -lt 3072 ]]; then
    warn "Only ${FREE_MB} MB free on /data. Recommended: ≥ 3072 MB."
fi
ok "Free storage: ${FREE_MB} MB"

# ── Step 1 — Enable sideloading ───────────────────────────────────────────────
step "Step 1 — Enable APK sideloading"

# These settings allow the phone UI to install APKs from unknown sources.
# adb install works regardless, but this prepares the device for manual installs too.
$ADB shell "settings put global install_non_market_apps 1" 2>/dev/null || true
$ADB shell "settings put secure install_non_market_apps 1" 2>/dev/null || true
ok "Sideloading enabled"

# ── Step 2 — Disable Samsung / Google bloatware (reversible) ─────────────────
step "Step 2 — Disable Samsung / Google bloatware (reversible)"

# Re-enable anything here with: adb shell pm enable --user 0 <package>
BLOATWARE=(
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

for pkg in "${BLOATWARE[@]}"; do
    result=$($ADB shell "pm disable-user --user 0 $pkg 2>/dev/null" || true)
    if echo "$result" | grep -qi "disabled"; then
        info "  Disabled: $pkg"
    fi
done
ok "Bloatware disabled (reversible — see uninstall_s24ultra.sh)"

# ── Step 3 — Battery optimisation exemption ───────────────────────────────────
step "Step 3 — Exempt Termux from battery optimisation"

$ADB shell "dumpsys deviceidle whitelist +com.termux 2>/dev/null || true"
$ADB shell "settings put global background_process_limit 4 2>/dev/null || true"
$ADB shell "settings put global app_standby_enabled 0 2>/dev/null || true"
ok "Battery optimisation exemption applied"

# ── Step 4 — Install Termux ───────────────────────────────────────────────────
step "Step 4 — Install Termux, Termux:Boot, Termux:API"

TERMUX_VERSION="0.118.0"
TERMUX_URL="https://f-droid.org/repo/com.termux_${TERMUX_VERSION//./_}.apk"
TERMUX_BOOT_URL="https://f-droid.org/repo/com.termux.boot_7.apk"
TERMUX_API_URL="https://f-droid.org/repo/com.termux.api_51.apk"

TMP_DIR="$(mktemp -d)"
trap "rm -rf $TMP_DIR" EXIT

install_if_missing() {
    local pkg="$1" url="$2" fname="$3"
    if $ADB shell pm list packages 2>/dev/null | grep -q "$pkg"; then
        ok "$pkg already installed"
    else
        info "Downloading $fname …"
        if curl -fsSL -o "$TMP_DIR/$fname" "$url" 2>/dev/null; then
            $ADB install -r "$TMP_DIR/$fname" && ok "$pkg installed" || warn "$pkg install failed (check F-Droid URL)"
        else
            warn "Download failed for $fname — install manually from F-Droid:"
            echo "  https://f-droid.org/packages/$pkg/"
        fi
    fi
}

install_if_missing "com.termux"      "$TERMUX_URL"      "termux.apk"
install_if_missing "com.termux.boot" "$TERMUX_BOOT_URL" "termux_boot.apk"
install_if_missing "com.termux.api"  "$TERMUX_API_URL"  "termux_api.apk"

# ── Step 5 — Bootstrap Termux Python environment ──────────────────────────────
step "Step 5 — Bootstrap Termux Python / ggwave / diary (via setup_android.sh)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Push the existing setup_android.sh to internal storage and run it in Termux.
# setup_android.sh handles: pkg update, Python deps, git clone, secret gen, verify.
SETUP_SCRIPT="$SCRIPT_DIR/setup_android.sh"
if [[ -f "$SETUP_SCRIPT" ]]; then
    $ADB push "$SETUP_SCRIPT" /sdcard/setup_android.sh
    $ADB shell "chmod +x /sdcard/setup_android.sh 2>/dev/null || true"
    info "setup_android.sh pushed to /sdcard/setup_android.sh"

    info "Opening Termux and running setup_android.sh (takes 2–5 minutes — watch the screen)…"
    $ADB shell "am start -n com.termux/.HomeActivity 2>/dev/null || true"
    sleep 3
    $ADB shell "input text 'bash /sdcard/setup_android.sh'" 2>/dev/null && \
        $ADB shell "input keyevent 66" 2>/dev/null || \
        warn "Could not send text to Termux automatically."
    info "Waiting 60 s for bootstrap to start (watch the phone screen)…"
    sleep 60
else
    warn "setup_android.sh not found at $SETUP_SCRIPT — sending inline bootstrap instead."
    $ADB shell "am start -n com.termux/.HomeActivity 2>/dev/null || true"
    sleep 3
    BOOTSTRAP_CMD='pkg update -y && pkg upgrade -y && pkg install -y python python-pip portaudio libzmq git curl wget && pip install ggwave numpy pyaudio requests && git clone https://github.com/wuzbak/diary.git ~/diary && echo BOOTSTRAP_OK'
    $ADB shell "input text '${BOOTSTRAP_CMD}'" 2>/dev/null && \
        $ADB shell "input keyevent 66" 2>/dev/null || \
        warn "Run this manually in Termux:\n  $BOOTSTRAP_CMD"
fi

info "NOTE: After bootstrap, open Termux and run:"
info "  python ~/diary/Gibberlink/scripts/noise_calibrate.py --sweep --play"
info "  The S24 Ultra has Dolby Atmos processing that may affect ggwave FSK."
info "  Calibration identifies your device's safe_ceiling_hz before first use."

# ── Step 6 — Install GibberNode APK ──────────────────────────────────────────
step "Step 6 — Install Unitary Pentacorder APK"

if [[ -z "$APK_PATH" ]]; then
    # Auto-download the latest release APK from GitHub
    if command -v curl &>/dev/null; then
        info "No --apk provided — downloading latest release from GitHub…"
        info "  $RELEASE_APK_URL"
        DOWNLOAD_PATH="$TMP_DIR/$RELEASE_APK_NAME"
        if curl -fL --progress-bar -o "$DOWNLOAD_PATH" "$RELEASE_APK_URL" 2>/dev/null; then
            ok "Downloaded $RELEASE_APK_NAME ($(du -h "$DOWNLOAD_PATH" | cut -f1))"
            APK_PATH="$DOWNLOAD_PATH"
        else
            warn "Auto-download failed. Possible reasons:"
            warn "  • No internet access"
            warn "  • No release published yet (CI hasn't run or build failed)"
            warn "  Build the APK manually and re-run with --apk:"
            warn "    cd Android && ./gradlew assembleDebug"
            warn "    ./install_s24ultra.sh --apk Android/app/build/outputs/apk/debug/app-debug.apk"
        fi
    else
        warn "curl not found — cannot auto-download APK."
        warn "Install curl or provide the APK manually with --apk."
    fi
fi

if [[ -n "$APK_PATH" && -f "$APK_PATH" ]]; then
    $ADB install -r "$APK_PATH" && ok "Unitary Pentacorder.apk installed" || warn "APK install failed"

    PERMISSIONS=(
        "android.permission.RECORD_AUDIO"
        "android.permission.ACCESS_FINE_LOCATION"
        "android.permission.ACCESS_COARSE_LOCATION"
    )
    for perm in "${PERMISSIONS[@]}"; do
        $ADB shell "pm grant com.axiomzero.pentacorder $perm 2>/dev/null || true" && ok "  Granted: $perm"
    done
else
    warn "APK not available — skipping GibberNode installation."
    info "Build the APK first: cd Android && ./gradlew assembleDebug"
    info "Debug APK path: Android/app/build/outputs/apk/debug/app-debug.apk"
    info "Re-run: ./install_s24ultra.sh --apk <path>"
fi

# ── Step 7 — Configure Termux:Boot auto-start ─────────────────────────────────
step "Step 7 — Configure Termux:Boot auto-start"

# Use the S24 Ultra-specific boot script (no BV9900 sentinel, S24ULTRA device-id)
BOOT_SCRIPT="$SCRIPT_DIR/termux_boot_s24ultra.sh"
if [[ ! -f "$BOOT_SCRIPT" ]]; then
    BOOT_SCRIPT="$SCRIPT_DIR/termux_boot.sh"  # fallback
fi

if [[ -f "$BOOT_SCRIPT" ]]; then
    $ADB push "$BOOT_SCRIPT" /sdcard/start-gibberlink.sh
    $ADB shell "mkdir -p ~/.termux/boot && cp /sdcard/start-gibberlink.sh ~/.termux/boot/ && chmod +x ~/.termux/boot/start-gibberlink.sh"
    ok "Termux:Boot auto-start configured ($(basename $BOOT_SCRIPT))"
else
    warn "No boot script found — skipping Termux:Boot setup"
fi

# ── Step 8 — Push project content to internal storage ────────────────────────
# Note: S24 Ultra has no microSD slot — /sdcard maps to internal storage.
step "Step 8 — Push project content to internal storage (/sdcard)"

REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [[ -d "$REPO_ROOT/Unitary-Manifold" ]]; then
    info "Pushing Unitary-Manifold → /sdcard/manifold/ …"
    $ADB shell "mkdir -p /sdcard/manifold"
    $ADB push "$REPO_ROOT/Unitary-Manifold/" /sdcard/manifold/ 2>/dev/null && ok "Manifold pushed" || warn "Manifold push failed (large directory — push manually if needed)"
fi

if [[ -d "$REPO_ROOT/Gibberlink" ]]; then
    info "Pushing Gibberlink → /sdcard/gibberlink/ …"
    $ADB shell "mkdir -p /sdcard/gibberlink"
    $ADB push "$REPO_ROOT/Gibberlink/" /sdcard/gibberlink/ 2>/dev/null && ok "Gibberlink pushed" || warn "Gibberlink push failed"
fi

# ── Step 9 — Verify ──────────────────────────────────────────────────────────
step "Step 9 — Verify installation"

echo
if $ADB shell pm list packages 2>/dev/null | grep -q com.termux; then
    ok "Termux: installed"
else
    warn "Termux: NOT found"
fi

if $ADB shell pm list packages 2>/dev/null | grep -q com.axiomzero.pentacorder; then
    ok "Unitary Pentacorder: installed"
    info "Launching Unitary Pentacorder…"
    $ADB shell "am start -n com.axiomzero.pentacorder/.MainActivity" 2>/dev/null || true
else
    warn "Unitary Pentacorder: NOT installed (build the APK and run with --apk flag)"
fi

echo
echo -e "${GRN}════════════════════════════════════════════════════════${RST}"
echo -e "${GRN}  Installation complete.${RST}"
echo -e "${GRN}  Next steps:${RST}"
echo    "    1. Open Termux and run: source ~/diary/Gibberlink/.env"
echo    "    2. Open Unitary Pentacorder → complete Calibration Wizard → tap the ✨ FAB for the Assistant"
echo    "    3. Reboot the phone to verify Termux:Boot auto-start"
echo -e "${GRN}  If something goes wrong, run:${RST}"
echo    "    ./uninstall_s24ultra.sh   (full clean exit)"
echo -e "${GRN}  Re-enable any disabled package:${RST}"
echo    "    adb shell pm enable --user 0 <package.name>"
echo -e "${GRN}════════════════════════════════════════════════════════${RST}"
