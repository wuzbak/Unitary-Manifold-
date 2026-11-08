# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Fresh-interpreter compatibility checks for physically sharded core pillars."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("module_name", "symbol"),
    [
        ("pillar1129_malecns_connectome_empirical_bridge", "_repository_root"),
        ("pillar1133_superfluid_effective_theory", "bogoliubov_energy_joule"),
        ("pillar1134_rare_decay_probes", "SignificanceAssessment"),
        (
            "pillar1136_planar_radion_scalar_energy_balance",
            "planar_radion_scalar_energy_balance_certificate",
        ),
    ],
)
def test_flat_import_identity_introspection_and_discovery(module_name, symbol):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import importlib
import inspect
import pathlib
import pickle
import pkgutil
import sys

import src.core

name, symbol, root = sys.argv[1:]
qualified = "src.core." + name
discovered = [info for info in pkgutil.iter_modules(src.core.__path__)
              if info.name == name]
assert len(discovered) == 1, discovered
module = importlib.import_module(qualified)
assert getattr(src.core, name) is module
assert sys.modules[qualified] is module
assert importlib.import_module(qualified) is module
expected = pathlib.Path(root) / "src/core/pillar_1129_1168" / (name + ".py")
assert pathlib.Path(module.__file__).resolve() == expected
assert pathlib.Path(module.__spec__.origin).resolve() == expected
assert module.__name__ == qualified
assert module.__package__ == "src.core"
obj = getattr(module, symbol)
assert obj.__module__ == qualified
assert pathlib.Path(inspect.getfile(obj)).resolve() == expected
assert inspect.getmodule(obj) is module
assert pickle.loads(pickle.dumps(obj)) is obj
namespace = {}
exec("from " + qualified + " import " + symbol, namespace)
assert namespace[symbol] is obj
if name.startswith("pillar1129_"):
    assert module._repository_root() == pathlib.Path(root)
""",
            module_name,
            symbol,
            str(root),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
