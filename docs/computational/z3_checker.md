# Z3 Pentad Checker

Z3 SMT solver proves four Unitary Pentad governance constraints at compile time.

## Checks

| Check | Claim | Z3 verdict |
|-------|-------|------------|
| Trust stability | φ_trust ≥ 0.1 → c_s > 0 | sat (stable) |
| No deadlock | ¬(all bodies < 0.1 simultaneously) | unsat (impossible) |
| c_s ∈ (0,1) | 12/37 is in unit interval | unsat (out-of-range impossible) |
| ξ_c < 1/2 | 35/74 below symmetry point | unsat (violation impossible) |
