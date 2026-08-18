#!/usr/bin/env bash
# =============================================================================
# install_bv9900.sh — GibberNode installer for Blackview BV9900 Pro
# =============================================================================
# Runs on the LAPTOP/PC side over USB ADB.
# The phone must already have USB Debugging enabled.
#
# Usage:
#   chmod +x install_bv9900.sh
#   ./install_bv9900.sh [--apk path/to/GibberNode.apk]
#
# All ADB commands are non-destructive and fully reversible.
# Nothing is written to /system. Bootloader is untouched.
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
step "Step 0 — Pre-flight: detect BV9900 Pro"

# Restart ADB server to clear stale state
adb kill-server &>/dev/null || true
adb start-server &>/dev/null

DEVICE_LIST=$(adb devices 2>/dev/null | tail -n +2 | grep -v "^$" || true)
if [[ -z "$DEVICE_LIST" ]]; then
    echo
    warn "No device detected. Please:"
    echo "  1. Connect the BV9900 Pro via USB"
    echo "  2. Settings → About Phone → Software Information"
    echo "  3. Tap 'Build Number' exactly 7 times"
    echo "  4. Settings → Developer Options → USB Debugging: ON"
    echo "  5. Unlock the phone and accept the ADB authorisation prompt"
    echo "  6. Re-run this script"
    fail "No device connected"
fi

# Use first listed device
SERIAL=$(adb devices 2>/dev/null | tail -n +2 | grep -v "^$" | awk '{print $1}' | head -1)
ADB="adb -s $SERIAL"
info "Using device: $SERIAL"

ANDROID_VER=$($ADB shell getprop ro.build.version.release 2>/dev/null | tr -d '\r')
MODEL=$($ADB shell getprop ro.product.model 2>/dev/null | tr -d '\r')
info "Device: $MODEL  Android: $ANDROID_VER"

# Battery check
BAT_PCT=$($ADB shell dumpsys battery 2>/dev/null | grep "level:" | awk '{print $2}' | tr -d '\r' || echo "0")
if [[ "$BAT_PCT" =~ ^[0-9]+$ ]] && [[ "$BAT_PCT" -lt 30 ]]; then
    warn "Battery is at ${BAT_PCT}%. Charge to at least 30% before installing."
    read -r -p "Continue anyway? [y/N] " REPLY
    [[ "$REPLY" =~ ^[Yy]$ ]] || fail "Aborted: low battery"
fi
ok "Battery: ${BAT_PCT}%"

# Storage check (require 2 GB free)
FREE_KB=$($ADB shell df /data 2>/dev/null | tail -1 | awk '{print $4}' | tr -d '\r' || echo "0")
FREE_MB=$(( ${FREE_KB:-0} / 1024 ))
if [[ "$FREE_MB" -lt 2048 ]]; then
    warn "Only ${FREE_MB} MB free on /data. Recommended: ≥ 2048 MB."
fi
ok "Free storage: ${FREE_MB} MB"

# ── Step 1 — Disable child-lock / Kids Mode ───────────────────────────────────
step "Step 1 — Disable Blackview Kids Mode / restricted profile"

$ADB shell "am force-stop com.blackview.kidzone 2>/dev/null || true"
$ADB shell "settings put secure restricted_profile_id 0 2>/dev/null || true"
$ADB shell "pm disable-user --user 0 com.blackview.kidzone 2>/dev/null || true"

# Disable Google Family Link supervisor if present
$ADB shell "pm disable-user --user 0 com.google.android.apps.kids.familylinkhelper 2>/dev/null || true"

ok "Kids Mode / restricted profile cleared"

# ── Step 2 — Enable sideloading ───────────────────────────────────────────────
step "Step 2 — Enable APK sideloading"

$ADB shell "settings put global install_non_market_apps 1"
$ADB shell "settings put secure install_non_market_apps 1"
ok "Sideloading enabled"

# ── Step 3 — Disable OEM bloatware ────────────────────────────────────────────
step "Step 3 — Disable OEM / surveillance bloatware (reversible)"

BLOATWARE=(
    "com.mediatek.mdmconfig"
    "com.mediatek.mdmloge"
    "com.mediatek.wfo.legacy"
    "com.mediatek.engineermode"
    "com.mediatek.ygps"
    "com.mediatek.mtklogger"
    "com.facebook.appmanager"
    "com.facebook.services"
    "com.google.android.videos"
    "com.google.android.apps.tachyon"
)

for pkg in "${BLOATWARE[@]}"; do
    $ADB shell "pm disable-user --user 0 $pkg 2>/dev/null && echo 'disabled $pkg' || echo 'not present: $pkg'" \
        | grep -v "not present" | while read -r line; do info "$line"; done
done
ok "Bloatware disabled"

# ── Step 4 — Battery optimisation exemption ───────────────────────────────────
step "Step 4 — Exempt Termux from battery optimisation"

$ADB shell "dumpsys deviceidle whitelist +com.termux 2>/dev/null || true"
$ADB shell "settings put global background_process_limit 4 2>/dev/null || true"
$ADB shell "settings put global app_standby_enabled 0 2>/dev/null || true"
ok "Battery optimisation exemption applied"

# ── Step 5 — Install Termux ───────────────────────────────────────────────────
step "Step 5 — Install Termux, Termux:Boot, Termux:API"

TERMUX_VERSION="0.118.0"
TERMUX_URL="https://f-droid.org/repo/com.termux_${TERMUX_VERSION//./_}.apk"
TERMUX_BOOT_URL="https://f-droid.org/repo/com.termux.boot_7.apk"
TERMUX_API_URL="https://f-droid.org/repo/com.termux.api_51.apk"

TMP_DIR="$(mktemp -d)"
trap "rm -rf $TMP_DIR" EXIT

# Only install if not already present
install_if_missing() {
    local pkg="$1" url="$2" fname="$3"
    if $ADB shell pm list packages 2>/dev/null | grep -q "$pkg"; then
        ok "$pkg already installed"
    else
        info "Downloading $fname …"
        if curl -fsSL -o "$TMP_DIR/$fname" "$url" 2>/dev/null; then
            $ADB install -r "$TMP_DIR/$fname" && ok "$pkg installed" || warn "$pkg install failed (F-Droid URL may have changed)"
        else
            warn "Download failed for $fname — install manually from F-Droid"
        fi
    fi
}

install_if_missing "com.termux"      "$TERMUX_URL"      "termux.apk"
install_if_missing "com.termux.boot" "$TERMUX_BOOT_URL" "termux_boot.apk"
install_if_missing "com.termux.api"  "$TERMUX_API_URL"  "termux_api.apk"

# ── Step 6 — Bootstrap Termux Python environment ──────────────────────────────
step "Step 6 — Bootstrap Termux Python / ggwave / diary"

info "This step opens Termux on the phone — watch the screen for prompts."
info "Sending setup commands via ADB (takes 2–5 minutes)…"

BOOTSTRAP_CMD='pkg update -y && pkg upgrade -y && pkg install -y python python-pip portaudio libzmq git curl wget && pip install ggwave numpy pyaudio requests && echo BOOTSTRAP_OK'

$ADB shell "am start -n com.termux/.HomeActivity 2>/dev/null || true"
sleep 3

# Use adb shell input to type into Termux (best-effort; interactive fallback below)
$ADB shell "input text '${BOOTSTRAP_CMD}'" 2>/dev/null && \
    $ADB shell "input keyevent 66" 2>/dev/null || \
    warn "Could not send text to Termux automatically. Run this command manually in Termux:\n  $BOOTSTRAP_CMD"

info "Waiting 30 s for bootstrap to start (watch the phone)…"
sleep 30

# Clone diary repo if not already present
CLONE_CMD='test -d ~/diary || (git clone https://github.com/wuzbak/diary.git ~/diary && echo CLONE_OK) && echo DIARY_READY'
$ADB shell "input text '${CLONE_CMD}'" 2>/dev/null && \
    $ADB shell "input keyevent 66" 2>/dev/null || \
    warn "Run in Termux: git clone https://github.com/wuzbak/diary.git ~/diary"

# ── Step 7 — Install GibberNode APK ──────────────────────────────────────────
step "Step 7 — Install GibberNode.apk"

if [[ -n "$APK_PATH" && -f "$APK_PATH" ]]; then
    $ADB install -r "$APK_PATH" && ok "GibberNode.apk installed" || warn "APK install failed"

    # Grant runtime permissions
    PERMISSIONS=(
        "android.permission.RECORD_AUDIO"
        "android.permission.ACCESS_FINE_LOCATION"
        "android.permission.ACCESS_COARSE_LOCATION"
    )
    for perm in "${PERMISSIONS[@]}"; do
        $ADB shell "pm grant com.axiomzero.pentacorder $perm 2>/dev/null || true" && ok "Granted: $perm"
    done
else
    warn "No APK provided (use --apk path/to/GibberNode.apk to install)."
    info "Build the APK first: cd Android && ./gradlew assembleRelease"
fi

# ── Step 8 — Configure Termux:Boot auto-start ─────────────────────────────────
step "Step 8 — Configure Termux:Boot auto-start"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOT_SCRIPT="$SCRIPT_DIR/termux_boot.sh"

if [[ -f "$BOOT_SCRIPT" ]]; then
    $ADB push "$BOOT_SCRIPT" /sdcard/start-gibberlink.sh
    $ADB shell "mkdir -p ~/.termux/boot && cp /sdcard/start-gibberlink.sh ~/.termux/boot/ && chmod +x ~/.termux/boot/start-gibberlink.sh"
    ok "Termux:Boot auto-start configured"
else
    warn "termux_boot.sh not found at $BOOT_SCRIPT — skipping boot script"
fi

# ── Step 9 — Push SD card content ────────────────────────────────────────────
step "Step 9 — Push project content to SD card"

REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [[ -d "$REPO_ROOT/Unitary-Manifold" ]]; then
    info "Pushing Unitary-Manifold → /sdcard/manifold/ …"
    $ADB shell "mkdir -p /sdcard/manifold"
    $ADB push "$REPO_ROOT/Unitary-Manifold/" /sdcard/manifold/ 2>/dev/null && ok "Manifold pushed" || warn "Manifold push failed (large directory)"
fi

if [[ -d "$REPO_ROOT/Gibberlink" ]]; then
    info "Pushing Gibberlink → /sdcard/gibberlink/ …"
    $ADB shell "mkdir -p /sdcard/gibberlink"
    $ADB push "$REPO_ROOT/Gibberlink/" /sdcard/gibberlink/ 2>/dev/null && ok "Gibberlink pushed" || warn "Gibberlink push failed"
fi

# ── Step 10 — Verify ─────────────────────────────────────────────────────────
step "Step 10 — Verify installation"

echo
if $ADB shell pm list packages 2>/dev/null | grep -q com.termux; then
    ok "Termux: installed"
else
    warn "Termux: NOT found"
fi

if $ADB shell pm list packages 2>/dev/null | grep -q com.axiomzero.pentacorder; then
    ok "GibberNode: installed"
    info "Launching GibberNode…"
    $ADB shell "am start -n com.axiomzero.pentacorder/.MainActivity" 2>/dev/null || true
else
    warn "GibberNode: NOT installed (build the APK and run with --apk)"
fi

echo
echo -e "${GRN}════════════════════════════════════════════════════════${RST}"
echo -e "${GRN}  Installation complete.${RST}"
echo -e "${GRN}  Next steps:${RST}"
echo    "    1. Open Termux and run: source ~/diary/Gibberlink/.env"
echo    "    2. Open GibberNode and complete the Calibration Wizard"
echo    "    3. Reboot the phone to verify Termux:Boot auto-start"
echo -e "${GRN}  Revert anything: adb shell pm enable <package.name>${RST}"
echo -e "${GRN}════════════════════════════════════════════════════════${RST}"
