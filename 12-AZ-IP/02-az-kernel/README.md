# 02-az-kernel — Canonical AxiomZero Rust Kernel

This folder is the canonical merge of `az-kernel/` (full implementation) and `11-AZ-OS/ax-kernel/` (earlier prototype).

## Merge policy applied

- Preserved the **fuller** `az-kernel/` tree: drivers, filesystem, framebuffer, panic handler, build scripts, and assets.
- Added the unique legacy IPC primitive: `src/ipc/kk_channel.rs`.
- Preserved legacy toolchain guidance in `LEGACY_README.md` and carried forward `.cargo/config.toml`.

## Build

```bash
cd 12-AZ-IP/02-az-kernel
cargo check
bash 12-AZ-IP/02-az-kernel/scripts/build.sh
```

## Deployment targets

- UEFI x86-64 boot image
- QEMU / OVMF integration
- ARM64 cross-build via `scripts/build_arm64.sh`

## Tests

```bash
python3 -m pytest 12-AZ-IP/02-az-kernel/tests/test_layout.py -q
```

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, kernel engineering, and consolidation: **GitHub Copilot** (AI).

## Sprint BA integration

- Aligned with **Unitary Manifold v25.5** / **Sprint BA**.
- `SPRINT_BA_CONSTANTS.md` records the kernel-facing constants with honest status labels.
- `az_kernel_sprint_ba.py` exports the constants as a Python dict and provides a self-testable validator.
