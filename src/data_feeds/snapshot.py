# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/data_feeds/snapshot.py
==========================
Offline fallback cache for all data-feed adapters.

``latest_snapshot.json`` lives in the same directory as this file and is
committed to the repository pre-seeded with April 2026 observed values.
Adapters call ``load(key)`` on any network failure; a successful live fetch
can be persisted back via ``save(key, data)``.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import json
import pathlib
from typing import Any

_SNAPSHOT_PATH = pathlib.Path(__file__).parent / "latest_snapshot.json"


def load(key: str) -> Any:
    """Return the cached value for *key* from the snapshot file.

    Parameters
    ----------
    key : str
        Adapter identifier, e.g. ``"usgs_seismic"``.

    Returns
    -------
    Any
        The cached value.  Raises ``KeyError`` if the key is absent and
        ``FileNotFoundError`` if the snapshot file is missing.
    """
    with open(_SNAPSHOT_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    return data[key]


def save(key: str, value: Any) -> None:
    """Persist *value* for *key* in the snapshot file.

    The file is read, updated, and written atomically so that a crash
    during the write cannot corrupt existing entries.

    Parameters
    ----------
    key   : str — adapter identifier
    value : Any — JSON-serialisable value to store
    """
    try:
        with open(_SNAPSHOT_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        data = {}

    data[key] = value

    tmp = _SNAPSHOT_PATH.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    tmp.replace(_SNAPSHOT_PATH)
