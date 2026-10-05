# src/atomic_structure — Atomic Structure as KK Winding Modes (TIER 2)

**Epistemic status: Speculative physics extension — internally consistent; NOT empirically confirmed**

Implements Pillar 14: hydrogen energy levels, orbital radii, fine structure,
Lamb shift, and hyperfine splitting derived from Kaluza–Klein mode quantisation.

## What this is

A consequence of Tier 1: if KK winding modes govern atomic-scale physics,
the hydrogen spectrum should emerge from mode counting.  The Rydberg constant
and fine-structure constant α_em are not derived here from first principles —
they are correctly computed from standard formulae applied within the φ-field
context.

## What this is NOT

This is not a derivation of atomic structure from scratch.  Existing quantum
mechanics (Schrödinger/Dirac equations) already explain atomic spectra to
extraordinary precision.  This module shows consistency, not superiority.

## Tests

```bash
python -m pytest tests/test_atomic_structure.py -v
```
