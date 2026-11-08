#!/usr/bin/env bash
# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
#
# scripts/test_lib.sh — Run the host-testable kernel library (`cargo test --lib`)
# Use `--clippy` as the first argument to lint that library on the host instead.
# Remaining arguments are passed to Cargo, e.g. `--clippy --locked -- -D warnings`.
#
# The kernel binary target builds exclusively for `x86_64-unknown-uefi` with
# `-Zbuild-std`, forced by `.cargo/config.toml` (`[build] target = ...` and
# `[unstable] build-std = [...]`). That config applies to *every* cargo
# invocation in this directory, including a plain `cargo test`, so it also
# force-rebuilds `core`/`alloc` from source even when targeting the host
# triple — which collides with the host's own prebuilt `core` and fails
# with "duplicate lang item" errors.
#
# This script runs the host-testable `az_kernel` library (see src/lib.rs)
# against the real host `std` test harness by temporarily moving
# `.cargo/config.toml` out of the way, so Cargo falls back to ordinary host
# compilation for this one invocation. The UEFI kernel binary itself is
# never built here — verify it separately with `cargo check`/`cargo build`
# (uses the normal, unmodified config).
# Clippy likewise uses the host's prebuilt runtime and checks only the library,
# not the UEFI-only binary; no dependency version changes are needed.
#
# The original config is restored unconditionally (`trap ... EXIT`), even if
# the test run fails or the script is interrupted.
set -euo pipefail

CARGO_COMMAND=test
if [[ "${1:-}" == "--clippy" ]]; then
  CARGO_COMMAND=clippy
  shift
fi

cd "$(dirname "${BASH_SOURCE[0]}")/.."

CONFIG="./.cargo/config.toml"
BACKUP="./.cargo/config.toml.test_lib_bak"

if [[ -f "$BACKUP" ]]; then
  echo "error: stale backup $BACKUP exists from an interrupted run; resolve manually." >&2
  exit 1
fi

restore_config() {
  if [[ -f "$BACKUP" ]]; then
    mv "$BACKUP" "$CONFIG"
  fi
}
trap restore_config EXIT

mv "$CONFIG" "$BACKUP"

HOST_TRIPLE="$(rustc -vV | sed -n 's/^host: //p')"
cargo "$CARGO_COMMAND" --lib --target "$HOST_TRIPLE" "$@"
