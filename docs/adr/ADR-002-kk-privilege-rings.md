# ADR-002: KK-Mapped Privilege Rings for AZ-OS

**Date:** 2026-08-18
**Status:** Accepted
**Deciders:** ThomasCory Walker-Pearson, GitHub Copilot (AI)

---

## Context

The AZ-OS bare-metal kernel needs a security model for process isolation.
Standard OS ring models (0–3, kernel to user) are based on arbitrary
engineering convention.  AZ-OS requires a principled model derived directly
from the underlying physics framework.

## Decision

Map the 5 Kaluza-Klein extra-dimension privilege rings directly to OS security rings:

| KK concept | AZ-OS ring |
|---|---|
| Fiber bundle — 5 KK extra dimensions | 5 privilege rings (KK levels 0–4) |
| Winding number n_w = 5 | 5 interrupt priority rings |
| k_cs = 74 = 5² + 7² | 74 pages per compactification domain |
| KK adjacency rule | IPC rule: only adjacent rings may communicate |
| φ-debt entropy (Pillar 16) | Memory eviction: evict lowest φ-debt pages first |
| Holographic boundary (Pillar 4) | IPC channel interface boundary |
| Pentad clearance bits | Process security descriptor |

## Rationale

1. **Principled derivation.** Every security property is a theorem of the KK
   geometry, not an engineering choice.
2. **IPC type safety.** The adjacency rule is enforceable at compile time using
   Rust newtypes for each ring level — cross-ring violations are caught before
   runtime.
3. **Memory management.** φ-debt scoring gives a physics-grounded eviction policy
   that is more predictable than LRU alone.

## Consequences

* **Positive:** Security model is formally derivable and falsifiable.
* **Positive:** Compile-time IPC safety prevents entire class of privilege-escalation bugs.
* **Negative:** 5-ring model is less standard than 4-ring x86; kernel developers need
  to understand the KK geometry to reason about security.
* **Negative:** φ-debt eviction requires tracking per-page entropy state; adds ~8 bytes/page overhead.

## Implementation notes

The adjacency rule: process at ring `i` may send IPC messages only to rings
`i-1` and `i+1` (modulo 5 for ring 0 and ring 4, with special kernel-bypass
for emergency signals).

*Theory: ThomasCory Walker-Pearson. Code: GitHub Copilot (AI).*
