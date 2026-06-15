#!/usr/bin/env bash
# az-kernel/scripts/build.sh — Build AxiomZero kernel for x86-64 UEFI
# Sprint 0: Produces az-kernel.efi ready for QEMU boot or USB flash.
#
# Usage:
#   ./scripts/build.sh [--release]
#
# Requires: rustup, cargo, llvm-tools (rustup component add llvm-tools)
# Optional: qemu-system-x86_64 (for scripts/qemu_run.sh)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$(cd "$KERNEL_DIR/.." && pwd)"

PROFILE="${1:-dev}"
[[ "$PROFILE" == "--release" ]] && PROFILE="release" || true

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AxiomZero Bare-Metal Kernel — Build Script"
echo "  Target: x86_64-unknown-uefi  |  Profile: $PROFILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --- Font asset (Sprint 0 requirement) ---
FONT_ASSET="$KERNEL_DIR/assets/font8x16.bin"
mkdir -p "$KERNEL_DIR/assets"
if [[ ! -f "$FONT_ASSET" ]]; then
    echo "[BUILD] Generating minimal 8×16 monospace font binary..."
    python3 "$KERNEL_DIR/scripts/gen_font.py" "$FONT_ASSET"
fi

# --- Rust build ---
cd "$KERNEL_DIR"
echo "[BUILD] Running cargo build..."
if [[ "$PROFILE" == "release" ]]; then
    cargo build --release --target x86_64-unknown-uefi 2>&1
else
    cargo build --target x86_64-unknown-uefi 2>&1
fi

# --- Output EFI binary ---
EFI_SRC="$KERNEL_DIR/target/x86_64-unknown-uefi/$PROFILE/az-kernel.efi"
EFI_DST="$KERNEL_DIR/dist/EFI/BOOT/BOOTX64.EFI"
mkdir -p "$(dirname "$EFI_DST")"
cp "$EFI_SRC" "$EFI_DST"
echo "[BUILD] EFI binary → $EFI_DST"
echo "[BUILD] ✅ Sprint 0 milestone: az-kernel.efi built successfully."
echo ""
echo "  Next: ./scripts/qemu_run.sh       (test in QEMU)"
echo "  Next: ./scripts/build_iso.sh      (create bootable ISO)"
echo "  Next: ./scripts/build_arm64.sh    (Sprint 3: ARM64 port)"
