# src/cold_fusion — φ-Enhanced Tunneling (TIER 2)

**Epistemic status: Speculative physics extension — internally consistent; experimentally contested domain**

Implements Pillar 15: anomalous heat production in deuterium-loaded palladium
modeled via φ-field enhancement of the Gamow tunneling exponent.

## What this is

If the φ field increases coherence length in the Pd lattice, the D+D reaction
tunneling probability is modified.  This module computes the expected COP and
anomalous heat significance σ under that assumption.

## What this is NOT

This is not a claim that cold fusion is a confirmed phenomenon.  The
experimental evidence for anomalous heat in Pd/D systems is contested in the
mainstream physics community.  This module provides a *first-principles
account of the magnitude* of the effect *if* the observations are real.

## Tests

```bash
python -m pytest tests/test_cold_fusion.py -v
```
