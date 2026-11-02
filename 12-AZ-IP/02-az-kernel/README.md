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

### Kernel unit tests (`cargo test`)

The hardware-independent kernel logic — the heap allocator, memory
bookkeeping, φ-debt RAM filesystem, and IPC ring buffers/channel table — is
factored into a library crate (`src/lib.rs`, `az_kernel`) that compiles with
`std` under `#[cfg(test)]`, so it runs on the ordinary host `cargo test`
harness instead of requiring a UEFI test runner:

```bash
bash 12-AZ-IP/02-az-kernel/scripts/test_lib.sh
# or: make -C 12-AZ-IP/02-az-kernel test
```

(`.cargo/config.toml` pins every cargo invocation in this directory to the
`x86_64-unknown-uefi` target with `-Zbuild-std`, which collides with a plain
host `cargo test`; the script above temporarily relocates that config file
for the one host-targeted test invocation and always restores it on exit —
see the script's header comment for the full rationale.) The `[[bin]]`
target (`az-kernel`, the actual bootable UEFI image) is unaffected and keeps
building exclusively for `x86_64-unknown-uefi` via `cargo build`/`cargo check`.

### AZ-HEAP: kernel-owned allocator

`src/mm/heap.rs` is a first-fit, coalescing free-list allocator (`unsafe impl
GlobalAlloc`) backed by a static arena compiled into the kernel image. It
replaces the `uefi` crate's `global_allocator` feature, which serviced every
allocation via the UEFI `AllocatePool`/`FreePool` boot services — services
that become invalid the instant `boot::exit_boot_services` runs, while the
kernel kept calling `alloc::format!` afterwards. `mm::heap` owns its memory
for the kernel's entire lifetime instead, so allocation never depends on a
firmware (or host) shortcut. Covered by 10 unit tests, including alignment
rounding, recovery of representable fragments, coalescing, and out-of-memory
behaviour.

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, kernel engineering, and consolidation: **GitHub Copilot** (AI).

## Sprint BA integration

- Aligned with **Unitary Manifold v25.5** / **Sprint BA**.
- `SPRINT_BA_CONSTANTS.md` records the kernel-facing constants with honest status labels.
- `az_kernel_sprint_ba.py` exports the constants as a Python dict and provides a self-testable validator.
