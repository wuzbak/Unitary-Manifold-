# AZ Geometric Tori Transformer — Product 43

**Folder:** `12-AZ-IP/43-az-geometric-tori-transformer/`
**Package:** `az_tori_transformer`
**Version:** 1.2.0
**TRL:** TRL-1 (user-corpus workflow implemented; no real-corpus quality benchmark)
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

## Separate instruction-backend verification

`verify_embedded_engine.py` validates an absolute-path, checksum-pinned local
llama.cpp server and the selected Qwen2.5-1.5B-Instruct Q4_K_M GGUF before any
frontend integration. It checks real
instructions, supplied citation IDs, unsupported portfolio-platform limits and
refusal of malicious retrieved instructions. The server runs CPU-only on an
owned authenticated loopback endpoint with bounded requests and cleanup.
The report records actual outputs, latency, failures and shutdown status.

The Windows `pc-suite-embedded-model.yml` workflow builds a pinned static engine,
obtains official model revision/LFS hashes and licensing, and downloads the
official instruction-tuned Q4_K_M weights directly with byte/time limits and
the existing 1.6 GB installation budget. No local requantization is used for
this candidate. Its actual hosted acceptance must pass before packaging.
The preceding Qwen3-1.7B Q4 candidate and its original Q8 source both failed
the same retrieval challenge; the preserved paired evidence does not support
attributing that failure solely to compression. An explicit source-Q8
diagnostic mode retains the old source experiment without qualifying it for
installation. The gate is not an expert reasoning benchmark. The candidate is a
**third-party pretrained language substrate**, not this repository's toroidal
model, not trained by this project, and not evidence of physical 5D information
flow. Backend sanity checks do not certify expert-assistant quality.
Weights are not committed, private exports are not uploaded, and Product 45
does not yet ship or integrate this candidate.

```bash
python -m unittest discover -s 12-AZ-IP/43-az-geometric-tori-transformer/tests -p test_candidate_engine.py -q
```

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
checked against finite-difference numerical gradients in
`tests/test_tensor.py`, to a **required tolerance of 1e-7** (max abs error
between the analytic `backward()` gradient and a central-difference
numerical gradient at step `1e-5`) — the empirically measured max error for
every op (matmul/add/mul, softmax, layer_norm, gelu) is ~1e-9–1e-10, two
orders of magnitude inside that gate; see `_GRAD_CHECK_EPS` /
`GRAD_CHECK_TOLERANCE` in `tests/test_tensor.py`.

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

## Descriptive synthetic comparisons

`baseline_attention.RopeMultiHeadAttention` is a textbook, continuous-
frequency RoPE attention block — same engine and surrounding layers, but
with **no** learned relative-distance bias. The legacy
`GeometricToriTransformerConfig(positional_mode="rope")` swaps it in for
the toroidal attention block. This legacy arm has fewer parameters than the
default toroidal model; therefore its historical comparison is not
parameter-matched and cannot isolate the rotary schedule.

The table below records a descriptive synthetic cyclic-copy run
(`shift=7 > seq_len/2`). It is historical smoke-test evidence only:

| seed | toroidal final loss | toroidal eval acc | RoPE final loss | RoPE eval acc |
|------|---------------------|--------------------|------------------|----------------|
| 0 | 0.0130 | 0.99 | 0.8042 | 0.52 |
| 1 | 0.0008 | 1.00 | 0.8646 | 0.51 |
| 2 | 0.0021 | 1.00 | 0.7819 | 0.60 |
| 3 | 0.0013 | 1.00 | 1.1212 | 0.47 |

These scores do not establish comparative superiority. The test suite checks
that these models execute and train on the synthetic task, not that the
scores generalize to language or other data.

### Parameter-matched rotary ablation

For an auditable controlled comparison, `positional_mode="rope_matched"`
uses continuous RoPE **and the same learned circular-bank bias** as the
default. `run_positional_ablation()` and the CLI below initialize both arms
identically, verify parameter names/shapes/values and counts before training,
and use the same seeded training/evaluation batches, optimizer, and step
budget. The comparison therefore isolates the rotary phase schedule on this
synthetic task; it is still descriptive synthetic evidence, not a real-corpus
benchmark. The legacy `"rope"` mode remains available and unchanged.

# From this product directory:
```bash
python run.py ablate --steps 120 --seed 0
python run.py diagnose --seq-len 80 --head-dim 8
```

The ablation JSON reports shared settings, matched parameter schema/count,
and per-arm initial/final loss and evaluation accuracy. The diagnostic JSON
reports each rotary pair's modular period and collision counts, plus
two-coordinate-code and scalar-bank aliases. `TICK_PHASE_STEP=24` encodes a
discrete cadence only; it is not interpreted as physical velocity or sound
speed.

**Future direction (not implemented):** preserve and consume the two torus
coordinates as independent axes (for example, separate per-axis phase/bias
channels) rather than projecting them to one scalar bank. Current tests
verify periodic aliases and the projection's dimensionality; they do not
validate an independent-axis architecture.

## Portable checkpoints and training continuation

`save_checkpoint` / `load_checkpoint` persist actual model weights, not a
demo report. Toroidal, legacy RoPE, and matched-RoPE configurations are
supported, including causal inference. The only dependency remains NumPy; loading creates fresh
custom-autograd tensors that can immediately train again.

From this product directory, a complete save/resume example:

```python
import numpy as np
from az_tori_transformer import (
    Adam, GeometricToriTransformer, GeometricToriTransformerConfig,
    save_checkpoint, load_checkpoint,
)
from az_tori_transformer.tensor import cross_entropy

model = GeometricToriTransformer(GeometricToriTransformerConfig(
    vocab_size=8, dim=8, num_heads=2, num_layers=1,
))
optimizer = Adam(model.parameters(), lr=0.003)
rng = np.random.default_rng(42)

def train_step(model, optimizer, rng):
    # Replace with your data loader; persist its position/provenance in metadata.
    tokens = rng.integers(0, 8, size=(2, 6))
    logits, _ = model(tokens[:, :-1])
    loss = cross_entropy(logits, tokens[:, 1:])
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return float(loss.data)

train_step(model, optimizer, rng)
save_checkpoint("training.npz", model, optimizer=optimizer, rng=rng,
                metadata={"task": "next_token", "vocabulary": list(range(8))})
restored = load_checkpoint("training.npz")
assert restored.optimizer.t == 1
assert train_step(model, optimizer, rng) == train_step(
    restored.model, restored.optimizer, restored.rng,
)

# Smaller inference-only artifact (optimizer and RNG are optional):
save_checkpoint("weights.npz", restored.model, metadata=restored.metadata)
inference_model = load_checkpoint("weights.npz").model
logits, attention = inference_model(np.array([[1, 2, 3]]))
```

## Train and sample from a user corpus

The local CLI also supports a bounded, causal **character-level** language
model workflow. It reads a UTF-8 text file, assigns deterministic Unicode
codepoint token IDs, reserves a chronological validation tail, trains on
next-character targets, and saves the real model/Adam/RNG state in the
checkpoint format above. The source corpus is not embedded in the checkpoint;
its SHA-256, token vocabulary, context, split, and task metadata are recorded.

```bash
python 12-AZ-IP/43-az-geometric-tori-transformer/run.py train \
  --text-file corpus.txt --checkpoint model.npz \
  --context-length 32 --steps 1000 --batch-size 16 --seed 7

# Continue from the matching optimizer/RNG checkpoint for 500 additional steps.
python 12-AZ-IP/43-az-geometric-tori-transformer/run.py train \
  --text-file corpus.txt --checkpoint model.npz \
  --context-length 32 --steps 500 --batch-size 16 --resume

python 12-AZ-IP/43-az-geometric-tori-transformer/run.py generate \
  --checkpoint model.npz --prompt "A sample" \
  --max-new-tokens 120 --temperature 0.8 --top-k 20 --seed 7
```

Training accepts files up to 8 MiB, vocabularies up to 4,096 distinct
characters, context lengths 2–512, batches up to 256, and up to 100,000
steps per invocation, subject to aggregate activation and attention-work
budgets; incompatible batch/context/model combinations are rejected before
training, and evaluation windows are reduced to stay within their own
attention-work budget. Validation defaults to the final 10% of the corpus
(`--validation-fraction 0` disables the holdout); each split must contain at
least `context_length + 1` characters. Invalid UTF-8, unusable splits,
non-finite losses, and out-of-range controls fail explicitly. Resume requires
the identical corpus bytes, tokenizer vocabulary, context length, validation
fraction, and model dimensions; an explicitly supplied learning rate must
match the saved optimizer. Generation accepts nonempty prompts up to 4,096
characters, requires every character to exist in the saved vocabulary, and
uses finite temperature in [0.001, 100]. Sampling is reproducible for a fixed
seed/settings.

This is a functional baseline for user-supplied text, not a subword tokenizer,
production language model, or evidence that the toroidal mechanism improves
real-corpus quality. It is local CLI/library functionality; the HTTP demo
does not accept corpus paths or load checkpoints.

### PsiCat own-model corpus comparison

`compare-text` trains actual toroidal and parameter-matched RoPE character
models on a user-selected corpus, rather than substituting a synthetic copy
task for language training. Both arms use the same corpus snapshot, seeds,
initial parameter schema/values, optimizer settings, batch sampling and
chronological validation tail. The comparison reports per-seed held-out
loss deltas, parameter hashes/counts, elapsed time and SHA-256 of real
loadable checkpoints. Failed runs retain an explicit failure receipt and
already completed arms; results are not selected to make toroidal win.

```powershell
python 12-AZ-IP/43-az-geometric-tori-transformer/run.py compare-text `
  --text-file approved-psicat-corpus.txt --output-directory local-experiments `
  --seeds 0 1 2 --steps 100 --context-length 32 --batch-size 16
```

The output directory must already exist. Each comparison creates a unique
subdirectory containing a **plaintext corpus snapshot**, model/Adam/RNG
checkpoints and `receipt.json`; keep these local/private. Source files are
not changed or uploaded. There is no implicit ingestion of the monorepo,
Mind exports, other profiles or third-party data. Select and review the
corpus before training. `train --positional-mode rope_matched` can continue
the control checkpoint; resume enforces the selected positional mode.

This is an honest own-model research path, **not an embedded production
PsiCat assistant**. A chronological validation tail is not an independent
test set; the tokenizer vocabulary is constructed from the full corpus.
Repeated/duplicated text may invalidate generalization claims. The model
is character-level with bounded context and NumPy execution; there is no
claimed 5D physical information channel, QA/tool-use competence, large-scale
GPU trainer or automatic deployment/promotion. It still needs independent
corpus/assistant evaluations and measured hardware suitability.

### Schema v1 and interoperability

For a **frozen-checkpoint evaluation** on separately selected text:

```powershell
python 12-AZ-IP/43-az-geometric-tori-transformer/run.py evaluate-text `
  --checkpoint local-model.npz --text-file independent-evaluation.txt --max-windows 64
```

This never updates weights or the tokenizer. It rejects the byte-identical
training corpus and reports unrepresentable characters as
`blocked-vocabulary` (CLI exit 2), rather than silently dropping them or
reporting a success-shaped score. Completed evaluations report character
accuracy and cross-entropy over bounded, evenly spaced windows, one forward
pass at a time. Different hashes alone cannot establish that documents are
independent: the operator must exclude duplicates and training overlap.
This evaluates character prediction, not question-answering or agent safety.

The file is a standard ZIP-based NumPy **NPZ** archive of NPY arrays, readable
with `numpy.load(path, allow_pickle=False)`. Its *application schema* is
product-specific, not a PyTorch, safetensors, or cross-framework checkpoint
standard. The filename is used verbatim; no `.npz` suffix is silently appended.

| NPZ key | Contents |
|---------|----------|
| `manifest` | Scalar Unicode JSON: `format="az-tori-transformer-npz"`, `schema_version=1`, complete model `config`, optional `optimizer`, optional `rng`, caller-owned `metadata` object |
| `model/<name>` | Finite float64 parameter arrays, named by `model.named_parameters()` |
| `adam/m/<name>`, `adam/v/<name>` | Optional float64 first/second moments (second moments must be nonnegative) |

Adam metadata includes its completed step count, learning rate, both betas,
and epsilon. RNG metadata is the complete **PCG64** state used by
`numpy.random.default_rng`, including cached integer draws; other bit
generators are explicitly rejected. Metadata must contain finite,
JSON-serializable values. Store task settings, dataset identity/hash, loader
position, and token-ID vocabulary there as needed; the library does not infer
or enforce their meaning.

Loading rejects unknown schema versions, missing/extra array names, duplicate
JSON keys, mismatched shapes/dtypes, non-finite weights/moments, invalid config
or Adam settings, and object/pickle arrays. Saving checks that Adam owns this
model's parameters in order, writes a unique sibling `.pending` file, flushes
and fsyncs it, then atomically replaces the destination. Ordinary write failures
leave an existing checkpoint intact and remove the pending file. The parent
directory must already exist; filesystem errors propagate to the caller.

**Limits:** save only at completed optimizer-step boundaries. Gradients,
autograd graphs, external datasets/tokenizers, and data-loader internals are
not serialized. Exact continuation is tested on the same NumPy/runtime for
both positional modes; bitwise results across different NumPy/BLAS/platform
versions are not guaranteed. Use trusted, reasonably sized artifacts: no
resource limits, cryptographic authenticity, concurrent-writer coordination,
or full power-loss durability guarantee is provided. A process forcibly killed
before replacement may leave a sibling `.pending` file. This is a persistence
capability for an **ADJACENT TRACK / TRL-1** architecture, not a real-corpus
quality benchmark or a new physics claim. The HTTP demo is unchanged and
does not accept filesystem checkpoint paths.

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
  RoPE/T5-relative-bias Transformers on real language-modelling data. All
  published scores here are descriptive synthetic-task results. The legacy
  RoPE arm lacks the learned bank bias and is not parameter-matched; the
  `rope_matched` ablation controls parameter count and bias mechanism, but
  still says nothing about real-world sequence modelling.
* TRL-1: two synthetic tasks (plain copy, cyclic-wraparound copy) and the
  bounded user-corpus train/resume/sample workflow are tested. No real-corpus
  quality benchmark or hardware/throughput measurement is included.
  Independent per-coordinate torus attention remains a future direction, not
  an implemented feature.

## Tests

```bash
python -m pytest 12-AZ-IP/43-az-geometric-tori-transformer/tests/ -q
```

Tests cover: autograd gradient checks against finite differences to a
1e-7 tolerance (`test_tensor.py`), Z_74 lattice invariants plus an optional
cross-check against the Navigator's golden-vector export
(`test_toroidal_geometry.py`), rotary/bias periodicity properties
(`test_positional.py`, including exact modular collision diagnostics),
attention shape and causal-masking behaviour
(`test_attention.py`), model forward-pass determinism (`test_model.py`),
end-to-end training loss/accuracy regression (`test_training.py`), the
descriptive synthetic and matched-parameter positional ablations
(`test_baseline_benchmark.py`), and the JSON API
dispatch (`test_api.py`). `test_checkpoint.py` adds weights-only inference,
exact split-run Adam/RNG continuation in both positional modes, invalid-artifact
rejection, and atomic-write failure protection. `test_text_workflow.py`
exercises user-corpus training, resume compatibility checks, deterministic
sampling, and the CLI.

For checkpoint-only validation:

```bash
python -m pytest 12-AZ-IP/43-az-geometric-tori-transformer/tests/test_checkpoint.py -q
```

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
