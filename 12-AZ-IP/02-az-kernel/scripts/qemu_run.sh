#!/usr/bin/env bash
# az-kernel/scripts/qemu_run.sh — Boot AxiomZero in QEMU (Sprint 0 milestone)
#
# Usage:
#   ./scripts/qemu_run.sh [--debug]
#
# Requires: qemu-system-x86_64, OVMF UEFI firmware
#
# OVMF firmware (UEFI for QEMU):
#   Ubuntu/Debian: apt install ovmf  → /usr/share/OVMF/OVMF_CODE.fd
#   Arch Linux:    pacman -S edk2-ovmf
#   macOS:         brew install qemu  (OVMF bundled)
#   Windows:       download from https://www.tianocore.org/

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

DEBUG_FLAG=""
[[ "${1:-}" == "--debug" ]] && DEBUG_FLAG="-s -S" || true

# Locate OVMF firmware
OVMF_PATHS=(
    "/usr/share/OVMF/OVMF_CODE.fd"
    "/usr/share/edk2/x64/OVMF_CODE.fd"
    "/usr/local/share/qemu/edk2-x86_64-code.fd"
    "$KERNEL_DIR/dist/OVMF_CODE.fd"
)
OVMF=""
for p in "${OVMF_PATHS[@]}"; do
    if [[ -f "$p" ]]; then OVMF="$p"; break; fi
done

if [[ -z "$OVMF" ]]; then
    echo "[QEMU] OVMF not found. Attempting download..."
    mkdir -p "$KERNEL_DIR/dist"
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y ovmf 2>/dev/null && OVMF="/usr/share/OVMF/OVMF_CODE.fd"
    fi
fi

if [[ -z "$OVMF" ]]; then
    echo "[QEMU] ERROR: OVMF UEFI firmware not found."
    echo "       Install: apt install ovmf  OR  brew install qemu"
    exit 1
fi

# Build if needed
if [[ ! -f "$KERNEL_DIR/dist/EFI/BOOT/BOOTX64.EFI" ]]; then
    echo "[QEMU] EFI binary not found — running build first..."
    "$SCRIPT_DIR/build.sh"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AxiomZero — QEMU Boot (Sprint 0 Milestone)"
echo "  OVMF: $OVMF"
echo "  Press Ctrl+A, X to quit QEMU serial console"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

qemu-system-x86_64 \
    -machine q35,accel=kvm:tcg \
    -cpu host,+avx2 \
    -m 2G \
    -smp 4 \
    -drive if=pflash,format=raw,readonly=on,file="$OVMF" \
    -drive format=raw,file=fat:rw:"$KERNEL_DIR/dist" \
    -display gtk \
    -serial stdio \
    -net none \
    $DEBUG_FLAG \
    -no-reboot
