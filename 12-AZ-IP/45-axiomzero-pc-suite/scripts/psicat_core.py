# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Native desktop bridge to the repository's own causal toroidal model."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "43-az-geometric-tori-transformer"))

from az_tori_transformer import generate_text, load_checkpoint, train_text_file

MAX_REQUEST_BYTES = 16384
PROFILE = {"context_length": 64, "batch_size": 8, "dim": 64, "num_heads": 4, "num_layers": 2, "seed": 7}


def execute(request: dict) -> dict:
    if not isinstance(request, dict) or request.get("action") not in {"status", "train", "generate"}:
        raise ValueError("Native model action is not allowed.")
    checkpoint = request.get("checkpoint")
    if not isinstance(checkpoint, str) or not checkpoint or "\0" in checkpoint:
        raise ValueError("A valid local checkpoint path is required.")
    action = request["action"]
    if action == "train":
        corpus = request.get("corpus")
        steps = request.get("steps")
        if not isinstance(corpus, str) or not corpus or "\0" in corpus:
            raise ValueError("Select a local UTF-8 corpus.")
        if type(steps) is not int or not 1 <= steps <= 2000:
            raise ValueError("Training steps must be an integer between 1 and 2000.")
        if type(request.get("resume", False)) is not bool:
            raise ValueError("Resume must be Boolean.")
        report = train_text_file(
            corpus, checkpoint, steps=steps, resume=request.get("resume", False), **PROFILE
        )
        return {
            "status": "completed", "kind": "own-toroidal-character-model",
            "epistemicLabel": "UNVERIFIED", "productionAssistantVerified": False,
            "training": report,
        }
    loaded = load_checkpoint(checkpoint)
    if loaded.metadata.get("task") != "character_language_model" or not loaded.model.cfg.causal:
        raise ValueError("The bundled checkpoint is not a causal character model.")
    if loaded.model.cfg.positional_mode != "toroidal":
        raise ValueError("The desktop own-model runtime requires a toroidal checkpoint.")
    result = {
        "status": "ready", "kind": "own-toroidal-character-model",
        "epistemicLabel": "UNVERIFIED", "productionAssistantVerified": False,
        "parameterCount": loaded.model.num_parameters(),
        "contextLength": loaded.metadata["context_length"],
        "completedSteps": loaded.metadata.get("completed_steps"),
        "datasetSha256": loaded.metadata.get("dataset_sha256"),
    }
    if action == "generate":
        prompt = request.get("prompt")
        if not isinstance(prompt, str) or not 1 <= len(prompt) <= 400:
            raise ValueError("Prompt must contain 1-400 characters.")
        vocabulary = set(loaded.metadata["vocabulary"])
        unknown = sorted(set(prompt) - vocabulary)
        if unknown:
            return {**result, "status": "blocked-vocabulary", "unknownCharacters": unknown}
        text = generate_text(checkpoint, prompt, max_new_tokens=160, temperature=0.8, top_k=min(20, len(vocabulary)), seed=7)
        result.update({"status": "completed", "completion": text[len(prompt):]})
    return result


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
        if len(raw) > MAX_REQUEST_BYTES:
            raise ValueError("Native model request exceeds the input budget.")
        request = json.loads(raw.decode("utf-8"))
        print(json.dumps(execute(request), ensure_ascii=True, allow_nan=False), flush=True)
        return 0
    except (OSError, ValueError, TypeError, FloatingPointError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
