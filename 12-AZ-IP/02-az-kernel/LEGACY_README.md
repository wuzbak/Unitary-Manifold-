# AxiomZero Unitary Operating System — v0.1

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, kernel engineering, test suites: **GitHub Copilot** (AI).*

---

## What Is AxiomZero?

AxiomZero is a **5D Kaluza-Klein operating system** — the first OS whose kernel
architecture is derived directly from a unified physics framework.  It has two
tightly coupled layers:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AZ-KERNEL** | Rust (no_std, UEFI) | Bare-metal x86-64 / ARM64 kernel |
| **Cognitive Layer** | Python 3.12 + Ollama | 7-manager × 5-sub-agent AI network |

The two layers share the same mathematical constants and the same security model.
There is no arbitrary separation between "physics" and "computing" — the OS
*is* the physics.

---

## Physics-to-OS Mapping

Every kernel primitive is a direct geometric derivation from the
5D Kaluza-Klein metric ansatz:

| Physics concept | AZ-KERNEL primitive |
|----------------|---------------------|
| **Fiber bundle** (5 KK extra dimensions) | 5 privilege rings (KK levels 0–4) |
| **Winding number n_w = 5** | 5 interrupt priority rings |
| **k_cs = 74 = 5² + 7²** | 74 pages per compactification domain |
| **Geodesic equations** | CPU scheduler (process = point in metric space) |
| **φ-debt entropy** (Pillar 16) | Memory reclamation + filesystem eviction |
| **Holographic boundary** (Pillar 4) | IPC channel interface |
| **KK adjacency rule** | IPC security: only adjacent levels may communicate |
| **Pentad clearance bits** | Process security descriptor |
| **φ⁻¹ = 0.618** | Debt decay rate in MM and FS layers |

---

## Directory Structure

```
ax-kernel/              ← Rust bare-metal kernel
  Cargo.toml            ← Manifest (uefi, spin, heapless, bitflags, libm)
  rust-toolchain.toml   ← Pinned Rust stable toolchain
  src/
    main.rs             ← UEFI entry point, 3-phase boot
    framebuffer.rs      ← GOP display, 8×16 glyph renderer
    panic_handler.rs    ← Bare-metal panic: serial COM1 + HLT
    mm/                 ← Memory management
      mod.rs            ← AxiomMemoryManager façade
      fiber_bundle.rs   ← 5D fiber bundle address space
      pmm.rs            ← Bitmap physical memory manager
      vmm.rs            ← Virtual memory manager (5 ring layout)
      phi_debt.rs       ← φ-debt entropy accounting
    sched/              ← Scheduler
      mod.rs            ← AxiomScheduler (geodesic priority)
      process.rs        ← Process control block (5D metric state)
      geodesic.rs       ← Geodesic distance computation
    ipc/                ← Inter-process communication
      mod.rs            ← IPC façade
      holographic.rs    ← Holographic boundary channels
      ring_buffer.rs    ← Lock-free SPSC ring buffer
    fs/                 ← Filesystem
      mod.rs            ← AZ-FS façade (global RamFs)
      inode.rs          ← Inode with φ-debt tracking
      ramfs.rs          ← RAM filesystem with eviction sweep
    drv/                ← Drivers
      mod.rs            ← Driver boundary layer
      pcie.rs           ← PCI-E stub (Sprint 3)
      usb_hid.rs        ← USB HID stub
      net.rs            ← Network stub
  assets/
    font8x16.bin        ← 8×16 monospace glyph table (95 glyphs)
  scripts/
    build.sh            ← x86-64 UEFI build
    qemu_run.sh         ← QEMU test runner (requires OVMF)
    build_iso.sh        ← Limine bootable ISO builder
    build_arm64.sh      ← ARM64 cross-compilation (Pi 5 / Jetson)
    gen_font.py         ← Font binary generator

az-os/                  ← Python cognitive layer
  __init__.py
  agent_core.py         ← 7-manager orchestrator (main entry point)
  hils.py               ← HILS invariant enforcement engine
  state.py              ← SQLite state persistence (5 tables)
  managers/
    __init__.py
    m1_geometry.py      ← M1: 5D metric, Christoffel, Riemann, compactification, boundary
    m2_fields.py        ← M2: KK scalar, Maxwell, geodesic, stress-energy, EH action
    m3_symbolic.py      ← M3: SymPy + Z3 symbolic verification
    m4_test_guard.py    ← M4: 0-failure test guardian
    m5_corpus.py        ← M5: RAG corpus index + retrieval
    m6_research.py      ← M6: arXiv + Brave Search academic monitor
    m7_interface.py     ← M7: synthesis, reporting, HILS token issuance
  mcp/
    __init__.py
    filesystem.py       ← MCP Filesystem Server (sandboxed read/write)
    executor.py         ← MCP Command Execution Server (whitelist-only)
    browser.py          ← MCP Browser Server (domain-allowlist HTTP)

11-AZ-OS/               ← Documentation (this directory)
  README.md             ← This file
  ARCHITECTURE.md       ← Physics-to-OS mapping reference
  DEVELOPMENT.md        ← Build and test instructions

axiomzero_bootstrap.py  ← Cross-platform installer (one command)

tests/
  test_az_os_hils.py              ← HILS enforcement tests (27 tests)
  test_az_os_state.py             ← StateDB persistence tests (25 tests)
  test_az_os_managers.py          ← Manager unit tests (30 tests)
  test_az_os_mcp.py               ← MCP server safety tests (28 tests)
  test_axiomzero_kernel_spec.py   ← Kernel invariant specs (32 tests)
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Rust 1.75+ (for kernel only)
- 4 GB RAM minimum (16 GB recommended)
- NVIDIA GPU with ≥ 6 GB VRAM (optional, enables full-speed Ollama)

### One-command install (cognitive layer)

```bash
python3 axiomzero_bootstrap.py
```

This installs Ollama, pulls the physics and coding LLMs, writes Continue.dev
config, and registers AxiomZero as a system service.

### Build the bare-metal kernel

```bash
cd az-kernel
bash scripts/build.sh          # produces az-kernel.efi
bash scripts/qemu_run.sh       # boot in QEMU (requires OVMF)
bash scripts/build_iso.sh      # produce bootable ISO (requires Limine)
bash scripts/build_arm64.sh    # ARM64 binary for Raspberry Pi 5
```

### Start the cognitive layer

```python
import sys
sys.path.insert(0, ".")
from az_os.agent_core import AgentCore
core = AgentCore()
core.boot()
print(core.status())
```

### Run the test suite

```bash
# Full AxiomZero test suite (140 new tests)
python3 -m pytest tests/test_az_os_hils.py \
                  tests/test_az_os_state.py \
                  tests/test_az_os_managers.py \
                  tests/test_az_os_mcp.py \
                  tests/test_axiomzero_kernel_spec.py -v

# Full repository regression (46,885+ tests)
python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q
```

---

## HILS Invariant

**9 actions that always require human approval:**

| Action | Reason |
|--------|--------|
| `PILLAR_CANONICALISE` | Changes the physics ontology |
| `AUTHORSHIP_MODIFY` | Provenance integrity |
| `FALLIBILITY_WRITE` | Epistemic honesty |
| `FALSIFICATION_MODIFY` | Falsification condition integrity |
| `TEST_DELETE` | 0-failure invariant |
| `TEST_MODIFY_ASSERTION` | 0-failure invariant |
| `KERNEL_RING0_ACCESS` | Bare-metal ring 0 privilege |
| `COMMIT_TO_MAIN` | Main branch protection |
| `AGENT_SPAWN_UNLIMITED` | Loop-limit protection |

Tokens are single-use with a 5-minute TTL.  M7 is the only manager that can
issue tokens.  All HILS events are persisted to SQLite.

---

## Platform Support

| Platform | Cognitive Layer | Bare-Metal Kernel | Service |
|----------|----------------|-------------------|---------|
| Windows 10+ | ✅ | ✅ (UEFI boot) | Task Scheduler / NSSM |
| macOS 12+ | ✅ | ✅ (UEFI VM / Asahi) | launchd |
| Linux x86-64 | ✅ | ✅ (native boot) | systemd |
| Linux ARM64 | ✅ | ✅ (Pi 5 / Jetson) | systemd |
| Android (Termux) | ✅ (remote) | ❌ | Manual |

---

## Falsification Conditions

The kernel scheduler uses the same geodesic metric as the physics framework.
If LiteBIRD (~2032) returns birefringence β outside [0.22°, 0.38°], the entire
UM framework — including the kernel's metric weights — would require revision.

AxiomZero is honest: the OS inherits the falsifiability of its parent theory.

---

## Authorship

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, kernel engineering, test suites, document engineering: **GitHub Copilot** (AI).*
