# AZ Geometric Tori Transformer — Product 43

**Folder:** `12-AZ-IP/43-az-geometric-tori-transformer/`
**Package:** `az_tori_transformer`
**Version:** 1.0.0
**TRL:** TRL-1 (novel architecture, validated only on a synthetic smoke-test task)
**Status:** Active — new product; also wired into PsiCat Navigator (Product 20) as a native tool

## What this is

A from-scratch, trainable Transformer whose *entire* positional mechanism is
built from the repository's exact integer toroidal phase lattice — the
`Z_74` lattice, `(5, 7)` braid winding, and `12/37` tick cadence already
canonical to `12-AZ-IP/20-psicat-navigator`'s toroidal lane
(`PSICAT_TOROIDAL_ISA_SPEC.md`) — instead of continuous sinusoidal/RoPE
frequencies or a standard learned absolute positional embedding.

This is the "deep dive into transformer architecture" requested as the next
step after the toroidal ISA specification and the PsiCat phase-index work:
it is not a wrapper around PyTorch/transformers, and not a port of an
existing published architecture. Every op (matmul, softmax, layer norm,
GELU, embedding gather, the rotary encoding, and the relative-position
bias) is implemented and differentiated here (`tensor.py`), in NumPy only.

## The two geometric mechanisms

1. **Toroidal rotary encoding** (`positional.py::toroidal_rotation_table`,
   `attention.py::apply_rotation`). Each query/key channel pair is rotated
   by an *exact* phase index `wrap(step_k * position)` on `Z_74` — not a
   continuous frequency. Rotation composition still gives the RoPE
   invariant (`q'_i . k'_j` is a function of `i - j` only), but every pair's
   rotation now has a **finite orbit period** (`74 / gcd(step_k, 74)`): the
   phase wraps around and repeats. That periodic wraparound — information
   becoming geometrically close again after a full orbit, instead of
   monotonically decaying with raw distance — is the "tori information
   flowing" property the product is named for. See
   `tests/test_positional.py::test_rotation_table_is_periodic_with_orbit_period`
   and `test_rotation_preserves_relative_dot_product`.

2. **Toroidal relative attention bias** (`positional.py::toroidal_relative_bias_indices`,
   `attention.py::gather_relative_bias`). Each sequence position is mapped to
   a two-torus "bank" address (`toroidal_geometry.position_bank`), and a
   learned per-head bias is added to the attention logits, indexed by the
   *circular distance* between two positions' bank addresses. Because the
   bank address is a modular combination of two windings, positions far
   apart in raw sequence index can land on nearby (or identical) bank
   addresses — a second, independent channel for non-local geometric
   coupling. See `test_relative_bias_allows_distant_positions_to_be_geometrically_close`.

`toroidal_geometry.position_code` documents and deliberately avoids a
degenerate case: a torus code built purely from the `(5, 7)` braid windings
has bank address `(5² + 7²)·i mod 74 == 0` for every position, because
`5² + 7² == 74` *is* the definition of `K_CS`. The second coordinate instead
uses the independent `TICK_PHASE_STEP = 24` winding (the Pentad's `12/37`
cadence expressed on `Z_74`), which keeps the embedding non-degenerate.

## Architecture

```
tokens --Embedding--> x
for each of num_layers TransformerBlocks:
    x = x + ToroidalMultiHeadAttention(LayerNorm(x))   # rotary + relative bias
    x = x + FeedForward(LayerNorm(x))                  # GELU MLP
logits = Linear(LayerNorm(x))
```

There is deliberately **no separate additive absolute positional
embedding** — the toroidal rotary encoding and relative bias are the
model's only source of position-awareness.

`tensor.py` is a minimal reverse-mode autograd engine (the "array
micrograd" pattern) supporting exactly the ops above, each independently
checked against finite-difference numerical gradients in `tests/test_tensor.py`.

## Toy training demonstration

`train_demo.run_toroidal_copy_demo` trains the model on a **cyclic copy
task**: the target at position `i` is the input token at position
`(i + shift) mod seq_len` — a relation that wraps around the end of the
sequence, which is exactly the invariant the toroidal encoding is built to
carry. The model is bidirectional (non-causal) here; this is a fixed-offset
lookup task, not autoregressive generation.

```bash
python 12-AZ-IP/43-az-geometric-tori-transformer/run.py demo --steps 200
```

A representative run (`seq_len=16, vocab_size=12, shift=5, steps=200`)
drives the cross-entropy loss from ~2.9 (near `ln(12)`, i.e. chance) down to
well under 0.4, with >95% next-token accuracy on a held-out batch — see
`tests/test_training.py` for the pinned regression thresholds.

## Running as a web product

```bash
python 12-AZ-IP/43-az-geometric-tori-transformer/run.py serve --port 8143
# then open http://127.0.0.1:8143/
```

Endpoints (stdlib `http.server`, no web framework dependency):

* `GET /api/status` — product metadata.
* `GET /api/geometry?head_dim=&seq_len=` — rotation orbit periods per
  channel pair, and a sample of the toroidal relative-bias index matrix.
* `GET /api/demo?seq_len=&vocab_size=&shift=&steps=&seed=` — runs the
  toroidal-copy demo (steps capped at 500 per request) and returns the
  training/eval report.

## Integration with PsiCat Navigator and the PsiCat Browser

Following the precedent set by Product 42 (`_ensure_product42_on_path` in
`ox_navigator/engine/merlin_tools.py`), the Navigator lazily imports this
product's package (`_ensure_product43_on_path`) from
`ox_navigator/engine/merlin_tools.py` and exposes two read-only tools:

* `getToriTransformerGeometry` — the toroidal rotation/bias geometry report.
* `getToriTransformerDemo` — runs the toroidal-copy training demo and
  returns the report (steps capped, same as the HTTP API).

Both are registered in the Navigator's tool catalog, JSON-schema table, and
dispatch map exactly like every other native PsiCat tool, and are reachable
over `/api/psicat/tori-transformer`. The **PsiCat Web Browser** (Product 24)
needs no separate integration: its sidebar already sends free-text research
questions to the Navigator's generic `/api/psicat` query path, so once a
tool is registered with the Navigator it is reachable from the Browser the
same way every other PsiCat tool already is.

## Epistemic status

* ADJACENT TRACK. This is a software architecture product motivated by, and
  reusing the exact arithmetic of, the repository's hardgated (5, 7) braid
  winding and `K_CS = 74` constants — it is **not** a hardgate physics claim
  and makes no claim that the (5, 7) winding or the 5D Kaluza-Klein geometry
  requires this attention mechanism.
* No benchmark claim is made that this architecture outperforms standard
  RoPE/T5-relative-bias Transformers on real language-modelling data; the
  toy cyclic-copy task is a targeted architecture smoke test chosen to
  exercise the wraparound property, not a general capability benchmark.
* TRL-1: a single synthetic task has been validated; no training run on a
  real corpus, no comparison against a non-toroidal baseline of matched
  parameter count, and no hardware/throughput measurement have been done.

## Tests

```bash
python -m pytest 12-AZ-IP/43-az-geometric-tori-transformer/tests/ -q
```

46 tests covering: autograd gradient checks against finite differences
(`test_tensor.py`), Z_74 lattice invariants plus an optional cross-check
against the Navigator's golden-vector export (`test_toroidal_geometry.py`),
rotary/bias periodicity properties (`test_positional.py`), attention shape
and causal-masking behaviour (`test_attention.py`), model forward-pass
determinism (`test_model.py`), end-to-end training loss/accuracy regression
(`test_training.py`), and the JSON API dispatch (`test_api.py`).

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
