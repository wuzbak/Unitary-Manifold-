# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Local, bounded Product 16/43 adapters; no network or implicit model fallback.

Checkpoint identifiers and destinations are operator configuration, never request
paths. To train, predeclare an identifier whose destination is inside state_dir.
The corpus is explicit UTF-8 text (at most 64 KiB), not a filesystem reference.
All scores and synthetic experiments are descriptive, not scientific authority.
This internal registry does not authorize requests: the host must bind and
approve effectful calls before invoking it.
"""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
from uuid import uuid4


_PRODUCTS = {
    "az_tori_transformer": "43-az-geometric-tori-transformer",
    "oracle": "16-oracle",
}
_DIMENSIONS = (
    "Transparency", "Sequence Integrity", "Participation", "Accountability",
    "Resilience", "Epistemic Honesty", "Freedom Floor",
)
_IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
_ACTIONS = {
    "geometry": (False, "Exact Product 43 modular position and alias diagnostics."),
    "oracle": (False, "Product 16 synthesis of five explicit bodies and seven scores."),
    "generate": (False, "Local character generation from an operator-configured checkpoint."),
    "experiment": (True, "Bounded four-arm rotary-schedule × learned-bias synthetic experiment."),
    "train": (True, "Bounded Product 43 character training on explicit approved text."),
}


def _integer(name, value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return value


def _number(name, value, low, high):
    if type(value) not in (int, float) or not low <= value <= high:
        raise ValueError(f"{name} must be finite and in [{low}, {high}]")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite and in [{low}, {high}]")
    return float(value)


def _text(name, value, maximum=4096, *, empty=False):
    if type(value) is not str or (not value and not empty) or len(value) > maximum:
        raise ValueError(f"{name} must be {'possibly empty ' if empty else 'nonempty '}text, at most {maximum} characters")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{name} must be valid UTF-8 text") from exc
    return value


def _identifier(value):
    if type(value) is not str or not _IDENTIFIER.fullmatch(value):
        raise ValueError("checkpoint_id must match [A-Za-z][A-Za-z0-9_-]{0,63}")
    return value


def _keys(arguments, allowed, required=()):
    unknown = set(arguments) - set(allowed)
    missing = set(required) - set(arguments)
    if unknown or missing:
        raise ValueError(f"invalid arguments: unknown={sorted(unknown)}, missing={sorted(missing)}")


def _json_input(value, depth=0):
    if depth > 16:
        raise ValueError("arguments exceed JSON nesting limit")
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) is list:
        for item in value:
            _json_input(item, depth + 1)
        return
    if type(value) is dict and all(type(key) is str for key in value):
        for item in value.values():
            _json_input(item, depth + 1)
        return
    raise ValueError("arguments must contain only finite JSON values with string object keys")


class Backends:
    """Registry for local adapters. Merely constructing it performs no writes."""

    def __init__(self, repo_root: Path, state_dir: Path, checkpoints: dict[str, Path] | None = None):
        self.repo_root = Path(repo_root).resolve()
        self.state_dir = Path(state_dir).resolve()
        if checkpoints is not None and type(checkpoints) is not dict:
            raise ValueError("checkpoints must be an operator-configured dictionary")
        self.checkpoints = {}
        for key, path in (checkpoints or {}).items():
            _identifier(key)
            if not isinstance(path, Path):
                raise ValueError("checkpoint destinations must be pathlib.Path objects")
            self.checkpoints[key] = path.resolve()

    def _import(self, module):
        package = module.split(".", 1)[0]
        root = self.repo_root / "12-AZ-IP" / _PRODUCTS[package]
        expected = (root / package / "__init__.py").resolve()
        if not expected.is_file():
            raise ImportError(f"local provider {package} is absent")
        cached = sys.modules.get(package)
        if cached is not None and Path(getattr(cached, "__file__", "") or "").resolve() != expected:
            raise ImportError(f"{package} name collision with a different installed package")
        original = list(sys.path)
        try:
            sys.path.insert(0, str(root))
            return importlib.import_module(module)
        finally:
            sys.path[:] = original

    def _available(self, package):
        root = self.repo_root / "12-AZ-IP" / _PRODUCTS[package] / package
        cached = sys.modules.get(package)
        if cached is not None and Path(getattr(cached, "__file__", "") or "").resolve() != (root / "__init__.py").resolve():
            return False
        return (root / "__init__.py").is_file() and (
            package == "oracle" or importlib.util.find_spec("numpy") is not None
        )

    def capabilities(self) -> dict[str, dict]:
        result = {}
        for action, (effect, description) in _ACTIONS.items():
            provider = "oracle" if action == "oracle" else "az_tori_transformer"
            available = self._available(provider)
            if action == "generate":
                available = available and any(path.is_file() for path in self.checkpoints.values())
            if action == "train":
                available = available and any(
                    path.is_relative_to(self.state_dir) and path.suffix == ".npz"
                    for path in self.checkpoints.values()
                )
            result[action] = {"effect": effect, "description": description, "available": available}
        return result

    def execute(self, action: str, arguments: dict) -> dict:
        if type(action) is not str or action not in _ACTIONS:
            raise ValueError(f"unknown backend action: {action!r}")
        if type(arguments) is not dict:
            raise ValueError("arguments must be a JSON object")
        _json_input(arguments)
        try:
            size = len(json.dumps(arguments, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        except (UnicodeEncodeError, ValueError) as exc:
            raise ValueError("arguments must be finite UTF-8 JSON") from exc
        if size > 131072:
            raise ValueError("arguments exceed the 128 KiB JSON limit")
        result = getattr(self, f"_{action}")(arguments)
        result["metadata"] = {
            "provider": "Product16.SynthesisOrchestrator" if action == "oracle" else "Product43.az_tori_transformer",
            "evidence_kind": {
                "geometry": "exact_modular_diagnostic",
                "oracle": "input_derived_heuristic",
                "generate": "local_checkpoint_inference",
                "train": "measured_local_training",
                "experiment": "measured_synthetic_factorial",
            }[action],
            "task": result["task"],
            "effect": _ACTIONS[action][0],
            "claims_superiority": False,
            "physics_claim": False,
            "limitations": "Descriptive local software evidence, not authority or evidence of general superiority.",
            "implementation_sha256": self._implementation_digest(action),
        }
        json.dumps(result, allow_nan=False)
        return result

    def _implementation_digest(self, action):
        package = "oracle" if action == "oracle" else "az_tori_transformer"
        root = self.repo_root / "12-AZ-IP" / _PRODUCTS[package] / package
        digest = hashlib.sha256()
        for path in [Path(__file__), *sorted(root.rglob("*.py"))]:
            label = "az_weave/backends.py" if path == Path(__file__) else str(path.relative_to(root))
            digest.update(label.encode("utf-8") + b"\0")
            digest.update(path.read_bytes())
        return digest.hexdigest()

    def _geometry(self, args):
        _keys(args, {"head_dim"})
        dim = _integer("head_dim", args.get("head_dim", 8), 2, 64)
        if dim % 2:
            raise ValueError("head_dim must be even")
        geometry = self._import("az_tori_transformer.toroidal_geometry")
        positional = self._import("az_tori_transformer.positional")
        return {
            "task": "exact_modular_position_diagnostics",
            "config": {
                "lattice_order": geometry.LATTICE_ORDER,
                "windings": list(geometry.BRAID_WINDINGS),
                "tick_phase_step": geometry.TICK_PHASE_STEP,
                "head_dim": dim,
                "bank_semantics": "scalar projection of two-coordinate code, not independent axes",
                "position_semantics": "finite modular aliasing, not physical information flow",
            },
            "alias_period": math.lcm(*positional.rotation_orbit_periods(dim).tolist()),
            "diagnostics": positional.modular_alias_diagnostics(80, dim),
            "positions": [
                {"position": i, "code": list(geometry.position_code(i)), "bank": geometry.position_bank(i)}
                for i in range(80)
            ],
        }

    def _oracle(self, args):
        _keys(args, {"system_name", "system_type", "body_specs", "dim_scores", "context",
                     "decision_question", "decision_options", "commitments"},
              {"system_name", "system_type", "body_specs", "dim_scores"})
        name = _text("system_name", args["system_name"], 256)
        kind = _text("system_type", args["system_type"], 256)
        context = _text("context", args.get("context", ""), empty=True)
        bodies = args["body_specs"]
        if type(bodies) is not list or len(bodies) != 5:
            raise ValueError("exactly five explicit body_specs are required")
        fields = {"name", "label", "status", "phi_trust", "description", "foundations",
                  "constraints", "open_gaps", "falsifiable_commitment"}
        labels = []
        for body in bodies:
            if type(body) is not dict:
                raise ValueError("each body_spec must be an object")
            _keys(body, fields, {"label", "status", "phi_trust"})
            if body["status"] not in ("SOLID", "CONSTRAINED", "ESTIMATED", "OPEN"):
                raise ValueError("body status must be SOLID, CONSTRAINED, ESTIMATED, or OPEN")
            _number("phi_trust", body["phi_trust"], 0, 1)
            for key, value in body.items():
                if key != "phi_trust":
                    _text(f"body.{key}", value, empty=key not in {"label", "status", "name"})
            labels.append(body["label"])
        if len(set(labels)) != 5:
            raise ValueError("body labels must be distinct")
        scores = args["dim_scores"]
        if type(scores) is not dict or set(scores) != set(_DIMENSIONS):
            raise ValueError(f"dim_scores must explicitly contain exactly {list(_DIMENSIONS)}")
        for key, value in scores.items():
            _number(key, value, 0, 1)
        question = _text("decision_question", args.get("decision_question", ""), empty=True)
        options = args.get("decision_options", [])
        if type(options) is not list or len(options) > 8:
            raise ValueError("decision_options must be a list of at most eight explicit alternatives")
        if bool(question) != bool(options) or (options and len(options) < 2):
            raise ValueError("decision analysis requires a nonempty question and two to eight alternatives")
        names = []
        for option in options:
            if type(option) is not dict:
                raise ValueError("decision alternative must be an object")
            _keys(option, {"name", "description", "impacts", "phi_trust_impact"},
                  {"name", "impacts", "phi_trust_impact"})
            names.append(_text("option.name", option["name"], 256))
            _text("option.description", option.get("description", ""), empty=True)
            _number("phi_trust_impact", option["phi_trust_impact"], -1, 1)
            impacts = option["impacts"]
            if type(impacts) is not list or len(impacts) > 5:
                raise ValueError("option impacts must be a list of at most five explicit body impacts")
            impacted = []
            for impact in impacts:
                if type(impact) is not dict:
                    raise ValueError("body impact must be an object")
                _keys(impact, {"body_label", "direction", "magnitude"}, {"body_label", "direction", "magnitude"})
                label = _text("impact.body_label", impact["body_label"])
                if label not in labels:
                    raise ValueError("impact body_label must identify an explicit body")
                impacted.append(label)
                if impact["direction"] not in ("improve", "harm", "neutral"):
                    raise ValueError("impact direction must be improve, harm, or neutral")
                _number("impact.magnitude", impact["magnitude"], 0, 2)
            if len(set(impacted)) != len(impacted):
                raise ValueError("alternative cannot repeat a body impact")
        if len(set(names)) != len(names):
            raise ValueError("decision alternative names must be distinct")
        commitments = args.get("commitments", [])
        if type(commitments) is not list or len(commitments) > 16:
            raise ValueError("commitments must be a list of at most sixteen commitments")
        commitment_fields = {"domain", "commitment", "falsification_condition", "test_horizon"}
        for commitment in commitments:
            if type(commitment) is not dict:
                raise ValueError("commitment must be an object")
            _keys(commitment, commitment_fields, commitment_fields)
            for field, value in commitment.items():
                _text(f"commitment.{field}", value)
        module = self._import("oracle.engine.synthesis")
        report = module.SynthesisOrchestrator().synthesize(
            system_name=name, system_type=kind, body_specs=bodies, dim_scores=scores, context=context,
            decision_question=question, decision_options=options, commitments=commitments,
        )
        return {
            "task": "explicit_input_synthesis",
            "report": asdict(report),
            "scores": {"omega": report.omega_score, "integrity": report.integrity_score,
                       "synthesis": report.synthesis_score},
            "interpretation": "Scores are explanatory transformations of supplied assessments, not independently verified authority or physics claims.",
        }

    def _checkpoint(self, args, *, writing=False):
        key = _identifier(args.get("checkpoint_id"))
        if key not in self.checkpoints:
            raise ValueError("checkpoint_id is not in the operator-configured allowlist")
        path = self.checkpoints[key]
        if writing:
            if path.suffix != ".npz" or not path.resolve().is_relative_to(self.state_dir):
                raise ValueError("training checkpoint must be an .npz destination inside state_dir")
        elif not path.is_file():
            raise RuntimeError("configured checkpoint is unavailable; train it or configure a real checkpoint")
        return key, path

    def _generate(self, args):
        _keys(args, {"checkpoint_id", "prompt", "max_new_tokens", "temperature", "top_k", "seed"},
              {"checkpoint_id", "prompt"})
        key, path = self._checkpoint(args)
        prompt = _text("prompt", args["prompt"], 128)
        count = _integer("max_new_tokens", args.get("max_new_tokens", 32), 1, 128)
        temperature = _number("temperature", args.get("temperature", 1.0), 0.001, 100)
        seed = _integer("seed", args.get("seed", 0), 0, 2**32 - 3)
        top_k = args.get("top_k")
        if top_k is not None:
            _integer("top_k", top_k, 1, 256)
        digest = self._sha(path)
        loaded = self._load_bounded_checkpoint(path)
        workflow = self._import("az_tori_transformer.text_workflow")
        generated = workflow.generate_text(
            path, prompt, max_new_tokens=count, temperature=temperature, top_k=top_k, seed=seed
        )
        if self._sha(path) != digest:
            raise RuntimeError("configured checkpoint changed during generation; retry with a stable checkpoint")
        return {"task": "character_language_model", "checkpoint_id": key,
                "checkpoint_sha256": digest, "model_config": asdict(loaded.model.cfg),
                "prompt": prompt, "text": generated, "max_new_tokens": count, "seed": seed}

    def _load_bounded_checkpoint(self, path):
        import numpy as np

        # Check allocation-driving fields before the provider builds a model.
        archive = np.load(path, allow_pickle=False)
        if not isinstance(archive, np.lib.npyio.NpzFile):
            raise ValueError("checkpoint must be an NPZ archive")
        with archive:
            if "manifest" not in archive:
                raise ValueError("checkpoint is missing its manifest")
            manifest = archive["manifest"]
            if manifest.shape != () or manifest.dtype.kind not in ("U", "S"):
                raise ValueError("checkpoint manifest must be a scalar JSON string")
            payload = json.loads(str(manifest.item()))
        if type(payload) is not dict or type(payload.get("config")) is not dict or type(payload.get("metadata")) is not dict:
            raise ValueError("checkpoint requires object config and metadata")
        cfg = payload["config"]
        for name, value, low, high in (
            ("dim", cfg.get("dim"), 2, 64), ("num_heads", cfg.get("num_heads"), 1, 8),
            ("num_layers", cfg.get("num_layers"), 1, 2), ("ff_hidden_dim", cfg.get("ff_hidden_dim"), 1, 256),
            ("vocab_size", cfg.get("vocab_size"), 1, 256),
            ("context_length", payload["metadata"].get("context_length"), 2, 128),
        ):
            _integer(f"checkpoint {name}", value, low, high)
        checkpoint = self._import("az_tori_transformer.checkpoint")
        return checkpoint.load_checkpoint(path)

    @staticmethod
    def _settings(args, *, experiment=False):
        values = {
            "steps": _integer("steps", args.get("steps", 8), 1, 100),
            "batch_size": _integer("batch_size", args.get("batch_size", 2), 1, 16),
            "dim": _integer("dim", args.get("dim", 8), 2, 64),
            "context_length": _integer("context_length", args.get("context_length", 12), 2, 128),
            "num_heads": _integer("num_heads", args.get("num_heads", 2), 1, 8),
            "num_layers": _integer("num_layers", args.get("num_layers", 1), 1, 2),
            "seed": _integer("seed", args.get("seed", 0), 0, 2**32 - 3),
            "learning_rate": _number("learning_rate", args.get("learning_rate", 0.01), 0.000001, 0.1),
        }
        if values["dim"] % values["num_heads"] or (values["dim"] // values["num_heads"]) % 2:
            raise ValueError("dim must be divisible by num_heads with an even head dimension")
        cells = values["steps"] * values["batch_size"] * values["context_length"]**2 * values["num_heads"] * values["num_layers"]
        if cells * ((12 if args.get("alias_probe", False) else 8) if experiment else 1) > 20_000_000:
            raise ValueError("settings exceed the bounded attention-work budget")
        return values

    def _private_dir(self, path):
        if not path.resolve().is_relative_to(self.state_dir):
            raise ValueError("output must remain inside state_dir")
        self.state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.state_dir.chmod(0o700)
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not path.resolve().is_relative_to(self.state_dir):
            raise ValueError("output directory escaped state_dir")
        path.chmod(0o700)

    def _write_private(self, path, raw):
        self._private_dir(path.parent)
        pending = path.with_name(f".{path.name}.{uuid4().hex}.pending")
        try:
            descriptor = os.open(pending, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(pending, path)
        finally:
            pending.unlink(missing_ok=True)

    @staticmethod
    def _sha(path):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _train(self, args):
        _keys(args, {"checkpoint_id", "corpus", "steps", "batch_size", "dim", "context_length",
                     "num_heads", "num_layers", "seed", "learning_rate", "validation_fraction",
                     "resume", "expected_checkpoint_sha256"},
              {"checkpoint_id", "corpus"})
        key, path = self._checkpoint(args, writing=True)
        resume = args.get("resume", False)
        if type(resume) is not bool:
            raise ValueError("resume must be a boolean")
        expected = args.get("expected_checkpoint_sha256")
        if resume:
            if type(expected) is not str or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
                raise ValueError("resume requires expected_checkpoint_sha256 as 64 lowercase hex characters")
            if not path.is_file():
                raise RuntimeError("resume requires an existing configured checkpoint")
            if self._sha(path) != expected:
                raise ValueError("expected_checkpoint_sha256 does not match the current checkpoint")
            loaded = self._load_bounded_checkpoint(path)
            if loaded.optimizer is None or loaded.rng is None:
                raise ValueError("resume requires optimizer and RNG state")
            defaults = {
                "dim": loaded.model.cfg.dim, "num_heads": loaded.model.cfg.num_heads,
                "num_layers": loaded.model.cfg.num_layers,
                "context_length": loaded.metadata.get("context_length"),
                "learning_rate": loaded.optimizer.lr,
                "validation_fraction": loaded.metadata.get("validation_fraction"),
            }
        else:
            if expected is not None:
                raise ValueError("expected_checkpoint_sha256 is only valid with resume=True")
            defaults = {}
        settings = self._settings({**defaults, **args})
        fraction = _number("validation_fraction", args.get("validation_fraction", defaults.get("validation_fraction", 0.2)), 0.05, 0.4)
        text = _text("corpus", args["corpus"], 65536)
        raw = text.encode("utf-8")
        if len(raw) > 65536 or len(set(text)) > 256:
            raise ValueError("corpus must be at most 64 KiB with at most 256 distinct characters")
        validation_size = int(len(text) * fraction)
        if min(validation_size, len(text) - validation_size) <= settings["context_length"]:
            raise ValueError("both corpus splits must contain at least context_length + 1 characters")
        if resume:
            metadata = loaded.metadata
            actual = {
                "task": "character_language_model", "dataset_sha256": hashlib.sha256(raw).hexdigest(),
                "context_length": settings["context_length"], "validation_fraction": fraction,
                "vocabulary": sorted(set(text)), "tokenizer": "unicode_codepoint",
            }
            if any(metadata.get(field) != value for field, value in actual.items()):
                raise ValueError("resume corpus or task settings do not match the checkpoint")
            cfg = loaded.model.cfg
            if not cfg.causal or cfg.vocab_size != len(actual["vocabulary"]):
                raise ValueError("resume requires a compatible causal character checkpoint")
            if any(getattr(cfg, field) != settings[field] for field in ("dim", "num_heads", "num_layers")):
                raise ValueError("resume model dimensions must match the checkpoint")
            if loaded.optimizer.lr != settings["learning_rate"]:
                raise ValueError("resume learning_rate must match the checkpoint optimizer")
            if self._sha(path) != expected:
                raise ValueError("checkpoint changed during resume validation")
        workflow = self._import("az_tori_transformer.text_workflow")
        checkpoint = self._import("az_tori_transformer.checkpoint")
        self._private_dir(path.parent)
        corpus_path = self.state_dir / "corpora" / f"{key}-{uuid4().hex}.txt"
        self._write_private(corpus_path, raw)
        metrics = workflow.train_text_file(
            corpus_path, path, **settings, validation_fraction=fraction, resume=resume
        )
        path.chmod(0o600)
        loaded = checkpoint.load_checkpoint(path)
        return {
            "task": "character_language_model", "checkpoint_id": key,
            "checkpoint_sha256": self._sha(path), "model_config": asdict(loaded.model.cfg),
            "metrics": metrics,
            "corpus_sha256": hashlib.sha256(raw).hexdigest(),
            "resumed_from_checkpoint_sha256": expected,
            "corpus_provenance": "Explicit caller-supplied text; caller is responsible for approval. No repository archives read.",
        }

    def _experiment(self, args):
        _keys(args, {"steps", "batch_size", "dim", "context_length", "num_heads",
                     "num_layers", "seed", "learning_rate", "alias_probe"})
        alias_probe = args.get("alias_probe", False)
        if type(alias_probe) is not bool:
            raise ValueError("alias_probe must be a boolean")
        settings = self._settings(args, experiment=True)
        if alias_probe and settings["context_length"] < 75:
            raise ValueError("alias_probe requires context_length >= 75 to distinguish offsets 0 and 74")
        import numpy as np

        model_module = self._import("az_tori_transformer.model")
        tensor = self._import("az_tori_transformer.tensor")
        optim = self._import("az_tori_transformer.optim")
        seq_len = settings["context_length"]
        tasks = {}
        task_names = ["periodic_copy", "nonperiodic_copy"]
        if alias_probe:
            task_names.append("alias74_lag_copy")
        for task in task_names:
            models = {}
            for mode in ("toroidal", "rope_matched"):
                for bias in (False, True):
                    arm = f"{mode}_bias_{'on' if bias else 'off'}"
                    cfg = model_module.GeometricToriTransformerConfig(
                        vocab_size=8, dim=settings["dim"], num_heads=settings["num_heads"],
                        num_layers=settings["num_layers"], causal=False,
                        seed=settings["seed"], positional_mode=mode,
                    )
                    model = model_module.GeometricToriTransformer(cfg)
                    for block in model.blocks:
                        block.attn.relative_bias.requires_grad = bias
                    models[arm] = model
            first = next(iter(models.values())).named_parameters()
            for model in models.values():
                named = model.named_parameters()
                if list(first) != list(named) or any(
                    not np.array_equal(first[name].data, named[name].data) for name in first
                ):
                    raise RuntimeError("factorial arms must share initialization and parameter schema")

            def batch(rng, count):
                tokens = rng.integers(0, 8, size=(count, seq_len))
                # Periodic copy wraps at the sequence boundary. Nonperiodic
                # copy uses a fixed start sentinel and never wraps.
                targets = np.roll(tokens, 1, axis=1)
                if task == "nonperiodic_copy":
                    targets[:, 0] = 0
                elif task == "alias74_lag_copy":
                    targets = tokens[:, :-74]
                return tokens, targets

            def measured_logits(model, inputs):
                logits, _ = model(inputs)
                return logits[:, 74:, :] if task == "alias74_lag_copy" else logits

            eval_tokens, eval_targets = batch(np.random.default_rng(settings["seed"] + 2), 8)
            arms = {}
            for arm, model in models.items():
                parameters = [p for p in model.parameters() if p.requires_grad]
                optimizer = optim.Adam(parameters, lr=settings["learning_rate"])
                rng = np.random.default_rng(settings["seed"] + 1)
                logits = measured_logits(model, eval_tokens)
                initial = float(tensor.cross_entropy(logits, eval_targets).data)
                for _ in range(settings["steps"]):
                    inputs, targets = batch(rng, settings["batch_size"])
                    logits = measured_logits(model, inputs)
                    loss = tensor.cross_entropy(logits, targets)
                    if not np.isfinite(loss.data):
                        raise RuntimeError("experiment training loss became non-finite")
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                logits = measured_logits(model, eval_tokens)
                arms[arm] = {
                    "parameter_count": model.num_parameters(),
                    "active_parameter_count": sum(p.data.size for p in parameters),
                    "initial_heldout_loss": initial,
                    "heldout_loss": float(tensor.cross_entropy(logits, eval_targets).data),
                    "heldout_accuracy": float(np.mean(np.argmax(logits.data, axis=-1) == eval_targets)),
                    "completed_steps": optimizer.t,
                    "bias_l2": float(sum(np.linalg.norm(block.attn.relative_bias.data) for block in model.blocks)),
                }
            tasks[task] = {
                "target_rule": {
                    "periodic_copy": "y[i]=x[(i-1)%T]",
                    "nonperiodic_copy": "y[0]=0; y[i]=x[i-1] for i>0",
                    "alias74_lag_copy": "y[i]=x[i-74]; train and evaluate only positions i>=74",
                }[task],
                "arms": arms,
            }
        result = {
            "task": "synthetic_rotary_bias_factorial",
            "shared_settings": {**settings, "vocab_size": 8, "causal": False,
                                "heldout_batch_size": 8, "alias_probe": alias_probe},
            "controls": {
                "identical_initial_parameters": True, "identical_batches_per_arm": True,
                "heldout_rng_seed": settings["seed"] + 2, "training_rng_seed": settings["seed"] + 1,
                "bias_off": "same allocated table, frozen at zero; excluded from optimizer",
                "optimizer": "Adam", "factors": ["rotary_schedule", "learned_scalar_bank_bias"],
            },
            "tasks": tasks,
            "run_scope": "alias-sensitive synthetic probe" if alias_probe else "default smoke execution only",
            "limitations": "Tiny descriptive synthetic runs; no convergence or superiority claim. Optional lag-74 copy probes raw offsets but does not establish resolution of modular aliasing. Bias-off arms have fewer active parameters.",
        }
        raw = json.dumps(result, allow_nan=False, sort_keys=True).encode("utf-8")
        artifact = self.state_dir / "experiments" / f"{uuid4().hex}.json"
        self._write_private(artifact, raw)
        result["artifact"] = {"path": str(artifact.relative_to(self.state_dir)),
                              "sha256": hashlib.sha256(raw).hexdigest()}
        return result
