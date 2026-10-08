# PsiCat Phase-Index ISA — Reference Specification (v0.1)

**Status:** 🔵 ADJACENT TRACK. Specification only. Nothing here describes existing hardware or claims a speedup.

## Purpose

PsiCat's toroidal navigation works on the integer phase lattice Z₇₄. A point on the circle is an index `k` in `0 … 73`; a point on the torus is a tuple of such indices. Every operation below is exact integer arithmetic. That exactness is the reason the specification targets phase indices rather than Cartesian fixed-point coordinates. The drift table in `PSICAT_TOROIDAL_NONSMOOTH_NAVIGATION.md` shows that Cartesian CORDIC accumulates error at every practical bit width. Phase-index rotation accumulates none.

The Python functions in `ox_navigator/engine/merlin_toroidal_geometry.py` are the golden model. Any re-implementation, whether in software, FPGA or RTL, is correct only if it reproduces `export_golden_vectors()` exactly. The tests pin the SHA-256 of the canonical vector set: `3aec49f2d748482657164ec8081157421b68e64397304107f99c8b5d34f2055d`.

## Operand format

Operands are 7-bit unsigned phase indices (`⌈log₂ 74⌉ = 7`), valid range `0 … 73`. Codes 74–127 are invalid. A conforming unit must reject or reduce them, and the reduction rule must be documented. The orbifold fixed points are 0 and 37. Index 37 is also the cut locus of every distance taken from 0.

## Operations

| Mnemonic | Semantics | Golden function |
|----------|-----------|-----------------|
| `PHROT a, b` | `(a + b) mod 74`, a rotation on the circle | `isa_phrot` |
| `PHNEG a` | `(−a) mod 74`, the S¹/Z₂ reflection; an involution fixing 0 and 37 | `isa_phneg` |
| `PHFOLD a` | `a` if `a ≤ 37`, else `74 − a`; projection to the orbifold fundamental domain | `orbifold_fold` |
| `PHDIST a, b` | `min(δ, 74 − δ)` with `δ = (a − b) mod 74`; geodesic distance on the circle | `circular_distance` |
| `PHSUB a, b` | 2-bit descent mask of `d(·, b)` at `a`: bit 0 means step −1 descends, bit 1 means step +1 descends; 0 means `a` is the minimum; 3 means `a` is on the cut locus, where both directions descend | `isa_phsub_mask` |
| `BANK a, b` | `(5a + 7b) mod 74`, the (5,7) braid bank of a 2-torus point | `braid_bank` |

`PHSUB` is the discrete counterpart of a Clarke generalised gradient. At the minimum and at the cut locus the Clarke gradient is the whole interval [−1, 1], so stationarity alone cannot tell them apart. The mask can: 0 at the minimum, 3 at the cut locus.

## Golden vector set

The sample indices are `0, 1, 5, 7, 24, 36, 37, 38, 50, 73`. They cover both fixed points, the braid windings, the Merlin tick step (24), and both neighbours of the cut locus. Binary operations are tabulated over all 100 ordered pairs and unary operations over all 10 samples, for 420 vectors in total. The canonical form is the JSON encoding with sorted keys and compact separators.

## What this specification does not claim

It does not claim that any of these operations is faster in hardware than in software. It does not claim that compute-in-memory or a custom core is warranted. It does not claim that the lattice improves Merlin's answers; the measured effects are reported in the design document. Its only purpose is to make sure that if a hardware path is ever taken, its correctness can be checked mechanically against a fixed reference.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
