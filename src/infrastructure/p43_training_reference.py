# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Independent NumPy forward/reverse equations for bounded P43 training checks.

No P43 Tensor, attention, positional or optimizer operation implements this
reference. P43 supplies the comparison model and initial weights only.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import numpy as np

from . import research_quantization as p43
from .artifact_io import publish_immutable
from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance


def _error(actual, expected):
    difference = np.abs(np.asarray(actual) - np.asarray(expected))
    if not np.all(np.isfinite(difference)):
        raise FloatingPointError("nonfinite implementation comparison")
    return float(np.max(difference))


def _norm(x, gamma, beta):
    centered = x - x.mean(axis=-1, keepdims=True)
    inverse = 1 / np.sqrt(np.mean(centered**2, axis=-1, keepdims=True) + 1e-5)
    normalized = centered * inverse
    return normalized * gamma + beta, (normalized, inverse, gamma)


def _norm_reverse(dy, cache):
    normalized, inverse, gamma = cache
    dz = dy * gamma
    dx = inverse * (
        dz - dz.mean(axis=-1, keepdims=True)
        - normalized * (dz * normalized).mean(axis=-1, keepdims=True)
    )
    axes = tuple(range(dy.ndim - 1))
    return dx, (dy * normalized).sum(axis=axes), dy.sum(axis=axes)


def _rotate(x, cosine, sine, reverse=False):
    even, odd = x[..., ::2], x[..., 1::2]
    sign = -1 if reverse else 1
    return np.stack(
        (even * cosine - sign * odd * sine, sign * even * sine + odd * cosine),
        axis=-1,
    ).reshape(x.shape)


def loss_and_gradients(weights, config, tokens, targets):
    """Return all-position logits, answer-only loss and all parameter gradients.

    Supports bounded, causal toroidal P43 configs and caller-owned float64
    arrays. Labels affect loss only, never the forward computation.
    """
    if not isinstance(weights, dict) or not weights or any(not isinstance(w, np.ndarray) for w in weights.values()):
        raise ValueError("weights must be a nonempty dictionary of arrays")
    cfg = p43._validate_model_size(config, sum(w.size for w in weights.values()))
    if not cfg.causal or cfg.positional_mode != "toroidal":
        raise ValueError("reference supports causal toroidal models only")
    if not isinstance(tokens, np.ndarray) or tokens.dtype.kind not in "iu":
        raise ValueError("tokens must be an integer array")
    if tokens.ndim != 2 or not 1 <= tokens.shape[0] <= 128 or not 1 <= tokens.shape[1] <= 128:
        raise ValueError("token batch/context exceeds reference bounds")
    if np.any(tokens < 0) or np.any(tokens >= cfg.vocab_size):
        raise ValueError("token ID outside vocabulary")
    if not isinstance(targets, np.ndarray) or targets.dtype.kind not in "iu":
        raise ValueError("targets must be an integer array")
    if targets.shape != (tokens.shape[0],) or np.any(targets < 0) or np.any(targets >= cfg.vocab_size):
        raise ValueError("targets must contain one in-vocabulary answer per prompt")
    batch, length = tokens.shape
    activation_elements = batch * length * (cfg.dim + cfg.vocab_size) + cfg.num_layers * (
        batch * cfg.num_heads * length**2 + batch * length * (cfg.dim + cfg.ff_hidden_dim)
    )
    if activation_elements > 4_000_000:
        raise ValueError("reference activation workspace exceeds the element bound")
    # Validate exact parameter names/shapes without using the model forward path.
    _, Model, _, _ = p43._p43_api()
    expected = Model(cfg).named_parameters()
    if set(weights) != set(expected):
        raise ValueError("reference weight names do not match model")
    for name, value in weights.items():
        if not isinstance(value, np.ndarray) or value.dtype != np.float64:
            raise ValueError("reference requires float64 weights")
        if value.shape != expected[name].data.shape or not np.all(np.isfinite(value)):
            raise ValueError("reference weight shape or finiteness mismatch")
    grads = {name: np.zeros_like(value) for name, value in weights.items()}
    heads, width = cfg.num_heads, cfg.dim // cfg.num_heads
    pair = np.arange(width // 2)
    steps = np.where(pair % 2 == 0, 5, 7) * (pair + 1)
    angles = 2 * np.pi * ((np.arange(length)[:, None] * steps) % 74) / 74
    cosine, sine = np.cos(angles), np.sin(angles)
    banks = (193 * np.arange(length)) % 74
    distance = (banks[:, None] - banks[None, :]) % 74
    distance = np.minimum(distance, 74 - distance)

    def linear(x, prefix):
        return x @ weights[prefix + ".weight"] + (
            weights[prefix + ".bias"] if prefix + ".bias" in weights else 0
        )

    def linear_reverse(dy, x, prefix):
        grads[prefix + ".weight"] += x.reshape(-1, x.shape[-1]).T @ dy.reshape(-1, dy.shape[-1])
        if prefix + ".bias" in grads:
            grads[prefix + ".bias"] += dy.sum(axis=tuple(range(dy.ndim - 1)))
        return dy @ weights[prefix + ".weight"].T

    x = weights["token_embedding.weight"][tokens]
    caches = []
    for index in range(cfg.num_layers):
        prefix = f"blocks.{index}"
        z, norm1 = _norm(x, weights[prefix + ".ln1.gamma"], weights[prefix + ".ln1.beta"])
        q, k, v = [
            linear(z, prefix + ".attn." + name).reshape(batch, length, heads, width).transpose(0, 2, 1, 3)
            for name in ("wq", "wk", "wv")
        ]
        q, k = _rotate(q, cosine, sine), _rotate(k, cosine, sine)
        scores = q @ k.swapaxes(-1, -2) / np.sqrt(width)
        scores += weights[prefix + ".attn.relative_bias"][:, distance][None]
        scores += np.triu(np.full((length, length), -1e9), k=1)
        scores -= scores.max(axis=-1, keepdims=True)
        probabilities = np.exp(scores)
        probabilities /= probabilities.sum(axis=-1, keepdims=True)
        merged = (probabilities @ v).transpose(0, 2, 1, 3).reshape(batch, length, cfg.dim)
        residual = x + linear(merged, prefix + ".attn.wo")
        z2, norm2 = _norm(residual, weights[prefix + ".ln2.gamma"], weights[prefix + ".ln2.beta"])
        hidden = linear(z2, prefix + ".ff.fc1")
        tanh = np.tanh(np.sqrt(2 / np.pi) * (hidden + 0.044715 * hidden**3))
        activated = 0.5 * hidden * (1 + tanh)
        x = residual + linear(activated, prefix + ".ff.fc2")
        caches.append((prefix, z, norm1, q, k, v, probabilities, merged, z2, norm2, hidden, tanh, activated))
    final, final_cache = _norm(x, weights["ln_final.gamma"], weights["ln_final.beta"])
    logits = linear(final, "head")
    answer = logits[:, -1]
    shifted = answer - answer.max(axis=-1, keepdims=True)
    probability = np.exp(shifted)
    probability /= probability.sum(axis=-1, keepdims=True)
    loss = float(np.mean(np.log(np.exp(shifted).sum(axis=-1)) - shifted[np.arange(batch), targets]))
    dlogits = np.zeros_like(logits)
    probability[np.arange(batch), targets] -= 1
    dlogits[:, -1] = probability / batch
    dx, grads["ln_final.gamma"], grads["ln_final.beta"] = _norm_reverse(
        linear_reverse(dlogits, final, "head"), final_cache,
    )
    for cache in reversed(caches):
        prefix, z, norm1, q, k, v, probabilities, merged, z2, norm2, hidden, tanh, activated = cache
        dactivation = linear_reverse(dx, activated, prefix + ".ff.fc2")
        dhidden = dactivation * (
            0.5 * (1 + tanh)
            + 0.5 * hidden * (1 - tanh**2) * np.sqrt(2 / np.pi) * (1 + 3 * 0.044715 * hidden**2)
        )
        dresidual, grads[prefix + ".ln2.gamma"], grads[prefix + ".ln2.beta"] = _norm_reverse(
            linear_reverse(dhidden, z2, prefix + ".ff.fc1"), norm2,
        )
        dresidual += dx
        dmerged = linear_reverse(dresidual, merged, prefix + ".attn.wo")
        dout = dmerged.reshape(batch, length, heads, width).transpose(0, 2, 1, 3)
        dp = dout @ v.swapaxes(-1, -2)
        dv = probabilities.swapaxes(-1, -2) @ dout
        ds = probabilities * (dp - (dp * probabilities).sum(axis=-1, keepdims=True))
        for head in range(heads):
            np.add.at(grads[prefix + ".attn.relative_bias"][head], distance, ds[:, head].sum(axis=0))
        dq = _rotate(ds @ k / np.sqrt(width), cosine, sine, reverse=True)
        dk = _rotate(ds.swapaxes(-1, -2) @ q / np.sqrt(width), cosine, sine, reverse=True)
        dz = np.zeros_like(z)
        for derivative, name in ((dq, "wq"), (dk, "wk"), (dv, "wv")):
            derivative = derivative.transpose(0, 2, 1, 3).reshape(batch, length, cfg.dim)
            dz += linear_reverse(derivative, z, prefix + ".attn." + name)
        dx, grads[prefix + ".ln1.gamma"], grads[prefix + ".ln1.beta"] = _norm_reverse(dz, norm1)
        dx += dresidual
    np.add.at(grads["token_embedding.weight"], tokens, dx)
    if not np.isfinite(loss) or not np.all(np.isfinite(logits)) or any(not np.all(np.isfinite(g)) for g in grads.values()):
        raise FloatingPointError("nonfinite reference loss, logits or gradients")
    return logits, loss, grads


def compare_training(*, steps=5, seed=43118, dim=32, layers=1, length=4, decay=0.1):
    """Compare every gradient and successive Adam updates on constructed inputs.

    This is implementation parity, not a held-out quality evaluation.
    """
    if type(steps) is not int or not 1 <= steps <= 20:
        raise ValueError("comparison steps must be in [1,20]")
    if type(seed) is not int or seed < 0 or type(dim) is not int or dim not in (8, 16, 32, 48):
        raise ValueError("invalid bounded comparison seed or dimension")
    if type(layers) is not int or not 0 <= layers <= 2 or type(length) is not int or not 1 <= length <= 128:
        raise ValueError("invalid comparison layers or context")
    if type(decay) not in (int, float) or not np.isfinite(decay) or not 0 <= decay <= 1:
        raise ValueError("decay must be finite and in [0,1]")
    Adam, Model, Config, cross_entropy = p43._p43_api()
    config = Config(vocab_size=14, dim=dim, num_heads=2 if dim == 8 else 4,
                    num_layers=layers, ff_hidden_dim=dim * 2, seed=seed)
    native = Model(config)
    optimizer = Adam(native.parameters(), lr=0.001)
    weights = {name: parameter.data.copy() for name, parameter in native.named_parameters().items()}
    moments = {name: (np.zeros_like(w), np.zeros_like(w)) for name, w in weights.items()}
    rng = np.random.default_rng(seed + 1)
    records = []
    for step in range(1, steps + 1):
        tokens = rng.integers(0, 14, size=(3, length))
        targets = rng.integers(0, 14, size=3)
        optimizer.zero_grad()
        logits, _ = native(tokens)
        loss = cross_entropy(logits[:, -1, :], targets)
        loss.backward()
        ref_logits, ref_loss, gradients = loss_and_gradients(weights, asdict(config), tokens, targets)
        gradient_error = max(_error(p.grad, gradients[name])
                             for name, p in native.named_parameters().items())
        logits_error = _error(logits.data, ref_logits)
        loss_error = _error(loss.data, ref_loss)
        # An independently stateful implementation of the published Adam equations.
        for name, w in weights.items():
            m, v = moments[name]
            g = gradients[name]
            m[:] = 0.9 * m + 0.1 * g
            v[:] = 0.999 * v + 0.001 * g**2
            w -= 0.001 * (m / (1 - 0.9**step)) / (np.sqrt(v / (1 - 0.999**step)) + 1e-8)
            w *= 1 - 0.001 * decay
        optimizer.step()
        for p in native.parameters():
            p.data *= 1 - 0.001 * decay
        weight_error = max(_error(p.data, weights[name])
                           for name, p in native.named_parameters().items())
        moment_error = max(
            _error(native_moment, reference_moment)
            for index, name in enumerate(weights)
            for native_moment, reference_moment in (
                (optimizer.m[index], moments[name][0]), (optimizer.v[index], moments[name][1])
            )
        )
        records.append({"step": step, "max_gradient_absolute_error": gradient_error,
                        "max_logits_absolute_error": logits_error, "loss_absolute_error": loss_error,
                        "max_updated_weight_absolute_error": weight_error,
                        "max_optimizer_moment_absolute_error": moment_error})
    return {
        "config": asdict(config), "steps": records, "parameter_count": native.num_parameters(),
        "context": length, "decay": decay, "learning_rate": 0.001,
        "tolerance_absolute": 1e-9,
        "passed": all(value <= 1e-9 for row in records for key, value in row.items() if key != "step"),
        "scope": "All-parameter CPU float64 implementation parity on constructed training inputs; no holdout, model utility, GPU or long-trajectory equivalence claim.",
    }


def compare_checkpoint(content):
    """Compare every gradient on the failed modulo-11 model's training rows only."""
    from .arithmetic_generalization import _v2_rows
    from .model_interchange import load_inference_checkpoint

    loaded = load_inference_checkpoint(content)
    if loaded.metadata.get("task") != "mod11_answer_only_weight_decay_v2":
        raise ValueError("checkpoint diagnostic supports the recorded modulo-11 task only")
    vocabulary = loaded.metadata.get("vocabulary")
    if vocabulary != sorted("\n+=ABCDEFGHIJK"):
        raise ValueError("checkpoint vocabulary differs from the declared task")
    model = loaded.model
    mapping = {character: index for index, character in enumerate(vocabulary)}
    rows = _v2_rows("train")
    tokens = np.array([[mapping[c] for c in row[:4]] for row in rows])
    targets = np.array([mapping[row[4]] for row in rows])
    for parameter in model.parameters():
        parameter.zero_grad()
    _, _, _, cross_entropy = p43._p43_api()
    logits, _ = model(tokens)
    loss = cross_entropy(logits[:, -1], targets)
    loss.backward()
    weights = {name: p.data.copy() for name, p in model.named_parameters().items()}
    ref_logits, ref_loss, gradients = loss_and_gradients(weights, asdict(model.cfg), tokens, targets)
    errors = {name: _error(p.grad, gradients[name])
              for name, p in model.named_parameters().items()}
    logits_error = _error(logits.data, ref_logits)
    loss_error = _error(loss.data, ref_loss)
    return {
        "checkpoint_sha256": hashlib.sha256(content).hexdigest(),
        "training_rows": len(rows),
        "training_rows_sha256": hashlib.sha256("".join(rows).encode("ascii")).hexdigest(),
        "parameter_gradient_absolute_errors": errors,
        "max_logits_absolute_error": logits_error, "loss_absolute_error": loss_error,
        "tolerance_absolute": 1e-9,
        "passed": max([*errors.values(), logits_error, loss_error]) <= 1e-9,
        "scope": "Read-only all-gradient parity on the selected failed model's training data; no test evaluation or update.",
    }


def benchmark(output_dir, checkpoint=None):
    """Publish deterministic source-bound parity measurements, including wraparound."""
    measurements = [
        compare_training(),
        compare_training(dim=16, layers=2, length=7),
        compare_training(steps=2, dim=8, length=75),
    ]
    report = {
        "schema_version": "az_p43_independent_training_reference_v1",
        "numpy_version": np.__version__, "measurements": measurements,
        "passed": all(row["passed"] for row in measurements),
        "implementation_sha256": {
            "src/infrastructure/p43_training_reference.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            **p43._source_identities(),
        },
        "external_runtime": "Explicit NumPy reverse equations, not a PyTorch comparison.",
    }
    if checkpoint is not None:
        from .model_interchange import _read_model

        report["failed_checkpoint_training_parity"] = compare_checkpoint(_read_model(Path(checkpoint)))
        report["passed"] = report["passed"] and report["failed_checkpoint_training_parity"]["passed"]
        report["implementation_sha256"].update({
            name: hashlib.sha256((p43._REPO_ROOT / name).read_bytes()).hexdigest()
            for name in ("src/infrastructure/arithmetic_generalization.py",
                         "src/infrastructure/model_interchange.py",
                         "src/infrastructure/tokenizer_interchange.py")
        })
    report["execution_spine"] = ExecutionSpineRecord(
        surface_id="p43-independent-training-reference", surface_kind="benchmark",
        lane="az_ml_infrastructure",
        generated_at_utc=None,
        canonical_paths=["src/infrastructure/p43_training_reference.py"],
        sources=[], health_checks=[], summary=report["measurements"][0]["scope"],
        status="ready" if report["passed"] else "blocked",
        governance=build_fail_closed_governance(
            epistemic_label="independent equations on constructed CPU training inputs",
            promotion_rule="Implementation parity does not establish model generalization or production readiness.",
            residual_blockers=["Model utility and sub-4-bit fidelity remain unqualified."],
        ),
        promotion={"eligible": False, "physics_claim": False},
    ).to_dict()
    content = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii") + b"\n"
    path = publish_immutable(Path(output_dir), hashlib.sha256(content).hexdigest(), content)
    return path, report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--checkpoint", help="Optional retained failed modulo-11 inference checkpoint")
    args = parser.parse_args(argv)
    path, report = benchmark(args.output_dir, args.checkpoint)
    print(json.dumps({"evidence": str(path), "passed": report["passed"]}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
