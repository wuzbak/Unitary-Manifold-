# Omega Synthesis Peer Review — Chief Technology Architect

**Review Subject:** `omega/omega_synthesis.py` — Universal Mechanics Engine (Pillar Ω)  
**Repository:** `wuzbak/Unitary-Manifold-` (v9.29)  
**Reviewer Role:** Chief Architect, Technology and Emerging Systems  
**Date:** 2026-05-02  
**Disclosure:** AI-conducted review (GitHub Copilot). Does not substitute for independent human architectural review.

---

## Executive Summary

`omega/omega_synthesis.py` is the declared capstone of a 99-pillar physics framework: a single-class Python module that presents itself as a "Universal Mechanics Engine" capable of computing any observable of the universe from five seed constants. Architecturally, the module is well-structured, readable, and defensively coded. The test suite is comprehensive. The API design is clean and the public contract is well-documented.

However, several structural issues range from minor technical debt to a fundamental architectural mismatch between the module's self-description and its implementation. The most important issue: **the module is not a computational engine — it is a curated encyclopedia of hardcoded constants with a queryable interface.** This is not a criticism of its physics; it is a structural observation with significant implications for maintainability, reproducibility, and scientific integrity of the codebase.

This review categorizes findings from critical to minor, credits genuine strengths, and concludes with a prioritized set of recommendations.

---

## 1. Architecture and Design Patterns

### 1.1 Critical: The "Engine" Is a Constant Lookup Table

**Severity: CRITICAL (Architectural Fraud — not in intent, but in structure)**

The module's entire docstring, README, and CALCULATOR.md consistently describe `UniversalEngine` as an engine that *derives* observables from five seed constants. The architecture does not deliver this. Every domain method — `cosmology()`, `particle_physics()`, `geometry()`, `consciousness()`, `hils()` — assembles a frozen dataclass from pre-baked class-level constants. There is no computation at call time.

```python
# Lines 780–803: cosmology() does not derive anything
def cosmology(self) -> CosmologyReport:
    return CosmologyReport(
        n_s=self._N_S,           # pre-computed class constant
        r_bare=self._R_BARE,     # pre-computed class constant
        r_braided=self._R_BRAIDED,  # pre-computed class constant
        ...
    )
```

The "derivations" occur at class body execution time, when `_N_S`, `_R_BARE`, `_R_BRAIDED`, etc. are assigned as class attributes (lines 609–639). At runtime, calling `cosmology()` does nothing more than wrap those constants in a dataclass. The phrase "derived from five seed constants" is true in the abstract mathematical sense, but the derivation chain is invisible in this module — values for `_BETA_57_DEG = 0.331` (line 626), `_M_HIGGS_TREE_GEV = 143.0` (line 673), `_R_EGG_MICRON = 59.7` (line 710) are numeric literals with no derivation formula present in the source.

The `src/` modules contain the actual pillar implementations. This module contains none of their computational outputs via import; it duplicates them as magic numbers. **If a pillar implementation is updated in `src/`, this module will silently diverge without any automated check.**

**Recommendation:** At minimum, all constants that are claimed to be derivable should either (a) import from the authoritative source module, or (b) include an inline assertion that cross-validates the hardcoded value against the authoritative module. For example:

```python
# Proper synthesis pattern (illustrative):
from src.core.inflation import compute_ns
_N_S_AUTHORITATIVE = compute_ns(phi0_eff=_PHI0_EFF)
_N_S = _N_S_AUTHORITATIVE  # assert abs(_N_S - 0.9635) < 1e-4
```

Currently, `compute_n_s()` (line 1080) just returns `self._N_S` — which is `1.0 - 6.0 * _EPSILON + 2.0 * _ETA` computed at line 619. This one formula is legitimately derived from the seed constants. The same cannot be said for the birefringence values, the Higgs mass, the fermion bulk masses, the Wolfenstein ρ̄, or the egg cell radius.

---

### 1.2 Major: Zero Integration with the 99 Source Pillars

**Severity: MAJOR**

The module contains a single import group (lines 89–92):

```python
import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any
```

There are **no imports from `src/`**. A module that claims to synthesize 99 pillars does not import a single one of them. This creates a maintenance hazard of the first order. The entire value proposition of Pillar Ω — that it is the *convergence point* of the framework — is undermined when it is architecturally isolated from the rest of the framework.

The `omega/` package was presumably designed to avoid circular imports and provide a clean summary surface. That design goal is valid. But without cross-validation hooks, there is no guarantee of consistency. The tests in `test_omega_synthesis.py` test only internal consistency of `omega_synthesis.py` against itself — not against the authoritative `src/` implementations.

---

### 1.3 Minor: `OmegaReport` Is Not Frozen

**Severity: MINOR**

Lines 475–505 define `OmegaReport` with `@dataclass` (mutable), while the five domain reports all use `@dataclass(frozen=True)`. This inconsistency means the aggregate report can be mutated after construction:

```python
report = engine.compute_all()
report.cosmology = None  # valid Python, silently corrupts the report
```

The `field(default=None)` pattern on lines 497–501 combined with `# type: ignore[assignment]` is a further code smell. The proper pattern is `Optional[CosmologyReport] = None` with explicit `Optional` types, or — better — make all fields required (since `compute_all()` always populates them).

**Recommendation:** Either use `@dataclass(frozen=True)` on `OmegaReport`, or add a `__post_init__` validation that asserts all domain reports are non-None if `compute_all()` is the only intended construction path.

---

### 1.4 Minor: Class Attribute Shadowing of Module-Level Constants

**Severity: MINOR**

Lines 599–604 define class attributes that shadow module-level constants:

```python
class UniversalEngine:
    N_W = N_W    # class attribute shadows module-level N_W
    N_2 = N_2
    K_CS = K_CS
    C_S = C_S
    XI_C = XI_C
```

This is redundant. The class already has direct access to the module-level constants. The shadowing pattern creates a false impression of encapsulation and opens the door to subtle divergence if a subclass overrides them. The `_stability_floor` classmethod (line 1204) references `cls.N_2`, which would silently use a subclass-overridden value — probably unintended.

---

### 1.5 Minor: Mutable Class-Level List (`_OPEN_GAPS`)

**Severity: MINOR**

Line 739 defines `_OPEN_GAPS: list[str] = [...]` as a class-level mutable list. This is shared across all instances. In CPython, this is safe as long as no code calls `_OPEN_GAPS.append()` or mutates it. But it is a recognized Python anti-pattern. It should be a `tuple` or annotated as `ClassVar[tuple[str, ...]]`.

---

## 2. Specific Code Issues

### 2.1 Critical: Unit Naming Bug — `_SUM_MNU_MEV`

**Severity: CRITICAL (silent wrong-unit storage)**

Line 664:
```python
_SUM_MNU_MEV: float = 62.4e-3  # Σm_ν in meV converted to MeV for storage
```

This stores `0.0624`. The comment claims "meV converted to MeV for storage" — meaning the intent is to store `62.4 meV` as `0.0000624 MeV`. But `62.4 meV = 0.0624 eV = 6.24e-5 keV = 6.24e-8 MeV`, not `6.24e-2 = 0.0624`. 

What the code actually stores is `0.0624` in **eV** (not MeV), which it then converts at line 830:
```python
sum_mnu_mev=self._SUM_MNU_MEV * 1e3,  # convert MeV→meV for display
```
The multiplication by `1e3` produces `62.4`, which is labeled as "meV" in the display — and `62.4 meV` is physically correct. But the comment "convert MeV→meV" is wrong: `0.0624 × 1e3 = 62.4 eV`, not meV. Or: if the stored value truly is in MeV, then `0.0624 MeV × 1e3 = 62.4 keV`, which is wrong for neutrino masses.

The correct interpretation: `_SUM_MNU_MEV` is stored in **eV** (its value is 0.0624 eV = 62.4 meV), and the ×1e3 converts eV → meV. The variable should be named `_SUM_MNU_EV` or `_SUM_MNU_MEV_DISPLAY_DIVISOR`. As written, the comment is self-contradictory and the variable name is incorrect.

The falsifier at line 1007 also displays `self._SUM_MNU_MEV * 1e3` meV = 62.4 meV, which is numerically correct, but anyone reading the code will be confused.

---

### 2.2 Major: Dead Code — `_ALPHA_INVERSE` (Line 688)

**Severity: MAJOR**

```python
_ALPHA_INVERSE: float = float(Fraction(N_W, 1)) * 2 * math.pi  # φ₀_eff² ≈ 987
```

This computes `5 × 2π ≈ 31.416`, which equals `_PHI0_EFF` (line 611) and `_J_KK` (line 609). The comment is also wrong: `31.416² ≈ 987`, not `α⁻¹`. The actual `α⁻¹ = 137.036` is stored separately as `_ALPHA_INVERSE_QED` (line 692), which is what `geometry()` returns (line 856). `_ALPHA_INVERSE` is never referenced again in the file. This is dead code that introduces naming confusion: `_ALPHA_INVERSE` computes the inflaton VEV, not the fine structure constant.

---

### 2.3 Major: Module-Level Dead Variables

**Severity: MAJOR**

Lines 121–122 define:
```python
_BETA_COUPLING_DEG: float = 0.3513
_BETA_COUPLING_RAD: float = math.radians(_BETA_COUPLING_DEG)
```

These module-level private variables are never referenced by `UniversalEngine`. The class uses its own class-level equivalents `_BETA_COUP_DEG` (line 701) and `_BETA_COUP_RAD` (line 702). The module-level definitions are **dead code** — duplicate state that diverges silently if one is updated and the other is not.

---

### 2.4 Major: Pillar Count Inconsistency in Source

**Severity: MAJOR (documentation / reproducibility)**

The `unitary_summation()` method (line 1042) returns a string stating:
```
"12. [Pillar Ω] All 98 pillars converge in the Universal Mechanics Engine..."
```

But `DEFAULT_N_PILLARS = 99` (line 593) and the `OmegaReport.n_pillars` field description says "99 + sub-pillars." The `compute_all()` call at line 1062 passes `n_pillars=self.n_pillars` (= 99), yet the canonical Unitary Summation text says "98." This discrepancy is baked into the text of Step 12 and will not change unless the string literal is updated.

---

### 2.5 Minor: `_OPEN_GAPS` References Stale Admission Numbering

**Severity: MINOR**

`_OPEN_GAPS[0]` (line 741) cites "Admission 2" for the CMB amplitude gap:
```
"...overall amplitude gap unresolved — Admission 2"
```

However, `FALLIBILITY.md` Section 3.2 (lines 106–164) labels:
- **Admission 1**: n_w = 5 observational selection
- **Admission 2**: k_CS = 74 algebraic derivation

The CMB amplitude gap is not "Admission 2" — it was admission 2 in an earlier version. This creates a stale cross-reference that will mislead readers who check `FALLIBILITY.md`.

---

### 2.6 Minor: `_WOLF_RHO_BAR` Is Borrowed from PDG, Not Derived

**Severity: MINOR (honesty / labeling)**

Line 653:
```python
_WOLF_RHO_BAR: float = 0.159  # (PDG value used as cross-check)
```

The comment is honest, but the value is included in `ParticlePhysicsReport.wolfenstein_rho_bar` without any annotation in the report dataclass that distinguishes it from derived quantities. The field docstring at line 225 says only "Wolfenstein ρ̄ (PDG 0.159)" — not "PDG-input, not derived." This inconsistency with the module's "everything derived from five seeds" claim should be explicitly flagged in the report docstring.

---

### 2.7 Minor: Version String Inconsistency Within the Module

**Severity: MINOR**

The module-level docstring (line 8) says `DEFAULT_VERSION = "v9.27 OMEGA EDITION"` (comment in docstring text implies v9.27), but line 592 sets `DEFAULT_VERSION = "v9.28 OMEGA EDITION"`, and line 594 sets `DEFAULT_N_TESTS = 15296` described as "v9.29 count." The README.md also says "v9.27 OMEGA EDITION." Three different version identifiers appear in adjacent files. Given that this module is the "final synthesis," having a stale version reference in its own docstring undermines reproducibility.

---

## 3. Test Architecture and Coverage

### 3.1 Comprehensive Coverage of Public Contract

The test file (`test_omega_synthesis.py`) delivers 168 tests across 10 sections (A–J), covering:

- Seed constant exactness (Section A: 15 tests)
- Cosmological observables (Section B: 26 tests, including convenience methods)
- Particle physics (Section C: 25 tests)
- Geometry (Section D: 15 tests)
- Consciousness/biology (Section E: 15 tests)
- HILS/Pentad dynamics (Section F: 22 tests)
- Falsifiers (Section G: 15 tests)
- Unitary Summation (Section H: 10 tests)
- OmegaReport integration (Section I: 15 tests)
- Edge cases (Section J: 10 tests)

The breadth is impressive. Every public method is exercised. Error cases (invalid `phi_trust`, negative `n_hil`, invalid `compute_beta` sector) are covered. The `monotone` property of the stability floor is verified (Section F, `test_stability_floor_monotone`). Idempotency of `compute_all()` is tested.

### 3.2 Major Gap: Tests Are Snapshot Tests, Not Derivation Tests

**Severity: MAJOR**

The tests confirm that the module returns what it has always returned. They do not test that the values are *correctly derived*. Consider:

```python
def test_n_s_approx_0_9635(self, cos):
    assert abs(cos.n_s - 0.9635) < 0.001
```

This test passes whether `_N_S` is correctly derived from slow-roll or hardcoded as `0.9635`. In fact, the tests for `n_s` would pass even if someone replaced the derivation formula with `_N_S = 0.9635` (a magic constant). The `_N_S` at line 619 is one of the few values that IS computed inline, but the test doesn't exercise the computation chain — it only checks the final float.

More importantly: `compute_n_s()` returns `self._N_S` (line 1082), which is a pre-baked class constant. The test:
```python
def test_compute_n_s_method(self, engine):
    assert engine.compute_n_s() == engine.cosmology().n_s
```
is tautologically true by construction — both calls return the same class constant. It tests that `compute_n_s()` and `cosmology().n_s` call the same variable, not that either value is correct.

**Recommendation:** Add at least one cross-validation test per domain that imports from `src/` and asserts numerical agreement:

```python
# Cross-validation test (illustrative):
def test_n_s_agrees_with_src():
    from src.core.inflation import compute_ns
    from omega.omega_synthesis import UniversalEngine, _PHI0_EFF
    expected = compute_ns(_PHI0_EFF)
    assert abs(UniversalEngine().compute_n_s() - expected) < 1e-6
```

### 3.3 Minor: No Property-Based Tests

**Severity: MINOR**

The HILS domain has state parameters (`phi_trust`, `n_hil`). The tests exercise a handful of discrete values. Property-based tests (e.g., using Hypothesis) would cover the continuous parameter space and find edge cases like floating-point boundary conditions around `phi_trust = float(C_S)` (the trust threshold).

### 3.4 Minor: `_stability_floor` Tested as Classmethod Directly

**Severity: MINOR**

`test_stability_floor_formula` (line 973) calls `UniversalEngine._stability_floor(n)` directly, bypassing the instance method. This tests an implementation detail. If the method were refactored to an instance method, this test would break at the test level, not at the API level. Prefer testing through the public interface.

---

## 4. API Design

### 4.1 Strength: Clean Public Contract

The API is well-designed for its stated purpose as a calculator. The six domain methods return frozen, self-describing dataclasses. The `compute_all()` master entry point is clearly named. The convenience calculator methods (`compute_n_s()`, `compute_beta()`, etc.) are appropriately thin wrappers. The immutable update pattern (`update_trust()`, `update_hil()`) returns new engine instances — correct for functional-style state management.

The `FalsifiablePrediction` dataclass is an excellent design choice. It makes falsifiability a first-class citizen of the API rather than a documentation artifact.

### 4.2 Major: No Serialization Support

**Severity: MAJOR (production-readiness)**

For a "universal mechanics engine" intended as an API and calculator, the frozen dataclasses offer no serialization path. `dataclasses.asdict()` would work on the leaf dataclasses, but `OmegaReport` (not frozen, containing `Fraction` objects and nested structures) would require custom handling.

For any downstream use — REST API, Jupyter notebook, logging, reproducibility records — users need `to_dict()`, `to_json()`, or at minimum documented guidance on how to serialize outputs. The `Fraction` fields (`xi_c`, `xi_human`, `omega_ratio`) are not JSON-serializable without conversion.

**Recommendation:** Add a `to_dict() -> dict[str, Any]` method to `OmegaReport` and all domain reports. Consider a `jsonable()` helper that converts `Fraction` to float for serialization contexts.

### 4.3 Minor: `compute_beta` Parameter Naming

**Severity: MINOR**

```python
def compute_beta(self, sector: int = 7) -> float:
```

The parameter name `sector` means "the second winding number of the braid pair." This is not obvious to a first-time user. The docstring says "Braid partner winding number: 7 for (5,7), 6 for (5,6)" — but `sector` is commonly used to mean something broader. A name like `n2` or `braid_partner` would be clearer.

### 4.4 Minor: No `__all__` in `omega_synthesis.py`

**Severity: MINOR**

The module-level namespace is crowded with private helpers (`_C_S_FLOAT`, `_C_S_SQ`, `_XI_C_FLOAT`, `_XI_HUMAN`, `_BETA_COUPLING_DEG`, `_BETA_COUPLING_RAD`) defined at lines 117–122. None of these appear in `__all__` (which is defined in `__init__.py`), but the module itself has no `__all__`. Any `from omega.omega_synthesis import *` would export all public names. The private-prefix convention provides some protection, but explicit `__all__` at the module level is best practice.

---

## 5. Scalability and Production-Readiness

### 5.1 No Async Support

For a calculator engine intended for API deployment, every domain method is synchronous. For the current use case (all values are pre-baked constants), this is adequate. But if the architecture evolves toward on-demand computation from `src/` modules (see §1.1), some computations (e.g., Richardson extrapolation, fixed-point iteration) may require async execution.

### 5.2 No Logging

The module does not use Python's `logging` module. This is acceptable for a pure computation library. The `__main__` entry point (`_print_omega_synthesis()`) prints directly to stdout. For production use, consider `logging.getLogger(__name__)` for diagnostic output.

### 5.3 No Type Stubs

The module uses `from __future__ import annotations` (line 77), enabling PEP 563 postponed evaluation. However, the `Any` import (line 92) is unused in the current code — `Any` appears only in `_OPEN_GAPS: list[str]` which doesn't need it, and the `OmegaReport.to_dict()` that doesn't exist yet. The unused import is minor technical debt.

### 5.4 No OpenAPI/Schema Definition

For deployment as a service, `OmegaReport` and domain reports need schema definitions (JSON Schema, Pydantic models, or Dataclasses-JSON annotations). The `9-INFRASTRUCTURE/schema.jsonld` file suggests the repository has a metadata schema, but `omega/` is not represented in it.

---

## 6. Versioning and Scientific Reproducibility

### 6.1 Critical: Test Count Is a Static Hardcoded Value

**Severity: CRITICAL (reproducibility)**

Line 594:
```python
DEFAULT_N_TESTS = 15296  # v9.29 count: 15,296 passed, 330 skipped, 0 failed
```

The engine reports `n_tests_passing=15296` as a fact in `OmegaReport`. This number is hardcoded, not dynamically queried from the test suite. When new tests are added, `DEFAULT_N_TESTS` must be manually updated. If it isn't, the engine reports an incorrect test count.

This may seem cosmetic, but it is a reproducibility issue: a reader who queries the engine and gets `n_tests_passing=15296` cannot trust that number without running the suite independently. The engine should either (a) not report this number (it's a repository property, not a physics result), or (b) compute it dynamically via `subprocess` or `pytest` API calls in a separate metadata function.

### 6.2 Major: `version` Parameter Is Both Overridable and Hardcoded

**Severity: MAJOR (reproducibility)**

The `version` parameter defaults to `DEFAULT_VERSION = "v9.28 OMEGA EDITION"` but can be overridden by the caller:

```python
engine = UniversalEngine(version="SPOOFED")
report = engine.compute_all()
assert report.version == "SPOOFED"  # passes
```

Since `OmegaReport.version` is the reported identity of the framework, allowing arbitrary override creates reproducibility risk. Downstream users who record `report.version` as provenance metadata may record a spoofed value.

**Recommendation:** Either remove the `version` parameter from `__init__` and derive it from a module-level constant only, or add a `validated` annotation to reports that were created with the canonical version string.

### 6.3 Minor: The `__provenance__` Pattern Is Excellent But Partial

The `__provenance__` dict (lines 79–87 in the module, and duplicated in `__init__.py` and `test_omega_synthesis.py`) is an excellent pattern for attribution. However, it is not queryable through the `UniversalEngine` API — there is no `engine.provenance()` method. The `OmegaReport` does not include provenance metadata. For maximum reproducibility, provenance should be a first-class field of `OmegaReport`.

---

## 7. Security and Dependency Hygiene

### 7.1 Dependency Surface

`requirements.txt` specifies: `numpy>=1.24,<3`, `scipy>=1.11,<2`, `pytest>=7.0,<9.1`, `mpmath>=1.3,<2`, `matplotlib>=3.7,<4`, `sympy>=1.12,<2`.

`omega_synthesis.py` imports none of these — only `math`, `dataclasses`, `fractions`, and `typing` from the standard library. This is architecturally clean for a summary/synthesis module. The dependency surface is zero for this specific module. From a security standpoint, there are no concerns specific to `omega/`.

### 7.2 No Executable User Input

The module takes only two numeric parameters (`phi_trust`, `n_hil`) with explicit range validation. There is no eval, no subprocess, no file I/O, no network calls. The attack surface is effectively zero.

---

## 8. Integration Patterns and Interoperability

### 8.1 The Module Is an Island

As noted in §1.2, the module imports nothing from `src/`. This makes it maximally independent but also maximally isolated. The `omega/` package is documented as the "capstone" of 99 pillars, but at the code level it is architecturally disconnected from all of them.

For downstream integration (MCP tools, Jupyter notebooks, API deployments), the isolation is actually a feature — users get a single import with no transitive dependency on the large `src/` tree. But for internal repository integrity, it is a liability.

**Recommendation:** Introduce an optional `validate_against_src=True` mode that, on first construction, imports authoritative values from `src/` and asserts agreement with the hardcoded constants. This would be gated behind a flag to avoid import overhead for production use.

### 8.2 MCP/LLM Readiness

The `__init__.py` exposes all public symbols cleanly. The `OmegaReport.summary()` method (lines 507–558) produces well-formatted text suitable for LLM consumption. The `FalsifiablePrediction.falsified_if` field is particularly valuable for AI-assisted validation pipelines.

The missing serialization (§4.2) is the primary gap for MCP integration. Without `to_dict()` or JSON-compatible serialization, piping an `OmegaReport` through an MCP tool requires manual conversion.

---

## 9. Genuine Strengths (Unconditional Credit)

The following design decisions are architecturally sound and merit explicit recognition:

1. **Frozen dataclasses for all domain reports** (except `OmegaReport` — see §1.3): Immutable science results are the correct default. This prevents accidental mutation and makes reports safe to pass across code boundaries.

2. **`Fraction` arithmetic for seed constants**: `C_S = Fraction(12, 37)` and `XI_C = Fraction(35, 74)` provide exact rational arithmetic where it matters. The test `test_c_s_exact_fraction` (line 84) correctly verifies the reduced form `12/37`, not the unreduced `24/74`. This is precise scientific computing practice.

3. **`FalsifiablePrediction` as a first-class type**: Making falsifiability structurally queryable (`engine.falsifiers()`) rather than a comment in documentation is an excellent design choice. It means falsifiability can be tested, iterated, and checked programmatically.

4. **Immutable state update pattern**: `update_trust()` and `update_hil()` return new engine instances rather than mutating state. This is correct functional design for a computational engine.

5. **Input validation in `__init__`**: `phi_trust ∈ [0, 1]` and `n_hil ≥ 0` are explicitly validated with informative error messages. This is production-quality defensive coding.

6. **`__provenance__` metadata dict**: Embedding structured provenance (author, DOI, license, fingerprint) at the module level is a reproducibility best practice that goes beyond what most scientific code achieves.

7. **Honest gap accounting**: `_OPEN_GAPS` (line 739) and `OmegaReport.open_gaps` make the theory's unresolved problems a queryable property of the engine itself. This is epistemically courageous and architecturally correct.

8. **SPDX license headers** on every `.py` file: Legal hygiene, correctly implemented.

9. **`compute_all()` as a single entry point**: The master computation gathers all six domains in one call and returns a complete, self-describing report. This is the correct design for a scientific calculator API.

10. **`__repr__`**: Informative, includes all state-bearing parameters, compatible with standard Python tooling.

---

## 10. Summary of Findings

| # | Issue | Severity | Section |
|---|-------|----------|---------|
| 1 | Engine is a constant lookup, not a computational engine; no integration with `src/` | CRITICAL | §1.1, §1.2 |
| 2 | Unit naming bug: `_SUM_MNU_MEV` stores eV, not MeV | CRITICAL | §2.1 |
| 3 | `DEFAULT_N_TESTS` is hardcoded static; will silently drift | CRITICAL | §6.1 |
| 4 | Tests are snapshot tests, not derivation tests | MAJOR | §3.2 |
| 5 | Dead code: `_ALPHA_INVERSE` computes VEV, never used | MAJOR | §2.2 |
| 6 | Dead code: module-level `_BETA_COUPLING_DEG/RAD` duplicated by class attrs | MAJOR | §2.3 |
| 7 | Pillar count: Step 12 of Unitary Summation says "98 pillars" vs DEFAULT=99 | MAJOR | §2.4 |
| 8 | No serialization support; `Fraction` fields not JSON-serializable | MAJOR | §4.2 |
| 9 | `version` parameter is caller-overridable; spoofable provenance | MAJOR | §6.2 |
| 10 | `OmegaReport` is mutable; inconsistent with frozen domain reports | MINOR | §1.3 |
| 11 | Class attribute shadowing of module-level constants (`N_W = N_W`, etc.) | MINOR | §1.4 |
| 12 | `_OPEN_GAPS` is mutable class-level list | MINOR | §1.5 |
| 13 | Stale Admission numbering in `_OPEN_GAPS[0]` vs FALLIBILITY.md | MINOR | §2.5 |
| 14 | `_WOLF_RHO_BAR` is PDG input, not labeled as such in report docstring | MINOR | §2.6 |
| 15 | Version string inconsistency across module, README, CALCULATOR.md | MINOR | §2.7 |
| 16 | No `__all__` in `omega_synthesis.py` | MINOR | §4.4 |
| 17 | `Any` import is unused | MINOR | §5.3 |
| 18 | `__provenance__` not queryable through engine API | MINOR | §6.3 |

---

## 11. Prioritized Recommendations

**P0 (Fix before any production deployment):**
1. Rename `_SUM_MNU_MEV` → `_SUM_MNU_EV` and fix the conversion comment (§2.1)
2. Remove or comment `_ALPHA_INVERSE` dead code (§2.2)
3. Remove module-level `_BETA_COUPLING_DEG` / `_BETA_COUPLING_RAD` duplicates (§2.3)

**P1 (Fix before next version milestone):**
4. Freeze `OmegaReport` or add `__post_init__` validation (§1.3)
5. Fix pillar count in `unitary_summation()` Step 12 (§2.4)
6. Fix stale "Admission 2" cross-reference in `_OPEN_GAPS[0]` (§2.5)
7. Add `to_dict()` / JSON serialization to all report types (§4.2)
8. Remove `version` from `__init__` parameters or make it read-only from a module constant (§6.2)

**P2 (Architectural improvement, next major version):**
9. Add cross-validation assertions against `src/` authoritative modules at engine construction time (§1.1, §1.2)
10. Add derivation-level tests that import from `src/` and check numerical agreement with `omega/` values (§3.2)
11. Make `DEFAULT_N_TESTS` dynamic, or remove it from `OmegaReport` (§6.1)
12. Add `engine.provenance()` method returning `__provenance__` dict (§6.3)

---

## 12. Closing Assessment

`omega/omega_synthesis.py` is a well-crafted, readable, and well-tested module. Its API design is clean, its documentation is thorough, and its commitment to honest gap accounting is exemplary. The frozen dataclass pattern, exact rational arithmetic, and first-class falsifiability make it a high-quality scientific software artifact.

The module's core deficiency is the gap between its aspirational description ("derives everything from five seeds") and its architectural reality (a curated constant store). For the current codebase stage — research software with a clean internal test suite — this gap is acceptable and arguably pragmatic. For any future deployment as an API, MCP tool, or collaborative scientific instrument, the isolation from `src/` becomes a maintenance liability that will compound with each new pillar.

The unit bug in `_SUM_MNU_MEV` should be fixed immediately; it does not affect numerical outputs (the displayed value is correct) but represents a maintenance hazard for anyone who reads the internal variable directly. The dead code should be cleaned for the same reason.

Overall rating as a research codebase artifact: **solid, with well-documented intent and well-exercised behavior, but architecturally brittle at the integration boundary.** The engine is credible as a reference implementation of the framework's claims. It is not yet credible as a self-validating synthesis of the pillar implementations it claims to unify.

---

*Review conducted by GitHub Copilot (AI) in the role of simulated Chief Technology Architect.*  
*Theory and scientific direction: ThomasCory Walker-Pearson.*  
*Part of the Omega Peer Review suite (2026-05-02), `3-FALSIFICATION/OMEGA_PEER_REVIEW_2026-05-02/`.*
