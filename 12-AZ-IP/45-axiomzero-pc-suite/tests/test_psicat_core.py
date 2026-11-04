# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Actual own-model desktop host contracts without a model provider."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/psicat_core.py"
spec = importlib.util.spec_from_file_location("desktop_psicat_core", SCRIPT)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def test_native_training_status_generation_and_vocabulary_refusal(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("PsiCat native corpus. " * 100, encoding="utf-8")
    checkpoint = tmp_path / "model.npz"
    result = core.execute({"action": "train", "corpus": str(corpus), "checkpoint": str(checkpoint), "steps": 1})
    assert result["training"]["completed_steps"] == 1
    assert result["productionAssistantVerified"] is False
    ready = core.execute({"action": "status", "checkpoint": str(checkpoint)})
    assert ready["contextLength"] == 64
    assert ready["kind"] == "own-toroidal-character-model"
    result = core.execute({"action": "generate", "checkpoint": str(checkpoint), "prompt": "PsiCat"})
    assert result["status"] == "completed"
    assert len(result["completion"]) == 160
    result = core.execute({"action": "generate", "checkpoint": str(checkpoint), "prompt": "\U0001f984"})
    assert result["status"] == "blocked-vocabulary"


@pytest.mark.parametrize("action", ["shell", "fetch", "unknown", None])
def test_native_host_denies_unregistered_actions(action):
    with pytest.raises(ValueError, match="not allowed"):
        core.execute({"action": action, "checkpoint": "unused"})


@pytest.mark.parametrize("steps", [0, 2001, True, "500"])
def test_native_training_budget_validation_precedes_filesystem_access(steps):
    with pytest.raises(ValueError, match="steps"):
        core.execute({"action": "train", "corpus": "unused", "checkpoint": "unused", "steps": steps})
