# Unitary Operating System (UOS)

> **A 5-dimensional Kaluza–Klein operating system built on the Unitary Manifold.**

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## What Is the UOS?

The Unitary Operating System (UOS) is a research-grade OS *kernel layer* that
replaces conventional 4D linear computing abstractions (linear schedulers,
linear address spaces, permission walls) with **5D geometric primitives**
derived from the Unitary Manifold.

The core thesis: every resource-management problem that makes today's operating
systems slow, fragmented, or insecure is a symptom of operating in 4D linear
logic.  By lifting the kernel into the 5D Kaluza–Klein manifold — the same
geometric framework that unifies gravity, electromagnetism, and the gauge
fields — these problems are resolved by *physical law* rather than by
engineering workarounds.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    UOS Kernel (5D Manifold Layer)                │
│                                                                  │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ Hypervisor │  │  Scheduler   │  │      Memory Manager      │ │
│  │            │←→│  (Geodesic)  │  │  (Unitary Addressing)    │ │
│  │ ManifoldSt │  │  ProcessGeo  │  │  Zero-Copy / No Frag     │ │
│  └────────────┘  └──────────────┘  └──────────────────────────┘ │
│         │                │                      │               │
│  ┌──────┴───────┐  ┌─────┴──────┐  ┌───────────┴────────────┐  │
│  │   Security   │  │ Filesystem │  │     Driver Wrapper     │  │
│  │ (Geometric   │  │(Holographic│  │  (5D intent → 4D HW)  │  │
│  │  Isolation)  │  │  Content-  │  │  X86 / ARM / RISC-V   │  │
│  └──────────────┘  │  Addressed)│  └────────────────────────┘  │
│                    └────────────┘                               │
└──────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │   Host OS (Linux / macOS /    │
              │   Windows) — monitor mode     │
              └───────────────────────────────┘
```

---

## Sub-Modules

### `UOS/hypervisor.py` — The Kernel

The `UOSHypervisor` is the **main engine**.  It manages the 5D manifold state
(`ManifoldState`: g, B, φ, t) and advances it one RK4 step per tick.

**Key capabilities:**
- `boot()` — initialise the manifold from flat Minkowski background
- `tick()` — advance one clock quantum (Δt = 12/37 ≈ 0.3243 manifold units)
- `run(steps)` — run N ticks; return history of `ManifoldState` snapshots
- `attach_to_host(cpu_load, mem_load)` — *monitor mode*: inject real system
  metrics; the manifold warps to reflect host resource pressure
- `manifold_invariant_ok()` — health gate: True when 5:7 braid ratio is intact
- `resource_report()` — full diagnostic dict

**Monitor / Hypervisor mode:**  
Run `hv.attach_to_host(cpu_load=psutil.cpu_percent()/100, mem_load=...)` in
a loop to shadow your current OS.  The manifold encodes resource state
geometrically — high CPU load increases the α coupling (more curvature).

### `UOS/scheduler.py` — Geodesic Scheduler

Replaces preemptive multitasking.  Processes are `ProcessGeodesic` objects
with a 5D phase-space `state_vector`.  The `GeodesicScheduler` picks the
next process by computing a *manifold affinity score*:

```
score = priority × φ_weight × ⟨state_vector, ∇φ⟩
```

The process whose trajectory is most aligned with the manifold φ-gradient
gets the CPU.  **No context-switch latency** — the manifold *predicts* which
process should run, rather than interrupting arbitrarily.

Capacity: **74 simultaneous geodesic lanes** (= K_CS = 5² + 7²).

### `UOS/memory.py` — Unitary Addressing

Memory pages are identified by *φ-addresses* on the radion gradient field,
not by integer offsets.

- **Zero-copy sharing**: `zero_copy_share(page_id, new_pid)` gives a second
  process access without copying any bytes — it just registers a second
  φ-address reference.
- **No fragmentation**: freed pages return to a sorted φ-address pool;
  `defragmentation_index()` is always 0.
- **Copy-on-write**: `write(page_id, data, writer_pid)` allocates a fresh
  φ-address for non-owner writers.

Capacity: **5476 pages** (= 74² = K_CS²).

### `UOS/security.py` — Geometric Isolation

Security is enforced by the **5:7 braid invariant**, not by permission walls.

The φ-fingerprint of any code block is:

```
φ_fingerprint = (Σ byte² mod K_CS) / K_CS
```

If this deviates from `INVARIANT_RATIO = 5/7 ≈ 0.7143` by more than the
tolerance, `SecurityViolation` is raised and the code cannot execute.

**Five isolation tiers** (= WINDING_NUMBER = n_w = 5):

| Tier | Name     | φ-deviation gate |
|------|----------|-----------------|
|  0   | Kernel   | exempt (seeds the manifold) |
|  1   | System   | < 10⁻⁶ |
|  2   | Trusted  | < 0.02 |
|  3   | Standard | < 0.02 |
|  4   | Sandbox  | < 0.02 |

### `UOS/filesystem.py` — Holographic Filesystem

Files are stored as **7-shard holographic projections** (one shard per
`UOS_FS_SHARDS = BRAID_PARTNER = 7` manifold dimension).

- Files are retrieved by **projection key** (content SHA-256 → K_CS), not by path.
- Any 4 of 7 shards reconstruct the full file (erasure tolerance = 3 lost shards).
- Identical content → identical projection key → automatic de-duplication.
- Data loss is physically impossible if ≥ 4 shards are intact.

### `UOS/driver_wrapper.py` — Universal 4D Hardware Wrapper

The KK dimensional reduction projects 5D intent vectors down to 4D hardware
signals:

```
signal[μ] = φ_scale × Σ_ν  intent[ν] × P[ν, μ]
```

where P is the (5×4) Kaluza–Klein projection matrix.  This means the UOS
can, in principle, drive **any** hardware by expressing its resource intent in
5D and projecting — no device-specific driver logic required.

74 hardware channels (`UOS_DRIVER_CHANNELS = K_CS`), supporting CPU, memory,
storage, network, and GPU resource classes.

---

## Quick Start

```python
from UOS import UOSHypervisor, GeodesicScheduler, ProcessGeodesic
from UOS import UnitaryMemory, GeometricSecurityEngine, HolographicFilesystem
from UOS import DriverWrapper
import numpy as np

# 1. Boot the hypervisor
hv = UOSHypervisor(n_grid=32)
hv.boot()

# 2. Run 10 clock ticks
snapshots = hv.run(steps=10)
print(hv.resource_report())

# 3. Schedule processes
sched = GeodesicScheduler()
sched.enqueue(ProcessGeodesic(pid=1, priority=0.9))
sched.enqueue(ProcessGeodesic(pid=2, priority=0.5))
next_proc = sched.next_process(snapshots[-1].phi)
print(f"Next process: PID {next_proc.pid}")

# 4. Allocate and share memory
mem = UnitaryMemory(n_pages=256)
page_id = mem.allocate(owner_pid=1, size_bytes=4096)
mem.write(page_id, np.arange(100, dtype=np.uint8), writer_pid=1)
mem.zero_copy_share(page_id, new_pid=2)   # zero-copy — no bytes moved
print(mem.stats())

# 5. Security check
sec = GeometricSecurityEngine()
sec.register(pid=1, tier=3, code_bytes=b"my process code")
print(sec.verify(pid=1))

# 6. Store a file holographically
fs = HolographicFilesystem()
key = fs.store("hello.txt", b"Hello, Manifold!")
print(fs.retrieve(key))

# 7. Hardware translation
dw = DriverWrapper()
dw.register_device(0, 'cpu', latency=0.05)
result = dw.execute(np.array([1.0, 0.5, 0.0, 0.0, 0.0]), 'cpu')
print(result['status'])  # 'dispatched'

# 8. Monitor mode: shadow your current OS
hv.attach_to_host(cpu_load=0.45, mem_load=0.60)
hv.tick()
print(hv.manifold_invariant_ok())
```

---

## Running the Tests

```bash
# UOS test suite only:
python -m pytest tests/test_uos_*.py -v

# Full repo regression (must include UOS with 0 failures):
python -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" omega/ -q
```

---

## Design Principles

| Principle | UOS implementation |
|-----------|-------------------|
| No legacy code | Built from scratch on UM geometry |
| Physical law as security | 5:7 braid invariant gate |
| Zero fragmentation | φ-address pool, always sorted |
| Zero-copy IPC | Manifold reference sharing |
| Predictive scheduling | Geodesic affinity score |
| Content-addressed storage | SHA-256 → K_CS projection key |
| Universal hardware | 5D→4D KK projection matrix |
| Monitor-mode compatible | `attach_to_host()` — runs beside existing OS |

---

## Constants (derived from the UM braid triad)

| Constant | Value | Meaning |
|----------|-------|---------|
| `WINDING_NUMBER` | 5 | Primary braid period; number of security tiers |
| `BRAID_PARTNER` | 7 | Secondary braid; number of FS shards |
| `K_CS` | 74 | = 5²+7²; process slots and driver channels |
| `BRAIDED_SOUND_SPEED` | 12/37 ≈ 0.3243 | Clock quantum (manifold time/tick) |
| `INVARIANT_RATIO` | 5/7 ≈ 0.7143 | Security gate target |
| `UOS_MEMORY_PAGES` | 74² = 5476 | Total memory pages |

---

## Relationship to the Unitary Manifold

The UOS shares the same geometric constants as the physics framework
(`WINDING_NUMBER`, `K_CS`, `PHI_BACKGROUND`, etc.) but does **not** depend
on the physics being correct.  It is an engineering framework that uses the
same mathematical structure — just as a GPS system uses general relativity
without claiming to be a physics experiment.

See `SEPARATION.md` for the precise boundary between physics claims and
engineering applications.
