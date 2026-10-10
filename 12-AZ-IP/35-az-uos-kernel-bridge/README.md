# AZ UOS/AZ-KERNEL Bridge — Product 35

**Folder:** `12-AZ-IP/35-az-uos-kernel-bridge/`
**Version:** 1.0.0
**TRL:** TRL-2 (design contract + Python reference implementation; no Rust code shipped into the kernel)
**Status:** Active — Phases 0-1 of article-354's "UOS on AZ-KERNEL" roadmap

## What this is

UOS (Product 05, 566 tests, TRL-3) and AZ-KERNEL (Product 02, bare-metal
Rust, TRL-3) have never been pointed at each other. This product is the
first concrete step:

- **Phase 0 — the interface contract.** `GEODESIC_SCHEDULABLE_RUST_CONTRACT`
  writes down, field by field, what `UOS.scheduler.ProcessGeodesic`'s public
  shape would need to look like as a Rust trait implementation — `pid: u64`,
  `priority: f32`, `phi_weight: f32`, `state_vector: [f32; 5]`, and an
  `affinity_score` method signature. `validate_schedulable()` checks that a
  real `ProcessGeodesic` instance satisfies the matching Python `Protocol`.
- **Phase 1 — the IPC primitive, cross-checked.** `WindingAddress` gives
  `12-AZ-IP/02-az-kernel/src/ipc/kk_channel.rs`'s existing ring-adjacency
  rule (ring i may talk only to ring i±1, mod 5, wrapping 0↔4) an explicit
  Python reference model. `parse_rust_adjacency_pairs()` parses the actual
  `impl KKAdjacent<Ring<A>, Ring<B>>` declarations out of the real `.rs`
  file, and `validate_against_kk_channel_rs()` confirms the Python model
  and the Rust source agree on all 10 directed adjacency pairs — a real
  cross-check between the two kernels, not an assumption.

## Epistemic status

Phase 2 (porting the simplest UOS scheduling primitive to boot under real
QEMU) and Phase 3 (honest TRL reassessment of both Products 02 and 05 based
on what Phase 2 actually demonstrates) are **not** part of this product —
they require Rust implementation work inside `02-az-kernel` itself and a
real QEMU boot, not a Python design/cross-check layer.

## Usage

```bash
python 12-AZ-IP/35-az-uos-kernel-bridge/run.py
```

## Tests

```bash
python -m pytest 12-AZ-IP/35-az-uos-kernel-bridge/tests -q
```

## Sources

- `12-AZ-IP/02-az-kernel/src/ipc/kk_channel.rs`
- `12-AZ-IP/05-uos-kernel/UOS/scheduler.py`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #8

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
