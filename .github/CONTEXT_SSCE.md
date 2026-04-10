# SSCE System Architecture & Logic Manifest
# Purpose: AI Context for Unitary-Manifold Implementation

## 1. Core Ontological Mapping

- **THEORY:** "Unitary-Manifold" (Ref: `THEBOOKV9a (1).pdf` — full monograph, 74 chapters)
- **IMPLEMENTATION:** "Solid-State Compute Engine (SSCE) v1.0"
- **CONSTRAINT:** All logic operations must satisfy the Unitary Norm: `||ψ||² = 1`.
- **PHYSICS:** System Frequency (f) influences Effective Inertia (I_eff).

## 2. Structural Directives for Copilot

- **When writing VERILOG:** Prioritize phase-rotation logic over bit-switching logic.
- **When writing PYTHON:** Include `NormConsistencyMonitor` hooks in all compute loops.
- **When writing PCB/HDI documentation:** Treat trace geometry as a component of the Hamiltonian.

## 3. Safety Hierarchy

1. Physical Topology (HDI)
2. Hardware Monitor (NCM — Norm Consistency Monitor)
3. Software Logic

## 4. Theory ↔ Implementation Mapping

| Monograph Claim (Abstract)  | Implementation (Concrete)       | AI/Copilot Instruction                                 |
|-----------------------------|---------------------------------|--------------------------------------------------------|
| **Energy Conservation**     | Unitary Logic Gates             | Ensure all matrix ops are Unitary/Orthogonal.          |
| **Frequency-Mass Coupling** | High-THz Clocking               | Optimize signal paths for phase-coherence.             |
| **Topological Invariance**  | HDI Differential Routing        | Maintain 50-ohm impedance with zero stubs.             |
| **Walker–Pearson equations**| `src/core/evolution.py`         | Field updates must conserve `‖∇·J_inf‖ ≈ 0`.          |
| **KK Metric Ansatz**        | `src/core/metric.py`            | 5D metric assembly; preserve block structure of G_AB.  |
| **FTUM Fixed Point**        | `src/multiverse/fixed_point.py` | Operator U = I + H + T must converge to `U Ψ* = Ψ*`.  |
| **Holographic Boundary**    | `src/holography/boundary.py`    | Entropy-area law: `S = A / 4G`; no boundary leakage.  |

## 5. Predicate-Based Docstring Contract

All functions in `/src` must document their theoretical anchor using the following pattern:

```python
def <function_name>(<args>):
    """
    IMPLEMENTATION of Monograph Section <X.Y> (<Topic>).
    IMPLICATION: <Physical / topological consequence of this operation>.
    LOGIC: <What the function computes and why it preserves the required invariant>.
    """
```

## 6. Isolation & Directory Convention

| Directory         | Purpose                                              | Edit Policy          |
|-------------------|------------------------------------------------------|----------------------|
| `THEBOOKV9a*.pdf` | Core monograph — the canonical theoretical reference | READ-ONLY            |
| `manuscript/`     | LaTeX / Markdown source of the monograph chapters    | READ-ONLY            |
| `src/`            | Numerical implementation of the field equations      | Editable             |
| `discussions/`    | Peer-review and AI-review records                    | Append-only          |
| `.github/`        | CI workflows and this context manifest               | Maintain carefully   |

## 7. Symmetry-Break Guard

If Copilot suggests an operation that violates unitarity (e.g., a standard irreversible XOR
gate, a non-Hermitian matrix update, or a lossy signal path without correction), treat it as
a **Symmetry Break** and reject or annotate the suggestion. The canonical test is:

```
Is the proposed matrix M unitary?  →  M† M = I  (up to numerical tolerance)
```
