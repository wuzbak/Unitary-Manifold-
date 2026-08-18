#!/usr/bin/env bash
# az-kernel/scripts/build_arm64.sh — Build AxiomZero for ARM64 (Sprint 3)
#
# Produces az-kernel-arm64.efi for Raspberry Pi 5 and Jetson Nano.
#
# Requires: Rust aarch64-unknown-uefi target, cross-compilation toolchain

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AxiomZero — ARM64 Build (Sprint 3)"
echo "  Target: aarch64-unknown-uefi"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$KERNEL_DIR"

# Ensure the ARM64 UEFI target is available
rustup target add aarch64-unknown-uefi 2>/dev/null || true

cargo build --release --target aarch64-unknown-uefi

EFI_SRC="$KERNEL_DIR/target/aarch64-unknown-uefi/release/az-kernel.efi"
EFI_DST="$KERNEL_DIR/dist-arm64/EFI/BOOT/BOOTAA64.EFI"
mkdir -p "$(dirname "$EFI_DST")"
cp "$EFI_SRC" "$EFI_DST"

echo "[BUILD] ✅ ARM64 EFI binary → $EFI_DST"
echo ""
echo "  Raspberry Pi 5: copy dist-arm64/ contents to SD card's FAT32 partition"
echo "  QEMU ARM64 test:"
echo "    qemu-system-aarch64 -machine virt -cpu cortex-a72 -m 1G \\"
echo "      -drive if=pflash,format=raw,readonly=on,file=OVMF_CODE.fd \\"
echo "      -drive format=raw,file=fat:rw:dist-arm64 \\"
echo "      -serial stdio -display none"
