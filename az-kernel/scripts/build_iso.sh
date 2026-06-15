#!/usr/bin/env bash
# az-kernel/scripts/build_iso.sh — Create bootable AxiomZero ISO (Sprint 3)
#
# Produces axiomzero-0.1.0.iso using the Limine bootloader.
#
# Requires: limine (https://limine-bootloader.org/), xorriso

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

VERSION="0.1.0"
ISO_NAME="axiomzero-$VERSION.iso"
ISO_DIR="$KERNEL_DIR/iso_root"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AxiomZero — ISO Builder (Sprint 3)"
echo "  Output: $ISO_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Build the EFI binary first
"$SCRIPT_DIR/build.sh" --release

# Download Limine if not present
LIMINE_DIR="$KERNEL_DIR/limine"
if [[ ! -d "$LIMINE_DIR" ]]; then
    echo "[ISO] Cloning Limine bootloader..."
    git clone https://github.com/limine-bootloader/limine.git --branch=v8.x-binary --depth=1 "$LIMINE_DIR"
    make -C "$LIMINE_DIR"
fi

# Build ISO root
rm -rf "$ISO_DIR"
mkdir -p "$ISO_DIR/EFI/BOOT"
mkdir -p "$ISO_DIR/boot/limine"

# Copy kernel EFI
cp "$KERNEL_DIR/dist/EFI/BOOT/BOOTX64.EFI" "$ISO_DIR/EFI/BOOT/BOOTX64.EFI"

# Copy Limine bootloader files
cp "$LIMINE_DIR/limine-bios.sys"    "$ISO_DIR/boot/limine/"
cp "$LIMINE_DIR/limine-bios-cd.bin" "$ISO_DIR/boot/limine/"
cp "$LIMINE_DIR/limine-uefi-cd.bin" "$ISO_DIR/boot/limine/"
cp "$LIMINE_DIR/BOOTX64.EFI"        "$ISO_DIR/EFI/BOOT/"

# Limine config
cat > "$ISO_DIR/boot/limine/limine.cfg" <<'EOF'
TIMEOUT=3

:AxiomZero Unitary Operating System
    PROTOCOL=efi_chainload
    IMAGE_PATH=boot():/EFI/BOOT/BOOTX64.EFI
EOF

# Build ISO with xorriso
xorriso -as mkisofs \
    -b boot/limine/limine-bios-cd.bin \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    --efi-boot boot/limine/limine-uefi-cd.bin \
    -efi-boot-part --efi-boot-image \
    --protective-msdos-label \
    "$ISO_DIR" -o "$KERNEL_DIR/dist/$ISO_NAME"

# Install Limine BIOS boot sector
"$LIMINE_DIR/limine" bios-install "$KERNEL_DIR/dist/$ISO_NAME"

echo ""
echo "[ISO] ✅ Sprint 3 milestone: $ISO_NAME created."
echo "      Flash to USB: dd if=$KERNEL_DIR/dist/$ISO_NAME of=/dev/sdX bs=1M"
