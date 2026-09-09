# Braid Correspondence Audit — External Topology Objects vs the Canonical (5,7) Chain

**Status:** Canonical audit ledger for braid correspondences  
**Theory:** ThomasCory Walker-Pearson  
**Documentation:** GitHub Copilot (AI)  
**Purpose:** Record which external braid/topology objects genuinely map onto the repository's canonical \((5,7)\) machinery, which are partial analogies, and which remain open or non-canonical.

---

## 1 · Audit rule

An external object counts as a real correspondence only if it preserves the internal role of the repository object it is being mapped to. In practice that means a proposed bridge must do more than share numbers or words. It must preserve the relevant invariant, remain compatible with the repository's \(S^1/Z_2\), APS, and Chern-Simons machinery, and strengthen or clarify the current proof path rather than merely decorate it.

The working rule is therefore:

> **Name overlap is not enough. Numerical overlap is not enough. Structural overlap is not enough unless the operational role is preserved.**

---

## 2 · Canonical internal targets

The braid lane in this repository is currently organized around the following internal targets:

- odd winding under the orbifold structure,
- candidate narrowing for the winding sector,
- the executable braid pair \((5,7)\),
- the algebraic level \(k_{\rm CS}=74\),
- the braided sound speed \(c_s=12/37\),
- the linked observables \(n_s\), \(r\), and \(\beta\),
- and the internal early-universe layering / resonance-locking picture.

Any external correspondence is judged against those targets.

---

## 3 · Ledger

| External object | Proposed internal counterpart | Invariant or role that would need to match | Current verdict | Why |
|-----------------|-------------------------------|--------------------------------------------|-----------------|-----|
| Coprime torus-knot pair \(T(5,7)\) | Working braid pair \((5,7)\) | Coprime closure / single connected winding sector | **PARTIAL — descriptive only** | Safely describes a coprime two-integer winding pair, but does not itself derive the repo's orbifold selection or observable chain |
| Braid group on five strands | Winding-sector combinatorics | Explicit braid operations must reproduce the repo's admissible sector structure | **OPEN** | No canonical repo theorem currently identifies braid-group generators with the internal selection machinery |
| Braid word \((\sigma_1\sigma_2\sigma_3\sigma_4)^7\) | Executable \((5,7)\) sector | The exact word would need to map to the internal \(S^1/Z_2\) / APS / CS operators | **OPEN — not mapped** | The repo does not currently prove this exact word is the operative internal object |
| Coprimality of 5 and 7 | Single connected topological sector | Must explain or reproduce the internal exclusion structure | **PARTIAL** | Good intuition for connectedness, but not a substitute for the internal orbifold/selection arguments |
| Generic Chern-Simons invariant in 3-manifold topology | Repo \(k_{\rm CS}\) level | Must reproduce the same role as the executable \(k_{\rm CS}\) machinery | **PARTIAL / term overlap** | Similar vocabulary is present, but equivalence of meaning is not yet proved |
| APS \(\eta\)-invariant from geometric analysis | Repo APS-based winding selection | Spectral-asymmetry role must match directly | **STRONG INTERNAL CORRESPONDENCE** | APS already functions as an internal object in the repository rather than an outside analogy |
| Brieskorn manifold \(\Sigma(2,5,7)\) | Braid/compactification sector | Must map to the canonical 5D/orbifold structure and improve the internal derivation chain | **OPEN** | No canonical theorem-level bridge yet exists |
| Poincaré-sphere or homology-sphere cosmology | Early-universe layering picture | Must preserve the internal Big Bang layering mechanics and falsifier structure | **OPEN / non-canonical** | At present this is a comparison class, not the source of the repo's early-universe mechanism |
| Exotic Planck-scale 4-manifold proposals | 5D KK + orbifold + radion framework | Must explain why a 4-manifold model reproduces the repo's 5D-specific structure | **MODEL-DISTINCT** | Similar ambition does not imply same mechanism |
| Knot invariants such as Alexander/self-linking data | Observable-locking braid fingerprints | Must feed or constrain \(k_{\rm CS}\), \(c_s\), or the admissible sector list | **PROMISING BUT OPEN** | The repo contains torus-knot-related utilities, but no canonical dependence of the core observables on these invariants is yet established |
| External Big Bang topology story | `src/multiverse/layering.py` resonance-locking event | Must reproduce the same energy partition and sector logic | **OPEN** | The repository already has an internal executable model; outside stories must meet that bar to count as bridges |

---

## 4 · Failure modes

Most correspondence proposals fail in one of four ways:

1. **Same numbers, different job**  
   The external object contains 5 and 7, but those numbers do not play the same role they play in the repository.

2. **Same vocabulary, different invariant**  
   Terms such as "Chern-Simons," "braid," or "Poincaré" appear in both places, but the conserved quantity or spectral statement is not the same.

3. **Same intuition, no operator map**  
   The outside picture feels compatible but does not identify which internal operator, boundary condition, or algebraic relation it reproduces.

4. **Same ambition, different model class**  
   Another cosmological topology model may also target the early universe, but it does not follow that it is part of the Unitary Manifold proof path.

These are reasons to slow down, not reasons to discard the research lane.

---

## 5 · What would upgrade a verdict

An OPEN or PARTIAL item should only be upgraded if a future derivation does at least one of the following:

- reproduces the admissible \((5,7)\) sector structure from the external object,
- preserves the same parity/boundary data as the internal \(S^1/Z_2\) machinery,
- recovers the same \(k_{\rm CS}\) role rather than merely the same number,
- sharpens the current falsifier logic instead of bypassing it,
- or resolves an already named open obligation in the canonical truth/fallibility layer.

If none of these occurs, the item remains descriptive or comparative only.

---

## 6 · Operational use rule

Use this audit when writing, reviewing, or extending braid-facing material:

- **STRONG INTERNAL CORRESPONDENCE** items may be discussed as part of the repo's working chain.
- **PARTIAL** items may be used as language or intuition, but not as closure.
- **OPEN** items belong to a research lane and must be labelled that way.
- **MODEL-DISTINCT** items may be compared, but not merged into the canonical derivation without a new proof.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
