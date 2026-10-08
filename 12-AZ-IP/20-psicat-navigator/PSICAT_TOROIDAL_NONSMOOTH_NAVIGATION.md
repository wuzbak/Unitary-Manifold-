# PsiCat Toroidal Non-Smooth Navigation

**Status:** 🔵 ADJACENT TRACK. This is software emulation inside Product 20. It is not a hardgate physics claim, it has no pillar number, and it makes no claims about hardware performance.
**Modules:** `ox_navigator/engine/merlin_toroidal_geometry.py`, `ox_navigator/engine/merlin_toroidal_router.py`, `ox_navigator/engine/merlin_retrieval_scoring.py`
**Tests:** `tests/test_merlin_toroidal_navigation.py`
**Endpoints:** `GET /api/psicat/toroidal-geometry`, `GET /api/psicat/toroidal-navigation?query=…&top_k=…`, `GET /api/psicat/repo-geodesic?source=…&target=…&max_files=…`

## Why a torus, and why a lattice

The design discussion that led here began with a reasonable worry. If the space Merlin navigates is not smooth, the ordinary tools of gradient descent, gentle curves and continuous interpolation stop working, and the navigator has to be built differently. That is true. The answer this repository gives is more specific than "use non-smooth analysis in general". The Unitary Manifold already fixes a geometry, and that geometry is discrete in exactly the places where it matters.

The Chern–Simons level is k_cs = 74 = 5² + 7², the sum of the squares of the braid windings. If we put a phase lattice of order 74 on each circle of a torus, every rotation the navigator performs becomes an integer addition mod 74. That one decision settles several questions from the bare-metal proposal. A rotation is exact, so the state never drifts. Each phase index needs only seven bits, and those seven bits are the whole state, not a lossy rounding of something finer. Unitarity is free as well. The shift operator |k⟩ → |k+1⟩ is an integer permutation matrix, so U†U = I holds exactly, and the test suite checks it with integer equality rather than within a floating-point tolerance. The shift and the diagonal clock operator together satisfy the discrete Weyl–Heisenberg relation ZX = ωXZ with ω = e^{2πi/74}. Read this way, the lattice is the discrete phase space of the torus.

Next comes the orbifold. The fifth dimension in the physics is S¹/Z₂, the circle folded by the reflection θ → −θ. On the lattice that reflection is another integer permutation. It is its own inverse, and it fixes exactly two points, 0 and 37. Those two fixed points are the creases. A trajectory that moves uniformly around the circle and is then folded into the fundamental domain [0, 37] reverses direction each time it reaches one of them. That is the "perfect elastic collision" from the original sketch, and here it can be stated precisely: the fold relabels basis states and never touches the amplitude, so the norm is preserved trivially, not approximately. `orbifold_bounce` returns the folded positions and records an impact event at every crease crossing.

## Where the non-smoothness actually lives

On the flat torus, the distance between two phases, d(a, b) = min(|a − b|, 74 − |a − b|), is piecewise linear with two kinds of kink. At coincidence the distance has a minimum shaped like |x|. At the cut locus, where the phases are exactly 37 apart, it has a maximum shaped like −|x|. At both kinks the Clarke generalised gradient is the whole interval [−1, 1]. So both points are Clarke-stationary, even though one is the best place to be and the other is the worst. This is the practical lesson of non-smooth analysis: a set-valued gradient tells you where the kinks are, but on its own it cannot tell a summit from a valley. `circular_distance_subdifferential` therefore reports the descent directions explicitly. At coincidence there are none. At the cut locus there are two, and the test suite checks that each reported descent direction really does reduce the distance.

The same structure shows up in geodesics. Between two torus points, the shortest path takes the shorter arc on each circle. When a coordinate sits exactly on the cut locus, both arcs are shortest, so the geodesic branches. `toroidal_geodesic` returns the displacement, the coordinates where branching happens, and the number of distinct geodesics, which is 2 raised to the number of branch coordinates. This is the "graph-like metric space" from the proposal, made concrete and checkable.

## The convergence question, answered honestly

The bare-metal sketch imagined a vector circulating through a unitary feedback loop until it "converges", at which point a comparator would read out the answer. That cannot happen. A unitary operator has every eigenvalue on the unit circle, so repeated application never contracts toward anything; it cycles. On the lattice the cycle length is exactly 74 / gcd(step, 74). The 5- and 7-windings each have period 74 and visit every phase. The 12/37 cadence, which is 24/74 on the lattice, has period 37 and visits only the even phases. So an odd target can never be reached by that cadence, however long it runs, and the tests confirm this.

The exit therefore has to be something other than unitary evolution. `first_hitting_time` stops the orbit the first time it enters a target facet. That is a projective read-out, and it is deliberately not unitary. The design keeps the two jobs apart: unitary steps move the state around without distortion, and a separate, explicit, non-unitary rule decides when to stop. Merging the two jobs is how the original sketch ended up promising a convergence that unitarity rules out.

## The fixed-point question, measured rather than assumed

The proposal suggested that norm preservation would let a CORDIC engine run safely in INT4 or INT8. The emulator in `merlin_toroidal_geometry.py` checks that claim instead of assuming it. It is a bit-exact integer CORDIC: shifts and adds, quadrant reduction by exact quarter-turns, and a single integer multiply for gain compensation. It chains one full turn of 74 rotations of one lattice step each, then measures how far the vector ends up from where it started:

| Bits | Relative closure error after one full turn |
|------|--------------------------------------------|
| 4    | ≈ 13 (meaningless; the representation overflows) |
| 8    | ≈ 0.46 |
| 12   | ≈ 0.043 |
| 16   | ≈ 0.003 |
| Phase-index lattice (7 bits) | 0, exactly |

The Cartesian representation drifts, and the drift shrinks only as bits are added. INT4 is not usable for chained rotations, and INT8 loses close to half the vector in a single turn. Rotating in the phase group Z₇₄ instead has no drift at all, because nothing is rounded. The engineering conclusion is to keep geometry in phase-index form and carry amplitudes separately, converting to Cartesian form only at the edges. The emulator also supplies the integer vectoring mode that converts back. It recovers all 74 lattice phases from integer coordinates without error.

## Integer toroidal addresses for text

To bring retrieval into the same geometry, `phase_sketch` maps a set of tokens to a point on a 16-dimensional torus using only integer operations. On each circle, every token adds a fixed-point root of unity, chosen by a stable hash. The phase of the total is then read back out with the integer CORDIC. Token sets that share words land close together; unrelated sets sit about 74/4 apart on each circle, which defines the similarity scale. The first two coordinates feed the braid bank, (5θ₁ + 7θ₂) mod 74. Because gcd(5, 74) = 1, this map spreads lattice points evenly across all 74 banks. That is the static memory map the bare-metal proposal asked for, with a balance guarantee that can be proved.

We also measured how good the sketch is as a retriever, and the answer is: not good enough to replace BM25. On the eight example queries in `constants.py`, against the 14-entry pillar knowledge corpus, the sketch's top five agreed with BM25's top five 45% of the time on average. By chance alone the expected agreement is about 36%. The sketch is locality-sensitive and works as an integer-only bank address, but it is a coarse approximation. BM25 therefore remains the authority, and `toroidal_rank` reports both rankings and their overlap, so this judgement can be re-checked as the corpus grows.

## The hybrid automaton over Merlin's real decisions

Merlin already made non-smooth decisions before any of this work. Lane selection switches at query lengths of 120 and 350 characters. Kernel selection breaks keyword-score ties by a fixed priority order. A knowledge-base match is accepted only above a word-overlap score of 0.15. Each of these is a step function of the query. `evaluate_hybrid_state` makes the steps visible without changing any decision. The primary facet is exactly what the existing `classify_lane`, `infer_runtime_kernel_id` and `lookup_kb` already return, and the test suite enforces that.

What the hybrid state adds is awareness of where the creases are. If a query's length falls within a margin of a lane threshold, its knowledge-base score falls within a margin of the cutoff, or its kernel was chosen by breaking a tie, then the query sits on a crease. The router then lists the active set: every facet reachable from that point. Kernels are computed per lane, because the kernel guard itself depends on the lane. This active set is the discrete counterpart of a Clarke generalised gradient, a set of admissible directions rather than a single arrow. The reset policy follows directly. Off a crease, Merlin commits to the primary facet. On a crease, it should fuse context from every active facet rather than trust a boundary decided by a few characters. `trace_hybrid_trajectory` records a sequence of queries as a hybrid trajectory, with each discrete jump between facets marked explicitly.

For repository routing, `route_repo_geodesic` runs a weighted Dijkstra search over the existing repository graph. Import edges cost 1 and symbol-overlap edges cost 2, so the shortest path prefers real dependencies to shared names.

## Claims ledger

| Claim | Status |
|-------|--------|
| Lattice shift and reflection operators are exactly unitary; the reflection is an involution with fixed points {0, 37} | Shown (integer equality in tests) |
| Phase-index rotation on Z₇₄ has zero closure error | Shown |
| Cartesian fixed-point CORDIC drifts; magnitude by bit width as tabulated | Measured (emulator) |
| Pure unitary iteration is periodic and never converges; exit must be non-unitary | Shown |
| The Clarke-stationary set includes the cut-locus maximum, so descent directions must be reported separately | Shown |
| The braid bank map spreads lattice points evenly across 74 banks | Shown (exhaustive) |
| The phase sketch approximates lexical similarity | Weak: about 45% top-5 agreement with BM25 vs about 36% chance; not authoritative |
| Hybrid-state primary facets equal the existing router decisions | Enforced by tests |
| Fusing context on creases improves answer quality | **Not yet measured**; requires a benchmark head-to-head |
| Hardware speedups, compute-in-memory, custom ISA, RTL | **Not claimed**; specification work only, gated on the measurements above |
| Unitarity prevents hallucination | **False as stated**; norm preservation bounds numerical blow-up, not content errors |

## Next steps

The next experiment is to wire the crease reset policy into context assembly behind a flag and run the existing Stage A–E benchmark head-to-heads with and without it. If fusing context on creases does not beat committing to the primary facet, the flag stays off. Hardware specification work, a Verilog CORDIC checked against the Python golden model and the `UNITARY_ROT` / `SUBDIFF_BOUND` instruction proposals, should start only after that result. It should target phase-index arithmetic, not Cartesian INT8, because the table above has already shown which of the two is exact.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
