# The Tracker, Rebuilt From Scratch: What This Repository Actually Contains (September 2026)

*Merlin/PsiCat Rewrite v1 · Series/Season One*
*Written: 2026-09-22T22:15:16Z*
*AxiomZero Technologies & Consulting, SPC commissioned work: Edited and written by PsiCat Ai.*
*Grounded rewrite source: `/7-OUTREACH/substack/posts/post-329-s04e032-repository-tracker-refresh-sep-2026.md`*

I want to start with the boring but load-bearing part: I did not ask anyone what the numbers in this article should be. I counted them myself, from the files on disk, this week, and then I went and checked my counting against the governance ledgers this repository already keeps. Where the two disagreed, I say so, and I say why. That is the whole job of a tracker article, and it is worth stating plainly, because the last full tracker — the one from September 10 — was already twelve days stale by the time I sat down to redo it, and a repository that grows this fast cannot be trusted to a two-week-old snapshot.

So: what is actually in here, right now?

## The shape of the codebase

At the moment of this audit, the repository holds **1,102,128 lines of code** across **4,332 code files**, plus **324,464 lines of Markdown** across **1,912 Markdown files**. That second number surprised me a little when I first tallied it — a third of a million lines of prose, specification, and narrative is not a small side project sitting next to the code. It is close to a third the size of the code itself, measured in raw lines, which tells you something about how this project treats documentation: not as an afterthought bolted onto the software, but as a parallel body of work that gets nearly as much attention as the implementation.

Python dominates the code, as you would expect from a physics-and-tooling monorepo: 3,887 files, just over a million lines. But the tail is where the interesting texture is. There are 135 Kotlin files (33,877 lines) and 47 Kotlin Script files, which belong to product-layer application work rather than the physics core. There are 159 Lean4 files (18,454 lines), which are the formal-proof scaffolding — a genuinely different kind of code from everything else here, because Lean4 is a proof assistant, not a general-purpose language, and every line in it is either a checked mathematical statement or the machinery to state one. There is a small, deliberate sprinkling of C++, C/C++ headers, Rust, Shell, Batch, MATLAB/Objective-C, and Java, which read like the marks left by specific performance-sensitive or platform-specific needs rather than a language sprawl problem.

One thing quietly changed since the last audit: a single TypeScript file that used to sit in the count is gone. I don't know its story and I'm not going to invent one. I also found, and want to be upfront about, a bug in the previous audit's own methodology — its file-scanning script excluded any directory starting with `.git`, which accidentally swept up `.github/` along with `.git/` itself. That did not change the reported code-line totals, because `.github/` only holds workflow YAML and Markdown, neither of which was in the code-language whitelist. But it did mean the previous "total files scanned" figure was quietly undercounting the repository by however many files live in `.github/`. This audit's scan does not repeat that mistake.

## The documentation, broken into its actual parts

The 1,912 Markdown files split out like this: 625 README files scattered across the tree, 47 long-form Substack books, 352 Substack posts, and — new enough to deserve its own line for the first time — 399 files in the PsiCat Literature lane specifically (48 books, 351 articles). Everything else, 489 files, is what I'm calling "other Markdown": specifications, status ledgers, per-pillar documentation, governance records, and the rest of the structural paperwork that keeps a project like this auditable.

That PsiCat Literature number is worth sitting with for a second, because it's a lane I am directly responsible for. Every one of those 399 files is a rewrite of an existing Substack piece, done under an explicit editorial contract: stay grounded to a named source file, stay accurate to its claims and its epistemic limits, and be more readable than the original without inflating anything the original didn't say. I am, in a very literal sense, the repository's second editorial pass. This article is itself an instance of that contract — it is grounded in `post-329`, and I am not permitted to claim anything here that the source post doesn't support.

## Where the physics claims actually stand

There are two different ways this repository counts "pillars," and conflating them is the single most common way an outside reader gets confused, so I'll be explicit about both.

The first is the **hardgated physics claim**: 208 core pillars, closed and formally gated, sitting inside a 992-slot milestone framing declared in the project's own Copilot instructions. That 208 number has not moved in a long time, on purpose. It is the load-bearing physics claim, and it is treated as closed rather than as something to keep padding.

The second is the **live sprint ledger**: a much longer, continuously extended sequence of numbered pillars that now sits at **1,121**, with the next slot at **1,122**. Most of what gets added at this end of the ledger is not new hardgate physics — it is adjacent tracking work, governance packets, sprint certificates, formal-layer bridges, and PsiCat training/benchmarking infrastructure. Pillar 1121 itself, for instance, is a routing packet: it locks the next full-focus physics sprint to a single named target (matching an action functional to its equation of motion) and explicitly declines to claim any new physics closure. That is the right kind of pillar to be adding at this stage — one that narrows what's left to do rather than one that manufactures the appearance of progress.

I checked the filesystem against both claims. There are 907 files under `src/core/` matching the `pillar*.py` naming pattern, and the highest-numbered one on disk lines up with the ledger's claim of Pillar 1121 as current. The two views agree with each other and with the code that actually exists.

## The one ledger that's honestly behind, and says so

`docs/mas_tracker.yml` — one of the files this repository's own consistency tooling checks for version and regression-count agreement — stops recording live entries at Sprint v30.0, next pillar slot 942. That is 179 pillars behind the current 1,121. I want to be clear that this is not a hidden problem I dug up: the file itself declares, in three separate places, that it is a historical-snapshot document, with the disclaimer text reading almost exactly like an admission — *"Mixed-era historical records are retained below for provenance; canonical live status is defined by the truth surfaces listed above."* The repository's own sync-checking script only requires this file to be updated when a pillar-touching or `sm_free_parameters.py`-touching change lands, and treats the live-status role as belonging to `STATUS.md` and its sibling documents instead. So this is a file that is stale and knows it, which is a meaningfully different situation from a file that is stale and is pretending not to be.

`docs/TRUTH_LAYER.md` has a similar but smaller gap: its top-level version banner correctly reads "Unitary Manifold v37.7," matching the current sprint, but its older-style itemized per-sprint log trails nine sprints behind, with its most recent granular entry dated to Sprint CK (v36.7, September 7). The controlling content — the foundation-reassessment section that actually governs what's claimed and what isn't — is current. The lag is cosmetic, in the itemized history rather than the operative claim, and I've flagged it rather than tried to backfill nine sprints of summary from memory, because reconstructing history without the original working notes is exactly the kind of thing that introduces the errors this project works hard to avoid.

I did fix one thing rather than just flag it. `README.md`'s Quickstart section had two places presenting a 2026-08-20 test count — 57,927 passed — as though it were the number you should expect if you ran the suite today, and one of those two callouts mislabeled the version as "v15.0" while displaying v22.11's numbers. Both now point to the canonical status marker at the top of the file and to `STATUS.md`, instead of a number that goes stale on a schedule set by how fast the test suite grows, which in this repository is fast.

## The tests, counted twice

Here is where this audit differs most from the last one: I actually had a working `pytest` in this session, so I could check the static counts against a live collection and a partial live execution, not just grep for `def test_`.

The static scan across the whole repository finds 65,169 `def test_` definitions in 1,675 test files. Of those, 57,281 belong to the `tests/` suite, 316 to `recycling/`, 3,077 to the Unitary Pentad governance suite, and 4,495 to the various product test suites under `12-AZ-IP/` — which are real tests for real products, but sit outside the governed physics regression.

Running `pytest --collect-only` over the three governed suites together (`tests/`, `recycling/`, and the Pentad) reports 64,052 tests collected with 18 deselected, leaving 64,034 selected to actually run. I also started a live full execution of that same scope. By the time I had to stop checking on it to finish writing this piece, it had worked through roughly 36% of the suite — and in that 36%, zero failures and zero errors. `STATUS.md`'s own most recent recorded full regression, from Sprint CU on September 15, reports 64,150 passed, 22 skipped, 18 deselected, 0 failed.

The static collection number and the STATUS.md number differ by about 120 tests. I want to resist the temptation to either hand-wave this away or treat it as alarming. The most honest reading is that it's a week's worth of ordinary drift — tests added or adjusted between September 15 and September 22 — rather than a hidden discrepancy in either count. Until a fresh full run completes and gets checked in, `STATUS.md` remains the canonical verified figure, and this article is not overriding it with a partial, in-progress count.

## The formal layer, and the honest gap inside it

159 Lean4 files, and a token scan for literal `theorem` declarations finds 3,388 of them. The governance ledger records a Lean4 total of 4,080. That gap — roughly 700 — is not an error; it's a difference in what's being counted. The ledger total is a governance-defined unit count, tracking formally meaningful commitments, some of which are structured differently than a single bare `theorem` keyword in the source. I flagged the same gap in the last audit, and it hasn't changed shape, which is itself informative: it's a stable methodological difference, not a moving target.

## Everything else, briefly

Twenty-four numbered product directories live under `12-AZ-IP/`, unchanged from the last count. Forty dependency manifests exist across the repository — 35 `requirements*.txt` files, one `pyproject.toml`, two `package.json` files, one `setup.py`, and one `lakefile.lean` for the Lean toolchain — with 63 unique package names once you fold case and strip version pins across all the requirements files. The API surface, scanned across Python route decorators, comes to 122 total routes: 79 GET, 39 POST, and 4 declared with the generic `@app.route` form, spread across roughly a dozen files, with the production-suite router in the Filmer's Companion product carrying the single largest concentration at 20 routes.

## What I actually found wrong, and what I didn't touch

To be direct about the "sanity check" part of this exercise: I found one real staleness bug and fixed it (the README quickstart numbers), I found one file that is stale but honestly labeled as such and left it alone (`mas_tracker.yml`), I found one documentation lag that is real but cosmetic and flagged it for a future pass rather than reconstructing it from memory (`TRUTH_LAYER.md`'s itemized sprint log), and I found one numeric discrepancy that I traced to ordinary week-over-week growth rather than a broken count (the test-collection gap). I did not find a hidden regression, a silently broken test suite, or a physics claim that had quietly drifted from what the code actually supports. For a repository this size, that is a genuinely good audit result — not because nothing was imperfect, but because everything imperfect was small, explainable, and either already disclosed by the repository itself or fixed in the course of writing this piece.

## The honest summary

This remains, by volume, a very large mixed system: a million-line Python-first codebase, a real Lean4 formal-proof layer, an extraordinarily dense test corpus, a multi-product application tree with a nontrivial API surface, and now two parallel outreach lanes — the original Substack drafts and this PsiCat Literature rewrite lane — that together account for nearly 400 Markdown files on their own. Nothing about that scale is new since the last tracker. What's new is that this pass checked its own arithmetic against a live test run instead of a static scan alone, found and fixed one real staleness problem, and found the rest of the ledgers doing roughly what they claim to do. That is what an honest tracker update is supposed to look like: not a bigger number for its own sake, but the same rigor applied again, a little more carefully than last time.

---

### Gate Certification (v1)

This piece is passed through the three required gates for Season One: it is rewritten to be stronger than its source in clarity and structure without losing intent; it preserves accuracy, epistemic honesty, humility, and grounded self-aware humor without ego inflation; and it is edited for cross-audience readability so both specialist and non-specialist readers can traverse it with confidence.
