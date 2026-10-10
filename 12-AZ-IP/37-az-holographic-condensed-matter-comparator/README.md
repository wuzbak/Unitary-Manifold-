# AZ Holographic Condensed-Matter Comparator — Product 37

**Folder:** `12-AZ-IP/37-az-holographic-condensed-matter-comparator/`
**Version:** 1.1.0
**TRL:** TRL-3 (scaffold-to-scaffold comparison tool, now a runnable web product; illustrative benchmarks only)
**Status:** Active — Phases 1-2 of article-354's "Holographic dictionary -> condensed-matter comparison" roadmap

## What this is

`src/holography/dual_cft_spectrum.py`'s `kk_tower_to_cft_operators()`
already assigns boundary-operator conformal dimensions
(`Delta_n ≈ 4 + 2n`) to the RS1 KK graviton tower. This product places
those dimensions side by side with well-known reference operator
dimensions from the holographic-superconductor literature
(`KNOWN_HOLOGRAPHIC_BENCHMARKS`), and computes the scalar two-point
correlation decay exponent (`2*Delta`) each one implies.

`compare_kk_level_to_benchmark(n, benchmark)` and
`compare_kk_tower_to_all_benchmarks(n_max)` return the gap between the
UM KK-tower dimension and a named benchmark; `closest_benchmark(n)`
reports which reference value is nearest.

## Epistemic status

The reference table (`marginal_scalar`, `bcs_like_order_parameter`,
`minimal_scalar_hair`) is **illustrative** — standard values quoted in
Hartnoll's lecture notes (arXiv:0903.3246) and Gubser's holographic
superconductor paper (arXiv:0801.2977), not a fit to any specific real
material's measured critical exponents. This tool makes no claim that
the UM KK-tower matches any laboratory condensed-matter system; it is a
scaffold-to-scaffold comparison only, as the article itself frames this
direction.

## Usage

```bash
python 12-AZ-IP/37-az-holographic-condensed-matter-comparator/run.py
```

## Running as a web product

```bash
python 12-AZ-IP/37-az-holographic-condensed-matter-comparator/run.py --serve --port 8137
```

Then visit `http://127.0.0.1:8137/` for the comparator dashboard, or query
the JSON API directly:

- `GET /api/status` — product metadata, benchmark count
- `GET /api/benchmarks` — the illustrative reference benchmark table
- `GET /api/compare?n_max=` — every KK-tower level up to `n_max` vs every benchmark
- `GET /api/closest?n=` — the benchmark closest to KK-tower level `n`

## Tests

```bash
python -m pytest 12-AZ-IP/37-az-holographic-condensed-matter-comparator/tests -q
```

## Sources

- `src/holography/dual_cft_spectrum.py` — `kk_tower_to_cft_operators`
- Hartnoll, "Lectures on holographic methods for condensed matter physics", arXiv:0903.3246
- Gubser, "Breaking an Abelian gauge symmetry near a black hole horizon", arXiv:0801.2977
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #10

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
