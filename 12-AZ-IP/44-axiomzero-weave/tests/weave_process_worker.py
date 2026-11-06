# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Importable spawn target independent of pytest's generated test-module names."""

from az_weave.governance import Journal


def process_effect(path, identifier, started, finish):
    journal = Journal(path)

    def handler():
        started.set()
        if not finish.wait(15):
            raise RuntimeError("test handler timeout")
        return {"actual": 1}

    journal.execute(identifier, "operator", "effect", {"target": "one"}, handler, lambda _: True)
