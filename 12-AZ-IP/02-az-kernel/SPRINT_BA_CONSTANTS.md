# Sprint BA Constants for az-kernel

This document records the Sprint BA constants consumed by `02-az-kernel` with
plain status labels only.

| Item | Value | Pillar | Status | Honest note |
|------|-------|--------|--------|-------------|
| `k_CS` | `74` | `P849` | `CLOSED` | Fixed by the 9D Green-Schwarz closure and treated as application-ready. |
| `φ₀` | `1` | `P853` | `PARTIAL` | The unit normalisation is tracked, but Sprint BA does not claim full closure here. |
| 11D→4D chain | `11→10→9→8→7→6→5→4` | `P858` | `CLOSED` | The 7-step dimensional descent is closed and exposed to the kernel-side tooling. |

## Internal consistency used by the Python wrapper

- `N_W = 5`
- `N_2 = 7`
- `k_CS = N_W^2 + N_2^2 = 74`
- `c_s = 12/37`
- The dimensional chain contains 8 nodes and therefore 7 reduction steps.

No epistemic inflation is applied: only `CLOSED`, `PARTIAL`, and `OPEN` labels
are used.
