# AZ UOS/AZ-KERNEL Bridge — Product 35

**Folder:** `12-AZ-IP/35-az-uos-kernel-bridge/`
**Version:** 1.2.0
**TRL:** TRL-2 (design contract + Python IPC adapter/reference implementation; no Rust bridge shipped into the kernel)
**Status:** Active — executable host-side message adapter and cross-checks for article-354's "UOS on AZ-KERNEL" roadmap

## What this is

UOS (Product 05, 566 tests, TRL-3) and AZ-KERNEL (Product 02, bare-metal
Rust, TRL-3) have never been pointed at each other. This product is an
executable host-side contract. It does not open or connect to a running
kernel; the HTTP endpoint validates and serializes a JSON adapter record with
the same fields as AZ-KERNEL's `KKMessage`.

- **Phase 0 — the interface contract.** `GEODESIC_SCHEDULABLE_RUST_CONTRACT`
  writes down, field by field, what `UOS.scheduler.ProcessGeodesic`'s public
  shape would need to look like as a Rust trait implementation — `pid: u64`,
  `priority: f32`, `phi_weight: f32`, `state_vector: [f32; 5]`, and an
  `affinity_score` method signature. `validate_schedulable()` checks that a
  real `ProcessGeodesic` instance satisfies the matching Python `Protocol`.
- **Phase 1 — the IPC primitive, cross-checked.** `WindingAddress` models
  the modulo-five `KKAdjacent` type-level rule in
  `02-az-kernel/src/ipc/kk_channel.rs`, including wraparound 0↔4. The
  cross-check also reads the runtime factory in `src/ipc/mod.rs`: it currently
  accepts only plain absolute-difference-one pairs. Therefore ring 0↔4 is
  allowed by the type-level declarations but rejected by `create_channel`.
  The API reports this mismatch instead of treating the two contracts as
  equivalent.
- **Host-side message adapter.** `KKMessage` uses the real Rust field names
  and integer widths (`usize`, `u64`, `u32`); `POST /api/ipc-message` validates
  field values and runtime-accepted ring pairs, then returns a canonical JSON
  record for a host integration to consume. This is a JSON adapter format,
  **not** a Rust memory layout, kernel wire ABI, queue operation, or live
  kernel connection.

## Epistemic status

No scheduler primitive has been ported into Rust, no IPC has been delivered
to a running kernel, and no bare-metal or QEMU boot was tested for this
change. A future native bridge still requires Rust implementation and a
demonstrated transport/queue integration in `02-az-kernel`.

## Usage

```bash
python 12-AZ-IP/35-az-uos-kernel-bridge/run.py
```

## Running as a web product

A stdlib-only JSON API and static dashboard provide the contract and adapter:

```bash
python 12-AZ-IP/35-az-uos-kernel-bridge/run.py serve --port 8135
# then open http://127.0.0.1:8135/
```

Endpoints: `GET /api/status`, `GET /api/validate-adjacency`,
`GET /api/neighbors?ring=`, `GET /api/contract`, and `POST /api/ipc-message`
with JSON fields `from_ring`, `to_ring`, `payload`, and `seq`. Example:

```bash
curl -sS -X POST http://127.0.0.1:8135/api/ipc-message \
  -H 'Content-Type: application/json' \
  -d '{"from_ring":0,"to_ring":1,"payload":42,"seq":0}'
```

The adapter rejects ring 0↔4 because the current runtime `create_channel`
does not accept wraparound, even though the separate `KKAdjacent` type-level
declarations do. It also checks `payload` as u64 and `seq` as u32.

## Tests

```bash
python -m pytest 12-AZ-IP/35-az-uos-kernel-bridge/tests -q
```

## Sources

- `12-AZ-IP/02-az-kernel/src/ipc/kk_channel.rs`
- `12-AZ-IP/02-az-kernel/src/ipc/mod.rs`
- `12-AZ-IP/05-uos-kernel/UOS/scheduler.py`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #8

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
