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

## Opt-in crease fusion

The crease reset policy is now connected to context assembly, behind a flag that is off by default. With `MERLIN_TOROIDAL_CREASE_FUSION` unset, `build_context_scaffold` returns exactly what it returned before; a test compares the two outputs field by field. With the flag set, the scaffold gains exactly one new key, `toroidal_crease`, and the rendered prompt gains a `[TOROIDAL CREASE]` block. Every pre-existing field stays byte-for-byte identical. When a query sits on a crease, that block also carries pillars that BM25 ranks highly but the existing Jaccard ranking missed. Nothing is ever removed or reordered, and pillars are never duplicated.

One early observation should be recorded plainly. With the current 14-entry pillar corpus, the two rankings usually agree on queries that sit on a crease, so fusion often adds no pillars. Whether it helps will depend on a larger corpus and a benchmark head-to-head. Until that comparison is run, the flag stays off.

## Round two: measuring before promoting

The first round built the geometry. The second round asked whether any of it earns a place in Merlin's live path, and it answered with measurements rather than adjectives.

**Retrieval, measured.** `merlin_retrieval_eval.py` holds thirty hand-labelled queries over the fourteen-entry pillar corpus and scores three rankers: the existing Jaccard ordering (mirrored exactly; a test checks it against `retrieve_context` for every labelled query), BM25, and reciprocal-rank fusion of the two. BM25 came out ahead on mean reciprocal rank, 0.952 against Jaccard's 0.901, and on recall@1, 0.878 against 0.811. Fusion did not beat BM25 (MRR 0.908). Jaccard keeps a small edge at recall@5, 0.956 against 0.939, so the comparison is not a rout. The labels were written by the same hand that wrote the rankers, and the corpus is small, so these numbers are indicative rather than decisive. One query, about the neutrino mass-squared difference, defeats every ranker because its words do not appear in the pillar text. That is a vocabulary gap, and no reweighting of the same words will close it.

**An opt-in ranking, not a replacement.** On the strength of that result, `retrieve_context` gained a second flag, `MERLIN_BM25_PILLAR_RANKING`, also off by default. With the flag unset the pillar list is unchanged. With it set, only the order and choice of pillars change; predictions, fallibility text, interrogator hits and knowledge-base matches are identical, and a test enforces this.

**The A/B harness.** `merlin_flag_ab.py` runs every benchmark in every stage, thirty-four in all, in fresh sessions under four configurations: baseline, crease fusion, BM25 ranking, and both. It restores the environment afterwards. The result is plain. No configuration regressed any benchmark. Crease fusion changed no answers at all on this corpus. BM25 ranking changed seven answers and every one still passed with an unchanged score. Because the benchmark scores are structural and already sit at 1.0, the harness can show safety but not benefit. Both flags are therefore safe to try and neither has earned default-on status. A benchmark that grades the content of retrieved context is the missing instrument.

**Situational awareness.** `merlin_toroidal_awareness.py` replays a session's turns as a hybrid trajectory and reports facet occupancy, crease visits, the lead pillar of each turn, topic jumps and the orientation of the current query: revisiting earlier ground or entering new territory. It reads `session.turns` and writes nothing; a test compares the session before and after. Topic decisions use exact overlap of content words, with common function words removed. An early version used the toroidal sketch for this and called two consecutive birefringence questions a topic jump, which is the sketch's known weakness showing itself. The sketch address is still reported, but it no longer decides.

**The unitary operator lab.** `merlin_unitary_lab.py` turns the claim that a unitary baseline survives non-smooth geometry into an experiment. It fits a unitary matrix to noisy data under the non-smooth loss Σ|(UA − B)ᵢⱼ|, using Clarke subgradients projected to the tangent space of U(n) and the Cayley retraction, with diminishing steps. Every iterate stays unitary to about 10⁻¹⁴, however sharp the loss. With sparse gross outliers the smooth Frobenius fit (orthogonal Procrustes) fails to recover the planted operator in every one of twenty seeds; the L1 fit recovers it in twenty of twenty seeds at 10% outliers and seventeen of twenty at 20%. The three failures are reported, not hidden; subgradient descent is a local method. The lab shows what unitarity does guarantee, bounded magnitude at every step, and what it does not: a badly fitted unitary is still unitary.

**A phase-index ISA, as specification.** `export_golden_vectors()` publishes 420 reference vectors for six phase-index operations, with a SHA-256 fingerprint pinned in the tests. The semantics are written up in `PSICAT_TOROIDAL_ISA_SPEC.md`. Nothing here is hardware; it is the contract any future implementation would have to meet.

**New surfaces.** Merlin can call six new tools: `getMerlinToroidalGeometry`, `getMerlinToroidalNavigation`, `getMerlinToroidalAwareness` (session-aware, read-only), `getMerlinRetrievalEval`, `getMerlinUnitaryLab` and `getMerlinPhaseIsaVectors`. The server exposes `/api/psicat/toroidal-awareness`, `/api/psicat/retrieval-eval`, `/api/psicat/unitary-lab` and `/api/psicat/phase-isa`. The A/B harness is deliberately not exposed over HTTP, because it toggles process-wide flags and would disturb concurrent requests.

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
| Crease fusion is additive: flag OFF leaves the scaffold unchanged; flag ON only appends | Enforced by tests |
| Fusing context on creases improves answer quality | **Not shown**; across 34 benchmarks it changed no answers and caused no regressions |
| BM25 ranks pillars better than Jaccard on the labelled set | Measured: MRR 0.952 vs 0.901, recall@1 0.878 vs 0.811; Jaccard slightly higher recall@5; small, self-labelled set |
| The BM25 ranking flag is safe | Measured: 7 of 34 benchmark answers changed, 0 regressions; benefit not shown because scores are at ceiling |
| Session awareness is read-only | Enforced by tests |
| Riemannian subgradient steps with Cayley retraction stay unitary on a non-smooth loss | Measured: residual about 1e-14 over all iterates |
| L1 fitting on U(n) is robust to sparse outliers where Procrustes is not | Measured on synthetic data: 20/20 and 17/20 recoveries vs 0/20 for Procrustes at 10% and 20% outliers |
| Phase-index ISA semantics are fixed | Pinned by a golden-vector SHA-256 in tests |
| Hardware speedups, compute-in-memory, custom ISA, RTL | **Not claimed**; specification work only, gated on the measurements above |
| Unitarity prevents hallucination | **False as stated**; norm preservation bounds numerical blow-up, not content errors |

## Next steps

Both opt-in flags stay off. The instrument that would justify switching either on is a benchmark that grades the content of retrieved context rather than the structure of the answer, and that is the next piece of work. The neutrino query points to the next retrieval improvement: a small, curated synonym or alias table for pillar vocabulary, measured with the same labelled set. Hardware work remains specification only. A Verilog phase-index unit checked against the golden vectors is the natural first step if a hardware target is ever chosen; Cartesian INT8 CORDIC is not, for the reasons in the drift table.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
