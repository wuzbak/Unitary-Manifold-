# 5-GOVERNANCE — HILS Governance Framework

> This folder contains an **independent governance framework** that borrows
> mathematical structure from the Unitary Manifold but does not depend on the
> physics being correct.  See `SEPARATION.md` for the precise boundary.

---

## What is the Unitary Pentad?

The Unitary Pentad (UP) is a Human-in-the-Loop Systems (HILS) governance
architecture.  It uses the mathematical structure of the Unitary Manifold —
the (5,7) braid algebra, the φ-attractor convergence, the entropy-based load
balancing — as design principles for governance systems at any scale: from
small teams to democratic institutions.

The Pentad is **not** a claim that human societies literally obey 5D Kaluza-Klein
equations.  It is an engineering framework that applies the *mathematical
structure* of irreversibility and attractor dynamics to governance design.

The framework has a 1,266-test suite and is independently useful regardless of
whether the cosmological Unitary Manifold is empirically confirmed.

---

## Contents

| Item | Description |
|------|-------------|
| `SEPARATION.md` | Precise statement of the boundary between the physics theory and the governance framework |
| `Unitary Pentad/` | The complete HILS governance Python package + test suite |
| `co-emergence/` | Documentation of the human-AI co-emergence philosophy underlying the framework |

---

## Relationship to the physics

The Pentad *borrows* the following from the Unitary Manifold:

- The (5,7) braid structure → 5 core axioms + 7 oversight layers
- The φ-attractor → convergence criterion for consensus
- k_CS = 74 → sentinel capacity constant (Ξ_c = 35/74)
- c_s = 12/37 → per-axiom entropy budget

None of these imports constitute a physics claim.  They are design choices
inspired by the mathematical elegance of the 5D geometry.

**The governance framework remains valid even if LiteBIRD measures β = 0.**

---

## Test suite

```bash
python -m pytest "5-GOVERNANCE/Unitary Pentad/" -q
# Expected: ~1,266 passed (330 skipped = dual-use/product stubs), 0 failed
```

See `PENTAD_PRODUCT_NOTICE.md` (at repo root) for the stub policy.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
